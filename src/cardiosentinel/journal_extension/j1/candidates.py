"""The two frozen candidate registries and the frozen selection order.

J1-S: 12 candidates, `NO EXPANSION` -- 4 quantile combinations x 3 persistence
profiles. J1 asks whether *the retained policy* survives a fair comparator, so
widening this space would change the object under test.

J1-W: 206 candidates. Larger on purpose. A memoryless comparator constrained to
resemble V1's W1 would rebuild the defect J1 exists to remove. The asymmetry is
disclosed, not corrected.

A candidate ID fixes rule structure and quantile level(s). Its numeric
thresholds are fold-specific FIT-derived quantities and are not stored here.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Callable

from .rows import ArmNeutralRow

Q_WATCH_LEVELS: tuple[float, ...] = (0.90, 0.95)
Q_EVENT_LEVELS: tuple[float, ...] = (0.99, 0.995)
PERSISTENCE_PROFILES: tuple[str, ...] = ("FAST", "MED", "SLOW")

#: J1-W threshold levels, frozen by protocol section 6.2.
W_LEVELS: tuple[float, ...] = (0.90, 0.95, 0.975, 0.99, 0.995)
#: Continuous signals available to a memoryless rule.
W_SIGNALS: tuple[str, ...] = ("pt", "st", "m2g")

_SIGNAL_FIELD = {
    "pt": "oof_calibrated_probability_p_t",
    "st": "s4d_temporal_evidence_s_t",
    "m2g": "m2g_detector_score",
}


@dataclass(frozen=True)
class StatefulCandidate:
    """One J1-S policy identity."""

    q_watch: float
    q_event: float
    profile: str

    @property
    def candidate_id(self) -> str:
        return f"S-qw{self.q_watch}-qe{self.q_event}-{self.profile}"


@dataclass(frozen=True)
class MemorylessCandidate:
    """One J1-W rule identity: structure plus quantile level(s)."""

    family: str
    signals: tuple[str, ...]
    levels: tuple[float, ...]
    uses_d_t: bool = False

    @property
    def candidate_id(self) -> str:
        signals = ".".join(self.signals) or "dt"
        levels = ".".join(str(level) for level in self.levels) or "na"
        return f"W-{self.family}-{signals}-{levels}"


def stateful_registry() -> tuple[StatefulCandidate, ...]:
    """The 12 frozen J1-S candidates, in deterministic order."""
    return tuple(
        StatefulCandidate(q_watch=qw, q_event=qe, profile=profile)
        for qw in Q_WATCH_LEVELS
        for qe in Q_EVENT_LEVELS
        for profile in PERSISTENCE_PROFILES
    )


def memoryless_registry() -> tuple[MemorylessCandidate, ...]:
    """The 206 frozen J1-W candidates, enumerated in deterministic order."""
    out: list[MemorylessCandidate] = []
    for signal in W_SIGNALS:  # A: single signal -- 15
        out.extend(
            MemorylessCandidate("A", (signal,), (level,)) for level in W_LEVELS
        )
    out.append(MemorylessCandidate("B", (), (), uses_d_t=True))  # B: d_t -- 1
    for a, b in combinations(W_SIGNALS, 2):  # C/D: pairwise, free levels -- 150
        for la in W_LEVELS:
            for lb in W_LEVELS:
                out.append(MemorylessCandidate("C", (a, b), (la, lb)))
                out.append(MemorylessCandidate("D", (a, b), (la, lb)))
    for signal in W_SIGNALS:  # E/F: continuous with d_t -- 30
        for level in W_LEVELS:
            out.append(
                MemorylessCandidate("E", (signal,), (level,), uses_d_t=True)
            )
            out.append(
                MemorylessCandidate("F", (signal,), (level,), uses_d_t=True)
            )
    for level in W_LEVELS:  # G/H: triple, matched level -- 10
        out.append(MemorylessCandidate("G", W_SIGNALS, (level,)))
        out.append(MemorylessCandidate("H", W_SIGNALS, (level,)))
    return tuple(out)


def memoryless_rule(
    candidate: MemorylessCandidate, thresholds: dict[str, float]
) -> Callable[[ArmNeutralRow], bool]:
    """Build the pure `row -> bool` rule for a candidate.

    No closure state, no counters, no history. The returned callable reads only
    the row handed to it, so it cannot become a second state machine.
    """
    fields = tuple(_SIGNAL_FIELD[s] for s in candidate.signals)

    def rule(row: ArmNeutralRow) -> bool:
        fired = [
            getattr(row, field) >= thresholds[signal]
            for signal, field in zip(candidate.signals, fields)
        ]
        if candidate.family in {"A"}:
            decision = all(fired)
        elif candidate.family == "B":
            decision = bool(row.detector_decision_d_t)
        elif candidate.family in {"C", "G"}:
            decision = all(fired)
        elif candidate.family in {"D", "H"}:
            decision = any(fired)
        elif candidate.family == "E":
            decision = all(fired) and bool(row.detector_decision_d_t)
        elif candidate.family == "F":
            decision = all(fired) or bool(row.detector_decision_d_t)
        else:  # pragma: no cover - families are closed
            raise ValueError(f"unknown J1-W family {candidate.family!r}")
        return bool(decision)

    return rule
