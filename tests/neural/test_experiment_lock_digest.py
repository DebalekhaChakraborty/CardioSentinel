"""Machine verification of committed experiment-lock self-digests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cardiosentinel.neural.integrity import (
    experiment_lock_sha256,
    verify_experiment_lock,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
REPRESENTATIVE_LOCKS = (
    (
        "B4B_cnn_transformer_v1",
        "reproducibility/demo_bundle/runs/phase3b2-architecture-v1/"
        "B4B_cnn_transformer_v1/EXPERIMENT_LOCK.json",
        "58e44a09ce3ebffecfcd49d957acfa368fc03b534fdcd990aedb9b6b0e9bda7b",
    ),
    (
        "P1B_phys_fusion_v1",
        "reproducibility/demo_bundle/runs/phase4-p1-physiology-v1/"
        "P1B_phys_fusion_v1/EXPERIMENT_LOCK.json",
        "796f00e3ea27b1be272f843f0fb82b2c3e450311308404b78a1def22eb0676d0",
    ),
    (
        "M1L_long_memory_v2",
        "reproducibility/demo_bundle/runs/phase5-m1-dual-memory-v2/"
        "M1L_long_memory_v2/EXPERIMENT_LOCK.json",
        "a2636855e14bdd54ff3b0a17f238579d097366bb64761e723003b6d6a13c75a5",
    ),
)


def _load_lock(relative_path: str) -> dict[str, object]:
    path = REPOSITORY_ROOT / relative_path
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("experiment_id", "relative_path", "expected_digest"),
    REPRESENTATIVE_LOCKS,
)
def test_representative_committed_lock_digest_validates(
    experiment_id: str,
    relative_path: str,
    expected_digest: str,
) -> None:
    lock = _load_lock(relative_path)

    assert lock["experiment_id"] == experiment_id
    assert lock["experiment_lock_sha256"] == expected_digest
    assert experiment_lock_sha256(lock) == expected_digest
    assert verify_experiment_lock(lock) is True


@pytest.mark.parametrize(
    ("_experiment_id", "relative_path", "_expected_digest"),
    REPRESENTATIVE_LOCKS,
)
def test_non_digest_field_tampering_fails_verification(
    _experiment_id: str,
    relative_path: str,
    _expected_digest: str,
) -> None:
    lock = _load_lock(relative_path)
    lock["experiment_id"] = f"{lock['experiment_id']}-tampered"

    assert verify_experiment_lock(lock) is False


def test_digest_field_mutation_fails_verification() -> None:
    lock = _load_lock(REPRESENTATIVE_LOCKS[0][1])
    lock["experiment_lock_sha256"] = "0" * 64

    assert verify_experiment_lock(lock) is False


def test_digest_field_is_excluded_from_its_own_payload() -> None:
    lock = _load_lock(REPRESENTATIVE_LOCKS[0][1])
    original = experiment_lock_sha256(lock)

    lock["experiment_lock_sha256"] = "f" * 64

    assert experiment_lock_sha256(lock) == original
    assert verify_experiment_lock(lock) is False


def test_digest_computation_does_not_mutate_the_lock() -> None:
    lock = _load_lock(REPRESENTATIVE_LOCKS[0][1])
    original = json.loads(json.dumps(lock))

    experiment_lock_sha256(lock)

    assert lock == original


@pytest.mark.parametrize("recorded", [None, 123])
def test_missing_or_non_string_digest_fails_verification(recorded: object) -> None:
    lock = _load_lock(REPRESENTATIVE_LOCKS[0][1])
    if recorded is None:
        lock.pop("experiment_lock_sha256")
    else:
        lock["experiment_lock_sha256"] = recorded

    assert verify_experiment_lock(lock) is False
