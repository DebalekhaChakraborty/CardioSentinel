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
    """
    require_raw_profile(raw_profile())
    source = Path(source_root)
    generator = CausalWindowGenerator(
        SAMPLING_FREQUENCY_HZ, WINDOW_SECONDS, STRIDE_SECONDS
    )
    chunk_samples = int(chunk_seconds * SAMPLING_FREQUENCY_HZ)
    limit = None if max_seconds is None else int(max_seconds * SAMPLING_FREQUENCY_HZ)

    start = 0
    while limit is None or start < limit:
        end = start + chunk_samples
        if limit is not None:
            end = min(end, limit)
        try:
            segment = read_local_segment(
                source, "ltstdb", record_id, start, end, (channel_index,)
            )
        except Exception:  # noqa: BLE001 - end of record is not an error
            return
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
