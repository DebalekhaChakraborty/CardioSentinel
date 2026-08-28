"""The registered E11 outer geometry endpoint, for the final phase-2 models.

**This is the scientific endpoint, not the diagnostic trajectory.** It answers
the registered primary question -- does the ischemia class direction stay stable
on unseen subjects -- from the final phase-2 representation of each fold and arm.

`e11_geometry_trajectory` answers a different, *diagnostic* question about how
geometry moved across phase-1 epochs, using inner-validation only. The two must
never be confused or pooled, so they carry different schema strings and
different namespaces: `e11-outer-geometry-v1` here,
`e11-geometry-trajectory-v1` there. A reader who finds one file can tell from
its schema which question it answers.

The construction is E10's frozen aggregation, unchanged: each arm's consensus is
built from **that arm's own outer-train representation**, unit-normalised per
stream with equal weight per stream, renormalised, and frozen before any
held-out row is embedded.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Final, Sequence

import numpy as np

from cardiosentinel.baseline.cache import write_json_atomic
from cardiosentinel.neural.e11_instrumentation import (
    E11InstrumentationError,
    StreamGeometrySummary,
    class_direction_consensus,
    stream_geometry_summaries,
)

__all__ = [
    "E11_OUTER_GEOMETRY_SCHEMA_VERSION",
    "OuterGeometry",
    "outer_geometry",
    "write_outer_geometry",
]

E11_OUTER_GEOMETRY_SCHEMA_VERSION: Final[str] = "e11-outer-geometry-v1"

#: Hard-coded. The consensus partition is never a parameter.
CONSENSUS_PARTITION: Final[str] = "outer_train"


@dataclass(frozen=True, slots=True)
class OuterGeometry:
    """One fold/arm's registered outer geometry."""

    fold: int
    arm: str
    consensus_partition: str
    consensus_streams: int
    train_cosine_median: float
    train_cosine_min: float
    train_negative_cosine_count: int
    train_norm_median: float
    held_out_streams_evaluable: int
    cosine_median: float
    cosine_min: float
    negative_cosine_count: int
    negative_cosine_fraction: float
    norm_median: float
    within_subject_median: float | None
    within_subject_subjects: int
    summaries: Sequence[StreamGeometrySummary] = field(default_factory=tuple)
    schema: str = E11_OUTER_GEOMETRY_SCHEMA_VERSION


def _stream_deltas(
    embeddings: np.ndarray, labels: np.ndarray, streams: np.ndarray
) -> dict[str, np.ndarray]:
    deltas: dict[str, np.ndarray] = {}
    streams = np.asarray(streams).astype(str)
    for stream in np.unique(streams):
        mask = streams == stream
        rows, targets = embeddings[mask], labels[mask]
        positive, negative = targets == 1, targets == 0
        if positive.sum() == 0 or negative.sum() == 0:
            continue
        deltas[str(stream)] = rows[positive].mean(axis=0) - rows[negative].mean(axis=0)
    return deltas


def outer_geometry(
    *,
    fold: int,
    arm: str,
    outer_train_embeddings: np.ndarray,
    outer_train_labels: np.ndarray,
    outer_train_streams: np.ndarray,
    held_out_embeddings: np.ndarray,
    held_out_labels: np.ndarray,
    held_out_subjects: np.ndarray,
    held_out_streams: np.ndarray,
) -> OuterGeometry:
    """Consensus from this arm's outer-train, then held-out geometry against it."""
    train_deltas = _stream_deltas(
        np.asarray(outer_train_embeddings, dtype=np.float64),
        np.asarray(outer_train_labels).astype(np.int64),
        outer_train_streams,
    )
    if not train_deltas:
        raise E11InstrumentationError("no evaluable outer-train stream for a consensus")
    consensus = class_direction_consensus(list(train_deltas.values()))
    train_norms = np.array([float(np.linalg.norm(d)) for d in train_deltas.values()])
    train_cosines = np.array(
        [
            float(d @ consensus / np.linalg.norm(d))
            for d in train_deltas.values()
            if np.linalg.norm(d) > 0
        ]
    )

    summaries = stream_geometry_summaries(
        held_out_embeddings,
        held_out_labels,
        held_out_subjects,
        held_out_streams,
        consensus,
    )
    evaluable = [s for s in summaries if s.evaluable]
    if not evaluable:
        raise E11InstrumentationError("no evaluable held-out stream")
    cosines = np.array([s.cosine_to_consensus for s in evaluable], dtype=np.float64)
    norms = np.array([s.delta_norm for s in evaluable], dtype=np.float64)

    held_out_deltas = _stream_deltas(
        np.asarray(held_out_embeddings, dtype=np.float64),
        np.asarray(held_out_labels).astype(np.int64),
        held_out_streams,
    )
    by_subject: dict[str, list[str]] = {}
    for summary in evaluable:
        by_subject.setdefault(summary.subject_id, []).append(summary.stream_id)
    within: list[float] = []
    for members in by_subject.values():
        if len(members) < 2:
            continue
        pairwise = [
            float(
                held_out_deltas[a]
                @ held_out_deltas[b]
                / (
                    np.linalg.norm(held_out_deltas[a])
                    * np.linalg.norm(held_out_deltas[b])
                )
            )
            for i, a in enumerate(members)
            for b in members[i + 1 :]
        ]
        within.append(float(np.mean(pairwise)))

    return OuterGeometry(
        fold=fold,
        arm=arm,
        consensus_partition=CONSENSUS_PARTITION,
        consensus_streams=len(train_deltas),
        train_cosine_median=float(np.median(train_cosines)),
        train_cosine_min=float(train_cosines.min()),
        train_negative_cosine_count=int((train_cosines < 0).sum()),
        train_norm_median=float(np.median(train_norms)),
        held_out_streams_evaluable=len(evaluable),
        cosine_median=float(np.median(cosines)),
        cosine_min=float(cosines.min()),
        negative_cosine_count=int((cosines < 0).sum()),
        negative_cosine_fraction=float((cosines < 0).mean()),
        norm_median=float(np.median(norms)),
        within_subject_median=float(np.median(within)) if within else None,
        within_subject_subjects=len(within),
        summaries=tuple(summaries),
    )


def write_outer_geometry(geometry: OuterGeometry, path: Path) -> str:
    payload = asdict(geometry)
    payload["summaries"] = [asdict(s) for s in geometry.summaries]
    payload["geometry_digest"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    write_json_atomic(Path(path), payload)
    return payload["geometry_digest"]
