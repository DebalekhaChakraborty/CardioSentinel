"""The builder authorization schema, its verifier, and the fail-closed gate.

**This module authorizes nothing and instantiates nothing.** It says what a
future `J1_BUILDER_AUTHORIZATION_V1` must contain and refuses everything that
falls short. The repository contains no builder authorization, and running any
of this does not create one.

**Why the gate lives here rather than in the workflow.** A check written in YAML
is reviewed once, by whoever reads the workflow. A check written here is
executed by the workflow, exercised by the test suite on every commit, and
cannot be edited without the diff appearing in a Python review. The workflow
calls `python -m ...builder_authorization` and obeys the exit status; it decides
nothing itself.

**The self-reference is resolved by the authorization, not by the workflow.**
A workflow cannot contain the commit that contains it. So the workflow does not
name its own identity: it reports the identity it is *running as* --
`github.workflow_ref` and `github.sha` -- and the authorization must already
name exactly that. A workflow running at a commit no human named is refused,
which is the same rule from the other direction and needs no placeholder.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Mapping

from .approved_runtime import APPROVED_DEPENDENCY_DIGEST
from .builder_protocol import (
    ARTIFACT_KIND,
    GENERIC_BUILDER_IDENTITIES,
    TARGET_PLATFORM,
    BuilderProtocolError,
)

#: Where a human-signed builder authorization would live. Its absence is the
#: repository's ordinary state and is why every build currently refuses.
BUILDER_AUTHORIZATION_PATH: Final = (
    "docs/journal-extension/j1/J1_BUILDER_AUTHORIZATION_V1.json"
)

#: Every field the future authorization must carry. None may default.
BUILDER_AUTHORIZATION_FIELDS: Final[tuple[str, ...]] = (
    "builder_authorization_id",
    "builder_candidate_id",
    "provider",
    "repository",
    "workflow_path",
    "workflow_commit",
    "runner_class",
    "controlled_build_protocol_identity",
    "controlled_build_protocol_digest",
    "source_repository",
    "authorized_source_commit",
    "target_platform",
    "artifact_type",
    "base_image_digest",
    "dependency_authority_identity",
    "dependency_digest",
    "build_configuration_digest",
    "provenance_destination",
    "authorization_timestamp",
    "human_authorizer_identity",
)

#: Values that would leave a field to be filled in after review.
PLACEHOLDER_VALUES: Final[tuple[str, ...]] = (
    "pending",
    "tbd",
    "todo",
    "n/a",
    "none",
    "unknown",
    "*",
    "any",
    "latest",
)

_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")
_IMAGE_BY_DIGEST = re.compile(r"^[^\s@]+@sha256:[0-9a-f]{64}$")

COMMIT_FIELDS: Final[tuple[str, ...]] = (
    "workflow_commit",
    "authorized_source_commit",
)
DIGEST_FIELDS: Final[tuple[str, ...]] = (
    "controlled_build_protocol_digest",
    "dependency_digest",
    "build_configuration_digest",
)


class BuilderAuthorizationError(RuntimeError):
    """No builder authorization, or one that does not say what it must say."""


@dataclass(frozen=True)
class VerifiedBuilderAuthorization:
    """A verified authorization. Only `verify_builder_authorization` builds one."""

    fields: Mapping[str, Any]

    @property
    def workflow_commit(self) -> str:
        return str(self.fields["workflow_commit"])

    @property
    def authorized_source_commit(self) -> str:
        return str(self.fields["authorized_source_commit"])

    def as_attestation(self) -> dict[str, Any]:
        return {
            "builder_authorization_id": self.fields["builder_authorization_id"],
            "workflow_commit": self.workflow_commit,
            "authorized_source_commit": self.authorized_source_commit,
            "human_authorizer_identity": self.fields["human_authorizer_identity"],
        }


def _require_text(document: Mapping[str, Any], name: str) -> str:
    value = document[name]
    if not isinstance(value, str) or not value.strip():
        raise BuilderAuthorizationError(
            f"{name!r} must be explicit text; a blank field is a refusal, not "
            "a permissive default."
        )
    if value.strip().lower() in PLACEHOLDER_VALUES:
        raise BuilderAuthorizationError(
            f"{name}={value!r} is a placeholder. A field left to be completed "
            "after review is a field nobody reviewed."
        )
    return value


def verify_builder_authorization(document: Any) -> VerifiedBuilderAuthorization:
    """Refuse unless every field is present, explicit and immutable.

    `None` -- the repository's current state -- is the ordinary case and is
    refused first, in its own words.
    """
    if document is None:
        raise BuilderAuthorizationError(
            "builder authorization absent. No human has named a controlled "
            "builder for the J1 environment artifact, so no build may run. "
            f"An authorization would live at {BUILDER_AUTHORIZATION_PATH}; the "
            "repository contains none, and running this does not create one."
        )
    if not isinstance(document, Mapping):
        raise BuilderAuthorizationError(
            "a builder authorization must be a mapping of explicit fields, got "
            f"{type(document).__name__}."
        )
    missing = [n for n in BUILDER_AUTHORIZATION_FIELDS if n not in document]
    if missing:
        raise BuilderAuthorizationError(
            "the builder authorization is incomplete; no field has a default. "
            "Missing: " + ", ".join(sorted(missing))
        )
    unknown = [n for n in document if n not in BUILDER_AUTHORIZATION_FIELDS]
    if unknown:
        raise BuilderAuthorizationError(
            "the authorization carries fields it does not define, which are "
            "held to no rule: " + ", ".join(sorted(unknown))
        )
    for name in BUILDER_AUTHORIZATION_FIELDS:
        _require_text(document, name)

    for name in COMMIT_FIELDS:
        if not _GIT_SHA.match(document[name]):
            raise BuilderAuthorizationError(
                f"{name}={document[name]!r} is not a full 40-character commit "
                "SHA. A branch name or tag can be moved after authorization, "
                "so the thing authorized and the thing that runs would differ."
            )
    for name in DIGEST_FIELDS:
        if not _SHA256_HEX.match(document[name]):
            raise BuilderAuthorizationError(
                f"{name}={document[name]!r} is not a full lowercase SHA-256."
            )
    if not _IMAGE_BY_DIGEST.match(document["base_image_digest"]):
        raise BuilderAuthorizationError(
            f"base_image_digest={document['base_image_digest']!r} is not "
            "addressed by digest as repository@sha256:<64 hex>."
        )
    if document["repository"].strip().lower() in GENERIC_BUILDER_IDENTITIES:
        raise BuilderAuthorizationError(
            f"{document['repository']!r} names a provider, not a repository. "
            "Authorizing it would authorize every workflow it covers."
        )
    if document["target_platform"] != TARGET_PLATFORM:
        raise BuilderAuthorizationError(
            f"target_platform={document['target_platform']!r} is not the frozen "
            f"platform {TARGET_PLATFORM}."
        )
    if document["artifact_type"] != ARTIFACT_KIND:
        raise BuilderAuthorizationError(
            f"artifact_type={document['artifact_type']!r} is not the frozen "
            f"artifact type {ARTIFACT_KIND}."
        )
    if document["dependency_digest"] != APPROVED_DEPENDENCY_DIGEST:
        raise BuilderAuthorizationError(
            "the authorization names a dependency digest that is not the "
            "approved one. A builder authorization consumes the runtime "
            "authority; it does not define a new one."
        )
    return VerifiedBuilderAuthorization(fields=dict(document))


def load_builder_authorization(repository_root: Path) -> Any:
    """Read the authorization document, or `None` when there is none.

    Absence returns `None` rather than raising, so the refusal comes from
    `verify_builder_authorization` in one place and reads the same whether the
    file is missing, empty or malformed.
    """
    path = repository_root / BUILDER_AUTHORIZATION_PATH
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def require_running_identity_is_authorized(
    authorization: VerifiedBuilderAuthorization,
    *,
    running_workflow_ref: str,
    running_commit: str,
) -> dict[str, str]:
    """The workflow must be running as the object a human actually named.

    `running_workflow_ref` is GitHub's `github.workflow_ref`, of the form
    `owner/repo/.github/workflows/file.yml@refs/heads/branch`. The path is
    compared; the ref suffix is not, because the commit is compared directly
    and is the stronger claim.
    """
    expected_path = str(authorization.fields["workflow_path"])
    if expected_path not in running_workflow_ref:
        raise BuilderAuthorizationError(
            "this workflow is not the one that was authorized.\n"
            f"  authorized: {expected_path}\n"
            f"  running:    {running_workflow_ref}"
        )
    if running_commit != authorization.workflow_commit:
        raise BuilderAuthorizationError(
            "this workflow is running at a commit no human authorized.\n"
            f"  authorized: {authorization.workflow_commit}\n"
            f"  running:    {running_commit}\n"
            "The authorization names the exact reviewed bytes; a later commit "
            "to the same path is a different object."
        )
    return {
        "workflow_path": expected_path,
        "workflow_commit": authorization.workflow_commit,
        "authorized_source_commit": authorization.authorized_source_commit,
    }


def main(argv: list[str] | None = None) -> int:
    """The fail-closed gate the controlled workflow invokes.

    Exits non-zero when no authorization exists, which is the current and
    ordinary state. There is no flag that makes it exit zero anyway.
    """
    parser = argparse.ArgumentParser(
        prog="j1-builder-authorization-gate",
        description="Refuse a controlled build that no human authorized.",
    )
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--running-workflow-ref", required=True)
    parser.add_argument("--running-commit", required=True)
    arguments = parser.parse_args(argv)

    root = Path(arguments.repository_root).resolve()
    try:
        authorization = verify_builder_authorization(
            load_builder_authorization(root)
        )
        proof = require_running_identity_is_authorized(
            authorization,
            running_workflow_ref=arguments.running_workflow_ref,
            running_commit=arguments.running_commit,
        )
    except (BuilderAuthorizationError, BuilderProtocolError, ValueError) as error:
        print("controlled build refused: builder authorization absent", file=sys.stderr)
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised as a subprocess
    raise SystemExit(main())
