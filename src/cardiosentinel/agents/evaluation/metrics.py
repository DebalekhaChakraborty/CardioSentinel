"""The four metrics of the evaluation protocol §3.

Every one is computed from the explanation text and the `ExplanationContext`
that produced it. Nothing here needs a model, a network, or a credential.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

from .. import claims
from ..context import ExplanationContext

#: Protocol §3.3. Four elements an explanation must carry.
COMPLETENESS_ELEMENTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("state_transition", ("EVENT", "WATCH", "NORMAL", "RECOVERY")),
    ("gate_behaviour", ("gate", "refractory", "normal enough", "blocked", "declined")),
    ("baseline_update_decision", ("baseline", "update", "learn")),
    ("limitation", ("does not establish", "system behaviour only")),
)

#: Numbers below this magnitude are formatting noise (window counts, clock
#: parts), not evidence claims. Fidelity scores the evidence-bearing values.
_NUMBER = re.compile(r"\d+\.\d{2,}")


def _numbers(text: str) -> list[str]:
    return _NUMBER.findall(text)


def _context_numbers(context: ExplanationContext) -> set[str]:
    """Every numeric value the arm was given, at several roundings.

    An explanation that says 0.546 for a context value of 0.545613 is rounding,
    not fabricating, so the supported set includes sensible renderings.
    """
    supported: set[str] = set()
    for section in (context.event, context.evidence):
        for value in section.values():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            for places in (2, 3, 4, 6):
                supported.add(f"{float(value):.{places}f}")
            supported.add(str(value))
    return supported


def evidence_fidelity(text: str, context: ExplanationContext) -> float | None:
    """Protocol §3.1. `None` when the text carries no evidence-bearing number.

    Never silently 1.0: an explanation that states no numbers has not
    demonstrated fidelity, it has avoided the question.
    """
    stated = _numbers(text)
    if not stated:
        return None
    supported = _context_numbers(context)
    matched = sum(1 for number in stated if number in supported)
    return matched / len(stated)


def claim_violations(text: str, quoting: tuple[str, ...] = ()) -> tuple[str, ...]:
    """Protocol §3.2."""
    return tuple(str(v) for v in claims.audit(text, quoting=quoting))


def completeness(text: str) -> tuple[float, tuple[str, ...]]:
    """Protocol §3.3. Returns the fraction and which elements were missing."""
    lowered = text.lower()
    missing = [
        name
        for name, markers in COMPLETENESS_ELEMENTS
        if not any(marker.lower() in lowered for marker in markers)
    ]
    present = len(COMPLETENESS_ELEMENTS) - len(missing)
    return present / len(COMPLETENESS_ELEMENTS), tuple(missing)


@dataclass(frozen=True)
class ExplanationScore:
    arm: str
    fidelity: float | None
    violations: tuple[str, ...]
    completeness: float
    missing_elements: tuple[str, ...]
    latency_seconds: float
    characters: int
    fabricated_numbers: tuple[str, ...] = ()

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def score_explanation(
    arm: str,
    text: str,
    context: ExplanationContext,
    *,
    latency_seconds: float,
    quoting: tuple[str, ...] = (),
) -> ExplanationScore:
    fidelity = evidence_fidelity(text, context)
    supported = _context_numbers(context)
    fabricated = tuple(n for n in _numbers(text) if n not in supported)
    ratio, missing = completeness(text)
    return ExplanationScore(
        arm=arm,
        fidelity=fidelity,
        violations=claim_violations(text, quoting=quoting),
        completeness=ratio,
        missing_elements=missing,
        latency_seconds=latency_seconds,
        characters=len(text),
        fabricated_numbers=fabricated,
    )
