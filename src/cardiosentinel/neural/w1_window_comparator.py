"""The window-only comparator arm registered by `W1_WINDOW_COMPARATOR_ANALYSIS_PLAN_V1`.

RQ4 -- *does longitudinal/episode reasoning improve monitoring quality?* -- is
recorded as unanswered because the T1 measurement is one-armed. This module is
the missing arm: a memoryless window-level alerting rule, evaluated on the same
rows, under the same frozen thresholds, and scored with the same episode
matching, so the contrast is attributable to the temporal state logic and to
nothing else.

**It never invokes the state machine.** `t1_protocol.next_state` is not imported
and not called. Arm T1's predictions are read from the persisted `emitted_state`
column; Arm W's are computed here. Nothing claims a run directory, nothing is
written, and no threshold is generated -- the frozen per-row `p_event` and
`s_event` are used exactly as the consumed attempt recorded them.

**It reads no labels.** Reference episodes are supplied by the caller, which owns
the §16 authority boundary and the human authorization that plan §6 requires.
This module receives arrays and returns numbers.

**The one rule.**

    alert(row) := t1_protocol.is_event_evidence(row, thresholds)

`is_event_evidence` is imported unchanged, including its documented cold-start
relaxation, so Arm W and Arm T1 agree about what counts as event evidence in a
single row and differ only in what they do with it across rows. Arm W has no
confirmation streak, carries no state, and has no WATCH gating or RECOVERY
hysteresis -- those three absences *are* the ablation.

Arm W is not a weaker model. It shares the encoder, fusion, memory, calibration
and temporal score with Arm T1, and above all it shares the thresholds, which
were frozen per fold before any held-out label was opened. A comparator handed
its own tuned operating point would make the contrast uninterpretable.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Final

import numpy as np

from cardiosentinel.evaluation.metrics import subject_bootstrap_plan
from cardiosentinel.neural.t1_protocol import (
    T1Row,
    T1Thresholds,
    is_event_evidence,
)

W1_COMPARATOR_CLASS: Final = "w1_window_only_comparator_v1"
W1_AUTHORITY: Final = "W1_WINDOW_COMPARATOR_ANALYSIS_PLAN_V1 §2.2"

#: Plan §4.2, bound to the design T1 and T2 already registered.
W1_BOOTSTRAP_SEED: Final = 2026
W1_BOOTSTRAP_REPLICATES: Final = 1000
W1_BOOTSTRAP_UNIT: Final = "subject"

#: Plan §4.1. Positive favours Arm T1, i.e. episode reasoning helped.
W1_DIFFERENCE_DEFINITION: Final = (
    "subject_macro_episode_f1_arm_t1_minus_subject_macro_episode_f1_arm_window_only"
)

#: The columns `t1_oof_state_evidence.npz` must supply for the rule to run.
W1_REQUIRED_COLUMNS: Final = (
    "detector_decision_d_t",
    "oof_calibrated_probability_p_t",
    "s4d_temporal_evidence_s_t",
    "elapsed_stream_seconds",
    "score_present",
    "p_watch",
    "s_watch",
    "p_event",
    "s_event",
)


class W1ComparatorError(RuntimeError):
    """A refusal. Never a value to substitute."""


def require_columns(columns: Mapping[str, Any]) -> None:
    missing = [name for name in W1_REQUIRED_COLUMNS if name not in columns]
    if missing:
        raise W1ComparatorError(
            f"the state-evidence store is missing {missing}; the window-only "
            "rule reads the same inputs and the same frozen thresholds the "
            "state machine read, and will not substitute a default for either."
        )


def window_only_event_flags(columns: Mapping[str, Any]) -> np.ndarray:
    """Arm W: one boolean per row, no state, no streak, no gating.

    An unscored row is not evidence of anything and never alerts -- the same
    treatment `next_state` gives it, so the two arms disagree about transitions
    rather than about which rows are readable.
    """
    require_columns(columns)
    present = np.asarray(columns["score_present"], dtype=bool)
    detector = np.asarray(columns["detector_decision_d_t"], dtype=bool)
    probability = np.asarray(columns["oof_calibrated_probability_p_t"], dtype=float)
    temporal = np.asarray(columns["s4d_temporal_evidence_s_t"], dtype=float)
    elapsed = np.asarray(columns["elapsed_stream_seconds"], dtype=float)
    p_watch = np.asarray(columns["p_watch"], dtype=float)
    s_watch = np.asarray(columns["s_watch"], dtype=float)
    p_event = np.asarray(columns["p_event"], dtype=float)
    s_event = np.asarray(columns["s_event"], dtype=float)

    flags = np.zeros(present.shape, dtype=bool)
    for index in range(present.size):
        if not present[index]:
            continue
        row = T1Row(
            stable_id="w1",
            score_present=True,
            detector_decision=bool(detector[index]),
            calibrated_probability=float(probability[index]),
            decision_error_uncertainty=0.0,
            temporal_evidence=float(temporal[index]),
            elapsed_stream_seconds=float(elapsed[index]),
        )
        thresholds = T1Thresholds(
            p_watch=float(p_watch[index]),
            s_watch=float(s_watch[index]),
            p_event=float(p_event[index]),
            s_event=float(s_event[index]),
        )
        flags[index] = bool(is_event_evidence(row, thresholds))
    return flags


def episode_f1(episodes: Mapping[str, int]) -> float | None:
    """`2 * matched / (predicted + reference)`; undefined when both are zero.

    Identical in form to `t1_continuation_results._episode_f1`, restated rather
    than imported so this module binds no continuation entry point. Equivalence
    is asserted by test, not assumed -- the same convention the continuation
    itself used for `contiguous_runs`.
    """
    matched = int(episodes["matched_episodes"])
    reference = int(episodes["reference_episodes"])
    predicted = int(episodes["predicted_event_runs"])
    denominator = predicted + reference
    if denominator == 0:
        return None
    return 2.0 * matched / denominator


def subject_macro(values: Mapping[str, float | None]) -> float | None:
    """Mean over subjects. An undefined subject is excluded, never zero-filled.

    T1's registered primary is the subject-macro mean of `episode_f1`, so this
    is the estimand both arms are compared on. A subject with no reference
    episodes and no predicted runs contributes nothing rather than a 0.0 that
    would read as a detection failure -- the distinction the T1 post-hoc
    analysis had to make after the fact.
    """
    defined = [float(v) for v in values.values() if v is not None]
    if not defined:
        return None
    return sum(defined) / len(defined)


def require_arm_reproduces_published(
    observed: float | None, published: float, *, tolerance: float = 1e-4
) -> None:
    """Arm T1 must reproduce its own published subject-macro mean.

    Plan §4.1. If the comparator's reading of the persisted trace does not
    reproduce 0.2524, it is scoring different rows and the analysis stops. The
    same self-check, and the same stopping rule, the T2 analysis used.
    """
    if observed is None:
        raise W1ComparatorError("Arm T1's subject-macro mean is undefined; stop.")
    if abs(float(observed) - float(published)) > tolerance:
        raise W1ComparatorError(
            f"Arm T1 reproduces {observed!r}, the published value is "
            f"{published!r}. The comparator is not reading the rows the T1 "
            "measurement scored. Stop; do not report either number."
        )


def paired_subject_macro_difference(
    arm_t1: Mapping[str, float | None],
    arm_window: Mapping[str, float | None],
    *,
    replicates: int = W1_BOOTSTRAP_REPLICATES,
    seed: int = W1_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Plan §4.2. Percentile interval for the paired subject-macro difference.

    One subject resample per replicate, applied to **both** arms, so each
    replicate contributes one difference rather than two marginals. The two
    mappings must cover the same subjects; a mismatch means the arms were not
    scored on the same population.
    """
    if set(arm_t1) != set(arm_window):
        raise W1ComparatorError(
            "the two arms cover different subjects; they are not the same "
            f"population. t1_only={sorted(set(arm_t1) - set(arm_window))} "
            f"window_only={sorted(set(arm_window) - set(arm_t1))}"
        )
    subjects = sorted(arm_t1)
    if not subjects:
        raise W1ComparatorError("no subjects supplied.")

    differences: list[float] = []
    undefined = 0
    for sample in subject_bootstrap_plan(subjects, replicates=replicates, seed=seed):
        left = subject_macro({f"{s}#{i}": arm_t1[s] for i, s in enumerate(sample)})
        right = subject_macro({f"{s}#{i}": arm_window[s] for i, s in enumerate(sample)})
        if left is None or right is None:
            undefined += 1
            continue
        differences.append(left - right)

    point_t1 = subject_macro(arm_t1)
    point_window = subject_macro(arm_window)
    point = (
        None
        if point_t1 is None or point_window is None
        else point_t1 - point_window
    )
    return {
        "evidence_class": W1_COMPARATOR_CLASS,
        "authority": W1_AUTHORITY,
        "statistic": W1_DIFFERENCE_DEFINITION,
        "unit": W1_BOOTSTRAP_UNIT,
        "paired": True,
        "same_subjects_both_arms": True,
        "model_refitted_per_replicate": False,
        "thresholds_changed": False,
        "state_machine_invoked": False,
        "seed": seed,
        "requested_replicates": replicates,
        "successful_replicates": len(differences),
        "undefined_replicates": undefined,
        "undefined_replicates_zero_filled": False,
        "subject_count": len(subjects),
        "arm_t1_subject_macro": point_t1,
        "arm_window_subject_macro": point_window,
        "point_estimate": point,
        "lower_95": (
            None if not differences else float(np.percentile(differences, 2.5))
        ),
        "upper_95": (
            None if not differences else float(np.percentile(differences, 97.5))
        ),
    }


def registered_predictions(
    group_a: Sequence[str], group_b: Sequence[str]
) -> dict[str, Any]:
    """Plan §5, as data rather than prose.

    Recorded so the directional expectations can be checked against the result
    mechanically, instead of being reread charitably afterwards.
    """
    return {
        "group_a_episode_free": list(group_a),
        "group_b_missed": list(group_b),
        "group_a_expectation": "worse_or_unchanged_at_zero",
        "group_b_expectation": "may_improve",
        "aggregate_expectation": "near_zero_difference_is_expected_and_uninformative",
        "contradiction_is_reported_not_reconciled": True,
    }
