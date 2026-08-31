"""The edge runtime fails closed at every trust boundary."""

from __future__ import annotations

import json
import shutil
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _metadata(replay, *, samples=30_000, channels=1):
    return replay.ReplayRecordMetadata(
        sample_count=samples,
        channel_count=channels,
        sampling_frequency_hz=250.0,
    )


class _PassthroughWindows:
    def __init__(self, *_args):
        pass

    def process(self, segment):
        return (segment,)


def test_replay_propagates_an_unexpected_read_failure_as_typed_error(monkeypatch):
    from cardiosentinel.edge import replay

    monkeypatch.setattr(
        replay, "_read_local_record_metadata", lambda *_args: _metadata(replay)
    )

    def corrupt(*_args, **_kwargs):
        raise PermissionError("synthetic unreadable record")

    monkeypatch.setattr(replay, "read_local_segment", corrupt)
    with pytest.raises(replay.ReplayReadError) as captured:
        list(replay.stream_windows("s20201", channel_index=0, max_seconds=60.0))
    message = str(captured.value)
    assert "s20201" in message
    assert "channel 0" in message
    assert "[0, 15000)" in message
    assert isinstance(captured.value.__cause__, PermissionError)


def test_exact_eof_never_probes_past_the_record(monkeypatch):
    from cardiosentinel.edge import replay

    calls = []
    monkeypatch.setattr(
        replay, "_read_local_record_metadata", lambda *_args: _metadata(replay)
    )
    monkeypatch.setattr(replay, "CausalWindowGenerator", _PassthroughWindows)

    def read(_root, _dataset, _record, start, end, channels):
        calls.append((start, end, channels))
        return SimpleNamespace(start_sample=start, end_sample=end)

    monkeypatch.setattr(replay, "read_local_segment", read)
    emitted = list(replay.stream_windows("s20201", chunk_seconds=60.0))
    assert calls == [(0, 15_000, (0,)), (15_000, 30_000, (0,))]
    assert len(emitted) == 2


def test_partial_final_region_is_read_without_padding(monkeypatch):
    from cardiosentinel.edge import replay

    calls = []
    monkeypatch.setattr(
        replay,
        "_read_local_record_metadata",
        lambda *_args: _metadata(replay, samples=20_000),
    )
    monkeypatch.setattr(replay, "CausalWindowGenerator", _PassthroughWindows)

    def read(_root, _dataset, _record, start, end, _channels):
        calls.append((start, end))
        return SimpleNamespace(start_sample=start, end_sample=end)

    monkeypatch.setattr(replay, "read_local_segment", read)
    list(replay.stream_windows("s20201", chunk_seconds=60.0))
    assert calls == [(0, 15_000), (15_000, 20_000)]


@pytest.mark.parametrize("chunk_seconds", [0.0, -1.0, 0.001])
def test_non_progressing_or_non_sample_aligned_chunks_are_refused(chunk_seconds):
    from cardiosentinel.edge import replay

    with pytest.raises(replay.ReplayConfigurationError, match="chunk_seconds"):
        list(replay.stream_windows("s20201", chunk_seconds=chunk_seconds))


def test_invalid_channel_is_refused_before_any_waveform_read(monkeypatch):
    from cardiosentinel.edge import replay

    monkeypatch.setattr(
        replay,
        "_read_local_record_metadata",
        lambda *_args: _metadata(replay, channels=1),
    )
    monkeypatch.setattr(
        replay,
        "read_local_segment",
        lambda *_args, **_kwargs: pytest.fail("invalid channel reached the reader"),
    )
    with pytest.raises(replay.ReplayConfigurationError, match="channel"):
        list(replay.stream_windows("s20201", channel_index=1))


@pytest.fixture
def staged_reproducibility(tmp_path):
    staged = tmp_path / "reproducibility"
    shutil.copytree(ROOT / "reproducibility" / "demo_bundle", staged / "demo_bundle")
    shutil.copy2(
        ROOT / "reproducibility" / "DEMO_BUNDLE_SELECTION.json",
        staged / "DEMO_BUNDLE_SELECTION.json",
    )
    return staged


def _mutate_runtime_artifact(staged: Path, artifact: str) -> None:
    bundle = staged / "demo_bundle"
    if artifact == "standardizer":
        target = bundle / "features/m1-stream-memory-v2/M1_DISTANCE_STANDARDIZER.json"
        payload = json.loads(target.read_text(encoding="utf-8"))
        payload["means"][0] += 0.125
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    elif artifact == "u1":
        target = bundle / (
            "runs/phase7-u1-development-v1/u1-v1-development/"
            "U1_DEPLOYMENT_CALIBRATOR.json"
        )
        payload = json.loads(target.read_text(encoding="utf-8"))
        payload["calibrator"]["a"] += 0.125
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    elif artifact == "t2":
        import torch

        target = bundle / (
            "runs/phase8-t2-development-v1/t2-v1-training/"
            "T2_S4D_BEST_CHECKPOINT.pt"
        )
        payload = torch.load(target, map_location="cpu", weights_only=True)
        state = payload["model"] if "model" in payload else payload
        first = next(iter(state))
        state[first] = state[first].clone()
        state[first].view(-1)[0] += 0.125
        torch.save(payload, target)
    else:
        selections = bundle / (
            "runs/phase9-t1-development-v1/t1-v1-development/fold_selections"
        )
        target = next(
            path
            for path in selections.glob("*.json")
            if json.loads(path.read_text())["held_out_subject"] == "ltstdb:s2020"
        )
        payload = json.loads(target.read_text(encoding="utf-8"))
        payload["q_watch"] += 0.001
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _rewrite_manifest_entry(staged: Path, relative: str, digest: str | None) -> None:
    manifest = staged / "DEMO_BUNDLE_SELECTION.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    entries = [entry for entry in payload["files"] if entry["path"] != relative]
    if digest is not None:
        entries.append({"path": relative, "sha256": digest})
    payload["files"] = entries
    payload["file_count"] = len(entries)
    manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")


@pytest.mark.parametrize("artifact", ["standardizer", "u1", "t2", "t1"])
def test_runtime_refuses_every_mutated_direct_artifact(
    staged_reproducibility, artifact
):
    from cardiosentinel.edge.artifacts import EdgeArtifactError, load_runtime_artifacts

    _mutate_runtime_artifact(staged_reproducibility, artifact)
    with pytest.raises(EdgeArtifactError, match="digest"):
        load_runtime_artifacts(
            "ltstdb:s2020",
            run_root=staged_reproducibility / "demo_bundle" / "runs",
            feature_root=staged_reproducibility / "demo_bundle" / "features",
        )


def test_runtime_refuses_a_required_artifact_without_an_expected_digest(
    staged_reproducibility,
):
    from cardiosentinel.edge.artifacts import EdgeArtifactError, load_runtime_artifacts

    relative = (
        "runs/phase7-u1-development-v1/u1-v1-development/"
        "U1_DEPLOYMENT_CALIBRATOR.json"
    )
    _rewrite_manifest_entry(staged_reproducibility, relative, None)
    with pytest.raises(EdgeArtifactError, match="no expected digest"):
        load_runtime_artifacts(
            "ltstdb:s2020",
            run_root=staged_reproducibility / "demo_bundle" / "runs",
            feature_root=staged_reproducibility / "demo_bundle" / "features",
        )


def test_runtime_refuses_a_missing_required_artifact(staged_reproducibility):
    from cardiosentinel.edge.artifacts import EdgeArtifactError, load_runtime_artifacts

    artifact = staged_reproducibility / "demo_bundle" / (
        "runs/phase8-t2-development-v1/t2-v1-training/"
        "T2_S4D_BEST_CHECKPOINT.pt"
    )
    artifact.unlink()
    with pytest.raises(EdgeArtifactError, match="missing"):
        load_runtime_artifacts(
            "ltstdb:s2020",
            run_root=staged_reproducibility / "demo_bundle" / "runs",
            feature_root=staged_reproducibility / "demo_bundle" / "features",
        )


def test_runtime_refuses_a_digest_consistent_but_wrong_frozen_identity(
    staged_reproducibility,
):
    from cardiosentinel.edge.artifacts import EdgeArtifactError, load_runtime_artifacts

    relative = (
        "runs/phase7-u1-development-v1/u1-v1-development/"
        "U1_DEPLOYMENT_CALIBRATOR.json"
    )
    artifact = staged_reproducibility / "demo_bundle" / relative
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    payload["calibrator"]["a"] += 0.125
    artifact.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _rewrite_manifest_entry(
        staged_reproducibility, relative, sha256(artifact.read_bytes()).hexdigest()
    )
    with pytest.raises(EdgeArtifactError, match="deployment identity"):
        load_runtime_artifacts(
            "ltstdb:s2020",
            run_root=staged_reproducibility / "demo_bundle" / "runs",
            feature_root=staged_reproducibility / "demo_bundle" / "features",
        )


def test_runtime_provenance_names_every_verified_direct_artifact():
    from cardiosentinel.edge.artifacts import load_runtime_artifacts

    artifacts = load_runtime_artifacts(
        "ltstdb:s2020",
        run_root=ROOT / "reproducibility" / "demo_bundle" / "runs",
        feature_root=ROOT / "reproducibility" / "demo_bundle" / "features",
    )
    records = artifacts.provenance()["runtime_artifacts"]
    assert {record["component"] for record in records} >= {
        "encoder",
        "physiology",
        "memory",
        "standardizer",
        "calibration",
        "temporal",
        "episode",
    }
    assert all(record["verification_status"] == "verified" for record in records)
    assert all(
        record["expected_sha256"] == record["observed_sha256"]
        for record in records
    )
