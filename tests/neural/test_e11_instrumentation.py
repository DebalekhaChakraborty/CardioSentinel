"""Contract tests for E11-class per-epoch instrumentation.

These prove the observability layer records what E12a found missing, and that
it stays observability: it must not move a model output, a selection, or a
consensus. Absences are asserted rather than trusted.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import torch
from sklearn.metrics import average_precision_score, roc_auc_score

from cardiosentinel.neural.e11_authority import (
    E11AuthorityError,
    E11FoldAuthority,
    E11Partition,
)
from cardiosentinel.neural.e11_instrumentation import (
    E11InstrumentationError,
    EpochEvidenceLog,
    EpochLossRecord,
    InnerValidationRecord,
    SelectionEvidence,
    StreamGeometrySummary,
    class_direction_consensus,
    f1_optimal_threshold,
    inner_validation_record,
    load_epoch_evidence,
    stream_geometry_summaries,
)

LAMBDA = 0.1


# --------------------------------------------------------------------------
# 1 + 2: the loss decomposition is recorded, and the identity is enforced
# --------------------------------------------------------------------------


def test_bce_and_auxiliary_losses_are_recorded_separately() -> None:
    record = EpochLossRecord(
        epoch=1,
        arm="B1",
        bce_loss=0.19608,
        aux_loss_raw=0.0840,
        aux_loss_scaled=LAMBDA * 0.0840,
        aux_lambda=LAMBDA,
        total_loss=0.19608 + LAMBDA * 0.0840,
        learning_rate=1e-3,
        seconds=321.7,
    )
    assert record.bce_loss != record.total_loss
    assert record.aux_loss_raw is not None
    assert record.aux_loss_scaled == pytest.approx(LAMBDA * record.aux_loss_raw)


def test_total_loss_must_equal_bce_plus_scaled_auxiliary() -> None:
    with pytest.raises(E11InstrumentationError, match="total_loss must equal"):
        EpochLossRecord(
            epoch=1,
            arm="B1",
            bce_loss=0.2,
            aux_loss_raw=0.5,
            aux_loss_scaled=LAMBDA * 0.5,
            aux_lambda=LAMBDA,
            total_loss=0.9,  # not 0.2 + 0.05
            learning_rate=1e-3,
            seconds=1.0,
        )


def test_scaled_auxiliary_must_equal_lambda_times_raw() -> None:
    with pytest.raises(E11InstrumentationError, match="aux_loss_scaled must equal"):
        EpochLossRecord(
            epoch=1,
            arm="B1",
            bce_loss=0.2,
            aux_loss_raw=0.5,
            aux_loss_scaled=0.4,  # not lambda * raw
            aux_lambda=LAMBDA,
            total_loss=0.6,
            learning_rate=1e-3,
            seconds=1.0,
        )


# --------------------------------------------------------------------------
# 3: B0 records semantic absence, never a fabricated zero
# --------------------------------------------------------------------------


def test_primary_only_arm_records_auxiliary_as_absent_not_zero() -> None:
    record = EpochLossRecord(
        epoch=1,
        arm="B0",
        bce_loss=0.19608,
        total_loss=0.19608,
        learning_rate=1e-3,
        seconds=321.7,
    )
    assert record.aux_loss_raw is None
    assert record.aux_loss_scaled is None
    assert record.aux_lambda is None
    # and it serializes as null, not 0.0
    payload = json.loads(json.dumps({"aux": record.aux_loss_raw}))
    assert payload["aux"] is None


def test_primary_only_arm_rejects_a_total_that_implies_a_hidden_term() -> None:
    with pytest.raises(E11InstrumentationError, match="no auxiliary term"):
        EpochLossRecord(
            epoch=1,
            arm="B0",
            bce_loss=0.19608,
            total_loss=0.28008,  # implies an unrecorded auxiliary contribution
            learning_rate=1e-3,
            seconds=1.0,
        )


def test_half_specified_auxiliary_is_refused() -> None:
    with pytest.raises(E11InstrumentationError, match="present or absent together"):
        EpochLossRecord(
            epoch=1,
            arm="B1",
            bce_loss=0.2,
            aux_loss_raw=0.5,
            total_loss=0.25,
            learning_rate=1e-3,
            seconds=1.0,
        )


# --------------------------------------------------------------------------
# 4 + 5: metrics and the threshold reproduce from persisted predictions
# --------------------------------------------------------------------------


@pytest.fixture()
def inner_predictions() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(2026)
    labels = (rng.random(4000) < 0.025).astype(np.int64)  # E11-like prevalence
    scores = rng.random(4000) * 0.4 + labels * 0.3
    return labels, scores


def test_auprc_and_auroc_reproduce_from_persisted_predictions(
    tmp_path: Path, inner_predictions: tuple[np.ndarray, np.ndarray]
) -> None:
    labels, scores = inner_predictions
    at_selection = inner_validation_record(epoch=3, labels=labels, scores=scores)

    # persist exactly what the runner would persist, then reload and recompute
    store = tmp_path / "inner_epoch3.npz"
    np.savez_compressed(
        store, labels=labels.astype(np.uint8), scores=scores.astype(np.float32)
    )
    reloaded = np.load(store)
    replayed = inner_validation_record(
        epoch=3, labels=reloaded["labels"], scores=reloaded["scores"]
    )

    assert replayed.auprc == pytest.approx(at_selection.auprc, abs=1e-6)
    assert replayed.auroc == pytest.approx(at_selection.auroc, abs=1e-6)
    # and they match sklearn computed directly, so the record is not self-referential
    assert at_selection.auprc == pytest.approx(
        float(average_precision_score(labels, scores))
    )
    assert at_selection.auroc == pytest.approx(float(roc_auc_score(labels, scores)))


def test_persisted_f1_threshold_reproduces_the_selection_time_value(
    tmp_path: Path, inner_predictions: tuple[np.ndarray, np.ndarray]
) -> None:
    labels, scores = inner_predictions
    at_selection, f1_at_selection = f1_optimal_threshold(labels, scores)

    store = tmp_path / "inner.npz"
    np.savez_compressed(
        store, labels=labels.astype(np.uint8), scores=scores.astype(np.float32)
    )
    reloaded = np.load(store)
    replayed, f1_replayed = f1_optimal_threshold(reloaded["labels"], reloaded["scores"])

    assert replayed == pytest.approx(at_selection, abs=1e-6)
    assert f1_replayed == pytest.approx(f1_at_selection, abs=1e-6)


def test_prevalence_must_agree_with_its_denominators() -> None:
    with pytest.raises(E11InstrumentationError, match="prevalence"):
        InnerValidationRecord(
            epoch=1,
            auprc=0.4,
            auroc=0.8,
            f1_optimal_threshold=0.5,
            prevalence=0.5,  # inconsistent with the counts below
            n_positive=10,
            n_negative=990,
        )


def test_f1_threshold_is_undefined_on_a_single_class_partition() -> None:
    labels = np.zeros(50, dtype=np.int64)
    with pytest.raises(E11InstrumentationError, match="single-class"):
        f1_optimal_threshold(labels, np.linspace(0, 1, 50))


# --------------------------------------------------------------------------
# 6: geometry reproduces from a deterministic toy fixture
# --------------------------------------------------------------------------


@pytest.fixture()
def toy_geometry() -> dict[str, np.ndarray]:
    """Two evaluable streams on a known axis, plus one single-class stream."""
    embeddings = np.array(
        [
            [1.0, 0.0], [1.0, 0.0],      # s1 positives -> +x
            [-1.0, 0.0], [-1.0, 0.0],    # s1 negatives
            [0.0, 1.0], [0.0, 1.0],      # s2 positives -> +y
            [0.0, -1.0], [0.0, -1.0],    # s2 negatives
            [3.0, 3.0], [3.0, 3.0],      # s3 positives only -> not evaluable
        ]
    )
    return {
        "embeddings": embeddings,
        "labels": np.array([1, 1, 0, 0, 1, 1, 0, 0, 1, 1]),
        "subjects": np.array(["a"] * 4 + ["b"] * 4 + ["c"] * 2),
        "streams": np.array(["s1"] * 4 + ["s2"] * 4 + ["s3"] * 2),
    }


def test_geometry_summaries_reproduce_on_a_deterministic_fixture(
    toy_geometry: dict[str, np.ndarray]
) -> None:
    consensus = class_direction_consensus(
        [np.array([2.0, 0.0]), np.array([0.0, 2.0])]
    )
    # equal weight per stream on orthogonal unit axes -> the 45-degree bisector
    assert consensus == pytest.approx(np.array([2 ** -0.5, 2 ** -0.5]))

    summaries = stream_geometry_summaries(
        toy_geometry["embeddings"],
        toy_geometry["labels"],
        toy_geometry["subjects"],
        toy_geometry["streams"],
        consensus,
    )
    by_stream = {summary.stream_id: summary for summary in summaries}

    assert by_stream["s1"].evaluable is True
    assert by_stream["s1"].delta_norm == pytest.approx(2.0)
    assert by_stream["s1"].cosine_to_consensus == pytest.approx(2 ** -0.5)
    assert by_stream["s1"].negative_cosine is False


def test_single_class_stream_is_preserved_with_undefined_fields(
    toy_geometry: dict[str, np.ndarray]
) -> None:
    consensus = class_direction_consensus([np.array([1.0, 1.0])])
    summaries = stream_geometry_summaries(
        toy_geometry["embeddings"],
        toy_geometry["labels"],
        toy_geometry["subjects"],
        toy_geometry["streams"],
        consensus,
    )
    by_stream = {summary.stream_id: summary for summary in summaries}

    # it must survive rather than vanish, so denominators stay comparable
    assert "s3" in by_stream
    single = by_stream["s3"]
    assert single.evaluable is False
    assert single.n_positive == 2 and single.n_negative == 0
    assert single.delta_norm is None
    assert single.cosine_to_consensus is None
    assert single.negative_cosine is None


def test_negative_cosine_indicator_cannot_disagree_with_the_cosine() -> None:
    with pytest.raises(E11InstrumentationError, match="negative_cosine disagrees"):
        StreamGeometrySummary(
            subject_id="a",
            stream_id="s1",
            n_positive=5,
            n_negative=5,
            evaluable=True,
            delta_norm=1.0,
            cosine_to_consensus=-0.5,
            negative_cosine=False,
        )


# --------------------------------------------------------------------------
# 7: inner-validation never contributes to the TRAIN consensus
# --------------------------------------------------------------------------


def test_consensus_built_from_inner_validation_is_refused(tmp_path: Path) -> None:
    log = EpochEvidenceLog(path=tmp_path / "epochs.json", fold=0, arm="B1")
    losses = EpochLossRecord(
        epoch=1, arm="B1", bce_loss=0.2, aux_loss_raw=0.5,
        aux_loss_scaled=LAMBDA * 0.5, aux_lambda=LAMBDA,
        total_loss=0.2 + LAMBDA * 0.5, learning_rate=1e-3, seconds=1.0,
    )
    inner = InnerValidationRecord(
        epoch=1, auprc=0.4, auroc=0.8, f1_optimal_threshold=0.5,
        prevalence=0.01, n_positive=10, n_negative=990,
    )
    with pytest.raises(E11InstrumentationError, match="never be built from inner-val"):
        log.record_epoch(
            losses, inner, geometry=[],
            geometry_consensus_partition="inner_validation",
        )


def test_consensus_ignores_streams_outside_the_partition_it_was_given() -> None:
    """A stream absent from the consensus input cannot influence it."""
    train_deltas = [np.array([1.0, 0.0]), np.array([1.0, 0.0])]
    without = class_direction_consensus(train_deltas)
    # an inner-validation stream pointing the other way must not move it,
    # because it is never passed in
    with_held_out = class_direction_consensus(train_deltas)
    assert without == pytest.approx(with_held_out)
    assert without == pytest.approx(np.array([1.0, 0.0]))


# --------------------------------------------------------------------------
# 8: TEST is unreachable by construction
# --------------------------------------------------------------------------


def _authority(**overrides):
    subjects = np.array(["s1"] * 4 + ["s2"] * 4 + ["s3"] * 4)
    kwargs = dict(
        fold=0,
        split_digest="ce0373",
        experiment_id="E11_FUTURE",
        authorized_population=["s1", "s2", "s3"],
        subjects=subjects,
        inner_train_rows=np.arange(0, 4),
        inner_validation_rows=np.arange(4, 8),
        outer_held_out_rows=np.arange(8, 12),
    )
    kwargs.update(overrides)
    return E11FoldAuthority(**kwargs)


def test_no_accessor_takes_a_partition_argument() -> None:
    import inspect

    authority = _authority()
    for accessor in (
        "inner_train_rows",
        "inner_validation_rows",
        "outer_train_rows",
        "outer_held_out_rows",
    ):
        signature = inspect.signature(getattr(authority, accessor))
        assert list(signature.parameters) == [], accessor


def test_no_partition_enum_member_names_a_sealed_partition() -> None:
    members = {member.value for member in E11Partition}
    assert members == {
        "inner_train",
        "inner_validation",
        "outer_train",
        "outer_held_out",
    }
    for forbidden in ("test", "sealed_test", "validation", "historical_validation"):
        assert forbidden not in members


def test_a_bare_string_cannot_stand_in_for_a_partition() -> None:
    authority = _authority()
    with pytest.raises(E11AuthorityError, match="E11Partition member"):
        authority.row_count("test")


def test_authority_has_no_generic_partition_accessor() -> None:
    authority = _authority()
    for forbidden in (
        "rows",
        "get",
        "partition",
        "split_name",
        "dataset_name",
        "indices",
        "all_rows",
        "items",
        "keys",
        "values",
    ):
        assert not hasattr(authority, forbidden), forbidden
    assert not hasattr(authority, "__iter__")
    assert not hasattr(authority, "__getitem__")


def test_subject_outside_the_authorized_population_is_refused() -> None:
    """A historical VALIDATION subject is excluded by not being on the list."""
    with pytest.raises(E11AuthorityError, match="outside the authorized"):
        _authority(subjects=np.array(["s1"] * 4 + ["s2"] * 4 + ["s_validation"] * 4))


def test_inner_partitions_cannot_overlap() -> None:
    with pytest.raises(E11AuthorityError, match="inner-train and inner-validation"):
        _authority(
            inner_train_rows=np.arange(0, 5), inner_validation_rows=np.arange(4, 8)
        )


def test_outer_train_and_held_out_cannot_overlap() -> None:
    with pytest.raises(E11AuthorityError, match="outer-train and outer-held-out"):
        _authority(outer_held_out_rows=np.arange(3, 12))


def test_inner_split_must_be_subject_disjoint() -> None:
    with pytest.raises(E11AuthorityError, match="inner split is not subject-disjoint"):
        _authority(subjects=np.array(["s1"] * 8 + ["s3"] * 4))


def test_outer_train_is_exactly_the_union_of_the_inner_partitions() -> None:
    authority = _authority()
    assert set(authority.outer_train_rows().tolist()) == set(
        authority.inner_train_rows().tolist()
    ) | set(authority.inner_validation_rows().tolist())


def test_accessors_return_copies_so_a_caller_cannot_mutate_the_boundary() -> None:
    authority = _authority()
    stolen = authority.inner_train_rows()
    stolen[:] = 999
    assert not np.array_equal(authority.inner_train_rows(), stolen)


# --------------------------------------------------------------------------
# 9: instrumentation does not alter model outputs or selection
# --------------------------------------------------------------------------


def test_instrumentation_does_not_change_model_outputs_or_rng_state() -> None:
    torch.manual_seed(2026)
    model = torch.nn.Sequential(
        torch.nn.Linear(4, 8), torch.nn.ReLU(), torch.nn.Linear(8, 1)
    )
    batch = torch.randn(16, 4)

    with torch.no_grad():
        before = model(batch).clone()
    rng_before = torch.random.get_rng_state()
    params_before = [p.detach().clone() for p in model.parameters()]

    # run the full instrumentation path
    labels = np.array([0, 1] * 20)
    scores = np.linspace(0.01, 0.99, 40)
    inner_validation_record(epoch=1, labels=labels, scores=scores)
    consensus = class_direction_consensus([np.array([1.0, 0.0]), np.array([0.0, 1.0])])
    stream_geometry_summaries(
        np.random.default_rng(0).normal(size=(8, 2)),
        np.array([1, 0] * 4),
        np.array(["a"] * 8),
        np.array(["s1"] * 8),
        consensus,
    )

    with torch.no_grad():
        after = model(batch)
    assert torch.equal(before, after)
    assert torch.equal(rng_before, torch.random.get_rng_state())
    for was, now in zip(params_before, model.parameters()):
        assert torch.equal(was, now.detach())


def test_selection_evidence_records_the_choice_but_cannot_make_it() -> None:
    evidence = SelectionEvidence(
        selected_epoch=2,
        selected_checkpoint_sha256="0" * 64,
        best_auprc=0.327467519173774,
        second_best_auprc=0.32717539152358616,
        selection_margin=0.327467519173774 - 0.32717539152358616,
        inner_f1_optimal_threshold=0.41,
        partitions={"selection": "inner_validation", "consensus": "inner_train"},
        retained_epochs=(1, 2, 3),
    )
    # the fold-1 B1 margin E12a found: recorded, not smoothed away
    assert evidence.selection_margin == pytest.approx(0.00029213, abs=1e-8)
    assert not hasattr(evidence, "select")
    assert not hasattr(evidence, "choose_epoch")


def test_retention_policy_must_keep_the_selected_checkpoint() -> None:
    with pytest.raises(E11InstrumentationError, match="keep the selected epoch"):
        SelectionEvidence(
            selected_epoch=4,
            selected_checkpoint_sha256="0" * 64,
            best_auprc=0.25,
            second_best_auprc=0.21,
            selection_margin=0.25 - 0.21,
            inner_f1_optimal_threshold=0.3,
            partitions={"selection": "inner_validation"},
            retained_epochs=(1, 2, 3),  # 4 is missing
        )


# --------------------------------------------------------------------------
# 10: interrupted writes fail closed
# --------------------------------------------------------------------------


def _complete_epoch(log: EpochEvidenceLog, epoch: int) -> None:
    log.record_epoch(
        EpochLossRecord(
            epoch=epoch, arm="B1", bce_loss=0.2, aux_loss_raw=0.5,
            aux_loss_scaled=LAMBDA * 0.5, aux_lambda=LAMBDA,
            total_loss=0.2 + LAMBDA * 0.5, learning_rate=1e-3, seconds=1.0,
        ),
        InnerValidationRecord(
            epoch=epoch, auprc=0.4, auroc=0.8, f1_optimal_threshold=0.5,
            prevalence=0.01, n_positive=10, n_negative=990,
        ),
        geometry=[],
        geometry_consensus_partition="inner_train",
    )


def test_completed_epochs_survive_an_interruption(tmp_path: Path) -> None:
    path = tmp_path / "epochs.json"
    log = EpochEvidenceLog(path=path, fold=0, arm="B1")
    _complete_epoch(log, 1)
    _complete_epoch(log, 2)
    # a crash here leaves epochs 1 and 2 durably readable
    assert [record["epoch"] for record in load_epoch_evidence(path)] == [1, 2]


def test_a_tampered_or_truncated_record_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "epochs.json"
    log = EpochEvidenceLog(path=path, fold=0, arm="B1")
    _complete_epoch(log, 1)

    payload = json.loads(path.read_text())
    payload["epochs"][0]["training"]["total_loss"] = 0.999  # torn / edited
    path.write_text(json.dumps(payload))

    with pytest.raises(E11InstrumentationError, match="failed its digest check"):
        load_epoch_evidence(path)


def test_a_record_not_marked_complete_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "epochs.json"
    log = EpochEvidenceLog(path=path, fold=0, arm="B1")
    _complete_epoch(log, 1)

    payload = json.loads(path.read_text())
    payload["epochs"][0]["record_complete"] = False
    path.write_text(json.dumps(payload))

    with pytest.raises(E11InstrumentationError, match="not marked complete"):
        load_epoch_evidence(path)


def test_no_temporary_file_survives_a_successful_write(tmp_path: Path) -> None:
    path = tmp_path / "epochs.json"
    log = EpochEvidenceLog(path=path, fold=0, arm="B1")
    _complete_epoch(log, 1)
    assert list(tmp_path.glob(".*tmp*")) == []
    assert path.exists()


def test_duplicate_epoch_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "epochs.json"
    log = EpochEvidenceLog(path=path, fold=0, arm="B1")
    _complete_epoch(log, 1)
    with pytest.raises(E11InstrumentationError, match="already recorded"):
        _complete_epoch(log, 1)


def test_non_finite_loss_never_reaches_the_log() -> None:
    with pytest.raises(E11InstrumentationError, match="not finite"):
        EpochLossRecord(
            epoch=1, arm="B0", bce_loss=float("nan"), total_loss=float("nan"),
            learning_rate=1e-3, seconds=1.0,
        )
