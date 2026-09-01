"""Qualification of the J1 calibration fitter and threshold deriver.

NON-SCIENTIFIC QUALIFICATION FIXTURE. Every score, label and subject below is
fabricated. No physiological data, annotation or reference-episode count is
read, no real fold is built, and nothing here authorizes J1.
"""

from __future__ import annotations

import inspect
import math

import pytest

from cardiosentinel.journal_extension.j1.calibration import (
    CALIBRATION_PROTOCOL_IDENTITY,
    CalibrationPopulationError,
    J1CalibrationFitter,
    subject_digest,
)
from cardiosentinel.journal_extension.j1.candidates import (
    MemorylessCandidate,
    StatefulCandidate,
    memoryless_registry,
    stateful_registry,
)
from cardiosentinel.journal_extension.j1.thresholds import (
    J1ThresholdDeriver,
    ThresholdDerivationError,
    ThresholdRow,
    empirical_order_statistic,
    threshold_population,
)

FIT_SUBJECTS = ("s01", "s02", "s03", "s04")
HELDOUT_SUBJECTS = ("s05", "s06")


# -- the order statistic, against the inherited implementation --------------


def _inherited_order_statistic():
    """Imported here, not in the J1 package: `t1_protocol`'s operating-point
    entry points are forbidden to J1 modules by name. A test may compare
    against the inherited rule; a J1 module may not reach for it."""
    from cardiosentinel.neural.t1_protocol import empirical_order_statistic as inherited

    return inherited


@pytest.mark.parametrize("quantile", [0.5, 0.90, 0.95, 0.975, 0.99, 0.995, 1.0])
def test_the_order_statistic_matches_the_inherited_rule(quantile: float) -> None:
    """The re-statement is only honest if it agrees where both are defined."""
    values = [0.11, 0.93, 0.42, 0.42, 0.77, 0.05, 0.61, 0.88, 0.30, 0.55]
    ids = [f"r{i:02d}" for i in range(len(values))]
    inherited = _inherited_order_statistic()
    assert empirical_order_statistic(values, ids, quantile) == inherited(
        values, ids, quantile
    )


def test_the_order_statistic_does_not_interpolate() -> None:
    values = [1.0, 2.0, 3.0, 4.0]
    ids = ["a", "b", "c", "d"]
    assert empirical_order_statistic(values, ids, 0.5) == 2.0
    assert empirical_order_statistic(values, ids, 0.75) == 3.0
    assert empirical_order_statistic(values, ids, 0.99) == 4.0


def test_the_order_statistic_is_independent_of_input_order() -> None:
    values = [0.4, 0.1, 0.9, 0.4, 0.7]
    ids = ["e", "b", "a", "c", "d"]
    forward = empirical_order_statistic(values, ids, 0.6)
    reversed_ = empirical_order_statistic(values[::-1], ids[::-1], 0.6)
    assert forward == reversed_


@pytest.mark.parametrize("quantile", [0.0, -0.1, 1.1])
def test_a_quantile_outside_the_unit_interval_is_refused(quantile: float) -> None:
    with pytest.raises(ThresholdDerivationError, match="outside"):
        empirical_order_statistic([1.0], ["a"], quantile)


def test_an_empty_population_has_no_order_statistic() -> None:
    with pytest.raises(ThresholdDerivationError, match="non-empty"):
        empirical_order_statistic([], [], 0.9)


# -- the threshold population, section 5.4 ---------------------------------


def _row(subject: str, index: int, **overrides: object) -> ThresholdRow:
    base: dict[str, object] = {
        "stable_id": f"{subject}-{index:03d}",
        "subject_id": subject,
        "is_primary": True,
        "is_background_negative": True,
        "score_present": True,
        "fit_calibrated_probability": 0.10 + 0.01 * index,
        "s4d_temporal_evidence_s_t": 0.20 + 0.005 * index,
        "m2g_detector_score": 0.30 + 0.002 * index,
    }
    base.update(overrides)
    return ThresholdRow(**base)  # type: ignore[arg-type]


def _fit_rows() -> list[ThresholdRow]:
    return [
        _row(subject, index)
        for subject in FIT_SUBJECTS
        for index in range(1, 26)
    ]


def test_a_held_out_row_in_the_threshold_population_is_a_hard_failure() -> None:
    """Dropping it silently would hide that the caller built the wrong set."""
    rows = [*_fit_rows(), _row("s05", 1)]
    with pytest.raises(ThresholdDerivationError, match="not in the fit population"):
        threshold_population(rows, fit_subjects=FIT_SUBJECTS)


@pytest.mark.parametrize(
    "field", ["is_primary", "is_background_negative", "score_present"]
)
def test_all_three_admissibility_terms_are_required(field: str) -> None:
    rows = [_row("s01", i, **{field: False}) for i in range(1, 6)]
    with pytest.raises(ThresholdDerivationError, match="PRIMARY"):
        threshold_population(rows, fit_subjects=FIT_SUBJECTS)


def test_inadmissible_rows_are_excluded_but_admissible_ones_kept() -> None:
    rows = [*_fit_rows(), _row("s01", 99, score_present=False)]
    kept = threshold_population(rows, fit_subjects=FIT_SUBJECTS)
    assert len(kept) == len(_fit_rows())


def test_a_threshold_population_needs_an_explicit_fit_set() -> None:
    with pytest.raises(ThresholdDerivationError, match="explicit fit-subject set"):
        threshold_population(_fit_rows(), fit_subjects=())


# -- derivation, both arms -------------------------------------------------


def test_stateful_thresholds_are_the_four_frozen_quantities() -> None:
    deriver = J1ThresholdDeriver()
    candidate = StatefulCandidate(q_watch=0.90, q_event=0.99, profile="MED")
    derived = deriver.derive(
        candidate, rows=_fit_rows(), fit_subjects=FIT_SUBJECTS
    )
    assert sorted(derived) == ["p_event", "p_watch", "s_event", "s_watch"]
    assert derived["p_event"] >= derived["p_watch"]
    assert derived["s_event"] >= derived["s_watch"]


def test_a_stateful_threshold_is_the_quantile_of_the_fit_population() -> None:
    deriver = J1ThresholdDeriver()
    population = threshold_population(_fit_rows(), fit_subjects=FIT_SUBJECTS)
    expected = empirical_order_statistic(
        [r.fit_calibrated_probability for r in population],
        [r.stable_id for r in population],
        0.95,
    )
    derived = deriver.derive(
        StatefulCandidate(q_watch=0.95, q_event=0.995, profile="FAST"),
        rows=_fit_rows(),
        fit_subjects=FIT_SUBJECTS,
    )
    assert derived["p_watch"] == expected


def test_a_detector_only_candidate_derives_no_quantile_threshold() -> None:
    """`d_t` is the inherited binary decision; it needs no new threshold."""
    deriver = J1ThresholdDeriver()
    only_dt = MemorylessCandidate("B", (), (), uses_d_t=True)
    assert deriver.derive(only_dt, rows=_fit_rows(), fit_subjects=FIT_SUBJECTS) == {}


def test_a_matched_level_family_derives_one_threshold_per_signal() -> None:
    """G and H name three signals at a single level; a strict zip would
    derive one threshold and leave the rule reading two missing keys."""
    deriver = J1ThresholdDeriver()
    triple = MemorylessCandidate("G", ("pt", "st", "m2g"), (0.99,))
    derived = deriver.derive(triple, rows=_fit_rows(), fit_subjects=FIT_SUBJECTS)
    assert sorted(derived) == ["m2g", "pt", "st"]


def test_a_pairwise_family_honours_its_two_independent_levels() -> None:
    deriver = J1ThresholdDeriver()
    low = deriver.derive(
        MemorylessCandidate("C", ("pt", "st"), (0.90, 0.90)),
        rows=_fit_rows(),
        fit_subjects=FIT_SUBJECTS,
    )
    high = deriver.derive(
        MemorylessCandidate("C", ("pt", "st"), (0.995, 0.90)),
        rows=_fit_rows(),
        fit_subjects=FIT_SUBJECTS,
    )
    assert high["pt"] > low["pt"]
    assert high["st"] == low["st"]


def test_every_frozen_candidate_in_both_registries_derives() -> None:
    """12 + 206. A candidate the deriver cannot serve is an unrunnable fold."""
    deriver = J1ThresholdDeriver()
    rows = _fit_rows()
    for candidate in (*stateful_registry(), *memoryless_registry()):
        derived = deriver.derive(candidate, rows=rows, fit_subjects=FIT_SUBJECTS)
        assert isinstance(derived, dict)
        assert all(math.isfinite(v) for v in derived.values())


def test_a_mismatched_signal_and_level_count_is_refused() -> None:
    deriver = J1ThresholdDeriver()
    malformed = MemorylessCandidate("C", ("pt", "st"), (0.9, 0.95, 0.99))
    with pytest.raises(ThresholdDerivationError, match="must correspond"):
        deriver.derive(malformed, rows=_fit_rows(), fit_subjects=FIT_SUBJECTS)


# -- calibration: the population boundary, sections 5.3, 5.9 and 5.11 ------


def _scores_and_labels(subjects: tuple[str, ...]) -> tuple[dict, dict]:
    scores: dict[str, list[float]] = {}
    labels: dict[str, list[int]] = {}
    for s_index, subject in enumerate(subjects):
        row_scores = []
        row_labels = []
        for index in range(24):
            value = 0.05 + 0.035 * ((index + s_index) % 25)
            row_scores.append(min(max(value, 0.01), 0.99))
            # Deliberately not perfectly separable: a separable fixture drives
            # the Platt fit to saturation, where every calibrated value is
            # exactly 0.0 or 1.0 and the boundary tests prove nothing.
            label = 1 if value > 0.45 else 0
            row_labels.append(1 - label if (index + s_index) % 7 == 0 else label)
        scores[subject] = row_scores
        labels[subject] = row_labels
    return scores, labels


def _fitted():
    fitter = J1CalibrationFitter(source_score_artifact_identity="synthetic-m2g-v0")
    scores, labels = _scores_and_labels(FIT_SUBJECTS + HELDOUT_SUBJECTS)
    return fitter.fit_inner(
        fit_subjects=FIT_SUBJECTS,
        heldout_subjects=HELDOUT_SUBJECTS,
        scores_by_subject=scores,
        labels_by_subject=labels,
        outer_fold_index=0,
        inner_fold_index=3,
    )


def test_a_fit_produces_a_monotonic_calibrator() -> None:
    fitted = _fitted()
    assert fitted.calibrator.a > 0.0
    assert fitted.calibrator.fit_subjects == FIT_SUBJECTS


def test_overlapping_fit_and_held_out_populations_are_refused() -> None:
    fitter = J1CalibrationFitter(source_score_artifact_identity="synthetic-m2g-v0")
    scores, labels = _scores_and_labels(FIT_SUBJECTS + HELDOUT_SUBJECTS)
    with pytest.raises(CalibrationPopulationError, match="fitted on itself"):
        fitter.fit_inner(
            fit_subjects=FIT_SUBJECTS,
            heldout_subjects=("s04", "s05"),
            scores_by_subject=scores,
            labels_by_subject=labels,
            outer_fold_index=0,
            inner_fold_index=1,
        )


@pytest.mark.parametrize("method", ["fit_inner", "fit_outer"])
def test_no_parameter_relaxes_the_population_boundary(method: str) -> None:
    signature = inspect.signature(getattr(J1CalibrationFitter, method))
    for forbidden in ("force", "allow_overlap", "strict", "skip_disjointness"):
        assert forbidden not in signature.parameters


def test_a_fit_subject_cannot_be_given_a_held_out_probability() -> None:
    """The name would be false: that calibrator saw the subject's rows."""
    fitted = _fitted()
    with pytest.raises(CalibrationPopulationError, match="held-out"):
        fitted.oof_probabilities("s01", [0.4, 0.6])


def test_a_held_out_subject_cannot_be_given_a_fit_side_probability() -> None:
    fitted = _fitted()
    with pytest.raises(CalibrationPopulationError, match="fit"):
        fitted.fit_side_probabilities("s05", [0.4, 0.6])


def test_held_out_probabilities_are_produced_for_the_held_out_population() -> None:
    fitted = _fitted()
    values = fitted.oof_probabilities("s05", [0.2, 0.5, 0.8])
    assert len(values) == 3
    assert all(0.0 < v < 1.0 for v in values)


def test_the_provenance_carries_every_binding_section_5_11_requires() -> None:
    attestation = _fitted().provenance.as_attestation()
    for field in (
        "outer_fold_index",
        "inner_fold_index",
        "fit_subjects_digest",
        "heldout_subjects_digest",
        "calibrator_digest",
        "calibration_protocol_identity",
        "source_score_artifact_identity",
        "fit_heldout_disjoint",
    ):
        assert field in attestation
    assert attestation["calibration_protocol_identity"] == CALIBRATION_PROTOCOL_IDENTITY
    assert attestation["fit_heldout_disjoint"] is True


def test_an_outer_fit_records_no_inner_fold_index() -> None:
    fitter = J1CalibrationFitter(source_score_artifact_identity="synthetic-m2g-v0")
    scores, labels = _scores_and_labels(FIT_SUBJECTS + HELDOUT_SUBJECTS)
    fitted = fitter.fit_outer(
        fit_subjects=FIT_SUBJECTS,
        heldout_subjects=HELDOUT_SUBJECTS,
        scores_by_subject=scores,
        labels_by_subject=labels,
        outer_fold_index=2,
    )
    assert fitted.provenance.inner_fold_index is None
    assert fitted.provenance.level == "outer"


def test_the_subject_digest_is_order_independent_and_membership_sensitive() -> None:
    assert subject_digest(["b", "a"]) == subject_digest(["a", "b"])
    assert subject_digest(["a", "b"]) != subject_digest(["a", "b", "c"])


def test_a_calibrated_row_must_name_its_source_score_artifact() -> None:
    with pytest.raises(CalibrationPopulationError, match="source score artifact"):
        J1CalibrationFitter(source_score_artifact_identity="   ")


def test_misaligned_scores_and_labels_are_refused() -> None:
    fitter = J1CalibrationFitter(source_score_artifact_identity="synthetic-m2g-v0")
    scores, labels = _scores_and_labels(FIT_SUBJECTS + HELDOUT_SUBJECTS)
    labels["s01"] = labels["s01"][:-1]
    with pytest.raises(CalibrationPopulationError, match="align one to one"):
        fitter.fit_inner(
            fit_subjects=FIT_SUBJECTS,
            heldout_subjects=HELDOUT_SUBJECTS,
            scores_by_subject=scores,
            labels_by_subject=labels,
            outer_fold_index=0,
            inner_fold_index=0,
        )
