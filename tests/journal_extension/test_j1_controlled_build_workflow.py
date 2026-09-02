"""Governance of the inert controlled-build workflow.

**No image is built, no artifact digest is produced, no builder is authorized,
no environment record exists, and no scientific data is touched.** These tests
prove the workflow is complete *and* cannot start.

The checks parse the workflow semantically rather than grepping it. A grep for
`on: push` misses `on: {push: {branches: [main]}}`, and a grep for `needs`
cannot tell which job it belongs to.
"""

from __future__ import annotations

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
    load_builder_authorization,
    verify_builder_authorization,
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


def test_the_gate_refuses_right_now() -> None:
    """End to end, as a subprocess, exactly as the workflow invokes it."""
    assert not (REPOSITORY_ROOT / BUILDER_AUTHORIZATION_PATH).exists()
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "cardiosentinel.journal_extension.j1.builder_authorization",
            "--repository-root",
            str(REPOSITORY_ROOT),
            "--running-workflow-ref",
            "owner/repo/.github/workflows/j1-environment-artifact-build.yml@x",
            "--running-commit",
            "0" * 40,
        ],
        capture_output=True,
        text=True,
        cwd=REPOSITORY_ROOT,
    )
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


def test_no_builder_authorization_exists() -> None:
    assert load_builder_authorization(REPOSITORY_ROOT) is None


def test_an_absent_authorization_refuses_in_its_own_words() -> None:
    with pytest.raises(BuilderAuthorizationError, match="authorization absent"):
        verify_builder_authorization(None)


def test_the_schema_names_every_required_field() -> None:
    for field in (
        "builder_authorization_id",
        "workflow_commit",
        "runner_class",
        "authorized_source_commit",
        "build_configuration_digest",
        "human_authorizer_identity",
    ):
        assert field in BUILDER_AUTHORIZATION_FIELDS
    assert len(BUILDER_AUTHORIZATION_FIELDS) == 20


# -- what a future authorization must survive ------------------------------


def _authorization(**overrides: object) -> dict[str, object]:
    """Entirely fabricated. Nothing here is written to disk."""
    from cardiosentinel.journal_extension.j1.approved_runtime import (
        APPROVED_DEPENDENCY_DIGEST,
    )

    document: dict[str, object] = {
        "builder_authorization_id": "SYNTHETIC-NOT-REAL",
        "builder_candidate_id": "github-actions:synthetic//wf.yml@" + "0" * 40,
        "provider": "github-actions",
        "repository": "DebalekhaChakraborty/CardioSentinel",
        "workflow_path": ".github/workflows/j1-environment-artifact-build.yml",
        "workflow_commit": "1" * 40,
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
        "provenance_destination": "s3://synthetic-provenance/j1/",
        "authorization_timestamp": "2026-09-02T00:00:00Z",
        "human_authorizer_identity": "synthetic signatory",
    }
    document.update(overrides)
    return document


def test_a_complete_synthetic_authorization_verifies() -> None:
    verified = verify_builder_authorization(_authorization())
    assert verified.workflow_commit == "1" * 40


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


@pytest.mark.parametrize("field", ["workflow_commit", "authorized_source_commit"])
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


def test_a_workflow_running_at_an_unnamed_commit_is_refused() -> None:
    """The self-reference resolved from the other direction: the workflow says
    what it is running as, and the authorization must already name it."""
    from cardiosentinel.journal_extension.j1.builder_authorization import (
        require_running_identity_is_authorized,
    )

    verified = verify_builder_authorization(_authorization())
    with pytest.raises(BuilderAuthorizationError, match="no human authorized"):
        require_running_identity_is_authorized(
            verified,
            running_workflow_ref=(
                "o/r/.github/workflows/j1-environment-artifact-build.yml@refs/x"
            ),
            running_commit="9" * 40,
        )


def test_a_different_workflow_at_the_right_commit_is_refused() -> None:
    from cardiosentinel.journal_extension.j1.builder_authorization import (
        require_running_identity_is_authorized,
    )

    verified = verify_builder_authorization(_authorization())
    with pytest.raises(BuilderAuthorizationError, match="not the one that was"):
        require_running_identity_is_authorized(
            verified,
            running_workflow_ref="o/r/.github/workflows/ci.yml@refs/heads/master",
            running_commit="1" * 40,
        )


# -- the build inputs must actually be in the repository -------------------


BUILD_CONFIGURATION_SOURCES = (
    "containers/j1-environment/Containerfile",
    "containers/j1-environment/build.sh",
    "containers/j1-environment/validate_artifact.sh",
    ".github/workflows/j1-environment-artifact-build.yml",
)


@pytest.mark.parametrize("relative", BUILD_CONFIGURATION_SOURCES)
def test_every_build_input_is_tracked_by_git(relative: str) -> None:
    """These files were first written under `build/`, which `.gitignore`
    excludes as a Python packaging convention. They existed on disk, every
    local test passed, and none of them would have reached the repository --
    the same shape as the `docs/paper/` failure that kept master red for
    eighteen hours. Presence on disk is not membership of the build.
    """
    assert (REPOSITORY_ROOT / relative).is_file()
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", relative],
        capture_output=True,
        text=True,
        cwd=REPOSITORY_ROOT,
    )
    ignored = subprocess.run(
        ["git", "check-ignore", relative],
        capture_output=True,
        text=True,
        cwd=REPOSITORY_ROOT,
    )
    assert ignored.returncode != 0, f"{relative} is gitignored"
    assert tracked.returncode == 0, f"{relative} is not tracked by git"


def test_the_generated_dependency_input_is_not_tracked() -> None:
    """Its generator and the proof it equals the frozen authority are tracked;
    its output is not, so a stale copy cannot be mistaken for the authority."""
    ignored = subprocess.run(
        ["git", "check-ignore", "containers/j1-environment/requirements.pypi.txt"],
        capture_output=True,
        text=True,
        cwd=REPOSITORY_ROOT,
    )
    assert ignored.returncode == 0


def test_the_workflow_references_only_tracked_build_inputs() -> None:
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "build/j1-environment" not in text, (
        "the workflow points at the gitignored build/ path"
    )
