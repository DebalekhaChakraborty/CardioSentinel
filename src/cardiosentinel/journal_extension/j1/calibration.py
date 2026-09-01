"""The J1 calibration fitter, protocol sections 5.3.1, 5.9, 5.10 and 5.11.

The U1 Platt procedure is **inherited, not reimplemented**. J1 asks whether a
stateful episode policy survives a fair comparator; refitting the calibration
mathematics here would change a nuisance quantity the question depends on, and
two implementations of one frozen procedure would eventually disagree. So this
module calls `cardiosentinel.neural.u1_calibration.fit_calibrator` and adds only
what J1 needs on top: the population boundary, the four probability types, and
the provenance binding.

**The property this module exists to hold.** An evaluated subject's calibrated
probability must come from a calibrator that saw no row of that subject. The fit
population and the population being scored are therefore separate arguments at
every entry point, and their disjointness is proven structurally rather than
documented -- §5.11 requires exactly that, and adds that no runtime flag may
bypass it. There is no `force`, `allow_overlap` or `strict` parameter here, and
a test asserts their absence.

**Why fit-side and held-out application are different methods.** §5.10 forbids a
fit-side calibrated value from ever being persisted or labelled
`oof_calibrated_probability_p_t`. A single `apply` returning a bare `float`
would make that a naming convention. `fit_side_probabilities` and
`oof_probabilities` return distinct `NewType`s, refuse the other population by
subject identity, and cannot be substituted for one another without a
deliberate rename at the call site.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from cardiosentinel.neural.u1_calibration import (
    FAMILY_PLATT,
    U1Calibrator,
    fit_calibrator,
    recover_logits,
)
from cardiosentinel.neural.u1_protocol import (
    U1_CLAMP_DELTA,
    U1_PROTOCOL_NAME,
    U1_PROTOCOL_SHA256,
)

from .capability_gate import J1CapabilityAttestation
from .rows import (
    InnerFitCalibratedProbability,
    InnerOofCalibratedProbability,
    OuterFitCalibratedProbability,
    OuterOofCalibratedProbability,
)

#: The inherited calibration identity every J1 calibrated row is bound to.
CALIBRATION_PROTOCOL_IDENTITY: str = U1_PROTOCOL_NAME
CALIBRATION_PROTOCOL_SHA256: str = U1_PROTOCOL_SHA256

#: J1 uses the primary family only. The temperature-only comparator is a U1
#: selection question that J1 does not reopen.
CALIBRATION_FAMILY: str = FAMILY_PLATT

INNER = "inner"
OUTER = "outer"


class CalibrationPopulationError(RuntimeError):
    """A fit population that overlaps the population it is about to score."""


def subject_digest(subjects: Iterable[str]) -> str:
    """SHA-256 over the sorted, newline-joined subject identities.

    Sorted, so a manifest written in a different order binds to the same
    digest; a set that differs by one subject does not.
    """
    ordered = sorted(set(subjects))
    return hashlib.sha256(("\n".join(ordered) + "\n").encode("utf-8")).hexdigest()


def _calibrator_digest(calibrator: U1Calibrator) -> str:
    """SHA-256 over the fitted parameters that determine the mapping."""
    payload = (
        f"family={calibrator.family}\n"
        f"a={calibrator.a!r}\n"
        f"b={calibrator.b!r}\n"
        f"clamp_delta={calibrator.clamp_delta!r}\n"
        f"fit_row_count={calibrator.fit_row_count}\n"
        f"fit_subjects={','.join(sorted(calibrator.fit_subjects))}\n"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CalibrationProvenance:
    """Every binding §5.11 requires of a calibrated assessment row."""

    level: str
    outer_fold_index: int
    inner_fold_index: int | None
    fit_subjects: tuple[str, ...]
    fit_subjects_digest: str
    heldout_subjects: tuple[str, ...]
    heldout_subjects_digest: str
    calibrator_digest: str
    calibration_protocol_identity: str
    calibration_protocol_sha256: str
    source_score_artifact_identity: str

    def as_attestation(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "outer_fold_index": self.outer_fold_index,
            "inner_fold_index": self.inner_fold_index,
            "fit_subject_count": len(self.fit_subjects),
            "fit_subjects_digest": self.fit_subjects_digest,
            "heldout_subject_count": len(self.heldout_subjects),
            "heldout_subjects_digest": self.heldout_subjects_digest,
            "calibrator_digest": self.calibrator_digest,
            "calibration_protocol_identity": self.calibration_protocol_identity,
            "calibration_protocol_sha256": self.calibration_protocol_sha256,
            "source_score_artifact_identity": self.source_score_artifact_identity,
            "fit_heldout_disjoint": True,
        }


@dataclass(frozen=True)
class FittedCalibration:
    """A fitted calibrator that knows which subjects it is allowed to score.

    It carries its own populations so the boundary travels with the artifact.
    A caller cannot hold this object and quietly score the fit side as evidence.
    """

    calibrator: U1Calibrator
    provenance: CalibrationProvenance

    @property
    def fit_subjects(self) -> frozenset[str]:
        return frozenset(self.provenance.fit_subjects)

    @property
    def heldout_subjects(self) -> frozenset[str]:
        return frozenset(self.provenance.heldout_subjects)

    def _require_population(
        self, subject: str, permitted: frozenset[str], what: str
    ) -> None:
        if subject not in permitted:
            raise CalibrationPopulationError(
                f"{subject!r} is not in this calibrator's {what} population, so "
                "the value asked for would not mean what its name says."
            )

    def fit_side_probabilities(
        self, subject: str, scores: Sequence[float]
    ) -> tuple[float, ...]:
        """§5.3.2 fit-side values. Threshold derivation only, never evidence.

        Returned as `InnerFitCalibratedProbability` or
        `OuterFitCalibratedProbability`, neither of which `assessment_row`
        accepts.
        """
        self._require_population(subject, self.fit_subjects, "fit")
        wrap = (
            InnerFitCalibratedProbability
            if self.provenance.level == INNER
            else OuterFitCalibratedProbability
        )
        return tuple(wrap(float(p)) for p in self._apply(scores))

    def oof_probabilities(
        self, subject: str, scores: Sequence[float]
    ) -> tuple[float, ...]:
        """§5.3.3 / §5.9 held-out values. The only admissible evidence."""
        self._require_population(subject, self.heldout_subjects, "held-out")
        wrap = (
            InnerOofCalibratedProbability
            if self.provenance.level == INNER
            else OuterOofCalibratedProbability
        )
        return tuple(wrap(float(p)) for p in self._apply(scores))

    def _apply(self, scores: Sequence[float]) -> Any:
        return self.calibrator.apply_to_scores(list(scores))


def _require_disjoint(
    fit_subjects: Iterable[str], heldout_subjects: Iterable[str]
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """§5.11's structural proof. There is no parameter that relaxes this."""
    fit = tuple(sorted(set(fit_subjects)))
    heldout = tuple(sorted(set(heldout_subjects)))
    if not fit:
        raise CalibrationPopulationError("a calibrator needs a fit population.")
    if not heldout:
        raise CalibrationPopulationError(
            "a calibrator fitted for J1 must name the population it will score; "
            "an unnamed held-out set cannot be proven disjoint."
        )
    overlap = sorted(set(fit) & set(heldout))
    if overlap:
        raise CalibrationPopulationError(
            "fit and held-out populations overlap, so a subject would be "
            f"scored by a calibrator fitted on itself: {overlap}."
        )
    return fit, heldout


def _stack(
    scores_by_subject: Mapping[str, Sequence[float]],
    labels_by_subject: Mapping[str, Sequence[int]],
    subjects: tuple[str, ...],
) -> tuple[list[float], list[int]]:
    """Rows in sorted-subject order, so the fit does not depend on dict order."""
    missing = [s for s in subjects if s not in scores_by_subject]
    if missing:
        raise CalibrationPopulationError(
            f"no scores supplied for fit subjects {missing}."
        )
    scores: list[float] = []
    labels: list[int] = []
    for subject in subjects:
        subject_scores = list(scores_by_subject[subject])
        subject_labels = list(labels_by_subject.get(subject, ()))
        if len(subject_scores) != len(subject_labels):
            raise CalibrationPopulationError(
                f"{subject!r} has {len(subject_scores)} scores and "
                f"{len(subject_labels)} labels; they must align one to one."
            )
        scores.extend(subject_scores)
        labels.extend(subject_labels)
    if not scores:
        raise CalibrationPopulationError("the fit population contributed no rows.")
    return scores, labels


class J1CalibrationFitter:
    """The `calibration_fitter` collaborator the capability gate requires.

    `fit_inner` and `fit_outer` are separate methods rather than one method with
    a level argument, because §5.10's whole point is that the two levels produce
    quantities that must not be interchangeable. A level *argument* would be a
    value a caller could pass wrongly.
    """

    def __init__(self, *, source_score_artifact_identity: str) -> None:
        if not source_score_artifact_identity.strip():
            raise CalibrationPopulationError(
                "a calibrated row must name the score artifact it came from; "
                "§5.11 requires the source score artifact identity."
            )
        self._source = source_score_artifact_identity

    def j1_execution_capability(self) -> J1CapabilityAttestation:
        return J1CapabilityAttestation(
            collaborator="calibration_fitter",
            execution_capable=True,
            detail="inherited U1 Platt fit with a proven population boundary",
        )

    def _fit(
        self,
        *,
        level: str,
        fit_subjects: Iterable[str],
        heldout_subjects: Iterable[str],
        scores_by_subject: Mapping[str, Sequence[float]],
        labels_by_subject: Mapping[str, Sequence[int]],
        outer_fold_index: int,
        inner_fold_index: int | None,
    ) -> FittedCalibration:
        fit, heldout = _require_disjoint(fit_subjects, heldout_subjects)
        scores, labels = _stack(scores_by_subject, labels_by_subject, fit)
        calibrator = fit_calibrator(
            logits=recover_logits(scores, delta=U1_CLAMP_DELTA),
            labels=labels,
            family=CALIBRATION_FAMILY,
            fit_subjects=fit,
            delta=U1_CLAMP_DELTA,
        )
        provenance = CalibrationProvenance(
            level=level,
            outer_fold_index=int(outer_fold_index),
            inner_fold_index=(
                None if inner_fold_index is None else int(inner_fold_index)
            ),
            fit_subjects=fit,
            fit_subjects_digest=subject_digest(fit),
            heldout_subjects=heldout,
            heldout_subjects_digest=subject_digest(heldout),
            calibrator_digest=_calibrator_digest(calibrator),
            calibration_protocol_identity=CALIBRATION_PROTOCOL_IDENTITY,
            calibration_protocol_sha256=CALIBRATION_PROTOCOL_SHA256,
            source_score_artifact_identity=self._source,
        )
        return FittedCalibration(calibrator=calibrator, provenance=provenance)

    def fit_inner(
        self,
        *,
        fit_subjects: Iterable[str],
        heldout_subjects: Iterable[str],
        scores_by_subject: Mapping[str, Sequence[float]],
        labels_by_subject: Mapping[str, Sequence[int]],
        outer_fold_index: int,
        inner_fold_index: int,
    ) -> FittedCalibration:
        """§5.3.1. Fitted on `INNER_FIT_j` only; scores `INNER_HELDOUT_j`."""
        return self._fit(
            level=INNER,
            fit_subjects=fit_subjects,
            heldout_subjects=heldout_subjects,
            scores_by_subject=scores_by_subject,
            labels_by_subject=labels_by_subject,
            outer_fold_index=outer_fold_index,
            inner_fold_index=inner_fold_index,
        )

    def fit_outer(
        self,
        *,
        fit_subjects: Iterable[str],
        heldout_subjects: Iterable[str],
        scores_by_subject: Mapping[str, Sequence[float]],
        labels_by_subject: Mapping[str, Sequence[int]],
        outer_fold_index: int,
    ) -> FittedCalibration:
        """§5.8 step 1 and §5.9. One calibrator on the 48; scores the eight."""
        return self._fit(
            level=OUTER,
            fit_subjects=fit_subjects,
            heldout_subjects=heldout_subjects,
            scores_by_subject=scores_by_subject,
            labels_by_subject=labels_by_subject,
            outer_fold_index=outer_fold_index,
            inner_fold_index=None,
        )
