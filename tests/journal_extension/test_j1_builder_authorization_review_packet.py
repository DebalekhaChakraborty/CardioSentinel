"""The V3 review packet, checked against external facts; V1 and V2 kept as receipts.

**No builder is authorized here, and no authorization document is written.** The
canonical path stays empty for the whole of this module, and a test asserts that
after every synthetic authorization has been constructed and verified.

Three packets, three jobs. V1 and V2 are **audit receipts** whose bytes are the
record: V1 carried findings F1-F5 against values the remediation superseded, and
V2 carried the remediation's own values while three fields were still blocked on
a merge. Re-pointing either at current values would erase the discrepancy each
exists to record, so they are asserted byte-unchanged and never re-checked
against live code. V3 is the live packet.

V3's central claim is that `BLOCKED = 0` -- every machine-resolvable field is
resolved against a commit that now exists. Two things are proven separately and
must never collapse into one: that **every machine requirement can pass**, and
that **no human authorization exists**. A test asserts each, and a test asserts
they are different claims.
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
    APPROVED_PYTHON_RUNTIME_IDENTITY,
    approved_runtime_fields,
)
from cardiosentinel.journal_extension.j1.authorization import (
    AuthorizationError,
    verify_authorization,
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
    ARTIFACT_MEDIA_TYPE,
    GENERIC_BUILDER_IDENTITIES,
    REQUIRED_BUILD_CONFIGURATION_INPUTS,
    TARGET_PLATFORM,
    ControlledBuilderIdentity,
    require_specific_builder_identity,
)
from cardiosentinel.journal_extension.j1.controlled_build import (
    configuration_digest,
    write_dependency_input,
)
from cardiosentinel.journal_extension.j1.qualification import (
    QUALIFICATION_POLICY,
    SINGLE_CLAIM_POLICY,
    durable_evidence_destination,
)

REPOSITORY_ROOT = Path(preflight.J1_PACKAGE_ROOT).parents[3]
J1_DOCS = "docs/journal-extension/j1"

PACKET_RELATIVE = f"{J1_DOCS}/J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V3.md"
PACKET_PATH = REPOSITORY_ROOT / PACKET_RELATIVE
PROTOCOL_RELATIVE = f"{J1_DOCS}/J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2.md"
WORKFLOW_RELATIVE = CONTROLLED_BUILD_WORKFLOW_PATH

#: Retained receipts. Their bytes are the record; they are never re-pointed.
RETAINED_RECEIPTS = {
    f"{J1_DOCS}/J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V1.md": (
        "86c298efd424d5dd2e86802d015f3f1d90690c78311cc99c18f6cb8a604243c2"
    ),
    f"{J1_DOCS}/J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V2.md": (
        "b1390c3512b37f81966cc226a552dfb0c4673cbcab5aae10735e6ac74059c992"
    ),
    f"{J1_DOCS}/J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V1.md": (
        "e980d0f7b22851a6dadd1158ba979cb95395ebc765c71ce5b068ce55fcb651aa"
    ),
    f"{J1_DOCS}/J1_BUILDER_SELECTION_RECEIPT_V1.md": (
        "3130fac6e8198fb28fff55682bd93af47f81df921ab5919aafb8d36d42aa58cc"
    ),
}

PERMITTED_STATUSES = (
    "MACHINE-VERIFIED",
    "HUMAN-DECISION-REQUIRED",
    "HUMAN-DERIVED",
    "BLOCKED",
)

#: The em dash the packet uses where a value must not exist.
UNRESOLVED = "—"

HUMAN_FIELDS = (
    "builder_authorization_id",
    "authorization_timestamp",
    "human_authorizer_identity",
)
#: Determined by a rule, not by a choice: the human picks the id and this
#: follows. Recorded as its derivation, never as a literal path.
DERIVED_FIELDS = ("provenance_destination",)
PROVENANCE_RULE = "durable_evidence_destination(builder_authorization_id)"

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

SYNTHETIC_AUTHORIZATION_ID = "SYNTHETIC-V3-NOT-A-REAL-AUTHORIZATION"

#: The authorization a human recorded in #154, after reviewing the V3 packet.
#: Named here so a test can tell it apart from the fixture above -- the one
#: confusion this module exists to make impossible.
REAL_AUTHORIZATION_ID = "J1-ENV-BUILDER-AUTH-001"
AUTHORIZATION_SHA256 = (
    "86c32cfd4d3e2a48f903f9c61d25dfb377937cd5d9220e4ac9718dd66f84b5e7"
)


# -- reading the packet ----------------------------------------------------


def _packet_text() -> str:
    return PACKET_PATH.read_text(encoding="utf-8")


def _packet_prose() -> str:
    """The packet with runs of whitespace collapsed.

    Prose assertions run against this. A sentence that happens to wrap across
    two lines is the same sentence, and a test that failed on the wrap point
    would be testing the fill width rather than the claim.
    """
    return " ".join(_packet_text().split())


def _field_table() -> dict[str, dict[str, str]]:
    """Parse the packet's own field table. It is the single source of truth."""
    lines = _packet_text().splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.startswith("| Field | Candidate value |"):
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
        f"{field} is {row['status']}, so it carries no verified value"
    )
    return row["value"]


def _git(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(REPOSITORY_ROOT), *arguments],
        capture_output=True,
        check=False,
    )


def _require_commit(commit: str) -> None:
    """Skip visibly rather than pass silently on a shallow checkout."""
    if _git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
        pytest.skip(
            f"commit {commit} is not in this checkout's object store "
            "(shallow clone); the checkout-based digest checks still ran"
        )


# -- V1 and V2 are receipts ------------------------------------------------


@pytest.mark.parametrize("relative,digest", sorted(RETAINED_RECEIPTS.items()))
def test_every_retained_receipt_is_byte_unchanged(
    relative: str, digest: str
) -> None:
    """A receipt that gets updated is not a receipt.

    Each of these carries values or statements the later work superseded. Their
    bytes record what was believed and when, and re-pointing one at current
    values would delete the discrepancy that justified the next round.
    """
    raw = (REPOSITORY_ROOT / relative).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest, relative


def test_v3_names_the_receipts_it_supersedes_with_their_digests() -> None:
    text = _packet_text()
    for relative, digest in RETAINED_RECEIPTS.items():
        assert Path(relative).name in text, relative
        assert digest in text, relative


def test_v3_records_the_lineage_without_rewriting_it() -> None:
    prose = _packet_prose()
    for marker in ("V1 review packet", "#151", "#152", "V3"):
        assert marker in prose, marker
    assert "historical evidence, not current authority" in prose


# -- the packet is not, and cannot become, an authorization ----------------


def test_the_packet_exists_and_is_not_the_canonical_authorization() -> None:
    assert PACKET_PATH.is_file()
    assert PACKET_RELATIVE != BUILDER_AUTHORIZATION_PATH


def test_the_builder_authorization_is_present_and_valid() -> None:
    """Superseded live state, recorded by #154.

    This module asserted absence at every commit up to #154, and the assertion
    was correct each time. It is re-pointed rather than removed: the same
    question asked of the new truth is a stronger check than absence was.
    """
    document = load_builder_authorization(REPOSITORY_ROOT)
    assert document is not None
    verified = verify_builder_authorization(document)
    assert verified.fields["builder_authorization_id"] == REAL_AUTHORIZATION_ID


def test_the_packet_is_still_not_the_authorization() -> None:
    """Two different documents. The packet describes; the JSON authorizes."""
    with pytest.raises(json.JSONDecodeError):
        json.loads(_packet_text())
    assert PACKET_RELATIVE != BUILDER_AUTHORIZATION_PATH
    assert (REPOSITORY_ROOT / BUILDER_AUTHORIZATION_PATH).is_file()


def test_the_authorization_matches_the_packet_it_was_taken_from() -> None:
    """A human may only authorize the object that was reviewed.

    Every machine-verified value in the merged V3 packet must appear unchanged
    in the authorization. A digest quietly differing here would mean the thing
    authorized and the thing reviewed were different objects.
    """
    document = load_builder_authorization(REPOSITORY_ROOT)
    assert document is not None
    table = _field_table()
    for name, row in table.items():
        if row["status"] != "MACHINE-VERIFIED":
            continue
        assert document[name] == row["value"], name


def test_the_authorization_derives_its_own_provenance_destination() -> None:
    """The human chose an id; the destination was not a separate choice."""
    document = load_builder_authorization(REPOSITORY_ROOT)
    assert document is not None
    assert document["provenance_destination"] == durable_evidence_destination(
        document["builder_authorization_id"]
    )


# -- the readiness claim ---------------------------------------------------


def test_the_packet_claims_readiness_only_because_nothing_is_blocked() -> None:
    """The status and the table must agree, or the status is a wish."""
    statuses = [row["status"] for row in _field_table().values()]
    blocked = [s for s in statuses if s == "BLOCKED"]
    text = _packet_text()
    if blocked:
        assert "NOT READY — MACHINE AUTHORITY BLOCKED" in text
    else:
        assert "READY FOR EXPLICIT HUMAN BUILDER-AUTHORIZATION DECISION" in text
    assert not blocked, f"BLOCKED must be 0 for a READY packet, got {len(blocked)}"


def test_the_declared_status_counts_match_the_table() -> None:
    statuses = [row["status"] for row in _field_table().values()]
    counts = {name: statuses.count(name) for name in PERMITTED_STATUSES}
    assert counts == {
        "MACHINE-VERIFIED": 18,
        "HUMAN-DECISION-REQUIRED": 3,
        "HUMAN-DERIVED": 1,
        "BLOCKED": 0,
    }
    text = _packet_text()
    for name, count in counts.items():
        assert f"{name}" in text
        assert f"{count}" in text


def test_the_table_covers_every_schema_field_exactly_once() -> None:
    table = _field_table()
    assert set(table) == set(BUILDER_AUTHORIZATION_FIELDS)
    assert len(table) == len(BUILDER_AUTHORIZATION_FIELDS) == 22


def test_only_the_four_permitted_statuses_appear() -> None:
    for field, row in _field_table().items():
        assert row["status"] in PERMITTED_STATUSES, f"{field}: {row['status']}"


def test_no_pending_status_masquerades_as_authorization_content() -> None:
    for field, row in _field_table().items():
        assert "PENDING" not in row["status"].upper(), field


def test_human_fields_carry_no_value() -> None:
    """A machine may not synthesize a human field, nor predate a timestamp."""
    table = _field_table()
    for field in HUMAN_FIELDS:
        assert table[field]["status"] == "HUMAN-DECISION-REQUIRED", field
        assert table[field]["value"] == UNRESOLVED, field
    verification = table["authorization_timestamp"]["verification"]
    assert "not" in verification and "predated" in verification


def test_the_derived_field_carries_its_rule_and_not_a_literal() -> None:
    """`HUMAN-DERIVED`, because the rule is total: the human picks only the id."""
    row = _field_table()["provenance_destination"]
    assert row["status"] == "HUMAN-DERIVED"
    assert row["value"] == PROVENANCE_RULE
    assert "/" not in row["value"].replace("(", "").replace(")", "")


def test_no_resolved_value_is_a_placeholder() -> None:
    for field, row in _field_table().items():
        if row["value"] == UNRESOLVED:
            continue
        assert row["value"].strip().lower() not in PLACEHOLDER_VALUES, field


# -- machine values, re-derived from outside the packet --------------------


def test_workflow_digest_recomputed_from_the_checkout() -> None:
    raw = (REPOSITORY_ROOT / WORKFLOW_RELATIVE).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == _machine_value("workflow_sha256")


def test_workflow_digest_recomputed_from_the_git_object_store() -> None:
    """V2 could not do this. A commit now holds these bytes as merged history."""
    commit = _machine_value("workflow_review_commit")
    _require_commit(commit)
    completed = _git("cat-file", "blob", f"{commit}:{WORKFLOW_RELATIVE}")
    assert completed.returncode == 0
    assert hashlib.sha256(completed.stdout).hexdigest() == _machine_value(
        "workflow_sha256"
    )


def test_the_review_commit_and_master_hold_one_blob() -> None:
    """Stronger than digest equality: it is git's own identity for the content."""
    commit = _machine_value("workflow_review_commit")
    _require_commit(commit)
    at_commit = _git("rev-parse", f"{commit}:{WORKFLOW_RELATIVE}")
    at_head = _git("rev-parse", f"HEAD:{WORKFLOW_RELATIVE}")
    assert at_commit.returncode == 0 and at_head.returncode == 0
    assert at_commit.stdout.strip() == at_head.stdout.strip()
    assert at_commit.stdout.decode().strip() in _packet_text()


def test_the_commit_fields_are_full_shas_and_are_the_same_commit() -> None:
    review = _machine_value("workflow_review_commit")
    source = _machine_value("authorized_source_commit")
    for value in (review, source):
        assert len(value) == 40
        assert set(value) <= set("0123456789abcdef")
    assert review == source


def test_the_authorized_source_commit_holds_every_build_input() -> None:
    commit = _machine_value("authorized_source_commit")
    _require_commit(commit)
    for relative in BUILD_CONFIGURATION_PATHS.values():
        assert _git("cat-file", "-e", f"{commit}:{relative}").returncode == 0, (
            f"{relative} is absent at the authorized source commit"
        )


def test_no_later_commit_touches_a_build_input() -> None:
    """Authority may not be moved forward silently; here there is nowhere to move."""
    commit = _machine_value("authorized_source_commit")
    _require_commit(commit)
    completed = _git(
        "log",
        "--oneline",
        f"{commit}..HEAD",
        "--",
        "containers/",
        ".github/workflows/",
        "src/cardiosentinel/journal_extension/j1/",
    )
    assert completed.returncode == 0
    assert not completed.stdout.strip(), completed.stdout.decode()


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
    assert result["member_count"] == 7
    # The digested workflow is the reviewed workflow, not a file of the same name.
    assert result["inputs"]["workflow"] == _machine_value("workflow_sha256")


def test_every_member_digest_appears_in_the_packet(tmp_path: Path) -> None:
    """The member table must be the digests that were actually combined."""
    write_dependency_input(REPOSITORY_ROOT, tmp_path)
    paths = {
        name: REPOSITORY_ROOT / relative
        for name, relative in BUILD_CONFIGURATION_PATHS.items()
    }
    paths["dependency_input_pypi"] = tmp_path / "requirements.pypi.txt"
    paths["dependency_input_pytorch"] = tmp_path / "requirements.pytorch-cpu.txt"
    text = _packet_text()
    for role, digest in configuration_digest(paths)["inputs"].items():
        assert digest in text, role


def test_the_derived_dependency_inputs_regenerate_identically(
    tmp_path: Path,
) -> None:
    first = write_dependency_input(REPOSITORY_ROOT, tmp_path / "a")
    second = write_dependency_input(REPOSITORY_ROOT, tmp_path / "b")
    assert first["files"] == second["files"]
    for name in ("requirements.pypi.txt", "requirements.pytorch-cpu.txt"):
        assert (tmp_path / "a" / name).read_bytes() == (
            tmp_path / "b" / name
        ).read_bytes()
    assert sum(first["counts"].values()) == APPROVED_PACKAGE_COUNT


def test_dependency_authority_is_resolved_not_retyped() -> None:
    fields = approved_runtime_fields()
    assert _machine_value("dependency_digest") == APPROVED_DEPENDENCY_DIGEST
    assert (
        _machine_value("dependency_authority_identity")
        == fields["dependency_lock_identity"]
    )
    text = _packet_text()
    assert APPROVED_PYTHON_RUNTIME_IDENTITY in text
    assert str(APPROVED_PACKAGE_COUNT) in text


def test_target_artifact_and_policy_are_the_frozen_constants() -> None:
    assert _machine_value("target_platform") == TARGET_PLATFORM
    assert _machine_value("artifact_type") == ARTIFACT_KIND
    assert _machine_value("qualification_policy") == QUALIFICATION_POLICY
    text = _packet_text()
    assert ARTIFACT_MEDIA_TYPE in text
    assert SINGLE_CLAIM_POLICY in text


def test_the_builder_candidate_id_is_composed_by_the_implementation() -> None:
    """Derived through the repository's own model, not typed into the packet."""
    identity = ControlledBuilderIdentity(
        provider=_machine_value("provider"),
        workflow_repository=_machine_value("repository"),
        workflow_path=_machine_value("workflow_path"),
        workflow_commit=_machine_value("workflow_review_commit"),
        runner_class=_machine_value("runner_class"),
    )
    require_specific_builder_identity(identity)
    assert identity.builder_id == _machine_value("builder_candidate_id")
    assert "j1-environment-build.yml" not in identity.builder_id


def test_the_base_image_is_digest_addressed_and_in_the_protocol() -> None:
    value = _machine_value("base_image_digest")
    repository, separator, digest = value.partition("@sha256:")
    assert separator and repository
    assert len(digest) == 64
    protocol = (REPOSITORY_ROOT / PROTOCOL_RELATIVE).read_text(encoding="utf-8")
    assert value in protocol


def test_the_build_tool_pins_are_in_the_workflow_and_the_packet() -> None:
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


# -- the two claims, proven separately -------------------------------------


def _authorization_from_packet(**overrides: Any) -> dict[str, Any]:
    """Built from the packet's machine-verified rows. Entirely in memory.

    The human fields are unmistakably synthetic, and the derived field is
    computed from the synthetic id by the same function the verifier uses.
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
    document["authorization_timestamp"] = "SYNTHETIC-NOT-AN-AUTHORIZATION-ACT"
    document["human_authorizer_identity"] = "synthetic, not a signatory"
    document.update(overrides)
    return document


def test_every_machine_requirement_can_pass() -> None:
    """Claim one: machine sufficiency. Says nothing about permission."""
    document = _authorization_from_packet()
    assert set(document) == set(BUILDER_AUTHORIZATION_FIELDS)
    verified = verify_builder_authorization(document)
    assert verified.workflow_sha256 == _machine_value("workflow_sha256")


def test_the_machine_values_verify_against_real_git_history() -> None:
    """The strongest form: the reviewed bytes exist at the named commit."""
    commit = _machine_value("workflow_review_commit")
    _require_commit(commit)
    proof = verify_workflow_identity(
        verify_builder_authorization(_authorization_from_packet()),
        repository_root=REPOSITORY_ROOT,
        running_workflow_ref=f"o/r/{WORKFLOW_RELATIVE}@refs/heads/master",
        running_commit=commit,
    )
    declared = _machine_value("workflow_sha256")
    assert proof["workflow_sha256_recomputed_from_review_commit"] == declared
    assert proof["workflow_sha256_recomputed_from_checkout"] == declared
    assert proof["running_commit_descends_from_review_commit"] == "verified"


def test_human_authorization_now_exists_and_a_person_made_it() -> None:
    """Claim two, and it is still a different claim.

    Machine sufficiency was provable before any human acted, and it did not
    create permission. Permission arrived separately, in #154, as a document
    naming a person and a moment.
    """
    document = load_builder_authorization(REPOSITORY_ROOT)
    assert document is not None
    verified = verify_builder_authorization(document)
    identity = str(verified.fields["human_authorizer_identity"])
    assert identity
    assert "synthetic" not in identity.lower()
    assert str(verified.fields["authorization_timestamp"]) != ""


def test_machine_sufficiency_is_not_authorization() -> None:
    """The two claims must not be collapsible into one.

    Still true, and now checkable against a real document beside the fixture:
    the synthetic id is unmistakable, the real one is different, and no fixture
    value leaked into what was actually authorized.
    """
    fixture = _authorization_from_packet()
    assert "SYNTHETIC" in fixture["builder_authorization_id"]
    assert "synthetic" in fixture["human_authorizer_identity"]
    assert fixture["builder_authorization_id"] not in _packet_text()

    real = load_builder_authorization(REPOSITORY_ROOT)
    assert real is not None
    assert real["builder_authorization_id"] != fixture["builder_authorization_id"]
    assert "SYNTHETIC" not in real["builder_authorization_id"].upper()
    assert "synthetic" not in real["human_authorizer_identity"].lower()


def test_a_builder_authorization_does_not_authorize_j1_science() -> None:
    """The invariant that had to survive #154, asserted where it is easiest to lose.

    The builder is authorized. J1 is not. They are different documents verified
    by different code, and the existence of one says nothing about the other.
    """
    assert load_builder_authorization(REPOSITORY_ROOT) is not None
    with pytest.raises(AuthorizationError, match="J1 authorization absent"):
        verify_authorization(None)


@pytest.mark.parametrize("field", HUMAN_FIELDS + DERIVED_FIELDS)
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


def test_a_destination_the_human_chose_freely_is_refused() -> None:
    """The human picks the id; the destination is not a separate choice."""
    with pytest.raises(BuilderAuthorizationError, match="not the destination"):
        verify_builder_authorization(
            _authorization_from_packet(
                provenance_destination="docs/journal-extension/j1/evidence/elsewhere/"
            )
        )


@pytest.mark.parametrize("generic", GENERIC_BUILDER_IDENTITIES)
def test_the_authorization_cannot_broaden_to_a_generic_provider(
    generic: str,
) -> None:
    with pytest.raises(BuilderAuthorizationError, match="names a provider"):
        verify_builder_authorization(_authorization_from_packet(repository=generic))


def test_the_historical_workflow_filename_is_still_refused() -> None:
    wrong = ".github/workflows/j1-environment-build.yml"
    assert not (REPOSITORY_ROOT / wrong).exists()
    with pytest.raises(BuilderAuthorizationError, match="not the controlled"):
        verify_builder_authorization(_authorization_from_packet(workflow_path=wrong))


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


# -- disclosures the packet must keep making -------------------------------


def test_the_residual_trust_statement_is_not_softened() -> None:
    text = _packet_prose()
    for clause in (
        "GitHub remains the external authority for the hosted",
        "run ordering",
        "run-attempt identity",
        "run-list completeness",
        "is not cryptographically reproducible",
        "falsifiable property",
    ):
        assert clause in text, clause


def test_the_packet_does_not_claim_dispatch_prevention() -> None:
    text = _packet_prose()
    assert "not dispatch prevention" in text
    assert "Nothing stops a second dispatch" in text
    assert "detection at evidence preservation" in text


def test_the_packet_states_the_excluded_scope() -> None:
    text = _packet_prose()
    for excluded in (
        "TRAIN access",
        "candidate evaluation",
        "threshold selection",
        "scientific attempt claim",
        "J1 execution",
    ):
        assert excluded in text, excluded


def test_the_packet_poses_the_human_questions_without_answering_them() -> None:
    text = _packet_text()
    assert "HUMAN DECISION REQUIRED" in text
    assert text.count("?") >= 6


# -- negative capability ---------------------------------------------------


def test_authorized_but_nothing_built() -> None:
    """The live state after #154, in one place.

    Authorizing a builder and running it are separate acts, and only the first
    has happened. The JSON that grants permission is the *only* JSON here: an
    evidence directory or a build record appearing beside it would mean the
    second act had occurred too.
    """
    for pattern in ("*.oci.tar", "build-a.json", "build-b.json"):
        assert not list(REPOSITORY_ROOT.glob(pattern)), pattern
    documents = sorted(p.name for p in (REPOSITORY_ROOT / J1_DOCS).glob("*.json"))
    assert documents == [Path(BUILDER_AUTHORIZATION_PATH).name], documents
    assert not (REPOSITORY_ROOT / J1_DOCS / "evidence").exists()


def test_the_authorization_is_unchanged_after_every_test_in_this_module() -> None:
    """No test here may edit the document that grants permission.

    The digest is recomputed at the end and compared against the bytes on disk
    at the start, so a fixture that wrote to the canonical path -- the one
    mistake this module must never make -- shows up as a mismatch.
    """
    raw = (REPOSITORY_ROOT / BUILDER_AUTHORIZATION_PATH).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == AUTHORIZATION_SHA256
    verify_builder_authorization(load_builder_authorization(REPOSITORY_ROOT))
