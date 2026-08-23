"""Frozen artifact resolution for the edge runtime.

Nothing here trains, fits, selects or re-derives anything. Every object this
module returns was produced by a completed experiment, is bound by an immutable
lock, and is loaded through the same digest-checked path the research code
already uses -- `p1_experiment.load_official_b4b_encoder` and
`m1_experiment.load_frozen_physiology_transform`, not a private reimplementation.

That reuse is the point. If the edge runtime loaded weights by a second route,
"the demo runs the validated pipeline" would be an assertion rather than a
consequence.

**This module never touches TEST.** It resolves development-partition artifacts
only, and the sealed neural test remains unopened.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..neural.m1_experiment import load_frozen_physiology_transform
from ..neural.p1_experiment import load_official_b4b_encoder
from ..neural.physiology_fusion import (
    EMBEDDING_DIM,
    PHYSIOLOGY_DIM,
    PhysiologyTransform,
)

#: The canonical run directories, relative to a run root. These are the runs the
#: retention decisions named; they are not configurable by accident.
B4B_RUN = ("phase3b2-architecture-v1", "B4B_cnn_transformer_v1")
P1B_RUN = ("phase4-p1-physiology-v1", "P1B_phys_fusion_v1")

DEFAULT_RUN_ROOT = Path("cardiosentinel-runs")
DEFAULT_SOURCE_ROOT = Path("cardiosentinel-data/ltstdb/1.0.0")


class EdgeArtifactError(RuntimeError):
    """A frozen artifact could not be resolved, or is not the retained one."""


@dataclass(frozen=True)
class FrozenArtifacts:
    """The retained inference components, loaded and proven.

    `encoder` is the selected B4-B encoder with `requires_grad_(False)` and
    `eval()` already applied by its loader. `physiology` is the train-fitted
    transform whose digest was checked against the P1-B lock before it was
    allowed to touch a representation.
    """

    encoder: Any
    physiology: PhysiologyTransform
    b4b_run_dir: Path
    p1b_run_dir: Path

    @property
    def embedding_dim(self) -> int:
        return EMBEDDING_DIM

    @property
    def physiology_dim(self) -> int:
        return PHYSIOLOGY_DIM

    def provenance(self) -> dict[str, Any]:
        """The digests a decision made with these artifacts should carry.

        Runtime governance, not experiment governance: an alert that cannot name
        the weights that produced it is not auditable, however good the
        experiment record behind it is.
        """
        transform = self.physiology.as_dict()
        return {
            "encoder_architecture": type(self.encoder).__name__,
            "encoder_run_dir": str(self.b4b_run_dir),
            "embedding_tap": "B4BTransformerCNN.encode:pooled_post_final_norm",
            "embedding_dim": EMBEDDING_DIM,
            "physiology_run_dir": str(self.p1b_run_dir),
            "physiology_transform_sha256": transform["transform_sha256"],
            "physiology_schema_sha256": transform["schema_sha256"],
            "physiology_dim": PHYSIOLOGY_DIM,
            "physiology_fitted_on_partition": transform["fitted_on_partition"],
            "encoder_fine_tuned": False,
            "test_accessed": False,
            "sealed_test_state": "unopened",
        }


def resolve_run_dir(run_root: Path, parts: tuple[str, str]) -> Path:
    directory = Path(run_root).joinpath(*parts)
    if not directory.is_dir():
        raise EdgeArtifactError(
            f"Frozen run directory {directory} does not exist. The edge runtime "
            "loads retained artifacts; it never creates them."
        )
    return directory


def load_frozen_artifacts(run_root: Path | str = DEFAULT_RUN_ROOT) -> FrozenArtifacts:
    """Load the retained encoder and physiology transform, digests checked.

    Both loaders raise if the artifact is not the selected one, so a wrong or
    tampered checkpoint fails here rather than producing a plausible number
    downstream.
    """
    root = Path(run_root)
    b4b = resolve_run_dir(root, B4B_RUN)
    p1b = resolve_run_dir(root, P1B_RUN)
    return FrozenArtifacts(
        encoder=load_official_b4b_encoder(b4b),
        physiology=load_frozen_physiology_transform(p1b),
        b4b_run_dir=b4b,
        p1b_run_dir=p1b,
    )
