"""J1 environment authority. QUALIFICATION CANDIDATE -- NOT AUTHORIZED.

`environment_sha256` must answer *"what exact scientific runtime was approved?"*
-- not *"what happened to exist when someone ran a command."* A mutable
workstation snapshot is not an authority, and this package refuses to let one
become the answer.
"""

from .record import (
    ENVIRONMENT_RECORD_FIELDS,
    EnvironmentAuthorityError,
    EnvironmentAuthorityRecord,
    canonical_serialization,
    environment_sha256,
)
from .states import EnvironmentAuthorityState
from .verifier import (
    RuntimeMismatch,
    verify_authority_record,
    verify_runtime_matches,
)

__all__ = [
    "ENVIRONMENT_RECORD_FIELDS",
    "EnvironmentAuthorityError",
    "EnvironmentAuthorityRecord",
    "EnvironmentAuthorityState",
    "RuntimeMismatch",
    "canonical_serialization",
    "environment_sha256",
    "verify_authority_record",
    "verify_runtime_matches",
]
