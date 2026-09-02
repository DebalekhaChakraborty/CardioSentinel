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
    FIRST_PARTY_SOURCE,
    INDEX_MEDIA_TYPES,
    PYPI,
    PYTORCH_CPU_INDEX,
    TARGET_ARCHITECTURE,
    TARGET_OS,
    BuilderProtocolError,
    build_configuration_digest,
    derived_build_input,
    derived_input_digest,
    require_derived_input_matches_authority,
    require_pinned_dependency_specifier,
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

    first_party = grouped[FIRST_PARTY_SOURCE]
    return {
        "derived_input_digest": derived_input_digest(grouped),
        "dependency_authority_digest": APPROVED_DEPENDENCY_DIGEST,
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
    """Digest every build-affecting file, then combine them canonically."""
    inputs = {}
    for name, path in paths.items():
        if not path.is_file():
            raise ControlledBuildError(
                f"build configuration input {name!r} is missing at {path}."
            )
        inputs[name] = _digest_file(path)
    return {
        "build_configuration_digest": build_configuration_digest(inputs),
        "inputs": inputs,
    }


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
    }


def compare_builds(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    """The reproducibility gate. Divergence stops; it never selects a winner."""
    shared = (
        "source_commit",
        "base_image_digest",
        "dependency_digest",
        "build_configuration_digest",
        "target_platform",
    )
    differing = [k for k in shared if first.get(k) != second.get(k)]
    if differing:
        raise ControlledBuildError(
            "the two builds do not share the contract's inputs, so they say "
            f"nothing about reproducibility. Differing: {sorted(differing)}."
        )
    if first["build_id"] == second["build_id"]:
        raise ControlledBuildError(
            "both records carry the same build_id; that is one build recorded "
            "twice."
        )
    a = first["output_artifact_digest"]
    b = second["output_artifact_digest"]
    if a != b:
        raise ControlledBuildError(
            "identical inputs produced different artifacts.\n"
            f"  BUILD_A: {a}\n  BUILD_B: {b}\n"
            "STOP. Neither digest is promoted, neither build is selected, and "
            "this is not reclassified as documented non-reproducibility. A "
            "divergence is a finding requiring human review."
        )
    return {
        "reproducibility_class": "BIT_REPRODUCIBLE",
        "output_artifact_digest": a,
        "build_ids": [first["build_id"], second["build_id"]],
    }


def _command_dependency_input(arguments: argparse.Namespace) -> dict[str, Any]:
    return write_dependency_input(
        Path(arguments.repository_root).resolve(), Path(arguments.out_dir)
    )


def _command_configuration_digest(arguments: argparse.Namespace) -> dict[str, Any]:
    return configuration_digest(
        {
            "containerfile": Path(arguments.containerfile),
            "dependency_input": Path(arguments.dependency_input),
            "build_script": Path(arguments.build_script),
            "workflow": Path(arguments.workflow),
            "artifact_validation_script": Path(arguments.validation_script),
        }
    )


def _command_artifact_digest(arguments: argparse.Namespace) -> dict[str, Any]:
    return read_oci_archive_manifest(Path(arguments.oci_archive))


def _command_compare(arguments: argparse.Namespace) -> dict[str, Any]:
    return compare_builds(
        json.loads(Path(arguments.build_a).read_text(encoding="utf-8")),
        json.loads(Path(arguments.build_b).read_text(encoding="utf-8")),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="j1-controlled-build")
    parser.add_argument("--repository-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    dependency = sub.add_parser("dependency-input")
    dependency.add_argument("--out-dir", required=True)
    dependency.set_defaults(handler=_command_dependency_input)

    configuration = sub.add_parser("configuration-digest")
    for flag in (
        "containerfile",
        "dependency-input",
        "build-script",
        "workflow",
        "validation-script",
    ):
        configuration.add_argument(f"--{flag}", required=True)
    configuration.set_defaults(handler=_command_configuration_digest)

    artifact = sub.add_parser("artifact-digest")
    artifact.add_argument("--oci-archive", required=True)
    artifact.set_defaults(handler=_command_artifact_digest)

    compare = sub.add_parser("compare-builds")
    compare.add_argument("--build-a", required=True)
    compare.add_argument("--build-b", required=True)
    compare.set_defaults(handler=_command_compare)
    return parser


def main(argv: list[str] | None = None) -> int:
    """No subcommand checks permission. That gate ran before any of this."""
    arguments = build_parser().parse_args(argv)
    try:
        result = arguments.handler(arguments)
    except (ControlledBuildError, BuilderProtocolError) as error:
        print(f"controlled build step failed: {error}")
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised as a subprocess
    raise SystemExit(main())
