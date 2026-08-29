"""Laptop edge simulation: replay an LTSTDB record as a live ECG stream.

**This is a simulation and the documents must say so.** It replays a stored
recording in chunks; it is not an acquisition path and there is no sensor. The
honest claim is *"laptop-based edge simulation using streaming physiological
replay"*, which is what an Intelligent Physical Systems submission needs at
this stage, and no more than that.

**Only the twelve T1 validation subjects can be replayed.** Their operating
points are leave-one-subject-out; every other record has no validated
threshold, and borrowing one would produce a demo that looks right and means
nothing. `load_runtime_artifacts` refuses, and this module does not work around
the refusal.
"""

from __future__ import annotations

import math
import time
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..signal.config import raw_profile
from ..signal.io import read_local_segment
from ..signal.windows import CausalWindowGenerator
from .alerts import AlertBuilder, AlertEvent
from .artifacts import (
    DEFAULT_FEATURE_ROOT,
    DEFAULT_RUN_ROOT,
    DEFAULT_SOURCE_ROOT,
    load_runtime_artifacts,
)
from .representation import require_raw_profile
from .session import EdgeObservation, StreamingInferenceSession

#: The frozen windowing: 10 s windows, 5 s stride, 250 Hz.
WINDOW_SECONDS = 10.0
STRIDE_SECONDS = 5.0
SAMPLING_FREQUENCY_HZ = 250.0

#: One minute of ECG per read. Large enough that disk cost amortises, small
#: enough that the stream still feels incremental.
DEFAULT_CHUNK_SECONDS = 60.0


class ReplayError(RuntimeError):
    """The stored-record replay could not proceed safely."""


class ReplayConfigurationError(ReplayError):
    """A replay argument or record property violates the causal contract."""


class ReplayReadError(ReplayError):
    """Record metadata or a requested sample interval could not be read."""


@dataclass(frozen=True)
class ReplayRecordMetadata:
    """The authoritative WFDB bounds needed before any segment is requested."""

    sample_count: int
    channel_count: int
    sampling_frequency_hz: float


@dataclass
class ReplayResult:
    observations: list[EdgeObservation]
    alerts: list[AlertEvent]
    provenance: dict[str, Any]
    wall_seconds: float
    simulated_seconds: float

    @property
    def real_time_factor(self) -> float:
        return (
            self.simulated_seconds / self.wall_seconds if self.wall_seconds else 0.0
        )


def subject_for_record(record_id: str) -> str:
    """LTSTDB's own convention: the subject is the record minus its trailing digit."""
    from ..signal.catalog import subject_id_for_record

    return subject_id_for_record("ltstdb", record_id)


def _seconds_to_samples(name: str, value: float, *, allow_zero: bool) -> int:
    try:
        seconds = float(value)
    except (TypeError, ValueError) as error:
        raise ReplayConfigurationError(f"{name} must be a finite number.") from error
    if not math.isfinite(seconds) or seconds < 0 or (seconds == 0 and not allow_zero):
        qualifier = "non-negative" if allow_zero else "positive"
        raise ReplayConfigurationError(f"{name} must be finite and {qualifier}.")
    exact_samples = seconds * SAMPLING_FREQUENCY_HZ
    samples = round(exact_samples)
    if not math.isclose(exact_samples, samples, abs_tol=1e-9):
        raise ReplayConfigurationError(
            f"{name}={seconds!r} does not align to the "
            f"{SAMPLING_FREQUENCY_HZ:g} Hz sample grid."
        )
    if samples == 0 and not allow_zero:
        raise ReplayConfigurationError(
            f"{name} must advance by at least one source sample."
        )
    return samples


def _read_local_record_metadata(source: Path, record_id: str) -> ReplayRecordMetadata:
    """Read WFDB bounds once, before constructing any bounded segment request."""
    try:
        import wfdb

        header = wfdb.rdheader(str(Path(source) / record_id))
        metadata = ReplayRecordMetadata(
            sample_count=int(header.sig_len),
            channel_count=int(header.n_sig),
            sampling_frequency_hz=float(header.fs),
        )
    except Exception as error:  # noqa: BLE001 - converted, never mistaken for EOF
        raise ReplayReadError(
            f"Could not read WFDB metadata for record {record_id!r} from "
            f"{Path(source)} ({type(error).__name__})."
        ) from error
    if metadata.sample_count <= 0 or metadata.channel_count <= 0:
        raise ReplayConfigurationError(
            f"Record {record_id!r} reports {metadata.sample_count} samples and "
            f"{metadata.channel_count} channels; both must be positive."
        )
    if not math.isclose(
        metadata.sampling_frequency_hz, SAMPLING_FREQUENCY_HZ, abs_tol=1e-9
    ):
        raise ReplayConfigurationError(
            f"Record {record_id!r} reports {metadata.sampling_frequency_hz:g} Hz; "
            f"the frozen replay contract requires {SAMPLING_FREQUENCY_HZ:g} Hz."
        )
    return metadata


def stream_windows(
    record_id: str,
    *,
    channel_index: int = 0,
    source_root: Path | str = DEFAULT_SOURCE_ROOT,
    chunk_seconds: float = DEFAULT_CHUNK_SECONDS,
    max_seconds: float | None = None,
) -> Iterator[Any]:
    """Yield causal windows from a stored record, as a stream would deliver them.

    The frozen corpus was built under the **raw** identity profile, so no filter
    is applied here. `require_raw_profile` states that rather than leaving it
    implicit: a band-pass inserted later would shift every embedding silently.

    The final bounded read may be shorter than ``chunk_seconds``. It is still
    passed to the causal generator so every complete 10-second window is
    emitted. Any residual samples that cannot complete a window remain
    un-emitted: the contract authorizes neither padding nor interpolation.
    """
    if isinstance(channel_index, bool) or not isinstance(channel_index, int):
        raise ReplayConfigurationError("channel_index must be an integer.")
    if channel_index < 0:
        raise ReplayConfigurationError("channel_index must be non-negative.")
    chunk_samples = _seconds_to_samples(
        "chunk_seconds", chunk_seconds, allow_zero=False
    )
    limit = (
        None
        if max_seconds is None
        else _seconds_to_samples("max_seconds", max_seconds, allow_zero=True)
    )
    window_samples = _seconds_to_samples(
        "WINDOW_SECONDS", WINDOW_SECONDS, allow_zero=False
    )
    stride_samples = _seconds_to_samples(
        "STRIDE_SECONDS", STRIDE_SECONDS, allow_zero=False
    )
    if stride_samples > window_samples:
        raise ReplayConfigurationError(
            "The frozen stride cannot exceed the causal window length."
        )

    require_raw_profile(raw_profile())
    source = Path(source_root)
    metadata = _read_local_record_metadata(source, record_id)
    if channel_index >= metadata.channel_count:
        raise ReplayConfigurationError(
            f"Record {record_id!r} has {metadata.channel_count} channels; "
            f"channel {channel_index} is outside its WFDB metadata."
        )
    generator = CausalWindowGenerator(
        SAMPLING_FREQUENCY_HZ, WINDOW_SECONDS, STRIDE_SECONDS
    )
    readable_samples = metadata.sample_count
    if limit is not None:
        readable_samples = min(readable_samples, limit)

    start = 0
    while start < readable_samples:
        end = min(start + chunk_samples, readable_samples)
        try:
            segment = read_local_segment(
                source, "ltstdb", record_id, start, end, (channel_index,)
            )
        except Exception as error:  # noqa: BLE001 - preserve context in typed error
            raise ReplayReadError(
                f"Failed to read record {record_id!r}, channel {channel_index}, "
                f"requested sample interval [{start}, {end}) "
                f"({type(error).__name__})."
            ) from error
        if segment.start_sample != start or segment.end_sample != end:
            raise ReplayReadError(
                f"Reader returned [{segment.start_sample}, {segment.end_sample}) "
                f"for record {record_id!r}, channel {channel_index}, requested "
                f"sample interval [{start}, {end})."
            )
        yield from generator.process(segment)
        start = end


def replay_record(
    record_id: str,
    *,
    channel_index: int = 0,
    max_seconds: float | None = 600.0,
    source_root: Path | str = DEFAULT_SOURCE_ROOT,
    run_root: Path | str = DEFAULT_RUN_ROOT,
    feature_root: Path | str = DEFAULT_FEATURE_ROOT,
    chunk_seconds: float = DEFAULT_CHUNK_SECONDS,
    on_observation=None,
) -> ReplayResult:
    """Replay one record through the composed edge pipeline."""
    subject_id = subject_for_record(record_id)
    artifacts = load_runtime_artifacts(
        subject_id, run_root=run_root, feature_root=feature_root
    )
    session = StreamingInferenceSession(
        artifacts,
        subject_id=subject_id,
        record_id=record_id,
        channel_index=channel_index,
    )
    provenance = session.provenance()
    builder = AlertBuilder(provenance)

    observations: list[EdgeObservation] = []
    started = time.perf_counter()
    for window in stream_windows(
        record_id,
        channel_index=channel_index,
        source_root=source_root,
        chunk_seconds=chunk_seconds,
        max_seconds=max_seconds,
    ):
        observation = session.step(window)
        observations.append(observation)
        builder.observe(observation)
        if on_observation is not None:
            on_observation(observation)
    builder.finalize()
    wall = time.perf_counter() - started

    return ReplayResult(
        observations=observations,
        alerts=list(builder.alerts),
        provenance=provenance,
        wall_seconds=wall,
        simulated_seconds=(
            observations[-1].elapsed_stream_seconds if observations else 0.0
        ),
    )
