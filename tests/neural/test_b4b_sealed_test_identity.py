"""The selected-architecture evaluator must refuse anything but B4-B.

Every negative case asserts the same two things: the call raises, and no
`TEST_ATTEMPT.json` exists anywhere afterwards. A refusal that consumed the
one-shot budget would be worse than the defect these tests exist to prevent.

None of these tests reads a sealed-test row, label or cache. The positive cases
use development artifacts and the validation partition only.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest
import torch

from cardiosentinel.neural.b4b_sealed_test import (
    B4B_BINDING,
    SelectedArchitectureBinding,
    SelectionIdentityError,
    describe_binding,
    resolve_selected_run_dir,
    verify_selection_identity,
)
from cardiosentinel.neural.candidates import B4BTransformerCNN
from cardiosentinel.neural.model import B4CompactCNN
from cardiosentinel.neural.protocol import REPOSITORY_ROOT

RUNS = Path(REPOSITORY_ROOT) / "cardiosentinel-runs"
B4B_ROOT = RUNS / "phase3b2-architecture-v1"
B4A_ROOT = RUNS / "phase3b2-b4-v1"

B4A_EXPERIMENT_ID = "B4_raw_compact_cnn_v1"
B4A_CHECKPOINT_SHA256 = (
    "3a33cfb3c05e0f26fc8bc9c3bb826710215921da11b1ecd3a7ea92c3c57e9175"
)
B4A_LOCK_SHA256 = (
    "ea1e1d76365b0cd52ba1b7f022f22f85af848bbdc002beeae806eda9c39a78fa"
)


def _no_attempt_anywhere() -> int:
    return len(list(RUNS.rglob("TEST_ATTEMPT*")))


@pytest.fixture(autouse=True)
def sealed_test_stays_unopened():
    """Guard every test in this module on both sides of the call."""
    assert _no_attempt_anywhere() == 0, "A TEST_ATTEMPT existed before the test."
    yield
    assert _no_attempt_anywhere() == 0, "A TEST_ATTEMPT was created by the test."


# --------------------------------------------------------------------------
# positive: the binding is the selected architecture
# --------------------------------------------------------------------------


def test_binding_names_the_selected_experiment():
    assert B4B_BINDING.experiment_id == "B4B_cnn_transformer_v1"
    assert B4B_BINDING.architecture == "B4BTransformerCNN"
    assert B4B_BINDING.run_collection == "phase3b2-architecture-v1"


def test_binding_agrees_with_the_frozen_selection_record():
    record = json.loads(
        (Path(REPOSITORY_ROOT) / "docs/B4_GLOBAL_ENCODER_SELECTION_V1.json").read_text()
    )
    assert record["selected_official_model"] == "B4-B"
    assert record["experiment_id"] == B4B_BINDING.experiment_id
    assert record["architecture"] == B4B_BINDING.architecture
    assert record["checkpoint_sha256"] == B4B_BINDING.checkpoint_sha256
    assert record["experiment_lock_sha256"] == B4B_BINDING.experiment_lock_sha256


def test_identity_verifies_for_the_selected_model():
    result = verify_selection_identity(B4B_ROOT)
    assert result["identity_verified"] is True
    assert result["authorized_experiment_id"] == result["evaluator_experiment_id"]
    assert result["authorized_architecture"] == result["evaluator_model_class"]
    assert result["threshold_selected_from"] == "validation"
    assert result["threshold_test_informed"] is False


def test_model_factory_builds_the_authorized_class():
    model = B4B_BINDING.build_model()
    assert type(model).__name__ == "B4BTransformerCNN"


# --------------------------------------------------------------------------
# negative: B4-A in any form must be refused, fail closed
# --------------------------------------------------------------------------


def test_refuses_b4a_run_root():
    """The B4-A collection holds no directory for the bound experiment."""
    with pytest.raises(SelectionIdentityError):
        verify_selection_identity(B4A_ROOT)


def test_refuses_b4a_experiment_id():
    binding = replace(B4B_BINDING, experiment_id=B4A_EXPERIMENT_ID)
    with pytest.raises(SelectionIdentityError) as excinfo:
        verify_selection_identity(B4A_ROOT, binding)
    assert "rejected candidate" in str(excinfo.value)


def test_refuses_b4a_lock_digest():
    binding = replace(B4B_BINDING, experiment_lock_sha256=B4A_LOCK_SHA256)
    with pytest.raises(SelectionIdentityError) as excinfo:
        verify_selection_identity(B4B_ROOT, binding)
    assert "not the one the authorization names" in str(excinfo.value)


def test_refuses_b4a_checkpoint_digest():
    binding = replace(B4B_BINDING, checkpoint_sha256=B4A_CHECKPOINT_SHA256)
    with pytest.raises(SelectionIdentityError) as excinfo:
        verify_selection_identity(B4B_ROOT, binding)
    assert "not the one the authorization names" in str(excinfo.value)


def test_refuses_mismatched_model_class():
    """A factory that builds the rejected architecture is refused."""
    binding = replace(B4B_BINDING, model_factory=B4CompactCNN)
    with pytest.raises(SelectionIdentityError) as excinfo:
        verify_selection_identity(B4B_ROOT, binding)
    assert "B4CompactCNN" in str(excinfo.value)


def test_refuses_architecture_name_disagreeing_with_the_lock():
    binding = replace(
        B4B_BINDING, architecture="B4CompactCNN", model_factory=B4CompactCNN
    )
    with pytest.raises(SelectionIdentityError):
        verify_selection_identity(B4B_ROOT, binding)


def test_refuses_absent_run_directory(tmp_path):
    with pytest.raises(SelectionIdentityError):
        verify_selection_identity(tmp_path)


# --------------------------------------------------------------------------
# development-only validation: weights are not interchangeable
# --------------------------------------------------------------------------


def test_b4b_checkpoint_loads_into_the_selected_architecture():
    """Development artifact only. No test partition is touched."""
    run_dir = resolve_selected_run_dir(B4B_ROOT)
    state = torch.load(
        run_dir / B4B_BINDING.checkpoint_name, map_location="cpu", weights_only=True
    )
    assert "optimizer" not in state
    model = B4BTransformerCNN()
    model.load_state_dict(state)
    model.eval()
    model.requires_grad_(False)
    assert not model.training
    assert all(not p.requires_grad for p in model.parameters())


def test_b4a_checkpoint_cannot_load_into_the_selected_architecture():
    """The two candidates are not weight-compatible; confusion cannot be silent."""
    b4a_checkpoint = B4A_ROOT / B4A_EXPERIMENT_ID / "model_selected.pt"
    if not b4a_checkpoint.is_file():
        pytest.skip("B4-A development checkpoint is not present in this tree.")
    state = torch.load(b4a_checkpoint, map_location="cpu", weights_only=True)
    with pytest.raises(RuntimeError):
        B4BTransformerCNN().load_state_dict(state)


def test_b4b_checkpoint_cannot_load_into_the_rejected_architecture():
    run_dir = resolve_selected_run_dir(B4B_ROOT)
    state = torch.load(
        run_dir / B4B_BINDING.checkpoint_name, map_location="cpu", weights_only=True
    )
    with pytest.raises(RuntimeError):
        B4CompactCNN().load_state_dict(state)


# --------------------------------------------------------------------------
# provenance
# --------------------------------------------------------------------------


def test_describe_binding_reports_the_selected_identity():
    described = describe_binding()
    assert described["experiment_id"] == "B4B_cnn_transformer_v1"
    assert described["architecture"] == "B4BTransformerCNN"
    assert described["checkpoint_sha256"] == B4B_BINDING.checkpoint_sha256


def test_identity_result_carries_provenance_for_the_receipt():
    result = verify_selection_identity(B4B_ROOT)
    for field in (
        "selection_document",
        "authorized_experiment_id",
        "evaluator_experiment_id",
        "evaluator_model_class",
        "checkpoint_sha256",
        "experiment_lock_sha256",
        "locked_validation_threshold",
        "threshold_source",
    ):
        assert field in result, f"receipt provenance missing {field}"
    assert result["threshold_source"] == "immutable_development_experiment_lock"


def test_binding_is_immutable():
    with pytest.raises(Exception):
        B4B_BINDING.experiment_id = "B4_raw_compact_cnn_v1"  # type: ignore[misc]


def test_selected_architecture_binding_is_frozen_dataclass():
    assert SelectedArchitectureBinding.__dataclass_params__.frozen is True
