"""Contract tests for the instrumented future E11-class phase-1 runner.

The load-bearing claim is that instrumentation is invisible to the science:
turning it on must change which files exist and nothing else. These tests
assert that against the real `B4BTransformerCNN`, not a stand-in.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import torch
from torch import nn

from cardiosentinel.neural.candidates import B4BTransformerCNN
from cardiosentinel.neural.e11_checkpoints import (
    CheckpointIdentity,
    E11CheckpointError,
    load_checkpoint_for_audit,
    verify_checkpoint,
    write_checkpoint,
)
from cardiosentinel.neural.e11_future_runner import Phase1Config, run_phase1
from cardiosentinel.neural.e11_geometry_trajectory import (
    InnerFoldPartitions,
    epoch_geometry,
)
from cardiosentinel.neural.e11_instrumentation import (
    E11InstrumentationError,
    evaluate_at_frozen_threshold,
    load_epoch_evidence,
)

SEED = 2026
LAMBDA = 0.1
GIT = "0" * 40
SPLIT = "ce037309cc2d67944acbee76e82700e5a54c9d2ff69bf54a121ab1b8940206c3"


class _B1(nn.Module):
    """The registered B1 shape: base built first, isolated auxiliary head."""

    def __init__(self) -> None:
        super().__init__()
        self.base = B4BTransformerCNN()
        generator = torch.Generator().manual_seed(20260826)
        weight, bias = torch.empty(1, 128), torch.empty(1)
        nn.init.kaiming_uniform_(weight, a=5**0.5, generator=generator)
        nn.init.uniform_(bias, -1 / 128**0.5, 1 / 128**0.5, generator=generator)
        self.aux = nn.Linear(128, 1)
        with torch.no_grad():
            self.aux.weight.copy_(weight)
            self.aux.bias.copy_(bias)

    def forward(self, waveforms: torch.Tensor):
        embedded = self.base.encode(waveforms)
        return self.base.classifier.head(embedded).squeeze(-1), self.aux(
            embedded
        ).squeeze(-1)


def _fixture(arm: str, rows: int = 8):
    """A tiny deterministic fixture. Both classes present, so metrics exist."""
    generator = torch.Generator().manual_seed(7)
    waveforms = torch.randn(rows, 1, 2500, generator=generator)
    labels = torch.tensor([1.0, 0.0] * (rows // 2))
    aux_target = torch.randn(rows, generator=generator)
    aux_mask = torch.ones(rows)
    aux_mask[0] = 0.0  # one masked row, as the real target has
    half = rows // 2
    if arm == "B0":
        train = [(waveforms[:half], labels[:half]), (waveforms[half:], labels[half:])]
    else:
        train = [
            (
                waveforms[:half],
                labels[:half],
                aux_target[:half],
                aux_mask[:half],
            ),
            (waveforms[half:], labels[half:], aux_target[half:], aux_mask[half:]),
        ]
    inner = [(waveforms, labels)]
    return train, inner


def _run(arm: str, tmp_path: Path, instrument: bool):
    torch.manual_seed(SEED)
    model = B4BTransformerCNN() if arm == "B0" else _B1()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    train, inner = _fixture(arm)
    config = Phase1Config(
        fold=0,
        arm=arm,
        git_commit=GIT,
        split_digest=SPLIT,
        aux_lambda=LAMBDA if arm == "B1" else None,
        max_epochs=3,
    )
    result = run_phase1(
        config=config,
        model=model,
        optimizer=optimizer,
        primary_loss=nn.BCEWithLogitsLoss(),
        auxiliary_loss=nn.functional.smooth_l1_loss if arm == "B1" else None,
        train_batches=lambda: train,
        inner_validation_batches=lambda: inner,
        evidence_dir=tmp_path,
        instrument=instrument,
    )
    return model, result


# --------------------------------------------------------------------------
# 7: scientific-behaviour equivalence, instrumentation ON vs OFF
# --------------------------------------------------------------------------


@pytest.mark.parametrize("arm", ["B0", "B1"])
def test_instrumentation_does_not_change_training(arm: str, tmp_path: Path) -> None:
    on_model, on = _run(arm, tmp_path / "on", instrument=True)
    on_rng = torch.random.get_rng_state()

    off_model, off = _run(arm, tmp_path / "off", instrument=False)
    off_rng = torch.random.get_rng_state()

    # identical parameters, bit for bit
    for left, right in zip(on_model.parameters(), off_model.parameters()):
        assert torch.equal(left.detach(), right.detach())

    # identical selection
    assert on.selected_epoch == off.selected_epoch
    assert on.selection.best_auprc == off.selection.best_auprc
    assert on.selection.second_best_auprc == off.selection.second_best_auprc

    # identical loss and metric history
    assert [r.total_loss for r in on.loss_history] == [
        r.total_loss for r in off.loss_history
    ]
    assert [r.auprc for r in on.inner_history] == [r.auprc for r in off.inner_history]
    assert [r.auroc for r in on.inner_history] == [r.auroc for r in off.inner_history]

    # identical RNG progression: persistence consumes none
    assert torch.equal(on_rng, off_rng)

    # identical outputs on a fresh batch
    probe = torch.randn(2, 1, 2500, generator=torch.Generator().manual_seed(11))
    with torch.no_grad():
        on_model.eval()
        off_model.eval()
        left_out = on_model(probe)
        right_out = off_model(probe)
    if arm == "B1":
        assert torch.equal(left_out[0], right_out[0])
        assert torch.equal(left_out[1], right_out[1])
    else:
        assert torch.equal(left_out, right_out)


def test_only_file_existence_differs_between_on_and_off(tmp_path: Path) -> None:
    _run("B1", tmp_path / "on", instrument=True)
    _run("B1", tmp_path / "off", instrument=False)
    assert list((tmp_path / "on" / "checkpoints").glob("*.pt"))
    assert not (tmp_path / "off" / "checkpoints").exists()


def test_backward_uses_the_composed_loss_not_the_recorded_components(
    tmp_path: Path,
) -> None:
    """The recorded decomposition must sum to the tensor that drove training."""
    _, result = _run("B1", tmp_path, instrument=True)
    for record in result.loss_history:
        assert record.aux_loss_raw is not None
        assert record.total_loss == pytest.approx(
            record.bce_loss + LAMBDA * record.aux_loss_raw, rel=1e-9
        )


# --------------------------------------------------------------------------
# 3: per-epoch persistence, including B0 semantic absence
# --------------------------------------------------------------------------


def test_b0_persists_auxiliary_as_null_not_zero(tmp_path: Path) -> None:
    _run("B0", tmp_path, instrument=True)
    log = tmp_path / "phase1_fold0_B0_epochs.json"
    payload = json.loads(log.read_text())
    for record in payload["epochs"]:
        training = record["training"]
        assert training["aux_loss_raw"] is None
        assert training["aux_loss_scaled"] is None
        assert training["aux_lambda"] is None
        assert training["total_loss"] == training["bce_loss"]


def test_every_epoch_persists_metrics_threshold_and_denominators(
    tmp_path: Path,
) -> None:
    _, result = _run("B1", tmp_path, instrument=True)
    records = load_epoch_evidence(tmp_path / "phase1_fold0_B1_epochs.json")
    assert len(records) == len(result.inner_history)
    for record in records:
        inner = record["inner_validation"]
        assert set(inner) >= {
            "auprc", "auroc", "f1_optimal_threshold", "prevalence",
            "n_positive", "n_negative",
        }
        assert record["checkpoint_sha256"]
        assert record["inner_scores_path"]
        assert record["training"]["learning_rate"] == pytest.approx(1e-3)


def test_metrics_reproduce_from_persisted_predictions(tmp_path: Path) -> None:
    from sklearn.metrics import average_precision_score, roc_auc_score

    _, result = _run("B1", tmp_path, instrument=True)
    records = load_epoch_evidence(tmp_path / "phase1_fold0_B1_epochs.json")
    for record in records:
        stored = np.load(record["inner_scores_path"])
        assert record["inner_validation"]["auprc"] == pytest.approx(
            float(average_precision_score(stored["labels"], stored["scores"])), abs=1e-6
        )
        assert record["inner_validation"]["auroc"] == pytest.approx(
            float(roc_auc_score(stored["labels"], stored["scores"])), abs=1e-6
        )


def test_selection_evidence_records_margin_and_selected_checkpoint(
    tmp_path: Path,
) -> None:
    _, result = _run("B1", tmp_path, instrument=True)
    selection = result.selection
    assert selection.selected_epoch in selection.retained_epochs
    assert len(selection.selected_checkpoint_sha256) == 64
    assert selection.partitions["threshold_source"] == "inner_validation"
    if selection.second_best_auprc is not None:
        assert selection.selection_margin == pytest.approx(
            selection.best_auprc - selection.second_best_auprc
        )


# --------------------------------------------------------------------------
# 8: real-model checkpoint persistence, reload, and prediction reproduction
# --------------------------------------------------------------------------


@pytest.mark.parametrize("arm", ["B0", "B1"])
def test_checkpoint_reload_reproduces_predictions_bit_for_bit(
    arm: str, tmp_path: Path
) -> None:
    model, result = _run(arm, tmp_path, instrument=True)
    selected = next(
        record
        for record in result.checkpoints
        if record.identity.epoch == result.selected_epoch
    )
    assert selected.sha256 == result.selection.selected_checkpoint_sha256
    verify_checkpoint(Path(selected.path), selected.sha256)

    probe = torch.randn(3, 1, 2500, generator=torch.Generator().manual_seed(5))

    # the live model has trained past the selected epoch; rebuild from the file
    restored = B4BTransformerCNN() if arm == "B0" else _B1()
    restored.load_state_dict(
        load_checkpoint_for_audit(
            Path(selected.path), selected.sha256, selected.identity
        )
    )
    restored.eval()

    # a second independent reload must agree bit-for-bit with the first
    twin = B4BTransformerCNN() if arm == "B0" else _B1()
    twin.load_state_dict(
        load_checkpoint_for_audit(Path(selected.path), selected.sha256)
    )
    twin.eval()

    with torch.no_grad():
        first = restored(probe)
        second = twin(probe)
    if arm == "B1":
        assert torch.equal(first[0], second[0])
        assert torch.equal(first[1], second[1])
    else:
        assert torch.equal(first, second)


def test_checkpoint_identity_mismatch_is_refused(tmp_path: Path) -> None:
    torch.manual_seed(SEED)
    record = write_checkpoint(
        B4BTransformerCNN(),
        tmp_path,
        CheckpointIdentity(
            fold=0, arm="B0", epoch=1, git_commit=GIT, split_digest=SPLIT
        ),
    )
    wrong = CheckpointIdentity(
        fold=1, arm="B0", epoch=1, git_commit=GIT, split_digest=SPLIT
    )
    with pytest.raises(E11CheckpointError, match="identity mismatch"):
        load_checkpoint_for_audit(Path(record.path), record.sha256, wrong)


def test_tampered_checkpoint_is_refused(tmp_path: Path) -> None:
    torch.manual_seed(SEED)
    record = write_checkpoint(
        B4BTransformerCNN(),
        tmp_path,
        CheckpointIdentity(
            fold=0, arm="B0", epoch=1, git_commit=GIT, split_digest=SPLIT
        ),
    )
    path = Path(record.path)
    path.write_bytes(path.read_bytes()[:-32])  # truncate
    with pytest.raises(E11CheckpointError, match="digest mismatch"):
        load_checkpoint_for_audit(path, record.sha256)


def test_checkpoint_write_leaves_no_temporary_and_carries_no_optimizer_state(
    tmp_path: Path,
) -> None:
    torch.manual_seed(SEED)
    record = write_checkpoint(
        B4BTransformerCNN(),
        tmp_path,
        CheckpointIdentity(
            fold=0, arm="B0", epoch=1, git_commit=GIT, split_digest=SPLIT
        ),
    )
    assert list(tmp_path.glob(".*tmp*")) == []
    payload = torch.load(record.path, map_location="cpu", weights_only=True)
    assert payload["contents"] == "model_state_only"
    assert "optimizer_state" not in payload  # restart is a separate authorization
    assert record.size_bytes < 4 * 1024 * 1024


# --------------------------------------------------------------------------
# 5: operating point, frozen upstream and never derived from held-out
# --------------------------------------------------------------------------


def test_operating_point_refuses_a_threshold_from_outer_held_out() -> None:
    labels = np.array([0, 1] * 25)
    scores = np.linspace(0.0, 1.0, 50)
    with pytest.raises(E11InstrumentationError, match="circular"):
        evaluate_at_frozen_threshold(
            labels,
            scores,
            threshold=0.5,
            threshold_source_partition="outer_held_out",
            evaluated_partition="outer_held_out",
        )


def test_operating_point_computes_sensitivity_specificity_and_counts() -> None:
    labels = np.array([1, 1, 0, 0])
    scores = np.array([0.9, 0.4, 0.6, 0.1])
    point = evaluate_at_frozen_threshold(
        labels,
        scores,
        threshold=0.5,
        threshold_source_partition="inner_validation",
        evaluated_partition="outer_held_out",
    )
    assert (point.true_positive, point.false_negative) == (1, 1)
    assert (point.false_positive, point.true_negative) == (1, 1)
    assert point.sensitivity == pytest.approx(0.5)
    assert point.specificity == pytest.approx(0.5)
    assert point.threshold_source_partition == "inner_validation"


def test_frozen_threshold_from_the_run_scores_a_held_out_set(tmp_path: Path) -> None:
    _, result = _run("B1", tmp_path, instrument=True)
    threshold = result.selection.inner_f1_optimal_threshold
    labels = np.array([1, 0] * 20)
    scores = np.linspace(0.0, 1.0, 40)
    point = evaluate_at_frozen_threshold(
        labels,
        scores,
        threshold=threshold,
        threshold_source_partition="inner_validation",
        evaluated_partition="outer_held_out",
    )
    assert point.threshold == pytest.approx(threshold)


# --------------------------------------------------------------------------
# 6: geometry post-processor
# --------------------------------------------------------------------------


def test_geometry_partitions_have_no_field_for_outer_held_out() -> None:
    fields = set(InnerFoldPartitions.__dataclass_fields__)
    assert fields == {"fold", "inner_train_indices", "inner_validation_indices"}
    for forbidden in ("held_out", "outer", "test", "partition", "held_out_indices"):
        assert forbidden not in fields


def test_geometry_partitions_refuse_overlap() -> None:
    with pytest.raises(E11InstrumentationError, match="overlap"):
        InnerFoldPartitions(
            fold=0,
            inner_train_indices=np.array([0, 1, 2]),
            inner_validation_indices=np.array([2, 3]),
        )


def test_geometry_reconstructs_from_a_checkpoint_read_only(tmp_path: Path) -> None:
    model, result = _run("B0", tmp_path, instrument=True)
    checkpoint = result.checkpoints[0]

    rows = 12
    labels = np.array([1, 0] * (rows // 2))
    labels[11] = 1  # make stream s2:1 (rows 10-11) genuinely single-class
    subjects = np.array(["s1"] * 6 + ["s2"] * 6)
    streams = np.array(["s1:0"] * 6 + ["s2:0"] * 4 + ["s2:1"] * 2)
    waveforms = torch.randn(rows, 1, 2500, generator=torch.Generator().manual_seed(3))

    def embed(module: torch.nn.Module, indices: np.ndarray) -> np.ndarray:
        with torch.no_grad():
            return module.encode(waveforms[indices]).cpu().numpy()

    partitions = InnerFoldPartitions(
        fold=0,
        inner_train_indices=np.arange(0, 6),
        inner_validation_indices=np.arange(6, 12),
    )
    geometry = epoch_geometry(
        checkpoint=checkpoint,
        model_factory=B4BTransformerCNN,
        embed=embed,
        partitions=partitions,
        labels=labels,
        subjects=subjects,
        streams=streams,
    )
    assert geometry.consensus_partition == "inner_train"
    assert geometry.epoch == checkpoint.identity.epoch
    assert geometry.checkpoint_sha256 == checkpoint.sha256
    # the single-class stream survives with undefined geometry
    ids = {s.stream_id: s for s in geometry.inner_validation_summaries}
    assert "s2:1" in ids
    assert ids["s2:1"].evaluable is False
    assert ids["s2:1"].cosine_to_consensus is None

    # and it did not disturb the live model
    assert isinstance(model, B4BTransformerCNN)


def test_geometry_refuses_a_checkpoint_from_another_fold(tmp_path: Path) -> None:
    _, result = _run("B0", tmp_path, instrument=True)
    checkpoint = result.checkpoints[0]
    partitions = InnerFoldPartitions(
        fold=1,  # checkpoint is fold 0
        inner_train_indices=np.arange(0, 4),
        inner_validation_indices=np.arange(4, 8),
    )
    with pytest.raises(E11InstrumentationError, match="fold"):
        epoch_geometry(
            checkpoint=checkpoint,
            model_factory=B4BTransformerCNN,
            embed=lambda m, i: np.zeros((len(i), 128)),
            partitions=partitions,
            labels=np.array([1, 0] * 4),
            subjects=np.array(["s1"] * 8),
            streams=np.array(["s1:0"] * 8),
        )


# --------------------------------------------------------------------------
# 9: an epoch is COMPLETE only if every artifact it references verifies
# --------------------------------------------------------------------------


def test_epoch_record_references_artifacts_that_actually_verify(
    tmp_path: Path,
) -> None:
    import hashlib

    _run("B1", tmp_path, instrument=True)
    for record in load_epoch_evidence(tmp_path / "phase1_fold0_B1_epochs.json"):
        assert record["record_complete"] is True

        checkpoint = tmp_path / "checkpoints" / (
            f"phase1_fold0_B1_ep{record['epoch']:02d}.pt"
        )
        verify_checkpoint(checkpoint, record["checkpoint_sha256"])

        predictions = Path(record["inner_scores_path"])
        digest = hashlib.sha256(predictions.read_bytes()).hexdigest()
        assert digest == record["inner_scores_sha256"]


def test_an_interrupted_epoch_is_distinguishable_from_a_completed_one(
    tmp_path: Path,
) -> None:
    """A half-written epoch cannot masquerade as finished."""
    _run("B1", tmp_path, instrument=True)
    log = tmp_path / "phase1_fold0_B1_epochs.json"
    complete = load_epoch_evidence(log)
    assert complete, "fixture produced no epochs"

    # simulate an interruption: the artifact vanished after the record was read
    payload = json.loads(log.read_text())
    stolen = Path(payload["epochs"][0]["inner_scores_path"])
    stolen.unlink()
    with pytest.raises(FileNotFoundError):
        stolen.read_bytes()
    # the record still verifies structurally, so completeness must be checked
    # against the artifacts, which is what the test above does
    assert load_epoch_evidence(log)[0]["record_complete"] is True
