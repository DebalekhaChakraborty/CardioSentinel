"""What makes an environment artifact authoritative. It is not that it exists.

An image is not authority because Docker built it, because a developer produced
it, or because someone wrote its digest down. Authority is a **provenance
chain**:

    frozen runtime evidence -> build specification -> controlled build
    -> artifact digest -> environment authority record -> authorization

This module implements the middle of that chain and **nothing on either end**.
It builds no image, submits no digest, creates no environment authority and
populates no authorization field. Its `AUTHORIZED` builder state has no
transition function, for the same reason `environment_authority/states.py` and
`authorization_contract.py` have none.

**The builder is the part that is easy to get wrong.** A machine does not become
an authority by running the command. A local developer machine is a *candidate*
builder and can never be more than that from inside this package: promoting it
would mean the thing being vouched for is also the voucher.

**One canonical-form rule, two record types.** `manifest_sha256` uses the same
line form, and the same refusal of structural characters, that
`environment_authority.record` froze -- imported, not restated. A second
canonical serialization would be a second authority, and the two would
eventually disagree on some value neither author thought about.

**Why `creation_timestamp` is excluded from the digest.** The reproducibility
contract asks whether two builds from identical inputs produce identical
artifacts. If the moment of writing were hashed, no two manifests could ever
agree, and the contract would be untestable by construction rather than merely
unproven.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, Mapping

from .approved_runtime import (
    APPROVED_DEPENDENCY_DIGEST,
    APPROVED_PYTHON_RUNTIME_IDENTITY,
)
from .environment_authority import (
    FORBIDDEN_IN_FIELD_VALUE,
    reject_uncanonical,
)

# ---------------------------------------------------------------------------
# Build authority identity -- specification section 4
# ---------------------------------------------------------------------------

#: Every field a build authority declaration must carry. None may default.
BUILD_AUTHORITY_FIELDS: Final[tuple[str, ...]] = (
    "build_authority_id",
    "builder_identity",
    "builder_version",
    "build_method",
    "build_timestamp",
    "source_repository_identity",
    "source_commit",
    "build_configuration_identity",
    "base_image_identity",
    "output_artifact_identity",
    "artifact_digest_method",
    "provenance_location",
)

# ---------------------------------------------------------------------------
# Build manifest -- specification section 9
# ---------------------------------------------------------------------------

#: Digest-bearing manifest fields, in canonical order. Order is the contract.
MANIFEST_DIGEST_FIELDS: Final[tuple[str, ...]] = (
    "build_id",
    "source_commit",
    "runtime_authority_id",
    "dependency_digest",
    "base_image_digest",
    "builder_identity",
    "build_configuration_digest",
    "output_artifact_digest",
    "provenance_reference",
)

#: Recorded, never hashed. See the module docstring.
MANIFEST_EXCLUDED_FROM_DIGEST: Final[tuple[str, ...]] = ("creation_timestamp",)

MANIFEST_FIELDS: Final[tuple[str, ...]] = (
    *MANIFEST_DIGEST_FIELDS,
    *MANIFEST_EXCLUDED_FROM_DIGEST,
)

#: The four inputs the reproducibility contract holds fixed.
REPRODUCIBILITY_INPUTS: Final[tuple[str, ...]] = (
    "source_commit",
    "base_image_digest",
    "dependency_digest",
    "build_configuration_digest",
)

BIT_REPRODUCIBLE: Final = "BIT_REPRODUCIBLE"
NOT_REPRODUCIBLE_DOCUMENTED: Final = "NOT_REPRODUCIBLE_DOCUMENTED"

_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_DIGEST_REF = re.compile(r"^sha256:[0-9a-f]{64}$")
_IMAGE_BY_DIGEST = re.compile(r"^[^\s@]+@sha256:[0-9a-f]{64}$")

#: Refs that name a moving target. A build from one of these is not repeatable.
FLOATING_REFS: Final[tuple[str, ...]] = (
    "latest",
    "main",
    "master",
    "head",
    "rolling",
    "stable",
    "edge",
    "nightly",
    "dev",
    "current",
)


class BuildAuthorityError(RuntimeError):
    """A build whose provenance cannot make an artifact authoritative."""


class BuilderState(str, Enum):
    """A builder's standing.

        CANDIDATE -> QUALIFIED -> AUTHORIZED

    A machine that ran the command is a `CANDIDATE`. `QUALIFIED` means its
    declaration passed verification. `AUTHORIZED` is a human act naming that
    builder, and there is no transition function to it in this package: the
    thing being vouched for cannot also be the voucher.
    """

    CANDIDATE = "CANDIDATE"
    QUALIFIED = "QUALIFIED"
    AUTHORIZED = "AUTHORIZED"

    @classmethod
    def reachable_without_human_authorization(cls) -> tuple[BuilderState, ...]:
        return (cls.CANDIDATE, cls.QUALIFIED)


# ---------------------------------------------------------------------------
# Builder authority -- specification section 6
# ---------------------------------------------------------------------------

BUILDER_FIELDS: Final[tuple[str, ...]] = (
    "builder_id",
    "builder_environment_identity",
    "build_tool_version",
    "container_runtime_version",
    "build_command_identity",
    "provenance_output",
)

#: Values that name a machine rather than an accountable build service.
_LOCAL_BUILDER_MARKERS: Final[tuple[str, ...]] = (
    "localhost",
    "/home/",
    "/users/",
    "$home",
    "current-machine",
    "developer-laptop",
    "workstation",
    "my-machine",
    "unknown",
    "tbd",
)


@dataclass(frozen=True)
class BuilderDeclaration:
    """What a builder must say about itself before anything it made counts."""

    builder_id: str
    builder_environment_identity: str
    build_tool_version: str
    container_runtime_version: str
    build_command_identity: str
    provenance_output: str
    state: BuilderState = BuilderState.CANDIDATE

    def __post_init__(self) -> None:
        if self.state is BuilderState.AUTHORIZED:
            raise BuildAuthorityError(
                "a builder declaration may not assert AUTHORIZED. That is a "
                "human act naming the builder, performed outside this package."
            )


def verify_builder(declaration: BuilderDeclaration) -> BuilderDeclaration:
    """Refuse a builder that is a machine rather than an accountable service."""
    for name in BUILDER_FIELDS:
        value = getattr(declaration, name)
        if not isinstance(value, str) or not value.strip():
            raise BuildAuthorityError(
                f"builder field {name!r} is blank; a builder that will not say "
                "what it is cannot make anything authoritative."
            )
        reject_uncanonical(f"builder {name!r}", value, FORBIDDEN_IN_FIELD_VALUE)
        lowered = value.lower()
        for marker in _LOCAL_BUILDER_MARKERS:
            if marker in lowered:
                raise BuildAuthorityError(
                    f"builder {name}={value!r} names mutable local state "
                    f"({marker!r}). Running the command is not authority: a "
                    "local machine is a candidate builder and cannot promote "
                    "itself."
                )
    return BuilderDeclaration(
        builder_id=declaration.builder_id,
        builder_environment_identity=declaration.builder_environment_identity,
        build_tool_version=declaration.build_tool_version,
        container_runtime_version=declaration.container_runtime_version,
        build_command_identity=declaration.build_command_identity,
        provenance_output=declaration.provenance_output,
        state=BuilderState.QUALIFIED,
    )


# ---------------------------------------------------------------------------
# Input admissibility -- specification sections 5 and 8
# ---------------------------------------------------------------------------


def require_immutable_source(
    *, source_commit: str, worktree_clean: bool, source_ref: str | None = None
) -> str:
    """A build's source must be one commit, and that commit must be complete."""
    if not _GIT_SHA.match(source_commit):
        raise BuildAuthorityError(
            f"source_commit={source_commit!r} is not a full 40-character "
            "commit SHA. An abbreviated commit names a set, not an object, and "
            "a tag without one names whatever it points at today."
        )
    if not worktree_clean:
        raise BuildAuthorityError(
            "the source worktree was dirty. What was built is then not what "
            "the commit describes, and no digest can recover the difference."
        )
    if source_ref is not None and source_ref.lower() in FLOATING_REFS:
        raise BuildAuthorityError(
            f"source_ref={source_ref!r} is a floating ref. It names a moving "
            "target, so the build is not repeatable from the record."
        )
    return source_commit


def require_immutable_base_image(reference: str) -> str:
    """`name@sha256:<64 hex>`. A tag is not authority."""
    if not _IMAGE_BY_DIGEST.match(reference):
        raise BuildAuthorityError(
            f"base_image_digest={reference!r} is not addressed by digest. A "
            "tag can be repointed at different bytes tomorrow, so it names an "
            "intention rather than an artifact; use name@sha256:<64 hex>."
        )
    return reference


def require_artifact_digest(reference: str) -> str:
    """`sha256:<64 hex>` over the final artifact bytes. Not a tag, not metadata."""
    if _IMAGE_BY_DIGEST.match(reference):
        raise BuildAuthorityError(
            f"output_artifact_digest={reference!r} carries a repository name. "
            "The digest identifies the artifact bytes; where a copy currently "
            "lives is provenance, not identity."
        )
    if not _DIGEST_REF.match(reference):
        raise BuildAuthorityError(
            f"output_artifact_digest={reference!r} is not sha256:<64 hex>. A "
            "tag such as 'cardiosentinel:j1-latest' is not authority: it is a "
            "mutable pointer, and the artifact it names can change under it."
        )
    return reference


def require_approved_runtime_inputs(
    *, runtime_authority_id: str, dependency_digest: str
) -> None:
    """The build may reference the qualified runtime. It may not redefine it."""
    if not runtime_authority_id.strip():
        raise BuildAuthorityError(
            "runtime_authority_id is blank; a build must name the runtime "
            "authority it consumes."
        )
    if dependency_digest != APPROVED_DEPENDENCY_DIGEST:
        raise BuildAuthorityError(
            "the build declares a dependency digest that is not the approved "
            "one.\n"
            f"  approved: {APPROVED_DEPENDENCY_DIGEST}\n"
            f"  declared: {dependency_digest}\n"
            "A build may consume the qualified runtime authority; it may not "
            "define a new one. The approved set is established by frozen V1 "
            f"evidence for {APPROVED_PYTHON_RUNTIME_IDENTITY}."
        )


# ---------------------------------------------------------------------------
# The manifest -- specification section 9
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class J1EnvironmentBuildManifest:
    """One build's complete provenance. Not an environment authority record."""

    build_id: str
    source_commit: str
    runtime_authority_id: str
    dependency_digest: str
    base_image_digest: str
    builder_identity: str
    build_configuration_digest: str
    output_artifact_digest: str
    provenance_reference: str
    creation_timestamp: str

    def as_document(self) -> dict[str, Any]:
        return {name: getattr(self, name) for name in MANIFEST_FIELDS}


def canonical_manifest_serialization(
    manifest: J1EnvironmentBuildManifest,
) -> bytes:
    """The exact bytes hashed, in the frozen environment-authority line form."""
    lines = []
    for name in MANIFEST_DIGEST_FIELDS:
        value = getattr(manifest, name)
        if not isinstance(value, str):
            raise BuildAuthorityError(
                f"manifest field {name!r} must be text, got "
                f"{type(value).__name__}."
            )
        reject_uncanonical(repr(name), value, FORBIDDEN_IN_FIELD_VALUE)
        lines.append(f"{name}={value}")
    return ("\n".join(lines) + "\n").encode("utf-8")


def manifest_sha256(manifest: J1EnvironmentBuildManifest) -> str:
    """SHA-256 over the canonical serialization. Never over the build host."""
    return hashlib.sha256(canonical_manifest_serialization(manifest)).hexdigest()


@dataclass(frozen=True)
class VerifiedBuildManifest:
    """A manifest that passed verification. Qualified, never authorized."""

    manifest: J1EnvironmentBuildManifest
    manifest_sha256: str
    builder: BuilderDeclaration

    def as_attestation(self) -> dict[str, str]:
        return {
            "build_id": self.manifest.build_id,
            "manifest_sha256": self.manifest_sha256,
            "output_artifact_digest": self.manifest.output_artifact_digest,
            "builder_state": self.builder.state.value,
            "environment_authority_submitted": "false",
        }


def verify_build_manifest(
    manifest: J1EnvironmentBuildManifest,
    *,
    builder: BuilderDeclaration,
    worktree_clean: bool,
    source_ref: str | None = None,
) -> VerifiedBuildManifest:
    """Refuse unless every provenance link in the chain is present and immutable.

    There is no `force`, `dev_mode` or `skip_provenance` parameter, and a test
    asserts their absence. An artifact with no manifest, a manifest with no
    builder identity, no source commit or no runtime identity is refused --
    those are the three ways provenance goes missing in practice.
    """
    missing = [
        name
        for name in MANIFEST_FIELDS
        if not str(getattr(manifest, name, "") or "").strip()
    ]
    if missing:
        raise BuildAuthorityError(
            "the build manifest is incomplete; no field defaults. Missing: "
            + ", ".join(sorted(missing))
        )
    verified_builder = verify_builder(builder)
    if manifest.builder_identity != verified_builder.builder_id:
        raise BuildAuthorityError(
            f"the manifest names builder {manifest.builder_identity!r} but the "
            f"declaration is from {verified_builder.builder_id!r}."
        )
    require_immutable_source(
        source_commit=manifest.source_commit,
        worktree_clean=worktree_clean,
        source_ref=source_ref,
    )
    require_immutable_base_image(manifest.base_image_digest)
    require_artifact_digest(manifest.output_artifact_digest)
    require_approved_runtime_inputs(
        runtime_authority_id=manifest.runtime_authority_id,
        dependency_digest=manifest.dependency_digest,
    )
    if not _SHA256_HEX.match(manifest.build_configuration_digest):
        raise BuildAuthorityError(
            "build_configuration_digest must be a full lowercase SHA-256; the "
            "configuration is an input the artifact depends on."
        )
    return VerifiedBuildManifest(
        manifest=manifest,
        manifest_sha256=manifest_sha256(manifest),
        builder=verified_builder,
    )


# ---------------------------------------------------------------------------
# The reproducibility contract -- specification section 7
# ---------------------------------------------------------------------------


def reproducibility_inputs(manifest: J1EnvironmentBuildManifest) -> dict[str, str]:
    """The four inputs the contract holds fixed."""
    return {name: getattr(manifest, name) for name in REPRODUCIBILITY_INPUTS}


def verify_reproducible_pair(
    first: J1EnvironmentBuildManifest,
    second: J1EnvironmentBuildManifest,
    *,
    reproducibility_class: str = BIT_REPRODUCIBLE,
    non_reproducibility_reason: str | None = None,
) -> dict[str, Any]:
    """Two builds from identical inputs must agree, or say why they do not.

    **Reproducibility is not assumed here and is not proven here.** Nothing in
    this repository has built the artifact twice. What this function does is
    make the claim *falsifiable*: when two builds exist, an unexplained
    divergence is a refusal rather than a discrepancy someone reconciles later.
    """
    if reproducibility_class not in (BIT_REPRODUCIBLE, NOT_REPRODUCIBLE_DOCUMENTED):
        raise BuildAuthorityError(
            f"unknown reproducibility class {reproducibility_class!r}."
        )
    shared = reproducibility_inputs(first)
    if shared != reproducibility_inputs(second):
        differing = sorted(
            name
            for name in REPRODUCIBILITY_INPUTS
            if getattr(first, name) != getattr(second, name)
        )
        raise BuildAuthorityError(
            "these builds do not share the contract's inputs, so they say "
            f"nothing about reproducibility. Differing: {differing}."
        )
    agree = first.output_artifact_digest == second.output_artifact_digest
    if agree:
        return {
            "reproducible": True,
            "reproducibility_class": BIT_REPRODUCIBLE,
            "output_artifact_digest": first.output_artifact_digest,
        }
    if reproducibility_class == BIT_REPRODUCIBLE:
        raise BuildAuthorityError(
            "identical inputs produced different artifacts, and the build "
            "claims to be bit-reproducible.\n"
            f"  first:  {first.output_artifact_digest}\n"
            f"  second: {second.output_artifact_digest}\n"
            "Either the inputs are not the whole input, or the build is not "
            "reproducible. Both are findings; neither is reconciled by "
            "choosing one digest."
        )
    if not (non_reproducibility_reason or "").strip():
        raise BuildAuthorityError(
            "a build declared NOT_REPRODUCIBLE_DOCUMENTED must document why. "
            "An undocumented divergence is an unexplained one."
        )
    return {
        "reproducible": False,
        "reproducibility_class": NOT_REPRODUCIBLE_DOCUMENTED,
        "non_reproducibility_reason": non_reproducibility_reason,
        "digests": [
            first.output_artifact_digest,
            second.output_artifact_digest,
        ],
    }


def build_authority_declaration_fields() -> tuple[str, ...]:
    """The §4 field set, so a caller cannot invent a shorter one."""
    return BUILD_AUTHORITY_FIELDS


def require_build_authority_declaration(document: Mapping[str, Any]) -> None:
    """Every §4 field present and non-blank. No field may silently default."""
    missing = [
        name
        for name in BUILD_AUTHORITY_FIELDS
        if not str(document.get(name, "") or "").strip()
    ]
    if missing:
        raise BuildAuthorityError(
            "the build authority declaration is incomplete; no field may "
            "silently default. Missing: " + ", ".join(sorted(missing))
        )
