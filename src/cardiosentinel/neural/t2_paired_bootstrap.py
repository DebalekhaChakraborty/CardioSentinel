"""The one derived analysis `T2_ARM_COMPARISON_ANALYSIS_PLAN_V1` authorizes.

The outer-validation artifacts carry a `subject_bootstrap` **per arm** and no
interval on the S4D - GRU difference. The plan's primary estimand is that
difference, so it has a point estimate and no uncertainty. This module supplies
exactly that interval and nothing else.

**It computes nothing on import and reads no artifact.** Every function here
takes arrays as arguments. Reading measured values is a separate, separately
authorized step; this module exists so that step has a reviewed implementation
to invoke rather than one written while the numbers are visible.

**Why the resampler is imported rather than rewritten.** `subject_bootstrap_plan`
is deterministic in `(sorted unique subjects, replicates, seed)`. Reusing it
means replicate *r* here draws the same subject multiset that replicate *r* of
the already-published per-arm bootstrap drew. That is what makes this paired: the
two arms are compared on one resample, not on two independent ones, and the
interval is for the difference rather than for two marginals that happen to be
plotted next to each other.

**Pairing is by row position, not by subject alone.** The outer evidence store
keeps one identity array and one score array per arm, in the same row order, so
position *i* is the same window in both arms. The caller passes both arms'
scores already aligned to that shared identity; `require_paired_inputs` refuses
anything else rather than silently comparing different rows.

**Undefined replicates are preserved.** A resample can draw a subject multiset
whose pooled labels are single-class, and AUPRC is undefined there for both arms
at once. Those replicates are counted and reported, never zero-filled and never
imputed -- substituting a zero would move the interval toward "no difference"
and would do it invisibly.

Registered design, from plan §4, restated here so a drift between the plan and
the code fails a test rather than being resolved at analysis time:

    unit                        subject
    rows                        the same resampled rows for both arms
    statistic                   pooled AUPRC(S4D) - pooled AUPRC(GRU)
    model refitting             none
    threshold changes           none
    reselection                 none
    seed                        2026
    replicates                  1000
    interval                    percentile, lower_95 / upper_95
    undefined replicates        preserved and reported

What this module may never be used for: reselecting an arm, sweeping a
threshold, re-fitting anything, producing an unbiased absolute figure for either
arm, or attaching calibration language to a T2 score.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Final

import numpy as np

from cardiosentinel.baseline.metrics import binary_metrics
from cardiosentinel.evaluation.metrics import subject_bootstrap_plan
from cardiosentinel.neural.t2_protocol import (
    T2_ARM_GRU,
    T2_ARM_S4D,
    T2_BOOTSTRAP_REPLICATES,
    T2_BOOTSTRAP_SEED,
    T2_BOOTSTRAP_UNIT,
)

#: Artifact class of the payload this module returns.
T2_PAIRED_BOOTSTRAP_CLASS: Final = "t2_v1_paired_subject_bootstrap_difference"

#: The analysis plan this implements, and the section that authorizes it.
T2_PAIRED_BOOTSTRAP_AUTHORITY: Final = "T2_ARM_COMPARISON_ANALYSIS_PLAN_V1 §4"

#: Sign convention, stated once. A positive difference favours S4D.
T2_PAIRED_DIFFERENCE_DEFINITION: Final = (
    "pooled_primary_auprc_s4d_minus_pooled_primary_auprc_gru"
)

#: The threshold argument is a required input of `binary_metrics` and plays no
#: part in AUPRC, which is computed over the full score ordering. It is fixed
#: here so no caller can pass one and imagine it moved the result.
_AUPRC_THRESHOLD_IS_INERT: Final = 0.5

#: What the interval is an interval for. Copied from the per-arm claim so the
#: derived analysis cannot quietly widen its own scope.
T2_PAIRED_BOOTSTRAP_CLAIM: Final = (
    "between_subject_variation_in_the_paired_arm_difference_conditional_on_two_"
    "fitted_temporal_models_and_frozen_thresholds"
)


class T2PairedBootstrapError(RuntimeError):
    """A refusal. Never a value to substitute."""


def require_registered_design(subject_bootstrap: dict[str, Any]) -> dict[str, Any]:
    """Bind this analysis to the design the artifact itself registered.

    Plan §4 fixes seed 2026 and 1000 replicates *by reference to the artifact's
    own `subject_bootstrap` block*, so that the derived interval is drawn from
    the same design as the per-arm ones rather than from a number retyped into
    an analysis script. If the artifact ever disagrees with the constants here,
    that is a fact about the evidence and must stop the analysis.

    `subject_bootstrap` is the artifact's block for either arm; both arms carry
    the same design and either may be passed.
    """
    expected = {
        "seed": T2_BOOTSTRAP_SEED,
        "replicates": T2_BOOTSTRAP_REPLICATES,
        "unit": T2_BOOTSTRAP_UNIT,
        "model_refitted_per_replicate": False,
    }
    observed = {key: subject_bootstrap.get(key) for key in expected}
    if observed != expected:
        raise T2PairedBootstrapError(
            "The artifact's registered subject-bootstrap design does not match "
            f"the design this analysis is bound to. expected {expected}, "
            f"observed {observed}. Plan §4 binds the derived interval to the "
            "artifact's own design; a mismatch is evidence, not a parameter."
        )
    return dict(expected)


def require_paired_inputs(
    subjects: Sequence[str],
    labels: Sequence[int],
    s4d_scores: Sequence[float],
    gru_scores: Sequence[float],
) -> None:
    """Both arms must be the same rows, in the same order, with one label vector.

    The store holds one identity file and one label vector serving both arms, so
    a length disagreement means the caller assembled the inputs from somewhere
    else. Refuse rather than compare different rows and report a difference.
    """
    lengths = {
        "subjects": len(subjects),
        "labels": len(labels),
        T2_ARM_S4D: len(s4d_scores),
        T2_ARM_GRU: len(gru_scores),
    }
    if len(set(lengths.values())) != 1:
        raise T2PairedBootstrapError(
            f"Paired inputs must be row-aligned; lengths are {lengths}. One "
            "identity array and one label vector serve both arms."
        )
    # `len(...) == 0`, never `not subjects`: the real caller hands these numpy
    # arrays, and truthiness on an array of more than one element raises rather
    # than answering. The synthetic tests passed lists and never reached it.
    if len(subjects) == 0:
        raise T2PairedBootstrapError("Paired inputs are empty.")
    distinct = {int(value) for value in labels}
    if not distinct <= {0, 1}:
        raise T2PairedBootstrapError(f"Labels must be binary; saw {sorted(distinct)}.")


def _pooled_auprc(labels: np.ndarray, scores: np.ndarray) -> float | None:
    """Pooled AUPRC, or `None` where it is undefined. Never a substitute value."""
    value = binary_metrics(labels, scores, _AUPRC_THRESHOLD_IS_INERT)["auprc"]
    return None if value is None else float(value)


def paired_subject_bootstrap_difference(
    subjects: Sequence[str],
    labels: Sequence[int],
    s4d_scores: Sequence[float],
    gru_scores: Sequence[float],
    *,
    replicates: int = T2_BOOTSTRAP_REPLICATES,
    seed: int = T2_BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Percentile interval for pooled AUPRC(S4D) - pooled AUPRC(GRU).

    One resample of subjects per replicate, applied to **both** arms, so each
    replicate contributes one difference rather than two marginals. Nothing is
    refitted, no threshold is consulted and no arm is re-chosen inside the loop.
    """
    require_paired_inputs(subjects, labels, s4d_scores, gru_scores)

    subject_array = np.asarray(subjects, dtype=str)
    label_array = np.asarray(labels, dtype=np.int64)
    s4d_array = np.asarray(s4d_scores, dtype=np.float64)
    gru_array = np.asarray(gru_scores, dtype=np.float64)

    index_by_subject = {
        subject: np.flatnonzero(subject_array == subject)
        for subject in sorted(set(subject_array.tolist()))
    }

    differences: list[float] = []
    undefined = 0
    for sampled in subject_bootstrap_plan(
        subject_array.tolist(), replicates=replicates, seed=seed
    ):
        indices = np.concatenate([index_by_subject[subject] for subject in sampled])
        resampled_labels = label_array[indices]
        s4d_value = _pooled_auprc(resampled_labels, s4d_array[indices])
        gru_value = _pooled_auprc(resampled_labels, gru_array[indices])
        if s4d_value is None or gru_value is None:
            undefined += 1
            continue
        differences.append(s4d_value - gru_value)

    point = _paired_point_estimate(label_array, s4d_array, gru_array)
    return {
        "evidence_class": T2_PAIRED_BOOTSTRAP_CLASS,
        "authority": T2_PAIRED_BOOTSTRAP_AUTHORITY,
        "statistic": T2_PAIRED_DIFFERENCE_DEFINITION,
        "unit": T2_BOOTSTRAP_UNIT,
        "paired": True,
        "same_rows_both_arms": True,
        "model_refitted_per_replicate": False,
        "thresholds_changed": False,
        "reselection_performed": False,
        "window_bootstrap_performed": False,
        "claim_scope": T2_PAIRED_BOOTSTRAP_CLAIM,
        "seed": seed,
        "requested_replicates": replicates,
        "successful_replicates": len(differences),
        "undefined_replicates": undefined,
        "undefined_replicates_zero_filled": False,
        "subject_count": len(index_by_subject),
        "row_count": int(subject_array.size),
        "point_estimate": point,
        "lower_95": (
            None if not differences else float(np.percentile(differences, 2.5))
        ),
        "upper_95": (
            None if not differences else float(np.percentile(differences, 97.5))
        ),
    }


def _paired_point_estimate(
    labels: np.ndarray, s4d_scores: np.ndarray, gru_scores: np.ndarray
) -> float | None:
    """The observed difference on the unresampled rows.

    Reported alongside the interval so the interval is legible, and computed the
    same way as the replicates so the two cannot disagree about what "pooled
    primary AUPRC" means. This is **not** a new primary result: the plan's
    primary contrast is read verbatim from `selection_decision`, and this value
    must equal it.
    """
    s4d_value = _pooled_auprc(labels, s4d_scores)
    gru_value = _pooled_auprc(labels, gru_scores)
    if s4d_value is None or gru_value is None:
        return None
    return s4d_value - gru_value


def require_point_estimate_agrees(
    derived: dict[str, Any], registered_difference: float, *, tolerance: float = 1e-9
) -> None:
    """The derived point estimate must reproduce the artifact's own difference.

    The plan reports the primary contrast verbatim from `selection_decision`.
    If this module's recomputation of the same quantity disagrees, then either
    the rows it was handed are not the rows the selection saw, or the two are
    not computing the same statistic. Both are reasons to stop, and neither is
    a reason to prefer one number.
    """
    observed = derived.get("point_estimate")
    if observed is None:
        raise T2PairedBootstrapError(
            "The derived point estimate is undefined; it cannot be checked "
            "against the registered difference."
        )
    if abs(float(observed) - float(registered_difference)) > tolerance:
        raise T2PairedBootstrapError(
            f"The derived point estimate {observed!r} does not reproduce the "
            f"registered selection difference {registered_difference!r} within "
            f"{tolerance}. The inputs are not the rows the selection saw, or the "
            "statistics differ. Stop; do not report either number."
        )
