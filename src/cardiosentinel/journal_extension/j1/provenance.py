"""The attempt-claim contract and the provenance artifact schema.

The run directory *is* the claim. Claiming is atomic and refuses reuse, so an
attempt cannot be silently consumed twice.

The real sink is not chosen here: its value must come from the future
authorization. This module defines the interface and the artifact identities the
canonical attempt root must carry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

#: Identities/digests a canonical J1 attempt root must carry.
REQUIRED_ATTEMPT_ARTIFACTS: tuple[str, ...] = (
    "authorization",
    "protocol",
    "pre_registration",
    "freeze_receipt",
    "execution_git_sha",
    "environment",
    "split_manifest",
    "attempt_claim",
    "negative_capability_proof",
    "capability_proof",
    "stage_receipts",
    "fold_manifest",
    "calibrators",
    "candidate_registries",
    "candidate_selections",
    "numeric_thresholds",
    "outer_oof_evidence",
    "per_subject_metrics",
    "bootstrap",
    "gate_a_decision",
    "failure_or_result_receipt",
)


class ProvenanceSinkError(RuntimeError):
    """No sink, an unusable sink, or an attempt root that already exists."""


class ProvenanceSink(Protocol):
    """Append-only promotion. A sink that can overwrite is not a sink."""

    def open_attempt(self, attempt_id: str) -> str:
        """Atomically claim `attempt_id`. Must refuse an existing claim."""
        ...

    def promote(self, attempt_id: str, artifact: str, digest: str) -> None:
        """Record an artifact identity. Must refuse to replace one."""
        ...


@dataclass(frozen=True)
class AttemptClaim:
    """Proof that an attempt was claimed before any scientific access."""

    attempt_id: str
    root: str

    def as_attestation(self) -> dict[str, str]:
        return {"attempt_id": self.attempt_id, "attempt_root": self.root}


def require_sink(sink: object | None) -> ProvenanceSink:
    """Refuse a missing or incomplete sink before anything is claimed."""
    if sink is None:
        raise ProvenanceSinkError(
            "no provenance sink. The sink is named by the authorization; there "
            "is no default, and no run may proceed without one."
        )
    for method in ("open_attempt", "promote"):
        if not callable(getattr(sink, method, None)):
            raise ProvenanceSinkError(
                f"provenance sink does not implement {method!r}."
            )
    return sink  # type: ignore[return-value]
