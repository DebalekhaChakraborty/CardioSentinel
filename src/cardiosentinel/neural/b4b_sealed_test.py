"""Sealed-test entry point bound to the architecture selected in development.

`sealed_test` targets `B4_raw_compact_cnn_v1` (B4-A) through module constants.
B4-A was **rejected** during Phase 3B-2 architecture selection; the selected
global short-window encoder is **B4-B**, `B4B_cnn_transformer_v1` /
`B4BTransformerCNN`, frozen by `docs/B4_GLOBAL_ENCODER_SELECTION_V1.md`.

Nothing in the repository previously connected the experiment named in a
sealed-test authorization to the experiment the evaluator would actually load.
Both were individually correct and they referred to different models. This
module closes that gap by binding the evaluator to a declared selection and
refusing to run when any element of the identity chain disagrees.

**Order matters.** `verify_selection_identity` runs to completion before any
attempt receipt is created and before any sealed-test artifact is resolved,
opened or hashed. Every check it performs reads development artifacts only. A
mismatch therefore fails closed: no test access, no `TEST_ATTEMPT.json`, and the
one-shot budget remains unspent.

Protections inherited from `sealed_test` are preserved verbatim: receipt before
access, capability-gated resolution, checkpoint-only weights with no optimizer
state, `eval()` with gradients disabled, threshold read from the immutable
development lock, and exactly one attempt with no force, retry or reset.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import torch
from torch import nn

from cardiosentinel.baseline.cache import read_json
from cardiosentinel.data.provenance import sha256_file
from cardiosentinel.neural.candidates import B4BTransformerCNN
from cardiosentinel.neural.experiment import (
    EXPERIMENT_LOCK_NAME,
    validate_experiment_lock,
)
from cardiosentinel.neural.integrity import verify_experiment_lock
from cardiosentinel.neural.protocol import REPOSITORY_ROOT
from cardiosentinel.neural.sealed_test import (
    SealedTestAttemptError,
    _require_access,
)

SELECTION_DOCUMENT = "docs/B4_GLOBAL_ENCODER_SELECTION_V1.json"
VALIDATION_THRESHOLD_NAME = "VALIDATION_THRESHOLD.json"
LOCKED_FOR_TEST = "locked_for_one_shot_test"


class SelectionIdentityError(RuntimeError):
    """Raised when the evaluator is not provably bound to the selected model.

    Distinct from `SealedTestAttemptError` on purpose: this is refused *before*
    the one-shot contract is entered at all, so raising it leaves the sealed
    test unopened rather than consuming an attempt.
    """


@dataclass(frozen=True, slots=True)
class SelectedArchitectureBinding:
    """The identity a sealed evaluation is authorized against.

    Every field is a value an authorization document names. The binding exists
    so that "the model the authorization names" and "the model the evaluator
    loads" are one object that can be compared, rather than two module
    constants in different files that happen to agree, or in our case did not.
    """

    experiment_id: str
    architecture: str
    run_collection: str
    checkpoint_name: str
    checkpoint_sha256: str
    experiment_lock_sha256: str
    model_factory: Callable[[], nn.Module]

    def build_model(self) -> nn.Module:
        model = self.model_factory()
        observed = type(model).__name__
        if observed != self.architecture:
            raise SelectionIdentityError(
                f"Model factory produced {observed}, not {self.architecture}."
            )
        return model


B4B_BINDING = SelectedArchitectureBinding(
    experiment_id="B4B_cnn_transformer_v1",
    architecture="B4BTransformerCNN",
    run_collection="phase3b2-architecture-v1",
    checkpoint_name="model_selected.pt",
    checkpoint_sha256=(
        "b1301723909c641a0014c31f6daa9549d47ab231f0b07483e0de729aff5591c9"
    ),
    experiment_lock_sha256=(
        "58e44a09ce3ebffecfcd49d957acfa368fc03b534fdcd990aedb9b6b0e9bda7b"
    ),
    model_factory=B4BTransformerCNN,
)


def resolve_selected_run_dir(
    run_root: Path, binding: SelectedArchitectureBinding = B4B_BINDING
) -> Path:
    """Resolve the run directory for the bound experiment, and only that one."""
    run_dir = Path(run_root) / binding.experiment_id
    if not run_dir.is_dir():
        raise SelectionIdentityError(
            f"No run directory for {binding.experiment_id} under {run_root}."
        )
    return run_dir


def read_selection_record(
    repository_root: Path = REPOSITORY_ROOT,
) -> dict[str, Any]:
    """Read the frozen architecture-selection record. Development artifact."""
    path = Path(repository_root) / SELECTION_DOCUMENT
    if not path.is_file():
        raise SelectionIdentityError(f"Selection record absent: {path}.")
    return json.loads(path.read_text())


def verify_selection_identity(
    run_root: Path,
    binding: SelectedArchitectureBinding = B4B_BINDING,
    *,
    repository_root: Path = REPOSITORY_ROOT,
) -> dict[str, Any]:
    """Prove the evaluator, the authorization and the artifacts name one model.

    Reads development artifacts only -- the selection record, the experiment
    lock, the checkpoint bytes and the validation-threshold receipt. It resolves
    no sealed-test path, opens no test cache, and reads no label. Raising here
    leaves the sealed test unopened.

    Returns the verified identity for recording in the attempt receipt.
    """
    selection = read_selection_record(repository_root)

    # 1. the selection record names this experiment as the selected model.
    #
    # The rejected-candidate check runs FIRST and deliberately so. A binding
    # naming a rejected candidate would also fail the equality check below, but
    # with a message about two identifiers disagreeing -- true, and useless for
    # diagnosis. Naming the candidate as rejected is what tells a reader which
    # mistake they made, and that mistake is the one this module exists for.
    rejected = selection.get("rejected_candidates") or {}
    for label, entry in rejected.items():
        if entry.get("experiment_id") == binding.experiment_id:
            raise SelectionIdentityError(
                f"{binding.experiment_id} is recorded as rejected candidate "
                f"{label}. A rejected architecture cannot be evaluated through "
                f"the selected-model test path."
            )
    if selection.get("experiment_id") != binding.experiment_id:
        raise SelectionIdentityError(
            f"Selection record names {selection.get('experiment_id')!r}; the "
            f"evaluator is bound to {binding.experiment_id!r}."
        )
    if selection.get("architecture") != binding.architecture:
        raise SelectionIdentityError(
            f"Selection record names architecture "
            f"{selection.get('architecture')!r}; the evaluator is bound to "
            f"{binding.architecture!r}."
        )

    # 2. the lock is internally valid and is the lock the authorization names
    run_dir = resolve_selected_run_dir(run_root, binding)
    lock = validate_experiment_lock(run_dir)
    if not verify_experiment_lock(lock):
        raise SelectionIdentityError("Experiment lock self-digest does not verify.")
    if lock["experiment_lock_sha256"] != binding.experiment_lock_sha256:
        raise SelectionIdentityError(
            "Experiment lock digest is not the one the authorization names."
        )
    if lock["experiment_id"] != binding.experiment_id:
        raise SelectionIdentityError(
            f"Lock holds {lock['experiment_id']!r}; the evaluator is bound to "
            f"{binding.experiment_id!r}."
        )
    if lock.get("candidate_architecture") != binding.architecture:
        raise SelectionIdentityError(
            f"Lock holds architecture {lock.get('candidate_architecture')!r}; "
            f"the evaluator is bound to {binding.architecture!r}."
        )
    if lock.get("status") != LOCKED_FOR_TEST:
        raise SelectionIdentityError("The development lock is not sealed for test.")
    if lock.get("test") is not None:
        raise SelectionIdentityError("The development lock already records a test.")
    if lock.get("git_dirty") is not False:
        raise SelectionIdentityError("The development lock is not from a clean tree.")

    # 3. the checkpoint on disk is the one the authorization names
    if str(lock["locked_inference_model"]) != binding.checkpoint_name:
        raise SelectionIdentityError(
            f"Lock names checkpoint {lock['locked_inference_model']!r}; the "
            f"evaluator is bound to {binding.checkpoint_name!r}."
        )
    checkpoint = run_dir / binding.checkpoint_name
    if not checkpoint.is_file():
        raise SelectionIdentityError("The locked inference checkpoint is absent.")
    observed_checkpoint = sha256_file(checkpoint)
    if observed_checkpoint != binding.checkpoint_sha256:
        raise SelectionIdentityError(
            "Checkpoint SHA-256 is not the one the authorization names."
        )
    if observed_checkpoint != lock["checkpoint_sha256"]:
        raise SelectionIdentityError("Checkpoint SHA-256 disagrees with the lock.")

    # 4. the threshold came from validation and from this lock
    threshold_path = run_dir / VALIDATION_THRESHOLD_NAME
    if not threshold_path.is_file():
        raise SelectionIdentityError("The validation-threshold receipt is absent.")
    receipt = read_json(threshold_path)
    if receipt.get("selected_from") != "validation":
        raise SelectionIdentityError(
            f"Threshold selected_from is {receipt.get('selected_from')!r}, "
            "not 'validation'."
        )
    if receipt.get("test_informed") is not False:
        raise SelectionIdentityError("The threshold receipt is test-informed.")
    if receipt.get("threshold") != lock["validation_threshold"]:
        raise SelectionIdentityError(
            "Threshold receipt and experiment lock disagree."
        )

    # 5. the model class the evaluator would construct
    model = binding.build_model()
    architecture_observed = type(model).__name__
    del model

    return {
        "selection_document": SELECTION_DOCUMENT,
        "authorized_experiment_id": binding.experiment_id,
        "evaluator_experiment_id": lock["experiment_id"],
        "authorized_architecture": binding.architecture,
        "evaluator_model_class": architecture_observed,
        "run_collection": binding.run_collection,
        "run_dir": str(run_dir),
        "checkpoint_name": binding.checkpoint_name,
        "checkpoint_sha256": observed_checkpoint,
        "experiment_lock_sha256": lock["experiment_lock_sha256"],
        "locked_validation_threshold": lock["validation_threshold"],
        "threshold_source": "immutable_development_experiment_lock",
        "threshold_selected_from": receipt["selected_from"],
        "threshold_test_informed": receipt["test_informed"],
        "identity_verified": True,
    }


def load_selected_model(
    access: Any,
    run_dir: Path,
    lock: dict[str, Any],
    device: str,
    binding: SelectedArchitectureBinding = B4B_BINDING,
) -> nn.Module:
    """Load the bound architecture's locked weights. No optimizer, no gradients.

    Mirrors `sealed_test.load_locked_model` guard for guard, differing only in
    which architecture is constructed and in refusing a checkpoint whose digest
    is not the bound one.
    """
    _require_access(access)
    checkpoint = Path(run_dir) / binding.checkpoint_name
    observed = sha256_file(checkpoint)
    if observed != binding.checkpoint_sha256:
        raise SelectionIdentityError(
            "Checkpoint is not the bound selected checkpoint."
        )
    if observed != access.checkpoint_sha256:
        raise SealedTestAttemptError(
            "The locked checkpoint changed before inference."
        )
    state = torch.load(checkpoint, map_location="cpu", weights_only=True)
    if "optimizer" in state:
        raise SealedTestAttemptError(
            "The locked inference artifact must not carry optimizer state."
        )
    model = binding.build_model()
    model.load_state_dict(state)
    model.to(torch.device(device))
    model.eval()
    model.requires_grad_(False)
    return model


def describe_binding(
    binding: SelectedArchitectureBinding = B4B_BINDING,
) -> dict[str, str]:
    """Report the binding without touching disk. For provenance and reporting."""
    return {
        "experiment_id": binding.experiment_id,
        "architecture": binding.architecture,
        "run_collection": binding.run_collection,
        "checkpoint_name": binding.checkpoint_name,
        "checkpoint_sha256": binding.checkpoint_sha256,
        "experiment_lock_sha256": binding.experiment_lock_sha256,
    }


# ---------------------------------------------------------------------------
# One-shot attempt and evaluation for the selected architecture
#
# The private helpers below are imported from `sealed_test` rather than
# reimplemented. The one-shot receipt logic -- the atomic O_EXCL claim, the
# durable amend, the fsync discipline -- must have exactly one implementation.
# A second copy would be a second thing to get wrong, in the one place where
# being wrong costs the budget.
# ---------------------------------------------------------------------------

import re
import time
import traceback

import numpy as np

from cardiosentinel.baseline.source import OFFICIAL_MANIFEST_SHA256
from cardiosentinel.data.provenance import git_provenance
from cardiosentinel.neural.determinism import initialize_determinism
from cardiosentinel.neural.experiment import PROGRAM_IDENTITY, input_contract
from cardiosentinel.neural.integrity import canonical_sha256
from cardiosentinel.neural.protocol import (
    DATASET,
    DATASET_VERSION,
    FEATURE_CORPUS_SHA256,
    validate_frozen_protocol,
)
from cardiosentinel.neural.provenance import runtime_environment
from cardiosentinel.neural.sealed_test import (
    ATTEMPT_COMPLETE,
    ATTEMPT_FAILED,
    ATTEMPT_SEQUENCE,
    ATTEMPT_STARTED,
    CHALLENGE_FAMILIES,
    TEST_ATTEMPT_NAME,
    TEST_AUDIT_NAME,
    TEST_METRICS_NAME,
    TEST_PREDICTIONS_NAME,
    SealedTestAccess,
    _arrays,
    _execution_payload,
    _update_attempt,
    build_test_evidence,
    claim_attempt_exclusively,
    load_sealed_test_references,
    model_state_sha256,
    score_sealed_test,
    validate_sealed_test_feature_integrity,
    validate_sealed_test_source_integrity,
    verify_primary_population,
    write_json_durable,
    write_test_predictions,
)

SELECTED_DEFAULT_COMMAND = "cardiosentinel b4b evaluate-selected-locked-test"

SELECTED_EXPERIMENT_ID = "B4B_cnn_transformer_v1"
SELECTED_ARCHITECTURE = "B4BTransformerCNN"

#: Fields the audit artifact must carry. The reporting commitment in
#: B4_TEST_AUTHORIZATION_V1 depends on every one of them, so a payload missing
#: any is not a partial result -- it is an unreportable one.
REQUIRED_AUDIT_FIELDS: frozenset[str] = frozenset({
    "experiment_id",
    "architecture",
    "selection_identity",
    "attempt_status",
    "attempt_sequence",
    "repeat_attempt_permitted",
    "experiment_lock_sha256",
    "initial_attempt_receipt_sha256",
    "development_git_sha",
    "evaluator_git_sha",
    "checkpoint_sha256",
    "locked_validation_threshold",
    "threshold_source",
    "split_sha256",
    "dataset",
    "dataset_version",
    "sealed_test_feature_integrity_sha256",
    "sealed_test_source_integrity_sha256",
    "test_primary_counts",
    "test_challenge_counts",
    "scored_row_count",
    "predictions_sha256",
    "metrics_sha256",
    "model_state_sha256_before_inference",
    "model_state_sha256_after_inference",
    "model_weights_unchanged",
    "optimizer_constructed",
    "backward_invoked",
    "threshold_selection_performed",
})

#: Lock keys the audit assembly reads. Absence would raise KeyError after the
#: rows had been read, which spends the budget and produces nothing.
REQUIRED_LOCK_KEYS: tuple[str, ...] = (
    "experiment_id",
    "experiment_lock_sha256",
    "checkpoint_sha256",
    "locked_inference_model",
    "validation_threshold",
    "threshold_selection_rule",
    "split_sha256",
    "git_sha",
)

_SHA256_PATTERN = re.compile(r"\A[0-9a-f]{64}\Z")


class AuditSchemaError(RuntimeError):
    """Raised when the audit payload could not be assembled or is incomplete.

    Like `SelectionIdentityError`, raising this before the attempt is claimed
    leaves the sealed test unopened. The pre-flight exists so that a payload
    defect is discovered then, rather than after the rows have been read.
    """


def preflight_audit_schema(
    binding: SelectedArchitectureBinding,
    lock: dict[str, Any],
    identity: dict[str, Any],
    run_dir: Path,
) -> dict[str, Any]:
    """Prove the audit payload is assemblable **before** any sealed-test access.

    Reads development artifacts only. Every failure here happens before
    `TEST_ATTEMPT.json` exists and before a single test row is loaded.
    """
    if binding.experiment_id != SELECTED_EXPERIMENT_ID:
        raise AuditSchemaError(
            f"Audit identity is {binding.experiment_id!r}; the authorized "
            f"experiment is {SELECTED_EXPERIMENT_ID!r}."
        )
    if binding.architecture != SELECTED_ARCHITECTURE:
        raise AuditSchemaError(
            f"Audit architecture is {binding.architecture!r}; the authorized "
            f"architecture is {SELECTED_ARCHITECTURE!r}."
        )
    if identity.get("identity_verified") is not True:
        raise AuditSchemaError("Selection identity was not verified.")

    for key in ("checkpoint_sha256", "experiment_lock_sha256"):
        value = getattr(binding, key)
        if not isinstance(value, str) or not _SHA256_PATTERN.match(value):
            raise AuditSchemaError(f"Binding {key} is not a SHA-256 digest.")

    missing = [key for key in REQUIRED_LOCK_KEYS if key not in lock]
    if missing:
        raise AuditSchemaError(f"Lock is missing audit references: {missing}.")
    if lock["experiment_id"] != binding.experiment_id:
        raise AuditSchemaError("Lock experiment does not match the binding.")
    for key in ("checkpoint_sha256", "experiment_lock_sha256", "split_sha256"):
        if not _SHA256_PATTERN.match(str(lock[key])):
            raise AuditSchemaError(f"Lock {key} is not a SHA-256 digest.")

    checkpoint = Path(run_dir) / str(lock["locked_inference_model"])
    if not checkpoint.is_file():
        raise AuditSchemaError("Lock references a checkpoint that does not resolve.")

    return {
        "audit_schema_verified": True,
        "required_audit_fields": sorted(REQUIRED_AUDIT_FIELDS),
        "required_lock_keys": list(REQUIRED_LOCK_KEYS),
    }


def validate_audit_payload(audit: dict[str, Any]) -> dict[str, Any]:
    """Refuse to write an audit that the reporting commitment cannot use."""
    missing = sorted(REQUIRED_AUDIT_FIELDS - set(audit))
    if missing:
        raise AuditSchemaError(f"Audit payload is missing fields: {missing}.")
    if audit.get("experiment_id") != SELECTED_EXPERIMENT_ID:
        raise AuditSchemaError("Audit payload names the wrong experiment.")
    if audit.get("architecture") != SELECTED_ARCHITECTURE:
        raise AuditSchemaError("Audit payload names the wrong architecture.")
    return audit


def open_selected_sealed_test_attempt(
    source: Path,
    feature_root: Path,
    run_root: Path,
    binding: SelectedArchitectureBinding = B4B_BINDING,
    *,
    command: str = SELECTED_DEFAULT_COMMAND,
    requested_device: str | None = None,
    workers: int = 0,
) -> tuple[SealedTestAccess, dict[str, Any], dict[str, Any]]:
    """Verify the selection identity, then durably claim attempt #1.

    Mirrors `sealed_test.open_sealed_test_attempt` guard for guard, with one
    addition and one substitution: `verify_selection_identity` runs first, and
    the bound experiment replaces the module-level B4-A constant.

    Every check below reads development artifacts only. If any fails, no
    receipt is written and the sealed test remains unopened.
    """
    # The identity gate. Nothing beyond this point may run for a model the
    # authorization does not name.
    identity = verify_selection_identity(run_root, binding)

    protocol_sha256 = validate_frozen_protocol()
    provenance = git_provenance(REPOSITORY_ROOT)
    if provenance["git_dirty"]:
        raise SealedTestAttemptError(
            "The sealed-test evaluation requires a clean evaluator checkout."
        )
    run_dir = resolve_selected_run_dir(run_root, binding)
    lock = validate_experiment_lock(run_dir)

    threshold = lock["validation_threshold"]
    if not isinstance(threshold, float) or not np.isfinite(threshold):
        raise SealedTestAttemptError("The lock has no finite validation threshold.")

    # Audit schema pre-flight. Assembling the audit is the last thing the
    # evaluation does, and a defect there would surface after the rows had been
    # read. Prove it is assemblable now, while failing still costs nothing.
    schema = preflight_audit_schema(binding, lock, identity, run_dir)

    receipt_path = run_dir / TEST_ATTEMPT_NAME
    determinism = initialize_determinism(requested_device=requested_device)
    environment = runtime_environment(determinism.device, workers)
    execution = _execution_payload(
        command, source, feature_root, run_root, requested_device,
        determinism.device, workers,
    )
    receipt = {
        "experiment_id": binding.experiment_id,
        "architecture": binding.architecture,
        "selection_identity": identity,
        "audit_schema": schema,
        "attempt_sequence": ATTEMPT_SEQUENCE,
        "attempt_status": ATTEMPT_STARTED,
        "repeat_attempt_permitted": False,
        "experiment_lock_sha256": lock["experiment_lock_sha256"],
        "locked_checkpoint_sha256": lock["checkpoint_sha256"],
        "locked_validation_threshold": threshold,
        "threshold_selection_rule": lock["threshold_selection_rule"],
        "development_git_sha": lock["git_sha"],
        "evaluator_git_sha": provenance["git_sha"],
        "evaluator_git_dirty": provenance["git_dirty"],
        "protocol_sha256": protocol_sha256,
        "split_sha256": lock["split_sha256"],
        "dataset": DATASET,
        "dataset_version": DATASET_VERSION,
        "input_contract": input_contract(),
        "program": PROGRAM_IDENTITY,
        "environment": environment,
        "execution": execution,
        "created_at_utc_audit_only": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
        ),
        "test_data_access_began": False,
        "test": None,
    }
    # Atomic, durable, exactly once. Nothing above this line has resolved or
    # opened a single sealed-test artifact.
    initial_receipt_sha256 = claim_attempt_exclusively(receipt_path, receipt)
    access = SealedTestAccess(
        run_dir=run_dir,
        receipt_path=receipt_path,
        initial_attempt_receipt_sha256=initial_receipt_sha256,
        experiment_lock_sha256=lock["experiment_lock_sha256"],
        checkpoint_sha256=lock["checkpoint_sha256"],
        locked_threshold=threshold,
    )
    return access, lock, identity


def evaluate_selected_locked_test(
    source: Path,
    feature_root: Path,
    run_root: Path,
    binding: SelectedArchitectureBinding = B4B_BINDING,
    *,
    command: str = SELECTED_DEFAULT_COMMAND,
    requested_device: str | None = None,
    workers: int = 0,
    _reader=None,
) -> dict[str, Any]:
    """Perform the single predeclared sealed-test evaluation of the selected model.

    There is no force, retry, reset, threshold, checkpoint or seed option. The
    checkpoint and threshold come only from the immutable development lock, and
    the architecture comes only from the binding the authorization names.
    """
    started = time.monotonic()
    access, lock, identity = open_selected_sealed_test_attempt(
        source,
        feature_root,
        run_root,
        binding,
        command=command,
        requested_device=requested_device,
        workers=workers,
    )
    run_dir = access.run_dir
    device = read_json(access.receipt_path)["execution"]["resolved_device"]
    test_access_began = False
    try:
        test_access_began = True
        _update_attempt(access, test_data_access_began=True)
        feature_receipt = validate_sealed_test_feature_integrity(access, feature_root)
        source_receipt = validate_sealed_test_source_integrity(
            access, source, feature_receipt
        )

        references = load_sealed_test_references(access, feature_root)
        primary_counts = verify_primary_population(references)

        model = load_selected_model(access, run_dir, lock, device, binding)
        model_sha_before = model_state_sha256(model)
        scores = score_sealed_test(
            access, source, references, model, device, _reader=_reader
        )
        model_sha_after = model_state_sha256(model)
        if model_sha_before != model_sha_after:
            raise SealedTestAttemptError(
                "The locked weights changed during sealed-test inference."
            )

        evidence = build_test_evidence(references, scores, access.locked_threshold)
        metrics_sha256 = write_json_durable(run_dir / TEST_METRICS_NAME, evidence)
        predictions_sha256 = write_test_predictions(
            access, run_dir / TEST_PREDICTIONS_NAME, references, scores
        )
        duration = time.monotonic() - started
        audit = {
            "experiment_id": binding.experiment_id,
            "architecture": binding.architecture,
            "selection_identity": identity,
            "attempt_status": ATTEMPT_COMPLETE,
            "attempt_sequence": ATTEMPT_SEQUENCE,
            "repeat_attempt_permitted": False,
            "experiment_lock_sha256": access.experiment_lock_sha256,
            "initial_attempt_receipt_sha256": access.initial_attempt_receipt_sha256,
            "development_git_sha": lock["git_sha"],
            "evaluator_git_sha": git_provenance(REPOSITORY_ROOT)["git_sha"],
            "evaluator_git_dirty": False,
            "checkpoint_sha256": access.checkpoint_sha256,
            "locked_validation_threshold": access.locked_threshold,
            "threshold_source": "immutable_development_experiment_lock",
            "split_sha256": lock["split_sha256"],
            "dataset": DATASET,
            "dataset_version": DATASET_VERSION,
            "input_contract": input_contract(),
            "waveform_retrieval": "record-aware direct canonical source reads",
            "external_test_waveform_cache": None,
            "sealed_test_feature_integrity_sha256": feature_receipt[
                "sealed_test_feature_integrity_sha256"
            ],
            "sealed_test_source_integrity_sha256": source_receipt[
                "sealed_test_source_integrity_sha256"
            ],
            "canonical_feature_corpus_sha256": FEATURE_CORPUS_SHA256,
            "official_source_manifest_sha256": OFFICIAL_MANIFEST_SHA256,
            "verified_test_record_count": feature_receipt["verified_test_record_count"],
            "verified_test_cache_count": feature_receipt["verified_test_cache_count"],
            "verified_test_source_file_count": source_receipt[
                "verified_test_source_file_count"
            ],
            "test_primary_counts": primary_counts,
            "test_challenge_counts": {
                family: int(np.sum(_arrays(references)["target_family"] == family))
                for family in CHALLENGE_FAMILIES
            },
            "scored_row_count": int(scores.size),
            "environment": runtime_environment(device, workers),
            "execution": read_json(access.receipt_path)["execution"],
            "predictions_sha256": predictions_sha256,
            "metrics_sha256": metrics_sha256,
            "model_state_sha256_before_inference": model_sha_before,
            "model_state_sha256_after_inference": model_sha_after,
            "model_weights_unchanged": True,
            "optimizer_constructed": False,
            "backward_invoked": False,
            "threshold_selection_performed": False,
            "duration_seconds": duration,
        }
        validate_audit_payload(audit)
        audit["test_audit_sha256"] = canonical_sha256(audit)
        audit_sha256 = write_json_durable(run_dir / TEST_AUDIT_NAME, audit)
        _update_attempt(
            access,
            attempt_status=ATTEMPT_COMPLETE,
            test_data_access_began=True,
            test_audit_sha256=audit_sha256,
            test_metrics_sha256=metrics_sha256,
            test_predictions_sha256=predictions_sha256,
            sealed_test_feature_integrity_sha256=feature_receipt[
                "sealed_test_feature_integrity_sha256"
            ],
            sealed_test_source_integrity_sha256=source_receipt[
                "sealed_test_source_integrity_sha256"
            ],
            completed_at_utc_audit_only=time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
            ),
        )
        return {
            "attempt_status": ATTEMPT_COMPLETE,
            "experiment_id": binding.experiment_id,
            "architecture": binding.architecture,
            "run_dir": str(run_dir),
            "threshold": access.locked_threshold,
            "test_evidence": evidence,
            "test_audit_sha256": audit_sha256,
            "repeat_attempt_permitted": False,
        }
    except BaseException as error:
        # Recording the failure must never replace the failure. Catching only
        # OSError here would let any other recording fault -- a KeyError, a
        # serialisation fault, a full disk surfacing as something else --
        # propagate in place of the original, and the original is the one that
        # explains what happened to the budget.
        try:
            _update_attempt(
                access,
                attempt_status=ATTEMPT_FAILED,
                test_data_access_began=test_access_began,
                error_type=type(error).__name__,
                error=str(error),
                traceback=traceback.format_exc(limit=20),
                human_review_required=True,
                repeat_attempt_permitted=False,
            )
        except BaseException as recording_error:  # noqa: BLE001
            note = (
                "Failure recording ALSO failed: "
                f"{type(recording_error).__name__}: {recording_error}. "
                f"The attempt receipt at {access.receipt_path} may be stale or "
                "absent; the attempt was nonetheless consumed and requires "
                "human review."
            )
            try:
                error.add_note(note)
            except AttributeError:  # pragma: no cover - Python < 3.11
                pass
        raise
