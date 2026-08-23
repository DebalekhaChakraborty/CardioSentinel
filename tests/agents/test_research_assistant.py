"""The research assistant, and the verification that keeps its curation honest.

The evidence objects were written by hand from merged reports. Hand-written
numbers drift. These tests re-read the frozen record and compare, so a curated
object that stops matching the evidence fails here rather than in a paper.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from cardiosentinel.agents import claims
from cardiosentinel.agents.research import (
    RESEARCH_REGISTRY,
    ResearchAssistantAgent,
    ResearchQuestionError,
    find_evidence,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DOCS = REPOSITORY_ROOT / "docs"


def topic(name: str):
    return next(item for item in RESEARCH_REGISTRY if item.topic == name)


# -- structure -------------------------------------------------------------


def test_every_object_declares_both_halves_of_its_boundary():
    for item in RESEARCH_REGISTRY:
        assert item.claims_allowed, f"{item.topic} allows nothing"
        assert item.claims_forbidden, f"{item.topic} forbids nothing"
        assert item.source_document.startswith("docs/")
        assert item.keywords, f"{item.topic} is unreachable"


def test_every_cited_source_document_exists():
    for item in RESEARCH_REGISTRY:
        path = REPOSITORY_ROOT / item.source_document
        assert path.is_file(), f"{item.topic} cites a missing {item.source_document}"


def test_topics_are_unique():
    topics = [item.topic for item in RESEARCH_REGISTRY]
    assert len(topics) == len(set(topics))


# -- the values, against the frozen record ---------------------------------


@pytest.mark.skipif(
    not (DOCS / "T2_ARM_COMPARISON_REPORT_V1.md").is_file(),
    reason="merged reports absent",
)
def test_the_t2_numbers_match_the_merged_report():
    report = (DOCS / "T2_ARM_COMPARISON_REPORT_V1.md").read_text(encoding="utf-8")
    basis = topic("t2_s4d_selected").basis
    assert str(basis["pooled_auprc_difference"]) in report
    low, high = basis["paired_subject_bootstrap_95"]
    assert f"[{low}, {high}]" in report or f"{low}" in report
    assert basis["selection_basis"] in report
    assert basis["selected_arm"] in report
    assert basis["interval_includes_zero"] is True and low < 0 < high


@pytest.mark.skipif(
    not (DOCS / "W1_WINDOW_COMPARATOR_REPORT_V1.md").is_file(),
    reason="merged reports absent",
)
def test_the_w1_numbers_match_the_merged_report():
    report = (DOCS / "W1_WINDOW_COMPARATOR_REPORT_V1.md").read_text(encoding="utf-8")
    basis = topic("w1_rq4_answered").basis
    for key in (
        "arm_t1_subject_macro_episode_f1",
        "arm_window_subject_macro_episode_f1",
        "difference",
    ):
        assert str(basis[key]) in report, key
    low, high = basis["paired_subject_bootstrap_95"]
    assert basis["interval_excludes_zero"] is True and low > 0
    assert str(low) in report and str(high) in report


@pytest.mark.skipif(
    not (DOCS / "U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md").is_file(),
    reason="merged reports absent",
)
def test_the_router_rejection_basis_matches_the_retention_decision():
    """The guard that was raised, and the guard that passed."""
    decision = (
        DOCS / "U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md"
    ).read_text(encoding="utf-8")
    basis = topic("u1_router_rejected").basis
    for key in (
        "positive_label_escalation_fraction",
        "negative_label_escalation_fraction",
        "escalation_ratio",
        "u_star_dev",
        "accepted_sensitivity_at_u_star",
        "risk_agreement_absolute_error",
    ):
        assert str(basis[key]) in decision, key
    # The distinction the object exists to preserve.
    assert basis["calibration_agreement_guard"] == "PASSED"
    assert basis["asymmetric_abstention_guard"] == "RAISED"
    assert basis["escalation_ratio"] > basis["frozen_asymmetric_abstention_limit"]


@pytest.mark.skipif(
    not (DOCS / "U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md").is_file(),
    reason="merged reports absent",
)
def test_the_calibration_numbers_match_the_retention_decision():
    decision = (
        DOCS / "U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md"
    ).read_text(encoding="utf-8")
    basis = topic("u1_calibration_retained").basis
    for key in ("platt_nll", "baseline_nll", "platt_brier", "baseline_brier"):
        assert str(basis[key]) in decision, key
    assert basis["platt_nll"] < basis["baseline_nll"]
    assert basis["platt_brier"] < basis["baseline_brier"]


@pytest.mark.skipif(
    not (REPOSITORY_ROOT / "cardiosentinel-runs").exists(),
    reason="evidence tree absent",
)
def test_the_sealed_test_claim_matches_the_tree():
    """The one fact a reviewer will check first."""
    attempts = list(REPOSITORY_ROOT.rglob("TEST_ATTEMPT.json"))
    assert topic("sealed_test_unopened").basis["test_attempt_files_present"] == len(
        attempts
    ) == 0


# -- retrieval and refusal -------------------------------------------------


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("Why was the selective router rejected?", "u1_router_rejected"),
        ("Why was S4D selected instead of GRU?", "t2_s4d_selected"),
        ("Does episode reasoning help?", "w1_rq4_answered"),
        ("Why was the B4-B encoder selected?", "b4b_encoder_selected"),
        ("Why is the sealed test unopened?", "sealed_test_unopened"),
        ("Why was Platt calibration retained?", "u1_calibration_retained"),
    ],
)
def test_questions_route_to_the_right_evidence(question, expected):
    assert find_evidence(question).topic == expected


@pytest.mark.parametrize(
    "question",
    [
        "Will this work on paediatric patients?",
        "What is the five-year survival benefit?",
        "Should we deploy this in an ICU?",
    ],
)
def test_uncovered_questions_are_refused_not_improvised(question):
    """No curated object, no answer. This is the whole design."""
    with pytest.raises(ResearchQuestionError, match="No curated research evidence"):
        find_evidence(question)


def test_the_refusal_names_what_it_does_know():
    with pytest.raises(ResearchQuestionError) as caught:
        find_evidence("what about paediatrics")
    message = str(caught.value)
    assert "does not search documents" in message
    assert "u1_router_rejected" in message


# -- the answer itself -----------------------------------------------------


def test_every_registered_question_answers_within_the_claim_boundary():
    agent = ResearchAssistantAgent()
    for item in RESEARCH_REGISTRY:
        answer = agent.answer(item.question)
        assert item.decision in answer
        assert "This evidence does NOT support:" in answer
        # Guarded with the object's own forbidden list declared as quotation.
        assert claims.audit(answer, quoting=item.claims_forbidden) == ()


def test_the_router_answer_states_the_rejection_without_overclaiming():
    answer = ResearchAssistantAgent().answer("Why was the selective router rejected?")
    assert "evaluated and NOT retained" in answer
    assert "6.453604523726777" in answer
    assert "uncertainty estimation is ineffective" in answer  # as a FORBIDDEN claim
    assert "RQ3 is answered negatively" in answer


def test_the_s4d_answer_refuses_the_superiority_reading():
    answer = ResearchAssistantAgent().answer("Why was S4D selected instead of GRU?")
    assert "predefined selection rule" in answer
    assert "S4D outperforms GRU" in answer  # listed as forbidden
    assert "-0.015229" in answer


def test_quoting_a_forbidden_claim_does_not_blind_the_guard():
    """Declaring a quotation must not let an actual claim through."""
    quoted = ("selective routing is implemented or deployed",)
    smuggled = (
        "selective routing is implemented or deployed. Also the system is "
        "deployment-ready."
    )
    violations = claims.audit(smuggled, quoting=quoted)
    assert any("claim 2" in str(v) for v in violations)


def test_an_ambiguous_question_is_refused_not_guessed():
    """Two topics scoring equally means the keywords are not discriminating.

    Answering from whichever was declared first is how an assistant gives a
    confident answer about the wrong experiment. Found in practice: "Why was
    the B4-B encoder selected?" tied on the generic keyword "selected" and
    routed to the T2 arm comparison.
    """
    with pytest.raises(ResearchQuestionError, match="matches 2 topics equally"):
        find_evidence("Tell me about the s4d encoder")
