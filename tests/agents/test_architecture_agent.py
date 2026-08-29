"""The architecture agent explains selections. It must never recommend."""

from __future__ import annotations

from pathlib import Path

import pytest

from cardiosentinel.agents import claims
from cardiosentinel.agents.architecture import (
    ARCHITECTURE_REGISTRY,
    LIFECYCLE_STAGES,
    ArchitectureQuestionError,
    ArchitectureSelectionAgent,
    find_candidate,
)

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"


def candidate(key: str):
    return next(item for item in ARCHITECTURE_REGISTRY if item.key == key)


def test_every_candidate_has_a_complete_ordered_lifecycle():
    """The ordering is the evidence, not decoration."""
    for item in ARCHITECTURE_REGISTRY:
        stages = [event.stage for event in item.timeline]
        assert stages == list(LIFECYCLE_STAGES), f"{item.key}: {stages}"


def test_every_candidate_declares_both_halves_of_its_boundary():
    for item in ARCHITECTURE_REGISTRY:
        assert item.claims_allowed and item.claims_forbidden, item.key
        assert item.limitations, item.key
        assert (ROOT / item.source_document).is_file(), item.source_document


def test_the_protocol_was_locked_before_the_measurement():
    """Prospectivity is the property that makes a selection meaningful."""
    for item in ARCHITECTURE_REGISTRY:
        stages = [event.stage for event in item.timeline]
        assert stages.index("protocol_locked") < stages.index("measured"), item.key
        assert stages.index("measured") < stages.index("decided"), item.key


@pytest.mark.skipif(
    not (
        DOCS / "experiments" / "u1" / "U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md"
    ).is_file(),
    reason="merged reports absent",
)
def test_the_router_numbers_match_the_retention_decision():
    decision = (
        DOCS / "experiments" / "u1" / "U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md"
    ).read_text(encoding="utf-8")
    observed = candidate("U1-router").observed
    for key in (
        "risk_agreement_absolute_error",
        "escalation_ratio",
        "accepted_sensitivity_at_u_star",
    ):
        assert str(observed[key]) in decision, key
    assert observed["calibration_agreement_guard"] == "PASSED"
    assert observed["asymmetric_abstention_guard"] == "RAISED"
    assert observed["escalation_ratio"] > observed["frozen_limit"]


@pytest.mark.skipif(
    not (DOCS / "experiments" / "t2" / "T2_ARM_COMPARISON_REPORT_V1.md").is_file(),
    reason="merged reports absent",
)
def test_the_s4d_numbers_match_the_merged_report():
    report = (
        DOCS / "experiments" / "t2" / "T2_ARM_COMPARISON_REPORT_V1.md"
    ).read_text(encoding="utf-8")
    observed = candidate("T2-S4D").observed
    assert str(observed["pooled_auprc_difference"]) in report
    low, high = observed["paired_subject_bootstrap_95"]
    assert low < 0 < high and observed["interval_includes_zero"] is True
    assert observed["score_is_calibrated_probability"] is False


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("Why was the selective router rejected?", "U1-router"),
        ("Why was S4D selected?", "T2-S4D"),
        ("Why was the B4-B encoder selected?", "B4-B"),
        ("What happened to B4-C and its SSM block?", "B4-C"),
        ("Why was the GRU arm not selected?", "T2-GRU"),
    ],
)
def test_questions_route_to_the_right_candidate(question, expected):
    assert find_candidate(question).key == expected


def test_an_uncovered_question_is_refused_and_says_it_does_not_recommend():
    with pytest.raises(ArchitectureQuestionError) as caught:
        find_candidate("Which architecture should we use for paediatrics?")
    message = str(caught.value)
    assert "does not recommend" in message


def test_an_ambiguous_question_is_refused():
    with pytest.raises(ArchitectureQuestionError, match="matches 2 candidates"):
        find_candidate("compare b4-a and b4-c")


def test_every_answer_stays_inside_the_claim_boundary():
    agent = ArchitectureSelectionAgent()
    for item in ARCHITECTURE_REGISTRY:
        answer = agent.explain(item.name)
        assert claims.audit(answer, quoting=item.claims_forbidden) == ()
        assert "This evidence does NOT support:" in answer
        assert "Lifecycle:" in answer


def test_the_selected_candidates_never_claim_superiority():
    """The distinction the whole agent exists to preserve."""
    agent = ArchitectureSelectionAgent()
    for key in ("B4-B", "T2-S4D"):
        item = candidate(key)
        answer = agent.explain(item.name)
        assert "Selected" in answer
        assert any("better architecture" in c for c in item.claims_forbidden)


def test_the_router_answer_distinguishes_the_two_guards():
    """One guard passed and a different one failed -- the useful detail."""
    answer = ArchitectureSelectionAgent().explain("selective router")
    assert "PASSED" in answer and "RAISED" in answer
    assert "6.453604523726777" in answer
    assert "uncertainty estimation is ineffective" in answer  # as FORBIDDEN


def test_an_unknown_lifecycle_stage_is_refused():
    from cardiosentinel.agents.architecture import LifecycleEvent

    with pytest.raises(ArchitectureQuestionError, match="Stages are closed"):
        LifecycleEvent("speculated", "x")


def test_keywords_are_discriminative_across_candidates():
    """A keyword shared by two candidates makes both unreachable.

    Found here: "arm" and "longitudinal" described BOTH T2 candidates, so
    "Why was the GRU arm not selected?" tied and was refused. Same defect class
    as the research registry's "selected" collision.
    """
    seen: dict[str, str] = {}
    for item in ARCHITECTURE_REGISTRY:
        for keyword in item.keywords:
            assert keyword not in seen, (
                f"{keyword!r} is shared by {seen.get(keyword)} and {item.key}"
            )
            seen[keyword] = item.key


def test_each_candidate_is_reachable_by_its_own_name():
    agent = ArchitectureSelectionAgent()
    for item in ARCHITECTURE_REGISTRY:
        assert find_candidate(item.name).key == item.key
        agent.explain(item.name)
