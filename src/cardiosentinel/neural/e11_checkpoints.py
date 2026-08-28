"""Identity-bound, fail-closed phase-1 checkpoint persistence for E11-class runs.

E12a could not answer whether the morphology auxiliary objective was mature at
checkpoint selection, because the phase-1 models were discarded by construction
and nothing about them survived. This module makes them survive.

**The size audit decided the policy.** A B4-B checkpoint is **1.20 MB** of model
state. Retaining *every* phase-1 epoch for a whole E11-class run costs **108 MB**
worst case (15 epochs x 3 folds x 2 arms) and **41 MB** at E11 ATTEMPT 2's
observed epoch counts -- against 1.07 GB of artifacts that run already produced.
At that price there is no reason to discard the trajectory, so the registered
retention policy is **every phase-1 epoch, model state only**.

**Model state only, and that is a deliberate boundary.** Optimizer state would
roughly triple the cost (325 MB) and buys exactly one thing: deterministic
*continuation*. Continuation is restart, restart is an authorization question,
and this module has no authority to answer it. An audit checkpoint and an
execution-recovery checkpoint are different artifacts with different contents,
and only the first is written here.

**Persisting a checkpoint does not enable restart.** There is no function here
that rebuilds an optimizer, resumes an epoch counter, or continues training.
`load_checkpoint_for_audit` returns weights for read-only inspection and says so
in its name.

**Fail closed.** The bytes are written to a same-directory temporary file,
hashed *before* the rename, and only then published. A checkpoint that exists at
its final path has been hashed; a torn write cannot occupy that path. The digest
is what the epoch record references, so an epoch is complete only if its
checkpoint is complete.
"""

from __future__ import annotations

import hashlib
import io
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final, Mapping

import torch

__all__ = [
    "E11_CHECKPOINT_SCHEMA_VERSION",
    "E11CheckpointError",
    "CheckpointIdentity",
    "CheckpointRecord",
    "RETENTION_ALL_EPOCHS_MODEL_ONLY",
    "checkpoint_filename",
    "write_checkpoint",
    "load_checkpoint_for_audit",
    "verify_checkpoint",
]

E11_CHECKPOINT_SCHEMA_VERSION: Final[str] = "e11-checkpoint-v1"

#: The audited retention policy. Named so a receipt can record which one ran.
RETENTION_ALL_EPOCHS_MODEL_ONLY: Final[str] = "all_phase1_epochs_model_state_only"


class E11CheckpointError(RuntimeError):
    """Checkpoint contract violated."""


@dataclass(frozen=True, slots=True)
class CheckpointIdentity:
    """What a checkpoint is, bound at write time and re-checked at read time.

    A bare `state_dict` on disk is anonymous: nothing in it says which fold,
    arm or epoch produced it, or which code and split it belongs to. Every one
    of those is a way to silently analyse the wrong model, so all of them are
    carried with the weights and verified on load.
    """

    fold: int
    arm: str
    epoch: int
    git_commit: str
    split_digest: str
    schema: str = E11_CHECKPOINT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.fold not in (0, 1, 2):
            raise E11CheckpointError(f"unknown outer fold: {self.fold!r}")
        if self.arm not in ("B0", "B1"):
            raise E11CheckpointError(f"unknown arm: {self.arm!r}")
        if self.epoch < 1:
            raise E11CheckpointError(f"epoch must be >= 1, got {self.epoch}")
        if not self.split_digest:
            raise E11CheckpointError("split_digest is required")

    def matches(self, other: Mapping[str, Any]) -> bool:
        return all(getattr(self, key) == other.get(key) for key in asdict(self))


@dataclass(frozen=True, slots=True)
class CheckpointRecord:
    """The immutable reference an epoch record points at."""

    path: str
    sha256: str
    size_bytes: int
    identity: CheckpointIdentity
    contents: str = "model_state_only"
    retention_policy: str = RETENTION_ALL_EPOCHS_MODEL_ONLY


def checkpoint_filename(fold: int, arm: str, epoch: int) -> str:
    return f"phase1_fold{fold}_{arm}_ep{epoch:02d}.pt"


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_checkpoint(
    model: torch.nn.Module, directory: Path, identity: CheckpointIdentity
) -> CheckpointRecord:
    """Serialize model state atomically and return its immutable reference.

    Serialization is performed into memory first, so the digest is computed over
    exactly the bytes that will occupy the final path. Nothing here consumes
    global RNG: `state_dict()` reads tensors and `torch.save` writes them.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    final = directory / checkpoint_filename(identity.fold, identity.arm, identity.epoch)

    payload = {
        "schema": E11_CHECKPOINT_SCHEMA_VERSION,
        "identity": asdict(identity),
        "contents": "model_state_only",
        # Detached CPU copies: a checkpoint must not alias live training tensors.
        "model_state": {
            key: value.detach().cpu().clone()
            for key, value in model.state_dict().items()
        },
    }
    buffer = io.BytesIO()
    torch.save(payload, buffer)
    raw = buffer.getvalue()
    digest = _sha256_bytes(raw)

    temporary = final.with_name(f".{final.name}.tmp")
    temporary.write_bytes(raw)
    if _sha256_bytes(temporary.read_bytes()) != digest:
        temporary.unlink(missing_ok=True)
        raise E11CheckpointError(
            f"checkpoint failed its post-write digest check: {final.name}"
        )
    os.replace(temporary, final)          # atomic publish, same directory
    return CheckpointRecord(
        path=str(final),
        sha256=digest,
        size_bytes=len(raw),
        identity=identity,
    )


def verify_checkpoint(path: Path, expected_sha256: str) -> None:
    """Refuse a checkpoint whose bytes do not match the recorded digest."""
    path = Path(path)
    if not path.exists():
        raise E11CheckpointError(f"checkpoint is missing: {path}")
    actual = _sha256_bytes(path.read_bytes())
    if actual != expected_sha256:
        raise E11CheckpointError(
            f"checkpoint digest mismatch for {path.name}: "
            f"expected {expected_sha256}, found {actual}"
        )


def load_checkpoint_for_audit(
    path: Path,
    expected_sha256: str,
    expected_identity: CheckpointIdentity | None = None,
) -> dict[str, torch.Tensor]:
    """Load model weights for **read-only inspection**. Not a restart facility.

    Returns the model state only. There is no optimizer state to return, no
    epoch counter to resume and no function here that continues training --
    persisting a checkpoint deliberately does not enable restart, which remains
    a separate authorization question.
    """
    path = Path(path)
    verify_checkpoint(path, expected_sha256)
    payload = torch.load(path, map_location="cpu", weights_only=True)
    if payload.get("schema") != E11_CHECKPOINT_SCHEMA_VERSION:
        raise E11CheckpointError(
            f"unknown checkpoint schema: {payload.get('schema')!r}"
        )
    if payload.get("contents") != "model_state_only":
        raise E11CheckpointError(
            f"unexpected checkpoint contents: {payload.get('contents')!r}"
        )
    if expected_identity is not None and not expected_identity.matches(
        payload.get("identity", {})
    ):
        raise E11CheckpointError(
            "checkpoint identity mismatch: refusing to analyse a model from a "
            f"different fold/arm/epoch/commit/split ({payload.get('identity')!r})"
        )
    return payload["model_state"]
