"""The executable steps of the controlled build. Capability, never permission.

Every function here can complete its part of the frozen build protocol. None of
them checks whether a build may start -- that is
`builder_authorization.main`'s question, asked once, in its own job, before any
of this runs. Keeping the two apart is the point: a complete build path that
still refuses is the same doctrine as the J1 execution instrument.

**The artifact is produced as an OCI layout archive, not pushed.** The digest
J1 freezes is over the canonical single-platform image manifest bytes, and an
OCI archive contains exactly those bytes, so the digest can be recomputed from
the artifact rather than read from a registry's response. It also means the
build needs no registry credentials, which is why none exist.

**Nothing here builds an image.** `subprocess` is deliberately absent: the
container build is invoked by the workflow, and this module only prepares its
inputs and verifies its outputs. A test asserts the absence structurally.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from pathlib import Path
from typing import Any, Final

from .approved_runtime import APPROVED_DEPENDENCY_DIGEST, APPROVED_PACKAGE_COUNT
from .builder_protocol import (
    ARTIFACT_MEDIA_TYPE,
    DERIVED_INPUT_PROPERTIES,
    FIRST_PARTY_SOURCE,
    INDEX_MEDIA_TYPES,
    PYPI,
    PYTORCH_CPU_INDEX,
    REQUIRED_BUILD_CONFIGURATION_INPUTS,
    TARGET_ARCHITECTURE,
    TARGET_OS,
    BuilderProtocolError,
    build_configuration_manifest,
    derived_build_input,
    derived_input_digest,
    require_derived_input_matches_authority,
    require_derived_input_properties,
    require_pinned_dependency_specifier,
)
from .qualification import (
    QUALIFICATION_POLICY,
    QualificationError,
    classify_divergence,
    verify_qualification_claim,
)

#: The frozen V1 lock the approved package set is read from.
FROZEN_LOCK_PATH: Final = (
    "reproducibility/demo_bundle/runs/phase3b2-architecture-v1/"
    "B4B_cnn_transformer_v1/EXPERIMENT_LOCK.json"
)

#: The extra index the two `+cpu` wheels come from. Named, never discovered.
PYTORCH_CPU_INDEX_URL: Final = "https://download.pytorch.org/whl/cpu"

PYPI_REQUIREMENTS: Final = "requirements.pypi.txt"
PYTORCH_REQUIREMENTS: Final = "requirements.pytorch-cpu.txt"


class ControlledBuildError(RuntimeError):
    """A build input or output the frozen protocol does not admit."""


def _digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_frozen_packages(repository_root: Path) -> list[dict[str, str]]:
    """The approved package set, read from frozen V1 evidence."""
    lock = json.loads(
        (repository_root / FROZEN_LOCK_PATH).read_text(encoding="utf-8")
    )
    packages = lock["environment"]["dependencies"]["installed_packages"]
    if len(packages) != APPROVED_PACKAGE_COUNT:
        raise ControlledBuildError(
            f"the frozen lock holds {len(packages)} packages; the approved set "
            f"is {APPROVED_PACKAGE_COUNT}."
        )
    return list(packages)


def write_dependency_input(repository_root: Path, out_dir: Path) -> dict[str, Any]:
    """Emit the derived build input, then prove it is the frozen mapping.

    Two files, because the approved set does not come from one index. The
    first-party package is written to neither: no index resolves
    `cardiosentinel`, and it is installed from the source tree at the
    authorized commit, which is what pins it.
    """
    packages = load_frozen_packages(repository_root)
    grouped = derived_build_input(packages)
    require_derived_input_matches_authority(grouped, packages)

    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, str] = {}
    for filename, source in (
        (PYPI_REQUIREMENTS, PYPI),
        (PYTORCH_REQUIREMENTS, PYTORCH_CPU_INDEX),
    ):
        lines = []
        for name, version in grouped[source]:
            lines.append(require_pinned_dependency_specifier(f"{name}=={version}"))
        path = out_dir / filename
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        written[filename] = _digest_file(path)

    # Determinism is demonstrated here, not asserted in a comment: the whole
    # grouping is recomputed from the frozen lock a second time and the bytes
    # that would be written are compared to the bytes that were. A derived input
    # that could differ between two runs is an unbound build input, and BUILD_A
    # and BUILD_B would diverge for a reason nobody could see in the digest.
    regrouped = derived_build_input(load_frozen_packages(repository_root))
    for filename, source in (
        (PYPI_REQUIREMENTS, PYPI),
        (PYTORCH_REQUIREMENTS, PYTORCH_CPU_INDEX),
    ):
        expected = "\n".join(
            f"{name}=={version}" for name, version in regrouped[source]
        ) + "\n"
        actual = (out_dir / filename).read_text(encoding="utf-8")
        if expected != actual:
            raise ControlledBuildError(
                f"regenerating {filename} produced different bytes. The derived "
                "build input is not deterministic, so it cannot stand in for a "
                "tracked input: make it an immutable tracked file instead."
            )

    require_derived_input_properties(
        {
            # The generator is this module, carried by the source tree at the
            # authorized commit.
            "generator_pinned_by_source_commit": True,
            # Its only input is the frozen V1 experiment lock, also committed.
            "generator_inputs_authority_bound": True,
            # Just demonstrated above, by regeneration.
            "generation_is_deterministic": True,
            "output_sha256_computed": set(written) == {
                PYPI_REQUIREMENTS,
                PYTORCH_REQUIREMENTS,
            },
            # `require_derived_input_matches_authority` ran before any write.
            "output_matches_frozen_authority": True,
            # The Containerfile COPYs these exact paths.
            "build_consumes_verified_bytes": True,
            # The regeneration check above raises rather than warns.
            "regeneration_mismatch_hard_fails": True,
            # Both files are members of the build configuration manifest.
            "output_digest_in_provenance": True,
        }
    )

    first_party = grouped[FIRST_PARTY_SOURCE]
    return {
        "derived_input_digest": derived_input_digest(grouped),
        "dependency_authority_digest": APPROVED_DEPENDENCY_DIGEST,
        "derived_input_properties": list(DERIVED_INPUT_PROPERTIES),
        "files": written,
        "counts": {
            PYPI: len(grouped[PYPI]),
            PYTORCH_CPU_INDEX: len(grouped[PYTORCH_CPU_INDEX]),
            FIRST_PARTY_SOURCE: len(first_party),
        },
        "first_party_from_source_tree": [name for name, _ in first_party],
        "pytorch_cpu_index_url": PYTORCH_CPU_INDEX_URL,
    }


def configuration_digest(paths: dict[str, Path]) -> dict[str, Any]:
    """Digest every declared build input, then combine them canonically.

    Every role in `REQUIRED_BUILD_CONFIGURATION_INPUTS` must be supplied. The
    previous five-slot form let `requirements.pytorch-cpu.txt` influence the
    image without influencing this digest; the manifest now enumerates one role
    per file, so an omission is a refusal rather than a silent gap.
    """
    missing = [
        role for role in REQUIRED_BUILD_CONFIGURATION_INPUTS if role not in paths
    ]
    if missing:
        raise ControlledBuildError(
            "the build configuration does not cover every declared input. "
            "Missing: " + ", ".join(sorted(missing))
        )
    inputs = {}
    for name, path in paths.items():
        if not path.is_file():
            raise ControlledBuildError(
                f"build configuration input {name!r} is missing at {path}."
            )
        inputs[name] = _digest_file(path)
    manifest = build_configuration_manifest(inputs)
    # `inputs` is retained beside the manifest: callers and provenance records
    # read it by role, and the manifest is the reviewable form of the same facts.
    manifest["inputs"] = inputs
    return manifest


def read_oci_archive_manifest(archive: Path) -> dict[str, Any]:
    """Extract the single-platform image manifest identity from an OCI layout.

    The digest is **recomputed from the manifest bytes in the archive**, never
    read from a registry response or a build tool's summary line. An archive
    carrying an index with more than one manifest is refused: the artifact J1
    freezes is one image, and an index would put a layer of indirection between
    the authorization and the thing that executes.
    """
    if not archive.is_file():
        raise ControlledBuildError(f"no OCI archive at {archive}.")
    with tarfile.open(archive, "r:*") as tar:
        def _read(member_name: str) -> bytes:
            member = tar.extractfile(member_name)
            if member is None:
                raise ControlledBuildError(
                    f"{archive} does not contain {member_name}; it is not an "
                    "OCI layout archive."
                )
            return member.read()

        index = json.loads(_read("index.json"))
        entries = index.get("manifests", [])
        if len(entries) != 1:
            raise ControlledBuildError(
                f"the archive index holds {len(entries)} manifests; the frozen "
                "artifact is a single-platform image. A multi-entry index "
                "identifies a list, not the image J1 would execute."
            )
        entry = entries[0]
        if entry["mediaType"] in INDEX_MEDIA_TYPES:
            raise ControlledBuildError(
                f"the archive's top entry is {entry['mediaType']}, an image "
                "index. Build with a single --platform and no attestations."
            )
        if entry["mediaType"] != ARTIFACT_MEDIA_TYPE:
            raise ControlledBuildError(
                f"the archive's manifest media type is {entry['mediaType']!r}, "
                f"not the frozen {ARTIFACT_MEDIA_TYPE}."
            )
        algorithm, _, hexdigest = entry["digest"].partition(":")
        if algorithm != "sha256":
            raise ControlledBuildError(
                f"unexpected digest algorithm {algorithm!r}; the frozen "
                "algorithm is sha256."
            )
        blob = _read(f"blobs/sha256/{hexdigest}")

    # The archive's own digest is transport metadata, computed over the tar
    # bytes. It is recorded so a retained archive can be checked end to end, and
    # it is deliberately NOT the artifact identity: two archives of one image
    # differ in tar framing while naming the same manifest.
    archive_sha256 = hashlib.sha256(archive.read_bytes()).hexdigest()

    recomputed = "sha256:" + hashlib.sha256(blob).hexdigest()
    if recomputed != entry["digest"]:
        raise ControlledBuildError(
            "the archive's manifest bytes do not hash to the digest the index "
            f"names.\n  index:      {entry['digest']}\n"
            f"  recomputed: {recomputed}"
        )
    manifest = json.loads(blob)
    platform = entry.get("platform") or {}
    if platform and (
        platform.get("os") != TARGET_OS
        or platform.get("architecture") != TARGET_ARCHITECTURE
    ):
        raise ControlledBuildError(
            f"the archive targets {platform.get('os')}/"
            f"{platform.get('architecture')}, not the frozen "
            f"{TARGET_OS}/{TARGET_ARCHITECTURE}."
        )
    return {
        "output_artifact_digest": recomputed,
        "artifact_media_type": entry["mediaType"],
        "target_platform": f"{TARGET_OS}/{TARGET_ARCHITECTURE}",
        "manifest_config_digest": manifest.get("config", {}).get("digest"),
        "layer_count": len(manifest.get("layers", [])),
        "archive_sha256": archive_sha256,
        "archive_digest_is_not_artifact_identity": True,
    }


#: The two builds agreed. The preferred outcome, and the only one that permits
#: an artifact to go forward to qualification.
BIT_REPRODUCIBLE: Final = "BIT_REPRODUCIBLE"
#: Identical inputs produced different artifacts. A **valid observed outcome**,
#: not an error -- which is the whole reason the two-build procedure exists. It
#: is recorded first and refused second.
DIVERGED: Final = "DIVERGED"

REPRODUCIBILITY_CLASSES: Final[tuple[str, ...]] = (BIT_REPRODUCIBLE, DIVERGED)

#: Every field a build provenance record must carry before it can be compared.
#: A record missing one of these is malformed input, not evidence about
#: reproducibility.
REQUIRED_BUILD_RECORD_FIELDS: Final[tuple[str, ...]] = (
    "build_id",
    "source_commit",
    "base_image_digest",
    "dependency_digest",
    "build_configuration_digest",
    "target_platform",
    "output_artifact_digest",
)

#: The inputs the reproducibility contract holds fixed. Two builds that differ
#: in any of them are not a reproducibility experiment.
SHARED_CONTRACT_INPUTS: Final[tuple[str, ...]] = (
    "source_commit",
    "base_image_digest",
    "dependency_digest",
    "build_configuration_digest",
    "target_platform",
)


def require_comparable_builds(
    first: dict[str, Any], second: dict[str, Any]
) -> None:
    """Refuse inputs that cannot answer the reproducibility question at all.

    **These are protocol failures, not reproducibility findings.** Two builds
    from different source commits disagreeing tells you nothing about whether
    the environment is reproducible, and recording that as `DIVERGED` would
    manufacture a finding out of a mistake. They raise; a genuine divergence
    does not.
    """
    for label, record in (("BUILD_A", first), ("BUILD_B", second)):
        if not isinstance(record, dict):
            raise ControlledBuildError(
                f"{label} provenance is malformed: expected an object, got "
                f"{type(record).__name__}."
            )
        missing = [n for n in REQUIRED_BUILD_RECORD_FIELDS if not record.get(n)]
        if missing:
            raise ControlledBuildError(
                f"{label} provenance is malformed; it carries no "
                + ", ".join(sorted(missing))
                + ". A record missing a contract field is invalid input, not a "
                "reproducibility observation."
            )
    differing = [
        name
        for name in SHARED_CONTRACT_INPUTS
        if first.get(name) != second.get(name)
    ]
    if differing:
        raise ControlledBuildError(
            "the two builds do not share the contract's inputs, so they say "
            f"nothing about reproducibility. Differing: {sorted(differing)}. "
            "This is an invalid qualification input, not a divergence."
        )
    if first["build_id"] == second["build_id"]:
        raise ControlledBuildError(
            "both records carry the same build_id; that is one build recorded "
            "twice, which is an invalid qualification input rather than a "
            "reproducibility result."
        )


def reproducibility_record(
    *,
    first: dict[str, Any],
    second: dict[str, Any],
    claim: dict[str, Any],
) -> dict[str, Any]:
    """Phase A -- record the observation. **A divergence never raises here.**

    An earlier version computed the comparison and the refusal in one call, so a
    divergence raised before any record was written: the single outcome the
    procedure exists to detect was the one outcome that left no evidence, and
    the finding survived only as a line in an expiring run log.

    Invalid inputs still raise, because there is nothing to observe.
    """
    verified = verify_qualification_claim(claim)
    require_comparable_builds(first, second)

    a = first["output_artifact_digest"]
    b = second["output_artifact_digest"]
    agreed = a == b
    return {
        "qualification_policy": QUALIFICATION_POLICY,
        "builder_authorization_id": verified.authorization_id,
        "workflow_run_id": verified.fields["workflow_run_id"],
        "workflow_run_attempt": verified.fields["workflow_run_attempt"],
        "build_a_artifact_digest": a,
        "build_b_artifact_digest": b,
        "build_a_archive_sha256": first.get("archive_sha256"),
        "build_b_archive_sha256": second.get("archive_sha256"),
        "reproducibility_class": BIT_REPRODUCIBLE if agreed else DIVERGED,
        "failure_class": classify_divergence(
            build_a_digest=a, build_b_digest=b
        ),
        "build_ids": [first["build_id"], second["build_id"]],
        "source_commit": first["source_commit"],
        "base_image_digest": first["base_image_digest"],
        "dependency_digest": first["dependency_digest"],
        "build_configuration_digest": first["build_configuration_digest"],
        "target_platform": first["target_platform"],
        # Deliberately absent on divergence, and absent here in both cases: no
        # single artifact is selected by this record. Promotion is a later act.
        "promoted_artifact": None,
    }


def enforce_reproducibility(record: Any) -> dict[str, Any]:
    """Phase B -- read the written record and refuse a divergence.

    Separate from Phase A so the evidence exists on disk before anything fails.
    This reads a record rather than recomputing one: enforcing against a value
    the enforcement step derived itself would not prove the retained evidence
    says what the failure claims.
    """
    if not isinstance(record, dict) or not record:
        raise ControlledBuildError(
            "the reproducibility record is empty or malformed. Once BUILD_A and "
            "BUILD_B produced valid records, failing to produce the comparison "
            "record is itself a protocol failure, not a missing file."
        )
    missing = [
        name
        for name in (
            "reproducibility_class",
            "build_a_artifact_digest",
            "build_b_artifact_digest",
        )
        if not record.get(name)
    ]
    if missing:
        raise ControlledBuildError(
            "the reproducibility record does not carry "
            + ", ".join(sorted(missing))
            + "; it cannot be enforced against."
        )
    classification = record["reproducibility_class"]
    if classification not in REPRODUCIBILITY_CLASSES:
        raise ControlledBuildError(
            f"reproducibility_class={classification!r} is not one of "
            + ", ".join(REPRODUCIBILITY_CLASSES)
        )
    if classification == DIVERGED:
        raise ControlledBuildError(
            "identical inputs produced different artifacts.\n"
            f"  BUILD_A: {record['build_a_artifact_digest']}\n"
            f"  BUILD_B: {record['build_b_artifact_digest']}\n"
            "STOP. Neither digest is promoted, neither build is selected, and "
            "this is not reclassified as documented non-reproducibility. A "
            "divergence is a finding requiring human review, and the record of "
            "it has already been written and retained."
        )
    return {
        "reproducibility_class": BIT_REPRODUCIBLE,
        "output_artifact_digest": record["build_a_artifact_digest"],
        "build_ids": record.get("build_ids", []),
    }


def _command_dependency_input(arguments: argparse.Namespace) -> dict[str, Any]:
    return write_dependency_input(
        Path(arguments.repository_root).resolve(), Path(arguments.out_dir)
    )


def _command_configuration_digest(arguments: argparse.Namespace) -> dict[str, Any]:
    """One flag per declared member, derived from the member tuple itself.

    Adding a build input therefore adds a required flag, and a workflow that has
    not been updated fails loudly rather than digesting a smaller set.
    """
    return configuration_digest(
        {
            role: Path(getattr(arguments, role))
            for role in REQUIRED_BUILD_CONFIGURATION_INPUTS
        }
    )


def _command_artifact_digest(arguments: argparse.Namespace) -> dict[str, Any]:
    return read_oci_archive_manifest(Path(arguments.oci_archive))


def _command_qualification_claim(arguments: argparse.Namespace) -> dict[str, Any]:
    """Emit the claim record. Verified on the way out, never on the way in."""
    claim = verify_qualification_claim(
        {
            "builder_authorization_id": arguments.builder_authorization_id,
            "qualification_policy": QUALIFICATION_POLICY,
            "provider": arguments.provider,
            "workflow_run_id": arguments.run_id,
            "workflow_run_number": arguments.run_number,
            "workflow_run_attempt": arguments.run_attempt,
            "workflow_sha256": arguments.workflow_sha256,
            "authorized_source_commit": arguments.authorized_source_commit,
            "build_configuration_digest": arguments.build_configuration_digest,
            "claimed_at": arguments.claimed_at,
        }
    )
    return claim.as_document()


def _command_reproducibility_record(
    arguments: argparse.Namespace,
) -> dict[str, Any]:
    return reproducibility_record(
        first=json.loads(Path(arguments.build_a).read_text(encoding="utf-8")),
        second=json.loads(Path(arguments.build_b).read_text(encoding="utf-8")),
        claim=json.loads(Path(arguments.claim).read_text(encoding="utf-8")),
    )


def _command_enforce_reproducibility(
    arguments: argparse.Namespace,
) -> dict[str, Any]:
    raw = Path(arguments.record).read_text(encoding="utf-8")
    if not raw.strip():
        raise ControlledBuildError(
            f"{arguments.record} is empty. An empty comparison record is a "
            "protocol failure, not an absent result."
        )
    return enforce_reproducibility(json.loads(raw))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="j1-controlled-build")
    parser.add_argument("--repository-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    dependency = sub.add_parser("dependency-input")
    dependency.add_argument("--out-dir", required=True)
    dependency.set_defaults(handler=_command_dependency_input)

    configuration = sub.add_parser("configuration-digest")
    for role in REQUIRED_BUILD_CONFIGURATION_INPUTS:
        configuration.add_argument(
            f"--{role.replace('_', '-')}", dest=role, required=True
        )
    configuration.set_defaults(handler=_command_configuration_digest)

    claim = sub.add_parser("qualification-claim")
    for flag in (
        "builder-authorization-id",
        "provider",
        "run-id",
        "run-number",
        "run-attempt",
        "workflow-sha256",
        "authorized-source-commit",
        "build-configuration-digest",
        "claimed-at",
    ):
        claim.add_argument(f"--{flag}", required=True)
    claim.set_defaults(handler=_command_qualification_claim)

    artifact = sub.add_parser("artifact-digest")
    artifact.add_argument("--oci-archive", required=True)
    artifact.set_defaults(handler=_command_artifact_digest)

    # Two commands, deliberately not one. Recording and enforcement are
    # separate steps so the evidence is on disk before anything can fail.
    record = sub.add_parser("reproducibility-record")
    record.add_argument("--build-a", required=True)
    record.add_argument("--build-b", required=True)
    record.add_argument("--claim", required=True)
    record.set_defaults(handler=_command_reproducibility_record)

    enforce = sub.add_parser("enforce-reproducibility")
    enforce.add_argument("--record", required=True)
    enforce.set_defaults(handler=_command_enforce_reproducibility)
    return parser


def main(argv: list[str] | None = None) -> int:
    """No subcommand checks permission. That gate ran before any of this."""
    arguments = build_parser().parse_args(argv)
    try:
        result = arguments.handler(arguments)
    except (ControlledBuildError, BuilderProtocolError, QualificationError) as error:
        print(f"controlled build step failed: {error}")
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised as a subprocess
    raise SystemExit(main())
