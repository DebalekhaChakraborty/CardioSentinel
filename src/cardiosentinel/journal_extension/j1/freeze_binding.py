"""The frozen scientific bytes, and the gate that proves they have not moved.

J1's protocol and pre-registration were frozen and digest-bound by
`docs/journal-extension/j1/J1_FREEZE_RECEIPT_V1.md`. Everything downstream --
authorization, the attempt claim, every scientific access -- is only meaningful
if those bytes are still the reviewed ones.

The digests are constants here rather than read from the receipt. Reading them
from a file the same change could edit would prove nothing: a drifted document
and a drifted receipt would agree with each other. `INVALID_EXECUTION` is
therefore decided against a value compiled into the instrument.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
J1_DOCUMENTS = REPOSITORY_ROOT / "docs" / "journal-extension" / "j1"

#: Frozen 2026-09-01. A mismatch is INVALID_EXECUTION, never a new baseline.
FROZEN_PROTOCOL_SHA256 = (
    "cedb152eef187fd573212daaad7492242d6963d9b9de897ed1312cde0a976cf0"
)
FROZEN_PRE_REGISTRATION_SHA256 = (
    "1b6eb6645bf2449e4b76fb40b5ee7e44250474bd08c4a1c42ba79c00dc45fcd1"
)

PROTOCOL_PATH = J1_DOCUMENTS / "J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1.md"
PRE_REGISTRATION_PATH = J1_DOCUMENTS / "J1_PRE_REGISTRATION_V1.md"


class FreezeBindingError(RuntimeError):
    """The frozen scientific bytes are not the bytes that were reviewed."""


@dataclass(frozen=True)
class FreezeBinding:
    """Proof that both bound documents still hash to their frozen values."""

    protocol_sha256: str
    pre_registration_sha256: str

    def as_attestation(self) -> dict[str, str]:
        return {
            "protocol_sha256": self.protocol_sha256,
            "pre_registration_sha256": self.pre_registration_sha256,
        }


def _digest(path: Path) -> str:
    """SHA-256 over raw bytes. No canonicalisation -- the receipt's own method."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_freeze_binding(
    *, repository_root: Path | None = None
) -> FreezeBinding:
    """Refuse unless both documents match their frozen digests exactly."""
    root = repository_root or REPOSITORY_ROOT
    documents = root / "docs" / "journal-extension" / "j1"
    checks = (
        ("protocol", documents / PROTOCOL_PATH.name, FROZEN_PROTOCOL_SHA256),
        (
            "pre-registration",
            documents / PRE_REGISTRATION_PATH.name,
            FROZEN_PRE_REGISTRATION_SHA256,
        ),
    )
    for label, path, expected in checks:
        if not path.is_file():
            raise FreezeBindingError(
                f"INVALID_EXECUTION: the frozen J1 {label} is missing at {path}."
            )
        actual = _digest(path)
        if actual != expected:
            raise FreezeBindingError(
                f"INVALID_EXECUTION: the frozen J1 {label} has drifted.\n"
                f"  frozen:   {expected}\n"
                f"  on disk:  {actual}\n"
                "A scientific amendment requires a new versioned protocol and "
                "pre-registration, new digests and a new human freeze review. "
                "This digest is never silently adopted."
            )
    return FreezeBinding(FROZEN_PROTOCOL_SHA256, FROZEN_PRE_REGISTRATION_SHA256)
