"""Governance of the inert controlled-build workflow.

**No image is built, no artifact digest is produced, no builder is authorized,
no environment record exists, and no scientific data is touched.** These tests
prove the workflow is complete *and* cannot start.

The checks parse the workflow semantically rather than grepping it. A grep for
`on: push` misses `on: {push: {branches: [main]}}`, and a grep for `needs`
cannot tell which job it belongs to.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

from cardiosentinel.journal_extension.j1 import preflight
from cardiosentinel.journal_extension.j1.builder_authorization import (
    BUILDER_AUTHORIZATION_FIELDS,
    BUILDER_AUTHORIZATION_PATH,
    BuilderAuthorizationError,
    CurrentWorkflowMismatchError,
    ReviewedWorkflowDriftError,
    load_builder_authorization,
    verify_builder_authorization,
    verify_workflow_identity,
)

REPOSITORY_ROOT = Path(preflight.J1_PACKAGE_ROOT).parents[3]
WORKFLOW_PATH = (
    REPOSITORY_ROOT / ".github/workflows/j1-environment-artifact-build.yml"
)

#: Jobs that could touch a base image, a registry or an artifact.
ARTIFACT_PRODUCING_JOBS = ("build-a", "build-b", "reproducibility")

FORBIDDEN_TRIGGERS = (
    "push",
    "pull_request",
    "pull_request_target",
    "schedule",
    "release",
    "create",
    "registry_package",
    "repository_dispatch",
    "workflow_run",
    "workflow_call",
    "issues",
    "check_suite",
)


def _workflow() -> dict[str, Any]:
    return yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))


def _triggers(document: dict[str, Any]) -> dict[str, Any]:
    """PyYAML parses a bare `on:` key as the boolean `True`, not the string.

    A test that looked up `"on"` would find nothing and pass while the
    workflow triggered on every push, so the key is resolved explicitly.
    """
    if "on" in document:
        return document["on"] or {}
    return document.get(True) or {}


def _steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    return list(job.get("steps") or [])


# -- the workflow exists and is a real object ------------------------------


def test_the_controlled_build_workflow_exists_and_parses() -> None:
    """A future authorization must be able to name an actual workflow object."""
    assert WORKFLOW_PATH.is_file()
    document = _workflow()
    assert document["name"]
    assert set(document["jobs"]) >= {
        "builder-authorization",
        "build-capability",
        *ARTIFACT_PRODUCING_JOBS,
    }


def test_ci_is_not_repurposed() -> None:
    """Proving code correct and building a scientific environment are separate
    concerns, and `ci.yml` is deliberately still the unpinned 3.11 job."""
    ci = yaml.safe_load(
        (REPOSITORY_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    )
    assert ci["name"] == "CI"
    assert "j1" not in json.dumps(ci).lower()


# -- trigger model: nothing automatic --------------------------------------


def test_the_only_trigger_is_manual_invocation() -> None:
    assert set(_triggers(_workflow())) == {"workflow_dispatch"}


@pytest.mark.parametrize("trigger", FORBIDDEN_TRIGGERS)
def test_no_automatic_trigger_exists(trigger: str) -> None:
    assert trigger not in _triggers(_workflow())


def test_manual_invocation_cannot_supply_any_value() -> None:
    """An input is a value a caller supplies; no supplied value may contribute
    to authorization, so the dispatch accepts none at all."""
    dispatch = _triggers(_workflow())["workflow_dispatch"] or {}
    assert not dispatch.get("inputs")


def test_invoking_the_workflow_is_not_authorization() -> None:
    """The first job verifies an authorization; it does not create one."""
    gate = _workflow()["jobs"]["builder-authorization"]
    commands = " ".join(str(step.get("run", "")) for step in _steps(gate))
    assert "builder_authorization" in commands
    assert BUILDER_AUTHORIZATION_PATH not in commands, (
        "the gate must not write the authorization document it checks"
    )


# -- the gate is mandatory and fail-closed ---------------------------------


@pytest.mark.parametrize("job_name", ARTIFACT_PRODUCING_JOBS)
def test_every_artifact_producing_job_depends_on_the_gate(job_name: str) -> None:
    """Transitively is enough: `reproducibility` needs the builds, which need
    the gate, so no artifact-producing job can run without it."""
    jobs = _workflow()["jobs"]
    resolved: set[str] = set()
    frontier = [job_name]
    while frontier:
        current = frontier.pop()
        for dependency in jobs[current].get("needs") or []:
            if dependency not in resolved:
                resolved.add(dependency)
                frontier.append(dependency)
    assert "builder-authorization" in resolved


def test_the_gate_job_itself_produces_no_artifact() -> None:
    gate = _workflow()["jobs"]["builder-authorization"]
    for step in _steps(gate):
        uses = str(step.get("uses", ""))
        run = str(step.get("run", ""))
        assert "build-push-action" not in uses
        assert "upload-artifact" not in uses
        assert "docker buildx build" not in run
        assert "build.sh" not in run


def test_the_gate_step_cannot_be_shrugged_off() -> None:
    """`continue-on-error` on the gate would make the refusal advisory."""
    gate = _workflow()["jobs"]["builder-authorization"]
    assert not gate.get("continue-on-error")
    for step in _steps(gate):
        assert not step.get("continue-on-error")
    for name in ARTIFACT_PRODUCING_JOBS:
        job = _workflow()["jobs"][name]
        assert not job.get("continue-on-error")
        assert not job.get("if"), (
            f"{name} carries an `if:` condition, which could let it run when "
            "the gate did not succeed"
        )


def test_no_override_input_or_flag_exists_anywhere() -> None:
    text = json.dumps(_workflow()).lower()
    for forbidden in (
        "allow_unauthorized",
        "skip_authorization",
        "force_build",
        "dev_mode",
        "bypass",
        "--force",
        "skip_env_check",
    ):
        assert forbidden not in text


def _run_gate(repository_root: Path) -> subprocess.CompletedProcess[str]:
    """The gate, as a subprocess, exactly as the workflow invokes it."""
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "cardiosentinel.journal_extension.j1.builder_authorization",
            "--repository-root",
            str(repository_root),
            "--running-workflow-ref",
            "owner/repo/.github/workflows/j1-environment-artifact-build.yml@x",
            "--running-commit",
            "0" * 40,
        ],
        capture_output=True,
        text=True,
        cwd=REPOSITORY_ROOT,
    )


def _require_reviewed_commit_readable() -> None:
    """Skip loudly where git cannot answer, rather than assert into a refusal.

    The gate reads the reviewed workflow bytes out of git's object store at
    `workflow_review_commit`. `ci.yml` checks out at the default depth, so that
    object is absent there and the gate refuses -- correctly, and fail-closed:
    it will not admit a workflow whose reviewed bytes it cannot see.

    That refusal is right, so this test must not treat it as a failure. The real
    controlled-build workflow sets `fetch-depth: 0` on the gate job for exactly
    this reason, which is where the admit path actually runs.
    """
    document = load_builder_authorization(REPOSITORY_ROOT)
    assert document is not None
    commit = str(document["workflow_review_commit"])
    probe = subprocess.run(
        ["git", "-C", str(REPOSITORY_ROOT), "cat-file", "-e", f"{commit}^{{commit}}"],
        capture_output=True,
        check=False,
    )
    if probe.returncode != 0:
        pytest.skip(
            f"the reviewed commit {commit} is not in this checkout's object "
            "store (shallow clone). The gate refuses without it, which is "
            "correct; the controlled-build workflow uses fetch-depth: 0."
        )


def test_the_gate_refuses_and_the_refusal_is_its_own() -> None:
    """`J1-ENV-BUILDER-AUTH-001` was retired, so the gate refuses again.

    The interesting assertion is the second one. Run 33800630377 also produced
    a non-zero exit and the words "builder authorization absent" on stderr --
    while the gate had in fact crashed during import, having verified nothing.
    An exit code alone cannot tell those two apart, so this requires the gate to
    have reached its own logic rather than died on the way there.
    """
    completed = _run_gate(REPOSITORY_ROOT)
    assert completed.returncode != 0
    assert "builder authorization absent" in completed.stderr
    assert "ModuleNotFoundError" not in completed.stderr, completed.stderr
    for package in ("numpy", "torch", "scipy", "sklearn"):
        assert f"No module named '{package}'" not in completed.stderr


def test_the_gate_still_fails_closed_without_an_authorization(
    tmp_path: Path,
) -> None:
    """Fail-closed is a property of the gate, not of this repository's state.

    Pointed at a tree carrying no authorization, the same gate refuses in the
    same words. An authorization existing here must not make the mechanism
    permissive anywhere else.
    """
    completed = _run_gate(tmp_path)
    assert completed.returncode != 0
    assert "builder authorization absent" in completed.stderr


# -- pins, runner, credentials ---------------------------------------------


def _all_uses() -> list[str]:
    return [
        str(step["uses"])
        for job in _workflow()["jobs"].values()
        for step in _steps(job)
        if "uses" in step
    ]


def test_every_action_is_pinned_by_commit_sha() -> None:
    for uses in _all_uses():
        _, _, ref = uses.rpartition("@")
        assert len(ref) == 40 and all(c in "0123456789abcdef" for c in ref), (
            f"{uses} is not pinned to an immutable commit"
        )


def test_the_runner_class_is_pinned() -> None:
    for name, job in _workflow()["jobs"].items():
        runner = job["runs-on"]
        assert not str(runner).endswith("-latest"), (
            f"{name} runs on {runner}, which is a moving target"
        )


def test_no_registry_credentials_or_push() -> None:
    """§23: no secrets, no login, no push. The artifact is an OCI archive."""
    text = json.dumps(_workflow())
    assert "secrets." not in text
    assert "docker/login-action" not in text
    assert "push: true" not in text
    for job in _workflow()["jobs"].values():
        for step in _steps(job):
            assert "docker push" not in str(step.get("run", ""))


def test_permissions_are_read_only() -> None:
    document = _workflow()
    assert document.get("permissions") == {"contents": "read"}


def test_no_automatic_retry_loop() -> None:
    """§20: nothing may rebuild until two artifacts happen to agree."""
    text = json.dumps(_workflow()).lower()
    for forbidden in ("retry", "until", "max-attempts", "nick-fields/retry"):
        assert forbidden not in text


# -- the future authorization schema ---------------------------------------


def test_no_builder_authorization_is_active() -> None:
    """`J1-ENV-BUILDER-AUTH-001` is retired, not spent.

    It was never spent -- its run failed before any qualification claim -- but
    it names a source commit that this remediation supersedes, and the source
    tree is image content. Leaving it active would let an accidental dispatch
    build the broken gate into the artifact.
    """
    assert not (REPOSITORY_ROOT / BUILDER_AUTHORIZATION_PATH).exists()
    assert load_builder_authorization(REPOSITORY_ROOT) is None


def test_an_absent_authorization_refuses_in_its_own_words() -> None:
    with pytest.raises(BuilderAuthorizationError, match="authorization absent"):
        verify_builder_authorization(None)


def test_the_schema_names_every_required_field() -> None:
    for field in (
        "builder_authorization_id",
        "workflow_review_commit",
        "workflow_sha256",
        "runner_class",
        "authorized_source_commit",
        "build_configuration_digest",
        "provenance_destination",
        "qualification_policy",
        "human_authorizer_identity",
    ):
        assert field in BUILDER_AUTHORIZATION_FIELDS
    assert len(BUILDER_AUTHORIZATION_FIELDS) == 22


# -- what a future authorization must survive ------------------------------


def _authorization(**overrides: object) -> dict[str, object]:
    """Entirely fabricated. Nothing here is written to disk."""
    from cardiosentinel.journal_extension.j1.approved_runtime import (
        APPROVED_DEPENDENCY_DIGEST,
    )
    from cardiosentinel.journal_extension.j1.qualification import (
        QUALIFICATION_POLICY,
        durable_evidence_destination,
    )

    document: dict[str, object] = {
        "builder_authorization_id": "SYNTHETIC-NOT-REAL",
        "builder_candidate_id": "github-actions:synthetic//wf.yml@" + "0" * 40,
        "provider": "github-actions",
        "repository": "DebalekhaChakraborty/CardioSentinel",
        "workflow_path": ".github/workflows/j1-environment-artifact-build.yml",
        "workflow_review_commit": "1" * 40,
        "workflow_sha256": "b" * 64,
        "runner_class": "ubuntu-24.04",
        "controlled_build_protocol_identity": "J1_CONTROLLED_BUILD_PROTOCOL_V1",
        "controlled_build_protocol_digest": "a" * 64,
        "source_repository": "DebalekhaChakraborty/CardioSentinel",
        "authorized_source_commit": "2" * 40,
        "target_platform": "linux/amd64",
        "artifact_type": "oci_single_platform_image_manifest",
        "base_image_digest": "python@sha256:" + "c" * 64,
        "dependency_authority_identity": "j1-approved-runtime-v1",
        "dependency_digest": APPROVED_DEPENDENCY_DIGEST,
        "build_configuration_digest": "d" * 64,
        # Derived from the id above, because the schema now refuses any other
        # value: the destination is a function of the authorization, not a
        # free-text field a fixture can invent.
        "provenance_destination": durable_evidence_destination("SYNTHETIC-NOT-REAL"),
        "qualification_policy": QUALIFICATION_POLICY,
        "authorization_timestamp": "2026-09-02T00:00:00Z",
        "human_authorizer_identity": "synthetic signatory",
    }
    document.update(overrides)
    return document


def test_a_complete_synthetic_authorization_verifies() -> None:
    verified = verify_builder_authorization(_authorization())
    assert verified.workflow_review_commit == "1" * 40
    assert verified.workflow_sha256 == "b" * 64


@pytest.mark.parametrize("field", BUILDER_AUTHORIZATION_FIELDS)
def test_every_authorization_field_is_required(field: str) -> None:
    document = _authorization()
    del document[field]
    with pytest.raises(BuilderAuthorizationError, match="incomplete"):
        verify_builder_authorization(document)


@pytest.mark.parametrize("value", ["PENDING", "TBD", "n/a", "*", "any", "latest"])
def test_no_field_may_be_left_to_be_filled_in_later(value: str) -> None:
    """A field completed after review is a field nobody reviewed."""
    with pytest.raises(BuilderAuthorizationError, match="placeholder"):
        verify_builder_authorization(_authorization(human_authorizer_identity=value))


@pytest.mark.parametrize(
    "field", ["workflow_review_commit", "authorized_source_commit"]
)
@pytest.mark.parametrize("value", ["main", "v1.0", "abc1234", "HEAD"])
def test_a_branch_where_a_commit_is_required_is_refused(
    field: str, value: str
) -> None:
    with pytest.raises(BuilderAuthorizationError, match="40-character commit"):
        verify_builder_authorization(_authorization(**{field: value}))


def test_a_generic_provider_cannot_be_authorized() -> None:
    with pytest.raises(BuilderAuthorizationError, match="names a provider"):
        verify_builder_authorization(_authorization(repository="GitHub Actions"))


def test_the_authorization_may_not_redefine_the_dependency_authority() -> None:
    with pytest.raises(BuilderAuthorizationError, match="not the approved one"):
        verify_builder_authorization(_authorization(dependency_digest="e" * 64))


def test_a_base_image_by_tag_is_refused() -> None:
    with pytest.raises(BuilderAuthorizationError, match="addressed by digest"):
        verify_builder_authorization(
            _authorization(base_image_digest="python:3.12.6-slim-bookworm")
        )


def test_an_unknown_field_is_refused() -> None:
    with pytest.raises(BuilderAuthorizationError, match="held to no rule"):
        verify_builder_authorization(_authorization(allow_unauthorized="true"))


def test_the_schema_no_longer_carries_an_unsatisfiable_commit_equality() -> None:
    """The previous rule required `github.sha == workflow_commit`.

    The authorization lives in the repository, so the commit that adds it is
    the commit the workflow then runs at, and the document would have had to
    contain the SHA of the commit containing itself. It could never be written.
    """
    assert "workflow_commit" not in BUILDER_AUTHORIZATION_FIELDS
    assert "workflow_review_commit" in BUILDER_AUTHORIZATION_FIELDS
    assert "workflow_sha256" in BUILDER_AUTHORIZATION_FIELDS


# -- the self-reference fix, exercised against real git history ------------


def _git(repo: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *arguments],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


@pytest.fixture
def reviewed_repository(tmp_path: Path) -> dict[str, Any]:
    """Commit A introduces the workflow; commit B adds the authorization.

    This is the ordinary case the previous rule made impossible: a human
    reviews a workflow, then signs an authorization in a *later* commit.
    """
    repo = tmp_path / "repo"
    workflow_relative = ".github/workflows/j1-environment-artifact-build.yml"
    (repo / ".github/workflows").mkdir(parents=True)
    repo_workflow = repo / workflow_relative
    repo_workflow.write_bytes(WORKFLOW_PATH.read_bytes())

    _git(repo.parent, "init", "-q", str(repo))
    _git(repo, "config", "user.email", "qualification@example.invalid")
    _git(repo, "config", "user.name", "qualification")
    _git(repo, "add", workflow_relative)
    _git(repo, "commit", "-q", "-m", "commit A: introduce the workflow")
    commit_a = _git(repo, "rev-parse", "HEAD")

    reviewed_digest = hashlib.sha256(repo_workflow.read_bytes()).hexdigest()

    (repo / "unrelated.txt").write_text("commit B changes something else\n")
    _git(repo, "add", "unrelated.txt")
    _git(repo, "commit", "-q", "-m", "commit B: add the authorization")
    commit_b = _git(repo, "rev-parse", "HEAD")

    return {
        "root": repo,
        "path": workflow_relative,
        "commit_a": commit_a,
        "commit_b": commit_b,
        "digest": reviewed_digest,
    }


def _authorization_for(fixture: dict[str, Any], **overrides: object):
    fields: dict[str, object] = {
        "workflow_path": fixture["path"],
        "workflow_review_commit": fixture["commit_a"],
        "workflow_sha256": fixture["digest"],
    }
    fields.update(overrides)
    return verify_builder_authorization(_authorization(**fields))


def test_an_authorization_may_live_in_a_later_commit(
    reviewed_repository: dict[str, Any],
) -> None:
    """Commit A holds the workflow, commit B holds the authorization, and the
    workflow bytes are unchanged. This must be able to pass."""
    proof = verify_workflow_identity(
        _authorization_for(reviewed_repository),
        repository_root=reviewed_repository["root"],
        running_workflow_ref=f"o/r/{reviewed_repository['path']}@refs/heads/x",
        running_commit=reviewed_repository["commit_b"],
    )
    assert proof["workflow_sha256_recomputed_from_review_commit"] == (
        reviewed_repository["digest"]
    )
    assert proof["workflow_sha256_recomputed_from_checkout"] == (
        reviewed_repository["digest"]
    )
    assert proof["running_commit_descends_from_review_commit"] == "verified"


def test_a_one_byte_workflow_change_after_authorization_refuses(
    reviewed_repository: dict[str, Any],
) -> None:
    """Commit C alters the workflow by a single byte."""
    repo = reviewed_repository["root"]
    workflow = repo / reviewed_repository["path"]
    workflow.write_bytes(workflow.read_bytes() + b" ")
    _git(repo, "add", reviewed_repository["path"])
    _git(repo, "commit", "-q", "-m", "commit C: one byte")

    with pytest.raises(
        CurrentWorkflowMismatchError, match="differs from the authorized"
    ):
        verify_workflow_identity(
            _authorization_for(reviewed_repository),
            repository_root=repo,
            running_commit=_git(repo, "rev-parse", "HEAD"),
        )


def test_a_declared_digest_is_not_evidence(
    reviewed_repository: dict[str, Any],
) -> None:
    """A valid-looking but wrong 64-hex digest must not create its own truth."""
    with pytest.raises(
        ReviewedWorkflowDriftError, match="never reviewed at that commit"
    ):
        verify_workflow_identity(
            _authorization_for(reviewed_repository, workflow_sha256="a" * 64),
            repository_root=reviewed_repository["root"],
        )


def test_a_wrong_historical_review_commit_refuses(
    reviewed_repository: dict[str, Any],
) -> None:
    """The named commit does not contain the authorized bytes at that path."""
    repo = reviewed_repository["root"]
    workflow = repo / reviewed_repository["path"]
    workflow.write_bytes(workflow.read_bytes() + b"# altered\n")
    _git(repo, "add", reviewed_repository["path"])
    _git(repo, "commit", "-q", "-m", "commit C: altered workflow")
    commit_c = _git(repo, "rev-parse", "HEAD")

    # The authorization names commit C as the review commit, but declares the
    # digest of the bytes as they were at commit A.
    with pytest.raises(ReviewedWorkflowDriftError, match="reviewed historical"):
        verify_workflow_identity(
            _authorization_for(reviewed_repository, workflow_review_commit=commit_c),
            repository_root=repo,
        )


def test_the_two_refusals_are_reported_separately(
    reviewed_repository: dict[str, Any],
) -> None:
    """Both refuse, but they mean different things and are different types."""
    assert issubclass(ReviewedWorkflowDriftError, BuilderAuthorizationError)
    assert issubclass(CurrentWorkflowMismatchError, BuilderAuthorizationError)
    assert not issubclass(ReviewedWorkflowDriftError, CurrentWorkflowMismatchError)
    assert not issubclass(CurrentWorkflowMismatchError, ReviewedWorkflowDriftError)


def test_the_digest_is_over_raw_bytes_not_a_parse_cycle(
    reviewed_repository: dict[str, Any],
) -> None:
    """A digest over re-rendered YAML would agree with a file nobody wrote."""
    repo = reviewed_repository["root"]
    raw = (repo / reviewed_repository["path"]).read_bytes()
    reparsed = yaml.safe_dump(yaml.safe_load(raw.decode("utf-8"))).encode("utf-8")
    assert hashlib.sha256(raw).hexdigest() == reviewed_repository["digest"]
    assert hashlib.sha256(reparsed).hexdigest() != reviewed_repository["digest"]


# -- build tool identities, kept separate ----------------------------------


def _buildx_step() -> dict[str, Any]:
    for job in _workflow()["jobs"].values():
        for step in _steps(job):
            if "setup-buildx-action" in str(step.get("uses", "")):
                return step
    raise AssertionError("no setup-buildx step found")


def test_the_buildx_binary_version_is_pinned() -> None:
    """Pinning the action pins the action, not the binary it installs."""
    version = _buildx_step()["with"]["version"]
    assert version == "v0.36.1"
    assert version not in ("latest", "stable", "current", "edge")


#: The frozen BuildKit authority: the linux/amd64 image manifest inside the
#: index below. Verified by recomputing SHA-256 over the raw manifest bytes.
BUILDKIT_AMD64_MANIFEST = (
    "sha256:040d34121c27906c4ff9ac152a30d52bf2c5d328d3bb748916bb3d2743c02528"
)
#: Provenance evidence only. Naming a list where the executable image belongs
#: would leave a platform-resolution step between authorization and execution.
BUILDKIT_MULTIPLATFORM_INDEX = (
    "sha256:28a898719c18a33f4e8000685287fa36fd0dd9560c6440227d3a732d79bb41d8"
)


def _buildx_steps() -> list[dict[str, Any]]:
    return [
        step
        for job in _workflow()["jobs"].values()
        for step in _steps(job)
        if "setup-buildx-action" in str(step.get("uses", ""))
    ]


def test_the_buildkit_daemon_image_is_pinned_by_digest() -> None:
    """The docker-container driver runs a daemon image; a tag would float."""
    options = _buildx_step()["with"]["driver-opts"]
    assert "moby/buildkit@sha256:" in options
    assert "buildx-stable-1" not in options
    assert "moby/buildkit:latest" not in options


def test_the_buildkit_authority_is_the_linux_amd64_manifest() -> None:
    """The builder is frozen to one platform, so the authority names the exact
    image that executes rather than a list needing a further resolution step."""
    for step in _buildx_steps():
        options = step["with"]["driver-opts"]
        assert f"image=moby/buildkit@{BUILDKIT_AMD64_MANIFEST}" in options


def test_the_index_digest_cannot_stand_in_for_the_platform_manifest() -> None:
    """Both are immutable and both are 64 hex, so a shape check would accept
    either. The index is provenance; only the manifest is the authority."""
    assert BUILDKIT_MULTIPLATFORM_INDEX != BUILDKIT_AMD64_MANIFEST
    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert BUILDKIT_MULTIPLATFORM_INDEX not in workflow_text, (
        "the multi-platform index digest appears in the workflow, where only "
        "the linux/amd64 manifest may be the executable BuildKit authority"
    )
    assert BUILDKIT_AMD64_MANIFEST in workflow_text


def test_both_builds_use_identical_tool_identities() -> None:
    """BUILD_A and BUILD_B differ only in which run they happen in. A tool that
    differed between them would make a digest comparison meaningless."""
    steps = _buildx_steps()
    assert len(steps) == 2
    first, second = steps
    assert first["uses"] == second["uses"]
    assert first["with"]["version"] == second["with"]["version"]
    assert first["with"]["driver"] == second["with"]["driver"] == "docker-container"
    assert first["with"]["driver-opts"] == second["with"]["driver-opts"]

    jobs = _workflow()["jobs"]
    assert jobs["build-a"]["runs-on"] == jobs["build-b"]["runs-on"]


def test_the_four_tool_identities_are_not_collapsed() -> None:
    """Action commit, Buildx version, BuildKit digest and runner class are
    four separate things; "Docker version" is none of them."""
    step = _buildx_step()
    action_sha = str(step["uses"]).rpartition("@")[2]
    assert len(action_sha) == 40
    assert step["with"]["version"]
    assert "sha256:" in step["with"]["driver-opts"]
    assert _workflow()["jobs"]["build-a"]["runs-on"] == "ubuntu-24.04"


def test_the_gate_checks_out_enough_history_to_read_the_review_commit() -> None:
    gate = _workflow()["jobs"]["builder-authorization"]
    checkout = next(s for s in _steps(gate) if "checkout" in str(s.get("uses", "")))
    assert checkout["with"]["fetch-depth"] == 0
