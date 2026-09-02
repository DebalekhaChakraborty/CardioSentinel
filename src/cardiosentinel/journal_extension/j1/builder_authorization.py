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

**The identity is the reviewed workflow *bytes*, not a commit equality.**

An earlier version of this module required `github.sha` to equal a
`workflow_commit` field carried by the authorization. That rule was
**unsatisfiable**: the authorization lives in the repository, so the commit that
adds it is the commit the workflow then runs at, and the document would have had
to contain the SHA of the commit containing itself. It could never be written.

What a human actually reviews is a *file*, so that is what the authorization
names: the path, the historical commit at which those bytes were reviewed, and
the SHA-256 of the raw committed bytes. The authorization may therefore live in
a **later** commit than the workflow it authorizes, which is the normal case.
Execution from a later commit is permitted **only while the workflow bytes are
unchanged**; a single differing byte is a hard refusal.

Two ways that can fail, kept separate because they mean different things:

- **reviewed historical workflow drift** -- the bytes at the reviewed commit do
  not hash to the digest the authorization declares, so the authorization is
  describing something that was never there;
- **current workflow differs from the authorized reviewed bytes** -- the
  reviewed commit is intact, but the file being executed has since changed.

**A declared digest is never trusted.** Both digests are recomputed: one from
the working tree, one from git's own object store at the reviewed commit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
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
    "workflow_review_commit",
    "workflow_sha256",
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
    "workflow_review_commit",
    "authorized_source_commit",
)
DIGEST_FIELDS: Final[tuple[str, ...]] = (
    "workflow_sha256",
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
    def workflow_review_commit(self) -> str:
        return str(self.fields["workflow_review_commit"])

    @property
    def workflow_sha256(self) -> str:
        return str(self.fields["workflow_sha256"])

    @property
    def workflow_path(self) -> str:
        return str(self.fields["workflow_path"])

    @property
    def authorized_source_commit(self) -> str:
        return str(self.fields["authorized_source_commit"])

    def as_attestation(self) -> dict[str, Any]:
        return {
            "builder_authorization_id": self.fields["builder_authorization_id"],
            "workflow_review_commit": self.workflow_review_commit,
            "workflow_sha256": self.workflow_sha256,
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


class ReviewedWorkflowDriftError(BuilderAuthorizationError):
    """The reviewed commit does not contain the bytes the authorization names."""


class CurrentWorkflowMismatchError(BuilderAuthorizationError):
    """The workflow about to run is not the one that was reviewed."""


def _git(arguments: list[str], *, repository_root: Path) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repository_root), *arguments],
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise BuilderAuthorizationError(
            "git could not answer a question the authorization depends on: "
            f"git {' '.join(arguments)}\n"
            + completed.stderr.decode("utf-8", "replace").strip()
        )
    return completed.stdout


def workflow_bytes_at_commit(
    repository_root: Path, *, commit: str, path: str
) -> bytes:
    """The raw committed bytes, read from git's object store.

    Not the working tree, and not a parsed-and-re-rendered document: YAML
    round-trips through a parser lossily, and a digest over re-rendered bytes
    would agree with a file nobody wrote.
    """
    return _git(
        ["cat-file", "blob", f"{commit}:{path}"],
        repository_root=repository_root,
    )


def verify_workflow_identity(
    authorization: VerifiedBuilderAuthorization,
    *,
    repository_root: Path,
    running_workflow_ref: str | None = None,
    running_commit: str | None = None,
) -> dict[str, Any]:
    """Bind execution to reviewed bytes rather than to a commit equality.

    Three independent checks, none of which trusts a declared value:

    1. the workflow now on disk hashes to the authorized digest;
    2. the bytes git holds at `workflow_review_commit` hash to the same digest;
    3. the running workflow, if reported, is the authorized path.

    The authorization may live in a commit that did not exist when the workflow
    was reviewed. That is the ordinary case and is exactly what the previous
    commit-equality rule made impossible.
    """
    declared = authorization.workflow_sha256
    path = authorization.workflow_path

    current_file = repository_root / path
    if not current_file.is_file():
        raise CurrentWorkflowMismatchError(
            f"the authorized workflow {path!r} is not present in this checkout."
        )
    current_digest = hashlib.sha256(current_file.read_bytes()).hexdigest()

    reviewed_bytes = workflow_bytes_at_commit(
        repository_root,
        commit=authorization.workflow_review_commit,
        path=path,
    )
    reviewed_digest = hashlib.sha256(reviewed_bytes).hexdigest()

    # Reported before the current-file comparison: if the reviewed commit never
    # held these bytes, the authorization is describing something that did not
    # exist, and the state of the working tree is beside the point.
    if reviewed_digest != declared:
        raise ReviewedWorkflowDriftError(
            "reviewed historical workflow drift: the authorization declares a "
            "digest the reviewed commit does not contain.\n"
            f"  path:               {path}\n"
            f"  review commit:      {authorization.workflow_review_commit}\n"
            f"  declared:           {declared}\n"
            f"  recomputed at that commit: {reviewed_digest}\n"
            "A declared digest is not evidence. This authorization describes "
            "bytes that were never reviewed at that commit."
        )
    if current_digest != declared:
        raise CurrentWorkflowMismatchError(
            "current workflow differs from the authorized reviewed bytes.\n"
            f"  path:       {path}\n"
            f"  authorized: {declared}\n"
            f"  current:    {current_digest}\n"
            "Execution from a later commit is permitted only while the workflow "
            "bytes are unchanged. One differing byte is a different workflow."
        )
    if running_workflow_ref is not None and path not in running_workflow_ref:
        raise CurrentWorkflowMismatchError(
            "this workflow is not the one that was authorized.\n"
            f"  authorized: {path}\n"
            f"  running:    {running_workflow_ref}"
        )

    proof: dict[str, Any] = {
        "workflow_path": path,
        "workflow_review_commit": authorization.workflow_review_commit,
        "workflow_sha256": declared,
        "workflow_sha256_recomputed_from_review_commit": reviewed_digest,
        "workflow_sha256_recomputed_from_checkout": current_digest,
        "authorized_source_commit": authorization.authorized_source_commit,
    }
    proof["running_commit_descends_from_review_commit"] = _describe_ancestry(
        repository_root,
        ancestor=authorization.workflow_review_commit,
        descendant=running_commit,
    )
    return proof


def _describe_ancestry(
    repository_root: Path, *, ancestor: str, descendant: str | None
) -> str:
    """Record whether the running commit descends from the reviewed one.

    Recorded, not enforced. A CI checkout is routinely shallow, so ancestry is
    frequently unprovable locally, and a check that silently passes whenever it
    cannot run is worse than one that says it did not run. The binding claim is
    the byte digest, which needs no history.
    """
    if descendant is None:
        return "not_reported"
    completed = subprocess.run(
        ["git", "-C", str(repository_root), "merge-base", "--is-ancestor",
         ancestor, descendant],
        capture_output=True,
        check=False,
    )
    if completed.returncode == 0:
        return "verified"
    if completed.returncode == 1:
        return "not_a_descendant"
    return "unverifiable_shallow_or_missing_history"


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
    parser.add_argument("--running-commit", default=None)
    arguments = parser.parse_args(argv)

    root = Path(arguments.repository_root).resolve()
    try:
        authorization = verify_builder_authorization(
            load_builder_authorization(root)
        )
        proof = verify_workflow_identity(
            authorization,
            repository_root=root,
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
