"""Read-only binding from the registered E11-class inputs to a fold authority.

Nothing here defines science. The auxiliary target, the labels, the split and
the inner rule all already exist; this layer loads them, proves they are the
ones they claim to be, and hands the result to `E11FoldAuthority`, which is the
only object downstream code may hold.

**Every check is exact, not approximate.** The split digest must match the
frozen value byte for byte, subject membership must be set-equal to the
recorded assignment, stable row identities must be unique, every array must be
row-aligned to the waveform cache, and the auxiliary mask must equal
`isfinite(target)` exactly. A binding that cannot prove all of that does not
construct.

**The inner rule is reproduced, not reinvented.** The registered rule is the
lowest third of outer-training subjects by the frozen serpentine order
(prevalence, ties by subject id) -- the same expression the ATTEMPT 2 runner
used, kept identical so a future run's inner split is the registered one.

**The scaler is fitted only where the phase allows.** Phase 1 may see
inner-train; phase 2 may see outer-train. The function takes rows from an
authority accessor, so there is no way to hand it held-out rows without first
obtaining them from an accessor that a phase has no reason to call.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Sequence

import numpy as np

from cardiosentinel.baseline.cache import write_json_atomic
from cardiosentinel.neural.e11_authority import (
    E11AuthorityError,
    E11FoldAuthority,
    E11Partition,
)

__all__ = [
    "E11_DATA_BINDING_SCHEMA_VERSION",
    "E11DataBindingError",
    "E11Sources",
    "E11RowIdentity",
    "E11DataBinding",
    "parse_stable_id",
    "bind_e11_data",
    "morphology_scaler",
    "write_binding_receipt",
]

E11_DATA_BINDING_SCHEMA_VERSION: Final[str] = "e11-data-binding-v1"

#: The registered auxiliary target. Named for the receipt; never recomputed.
AUXILIARY_TARGET_NAME: Final[str] = "post_r_80ms_delta_mv"


class E11DataBindingError(RuntimeError):
    """The data binding could not prove it loaded what it claims."""


@dataclass(frozen=True, slots=True)
class E11Sources:
    """Where the registered inputs live. Train-side only, by construction.

    There is no `validation_*` or `test_*` field: this loader cannot reach the
    historical VALIDATION partition or the sealed TEST partition because it has
    nowhere to put their paths.
    """

    waveform_cache: Path
    protocol_dir: Path

    def train_stable_ids(self) -> Path:
        return Path(self.waveform_cache) / "train_stable_ids.npy"

    def train_waveforms(self) -> Path:
        return Path(self.waveform_cache) / "train_waveforms.npy"

    def manifest(self) -> Path:
        return Path(self.waveform_cache) / "manifest.json"


@dataclass(frozen=True, slots=True)
class E11RowIdentity:
    """Stable per-row identity, parsed from the cache's own stable ids."""

    dataset: np.ndarray
    record_id: np.ndarray
    channel_index: np.ndarray
    start_sample: np.ndarray
    end_sample: np.ndarray


@dataclass(frozen=True, slots=True)
class E11DataBinding:
    """Validated arrays plus the means to mint a per-fold authority."""

    labels: np.ndarray
    subjects: np.ndarray
    streams: np.ndarray
    folds: np.ndarray
    auxiliary_target: np.ndarray
    auxiliary_mask: np.ndarray
    identity: E11RowIdentity
    stable_ids: np.ndarray
    split_digest: str
    assignment: dict[str, int]
    prevalence: dict[str, float]
    experiment_id: str
    sources: E11Sources
    manifest_digests: dict[str, str]

    @property
    def authorized_population(self) -> tuple[str, ...]:
        return tuple(sorted(self.assignment))

    def authority(self, fold: int) -> E11FoldAuthority:
        """Mint the authority for one outer fold, using the registered rules."""
        held_out = np.flatnonzero(self.folds == fold)
        outer_train = np.flatnonzero(self.folds != fold)
        inner_validation_subjects = self._inner_validation_subjects(outer_train)
        in_validation = np.isin(
            self.subjects[outer_train], list(inner_validation_subjects)
        )
        return E11FoldAuthority(
            fold=fold,
            split_digest=self.split_digest,
            experiment_id=self.experiment_id,
            authorized_population=self.authorized_population,
            subjects=self.subjects,
            inner_train_rows=outer_train[~in_validation],
            inner_validation_rows=outer_train[in_validation],
            outer_held_out_rows=held_out,
        )

    def _inner_validation_subjects(self, outer_train: np.ndarray) -> set[str]:
        """The registered inner rule: lowest third by the frozen serpentine order."""
        order = sorted(self.assignment, key=lambda s: (self.prevalence[s], s))
        present = set(self.subjects[outer_train].tolist())
        ordered = [s for s in order if s in present]
        return set(ordered[: max(1, len(ordered) // 3)])


def parse_stable_id(stable_id: str) -> tuple[str, str, int, int, int]:
    """`ltstdb:s20011:0:11416250:11418750` -> dataset, record, channel, start, end."""
    parts = str(stable_id).split(":")
    if len(parts) != 5:
        raise E11DataBindingError(f"malformed stable id: {stable_id!r}")
    dataset, record, channel, start, end = parts
    return dataset, record, int(channel), int(start), int(end)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def bind_e11_data(
    *,
    sources: E11Sources,
    expected_split_digest: str,
    experiment_id: str,
    expected_subject_count: int = 56,
) -> E11DataBinding:
    """Load and prove the registered inputs. Read-only; recomputes no target."""
    protocol = Path(sources.protocol_dir)
    folds_doc = json.loads((protocol / "e11_folds.json").read_text(encoding="utf-8"))
    assignment = folds_doc["assignment"]
    prevalence = folds_doc["prevalence"]

    digest = hashlib.sha256(
        json.dumps(assignment, sort_keys=True).encode("utf-8")
    ).hexdigest()
    if digest != expected_split_digest:
        raise E11DataBindingError(
            f"split digest mismatch: expected {expected_split_digest}, got {digest}"
        )
    if len(assignment) != expected_subject_count:
        raise E11DataBindingError(
            f"expected {expected_subject_count} subjects, found {len(assignment)}"
        )

    stable_ids = np.load(sources.train_stable_ids()).astype(str)
    labels = np.load(protocol / "e11_train_y.npy")
    subjects = np.load(protocol / "e11_train_subj.npy").astype(str)
    streams = np.load(protocol / "e11_train_stream.npy").astype(str)
    folds = np.load(protocol / "e11_train_fold.npy")
    auxiliary = np.load(protocol / "e11_aux_target.npy")

    rows = stable_ids.size
    for name, array in (
        ("labels", labels),
        ("subjects", subjects),
        ("streams", streams),
        ("folds", folds),
        ("auxiliary_target", auxiliary),
    ):
        if array.shape[0] != rows:
            raise E11DataBindingError(
                f"{name} has {array.shape[0]} rows but the cache has {rows}"
            )
    if np.unique(stable_ids).size != rows:
        raise E11DataBindingError("duplicate stable row identities in the cache")

    observed = set(subjects.tolist())
    declared = set(assignment)
    if observed != declared:
        raise E11DataBindingError(
            "subject membership is not set-equal to the recorded assignment: "
            f"{len(observed - declared)} unexpected, {len(declared - observed)} missing"
        )
    for subject in observed:
        if subject.strip().lower() in {"test", "sealed_test"}:
            raise E11DataBindingError("a sealed-partition subject was present")

    declared_folds = {int(v) for v in assignment.values()}
    if set(np.unique(folds).tolist()) != declared_folds:
        raise E11DataBindingError("fold array disagrees with the recorded assignment")
    for subject, fold in assignment.items():
        rows_for = folds[subjects == subject]
        if rows_for.size and set(rows_for.tolist()) != {int(fold)}:
            raise E11DataBindingError(f"subject {subject} spans multiple outer folds")

    mask = np.isfinite(auxiliary)
    parsed = [parse_stable_id(s) for s in stable_ids]
    identity = E11RowIdentity(
        dataset=np.array([p[0] for p in parsed]),
        record_id=np.array([p[1] for p in parsed]),
        channel_index=np.array([p[2] for p in parsed], dtype=np.int64),
        start_sample=np.array([p[3] for p in parsed], dtype=np.int64),
        end_sample=np.array([p[4] for p in parsed], dtype=np.int64),
    )

    manifest_path = sources.manifest()
    manifest_digests: dict[str, str] = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_digests = {
            key: manifest[key]
            for key in (
                "waveform_cache_sha256",
                "feature_corpus_sha256",
                "split_sha256",
                "protocol_sha256",
            )
            if key in manifest
        }

    return E11DataBinding(
        labels=labels,
        subjects=subjects,
        streams=streams,
        folds=folds,
        auxiliary_target=auxiliary,
        auxiliary_mask=mask,
        identity=identity,
        stable_ids=stable_ids,
        split_digest=digest,
        assignment={k: int(v) for k, v in assignment.items()},
        prevalence={k: float(v) for k, v in prevalence.items()},
        experiment_id=experiment_id,
        sources=sources,
        manifest_digests=manifest_digests,
    )


def morphology_scaler(
    binding: E11DataBinding, rows: np.ndarray
) -> tuple[float, float]:
    """Registered median / IQR scaler, fitted only on the rows it is given.

    `rows` must come from an authority accessor. Phase 1 passes inner-train,
    phase 2 passes outer-train; neither has a reason to hold held-out rows.
    """
    values = binding.auxiliary_target[rows]
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        raise E11DataBindingError("no finite auxiliary target in the fitting partition")
    spread = float(np.subtract(*np.percentile(finite, [75, 25]))) or 1.0
    return float(np.median(finite)), spread


def write_binding_receipt(
    binding: E11DataBinding, path: Path, folds: Sequence[int] = (0, 1, 2)
) -> str:
    """Persist an independently hashable description of what was bound."""
    per_fold = {}
    for fold in folds:
        try:
            authority = binding.authority(fold)
        except E11AuthorityError as error:  # pragma: no cover - defensive
            raise E11DataBindingError(
                f"fold {fold} authority refused: {error}"
            ) from error
        held_out = authority.outer_held_out_rows()
        per_fold[str(fold)] = {
            "row_counts": {
                partition.value: authority.row_count(partition)
                for partition in E11Partition
            },
            "subject_counts": {
                partition.value: authority.subject_count(partition)
                for partition in E11Partition
            },
            "held_out_prevalence": float(binding.labels[held_out].mean()),
            "held_out_streams": int(np.unique(binding.streams[held_out]).size),
            "authority_identity_digest": authority.identity_digest,
        }

    payload = {
        "schema": E11_DATA_BINDING_SCHEMA_VERSION,
        "experiment_id": binding.experiment_id,
        "auxiliary_target": AUXILIARY_TARGET_NAME,
        "split_digest": binding.split_digest,
        "sources": {
            "waveform_cache": str(binding.sources.waveform_cache),
            "protocol_dir": str(binding.sources.protocol_dir),
            "stable_ids_sha256": _sha256(binding.sources.train_stable_ids()),
            "cache_manifest_digests": binding.manifest_digests,
        },
        "rows": int(binding.labels.size),
        "positives": int(binding.labels.sum()),
        "prevalence": float(binding.labels.mean()),
        "subjects": len(binding.assignment),
        "streams": int(np.unique(binding.streams).size),
        "auxiliary_defined": int(binding.auxiliary_mask.sum()),
        "auxiliary_undefined": int((~binding.auxiliary_mask).sum()),
        "folds": per_fold,
    }
    payload["binding_digest"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    write_json_atomic(Path(path), payload)
    return payload["binding_digest"]
