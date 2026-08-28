"""Phase-1 training loop for a FUTURE E11-class run, fully instrumented.

This is the wiring the E12a audit found missing. It is **not** the runner that
produced E11 ATTEMPT 2 -- that script is preserved unmodified under
`cardiosentinel-runs/b4-e11-morphology-aware-v1/E11_ATTEMPT_2/protocol/` and
nothing here touches it or its results.

**Nothing here is authorized to run.** No scientific parameter is chosen in this
module: lambda, the auxiliary target, the architecture and the split all arrive
as arguments. It exists so that when an experiment *is* authorized, the evidence
E12a wanted already gets written.

**The selection rule is unchanged and is not re-derived here.** Maximum inner
pooled AUPRC, earliest epoch wins an exact tie, patience-4 early stopping on
`EARLY_STOPPING_DELTA` -- imported from `training`, applied identically to both
arms, and never consulting any instrumentation output.

**Why instrumentation cannot perturb training.** The tensor handed to
`backward()` is constructed exactly as before; the decomposition is recorded by
`.detach()`-ing its already-computed components. No extra forward pass, no extra
RNG draw, no change to batch order. Serialization reads `state_dict()` and
writes bytes. `instrument=False` therefore differs from `instrument=True` only
in which files exist afterwards, and a test asserts bit-identical parameters,
outputs, selected epoch and RNG state across the two.
"""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Sequence

import numpy as np
import torch

from cardiosentinel.baseline.cache import write_json_atomic
from cardiosentinel.neural.e11_checkpoints import (
    CheckpointIdentity,
    CheckpointRecord,
    write_checkpoint,
)
from cardiosentinel.neural.e11_instrumentation import (
    PERMITTED_THRESHOLD_SOURCES,
    E11InstrumentationError,
    EpochEvidenceLog,
    EpochLossRecord,
    InnerValidationRecord,
    OperatingPointRecord,
    SelectionEvidence,
    evaluate_at_frozen_threshold,
    inner_validation_record,
)
from cardiosentinel.neural.training import (
    EARLY_STOPPING_DELTA,
    EARLY_STOPPING_PATIENCE,
    MAX_EPOCHS,
)

__all__ = [
    "Phase1Config",
    "Phase1Result",
    "run_phase1",
    "Phase2Result",
    "run_phase2",
    "OuterEvaluation",
    "evaluate_outer_held_out",
]


@dataclass(frozen=True, slots=True)
class Phase1Config:
    """Everything the loop needs that is not data or a factory.

    `aux_lambda` is `None` for a primary-only arm. That is semantic absence:
    B0 has no auxiliary term, and its records say so rather than reporting 0.0.
    """

    fold: int
    arm: str
    git_commit: str
    split_digest: str
    aux_lambda: float | None = None
    max_epochs: int = MAX_EPOCHS
    patience: int = EARLY_STOPPING_PATIENCE
    delta: float = EARLY_STOPPING_DELTA

    def __post_init__(self) -> None:
        if self.arm not in ("B0", "B1"):
            raise E11InstrumentationError(f"unknown arm: {self.arm!r}")
        if (self.arm == "B1") != (self.aux_lambda is not None):
            raise E11InstrumentationError(
                "aux_lambda is required for B1 and forbidden for B0"
            )


@dataclass(slots=True)
class Phase1Result:
    selected_epoch: int
    selection: SelectionEvidence
    checkpoints: list[CheckpointRecord] = field(default_factory=list)
    inner_history: list[InnerValidationRecord] = field(default_factory=list)
    loss_history: list[EpochLossRecord] = field(default_factory=list)


def _learning_rate(optimizer: torch.optim.Optimizer) -> float:
    return float(optimizer.param_groups[0]["lr"])


def run_phase1(
    *,
    config: Phase1Config,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    primary_loss: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
    auxiliary_loss: Callable[[torch.Tensor, torch.Tensor], torch.Tensor] | None,
    train_batches: Callable[[], Iterable[Sequence[torch.Tensor]]],
    inner_validation_batches: Callable[[], Iterable[Sequence[torch.Tensor]]],
    evidence_dir: Path,
    clock: Callable[[], float] = lambda: 0.0,
    instrument: bool = True,
) -> Phase1Result:
    """Run phase 1 and, when instrumented, persist per-epoch evidence.

    A batch is `(waveforms, labels)` for B0 and
    `(waveforms, labels, aux_target, aux_mask)` for B1.
    """
    evidence_dir = Path(evidence_dir)
    log = (
        EpochEvidenceLog(
            path=evidence_dir / f"phase1_fold{config.fold}_{config.arm}_epochs.json",
            fold=config.fold,
            arm=config.arm,
        )
        if instrument
        else None
    )
    checkpoints: list[CheckpointRecord] = []
    inner_history: list[InnerValidationRecord] = []
    loss_history: list[EpochLossRecord] = []

    best = -np.inf
    best_epoch = 0
    stale = 0
    scored: list[tuple[int, float]] = []

    for epoch in range(1, config.max_epochs + 1):
        model.train()
        started = clock()
        bce_total = aux_total = weight = 0.0

        for batch in train_batches():
            optimizer.zero_grad(set_to_none=True)
            if config.arm == "B0":
                waveforms, labels = batch
                loss = primary_loss(model(waveforms), labels)
                bce_component = loss
                aux_component = None
            else:
                waveforms, labels, aux_target, aux_mask = batch
                logits, auxiliary = model(waveforms)
                bce_component = primary_loss(logits, labels)
                loss = bce_component
                aux_component = None
                selected = aux_mask.bool()
                if selected.any():
                    assert auxiliary_loss is not None
                    # Index selection, never multiplication: NaN * 0 == NaN.
                    aux_component = auxiliary_loss(
                        auxiliary[selected], aux_target[selected]
                    )
                    loss = bce_component + config.aux_lambda * aux_component

            if not torch.isfinite(loss):
                raise E11InstrumentationError(
                    f"non-finite loss at fold {config.fold} {config.arm} epoch {epoch}"
                )
            # backward() sees exactly the tensor it would see uninstrumented.
            loss.backward()
            optimizer.step()

            count = float(labels.numel())
            weight += count
            bce_total += float(bce_component.detach()) * count
            if aux_component is not None:
                aux_total += float(aux_component.detach()) * count

        bce_mean = bce_total / weight
        aux_mean = (aux_total / weight) if config.arm == "B1" else None
        scaled = (config.aux_lambda * aux_mean) if aux_mean is not None else None
        losses = EpochLossRecord(
            epoch=epoch,
            arm=config.arm,
            bce_loss=bce_mean,
            aux_loss_raw=aux_mean,
            aux_loss_scaled=scaled,
            aux_lambda=config.aux_lambda if aux_mean is not None else None,
            total_loss=bce_mean + (scaled or 0.0),
            learning_rate=_learning_rate(optimizer),
            seconds=clock() - started,
        )

        model.eval()
        targets: list[np.ndarray] = []
        scores: list[np.ndarray] = []
        with torch.no_grad():
            for batch in inner_validation_batches():
                waveforms, labels = batch[0], batch[1]
                output = model(waveforms)
                logits = output[0] if config.arm == "B1" else output
                scores.append(torch.sigmoid(logits).cpu().numpy())
                targets.append(labels.cpu().numpy())
        inner_labels = np.concatenate(targets)
        inner_scores = np.concatenate(scores)
        inner = inner_validation_record(epoch, inner_labels, inner_scores)

        loss_history.append(losses)
        inner_history.append(inner)
        scored.append((epoch, inner.auprc))

        if instrument:
            record = write_checkpoint(
                model,
                evidence_dir / "checkpoints",
                CheckpointIdentity(
                    fold=config.fold,
                    arm=config.arm,
                    epoch=epoch,
                    git_commit=config.git_commit,
                    split_digest=config.split_digest,
                ),
            )
            checkpoints.append(record)
            predictions = evidence_dir / "inner" / (
                f"fold{config.fold}_{config.arm}_ep{epoch:02d}.npz"
            )
            predictions.parent.mkdir(parents=True, exist_ok=True)
            # Fail-safe order: write to a temporary, hash the bytes that will
            # occupy the final path, publish atomically, and only then let the
            # epoch record reference the digest.
            temporary = predictions.with_name(f".{predictions.name}.tmp.npz")
            with open(temporary, "wb") as handle:
                np.savez_compressed(
                    handle,
                    labels=inner_labels.astype(np.uint8),
                    scores=inner_scores.astype(np.float32),
                )
            predictions_sha256 = hashlib.sha256(temporary.read_bytes()).hexdigest()
            temporary.replace(predictions)
            assert log is not None
            log.record_epoch(
                losses,
                inner,
                geometry=[],  # trajectory is reconstructed post-hoc from checkpoints
                geometry_consensus_partition="inner_train",
                inner_scores_path=str(predictions),
                inner_scores_sha256=predictions_sha256,
                checkpoint_sha256=record.sha256,
            )

        # ---- registered selection rule, unchanged ----
        if inner.auprc > best + config.delta:
            best, best_epoch, stale = inner.auprc, epoch, 0
        else:
            stale += 1
        if stale >= config.patience:
            break

    ranked = sorted((auprc for _, auprc in scored), reverse=True)
    second = ranked[1] if len(ranked) > 1 else None
    selected_inner = next(rec for rec in inner_history if rec.epoch == best_epoch)
    selection = SelectionEvidence(
        selected_epoch=best_epoch,
        selected_checkpoint_sha256=next(
            (rec.sha256 for rec in checkpoints if rec.identity.epoch == best_epoch),
            "",
        ),
        best_auprc=best,
        second_best_auprc=second,
        selection_margin=(best - second) if second is not None else None,
        inner_f1_optimal_threshold=selected_inner.f1_optimal_threshold,
        partitions={
            "selection": "inner_validation",
            "consensus": "inner_train",
            "threshold_source": "inner_validation",
        },
        retained_epochs=tuple(rec.identity.epoch for rec in checkpoints)
        or (best_epoch,),
    )
    return Phase1Result(
        selected_epoch=best_epoch,
        selection=selection,
        checkpoints=checkpoints,
        inner_history=inner_history,
        loss_history=loss_history,
    )


# --------------------------------------------------------------------------
# phase 2: refit on all outer-train for exactly the selected duration
# --------------------------------------------------------------------------


@dataclass(slots=True)
class Phase2Result:
    epochs_run: int
    selected_phase1_epoch: int
    justifying_checkpoint_sha256: str
    final_checkpoint: CheckpointRecord
    loss_history: list[EpochLossRecord] = field(default_factory=list)
    scaler: tuple[float, float] | None = None


def run_phase2(
    *,
    config: Phase1Config,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    primary_loss: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
    auxiliary_loss: Callable[[torch.Tensor, torch.Tensor], torch.Tensor] | None,
    outer_train_batches: Callable[[], Iterable[Sequence[torch.Tensor]]],
    selection: SelectionEvidence,
    evidence_dir: Path,
    outer_train_scaler: tuple[float, float] | None = None,
    clock: Callable[[], float] = lambda: 0.0,
) -> Phase2Result:
    """Retrain on all outer-train for exactly the phase-1 selected duration.

    **There is no selection here.** The epoch count arrives from
    `selection.selected_epoch` and the loop simply runs that many epochs; no
    inner-validation is scored, no checkpoint is compared, and nothing in this
    function can change which duration was chosen. Outer-held-out is not an
    input, so it cannot influence any training decision.
    """
    if selection.selected_epoch < 1:
        raise E11InstrumentationError("phase 2 requires a selected phase-1 epoch")
    evidence_dir = Path(evidence_dir)
    history: list[EpochLossRecord] = []

    for epoch in range(1, selection.selected_epoch + 1):
        model.train()
        started = clock()
        bce_total = aux_total = weight = 0.0
        for batch in outer_train_batches():
            optimizer.zero_grad(set_to_none=True)
            if config.arm == "B0":
                waveforms, labels = batch
                loss = primary_loss(model(waveforms), labels)
                bce_component, aux_component = loss, None
            else:
                waveforms, labels, aux_target, aux_mask = batch
                logits, auxiliary = model(waveforms)
                bce_component = primary_loss(logits, labels)
                loss = bce_component
                aux_component = None
                selected = aux_mask.bool()
                if selected.any():
                    assert auxiliary_loss is not None
                    aux_component = auxiliary_loss(
                        auxiliary[selected], aux_target[selected]
                    )
                    loss = bce_component + config.aux_lambda * aux_component
            if not torch.isfinite(loss):
                raise E11InstrumentationError(
                    f"non-finite phase-2 loss at {config.arm} epoch {epoch}"
                )
            loss.backward()
            optimizer.step()
            count = float(labels.numel())
            weight += count
            bce_total += float(bce_component.detach()) * count
            if aux_component is not None:
                aux_total += float(aux_component.detach()) * count

        bce_mean = bce_total / weight
        aux_mean = (aux_total / weight) if config.arm == "B1" else None
        scaled = (config.aux_lambda * aux_mean) if aux_mean is not None else None
        history.append(
            EpochLossRecord(
                epoch=epoch,
                arm=config.arm,
                bce_loss=bce_mean,
                aux_loss_raw=aux_mean,
                aux_loss_scaled=scaled,
                aux_lambda=config.aux_lambda if aux_mean is not None else None,
                total_loss=bce_mean + (scaled or 0.0),
                learning_rate=_learning_rate(optimizer),
                seconds=clock() - started,
            )
        )

    final = write_checkpoint(
        model,
        evidence_dir / "checkpoints",
        CheckpointIdentity(
            fold=config.fold,
            arm=config.arm,
            epoch=1000 + selection.selected_epoch,  # phase-2 namespace
            git_commit=config.git_commit,
            split_digest=config.split_digest,
        ),
    )
    payload = {
        "schema": "e11-phase2-v1",
        "fold": config.fold,
        "arm": config.arm,
        "selected_phase1_epoch": selection.selected_epoch,
        "justifying_checkpoint_sha256": selection.selected_checkpoint_sha256,
        "phase2_epochs_run": selection.selected_epoch,
        "phase2_selection_performed": False,
        "outer_train_morphology_scaler": (
            {"median": outer_train_scaler[0], "iqr": outer_train_scaler[1]}
            if outer_train_scaler is not None
            else None
        ),
        "final_checkpoint_sha256": final.sha256,
        "final_checkpoint_path": final.path,
        "epochs": [asdict(record) for record in history],
    }
    write_json_atomic(
        evidence_dir / f"phase2_fold{config.fold}_{config.arm}.json", payload
    )
    return Phase2Result(
        epochs_run=selection.selected_epoch,
        selected_phase1_epoch=selection.selected_epoch,
        justifying_checkpoint_sha256=selection.selected_checkpoint_sha256,
        final_checkpoint=final,
        loss_history=history,
        scaler=outer_train_scaler,
    )


# --------------------------------------------------------------------------
# outer-held-out evaluation at the frozen inner threshold
# --------------------------------------------------------------------------


@dataclass(slots=True)
class OuterEvaluation:
    fold: int
    arm: str
    prevalence: float
    pooled_auprc: float
    pooled_auroc: float
    subject_macro_auprc: float
    subject_macro_auroc: float
    subject_macro_denominator: int
    subjects_in_fold: int
    stream_auroc_median: float | None
    stream_denominator: int
    operating_point: OperatingPointRecord
    evidence_path: str
    evidence_sha256: str


def evaluate_outer_held_out(
    *,
    fold: int,
    arm: str,
    scores: np.ndarray,
    labels: np.ndarray,
    stable_ids: np.ndarray,
    subjects: np.ndarray,
    streams: np.ndarray,
    frozen_threshold: float,
    threshold_source_partition: str,
    evidence_dir: Path,
) -> OuterEvaluation:
    """Score the held-out fold. Derives nothing from the scores it is given.

    The threshold is an argument. There is no code path here that inspects
    `scores` to choose one, and `threshold_source_partition` must name an inner
    partition -- `evaluate_at_frozen_threshold` refuses anything else.
    """
    from sklearn.metrics import average_precision_score, roc_auc_score

    if threshold_source_partition not in PERMITTED_THRESHOLD_SOURCES:
        raise E11InstrumentationError(
            "the outer operating point must come from an inner partition; "
            f"refusing {threshold_source_partition!r}"
        )
    if frozen_threshold is None or not np.isfinite(frozen_threshold):
        raise E11InstrumentationError(
            "the frozen threshold must exist before outer scoring begins"
        )

    labels = np.asarray(labels).astype(np.int64).ravel()
    scores = np.asarray(scores, dtype=np.float64).ravel()
    subjects = np.asarray(subjects).astype(str)
    streams = np.asarray(streams).astype(str)

    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence = evidence_dir / f"outer_fold{fold}_{arm}.npz"
    temporary = evidence.with_name(f".{evidence.name}.tmp.npz")
    with open(temporary, "wb") as handle:
        np.savez_compressed(
            handle,
            score=scores.astype(np.float32),
            label=labels.astype(np.uint8),
            stable_id=np.asarray(stable_ids).astype(str),
            subject_id=subjects,
            stream_id=streams,
        )
    evidence_sha = hashlib.sha256(temporary.read_bytes()).hexdigest()
    temporary.replace(evidence)

    subject_auprc: list[float] = []
    subject_auroc: list[float] = []
    for subject in np.unique(subjects):
        mask = subjects == subject
        if labels[mask].sum() in (0, int(mask.sum())):
            continue
        subject_auprc.append(float(average_precision_score(labels[mask], scores[mask])))
        subject_auroc.append(float(roc_auc_score(labels[mask], scores[mask])))
    stream_auroc: list[float] = []
    for stream in np.unique(streams):
        mask = streams == stream
        if labels[mask].sum() in (0, int(mask.sum())):
            continue
        stream_auroc.append(float(roc_auc_score(labels[mask], scores[mask])))

    point = evaluate_at_frozen_threshold(
        labels,
        scores,
        threshold=frozen_threshold,
        threshold_source_partition=threshold_source_partition,
        evaluated_partition="outer_held_out",
    )
    result = OuterEvaluation(
        fold=fold,
        arm=arm,
        prevalence=float(labels.mean()),
        pooled_auprc=float(average_precision_score(labels, scores)),
        pooled_auroc=float(roc_auc_score(labels, scores)),
        subject_macro_auprc=(
            float(np.mean(subject_auprc)) if subject_auprc else float("nan")
        ),
        subject_macro_auroc=(
            float(np.mean(subject_auroc)) if subject_auroc else float("nan")
        ),
        subject_macro_denominator=len(subject_auprc),
        subjects_in_fold=int(np.unique(subjects).size),
        stream_auroc_median=float(np.median(stream_auroc)) if stream_auroc else None,
        stream_denominator=len(stream_auroc),
        operating_point=point,
        evidence_path=str(evidence),
        evidence_sha256=evidence_sha,
    )
    write_json_atomic(
        evidence_dir / f"outer_fold{fold}_{arm}.json",
        {"schema": "e11-outer-evaluation-v1", **asdict(result)},
    )
    return result
