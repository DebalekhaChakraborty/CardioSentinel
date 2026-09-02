"""The builder authorization review packet, checked against external facts.

**No builder is authorized here, and no authorization document is written.** The
canonical path stays empty for the whole of this module, and a test asserts that
after every synthetic authorization has been constructed and verified.

The packet is a *claim* about mechanically resolvable values. A test that read
those values out of the packet and compared them to constants written beside it
would prove only that one hand wrote both. So every machine-verified row is
re-derived from something the packet cannot supply: git's object store, the raw
bytes on disk, the repository's own canonical digest implementation, and the
frozen V1 evidence the runtime authority is read from.

The final state these tests establish is the one the packet claims: every
non-human rule is already satisfied, and the only missing condition is the human
act.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from cardiosentinel.journal_extension.j1 import preflight
from cardiosentinel.journal_extension.j1.approved_runtime import (
    APPROVED_DEPENDENCY_DIGEST,
    APPROVED_PACKAGE_COUNT,
    approved_runtime_fields,
)
from cardiosentinel.journal_extension.j1.builder_authorization import (
    BUILDER_AUTHORIZATION_FIELDS,
    BUILDER_AUTHORIZATION_PATH,
    PLACEHOLDER_VALUES,
    BuilderAuthorizationError,
    load_builder_authorization,
    verify_builder_authorization,
    verify_workflow_identity,
)
from cardiosentinel.journal_extension.j1.builder_protocol import (
    ARTIFACT_KIND,
    GENERIC_BUILDER_IDENTITIES,
    REQUIRED_BUILD_CONFIGURATION_INPUTS,
    TARGET_PLATFORM,
)
from cardiosentinel.journal_extension.j1.controlled_build import (
    configuration_digest,
    write_dependency_input,
)

REPOSITORY_ROOT = Path(preflight.J1_PACKAGE_ROOT).parents[3]
PACKET_RELATIVE = (
    "docs/journal-extension/j1/J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V1.md"
)
PACKET_PATH = REPOSITORY_ROOT / PACKET_RELATIVE
WORKFLOW_RELATIVE = ".github/workflows/j1-environment-artifact-build.yml"
PROTOCOL_RELATIVE = (
    "docs/journal-extension/j1/J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V1.md"
)

PERMITTED_STATUSES = ("MACHINE-VERIFIED", "HUMAN-DECISION-REQUIRED", "BLOCKED")

#: The em dash the packet uses where a value must not exist. Not a placeholder
#: string: a placeholder is something that looks like content.
UNRESOLVED = "—"

#: Fields no mechanism derives. The packet must leave every one of them empty.
HUMAN_FIELDS = (
    "builder_authorization_id",
    "authorization_timestamp",
    "human_authorizer_identity",
)
#: Required by the schema, determined by no committed document.
BLOCKED_FIELDS = ("provenance_destination",)

BUILD_CONFIGURATION_PATHS = {
    "containerfile": "containers/j1-environment/Containerfile",
    "build_script": "containers/j1-environment/build.sh",
    "artifact_validation_script": "containers/j1-environment/validate_artifact.sh",
    "workflow": WORKFLOW_RELATIVE,
}

BUILDKIT_MANIFEST = (
    "moby/buildkit@sha256:"
    "040d34121c27906c4ff9ac152a30d52bf2c5d328d3bb748916bb3d2743c02528"
)
SETUP_BUILDX_ACTION = (
    "docker/setup-buildx-action@8d2750c68a42422c14e847fe6c8ac0403b4cbd6f"
)


# -- reading the packet ----------------------------------------------------


def _packet_text() -> str:
    return PACKET_PATH.read_text(encoding="utf-8")


def _field_table() -> dict[str, dict[str, str]]:
    """Parse the packet's own field table. It is the single source of truth."""
    lines = _packet_text().splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.startswith("| Field | Resolved value |"):
            start = index + 2
            break
    assert start is not None, "the packet carries no field table"

    table: dict[str, dict[str, str]] = {}
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        assert len(cells) == 5, f"malformed field-table row: {line}"
        table[cells[0]] = {
            "value": cells[1],
            "source": cells[2],
            "verification": cells[3],
            "status": cells[4],
        }
    return table


def _machine_value(field: str) -> str:
    row = _field_table()[field]
    assert row["status"] == "MACHINE-VERIFIED", (
        f"{field} is {row['status']}, so it carries no value to check"
    )
    return row["value"]


# -- git, used only where it can answer ------------------------------------


def _git(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(REPOSITORY_ROOT), *arguments],
        capture_output=True,
        check=False,
    )


def _require_commit(commit: str) -> None:
    """Skip visibly rather than pass silently on a shallow checkout.

    CI checks out at the default depth, so a historical commit object is
    frequently absent there. A check that quietly succeeds when it could not run
    is worse than one that says it did not run, so this skips loudly and the
    checkout-based recomputations -- which need no history -- still run.
    """
    if _git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
        pytest.skip(
            f"commit {commit} is not in this checkout's object store "
            "(shallow clone); the checkout-based digest checks still ran"
        )


# -- the packet is not, and cannot become, an authorization ----------------


def test_the_packet_exists_and_is_not_the_canonical_authorization() -> None:
    assert PACKET_PATH.is_file()
    assert PACKET_RELATIVE != BUILDER_AUTHORIZATION_PATH


def test_no_builder_authorization_exists_before_or_after_this_module() -> None:
    assert not (REPOSITORY_ROOT / BUILDER_AUTHORIZATION_PATH).exists()
    assert load_builder_authorization(REPOSITORY_ROOT) is None


def test_the_packet_is_not_loadable_as_an_authorization() -> None:
    """Markdown is not a mapping of fields, and the loader reads one path."""
    with pytest.raises(json.JSONDecodeError):
        json.loads(_packet_text())
    with pytest.raises(BuilderAuthorizationError, match="authorization absent"):
        verify_builder_authorization(load_builder_authorization(REPOSITORY_ROOT))


def test_the_packet_declares_its_state_in_its_own_words() -> None:
    text = _packet_text()
    assert "READY FOR HUMAN DECISION — BUILDER NOT AUTHORIZED" in text
    assert "PRE-REGISTERED" in text
    assert "NOT AUTHORIZED" in text


# -- the field table ------------------------------------------------------


def test_the_table_covers_every_schema_field_exactly_once() -> None:
    table = _field_table()
    assert set(table) == set(BUILDER_AUTHORIZATION_FIELDS)
    assert len(table) == len(BUILDER_AUTHORIZATION_FIELDS) == 21


def test_only_the_three_permitted_statuses_appear() -> None:
    for field, row in _field_table().items():
        assert row["status"] in PERMITTED_STATUSES, f"{field}: {row['status']}"


def test_no_pending_status_masquerades_as_authorization_content() -> None:
    for field, row in _field_table().items():
        assert "PENDING" not in row["status"].upper(), field


def test_human_and_blocked_fields_carry_no_value() -> None:
    """A machine may not synthesize a human field, not even plausibly."""
    table = _field_table()
    for field in HUMAN_FIELDS:
        assert table[field]["status"] == "HUMAN-DECISION-REQUIRED", field
        assert table[field]["value"] == UNRESOLVED, field
    for field in BLOCKED_FIELDS:
        assert table[field]["status"] == "BLOCKED", field
        assert table[field]["value"] == UNRESOLVED, field


def test_every_other_field_is_machine_verified_and_non_empty() -> None:
    table = _field_table()
    unresolved = set(HUMAN_FIELDS) | set(BLOCKED_FIELDS)
    for field in BUILDER_AUTHORIZATION_FIELDS:
        if field in unresolved:
            continue
        assert table[field]["status"] == "MACHINE-VERIFIED", field
        assert table[field]["value"] not in ("", UNRESOLVED), field


def test_no_resolved_value_is_a_placeholder() -> None:
    for field, row in _field_table().items():
        if row["value"] == UNRESOLVED:
            continue
        assert row["value"].strip().lower() not in PLACEHOLDER_VALUES, field


# -- machine-verified values, re-derived from outside the packet -----------


def test_workflow_digest_recomputed_from_the_checkout() -> None:
    """Runs everywhere: the working tree needs no git history."""
    raw = (REPOSITORY_ROOT / WORKFLOW_RELATIVE).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == _machine_value("workflow_sha256")


def test_workflow_digest_recomputed_from_the_git_object_store() -> None:
    """The declared review commit must actually hold the declared bytes."""
    commit = _machine_value("workflow_review_commit")
    _require_commit(commit)
    completed = _git("cat-file", "blob", f"{commit}:{WORKFLOW_RELATIVE}")
    assert completed.returncode == 0
    assert hashlib.sha256(completed.stdout).hexdigest() == _machine_value(
        "workflow_sha256"
    )


def test_the_workflow_path_the_packet_names_is_the_one_on_disk() -> None:
    assert _machine_value("workflow_path") == WORKFLOW_RELATIVE
    assert (REPOSITORY_ROOT / _machine_value("workflow_path")).is_file()


def test_the_commit_fields_are_full_shas_not_moving_refs() -> None:
    for field in ("workflow_review_commit", "authorized_source_commit"):
        value = _machine_value(field)
        assert len(value) == 40, field
        assert set(value) <= set("0123456789abcdef"), field


def test_protocol_digest_recomputed_from_the_checkout() -> None:
    raw = (REPOSITORY_ROOT / PROTOCOL_RELATIVE).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == _machine_value(
        "controlled_build_protocol_digest"
    )


def test_protocol_digest_recomputed_from_the_git_object_store() -> None:
    commit = _machine_value("workflow_review_commit")
    _require_commit(commit)
    completed = _git("cat-file", "blob", f"{commit}:{PROTOCOL_RELATIVE}")
    assert completed.returncode == 0
    assert hashlib.sha256(completed.stdout).hexdigest() == _machine_value(
        "controlled_build_protocol_digest"
    )


def test_the_protocol_identity_names_the_document_that_was_digested() -> None:
    assert Path(PROTOCOL_RELATIVE).stem == _machine_value(
        "controlled_build_protocol_identity"
    )


def test_build_configuration_digest_recomputed_canonically(tmp_path: Path) -> None:
    """Recomputed with the repository's own implementation, not a second one.

    The dependency input is regenerated from the frozen lock rather than read
    from a fixture, so this fails if the frozen package authority moves.
    """
    write_dependency_input(REPOSITORY_ROOT, tmp_path)
    paths = {
        name: REPOSITORY_ROOT / relative
        for name, relative in BUILD_CONFIGURATION_PATHS.items()
    }
    paths["dependency_input"] = tmp_path / "requirements.pypi.txt"
    assert set(paths) == set(REQUIRED_BUILD_CONFIGURATION_INPUTS)

    result = configuration_digest(paths)
    assert result["build_configuration_digest"] == _machine_value(
        "build_configuration_digest"
    )
    # The digested workflow is the reviewed workflow, not merely a file of the
    # same name.
    assert result["inputs"]["workflow"] == _machine_value("workflow_sha256")


def test_the_derived_dependency_input_is_deterministic(tmp_path: Path) -> None:
    """Two independent generations, because one proves nothing about drift."""
    first = write_dependency_input(REPOSITORY_ROOT, tmp_path / "a")
    second = write_dependency_input(REPOSITORY_ROOT, tmp_path / "b")
    assert first == second
    assert first["dependency_authority_digest"] == APPROVED_DEPENDENCY_DIGEST
    assert sum(first["counts"].values()) == APPROVED_PACKAGE_COUNT


def test_dependency_digest_is_the_approved_authority_not_a_new_one() -> None:
    assert _machine_value("dependency_digest") == APPROVED_DEPENDENCY_DIGEST


def test_dependency_authority_identity_comes_from_the_authority() -> None:
    assert (
        _machine_value("dependency_authority_identity")
        == approved_runtime_fields()["dependency_lock_identity"]
    )


def test_target_platform_and_artifact_type_are_the_frozen_constants() -> None:
    assert _machine_value("target_platform") == TARGET_PLATFORM
    assert _machine_value("artifact_type") == ARTIFACT_KIND


def test_the_base_image_is_digest_addressed_and_committed() -> None:
    """A tag is not authority, and a digest nobody committed is not evidence."""
    value = _machine_value("base_image_digest")
    repository, separator, digest = value.partition("@sha256:")
    assert separator and repository
    assert len(digest) == 64

    workflow = (REPOSITORY_ROOT / WORKFLOW_RELATIVE).read_text(encoding="utf-8")
    protocol = (REPOSITORY_ROOT / PROTOCOL_RELATIVE).read_text(encoding="utf-8")
    assert value in workflow
    assert digest in protocol, "workflow and protocol name different base images"


def test_the_build_tool_pins_are_in_the_committed_workflow() -> None:
    workflow = (REPOSITORY_ROOT / WORKFLOW_RELATIVE).read_text(encoding="utf-8")
    protocol = (REPOSITORY_ROOT / PROTOCOL_RELATIVE).read_text(encoding="utf-8")
    for pin in (
        BUILDKIT_MANIFEST,
        "version: v0.36.1",
        SETUP_BUILDX_ACTION,
        f"runs-on: {_machine_value('runner_class')}",
    ):
        assert pin in workflow, pin
    assert "ubuntu-latest" not in workflow
    assert BUILDKIT_MANIFEST.partition("@sha256:")[2] in protocol
    assert "v0.36.1" in protocol


def test_the_authorized_source_commit_holds_every_build_input() -> None:
    commit = _machine_value("authorized_source_commit")
    _require_commit(commit)
    for relative in BUILD_CONFIGURATION_PATHS.values():
        assert _git("cat-file", "-e", f"{commit}:{relative}").returncode == 0, (
            f"{relative} is absent at the authorized source commit"
        )


def test_the_builder_candidate_id_is_composed_of_the_other_fields() -> None:
    """Derived, not typed: it must agree with the fields beside it."""
    candidate = _machine_value("builder_candidate_id")
    for part in (
        _machine_value("provider"),
        _machine_value("repository"),
        _machine_value("workflow_path"),
        _machine_value("workflow_review_commit"),
        _machine_value("runner_class"),
    ):
        assert part in candidate, part


# -- a synthetic authorization, never written to disk ----------------------


def _authorization_from_packet(**overrides: Any) -> dict[str, Any]:
    """Built from the packet's machine-verified rows. Entirely in memory.

    The human and blocked fields are supplied here as obviously synthetic
    strings. That is the whole point: substituting them is what turns a review
    packet into something that verifies, and only a human may do it for real.
    """
    table = _field_table()
    document: dict[str, Any] = {
        name: table[name]["value"]
        for name in BUILDER_AUTHORIZATION_FIELDS
        if table[name]["status"] == "MACHINE-VERIFIED"
    }
    document["builder_authorization_id"] = "SYNTHETIC-IN-MEMORY-NOT-REAL"
    document["authorization_timestamp"] = "2026-09-02T00:00:00Z"
    document["human_authorizer_identity"] = "synthetic, not a signatory"
    document["provenance_destination"] = "synthetic://not-a-destination"
    document.update(overrides)
    return document


def test_the_packet_values_satisfy_every_non_human_rule() -> None:
    """The end state: only the human act is missing."""
    verified = verify_builder_authorization(_authorization_from_packet())
    assert verified.workflow_sha256 == _machine_value("workflow_sha256")
    assert verified.authorized_source_commit == _machine_value(
        "authorized_source_commit"
    )


@pytest.mark.parametrize("field", HUMAN_FIELDS + BLOCKED_FIELDS)
def test_without_the_human_fields_the_authorization_is_incomplete(
    field: str,
) -> None:
    document = _authorization_from_packet()
    del document[field]
    with pytest.raises(BuilderAuthorizationError, match="incomplete"):
        verify_builder_authorization(document)


@pytest.mark.parametrize("value", ["PENDING", "TBD", "n/a", "unknown", "any"])
def test_a_placeholder_human_field_cannot_complete_the_authorization(
    value: str,
) -> None:
    with pytest.raises(BuilderAuthorizationError, match="placeholder"):
        verify_builder_authorization(
            _authorization_from_packet(human_authorizer_identity=value)
        )


@pytest.mark.parametrize("generic", GENERIC_BUILDER_IDENTITIES)
def test_the_authorization_cannot_broaden_to_a_generic_provider(
    generic: str,
) -> None:
    """'GitHub Actions may build future J1 environments' stays unwritable."""
    with pytest.raises(BuilderAuthorizationError, match="names a provider"):
        verify_builder_authorization(_authorization_from_packet(repository=generic))


def test_a_different_dependency_digest_is_refused() -> None:
    with pytest.raises(BuilderAuthorizationError, match="dependency digest"):
        verify_builder_authorization(
            _authorization_from_packet(dependency_digest="f" * 64)
        )


def test_a_base_image_by_tag_is_refused() -> None:
    with pytest.raises(BuilderAuthorizationError, match="addressed by digest"):
        verify_builder_authorization(
            _authorization_from_packet(base_image_digest="python:3.12.6-slim-bookworm")
        )


# -- workflow identity, against a repository seeded with the real bytes ----


def _seed(repository: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        capture_output=True,
        check=True,
        text=True,
    )
    return completed.stdout.strip()


@pytest.fixture
def seeded_repository(tmp_path: Path) -> dict[str, Any]:
    """A throwaway repository holding the *real* committed workflow bytes.

    This binds the packet's digest to the file's actual content through the real
    verifier, without depending on this checkout having history -- which CI,
    checking out at the default depth, does not.
    """
    repository = tmp_path / "seeded"
    (repository / ".github/workflows").mkdir(parents=True)
    raw = (REPOSITORY_ROOT / WORKFLOW_RELATIVE).read_bytes()
    (repository / WORKFLOW_RELATIVE).write_bytes(raw)

    _seed(tmp_path, "init", "-q", str(repository))
    _seed(repository, "config", "user.email", "packet@example.invalid")
    _seed(repository, "config", "user.name", "packet")
    _seed(repository, "add", WORKFLOW_RELATIVE)
    _seed(repository, "commit", "-q", "-m", "seed: the reviewed workflow bytes")
    return {"root": repository, "commit": _seed(repository, "rev-parse", "HEAD")}


def test_the_packet_digest_is_what_the_verifier_accepts(
    seeded_repository: dict[str, Any],
) -> None:
    proof = verify_workflow_identity(
        verify_builder_authorization(
            _authorization_from_packet(
                workflow_review_commit=seeded_repository["commit"]
            )
        ),
        repository_root=seeded_repository["root"],
        running_workflow_ref=f"o/r/{WORKFLOW_RELATIVE}@refs/heads/x",
        running_commit=seeded_repository["commit"],
    )
    declared = _machine_value("workflow_sha256")
    assert proof["workflow_sha256_recomputed_from_review_commit"] == declared
    assert proof["workflow_sha256_recomputed_from_checkout"] == declared


def test_one_byte_of_drift_refuses_the_packet_digest(
    seeded_repository: dict[str, Any],
) -> None:
    """If this passed, the packet would be pinning nothing."""
    workflow = seeded_repository["root"] / WORKFLOW_RELATIVE
    workflow.write_bytes(workflow.read_bytes() + b" ")
    with pytest.raises(BuilderAuthorizationError):
        verify_workflow_identity(
            verify_builder_authorization(
                _authorization_from_packet(
                    workflow_review_commit=seeded_repository["commit"]
                )
            ),
            repository_root=seeded_repository["root"],
        )


def test_workflow_identity_against_this_repository_history() -> None:
    """The same check against the real review commit, where history allows."""
    _require_commit(_machine_value("workflow_review_commit"))
    proof = verify_workflow_identity(
        verify_builder_authorization(_authorization_from_packet()),
        repository_root=REPOSITORY_ROOT,
        running_workflow_ref=f"o/r/{WORKFLOW_RELATIVE}@refs/heads/master",
    )
    declared = _machine_value("workflow_sha256")
    assert proof["workflow_sha256_recomputed_from_review_commit"] == declared
    assert proof["workflow_sha256_recomputed_from_checkout"] == declared


# -- the boundary the schema does not enforce, recorded rather than hidden --


def test_no_build_count_bound_exists_in_the_schema() -> None:
    """The packet says this. The schema is what makes it true."""
    for bound in ("attempt_budget", "build_budget", "run_budget", "max_builds"):
        assert bound not in BUILDER_AUTHORIZATION_FIELDS
    assert "exactly one BUILD_A/BUILD_B pair" in _packet_text()


def test_the_packet_states_the_residual_trust_without_softening_it() -> None:
    text = _packet_text()
    assert "GitHub remains the external" in text
    assert "underlying hardware and execution" in text
    assert "is **not** cryptographically reproducible" in text


def test_the_packet_records_the_provenance_gap_rather_than_filling_it() -> None:
    table = _field_table()
    assert table["provenance_destination"]["status"] == "BLOCKED"
    assert table["provenance_destination"]["value"] == UNRESOLVED
    assert "s3://" not in _packet_text()


# -- negative capability ---------------------------------------------------


def test_nothing_was_built() -> None:
    for pattern in ("*.oci.tar", "build-a.json", "build-b.json"):
        assert not list(REPOSITORY_ROOT.glob(pattern)), pattern
    assert not list((REPOSITORY_ROOT / "docs/journal-extension/j1").glob("*.json"))


def test_the_gate_still_refuses_after_every_test_in_this_module() -> None:
    assert not (REPOSITORY_ROOT / BUILDER_AUTHORIZATION_PATH).exists()
    with pytest.raises(BuilderAuthorizationError, match="authorization absent"):
        verify_builder_authorization(load_builder_authorization(REPOSITORY_ROOT))
