"""End-to-end synthetic qualification of the J1 choreography.

NON-SCIENTIFIC QUALIFICATION FIXTURE. Every value is fabricated. No real subject
identifier, measurement, annotation or model output appears here, and nothing
produced by this file is J1 evidence or may enter the experiment ledger.

The point is to exercise the real 7 x 8 and 6 x 8 geometry so the choreography's
disjointness properties are proven on the actual shape, not a toy one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest

from cardiosentinel.journal_extension.j1 import (
    candidates,
    choreography,
    folds,
    negative_capability,
    preflight,
    provenance,
    rows,
    statistics,
    visibility,
)

SUBJECTS = tuple(f"synthetic:sub{i:03d}" for i in range(56))


def _burdens() -> list[folds.SubjectBurden]:
    return [folds.SubjectBurden(s, (i * 7) % 5) for i, s in enumerate(SUBJECTS)]


@dataclass
class _DataSourceSpy:
    """Stands in for every physiological access. Must stay untouched."""

    calls: list[str] = field(default_factory=list)

    def open_subject(self, subject: str) -> None:
        self.calls.append(subject)

    @property
    def untouched(self) -> bool:
        return not self.calls


@dataclass
class _SyntheticCalibrator:
    """Remembers who it saw, so a violation is detectable rather than implied."""

    fit_subjects: frozenset[str]

    def probability(self, subject: str) -> float:
        if subject in self.fit_subjects:
            raise AssertionError(
                f"{subject} scored by a calibrator that saw it -- the exact "
                "defect the nested choreography exists to prevent"
            )
        return 0.5


# -- pre-access refusals must never touch the data source --------------------


def test_every_pre_access_refusal_leaves_the_data_source_untouched() -> None:
    spy = _DataSourceSpy()
    with pytest.raises(preflight.PreflightError):
        preflight.run_preflight(
            authorization_document=None,
            collaborators={},
            provenance_sink=None,
            repository_root=Path(preflight.J1_PACKAGE_ROOT).parents[3],
        )
    assert spy.untouched, "no physiological access before the attempt claim"


def test_the_latch_is_false_through_every_refusal() -> None:
    latch = visibility.ScientificVisibility()
    with pytest.raises(preflight.PreflightError):
        preflight.run_preflight(
            authorization_document=None,
            repository_root=Path(preflight.J1_PACKAGE_ROOT).parents[3],
            visibility=latch,
        )
    assert not latch.visible
    assert latch.failure_classification() == "INFRASTRUCTURE"


# -- the real geometry, on synthetic subjects --------------------------------


def test_synthetic_end_to_end_choreography() -> None:
    counters = negative_capability.ForbiddenCounters()

    outer = folds.allocate_folds(_burdens(), folds=7)
    assert len(outer) == 7 and all(len(f) == 8 for f in outer)

    assessment = outer[0]
    development = tuple(s for f in outer[1:] for s in f)
    assert len(development) == 48
    assert not set(assessment) & set(development)

    burdens = {b.subject_id: b for b in _burdens()}
    inner = folds.allocate_folds([burdens[s] for s in development], folds=6)
    assert len(inner) == 6 and all(len(f) == 8 for f in inner)

    stateful_ids = tuple(c.candidate_id for c in candidates.stateful_registry())
    memoryless_ids = tuple(
        c.candidate_id for c in candidates.memoryless_registry()
    )
    assert len(stateful_ids) == 12 and len(memoryless_ids) == 206

    # Inner selection: fit on 40, score the held-out 8, six times.
    def fit(fit_subjects: frozenset[str]) -> _SyntheticCalibrator:
        assert len(fit_subjects) == 40
        return _SyntheticCalibrator(fit_subjects)

    def score(cid: str, subject: str, calibrator: object) -> float:
        assert isinstance(calibrator, _SyntheticCalibrator)
        return calibrator.probability(subject) + (len(cid) % 7) / 100.0

    for arm_ids in (stateful_ids, memoryless_ids[:12]):
        assembly = choreography.run_inner_selection(
            inner_folds=inner,
            development_subjects=development,
            candidate_ids=arm_ids,
            fit_calibrator=fit,
            score_subject=score,
        )
        for cid in arm_ids:
            assert len(assembly[cid]) == 48, "one evaluation per subject"

    # Selection happens on inner OOF alone, and is fixed before outer assessment.
    selected_s = max(stateful_ids, key=lambda c: (len(c), c))
    selected_w = max(memoryless_ids[:12], key=lambda c: (len(c), c))
    frozen_ids = (selected_s, selected_w)

    # Outer: one arm-neutral row set, handed identically to both arms.
    outer_fit = frozenset(development)
    outer_calibrator = _SyntheticCalibrator(outer_fit)
    assessment_rows = {
        subject: rows.assessment_row(
            stable_id=f"{subject}:0",
            m2g_detector_score=0.3,
            detector_decision_d_t=False,
            outer_oof_p_t=rows.OuterOofCalibratedProbability(
                outer_calibrator.probability(subject)
            ),
            decision_error_uncertainty_u_t=0.2,
            s4d_temporal_evidence_s_t=0.4,
            score_present=True,
            elapsed_stream_seconds=10.0,
        )
        for subject in assessment
    }
    assert len(assessment_rows) == 8
    assert frozen_ids == (selected_s, selected_w), "IDs fixed before assessment"

    # Both arms receive the identical object, not a copy.
    for subject, row in assessment_rows.items():
        assert row is assessment_rows[subject]
        assert not hasattr(row, "elapsed_state_seconds")

    # Paired subject aggregation over the reference-defined primary cohort.
    eligible = [s for s in assessment if burdens[s].reference_episode_count > 0]
    stateful_f1 = {s: 0.62 for s in eligible}
    memoryless_f1 = {s: 0.55 for s in eligible}
    contrast = statistics.paired_contrast(stateful_f1, memoryless_f1)
    assert contrast.subjects == len(eligible)
    assert contrast.gate_a() in {"PASS", "MIXED", "FAIL"}

    # Negative-capability counters must all still be zero.
    assert counters.require_all_zero() == dict.fromkeys(
        negative_capability.COUNTER_NAMES, 0
    )


def test_a_calibrator_that_saw_its_own_subject_is_caught() -> None:
    """The guard must fail loudly, not silently produce a plausible number."""
    outer = folds.allocate_folds(_burdens(), folds=7)
    development = tuple(s for f in outer[1:] for s in f)
    burdens = {b.subject_id: b for b in _burdens()}
    inner = folds.allocate_folds([burdens[s] for s in development], folds=6)

    def leaky_fit(_fit_subjects: frozenset[str]) -> _SyntheticCalibrator:
        return _SyntheticCalibrator(frozenset(development))  # saw everyone

    with pytest.raises(AssertionError, match="calibrator that saw it"):
        choreography.run_inner_selection(
            inner_folds=inner,
            development_subjects=development,
            candidate_ids=("W-A-pt-0.9",),
            fit_calibrator=leaky_fit,
            score_subject=lambda _c, s, cal: cal.probability(s),
        )


def test_double_evaluation_of_a_subject_is_refused() -> None:
    assembly = choreography.InnerAssembly("W-A-pt-0.9")
    assembly.record("synthetic:sub000", 0.5, frozenset({"synthetic:sub001"}))
    with pytest.raises(choreography.ChoreographyError, match="already has"):
        assembly.record("synthetic:sub000", 0.6, frozenset({"synthetic:sub001"}))


def test_no_synthetic_artifact_is_written_to_a_canonical_run_path() -> None:
    root = Path(preflight.J1_PACKAGE_ROOT).parents[3]
    assert not (root / "cardiosentinel-runs" / "j1").exists()
    assert provenance.REQUIRED_ATTEMPT_ARTIFACTS
