"""J1 environment authority. QUALIFICATION CANDIDATE -- NOT AUTHORIZED.

`environment_sha256` must answer *"what exact scientific runtime was approved?"*
-- not *"what happened to exist when someone ran a command."* A mutable
workstation snapshot is not an authority, and this package refuses to let one
become the answer.
"""

from .record import (
    ENVIRONMENT_RECORD_FIELDS,
    FORBIDDEN_IN_DEPENDENCY,
    FORBIDDEN_IN_FIELD_VALUE,
    EnvironmentAuthorityError,
    EnvironmentAuthorityRecord,
    canonical_serialization,
    environment_sha256,
    reject_mutable_local_state,
)
from .states import EnvironmentAuthorityState
from .verifier import (
    RuntimeMismatch,
    VerifiedEnvironmentAuthority,
    verify_authority_record,
    verify_runtime_matches,
)

__all__ = [
    "ENVIRONMENT_RECORD_FIELDS",
    "FORBIDDEN_IN_DEPENDENCY",
    "FORBIDDEN_IN_FIELD_VALUE",
    "EnvironmentAuthorityError",
    "EnvironmentAuthorityRecord",
    "EnvironmentAuthorityState",
    "RuntimeMismatch",
    "VerifiedEnvironmentAuthority",
    "canonical_serialization",
    "environment_sha256",
    "reject_mutable_local_state",
    "verify_authority_record",
    "verify_runtime_matches",
]
