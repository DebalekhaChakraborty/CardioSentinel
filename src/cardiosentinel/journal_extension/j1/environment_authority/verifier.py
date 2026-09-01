"""Verify an authority record, and verify the runtime against it.

Two separate questions, deliberately separate functions:

1. **Is this record admissible as authority?** Schema, digest integrity, no
   mutable local state, an immutable artifact reference that exists.
2. **Is the runtime executing right now the one the record describes?**

Both refuse hard. Neither has a bypass, and there is no `DEV_MODE`,
`FORCE_ENVIRONMENT` or `SKIP_ENV_CHECK` parameter anywhere in this package.
"""

from __future__ import annotations

import platform
from dataclasses import dataclass
from typing import Any, Callable

from .record import (
    ENVIRONMENT_RECORD_FIELDS,
    EXCLUDED_FROM_DIGEST,
    EnvironmentAuthorityError,
    EnvironmentAuthorityRecord,
    environment_sha256,
    reject_mutable_local_state,
)
from .states import EnvironmentAuthorityState


class RuntimeMismatch(EnvironmentAuthorityError):
    """The running interpreter is not the environment that was approved."""


@dataclass(frozen=True)
class VerifiedEnvironmentAuthority:
    """A record that passed verification. Qualified, never authorized."""

    record: EnvironmentAuthorityRecord
    environment_sha256: str
    state: EnvironmentAuthorityState

    def as_attestation(self) -> dict[str, str]:
        return {
            "environment_id": self.record.environment_id,
            "environment_sha256": self.environment_sha256,
            "state": self.state.value,
        }


def verify_authority_record(
    record: EnvironmentAuthorityRecord,
    *,
    declared_sha256: str,
    artifact_exists: Callable[[str], bool],
) -> VerifiedEnvironmentAuthority:
    """Refuse unless the record is complete, honest and immutably located."""
    missing = [
        name
        for name in (*ENVIRONMENT_RECORD_FIELDS, *EXCLUDED_FROM_DIGEST)
        if not str(getattr(record, name, "") or "").strip()
    ]
    if missing:
        raise EnvironmentAuthorityError(
            "environment authority record is incomplete; no field defaults. "
            "Missing: " + ", ".join(sorted(missing))
        )
    if not record.runtime_dependencies:
        raise EnvironmentAuthorityError(
            "an empty dependency set is not a described environment."
        )

    reject_mutable_local_state(record)

    computed = environment_sha256(record)
    if computed != declared_sha256:
        raise EnvironmentAuthorityError(
            "environment digest mismatch: the record does not hash to the "
            f"digest it declares.\n  declared: {declared_sha256}\n"
            f"  computed: {computed}"
        )
    if not artifact_exists(record.immutable_artifact_location):
        raise EnvironmentAuthorityError(
            "the immutable artifact this record references does not exist at "
            f"{record.immutable_artifact_location!r}. An authority that points "
            "at nothing cannot be reproduced."
        )
    return VerifiedEnvironmentAuthority(
        record=record,
        environment_sha256=computed,
        state=EnvironmentAuthorityState.QUALIFIED,
    )


def observe_runtime() -> dict[str, str]:
    """What the interpreter reports about itself.

    This is an *observation used for comparison*, never a source of authority:
    nothing here is hashed, and no value from it can become an
    `environment_sha256`.
    """
    return {
        "python_runtime_identity": (
            f"{platform.python_implementation()}-{platform.python_version()}"
        ),
        "operating_system_identity": f"{platform.system()}-{platform.machine()}",
    }


def verify_runtime_matches(
    authority: VerifiedEnvironmentAuthority,
    *,
    dependency_digest: str,
    observed: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Refuse unless the running runtime is the approved one."""
    seen = observed if observed is not None else observe_runtime()
    record = authority.record
    for field_name, expected in (
        ("python_runtime_identity", record.python_runtime_identity),
        ("operating_system_identity", record.operating_system_identity),
    ):
        actual = seen.get(field_name)
        if actual != expected:
            raise RuntimeMismatch(
                f"{field_name} mismatch: the authority approves {expected!r}, "
                f"this runtime is {actual!r}."
            )
    if dependency_digest != record.dependency_digest:
        raise RuntimeMismatch(
            "dependency digest mismatch: the authority approves "
            f"{record.dependency_digest}, this runtime reports "
            f"{dependency_digest}."
        )
    return {
        "environment_authority_verified": True,
        "environment_sha256": authority.environment_sha256,
        "state": authority.state.value,
    }
