"""The Explanation Context Builder: what a language model is allowed to see.

The evidence graph for one alert is 35 nodes and 39 edges. Handing all of it to
a model is the RAG failure mode in miniature -- give it everything and it will
narrate whatever correlation it notices. This module decides what the model
sees, and the decision is deliberately narrow.

**Four sections, and nothing else.** What happened, what was measured, what the
safety layer did, and what the result does not establish. No handbook, no
reports, no research prose, no free-text field an author could smuggle context
through. The model is a translator; this is its dictionary.

**The limitations travel with the evidence.** They are not appended after the
model has spoken -- they are part of the input, so a model that ignores them is
visibly ignoring its own brief, and the claim guard catches it on the way out.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .graph import EvidenceGraph

#: Gate conditions whose failure means the safety layer refused to learn from
#: the window, with the plain reason. G4 and G5 are the contamination controls.
LEARNING_BLOCKERS: dict[str, str] = {
    "G1": "the window was not a usable physical observation",
    "G2": "the representation was not finite",
    "G3": "signal quality was outside its frozen bounds",
    "G4": "the window did not look normal enough to learn from",
    "G5": "a memory-update refractory was still active",
    "G6": "morphology could not be computed",
}


@dataclass(frozen=True)
class ExplanationContext:
    """The compact, closed schema a generator receives."""

    event: dict[str, Any]
    evidence: dict[str, Any]
    safety: dict[str, Any]
    limitations: tuple[str, ...]
    provenance: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_context(graph: EvidenceGraph) -> ExplanationContext:
    """Reduce an evidence graph to the four sections a generator may use."""
    alert = graph.node(graph.root)

    measurements = {
        node.evidence["symbol"]: node.evidence
        for node in graph.of_kind("measurement")
    }

    def value(symbol: str) -> float | None:
        entry = measurements.get(symbol)
        return None if entry is None else entry.get("value")

    gates = {
        node.evidence["condition"]: node.evidence
        for node in graph.of_kind("gate")
    }
    blocked = [
        condition
        for condition, entry in sorted(gates.items())
        if entry.get("passed") is False
    ]

    policy_nodes = graph.of_kind("policy")
    policy = policy_nodes[0].evidence if policy_nodes else {}

    return ExplanationContext(
        event={
            # An AlertEvent only ever represents a contiguous EVENT run; the
            # state machine's other states never produce one.
            "type": "EVENT",
            "entered_from": alert.evidence.get("entered_from"),
            "closed_into": alert.evidence.get("closed_into"),
            "still_open": alert.evidence.get("still_open"),
            "opened_at": alert.evidence.get("opened_at"),
            "duration_seconds": alert.evidence.get("duration_seconds"),
            "window_count": alert.evidence.get("window_count"),
        },
        evidence={
            # p_t is the only calibrated probability in the pipeline. s_t is a
            # bounded score and is named so the generator cannot promote it.
            "calibrated_probability": value("p_t"),
            "temporal_support_bounded_score": value("s_t"),
            "memory_deviation": value("d_long"),
            "decision_error_uncertainty": value("u_t"),
            "temporal_support_is_a_probability": False,
        },
        safety={
            "learning_blocked": bool(blocked),
            "blocked_by": tuple(blocked),
            "reasons": tuple(
                LEARNING_BLOCKERS[condition]
                for condition in blocked
                if condition in LEARNING_BLOCKERS
            ),
            "conditions_passed": tuple(
                condition
                for condition, entry in sorted(gates.items())
                if entry.get("passed") is True
            ),
            "note": (
                "The patient baseline is only updated by windows that look "
                "normal and are outside a refractory. A blocked update is the "
                "contamination control working, not a failure."
            ),
        },
        limitations=tuple(
            node.evidence["does_not_establish"]
            for node in graph.of_kind("constraint")
        ),
        provenance={
            key: policy[key]
            for key in ("t1_policy_id", "t1_held_out_subject")
            if key in policy
        },
    )
