"""Categorical state alignment: prose must agree with the structured fields.

Every test is stub-backed. No model, no weights, no network.

The failure this layer exists for was found by running Arm B, not by predicting
it: `Qwen3-1.7B` produced a fluent, claim-compliant, numerically-faithful
explanation asserting *"The system passed several safety checks, including G1
through G6"* when G4 and G5 were blocked. See protocol §4.4.
"""

from __future__ import annotations

import pytest

from cardiosentinel.agents import claims
from cardiosentinel.agents.alignment import categorical_violations
from cardiosentinel.agents.context import ExplanationContext
from cardiosentinel.agents.explain import (
    DETERMINISTIC,
    GENERATIVE,
    PatientExplanationAgent,
    TemplateRenderer,
)


@pytest.fixture
def context() -> ExplanationContext:
    """The demo scenario's shape: G4 and G5 blocked, the rest passed."""
    return ExplanationContext(
        event={
            "type": "EVENT",
            "entered_from": "WATCH",
            "closed_into": "NORMAL",
            "still_open": False,
            "opened_at": "00:17:05",
            "duration_seconds": 640,
            "window_count": 129,
        },
        evidence={
            "calibrated_probability": 0.545613,
            "temporal_support_bounded_score": 0.953344,
            "memory_deviation": 1.411607,
        },
        safety={
            "learning_blocked": True,
            "blocked_by": ("G4", "G5"),
            "conditions_passed": ("G1", "G2", "G3", "G6"),
            "reasons": ("the window did not look normal enough to learn from",),
            "note": "the contamination control working",
        },
        limitations=("a diagnosis",),
        provenance={},
    )


class Stub:
    name = "stub"
    model_name = "stub-model@abcdef1"
    identity = None

    def __init__(self, text: str) -> None:
        self._text = text

    def generate(self, brief: str, payload: str) -> str:
        return self._text


# -- correct summaries must pass -------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "G1, G2, G3 and G6 passed, while G4 and G5 blocked the update.",
        "The system blocked G4 and G5; G1, G2, G3 and G6 were satisfied.",
        "G4 and G5 were blocked but G1, G2, G3 and G6 passed.",
    ],
)
def test_a_correct_gate_summary_passes(text, context):
    """The one summary that is right must not be the one that is flagged.

    Proximity alone would attribute G4 to "passed" in the first sentence, so the
    validator splits on the contrast before attributing polarity.
    """
    assert categorical_violations(text, context) == ()


def test_text_asserting_nothing_categorical_passes(context):
    """Silence is a completeness question, not an alignment failure."""
    text = "The calibrated probability reached 0.546 and the event held 640 s."
    assert categorical_violations(text, context) == ()


def test_naming_gates_without_polarity_passes(context):
    """A gate mentioned with no claim about it is not a claim."""
    assert categorical_violations("The gates are G1 to G6.", context) == ()


def test_the_deterministic_renderer_passes_its_own_gate(context):
    """A gate that rejected the fallback would make every failure two failures."""
    assert categorical_violations(TemplateRenderer().render(context), context) == ()


# -- the failures it exists for --------------------------------------------


def test_the_observed_arm_b_failure_is_caught(context):
    """The exact sentence Qwen3-1.7B produced, which every other gate passed."""
    text = "The system passed several safety checks, including G1 through G6."
    assert not claims.audit(text), "precondition: the claim guard allows this"
    assert not PatientExplanationAgent._unsupported_numeric_claims(text, context), (
        "precondition: the numeric guard allows this"
    )
    violations = categorical_violations(text, context)
    assert violations
    assert "G4" in violations[0].detail and "G5" in violations[0].detail


def test_all_gates_passed_fails_when_any_is_blocked(context):
    violations = categorical_violations("All safety gates passed.", context)
    assert violations
    assert violations[0].kind == "universal_gate_claim"


def test_a_blocked_passed_inversion_fails(context):
    violations = categorical_violations(
        "G4 and G5 passed, while G1 and G2 were blocked.", context
    )
    kinds = {item.kind for item in violations}
    assert "gate_passed" in kinds
    assert "gate_blocked" in kinds


def test_a_lifecycle_state_the_event_never_carried_fails(context):
    violations = categorical_violations(
        "The system entered RECOVERY after the event.", context
    )
    assert violations
    assert violations[0].kind == "lifecycle_state"


def test_licensed_lifecycle_states_pass(context):
    text = "The system entered the EVENT state from WATCH and closed into NORMAL."
    assert categorical_violations(text, context) == ()


# -- integration: the agent falls back and records why ----------------------


def _graph_backed_agent_text(text: str):
    return PatientExplanationAgent(Stub(text))


def test_the_agent_falls_back_and_records_the_contradiction(context, monkeypatch):
    """Requirement 4: record violation details, fall back deterministically."""
    bad = (
        "The system passed several safety checks, including G1 through G6. "
        + claims.SYSTEM_BEHAVIOUR_ONLY
    )
    agent = _graph_backed_agent_text(bad)
    monkeypatch.setattr(
        "cardiosentinel.agents.explain.build_context", lambda _graph: context
    )
    explanation = agent.explain(object())
    assert explanation.explanation_mode == DETERMINISTIC
    assert "contradicts the recorded state" in (explanation.fallback_reason or "")
    assert explanation.claim_violations, (
        "the details must be recorded, not merely counted"
    )


def test_an_aligned_generation_is_returned_as_generative(context, monkeypatch):
    good = (
        "The system entered the EVENT state from WATCH. G1, G2, G3 and G6 passed, "
        "while G4 and G5 blocked the baseline update. "
        + claims.SYSTEM_BEHAVIOUR_ONLY
    )
    agent = _graph_backed_agent_text(good)
    monkeypatch.setattr(
        "cardiosentinel.agents.explain.build_context", lambda _graph: context
    )
    explanation = agent.explain(object())
    assert explanation.explanation_mode == GENERATIVE
