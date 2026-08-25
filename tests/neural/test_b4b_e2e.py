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
from test_sealed_test import THRESHOLD, WINDOW, _synthetic_references  # noqa: E402

from cardiosentinel.neural import b4b_sealed_test as b4b
from cardiosentinel.neural import sealed_test
from cardiosentinel.neural.candidates import B4BTransformerCNN


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
        lambda root, bind=binding, **kw: {
            "identity_verified": True,
            "authorized_experiment_id": bind.experiment_id,
        },
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


# --------------------------------------------------------------------------
# 1. audit schema pre-flight fails before the attempt is claimed
# --------------------------------------------------------------------------


def test_malformed_lock_fails_before_attempt_claim(harness, monkeypatch, tmp_path):
    """A lock missing an audit reference is refused with no receipt written."""
    lock_path = harness["run_dir"] / "EXPERIMENT_LOCK.json"
    lock = json.loads(lock_path.read_text())
    lock.pop("split_sha256")
    lock["experiment_lock_sha256"] = sealed_test.canonical_sha256(
        {k: v for k, v in lock.items() if k != "experiment_lock_sha256"}
    )
    lock_path.write_text(json.dumps(lock, indent=2, sort_keys=True), encoding="utf-8")
    monkeypatch.setattr(b4b, "validate_experiment_lock", lambda run_dir: lock)

    with pytest.raises(b4b.AuditSchemaError, match="missing audit references"):
        b4b.evaluate_selected_locked_test(
            harness["source"], harness["feature_root"], harness["run_root"],
            harness["binding"], requested_device="cpu", _reader=harness["reader"])
    assert not (harness["run_dir"] / "TEST_ATTEMPT.json").exists()
    assert not (harness["run_dir"] / "TEST_METRICS.json").exists()


def test_wrong_architecture_in_audit_identity_fails_before_claim(harness):
    from dataclasses import replace as _replace

    binding = _replace(harness["binding"], architecture="B4CompactCNN")
    with pytest.raises((b4b.AuditSchemaError, b4b.SelectionIdentityError)):
        b4b.evaluate_selected_locked_test(
            harness["source"], harness["feature_root"], harness["run_root"],
            binding, requested_device="cpu", _reader=harness["reader"])
    assert not (harness["run_dir"] / "TEST_ATTEMPT.json").exists()


def test_malformed_checkpoint_digest_fails_before_claim(harness):
    from dataclasses import replace as _replace

    binding = _replace(harness["binding"], checkpoint_sha256="not-a-digest")
    with pytest.raises(b4b.AuditSchemaError, match="not a SHA-256 digest"):
        b4b.evaluate_selected_locked_test(
            harness["source"], harness["feature_root"], harness["run_root"],
            binding, requested_device="cpu", _reader=harness["reader"])
    assert not (harness["run_dir"] / "TEST_ATTEMPT.json").exists()


def test_incomplete_audit_payload_is_refused_before_writing():
    with pytest.raises(b4b.AuditSchemaError, match="missing fields"):
        b4b.validate_audit_payload({"experiment_id": "B4B_cnn_transformer_v1"})


def test_audit_payload_naming_the_rejected_experiment_is_refused():
    payload = {field: None for field in b4b.REQUIRED_AUDIT_FIELDS}
    payload["experiment_id"] = "B4_raw_compact_cnn_v1"
    payload["architecture"] = "B4BTransformerCNN"
    with pytest.raises(b4b.AuditSchemaError, match="wrong experiment"):
        b4b.validate_audit_payload(payload)


def test_preflight_runs_before_the_claim_in_source_order():
    import inspect

    body = inspect.getsource(b4b.open_selected_sealed_test_attempt)
    assert body.index("preflight_audit_schema(") < body.index(
        "claim_attempt_exclusively("
    )


# --------------------------------------------------------------------------
# 2. failure recording must never replace the failure
# --------------------------------------------------------------------------


def test_failure_recording_failure_preserves_original_exception(
    harness, monkeypatch
):
    """If _update_attempt itself fails, the ORIGINAL error still surfaces."""
    monkeypatch.setattr(
        b4b, "score_sealed_test",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("original failure")))

    calls = {"n": 0}

    def exploding_update(access, **fields):
        calls["n"] += 1
        if fields.get("attempt_status") == "FAILED_OR_INTERRUPTED":
            raise KeyError("recording blew up")
        return {}

    monkeypatch.setattr(b4b, "_update_attempt", exploding_update)

    with pytest.raises(RuntimeError, match="original failure") as excinfo:
        b4b.evaluate_selected_locked_test(
            harness["source"], harness["feature_root"], harness["run_root"],
            harness["binding"], requested_device="cpu", _reader=harness["reader"])

    notes = getattr(excinfo.value, "__notes__", [])
    assert any("Failure recording ALSO failed" in n for n in notes), notes
    assert any("KeyError" in n for n in notes), notes
    assert any("requires\nhuman review" in n or "human review" in n for n in notes)


def test_failure_recording_failure_is_not_limited_to_oserror(harness, monkeypatch):
    """A non-OSError recording fault must not propagate in place of the original."""
    monkeypatch.setattr(
        b4b, "score_sealed_test",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("scoring died")))
    monkeypatch.setattr(
        b4b, "_update_attempt",
        lambda access, **f: (_ for _ in ()).throw(TypeError("not an OSError"))
        if f.get("attempt_status") == "FAILED_OR_INTERRUPTED" else {})

    with pytest.raises(ValueError, match="scoring died"):
        b4b.evaluate_selected_locked_test(
            harness["source"], harness["feature_root"], harness["run_root"],
            harness["binding"], requested_device="cpu", _reader=harness["reader"])
