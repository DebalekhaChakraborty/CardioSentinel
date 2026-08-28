"""The partition authority for a future E11-class run: the only door to rows.

Every earlier stage of this programme learned the same lesson a different way:
a partition that can be *named* is a partition that can be *reached*. T1 solved
it by hard-coding the partition instead of passing it, and recorded the reason
in `t1_fold_authority`: "TEST cannot be requested because there is no parameter
that could carry it."

This module applies that to E11's nested design. The authority exposes exactly
four accessors -- `inner_train_rows`, `inner_validation_rows`,
`outer_train_rows`, `outer_held_out_rows` -- and **none of them takes an
argument**. There is no `partition=`, no `split_name=`, no `dataset_name=`, and
no way to hand in arbitrary indices. TEST and the historical 12-subject
VALIDATION partition are unreachable not because the code refuses them but
because nothing can express them.

**The authorized population is a whitelist, not a blacklist.** Construction
fails unless every subject is inside the population the authority was built for
-- the original 56 TRAIN subjects. A historical VALIDATION subject is therefore
excluded by *not being on the list*, which needs no reference to that partition
and cannot be defeated by inventing a new name for it.

**Structure is checked, not assumed.** Construction asserts that inner-train and
inner-validation are disjoint and together exactly reconstitute outer-train, and
that outer-train and outer-held-out are disjoint in both rows and subjects.
An authority that cannot satisfy those does not exist.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Final, Mapping, Sequence

import numpy as np

__all__ = [
    "E11_AUTHORITY_SCHEMA_VERSION",
    "E11AuthorityError",
    "E11Partition",
    "E11FoldAuthority",
]

E11_AUTHORITY_SCHEMA_VERSION: Final[str] = "e11-authority-v1"

#: Tokens that must never appear as a subject id or an experiment identity.
_SEALED_TOKENS: Final[frozenset[str]] = frozenset(
    {"test", "sealed", "sealed_test", "holdout_test"}
)


class E11AuthorityError(RuntimeError):
    """The partition boundary was violated."""


class E11Partition(Enum):
    """The four partitions the registered nested protocol defines.

    A label for receipts, never a selector: no accessor takes one of these as
    an argument. There is deliberately no member for TEST or for the historical
    12-subject VALIDATION partition, so neither can be named in a receipt
    either. Not a `str` subclass -- a bare string must never satisfy it.
    """

    INNER_TRAIN = "inner_train"
    INNER_VALIDATION = "inner_validation"
    OUTER_TRAIN = "outer_train"
    OUTER_HELD_OUT = "outer_held_out"


def _digest(payload: object) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class E11FoldAuthority:
    """Binds one outer fold's row sets, its subjects, and the run's identity.

    Construction reads nothing from disk. It is a permission object over index
    arrays that a binding layer has already validated, not a loaded dataset.
    """

    fold: int
    split_digest: str
    experiment_id: str
    _authorized_population: frozenset[str]
    _subjects: Mapping[E11Partition, frozenset[str]]
    _rows: Mapping[E11Partition, np.ndarray]

    def __init__(
        self,
        *,
        fold: int,
        split_digest: str,
        experiment_id: str,
        authorized_population: Sequence[str],
        subjects: np.ndarray,
        inner_train_rows: np.ndarray,
        inner_validation_rows: np.ndarray,
        outer_held_out_rows: np.ndarray,
    ) -> None:
        if fold not in (0, 1, 2):
            raise E11AuthorityError(f"unknown outer fold: {fold!r}")
        if not split_digest:
            raise E11AuthorityError("split_digest is required")
        if experiment_id.strip().lower() in _SEALED_TOKENS:
            raise E11AuthorityError("experiment identity may not name a sealed run")

        population = frozenset(str(s) for s in authorized_population)
        if not population:
            raise E11AuthorityError("an authorized development population is required")
        for subject in population:
            if subject.strip().lower() in _SEALED_TOKENS:
                raise E11AuthorityError(
                    "the authorized population may not name a sealed partition"
                )

        subjects = np.asarray(subjects).astype(str)
        inner_train = np.unique(np.asarray(inner_train_rows).ravel())
        inner_validation = np.unique(np.asarray(inner_validation_rows).ravel())
        held_out = np.unique(np.asarray(outer_held_out_rows).ravel())
        outer_train = np.union1d(inner_train, inner_validation)

        for name, rows in (
            ("inner_train", inner_train),
            ("inner_validation", inner_validation),
            ("outer_held_out", held_out),
        ):
            if rows.size == 0:
                raise E11AuthorityError(f"{name} is empty")

        if np.intersect1d(inner_train, inner_validation).size:
            raise E11AuthorityError(
                "inner-train and inner-validation overlap: selection would be "
                "scored against rows it was fitted on"
            )
        if np.intersect1d(outer_train, held_out).size:
            raise E11AuthorityError(
                "outer-train and outer-held-out overlap: the held-out fold would "
                "influence gradients"
            )

        by_partition = {
            E11Partition.INNER_TRAIN: inner_train,
            E11Partition.INNER_VALIDATION: inner_validation,
            E11Partition.OUTER_TRAIN: outer_train,
            E11Partition.OUTER_HELD_OUT: held_out,
        }
        subject_sets = {
            partition: frozenset(subjects[rows].tolist())
            for partition, rows in by_partition.items()
        }

        outside = set().union(*subject_sets.values()) - population
        if outside:
            raise E11AuthorityError(
                "subjects outside the authorized development population were "
                f"supplied and are refused: {sorted(outside)[:5]}"
            )
        if subject_sets[E11Partition.INNER_TRAIN] & subject_sets[
            E11Partition.INNER_VALIDATION
        ]:
            raise E11AuthorityError("inner split is not subject-disjoint")
        if subject_sets[E11Partition.OUTER_TRAIN] & subject_sets[
            E11Partition.OUTER_HELD_OUT
        ]:
            raise E11AuthorityError("outer split is not subject-disjoint")

        object.__setattr__(self, "fold", fold)
        object.__setattr__(self, "split_digest", split_digest)
        object.__setattr__(self, "experiment_id", experiment_id)
        object.__setattr__(self, "_authorized_population", population)
        object.__setattr__(self, "_subjects", subject_sets)
        object.__setattr__(self, "_rows", by_partition)

    # -- the only four data accessors, none of which takes an argument -------

    def inner_train_rows(self) -> np.ndarray:
        return self._rows[E11Partition.INNER_TRAIN].copy()

    def inner_validation_rows(self) -> np.ndarray:
        return self._rows[E11Partition.INNER_VALIDATION].copy()

    def outer_train_rows(self) -> np.ndarray:
        return self._rows[E11Partition.OUTER_TRAIN].copy()

    def outer_held_out_rows(self) -> np.ndarray:
        return self._rows[E11Partition.OUTER_HELD_OUT].copy()

    # -- counts and identity, for receipts ----------------------------------

    def subject_count(self, partition: E11Partition) -> int:
        if not isinstance(partition, E11Partition):
            raise E11AuthorityError(
                "partition must be an E11Partition member; a bare string is "
                "refused so that no unlisted partition can be named"
            )
        return len(self._subjects[partition])

    def row_count(self, partition: E11Partition) -> int:
        if not isinstance(partition, E11Partition):
            raise E11AuthorityError("partition must be an E11Partition member")
        return int(self._rows[partition].size)

    def permits(self, subject_id: str) -> bool:
        """One subject at a time, and only inside the authorized population."""
        return str(subject_id) in self._authorized_population

    @property
    def identity(self) -> dict[str, object]:
        return {
            "schema": E11_AUTHORITY_SCHEMA_VERSION,
            "fold": self.fold,
            "split_digest": self.split_digest,
            "experiment_id": self.experiment_id,
            "population_size": len(self._authorized_population),
            "population_digest": _digest(sorted(self._authorized_population)),
            "subject_counts": {
                partition.value: len(members)
                for partition, members in self._subjects.items()
            },
            "row_counts": {
                partition.value: int(rows.size)
                for partition, rows in self._rows.items()
            },
        }

    @property
    def identity_digest(self) -> str:
        return _digest(self.identity)
