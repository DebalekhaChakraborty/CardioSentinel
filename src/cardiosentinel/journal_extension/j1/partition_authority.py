"""TRAIN-only data authority, with VALIDATION and TEST structurally absent.

The frozen protocol permits exactly one physiological population: the 56 V1
TRAIN subjects. V1 VALIDATION is historical-only and V1 TEST was consumed on
2026-08-25.

Prose cannot enforce that, and neither can an enum. A `Partition` enum with
three members, or an API taking `partition: str`, both leave VALIDATION one
token away from any caller. This module has no such type. The only authority
object it can construct represents `V1_TRAIN_ONLY`, and there is no constructor,
factory, classmethod or module function anywhere in the J1 package that returns
an authority over any other partition. Reaching VALIDATION is not forbidden
here; it is unrepresentable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

#: The single permitted physiological partition. Not one member of an enum --
#: there is no enum, because an enum is a menu.
V1_TRAIN_ONLY: Final = "V1_TRAIN_ONLY"

#: The frozen split this authority must eventually bind to. Recorded, not opened.
FROZEN_SPLIT_SHA256: Final = (
    "66e25d77b6aaa25502974b4b60667b4c4b24d649bf9493666827c747a385ced7"
)
FROZEN_SPLIT_PATH: Final = "protocols/splits/ltstdb_v1.json"
EXPECTED_TRAIN_SUBJECT_COUNT: Final = 56


class PartitionAuthorityError(RuntimeError):
    """A subject or partition outside the single permitted authority."""


@dataclass(frozen=True)
class TrainOnlyDataAuthority:
    """Authority over the V1 TRAIN partition, and nothing else.

    Construct only through `train_only_authority`. The instance carries no
    partition selector, so there is no field an attacker or a careless caller
    could set to `"validation"`.
    """

    split_sha256: str
    authorized_subjects: frozenset[str]

    @property
    def partition(self) -> str:
        """Always `V1_TRAIN_ONLY`. There is no other value this can return."""
        return V1_TRAIN_ONLY

    def require_subject(self, subject_id: str) -> str:
        """Refuse any subject not named by the authorized TRAIN manifest."""
        if subject_id not in self.authorized_subjects:
            raise PartitionAuthorityError(
                f"{subject_id!r} is not in the authorized V1 TRAIN manifest. "
                "J1 has no authority over any other subject, and none can be "
                "granted by changing an argument."
            )
        return subject_id

    def as_attestation(self) -> dict[str, object]:
        return {
            "data_authority": V1_TRAIN_ONLY,
            "split_sha256": self.split_sha256,
            "authorized_subject_count": len(self.authorized_subjects),
        }


def train_only_authority(
    *, split_sha256: str, authorized_subjects: frozenset[str]
) -> TrainOnlyDataAuthority:
    """The only authority constructor in J1.

    The split digest must match the frozen split. The subject set is supplied by
    a verified authorization, never discovered by this module: reading the split
    file here would be physiological-adjacent access before the attempt claim.
    """
    if split_sha256 != FROZEN_SPLIT_SHA256:
        raise PartitionAuthorityError(
            "split identity mismatch: J1's TRAIN authority is bound to "
            f"{FROZEN_SPLIT_SHA256}, received {split_sha256}."
        )
    if not authorized_subjects:
        raise PartitionAuthorityError(
            "an empty TRAIN manifest is a refusal, not an authority over nothing."
        )
    return TrainOnlyDataAuthority(
        split_sha256=split_sha256, authorized_subjects=authorized_subjects
    )
