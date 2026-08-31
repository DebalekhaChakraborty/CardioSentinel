"""Per-epoch observability for E11-class representation experiments.

E11 ATTEMPT 2 ran correctly and was under-instrumented. The E12a audit
(`docs/experiments/b4/B4_E12A_TRAINING_DYNAMICS_SELECTION_AUDIT_V1.md`) could
establish that checkpoint selection was unstable, and could **not** establish
whether the morphology auxiliary objective was mature at the selected epoch --
because the auxiliary loss was never logged as a separate term. That single
missing scalar is why E12a returned "no further conclusion" rather than a
finding.

This module supplies the missing instrumentation for **future** authorized
runs. It records nothing about E11 ATTEMPT 2, regenerates no historical
checkpoint, and changes no scientific behaviour.

**It is observability only.** Every function here is read-only with respect to
the model: geometry and metrics are computed under `torch.no_grad()` from
detached tensors, no function consumes global RNG, and nothing here may be
consulted by a checkpoint-selection rule. The registered selection rule --
maximum inner pooled AUPRC, earliest epoch wins an exact tie -- is unchanged
and lives elsewhere.

**Semantic absence, not fabricated zero.** A B0 fit has no auxiliary term. Its
auxiliary fields are `None` and serialize as JSON `null`. A `0.0` would be a
measurement claim, and a false one.

**Fail closed.** An epoch record is validated in full in memory and only then
written atomically. A crash cannot leave a half-written record that reads as
complete: every record carries a digest over its own canonical form, and the
loader refuses a log whose digests do not verify.

**TEST is unreachable by construction.** `E11FoldAuthority` binds an explicit
subject set and exposes no partition parameter, so no caller can request TEST
-- there is no argument that could carry it.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Final, Mapping, Sequence

import numpy as np

from cardiosentinel.baseline.cache import write_json_atomic

__all__ = [
    "E11_INSTRUMENTATION_SCHEMA_VERSION",
    "E11InstrumentationError",
    "EpochLossRecord",
    "InnerValidationRecord",
    "StreamGeometrySummary",
    "SelectionEvidence",
    "OperatingPointRecord",
    "F1_THRESHOLD_DERIVATION",
    "PERMITTED_THRESHOLD_SOURCES",
    "evaluate_at_frozen_threshold",
    "EpochEvidenceLog",
    "f1_optimal_threshold",
    "class_direction_consensus",
    "stream_geometry_summaries",
    "inner_validation_record",
    "load_epoch_evidence",
    "checkpoint_sha256",
]

E11_INSTRUMENTATION_SCHEMA_VERSION: Final[str] = "e11-instrumentation-v1"

class E11InstrumentationError(RuntimeError):
    """Instrumentation contract violated. Never raised by scientific code."""


# --------------------------------------------------------------------------
# records
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class EpochLossRecord:
    """One phase-1 epoch's loss decomposition.

    `total_loss` must equal `bce_loss + aux_loss_scaled` for an auxiliary arm,
    and `bce_loss` exactly for a primary-only arm. That identity is asserted on
    construction, so a runner that accumulates the combined scalar and forgets
    to split it cannot produce a record that validates.
    """

    epoch: int
    bce_loss: float
    total_loss: float
    learning_rate: float
    seconds: float
    aux_loss_raw: float | None = None
    aux_loss_scaled: float | None = None
    aux_lambda: float | None = None
    arm: str = ""

    def __post_init__(self) -> None:
        if self.epoch < 1:
            raise E11InstrumentationError(f"epoch must be >= 1, got {self.epoch}")
        for name in ("bce_loss", "total_loss", "learning_rate", "seconds"):
            value = getattr(self, name)
            if not np.isfinite(value):
                raise E11InstrumentationError(f"{name} is not finite: {value!r}")
        has_aux = self.aux_loss_raw is not None
        if has_aux != (self.aux_loss_scaled is not None):
            raise E11InstrumentationError(
                "aux_loss_raw and aux_loss_scaled must be present or absent together"
            )
        if not has_aux:
            # Primary-only arm: absence is the measurement, not zero.
            if abs(self.total_loss - self.bce_loss) > 1e-9:
                raise E11InstrumentationError(
                    "arm has no auxiliary term, so total_loss must equal bce_loss "
                    f"({self.total_loss!r} vs {self.bce_loss!r})"
                )
            return
        if self.aux_lambda is None:
            raise E11InstrumentationError("aux_lambda required when auxiliary present")
        for name in ("aux_loss_raw", "aux_loss_scaled", "aux_lambda"):
            value = getattr(self, name)
            if not np.isfinite(value):
                raise E11InstrumentationError(f"{name} is not finite: {value!r}")
        expected = self.aux_lambda * self.aux_loss_raw
        if abs(self.aux_loss_scaled - expected) > 1e-6 * max(1.0, abs(expected)):
            raise E11InstrumentationError(
                "aux_loss_scaled must equal aux_lambda * aux_loss_raw "
                f"({self.aux_loss_scaled!r} vs {expected!r})"
            )
        composed = self.bce_loss + self.aux_loss_scaled
        if abs(self.total_loss - composed) > 1e-6 * max(1.0, abs(composed)):
            raise E11InstrumentationError(
                "total_loss must equal bce_loss + aux_loss_scaled "
                f"({self.total_loss!r} vs {composed!r})"
            )


@dataclass(frozen=True, slots=True)
class InnerValidationRecord:
    """Inner-validation metrics for one epoch, with their denominators.

    Prevalence and the positive/negative counts travel with the metrics
    because AUPRC is bounded below by prevalence, and E11's inner-validation
    prevalence ran 8.4x-12.1x below inner-train.
    """

    epoch: int
    auprc: float
    auroc: float
    f1_optimal_threshold: float
    prevalence: float
    n_positive: int
    n_negative: int
    partition: str = "inner_validation"

    def __post_init__(self) -> None:
        if self.n_positive < 0 or self.n_negative < 0:
            raise E11InstrumentationError("counts must be non-negative")
        total = self.n_positive + self.n_negative
        if total == 0:
            raise E11InstrumentationError("inner-validation partition is empty")
        expected = self.n_positive / total
        if abs(self.prevalence - expected) > 1e-9:
            raise E11InstrumentationError(
                f"prevalence {self.prevalence!r} disagrees with counts {expected!r}"
            )


@dataclass(frozen=True, slots=True)
class StreamGeometrySummary:
    """One stream's class-direction geometry at one epoch.

    A single-class stream is **preserved with undefined fields**, never
    silently dropped: `delta_norm`, `cosine_to_consensus` and
    `negative_cosine` are `None` and `evaluable` is `False`. Dropping such a
    stream would make the denominator of "negative-cosine fraction" move
    between epochs without record.
    """

    subject_id: str
    stream_id: str
    n_positive: int
    n_negative: int
    evaluable: bool
    delta_norm: float | None = None
    cosine_to_consensus: float | None = None
    negative_cosine: bool | None = None

    def __post_init__(self) -> None:
        if self.evaluable:
            if self.n_positive == 0 or self.n_negative == 0:
                raise E11InstrumentationError(
                    "an evaluable stream needs both classes present"
                )
            if self.delta_norm is None or self.cosine_to_consensus is None:
                raise E11InstrumentationError("evaluable stream missing geometry")
            if self.negative_cosine != (self.cosine_to_consensus < 0.0):
                raise E11InstrumentationError(
                    "negative_cosine disagrees with cosine_to_consensus"
                )
        else:
            if any(
                value is not None
                for value in (
                    self.delta_norm,
                    self.cosine_to_consensus,
                    self.negative_cosine,
                )
            ):
                raise E11InstrumentationError(
                    "a non-evaluable stream must carry undefined geometry, not values"
                )


@dataclass(frozen=True, slots=True)
class SelectionEvidence:
    """What the registered selection rule saw, and what it chose.

    This records the decision. It does not make it, and nothing in this module
    may be consulted by the rule.
    """

    selected_epoch: int
    selected_checkpoint_sha256: str
    best_auprc: float
    second_best_auprc: float | None
    selection_margin: float | None
    inner_f1_optimal_threshold: float
    partitions: Mapping[str, str]
    retained_epochs: Sequence[int] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.second_best_auprc is None:
            if self.selection_margin is not None:
                raise E11InstrumentationError(
                    "selection_margin undefined when there is no second-best"
                )
            return
        expected = self.best_auprc - self.second_best_auprc
        margin = self.selection_margin
        if margin is None or abs(margin - expected) > 1e-12:
            raise E11InstrumentationError(
                f"selection_margin must equal best - second_best ({expected!r})"
            )
        if self.selected_epoch not in tuple(self.retained_epochs):
            raise E11InstrumentationError(
                "retention policy must keep the selected epoch's checkpoint"
            )


#: Threshold derivation, versioned so a receipt records *how* it was obtained.
F1_THRESHOLD_DERIVATION: Final[str] = "max-f1-over-score-ranks-v1"

#: The only partitions a frozen operating point may be derived from. The outer
#: held-out fold is absent by design: E11 report s9.1 records that deriving a
#: threshold from held-out scores is circular and forbidden by plan s3.2.
PERMITTED_THRESHOLD_SOURCES: Final[frozenset[str]] = frozenset(
    {"inner_validation", "inner_train"}
)


@dataclass(frozen=True, slots=True)
class OperatingPointRecord:
    """Sensitivity / specificity at a threshold frozen on an inner partition.

    This closes E11 report s9.1 prospectively. The threshold, the partition it
    came from, and the derivation method all travel with the metrics, so a
    later reader can tell what was frozen and when -- which is precisely what
    ATTEMPT 2 failed to persist.
    """

    threshold: float
    threshold_source_partition: str
    threshold_derivation: str
    evaluated_partition: str
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int
    sensitivity: float
    specificity: float

    def __post_init__(self) -> None:
        if self.threshold_source_partition not in PERMITTED_THRESHOLD_SOURCES:
            raise E11InstrumentationError(
                "an operating point may only be frozen on "
                f"{sorted(PERMITTED_THRESHOLD_SOURCES)}; refusing "
                f"{self.threshold_source_partition!r} -- a threshold derived "
                "from outer-held-out scores is circular"
            )
        positives = self.true_positive + self.false_negative
        negatives = self.true_negative + self.false_positive
        if positives == 0 or negatives == 0:
            raise E11InstrumentationError(
                "sensitivity and specificity are undefined on a single-class set"
            )
        if abs(self.sensitivity - self.true_positive / positives) > 1e-9:
            raise E11InstrumentationError("sensitivity disagrees with its counts")
        if abs(self.specificity - self.true_negative / negatives) > 1e-9:
            raise E11InstrumentationError("specificity disagrees with its counts")


def evaluate_at_frozen_threshold(
    labels: np.ndarray,
    scores: np.ndarray,
    threshold: float,
    threshold_source_partition: str,
    evaluated_partition: str,
    threshold_derivation: str = F1_THRESHOLD_DERIVATION,
) -> OperatingPointRecord:
    """Score an already-frozen threshold. It never derives one from `scores`.

    The threshold is an argument, not a return value: this function cannot
    produce an operating point tuned to the partition it is scoring, which is
    the whole point of freezing it upstream.
    """
    labels = np.asarray(labels).astype(np.int64).ravel()
    scores = np.asarray(scores, dtype=np.float64).ravel()
    if labels.size != scores.size:
        raise E11InstrumentationError("labels and scores differ in length")
    predicted = scores >= float(threshold)
    true_positive = int(np.sum(predicted & (labels == 1)))
    false_positive = int(np.sum(predicted & (labels == 0)))
    true_negative = int(np.sum(~predicted & (labels == 0)))
    false_negative = int(np.sum(~predicted & (labels == 1)))
    positives = true_positive + false_negative
    negatives = true_negative + false_positive
    if positives == 0 or negatives == 0:
        raise E11InstrumentationError(
            "sensitivity and specificity are undefined on a single-class set"
        )
    return OperatingPointRecord(
        threshold=float(threshold),
        threshold_source_partition=threshold_source_partition,
        threshold_derivation=threshold_derivation,
        evaluated_partition=evaluated_partition,
        true_positive=true_positive,
        false_positive=false_positive,
        true_negative=true_negative,
        false_negative=false_negative,
        sensitivity=true_positive / positives,
        specificity=true_negative / negatives,
    )


# --------------------------------------------------------------------------
# metric and geometry computation -- read-only, no RNG, no gradient
# --------------------------------------------------------------------------


def f1_optimal_threshold(
    labels: np.ndarray,
    scores: np.ndarray,
    source_partition: str = "inner_validation",
    ) -> tuple[float, float]:
    """Return (threshold, f1) maximizing F1, ties broken by lower threshold.

    **Fails closed on the partition.** A threshold derived from outer-held-out
    scores is circular and is forbidden by plan s3.2; rather than trusting
    callers not to do it, this function refuses any `source_partition` outside
    `PERMITTED_THRESHOLD_SOURCES`. Passing held-out scores here is an error, not
    a silently-accepted shortcut.
    """
    if source_partition not in PERMITTED_THRESHOLD_SOURCES:
        raise E11InstrumentationError(
            "a threshold may only be derived from "
            f"{sorted(PERMITTED_THRESHOLD_SOURCES)}; refusing "
            f"{source_partition!r} -- deriving an operating point from "
            "outer-held-out scores is circular"
        )
    labels = np.asarray(labels).astype(np.int64).ravel()
    scores = np.asarray(scores, dtype=np.float64).ravel()
    if labels.size != scores.size:
        raise E11InstrumentationError("labels and scores differ in length")
    positives = int(labels.sum())
    if positives == 0 or positives == labels.size:
        raise E11InstrumentationError("F1 threshold undefined on a single-class set")
    order = np.argsort(-scores, kind="stable")
    ranked = labels[order]
    tp = np.cumsum(ranked)
    predicted = np.arange(1, labels.size + 1)
    precision = tp / predicted
    recall = tp / positives
    denominator = precision + recall
    f1 = np.zeros_like(denominator)
    np.divide(2.0 * precision * recall, denominator, out=f1, where=denominator > 0)
    best = int(np.argmax(f1))
    return float(scores[order][best]), float(f1[best])


def class_direction_consensus(deltas: Sequence[np.ndarray]) -> np.ndarray:
    """E10's frozen aggregation: unit-normalise, equal weight per stream, renormalise.

    Equal weight per stream is the point: window counts are not replication.
    """
    unit = []
    for delta in deltas:
        norm = float(np.linalg.norm(delta))
        if norm > 0.0:
            unit.append(np.asarray(delta, dtype=np.float64) / norm)
    if not unit:
        raise E11InstrumentationError("no evaluable stream to build a consensus from")
    consensus = np.mean(np.stack(unit), axis=0)
    norm = float(np.linalg.norm(consensus))
    if norm == 0.0:
        raise E11InstrumentationError("consensus degenerated to the zero vector")
    return consensus / norm


def _stream_delta(
    embeddings: np.ndarray, labels: np.ndarray
) -> tuple[np.ndarray | None, int, int]:
    positives = labels == 1
    negatives = labels == 0
    n_pos, n_neg = int(positives.sum()), int(negatives.sum())
    if n_pos == 0 or n_neg == 0:
        return None, n_pos, n_neg
    delta = embeddings[positives].mean(axis=0) - embeddings[negatives].mean(axis=0)
    return delta, n_pos, n_neg


def stream_geometry_summaries(
    embeddings: np.ndarray,
    labels: np.ndarray,
    subjects: np.ndarray,
    streams: np.ndarray,
    consensus: np.ndarray,
) -> list[StreamGeometrySummary]:
    """Summarize per-stream geometry against an already-frozen consensus.

    The consensus is passed in, never derived here, so that the caller is
    forced to state which partition built it.
    """
    embeddings = np.asarray(embeddings, dtype=np.float64)
    labels = np.asarray(labels).astype(np.int64).ravel()
    summaries: list[StreamGeometrySummary] = []
    for stream in np.unique(np.asarray(streams).astype(str)):
        mask = np.asarray(streams).astype(str) == stream
        delta, n_pos, n_neg = _stream_delta(embeddings[mask], labels[mask])
        subject = str(np.asarray(subjects).astype(str)[mask][0])
        if delta is None:
            summaries.append(
                StreamGeometrySummary(
                    subject_id=subject,
                    stream_id=str(stream),
                    n_positive=n_pos,
                    n_negative=n_neg,
                    evaluable=False,
                )
            )
            continue
        norm = float(np.linalg.norm(delta))
        cosine = float(delta @ consensus / norm) if norm > 0.0 else 0.0
        summaries.append(
            StreamGeometrySummary(
                subject_id=subject,
                stream_id=str(stream),
                n_positive=n_pos,
                n_negative=n_neg,
                evaluable=True,
                delta_norm=norm,
                cosine_to_consensus=cosine,
                negative_cosine=cosine < 0.0,
            )
        )
    return summaries


def inner_validation_record(
    epoch: int, labels: np.ndarray, scores: np.ndarray
) -> InnerValidationRecord:
    """Compute the inner-validation record from persisted-shaped inputs.

    Deliberately takes arrays rather than a model: the same function reproduces
    the metrics later from the persisted scores, which is what makes the
    persisted evidence auditable without retraining.
    """
    from sklearn.metrics import average_precision_score, roc_auc_score

    labels = np.asarray(labels).astype(np.int64).ravel()
    scores = np.asarray(scores, dtype=np.float64).ravel()
    n_pos = int(labels.sum())
    n_neg = int(labels.size - n_pos)
    threshold, _ = f1_optimal_threshold(labels, scores)
    return InnerValidationRecord(
        epoch=epoch,
        auprc=float(average_precision_score(labels, scores)),
        auroc=float(roc_auc_score(labels, scores)),
        f1_optimal_threshold=threshold,
        prevalence=n_pos / labels.size,
        n_positive=n_pos,
        n_negative=n_neg,
    )


def checkpoint_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


# --------------------------------------------------------------------------
# fail-closed epoch log
# --------------------------------------------------------------------------


def _record_digest(payload: Mapping[str, Any]) -> str:
    body = {key: value for key, value in payload.items() if key != "record_digest"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(slots=True)
class EpochEvidenceLog:
    """Append-only per-epoch evidence, written atomically and digest-sealed.

    Each epoch is composed and validated entirely in memory, stamped with a
    digest over its own canonical form, and only then does the whole log go to
    disk through a same-directory temporary-file-then-rename. An interrupted
    run therefore leaves either the previous complete log or the new complete
    log, never a torn record that reads as finished.
    """

    path: Path
    fold: int
    arm: str
    records: list[dict[str, Any]] = field(default_factory=list)

    def record_epoch(
        self,
        losses: EpochLossRecord,
        inner: InnerValidationRecord,
        geometry: Sequence[StreamGeometrySummary],
        geometry_consensus_partition: str,
        inner_scores_path: str | None = None,
        inner_scores_sha256: str | None = None,
        checkpoint_sha256: str | None = None,
    ) -> None:
        if losses.epoch != inner.epoch:
            raise E11InstrumentationError(
                f"epoch mismatch: losses {losses.epoch}, inner {inner.epoch}"
            )
        if any(record["epoch"] == losses.epoch for record in self.records):
            raise E11InstrumentationError(f"epoch {losses.epoch} already recorded")
        if geometry_consensus_partition == "inner_validation":
            raise E11InstrumentationError(
                "the consensus may never be built from inner-validation; it must "
                "come from that epoch's inner-training representations only"
            )
        payload: dict[str, Any] = {
            "schema": E11_INSTRUMENTATION_SCHEMA_VERSION,
            "fold": self.fold,
            "arm": self.arm,
            "epoch": losses.epoch,
            "training": asdict(losses),
            "inner_validation": asdict(inner),
            "geometry": [asdict(summary) for summary in geometry],
            "geometry_consensus_partition": geometry_consensus_partition,
            "inner_scores_path": inner_scores_path,
            "inner_scores_sha256": inner_scores_sha256,
            "checkpoint_sha256": checkpoint_sha256,
            "record_complete": True,
        }
        payload["record_digest"] = _record_digest(payload)
        self.records.append(payload)
        self._flush()

    def _flush(self) -> None:
        write_json_atomic(
            self.path,
            {
                "schema": E11_INSTRUMENTATION_SCHEMA_VERSION,
                "fold": self.fold,
                "arm": self.arm,
                "epochs": self.records,
            },
        )


def load_epoch_evidence(path: Path) -> list[dict[str, Any]]:
    """Load an epoch log, refusing any record whose digest does not verify."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != E11_INSTRUMENTATION_SCHEMA_VERSION:
        raise E11InstrumentationError(f"unknown schema: {payload.get('schema')!r}")
    records = payload.get("epochs", [])
    for record in records:
        if not record.get("record_complete"):
            raise E11InstrumentationError(
                f"epoch {record.get('epoch')!r} is not marked complete"
            )
        if record.get("record_digest") != _record_digest(record):
            raise E11InstrumentationError(
                f"epoch {record.get('epoch')!r} failed its digest check"
            )
    return records
