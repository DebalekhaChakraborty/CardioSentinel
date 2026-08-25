"""The evaluation harness, exercised without credentials.

The generative arm is unexercised in this environment, so the harness itself
must be proven with stub providers -- including a deliberately bad one. A
measurement framework that has never detected the thing it measures is not a
measurement framework.
"""

from __future__ import annotations

import pytest

from cardiosentinel.agents import claims
from cardiosentinel.agents.context import ExplanationContext
from cardiosentinel.agents.evaluation import (
    COMPLETENESS_ELEMENTS,
    REPORTING_RULES,
    completeness,
    evaluate_arms,
    evidence_fidelity,
    render_report,
)
from cardiosentinel.agents.providers import ProviderIdentity

CONTEXT = ExplanationContext(
    event={
        "type": "EVENT",
        "entered_from": "WATCH",
        "closed_into": "NORMAL",
        "still_open": False,
        "opened_at": "00:17:05",
        "duration_seconds": 640.0,
        "window_count": 129,
    },
    evidence={
        "calibrated_probability": 0.545613,
        "temporal_support_bounded_score": 0.953344,
        "memory_deviation": 1.411607,
        "decision_error_uncertainty": 0.034096,
        "temporal_support_is_a_probability": False,
    },
    safety={
        "learning_blocked": True,
        "blocked_by": ("G4", "G5"),
        "reasons": ("the window did not look normal enough to learn from",),
        "conditions_passed": ("G1", "G2", "G3", "G6"),
        "note": "A blocked update is the contamination control working.",
    },
    limitations=claims.APPROVED_DISCLAIMERS,
    provenance={"t1_policy_id": "qw0.9_qe0.99_FAST"},
)


class Stub:
    def __init__(self, text: str, name: str = "stub") -> None:
        self._text = text
        self.name = name

    def generate(self, brief: str, payload: str) -> str:
        return self._text


# -- metrics ---------------------------------------------------------------


def test_fidelity_is_one_when_every_number_comes_from_the_evidence():
    text = "Probability reached 0.545613 and support reached 0.953344."
    assert evidence_fidelity(text, CONTEXT) == 1.0


def test_fidelity_accepts_sensible_rounding():
    """0.546 for 0.545613 is rounding, not fabrication."""
    assert evidence_fidelity("Probability reached 0.546.", CONTEXT) == 1.0


def test_fidelity_catches_a_fabricated_number():
    text = "Probability reached 0.545613 and sensitivity was 0.870000."
    assert evidence_fidelity(text, CONTEXT) == pytest.approx(0.5)


def test_fidelity_is_undefined_rather_than_one_when_no_number_is_stated():
    """Stating no numbers avoids the question; it does not answer it."""
    assert evidence_fidelity("An event occurred.", CONTEXT) is None


def test_completeness_names_what_is_missing():
    ratio, missing = completeness("An EVENT occurred.")
    assert ratio < 1.0
    assert "limitation" in missing
    assert len(COMPLETENESS_ELEMENTS) == 4


# -- the harness -----------------------------------------------------------


def test_the_deterministic_arm_scores_perfectly_and_that_is_expected():
    report = evaluate_arms([CONTEXT])
    arm = report.arms[0]
    assert arm.exercised is True
    assert arm.mean_fidelity == 1.0
    assert arm.total_violations == 0
    assert arm.mean_completeness == 1.0
    assert report.defects == (), report.defects


def test_an_unexercised_arm_is_marked_in_the_table_not_a_footnote():
    text = render_report(evaluate_arms([CONTEXT]))
    assert "NOT EXERCISED" in text
    header_rows = [line for line in text.split("\n") if line.startswith("exercised")]
    assert header_rows and "NOT EXERCISED" in header_rows[0]


def test_a_fabricating_generator_is_detected():
    """The load-bearing test: the harness must catch what it exists to measure."""
    bad = Stub(
        "The system entered EVENT from WATCH, declined to update the baseline, "
        "and measured a sensitivity of 0.912345. "
        f"{claims.SYSTEM_BEHAVIOUR_ONLY}"
    )
    report = evaluate_arms([CONTEXT], provider=bad)
    generative = report.arms[1]
    assert generative.exercised is True
    assert generative.mean_fidelity is not None and generative.mean_fidelity < 1.0
    assert "0.912345" in generative.scores[0].fabricated_numbers


def test_an_overclaiming_generator_is_detected():
    bad = Stub(
        "The system detected disease and is deployment-ready; it generalizes "
        "to other hospitals."
    )
    report = evaluate_arms([CONTEXT], provider=bad)
    assert report.arms[1].total_violations >= 2


def test_an_incomplete_generator_is_detected():
    report = evaluate_arms([CONTEXT], provider=Stub("Something happened."))
    assert report.arms[1].mean_completeness < 1.0
    assert report.arms[1].scores[0].missing_elements


def test_a_compliant_generator_scores_clean():
    good = Stub(
        "The system entered the EVENT state from WATCH and held it. The "
        "calibrated probability reached 0.545613. It declined to update the "
        "patient baseline because the window did not look normal enough to "
        f"learn from. {claims.SYSTEM_BEHAVIOUR_ONLY}"
    )
    report = evaluate_arms([CONTEXT], provider=good)
    generative = report.arms[1]
    assert generative.total_violations == 0
    assert generative.mean_fidelity == 1.0
    assert generative.mean_completeness == 1.0


def test_generative_evaluation_records_immutable_provider_identity():
    provider = Stub(claims.SYSTEM_BEHAVIOUR_ONLY)
    provider.identity = ProviderIdentity(
        provider="local_qwen",
        model_id="Qwen/Qwen3-4B-Instruct-2507",
        revision="a" * 40,
        quantization="Q4",
        runtime="transformers",
        device="cpu",
    )
    report = evaluate_arms([CONTEXT], provider=provider)
    generative = report.arms[1]
    serialized = generative.as_dict()
    assert serialized["provider"] == "local_qwen"
    assert serialized["model"] == "Qwen/Qwen3-4B-Instruct-2507"
    assert serialized["revision"] == "a" * 40
    assert serialized["quantization"] == "Q4"
    assert serialized["runtime"] == "transformers"
    assert serialized["host"] == "cpu"
    assert serialized["latency_scope"] == "total generation latency"
    assert generative.provider == "local_qwen"
    assert generative.model == "Qwen/Qwen3-4B-Instruct-2507"
    assert generative.revision == "a" * 40
    assert generative.quantization == "Q4"
    assert generative.runtime == "transformers"
    assert generative.host == "cpu"
    assert generative.latency_scope == "total generation latency"

    rendered = render_report(report)
    for field in (
        "provider",
        "model",
        "revision",
        "quantization",
        "runtime",
        "host",
        "latency scope",
    ):
        assert any(line.startswith(field) for line in rendered.splitlines())


# -- reporting discipline --------------------------------------------------


def test_the_report_never_declares_a_winner():
    """Scanned over the BODY, not the rules block.

    Fifth occurrence of the quotation pattern in this repository: the rules
    state their prohibition using the prohibited words -- "No winner is
    declared", "Neither arm is described as better than the other". The rules
    are curated constant text, like `claims.APPROVED_DISCLAIMERS`; the body is
    what could actually overclaim.
    """
    full = render_report(evaluate_arms([CONTEXT], provider=Stub("x")))
    body = full.split("Reporting rules in force:")[0].lower()
    assert body, "report body is empty"
    for banned in ("winner", "better than", "outperform", "beats", "superior"):
        assert banned not in body, banned
    # The rules themselves must still be present and must still say it.
    assert "No winner is declared" in full


def test_the_report_states_its_rules_and_conclusion():
    text = render_report(evaluate_arms([CONTEXT]))
    assert len(REPORTING_RULES) == 6
    for rule in REPORTING_RULES:
        assert rule in text
    assert "does not rank the arms" in text


def test_a_deterministic_arm_defect_is_reported_as_a_defect_here():
    """Protocol §6: the template can only emit what it was handed."""
    from cardiosentinel.agents.evaluation.protocol import ArmResult, EvaluationReport

    report = EvaluationReport(
        contexts_evaluated=1,
        arms=(ArmResult(arm="deterministic", exercised=True, provider="template"),),
        defects=("deterministic arm fabricated ['0.9']; this is a defect here",),
    )
    text = render_report(report)
    assert "DEFECTS IN THIS REPOSITORY, not findings about generation" in text


def test_both_arms_receive_the_identical_context_object():
    """If the arms saw different inputs, every metric would be uninterpretable."""
    seen = []

    class Recorder:
        name = "recorder"

        def generate(self, brief: str, payload: str) -> str:
            seen.append(payload)
            return claims.SYSTEM_BEHAVIOUR_ONLY

    import json

    evaluate_arms([CONTEXT], provider=Recorder())
    assert len(seen) == 1
    assert json.loads(seen[0]) == json.loads(
        json.dumps(CONTEXT.as_dict(), default=str)
    )


def test_no_context_is_refused_rather_than_scored_as_empty():
    with pytest.raises(ValueError, match="no evidence contexts"):
        evaluate_arms([])
