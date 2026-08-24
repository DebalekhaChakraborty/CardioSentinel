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
