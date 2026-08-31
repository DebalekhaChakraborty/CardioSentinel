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
        "EXPERIMENT_MAP.md",
        "CHECKSUM_MANIFEST.md",
    ):
        assert (REPRO / name).is_file(), name

    # The environment, data-access and run-the-demo documents were merged into
    # README.md; what they guaranteed is a section of it now, so assert on the
    # content rather than only on the filenames that used to carry it.
    readme = (REPRO / "README.md").read_text(encoding="utf-8")
    for heading in (
        "## Run the demonstration",
        "## Environment",
        "## Data access",
    ):
        assert heading in readme, heading


def test_the_package_does_not_depend_on_an_external_mirror():
    """Stated in the docs and enforced here."""
    checksum = (REPRO / "CHECKSUM_MANIFEST.md").read_text(encoding="utf-8")
    assert "not verified" in checksum
    assert "Nothing in this package depends on that mirror" in checksum


# --------------------------------------------------------------------------
# Usability. Integrity proves the bundle is intact; these prove it WORKS.
# --------------------------------------------------------------------------


BUNDLE_RUNS = BUNDLE / "runs"
BUNDLE_FEATURES = BUNDLE / "features"


def test_the_bundle_alone_loads_every_runtime_component():
    """The claim `README.md` makes under Run the demonstration, executed.

    **This runs everywhere**, including a fresh CI checkout, because the bundle
    is committed and no ECG record is needed to load artifacts. It is the test
    that would have failed when `.gitignore` silently dropped three
    checkpoints — integrity checks passed at that point, because the manifest
    and the missing files agreed with each other.
    """
    from cardiosentinel.edge.artifacts import load_runtime_artifacts

    artifacts = load_runtime_artifacts(
        "ltstdb:s2020", run_root=BUNDLE_RUNS, feature_root=BUNDLE_FEATURES
    )
    provenance = artifacts.provenance()

    assert provenance["encoder_architecture"] == "B4BTransformerCNN"
    assert provenance["m2_arm"] == "M2-G"
    assert provenance["u1_family"] == "platt_logistic_on_recovered_logit"
    assert provenance["t2_arm"] == "CausalS4DLongitudinal"
    assert provenance["t1_policy_id"] == "qw0.9_qe0.99_FAST"
    assert provenance["t1_held_out_subject"] == "ltstdb:s2020"
    assert provenance["sealed_test_state"] == "unopened"
    assert provenance["test_accessed"] is False
    # The digest a reviewer can compare against the merged corpus manifest.
    assert provenance["physiology_transform_sha256"].startswith("cc6bd3a3")


def test_the_bundle_refuses_an_unvalidated_subject():
    """The boundary travels with the bundle, not just with the research tree."""
    from cardiosentinel.edge.artifacts import EdgeArtifactError, load_runtime_artifacts

    with pytest.raises(EdgeArtifactError, match="not one of the twelve"):
        load_runtime_artifacts(
            "ltstdb:s2001", run_root=BUNDLE_RUNS, feature_root=BUNDLE_FEATURES
        )


DEMO_RECORD = ROOT / "cardiosentinel-data" / "ltstdb" / "1.0.0" / "s20201.hea"


@pytest.mark.skipif(
    not DEMO_RECORD.is_file(),
    reason=(
        "cardiosentinel-data/ltstdb/1.0.0/s20201 absent. The ECG record is "
        "downloaded from PhysioNet per README.md, Data access, and is not "
        "distributed "
        "here; the bundle-only loader test above still runs."
    ),
)
def test_the_documented_reviewer_path_runs_end_to_end():
    """ECG -> alert -> evidence -> explanation, from the bundle, as documented."""
    from cardiosentinel.agents.evidence import EvidenceAgent
    from cardiosentinel.agents.explain import DETERMINISTIC, PatientExplanationAgent
    from cardiosentinel.agents.graph import build_evidence_graph
    from cardiosentinel.edge.replay import replay_record

    result = replay_record(
        "s20201",
        max_seconds=1800.0,
        source_root=ROOT / "cardiosentinel-data" / "ltstdb" / "1.0.0",
        run_root=BUNDLE_RUNS,
        feature_root=BUNDLE_FEATURES,
    )
    assert result.observations, "no windows were produced"
    assert result.alerts, "s20201 should raise at least one alert in 30 minutes"

    evidence = EvidenceAgent(result.provenance).explain(
        result.alerts[0], result.observations, index=0
    )
    assert evidence.alert_id.startswith("EVT-s20201")
    assert len(evidence.gate) == 6

    graph = build_evidence_graph(evidence, run_root=BUNDLE_RUNS)
    lineage = [node.node_id for node in graph.lineage("measurement:p_t")]
    assert "component:calibration" in lineage

    explanation = PatientExplanationAgent(None).explain(graph)
    # No provider is configured in CI or in a reviewer's clone by default.
    assert explanation.explanation_mode == DETERMINISTIC
    assert explanation.fallback_reason == "no provider configured"
    assert "does not establish a diagnosis" in explanation.text
