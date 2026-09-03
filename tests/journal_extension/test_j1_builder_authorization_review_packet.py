"""The V2 review packet, checked against external facts; V1 kept as a receipt.

**No builder is authorized here, and no authorization document is written.** The
canonical path stays empty for the whole of this module, and a test asserts that
after every synthetic authorization has been constructed and verified.

Two packets, two different jobs. V1 is an **audit receipt**: it recorded findings
F1-F5 against values that the remediation then superseded, and its bytes are
asserted unchanged rather than re-checked against live code -- re-pointing a
receipt at current values would erase the discrepancy it exists to record. V2 is
the live packet, and every machine-verified row in it is re-derived from
something the packet cannot supply.

Three of V2's fields are `BLOCKED` on the merge that creates the review commit.
That is the honest state and the tests assert it rather than papering over it
with a working-tree value dressed as a commit.
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
    CONTROLLED_BUILD_WORKFLOW_PATH,
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
from cardiosentinel.journal_extension.j1.qualification import (
    QUALIFICATION_POLICY,
    durable_evidence_destination,
)

REPOSITORY_ROOT = Path(preflight.J1_PACKAGE_ROOT).parents[3]
J1_DOCS = "docs/journal-extension/j1"

PACKET_RELATIVE = f"{J1_DOCS}/J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V2.md"
PACKET_PATH = REPOSITORY_ROOT / PACKET_RELATIVE
PROTOCOL_RELATIVE = f"{J1_DOCS}/J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2.md"

#: Retained receipts. Their bytes are the record; they are never re-pointed.
PACKET_V1_RELATIVE = f"{J1_DOCS}/J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V1.md"
PACKET_V1_SHA256 = "86c298efd424d5dd2e86802d015f3f1d90690c78311cc99c18f6cb8a604243c2"
PROTOCOL_V1_RELATIVE = f"{J1_DOCS}/J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V1.md"
PROTOCOL_V1_SHA256 = (
    "e980d0f7b22851a6dadd1158ba979cb95395ebc765c71ce5b068ce55fcb651aa"
)

WORKFLOW_RELATIVE = CONTROLLED_BUILD_WORKFLOW_PATH

PERMITTED_STATUSES = ("MACHINE-VERIFIED", "HUMAN-DECISION-REQUIRED", "BLOCKED")

#: The em dash the packet uses where a value must not exist. Not a placeholder
#: string: a placeholder is something that looks like content.
UNRESOLVED = "—"

#: No mechanism derives these.
HUMAN_FIELDS = (
    "builder_authorization_id",
    "provenance_destination",
    "authorization_timestamp",
    "human_authorizer_identity",
)
#: Determined by an event that has not happened: the merge of the remediation
#: pull request, which is what creates the reviewed commit.
BLOCKED_FIELDS = (
    "builder_candidate_id",
    "workflow_review_commit",
    "authorized_source_commit",
)

BUILD_CONFIGURATION_PATHS = {
    "containerfile": "containers/j1-environment/Containerfile",
    "containerfile_dockerignore": (
        "containers/j1-environment/Containerfile.dockerignore"
    ),
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

SYNTHETIC_AUTHORIZATION_ID = "SYNTHETIC-REMEDIATION-NOT-REAL"


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


# -- V1 is a receipt, not a live document ----------------------------------


def test_the_v1_packet_is_byte_unchanged() -> None:
    """A receipt that gets updated is not a receipt.

    V1's values are superseded. Its bytes record what was reviewed and what was
    found, and re-pointing it at the remediated values would delete the very
    discrepancy that justified the remediation.
    """
    raw = (REPOSITORY_ROOT / PACKET_V1_RELATIVE).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PACKET_V1_SHA256


def test_the_v1_build_protocol_is_byte_unchanged() -> None:
    """V1 §12 is stale and stays stale. History is superseded, not rewritten."""
    raw = (REPOSITORY_ROOT / PROTOCOL_V1_RELATIVE).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PROTOCOL_V1_SHA256


def test_v2_declares_what_it_supersedes_and_names_its_digest() -> None:
    text = _packet_text()
    assert "J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V1.md" in text
    assert PACKET_V1_SHA256 in text
    assert "byte-unchanged" in text


def test_the_superseding_protocol_records_the_lineage() -> None:
    """A reader must be able to reconcile 'no workflow exists' with one that does."""
    protocol = (REPOSITORY_ROOT / PROTOCOL_RELATIVE).read_text(encoding="utf-8")
    assert PROTOCOL_V1_SHA256 in protocol
    assert "Supersedes" in protocol
    assert "j1-environment-build.yml" in protocol, "correction C1 must be recorded"


def test_the_packet_accounts_for_every_finding() -> None:
    """All six, each with a resolution and a stated remaining limitation."""
    text = _packet_text()
    for finding in ("F1", "F2", "F3", "F4", "F5", "F6"):
        assert f"**{finding}**" in text, finding
    assert "Remaining limitation" in text


# -- the packet is not, and cannot become, an authorization ----------------


def test_the_packet_exists_and_is_not_the_canonical_authorization() -> None:
    assert PACKET_PATH.is_file()
    assert PACKET_RELATIVE != BUILDER_AUTHORIZATION_PATH


def test_no_builder_authorization_exists_before_or_after_this_module() -> None:
    assert not (REPOSITORY_ROOT / BUILDER_AUTHORIZATION_PATH).exists()
    assert load_builder_authorization(REPOSITORY_ROOT) is None


def test_the_packet_is_not_loadable_as_an_authorization() -> None:
    with pytest.raises(json.JSONDecodeError):
        json.loads(_packet_text())
    with pytest.raises(BuilderAuthorizationError, match="authorization absent"):
        verify_builder_authorization(load_builder_authorization(REPOSITORY_ROOT))


def test_the_packet_does_not_claim_to_be_ready() -> None:
    """Three fields have no values, so a signature over it would sign nothing."""
    text = _packet_text()
    assert "NOT READY FOR HUMAN DECISION" in text
    assert "BUILDER NOT AUTHORIZED" in text
    assert "must not be signed" in text


# -- the field table ------------------------------------------------------


def test_the_table_covers_every_schema_field_exactly_once() -> None:
    table = _field_table()
    assert set(table) == set(BUILDER_AUTHORIZATION_FIELDS)
    assert len(table) == len(BUILDER_AUTHORIZATION_FIELDS) == 22


def test_only_the_three_permitted_statuses_appear() -> None:
    for field, row in _field_table().items():
        assert row["status"] in PERMITTED_STATUSES, f"{field}: {row['status']}"


def test_no_pending_status_masquerades_as_authorization_content() -> None:
    for field, row in _field_table().items():
        assert "PENDING" not in row["status"].upper(), field


def test_human_and_blocked_fields_carry_no_value() -> None:
    """A machine may not synthesize a human field, nor invent a commit."""
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


def test_the_blocked_fields_are_blocked_on_the_merge_not_on_a_choice() -> None:
    table = _field_table()
    for field in BLOCKED_FIELDS:
        assert "merge" in table[field]["source"] or "merge" in (
            table[field]["verification"]
        ), field


# -- machine-verified values, re-derived from outside the packet -----------


def test_workflow_digest_recomputed_from_the_checkout() -> None:
    raw = (REPOSITORY_ROOT / WORKFLOW_RELATIVE).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == _machine_value("workflow_sha256")


def test_the_workflow_path_is_the_one_the_verifier_enforces() -> None:
    assert _machine_value("workflow_path") == CONTROLLED_BUILD_WORKFLOW_PATH
    assert (REPOSITORY_ROOT / _machine_value("workflow_path")).is_file()


def test_protocol_digest_recomputed_from_the_checkout() -> None:
    raw = (REPOSITORY_ROOT / PROTOCOL_RELATIVE).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == _machine_value(
        "controlled_build_protocol_digest"
    )


def test_the_protocol_identity_names_the_document_that_was_digested() -> None:
    assert Path(PROTOCOL_RELATIVE).stem == _machine_value(
        "controlled_build_protocol_identity"
    )


def test_build_configuration_digest_recomputed_canonically(tmp_path: Path) -> None:
    """Recomputed with the repository's own implementation, over all seven members."""
    write_dependency_input(REPOSITORY_ROOT, tmp_path)
    paths = {
        name: REPOSITORY_ROOT / relative
        for name, relative in BUILD_CONFIGURATION_PATHS.items()
    }
    paths["dependency_input_pypi"] = tmp_path / "requirements.pypi.txt"
    paths["dependency_input_pytorch"] = tmp_path / "requirements.pytorch-cpu.txt"
    assert set(paths) == set(REQUIRED_BUILD_CONFIGURATION_INPUTS)

    result = configuration_digest(paths)
    assert result["build_configuration_digest"] == _machine_value(
        "build_configuration_digest"
    )
    assert result["inputs"]["workflow"] == _machine_value("workflow_sha256")
    assert result["member_count"] == 7


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


def test_the_qualification_policy_is_the_frozen_constant() -> None:
    assert _machine_value("qualification_policy") == QUALIFICATION_POLICY


def test_the_base_image_is_digest_addressed_and_in_the_protocol() -> None:
    """A tag is not authority, and a digest nobody committed is not evidence."""
    value = _machine_value("base_image_digest")
    repository, separator, digest = value.partition("@sha256:")
    assert separator and repository
    assert len(digest) == 64
    protocol = (REPOSITORY_ROOT / PROTOCOL_RELATIVE).read_text(encoding="utf-8")
    assert value in protocol


def test_the_build_tool_pins_are_in_the_workflow_and_the_packet() -> None:
    """The workflow is what runs; the packet is what a human reviews."""
    workflow = (REPOSITORY_ROOT / WORKFLOW_RELATIVE).read_text(encoding="utf-8")
    for pin in (
        BUILDKIT_MANIFEST,
        "version: v0.36.1",
        SETUP_BUILDX_ACTION,
        f"runs-on: {_machine_value('runner_class')}",
    ):
        assert pin in workflow, pin
    assert "ubuntu-latest" not in workflow

    packet = _packet_text()
    assert BUILDKIT_MANIFEST.partition("@sha256:")[2] in packet
    assert "v0.36.1" in packet
    assert SETUP_BUILDX_ACTION.partition("@")[2] in packet


# -- a synthetic authorization, never written to disk ----------------------


def _authorization_from_packet(**overrides: Any) -> dict[str, Any]:
    """Built from the packet's machine-verified rows. Entirely in memory.

    The human fields, and the three fields blocked on the merge, are supplied
    here as obviously synthetic values. Substituting them is exactly what turns
    a review packet into something that verifies -- and for the human fields
    only a human may do it, while for the blocked fields only the merge can.
    """
    table = _field_table()
    document: dict[str, Any] = {
        name: table[name]["value"]
        for name in BUILDER_AUTHORIZATION_FIELDS
        if table[name]["status"] == "MACHINE-VERIFIED"
    }
    document["builder_authorization_id"] = SYNTHETIC_AUTHORIZATION_ID
    document["provenance_destination"] = durable_evidence_destination(
        SYNTHETIC_AUTHORIZATION_ID
    )
    document["authorization_timestamp"] = "2026-09-02T00:00:00Z"
    document["human_authorizer_identity"] = "synthetic, not a signatory"
    document["builder_candidate_id"] = (
        "github-actions:DebalekhaChakraborty/CardioSentinel//"
        f"{CONTROLLED_BUILD_WORKFLOW_PATH}@{'1' * 40}#ubuntu-24.04"
    )
    document["workflow_review_commit"] = "1" * 40
    document["authorized_source_commit"] = "2" * 40
    document.update(overrides)
    return document


def test_the_packet_values_satisfy_every_non_human_rule() -> None:
    """Only the human act, and the merge that fixes the commits, are missing."""
    verified = verify_builder_authorization(_authorization_from_packet())
    assert verified.workflow_sha256 == _machine_value("workflow_sha256")


@pytest.mark.parametrize("field", HUMAN_FIELDS + BLOCKED_FIELDS)
def test_without_the_unresolved_fields_the_authorization_is_incomplete(
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
    """A throwaway repository holding the *real* workflow bytes.

    This binds the packet's digest to the file's actual content through the real
    verifier. It is what stands in for V1's git-object-store check while no
    commit yet contains these bytes as merged history.
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


# -- disclosures the packet must keep making -------------------------------


def test_the_packet_states_the_residual_trust_without_softening_it() -> None:
    text = _packet_text()
    assert "GitHub remains the external" in text
    assert "underlying hardware and execution" in text
    assert "is not cryptographically reproducible" in text


def test_the_packet_calls_the_pair_rule_detection_not_prevention() -> None:
    """The one claim that would be a lie if softened."""
    text = _packet_text()
    assert "detection, not prevention" in text
    assert "Nothing stops a second dispatch" in text


def test_the_packet_explains_why_no_pair_count_field_was_added() -> None:
    text = _packet_text()
    assert "qualification_pair_count" in text
    assert "not" in text


# -- negative capability ---------------------------------------------------


def test_nothing_was_built() -> None:
    for pattern in ("*.oci.tar", "build-a.json", "build-b.json"):
        assert not list(REPOSITORY_ROOT.glob(pattern)), pattern
    assert not list((REPOSITORY_ROOT / J1_DOCS).glob("*.json"))


def test_the_gate_still_refuses_after_every_test_in_this_module() -> None:
    assert not (REPOSITORY_ROOT / BUILDER_AUTHORIZATION_PATH).exists()
    with pytest.raises(BuilderAuthorizationError, match="authorization absent"):
        verify_builder_authorization(load_builder_authorization(REPOSITORY_ROOT))
