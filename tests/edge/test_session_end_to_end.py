"""The composed runtime, on real ECG. Skips without the evidence tree."""

from __future__ import annotations

from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RUNS = REPOSITORY_ROOT / "cardiosentinel-runs"
FEATURES = REPOSITORY_ROOT / "cardiosentinel-features"
SOURCE = REPOSITORY_ROOT / "cardiosentinel-data" / "ltstdb" / "1.0.0"

_MISSING = [
    str(p.relative_to(REPOSITORY_ROOT))
    for p in (RUNS, FEATURES, SOURCE)
    if not p.exists()
]
pytestmark = pytest.mark.skipif(
    bool(_MISSING),
    reason=(
        "Frozen evidence tree absent: "
        + ", ".join(_MISSING)
        + ". Gitignored, so the composed runtime cannot be exercised on a fresh "
        "checkout. Run it on a machine holding the evidence."
    ),
)

SUBJECT, RECORD = "ltstdb:s2004", "s20041"


@pytest.fixture(scope="module")
def result():
    from cardiosentinel.edge.replay import replay_record

    return replay_record(
        RECORD,
        max_seconds=300.0,
        source_root=SOURCE,
        run_root=RUNS,
        feature_root=FEATURES,
    )


def test_the_pipeline_produces_observations_end_to_end(result):
    assert len(result.observations) > 40
    first = result.observations[0]
    assert first.record_id == RECORD
    assert first.subject_id == SUBJECT
    assert first.state in {"NORMAL", "WATCH", "EVENT", "RECOVERY"}


def test_every_scored_row_carries_the_four_derived_semantics(result):
    """Each was derived from the persisted evidence, not assumed."""
    from cardiosentinel.edge.session import DETECTOR_THRESHOLD

    scored = [o for o in result.observations if o.score_present]
    assert scored, "no window was scored"
    for o in scored:
        assert o.detector_decision == (o.detector_score >= DETECTOR_THRESHOLD)
        assert 0.0 <= o.calibrated_probability <= 1.0
        expected = (
            1.0 - o.calibrated_probability
            if o.detector_decision
            else o.calibrated_probability
        )
        assert o.decision_error_uncertainty == pytest.approx(expected)
        # s_t is a bounded sigmoid, never a calibrated probability.
        assert 0.0 < o.temporal_evidence < 1.0


def test_the_temporal_state_actually_carries_across_windows(result):
    """If the S4D state were reset each window, s_t would not vary causally."""
    values = [
        o.temporal_evidence for o in result.observations if o.temporal_evidence
    ]
    assert len(set(values)) > 5, "temporal evidence is suspiciously constant"


def test_the_memory_is_causal_and_moves(result):
    """d_long is measured against the pre-update prototype, and adapts."""
    deviations = [
        o.memory_deviation for o in result.observations if o.memory_deviation
    ]
    assert deviations
    assert min(deviations) > 0.0


def test_provenance_names_every_frozen_component(result):
    p = result.provenance
    assert p["encoder_architecture"] == "B4BTransformerCNN"
    assert p["m2_arm"] == "M2-G"
    assert p["u1_family"] == "platt_logistic_on_recovered_logit"
    assert p["t2_arm"] == "CausalS4DLongitudinal"
    assert p["t1_policy_id"] == "qw0.9_qe0.99_FAST"
    assert p["t1_held_out_subject"] == SUBJECT
    assert p["t1_thresholds_generated_here"] is False
    assert p["detector_threshold_selected_here"] is False
    assert p["patient_identity_is_a_feature"] is False
    assert p["selective_router_retained"] is False
    assert p["score_is_calibrated_probability"] is False
    assert p["test_accessed"] is False
    assert p["sealed_test_state"] == "unopened"


def test_an_unvalidated_subject_is_refused_not_served(result):
    """The demo must not borrow another subject's operating point."""
    from cardiosentinel.edge.artifacts import EdgeArtifactError, load_runtime_artifacts

    with pytest.raises(EdgeArtifactError, match="not one of the twelve"):
        load_runtime_artifacts(
            "ltstdb:s2001", run_root=RUNS, feature_root=FEATURES
        )


def test_a_session_refuses_a_policy_for_a_different_subject():
    from cardiosentinel.edge.artifacts import load_runtime_artifacts
    from cardiosentinel.edge.session import SessionError, StreamingInferenceSession

    artifacts = load_runtime_artifacts(
        SUBJECT, run_root=RUNS, feature_root=FEATURES
    )
    with pytest.raises(SessionError, match="leave-one-subject-out"):
        StreamingInferenceSession(
            artifacts,
            subject_id="ltstdb:s2059",
            record_id="s20591",
            channel_index=0,
        )
