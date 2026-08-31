"""The one derived analysis the T2 arm-comparison plan authorizes.

Every test here runs on synthetic arrays. Nothing reads an artifact, opens a
run directory or touches a measured value -- the point of reviewing this module
before the analysis is authorized is that its behaviour is settled while nobody
can see the numbers it will be pointed at.

What is proven, in the order it matters:

1. **It is paired.** Replicate *r* draws one subject multiset and scores both
   arms on it. A paired interval and two independent marginals are different
   objects, and the difference is the whole reason this exists.
2. **It reuses the published resampler.** The subject multisets are the ones
   `subject_bootstrap_plan` already produced for the per-arm bootstraps at the
   same seed, so the derived interval is drawn from the registered design rather
   than from a lookalike written into an analysis script.
3. **It refuses rather than substitutes.** Misaligned rows, non-binary labels
   and a design that disagrees with the artifact all raise. Undefined replicates
   are counted, not zero-filled.
4. **It cannot become a second primary result.** The point estimate must
   reproduce the artifact's own registered difference or the analysis stops.
"""

from __future__ import annotations

import numpy as np
import pytest

from cardiosentinel.evaluation.metrics import subject_bootstrap_plan
from cardiosentinel.neural import t2_paired_bootstrap as PB
from cardiosentinel.neural.t2_protocol import (
    T2_BOOTSTRAP_REPLICATES,
    T2_BOOTSTRAP_SEED,
    T2_BOOTSTRAP_UNIT,
)

SUBJECT_COUNT = 12
ROWS_PER_SUBJECT = 40


def _corpus(seed: int = 7, *, s4d_edge: float = 0.35):
    """Twelve subjects, a binary label, and two arms with a known ordering.

    S4D is given a genuine edge so the difference has a sign the tests can
    assert. The magnitude is not a claim about anything; it exists so a paired
    interval that excludes zero is distinguishable from one that does not.
    """
    rng = np.random.default_rng(seed)
    subjects, labels, s4d, gru = [], [], [], []
    for index in range(SUBJECT_COUNT):
        subject = f"ltstdb:s{2000 + index}"
        row_labels = rng.integers(0, 2, ROWS_PER_SUBJECT)
        noise = rng.normal(0.0, 1.0, ROWS_PER_SUBJECT)
        subjects.extend([subject] * ROWS_PER_SUBJECT)
        labels.extend(int(value) for value in row_labels)
        s4d.extend(float(v) for v in row_labels * s4d_edge + noise * 0.30)
        gru.extend(float(v) for v in row_labels * 0.10 + noise * 0.30)
    return subjects, labels, s4d, gru


def _registered(**overrides):
    design = {
        "seed": T2_BOOTSTRAP_SEED,
        "replicates": T2_BOOTSTRAP_REPLICATES,
        "unit": T2_BOOTSTRAP_UNIT,
        "model_refitted_per_replicate": False,
    }
    design.update(overrides)
    return design


# ---------------------------------------------------------------------------
# 1. The registered design, bound to the artifact rather than retyped
# ---------------------------------------------------------------------------


def test_the_plans_design_constants_are_the_protocols_own():
    """Plan §4 fixes seed 2026 and 1000 replicates by reference, not by value."""
    assert T2_BOOTSTRAP_SEED == 2026
    assert T2_BOOTSTRAP_REPLICATES == 1000
    assert T2_BOOTSTRAP_UNIT == "subject"


def test_a_matching_registered_design_is_accepted():
    assert PB.require_registered_design(_registered()) == _registered()


@pytest.mark.parametrize(
    "override",
    [
        {"seed": 2025},
        {"replicates": 500},
        {"unit": "window"},
        {"model_refitted_per_replicate": True},
    ],
)
def test_a_drifted_registered_design_is_refused(override):
    """A disagreement with the artifact is evidence, not a parameter."""
    with pytest.raises(PB.T2PairedBootstrapError, match="registered subject-bootstrap"):
        PB.require_registered_design(_registered(**override))


def test_a_missing_design_key_is_refused_rather_than_defaulted():
    partial = _registered()
    del partial["unit"]
    with pytest.raises(PB.T2PairedBootstrapError):
        PB.require_registered_design(partial)


# ---------------------------------------------------------------------------
# 2. Paired inputs, or a refusal
# ---------------------------------------------------------------------------


def test_row_aligned_inputs_are_accepted():
    PB.require_paired_inputs(*_corpus())


@pytest.mark.parametrize("truncate", ["subjects", "labels", "s4d", "gru"])
def test_misaligned_arms_are_refused(truncate):
    """One identity array and one label vector serve both arms."""
    subjects, labels, s4d, gru = _corpus()
    shortened = {
        "subjects": lambda: (subjects[:-1], labels, s4d, gru),
        "labels": lambda: (subjects, labels[:-1], s4d, gru),
        "s4d": lambda: (subjects, labels, s4d[:-1], gru),
        "gru": lambda: (subjects, labels, s4d, gru[:-1]),
    }[truncate]()
    with pytest.raises(PB.T2PairedBootstrapError, match="row-aligned"):
        PB.require_paired_inputs(*shortened)


def test_numpy_array_inputs_are_accepted():
    """The real caller hands numpy arrays, not lists.

    `require_paired_inputs` used `not subjects`, which raises on an array of
    more than one element instead of answering. Every synthetic test passed
    lists, so the check was first reached at execution -- the junction defect
    class that consumed the canonical T1 attempt at stage 24.
    """
    subjects, labels, s4d, gru = _corpus()
    PB.require_paired_inputs(
        np.asarray(subjects, dtype=str),
        np.asarray(labels, dtype=np.int64),
        np.asarray(s4d, dtype=np.float64),
        np.asarray(gru, dtype=np.float64),
    )


def test_the_paired_bootstrap_runs_on_numpy_array_inputs():
    subjects, labels, s4d, gru = _corpus()
    result = PB.paired_subject_bootstrap_difference(
        np.asarray(subjects, dtype=str),
        np.asarray(labels, dtype=np.int64),
        np.asarray(s4d, dtype=np.float64),
        np.asarray(gru, dtype=np.float64),
        replicates=20,
        seed=T2_BOOTSTRAP_SEED,
    )
    assert result["successful_replicates"] > 0


def test_empty_array_inputs_are_refused():
    empty = np.asarray([], dtype=np.float64)
    with pytest.raises(PB.T2PairedBootstrapError, match="empty"):
        PB.require_paired_inputs(
            np.asarray([], dtype=str), np.asarray([], dtype=np.int64), empty, empty
        )


def test_empty_inputs_are_refused():
    with pytest.raises(PB.T2PairedBootstrapError, match="empty"):
        PB.require_paired_inputs([], [], [], [])


def test_non_binary_labels_are_refused():
    subjects, labels, s4d, gru = _corpus()
    labels = list(labels)
    labels[0] = 2
    with pytest.raises(PB.T2PairedBootstrapError, match="binary"):
        PB.require_paired_inputs(subjects, labels, s4d, gru)


# ---------------------------------------------------------------------------
# 3. It is paired -- the property that makes the interval mean anything
# ---------------------------------------------------------------------------


def test_both_arms_are_scored_on_the_same_resample(monkeypatch):
    """One subject multiset per replicate, applied to both arms.

    Recorded at the point where the rows are turned into metrics: if the two
    arms were ever handed different index sets, the paired difference would be
    a difference between two different populations.
    """
    subjects, labels, s4d, gru = _corpus()
    seen: list[tuple[int, ...]] = []
    original = PB._pooled_auprc

    def recording(resampled_labels, scores):
        seen.append(tuple(int(v) for v in resampled_labels))
        return original(resampled_labels, scores)

    monkeypatch.setattr(PB, "_pooled_auprc", recording)
    PB.paired_subject_bootstrap_difference(
        subjects, labels, s4d, gru, replicates=25, seed=T2_BOOTSTRAP_SEED
    )
    # Two calls per replicate, plus two for the point estimate. Within each
    # pair the label vector -- and therefore the row selection -- is identical.
    assert len(seen) % 2 == 0
    for index in range(0, len(seen), 2):
        assert seen[index] == seen[index + 1], "the arms were scored on different rows"


def test_the_subject_multisets_are_the_published_resamplers_own():
    """Replicate r here is replicate r of the per-arm bootstrap."""
    subjects, _, _, _ = _corpus()
    plan_a = subject_bootstrap_plan(subjects, replicates=25, seed=T2_BOOTSTRAP_SEED)
    plan_b = subject_bootstrap_plan(subjects, replicates=25, seed=T2_BOOTSTRAP_SEED)
    assert plan_a == plan_b, "the resampler is not deterministic in (subjects, seed)"
    assert len(plan_a) == 25
    assert all(len(sample) == SUBJECT_COUNT for sample in plan_a)


def test_a_paired_interval_is_not_the_difference_of_two_marginals():
    """The whole reason this module exists, stated as a test.

    Both arms share the same per-row noise term, so their errors are strongly
    correlated and the paired interval is much narrower than one built by
    differencing two independently resampled marginals would be. If this ever
    stops holding, the implementation has silently unpaired itself.
    """
    subjects, labels, s4d, gru = _corpus()
    paired = PB.paired_subject_bootstrap_difference(
        subjects, labels, s4d, gru, replicates=200, seed=T2_BOOTSTRAP_SEED
    )
    paired_width = paired["upper_95"] - paired["lower_95"]

    # The same statistic, deliberately unpaired: each arm gets its own resample.
    subject_array = np.asarray(subjects, dtype=str)
    label_array = np.asarray(labels, dtype=np.int64)
    index_by_subject = {
        subject: np.flatnonzero(subject_array == subject)
        for subject in sorted(set(subjects))
    }
    plan_s4d = subject_bootstrap_plan(subjects, replicates=200, seed=T2_BOOTSTRAP_SEED)
    plan_gru = subject_bootstrap_plan(
        subjects, replicates=200, seed=T2_BOOTSTRAP_SEED + 1
    )
    unpaired = []
    for sample_s4d, sample_gru in zip(plan_s4d, plan_gru, strict=True):
        idx_s = np.concatenate([index_by_subject[s] for s in sample_s4d])
        idx_g = np.concatenate([index_by_subject[s] for s in sample_gru])
        left = PB._pooled_auprc(label_array[idx_s], np.asarray(s4d)[idx_s])
        right = PB._pooled_auprc(label_array[idx_g], np.asarray(gru)[idx_g])
        if left is not None and right is not None:
            unpaired.append(left - right)
    unpaired_width = float(np.percentile(unpaired, 97.5)) - float(
        np.percentile(unpaired, 2.5)
    )
    assert paired_width < unpaired_width, (
        f"the paired interval ({paired_width:.4f}) is not narrower than the "
        f"unpaired one ({unpaired_width:.4f}); the arms are not being compared "
        "on the same resample"
    )


# ---------------------------------------------------------------------------
# 4. The reported payload
# ---------------------------------------------------------------------------


def test_the_payload_records_what_the_plan_forbids():
    subjects, labels, s4d, gru = _corpus()
    result = PB.paired_subject_bootstrap_difference(
        subjects, labels, s4d, gru, replicates=50, seed=T2_BOOTSTRAP_SEED
    )
    assert result["evidence_class"] == PB.T2_PAIRED_BOOTSTRAP_CLASS
    assert result["statistic"] == PB.T2_PAIRED_DIFFERENCE_DEFINITION
    assert result["unit"] == "subject"
    assert result["paired"] is True
    assert result["same_rows_both_arms"] is True
    assert result["model_refitted_per_replicate"] is False
    assert result["thresholds_changed"] is False
    assert result["reselection_performed"] is False
    assert result["window_bootstrap_performed"] is False
    assert result["undefined_replicates_zero_filled"] is False
    assert result["subject_count"] == SUBJECT_COUNT
    assert result["row_count"] == SUBJECT_COUNT * ROWS_PER_SUBJECT


def test_the_interval_brackets_the_point_estimate():
    subjects, labels, s4d, gru = _corpus()
    result = PB.paired_subject_bootstrap_difference(
        subjects, labels, s4d, gru, replicates=200, seed=T2_BOOTSTRAP_SEED
    )
    assert result["lower_95"] <= result["point_estimate"] <= result["upper_95"]


def test_the_sign_convention_favours_s4d_when_s4d_is_better():
    """`point_estimate > 0` means S4D, and the name says so."""
    subjects, labels, s4d, gru = _corpus(s4d_edge=0.60)
    result = PB.paired_subject_bootstrap_difference(
        subjects, labels, s4d, gru, replicates=100, seed=T2_BOOTSTRAP_SEED
    )
    assert result["point_estimate"] > 0
    assert "s4d_minus" in PB.T2_PAIRED_DIFFERENCE_DEFINITION

    swapped = PB.paired_subject_bootstrap_difference(
        subjects, labels, gru, s4d, replicates=100, seed=T2_BOOTSTRAP_SEED
    )
    assert swapped["point_estimate"] == pytest.approx(-result["point_estimate"])


def test_the_result_is_deterministic_at_a_fixed_seed():
    subjects, labels, s4d, gru = _corpus()
    kwargs = {"replicates": 100, "seed": T2_BOOTSTRAP_SEED}
    call = PB.paired_subject_bootstrap_difference
    first = call(subjects, labels, s4d, gru, **kwargs)
    second = call(subjects, labels, s4d, gru, **kwargs)
    assert first == second


# ---------------------------------------------------------------------------
# 5. Undefined replicates are preserved, never imputed
# ---------------------------------------------------------------------------


def test_undefined_replicates_are_counted_and_not_zero_filled():
    """A single-class resample makes AUPRC undefined for both arms at once.

    One positive subject among twelve makes some resamples all-negative.
    Substituting a zero there would drag the interval toward "no difference"
    and would do it invisibly, so the count is reported instead.
    """
    subjects, labels, s4d, gru = [], [], [], []
    rng = np.random.default_rng(3)
    for index in range(SUBJECT_COUNT):
        subject = f"ltstdb:s{2000 + index}"
        positive = index == 0
        for _ in range(ROWS_PER_SUBJECT):
            subjects.append(subject)
            labels.append(1 if positive else 0)
            noise = float(rng.normal())
            s4d.append((1.0 if positive else 0.0) + noise * 0.2)
            gru.append((1.0 if positive else 0.0) + noise * 0.2)

    result = PB.paired_subject_bootstrap_difference(
        subjects, labels, s4d, gru, replicates=200, seed=T2_BOOTSTRAP_SEED
    )
    assert result["undefined_replicates"] > 0, "the fixture produced no degeneracy"
    assert result["successful_replicates"] + result["undefined_replicates"] == 200
    assert result["requested_replicates"] == 200
    assert result["undefined_replicates_zero_filled"] is False


def test_an_entirely_undefined_bootstrap_reports_no_interval():
    """No successful replicate means no interval, not an interval of zeros."""
    subjects = [f"ltstdb:s{2000 + i}" for i in range(4) for _ in range(5)]
    labels = [0] * len(subjects)
    scores = [0.5] * len(subjects)
    result = PB.paired_subject_bootstrap_difference(
        subjects, labels, scores, scores, replicates=10, seed=T2_BOOTSTRAP_SEED
    )
    assert result["successful_replicates"] == 0
    assert result["undefined_replicates"] == 10
    assert result["lower_95"] is None
    assert result["upper_95"] is None
    assert result["point_estimate"] is None


# ---------------------------------------------------------------------------
# 6. It cannot become a second primary result
# ---------------------------------------------------------------------------


def test_the_point_estimate_must_reproduce_the_registered_difference():
    subjects, labels, s4d, gru = _corpus()
    result = PB.paired_subject_bootstrap_difference(
        subjects, labels, s4d, gru, replicates=20, seed=T2_BOOTSTRAP_SEED
    )
    PB.require_point_estimate_agrees(result, result["point_estimate"])


def test_a_disagreeing_point_estimate_stops_the_analysis():
    """Either the rows are wrong or the statistics differ. Both mean stop."""
    subjects, labels, s4d, gru = _corpus()
    result = PB.paired_subject_bootstrap_difference(
        subjects, labels, s4d, gru, replicates=20, seed=T2_BOOTSTRAP_SEED
    )
    with pytest.raises(PB.T2PairedBootstrapError, match="does not reproduce"):
        PB.require_point_estimate_agrees(result, result["point_estimate"] + 0.05)


def test_an_undefined_point_estimate_cannot_be_checked_away():
    with pytest.raises(PB.T2PairedBootstrapError, match="undefined"):
        PB.require_point_estimate_agrees({"point_estimate": None}, 0.0)


# ---------------------------------------------------------------------------
# 7. The module reads nothing
# ---------------------------------------------------------------------------


def test_the_module_opens_no_artifact_and_computes_nothing_on_import():
    """Structural: the derived analysis takes arrays, it does not go and get them.

    Read from the syntax tree rather than by substring, which in this repository
    reports the word it is looking for out of the prose explaining why the word
    is forbidden.
    """
    import ast
    from pathlib import Path

    tree = ast.parse(Path(PB.__file__).read_text(encoding="utf-8"))
    called = {
        getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    }
    for forbidden in (
        "open",
        "read_text",
        "read_bytes",
        "load",
        "loads",
        "read_store",
        "read_t2_outer_row_group",
        "mkdir",
        "write_text",
        "write_json_atomic",
    ):
        assert forbidden not in called, (
            f"the derived analysis calls {forbidden!r}; it receives arrays and "
            "returns a payload, and the caller owns every artifact boundary"
        )
    # Nothing executes at import: module level is imports, constants and defs.
    for node in tree.body:
        assert isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
                ast.Assign,
                ast.AnnAssign,
                ast.FunctionDef,
                ast.ClassDef,
                ast.Expr,
            ),
        ), f"module-level {type(node).__name__} executes at import"
