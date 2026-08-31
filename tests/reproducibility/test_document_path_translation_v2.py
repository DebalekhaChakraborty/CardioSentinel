"""Fail-closed tests for document path translation V2."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/provenance/document_path_translation.py"
SPEC = importlib.util.spec_from_file_location("document_path_translation", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
translation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(translation)


def test_v1_era_handbook_path_resolves_through_v1_and_v2() -> None:
    resolved = translation.resolve_current_path(
        "docs/handbook/v1/CardioSentinel_Research_Execution_Handbook_v1.5.md"
    )
    assert resolved == ROOT / (
        "docs/handbook/v1/CardioSentinel_Research_Execution_Handbook_v1.5.md"
    )


@pytest.mark.parametrize(
    "recorded,current",
    [
        (
            "handbook/CardioSentinel_Research_Execution_Handbook_v1.5.md",
            "docs/handbook/v1/CardioSentinel_Research_Execution_Handbook_v1.5.md",
        ),
        (
            "handoffs/CARDIOSENTINEL_HANDOFF_ECG24.md",
            "docs/handoffs/CARDIOSENTINEL_HANDOFF_ECG24.md",
        ),
    ],
)
def test_each_v2_root_resolves(recorded: str, current: str) -> None:
    assert translation.resolve_current_path(recorded) == ROOT / current


def test_a_retired_paper_path_fails_closed(tmp_path: Path) -> None:
    """The V1 publication workspace is retired, so its paths resolve to nothing.

    Resolution requires the file to exist. Asserting that a retired path still
    resolves would pass only on a machine where the gitignored directory happens
    to survive, and fail on a fresh clone.
    """
    # Resolved against an empty root, not this working copy: docs/paper/ is
    # gitignored rather than deleted, so a developer machine may still hold it and
    # would prove nothing either way.
    with pytest.raises(translation.UnknownDocumentPathError):
        translation.resolve_current_path(
            "paper/PAPER_S2_RELATED_WORK_DRAFT.md", repository_root=tmp_path
        )


def test_unknown_path_fails_without_basename_search() -> None:
    with pytest.raises(translation.UnknownDocumentPathError):
        translation.resolve_current_path(
            "unknown/CARDIOSENTIN_TACTICS_SUBMISSION_CANDIDATE_V1_FORMAT_PENDING.md"
        )


def test_immutable_recorded_path_is_not_rewritten_in_place() -> None:
    recorded = "docs/B4_E11_MORPHOLOGY_AWARE_REPRESENTATION_PLAN_V1.md"
    resolved = translation.resolve_current_path(recorded)
    assert recorded == "docs/B4_E11_MORPHOLOGY_AWARE_REPRESENTATION_PLAN_V1.md"
    assert resolved == ROOT / (
        "docs/experiments/b4/B4_E11_MORPHOLOGY_AWARE_REPRESENTATION_PLAN_V1.md"
    )


def test_translation_preserves_content_identity() -> None:
    receipt = ROOT / "docs/provenance/DOCUMENT_HIERARCHY_MIGRATION_V2_RECEIPT.tsv"
    with receipt.open(encoding="utf-8", newline="") as stream:
        rows = {
            row["old_path"]: row
            for row in csv.DictReader(stream, dialect="excel-tab")
        }
    # Was a paper/ document until the V1 publication workspace was retired; the
    # translation still resolves those recorded paths, but no file remains to hash,
    # so identity is demonstrated on a document the tree still carries.
    recorded = "handbook/CardioSentinel_Research_Execution_Handbook_v1.5.md"
    current = translation.resolve_current_path(recorded)
    assert hashlib.sha256(current.read_bytes()).hexdigest() == rows[recorded]["sha256"]
