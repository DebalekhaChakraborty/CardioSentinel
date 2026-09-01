"""The frozen deterministic fold allocator, protocol section 5.1.

Two independent implementers reading the protocol must produce byte-identical
assignments. That is the whole requirement, so nothing here is left to a
library's ordering or to dictionary insertion order.

Balancing uses reference-episode burden only. No model score, no J1 result and
no performance quantity participates.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

FOLD_SEED = "2026"


class FoldAllocationError(RuntimeError):
    """A pool that cannot be allocated under the frozen constraints."""


@dataclass(frozen=True)
class SubjectBurden:
    """The only per-subject inputs the allocator may see."""

    subject_id: str
    reference_episode_count: int

    @property
    def reference_positive(self) -> bool:
        return self.reference_episode_count > 0

    @property
    def identity_hash(self) -> str:
        return hashlib.sha256(
            f"{FOLD_SEED}:{self.subject_id}".encode()
        ).hexdigest()


def allocate_folds(
    subjects: list[SubjectBurden], *, folds: int
) -> tuple[tuple[str, ...], ...]:
    """Assign subjects to `folds` equal-capacity folds, deterministically."""
    total = len(subjects)
    if folds < 1:
        raise FoldAllocationError("fold count must be at least 1.")
    if total % folds:
        raise FoldAllocationError(
            f"{total} subjects do not divide into {folds} equal folds; the "
            "frozen geometry requires exact capacity."
        )
    capacity = total // folds
    if len({s.subject_id for s in subjects}) != total:
        raise FoldAllocationError("duplicate subject identity in the pool.")

    assigned: list[list[str]] = [[] for _ in range(folds)]
    positive_count = [0] * folds
    episode_burden = [0] * folds
    zero_reference_count = [0] * folds

    positives = sorted(
        (s for s in subjects if s.reference_positive),
        key=lambda s: (-s.reference_episode_count, s.identity_hash, s.subject_id),
    )
    for subject in positives:
        eligible = [i for i in range(folds) if len(assigned[i]) < capacity]
        chosen = min(
            eligible,
            key=lambda i: (
                positive_count[i],
                episode_burden[i],
                len(assigned[i]),
                i,
            ),
        )
        assigned[chosen].append(subject.subject_id)
        positive_count[chosen] += 1
        episode_burden[chosen] += subject.reference_episode_count

    zeros = sorted(
        (s for s in subjects if not s.reference_positive),
        key=lambda s: (s.identity_hash, s.subject_id),
    )
    for subject in zeros:
        eligible = [i for i in range(folds) if len(assigned[i]) < capacity]
        chosen = min(
            eligible,
            key=lambda i: (zero_reference_count[i], len(assigned[i]), i),
        )
        assigned[chosen].append(subject.subject_id)
        zero_reference_count[chosen] += 1

    for index, fold in enumerate(assigned):
        if len(fold) != capacity:
            raise FoldAllocationError(
                f"fold {index} holds {len(fold)} subjects, expected {capacity}."
            )
    return tuple(tuple(fold) for fold in assigned)
