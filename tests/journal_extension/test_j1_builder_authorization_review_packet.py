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
    build_configuration_digest,
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

PACKET_RELATIVE = f"{J1_DOCS}/J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V4.md"
PACKET_PATH = REPOSITORY_ROOT / PACKET_RELATIVE
#: The act receipt for `J1-ENV-BUILDER-AUTH-002`, recorded from this packet.
ACT_V2_RELATIVE = f"{J1_DOCS}/J1_BUILDER_AUTHORIZATION_ACT_V2.md"
#: The account of what 002's canonical run did. It independently records the
#: Containerfile digest of the object that was actually built.
RECEIPT_002_NAME = "J1_ENV_BUILDER_AUTH_002_POSTCLAIM_FAILURE_RECEIPT.md"
#: The canonical qualification claim run 33902875021 produced under 002, as the
#: provider emitted it. The object identity the build actually used lives here.
COMMITTED_CLAIM_PATH = (
    REPOSITORY_ROOT
    / J1_DOCS
    / "evidence/environment-build/J1-ENV-BUILDER-AUTH-002/j1-qualification-claim.json"
)
#: The source commit retired `J1-ENV-BUILDER-AUTH-001` named. Its tree contains
#: the broken gate and `COPY .` makes the source tree image content, so it must
#: never reappear in a live authorization.
RETIRED_001_SOURCE_COMMIT = "1983616f2021fa5587b7f6cec716501c610e4bf6"
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
    #: V3 joined them here. It was the live packet until the controlled build
    #: dispatched under the authorization it described failed in its gate, and
    #: the remediation changed the source tree it names. Its bytes record the
    #: object that `J1-ENV-BUILDER-AUTH-001` reviewed, and are not rewritten to
    #: the remediation commit.
    f"{J1_DOCS}/J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V3.md": (
        "209cd8689749bdf422d134d974ef0f2a0f286b31478716accce6263c6cb22115"
    ),
    f"{J1_DOCS}/J1_BUILDER_AUTHORIZATION_ACT_V1.md": (
        "7643a81062db0b0294c35334a425509aabfc74f6fc834a64afad7afb242528d6"
    ),
    #: The account of what authorization 001's single dispatch did and did not
    #: do. V4 exists because of it, so it is evidence rather than a draft.
    f"{J1_DOCS}/J1_ENV_BUILDER_AUTH_001_PRECLAIM_FAILURE_RECEIPT.md": (
        "b02e61c14e0384775d586538e9b9dec5ef62a3922177e0dee469f17bb0599460"
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


def _member_table() -> dict[str, str]:
    """The packet's section 7 build-configuration member table, role -> SHA-256.

    Parsed from the packet's own rows for the same reason the field table is:
    the packet is the source of truth for what it reviewed, and a second copy
    written here would be free to disagree with it.
    """
    table: dict[str, str] = {}
    for line in _packet_text().splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        if len(cells) == 3 and cells[1] in {"tracked", "derived"}:
            table[cells[0]] = cells[2]
    return table


def _machine_value_member(role: str) -> str:
    return _member_table()[role]


def _live_containerfile_digest() -> str:
    relative = BUILD_CONFIGURATION_PATHS["containerfile"]
    return hashlib.sha256((REPOSITORY_ROOT / relative).read_bytes()).hexdigest()


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


#: The receipts the live packet must name with their digests. A document cannot
#: name its own digest -- that is the self-reference the freeze receipt records
#: as unsatisfiable -- so the live packet is excluded from its own list.
NAMED_BY_THE_LIVE_PACKET = tuple(
    relative for relative in RETAINED_RECEIPTS if relative != PACKET_RELATIVE
)


def test_the_live_packet_names_every_retained_receipt_with_its_digest() -> None:
    text = _packet_text()
    for relative in NAMED_BY_THE_LIVE_PACKET:
        assert Path(relative).name in text, relative
        assert RETAINED_RECEIPTS[relative] in text, relative


def test_the_live_packet_records_the_lineage_without_rewriting_it() -> None:
    """V4 exists because a signed authorization produced a failed build.

    The lineage must be legible from the packet itself: which authorization,
    what happened to it, and why it may not be reused.
    """
    prose = _packet_prose()
    for marker in (
        "J1-ENV-BUILDER-AUTH-001",
        "PRE_ARTIFACT_INFRASTRUCTURE",
        "claim_recorded = false",
        "33800630377",
        "RETIRED, NOT SPENT",
        "MUST NOT BE REUSED",
    ):
        assert marker in prose, marker


def test_the_live_packet_warns_that_a_matching_config_digest_is_not_enough() -> None:
    """The trap V4 exists to close.

    Nothing in the seven-member configuration changed, so a reader comparing
    digests would conclude nothing had changed -- and could reuse authorization
    001, whose source commit contains the broken gate. The source tree is image
    content, and the packet has to say so where it cannot be missed.
    """
    prose = _packet_prose()
    assert "separately load-bearing" in prose
    assert "COPY . /opt/cardiosentinel/src-tree" in prose
    assert "unchanged build_configuration_digest" in prose


# -- the packet is not, and cannot become, an authorization ----------------


def test_the_packet_exists_and_is_not_the_canonical_authorization() -> None:
    assert PACKET_PATH.is_file()
    assert PACKET_RELATIVE != BUILDER_AUTHORIZATION_PATH


def test_this_packet_still_describes_the_object_002_actually_ran() -> None:
    """V4 is historical now, and it is bound to the run that consumed it.

    The authorization it reviewed is gone -- 002 was spent by run 33902875021
    and retired -- so there is no live document left to compare against. What
    remains checkable is stronger than a document comparison: the qualification
    claim the provider produced carries the object identity the build actually
    used, and it must equal what this packet reviewed. A packet quietly
    re-pointed at some later object would fail here.
    """
    claim = json.loads(COMMITTED_CLAIM_PATH.read_bytes())
    for field in (
        "authorized_source_commit",
        "build_configuration_digest",
        "workflow_sha256",
    ):
        assert claim[field] == _machine_value(field), field
    assert claim["builder_authorization_id"] == "J1-ENV-BUILDER-AUTH-002"
    assert claim["qualification_policy"] == _machine_value("qualification_policy")


def test_the_act_receipt_records_002_and_agrees_with_the_canonical_json() -> None:
    """The act is prose; the JSON authorizes. They must not drift apart.

    Whitespace is normalised before any prose assertion, so a line wrap cannot
    fail a claim, and the id and timestamp are compared against the canonical
    document rather than against a second copy of the prose.
    """
    act = (REPOSITORY_ROOT / ACT_V2_RELATIVE).read_text(encoding="utf-8")
    prose = " ".join(act.split())
    claim = json.loads(COMMITTED_CLAIM_PATH.read_bytes())

    assert "BUILDER AUTHORIZED AS 002 — NO BUILD DISPATCHED" in prose
    assert claim["builder_authorization_id"] in prose
    assert claim["authorized_source_commit"] in prose
    assert "DebalekhaChakraborty" in prose
    assert hashlib.sha256(PACKET_PATH.read_bytes()).hexdigest() in prose

    # 001 is named to be refused, never as something this act may fall back on.
    assert "must never be reused" in prose
    assert "J1-ENV-BUILDER-AUTH-001" in prose

    # The retired commit is refused as a *source* commit only. It remained the
    # legitimate `workflow_review_commit`: the workflow bytes were reviewed
    # there and had not changed, and reviewing bytes is not building a tree.
    # Conflating the two fields is the confusion V4 section 2 exists for.
    assert claim["authorized_source_commit"] != RETIRED_001_SOURCE_COMMIT
    assert _machine_value("workflow_review_commit") == RETIRED_001_SOURCE_COMMIT

    # The act records the state at the moment of authorizing, and is never
    # rewritten by what the build later did. Both were true when it was written.
    assert "No controlled-build workflow was dispatched" in prose
    assert "No qualification claim was recorded" in prose


def test_the_packet_is_not_the_authorization_and_never_was() -> None:
    """Two different documents. The packet describes; the JSON authorizes."""
    with pytest.raises(json.JSONDecodeError):
        json.loads(_packet_text())
    assert PACKET_RELATIVE != BUILDER_AUTHORIZATION_PATH


def test_the_retired_authorizations_id_is_recorded_not_erased() -> None:
    """Removing the active file must not delete the record of what happened."""
    receipt = (
        REPOSITORY_ROOT / J1_DOCS
        / "J1_ENV_BUILDER_AUTH_001_PRECLAIM_FAILURE_RECEIPT.md"
    ).read_text(encoding="utf-8")
    assert REAL_AUTHORIZATION_ID in receipt
    assert AUTHORIZATION_SHA256 in receipt, "the retired bytes must be digest-named"
    assert "33800630377" in receipt
    prose = " ".join(receipt.split())
    assert "WAS NOT SPENT BY QUALIFICATION CLAIM" in prose
    assert "WILL NOT BE REUSED AFTER SOURCE REMEDIATION" in prose


def test_the_provenance_destination_rule_is_unchanged_by_the_retirement() -> None:
    """The rule is a property of the mechanism, not of any one authorization."""
    assert durable_evidence_destination(REAL_AUTHORIZATION_ID).endswith(
        f"{REAL_AUTHORIZATION_ID}/"
    )
    assert _field_table()["provenance_destination"]["value"] == PROVENANCE_RULE


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


def test_the_commit_fields_are_full_shas_and_now_differ() -> None:
    """They were the same commit in V3. They are not any more, and must not be.

    The workflow was deliberately untouched by the remediation, so its review
    commit stands. The source tree moved, so the authorized source commit moved
    with it. An authorization carrying the old source commit would build the
    broken gate into the artifact.
    """
    review = _machine_value("workflow_review_commit")
    source = _machine_value("authorized_source_commit")
    for value in (review, source):
        assert len(value) == 40
        assert set(value) <= set("0123456789abcdef")
    assert review != source


def test_the_review_commit_is_an_ancestor_of_the_source_commit() -> None:
    """The workflow was reviewed before the source it will build was written.

    Split from the shape check above because it needs git history, and `ci.yml`
    checks out at the default depth. The shape and difference of the two commits
    are decidable anywhere; their ancestry is not.
    """
    review = _machine_value("workflow_review_commit")
    source = _machine_value("authorized_source_commit")
    _require_commit(review)
    _require_commit(source)
    assert _git("merge-base", "--is-ancestor", review, source).returncode == 0


def test_the_authorized_source_commit_holds_every_build_input() -> None:
    commit = _machine_value("authorized_source_commit")
    _require_commit(commit)
    for relative in BUILD_CONFIGURATION_PATHS.values():
        assert _git("cat-file", "-e", f"{commit}:{relative}").returncode == 0, (
            f"{relative} is absent at the authorized source commit"
        )


def test_the_build_inputs_moved_and_the_move_is_not_silent() -> None:
    """Authority may not be moved forward *silently*. This move is not silent.

    While 002 was live this asserted that nothing had touched a build input
    since `authorized_source_commit`. The apparatus remediation deliberately
    does touch one -- the Containerfile carried the defect that spent 002 -- so
    the guarantee changes shape rather than being deleted:

    # SOURCE IDENTITY CHANGED -- RE-DERIVATION REQUIRED

    What must remain true is that the divergence is *visible*: the live
    configuration no longer matches the packet, exactly one member accounts for
    it, and the workflow is not among the things that moved. None of those need
    git history, so this never skips; where history is present it also names the
    commits responsible.
    """
    assert _live_containerfile_digest() != _machine_value_member("containerfile")
    assert _machine_value_member("workflow") == hashlib.sha256(
        (REPOSITORY_ROOT / WORKFLOW_RELATIVE).read_bytes()
    ).hexdigest()

    commit = _machine_value("authorized_source_commit")
    if _git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
        return  # shallow checkout: the divergence checks above still ran

    workflow_changes = _git(
        "log", "--oneline", f"{commit}..HEAD", "--", ".github/workflows/"
    )
    assert workflow_changes.returncode == 0
    assert not workflow_changes.stdout.strip(), (
        "the controlled workflow's directory moved, which this repair must not "
        "do: " + workflow_changes.stdout.decode()
    )

    container_changes = _git(
        "log", "--oneline", f"{commit}..HEAD", "--", "containers/"
    )
    assert container_changes.returncode == 0
    assert container_changes.stdout.strip(), (
        "the Containerfile repair is missing from history between the "
        "authorized source commit and HEAD"
    )


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


def _live_configuration(tmp_path: Path) -> dict[str, Any]:
    """The seven-member configuration of the working tree, recomputed."""
    write_dependency_input(REPOSITORY_ROOT, tmp_path)
    paths = {
        name: REPOSITORY_ROOT / relative
        for name, relative in BUILD_CONFIGURATION_PATHS.items()
    }
    paths["dependency_input_pypi"] = tmp_path / "requirements.pypi.txt"
    paths["dependency_input_pytorch"] = tmp_path / "requirements.pytorch-cpu.txt"
    assert set(paths) == set(REQUIRED_BUILD_CONFIGURATION_INPUTS)
    return configuration_digest(paths)


def test_the_live_configuration_has_moved_away_from_what_v4_reviewed(
    tmp_path: Path,
) -> None:
    """The apparatus remediation changed the object, and V4 is not rewritten.

    V4 describes what `J1-ENV-BUILDER-AUTH-002` authorized. That authorization
    is spent and the Containerfile has since been repaired, so the working tree
    is a *different* build configuration and this must say so out loud.

    # SOURCE IDENTITY CHANGED -- RE-DERIVATION REQUIRED

    Six members are still what V4 recorded; only `containerfile` moved. That is
    the whole remediation, and a second member drifting here would mean the
    change was not the single-defect repair it claims to be.
    """
    result = _live_configuration(tmp_path)
    assert result["member_count"] == 7
    assert result["build_configuration_digest"] != _machine_value(
        "build_configuration_digest"
    )
    assert result["inputs"]["containerfile"] != _machine_value_member(
        "containerfile"
    )
    for role in REQUIRED_BUILD_CONFIGURATION_INPUTS:
        if role == "containerfile":
            continue
        assert result["inputs"][role] == _machine_value_member(role), role
    # The workflow is untouched by this repair and is still the reviewed one.
    assert result["inputs"]["workflow"] == _machine_value("workflow_sha256")


def test_v4_still_describes_the_configuration_it_reviewed() -> None:
    """What V4 reviewed is cross-checked against the record of what ran.

    Deliberately written so it **never skips**. The obvious form -- recompute
    every member from git at `authorized_source_commit` -- needs history the CI
    checkout does not have, and a check that only runs on a developer's machine
    is the failure ECG 29 named. So the always-available evidence comes first:

    - the `containerfile` digest V4 recorded is the one the 002 post-claim
      failure receipt independently records for the object that was built;
    - the six members this repair did not touch are still on disk unchanged.

    Where git history *is* present the stronger check runs as well, but its
    absence weakens this test rather than silencing it.
    """
    receipt = " ".join(
        (REPOSITORY_ROOT / J1_DOCS / RECEIPT_002_NAME).read_text(
            encoding="utf-8"
        ).split()
    )
    reviewed_containerfile = _machine_value_member("containerfile")
    assert reviewed_containerfile in receipt

    for role, relative in BUILD_CONFIGURATION_PATHS.items():
        if role == "containerfile":
            continue  # repaired; the live value is asserted to differ above
        on_disk = hashlib.sha256(
            (REPOSITORY_ROOT / relative).read_bytes()
        ).hexdigest()
        assert on_disk == _machine_value_member(role), role

    commit = _machine_value("authorized_source_commit")
    if _git("cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
        return  # shallow checkout: the checks above still ran
    for role, relative in BUILD_CONFIGURATION_PATHS.items():
        completed = _git("cat-file", "blob", f"{commit}:{relative}")
        assert completed.returncode == 0, relative
        recomputed = hashlib.sha256(completed.stdout).hexdigest()
        assert recomputed == _machine_value_member(role), role


def test_every_member_digest_in_the_packet_is_a_digest_it_combined(
    tmp_path: Path,
) -> None:
    """The member table must still be internally consistent.

    Recomputing the packet's own recorded members must reproduce the packet's
    own recorded configuration digest. This needs no git history and no working
    tree, so it keeps holding after the tree moves on.
    """
    recorded = {
        role: _machine_value_member(role)
        for role in REQUIRED_BUILD_CONFIGURATION_INPUTS
    }
    assert build_configuration_digest(recorded) == _machine_value(
        "build_configuration_digest"
    )
    text = _packet_text()
    for role, digest in recorded.items():
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


def test_machine_sufficiency_is_still_not_authorization() -> None:
    """The claim that survived an authorization arriving, being retired, and 002.

    Every machine rule remains satisfiable by a document no human ever signed.
    Passing the verifier is therefore not what makes 002 an authorization; the
    human fields are, and the synthetic fixture has none of them. Permission now
    exists, and it is a *different document* -- which is the point.
    """
    fixture = _authorization_from_packet()
    assert "SYNTHETIC" in fixture["builder_authorization_id"]
    assert "synthetic" in fixture["human_authorizer_identity"]
    assert fixture["builder_authorization_id"] not in _packet_text()
    verify_builder_authorization(fixture)
    assert load_builder_authorization(REPOSITORY_ROOT) is None


def test_j1_science_is_unauthorized_independently_of_the_builder() -> None:
    """Two authorizations, two documents, two verifiers.

    This held while a builder authorization existed and holds now that none
    does. One says nothing about the other, in either direction.
    """
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


def test_nothing_was_built_and_no_evidence_directory_exists() -> None:
    """One dispatch happened and produced nothing. That is the whole record.

    Run 33800630377 failed in its gate, so there is no claim, no build record,
    no archive and no evidence directory. The one JSON under the J1 documents is
    the canonical authorization itself; authorizing a builder produced no
    evidence, which is exactly what an authorization is not allowed to do.
    """
    for pattern in ("*.oci.tar", "build-a.json", "build-b.json"):
        assert not list(REPOSITORY_ROOT.glob(pattern)), pattern
    # No JSON sits directly under the J1 documents: the authorization was
    # removed when 002 was retired, and the claim lives under `evidence/`.
    assert not list((REPOSITORY_ROOT / J1_DOCS).glob("*.json"))
    evidence = REPOSITORY_ROOT / J1_DOCS / "evidence"
    preserved = sorted(p.name for p in evidence.rglob("*") if p.is_file())
    assert preserved == ["j1-qualification-claim.json"], preserved


def test_the_gate_still_refuses_after_every_test_in_this_module() -> None:
    """Nothing above wrote an authorization to disk.

    Every synthetic document in this module is built and verified in memory. If
    one had ever been written to the canonical path, this would admit.
    """
    assert not (REPOSITORY_ROOT / BUILDER_AUTHORIZATION_PATH).exists()
    with pytest.raises(BuilderAuthorizationError, match="authorization absent"):
        verify_builder_authorization(load_builder_authorization(REPOSITORY_ROOT))
