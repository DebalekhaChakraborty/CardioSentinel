"""The arm-neutral evidence row, and the four calibration probability types.

Frozen protocol section 3.1 fixes the arm-neutral row at **eight** fields. Both
arms receive that object, unchanged and identical.

`elapsed_state_seconds` is deliberately absent. It is not upstream evidence: it
is J1-S's own internal state, existing only because a state machine exists.
J1-W is not "denied" it -- the quantity is not in the row for either arm, and
J1-S derives it from its own state when invoking the retained T1 implementation.

Section 5.10 requires that fit-side and OOF probabilities cannot be confused.
They are distinct types here rather than a string flag, so a fit-side value
cannot satisfy an API expecting assessment evidence: that is a type error, not a
review comment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

#: Internal only. Derives thresholds on the fit side; never persisted as
#: evidence, never accepted where assessment evidence is required.
InnerFitCalibratedProbability = NewType("InnerFitCalibratedProbability", float)
OuterFitCalibratedProbability = NewType("OuterFitCalibratedProbability", float)

#: Out-of-fold. The calibrator that produced these saw no row of the subject.
InnerOofCalibratedProbability = NewType("InnerOofCalibratedProbability", float)
OuterOofCalibratedProbability = NewType("OuterOofCalibratedProbability", float)


@dataclass(frozen=True)
class ArmNeutralRow:
    """The eight frozen fields. Immutable, and identical for both arms."""

    stable_id: str
    m2g_detector_score: float
    detector_decision_d_t: bool
    oof_calibrated_probability_p_t: OuterOofCalibratedProbability
    decision_error_uncertainty_u_t: float
    s4d_temporal_evidence_s_t: float
    score_present: bool
    elapsed_stream_seconds: float


#: Frozen field order, asserted by the qualification tests.
ARM_NEUTRAL_FIELDS: tuple[str, ...] = (
    "stable_id",
    "m2g_detector_score",
    "detector_decision_d_t",
    "oof_calibrated_probability_p_t",
    "decision_error_uncertainty_u_t",
    "s4d_temporal_evidence_s_t",
    "score_present",
    "elapsed_stream_seconds",
)


class CalibrationBoundaryError(RuntimeError):
    """A fit-side probability reached an assessment-evidence interface."""


def assessment_row(
    *,
    stable_id: str,
    m2g_detector_score: float,
    detector_decision_d_t: bool,
    outer_oof_p_t: OuterOofCalibratedProbability,
    decision_error_uncertainty_u_t: float,
    s4d_temporal_evidence_s_t: float,
    score_present: bool,
    elapsed_stream_seconds: float,
) -> ArmNeutralRow:
    """Build an assessment row. Only an *outer OOF* probability is admissible.

    The keyword is named `outer_oof_p_t` rather than `p_t` so a caller holding a
    fit-side value has to rename it deliberately, not merely pass it along.
    """
    return ArmNeutralRow(
        stable_id=stable_id,
        m2g_detector_score=m2g_detector_score,
        detector_decision_d_t=detector_decision_d_t,
        oof_calibrated_probability_p_t=outer_oof_p_t,
        decision_error_uncertainty_u_t=decision_error_uncertainty_u_t,
        s4d_temporal_evidence_s_t=s4d_temporal_evidence_s_t,
        score_present=score_present,
        elapsed_stream_seconds=elapsed_stream_seconds,
    )
