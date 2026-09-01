"""The J1 fold evaluator: apply one candidate to one population, both arms.

Protocol sections 2.1, 2.2, 5.5, 5.6 and 5.9.

**What is inherited and what is re-stated, and why the line falls where it
does.** J1's forbidden `t1_protocol` entry points are all *operating-point*
functions -- `candidate_policies`, `policy_sort_key`, `empirical_order_statistic`
and `next_state` -- because T1/W1 were developed on the 12 VALIDATION subjects
J1 may not reopen. `group_reference_episodes` and `match_runs_to_episodes` are
not in that set and are not that kind of function: they are **measurement
conventions over reference truth**, they resolve no operating point, and §7.1.1
says V1's convention is *preserved unchanged*. So they are imported, which is
strictly better than re-stating them where re-stating is not required.

`next_state` is forbidden, so the state machine is re-stated here under the same
doctrine as §5.4's order statistic and §6.5's sort key: the same semantics,
computed inside J1, proven against the inherited implementation on shared
inputs.

**One thing a careful reading of §2.1 will get wrong.** §2.1 gives EVENT
evidence as `d_t AND p_t >= p_event AND s_t >= s_event`. The retained
implementation *relaxes the S4D term before* `T1_COLD_START_SECONDS`, because T2
recorded zero thresholded sensitivity in the first five minutes and demanding it
there makes early EVENT unreachable by construction. §2.1 also says the retained
state semantics are **not modified**. Read together, §2.1's line is the
mature-stream form and the cold-start relaxation is part of what is retained.
Implementing §2.1's prose literally would silently change the policy under test.

**State never crosses a boundary.** Every stream starts in `NORMAL`, and the
evaluator resets state per stream rather than trusting a caller to hand streams
over one at a time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, NamedTuple, Sequence

import numpy as np

from cardiosentinel.neural.t1_development_run import (
    contiguous_runs,
    false_event_onsets_per_hour,
    window_mcc,
)
from cardiosentinel.neural.t1_protocol import (
    T1_COLD_START_SECONDS,
    T1_PERSISTENCE_PROFILES,
    T1_STATE_EVENT,
    T1_STATE_NORMAL,
    T1_STATE_RECOVERY,
    T1_STATE_WATCH,
    T1PersistenceProfile,
    group_reference_episodes,
    match_runs_to_episodes,
)

from .candidates import MemorylessCandidate, StatefulCandidate, memoryless_rule
from .capability_gate import J1CapabilityAttestation
from .rows import ArmNeutralRow
from .selection import PROFILE_ALIASES
from .statistics import episode_f1, primary_f1_eligible

#: The four retained states. Re-stated by name, inherited in meaning.
EPISODE_STATES: tuple[str, ...] = (
    T1_STATE_NORMAL,
    T1_STATE_WATCH,
    T1_STATE_EVENT,
    T1_STATE_RECOVERY,
)
INITIAL_STATE: str = T1_STATE_NORMAL


class EvaluationError(RuntimeError):
    """A timeline or population the frozen evaluator does not admit."""


class Streaks(NamedTuple):
    """Consecutive-*available*-row counters, one per named condition."""

    event_confirm: int = 0
    watch_clear: int = 0
    event_release: int = 0
    re_event_confirm: int = 0
    recovery_clear: int = 0


ZERO_STREAKS = Streaks()


class StatefulThresholds(NamedTuple):
    """One J1-S candidate's four fold-derived numeric thresholds."""

    p_watch: float
    s_watch: float
    p_event: float
    s_event: float


@dataclass(frozen=True)
class SubjectTimeline:
    """One stream of one subject, with the reference truth beside it.

    Reference truth is carried, never derived from arm output: §4.2 anchors
    eligibility to reference truth precisely so the analysis set cannot become
    arm-dependent.
    """

    subject_id: str
    stream_key: tuple[str, int]
    rows: tuple[ArmNeutralRow, ...]
    start_samples: tuple[int, ...]
    primary_row: tuple[bool, ...]
    primary_positive: tuple[bool, ...]

    def __post_init__(self) -> None:
        lengths = {
            len(self.rows),
            len(self.start_samples),
            len(self.primary_row),
            len(self.primary_positive),
        }
        if len(lengths) != 1:
            raise EvaluationError(
                f"{self.subject_id}/{self.stream_key}: rows, start samples and "
                "reference truth must align one to one."
            )
        if not self.rows:
            raise EvaluationError(
                f"{self.subject_id}/{self.stream_key}: an empty stream is not a "
                "timeline."
            )


@dataclass(frozen=True)
class SubjectEvaluation:
    """One subject's complete held-out result for one candidate."""

    subject_id: str
    matched_episodes: int
    predicted_runs: int
    reference_episodes: int
    unmatched_runs: int
    position_count: int
    emitted_event_positions: int
    primary_true_positive: int
    primary_true_negative: int
    primary_false_positive: int
    primary_false_negative: int

    @property
    def episode_f1(self) -> float | None:
        return episode_f1(
            self.matched_episodes, self.predicted_runs, self.reference_episodes
        )

    @property
    def primary_f1_eligible(self) -> bool:
        return primary_f1_eligible(self.reference_episodes)


# -- the re-stated state machine, protocol section 2.1 ----------------------


def _profile_for(candidate: StatefulCandidate) -> T1PersistenceProfile:
    """J1's registry label to the inherited frozen profile it denotes."""
    name = PROFILE_ALIASES[candidate.profile]
    for profile in T1_PERSISTENCE_PROFILES:
        if profile.name == name:
            return profile
    raise EvaluationError(
        f"{candidate.profile!r} has no inherited persistence profile; J1's "
        "alias table and V1's frozen tuple have diverged."
    )


def is_cold_start(row: ArmNeutralRow) -> bool:
    return row.elapsed_stream_seconds < T1_COLD_START_SECONDS


def is_watch_evidence(row: ArmNeutralRow, thresholds: StatefulThresholds) -> bool:
    """Any one of the three signals is enough to raise attention."""
    return (
        bool(row.detector_decision_d_t)
        or float(row.oof_calibrated_probability_p_t) >= thresholds.p_watch
        or float(row.s4d_temporal_evidence_s_t) >= thresholds.s_watch
    )


def is_event_evidence(row: ArmNeutralRow, thresholds: StatefulThresholds) -> bool:
    """EVENT needs agreement, and needs more of it once the stream is mature.

    Before `T1_COLD_START_SECONDS` the S4D term is not required. That
    relaxation is part of the retained semantics, not a J1 change; see this
    module's docstring for why §2.1's prose reads otherwise.
    """
    if is_cold_start(row):
        return (
            bool(row.detector_decision_d_t)
            and float(row.oof_calibrated_probability_p_t) >= thresholds.p_event
        )
    return (
        bool(row.detector_decision_d_t)
        and float(row.oof_calibrated_probability_p_t) >= thresholds.p_event
        and float(row.s4d_temporal_evidence_s_t) >= thresholds.s_event
    )


def is_normal_evidence(row: ArmNeutralRow, thresholds: StatefulThresholds) -> bool:
    """All three signals must be quiet for a row to argue for de-escalation."""
    return (
        not bool(row.detector_decision_d_t)
        and float(row.oof_calibrated_probability_p_t) < thresholds.p_watch
        and float(row.s4d_temporal_evidence_s_t) < thresholds.s_watch
    )


def _required_event_confirm(
    row: ArmNeutralRow, profile: T1PersistenceProfile
) -> int:
    if is_cold_start(row):
        return profile.cold_event_confirm_windows
    return profile.event_confirm_windows


def next_episode_state(
    state: str,
    streaks: Streaks,
    row: ArmNeutralRow,
    thresholds: StatefulThresholds,
    profile: T1PersistenceProfile,
) -> tuple[str, Streaks]:
    """One causal step. Reads the current row and nothing ahead of it.

    An unavailable row is not evidence of anything: state is held, every
    confirmation streak resets, and no transition fires -- a gap must not be
    able to confirm an escalation or a release across itself.

    Escalation takes priority where a row satisfies more than one condition,
    and any state change clears every counter, so a streak can never survive
    into a state it was not accumulated in.
    """
    if state not in EPISODE_STATES:
        raise EvaluationError(f"{state!r} is not a retained episode state.")
    if not row.score_present:
        return state, ZERO_STREAKS

    event_evidence = is_event_evidence(row, thresholds)
    normal_evidence = is_normal_evidence(row, thresholds)
    watch_evidence = is_watch_evidence(row, thresholds)

    if state == T1_STATE_NORMAL:
        confirm = streaks.event_confirm + 1 if event_evidence else 0
        if event_evidence and confirm >= _required_event_confirm(row, profile):
            return T1_STATE_EVENT, ZERO_STREAKS
        if watch_evidence:
            # Immediate on one row; the streak survives so a WATCH entered by
            # an EVENT-evidence row keeps the confirmation it already earned.
            return T1_STATE_WATCH, Streaks(event_confirm=confirm)
        return T1_STATE_NORMAL, ZERO_STREAKS

    if state == T1_STATE_WATCH:
        if event_evidence:
            confirm = streaks.event_confirm + 1
            if confirm >= _required_event_confirm(row, profile):
                return T1_STATE_EVENT, ZERO_STREAKS
            return T1_STATE_WATCH, Streaks(event_confirm=confirm)
        if normal_evidence:
            clear = streaks.watch_clear + 1
            if clear >= profile.watch_clear_windows:
                return T1_STATE_NORMAL, ZERO_STREAKS
            return T1_STATE_WATCH, Streaks(watch_clear=clear)
        return T1_STATE_WATCH, ZERO_STREAKS

    if state == T1_STATE_EVENT:
        if event_evidence:
            return T1_STATE_EVENT, ZERO_STREAKS
        if normal_evidence:
            release = streaks.event_release + 1
            if release >= profile.event_release_windows:
                return T1_STATE_RECOVERY, ZERO_STREAKS
            return T1_STATE_EVENT, Streaks(event_release=release)
        # Ambiguous rows neither release nor re-confirm; they hold EVENT.
        return T1_STATE_EVENT, Streaks(event_release=streaks.event_release)

    # RECOVERY. There is deliberately no automatic path back to WATCH: a
    # recovering stream either re-escalates on EVENT evidence or clears.
    if event_evidence:
        confirm = streaks.re_event_confirm + 1
        if confirm >= profile.re_event_confirm_windows:
            return T1_STATE_EVENT, ZERO_STREAKS
        return T1_STATE_RECOVERY, Streaks(re_event_confirm=confirm)
    if normal_evidence:
        clear = streaks.recovery_clear + 1
        if clear >= profile.recovery_clear_windows:
            return T1_STATE_NORMAL, ZERO_STREAKS
        return T1_STATE_RECOVERY, Streaks(recovery_clear=clear)
    return T1_STATE_RECOVERY, ZERO_STREAKS


def run_stateful_policy(
    rows: Sequence[ArmNeutralRow],
    thresholds: StatefulThresholds,
    profile: T1PersistenceProfile,
) -> tuple[str, ...]:
    """Emitted states for one stream. Always starts in `NORMAL`."""
    state = INITIAL_STATE
    streaks = ZERO_STREAKS
    emitted: list[str] = []
    for row in rows:
        state, streaks = next_episode_state(state, streaks, row, thresholds, profile)
        emitted.append(state)
    return tuple(emitted)


def run_memoryless_rule(
    rows: Sequence[ArmNeutralRow],
    candidate: MemorylessCandidate,
    thresholds: Mapping[str, float],
) -> tuple[bool, ...]:
    """Per-row decisions for one stream, §2.2. No carried state of any kind.

    An unavailable row cannot be decided on: J1-W reads only the row it is
    given, and a row with no score carries no signal to read. It emits
    `False` rather than an invented value, which is the memoryless analogue of
    J1-S holding state across a gap -- neither arm may manufacture evidence.
    """
    rule = memoryless_rule(candidate, dict(thresholds))
    return tuple(bool(rule(row)) if row.score_present else False for row in rows)


# -- measurement, inherited unchanged --------------------------------------


def _confusion(
    predicted: Sequence[bool], actual: Sequence[bool], primary: Sequence[bool]
) -> tuple[int, int, int, int]:
    """Window confusion over PRIMARY rows only, §5.6 rank 2."""
    p = np.asarray(
        [bool(v) for v, keep in zip(predicted, primary) if keep], dtype=bool
    )
    a = np.asarray(
        [bool(v) for v, keep in zip(actual, primary) if keep], dtype=bool
    )
    return (
        int(np.count_nonzero(p & a)),
        int(np.count_nonzero(~p & ~a)),
        int(np.count_nonzero(p & ~a)),
        int(np.count_nonzero(~p & a)),
    )


def _evaluate_stream(
    timeline: SubjectTimeline, predicted_positive: Sequence[bool]
) -> tuple[int, int, int, int, tuple[int, int, int, int]]:
    episodes = group_reference_episodes(
        timeline.start_samples, timeline.primary_positive
    )
    runs = contiguous_runs(list(predicted_positive))
    matched = match_runs_to_episodes(episodes, runs)
    confusion = _confusion(
        predicted_positive, timeline.primary_positive, timeline.primary_row
    )
    return (
        len(matched),
        len(runs),
        len(episodes),
        len(runs) - len(set(matched.values())),
        confusion,
    )


@dataclass
class _SubjectTotals:
    """Running per-subject sums across that subject's streams.

    A subject's streams are summed, never averaged: the episode counts are
    counts of physical events and the confusion cells are counts of windows.
    """

    matched: int = 0
    predicted_runs: int = 0
    reference_episodes: int = 0
    unmatched_runs: int = 0
    positions: int = 0
    emitted_events: int = 0
    true_positive: int = 0
    true_negative: int = 0
    false_positive: int = 0
    false_negative: int = 0


@dataclass(frozen=True)
class CandidateEvaluation:
    """One candidate's result across a whole evaluated population."""

    candidate_id: str
    per_subject: dict[str, SubjectEvaluation]

    def selection_metrics(self) -> dict[str, float]:
        """The four §5.6 terms, in the form `selection.sort_key` consumes."""
        eligible = [
            subject
            for subject in self.per_subject.values()
            if subject.primary_f1_eligible
        ]
        if not eligible:
            raise EvaluationError(
                "no primary-F1-eligible subject in the evaluated population; "
                "the subject-macro mean is undefined and is never imputed."
            )
        scores = [subject.episode_f1 for subject in eligible]
        if any(score is None for score in scores):
            raise EvaluationError(
                "an eligible subject has an undefined episode F1, which §7.1.1 "
                "proves unreachable. This is an apparatus fault, not a result."
            )
        macro = sum(float(score) for score in scores) / len(scores)

        tp = sum(s.primary_true_positive for s in self.per_subject.values())
        tn = sum(s.primary_true_negative for s in self.per_subject.values())
        fp = sum(s.primary_false_positive for s in self.per_subject.values())
        fn = sum(s.primary_false_negative for s in self.per_subject.values())
        mcc = window_mcc(
            np.array([True] * tp + [True] * fp + [False] * fn + [False] * tn),
            np.array([True] * tp + [False] * fp + [True] * fn + [False] * tn),
        )

        unmatched = sum(s.unmatched_runs for s in self.per_subject.values())
        positions = sum(s.position_count for s in self.per_subject.values())
        emitted = sum(
            s.emitted_event_positions for s in self.per_subject.values()
        )
        return {
            "episode_f1": macro,
            "window_mcc": 0.0 if mcc is None else float(mcc),
            "false_onsets_per_hour": false_event_onsets_per_hour(
                unmatched, positions
            ),
            # Identical to the inherited `event_exposure_fraction` for the
            # stateful arm -- EVENT positions over all positions -- and stated
            # as a count because J1-W emits decisions rather than states, so
            # there is no state sequence to hand that function. A test asserts
            # the two agree wherever both are defined.
            "event_exposure_fraction": emitted / positions,
        }


class J1CandidateEvaluator:
    """The `candidate_evaluator` collaborator the capability gate requires.

    `evaluate_inner` and `evaluate_outer` are separate methods for the reason
    `calibration.py` keeps its two fits apart: the two levels produce evidence
    that must not be interchangeable, and a level argument is a value a caller
    can pass wrongly.
    """

    def j1_execution_capability(self) -> J1CapabilityAttestation:
        return J1CapabilityAttestation(
            collaborator="candidate_evaluator",
            execution_capable=True,
            detail="retained section 2.1 state machine and inherited episode "
            "matching, applied once per held-out subject",
        )

    def _evaluate(
        self,
        candidate: StatefulCandidate | MemorylessCandidate,
        *,
        thresholds: Mapping[str, float],
        timelines: Iterable[SubjectTimeline],
        permitted_subjects: Iterable[str],
    ) -> CandidateEvaluation:
        permitted = frozenset(permitted_subjects)
        if not permitted:
            raise EvaluationError(
                "an evaluation needs an explicit held-out population; without "
                "one there is nothing to prove a subject belongs to."
            )
        totals: dict[str, _SubjectTotals] = {}
        seen_streams: set[tuple[str, tuple[str, int]]] = set()
        for timeline in timelines:
            if timeline.subject_id not in permitted:
                raise EvaluationError(
                    f"{timeline.subject_id!r} is not in the held-out "
                    "population for this evaluation. A candidate is applied "
                    "once, to the subjects the fold holds out, and never to "
                    "the population its thresholds came from."
                )
            key = (timeline.subject_id, timeline.stream_key)
            if key in seen_streams:
                raise EvaluationError(
                    f"stream {key} appears twice; exactly one evaluation per "
                    "stream is permitted."
                )
            seen_streams.add(key)

            predicted = self._predict(candidate, timeline, thresholds)
            matched, runs, episodes, unmatched, confusion = _evaluate_stream(
                timeline, predicted
            )
            running = totals.setdefault(timeline.subject_id, _SubjectTotals())
            running.matched += matched
            running.predicted_runs += runs
            running.reference_episodes += episodes
            running.unmatched_runs += unmatched
            running.positions += len(timeline.rows)
            running.emitted_events += sum(1 for flag in predicted if flag)
            running.true_positive += confusion[0]
            running.true_negative += confusion[1]
            running.false_positive += confusion[2]
            running.false_negative += confusion[3]

        if not totals:
            raise EvaluationError("no timeline was supplied to evaluate.")
        per_subject = {
            subject: SubjectEvaluation(
                subject_id=subject,
                matched_episodes=running.matched,
                predicted_runs=running.predicted_runs,
                reference_episodes=running.reference_episodes,
                unmatched_runs=running.unmatched_runs,
                position_count=running.positions,
                emitted_event_positions=running.emitted_events,
                primary_true_positive=running.true_positive,
                primary_true_negative=running.true_negative,
                primary_false_positive=running.false_positive,
                primary_false_negative=running.false_negative,
            )
            for subject, running in totals.items()
        }
        return CandidateEvaluation(
            candidate_id=candidate.candidate_id, per_subject=per_subject
        )

    def _predict(
        self,
        candidate: StatefulCandidate | MemorylessCandidate,
        timeline: SubjectTimeline,
        thresholds: Mapping[str, float],
    ) -> tuple[bool, ...]:
        """One stream's predicted-positive flags, whichever arm is asked."""
        if isinstance(candidate, StatefulCandidate):
            emitted = run_stateful_policy(
                timeline.rows,
                StatefulThresholds(
                    p_watch=float(thresholds["p_watch"]),
                    s_watch=float(thresholds["s_watch"]),
                    p_event=float(thresholds["p_event"]),
                    s_event=float(thresholds["s_event"]),
                ),
                _profile_for(candidate),
            )
            return tuple(state == T1_STATE_EVENT for state in emitted)
        if isinstance(candidate, MemorylessCandidate):
            return run_memoryless_rule(timeline.rows, candidate, thresholds)
        raise EvaluationError(
            f"{type(candidate).__name__} is not a J1 candidate identity."
        )

    def evaluate_inner(
        self,
        candidate: StatefulCandidate | MemorylessCandidate,
        *,
        thresholds: Mapping[str, float],
        timelines: Iterable[SubjectTimeline],
        inner_heldout_subjects: Iterable[str],
    ) -> CandidateEvaluation:
        """§5.5. Applied once to `INNER_HELDOUT_j`, never to `INNER_FIT_j`."""
        return self._evaluate(
            candidate,
            thresholds=thresholds,
            timelines=timelines,
            permitted_subjects=inner_heldout_subjects,
        )

    def evaluate_outer(
        self,
        candidate: StatefulCandidate | MemorylessCandidate,
        *,
        thresholds: Mapping[str, float],
        timelines: Iterable[SubjectTimeline],
        outer_assessment_subjects: Iterable[str],
    ) -> CandidateEvaluation:
        """§5.9. Applied to the eight outer-assessment subjects only."""
        return self._evaluate(
            candidate,
            thresholds=thresholds,
            timelines=timelines,
            permitted_subjects=outer_assessment_subjects,
        )
