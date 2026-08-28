"""Read-only per-epoch geometry, derived from persisted phase-1 checkpoints.

The synchronous alternative -- recomputing inner-train embeddings inside every
training epoch -- was audited and costs about **40% additional training wall
time** (a 5-epoch x 3-fold x 2-arm phase 1 goes from 3.01 h to 4.22 h). Because
a checkpoint is only 1.20 MB, the same trajectory can instead be reconstructed
*after* phase 1 from the retained checkpoints, at **no cost on the training
critical path**, and re-run later with different summaries without retraining.

**The two routes are scientifically equivalent.** A checkpoint is the model at
that epoch; embedding under `eval()` and `no_grad()` is deterministic and
consumes no RNG, so embeddings recovered from a checkpoint are bit-identical to
embeddings taken synchronously. Nothing is lost by deferring, and the deferred
route gains re-runnability.

**Outer-held-out is unreachable by construction, not by discipline.**
`InnerFoldPartitions` carries an inner-training index set and an
inner-validation index set. It has no third field, so there is no argument that
could carry the outer-held-out fold or TEST -- the same pattern
`t1_fold_authority` uses, where the partition is hard-coded rather than passed.
Alternative-epoch inspection of held-out subjects is therefore not something
this module declines to do; it is something it cannot express.

**It does not select.** Nothing here returns a preferred epoch, and nothing here
may be consulted by the registered selection rule.
"""

from __future__ import annotations

import dataclasses
import pathlib
from dataclasses import dataclass, field
from typing import Callable, Final, Sequence

import numpy as np
import torch

from cardiosentinel.neural.e11_checkpoints import (
    CheckpointIdentity,
    CheckpointRecord,
    load_checkpoint_for_audit,
)
from cardiosentinel.neural.e11_instrumentation import (
    E11InstrumentationError,
    StreamGeometrySummary,
    class_direction_consensus,
    stream_geometry_summaries,
)

__all__ = [
    "E11_GEOMETRY_TRAJECTORY_SCHEMA_VERSION",
    "InnerFoldPartitions",
    "EpochGeometry",
    "epoch_geometry",
    "geometry_trajectory",
    "run_inner_geometry_driver",
]

E11_GEOMETRY_TRAJECTORY_SCHEMA_VERSION: Final[str] = "e11-geometry-trajectory-v1"

#: The consensus partition, hard-coded. Never a parameter.
CONSENSUS_PARTITION: Final[str] = "inner_train"


@dataclass(frozen=True, slots=True)
class InnerFoldPartitions:
    """The only partitions this module can see: inner-train and inner-validation.

    There is deliberately no `held_out`, `outer`, `test` or generic `partition`
    field. A caller who wants to inspect the outer fold at an alternative epoch
    has no way to say so.
    """

    fold: int
    inner_train_indices: np.ndarray
    inner_validation_indices: np.ndarray

    def __post_init__(self) -> None:
        if self.fold not in (0, 1, 2):
            raise E11InstrumentationError(f"unknown outer fold: {self.fold!r}")
        train = np.asarray(self.inner_train_indices).ravel()
        validation = np.asarray(self.inner_validation_indices).ravel()
        if train.size == 0 or validation.size == 0:
            raise E11InstrumentationError("both inner partitions must be non-empty")
        if np.intersect1d(train, validation).size:
            raise E11InstrumentationError(
                "inner-train and inner-validation overlap; the consensus would "
                "then be contaminated by the partition it is scored against"
            )


@dataclass(frozen=True, slots=True)
class EpochGeometry:
    """One epoch's geometry, reconstructed from that epoch's checkpoint."""

    fold: int
    arm: str
    epoch: int
    checkpoint_sha256: str
    consensus_partition: str
    consensus_streams: int
    train_cosine_median: float
    train_cosine_min: float
    train_negative_cosine_count: int
    inner_validation_summaries: Sequence[StreamGeometrySummary] = field(
        default_factory=tuple
    )
    schema: str = E11_GEOMETRY_TRAJECTORY_SCHEMA_VERSION


def _stream_deltas(
    embeddings: np.ndarray, labels: np.ndarray, streams: np.ndarray
) -> list[np.ndarray]:
    deltas: list[np.ndarray] = []
    streams = np.asarray(streams).astype(str)
    for stream in np.unique(streams):
        mask = streams == stream
        rows, targets = embeddings[mask], labels[mask]
        positive, negative = targets == 1, targets == 0
        if positive.sum() == 0 or negative.sum() == 0:
            continue
        deltas.append(rows[positive].mean(axis=0) - rows[negative].mean(axis=0))
    return deltas


def epoch_geometry(
    *,
    checkpoint: CheckpointRecord,
    model_factory: Callable[[], torch.nn.Module],
    embed: Callable[[torch.nn.Module, np.ndarray], np.ndarray],
    partitions: InnerFoldPartitions,
    labels: np.ndarray,
    subjects: np.ndarray,
    streams: np.ndarray,
    expected_identity: CheckpointIdentity | None = None,
) -> EpochGeometry:
    """Reconstruct one epoch's geometry from its checkpoint. Read-only.

    `embed` is supplied by the caller and is only ever handed index sets drawn
    from `partitions`, so this function cannot reach a row outside the two
    inner partitions even if the caller's data accessor could.
    """
    if partitions.fold != checkpoint.identity.fold:
        raise E11InstrumentationError(
            f"partitions are for fold {partitions.fold} but the checkpoint is "
            f"for fold {checkpoint.identity.fold}"
        )
    state = load_checkpoint_for_audit(
        checkpoint.path, checkpoint.sha256, expected_identity
    )
    model = model_factory()
    model.load_state_dict(state)
    model.eval()

    with torch.no_grad():
        train_embeddings = np.asarray(
            embed(model, partitions.inner_train_indices), dtype=np.float64
        )
        validation_embeddings = np.asarray(
            embed(model, partitions.inner_validation_indices), dtype=np.float64
        )

    train_index = partitions.inner_train_indices
    deltas = _stream_deltas(
        train_embeddings,
        np.asarray(labels)[train_index],
        np.asarray(streams)[train_index],
    )
    consensus = class_direction_consensus(deltas)
    cosines = np.array(
        [
            float(delta @ consensus / np.linalg.norm(delta))
            for delta in deltas
            if np.linalg.norm(delta) > 0
        ]
    )

    validation_index = partitions.inner_validation_indices
    summaries = stream_geometry_summaries(
        validation_embeddings,
        np.asarray(labels)[validation_index],
        np.asarray(subjects)[validation_index],
        np.asarray(streams)[validation_index],
        consensus,
    )
    return EpochGeometry(
        fold=checkpoint.identity.fold,
        arm=checkpoint.identity.arm,
        epoch=checkpoint.identity.epoch,
        checkpoint_sha256=checkpoint.sha256,
        consensus_partition=CONSENSUS_PARTITION,
        consensus_streams=len(deltas),
        train_cosine_median=float(np.median(cosines)),
        train_cosine_min=float(cosines.min()),
        train_negative_cosine_count=int((cosines < 0).sum()),
        inner_validation_summaries=tuple(summaries),
    )


def geometry_trajectory(
    *,
    checkpoints: Sequence[CheckpointRecord],
    model_factory: Callable[[], torch.nn.Module],
    embed: Callable[[torch.nn.Module, np.ndarray], np.ndarray],
    partitions: InnerFoldPartitions,
    labels: np.ndarray,
    subjects: np.ndarray,
    streams: np.ndarray,
) -> list[EpochGeometry]:
    """Reconstruct the whole phase-1 trajectory, in epoch order."""
    ordered = sorted(checkpoints, key=lambda record: record.identity.epoch)
    return [
        epoch_geometry(
            checkpoint=record,
            model_factory=model_factory,
            embed=embed,
            partitions=partitions,
            labels=labels,
            subjects=subjects,
            streams=streams,
        )
        for record in ordered
    ]


# --------------------------------------------------------------------------
# driver: reconstruct the whole diagnostic trajectory, and index it
# --------------------------------------------------------------------------


def run_inner_geometry_driver(
    *,
    checkpoints: Sequence[CheckpointRecord],
    model_factory: Callable[[], torch.nn.Module],
    embed: Callable[[torch.nn.Module, np.ndarray], np.ndarray],
    partitions: InnerFoldPartitions,
    labels: np.ndarray,
    subjects: np.ndarray,
    streams: np.ndarray,
    inner_split_digest: str,
    output_path: pathlib.Path,
) -> dict[str, object]:
    """Drive the read-only trajectory over every retained phase-1 checkpoint.

    Diagnostic only. It reads checkpoints that already exist, uses inner-train
    for the consensus and inner-validation for the trajectory, and **cannot
    influence the selected epoch** -- selection happened during phase 1 and is
    already sealed by the time this runs.
    """
    import hashlib as _hashlib
    import json as _json

    from cardiosentinel.baseline.cache import write_json_atomic

    entries: list[dict[str, object]] = []
    for geometry in geometry_trajectory(
        checkpoints=checkpoints,
        model_factory=model_factory,
        embed=embed,
        partitions=partitions,
        labels=labels,
        subjects=subjects,
        streams=streams,
    ):
        record = {
            "fold": geometry.fold,
            "arm": geometry.arm,
            "epoch": geometry.epoch,
            "checkpoint_sha256": geometry.checkpoint_sha256,
            "inner_split_digest": inner_split_digest,
            "consensus_partition": geometry.consensus_partition,
            "consensus_streams": geometry.consensus_streams,
            "train_cosine_median": geometry.train_cosine_median,
            "train_cosine_min": geometry.train_cosine_min,
            "train_negative_cosine_count": geometry.train_negative_cosine_count,
            "summaries": [
                dataclasses.asdict(summary)
                for summary in geometry.inner_validation_summaries
            ],
        }
        record["geometry_record_digest"] = _hashlib.sha256(
            _json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        entries.append(record)

    manifest = {
        "schema": E11_GEOMETRY_TRAJECTORY_SCHEMA_VERSION,
        "diagnostic_only": True,
        "influences_selection": False,
        "consensus_partition": CONSENSUS_PARTITION,
        "scored_partition": "inner_validation",
        "inner_split_digest": inner_split_digest,
        "epochs": entries,
    }
    write_json_atomic(pathlib.Path(output_path), manifest)
    return manifest
