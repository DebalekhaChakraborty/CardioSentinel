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

import json
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
M1_RUN = ("phase5-m1-dual-memory-v2",)
U1_RUN = ("phase7-u1-development-v1", "u1-v1-development")
T2_RUN = ("phase8-t2-development-v1", "t2-v1-training")
T1_RUN = ("phase9-t1-development-v1", "t1-v1-development")

#: The M1 distance standardizer lives beside the stream cache, not under a
#: run root, because it is a property of the frozen TRAIN population.
DEFAULT_FEATURE_ROOT = Path("cardiosentinel-features")
STANDARDIZER_PATH = ("m1-stream-memory-v2", "M1_DISTANCE_STANDARDIZER.json")

#: The retained arm and the promoted T1 policy. Named, not discovered.
RETAINED_M2_ARM = "M2-G"
PROMOTED_T1_POLICY_ID = "qw0.9_qe0.99_FAST"

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


# ---------------------------------------------------------------------------
# The full runtime artifact set
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class T1FoldPolicy:
    """One held-out subject's promoted T1 operating point.

    **These thresholds are leave-one-subject-out.** `threshold_population` is
    `fit_subject_primary_background_negative`: they were derived from the
    other eleven subjects and the held-out subject's labels were never opened
    (`held_out_labels_opened: false`). A policy is therefore valid *for its own
    held-out subject and no one else*, which is why `resolve_t1_policy` refuses
    to serve one for an unknown subject rather than borrowing the nearest.
    """

    held_out_subject: str
    fold_index: int
    policy_id: str
    persistence_profile: str
    thresholds: Any
    q_watch: float
    q_event: float
    threshold_population: str
    threshold_population_row_count: int

    def provenance(self) -> dict[str, Any]:
        return {
            "t1_held_out_subject": self.held_out_subject,
            "t1_fold_index": self.fold_index,
            "t1_policy_id": self.policy_id,
            "t1_persistence_profile": self.persistence_profile,
            "t1_p_watch": self.thresholds.p_watch,
            "t1_s_watch": self.thresholds.s_watch,
            "t1_p_event": self.thresholds.p_event,
            "t1_s_event": self.thresholds.s_event,
            "t1_q_watch": self.q_watch,
            "t1_q_event": self.q_event,
            "t1_threshold_population": self.threshold_population,
            "t1_threshold_population_row_count": self.threshold_population_row_count,
            "t1_thresholds_generated_here": False,
            "t1_held_out_labels_opened": False,
        }


def resolve_t1_policy(
    subject_id: str, run_root: Path | str = DEFAULT_RUN_ROOT
) -> T1FoldPolicy:
    """The promoted policy for one held-out subject, or a refusal.

    Refusing is the point. A record outside the twelve validation subjects has
    **no validated operating point**, and serving it another subject's
    thresholds would produce a demo that looks right and means nothing.
    """
    from ..neural.t1_protocol import (
        T1_PERSISTENCE_PROFILES,
        T1_VALIDATION_SUBJECTS,
        T1Thresholds,
    )

    if subject_id not in T1_VALIDATION_SUBJECTS:
        raise EdgeArtifactError(
            f"{subject_id!r} is not one of the twelve T1 validation subjects, so "
            "no leave-one-subject-out operating point exists for it. The edge "
            "runtime refuses to borrow another subject's thresholds. Validated "
            f"subjects: {', '.join(T1_VALIDATION_SUBJECTS)}."
        )
    directory = resolve_run_dir(Path(run_root), T1_RUN) / "fold_selections"
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("held_out_subject") != subject_id:
            continue
        if payload.get("selected_policy_id") != PROMOTED_T1_POLICY_ID:
            raise EdgeArtifactError(
                f"Fold for {subject_id} promoted "
                f"{payload.get('selected_policy_id')!r}, not the expected "
                f"{PROMOTED_T1_POLICY_ID!r}."
            )
        profile_name = str(payload["persistence_profile"])
        profiles = {profile.name: profile for profile in T1_PERSISTENCE_PROFILES}
        if profile_name not in profiles:
            raise EdgeArtifactError(f"Unknown persistence profile {profile_name!r}.")
        return T1FoldPolicy(
            held_out_subject=subject_id,
            fold_index=int(payload["fold_index"]),
            policy_id=str(payload["selected_policy_id"]),
            persistence_profile=profile_name,
            thresholds=T1Thresholds(
                p_watch=float(payload["p_watch"]),
                s_watch=float(payload["s_watch"]),
                p_event=float(payload["p_event"]),
                s_event=float(payload["s_event"]),
            ),
            q_watch=float(payload["q_watch"]),
            q_event=float(payload["q_event"]),
            threshold_population=str(payload["threshold_population"]),
            threshold_population_row_count=int(
                payload["threshold_population_row_count"]
            ),
        )
    raise EdgeArtifactError(f"No T1 fold selection found for {subject_id!r}.")


@dataclass(frozen=True)
class RuntimeArtifacts:
    """Every frozen component one streaming session needs, loaded once.

    The single controlled loader. Nothing else in `edge/` opens a checkpoint,
    a lock or a calibrator, so an alert can name exactly what produced it.
    """

    frozen: FrozenArtifacts
    standardizer: Any
    m1l_scorer: Any
    calibrator: Any
    temporal_model: Any
    t1_policy: T1FoldPolicy
    m2_arm: str = RETAINED_M2_ARM

    def provenance(self) -> dict[str, Any]:
        payload = dict(self.frozen.provenance())
        payload.update(
            {
                "m2_arm": self.m2_arm,
                "m1l_classification_threshold": (
                    self.m1l_scorer.classification_threshold
                ),
                "u1_family": self.calibrator.family,
                "u1_a": self.calibrator.a,
                "u1_b": self.calibrator.b,
                "u1_clamp_delta": self.calibrator.clamp_delta,
                "t2_arm": type(self.temporal_model).__name__,
                "score_is_calibrated_probability": False,
                "selective_router_retained": False,
            }
        )
        payload.update(self.t1_policy.provenance())
        return payload


def load_runtime_artifacts(
    subject_id: str,
    *,
    run_root: Path | str = DEFAULT_RUN_ROOT,
    feature_root: Path | str = DEFAULT_FEATURE_ROOT,
) -> RuntimeArtifacts:
    """Load every frozen component for one subject's streaming session.

    `subject_id` is not a model input. It selects the leave-one-subject-out T1
    operating point and nothing else -- the same rule the research pipeline
    obeyed, where patient identity chooses a state namespace and a calibrator
    and is never a predictive feature.
    """
    import torch

    from ..neural.m2_scorer import load_frozen_m1l_scorer
    from ..neural.patient_memory import M1DistanceStandardizer
    from ..neural.t2_protocol import T2_ARM_S4D
    from ..neural.t2_training import restore_model_state
    from ..neural.u1_calibration import U1Calibrator

    root = Path(run_root)
    features = Path(feature_root)

    payload = json.loads(
        features.joinpath(*STANDARDIZER_PATH).read_text(encoding="utf-8")
    )
    standardizer = M1DistanceStandardizer(
        means=tuple(payload["means"]),
        scales=tuple(payload["scales"]),
        prior=tuple(payload["prior"]),
        zero_variance_dimensions=tuple(payload["zero_variance_dimensions"]),
        fitted_rows=int(payload["fitted_rows"]),
        fitted_population=str(payload["fitted_population"]),
        input_identities=payload["input_identities"],
    )

    deployment = json.loads(
        (resolve_run_dir(root, U1_RUN) / "U1_DEPLOYMENT_CALIBRATOR.json").read_text(
            encoding="utf-8"
        )
    )
    fitted = deployment["calibrator"]
    calibrator = U1Calibrator(
        family=str(fitted["family"]),
        a=float(fitted["a"]),
        b=float(fitted["b"]),
        clamp_delta=float(fitted["clamp_delta"]),
        fit_row_count=int(fitted["fit_row_count"]),
        fit_subjects=tuple(fitted["fit_subjects"]),
        optimizer=fitted.get("optimizer", {}),
    )
    if deployment.get("selected_family") != calibrator.family:
        raise EdgeArtifactError(
            "The deployment calibrator's fitted family does not match the "
            "frozen family selection."
        )

    checkpoint = torch.load(
        resolve_run_dir(root, T2_RUN) / "T2_S4D_BEST_CHECKPOINT.pt",
        map_location="cpu",
        weights_only=True,
    )
    state_dict = (
        checkpoint["model"]
        if isinstance(checkpoint, dict) and "model" in checkpoint
        else checkpoint
    )
    temporal = restore_model_state(T2_ARM_S4D, state_dict)
    # `restore_model_state` calls eval() but leaves requires_grad set. Inference
    # never needs gradients, and leaving them on is how a "frozen" model
    # quietly stops being frozen.
    temporal.requires_grad_(False)

    return RuntimeArtifacts(
        frozen=load_frozen_artifacts(root),
        standardizer=standardizer,
        m1l_scorer=load_frozen_m1l_scorer(resolve_run_dir(root, M1_RUN)),
        calibrator=calibrator,
        temporal_model=temporal,
        t1_policy=resolve_t1_policy(subject_id, root),
    )
