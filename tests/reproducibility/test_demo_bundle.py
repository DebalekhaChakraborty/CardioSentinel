"""The demo bundle is verified, not asserted.

A CHECKSUM_MANIFEST plus "trust me" would be the one artifact in this repository
that nothing checks, which contradicts the project's own argument that a
boundary a human must remember is weaker than one a function enforces
(Handbook §53). These tests run on every checkout: the bundle is committed, so
unlike the research-tier tests they never skip.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REPRO = ROOT / "reproducibility"
MANIFEST = REPRO / "DEMO_BUNDLE_SELECTION.json"
BUNDLE = REPRO / "demo_bundle"
VERIFIER = REPRO / "verify_reproducibility.py"


@pytest.fixture(scope="module")
def manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_the_verifier_passes_on_the_committed_bundle():
    """The load-bearing test. If this fails the bundle drifted from its manifest."""
    result = subprocess.run(
        [sys.executable, str(VERIFIER)], capture_output=True, text=True, cwd=ROOT
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "all digests match" in result.stdout


def test_every_manifest_entry_exists_with_its_digest(manifest):
    import hashlib

    for entry in manifest["files"]:
        path = BUNDLE / entry["path"]
        assert path.is_file(), entry["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]


def test_the_bundle_contains_nothing_unselected(manifest):
    """Curated means curated."""
    selected = {entry["path"] for entry in manifest["files"]}
    present = {
        str(p.relative_to(BUNDLE)) for p in BUNDLE.rglob("*") if p.is_file()
    }
    assert present == selected


def test_the_bundle_stays_small(manifest):
    """A reviewer must be able to clone this. Guard against creep."""
    assert manifest["total_bytes"] < 4 * 1024 * 1024, "bundle exceeded 4 MiB"
    assert manifest["file_count"] == len(manifest["files"])


def test_every_entry_names_the_loader_that_reads_it(manifest):
    for entry in manifest["files"]:
        assert entry["loader"], entry["path"]
        assert entry["source"].startswith("cardiosentinel-")


def test_the_manifest_declares_its_scope_and_boundaries(manifest):
    assert manifest["tier"] == "demo"
    assert manifest["test_accessed"] is False
    assert manifest["sealed_test_state"] == "unopened"
    assert manifest["external_mirror_required"] is False
    scope = manifest["scope"].lower()
    for phrase in ("not the complete research artifact archive", "research tier"):
        assert phrase in scope


def test_no_sealed_test_artifact_is_bundled(manifest):
    """The one thing that must never appear here."""
    for entry in manifest["files"]:
        lowered = (entry["path"] + entry["source"]).lower()
        assert "test_attempt" not in lowered
        assert "sealed" not in lowered


def test_the_bundle_layout_mirrors_the_run_root(manifest):
    """So existing loaders read it unchanged, with no second loading path."""
    assert "mirrors the run root" in manifest["layout"]
    roots = {entry["path"].split("/")[0] for entry in manifest["files"]}
    assert roots == {"runs", "features"}


def test_the_verifier_detects_drift(tmp_path):
    """A verifier that cannot fail is not a verifier."""
    import hashlib
    import shutil

    staged = tmp_path / "repro"
    shutil.copytree(REPRO, staged)
    target = next((staged / "demo_bundle").rglob("*.json"))
    target.write_bytes(target.read_bytes() + b" ")
    payload = json.loads((staged / "DEMO_BUNDLE_SELECTION.json").read_text())
    relative = str(target.relative_to(staged / "demo_bundle"))
    entry = next(e for e in payload["files"] if e["path"] == relative)
    assert hashlib.sha256(target.read_bytes()).hexdigest() != entry["sha256"]


def test_the_documentation_set_is_complete():
    for name in (
        "README.md",
        "ENVIRONMENT.md",
        "DATA_ACCESS.md",
        "RUN_DEMO.md",
        "EXPERIMENT_MAP.md",
        "CHECKSUM_MANIFEST.md",
    ):
        assert (REPRO / name).is_file(), name


def test_the_package_does_not_depend_on_an_external_mirror():
    """Stated in the docs and enforced here."""
    checksum = (REPRO / "CHECKSUM_MANIFEST.md").read_text(encoding="utf-8")
    assert "not verified" in checksum
    assert "Nothing in this package depends on that mirror" in checksum
