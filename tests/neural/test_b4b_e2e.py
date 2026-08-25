"""End-to-end smoke test of the B4-B orchestrator on synthetic data.

Exercises the code that runs AFTER the point of no return -- the audit payload
assembly, the artifact writes, the receipt amend and the failure path -- with a
fake run directory. Nothing here touches the real sealed partition.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import torch

from cardiosentinel.neural import b4b_sealed_test as b4b
from cardiosentinel.neural import sealed_test
from cardiosentinel.neural.candidates import B4BTransformerCNN

from test_sealed_test import _synthetic_references, THRESHOLD, WINDOW  # noqa: E402


@pytest.fixture
def b4b_run_dir(tmp_path) -> Path:
    directory = tmp_path / "runs" / "B4B_cnn_transformer_v1"
    directory.mkdir(parents=True)
    torch.save(B4BTransformerCNN().state_dict(), directory / "model_selected.pt")
    from cardiosentinel.data.provenance import sha256_file

    checkpoint_sha = sha256_file(directory / "model_selected.pt")
    lock = {
        "experiment_id": "B4B_cnn_transformer_v1",
        "candidate_architecture": "B4BTransformerCNN",
        "status": "locked_for_one_shot_test",
        "git_sha": "0" * 40,
        "git_dirty": False,
        "split_sha256": "3" * 64,
        "locked_inference_model": "model_selected.pt",
        "checkpoint_sha256": checkpoint_sha,
        "validation_threshold": THRESHOLD,
        "threshold_selection_rule": "maximum validation F1",
        "test": None,
    }
    lock["experiment_lock_sha256"] = sealed_test.canonical_sha256(lock)
    (directory / "EXPERIMENT_LOCK.json").write_text(
        json.dumps(lock, indent=2, sort_keys=True), encoding="utf-8"
    )
    (directory / "VALIDATION_THRESHOLD.json").write_text(
        json.dumps(
            {"selected_from": "validation", "test_informed": False,
             "threshold": THRESHOLD}, indent=2, sort_keys=True
        ), encoding="utf-8"
    )
    return directory


@pytest.fixture
def harness(monkeypatch, b4b_run_dir, tmp_path):
    references = _synthetic_references()
    binding = b4b.SelectedArchitectureBinding(
        experiment_id="B4B_cnn_transformer_v1",
        architecture="B4BTransformerCNN",
        run_collection="phase3b2-architecture-v1",
        checkpoint_name="model_selected.pt",
        checkpoint_sha256=json.loads(
            (b4b_run_dir / "EXPERIMENT_LOCK.json").read_text()
        )["checkpoint_sha256"],
        experiment_lock_sha256=json.loads(
            (b4b_run_dir / "EXPERIMENT_LOCK.json").read_text()
        )["experiment_lock_sha256"],
        model_factory=B4BTransformerCNN,
    )
    monkeypatch.setattr(
        b4b, "verify_selection_identity",
        lambda root, bind=binding, **kw: {"identity_verified": True,
                                          "authorized_experiment_id": bind.experiment_id}
    )
    monkeypatch.setattr(
        b4b, "git_provenance",
        lambda root: {"git_sha": "a" * 40, "git_dirty": False})
    monkeypatch.setattr(b4b, "resolve_selected_run_dir",
                        lambda root, bind=None: b4b_run_dir)
    monkeypatch.setattr(b4b, "load_sealed_test_references",
                        lambda access, root: references)
    monkeypatch.setattr(
        b4b, "verify_primary_population",
        lambda refs: {"positive": 4, "negative": 4, "total": 8, "subjects": 2})
    monkeypatch.setattr(
        b4b, "validate_sealed_test_feature_integrity",
        lambda access, root: {
            "sealed_test_feature_integrity_sha256": "f" * 64,
            "verified_test_record_count": 3, "verified_test_cache_count": 3,
            "records": [{"record_id": "t1", "partition": "test"}]})
    monkeypatch.setattr(
        b4b, "validate_sealed_test_source_integrity",
        lambda access, source, receipt: {
            "sealed_test_source_integrity_sha256": "e" * 64,
            "verified_test_record_count": 3, "verified_test_source_file_count": 9})
    gen = np.random.default_rng(3)
    return {
        "source": tmp_path / "source", "feature_root": tmp_path / "features",
        "run_root": tmp_path / "runs", "run_dir": b4b_run_dir, "binding": binding,
        "reader": lambda s, r: gen.standard_normal(WINDOW).astype(np.float32),
    }


def test_full_orchestration_completes_and_writes_every_artifact(harness):
    result = b4b.evaluate_selected_locked_test(
        harness["source"], harness["feature_root"], harness["run_root"],
        harness["binding"], requested_device="cpu", _reader=harness["reader"])
    assert result["attempt_status"] == "COMPLETE"
    assert result["experiment_id"] == "B4B_cnn_transformer_v1"
    assert result["architecture"] == "B4BTransformerCNN"
    assert result["repeat_attempt_permitted"] is False
    d = harness["run_dir"]
    for name in ("TEST_ATTEMPT.json", "TEST_METRICS.json",
                 "TEST_PREDICTIONS.npz", "TEST_AUDIT.json"):
        assert (d / name).is_file(), f"{name} was not written"
    audit = json.loads((d / "TEST_AUDIT.json").read_text())
    for field in ("experiment_id", "architecture", "selection_identity",
                  "model_weights_unchanged", "optimizer_constructed",
                  "backward_invoked", "threshold_selection_performed",
                  "test_audit_sha256", "scored_row_count"):
        assert field in audit, f"audit payload missing {field}"
    assert audit["optimizer_constructed"] is False
    assert audit["backward_invoked"] is False
    assert audit["threshold_selection_performed"] is False
    assert audit["model_weights_unchanged"] is True


def test_second_attempt_is_refused(harness):
    b4b.evaluate_selected_locked_test(
        harness["source"], harness["feature_root"], harness["run_root"],
        harness["binding"], requested_device="cpu", _reader=harness["reader"])
    with pytest.raises(Exception):
        b4b.evaluate_selected_locked_test(
            harness["source"], harness["feature_root"], harness["run_root"],
            harness["binding"], requested_device="cpu", _reader=harness["reader"])


def test_failure_path_records_and_reraises(harness, monkeypatch):
    monkeypatch.setattr(b4b, "score_sealed_test",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(RuntimeError, match="boom"):
        b4b.evaluate_selected_locked_test(
            harness["source"], harness["feature_root"], harness["run_root"],
            harness["binding"], requested_device="cpu", _reader=harness["reader"])
    receipt = json.loads((harness["run_dir"] / "TEST_ATTEMPT.json").read_text())
    assert receipt["attempt_status"] == "FAILED_OR_INTERRUPTED"
    assert receipt["human_review_required"] is True
    assert receipt["repeat_attempt_permitted"] is False
    assert receipt["error_type"] == "RuntimeError"
