"""The 335-member dependency provenance audit, and the claims it may not make.

**No package is imported or executed, no environment is mutated, no build runs,
and no authority is activated.** The audit is documentation and analysis; these
tests hold it to the boundary it declares.

The historical locks record `name` and `version` and nothing else. That single
fact is why `wheel_or_sdist_byte_authority` is `ABSENT` for all 335 rows, and why
a version pin can never be treated as byte authority here.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

from cardiosentinel.journal_extension.j1 import preflight
from cardiosentinel.journal_extension.j1.approved_runtime import (
    APPROVED_DEPENDENCY_DIGEST,
    ESTABLISHING_EXPERIMENT_LOCKS,
)
from cardiosentinel.journal_extension.j1.authorization import (
    AuthorizationError,
    verify_authorization,
)
from cardiosentinel.journal_extension.j1.builder_authorization import (
    BUILDER_AUTHORIZATION_PATH,
    load_builder_authorization,
)

REPOSITORY_ROOT = Path(preflight.J1_PACKAGE_ROOT).parents[3]
J1_DOCS = REPOSITORY_ROOT / "docs/journal-extension/j1"

LEDGER_CSV = J1_DOCS / "J1_V2_DEPENDENCY_PROVENANCE_AUDIT_V1.csv"
LEDGER_MD = J1_DOCS / "J1_V2_DEPENDENCY_PROVENANCE_AUDIT_V1.md"
CLOSURE_MD = J1_DOCS / "J1_V2_SCIENTIFIC_CODE_CLOSURE_V1.md"
IMPORT_MAP = J1_DOCS / "J1_V2_IMPORT_DISTRIBUTION_MAP_V1.json"
LOCAL_DIAGNOSTIC = J1_DOCS / "J1_V2_LOCAL_DEPENDENCY_ORIGIN_DIAGNOSTIC_V1.json"
CANDIDATE = J1_DOCS / "J1_V2_DEPENDENCY_AUTHORITY_CANDIDATE_V1.json"
REPORT = J1_DOCS / "J1_V2_DEPENDENCY_AUTHORITY_AUDIT_REPORT_V1.md"

HISTORICAL_COUNT = 335
HISTORICAL_DIGEST = (
    "b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a"
)
#: The locks as they stood before the audit. Preservation must not edit evidence.
LOCK_DIGESTS = {
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

REQUIRED_NECESSITY = {"REQUIRED_FOR_J1_EXECUTION", "REQUIRED_ONLY_TRANSITIVELY"}
UNRESOLVED_RECON = {"SOURCE_UNRESOLVED", "LOCAL_ONLY_SOURCE"}


def ledger() -> list[dict[str, str]]:
    with LEDGER_CSV.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def candidate() -> dict:
    return json.loads(CANDIDATE.read_text(encoding="utf-8"))


def _prose(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


# -- 1, 2, 3. the ledger is complete and faithful to the historical record --


def test_the_ledger_has_exactly_one_row_per_historical_package() -> None:
    rows = ledger()
    assert len(rows) == HISTORICAL_COUNT
    indices = [int(r["historical_index"]) for r in rows]
    assert indices == list(range(1, HISTORICAL_COUNT + 1))
    assert len({r["normalized_name"] for r in rows}) == HISTORICAL_COUNT


def test_every_row_records_presence_in_all_three_locks() -> None:
    for row in ledger():
        for field in ("present_in_B4B", "present_in_P1B", "present_in_M1L"):
            assert row[field] in {"True", "False"}, (row["historical_name"], field)
        assert row["historical_agreement"] in {"ALL_THREE_AGREE", "DISAGREEMENT"}


def test_the_exact_historical_name_and_version_are_retained() -> None:
    """Normalization lives in its own column; the historical bytes are verbatim."""
    lock = json.loads(
        (REPOSITORY_ROOT / ESTABLISHING_EXPERIMENT_LOCKS[0]).read_text(
            encoding="utf-8"
        )
    )

    def find(node, key):
        if isinstance(node, dict):
            if key in node:
                return node[key]
            for value in node.values():
                found = find(value, key)
                if found is not None:
                    return found
        return None

    packages = find(lock, "packages") or find(lock, "installed_packages")
    expected = [(p["name"], p["version"]) for p in packages]
    actual = [(r["historical_name"], r["historical_version"]) for r in ledger()]
    assert actual == expected


# -- 4 & 5. the historical authority is untouched ---------------------------


@pytest.mark.parametrize("relative", sorted(ESTABLISHING_EXPERIMENT_LOCKS))
def test_every_establishing_lock_is_byte_unchanged(relative: str) -> None:
    label = relative.split("/")[-2]
    raw = (REPOSITORY_ROOT / relative).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == LOCK_DIGESTS[label], label


def test_the_historical_dependency_digest_is_unchanged() -> None:
    """The audit narrows what the digest *proves*, never the digest itself."""
    assert APPROVED_DEPENDENCY_DIGEST == HISTORICAL_DIGEST
    assert candidate()["historical_snapshot_digest"] == HISTORICAL_DIGEST
    report = _prose(REPORT)
    assert "remains a valid HISTORICAL SNAPSHOT AUTHORITY" in report
    assert "not, and this audit does not make it, a V2 RECONSTRUCTIBLE" in report


# -- 6 & 7. the candidate is a candidate ------------------------------------


def test_the_candidate_is_explicitly_candidate_only_and_not_authorized() -> None:
    document = candidate()
    assert document["status"] == "CANDIDATE_ONLY"
    assert document["authorization_status"] == "NOT_AUTHORIZED"
    for forbidden in ("APPROVED", "AUTHORIZED", "ACTIVE"):
        assert document["status"] != forbidden


def test_the_candidate_digest_is_not_named_as_an_authority() -> None:
    """A set does not become authority by hashing."""
    document = candidate()
    assert "candidate_dependency_set_digest" in document
    assert "dependency_authority_digest" not in document
    assert "approved_dependency_digest" not in document


# -- 8 & 9. no row disappears; no unresolved requirement is called ready ----


def test_no_package_lacks_a_disposition() -> None:
    for row in ledger():
        assert row["candidate_v2_disposition"], row["historical_name"]
        assert row["dependency_role"], row["historical_name"]
        assert row["necessity_class"], row["historical_name"]
        assert row["reconstructibility_class"], row["historical_name"]
        assert row["provenance_class"], row["historical_name"]


def test_no_j1_required_dependency_has_an_unresolved_source() -> None:
    """If one did, the candidate would be BLOCKED and must say so."""
    unresolved = [
        row["historical_name"]
        for row in ledger()
        if row["necessity_class"] in REQUIRED_NECESSITY
        and row["reconstructibility_class"] in UNRESOLVED_RECON
    ]
    assert unresolved == [], unresolved


def test_the_candidate_set_matches_the_j1_required_rows() -> None:
    required = {
        row["normalized_name"]
        for row in ledger()
        if row["necessity_class"] in REQUIRED_NECESSITY
    }
    members = {p["normalized_name"] for p in candidate()["candidate_packages"]}
    assert members == required
    assert candidate()["candidate_package_count"] == len(required)


# -- 10. incident-management is not declared removable ---------------------


def test_incident_management_is_not_declared_safe_to_remove() -> None:
    """Absence of established necessity is not proof of absence of necessity.

    Checked structurally, not by hunting substrings: the report *discusses* the
    phrase "safe to remove" in order to refuse it, so a substring search finds a
    hit inside the sentence that forbids the claim. What can be checked without
    ambiguity is what the document **declares** -- its headings -- plus the
    explicit refusal and the ledger disposition.
    """
    report = _prose(REPORT)
    assert "NO CARDIOSENTINEL NECESSITY ESTABLISHED" in report
    assert "does not conclude that the package may be removed" in report
    assert "different claim from removability" in report

    headings = [
        line.strip().lstrip("#").strip().strip("`").upper()
        for line in REPORT.read_text(encoding="utf-8").splitlines()
        if line.startswith("#")
    ]
    assert headings
    for heading in headings:
        assert "SAFE TO REMOVE" not in heading, heading
        assert "CONTAMINATION CONFIRMED" not in heading, heading
        assert "EXTRANEOUS" not in heading, heading

    row = next(r for r in ledger() if r["normalized_name"] == "incident-management")
    assert row["dependency_role"] == "UNRELATED_OR_CONTAMINATING_CANDIDATE"
    assert row["candidate_v2_disposition"] == "UNRESOLVED_DO_NOT_RETAIN"
    assert row["human_review_required"] == "True"


def test_the_contaminating_class_stays_a_candidate() -> None:
    """`CONTAMINATING` may never appear as a settled classification."""
    for row in ledger():
        role = row["dependency_role"]
        if "CONTAMIN" in role:
            assert role.endswith("_CANDIDATE"), role


# -- 11. local observations cannot masquerade as repository-proven ---------


def test_local_observations_are_labelled_local_only() -> None:
    diagnostic = json.loads(LOCAL_DIAGNOSTIC.read_text(encoding="utf-8"))
    assert "LOCAL_DIAGNOSTIC_ONLY" in diagnostic["STATUS"]
    assert "NOT REPOSITORY-PROVEN PROVENANCE" in diagnostic["STATUS"]
    assert "mutable" in diagnostic["caveat"]

    for row in ledger():
        if row["provenance_class"] in {"LOCAL_EDITABLE", "LOCAL_NON_EDITABLE"}:
            assert row["provenance_confidence"] == "LOCAL_DIAGNOSTIC_ONLY", row[
                "historical_name"
            ]


def test_index_provenance_is_marked_as_a_diagnostic_query() -> None:
    """A successful query proves a source serves it today. Nothing more."""
    for row in ledger():
        if row["provenance_class"] in {"PYPI_INDEX", "PYTORCH_CPU_INDEX"}:
            assert row["provenance_confidence"] == "DIAGNOSTIC_INDEX_QUERY"
            assert row["source_locator_authority"] == "DIAGNOSTIC_QUERY"


# -- 12. version pins are never byte authority ----------------------------


def test_no_row_claims_wheel_byte_authority() -> None:
    """The historical evidence carries name and version only, for every member."""
    for row in ledger():
        assert row["wheel_or_sdist_byte_authority"] == "ABSENT", row["historical_name"]
    assert candidate()["artifact_byte_authority_status"] == "ABSENT_FOR_ALL_MEMBERS"
    for member in candidate()["candidate_packages"]:
        assert member["wheel_or_sdist_byte_authority"] == "ABSENT"


def test_the_report_states_the_byte_authority_gap(  ) -> None:
    report = _prose(REPORT)
    assert "ABSENT` for all 335" in report or "ABSENT for all 335" in report
    assert "never the bytes that arrive" in report


# -- 13. the primary classification reconciles to 335 ---------------------


def test_primary_roles_are_mutually_exclusive_and_total_335() -> None:
    rows = ledger()
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["dependency_role"]] = counts.get(row["dependency_role"], 0) + 1
    assert sum(counts.values()) == HISTORICAL_COUNT
    # Each row carries exactly one primary role, so the counts cannot overlap.
    assert len(rows) == HISTORICAL_COUNT


def test_the_excluded_and_candidate_sets_partition_the_335() -> None:
    document = candidate()
    total = document["candidate_package_count"] + len(
        document["excluded_or_deferred_packages"]
    )
    assert total == HISTORICAL_COUNT


# -- 14 & 15. governance state is untouched by an audit -------------------


def test_no_builder_authorization_is_active() -> None:
    assert not (REPOSITORY_ROOT / BUILDER_AUTHORIZATION_PATH).exists()
    assert load_builder_authorization(REPOSITORY_ROOT) is None


def test_no_environment_authority_or_scientific_authorization_exists() -> None:
    with pytest.raises(AuthorizationError, match="J1 authorization absent"):
        verify_authorization(None)
    assert not list(J1_DOCS.glob("*ENVIRONMENT_AUTHORITY_RECORD*"))
    assert not list(J1_DOCS.glob("*ATTEMPT*"))


def test_no_authorization_004_was_created() -> None:
    for path in J1_DOCS.rglob("*"):
        if path.is_file():
            assert "AUTH-004" not in path.name
            assert "AUTH_004" not in path.name


# -- the audit records its own correction ---------------------------------


def test_the_audit_records_probing_the_wrong_source_for_the_cpu_wheels() -> None:
    """An audit that hides its own corrections is worth less than one that
    shows them."""
    report = _prose(REPORT)
    assert "PyTorch CPU index" in report
    assert "wrong source" in report
    row = next(r for r in ledger() if r["normalized_name"] == "torch")
    assert row["provenance_class"] == "PYTORCH_CPU_INDEX"
    assert row["source_availability"] == "AVAILABLE_FROM_QUERIED_SOURCE"
    assert "CORRECTED" in row["notes"]


def test_every_audit_artifact_exists() -> None:
    for path in (
        LEDGER_CSV,
        LEDGER_MD,
        CLOSURE_MD,
        IMPORT_MAP,
        LOCAL_DIAGNOSTIC,
        CANDIDATE,
        REPORT,
    ):
        assert path.is_file(), path.name
