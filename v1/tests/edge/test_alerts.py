"""The alert layer: contiguous EVENT runs become discrete events."""

from __future__ import annotations

from cardiosentinel.edge.alerts import AlertBuilder
from cardiosentinel.edge.session import EdgeObservation


def observation(state: str, seconds: float, *, before: str = "NORMAL", p=0.5):
    return EdgeObservation(
        stable_id=f"ltstdb:s20041:0:{int(seconds * 250)}:0",
        record_id="s20041",
        subject_id="ltstdb:s2004",
        channel_index=0,
        start_sample=int(seconds * 250),
        elapsed_stream_seconds=seconds,
        score_present=True,
        detector_score=0.8,
        detector_decision=True,
        calibrated_probability=p,
        decision_error_uncertainty=1 - p,
        temporal_evidence=0.6,
        memory_deviation=1.2,
        state_before=before,
        state=state,
        streaks={},
        memory_update_admitted=False,
        gate={},
        contains_filter_warmup=False,
    )


def stream(builder, states):
    """Feed states as a real session would: `state_before` threaded through."""
    emitted = []
    previous = "NORMAL"
    for index, state in enumerate(states):
        alert = builder.observe(observation(state, index * 5.0, before=previous))
        previous = state
        if alert is not None:
            emitted.append(alert)
    return emitted


def test_a_contiguous_event_run_becomes_one_alert():
    builder = AlertBuilder({"t1_policy_id": "qw0.9_qe0.99_FAST"})
    emitted = stream(
        builder,
        ["NORMAL", "WATCH", "EVENT", "EVENT", "EVENT", "RECOVERY", "NORMAL"],
    )

    assert len(emitted) == 1
    alert = emitted[0]
    assert alert.window_count == 3
    assert alert.opened_at_seconds == 10.0
    # closed_at is the LAST WINDOW STILL IN EVENT (20.0), not the RECOVERY
    # window at 25.0 that ended the run. See AlertEvent's timing convention.
    assert alert.closed_at_seconds == 20.0
    assert alert.duration_seconds == 10.0
    assert alert.entered_from == "WATCH"
    assert alert.closed_into == "RECOVERY"
    assert alert.open is False
    assert alert.opened_at == "00:00:10"
    assert alert.provenance["t1_policy_id"] == "qw0.9_qe0.99_FAST"


def test_two_runs_separated_by_recovery_are_two_alerts():
    builder = AlertBuilder()
    emitted = stream(builder, ["EVENT", "EVENT", "NORMAL", "EVENT", "NORMAL"])
    assert len(emitted) == 2
    assert [a.window_count for a in emitted] == [2, 1]


def test_a_run_still_open_at_end_of_stream_is_emitted_not_dropped():
    """A monitor that forgets in-progress episodes is worse than one that says so."""
    builder = AlertBuilder()
    for index, state in enumerate(["NORMAL", "EVENT", "EVENT"]):
        builder.observe(observation(state, index * 5.0))
    assert builder.alerts == ()
    alert = builder.finalize()
    assert alert is not None
    assert alert.open is True
    assert alert.closed_at is None
    assert alert.duration_seconds is None
    assert alert.window_count == 2
    assert len(builder.alerts) == 1


def test_finalize_is_idempotent_and_quiet_when_no_run_is_open():
    builder = AlertBuilder()
    builder.observe(observation("NORMAL", 0.0))
    assert builder.finalize() is None
    assert builder.finalize() is None


def test_peaks_are_taken_over_the_run_and_tolerate_missing_values():
    builder = AlertBuilder()
    builder.observe(observation("EVENT", 0.0, p=0.30))
    builder.observe(observation("EVENT", 5.0, p=0.91))
    builder.observe(observation("EVENT", 10.0, p=0.44))
    alert = builder.finalize()
    assert alert is not None
    assert alert.peak_calibrated_probability == 0.91


def test_the_timing_convention_is_the_last_event_window_not_the_exit_window():
    """Pinning the ambiguous half of the convention."""
    builder = AlertBuilder()
    for index, state in enumerate(["EVENT", "EVENT", "NORMAL"]):
        alert = builder.observe(observation(state, index * 5.0))
    assert alert is not None
    assert alert.opened_at_seconds == 0.0
    assert alert.closed_at_seconds == 5.0, "must be the last EVENT window"
    assert alert.duration_seconds == 5.0
    assert alert.closed_into == "NORMAL"
