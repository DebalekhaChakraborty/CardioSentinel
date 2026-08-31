"""End-to-end dry run of the future E11-class pipeline on a tiny fixture.

This is **not** a scientific experiment. It uses synthetic tensors and six
invented subjects, takes a handful of optimizer steps, and never touches the
registered E11 dataset. Its only job is to prove the seams hold together and
that the boundaries hold shut.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import torch
from torch import nn

from cardiosentinel.neural.candidates import B4BTransformerCNN
from cardiosentinel.neural.e11_authority import (
    E11AuthorityError,
    E11Partition,
)
from cardiosentinel.neural.e11_checkpoints import load_checkpoint_for_audit
from cardiosentinel.neural.e11_data_binding import (
    E11Sources,
    bind_e11_data,
    morphology_scaler,
    write_binding_receipt,
)
from cardiosentinel.neural.e11_future_runner import (
    Phase1Config,
    evaluate_outer_held_out,
    run_phase1,
    run_phase2,
)
from cardiosentinel.neural.e11_geometry_trajectory import (
    InnerFoldPartitions,
    run_inner_geometry_driver,
)
from cardiosentinel.neural.e11_instrumentation import (
    E11InstrumentationError,
    evaluate_at_frozen_threshold,
    f1_optimal_threshold,
)
from cardiosentinel.neural.e11_outer_geometry import (
    outer_geometry,
    write_outer_geometry,
)
from cardiosentinel.neural.e11_run_state import (
    E11RunReceipt,
    E11RunState,
    E11RunStateError,
)

SEED = 2026
LAMBDA = 0.1
GIT = "0" * 40
EXPERIMENT = "E11_FUTURE_DRYRUN"
SUBJECTS = [f"s00{i}" for i in range(1, 7)]
STREAMS_PER_SUBJECT = 2
ROWS_PER_STREAM = 4
ROWS = len(SUBJECTS) * STREAMS_PER_SUBJECT * ROWS_PER_STREAM  # 48


# --------------------------------------------------------------------------
# fixture
# --------------------------------------------------------------------------


@pytest.fixture()
def fixture(tmp_path: Path) -> dict:
    """A tiny, deterministic, entirely synthetic E11-shaped corpus."""
    cache = tmp_path / "cache"
    protocol = tmp_path / "protocol"
    cache.mkdir()
    protocol.mkdir()

    subjects, streams, stable_ids, labels, folds = [], [], [], [], []
    for index, subject in enumerate(SUBJECTS):
        fold = index // 2
        for channel in range(STREAMS_PER_SUBJECT):
            for row in range(ROWS_PER_STREAM):
                start = (index * 100 + channel * 10 + row) * 2500
                subjects.append(subject)
                streams.append(f"{subject}:{channel}")
                stable_ids.append(f"ltstdb:{subject}1:{channel}:{start}:{start + 2500}")
                labels.append(1.0 if row % 2 == 0 else 0.0)
                folds.append(fold)

    rng = np.random.default_rng(SEED)
    auxiliary = rng.normal(size=ROWS)
    auxiliary[3] = np.nan  # one undefined target, as the real one has

    np.save(cache / "train_stable_ids.npy", np.array(stable_ids))
    np.save(protocol / "e11_train_y.npy", np.array(labels))
    np.save(protocol / "e11_train_subj.npy", np.array(subjects))
    np.save(protocol / "e11_train_stream.npy", np.array(streams))
    np.save(protocol / "e11_train_fold.npy", np.array(folds))
    np.save(protocol / "e11_aux_target.npy", auxiliary)

    assignment = {s: i // 2 for i, s in enumerate(SUBJECTS)}
    prevalence = {s: 0.5 for s in SUBJECTS}
    (protocol / "e11_folds.json").write_text(
        json.dumps({"assignment": assignment, "prevalence": prevalence})
    )
    digest = hashlib.sha256(
        json.dumps(assignment, sort_keys=True).encode("utf-8")
    ).hexdigest()

    generator = torch.Generator().manual_seed(11)
    waveforms = torch.randn(ROWS, 1, 2500, generator=generator)
    return {
        "sources": E11Sources(waveform_cache=cache, protocol_dir=protocol),
        "split_digest": digest,
        "waveforms": waveforms,
        "root": tmp_path,
    }


class _B1(nn.Module):
    """Registered B1 shape: base built first, auxiliary head from isolated RNG."""

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
        head = self.base.classifier.head(embedded).squeeze(-1)
        return head, self.aux(embedded).squeeze(-1)


def _build(arm: str):
    torch.manual_seed(SEED)
    model = B4BTransformerCNN() if arm == "B0" else _B1()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    return model, optimizer


def _batches(fixture, binding, rows, arm, scaler=None, chunk=12):
    waveforms = fixture["waveforms"]
    labels = torch.tensor(binding.labels[rows], dtype=torch.float32)
    out = []
    for start in range(0, len(rows), chunk):
        window = rows[start : start + chunk]
        piece = [waveforms[window], labels[start : start + chunk]]
        if arm == "B1":
            target = binding.auxiliary_target[window]
            mask = np.isfinite(target).astype(np.float32)
            scaled = (np.nan_to_num(target, nan=0.0) - scaler[0]) / scaler[1]
            piece.append(torch.tensor(scaled, dtype=torch.float32))
            piece.append(torch.tensor(mask))
        out.append(tuple(piece))
    return out


def _encode(model, arm, waveforms, rows):
    base = model if arm == "B0" else model.base
    base.eval()
    with torch.no_grad():
        return base.encode(waveforms[rows]).cpu().numpy()


def _score(model, arm, waveforms, rows):
    base = model if arm == "B0" else model.base
    base.eval()
    with torch.no_grad():
        embedded = base.encode(waveforms[rows])
        return torch.sigmoid(base.classifier.head(embedded).squeeze(-1)).cpu().numpy()


# --------------------------------------------------------------------------
# the end-to-end pipeline
# --------------------------------------------------------------------------


def _pipeline(fixture, arm: str, fold: int = 0):
    root = fixture["root"] / f"run_{arm}"
    root.mkdir(exist_ok=True)
    receipt = E11RunReceipt(
        path=root / "run_receipt.json",
        authorization_identity="human-dry-run-not-an-experiment",
        experiment_id=EXPERIMENT,
    )

    binding = bind_e11_data(
        sources=fixture["sources"],
        expected_split_digest=fixture["split_digest"],
        experiment_id=EXPERIMENT,
        expected_subject_count=len(SUBJECTS),
    )
    binding_receipt = root / "data_binding_receipt.json"
    binding_digest = write_binding_receipt(binding, binding_receipt, folds=(fold,))
    receipt.advance(
        E11RunState.DATA_BOUND,
        artifacts=[binding_receipt],
        digests={"binding_digest": binding_digest},
    )

    authority = binding.authority(fold)
    inner_train = authority.inner_train_rows()
    inner_validation = authority.inner_validation_rows()
    outer_train = authority.outer_train_rows()
    held_out = authority.outer_held_out_rows()

    inner_scaler = morphology_scaler(binding, inner_train) if arm == "B1" else None
    config = Phase1Config(
        fold=fold,
        arm=arm,
        git_commit=GIT,
        split_digest=binding.split_digest,
        aux_lambda=LAMBDA if arm == "B1" else None,
        max_epochs=2,
    )
    model, optimizer = _build(arm)
    phase1 = run_phase1(
        config=config,
        model=model,
        optimizer=optimizer,
        primary_loss=nn.BCEWithLogitsLoss(),
        auxiliary_loss=nn.functional.smooth_l1_loss if arm == "B1" else None,
        train_batches=lambda: _batches(
            fixture, binding, inner_train, arm, inner_scaler
        ),
        inner_validation_batches=lambda: _batches(
            fixture, binding, inner_validation, "B0"
        ),
        evidence_dir=root,
        instrument=True,
    )
    log = root / f"phase1_fold{fold}_{arm}_epochs.json"
    receipt.advance(E11RunState.PHASE1_COMPLETE, artifacts=[log])
    receipt.advance(
        E11RunState.SELECTION_FROZEN,
        digests={"selected_checkpoint": phase1.selection.selected_checkpoint_sha256},
        detail={
            "selected_epoch": phase1.selected_epoch,
            "threshold": phase1.selection.inner_f1_optimal_threshold,
        },
    )

    outer_scaler = morphology_scaler(binding, outer_train) if arm == "B1" else None
    model2, optimizer2 = _build(arm)
    phase2 = run_phase2(
        config=config,
        model=model2,
        optimizer=optimizer2,
        primary_loss=nn.BCEWithLogitsLoss(),
        auxiliary_loss=nn.functional.smooth_l1_loss if arm == "B1" else None,
        outer_train_batches=lambda: _batches(
            fixture, binding, outer_train, arm, outer_scaler
        ),
        selection=phase1.selection,
        evidence_dir=root,
        outer_train_scaler=outer_scaler,
    )
    receipt.advance(
        E11RunState.PHASE2_COMPLETE,
        artifacts=[root / f"phase2_fold{fold}_{arm}.json"],
        digests={"final_checkpoint": phase2.final_checkpoint.sha256},
    )

    waveforms = fixture["waveforms"]
    scores = _score(model2, arm, waveforms, held_out)
    evaluation = evaluate_outer_held_out(
        fold=fold,
        arm=arm,
        scores=scores,
        labels=binding.labels[held_out],
        stable_ids=binding.stable_ids[held_out],
        subjects=binding.subjects[held_out],
        streams=binding.streams[held_out],
        frozen_threshold=phase1.selection.inner_f1_optimal_threshold,
        threshold_source_partition="inner_validation",
        evidence_dir=root,
    )
    receipt.advance(
        E11RunState.OUTER_SCORED,
        artifacts=[Path(evaluation.evidence_path)],
        digests={"outer_evidence": evaluation.evidence_sha256},
    )

    geometry = outer_geometry(
        fold=fold,
        arm=arm,
        outer_train_embeddings=_encode(model2, arm, waveforms, outer_train),
        outer_train_labels=binding.labels[outer_train],
        outer_train_streams=binding.streams[outer_train],
        held_out_embeddings=_encode(model2, arm, waveforms, held_out),
        held_out_labels=binding.labels[held_out],
        held_out_subjects=binding.subjects[held_out],
        held_out_streams=binding.streams[held_out],
    )
    outer_path = root / f"outer_geometry_fold{fold}_{arm}.json"
    geometry_digest = write_outer_geometry(geometry, outer_path)

    manifest = run_inner_geometry_driver(
        checkpoints=phase1.checkpoints,
        model_factory=(B4BTransformerCNN if arm == "B0" else _B1),
        embed=lambda module, rows: (
            (module if arm == "B0" else module.base)
            .encode(waveforms[rows])
            .cpu()
            .numpy()
        ),
        partitions=InnerFoldPartitions(
            fold=fold,
            inner_train_indices=inner_train,
            inner_validation_indices=inner_validation,
        ),
        labels=binding.labels,
        subjects=binding.subjects,
        streams=binding.streams,
        inner_split_digest="inner-" + binding.split_digest[:12],
        output_path=root / f"inner_geometry_fold{fold}_{arm}.json",
    )
    receipt.advance(
        E11RunState.GEOMETRY_COMPLETE,
        artifacts=[outer_path, root / f"inner_geometry_fold{fold}_{arm}.json"],
        digests={"outer_geometry": geometry_digest},
    )
    receipt.advance(E11RunState.ANALYSIS_READY)

    return {
        "root": root,
        "binding": binding,
        "authority": authority,
        "phase1": phase1,
        "phase2": phase2,
        "evaluation": evaluation,
        "outer_geometry": geometry,
        "inner_manifest": manifest,
        "receipt": receipt,
        "model2": model2,
        "held_out": held_out,
    }


@pytest.mark.parametrize("arm", ["B0", "B1"])
def test_end_to_end_pipeline_reaches_analysis_ready(fixture, arm: str) -> None:
    result = _pipeline(fixture, arm)
    receipt = result["receipt"]
    assert receipt.current_state is E11RunState.ANALYSIS_READY
    assert receipt.completed == (
        "DATA_BOUND",
        "PHASE1_COMPLETE",
        "SELECTION_FROZEN",
        "PHASE2_COMPLETE",
        "OUTER_SCORED",
        "GEOMETRY_COMPLETE",
        "ANALYSIS_READY",
    )
    assert receipt.failure_state is None
    E11RunReceipt.load(receipt.path)  # chain verifies


def test_phase2_duration_matches_the_selected_epoch(fixture) -> None:
    result = _pipeline(fixture, "B1")
    assert result["phase2"].epochs_run == result["phase1"].selected_epoch
    assert len(result["phase2"].loss_history) == result["phase1"].selected_epoch
    payload = json.loads(
        (result["root"] / "phase2_fold0_B1.json").read_text()
    )
    assert payload["phase2_selection_performed"] is False
    assert payload["justifying_checkpoint_sha256"] == (
        result["phase1"].selection.selected_checkpoint_sha256
    )


def test_selected_phase1_checkpoint_survives(fixture) -> None:
    result = _pipeline(fixture, "B0")
    selected = [
        record
        for record in result["phase1"].checkpoints
        if record.identity.epoch == result["phase1"].selected_epoch
    ]
    assert len(selected) == 1
    assert Path(selected[0].path).exists()
    assert selected[0].sha256 == result["phase1"].selection.selected_checkpoint_sha256


def test_final_scores_reproduce_after_checkpoint_reload(fixture) -> None:
    result = _pipeline(fixture, "B1")
    waveforms = fixture["waveforms"]
    held_out = result["held_out"]
    live = _score(result["model2"], "B1", waveforms, held_out)

    restored = _B1()
    restored.load_state_dict(
        load_checkpoint_for_audit(
            Path(result["phase2"].final_checkpoint.path),
            result["phase2"].final_checkpoint.sha256,
        )
    )
    reloaded = _score(restored, "B1", waveforms, held_out)
    assert np.array_equal(live, reloaded)


def test_operating_point_reproduces_from_persisted_evidence(fixture) -> None:
    result = _pipeline(fixture, "B0")
    evaluation = result["evaluation"]
    stored = np.load(evaluation.evidence_path)
    replayed = evaluate_at_frozen_threshold(
        stored["label"],
        stored["score"],
        threshold=evaluation.operating_point.threshold,
        threshold_source_partition="inner_validation",
        evaluated_partition="outer_held_out",
    )
    assert replayed.sensitivity == pytest.approx(
        evaluation.operating_point.sensitivity, abs=1e-6
    )
    assert replayed.specificity == pytest.approx(
        evaluation.operating_point.specificity, abs=1e-6
    )
    assert (replayed.true_positive, replayed.false_positive) == (
        evaluation.operating_point.true_positive,
        evaluation.operating_point.false_positive,
    )
    # the persisted evidence carries row identity, not just numbers
    assert set(stored.files) >= {
        "score", "label", "stable_id", "subject_id", "stream_id",
    }


def test_threshold_is_inner_derived_and_predates_outer_scoring(fixture) -> None:
    result = _pipeline(fixture, "B0")
    point = result["evaluation"].operating_point
    assert point.threshold_source_partition == "inner_validation"
    assert point.evaluated_partition == "outer_held_out"
    # the same threshold appears in the sealed SELECTION_FROZEN stage, which the
    # state machine required before OUTER_SCORED could be reached
    stages = {s["state"]: s for s in result["receipt"].stages}
    assert stages["SELECTION_FROZEN"]["detail"]["threshold"] == pytest.approx(
        point.threshold
    )
    assert stages["SELECTION_FROZEN"]["index"] < stages["OUTER_SCORED"]["index"]


def test_outer_and_inner_geometry_live_in_different_namespaces(fixture) -> None:
    result = _pipeline(fixture, "B1")
    outer = json.loads((result["root"] / "outer_geometry_fold0_B1.json").read_text())
    inner = json.loads((result["root"] / "inner_geometry_fold0_B1.json").read_text())
    assert outer["schema"] == "e11-outer-geometry-v1"
    assert inner["schema"] == "e11-geometry-trajectory-v1"
    assert outer["consensus_partition"] == "outer_train"
    assert inner["consensus_partition"] == "inner_train"
    assert inner["scored_partition"] == "inner_validation"
    assert inner["diagnostic_only"] is True
    assert inner["influences_selection"] is False


def test_inner_geometry_manifest_indexes_every_checkpoint(fixture) -> None:
    result = _pipeline(fixture, "B0")
    manifest = result["inner_manifest"]
    epochs = manifest["epochs"]
    assert len(epochs) == len(result["phase1"].checkpoints)
    hashes = {record.sha256 for record in result["phase1"].checkpoints}
    for entry in epochs:
        assert entry["checkpoint_sha256"] in hashes
        assert entry["inner_split_digest"]
        assert len(entry["geometry_record_digest"]) == 64


def test_geometry_outputs_reproduce(fixture) -> None:
    first = _pipeline(fixture, "B0")
    digests = [e["geometry_record_digest"] for e in first["inner_manifest"]["epochs"]]
    # re-driving over the same checkpoints must reproduce the same digests
    waveforms = fixture["waveforms"]
    authority = first["authority"]
    again = run_inner_geometry_driver(
        checkpoints=first["phase1"].checkpoints,
        model_factory=B4BTransformerCNN,
        embed=lambda m, rows: m.encode(waveforms[rows]).cpu().numpy(),
        partitions=InnerFoldPartitions(
            fold=0,
            inner_train_indices=authority.inner_train_rows(),
            inner_validation_indices=authority.inner_validation_rows(),
        ),
        labels=first["binding"].labels,
        subjects=first["binding"].subjects,
        streams=first["binding"].streams,
        inner_split_digest="inner-" + first["binding"].split_digest[:12],
        output_path=first["root"] / "inner_geometry_again.json",
    )
    assert [e["geometry_record_digest"] for e in again["epochs"]] == digests


# --------------------------------------------------------------------------
# boundaries
# --------------------------------------------------------------------------


def test_outer_held_out_cannot_influence_selection(fixture) -> None:
    """Scrambling held-out labels must not change phase-1 selection at all."""
    baseline = _pipeline(fixture, "B0")

    binding = bind_e11_data(
        sources=fixture["sources"],
        expected_split_digest=fixture["split_digest"],
        experiment_id=EXPERIMENT,
        expected_subject_count=len(SUBJECTS),
    )
    authority = binding.authority(0)
    held_out = authority.outer_held_out_rows()
    binding.labels[held_out] = 1.0 - binding.labels[held_out]  # invert held-out truth

    inner_train = authority.inner_train_rows()
    inner_validation = authority.inner_validation_rows()
    model, optimizer = _build("B0")
    scrambled = run_phase1(
        config=Phase1Config(
            fold=0, arm="B0", git_commit=GIT, split_digest=binding.split_digest,
            max_epochs=2,
        ),
        model=model,
        optimizer=optimizer,
        primary_loss=nn.BCEWithLogitsLoss(),
        auxiliary_loss=None,
        train_batches=lambda: _batches(fixture, binding, inner_train, "B0"),
        inner_validation_batches=lambda: _batches(
            fixture, binding, inner_validation, "B0"
        ),
        evidence_dir=fixture["root"] / "scrambled",
        instrument=True,
    )
    assert scrambled.selected_epoch == baseline["phase1"].selected_epoch
    assert scrambled.selection.best_auprc == baseline["phase1"].selection.best_auprc
    assert scrambled.selection.inner_f1_optimal_threshold == pytest.approx(
        baseline["phase1"].selection.inner_f1_optimal_threshold
    )


def test_a_historical_validation_subject_cannot_enter(fixture) -> None:
    binding = bind_e11_data(
        sources=fixture["sources"],
        expected_split_digest=fixture["split_digest"],
        experiment_id=EXPERIMENT,
        expected_subject_count=len(SUBJECTS),
    )
    binding.subjects[0] = "s_historical_validation"
    with pytest.raises(E11AuthorityError, match="outside the authorized"):
        binding.authority(0)


def test_no_accessor_can_name_a_sealed_partition(fixture) -> None:
    binding = bind_e11_data(
        sources=fixture["sources"],
        expected_split_digest=fixture["split_digest"],
        experiment_id=EXPERIMENT,
        expected_subject_count=len(SUBJECTS),
    )
    authority = binding.authority(0)
    assert {p.value for p in E11Partition} == {
        "inner_train", "inner_validation", "outer_train", "outer_held_out",
    }
    for forbidden in ("test_rows", "sealed_rows", "validation_rows", "rows"):
        assert not hasattr(authority, forbidden)


def test_threshold_selection_fails_closed_on_outer_scores() -> None:
    labels = np.array([1, 0] * 10)
    scores = np.linspace(0, 1, 20)
    with pytest.raises(E11InstrumentationError, match="circular"):
        f1_optimal_threshold(labels, scores, source_partition="outer_held_out")


def test_outer_evaluation_refuses_a_non_inner_threshold_source(
    fixture, tmp_path: Path
) -> None:
    with pytest.raises(E11InstrumentationError, match="inner partition"):
        evaluate_outer_held_out(
            fold=0, arm="B0",
            scores=np.linspace(0, 1, 8),
            labels=np.array([1, 0] * 4),
            stable_ids=np.array([f"id{i}" for i in range(8)]),
            subjects=np.array(["s1"] * 8),
            streams=np.array(["s1:0"] * 8),
            frozen_threshold=0.5,
            threshold_source_partition="outer_held_out",
            evidence_dir=tmp_path,
        )


def test_b0_and_b1_share_paired_stochastic_initialization() -> None:
    """A3: B1 builds the base first with byte-identical draws, then an isolated head."""
    torch.manual_seed(SEED)
    b0 = B4BTransformerCNN()
    torch.manual_seed(SEED)
    b1 = _B1()
    for left, right in zip(b0.parameters(), b1.base.parameters()):
        assert torch.equal(left.detach(), right.detach())
    assert torch.equal(torch.random.get_rng_state(), torch.random.get_rng_state())


# --------------------------------------------------------------------------
# state machine: fail closed
# --------------------------------------------------------------------------


def test_a_stage_cannot_be_skipped(tmp_path: Path) -> None:
    receipt = E11RunReceipt(
        path=tmp_path / "r.json", authorization_identity="h", experiment_id=EXPERIMENT
    )
    with pytest.raises(E11RunStateError, match="illegal transition"):
        receipt.advance(E11RunState.PHASE1_COMPLETE)


def test_a_stage_cannot_advance_without_its_artifacts(tmp_path: Path) -> None:
    receipt = E11RunReceipt(
        path=tmp_path / "r.json", authorization_identity="h", experiment_id=EXPERIMENT
    )
    with pytest.raises(E11RunStateError, match="does not exist"):
        receipt.advance(E11RunState.DATA_BOUND, artifacts=[tmp_path / "absent.json"])


def test_dropping_a_file_cannot_forge_a_later_state(fixture) -> None:
    result = _pipeline(fixture, "B0")
    payload = json.loads(result["receipt"].path.read_text())
    # forge: claim ANALYSIS_READY without its predecessors
    payload["stages"] = [payload["stages"][-1]]
    payload["stages"][0]["previous_seal"] = None
    result["receipt"].path.write_text(json.dumps(payload))
    with pytest.raises(E11RunStateError, match="out of order"):
        E11RunReceipt.load(result["receipt"].path)


def test_a_tampered_stage_breaks_the_chain(fixture) -> None:
    result = _pipeline(fixture, "B0")
    payload = json.loads(result["receipt"].path.read_text())
    payload["stages"][1]["detail"]["selected_epoch"] = 99
    result["receipt"].path.write_text(json.dumps(payload))
    with pytest.raises(E11RunStateError, match="failed its seal check"):
        E11RunReceipt.load(result["receipt"].path)


def test_a_failed_run_stops_and_does_not_retry(tmp_path: Path) -> None:
    receipt = E11RunReceipt(
        path=tmp_path / "r.json", authorization_identity="h", experiment_id=EXPERIMENT
    )
    receipt.record_failure("PHASE1", RuntimeError("boom"))
    assert receipt.failure_state is not None
    assert receipt.failure_state["relaunched"] is False
    with pytest.raises(E11RunStateError, match="new human authorization"):
        receipt.advance(E11RunState.DATA_BOUND)


def test_binding_refuses_a_wrong_split_digest(fixture) -> None:
    with pytest.raises(Exception, match="split digest mismatch"):
        bind_e11_data(
            sources=fixture["sources"],
            expected_split_digest="0" * 64,
            experiment_id=EXPERIMENT,
            expected_subject_count=len(SUBJECTS),
        )
