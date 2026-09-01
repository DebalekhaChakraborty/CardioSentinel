"""The nested inner-OOF choreography, protocol sections 5.3 to 5.9.

The property this module exists to hold is narrow and easy to lose: an
evaluated subject's calibrated probability must come from a calibrator that saw
no row of that subject. A single calibrator fitted on all 48 outer-development
subjects and then used during inner selection would violate it silently, and the
field name `oof_calibrated_probability_p_t` would be false at the inner level.

So the fit population is passed explicitly at every step and asserted disjoint
from the population being scored. Disjointness is checked here rather than
documented, because the failure is invisible in the output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable


class ChoreographyError(RuntimeError):
    """A fit population that overlaps the population it is about to score."""


@dataclass
class InnerAssembly:
    """One candidate's complete 48-subject inner-OOF evidence."""

    candidate_id: str
    per_subject: dict[str, float] = field(default_factory=dict)
    calibrator_fit_subjects: dict[str, frozenset[str]] = field(
        default_factory=dict
    )

    def record(
        self, subject: str, value: float, fit_subjects: frozenset[str]
    ) -> None:
        if subject in self.per_subject:
            raise ChoreographyError(
                f"{subject!r} already has an inner-held-out evaluation for "
                f"{self.candidate_id!r}; exactly one is permitted."
            )
        if subject in fit_subjects:
            raise ChoreographyError(
                f"{subject!r} was scored by a calibrator fitted on itself."
            )
        self.per_subject[subject] = value
        self.calibrator_fit_subjects[subject] = fit_subjects

    def require_complete(self, expected: Iterable[str]) -> dict[str, float]:
        expected_set = set(expected)
        missing = expected_set - set(self.per_subject)
        extra = set(self.per_subject) - expected_set
        if missing or extra:
            raise ChoreographyError(
                f"inner assembly for {self.candidate_id!r} is not exactly one "
                f"evaluation per subject: missing={sorted(missing)} "
                f"extra={sorted(extra)}"
            )
        return dict(self.per_subject)


def run_inner_selection(
    *,
    inner_folds: tuple[tuple[str, ...], ...],
    development_subjects: tuple[str, ...],
    candidate_ids: tuple[str, ...],
    fit_calibrator: Callable[[frozenset[str]], object],
    score_subject: Callable[[str, str, object], float],
) -> dict[str, dict[str, float]]:
    """Per inner fold: fit on 40, score the held-out 8, assemble across six.

    `fit_calibrator` receives the fit population only. `score_subject` receives
    the calibrator produced from a population that excludes its subject.
    """
    assemblies = {cid: InnerAssembly(cid) for cid in candidate_ids}
    everyone = set(development_subjects)
    for held_out in inner_folds:
        fit_subjects = frozenset(everyone - set(held_out))
        if fit_subjects & set(held_out):
            raise ChoreographyError("inner fit and held-out populations overlap.")
        calibrator = fit_calibrator(fit_subjects)
        for subject in held_out:
            for cid in candidate_ids:
                assemblies[cid].record(
                    subject, score_subject(cid, subject, calibrator), fit_subjects
                )
    return {
        cid: assembly.require_complete(development_subjects)
        for cid, assembly in assemblies.items()
    }
