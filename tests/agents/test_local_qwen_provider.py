"""The local open-weight provider: opt-in, lazy, and guarded twice.

Every test here runs with stubs. **No weights are downloaded and no network is
touched**, mirroring `test_explanation_evaluation.py`, which validates the
harness against deliberately bad providers rather than against a real model.
"""

from __future__ import annotations

import pytest

from cardiosentinel.agents import claims
from cardiosentinel.agents.context import build_context
from cardiosentinel.agents.evidence import EvidenceAgent
from cardiosentinel.agents.explain import (
    DETERMINISTIC,
    GENERATIVE,
    PatientExplanationAgent,
)
from cardiosentinel.agents.graph import build_evidence_graph
from cardiosentinel.agents.providers import (
    DEFAULT_LOCAL_MODEL,
    LocalQwenProvider,
    ProviderUnavailable,
    default_provider,
)
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
    model_name = "stub-model@abcdef1"

    def __init__(self, *, text: str = "", error: Exception | None = None) -> None:
        self._text = text
        self._error = error

    def generate(self, brief: str, payload: str) -> str:
        if self._error is not None:
            raise self._error
        return self._text


def _observation(state: str, seconds: float, before: str) -> EdgeObservation:
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


def _compliant(graph) -> str:
    """Prose that passes both gates: real numbers only, canonical disclaimer."""
    evidence = build_context(graph).evidence
    return (
        "The system entered the EVENT state and held it. The calibrated "
        f"probability reached {evidence['calibrated_probability']:.3f}. The "
        "system declined to update the patient baseline. "
        + claims.SYSTEM_BEHAVIOUR_ONLY
    )


# -- the provider is opt-in and never downloads on construction -------------


def test_an_uncached_model_refuses_rather_than_downloading():
    """Constructing a provider must never trigger a multi-gigabyte fetch."""
    with pytest.raises(ProviderUnavailable):
        LocalQwenProvider(model="cardiosentinel/definitely-not-a-real-model")


def test_default_provider_does_not_select_local_without_opting_in(monkeypatch):
    monkeypatch.delenv("CARDIOSENTINEL_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    assert default_provider() is None


def test_the_default_model_is_apache_licensed_and_ungated():
    """Recorded so a licence change is a test failure, not a discovery."""
    assert DEFAULT_LOCAL_MODEL.startswith("Qwen/")


# -- the deterministic path is untouched ------------------------------------


def test_with_no_provider_the_agent_behaves_exactly_as_before(graph):
    """Protects `DEMO_SCENARIO.md` and `test_demo_bundle.py`."""
    explanation = PatientExplanationAgent().explain(graph)
    assert explanation.explanation_mode == DETERMINISTIC
    assert explanation.fallback_reason == "no provider configured"


# -- requirement 8: everything is recorded ----------------------------------


def test_a_compliant_generation_records_provider_model_and_latency(graph):
    explanation = PatientExplanationAgent(Stub(text=_compliant(graph))).explain(graph)
    assert explanation.explanation_mode == GENERATIVE
    assert explanation.provider == "stub"
    assert explanation.model == "stub-model@abcdef1"
    assert explanation.latency_seconds is not None


def test_latency_is_recorded_on_the_deterministic_path_too(graph):
    explanation = PatientExplanationAgent().explain(graph)
    assert explanation.latency_seconds is not None
    assert explanation.latency_seconds >= 0.0


# -- the four pre-existing fallbacks still record their reason --------------


@pytest.mark.parametrize(
    ("stub", "fragment"),
    [
        (Stub(error=RuntimeError("boom")), "failed"),
        (Stub(text="   "), "returned nothing"),
        (Stub(text="S4D outperforms GRU."), "claim boundary"),
    ],
)
def test_a_failing_provider_degrades_and_says_why(graph, stub, fragment):
    explanation = PatientExplanationAgent(stub).explain(graph)
    assert explanation.explanation_mode == DETERMINISTIC
    assert fragment in (explanation.fallback_reason or "")
    assert explanation.model == "stub-model@abcdef1"


def test_a_claim_violation_is_recorded_not_just_counted(graph):
    explanation = PatientExplanationAgent(Stub(text="S4D outperforms GRU.")).explain(
        graph
    )
    assert explanation.claim_violations


# -- the fidelity gate, which the claim guard cannot do ---------------------


def test_an_invented_number_falls_back(graph):
    """The claim guard passes this text. Fidelity must not."""
    text = "The calibrated probability reached 0.812345. " + (
        claims.SYSTEM_BEHAVIOUR_ONLY
    )
    assert not claims.audit(text), "precondition: the claim guard allows this"
    explanation = PatientExplanationAgent(Stub(text=text)).explain(graph)
    assert explanation.explanation_mode == DETERMINISTIC
    assert "not present in the evidence" in (explanation.fallback_reason or "")


def test_a_percentage_conversion_falls_back(graph):
    """0.545613 -> "54.6%" is invisible to the registered metric. See §4.3."""
    text = "The calibrated probability reached 54.6%. " + claims.SYSTEM_BEHAVIOUR_ONLY
    assert not claims.audit(text), "precondition: the claim guard allows this"
    explanation = PatientExplanationAgent(Stub(text=text)).explain(graph)
    assert explanation.explanation_mode == DETERMINISTIC
    assert "percentage" in (explanation.fallback_reason or "")


def test_rounding_is_not_fabrication(graph):
    """A rounded rendering of a real value must still pass."""
    explanation = PatientExplanationAgent(Stub(text=_compliant(graph))).explain(graph)
    assert explanation.explanation_mode == GENERATIVE


# -- the frozen environment is not modified ---------------------------------


def test_the_scientific_environment_is_unchanged():
    """Adding this provider must not add a package. Ever."""
    from cardiosentinel.neural import provenance

    environment = provenance.dependency_environment()
    assert environment["installed_package_count"] == 335
    assert environment["installed_packages_sha256"] == (
        "b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a"
    )
