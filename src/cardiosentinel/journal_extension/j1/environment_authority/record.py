"""The canonical Environment Authority Record and its digest.

`environment_sha256` is SHA-256 over the **canonical serialization of this
record**. It is deliberately *not* a hash of live machine state, of the current
`pip freeze`, of a home directory, of untracked files, or of environment
variables. Those describe what happened to exist; the record describes what was
approved.

Canonical serialization, frozen so two independent implementations agree:

- fields emitted in `ENVIRONMENT_RECORD_FIELDS` order, never dictionary order;
- one `field=value` line per field;
- UTF-8, no BOM;
- `\\n` line endings, exactly one terminating the file;
- no leading or trailing whitespace on any line;
- values serialized as-is for strings, `int` decimal, and `key=value` pairs
  joined by `,` in sorted key order for mappings;
- `EXCLUDED_FROM_DIGEST` fields are recorded in the document but never hashed.

The exclusions matter as much as the inclusions. A creation timestamp, a
hostname or an owner path would make the digest depend on where the record was
written rather than on what it describes, so two faithful rebuilds of the same
environment would disagree.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Final

#: Digest-bearing fields, in canonical order. Order is part of the contract.
ENVIRONMENT_RECORD_FIELDS: Final[tuple[str, ...]] = (
    "environment_id",
    "environment_version",
    "creation_method",
    "base_image_identity",
    "operating_system_identity",
    "python_runtime_identity",
    "dependency_lock_identity",
    "dependency_digest",
    "hardware_profile",
    "accelerator_identity",
    "container_image_digest",
    "immutable_artifact_location",
)

#: Recorded for provenance, deliberately outside the digest. Including any of
#: these would bind the digest to where the record was written.
EXCLUDED_FROM_DIGEST: Final[tuple[str, ...]] = (
    "creation_timestamp",
    "owner_provenance_identity",
)

#: Values that name a machine rather than an approved artifact.
_MUTABLE_LOCAL_MARKERS: Final[tuple[str, ...]] = (
    "localhost",
    "/home/",
    "/Users/",
    "~",
    "$HOME",
    "current-machine",
    "developer-laptop",
    "workstation",
    "unbound",
    "unknown",
)


class EnvironmentAuthorityError(RuntimeError):
    """A record that cannot serve as scientific authority."""


@dataclass(frozen=True)
class EnvironmentAuthorityRecord:
    """An immutable, reproducible description of an approved runtime."""

    environment_id: str
    environment_version: str
    creation_method: str
    base_image_identity: str
    operating_system_identity: str
    python_runtime_identity: str
    dependency_lock_identity: str
    dependency_digest: str
    hardware_profile: str
    accelerator_identity: str
    container_image_digest: str
    immutable_artifact_location: str
    creation_timestamp: str
    owner_provenance_identity: str
    runtime_dependencies: dict[str, str] = field(default_factory=dict)

    def as_document(self) -> dict[str, Any]:
        document = {name: getattr(self, name) for name in ENVIRONMENT_RECORD_FIELDS}
        document.update({name: getattr(self, name) for name in EXCLUDED_FROM_DIGEST})
        document["runtime_dependencies"] = dict(self.runtime_dependencies)
        return document


def _serialize_value(value: Any) -> str:
    if isinstance(value, dict):
        return ",".join(f"{k}={value[k]}" for k in sorted(value))
    if isinstance(value, bool):
        raise EnvironmentAuthorityError("a boolean is not an environment identity.")
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return value
    raise EnvironmentAuthorityError(
        f"unserializable environment field of type {type(value).__name__}."
    )


def canonical_serialization(record: EnvironmentAuthorityRecord) -> bytes:
    """The exact bytes hashed. Field order fixed, exclusions omitted."""
    lines = []
    for name in ENVIRONMENT_RECORD_FIELDS:
        value = _serialize_value(getattr(record, name))
        if value != value.strip():
            raise EnvironmentAuthorityError(
                f"{name!r} carries leading or trailing whitespace; the canonical "
                "form has none, so a padded value would change the digest."
            )
        lines.append(f"{name}={value}")
    dependencies = _serialize_value(record.runtime_dependencies)
    lines.append(f"runtime_dependencies={dependencies}")
    return ("\n".join(lines) + "\n").encode("utf-8")


def environment_sha256(record: EnvironmentAuthorityRecord) -> str:
    """SHA-256 over the canonical serialization. Never over machine state."""
    return hashlib.sha256(canonical_serialization(record)).hexdigest()


def reject_mutable_local_state(record: EnvironmentAuthorityRecord) -> None:
    """Refuse a record that names a machine instead of an approved artifact."""
    for name in ENVIRONMENT_RECORD_FIELDS:
        value = getattr(record, name)
        if not isinstance(value, str):
            continue
        lowered = value.lower()
        for marker in _MUTABLE_LOCAL_MARKERS:
            if marker.lower() in lowered:
                raise EnvironmentAuthorityError(
                    f"{name}={value!r} names mutable local state ({marker!r}). A "
                    "workstation snapshot is not a scientific authority: the "
                    "record must reference an immutable, reproducible artifact."
                )
