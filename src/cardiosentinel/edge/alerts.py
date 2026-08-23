"""Turn the T1 state stream into discrete alert events.

`t1_assembly` already treats a contiguous run of `EVENT` rows as one predicted
episode; this is the streaming form of that, emitted as it happens rather than
assembled afterwards. The run boundaries are the same boundaries.

**An `AlertEvent` is the first object the agentic layer consumes**, so it
carries its evidence rather than just its outcome: the window that opened it,
the window that confirmed it, the observations spanned, and the frozen
provenance of everything that produced it. An alert that cannot name the
checkpoint, calibrator and threshold policy behind it is not auditable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ..neural.t1_protocol import T1_STATE_EVENT
from .session import EdgeObservation


def _clock(seconds: float) -> str:
    total = int(seconds)
    return f"{total // 3600:02d}:{(total % 3600) // 60:02d}:{total % 60:02d}"


@dataclass(frozen=True)
class AlertEvent:
    """One contiguous `EVENT` run: an episode the system asserted live.

    **Timing convention, stated because it is ambiguous otherwise.** All times
    are the *window* times the T1 state machine acted on:
    `elapsed_stream_seconds`, the end of each window's data. `opened_at` is the
    first window in `EVENT`, `closed_at` is the **last window still in
    `EVENT`** -- not the window that left it -- and `duration_seconds` is the
    span between them.

    That is the span over which the system *asserted* an event. It is not the
    duration of a physiological episode, and it is not the covered signal
    interval either: windows are 10 s long on a 5 s stride, so consecutive
    windows overlap. Reporting a covered interval would require a convention
    this programme never registered, so none is invented here.
    """

    record_id: str
    subject_id: str
    channel_index: int
    opened_at_seconds: float
    confirmed_at_seconds: float
    closed_at_seconds: float | None
    opened_at: str
    confirmed_at: str
    closed_at: str | None
    duration_seconds: float | None
    window_count: int
    peak_calibrated_probability: float | None
    peak_temporal_evidence: float | None
    max_memory_deviation: float | None
    entered_from: str
    closed_into: str | None
    open: bool
    provenance: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class AlertBuilder:
    """Accumulate observations and emit an `AlertEvent` per `EVENT` run.

    Streaming, so an alert is *opened* the moment the state machine confirms an
    event and *closed* when it leaves. A run still open at the end of the stream
    is emitted with `open=True` rather than silently dropped -- a monitoring
    system that forgets in-progress episodes is worse than one that says so.
    """

    def __init__(self, provenance: dict[str, Any] | None = None) -> None:
        self._provenance = dict(provenance or {})
        self._current: list[EdgeObservation] = []
        self._entered_from: str | None = None
        self._closed: list[AlertEvent] = []

    def observe(self, observation: EdgeObservation) -> AlertEvent | None:
        """Feed one observation. Returns an alert when a run *closes*."""
        in_event = observation.state == T1_STATE_EVENT
        if in_event:
            if not self._current:
                self._entered_from = observation.state_before
            self._current.append(observation)
            return None
        if self._current:
            alert = self._build(closed_into=observation.state, still_open=False)
            self._closed.append(alert)
            self._current = []
            self._entered_from = None
            return alert
        return None

    def finalize(self) -> AlertEvent | None:
        """Emit a still-open run at end of stream, marked `open=True`."""
        if not self._current:
            return None
        alert = self._build(closed_into=None, still_open=True)
        self._closed.append(alert)
        self._current = []
        return alert

    @property
    def alerts(self) -> tuple[AlertEvent, ...]:
        return tuple(self._closed)

    def _build(self, *, closed_into: str | None, still_open: bool) -> AlertEvent:
        run = self._current
        first, last = run[0], run[-1]

        def peak(name: str) -> float | None:
            values = [
                getattr(item, name) for item in run if getattr(item, name) is not None
            ]
            return max(values) if values else None

        opened = first.elapsed_stream_seconds
        closed = None if still_open else last.elapsed_stream_seconds
        return AlertEvent(
            record_id=first.record_id,
            subject_id=first.subject_id,
            channel_index=first.channel_index,
            opened_at_seconds=opened,
            # The state machine confirms an event only after
            # `event_confirm_windows` consecutive rows, so the run's first
            # window is the confirmation instant, not the first suspicion.
            confirmed_at_seconds=opened,
            closed_at_seconds=closed,
            opened_at=_clock(opened),
            confirmed_at=_clock(opened),
            closed_at=None if closed is None else _clock(closed),
            duration_seconds=None if closed is None else closed - opened,
            window_count=len(run),
            peak_calibrated_probability=peak("calibrated_probability"),
            peak_temporal_evidence=peak("temporal_evidence"),
            max_memory_deviation=peak("memory_deviation"),
            entered_from=self._entered_from or first.state_before,
            closed_into=closed_into,
            open=still_open,
            provenance=dict(self._provenance),
        )
