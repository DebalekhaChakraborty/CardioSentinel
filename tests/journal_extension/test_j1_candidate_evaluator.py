"""Qualification of the J1 candidate evaluator.

NON-SCIENTIFIC QUALIFICATION FIXTURE. Every row, threshold and reference
episode below is fabricated. No physiological data, annotation or
reference-episode count is read, no fold is built, and nothing here authorizes
or executes J1.
"""

from __future__ import annotations

import itertools

import pytest

from cardiosentinel.journal_extension.j1.candidates import (
    MemorylessCandidate,
    StatefulCandidate,
    memoryless_registry,
)
from cardiosentinel.journal_extension.j1.evaluation import (
    EPISODE_STATES,
    INITIAL_STATE,
    EvaluationError,
    J1CandidateEvaluator,
    StatefulThresholds,
    Streaks,
    SubjectTimeline,
    is_event_evidence,
    next_episode_state,
    run_memoryless_rule,
    run_stateful_policy,
)
from cardiosentinel.journal_extension.j1.rows import ArmNeutralRow
from cardiosentinel.journal_extension.j1.selection import sort_key

THRESHOLDS = StatefulThresholds(
    p_watch=0.40, s_watch=0.35, p_event=0.70, s_event=0.60
)
W_THRESHOLDS = {"pt": 0.70, "st": 0.60, "m2g": 0.50}


def _row(
    index: int,
    *,
    p: float = 0.1,
    s: float = 0.1,
    d: bool = False,
    m2g: float = 0.1,
    present: bool = True,
    elapsed: float = 1000.0,
) -> ArmNeutralRow:
    return ArmNeutralRow(
        stable_id=f"r{index:04d}",
        m2g_detector_score=m2g,
        detector_decision_d_t=d,
        oof_calibrated_probability_p_t=p,
        decision_error_uncertainty_u_t=1.0 - p if d else p,
        s4d_temporal_evidence_s_t=s,
        score_present=present,
        elapsed_stream_seconds=elapsed,
    )


# -- the re-stated state machine, against the inherited one -----------------


def _inherited():
    """`t1_protocol` is imported by the test, never by a J1 module: its
    operating-point entry points are forbidden to J1 by name."""
    from cardiosentinel.neural import t1_protocol

    return t1_protocol


def _as_t1_row(row: ArmNeutralRow):
    t1 = _inherited()
    return t1.T1Row(
        stable_id=row.stable_id,
        score_present=row.score_present,
        detector_decision=row.detector_decision_d_t,
        calibrated_probability=row.oof_calibrated_probability_p_t,
        decision_error_uncertainty=row.decision_error_uncertainty_u_t,
        temporal_evidence=row.s4d_temporal_evidence_s_t,
        elapsed_stream_seconds=row.elapsed_stream_seconds,
    )


def _row_grid() -> list[ArmNeutralRow]:
    grid = []
    index = 0
    for p, s, d, present, elapsed in itertools.product(
        (0.10, 0.45, 0.75, 0.95),
        (0.10, 0.38, 0.65),
        (False, True),
        (True, False),
        (10.0, 900.0),
    ):
        grid.append(
            _row(index, p=p, s=s, d=d, present=present, elapsed=elapsed)
        )
        index += 1
    return grid


def test_the_restated_transition_matches_the_inherited_one() -> None:
    """The re-statement is only honest if it agrees everywhere both are defined.

    `next_state` is a forbidden entry point for J1 modules, so the semantics
    are re-stated inside J1 and pinned here across every state, profile,
    streak shape and row the grid produces.
    """
    t1 = _inherited()
    thresholds = t1.T1Thresholds(*THRESHOLDS)
    streak_shapes = (
        Streaks(),
        Streaks(event_confirm=1),
        Streaks(event_confirm=5),
        Streaks(watch_clear=2),
        Streaks(event_release=2),
        Streaks(re_event_confirm=1),
        Streaks(recovery_clear=5),
    )
    compared = 0
    for state in EPISODE_STATES:
        for profile in t1.T1_PERSISTENCE_PROFILES:
            for streaks in streak_shapes:
                for row in _row_grid():
                    mine = next_episode_state(
                        state, streaks, row, THRESHOLDS, profile
                    )
                    theirs = t1.next_state(
                        state,
                        t1.T1Streaks(*streaks),
                        _as_t1_row(row),
                        thresholds,
                        profile,
                    )
                    assert mine[0] == theirs[0], (state, profile.name, row)
                    assert tuple(mine[1]) == tuple(theirs[1]), (
                        state,
                        profile.name,
                        row,
                    )
                    compared += 1
    assert compared > 3000, "the equivalence sweep must actually be a sweep"


def test_the_cold_start_relaxation_is_retained_not_invented() -> None:
    """Section 2.1's prose is the mature form; the retained rule relaxes S4D."""
    t1 = _inherited()
    thresholds = t1.T1Thresholds(*THRESHOLDS)
    cold = _row(1, p=0.9, s=0.0, d=True, elapsed=10.0)
    mature = _row(2, p=0.9, s=0.0, d=True, elapsed=900.0)
    assert is_event_evidence(cold, THRESHOLDS) is True
    assert is_event_evidence(mature, THRESHOLDS) is False
    for row in (cold, mature):
        assert is_event_evidence(row, THRESHOLDS) == t1.is_event_evidence(
            _as_t1_row(row), thresholds
        )


def test_an_unavailable_row_holds_state_and_resets_every_streak() -> None:
    """A gap must not confirm an escalation or a release across itself."""
    held, streaks = next_episode_state(
        "WATCH",
        Streaks(event_confirm=4, watch_clear=3),
        _row(1, present=False),
        THRESHOLDS,
        _inherited().T1_PROFILE_FAST,
    )
    assert held == "WATCH"
    assert streaks == Streaks()


def test_every_stream_starts_in_normal() -> None:
    quiet = [_row(i) for i in range(4)]
    assert run_stateful_policy(
        quiet, THRESHOLDS, _inherited().T1_PROFILE_FAST
    )[0] == INITIAL_STATE
    assert INITIAL_STATE == "NORMAL"


def test_state_does_not_cross_a_stream_boundary() -> None:
    """Two streams evaluated separately cannot inherit each other's state."""
    profile = _inherited().T1_PROFILE_FAST
    escalating = [_row(i, p=0.9, s=0.9, d=True) for i in range(6)]
    quiet = [_row(i) for i in range(6)]
    assert run_stateful_policy(escalating, THRESHOLDS, profile)[-1] == "EVENT"
    assert run_stateful_policy(quiet, THRESHOLDS, profile) == ("NORMAL",) * 6


# -- the memoryless arm carries no state ------------------------------------


def test_the_memoryless_arm_is_a_pure_function_of_its_row() -> None:
    """Section 2.2: no counter, timer, run-length, hysteresis or window."""
    candidate = MemorylessCandidate("A", ("pt",), (0.9,))
    rows = [_row(i, p=p) for i, p in enumerate([0.9, 0.1, 0.9, 0.1, 0.95])]
    forward = run_memoryless_rule(rows, candidate, W_THRESHOLDS)
    shuffled = [rows[i] for i in (4, 0, 3, 1, 2)]
    reshuffled = run_memoryless_rule(shuffled, candidate, W_THRESHOLDS)
    assert reshuffled == tuple(forward[i] for i in (4, 0, 3, 1, 2))


def test_an_unavailable_row_is_not_decided_positive() -> None:
    """Neither arm may manufacture evidence for a row that has none."""
    candidate = MemorylessCandidate("A", ("pt",), (0.9,))
    rows = [_row(0, p=0.99, present=False)]
    assert run_memoryless_rule(rows, candidate, W_THRESHOLDS) == (False,)


def test_every_memoryless_candidate_runs() -> None:
    rows = [_row(i, p=0.8, s=0.7, d=i % 2 == 0, m2g=0.6) for i in range(12)]
    for candidate in memoryless_registry():
        decisions = run_memoryless_rule(rows, candidate, W_THRESHOLDS)
        assert len(decisions) == len(rows)


# -- the fold evaluator and its population boundary -------------------------


def _timeline(subject: str, stream: int, pattern: str) -> SubjectTimeline:
    """`pattern` uses `.` for quiet and `X` for full escalating evidence."""
    rows = []
    positives = []
    for index, mark in enumerate(pattern):
        hot = mark == "X"
        rows.append(
            _row(index, p=0.9 if hot else 0.05, s=0.9 if hot else 0.05, d=hot)
        )
        positives.append(hot)
    return SubjectTimeline(
        subject_id=subject,
        stream_key=("rec", stream),
        rows=tuple(rows),
        start_samples=tuple(1250 * i for i in range(len(pattern))),
        primary_row=tuple(True for _ in pattern),
        primary_positive=tuple(positives),
    )


CANDIDATE = StatefulCandidate(q_watch=0.90, q_event=0.99, profile="FAST")
S_THRESHOLDS = {"p_watch": 0.40, "s_watch": 0.35, "p_event": 0.70, "s_event": 0.60}


def test_a_subject_outside_the_held_out_population_is_refused() -> None:
    """A candidate is never applied to the population its thresholds came from."""
    evaluator = J1CandidateEvaluator()
    with pytest.raises(EvaluationError, match="not in the held-out population"):
        evaluator.evaluate_inner(
            CANDIDATE,
            thresholds=S_THRESHOLDS,
            timelines=[_timeline("s99", 0, "....XXXX....")],
            inner_heldout_subjects=["s01", "s02"],
        )


def test_a_stream_may_be_evaluated_only_once() -> None:
    evaluator = J1CandidateEvaluator()
    timeline = _timeline("s01", 0, "....XXXX....")
    with pytest.raises(EvaluationError, match="appears twice"):
        evaluator.evaluate_inner(
            CANDIDATE,
            thresholds=S_THRESHOLDS,
            timelines=[timeline, timeline],
            inner_heldout_subjects=["s01"],
        )


def test_an_evaluation_needs_an_explicit_held_out_population() -> None:
    evaluator = J1CandidateEvaluator()
    with pytest.raises(EvaluationError, match="explicit held-out population"):
        evaluator.evaluate_inner(
            CANDIDATE,
            thresholds=S_THRESHOLDS,
            timelines=[_timeline("s01", 0, "....XXXX....")],
            inner_heldout_subjects=[],
        )


def test_a_subject_streams_are_summed_not_averaged() -> None:
    evaluator = J1CandidateEvaluator()
    result = evaluator.evaluate_inner(
        CANDIDATE,
        thresholds=S_THRESHOLDS,
        timelines=[
            _timeline("s01", 0, "....XXXXXX...."),
            _timeline("s01", 1, "....XXXXXX...."),
        ],
        inner_heldout_subjects=["s01"],
    )
    subject = result.per_subject["s01"]
    assert subject.reference_episodes == 2
    assert subject.position_count == 28


def test_a_detected_episode_is_matched_and_scores_a_defined_f1() -> None:
    evaluator = J1CandidateEvaluator()
    result = evaluator.evaluate_inner(
        CANDIDATE,
        thresholds=S_THRESHOLDS,
        timelines=[_timeline("s01", 0, "....XXXXXXXX....")],
        inner_heldout_subjects=["s01"],
    )
    subject = result.per_subject["s01"]
    assert subject.reference_episodes == 1
    assert subject.matched_episodes == 1
    assert subject.primary_f1_eligible is True
    assert subject.episode_f1 is not None and subject.episode_f1 > 0.0


def test_a_zero_reference_subject_is_not_primary_f1_eligible() -> None:
    """Eligibility depends on reference truth alone, never on arm output."""
    evaluator = J1CandidateEvaluator()
    result = evaluator.evaluate_inner(
        CANDIDATE,
        thresholds=S_THRESHOLDS,
        timelines=[_timeline("s02", 0, "............")],
        inner_heldout_subjects=["s02"],
    )
    assert result.per_subject["s02"].primary_f1_eligible is False


def test_selection_metrics_feed_the_frozen_selection_order() -> None:
    evaluator = J1CandidateEvaluator()
    result = evaluator.evaluate_inner(
        CANDIDATE,
        thresholds=S_THRESHOLDS,
        timelines=[
            _timeline("s01", 0, "....XXXXXXXX...."),
            _timeline("s02", 0, "..XXXX......"),
        ],
        inner_heldout_subjects=["s01", "s02"],
    )
    metrics = result.selection_metrics()
    assert sorted(metrics) == [
        "episode_f1",
        "event_exposure_fraction",
        "false_onsets_per_hour",
        "window_mcc",
    ]
    assert sort_key(CANDIDATE, metrics)


def test_the_exposure_fraction_matches_the_inherited_definition() -> None:
    """Stated as a count here because J1-W emits decisions, not states."""
    from cardiosentinel.neural.t1_development_run import event_exposure_fraction

    profile = _inherited().T1_PROFILE_FAST
    timeline = _timeline("s01", 0, "....XXXXXXXX....")
    emitted = run_stateful_policy(timeline.rows, THRESHOLDS, profile)
    inherited = event_exposure_fraction(emitted)

    result = J1CandidateEvaluator().evaluate_inner(
        CANDIDATE,
        thresholds=S_THRESHOLDS,
        timelines=[timeline],
        inner_heldout_subjects=["s01"],
    )
    assert result.selection_metrics()["event_exposure_fraction"] == inherited


def test_a_population_with_no_eligible_subject_refuses_rather_than_imputes() -> None:
    result = J1CandidateEvaluator().evaluate_inner(
        CANDIDATE,
        thresholds=S_THRESHOLDS,
        timelines=[_timeline("s02", 0, "............")],
        inner_heldout_subjects=["s02"],
    )
    with pytest.raises(EvaluationError, match="never imputed"):
        result.selection_metrics()


def test_outer_evaluation_holds_the_same_boundary() -> None:
    evaluator = J1CandidateEvaluator()
    with pytest.raises(EvaluationError, match="not in the held-out population"):
        evaluator.evaluate_outer(
            CANDIDATE,
            thresholds=S_THRESHOLDS,
            timelines=[_timeline("s07", 0, "..XXXX......")],
            outer_assessment_subjects=["s08"],
        )


def test_both_arms_evaluate_the_same_timeline() -> None:
    evaluator = J1CandidateEvaluator()
    timelines = [_timeline("s01", 0, "....XXXXXXXX....")]
    stateful = evaluator.evaluate_inner(
        CANDIDATE,
        thresholds=S_THRESHOLDS,
        timelines=timelines,
        inner_heldout_subjects=["s01"],
    )
    memoryless = evaluator.evaluate_inner(
        MemorylessCandidate("A", ("pt",), (0.9,)),
        thresholds=W_THRESHOLDS,
        timelines=timelines,
        inner_heldout_subjects=["s01"],
    )
    assert (
        stateful.per_subject["s01"].reference_episodes
        == memoryless.per_subject["s01"].reference_episodes
    )


def test_a_misaligned_timeline_is_refused() -> None:
    with pytest.raises(EvaluationError, match="align one to one"):
        SubjectTimeline(
            subject_id="s01",
            stream_key=("rec", 0),
            rows=(_row(0),),
            start_samples=(0, 1250),
            primary_row=(True,),
            primary_positive=(False,),
        )


def test_the_evaluator_attests_execution_capability() -> None:
    attestation = J1CandidateEvaluator().j1_execution_capability()
    assert attestation.execution_capable is True
    assert attestation.collaborator == "candidate_evaluator"


# -- the collaborator graph can now finish ----------------------------------


class _SyntheticSink:
    """A qualification sink. The real one's value comes from the authorization."""

    def j1_execution_capability(self):
        from cardiosentinel.journal_extension.j1.capability_gate import (
            J1CapabilityAttestation,
        )

        return J1CapabilityAttestation(
            collaborator="provenance_sink",
            execution_capable=True,
            detail="synthetic qualification sink; not a real destination",
        )

    def open_attempt(self, attempt_id: str) -> str:
        return f"memory://qualification/{attempt_id}"

    def promote(self, attempt_id: str, artifact: str, digest: str) -> None:
        return None


def test_the_whole_collaborator_graph_proves_it_can_finish() -> None:
    """Every collaborator the canonical driver calls, none of them a fixture.

    This proves capability, never permission: `require_execution_capability`
    reads no data and consults no authorization, and a capability attestation
    never implies one.
    """
    from cardiosentinel.journal_extension.j1.calibration import J1CalibrationFitter
    from cardiosentinel.journal_extension.j1.capability_gate import (
        REQUIRED_COLLABORATORS,
        require_execution_capability,
    )
    from cardiosentinel.journal_extension.j1.folds import J1FoldAllocator
    from cardiosentinel.journal_extension.j1.selection import J1SelectionRanker
    from cardiosentinel.journal_extension.j1.statistics import J1Bootstrap
    from cardiosentinel.journal_extension.j1.thresholds import J1ThresholdDeriver

    graph = {
        "fold_allocator": J1FoldAllocator(),
        "calibration_fitter": J1CalibrationFitter(
            source_score_artifact_identity="synthetic-m2g-v0"
        ),
        "threshold_deriver": J1ThresholdDeriver(),
        "candidate_evaluator": J1CandidateEvaluator(),
        "selection_ranker": J1SelectionRanker(),
        "bootstrap": J1Bootstrap(),
        "provenance_sink": _SyntheticSink(),
    }
    assert set(graph) == set(REQUIRED_COLLABORATORS)
    assert require_execution_capability(graph) == dict.fromkeys(graph, True)


def test_capability_is_not_permission() -> None:
    """The graph can finish. J1 still may not start."""
    from pathlib import Path

    from cardiosentinel.journal_extension.j1 import preflight

    with pytest.raises(preflight.PreflightError, match="authorization absent"):
        preflight.run_preflight(
            authorization_document=None,
            environment_authority=None,
            repository_root=Path(preflight.J1_PACKAGE_ROOT).parents[3],
        )
