"""The explanation agent: mode always declared, fallback never silent."""

from __future__ import annotations

import pytest

from cardiosentinel.agents import claims
from cardiosentinel.agents.context import build_context
from cardiosentinel.agents.evidence import EvidenceAgent
from cardiosentinel.agents.explain import (
    DETERMINISTIC,
    GENERATIVE,
    SYSTEM_BRIEF,
    PatientExplanationAgent,
    TemplateRenderer,
)
from cardiosentinel.agents.graph import build_evidence_graph
from cardiosentinel.edge.alerts import AlertBuilder
from cardiosentinel.edge.session import EdgeObservation

PROVENANCE = {
    "encoder_architecture": "B4BTransformerCNN",
    "m2_arm": "M2-G",
    "u1_family": "platt_logistic_on_recovered_logit",
    "t2_arm": "CausalS4DLongitudinal",
    "t1_policy_id": "qw0.9_qe0.99_FAST",
    "t1_held_out_subject": "ltstdb:s2004",
    "detector_threshold": 0.7554003000259399,
    "sealed_test_state": "unopened",
}
GATE = {
    "g1_available": True,
    "g2_finite_representation": True,
    "g3_sqi_admissible": True,
    "g4_normal_evidence": False,
    "g5_not_in_refractory": False,
    "g6_morphology_computable": True,
    "past_observed_count_before": 203,
    "past_update_count_before": 0,
}


class Stub:
    """A provider whose behaviour the test chooses."""

    name = "stub"

    def __init__(self, *, text: str = "", error: Exception | None = None) -> None:
        self._text = text
        self._error = error

    def generate(self, brief: str, payload: str) -> str:
        if self._error is not None:
            raise self._error
        return self._text


def _observation(state: str, seconds: float, before: str):
    return EdgeObservation(
        stable_id=f"ltstdb:s20041:0:{int(seconds * 250)}:0",
        record_id="s20041",
        subject_id="ltstdb:s2004",
        channel_index=0,
        start_sample=int(seconds * 250),
        elapsed_stream_seconds=seconds,
        score_present=True,
        detector_score=0.81,
        detector_decision=True,
        calibrated_probability=0.55,
        decision_error_uncertainty=0.45,
        temporal_evidence=0.95,
        memory_deviation=1.41,
        state_before=before,
        state=state,
        streaks={},
        memory_update_admitted=False,
        gate=dict(GATE),
        contains_filter_warmup=False,
    )


@pytest.fixture
def graph(tmp_path):
    builder = AlertBuilder(PROVENANCE)
    observations, previous, alert = [], "NORMAL", None
    for index, state in enumerate(["NORMAL", "WATCH", "EVENT", "EVENT", "NORMAL"]):
        item = _observation(state, index * 5.0, previous)
        previous = state
        observations.append(item)
        emitted = builder.observe(item)
        if emitted is not None:
            alert = emitted
    assert alert is not None
    record = EvidenceAgent(PROVENANCE).explain(alert, observations)
    return build_evidence_graph(record, run_root=tmp_path)


# -- the context the generator is allowed to see ---------------------------


def test_the_context_is_four_closed_sections(graph):
    context = build_context(graph).as_dict()
    assert set(context) == {"event", "evidence", "safety", "limitations", "provenance"}


def test_the_context_carries_no_research_prose(graph):
    """No handbook, no reports, no free-text smuggling channel."""
    import json

    blob = json.dumps(build_context(graph).as_dict()).lower()
    for leaked in ("handbook", "appendix", "auprc", "bootstrap", "s4d outperform"):
        assert leaked not in blob


def test_the_context_names_the_bounded_score_as_not_a_probability(graph):
    evidence = build_context(graph).evidence
    assert evidence["temporal_support_is_a_probability"] is False
    assert "temporal_support_bounded_score" in evidence


def test_the_safety_section_explains_a_blocked_update(graph):
    safety = build_context(graph).safety
    assert safety["learning_blocked"] is True
    assert set(safety["blocked_by"]) == {"G4", "G5"}
    assert safety["reasons"]
    assert "contamination control working" in safety["note"]


def test_the_limitations_travel_with_the_evidence(graph):
    assert len(build_context(graph).limitations) >= 5


# -- mode, and the four ways to fall back ----------------------------------


def test_no_provider_falls_back_and_says_so(graph):
    result = PatientExplanationAgent(None).explain(graph)
    assert result.explanation_mode == DETERMINISTIC
    assert result.fallback_reason == "no provider configured"
    assert result.provider == "template"
    assert result.text


def test_a_failing_provider_falls_back_and_names_the_failure(graph):
    agent = PatientExplanationAgent(Stub(error=TimeoutError("upstream timeout")))
    result = agent.explain(graph)
    assert result.explanation_mode == DETERMINISTIC
    assert "TimeoutError" in result.fallback_reason


def test_an_empty_response_falls_back(graph):
    result = PatientExplanationAgent(Stub(text="   ")).explain(graph)
    assert result.explanation_mode == DETERMINISTIC
    assert "returned nothing" in result.fallback_reason


def test_generated_text_that_breaks_the_boundary_falls_back_and_records_why(graph):
    """The interesting case: the model spoke, and what it said was not allowed."""
    agent = PatientExplanationAgent(
        Stub(text="The patient has ischemia; this is deployment-ready and "
                  "generalizes to other hospitals.")
    )
    result = agent.explain(graph)
    assert result.explanation_mode == DETERMINISTIC
    assert "claim boundary" in result.fallback_reason
    assert result.claim_violations
    assert any("claim 2" in v or "claim 3" in v for v in result.claim_violations)
    # The demo still produced a usable explanation.
    assert claims.SYSTEM_BEHAVIOUR_ONLY in result.text


def test_compliant_generated_text_is_returned_as_generative(graph):
    compliant = (
        "The monitor held an EVENT state for a period while temporal support "
        "rose, and declined to update the stored baseline during it. "
        f"{claims.SYSTEM_BEHAVIOUR_ONLY}"
    )
    result = PatientExplanationAgent(Stub(text=compliant)).explain(graph)
    assert result.explanation_mode == GENERATIVE
    assert result.provider == "stub"
    assert result.fallback_reason is None
    assert result.text == compliant


def test_every_explanation_declares_its_mode(graph):
    for provider in (None, Stub(text=""), Stub(error=RuntimeError("x"))):
        result = PatientExplanationAgent(provider).explain(graph)
        payload = result.as_dict()
        assert payload["explanation_mode"] in {GENERATIVE, DETERMINISTIC}
        assert payload["context_source"] == "EVIDENCE_GRAPH"


# -- the deterministic renderer itself -------------------------------------


def test_the_template_output_passes_the_claim_boundary(graph):
    text = TemplateRenderer().render(build_context(graph))
    stripped = claims.strip_approved_disclaimers(text)
    assert claims.find_violations(stripped) == ()


def test_the_template_uses_the_canonical_disclaimer_verbatim(graph):
    text = TemplateRenderer().render(build_context(graph))
    assert text.endswith(claims.SYSTEM_BEHAVIOUR_ONLY)


def test_the_brief_demands_the_exact_disclaimer(graph):
    """A model that rewords it trips the guard and we fall back -- by design."""
    assert claims.SYSTEM_BEHAVIOUR_ONLY in SYSTEM_BRIEF
    assert "copied EXACTLY" in SYSTEM_BRIEF


def test_the_template_reports_a_blocked_update_as_a_control_not_a_fault(graph):
    text = TemplateRenderer().render(build_context(graph))
    assert "declined to update" in text
    assert "behaving as designed" in text


def test_the_two_paths_agree_on_what_compliant_text_is():
    """Regression: the generative check once rejected a compliant disclaimer.

    `enforce` stripped registered disclaimers; the generative path did not, so
    a model that ended with the exact sentence its brief demanded was rejected
    for obeying. Both now route through `claims.audit`.
    """
    text = f"The monitor held an EVENT state. {claims.SYSTEM_BEHAVIOUR_ONLY}"
    assert claims.audit(text) == ()
    assert claims.enforce(text) == text
    assert claims.find_violations(text), (
        "raw matching still flags it, which is why audit() exists"
    )
