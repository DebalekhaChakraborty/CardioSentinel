"""Repository-level invariants for the path-only document migration V2."""

from __future__ import annotations

import csv
import hashlib
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "docs/provenance/DOCUMENT_HIERARCHY_MIGRATION_V2_RECEIPT.tsv"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _receipt_rows() -> list[dict[str, str]]:
    with RECEIPT.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, dialect="excel-tab"))


def test_only_the_three_authorized_trees_moved_under_docs() -> None:
    for name in ("paper", "handbook", "handoffs"):
        assert not (ROOT / name).exists()

    # handbook/ and handoffs/ are still trees under docs/. paper/ is not: the V1
    # publication workspace was retired and gitignored, so on a fresh clone the
    # directory does not exist at all. Asserting it is a directory passed only
    # where the ignored files happened to survive on disk.
    for name in ("handbook", "handoffs"):
        assert (ROOT / "docs" / name).is_dir()
    tracked_paper = subprocess.run(
        ["git", "ls-files", "--", "docs/paper"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split()
    assert tracked_paper == []


def test_tracked_move_counts_match_the_receipt() -> None:
    tracked = subprocess.run(
        [
            "git",
            "ls-files",
            "--",
            "docs/paper",
            "docs/handbook",
            "docs/handoffs",
            "docs/control-plane/figures",
            "docs/experiments/w1/figures",
            "docs/experiments/b4/figures",
            "docs/explanation/figures",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    # docs/paper/ was the V1 publication workspace and is retired: gitignored, and
    # preserved outside this repository. A fixed count of 31 would now assert the
    # opposite of what the tree records, so what is checked is the retirement --
    # that nothing under it is tracked, and that the evidence figures it held are
    # tracked at the locations they moved to.
    assert sum(path.startswith("docs/paper/") for path in tracked) == 0
    # The handbook is split by research programme: the V1 line under v1/, the
    # journal-extension line beginning at v2/. Counting them separately says which
    # of the two moved, where a single total would not.
    assert sum(path.startswith("docs/handbook/v1/") for path in tracked) == 10
    assert sum(path.startswith("docs/handbook/v2/") for path in tracked) == 2
    assert sum(path.startswith("docs/handbook/") for path in tracked) == 12
    relocated_figures = {
        row["new_path"]
        for row in _receipt_rows()
        if "/figures/F" in row["new_path"] and row["tracked"] == "Y"
    }
    assert len(relocated_figures) == 10
    assert relocated_figures <= set(tracked)

    # Handoffs accumulate: a session written after the migration is a new file,
    # not a moved one, so a fixed total would fail for the wrong reason. What the
    # receipt actually asserts is that every file it *moved* is still tracked at
    # its new path, and that is what is checked here.
    moved_handoffs = {
        row["new_path"]
        for row in _receipt_rows()
        if row["new_path"].startswith("docs/handoffs/")
    }
    assert len(moved_handoffs) == 23
    assert moved_handoffs <= set(tracked)


def test_frozen_and_historical_moved_files_retain_content_identity() -> None:
    # A retired document keeps its recorded digest as history, but there is no file
    # left in the tree to hash: identity is verified for what the tree still holds.
    protected = [
        row
        for row in _receipt_rows()
        if row["content_frozen"] == "Y" and row["tracked"] == "Y"
    ]
    assert protected
    for row in protected:
        current = ROOT / row["new_path"]
        assert current.stat().st_size == int(row["byte_size"])
        assert _sha256(current) == row["sha256"]


def test_v1_translation_record_is_byte_identical() -> None:
    v1 = ROOT / "docs/provenance/DOCUMENT_PATH_TRANSLATION_V1.md"
    assert _sha256(v1) == (
        "fb65a3179607b3c7f5481d6a4f174800a744da605330a26aef9f3d5383d74abe"
    )


def test_seven_t1_documents_remain_flat() -> None:
    expected = {
        "T1_CANONICAL_DEVELOPMENT_EXECUTION_SPEC_V1.md",
        "T1_CAUSAL_EPISODE_STATE_PROTOCOL_V1.md",
        "T1_DESCRIPTIVE_REPORT_V1.md",
        "T1_EVIDENCE_ANALYSIS_PLAN_V1.md",
        "T1_EXECUTION_RECOVERY_AMENDMENT_V1_1.md",
        "T1_POST_HOC_ANALYSIS_V1.md",
        "t1_episode_reasoning.md",
    }
    actual = {path.name for path in (ROOT / "docs").glob("T1_*.md")}
    episode_reasoning = ROOT / "docs/t1_episode_reasoning.md"
    assert episode_reasoning.is_file()
    actual.add(episode_reasoning.name)
    assert actual == expected
    assert not (ROOT / "docs/experiments/t1").exists()


def test_all_live_local_markdown_links_resolve() -> None:
    pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    broken: list[str] = []
    for source in ROOT.rglob("*.md"):
        if {".git", "legacy", ".pytest_cache"} & set(source.parts):
            continue
        for match in pattern.finditer(source.read_text(encoding="utf-8")):
            raw = match.group(1).strip().strip("<>")
            if re.match(r"^[a-z][a-z0-9+.-]*:", raw, re.I) or raw.startswith("//"):
                continue
            target = unquote(raw.split("#", 1)[0].split("?", 1)[0])
            if not target:
                continue
            candidate = (
                ROOT / target.lstrip("/")
                if raw.startswith("/")
                else source.parent / target
            )
            if not candidate.resolve().exists():
                broken.append(f"{source.relative_to(ROOT)} -> {raw}")
    assert not broken, "\n".join(broken)
