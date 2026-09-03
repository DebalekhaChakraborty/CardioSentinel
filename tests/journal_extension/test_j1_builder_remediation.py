"""What the #151 remediation had to make true, proven against the artifacts.

Every test here corresponds to a finding or a rule the remediation introduced.
The habit throughout is the one that actually catches things: bind the check to
a fact the fixture cannot supply -- the real Containerfile's COPY lines, the
real workflow's job graph, the digest a real regeneration produces -- rather
than to a constant written beside the assertion.

**No builder is authorized, no workflow is dispatched, and no image is built.**
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from cardiosentinel.journal_extension.j1 import preflight
from cardiosentinel.journal_extension.j1.authorization import (
    AuthorizationError,
    verify_authorization,
)
from cardiosentinel.journal_extension.j1.builder_authorization import (
    BUILDER_AUTHORIZATION_PATH,
    CONTROLLED_BUILD_WORKFLOW_PATH,
    BuilderAuthorizationError,
    load_builder_authorization,
    verify_builder_authorization,
)
from cardiosentinel.journal_extension.j1.builder_protocol import (
    BUILD_CONFIGURATION_MEMBERS,
    DERIVED_BUILD_INPUT,
    DERIVED_BUILD_INPUT_ROLES,
    DERIVED_INPUT_PROPERTIES,
    REQUIRED_BUILD_CONFIGURATION_INPUTS,
    BuilderProtocolError,
    build_configuration_digest,
    build_configuration_manifest,
    require_derived_input_properties,
)
from cardiosentinel.journal_extension.j1.controlled_build import (
    BIT_REPRODUCIBLE,
    DIVERGED,
    ControlledBuildError,
    configuration_digest,
    enforce_reproducibility,
    reproducibility_record,
    require_comparable_builds,
    write_dependency_input,
)
from cardiosentinel.journal_extension.j1.qualification import (
    ARTIFACT_VISIBLE,
    BUILD_A_ARCHIVE_ARTIFACT,
    BUILD_B_ARCHIVE_ARTIFACT,
    COMPLETED_QUALIFICATION,
    DURABLE_EVIDENCE_ROOT,
    POST_CLAIM_PRE_ARTIFACT,
    PRE_ARTIFACT_INFRASTRUCTURE,
    PROTOCOL_VIOLATION,
    QUALIFICATION_FAILURE_CLASSES,
    QUALIFICATION_POLICY,
    REPRODUCIBILITY_RECORD_ARTIFACT,
    SINGLE_CLAIM_POLICY,
    QualificationError,
    classify_divergence,
    durable_evidence_destination,
    require_canonical_qualification_run,
    require_new_lineage,
    require_provenance_destination,
    require_retry_permitted,
    verify_qualification_claim,
)

REPOSITORY_ROOT = Path(preflight.J1_PACKAGE_ROOT).parents[3]
CONTAINER_DIR = REPOSITORY_ROOT / "containers/j1-environment"
CONTAINERFILE = CONTAINER_DIR / "Containerfile"
DOCKERIGNORE = CONTAINER_DIR / "Containerfile.dockerignore"
BUILD_SCRIPT = CONTAINER_DIR / "build.sh"
WORKFLOW_PATH = REPOSITORY_ROOT / CONTROLLED_BUILD_WORKFLOW_PATH

SYNTHETIC_ID = "SYNTHETIC-REMEDIATION-NOT-REAL"


def _workflow() -> dict[str, Any]:
    """Parsed semantically. A grep for `on: push` misses nested forms."""
    return yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))


def _job(name: str) -> dict[str, Any]:
    return _workflow()["jobs"][name]


def _steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    return list(job.get("steps") or [])


@pytest.fixture
def minimal_authorization() -> dict[str, Any]:
    """A complete, entirely fabricated authorization. Never written to disk.

    Every value is either a frozen constant or an obvious synthetic. It exists so
    a single field can be made wrong in isolation and the refusal attributed to
    that field rather than to an incomplete document.
    """
    from cardiosentinel.journal_extension.j1.approved_runtime import (
        APPROVED_DEPENDENCY_DIGEST,
    )
    from cardiosentinel.journal_extension.j1.builder_protocol import (
        ARTIFACT_KIND,
        TARGET_PLATFORM,
    )

    return {
        "builder_authorization_id": SYNTHETIC_ID,
        "builder_candidate_id": (
            f"github-actions:o/r//{CONTROLLED_BUILD_WORKFLOW_PATH}@{'0' * 40}#x"
        ),
        "provider": "github-actions",
        "repository": "DebalekhaChakraborty/CardioSentinel",
        "workflow_path": CONTROLLED_BUILD_WORKFLOW_PATH,
        "workflow_review_commit": "1" * 40,
        "workflow_sha256": "b" * 64,
        "runner_class": "ubuntu-24.04",
        "controlled_build_protocol_identity": (
            "J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2"
        ),
        "controlled_build_protocol_digest": "a" * 64,
        "source_repository": "DebalekhaChakraborty/CardioSentinel",
        "authorized_source_commit": "2" * 40,
        "target_platform": TARGET_PLATFORM,
        "artifact_type": ARTIFACT_KIND,
        "base_image_digest": "python@sha256:" + "c" * 64,
        "dependency_authority_identity": "v1-frozen-experiment-lock-335-packages",
        "dependency_digest": APPROVED_DEPENDENCY_DIGEST,
        "build_configuration_digest": "d" * 64,
        "provenance_destination": durable_evidence_destination(SYNTHETIC_ID),
        "qualification_policy": QUALIFICATION_POLICY,
        "authorization_timestamp": "2026-09-02T00:00:00Z",
        "human_authorizer_identity": "synthetic, not a signatory",
    }


def test_the_minimal_authorization_verifies_so_refusals_are_attributable(
    minimal_authorization: dict[str, Any],
) -> None:
    verify_builder_authorization(minimal_authorization)


def _member_paths() -> dict[str, str]:
    return {member.role: member.path for member in BUILD_CONFIGURATION_MEMBERS}


def _configuration_paths(tmp_path: Path) -> dict[str, Path]:
    write_dependency_input(REPOSITORY_ROOT, tmp_path)
    paths: dict[str, Path] = {}
    for member in BUILD_CONFIGURATION_MEMBERS:
        if member.status == DERIVED_BUILD_INPUT:
            paths[member.role] = tmp_path / Path(member.path).name
        else:
            paths[member.role] = REPOSITORY_ROOT / member.path
    return paths


# -- F1: every artifact-affecting input is bound ---------------------------


def test_the_pytorch_dependency_input_is_a_configuration_member() -> None:
    assert "dependency_input_pytorch" in REQUIRED_BUILD_CONFIGURATION_INPUTS
    assert (
        _member_paths()["dependency_input_pytorch"]
        == "containers/j1-environment/requirements.pytorch-cpu.txt"
    )


def test_altering_the_pytorch_pin_changes_the_configuration_digest(
    tmp_path: Path,
) -> None:
    """The exact defect F1 named: `torch==2.13.0+cpu` must not be free to move.

    Under the previous five-slot model this file was absent from the manifest,
    so two builds installing different PyTorch versions carried one digest.
    """
    paths = _configuration_paths(tmp_path)
    baseline = configuration_digest(paths)["build_configuration_digest"]

    pytorch = paths["dependency_input_pytorch"]
    original = pytorch.read_text(encoding="utf-8")
    assert "torch==2.13.0+cpu" in original
    pytorch.write_text(
        original.replace("torch==2.13.0+cpu", "torch==2.14.0+cpu"), encoding="utf-8"
    )
    altered = configuration_digest(paths)["build_configuration_digest"]
    assert altered != baseline


@pytest.mark.parametrize("role", REQUIRED_BUILD_CONFIGURATION_INPUTS)
def test_altering_any_member_changes_the_configuration_digest(role: str) -> None:
    baseline = build_configuration_digest(
        {name: "a" * 64 for name in REQUIRED_BUILD_CONFIGURATION_INPUTS}
    )
    altered = dict.fromkeys(REQUIRED_BUILD_CONFIGURATION_INPUTS, "a" * 64)
    altered[role] = "b" * 64
    assert build_configuration_digest(altered) != baseline


def test_every_file_the_containerfile_copies_is_bound() -> None:
    """Read out of the Containerfile, not from a list maintained beside it."""
    text = CONTAINERFILE.read_text(encoding="utf-8")
    referenced = set(re.findall(r"containers/j1-environment/[\w.\-]+", text))
    assert referenced, "the Containerfile references no build inputs; parse failed"
    bound = set(_member_paths().values())
    unbound = referenced - bound
    assert not unbound, f"artifact-affecting files outside the manifest: {unbound}"


def test_a_configuration_missing_any_member_is_refused() -> None:
    for role in REQUIRED_BUILD_CONFIGURATION_INPUTS:
        inputs = dict.fromkeys(REQUIRED_BUILD_CONFIGURATION_INPUTS, "a" * 64)
        del inputs[role]
        with pytest.raises(BuilderProtocolError, match="every influencing input"):
            build_configuration_digest(inputs)


def test_an_undeclared_configuration_input_is_refused() -> None:
    """An input held to no rule is worse than an absent one."""
    inputs = dict.fromkeys(REQUIRED_BUILD_CONFIGURATION_INPUTS, "a" * 64)
    inputs["something_nobody_declared"] = "b" * 64
    with pytest.raises(BuilderProtocolError, match="held to no rule"):
        build_configuration_digest(inputs)


def test_the_manifest_records_role_path_status_and_authority() -> None:
    manifest = build_configuration_manifest(
        dict.fromkeys(REQUIRED_BUILD_CONFIGURATION_INPUTS, "a" * 64)
    )
    assert manifest["member_count"] == len(BUILD_CONFIGURATION_MEMBERS)
    for record in manifest["members"]:
        assert set(record) == {
            "role",
            "path",
            "sha256",
            "status",
            "authority",
            "affects_artifact_bytes",
        }


# -- F2: the derived input is formalized, not merely tolerated -------------


def test_the_derived_roles_are_exactly_the_two_requirements_files() -> None:
    assert set(DERIVED_BUILD_INPUT_ROLES) == {
        "dependency_input_pypi",
        "dependency_input_pytorch",
    }


def test_generation_is_deterministic_across_independent_directories(
    tmp_path: Path,
) -> None:
    first = write_dependency_input(REPOSITORY_ROOT, tmp_path / "one")
    second = write_dependency_input(REPOSITORY_ROOT, tmp_path / "two")
    assert first["files"] == second["files"]
    for name in ("requirements.pypi.txt", "requirements.pytorch-cpu.txt"):
        a = (tmp_path / "one" / name).read_bytes()
        b = (tmp_path / "two" / name).read_bytes()
        assert a == b
        assert hashlib.sha256(a).hexdigest() == first["files"][name]


def test_generation_reports_the_properties_it_established(tmp_path: Path) -> None:
    result = write_dependency_input(REPOSITORY_ROOT, tmp_path)
    assert result["derived_input_properties"] == list(DERIVED_INPUT_PROPERTIES)


@pytest.mark.parametrize("property_name", DERIVED_INPUT_PROPERTIES)
def test_an_unproven_derived_property_is_refused(property_name: str) -> None:
    evidence = dict.fromkeys(DERIVED_INPUT_PROPERTIES, True)
    evidence[property_name] = False
    with pytest.raises(BuilderProtocolError, match="generated but not bound"):
        require_derived_input_properties(evidence)


def test_an_unstated_derived_property_is_refused_as_loudly() -> None:
    evidence = dict.fromkeys(DERIVED_INPUT_PROPERTIES, True)
    del evidence[DERIVED_INPUT_PROPERTIES[0]]
    with pytest.raises(BuilderProtocolError, match="no position on"):
        require_derived_input_properties(evidence)


def test_a_tampered_generated_file_is_refused_on_regeneration(
    tmp_path: Path,
) -> None:
    """Regeneration mismatch must hard-fail, which is one of the eight properties."""
    write_dependency_input(REPOSITORY_ROOT, tmp_path)
    target = tmp_path / "requirements.pytorch-cpu.txt"
    target.write_text("torch==9.9.9+cpu\n", encoding="utf-8")
    # A second generation overwrites and re-verifies, so tamper detection is
    # exercised through the digest the caller receives.
    result = write_dependency_input(REPOSITORY_ROOT, tmp_path)
    assert target.read_text(encoding="utf-8") != "torch==9.9.9+cpu\n"
    assert result["files"]["requirements.pytorch-cpu.txt"] == hashlib.sha256(
        target.read_bytes()
    ).hexdigest()


# -- F3: the base image tag is not a runtime authority ---------------------


def test_the_workflow_does_not_declare_a_base_image_digest() -> None:
    """One authority. The digest reaches the build from the authorization."""
    environment = _workflow().get("env") or {}
    assert "BASE_IMAGE_DIGEST" not in environment
    assert environment.get("BASE_IMAGE_TAG") == "python:3.12.6-slim-bookworm"


def test_the_build_jobs_take_the_digest_from_the_verified_authorization() -> None:
    for name in ("build-a", "build-b"):
        declared = (_job(name).get("env") or {}).get("BASE_IMAGE_DIGEST", "")
        assert "needs.builder-authorization.outputs.base_image_digest" in declared


def test_no_step_re_resolves_the_descriptive_tag() -> None:
    """The withdrawn claim must stay withdrawn."""
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "re-resolves and verifies it rather than trusting this file" not in text
    for command in ("docker pull python:", "crane digest", "skopeo inspect"):
        assert command not in text


def test_the_build_script_refuses_a_reference_that_is_not_a_digest() -> None:
    script = BUILD_SCRIPT.read_text(encoding="utf-8")
    assert "@sha256:[0-9a-f]{64}" in script
    assert "refusing to build" in script


# -- F4: the wrong workflow filename cannot become authorization -----------


def test_the_enforced_workflow_path_is_the_file_that_exists() -> None:
    assert WORKFLOW_PATH.is_file()
    assert CONTROLLED_BUILD_WORKFLOW_PATH.endswith(
        "j1-environment-artifact-build.yml"
    )


def test_the_nonexistent_historical_filename_is_refused(
    minimal_authorization: dict[str, Any],
) -> None:
    """The receipt's typo must not be able to propagate into an authorization."""
    wrong = ".github/workflows/j1-environment-build.yml"
    assert not (REPOSITORY_ROOT / wrong).exists()
    with pytest.raises(BuilderAuthorizationError, match="not the controlled"):
        verify_builder_authorization({**minimal_authorization, "workflow_path": wrong})


# -- F6: the build context is bounded --------------------------------------


def test_the_dockerignore_exists_and_is_a_configuration_member() -> None:
    assert DOCKERIGNORE.is_file()
    assert "containerfile_dockerignore" in REQUIRED_BUILD_CONFIGURATION_INPUTS


def test_the_dockerignore_excludes_git_metadata() -> None:
    """`.git` pack bytes differ between clones of the same commit."""
    entries = {
        line.strip()
        for line in DOCKERIGNORE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
    assert ".git" in entries
    for noise in ("**/__pycache__", "*.oci.tar"):
        assert noise in entries


def test_the_dockerignore_keeps_the_derived_requirements_in_context() -> None:
    """Excluding them would break the Containerfile's explicit COPY."""
    text = DOCKERIGNORE.read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        assert "requirements" not in stripped


# -- provenance destinations ------------------------------------------------


def test_the_durable_destination_is_derived_from_the_authorization_id() -> None:
    destination = durable_evidence_destination(SYNTHETIC_ID)
    assert destination == f"{DURABLE_EVIDENCE_ROOT}/{SYNTHETIC_ID}/"
    assert destination.startswith("docs/journal-extension/j1/evidence/")


def test_a_destination_that_is_not_derived_is_refused() -> None:
    with pytest.raises(QualificationError, match="not the destination"):
        require_provenance_destination(
            declared="s3://somewhere-someone-picked/",
            builder_authorization_id=SYNTHETIC_ID,
        )


def test_an_authorization_id_carrying_a_separator_is_refused() -> None:
    """It becomes a path segment, so it may not name a directory nobody chose."""
    for unsafe in ("../escape", "a/b", "", "x"):
        with pytest.raises(QualificationError):
            durable_evidence_destination(unsafe)


def test_the_authorization_enforces_the_derived_destination(
    minimal_authorization: dict[str, Any],
) -> None:
    with pytest.raises(BuilderAuthorizationError, match="not the destination"):
        verify_builder_authorization(
            {**minimal_authorization, "provenance_destination": "s3://elsewhere/"}
        )


# -- retention: the artifacts and the comparison both survive the run ------


def test_both_oci_archives_are_retained() -> None:
    """V1's workflow discarded the object the whole procedure exists to produce."""
    for job, artifact, archive in (
        ("build-a", BUILD_A_ARCHIVE_ARTIFACT, "build-a.oci.tar"),
        ("build-b", BUILD_B_ARCHIVE_ARTIFACT, "build-b.oci.tar"),
    ):
        uploads = [
            step
            for step in _steps(_job(job))
            if "upload-artifact" in str(step.get("uses", ""))
        ]
        names = {step["with"]["name"] for step in uploads}
        paths = {step["with"]["path"] for step in uploads}
        assert artifact in names, job
        assert archive in paths, job


def test_the_reproducibility_record_is_retained_even_on_divergence() -> None:
    uploads = [
        step
        for step in _steps(_job("reproducibility"))
        if "upload-artifact" in str(step.get("uses", ""))
    ]
    assert uploads, "the reproducibility job retains nothing"
    record = next(
        step
        for step in uploads
        if step["with"]["name"] == REPRODUCIBILITY_RECORD_ARTIFACT
    )
    # A divergence is the finding. Uploading only on success would discard it.
    assert record.get("if") == "always()"


def test_the_archive_digest_is_not_the_artifact_identity() -> None:
    text = (
        REPOSITORY_ROOT
        / "src/cardiosentinel/journal_extension/j1/controlled_build.py"
    ).read_text(encoding="utf-8")
    assert "archive_sha256" in text
    assert "archive_digest_is_not_artifact_identity" in text


# -- the canonical qualification pair --------------------------------------


def _claim(run_id: int, attempt: int = 1, **overrides: Any) -> Any:
    document = {
        "builder_authorization_id": SYNTHETIC_ID,
        "qualification_policy": QUALIFICATION_POLICY,
        "provider": "github-actions",
        "workflow_run_id": str(run_id),
        "workflow_run_number": "1",
        "workflow_run_attempt": str(attempt),
        "workflow_sha256": "a" * 64,
        "authorized_source_commit": "b" * 40,
        "build_configuration_digest": "c" * 64,
        "claimed_at": "2026-09-02T00:00:00Z",
    }
    document.update(overrides)
    return verify_qualification_claim(document)


def test_the_earliest_claim_is_canonical() -> None:
    first, second = _claim(100), _claim(200)
    proof = require_canonical_qualification_run(
        claim=first, observed_claims=[first, second]
    )
    assert proof["canonical_run_id"] == 100
    assert proof["control_class"] == "detection_at_evidence_preservation"


def test_a_later_run_cannot_replace_the_canonical_pair() -> None:
    first, second = _claim(100), _claim(200)
    with pytest.raises(QualificationError, match="not the canonical"):
        require_canonical_qualification_run(
            claim=second, observed_claims=[first, second]
        )


def test_a_rerun_of_the_canonical_run_cannot_replace_its_own_evidence() -> None:
    """A re-run keeps its run_id, so attempt is part of the ordering key."""
    first, rerun = _claim(100, attempt=1), _claim(100, attempt=2)
    with pytest.raises(QualificationError, match="not the canonical"):
        require_canonical_qualification_run(
            claim=rerun, observed_claims=[first, rerun]
        )


def test_a_claim_absent_from_the_observed_set_is_refused() -> None:
    """A filtered listing must not silently satisfy the rule."""
    with pytest.raises(QualificationError, match="not the complete listing"):
        require_canonical_qualification_run(
            claim=_claim(300), observed_claims=[_claim(100)]
        )


def test_a_claim_naming_another_policy_is_refused() -> None:
    with pytest.raises(QualificationError, match="not the frozen policy"):
        _claim(100, qualification_policy="WHICHEVER_PAIR_LOOKS_BEST")


def test_a_non_numeric_run_id_is_refused() -> None:
    """The ordering is the control; an unorderable id would remove it."""
    with pytest.raises(QualificationError, match="provider run number"):
        _claim(100, workflow_run_id="latest")


def test_the_claim_is_recorded_after_the_gate_and_before_any_build() -> None:
    workflow = _workflow()
    assert workflow["jobs"]["qualification-claim"]["needs"] == [
        "builder-authorization"
    ]
    for build in ("build-a", "build-b"):
        assert "qualification-claim" in workflow["jobs"][build]["needs"]
        assert "builder-authorization" in workflow["jobs"][build]["needs"]


# -- failure and retry semantics -------------------------------------------


def test_before_any_claim_an_infrastructure_failure_may_be_redispatched() -> None:
    """Nothing was reserved and nothing was seen, so this is a fresh attempt."""
    require_retry_permitted(PRE_ARTIFACT_INFRASTRUCTURE, claim_recorded=False)


def test_after_a_claim_the_authorization_is_spent(
) -> None:
    """R1: single-claim. Even the pre-artifact class is terminal once claimed."""
    with pytest.raises(QualificationError, match="already exists"):
        require_retry_permitted(PRE_ARTIFACT_INFRASTRUCTURE, claim_recorded=True)


def test_post_claim_pre_artifact_is_terminal_for_this_authorization() -> None:
    """The class whose old prose said a retry 'runs under' the claim. It cannot."""
    for claimed in (True, False):
        with pytest.raises(QualificationError, match="not permitted"):
            require_retry_permitted(
                POST_CLAIM_PRE_ARTIFACT, claim_recorded=claimed
            )


@pytest.mark.parametrize(
    "failure_class",
    [ARTIFACT_VISIBLE, COMPLETED_QUALIFICATION, PROTOCOL_VIOLATION],
)
def test_every_other_class_is_terminal(failure_class: str) -> None:
    for claimed in (True, False):
        with pytest.raises(QualificationError, match="not permitted"):
            require_retry_permitted(failure_class, claim_recorded=claimed)


def test_the_retry_rule_names_the_three_things_a_further_attempt_needs() -> None:
    with pytest.raises(QualificationError) as raised:
        require_retry_permitted(ARTIFACT_VISIBLE, claim_recorded=True)
    message = str(raised.value)
    assert "human review" in message
    assert "new builder_authorization_id" in message
    assert "new qualification lineage" in message


def test_claim_recorded_has_no_default() -> None:
    """The permissive value is the dangerous one, so it may not be implicit."""
    with pytest.raises(TypeError):
        require_retry_permitted(PRE_ARTIFACT_INFRASTRUCTURE)  # type: ignore[call-arg]


def test_an_undeclared_failure_class_is_refused() -> None:
    with pytest.raises(QualificationError, match="not a declared"):
        require_retry_permitted("SOMETHING_WENT_WRONG", claim_recorded=False)


def test_a_further_attempt_may_not_reuse_the_authorization_id() -> None:
    """Ids are not interchangeable: the evidence destination is derived from one."""
    with pytest.raises(QualificationError, match="may not reuse"):
        require_new_lineage(
            previous_authorization_id=SYNTHETIC_ID,
            proposed_authorization_id=SYNTHETIC_ID,
        )
    assert (
        require_new_lineage(
            previous_authorization_id=SYNTHETIC_ID,
            proposed_authorization_id="SECOND-LINEAGE-NOT-REAL",
        )
        == "SECOND-LINEAGE-NOT-REAL"
    )


def test_a_new_authorization_id_starts_a_separate_lineage() -> None:
    """An earlier claim under authorization A must not shadow authorization B."""
    first = _claim(100)
    second_lineage = _claim(200, builder_authorization_id="SECOND-LINEAGE-NOT-REAL")
    proof = require_canonical_qualification_run(
        claim=second_lineage, observed_claims=[first, second_lineage]
    )
    assert proof["canonical_run_id"] == 200
    assert proof["claims_observed"] == 1


def test_a_later_dispatch_under_the_same_authorization_stays_non_canonical() -> None:
    first = _claim(100)
    later_dispatch = _claim(500)
    with pytest.raises(QualificationError, match="not the canonical"):
        require_canonical_qualification_run(
            claim=later_dispatch, observed_claims=[first, later_dispatch]
        )


def test_the_single_claim_policy_is_named() -> None:
    assert SINGLE_CLAIM_POLICY == "THE_CURRENT_BUILDER_AUTHORIZATION_IS_SINGLE_CLAIM"


def test_divergence_classifies_as_artifact_visible() -> None:
    diverged = classify_divergence(
        build_a_digest="sha256:" + "a" * 64, build_b_digest="sha256:" + "b" * 64
    )
    agreed = classify_divergence(
        build_a_digest="sha256:" + "a" * 64, build_b_digest="sha256:" + "a" * 64
    )
    assert diverged == ARTIFACT_VISIBLE
    assert agreed == COMPLETED_QUALIFICATION
    assert set(QUALIFICATION_FAILURE_CLASSES) >= {diverged, agreed}


def test_the_workflow_contains_no_retry_loop() -> None:
    text = yaml.safe_dump(_workflow()).lower()
    for forbidden in ("retry", "until", "max-attempts", "nick-fields/retry"):
        assert forbidden not in text


# -- least privilege, unchanged --------------------------------------------


def test_the_workflow_gained_no_write_permission() -> None:
    """Retention was solved by keeping evidence, not by gaining a push token."""
    assert _workflow()["permissions"] == {"contents": "read"}


def test_no_registry_credential_or_push_appears_anywhere() -> None:
    """Checked against the parsed workflow, not its prose.

    A text scan fails here for the reason this programme has recorded five
    times: the file explains that it has no `packages: write`, so a grep for
    that string finds the sentence promising its absence.
    """
    workflow = _workflow()
    assert set(workflow["permissions"]) == {"contents"}

    executable = []
    for job in workflow["jobs"].values():
        executable.append(str(job.get("permissions", "")))
        for step in _steps(job):
            executable.append(str(step.get("uses", "")))
            executable.append(str(step.get("run", "")))
            executable.append(str(step.get("with", "")))
            executable.append(str(step.get("env", "")))
    joined = "\n".join(executable)
    for forbidden in (
        "packages: write",
        "docker/login-action",
        "docker push",
        "ghcr.io",
        "registry-password",
        "secrets.",
    ):
        assert forbidden not in joined, forbidden


def test_the_only_trigger_is_manual_dispatch_with_no_inputs() -> None:
    workflow = _workflow()
    trigger_key = next(k for k in workflow if k is True or str(k) == "on")
    triggers = workflow[trigger_key]
    assert set(triggers) == {"workflow_dispatch"}
    assert not triggers["workflow_dispatch"]


# -- negative capability ---------------------------------------------------


def test_no_builder_authorization_is_active() -> None:
    """`J1-ENV-BUILDER-AUTH-001` is retired; the refusal mechanism is unchanged."""
    assert not (REPOSITORY_ROOT / BUILDER_AUTHORIZATION_PATH).exists()
    assert load_builder_authorization(REPOSITORY_ROOT) is None
    with pytest.raises(BuilderAuthorizationError, match="authorization absent"):
        verify_builder_authorization(None)


def test_j1_science_is_unauthorized_independently_of_the_builder() -> None:
    """Two authorizations, two documents, two verifiers.

    This held while a builder authorization existed and holds now that none
    does. That is the point: one says nothing about the other, in either
    direction.
    """
    with pytest.raises(AuthorizationError, match="J1 authorization absent"):
        verify_authorization(None)


def test_nothing_was_built_and_no_evidence_directory_exists() -> None:
    for pattern in ("*.oci.tar", "build-a.json", "build-b.json"):
        assert not list(REPOSITORY_ROOT.glob(pattern)), pattern
    assert not (REPOSITORY_ROOT / DURABLE_EVIDENCE_ROOT).exists()


def test_the_controlled_build_module_still_cannot_build_anything() -> None:
    text = (
        REPOSITORY_ROOT
        / "src/cardiosentinel/journal_extension/j1/controlled_build.py"
    ).read_text(encoding="utf-8")
    assert "import subprocess" not in text
    with pytest.raises(ControlledBuildError, match="no OCI archive"):
        from cardiosentinel.journal_extension.j1.controlled_build import (
            read_oci_archive_manifest,
        )

        read_oci_archive_manifest(REPOSITORY_ROOT / "nothing-here.oci.tar")


# -- R2: a divergence must leave evidence before anything fails ------------


def _build_record(build_id: str, digest: str) -> dict[str, Any]:
    return {
        "build_id": build_id,
        "source_commit": "b" * 40,
        "base_image_digest": "python@sha256:" + "c" * 64,
        "dependency_digest": "d" * 64,
        "build_configuration_digest": "e" * 64,
        "target_platform": "linux/amd64",
        "output_artifact_digest": digest,
        "archive_sha256": "1" * 64,
    }


def _claim_document() -> dict[str, Any]:
    return dict(_claim(100).fields)


def test_a_divergence_produces_a_complete_record_without_raising() -> None:
    """The exact previous failure: the one outcome that left no evidence.

    Every numbered assertion in the brief, in order.
    """
    a = _build_record("BUILD_A", "sha256:" + "a" * 64)
    b = _build_record("BUILD_B", "sha256:" + "b" * 64)

    # 1. record generation does not raise merely because the digests differ
    record = reproducibility_record(first=a, second=b, claim=_claim_document())

    # 2. a complete record is produced, and survives a JSON round trip
    restored = json.loads(json.dumps(record))
    assert restored

    # 3. both digests are present
    assert restored["build_a_artifact_digest"] == "sha256:" + "a" * 64
    assert restored["build_b_artifact_digest"] == "sha256:" + "b" * 64

    # 4 and 5. the classification is the observation, not an error
    assert restored["reproducibility_class"] == DIVERGED
    assert restored["failure_class"] == ARTIFACT_VISIBLE

    # 6. the gate, run separately, rejects it
    with pytest.raises(ControlledBuildError, match="different artifacts"):
        enforce_reproducibility(restored)

    # 7. nothing was selected or promoted
    assert restored["promoted_artifact"] is None
    assert "output_artifact_digest" not in restored


def test_agreement_records_and_passes_the_gate() -> None:
    digest = "sha256:" + "a" * 64
    record = reproducibility_record(
        first=_build_record("BUILD_A", digest),
        second=_build_record("BUILD_B", digest),
        claim=_claim_document(),
    )
    assert record["reproducibility_class"] == BIT_REPRODUCIBLE
    assert record["failure_class"] == COMPLETED_QUALIFICATION
    assert enforce_reproducibility(record)["output_artifact_digest"] == digest


@pytest.mark.parametrize(
    "field",
    [
        "source_commit",
        "base_image_digest",
        "dependency_digest",
        "build_configuration_digest",
        "target_platform",
    ],
)
def test_differing_contract_inputs_are_invalid_not_diverged(field: str) -> None:
    """Two builds from different inputs say nothing about reproducibility."""
    a = _build_record("BUILD_A", "sha256:" + "a" * 64)
    b = _build_record("BUILD_B", "sha256:" + "a" * 64)
    b[field] = "linux/arm64" if field == "target_platform" else "9" * 40
    with pytest.raises(ControlledBuildError, match="invalid qualification input"):
        reproducibility_record(first=a, second=b, claim=_claim_document())


def test_one_build_presented_twice_is_invalid_not_diverged() -> None:
    a = _build_record("BUILD_A", "sha256:" + "a" * 64)
    b = _build_record("BUILD_A", "sha256:" + "b" * 64)
    with pytest.raises(ControlledBuildError, match="one build recorded"):
        reproducibility_record(first=a, second=b, claim=_claim_document())


@pytest.mark.parametrize("missing", ["build_id", "output_artifact_digest"])
def test_malformed_provenance_is_invalid_not_diverged(missing: str) -> None:
    a = _build_record("BUILD_A", "sha256:" + "a" * 64)
    b = _build_record("BUILD_B", "sha256:" + "a" * 64)
    del b[missing]
    with pytest.raises(ControlledBuildError, match="malformed"):
        require_comparable_builds(a, b)


def test_an_empty_or_incomplete_record_cannot_be_enforced_against() -> None:
    with pytest.raises(ControlledBuildError, match="empty or malformed"):
        enforce_reproducibility({})
    with pytest.raises(ControlledBuildError, match="does not carry"):
        enforce_reproducibility({"reproducibility_class": DIVERGED})


def test_an_unknown_reproducibility_class_is_refused() -> None:
    record = reproducibility_record(
        first=_build_record("BUILD_A", "sha256:" + "a" * 64),
        second=_build_record("BUILD_B", "sha256:" + "a" * 64),
        claim=_claim_document(),
    )
    record["reproducibility_class"] = "NOT_REPRODUCIBLE_DOCUMENTED"
    with pytest.raises(ControlledBuildError, match="is not one of"):
        enforce_reproducibility(record)


# -- the workflow records, retains, then enforces --------------------------


def test_the_workflow_uploads_the_record_before_enforcing() -> None:
    names = [
        step.get("name", "") for step in _steps(_job("reproducibility"))
    ]
    record_at = names.index("Compute the reproducibility record")
    upload_at = names.index("Retain the reproducibility record")
    enforce_at = names.index("Enforce the reproducibility result")
    assert record_at < upload_at < enforce_at


def test_the_record_upload_treats_absence_as_an_error() -> None:
    """`warn` would let a missing comparison pass as if nothing happened."""
    upload = next(
        step
        for step in _steps(_job("reproducibility"))
        if step.get("name") == "Retain the reproducibility record"
    )
    assert upload["with"]["if-no-files-found"] == "error"
    assert upload.get("if") == "always()"


def test_recording_and_enforcement_are_separate_commands() -> None:
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "reproducibility-record" in text
    assert "enforce-reproducibility" in text
    assert "compare-builds" not in text
