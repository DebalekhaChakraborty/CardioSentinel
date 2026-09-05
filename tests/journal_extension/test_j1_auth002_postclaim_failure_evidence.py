"""The terminal outcome of qualification 002, and the state it leaves behind.

**No builder is authorized, no workflow is dispatched, and no image is built.**
Run `33902875021` admitted at its gate, recorded the canonical qualification
claim, and then failed in both builds before either produced an artifact.

Two failures now exist in this programme's history and they must never be
conflated, because exactly one fact separates them and that fact decides whether
an authorization can ever be used again:

```text
001  gate refused          -> no claim      -> PRE_ARTIFACT_INFRASTRUCTURE
                                            -> RETIRED, NOT SPENT
002  gate admitted, claimed -> builds failed -> POST_CLAIM_PRE_ARTIFACT
                                            -> SPENT, RETIRED
```

The claim preserved here is the provider's own bytes, byte-identical to the
artifact `33902875021` uploaded. Nothing beside it was fabricated: there is no
BUILD_A record, no BUILD_B record, no OCI archive and no reproducibility record,
because none of those ever existed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from cardiosentinel.journal_extension.j1 import preflight
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

AUTHORIZATION_002 = "J1-ENV-BUILDER-AUTH-002"
AUTHORIZATION_001 = "J1-ENV-BUILDER-AUTH-001"

#: The canonical run under 002. Recorded a claim, then failed pre-artifact.
CANONICAL_RUN_ID = "33902875021"
CANONICAL_RUN_NUMBER = "2"
CANONICAL_RUN_ATTEMPT = "1"

#: 001's run. Never reached a claim, so it does not compete for canonicality.
RUN_001_ID = "33800630377"

ACT_V2_PATH = J1_DOCS / "J1_BUILDER_AUTHORIZATION_ACT_V2.md"
#: The act records the moment of authorizing and is never rewritten by what the
#: build later did. Pinned so a later session cannot quietly restate it.
ACT_V2_SHA256 = "c37209a901599f76061046049e50adfde8a207a64a10081be1f61d0acd539719"

RECEIPT_002_PATH = J1_DOCS / "J1_ENV_BUILDER_AUTH_002_POSTCLAIM_FAILURE_RECEIPT.md"
RECEIPT_001_PATH = J1_DOCS / "J1_ENV_BUILDER_AUTH_001_PRECLAIM_FAILURE_RECEIPT.md"

CLAIM_PATH = (
    REPOSITORY_ROOT
    / durable_evidence_destination(AUTHORIZATION_002)
    / "j1-qualification-claim.json"
)
#: SHA-256 of the provider's claim bytes, recomputed from the downloaded
#: artifact rather than accepted from the provider's declared digest.
CLAIM_SHA256 = "75716bd87552c3a36d2b1f8915778621d2409eac9e66179c13cb1c1b8c6a0236"


def _prose(path: Path) -> str:
    """Whitespace-normalised text.

    Prose assertions run against this: a sentence that happens to wrap is the
    same sentence, and a test failing on the fill width tests nothing.
    """
    return " ".join(path.read_text(encoding="utf-8").split())


# -- 1. the canonical authorization file is gone ---------------------------


def test_the_canonical_authorization_is_no_longer_002() -> None:
    """002 is spent, so the document that authorized it is gone for good.

    003 succeeded it over a new lineage and has since been spent and retired
    too, so no authorization is live. What must never become true is that the
    canonical path names 002 -- or 001 -- again.
    """
    assert not (REPOSITORY_ROOT / BUILDER_AUTHORIZATION_PATH).exists()
    assert load_builder_authorization(REPOSITORY_ROOT) is None
    with pytest.raises(BuilderAuthorizationError, match="authorization absent"):
        verify_builder_authorization(None)


# -- 2. the act receipt is history and stays byte-identical -----------------


def test_the_act_v2_receipt_is_byte_unchanged() -> None:
    """The act recorded a human decision. Retiring 002 does not revise it.

    It said "no build dispatched", which was true when it was written. A later
    dispatch does not make it false; it makes it the record of a moment.
    """
    assert ACT_V2_PATH.is_file()
    assert hashlib.sha256(ACT_V2_PATH.read_bytes()).hexdigest() == ACT_V2_SHA256


# -- 3. the failure receipt names the authorization and the run -------------


def test_the_failure_receipt_names_002_and_the_canonical_run() -> None:
    receipt = _prose(RECEIPT_002_PATH)
    assert AUTHORIZATION_002 in receipt
    assert CANONICAL_RUN_ID in receipt
    assert f"workflow_run_number = {CANONICAL_RUN_NUMBER}" in receipt
    assert f"workflow_run_attempt = {CANONICAL_RUN_ATTEMPT}" in receipt
    assert POST_CLAIM_PRE_ARTIFACT in receipt


def test_the_failure_receipt_records_the_root_cause_verbatim() -> None:
    """The defect is quoted, and located in the authorized source."""
    receipt = _prose(RECEIPT_002_PATH)
    assert "--require-hashes option does not take a value" in receipt
    assert "--require-hashes=false" in receipt
    assert "containers/j1-environment/Containerfile" in receipt
    assert "8c7a385ddd60072abaf8fd2cfe493f1cefe12885" in receipt


def test_the_receipt_records_the_provider_artifact_identity() -> None:
    """A claim without its provider identity cannot be traced back."""
    receipt = _prose(RECEIPT_002_PATH)
    assert "9948308402" in receipt
    assert CLAIM_SHA256 in receipt


# -- 4 & 5. the committed claim is the provider's, and is run 2 / attempt 1 -


def test_the_committed_claim_verifies() -> None:
    """The repository's own verifier accepts the preserved bytes."""
    raw = CLAIM_PATH.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CLAIM_SHA256
    claim = verify_qualification_claim(json.loads(raw))
    assert claim is not None


def test_the_committed_claim_names_002_and_the_canonical_run() -> None:
    document = json.loads(CLAIM_PATH.read_bytes())
    assert document["builder_authorization_id"] == AUTHORIZATION_002
    assert document["workflow_run_id"] == CANONICAL_RUN_ID
    assert document["workflow_run_number"] == CANONICAL_RUN_NUMBER
    assert document["workflow_run_attempt"] == CANONICAL_RUN_ATTEMPT


def test_the_claim_is_canonical_for_002() -> None:
    """One claim was observed under this authorization, and it is this one."""
    claim = verify_qualification_claim(json.loads(CLAIM_PATH.read_bytes()))
    result = require_canonical_qualification_run(
        claim=claim, observed_claims=[claim]
    )
    assert result["claims_observed"] == 1
    assert str(result["canonical_run_id"]) == CANONICAL_RUN_ID
    assert str(result["canonical_run_attempt"]) == CANONICAL_RUN_ATTEMPT


# -- 6 & 7. nothing that never existed was invented -------------------------


def test_no_build_record_or_archive_is_committed() -> None:
    """BUILD_A and BUILD_B failed before producing anything.

    Committing a placeholder for either would turn an honest absence into a
    false record, so the evidence directory holds the claim and nothing else.
    """
    evidence = REPOSITORY_ROOT / DURABLE_EVIDENCE_ROOT
    assert evidence.is_dir()
    preserved = sorted(p.name for p in evidence.rglob("*") if p.is_file())
    # 002's claim, and 003's. Two claims, three dispatches, zero artifacts.
    assert preserved == [
        "j1-qualification-claim.json",
        "j1-qualification-claim.json",
    ], preserved
    own = sorted(
        p.name
        for p in (evidence / AUTHORIZATION_002).rglob("*")
        if p.is_file()
    )
    assert own == ["j1-qualification-claim.json"], own


@pytest.mark.parametrize(
    "pattern",
    ["*.oci.tar", "build-a.json", "build-b.json", "j1-reproducibility*.json"],
)
def test_no_artifact_or_reproducibility_record_exists_anywhere(
    pattern: str,
) -> None:
    assert not list(REPOSITORY_ROOT.rglob(pattern)), pattern


def test_the_receipt_states_the_absences_rather_than_implying_them() -> None:
    receipt = _prose(RECEIPT_002_PATH)
    for absence in (
        "manifest A = absent",
        "manifest B = absent",
        "OCI archive A = absent",
        "OCI archive B = absent",
    ):
        assert absence in receipt, absence
    assert "reproducibility_classification = NONE" in receipt


def test_the_outcome_is_not_labelled_as_a_reproducibility_verdict() -> None:
    """No manifest existed, so reproducibility was never observed.

    `DIVERGED` would assert two artifacts existed and disagreed. Both are false,
    and either label would send a future reader to investigate a comparison that
    never happened.
    """
    receipt = RECEIPT_002_PATH.read_text(encoding="utf-8")
    for line in receipt.splitlines():
        stripped = line.strip().strip("`")
        assert stripped != "reproducibility_classification = BIT_REPRODUCIBLE"
        assert stripped != "reproducibility_classification = DIVERGED"
        assert stripped != f"failure_class = {PRE_ARTIFACT_INFRASTRUCTURE}"


# -- 8. 002 is spent, and the code agrees -----------------------------------


def test_the_receipt_declares_002_spent_and_never_reusable() -> None:
    receipt = _prose(RECEIPT_002_PATH)
    assert "AUTHORIZATION 002 IS SPENT AND MUST NEVER BE REUSED" in receipt
    assert "authorization_spent = true" in receipt
    assert "claim_recorded = true" in receipt


def test_the_repository_itself_refuses_a_retry_of_002() -> None:
    """Not a claim in prose: the mechanism is asked, and it refuses."""
    with pytest.raises(QualificationError, match="retry is not permitted"):
        require_retry_permitted(POST_CLAIM_PRE_ARTIFACT, claim_recorded=True)


def test_the_receipt_never_declares_002_retryable() -> None:
    """Checked on the headings, not by hunting substrings in the prose.

    The body says "002 is **not** retry-eligible", so a substring search for
    "retry-eligible" finds a hit inside the sentence that forbids it -- the
    recurring trap of grepping a document that explains the thing it prohibits.
    What can be checked without ambiguity is what the document *declares*: its
    headings, and the state block. 001's headline does claim retry eligibility,
    and that difference is the point.
    """
    headings = [
        line.strip().lstrip("#").strip().strip("`").upper()
        for line in RECEIPT_002_PATH.read_text(encoding="utf-8").splitlines()
        if line.startswith("#")
    ]
    assert headings, "the receipt has no headings to check"
    for heading in headings:
        assert "RETRY-ELIGIBLE" not in heading, heading
    assert any("NO RETRY" in heading for heading in headings)
    assert any("SPENT" in heading for heading in headings)

    receipt = _prose(RECEIPT_002_PATH)
    assert "authorization_spent = true" in receipt
    assert "not retry-eligible" in receipt

    # 001 is the one whose headline carries retry eligibility. If both receipts
    # said the same thing, neither would be recording anything.
    assert any(
        "RETRY-ELIGIBLE" in line.upper()
        for line in RECEIPT_001_PATH.read_text(encoding="utf-8").splitlines()
        if line.startswith("#")
    )


# -- 9 & 10. the two failures are different, and stay different -------------


def test_001_remains_retired_but_not_spent() -> None:
    """Its own receipt is unchanged and still says it recorded no claim."""
    receipt = _prose(RECEIPT_001_PATH)
    assert AUTHORIZATION_001 in receipt
    assert "claim_recorded = false" in receipt
    assert PRE_ARTIFACT_INFRASTRUCTURE in receipt
    assert RUN_001_ID in receipt


def test_the_two_failures_cannot_be_conflated() -> None:
    """Different runs, different classes, different consequences.

    The failure classes are disjoint, the run ids are different, and each
    receipt names only its own. Reading either receipt must not leave a reader
    able to mistake one outcome for the other.
    """
    assert POST_CLAIM_PRE_ARTIFACT != PRE_ARTIFACT_INFRASTRUCTURE
    assert CANONICAL_RUN_ID != RUN_001_ID

    receipt_002 = _prose(RECEIPT_002_PATH)
    receipt_001 = _prose(RECEIPT_001_PATH)

    # 001's receipt predates 002 entirely and must not have been rewritten.
    assert AUTHORIZATION_002 not in receipt_001
    assert CANONICAL_RUN_ID not in receipt_001
    assert POST_CLAIM_PRE_ARTIFACT not in receipt_001

    # 002's receipt names 001 only to distinguish itself from it.
    assert AUTHORIZATION_001 in receipt_002
    assert "RETIRED, NOT SPENT" in receipt_002
    assert "SPENT" in receipt_002


def test_the_claim_binds_002_to_the_object_it_authorized() -> None:
    """The spent authorization's object identity survives in the claim.

    The authorization document is gone. What it authorized is not lost: the
    claim the provider produced carries the source commit and configuration
    digest the build actually used.
    """
    document = json.loads(CLAIM_PATH.read_bytes())
    assert document["authorized_source_commit"] == (
        "8c7a385ddd60072abaf8fd2cfe493f1cefe12885"
    )
    assert document["build_configuration_digest"] == (
        "c9e9b5a636e65957c19103c22d29fdaf7d0dc8b9ed073a2aab146a86b2adf12c"
    )
    assert document["workflow_sha256"] == (
        "6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53"
    )


# -- the scientific boundary is untouched by any of this -------------------


def test_no_scientific_authorization_or_environment_authority_exists() -> None:
    from cardiosentinel.journal_extension.j1.authorization import (
        AuthorizationError,
        verify_authorization,
    )

    with pytest.raises(AuthorizationError, match="J1 authorization absent"):
        verify_authorization(None)
    assert not list(J1_DOCS.glob("*ENVIRONMENT_AUTHORITY_RECORD*"))
    # No authorization is live, so no JSON sits directly under the J1 documents;
    # the claims live under `evidence/`. J1 science is unauthorized regardless.
    assert not list(J1_DOCS.glob("*.json"))
