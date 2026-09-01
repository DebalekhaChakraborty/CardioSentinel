"""The production entry point, and the ordering that keeps it safe.

Stage order is structural, not documentary. Every stage below must pass before
the next is attempted, and **no physiological datum, annotation-derived
quantity, score artifact or fold metadata may be opened before the attempt is
claimed**:

    freeze binding
    -> authorization verification
    -> git identity verification
    -> environment authority verification
    -> negative-capability proof
    -> execution-capability proof
    -> provenance sink validation
    -> attempt-budget validation
    -> atomic attempt claim
    -> ONLY THEN scientific data access

In the repository's current state this function stops at stage 2 with
`J1 authorization absent`, because J1 is PRE-REGISTERED and not AUTHORIZED.

There is no `force`, `DEV_MODE`, `skip_authorization` or `allow_unauthorized`
parameter. Synthetic qualification does not call this function at all; it
exercises the stages directly with in-memory fixtures, so no fixture can ever be
mistaken by production code for an authorization.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .authorization import AuthorizationError, J1Authorization, verify_authorization
from .capability_gate import require_execution_capability
from .environment_authority import (
    EnvironmentAuthorityError,
    verify_runtime_matches,
)
from .freeze_binding import verify_freeze_binding
from .negative_capability import (
    ForbiddenCounters,
    NegativeCapabilityError,
    runtime_absence_proof,
    structural_proof,
)
from .provenance import require_sink
from .visibility import ScientificVisibility

J1_PACKAGE_ROOT = Path(__file__).resolve().parent


class PreflightError(RuntimeError):
    """A stage refused. The run stops here; nothing downstream is attempted."""


@dataclass(frozen=True)
class PreflightResult:
    """What a passing preflight proved. Not a permission to skip anything."""

    authorization: J1Authorization
    stages_passed: tuple[str, ...]
    counters: dict[str, int]
    environment_authority_verified: bool


def _git(args: list[str], *, repository_root: Path) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repository_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def run_preflight(
    *,
    authorization_document: Any | None,
    collaborators: dict[str, Any] | None = None,
    provenance_sink: object | None = None,
    environment_authority: Any | None = None,
    observed_dependency_digest: str | None = None,
    repository_root: Path | None = None,
    visibility: ScientificVisibility | None = None,
) -> PreflightResult:
    """Run every gate in order. Refuses before any scientific access."""
    root = repository_root or J1_PACKAGE_ROOT.parents[3]
    latch = visibility or ScientificVisibility()
    latch.require_not_visible("preflight")
    passed: list[str] = []

    # 1. freeze binding -- the reviewed bytes, or INVALID_EXECUTION.
    verify_freeze_binding(repository_root=root)
    passed.append("freeze_binding")

    # 2. authorization. In the current repository state this is where it stops.
    try:
        authorization = verify_authorization(authorization_document)
    except AuthorizationError as error:
        raise PreflightError(str(error)) from error
    passed.append("authorization")

    # 3. git and environment identity.
    head = _git(["rev-parse", "HEAD"], repository_root=root)
    if head != authorization.authorized_execution_git_sha:
        raise PreflightError(
            "execution git SHA mismatch: authorization names "
            f"{authorization.authorized_execution_git_sha}, HEAD is {head}."
        )
    if _git(["status", "--porcelain"], repository_root=root):
        raise PreflightError(
            "the worktree is dirty; a scientific attempt requires a clean tree."
        )
    passed.append("git_identity")

    # 4. environment authority. The digest must name an approved runtime, not
    #    whatever happened to exist. There is no bypass parameter.
    if environment_authority is None:
        raise PreflightError(
            "environment authority absent. J1 requires a qualified environment "
            "authority record whose digest the authorization names; a developer "
            "machine is not a scientific authority."
        )
    if environment_authority.environment_sha256 != authorization.environment_sha256:
        raise PreflightError(
            "environment digest mismatch: the authorization names "
            f"{authorization.environment_sha256}, the supplied authority is "
            f"{environment_authority.environment_sha256}."
        )
    try:
        environment_proof = verify_runtime_matches(
            environment_authority,
            dependency_digest=observed_dependency_digest or "",
        )
    except EnvironmentAuthorityError as error:
        raise PreflightError(str(error)) from error
    passed.append("environment_authority")

    # 5. negative capability, layers 1 and 2a.
    counters = ForbiddenCounters()
    try:
        structural_proof(J1_PACKAGE_ROOT)
        runtime_absence_proof()
    except NegativeCapabilityError as error:
        raise PreflightError(str(error)) from error
    passed.append("negative_capability")

    # 6. execution capability -- can the graph finish?
    require_execution_capability(collaborators or {})
    passed.append("capability")

    # 7. provenance sink.
    require_sink(provenance_sink)
    passed.append("provenance_sink")

    # 8. attempt budget. Absence is refusal; zero is never read as one.
    if authorization.attempt_budget < 1:
        raise PreflightError("attempt budget absent or non-positive.")
    passed.append("attempt_budget")

    return PreflightResult(
        authorization=authorization,
        stages_passed=tuple(passed),
        counters=counters.require_all_zero(),
        environment_authority_verified=bool(
            environment_proof["environment_authority_verified"]
        ),
    )


def main() -> int:
    """Unarmed production entry point. Stops before anything is claimed."""
    try:
        run_preflight(authorization_document=None)
    except PreflightError as error:
        print(f"J1 refused: {error}")
        return 1
    print("J1 preflight passed; execution is a separate authorized act.")
    return 0
