"""The live state created by builder authorization 003, and what it did not create.

**No controlled build was dispatched, no image exists, and J1 science remains
unauthorized.** `J1-ENV-BUILDER-AUTH-003` is *authorized and unspent*: a builder
authorization becomes spent when a qualification claim is recorded under it, and
no claim under 003 exists.

Three authorizations now have three different lifecycles, and conflating any two
of them would lose the fact that decides whether one can be used again:

```text
001  gate refused, no claim        PRE_ARTIFACT_INFRASTRUCTURE
                                   RETIRED, NOT SPENT
002  claim recorded, builds failed POST_CLAIM_PRE_ARTIFACT
                                   SPENT, RETIRED, NOT REUSABLE
003  authorized, nothing dispatched
                                   ACTIVE, AUTHORIZED, UNSPENT
```

The load-bearing field is `authorized_source_commit`. It is the commit V5
machine-verified, **not** the merge that added V5 to the repository -- the
Containerfile ends with `COPY .`, so the source tree is image content and the
two commits are two different artifacts.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from cardiosentinel.journal_extension.j1 import preflight
from cardiosentinel.journal_extension.j1.authorization import (
    AuthorizationError,
    verify_authorization,
)
from cardiosentinel.journal_extension.j1.builder_authorization import (
    BUILDER_AUTHORIZATION_FIELDS,
    BUILDER_AUTHORIZATION_PATH,
    load_builder_authorization,
    verify_builder_authorization,
    verify_workflow_identity,
)
from cardiosentinel.journal_extension.j1.qualification import (
    DURABLE_EVIDENCE_ROOT,
    durable_evidence_destination,
)

REPOSITORY_ROOT = Path(preflight.J1_PACKAGE_ROOT).parents[3]
J1_DOCS = REPOSITORY_ROOT / "docs/journal-extension/j1"

AUTHORIZATION_003 = "J1-ENV-BUILDER-AUTH-003"
#: The commit V5 machine-verified as the build candidate.
AUTHORIZED_SOURCE_COMMIT = "bc9337aed38b7ce3f48a47f917a2f4e320e7368a"
#: The #160 merge, which added the V5 packet and its tests and **no build input**.
#: Authorizing it would name a source object no packet ever verified.
REVIEW_MERGE_COMMIT = "709d980d086a0d0a03c8df3473645881f1958a8c"

#: Every field of the authorization, as the human act recorded it.
EXPECTED_FIELDS = {
    "builder_authorization_id": AUTHORIZATION_003,
    "builder_candidate_id": (
        "github-actions:DebalekhaChakraborty/CardioSentinel//"
        ".github/workflows/j1-environment-artifact-build.yml@"
        "1983616f2021fa5587b7f6cec716501c610e4bf6#ubuntu-24.04"
    ),
    "provider": "github-actions",
    "repository": "DebalekhaChakraborty/CardioSentinel",
    "workflow_path": ".github/workflows/j1-environment-artifact-build.yml",
    "workflow_review_commit": "1983616f2021fa5587b7f6cec716501c610e4bf6",
    "workflow_sha256": (
        "6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53"
    ),
    "runner_class": "ubuntu-24.04",
    "controlled_build_protocol_identity": (
        "J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2"
    ),
    "controlled_build_protocol_digest": (
        "3454c4096fe025a5c88f744cc92b15c1975a9ddf3d2e2e59259770b5b4dea412"
    ),
    "source_repository": "DebalekhaChakraborty/CardioSentinel",
    "authorized_source_commit": AUTHORIZED_SOURCE_COMMIT,
    "target_platform": "linux/amd64",
    "artifact_type": "oci_single_platform_image_manifest",
    "base_image_digest": (
        "python@sha256:"
        "c0d63ec61d3a1321f8dc2d46ab6bd38465e005237c0a463712020e5d338eae25"
    ),
    "dependency_authority_identity": "v1-frozen-experiment-lock-335-packages",
    "dependency_digest": (
        "b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a"
    ),
    "build_configuration_digest": (
        "54f40d3136e17d6db11be975b209087d329f30019d9ecaa05cc38e69dda5d80f"
    ),
    "provenance_destination": (
        "docs/journal-extension/j1/evidence/environment-build/"
        "J1-ENV-BUILDER-AUTH-003/"
    ),
    "qualification_policy": "FIRST_AUTHORIZED_QUALIFICATION_RUN_IS_CANONICAL",
    "authorization_timestamp": "2026-09-04T22:40:57Z",
    "human_authorizer_identity": "DebalekhaChakraborty",
}

ACT_V3_PATH = J1_DOCS / "J1_BUILDER_AUTHORIZATION_ACT_V3.md"


def _document() -> dict[str, object]:
    document = load_builder_authorization(REPOSITORY_ROOT)
    assert document is not None, "no active builder authorization"
    return dict(document)


def _reviewed_commit_readable(commit: str) -> bool:
    """Whether git can answer for this commit here. CI checks out shallow."""
    return subprocess.run(
        ["git", "-C", str(REPOSITORY_ROOT), "cat-file", "-e", f"{commit}^{{commit}}"],
        capture_output=True,
        check=False,
    ).returncode == 0


def _act_prose() -> str:
    return " ".join(ACT_V3_PATH.read_text(encoding="utf-8").split())


# -- the authorization exists, verifies, and says exactly what it should ----


def test_the_active_authorization_is_003() -> None:
    assert (REPOSITORY_ROOT / BUILDER_AUTHORIZATION_PATH).is_file()
    assert _document()["builder_authorization_id"] == AUTHORIZATION_003


@pytest.mark.parametrize("field", sorted(EXPECTED_FIELDS))
def test_every_authorization_field_is_what_the_act_recorded(field: str) -> None:
    """All 22 fields, one assertion each, so a failure names the field."""
    assert _document()[field] == EXPECTED_FIELDS[field]


def test_the_authorization_carries_exactly_the_schema_fields() -> None:
    document = _document()
    assert set(document) == set(BUILDER_AUTHORIZATION_FIELDS)
    assert set(document) == set(EXPECTED_FIELDS)
    assert len(document) == 22


def test_the_authorization_verifies() -> None:
    verify_builder_authorization(_document())


def test_the_workflow_identity_verifies_against_recomputed_bytes() -> None:
    """Both digests are recomputed by the verifier; neither is echoed back.

    Written so it never skips and never fails for the wrong reason. The
    checkout-side digest needs no history and is always checked; the
    reviewed-commit side needs the object store, so where the checkout is
    shallow this degrades to the half it can prove rather than raising.
    """
    document = _document()
    declared = document["workflow_sha256"]
    on_disk = hashlib.sha256(
        (REPOSITORY_ROOT / str(document["workflow_path"])).read_bytes()
    ).hexdigest()
    assert on_disk == declared

    verified = verify_builder_authorization(document)
    if not _reviewed_commit_readable(str(document["workflow_review_commit"])):
        return  # shallow checkout: the checkout-side digest above still ran
    proof = verify_workflow_identity(verified, repository_root=REPOSITORY_ROOT)
    assert proof["workflow_sha256_recomputed_from_checkout"] == declared
    assert proof["workflow_sha256_recomputed_from_review_commit"] == declared


def test_the_provenance_destination_is_derived_not_chosen() -> None:
    assert _document()["provenance_destination"] == durable_evidence_destination(
        AUTHORIZATION_003
    )


# -- the source commit is the reviewed candidate, not the review merge ------


def test_the_authorized_source_commit_is_the_reviewed_candidate() -> None:
    """The one field most easily got wrong, asserted in both directions.

    V5 machine-verified `bc9337ae`. The #160 merge added the packet and its
    tests and no build input, so naming it would authorize a source object no
    packet ever verified -- the class of error that retired 001.
    """
    document = _document()
    assert document["authorized_source_commit"] == AUTHORIZED_SOURCE_COMMIT
    assert document["authorized_source_commit"] != REVIEW_MERGE_COMMIT


def test_the_act_explains_why_the_merge_commit_was_not_used() -> None:
    prose = _act_prose()
    assert AUTHORIZED_SOURCE_COMMIT in prose
    assert REVIEW_MERGE_COMMIT in prose
    assert "did **not** redefine the candidate object" in prose or (
        "did not redefine the candidate object" in prose
    )


# -- the act receipt records the decision and its accepted limits -----------


def test_the_act_receipt_agrees_with_the_canonical_json() -> None:
    prose = _act_prose()
    document = _document()
    assert "BUILDER AUTHORIZED AS 003" in prose
    for field in (
        "builder_authorization_id",
        "authorization_timestamp",
        "human_authorizer_identity",
        "authorized_source_commit",
        "build_configuration_digest",
    ):
        assert str(document[field]) in prose, field


@pytest.mark.parametrize(
    "limitation",
    [
        "not cryptographically reproducible",
        "falsifiable reproducibility test, not a guarantee",
        "not wheel-byte authority",
        "governed wheelhouse",
        "digest and structural controls only",
    ],
)
def test_the_act_records_the_accepted_limitations_without_softening(
    limitation: str,
) -> None:
    """The limitations a future reader is likeliest to assume away.

    They were accepted as they stand, not resolved, and the act must say so.
    """
    assert limitation in _act_prose(), limitation


def test_the_act_states_the_scope_and_what_it_is_not() -> None:
    prose = _act_prose()
    assert "THIS AUTHORIZATION APPLIES ONLY TO ENVIRONMENT QUALIFICATION." in prose
    assert "THIS IS NOT J1 SCIENTIFIC AUTHORIZATION." in prose
    assert "NO CONTROLLED BUILD WAS DISPATCHED BY THIS AUTHORIZATION ACT." in prose


# -- 003 is authorized and UNSPENT ------------------------------------------


def test_no_qualification_claim_exists_under_003() -> None:
    """Authorized is not spent. 003 becomes spent only when a claim is recorded."""
    destination = REPOSITORY_ROOT / durable_evidence_destination(AUTHORIZATION_003)
    assert not destination.exists(), "a prospective destination is not evidence"
    evidence = REPOSITORY_ROOT / DURABLE_EVIDENCE_ROOT
    preserved = sorted(p.name for p in evidence.rglob("*") if p.is_file())
    # Only 002's canonical claim exists, and it names 002.
    assert preserved == ["j1-qualification-claim.json"], preserved
    claim = json.loads(
        next(evidence.rglob("j1-qualification-claim.json")).read_bytes()
    )
    assert claim["builder_authorization_id"] == "J1-ENV-BUILDER-AUTH-002"


@pytest.mark.parametrize(
    "pattern",
    ["*.oci.tar", "build-a.json", "build-b.json", "j1-reproducibility*.json"],
)
def test_no_build_output_exists_anywhere(pattern: str) -> None:
    assert not list(REPOSITORY_ROOT.rglob(pattern)), pattern


def test_the_act_records_003_as_unspent() -> None:
    prose = _act_prose()
    assert "ACTIVE, AUTHORIZED, UNSPENT" in prose
    assert "authorized but not spent" in prose


# -- 001 and 002 keep their own lifecycles ----------------------------------


def test_the_retired_authorizations_are_still_recorded_as_they_were() -> None:
    """Authorizing 003 rewrites nothing about what came before."""
    receipt_001 = " ".join(
        (J1_DOCS / "J1_ENV_BUILDER_AUTH_001_PRECLAIM_FAILURE_RECEIPT.md")
        .read_text(encoding="utf-8")
        .split()
    )
    receipt_002 = " ".join(
        (J1_DOCS / "J1_ENV_BUILDER_AUTH_002_POSTCLAIM_FAILURE_RECEIPT.md")
        .read_text(encoding="utf-8")
        .split()
    )
    assert "claim_recorded = false" in receipt_001
    assert "PRE_ARTIFACT_INFRASTRUCTURE" in receipt_001
    assert "authorization_spent = true" in receipt_002
    assert "POST_CLAIM_PRE_ARTIFACT" in receipt_002
    # Neither receipt was rewritten to mention the authorization that followed.
    assert AUTHORIZATION_003 not in receipt_001
    assert AUTHORIZATION_003 not in receipt_002


def test_the_earlier_authorization_acts_are_untouched() -> None:
    """Three acts, three moments. None is revised by the next."""
    pinned = {
        "J1_BUILDER_AUTHORIZATION_ACT_V1.md": (
            "7643a81062db0b0294c35334a425509aabfc74f6fc834a64afad7afb242528d6"
        ),
        "J1_BUILDER_AUTHORIZATION_ACT_V2.md": (
            "c37209a901599f76061046049e50adfde8a207a64a10081be1f61d0acd539719"
        ),
    }
    for name, digest in pinned.items():
        raw = (J1_DOCS / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == digest, name


# -- a builder authorization is not a scientific one ------------------------


def test_j1_science_remains_unauthorized() -> None:
    """The whole point of the scope statement, asserted against the verifier."""
    with pytest.raises(AuthorizationError, match="J1 authorization absent"):
        verify_authorization(None)
    assert not list(J1_DOCS.glob("*ENVIRONMENT_AUTHORITY_RECORD*"))
    assert not list(J1_DOCS.glob("*ATTEMPT*"))
