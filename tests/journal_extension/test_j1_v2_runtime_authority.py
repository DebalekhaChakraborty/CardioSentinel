"""The V2 runtime authority gate, and the two blockers PR #165 found.

**No environment is built, no package installed, no authority activated.** The
rules are exercised against supplied inventories rather than whichever
interpreter happens to run the suite, so a test here proves the rule and not the
machine it ran on.

Two concepts, kept apart:

```text
V1 historical runtime   approved_runtime      immutable, reproduce-only
V2 governed runtime     v2_runtime_authority  checked against a supplied authority
```

A V2 environment failing V1's gate is the boundary working, not a regression, so
the V1 gate is proven *still to refuse* here rather than quietly relaxed.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from cardiosentinel.journal_extension.j1 import approved_runtime as ar
from cardiosentinel.journal_extension.j1 import preflight
from cardiosentinel.journal_extension.j1 import v2_runtime_authority as v2

REPOSITORY_ROOT = Path(preflight.J1_PACKAGE_ROOT).parents[3]
J1_DOCS = REPOSITORY_ROOT / "docs/journal-extension/j1"

CANDIDATE_PATH = J1_DOCS / "J1_V2_DEPENDENCY_AUTHORITY_CANDIDATE_V2.json"
MANIFEST_PATH = J1_DOCS / "J1_V2_DEPENDENCY_ARTIFACT_MANIFEST_CANDIDATE_V1.json"
RECONCILIATION_MD = J1_DOCS / "J1_V2_MODULE_CLOSURE_RECONCILIATION_V1.md"
RECONCILIATION_JSON = J1_DOCS / "J1_V2_MODULE_CLOSURE_RECONCILIATION_V1.json"
APPARATUS_MD = J1_DOCS / "J1_V2_DEPENDENCY_AUTHORITY_APPARATUS_QUALIFICATION_V1.md"

V2_MODULE = (
    REPOSITORY_ROOT
    / "src/cardiosentinel/journal_extension/j1/v2_runtime_authority.py"
)

CANDIDATE_DIGEST = "cb4ec16d399db7c85095ab9a6410afd226092d718b2e45497865aee8c9c2d94f"
V1_HISTORICAL_DIGEST = (
    "b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a"
)

ESTABLISHING_LOCK_BYTES = {
    "reproducibility/demo_bundle/runs/phase3b2-architecture-v1/"
    "B4B_cnn_transformer_v1/EXPERIMENT_LOCK.json":
        "5bf251780f469115164d61a3f3cef2eecfc9ef9765af3f544479e961da00e7bc",
    "reproducibility/demo_bundle/runs/phase4-p1-physiology-v1/"
    "P1B_phys_fusion_v1/EXPERIMENT_LOCK.json":
        "fdde6475a02e0249e0238b89168e6b043b3ade1ec2bfd75922628127fb27d2ca",
    "reproducibility/demo_bundle/runs/phase5-m1-dual-memory-v2/"
    "M1L_long_memory_v2/EXPERIMENT_LOCK.json":
        "6aa199ea5410dde860fd3fcce9ceef0194a364ed2ed5b01678e0648fea60a452",
}


@pytest.fixture(scope="module")
def candidate() -> dict:
    return json.loads(CANDIDATE_PATH.read_text())


@pytest.fixture(scope="module")
def manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text())


@pytest.fixture(scope="module")
def governed_inventory(manifest: dict) -> dict[str, list[str]]:
    """Exactly what the authority governs, plus first-party and one substrate."""
    observed = {
        entry["normalized_name"]: [entry["version"]]
        for entry in manifest["external_packages"]
    }
    observed["cardiosentinel"] = ["0.1.0"]
    observed["pip"] = ["26.2.1"]
    return observed


# ------------------------------------------------------------------- 1, 11 ---
def test_the_v2_verifier_infers_no_repository_root() -> None:
    """The habit that made the gate unimportable, refused structurally."""
    tree = ast.parse(V2_MODULE.read_text(encoding="utf-8"))

    # Structural, not textual: the module's prose explains that it does not walk
    # `__file__`, so a substring search finds the sentence that forbids the thing
    # and fails on it. Only a real name reference counts.
    for node in ast.walk(tree):
        assert not (isinstance(node, ast.Name) and node.id == "__file__"), (
            "the V2 verifier references __file__"
        )
        if isinstance(node, ast.Attribute):
            assert node.attr != "parents", "the V2 verifier walks parent directories"
    assert not hasattr(v2, "REPOSITORY_ROOT")


def test_the_v2_verifier_will_not_find_its_own_authority() -> None:
    with pytest.raises(v2.V2RuntimeAuthorityError, match="no authority path"):
        v2.load_authority_document(None)  # type: ignore[arg-type]


# ---------------------------------------------------------------- 2, 3, 17 ---
def test_the_v1_historical_digest_is_unchanged() -> None:
    assert ar.V1_HISTORICAL_DEPENDENCY_DIGEST == V1_HISTORICAL_DIGEST
    assert ar.APPROVED_DEPENDENCY_DIGEST == V1_HISTORICAL_DIGEST


def test_the_explicit_root_evidence_audit_reconciles_all_three_locks() -> None:
    resolved = ar.verify_v1_historical_runtime_evidence(REPOSITORY_ROOT)
    assert resolved == V1_HISTORICAL_DIGEST
    for relative in ar.ESTABLISHING_EXPERIMENT_LOCKS:
        assert relative in ESTABLISHING_LOCK_BYTES


def test_the_historical_locks_remain_byte_unchanged() -> None:
    import hashlib

    for relative, expected in ESTABLISHING_LOCK_BYTES.items():
        path = REPOSITORY_ROOT / relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, relative


# ------------------------------------------------------------------ 4, 5, 6 ---
def test_the_candidate_verifier_accepts_the_exact_governed_inventory(
    candidate: dict, manifest: dict, governed_inventory: dict
) -> None:
    result = v2.qualify_v2_dependency_candidate(
        candidate, manifest=manifest, observed=governed_inventory
    )
    assert result.passed, result.refusals
    assert result.classification == "QUALIFICATION_ONLY"
    assert result.governed_package_count == 47
    assert result.authority_digest == CANDIDATE_DIGEST


def test_an_allowed_substrate_version_does_not_change_the_governed_digest(
    candidate: dict, manifest: dict, governed_inventory: dict
) -> None:
    """The whole of V2-BLOCKER-1 in one assertion.

    Under V1's method -- which hashes every installed distribution, `pip`
    included -- these two environments have different identities. They are the
    same governed runtime, and PR #165's network-sealed replay differed in
    exactly this way.
    """
    other = dict(governed_inventory)
    other["pip"] = ["24.2"]

    first = v2.qualify_v2_dependency_candidate(
        candidate, manifest=manifest, observed=governed_inventory
    )
    second = v2.qualify_v2_dependency_candidate(
        candidate, manifest=manifest, observed=other
    )

    assert first.passed and second.passed
    assert (
        first.governed_dependency_inventory_digest
        == second.governed_dependency_inventory_digest
    )
    assert first.substrate_inventory != second.substrate_inventory
    assert first.substrate_inventory == {"pip": "26.2.1"}
    assert second.substrate_inventory == {"pip": "24.2"}


def test_substrate_stays_visible_rather_than_hidden(
    candidate: dict, manifest: dict, governed_inventory: dict
) -> None:
    result = v2.qualify_v2_dependency_candidate(
        candidate, manifest=manifest, observed=governed_inventory
    )
    assert result.substrate_inventory == {"pip": "26.2.1"}
    assert result.substrate_allowlist == v2.DEFAULT_SUBSTRATE_ALLOWLIST


# ------------------------------------------------------------------ 7, 8, 9 ---
def test_an_unexpected_package_is_refused(
    candidate: dict, manifest: dict, governed_inventory: dict
) -> None:
    """Excluding substrate from the identity is not licence to ignore extras."""
    polluted = dict(governed_inventory)
    polluted["incident-management"] = ["0.1.0"]
    result = v2.qualify_v2_dependency_candidate(
        candidate, manifest=manifest, observed=polluted
    )
    assert not result.passed
    assert result.ungoverned == ("incident-management",)
    assert any("neither governed" in refusal for refusal in result.refusals)


def test_a_missing_governed_member_is_refused(
    candidate: dict, manifest: dict, governed_inventory: dict
) -> None:
    incomplete = dict(governed_inventory)
    del incomplete["scipy"]
    result = v2.qualify_v2_dependency_candidate(
        candidate, manifest=manifest, observed=incomplete
    )
    assert not result.passed
    assert result.missing == ("scipy",)


def test_a_wrong_governed_version_is_refused(
    candidate: dict, manifest: dict, governed_inventory: dict
) -> None:
    drifted = dict(governed_inventory)
    drifted["numpy"] = ["2.3.3"]
    result = v2.qualify_v2_dependency_candidate(
        candidate, manifest=manifest, observed=drifted
    )
    assert not result.passed
    assert result.version_mismatches == (("numpy", "2.3.2", "2.3.3"),)


def test_a_duplicated_governed_member_is_refused(
    candidate: dict, manifest: dict, governed_inventory: dict
) -> None:
    doubled = dict(governed_inventory)
    doubled["torch"] = ["2.13.0+cpu", "2.13.0"]
    result = v2.qualify_v2_dependency_candidate(
        candidate, manifest=manifest, observed=doubled
    )
    assert not result.passed
    assert result.duplicated == ("torch",)


# --------------------------------------------------------------------- 10 ---
def test_the_production_gate_rejects_a_candidate(
    candidate: dict, manifest: dict, governed_inventory: dict
) -> None:
    """A perfect environment is still not an authorized one."""
    assert candidate["status"] == v2.CANDIDATE_STATUS
    assert candidate["authorization_status"] == v2.CANDIDATE_AUTHORIZATION_STATUS

    qualifies = v2.qualify_v2_dependency_candidate(
        candidate, manifest=manifest, observed=governed_inventory
    )
    assert qualifies.passed

    with pytest.raises(v2.V2AuthorityNotAuthorizedError, match="not an authorized"):
        v2.require_authorized_v2_runtime(
            candidate, manifest=manifest, observed=governed_inventory
        )


def test_the_production_gate_accepts_only_an_explicit_authorized_status(
    candidate: dict, manifest: dict, governed_inventory: dict
) -> None:
    authorized = dict(candidate)
    authorized["authorization_status"] = v2.AUTHORIZED_STATUS
    result = v2.require_authorized_v2_runtime(
        authorized, manifest=manifest, observed=governed_inventory
    )
    assert result.passed
    # And no such object exists in the repository.
    for path in J1_DOCS.rglob("*.json"):
        document = json.loads(path.read_text())
        if isinstance(document, dict):
            status = document.get("authorization_status")
            assert status != v2.AUTHORIZED_STATUS, path.name


def test_an_object_that_does_not_declare_its_status_is_refused() -> None:
    with pytest.raises(v2.V2RuntimeAuthorityError, match="carries no"):
        v2.read_governed_authority({"candidate_id": "anonymous"})


# ---------------------------------------------------- receipt and digests ---
def test_the_governed_digest_is_not_named_an_artifact_authority() -> None:
    for forbidden in (
        "artifact_authority_digest",
        "wheel_digest",
        "dependency_authority_digest",
    ):
        assert not hasattr(v2, forbidden)
    doc = v2.governed_dependency_inventory_digest.__doc__ or ""
    assert "eaker than artifact-byte authority" in doc


def test_the_install_receipt_is_data_free_and_not_an_authority(
    candidate: dict, manifest: dict, governed_inventory: dict
) -> None:
    authority = v2.read_governed_authority(candidate, manifest=manifest)
    result = v2.qualify_v2_dependency_candidate(
        candidate, manifest=manifest, observed=governed_inventory
    )
    receipt = v2.dependency_install_receipt(
        result,
        authority=authority,
        hash_locked_requirement_digests={"a.txt": "0" * 64},
        first_party_source_identity={"source_kind": "FIRST_PARTY_CARDIOSENTINEL"},
        installation_timestamp="2026-09-05T00:00:00+00:00",
    )
    assert receipt["qualification_only"] is True
    assert receipt["scientific_data_accessed"] is False
    assert receipt["scientific_attempt"] is False
    auth_status = receipt["authority_authorization_status"]
    assert auth_status == v2.CANDIDATE_AUTHORIZATION_STATUS
    assert receipt["artifact_manifest_digest"] == manifest["artifact_manifest_digest"]
    assert receipt["governed_dependency_inventory_digest"]
    assert "AUTHORIZED" != receipt["authority_status"]


# ------------------------------------------------------------- 13, 14, 15 ---
def test_the_module_closure_reconciliation_is_recorded() -> None:
    assert RECONCILIATION_MD.is_file()
    data = json.loads(RECONCILIATION_JSON.read_text())
    for key in (
        "pr_164_recorded_module_count",
        "pr_165_module_count",
        "reconciled_module_count",
        "reconciled_modules",
        "module_classifications",
        "new_external_distribution_roots",
        "pr_164_module_set_recoverable",
    ):
        assert key in data, key
    assert data["pr_164_recorded_module_count"] == 113
    assert data["pr_165_module_count"] == 108
    assert len(data["reconciled_modules"]) == data["reconciled_module_count"]
    assert set(data["module_classifications"]) == set(data["reconciled_modules"])


def test_no_new_external_distribution_root_appears() -> None:
    data = json.loads(RECONCILIATION_JSON.read_text())
    assert data["new_external_distribution_roots"] == []
    assert data["third_party_import_roots"] == [
        "numpy",
        "scipy",
        "sklearn",
        "torch",
        "wfdb",
        "yaml",
    ]


def test_every_reconciled_module_carries_a_classification() -> None:
    data = json.loads(RECONCILIATION_JSON.read_text())
    allowed = {
        "SCIENTIFIC_EXECUTION_MODULE",
        "APPARATUS/GOVERNANCE_MODULE",
        "TEST/UTILITY_MODULE",
        "TRANSITIVE_INTERNAL_MODULE",
        "OUTSIDE_FROZEN_J1_EXECUTION_SURFACE",
    }
    for module, classification in data["module_classifications"].items():
        assert classification in allowed, (module, classification)


def test_the_candidate_digest_and_manifest_are_unchanged(
    candidate: dict, manifest: dict
) -> None:
    assert candidate["candidate_v2_dependency_authority_digest"] == CANDIDATE_DIGEST
    assert candidate["artifact_derived_package_count"] == 48
    assert candidate["artifact_derived_external_package_count"] == 47
    assert manifest["external_package_count"] == 47
    assert manifest["source_class_counts"] == {
        "PYPI_INDEX": 46,
        "PYTORCH_CPU_INDEX": 1,
        "FIRST_PARTY_CARDIOSENTINEL": 1,
    }
    delta = candidate["seed_vs_artifact_delta"]
    assert delta["seed_only_packages"] == []
    assert delta["artifact_only_packages"] == []
    assert delta["version_conflicts"] == []
    assert candidate["sdist_authority_required"] == []


# ------------------------------------------------------------- 18, 19, 20 ---
def test_no_builder_authorization_004_exists() -> None:
    from cardiosentinel.journal_extension.j1.builder_authorization import (
        BUILDER_AUTHORIZATION_PATH,
    )

    assert not (REPOSITORY_ROOT / BUILDER_AUTHORIZATION_PATH).exists()
    for path in J1_DOCS.rglob("*"):
        assert "AUTH-004" not in path.name
        assert "AUTH_004" not in path.name


def test_no_environment_authority_record_exists() -> None:
    for path in J1_DOCS.rglob("*"):
        assert "ENVIRONMENT_AUTHORITY_RECORD" not in path.name.upper()


def test_the_apparatus_qualification_claims_no_authorization() -> None:
    text = APPARATUS_MD.read_text()
    assert CANDIDATE_DIGEST in text
    assert "THIS DOCUMENT DOES NOT AUTHORIZE THE DEPENDENCY AUTHORITY." in text


def test_the_apparatus_document_records_zero_scientific_attempts() -> None:
    data = json.loads(RECONCILIATION_JSON.read_text())
    assert data["scientific_data_accessed"] is False
    assert data["scientific_attempts"] == 0
