"""Phase 0: choose the demo bundle's contents, before anything is copied.

This programme has spent months proving it does not accidentally use the wrong
artifact. A reproducibility bundle assembled by hand would be the one place that
discipline lapsed, so the selection is **generated from the loaders' own
constants** and written out as a manifest first. `verify_reproducibility.py`
then checks the bundle against that manifest, and CI checks it again.

**Layout mirrors the run root on purpose.** The bundle is not restructured into
`models/`, `locks/`, `transforms/` — a flatter tree would read better and would
require a second way to load weights, which is exactly what #82 refused to
create. Mirroring means `--run-root reproducibility/demo_bundle/runs` is loaded
by the same `load_runtime_artifacts` the research path uses, with no new code
and nothing to drift.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[2]

#: Every file the edge runtime opens, with the loader that opens it. Derived by
#: reading `edge/artifacts.py`, not guessed.
SELECTION: tuple[tuple[str, str, str], ...] = (
    (
        "runs/phase3b2-architecture-v1/B4B_cnn_transformer_v1/model_selected.pt",
        "cardiosentinel-runs/phase3b2-architecture-v1/B4B_cnn_transformer_v1"
        "/model_selected.pt",
        "resource_benchmark.load_locked_model"
        " via p1_experiment.load_official_b4b_encoder",
    ),
    (
        "runs/phase3b2-architecture-v1/B4B_cnn_transformer_v1/EXPERIMENT_LOCK.json",
        "cardiosentinel-runs/phase3b2-architecture-v1/B4B_cnn_transformer_v1"
        "/EXPERIMENT_LOCK.json",
        "p1_experiment.load_official_b4b_encoder (lock + checkpoint digest check)",
    ),
    (
        "runs/phase4-p1-physiology-v1/P1B_phys_fusion_v1/EXPERIMENT_LOCK.json",
        "cardiosentinel-runs/phase4-p1-physiology-v1/P1B_phys_fusion_v1/EXPERIMENT_LOCK.json",
        "m1_experiment.load_frozen_physiology_transform (digest binding)",
    ),
    (
        "runs/phase4-p1-physiology-v1/P1B_phys_fusion_v1/PHYSIOLOGY_TRANSFORM.json",
        "cardiosentinel-runs/phase4-p1-physiology-v1/P1B_phys_fusion_v1/PHYSIOLOGY_TRANSFORM.json",
        "m1_experiment.load_frozen_physiology_transform",
    ),
    (
        "runs/phase7-u1-development-v1/u1-v1-development/U1_DEPLOYMENT_CALIBRATOR.json",
        "cardiosentinel-runs/phase7-u1-development-v1/u1-v1-development/U1_DEPLOYMENT_CALIBRATOR.json",
        "edge.artifacts.load_runtime_artifacts (U1Calibrator)",
    ),
    (
        "runs/phase8-t2-development-v1/t2-v1-training/T2_S4D_BEST_CHECKPOINT.pt",
        "cardiosentinel-runs/phase8-t2-development-v1/t2-v1-training/T2_S4D_BEST_CHECKPOINT.pt",
        "t2_training.restore_model_state",
    ),
    (
        "features/m1-stream-memory-v2/M1_DISTANCE_STANDARDIZER.json",
        "cardiosentinel-features/m1-stream-memory-v2/M1_DISTANCE_STANDARDIZER.json",
        "edge.artifacts.load_runtime_artifacts (M1DistanceStandardizer)",
    ),
)

#: Directories copied whole because their loader reads several files from them.
SELECTION_TREES: tuple[tuple[str, str, str], ...] = (
    (
        "runs/phase5-m1-dual-memory-v2/M1L_long_memory_v2",
        "cardiosentinel-runs/phase5-m1-dual-memory-v2/M1L_long_memory_v2",
        "m2_scorer.load_frozen_m1l_scorer",
    ),
    (
        "runs/phase9-t1-development-v1/t1-v1-development/fold_selections",
        "cardiosentinel-runs/phase9-t1-development-v1/t1-v1-development/fold_selections",
        "edge.artifacts.resolve_t1_policy (leave-one-subject-out thresholds)",
    ),
)

SCOPE = (
    "This bundle exists only to reproduce the CardioSentinel IPS demonstration. "
    "It is NOT the complete research artifact archive, is NOT sufficient to "
    "reproduce all experiments, and does NOT replace the locked experiment "
    "stores. Full scientific validation requires the research tier."
)


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(root: pathlib.Path) -> dict:
    entries = []
    for relative, source, loader in SELECTION:
        path = root / source
        if not path.is_file():
            raise SystemExit(f"missing source artifact: {source}")
        entries.append(
            {
                "path": relative,
                "source": source,
                "sha256": digest(path),
                "bytes": path.stat().st_size,
                "loader": loader,
            }
        )
    for relative, source, loader in SELECTION_TREES:
        directory = root / source
        if not directory.is_dir():
            raise SystemExit(f"missing source tree: {source}")
        for path in sorted(p for p in directory.rglob("*") if p.is_file()):
            entries.append(
                {
                    "path": f"{relative}/{path.relative_to(directory)}",
                    "source": f"{source}/{path.relative_to(directory)}",
                    "sha256": digest(path),
                    "bytes": path.stat().st_size,
                    "loader": loader,
                }
            )
    return {
        "artifact_class": "cardiosentinel_demo_bundle_selection",
        "purpose": "IPS demo reproduction",
        "scope": SCOPE,
        "tier": "demo",
        "layout": "mirrors the run root so existing loaders read it unchanged",
        "test_accessed": False,
        "sealed_test_state": "unopened",
        "external_mirror_required": False,
        "file_count": len(entries),
        "total_bytes": sum(entry["bytes"] for entry in entries),
        "files": entries,
    }


def main(argv: list[str]) -> int:
    root = REPOSITORY_ROOT
    payload = build(root)
    default = root / "reproducibility" / "DEMO_BUNDLE_SELECTION.json"
    destination = pathlib.Path(argv[1] if len(argv) > 1 else default)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"selected {payload['file_count']} files, "
        f"{payload['total_bytes'] / 1_048_576:.2f} MiB -> {destination}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
