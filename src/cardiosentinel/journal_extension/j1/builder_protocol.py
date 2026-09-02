"""Which controlled builder is proposed, and exactly what it must produce.

`build_authority.py` said what a trustworthy build must *prove*. This says which
mechanism is proposed to perform it and what artifact object it must emit.

**Nothing here builds, pushes, or promotes anything.** No image, no artifact
digest, no environment record, no authorization. The builder reaches `CANDIDATE`
and, on passing verification, `QUALIFIED`. `AUTHORIZED` is a human act naming a
specific workflow at a specific commit, and this module has no path to it.

**"GitHub Actions" is not an identity.** A builder named that way would let any
future workflow in any repository inherit the authorization. The identity that
can eventually be authorized is a *workflow file at a commit*, on a named runner
class, and `require_specific_builder_identity` refuses the generic forms.

**The host is not the target.** The runner orchestrating the build may execute
Python 3.11 -- CI does today. That does not redefine the environment the
artifact must contain, which is the approved scientific runtime established from
frozen V1 evidence. A build that installs the host's interpreter or resolves its
own dependency versions has produced something else.

**The digest ambiguity is resolved prospectively, because it is real.** The tag
`python:3.12.6-slim-bookworm` resolves to an OCI *image index*, whose digest
differs from the linux/amd64 *image manifest* inside it. "Image SHA-256" names
neither unambiguously. J1 freezes the single-platform image manifest.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any, Final, Mapping, Sequence

from .approved_runtime import (
    APPROVED_DEPENDENCY_DIGEST,
    APPROVED_PACKAGE_COUNT,
    APPROVED_PYTHON_RUNTIME_IDENTITY,
)
from .build_authority import BuildAuthorityError, require_immutable_base_image

# ---------------------------------------------------------------------------
# Target platform -- read out of frozen V1 evidence, not chosen
# ---------------------------------------------------------------------------

#: All three V1 experiment locks record device=cpu, gpu_model=None,
#: cuda_version=None, amp_enabled=False, and torch 2.13.0+cpu -- a CPU-only
#: wheel that cannot use CUDA. Introducing an accelerator would require a
#: different torch build, which would change the approved dependency digest.
TARGET_OS: Final = "linux"
TARGET_ARCHITECTURE: Final = "amd64"
TARGET_VARIANT: Final = None
TARGET_ACCELERATOR: Final = "none"
TARGET_COMPUTE_DEVICE: Final = "cpu"
#: From `platform` in the locks: Linux-...-x86_64-with-glibc2.36.
TARGET_LIBC: Final = "glibc2.36"

TARGET_PLATFORM: Final = f"{TARGET_OS}/{TARGET_ARCHITECTURE}"

# ---------------------------------------------------------------------------
# Artifact type -- specification section 9
# ---------------------------------------------------------------------------

ARTIFACT_KIND: Final = "oci_single_platform_image_manifest"
ARTIFACT_MEDIA_TYPE: Final = "application/vnd.oci.image.manifest.v1+json"
ARTIFACT_DIGEST_ALGORITHM: Final = "sha256"

#: Refused as the artifact object. An index is a list of manifests; its digest
#: identifies the list, not the image J1 would execute.
INDEX_MEDIA_TYPES: Final[tuple[str, ...]] = (
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
)

#: Also refused: these name transfer or archive encodings, not the manifest.
NON_AUTHORITATIVE_DIGEST_SOURCES: Final[tuple[str, ...]] = (
    "docker_save_tar",
    "compressed_layer_bytes",
    "filesystem_directory_hash",
    "image_tag",
    "registry_url",
)

# ---------------------------------------------------------------------------
# Dependency sources -- specification sections 13 and 17
# ---------------------------------------------------------------------------

PYPI: Final = "PYPI"
PYTORCH_CPU_INDEX: Final = "PYTORCH_CPU_INDEX"
FIRST_PARTY_SOURCE: Final = "FIRST_PARTY_SOURCE"

#: Two packages in the approved set carry a `+cpu` local version. Those are not
#: PyPI releases and require the PyTorch CPU index, named explicitly.
LOCAL_VERSION_PACKAGES: Final[tuple[str, ...]] = ("torch", "torchvision")
#: The repository itself is in the approved set. No index resolves it: it is
#: installed from the source tree at `source_commit`, which is what pins it.
FIRST_PARTY_PACKAGES: Final[tuple[str, ...]] = ("cardiosentinel",)

PERMITTED_DEPENDENCY_SOURCES: Final[tuple[str, ...]] = (
    PYPI,
    PYTORCH_CPU_INDEX,
    FIRST_PARTY_SOURCE,
)

# ---------------------------------------------------------------------------
# Build configuration -- specification section 15
# ---------------------------------------------------------------------------

#: A member whose bytes are committed at the authorized source commit.
TRACKED_SOURCE: Final = "TRACKED_SOURCE"
#: A member generated at build time from an authority-bound input. Acceptable
#: only under the conditions `require_derived_input_properties` enumerates.
DERIVED_BUILD_INPUT: Final = "DERIVED_BUILD_INPUT"


@dataclass(frozen=True)
class BuildConfigurationMember:
    """One artifact-affecting build input, and why it is bound.

    The previous model was five fixed slots with a single `dependency_input`.
    That was not an abstraction, it was an undercount: the build materialises
    *two* requirements files and the Containerfile installs from both, so a
    change from `torch==2.13.0+cpu` to anything else left the configuration
    digest unmoved. Roles are enumerated here instead, one per file, so adding
    a build input is a visible change to this tuple rather than a silent gap.
    """

    role: str
    path: str
    status: str
    authority: str
    affects_artifact_bytes: bool


#: Every input capable of changing the produced artifact's bytes, plus the
#: validation script, which does not change the artifact but decides whether it
#: is accepted. Traced from the Containerfile and build script rather than
#: inherited: see `J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2.md` §3.
BUILD_CONFIGURATION_MEMBERS: Final[tuple[BuildConfigurationMember, ...]] = (
    BuildConfigurationMember(
        role="containerfile",
        path="containers/j1-environment/Containerfile",
        status=TRACKED_SOURCE,
        authority="authorized_source_commit",
        affects_artifact_bytes=True,
    ),
    BuildConfigurationMember(
        role="containerfile_dockerignore",
        path="containers/j1-environment/Containerfile.dockerignore",
        status=TRACKED_SOURCE,
        authority="authorized_source_commit",
        # `COPY . /opt/cardiosentinel/src-tree` puts the build context into a
        # layer. What the context excludes is therefore image content.
        affects_artifact_bytes=True,
    ),
    BuildConfigurationMember(
        role="dependency_input_pypi",
        path="containers/j1-environment/requirements.pypi.txt",
        status=DERIVED_BUILD_INPUT,
        authority="frozen V1 experiment lock, via the pinned generator",
        affects_artifact_bytes=True,
    ),
    BuildConfigurationMember(
        role="dependency_input_pytorch",
        path="containers/j1-environment/requirements.pytorch-cpu.txt",
        status=DERIVED_BUILD_INPUT,
        authority="frozen V1 experiment lock, via the pinned generator",
        affects_artifact_bytes=True,
    ),
    BuildConfigurationMember(
        role="build_script",
        path="containers/j1-environment/build.sh",
        status=TRACKED_SOURCE,
        authority="authorized_source_commit",
        affects_artifact_bytes=True,
    ),
    BuildConfigurationMember(
        role="workflow",
        path=".github/workflows/j1-environment-artifact-build.yml",
        status=TRACKED_SOURCE,
        authority="authorized_source_commit",
        # Carries the base image digest, the BuildKit image digest, the Buildx
        # version and the runner class -- four artifact-affecting values that
        # exist nowhere else.
        affects_artifact_bytes=True,
    ),
    BuildConfigurationMember(
        role="artifact_validation_script",
        path="containers/j1-environment/validate_artifact.sh",
        status=TRACKED_SOURCE,
        authority="authorized_source_commit",
        # Does not change the artifact; decides whether it is accepted.
        affects_artifact_bytes=False,
    ),
)

REQUIRED_BUILD_CONFIGURATION_INPUTS: Final[tuple[str, ...]] = tuple(
    member.role for member in BUILD_CONFIGURATION_MEMBERS
)

#: The members the build generates rather than reads from the source tree.
DERIVED_BUILD_INPUT_ROLES: Final[tuple[str, ...]] = tuple(
    member.role
    for member in BUILD_CONFIGURATION_MEMBERS
    if member.status == DERIVED_BUILD_INPUT
)


def build_configuration_member(role: str) -> BuildConfigurationMember:
    """The declared member for a role, or a refusal naming the known roles."""
    for member in BUILD_CONFIGURATION_MEMBERS:
        if member.role == role:
            return member
    raise BuilderProtocolError(
        f"{role!r} is not a declared build configuration member. Known roles: "
        + ", ".join(REQUIRED_BUILD_CONFIGURATION_INPUTS)
    )

_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")

#: Identities that would let any future workflow inherit an authorization.
GENERIC_BUILDER_IDENTITIES: Final[tuple[str, ...]] = (
    "github actions",
    "github",
    "actions",
    "ci",
    "the builder",
    "build server",
    "pipeline",
)


class BuilderProtocolError(RuntimeError):
    """A builder or build protocol that cannot produce an authoritative artifact."""


# ---------------------------------------------------------------------------
# Builder identity -- specification section 7
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ControlledBuilderIdentity:
    """A workflow at a commit, on a named runner class. Not a provider name."""

    provider: str
    workflow_repository: str
    workflow_path: str
    workflow_commit: str
    runner_class: str

    @property
    def builder_id(self) -> str:
        return (
            f"{self.provider}:{self.workflow_repository}"
            f"//{self.workflow_path}@{self.workflow_commit}"
            f"#{self.runner_class}"
        )


def require_specific_builder_identity(
    identity: ControlledBuilderIdentity,
) -> ControlledBuilderIdentity:
    """Refuse a builder identity that names a provider rather than a workflow."""
    for name in (
        "provider",
        "workflow_repository",
        "workflow_path",
        "workflow_commit",
        "runner_class",
    ):
        value = getattr(identity, name)
        if not isinstance(value, str) or not value.strip():
            raise BuilderProtocolError(
                f"builder identity field {name!r} is blank; an identity that "
                "does not say which workflow ran cannot be authorized."
            )
    if identity.workflow_repository.strip().lower() in GENERIC_BUILDER_IDENTITIES:
        raise BuilderProtocolError(
            f"{identity.workflow_repository!r} names a provider, not a builder. "
            "Authorizing it would authorize every future workflow in every "
            "repository it covers."
        )
    if not _GIT_SHA.match(identity.workflow_commit):
        raise BuilderProtocolError(
            f"workflow_commit={identity.workflow_commit!r} is not a full "
            "40-character commit SHA. A workflow referenced by branch or tag "
            "can be edited after authorization, so the thing authorized and "
            "the thing that runs would be different objects."
        )
    return identity


def require_pinned_action(uses: str) -> str:
    """`owner/repo@<40 hex>`. A floating tag can be repointed after review."""
    if "@" not in uses:
        raise BuilderProtocolError(
            f"action {uses!r} is unpinned; it must be referenced by commit SHA."
        )
    reference, _, ref = uses.rpartition("@")
    if not _GIT_SHA.match(ref):
        raise BuilderProtocolError(
            f"action {reference}@{ref} is pinned to a mutable ref. A tag such "
            "as 'v4' or a branch such as 'main' can be moved to different code "
            "after the build protocol is reviewed; pin the commit SHA and keep "
            "the version as a comment."
        )
    return uses


# ---------------------------------------------------------------------------
# Host versus target -- specification section 6
# ---------------------------------------------------------------------------


def require_host_does_not_redefine_target(
    *, host_python_identity: str, target_python_identity: str
) -> None:
    """The runner may orchestrate the build. It may not substitute itself."""
    if target_python_identity != APPROVED_PYTHON_RUNTIME_IDENTITY:
        raise BuilderProtocolError(
            "the build declares a target runtime that is not the approved "
            f"one.\n  approved: {APPROVED_PYTHON_RUNTIME_IDENTITY}\n"
            f"  declared: {target_python_identity}\n"
            "The builder host's own interpreter is irrelevant to this: what "
            "the artifact must contain is fixed by frozen V1 evidence."
        )
    if host_python_identity == target_python_identity:
        return
    # A differing host is expected and permitted; it is recorded, not refused.
    return


# ---------------------------------------------------------------------------
# Artifact type -- specification section 9
# ---------------------------------------------------------------------------


def require_single_platform_manifest(media_type: str) -> str:
    """The digest-bearing object is one image manifest, never an index."""
    if media_type in INDEX_MEDIA_TYPES:
        raise BuilderProtocolError(
            f"{media_type!r} is an image index. Its digest identifies a list "
            "of manifests, not the image J1 would execute; a tag commonly "
            "resolves to one, which is why 'image SHA-256' is ambiguous. "
            f"Freeze the single-platform manifest: {ARTIFACT_MEDIA_TYPE}."
        )
    if media_type != ARTIFACT_MEDIA_TYPE:
        raise BuilderProtocolError(
            f"{media_type!r} is not the frozen artifact media type "
            f"{ARTIFACT_MEDIA_TYPE}."
        )
    return media_type


def require_declared_platform(*, os_name: str, architecture: str) -> str:
    """The platform is explicit, and it is the one the frozen evidence names."""
    if not os_name.strip() or not architecture.strip():
        raise BuilderProtocolError(
            "the target platform must be explicit; a build that does not say "
            "what it targets can produce a different image on a different "
            "runner."
        )
    if (os_name, architecture) != (TARGET_OS, TARGET_ARCHITECTURE):
        raise BuilderProtocolError(
            f"target platform {os_name}/{architecture} is not the platform the "
            f"inherited scaffold was built on ({TARGET_PLATFORM})."
        )
    return f"{os_name}/{architecture}"


# ---------------------------------------------------------------------------
# Dependency reconstruction -- specification section 13
# ---------------------------------------------------------------------------


def classify_dependency_source(name: str, version: str) -> str:
    """Which index, if any, can resolve this package."""
    normalized = name.strip().lower()
    if normalized in FIRST_PARTY_PACKAGES:
        return FIRST_PARTY_SOURCE
    if "+" in version:
        if normalized in LOCAL_VERSION_PACKAGES:
            return PYTORCH_CPU_INDEX
        raise BuilderProtocolError(
            f"{name}=={version} carries a local version but is not a known "
            "PyTorch CPU package; its source index is undetermined and the "
            "build would have to guess."
        )
    return PYPI


def derived_build_input(packages: Sequence[Mapping[str, str]]) -> dict[str, list]:
    """Group the approved set by the index that must resolve it.

    **This is a derived build input, not a new dependency authority.** It
    re-expresses the frozen 335-package mapping in a form a container build can
    consume. No version may be added, removed or changed to make an image build
    succeed; `require_derived_input_matches_authority` proves it did not.
    """
    grouped: dict[str, list] = {source: [] for source in PERMITTED_DEPENDENCY_SOURCES}
    for entry in packages:
        source = classify_dependency_source(entry["name"], entry["version"])
        grouped[source].append((entry["name"], entry["version"]))
    for source in grouped:
        grouped[source].sort()
    return grouped


def derived_input_digest(grouped: Mapping[str, Sequence]) -> str:
    """SHA-256 over the canonical grouping, so the input itself has identity."""
    lines = []
    for source in PERMITTED_DEPENDENCY_SOURCES:
        for name, version in grouped.get(source, ()):
            lines.append(f"{source}\t{name}\t{version}")
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def require_derived_input_matches_authority(
    grouped: Mapping[str, Sequence], packages: Sequence[Mapping[str, str]]
) -> None:
    """Prove the derived input is exactly the frozen mapping, no more or less."""
    flattened = {
        (name, version)
        for source in PERMITTED_DEPENDENCY_SOURCES
        for name, version in grouped.get(source, ())
    }
    authority = {(entry["name"], entry["version"]) for entry in packages}
    if flattened != authority:
        added = sorted(flattened - authority)
        dropped = sorted(authority - flattened)
        raise BuilderProtocolError(
            "the derived build input is not the frozen package authority.\n"
            f"  added:   {added}\n  dropped: {dropped}\n"
            "No package version may be added, removed or changed to make an "
            "image build succeed. If the frozen environment cannot be "
            "reproduced, that is a finding to record, not a set to edit."
        )
    if len(authority) != APPROVED_PACKAGE_COUNT:
        raise BuilderProtocolError(
            f"the authority set holds {len(authority)} packages; the approved "
            f"set is {APPROVED_PACKAGE_COUNT}."
        )


def require_pinned_dependency_specifier(specifier: str) -> str:
    """`name==version`. A range resolves differently on different days."""
    if not re.match(r"^[A-Za-z0-9_.\-]+==[^\s,<>!~]+$", specifier):
        raise BuilderProtocolError(
            f"dependency specifier {specifier!r} is not an exact pin. A range "
            "such as 'numpy>=1.26,<3' resolves to whatever is newest at build "
            "time, so two builds from identical inputs would differ."
        )
    return specifier


# ---------------------------------------------------------------------------
# Build configuration digest -- specification section 15
# ---------------------------------------------------------------------------


def build_configuration_digest(inputs: Mapping[str, str]) -> str:
    """SHA-256 over a canonical manifest of every build-affecting input.

    **The single configuration digest.** There is deliberately no second
    algorithm and no "extended" variant: two digests over overlapping input sets
    would eventually disagree, and the question "which one did the authorization
    name" has no good answer.

    Every role in `BUILD_CONFIGURATION_MEMBERS` must be present. An input the
    manifest omits is an input the authorization does not pin, which is how
    `requirements.pytorch-cpu.txt` was able to change the image without changing
    this value.
    """
    missing = [
        name for name in REQUIRED_BUILD_CONFIGURATION_INPUTS if name not in inputs
    ]
    if missing:
        raise BuilderProtocolError(
            "the build configuration does not cover every influencing input. "
            "Missing: " + ", ".join(sorted(missing))
        )
    unknown = [
        name for name in inputs if name not in REQUIRED_BUILD_CONFIGURATION_INPUTS
    ]
    if unknown:
        raise BuilderProtocolError(
            "the build configuration carries inputs it does not declare, which "
            "are held to no rule: " + ", ".join(sorted(unknown))
        )
    lines = []
    for name in sorted(inputs):
        digest = inputs[name]
        if not _SHA256_HEX.match(str(digest)):
            raise BuilderProtocolError(
                f"build configuration input {name!r} is not identified by a "
                "full lowercase SHA-256."
            )
        lines.append(f"{name}={digest}")
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def build_configuration_manifest(inputs: Mapping[str, str]) -> dict[str, Any]:
    """The digest together with what each member is and why it is bound.

    A bare digest is unreviewable: it says two builds agree without saying what
    they agreed about. This records, per member, the logical role, the path or
    derived identity, the SHA-256, whether it is tracked or derived, and the
    authority it hangs from.
    """
    digest = build_configuration_digest(inputs)
    members = []
    for member in BUILD_CONFIGURATION_MEMBERS:
        members.append(
            {
                "role": member.role,
                "path": member.path,
                "sha256": inputs[member.role],
                "status": member.status,
                "authority": member.authority,
                "affects_artifact_bytes": member.affects_artifact_bytes,
            }
        )
    return {
        "build_configuration_digest": digest,
        "members": members,
        "member_count": len(members),
        "derived_members": list(DERIVED_BUILD_INPUT_ROLES),
    }


#: Every property a `DERIVED_BUILD_INPUT` must have to be acceptable in place of
#: a tracked file. A derived member that cannot demonstrate all of them is not a
#: derived input, it is an unbound one.
DERIVED_INPUT_PROPERTIES: Final[tuple[str, ...]] = (
    "generator_pinned_by_source_commit",
    "generator_inputs_authority_bound",
    "generation_is_deterministic",
    "output_sha256_computed",
    "output_matches_frozen_authority",
    "build_consumes_verified_bytes",
    "regeneration_mismatch_hard_fails",
    "output_digest_in_provenance",
)


def require_derived_input_properties(evidence: Mapping[str, bool]) -> None:
    """Refuse a derived build input that cannot prove every property.

    Being gitignored is not the defect and tracking the file is not the fix: a
    generated file committed by hand is a copy that drifts. What makes a derived
    input acceptable is that it cannot differ from the authority it is derived
    from, and each property below closes one way it otherwise could.
    """
    missing = [name for name in DERIVED_INPUT_PROPERTIES if name not in evidence]
    if missing:
        raise BuilderProtocolError(
            "the derived build input claims no position on: "
            + ", ".join(sorted(missing))
            + ". An unstated property is not a satisfied one."
        )
    unproven = [name for name in DERIVED_INPUT_PROPERTIES if not evidence[name]]
    if unproven:
        raise BuilderProtocolError(
            "this input is generated but not bound, so it is an unbound build "
            "input: " + ", ".join(sorted(unproven)) + ". Either establish these "
            "properties or make the file an immutable tracked input; do not "
            "leave it derived and unproven."
        )


# ---------------------------------------------------------------------------
# Two independent builds -- specification section 18
# ---------------------------------------------------------------------------


def require_independent_builds(
    *,
    first_build_id: str,
    second_build_id: str,
    first_run_identity: str,
    second_run_identity: str,
    second_consumed_first_artifact: bool,
) -> None:
    """Two builds, or one build counted twice. The difference is the point."""
    if first_build_id == second_build_id:
        raise BuilderProtocolError(
            "both builds carry the same build_id; that is one build recorded "
            "twice and it demonstrates nothing about reproducibility."
        )
    if first_run_identity == second_run_identity:
        raise BuilderProtocolError(
            "both builds report the same run identity. Independent builds must "
            "come from separate clean runs, or a shared cache can make two "
            "invocations agree without the build being reproducible."
        )
    if second_consumed_first_artifact:
        raise BuilderProtocolError(
            "the second build consumed the first build's artifact. It then "
            "reproduces a copy rather than the build, which is the one thing "
            "the two-build procedure exists to rule out."
        )


def approved_dependency_digest() -> str:
    """The authority this protocol consumes. Imported, never retyped."""
    return APPROVED_DEPENDENCY_DIGEST


@dataclass(frozen=True)
class BaseImageAuthority:
    """The digest is authority. The tag is descriptive metadata only.

    Both are recorded, because a bare digest is unreadable to a reviewer and a
    bare tag is unverifiable by a build. Only one of them decides anything.
    """

    descriptive_tag: str
    digest_reference: str
    index_digest: str
    platform: str

    def as_attestation(self) -> dict[str, str]:
        return {
            "descriptive_tag": self.descriptive_tag,
            "digest_reference": self.digest_reference,
            "resolved_from_index_digest": self.index_digest,
            "platform": self.platform,
            "authority": "digest_reference",
        }


def require_base_image_authority(
    authority: BaseImageAuthority,
) -> BaseImageAuthority:
    """Refuse a base image that is not addressed by an immutable digest.

    The tag is checked only for presence: it exists so a reviewer can read the
    record, and a build that resolved it differently would still be caught by
    the digest.
    """
    if not authority.descriptive_tag.strip():
        raise BuilderProtocolError(
            "the base image record carries no descriptive tag; a digest alone "
            "is unreadable to the human who must review this."
        )
    try:
        require_immutable_base_image(authority.digest_reference)
    except BuildAuthorityError as error:
        raise BuilderProtocolError(str(error)) from error
    require_declared_platform(
        os_name=authority.platform.split("/")[0],
        architecture=authority.platform.split("/")[-1],
    )
    return authority


def require_artifact_identity_separate_from_location(
    *, output_artifact_digest: str, artifact_location: str
) -> None:
    """Identity is the digest. Location is provenance. Two mirrors, one identity."""
    if "@" in output_artifact_digest or "/" in output_artifact_digest:
        raise BuilderProtocolError(
            f"output_artifact_digest={output_artifact_digest!r} carries a "
            "location. Where a copy lives is provenance; record it in "
            "artifact_location."
        )
    if not artifact_location.strip():
        raise BuilderProtocolError(
            "artifact_location is blank; an artifact nobody can fetch cannot "
            "be verified by a second party."
        )
