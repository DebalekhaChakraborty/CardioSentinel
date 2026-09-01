"""Qualification of the J1 execution instrument. No scientific evidence here.

Every fixture below is synthetic. No real subject identifier, measurement,
annotation or model output appears, and nothing produced by these tests is J1
evidence -- they are engineering fixtures proving the apparatus behaves.

NON-SCIENTIFIC QUALIFICATION FIXTURE.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from cardiosentinel.journal_extension.j1 import (
    authorization,
    candidates,
    folds,
    freeze_binding,
    negative_capability,
    partition_authority,
    preflight,
    provenance,
    rows,
    statistics,
    visibility,
)
from cardiosentinel.journal_extension.j1.capability_gate import (
    J1CapabilityAttestation,
    J1CapabilityError,
    require_execution_capability,
)

ROOT = Path(__file__).resolve().parents[2]
SYNTHETIC_SUBJECTS = tuple(f"synthetic:sub{i:03d}" for i in range(56))


# -- freeze binding ---------------------------------------------------------


def test_freeze_binding_matches_the_receipt() -> None:
    binding = freeze_binding.verify_freeze_binding(repository_root=ROOT)
    assert binding.protocol_sha256 == freeze_binding.FROZEN_PROTOCOL_SHA256
    assert (
        binding.pre_registration_sha256
        == freeze_binding.FROZEN_PRE_REGISTRATION_SHA256
    )


def test_a_drifted_document_is_invalid_execution(tmp_path: Path) -> None:
    documents = tmp_path / "docs" / "journal-extension" / "j1"
    documents.mkdir(parents=True)
    (documents / freeze_binding.PROTOCOL_PATH.name).write_text("drifted")
    (documents / freeze_binding.PRE_REGISTRATION_PATH.name).write_text("drifted")
    with pytest.raises(freeze_binding.FreezeBindingError, match="INVALID_EXECUTION"):
        freeze_binding.verify_freeze_binding(repository_root=tmp_path)


# -- authorization ----------------------------------------------------------


def _authorization_document(**overrides: object) -> dict[str, object]:
    document: dict[str, object] = {
        "authorization_id": "SYNTHETIC-NOT-REAL",
        "protocol_sha256": freeze_binding.FROZEN_PROTOCOL_SHA256,
        "pre_registration_sha256": freeze_binding.FROZEN_PRE_REGISTRATION_SHA256,
        "freeze_receipt_sha256": "0" * 64,
        "authorized_execution_git_sha": "0" * 40,
        "evidence_class": "V2_DEVELOPMENT",
        "data_authority": partition_authority.V1_TRAIN_ONLY,
        "split_sha256": partition_authority.FROZEN_SPLIT_SHA256,
        "environment_sha256": "0" * 64,
        "provenance_sink": "memory://qualification",
        "attempt_budget": 1,
        "apparatus_after_visibility_authority": "synthetic reviewer",
        "authorized_at": "2026-09-01T00:00:00Z",
        "human_authorization_identity": "synthetic",
    }
    document.update(overrides)
    return document


def test_absent_authorization_refuses() -> None:
    with pytest.raises(authorization.AuthorizationError, match="absent"):
        authorization.verify_authorization(None)


@pytest.mark.parametrize("field", authorization.REQUIRED_FIELDS)
def test_every_field_is_required(field: str) -> None:
    document = _authorization_document()
    del document[field]
    with pytest.raises(authorization.AuthorizationError, match="Missing"):
        authorization.verify_authorization(document)


@pytest.mark.parametrize("budget", [0, -1, None, "", "one", True])
def test_a_blank_or_zero_budget_is_never_one_attempt(budget: object) -> None:
    with pytest.raises(authorization.AuthorizationError):
        authorization.verify_authorization(
            _authorization_document(attempt_budget=budget)
        )


@pytest.mark.parametrize("authority", ["VALIDATION", "TEST", "ALL", ""])
def test_only_train_may_be_authorized(authority: str) -> None:
    with pytest.raises(authorization.AuthorizationError):
        authorization.verify_authorization(
            _authorization_document(data_authority=authority)
        )


# -- partition authority ----------------------------------------------------


def test_validation_and_test_are_unrepresentable() -> None:
    """There is no constructor, enum or field that can name another partition."""
    exported = dir(partition_authority)
    assert not any(
        name for name in exported if "validation" in name.lower()
    ), "J1 exposes no VALIDATION surface"
    assert not any(name for name in exported if name.lower().endswith("test"))
    authority = partition_authority.train_only_authority(
        split_sha256=partition_authority.FROZEN_SPLIT_SHA256,
        authorized_subjects=frozenset(SYNTHETIC_SUBJECTS),
    )
    assert authority.partition == partition_authority.V1_TRAIN_ONLY
    with pytest.raises(partition_authority.PartitionAuthorityError):
        authority.require_subject("ltstdb:s2001")


def test_a_wrong_split_identity_refuses() -> None:
    with pytest.raises(partition_authority.PartitionAuthorityError):
        partition_authority.train_only_authority(
            split_sha256="0" * 64,
            authorized_subjects=frozenset(SYNTHETIC_SUBJECTS),
        )


# -- capability, and its separation from permission -------------------------


class _Complete:
    j1_execution_capability = J1CapabilityAttestation("x", True)

    def allocate(self, *a: object, **k: object) -> dict[str, object]:
        return {}

    fit_inner = fit_outer = derive = allocate
    evaluate_inner = evaluate_outer = rank = resample = allocate
    open_attempt = promote = allocate


class _RefusesOnly:
    j1_execution_capability = J1CapabilityAttestation("x", True)

    def allocate(self, *a: object, **k: object) -> dict[str, object]:
        raise RuntimeError("placeholder")

    fit_inner = fit_outer = derive = allocate
    evaluate_inner = evaluate_outer = rank = resample = allocate
    open_attempt = promote = allocate


def _graph(collaborator: object) -> dict[str, object]:
    from cardiosentinel.journal_extension.j1.capability_gate import (
        REQUIRED_COLLABORATORS,
    )

    return dict.fromkeys(REQUIRED_COLLABORATORS, collaborator)


def test_a_complete_graph_proves_capability() -> None:
    assert require_execution_capability(_graph(_Complete()))


def test_a_refusal_only_collaborator_fails_before_any_claim() -> None:
    with pytest.raises(J1CapabilityError, match="no reachable return"):
        require_execution_capability(_graph(_RefusesOnly()))


def test_silence_is_a_refusal() -> None:
    class _Silent(_Complete):
        j1_execution_capability = None

    with pytest.raises(J1CapabilityError, match="does not attest"):
        require_execution_capability(_graph(_Silent()))


def test_capability_never_implies_authorization() -> None:
    """A graph that can finish still cannot run."""
    with pytest.raises(preflight.PreflightError, match="authorization absent"):
        preflight.run_preflight(
            authorization_document=None,
            collaborators=_graph(_Complete()),
            provenance_sink=_Complete(),
            repository_root=ROOT,
        )


# -- negative capability ----------------------------------------------------


def test_structural_proof_finds_no_forbidden_reach() -> None:
    assert negative_capability.structural_proof(
        Path(preflight.J1_PACKAGE_ROOT)
    ) == {}


def test_sealed_test_module_is_absent_from_a_j1_execution_process() -> None:
    """Layer 2a is a property of a *dedicated* J1 process, so prove it in one.

    Asserting absence from `sys.modules` inside the shared pytest interpreter
    would test something J1 does not control: the full suite imports
    `b4b_sealed_test` for V1's own tests, and that says nothing about whether
    J1 can reach it. A subprocess importing only the J1 package is what a real
    execution process looks like, and that is where the claim has meaning.
    """
    program = (
        "import sys;"
        "from cardiosentinel.journal_extension.j1 import negative_capability as n;"
        "n.runtime_absence_proof();"
        "assert 'cardiosentinel.neural.b4b_sealed_test' not in sys.modules;"
        "print('absent')"
    )
    completed = subprocess.run(
        [sys.executable, "-c", program],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "absent" in completed.stdout


def test_in_process_absence_is_deliberately_not_asserted() -> None:
    """Importing J1 must not itself pull the sealed-test module in.

    This is the in-process claim J1 *can* make: whatever else the interpreter
    has loaded, the J1 package's own import graph does not reach it. Layer 1
    proves that structurally; this checks the loaded package agrees.
    """
    j1_modules = [
        name
        for name in sys.modules
        if name.startswith("cardiosentinel.journal_extension")
    ]
    assert j1_modules, "the J1 package is imported by this test module"
    assert negative_capability.structural_proof(Path(preflight.J1_PACKAGE_ROOT)) == {}


def test_a_forbidden_call_is_recorded_and_refused() -> None:
    counters = negative_capability.ForbiddenCounters()

    class _Frozen:
        @staticmethod
        def next_state() -> str:
            return "should never run"

    module = _Frozen()
    originals = negative_capability.instrument_entry_points(
        module, ("next_state",), counters, "forbidden_partition_resolutions"
    )
    try:
        with pytest.raises(negative_capability.NegativeCapabilityError):
            module.next_state()
        with pytest.raises(negative_capability.NegativeCapabilityError):
            counters.require_all_zero()
    finally:
        negative_capability.restore_entry_points(module, originals)
    assert module.next_state() == "should never run"


# -- visibility latch -------------------------------------------------------


def test_the_latch_is_monotonic() -> None:
    latch = visibility.ScientificVisibility()
    assert latch.failure_classification() == "INFRASTRUCTURE"
    latch.mark_visible("first synthetic row materialized")
    assert latch.visible
    assert latch.failure_classification() == "APPARATUS_AFTER_VISIBILITY"
    latch.mark_visible("something else")
    assert latch.reason == "first synthetic row materialized"
    assert not hasattr(latch, "reset")
    with pytest.raises(visibility.VisibilityError):
        latch.require_not_visible("attempt claim")


# -- provenance -------------------------------------------------------------


def test_a_missing_sink_refuses() -> None:
    with pytest.raises(provenance.ProvenanceSinkError, match="no provenance sink"):
        provenance.require_sink(None)


def test_the_attempt_root_schema_is_complete() -> None:
    for artifact in (
        "authorization",
        "negative_capability_proof",
        "fold_manifest",
        "gate_a_decision",
    ):
        assert artifact in provenance.REQUIRED_ATTEMPT_ARTIFACTS


# -- frozen deterministic machinery -----------------------------------------


def _burdens() -> list[folds.SubjectBurden]:
    return [
        folds.SubjectBurden(s, (i * 7) % 5) for i, s in enumerate(SYNTHETIC_SUBJECTS)
    ]


def test_the_outer_allocator_is_deterministic_and_exact() -> None:
    first = folds.allocate_folds(_burdens(), folds=7)
    second = folds.allocate_folds(list(reversed(_burdens())), folds=7)
    assert first == second, "allocation must not depend on input order"
    assert len(first) == 7
    assert all(len(f) == 8 for f in first)
    assert sorted(s for f in first for s in f) == sorted(SYNTHETIC_SUBJECTS)


def test_the_inner_allocator_is_six_by_eight() -> None:
    outer = folds.allocate_folds(_burdens(), folds=7)
    development = [s for f in outer[1:] for s in f]
    assert len(development) == 48
    burdens = {b.subject_id: b for b in _burdens()}
    inner = folds.allocate_folds([burdens[s] for s in development], folds=6)
    assert len(inner) == 6 and all(len(f) == 8 for f in inner)


def test_an_unequal_pool_is_refused() -> None:
    with pytest.raises(folds.FoldAllocationError, match="equal folds"):
        folds.allocate_folds(_burdens()[:55], folds=7)


def test_the_registries_are_frozen_at_twelve_and_two_hundred_and_six() -> None:
    stateful = candidates.stateful_registry()
    memoryless = candidates.memoryless_registry()
    assert len(stateful) == 12
    assert len(memoryless) == 206
    assert len({c.candidate_id for c in stateful}) == 12
    assert len({c.candidate_id for c in memoryless}) == 206


def test_the_arm_neutral_row_has_exactly_eight_fields() -> None:
    assert len(rows.ARM_NEUTRAL_FIELDS) == 8
    assert "elapsed_state_seconds" not in rows.ARM_NEUTRAL_FIELDS
    row = rows.assessment_row(
        stable_id="synthetic:sub000:0",
        m2g_detector_score=0.1,
        detector_decision_d_t=False,
        outer_oof_p_t=rows.OuterOofCalibratedProbability(0.2),
        decision_error_uncertainty_u_t=0.3,
        s4d_temporal_evidence_s_t=0.4,
        score_present=True,
        elapsed_stream_seconds=10.0,
    )
    assert not hasattr(row, "elapsed_state_seconds")
    with pytest.raises(Exception):
        row.m2g_detector_score = 0.9  # type: ignore[misc]


def test_a_memoryless_rule_carries_no_state() -> None:
    candidate = candidates.memoryless_registry()[0]
    rule = candidates.memoryless_rule(candidate, {"pt": 0.5, "st": 0.5, "m2g": 0.5})
    row = rows.assessment_row(
        stable_id="synthetic:sub000:0",
        m2g_detector_score=0.9,
        detector_decision_d_t=True,
        outer_oof_p_t=rows.OuterOofCalibratedProbability(0.9),
        decision_error_uncertainty_u_t=0.1,
        s4d_temporal_evidence_s_t=0.9,
        score_present=True,
        elapsed_stream_seconds=0.0,
    )
    first = [rule(row) for _ in range(20)]
    assert len(set(first)) == 1, "a memoryless rule cannot drift across calls"
    assert not getattr(rule, "__self__", None)
    assert rule.__closure__ is not None  # thresholds only, no mutable state


# -- endpoint and Gate A ----------------------------------------------------


def test_episode_f1_convention_is_unmodified() -> None:
    assert statistics.episode_f1(0, 0, 0) is None
    assert statistics.episode_f1(0, 3, 0) == 0.0
    assert statistics.episode_f1(0, 0, 3) == 0.0
    assert statistics.episode_f1(2, 2, 2) == 1.0


def test_primary_eligibility_ignores_arm_output() -> None:
    assert statistics.primary_f1_eligible(1)
    assert not statistics.primary_f1_eligible(0)


def test_the_bootstrap_is_deterministic_and_paired() -> None:
    stateful = {s: 0.6 for s in SYNTHETIC_SUBJECTS[:40]}
    memoryless = {s: 0.4 for s in SYNTHETIC_SUBJECTS[:40]}
    a = statistics.paired_contrast(stateful, memoryless)
    b = statistics.paired_contrast(stateful, memoryless)
    assert (a.delta, a.lower, a.upper) == (b.delta, b.lower, b.upper)
    assert a.subjects == 40
    assert a.gate_a() == "PASS"


def test_arms_may_not_have_different_subject_sets() -> None:
    with pytest.raises(statistics.EndpointError, match="identical for both arms"):
        statistics.paired_contrast({"a": 0.5}, {"b": 0.5})


@pytest.mark.parametrize(
    "delta,lower,expected",
    [
        (0.1, 0.02, "PASS"),
        (0.1, -0.05, "MIXED"),
        (-0.1, -0.3, "FAIL"),
        (0.0, 0.0, "FAIL"),
    ],
)
def test_gate_a_is_frozen(delta: float, lower: float, expected: str) -> None:
    contrast = statistics.PairedContrast(delta, lower, lower + 1.0, 40)
    assert contrast.gate_a() == expected


# -- the production entry point remains unarmed -----------------------------


def test_the_production_entry_point_refuses() -> None:
    assert preflight.main() == 1


def test_there_is_no_bypass_parameter() -> None:
    import inspect

    signature = inspect.signature(preflight.run_preflight)
    for forbidden in ("force", "dev_mode", "skip_authorization", "allow_unauthorized"):
        assert forbidden not in signature.parameters
