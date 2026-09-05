"""The terminal outcome of qualification 003, and the state it leaves behind.

**No builder is authorized, no image exists, and J1 science remains
unauthorized.** Run `33984680149` admitted at its gate, recorded the canonical
qualification claim, and then failed in both builds -- this time on a dependency
the configured source did not supply.

Three authorizations, three lifecycles, and the differences are load-bearing:

```text
001  gate refused, no claim        PRE_ARTIFACT_INFRASTRUCTURE
                                   RETIRED, NOT SPENT
002  claim recorded, builds failed POST_CLAIM_PRE_ARTIFACT   (pip CLI syntax)
                                   SPENT, RETIRED
003  claim recorded, builds failed POST_CLAIM_PRE_ARTIFACT   (dependency source)
                                   SPENT, RETIRED
```

**002 and 003 share a failure class and do not share a cause.** The #159
apparatus repair worked: pip parsed its arguments and resolved 128 packages
before stopping on `incident-management==0.1.0`, which is present in all three
frozen locks and was not supplied by the configured source. Whether it is
obtainable elsewhere is not something this run tested.

This module asserts the preserved record, never a live authorization -- there
is none.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from cardiosentinel.journal_extension.j1 import preflight
from cardiosentinel.journal_extension.j1.approved_runtime import (
    ESTABLISHING_EXPERIMENT_LOCKS,
)
from cardiosentinel.journal_extension.j1.authorization import (
    AuthorizationError,
    verify_authorization,
)
from cardiosentinel.journal_extension.j1.builder_authorization import (
    BUILDER_AUTHORIZATION_PATH,
    BuilderAuthorizationError,
    load_builder_authorization,
    verify_builder_authorization,
)
from cardiosentinel.journal_extension.j1.qualification import (
    DURABLE_EVIDENCE_ROOT,
    POST_CLAIM_PRE_ARTIFACT,
    PRE_ARTIFACT_INFRASTRUCTURE,
    QualificationError,
    durable_evidence_destination,
    require_canonical_qualification_run,
    require_retry_permitted,
    verify_qualification_claim,
)

REPOSITORY_ROOT = Path(preflight.J1_PACKAGE_ROOT).parents[3]
J1_DOCS = REPOSITORY_ROOT / "docs/journal-extension/j1"

AUTHORIZATION_001 = "J1-ENV-BUILDER-AUTH-001"
AUTHORIZATION_002 = "J1-ENV-BUILDER-AUTH-002"
AUTHORIZATION_003 = "J1-ENV-BUILDER-AUTH-003"

CANONICAL_RUN_ID = "33984680149"
CANONICAL_RUN_NUMBER = "3"
CANONICAL_RUN_ATTEMPT = "1"
RUN_002_ID = "33902875021"
RUN_001_ID = "33800630377"

#: The unresolvable requirement. Named here because the whole finding is that it
#: is in the historical evidence, not invented by the generator.
UNRESOLVED_REQUIREMENT = "incident-management"
UNRESOLVED_VERSION = "0.1.0"

CLAIM_003_PATH = (
    REPOSITORY_ROOT
    / durable_evidence_destination(AUTHORIZATION_003)
    / "j1-qualification-claim.json"
)
CLAIM_003_SHA256 = (
    "a1b5e0ac035b1d1cf37e2959466c8b4eb52124c90dbadefad0b42a2d2198df13"
)
CLAIM_002_PATH = (
    REPOSITORY_ROOT
    / durable_evidence_destination(AUTHORIZATION_002)
    / "j1-qualification-claim.json"
)

RECEIPT_001 = J1_DOCS / "J1_ENV_BUILDER_AUTH_001_PRECLAIM_FAILURE_RECEIPT.md"
RECEIPT_002 = J1_DOCS / "J1_ENV_BUILDER_AUTH_002_POSTCLAIM_FAILURE_RECEIPT.md"
RECEIPT_003 = J1_DOCS / "J1_ENV_BUILDER_AUTH_003_POSTCLAIM_FAILURE_RECEIPT.md"
DIAGNOSTIC_003 = J1_DOCS / "J1_ENV_BUILDER_AUTH_003_LOCAL_ORIGIN_DIAGNOSTIC.md"
CORRECTION_003 = J1_DOCS / "J1_ENV_BUILDER_AUTH_003_EVIDENTIARY_CORRECTION.md"

#: The PR #162 merge, where the overbroad wording was merged and still lives.
PR_162_MERGE_COMMIT = "b0ddc50dba32172ae0b32e44ccf26d82c209db5c"

#: Universal negatives one query against one configured source cannot support.
#: These are claims *we* would be making, not provider output we quote.
UNIVERSAL_NEGATIVES = (
    "any public index",
    "never existed on any index",
    "not obtainable anywhere",
    "globally unavailable",
    "no distribution exists",
    "unresolvable anywhere",
    "safe to remove",
)

#: Documents whose bytes are the record. Retiring 003 revises none of them.
PINNED_BYTES = {
    "J1_BUILDER_AUTHORIZATION_ACT_V3.md": (
        "38b54e57a7b688da0c200c908f43577a1d7bf8dc7c5372fe8fac629d67f9acff"
    ),
    "J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V5.md": (
        "f27085c39fe518c315f3f2c405e938d45ab70281a40806635aec8932ca8f1f7a"
    ),
}

#: The three establishing locks, as they stood before this preservation.
PINNED_LOCKS = {
    "B4B_cnn_transformer_v1": (
        "5bf251780f469115164d61a3f3cef2eecfc9ef9765af3f544479e961da00e7bc"
    ),
    "P1B_phys_fusion_v1": (
        "fdde6475a02e0249e0238b89168e6b043b3ade1ec2bfd75922628127fb27d2ca"
    ),
    "M1L_long_memory_v2": (
        "6aa199ea5410dde860fd3fcce9ceef0194a364ed2ed5b01678e0648fea60a452"
    ),
}


def _prose(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _lock_packages(relative: str) -> list[dict[str, str]]:
    document = json.loads((REPOSITORY_ROOT / relative).read_text(encoding="utf-8"))

    def find(node: object, key: str) -> object:
        if isinstance(node, dict):
            if key in node:
                return node[key]
            for value in node.values():
                found = find(value, key)
                if found is not None:
                    return found
        return None

    packages = find(document, "packages") or find(document, "installed_packages")
    assert packages is not None, relative
    return list(packages)


# -- 1. the canonical authorization file is gone ---------------------------


def test_the_canonical_003_authorization_file_is_absent() -> None:
    """003 is spent, so the document that authorized it is removed."""
    assert not (REPOSITORY_ROOT / BUILDER_AUTHORIZATION_PATH).exists()
    assert load_builder_authorization(REPOSITORY_ROOT) is None
    with pytest.raises(BuilderAuthorizationError, match="authorization absent"):
        verify_builder_authorization(load_builder_authorization(REPOSITORY_ROOT))


# -- 2 & 3. the act and the packet are history and stay byte-identical ------


@pytest.mark.parametrize("name,digest", sorted(PINNED_BYTES.items()))
def test_the_authorizing_documents_are_byte_unchanged(
    name: str, digest: str
) -> None:
    """The act recorded a decision; V5 recorded the object. Neither is revised.

    Act V3 says no build was dispatched, which was true when it was written. A
    later dispatch does not make it false; it makes it the record of a moment.
    """
    raw = (J1_DOCS / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest, name


# -- 4, 5 & 6. the claim is preserved, verifies, and is canonical -----------


def test_the_003_claim_is_preserved_at_the_derived_destination() -> None:
    assert CLAIM_003_PATH.is_file()
    assert CLAIM_003_PATH.parent == (
        REPOSITORY_ROOT / durable_evidence_destination(AUTHORIZATION_003)
    )
    raw = CLAIM_003_PATH.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CLAIM_003_SHA256


def test_the_003_claim_verifies_and_names_the_canonical_run() -> None:
    document = json.loads(CLAIM_003_PATH.read_bytes())
    verify_qualification_claim(document)
    assert document["builder_authorization_id"] == AUTHORIZATION_003
    assert document["workflow_run_id"] == CANONICAL_RUN_ID
    assert document["workflow_run_number"] == CANONICAL_RUN_NUMBER
    assert document["workflow_run_attempt"] == CANONICAL_RUN_ATTEMPT


def test_the_003_claim_is_canonical_and_002_does_not_compete() -> None:
    """Canonicality is scoped by `builder_authorization_id`, in code.

    002's claim carries an earlier run id. If scoping were prose rather than
    implementation, it would displace 003's claim here.
    """
    claim_003 = verify_qualification_claim(json.loads(CLAIM_003_PATH.read_bytes()))
    claim_002 = verify_qualification_claim(json.loads(CLAIM_002_PATH.read_bytes()))
    result = require_canonical_qualification_run(
        claim=claim_003, observed_claims=[claim_002, claim_003]
    )
    assert result["claims_observed"] == 1
    assert str(result["canonical_run_id"]) == CANONICAL_RUN_ID
    assert str(result["canonical_run_attempt"]) == CANONICAL_RUN_ATTEMPT


# -- 7 & 9. the receipt records the class, and refuses the wrong ones -------


def test_the_receipt_records_the_failure_class_and_run() -> None:
    receipt = _prose(RECEIPT_003)
    assert AUTHORIZATION_003 in receipt
    assert CANONICAL_RUN_ID in receipt
    assert POST_CLAIM_PRE_ARTIFACT in receipt
    assert "claim_recorded = true" in receipt
    assert "authorization_spent = true" in receipt
    assert "reproducibility_classification = NONE" in receipt


def test_the_outcome_is_not_labelled_with_any_other_class() -> None:
    """No manifest existed, so reproducibility was never observed.

    `DIVERGED` and `ARTIFACT_VISIBLE` would assert artifacts existed;
    `PRE_ARTIFACT_INFRASTRUCTURE` would assert no claim was recorded. All three
    are false, and each would send a future reader somewhere different.
    """
    for line in RECEIPT_003.read_text(encoding="utf-8").splitlines():
        stripped = line.strip().strip("`")
        assert stripped != "reproducibility_classification = BIT_REPRODUCIBLE"
        assert stripped != "reproducibility_classification = DIVERGED"
        assert stripped != "reproducibility_classification = ARTIFACT_VISIBLE"
        assert stripped != f"failure_class = {PRE_ARTIFACT_INFRASTRUCTURE}"


def test_the_receipt_records_the_exact_resolution_failure() -> None:
    receipt = _prose(RECEIPT_003)
    assert f"{UNRESOLVED_REQUIREMENT}=={UNRESOLVED_VERSION}" in receipt
    assert "No matching distribution found" in receipt
    assert "from versions: none" in receipt


def test_the_receipt_distinguishes_the_002_cause_from_the_003_cause() -> None:
    """The apparatus repair worked. Saying otherwise would waste the next audit."""
    receipt = _prose(RECEIPT_003)
    assert "--require-hashes" in receipt
    assert "invalid pip CLI syntax" in receipt
    assert "dependency-source authority" in receipt


def test_the_receipt_does_not_call_the_dependency_digest_false() -> None:
    """The digest is not falsified; the *sufficiency* of the evidence is."""
    receipt = _prose(RECEIPT_003)
    assert "b0fd6eaa" in receipt
    assert "remains the valid digest" in receipt
    assert "not, by itself, a reconstructible dependency-source authority" in receipt


def test_the_receipt_declares_003_spent_and_never_reusable() -> None:
    receipt = _prose(RECEIPT_003)
    assert "AUTHORIZATION 003 IS SPENT AND MUST NEVER BE REUSED" in receipt
    headings = [
        line.strip().lstrip("#").strip().strip("`").upper()
        for line in RECEIPT_003.read_text(encoding="utf-8").splitlines()
        if line.startswith("#")
    ]
    assert any("NO RETRY" in heading for heading in headings)
    for heading in headings:
        assert "RETRY-ELIGIBLE" not in heading, heading


def test_the_repository_itself_refuses_a_retry_of_003() -> None:
    with pytest.raises(QualificationError, match="retry is not permitted"):
        require_retry_permitted(POST_CLAIM_PRE_ARTIFACT, claim_recorded=True)


# -- 8. nothing that never existed was invented -----------------------------


def test_no_build_record_or_archive_is_committed() -> None:
    """Two claims, and nothing beside them. Three dispatches produced no artifact."""
    evidence = REPOSITORY_ROOT / DURABLE_EVIDENCE_ROOT
    preserved = sorted(p.name for p in evidence.rglob("*") if p.is_file())
    assert preserved == [
        "j1-qualification-claim.json",
        "j1-qualification-claim.json",
    ], preserved


@pytest.mark.parametrize(
    "pattern",
    ["*.oci.tar", "build-a.json", "build-b.json", "j1-reproducibility*.json"],
)
def test_no_build_output_exists_anywhere(pattern: str) -> None:
    assert not list(REPOSITORY_ROOT.rglob(pattern)), pattern


def test_the_receipt_states_the_absences_rather_than_implying_them() -> None:
    receipt = _prose(RECEIPT_003)
    for absence in (
        "manifest A = ABSENT",
        "manifest B = ABSENT",
        "OCI archive A = ABSENT",
        "OCI archive B = ABSENT",
        "BUILD_A provenance = ABSENT",
        "BUILD_B provenance = ABSENT",
        "artifact validation = NOT REACHED",
    ):
        assert absence in receipt, absence


# -- 13 & 14. the locks carry the requirement, and are unmodified ----------


@pytest.mark.parametrize("relative", sorted(ESTABLISHING_EXPERIMENT_LOCKS))
def test_every_establishing_lock_still_contains_the_requirement(
    relative: str,
) -> None:
    """The generator did not invent it -- it is in the historical snapshot."""
    packages = _lock_packages(relative)
    assert len(packages) == 335
    matches = [
        entry
        for entry in packages
        if str(entry.get("name", entry)).lower().replace("_", "-")
        == UNRESOLVED_REQUIREMENT
    ]
    assert len(matches) == 1, relative
    assert matches[0]["version"] == UNRESOLVED_VERSION


@pytest.mark.parametrize("relative", sorted(ESTABLISHING_EXPERIMENT_LOCKS))
def test_every_establishing_lock_is_byte_unchanged(relative: str) -> None:
    """Preservation must not edit the evidence it preserves."""
    label = relative.split("/")[-2]
    raw = (REPOSITORY_ROOT / relative).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PINNED_LOCKS[label], label


def test_the_receipt_names_all_three_locks_with_their_digests() -> None:
    receipt = _prose(RECEIPT_003)
    for label, digest in PINNED_LOCKS.items():
        assert label in receipt, label
        assert digest in receipt, label


# -- 7 (task). the package is NOT yet declared extraneous ------------------


def test_the_receipt_does_not_declare_the_requirement_removable() -> None:
    """The next audit's question, deliberately left open.

    Concluding "safe to remove" from a build log and a filesystem observation is
    the shortcut this programme exists to refuse.
    """
    receipt = _prose(RECEIPT_003)
    assert "has not yet been established" in receipt
    assert "DOES NOT CONCLUDE THAT THE PACKAGE MAY BE REMOVED" in receipt.upper()
    lowered = receipt.lower()
    assert "safe to remove" not in lowered
    assert "may be removed from" not in lowered


def test_the_local_origin_evidence_is_kept_separate_and_labelled() -> None:
    """A filesystem observation is not repository-proven provenance.

    It is preserved -- with the `.pth` digest, its contents and the editable
    `direct_url.json` -- in its own document, precisely so it cannot be read as
    canonical lineage.
    """
    assert DIAGNOSTIC_003.is_file()
    diagnostic = _prose(DIAGNOSTIC_003)
    assert "LOCAL OBSERVATION — NOT REPOSITORY-PROVEN PROVENANCE" in diagnostic
    assert "932993476c98d54372180e3ce0b48bec52c712065460ef45853917680d0ed7c6" in (
        diagnostic
    )
    assert '"editable": true' in diagnostic
    assert "was not imported and not executed" in diagnostic
    assert "does not establish that the package is extraneous" in diagnostic.lower()


# -- the claim boundary, which must not regress ----------------------------


@pytest.mark.parametrize("document", [RECEIPT_003, DIAGNOSTIC_003])
@pytest.mark.parametrize("phrase", UNIVERSAL_NEGATIVES)
def test_no_universal_negative_is_asserted(document: Path, phrase: str) -> None:
    """One query against one configured source cannot support a universal negative.

    Qualification 003 established that `incident-management==0.1.0` was not
    supplied by the configured package source on the authorized reconstruction
    path. It established nothing about other public indices, private indices,
    historical repositories or source archives -- and the record must not claim
    otherwise.
    """
    assert phrase not in _prose(document).lower(), f"{document.name}: {phrase}"


@pytest.mark.parametrize("document", [RECEIPT_003, DIAGNOSTIC_003])
def test_the_bounded_claim_is_stated_positively(document: Path) -> None:
    """Bounding must not become vagueness: the real finding still has to be there."""
    prose = _prose(document).lower()
    assert "configured" in prose
    assert any(
        marker in prose
        for marker in ("reconstruction path", "package source", "package index")
    )


def test_the_provider_error_is_quoted_verbatim() -> None:
    """Provider output is evidence. Only our interpretation of it was bounded."""
    receipt = _prose(RECEIPT_003)
    assert (
        "Could not find a version that satisfies the requirement "
        "incident-management==0.1.0 (from versions: none)"
    ) in receipt
    assert "No matching distribution found for incident-management==0.1.0" in receipt


def test_the_local_diagnostic_bounds_its_publication_history_claim() -> None:
    """A `direct_url.json` says how *this* environment got the distribution.

    It carries no information about publication history anywhere else, and the
    diagnostic must say so rather than inferring one.
    """
    prose = _prose(DIAGNOSTIC_003)
    assert "editable installation sourced from a local filesystem path" in prose
    assert (
        "does not establish whether the same distribution name/version exists, "
        "existed, or was obtainable through any package index or other repository"
    ) in prose


# -- the correction is dated, attributed, and not mistaken for the original --


def test_the_correction_document_names_the_merge_it_corrects() -> None:
    """So it can never be read as original contemporaneous evidence."""
    assert CORRECTION_003.is_file()
    prose = _prose(CORRECTION_003)
    assert PR_162_MERGE_COMMIT in prose
    assert "CLAIM-BOUNDARY CORRECTION, NOT A CHANGE TO THE FAILURE OUTCOME" in prose


def test_the_correction_leaves_the_qualification_outcome_alone() -> None:
    """Bounding a claim must not quietly relitigate the outcome it describes."""
    prose = _prose(CORRECTION_003)
    # `_prose` collapses whitespace, so the aligned blocks lose their padding.
    assert f"failure_class = {POST_CLAIM_PRE_ARTIFACT}" in prose
    assert "reproducibility_classification = NONE" in prose
    assert "authorization_spent = true" in prose
    assert "claim_recorded = true" in prose
    assert "SPENT, RETIRED, NOT REUSABLE" in prose
    assert "b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a" in prose
    assert "remains the valid digest" in prose
    assert "not** the V2" in prose or "is **not** the V2" in prose


# -- 15. the three lifecycles stay distinguishable -------------------------


def test_the_three_authorizations_are_still_distinguishable() -> None:
    """One fact separates them, and it decides reusability. Do not lose it."""
    receipt_001 = _prose(RECEIPT_001)
    receipt_002 = _prose(RECEIPT_002)
    receipt_003 = _prose(RECEIPT_003)

    assert "claim_recorded = false" in receipt_001
    assert PRE_ARTIFACT_INFRASTRUCTURE in receipt_001
    assert "authorization_spent = true" in receipt_002
    assert "authorization_spent = true" in receipt_003

    # Earlier receipts are never rewritten by what followed them.
    for earlier in (receipt_001, receipt_002):
        assert AUTHORIZATION_003 not in earlier
        assert CANONICAL_RUN_ID not in earlier
    assert RUN_001_ID not in receipt_002 or AUTHORIZATION_001 in receipt_002

    # 003 names its predecessors only to distinguish itself from them.
    assert AUTHORIZATION_001 in receipt_003
    assert AUTHORIZATION_002 in receipt_003
    assert RUN_002_ID in receipt_003


# -- 10, 11 & 12. the scientific boundary is untouched --------------------


def test_no_environment_authority_or_scientific_authorization_exists() -> None:
    with pytest.raises(AuthorizationError, match="J1 authorization absent"):
        verify_authorization(None)
    assert not list(J1_DOCS.glob("*ENVIRONMENT_AUTHORITY_RECORD*"))
    assert not list(J1_DOCS.glob("*ATTEMPT*"))
    assert not list(J1_DOCS.glob("*.json"))
