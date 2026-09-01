"""Qualification of the J1 authorization contract.

NON-SCIENTIFIC QUALIFICATION FIXTURE. Every contract below is fabricated and
none is signed. No J1 authorization document exists, none is created here, and
nothing in this file authorizes anything. The repository state these tests run
against is `PRE-REGISTERED — NOT AUTHORIZED`.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from cardiosentinel.journal_extension.j1 import authorization, preflight
from cardiosentinel.journal_extension.j1.authorization_contract import (
    CONTRACT_FIELDS,
    DECISION_AUTHORITY_FIELDS,
    EXECUTION_SCHEMA_COVERAGE,
    AuthorizationContractError,
    AuthorizationState,
    J1AuthorizationContract,
    verify_contract,
)
from cardiosentinel.journal_extension.j1.partition_authority import V1_TRAIN_ONLY

CONTRACT_MODULE = (
    Path(preflight.J1_PACKAGE_ROOT) / "authorization_contract.py"
)


def _contract(**overrides: object) -> dict[str, object]:
    """A complete, admissible, entirely fabricated draft. Nobody signed it."""
    document: dict[str, object] = {
        "protocol_sha256": "a" * 64,
        "preregistration_sha256": "b" * 64,
        "freeze_receipt_sha256": "c" * 64,
        "execution_instrument_commit": "1" * 40,
        "collaborator_implementation_commit": "2" * 40,
        "authorized_execution_git_sha": "3" * 40,
        "evidence_class": "V2_DEVELOPMENT",
        "environment_authority_id": "synthetic-env-authority-1",
        "environment_sha256": "d" * 64,
        "allowed_partition": V1_TRAIN_ONLY,
        "train_data_authority_id": "synthetic-train-authority-1",
        "train_manifest_digest": "e" * 64,
        "split_sha256": "f" * 64,
        "attempt_budget": 1,
        "provenance_sink_id": "synthetic-sink-1",
        "provenance_sink_destination": "s3://synthetic-evidence/j1/",
        "scientific_success_authority": "synthetic principal investigator",
        "scientific_failure_authority": "synthetic principal investigator",
        "inconclusive_outcome_authority": "synthetic review panel",
        "apparatus_failure_authority": "synthetic engineering lead",
        "apparatus_after_visibility_authority": "synthetic review panel",
        "authorization_id": "SYNTHETIC-NOT-REAL",
        "authorized_at": "2026-09-01T00:00:00Z",
        "human_authorization_identity": "synthetic signatory",
    }
    document.update(overrides)
    return document


# -- the contract is not a permission --------------------------------------


def test_a_complete_contract_is_only_ever_a_draft() -> None:
    contract = verify_contract(_contract())
    assert contract.state is AuthorizationState.DRAFT
    assert contract.state is not AuthorizationState.AUTHORIZED
    assert contract.permits_attempt is False
    assert contract.as_attestation()["execution_authorized"] is False


def test_authorized_is_not_reachable_without_a_human_act() -> None:
    reachable = AuthorizationState.reachable_without_human_action()
    assert AuthorizationState.AUTHORIZED not in reachable
    assert reachable == (AuthorizationState.ABSENT, AuthorizationState.DRAFT)


def test_no_code_path_in_the_package_produces_an_authorized_state() -> None:
    """Structural, by AST over the whole J1 package.

    A text scan would match this module's own enum member and the sentences
    that explain why it is unreachable, so the proof walks the syntax tree and
    looks for the attribute being *read* outside the two places entitled to
    name it: the enum definition, and the reachability classmethod that
    excludes it.
    """
    offenders: list[str] = []
    for path in sorted(Path(preflight.J1_PACKAGE_ROOT).rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and node.attr == "AUTHORIZED"
                and isinstance(node.value, ast.Name)
                and node.value.id == "AuthorizationState"
            ):
                offenders.append(f"{path.name}:{node.lineno}")
    assert not offenders, (
        "AuthorizationState.AUTHORIZED is referenced in the package at "
        f"{offenders}; no code path may promote itself to authorized"
    )


def test_verify_contract_has_no_bypass_parameter() -> None:
    signature = inspect.signature(verify_contract)
    for forbidden in ("dev_mode", "force", "skip_checks", "state", "authorized"):
        assert forbidden not in signature.parameters


def test_the_contract_class_exposes_no_promotion_method() -> None:
    """A method named `authorize`, `sign` or `promote` would be that path."""
    for name in ("authorize", "sign", "promote", "approve", "grant"):
        assert not hasattr(J1AuthorizationContract, name)


def test_an_absent_contract_is_refused_first() -> None:
    with pytest.raises(AuthorizationContractError, match="no J1 authorization"):
        verify_contract(None)


# -- execution cannot start without authorization --------------------------


def test_execution_cannot_start_without_an_authorization() -> None:
    """Preflight refuses at the authorization stage, before anything else."""
    with pytest.raises(preflight.PreflightError, match="authorization absent"):
        preflight.run_preflight(
            authorization_document=None,
            environment_authority=None,
            repository_root=Path(preflight.J1_PACKAGE_ROOT).parents[3],
        )


def test_a_draft_contract_is_not_an_execution_authorization() -> None:
    """The contract's own vocabulary is not the execution schema's.

    Handing a draft contract to `verify_authorization` must fail rather than
    quietly satisfy it: a contract nobody signed is not a permission.
    """
    with pytest.raises(authorization.AuthorizationError):
        authorization.verify_authorization(_contract())


def test_the_contract_covers_every_execution_schema_field() -> None:
    """Total by test, so the two vocabularies cannot drift apart silently."""
    uncovered = [
        name
        for name in authorization.REQUIRED_FIELDS
        if name not in EXECUTION_SCHEMA_COVERAGE
    ]
    assert not uncovered, f"execution fields with no contract home: {uncovered}"
    for execution_field, contract_field in EXECUTION_SCHEMA_COVERAGE.items():
        assert execution_field in authorization.REQUIRED_FIELDS
        assert contract_field in CONTRACT_FIELDS


# -- every field is mandatory ----------------------------------------------


@pytest.mark.parametrize("field", CONTRACT_FIELDS)
def test_every_contract_field_is_required(field: str) -> None:
    document = _contract()
    del document[field]
    with pytest.raises(AuthorizationContractError):
        verify_contract(document)


@pytest.mark.parametrize(
    "field", [f for f in CONTRACT_FIELDS if f != "attempt_budget"]
)
def test_no_field_may_be_blank(field: str) -> None:
    with pytest.raises(AuthorizationContractError):
        verify_contract(_contract(**{field: "   "}))


def test_a_field_the_contract_does_not_define_is_refused() -> None:
    """An undefined field is held to no rule, so it cannot be carried."""
    with pytest.raises(AuthorizationContractError, match="does not define"):
        verify_contract(_contract(dev_mode="true"))


# -- 1. frozen scientific identity -----------------------------------------


@pytest.mark.parametrize(
    "field",
    [
        "protocol_sha256",
        "preregistration_sha256",
        "freeze_receipt_sha256",
        "environment_sha256",
        "train_manifest_digest",
        "split_sha256",
    ],
)
def test_an_abbreviated_digest_is_not_an_immutable_identifier(field: str) -> None:
    with pytest.raises(AuthorizationContractError, match="SHA-256"):
        verify_contract(_contract(**{field: "a" * 12}))


@pytest.mark.parametrize(
    "field",
    [
        "execution_instrument_commit",
        "collaborator_implementation_commit",
        "authorized_execution_git_sha",
    ],
)
def test_an_abbreviated_commit_is_refused(field: str) -> None:
    with pytest.raises(AuthorizationContractError, match="commit SHA"):
        verify_contract(_contract(**{field: "10e31f6"}))


def test_the_evidence_class_must_match(sub: None = None) -> None:
    with pytest.raises(AuthorizationContractError, match="evidence"):
        verify_contract(_contract(evidence_class="V1_CONFIRMATORY"))


# -- 2. the environment cannot be guessed ----------------------------------


@pytest.mark.parametrize(
    "field,value",
    [
        ("environment_authority_id", "current-machine"),
        ("environment_authority_id", "workstation-3"),
        ("environment_sha256", "unknown"),
        ("environment_authority_id", "/home/dev/env"),
        ("environment_authority_id", "TBD"),
    ],
)
def test_the_environment_cannot_be_guessed_or_taken_from_the_machine(
    field: str, value: str
) -> None:
    with pytest.raises(AuthorizationContractError):
        verify_contract(_contract(**{field: value}))


def test_the_contract_module_reads_no_machine_state() -> None:
    """Structural, by AST: an environment digest is never observed here."""
    forbidden = {"gethostname", "getlogin", "getuser", "expanduser", "walk"}
    tree = ast.parse(CONTRACT_MODULE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "attr", None) or getattr(
                node.func, "id", None
            )
            assert name not in forbidden, (
                f"the contract calls {name!r}; an authorization is never "
                "synthesized from the machine it is written on"
            )


# -- 3. TRAIN authority cannot expand --------------------------------------


@pytest.mark.parametrize(
    "partition", ["V1_VALIDATION", "V1_TEST", "ALL", "TRAIN", ""]
)
def test_only_the_train_partition_may_be_named(partition: str) -> None:
    with pytest.raises(AuthorizationContractError):
        verify_contract(_contract(allowed_partition=partition))


@pytest.mark.parametrize(
    "field,value",
    [
        ("train_data_authority_id", "v1-validation-cohort"),
        ("provenance_sink_id", "sealed_test-mirror"),
        ("scientific_success_authority", "the validation board"),
    ],
)
def test_no_field_may_reach_a_forbidden_partition(field: str, value: str) -> None:
    """VALIDATION is historical-only and TEST was consumed on 2026-08-25."""
    with pytest.raises(AuthorizationContractError, match="forbidden partition"):
        verify_contract(_contract(**{field: value}))


@pytest.mark.parametrize(
    "value",
    ["discover the manifest", "autodetect subjects", "glob the split directory"],
)
def test_the_manifest_is_supplied_never_discovered(value: str) -> None:
    with pytest.raises(AuthorizationContractError, match="discovering data"):
        verify_contract(_contract(train_data_authority_id=value))


def test_an_ordinary_name_containing_a_marker_substring_is_not_refused() -> None:
    """A contract that refuses a real reviewer's name is broken, not stricter."""
    contract = verify_contract(
        _contract(
            scientific_success_authority="the principal investigator, herself",
            train_data_authority_id="cardiac-scanner-cohort-1",
        )
    )
    assert contract.state is AuthorizationState.DRAFT


# -- 4. the attempt budget cannot default ----------------------------------


def test_an_absent_budget_is_a_refusal_never_one_attempt() -> None:
    document = _contract()
    del document["attempt_budget"]
    with pytest.raises(AuthorizationContractError, match="never read as one"):
        verify_contract(document)


@pytest.mark.parametrize("budget", [-1, -10])
def test_a_negative_budget_is_refused(budget: int) -> None:
    with pytest.raises(AuthorizationContractError, match="negative"):
        verify_contract(_contract(attempt_budget=budget))


@pytest.mark.parametrize("budget", ["1", 1.0, None, True, [1]])
def test_a_non_integer_budget_is_refused(budget: object) -> None:
    with pytest.raises(AuthorizationContractError, match="explicit integer"):
        verify_contract(_contract(attempt_budget=budget))


def test_zero_is_an_explicit_decision_that_permits_no_attempt() -> None:
    """Recordable, and distinct from absent. It is still not a permission."""
    contract = verify_contract(_contract(attempt_budget=0))
    assert contract.attempt_budget == 0
    assert contract.permits_attempt is False


def test_a_recorded_budget_never_becomes_a_permission() -> None:
    assert verify_contract(_contract(attempt_budget=3)).permits_attempt is False


# -- 5. provenance sink -----------------------------------------------------


@pytest.mark.parametrize(
    "destination",
    [
        "/var/lib/cardiosentinel/j1",
        "./runs/j1",
        "file:///var/lib/j1",
        "cardiosentinel-runs/j1",
        "http://example.invalid/j1",
    ],
)
def test_a_local_or_mutable_destination_is_insufficient_authority(
    destination: str,
) -> None:
    with pytest.raises(AuthorizationContractError):
        verify_contract(_contract(provenance_sink_destination=destination))


def test_an_addressed_immutable_destination_is_accepted() -> None:
    for destination in ("s3://evidence-bucket/j1/", "oci://registry/j1@sha256:ab"):
        contract = verify_contract(
            _contract(provenance_sink_destination=destination)
        )
        assert contract.state is AuthorizationState.DRAFT


# -- 6. decision authority --------------------------------------------------


@pytest.mark.parametrize("field", DECISION_AUTHORITY_FIELDS)
def test_the_runtime_may_not_be_named_as_the_decider(field: str) -> None:
    with pytest.raises(AuthorizationContractError, match="never decides"):
        verify_contract(_contract(**{field: "the runtime"}))


@pytest.mark.parametrize(
    "value", ["automatic", "the pipeline", "the code", "none"]
)
def test_no_outcome_may_be_declared_by_the_apparatus(value: str) -> None:
    with pytest.raises(AuthorizationContractError, match="never decides"):
        verify_contract(_contract(scientific_failure_authority=value))


def test_all_four_outcomes_have_a_named_authority() -> None:
    for field in (
        "scientific_success_authority",
        "scientific_failure_authority",
        "inconclusive_outcome_authority",
        "apparatus_failure_authority",
    ):
        assert field in CONTRACT_FIELDS


# -- the repository state this contract describes --------------------------


def test_the_repository_still_contains_no_authorization_document() -> None:
    """The contract defines a boundary; it does not populate one."""
    j1_docs = Path(preflight.J1_PACKAGE_ROOT).parents[3] / "docs"
    authorizations = sorted(j1_docs.glob("journal-extension/**/J1_AUTHORIZATION_V1.md"))
    assert authorizations == []
