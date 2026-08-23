"""The Evidence Agent: deterministic assembly, no inference."""

from __future__ import annotations

from pathlib import Path

import pytest

from cardiosentinel.agents.evidence import GATE_CONDITIONS, EvidenceAgent
from cardiosentinel.edge.alerts import AlertBuilder
from cardiosentinel.edge.session import EdgeObservation

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
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


def observation(state: str, seconds: float, *, before: str, p: float = 0.55):
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
        calibrated_probability=p,
        decision_error_uncertainty=1 - p,
        temporal_evidence=0.72,
        memory_deviation=1.31,
        state_before=before,
        state=state,
        streaks={},
        memory_update_admitted=False,
        gate=dict(GATE),
        contains_filter_warmup=False,
    )


@pytest.fixture
def alert_and_observations():
    builder = AlertBuilder(PROVENANCE)
    states = ["NORMAL", "WATCH", "EVENT", "EVENT", "EVENT", "RECOVERY"]
    observations, previous, alert = [], "NORMAL", None
    for index, state in enumerate(states):
        item = observation(state, index * 5.0, before=previous)
        previous = state
        observations.append(item)
        emitted = builder.observe(item)
        if emitted is not None:
            alert = emitted
    assert alert is not None
    return alert, observations


def test_the_record_carries_the_alert_identity(alert_and_observations):
    alert, observations = alert_and_observations
    record = EvidenceAgent(PROVENANCE).explain(alert, observations, index=7)
    assert record.alert_id == "EVT-s20041-0007"
    assert record.decision == "EVENT"
    assert record.entered_from == "WATCH"
    assert record.closed_into == "RECOVERY"
    assert record.window_count == 3


def test_all_six_gate_conditions_are_explained(alert_and_observations):
    alert, observations = alert_and_observations
    record = EvidenceAgent(PROVENANCE).explain(alert, observations)
    assert len(record.gate) == len(GATE_CONDITIONS) == 6
    status = {item.condition: item.status for item in record.gate}
    assert status == {
        "G1": "PASS",
        "G2": "PASS",
        "G3": "PASS",
        "G4": "BLOCK",
        "G5": "BLOCK",
        "G6": "PASS",
    }
    assert all(item.meaning for item in record.gate)


def test_memory_context_uses_recorded_counts_not_an_invented_similarity(
    alert_and_observations,
):
    """`past_observed_count` is a real counter. 'Historical similarity' is not."""
    alert, observations = alert_and_observations
    record = EvidenceAgent(PROVENANCE).explain(alert, observations)
    assert record.memory_windows_observed == 203
    assert record.memory_updates_admitted == 0


def test_no_calibrated_confidence_band_is_emitted(alert_and_observations):
    """The component that would have supplied one was rejected."""
    alert, observations = alert_and_observations
    agent = EvidenceAgent(PROVENANCE)
    record = agent.explain(alert, observations)
    assert record.decision_error_uncertainty == pytest.approx(0.45)
    rendered = agent.render(record)
    assert "confidence" not in rendered.lower().split("calibrated confidence")[0]
    assert "a calibrated confidence" in rendered


def test_render_passes_the_claim_boundary(alert_and_observations):
    """The agent guards its own output."""
    alert, observations = alert_and_observations
    agent = EvidenceAgent(PROVENANCE)
    rendered = agent.render(agent.explain(alert, observations))
    from cardiosentinel.agents import claims

    assert claims.find_violations(claims.strip_approved_disclaimers(rendered)) == ()
    assert "does not establish" in rendered


def test_render_names_the_frozen_provenance(alert_and_observations):
    alert, observations = alert_and_observations
    agent = EvidenceAgent(PROVENANCE)
    rendered = agent.render(agent.explain(alert, observations))
    for expected in (
        "B4BTransformerCNN",
        "M2-G",
        "CausalS4DLongitudinal",
        "qw0.9_qe0.99_FAST",
        "unopened",
    ):
        assert expected in rendered


def test_s_t_is_labelled_as_a_bounded_score_not_a_probability(
    alert_and_observations,
):
    alert, observations = alert_and_observations
    agent = EvidenceAgent(PROVENANCE)
    rendered = agent.render(agent.explain(alert, observations))
    assert "bounded score, not a probability" in rendered


def test_an_open_run_is_explained_as_open():
    builder = AlertBuilder(PROVENANCE)
    previous = "NORMAL"
    observations = []
    for index, state in enumerate(["WATCH", "EVENT", "EVENT"]):
        item = observation(state, index * 5.0, before=previous)
        previous = state
        observations.append(item)
        builder.observe(item)
    alert = builder.finalize()
    assert alert is not None
    agent = EvidenceAgent(PROVENANCE)
    record = agent.explain(alert, observations)
    assert record.still_open is True
    assert record.duration_seconds is None
    assert "still open at end of stream" in agent.render(record)
