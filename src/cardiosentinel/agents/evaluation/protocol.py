"""Protocol constants and result types. The rules live here, not in prose."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

PROTOCOL_DOCUMENT = "docs/EXPLANATION_EVALUATION_PROTOCOL.md"

ARM_DETERMINISTIC = "deterministic"
ARM_GENERATIVE = "generative"
ARMS = (ARM_DETERMINISTIC, ARM_GENERATIVE)

#: Protocol §5, restated as data so the renderer cannot omit them.
REPORTING_RULES: tuple[str, ...] = (
    "No winner is declared; this is a trade-off table.",
    "Neither arm is described as better than the other.",
    "A generative result is never reported without its violation count.",
    "Fidelity below 1.0 is reported as fabrication, not as a tendency.",
    "Latency is not comparable across hosts.",
    "An unexercised arm is marked in the table, not in a footnote.",
)


@dataclass(frozen=True)
class ArmResult:
    arm: str
    exercised: bool
    provider: str | None
    scores: tuple[Any, ...] = ()
    note: str | None = None

    @property
    def mean_fidelity(self) -> float | None:
        values = [s.fidelity for s in self.scores if s.fidelity is not None]
        return sum(values) / len(values) if values else None

    @property
    def total_violations(self) -> int:
        return sum(s.violation_count for s in self.scores)

    @property
    def mean_completeness(self) -> float | None:
        if not self.scores:
            return None
        return sum(s.completeness for s in self.scores) / len(self.scores)

    @property
    def mean_latency(self) -> float | None:
        if not self.scores:
            return None
        return sum(s.latency_seconds for s in self.scores) / len(self.scores)

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.update(
            {
                "mean_fidelity": self.mean_fidelity,
                "total_violations": self.total_violations,
                "mean_completeness": self.mean_completeness,
                "mean_latency_seconds": self.mean_latency,
            }
        )
        return payload


@dataclass(frozen=True)
class EvaluationReport:
    contexts_evaluated: int
    arms: tuple[ArmResult, ...]
    protocol: str = PROTOCOL_DOCUMENT
    reporting_rules: tuple[str, ...] = REPORTING_RULES
    conclusion: str = (
        "Generative explanations offer linguistic flexibility and require "
        "explicit evidence-boundary enforcement. This table reports that "
        "trade-off; it does not rank the arms."
    )
    defects: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, Any]:
        return {
            "protocol": self.protocol,
            "contexts_evaluated": self.contexts_evaluated,
            "arms": [arm.as_dict() for arm in self.arms],
            "reporting_rules": list(self.reporting_rules),
            "conclusion": self.conclusion,
            "defects": list(self.defects),
        }
