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
only. That remains true after the B4-B sealed test was consumed on 2026-08-25:
nothing here reads the test partition, its cache, or any of the four artifacts
that attempt produced.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from ..data.provenance import sha256_file
from ..neural.integrity import verify_experiment_lock
from ..neural.m1_experiment import load_frozen_physiology_transform
from ..neural.p1_experiment import (
    B4B_CHECKPOINT_SHA256,
    load_official_b4b_encoder,
    validate_p1_lock,
)
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
class RuntimeArtifactVerification:
    """One artifact identity verified before it can affect inference."""

    component: str
    logical_artifact_id: str
    canonical_path: str
    expected_sha256: str
    observed_sha256: str
    expected_digest_source: str
    verification_mechanism: str
    verification_status: str = "verified"

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class _RuntimeBundleManifest:
    path: Path
    bundle_root: Path
    entries: dict[str, dict[str, Any]]


def _require_sha256(label: str, value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise EdgeArtifactError(f"{label} does not contain an authoritative SHA-256.")
    return value


def _verification(
    *,
    component: str,
    logical_artifact_id: str,
    path: Path,
    expected_sha256: str,
    expected_digest_source: str,
    verification_mechanism: str,
) -> RuntimeArtifactVerification:
    expected = _require_sha256(
        f"Expected digest for {logical_artifact_id}", expected_sha256
    )
    artifact = Path(path)
    if not artifact.is_file():
        raise EdgeArtifactError(f"Required runtime artifact {artifact} is missing.")
    observed = sha256_file(artifact)
    if observed != expected:
        raise EdgeArtifactError(
            f"Runtime artifact {logical_artifact_id} digest mismatch: observed "
            f"{observed}, expected {expected} from {expected_digest_source}."
        )
    return RuntimeArtifactVerification(
        component=component,
        logical_artifact_id=logical_artifact_id,
        canonical_path=str(artifact),
        expected_sha256=expected,
        observed_sha256=observed,
        expected_digest_source=expected_digest_source,
        verification_mechanism=verification_mechanism,
    )


def _discover_runtime_bundle_manifest(
    run_root: Path, feature_root: Path
) -> _RuntimeBundleManifest | None:
    """Find the committed demo manifest from its mirrored run/feature layout."""
    runs = Path(run_root).resolve()
    features = Path(feature_root).resolve()
    if runs.name != "runs" or features.name != "features":
        return None
    if runs.parent != features.parent:
        return None
    bundle_root = runs.parent
    manifest_path = bundle_root.parent / "DEMO_BUNDLE_SELECTION.json"
    if not manifest_path.is_file():
        return None
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        files = list(payload["files"])
    except (KeyError, TypeError, json.JSONDecodeError, OSError) as error:
        raise EdgeArtifactError(
            f"Runtime bundle manifest {manifest_path} is unreadable or invalid."
        ) from error
    if payload.get("artifact_class") != "cardiosentinel_demo_bundle_selection":
        raise EdgeArtifactError(
            f"Runtime bundle manifest {manifest_path} has an unknown identity."
        )
    entries: dict[str, dict[str, Any]] = {}
    for entry in files:
        relative = entry.get("path") if isinstance(entry, dict) else None
        if not isinstance(relative, str) or not relative:
            raise EdgeArtifactError(
                f"Runtime bundle manifest {manifest_path} contains an invalid path."
            )
        if relative in entries:
            raise EdgeArtifactError(
                f"Runtime bundle manifest repeats artifact path {relative!r}."
            )
        _require_sha256(f"Manifest digest for {relative}", entry.get("sha256"))
        entries[relative] = dict(entry)
    try:
        file_count = int(payload.get("file_count", -1))
    except (TypeError, ValueError) as error:
        raise EdgeArtifactError(
            f"Runtime bundle manifest {manifest_path} has an invalid file count."
        ) from error
    if file_count != len(entries):
        raise EdgeArtifactError(
            f"Runtime bundle manifest {manifest_path} file count is inconsistent."
        )
    manifest = _RuntimeBundleManifest(manifest_path, bundle_root, entries)
    # Runtime correctness cannot depend on the caller remembering to invoke the
    # standalone verifier. Validate the selected bundle before any deserialiser.
    for relative, entry in entries.items():
        target = (bundle_root / relative).resolve()
        try:
            target.relative_to(bundle_root)
        except ValueError as error:
            raise EdgeArtifactError(
                f"Runtime bundle path {relative!r} escapes {bundle_root}."
            ) from error
        _verification(
            component="bundle",
            logical_artifact_id=relative,
            path=target,
            expected_sha256=str(entry["sha256"]),
            expected_digest_source=str(manifest_path),
            verification_mechanism="runtime_bundle_manifest",
        )
    return manifest


def _manifest_verification(
    manifest: _RuntimeBundleManifest,
    *,
    component: str,
    relative: str,
) -> RuntimeArtifactVerification:
    entry = manifest.entries.get(relative)
    if entry is None:
        raise EdgeArtifactError(
            f"Runtime bundle manifest {manifest.path} has no expected digest for "
            f"required artifact {relative}."
        )
    return _verification(
        component=component,
        logical_artifact_id=relative,
        path=manifest.bundle_root / relative,
        expected_sha256=str(entry["sha256"]),
        expected_digest_source=str(manifest.path),
        verification_mechanism="runtime_bundle_manifest",
    )


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
    p1b_lock: dict[str, Any]
    integrity: tuple[RuntimeArtifactVerification, ...]

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
            # Read from the P1-B lock, not hardcoded. These two fields are that
            # experiment's attestation about its own run -- P1-B was fitted with
            # the B4 test unopened, and its lock says so permanently. Asserting
            # them as constants here made the runtime state a claim about the
            # programme rather than a fact about the artifacts it loaded, and
            # that claim stopped being readable as true on 2026-08-25. The
            # value is unchanged; what changed is that it is now sourced.
            "test_accessed": self.p1b_lock["test_accessed"],
            "sealed_test_state": self.p1b_lock["sealed_test_state"],
        }


def resolve_run_dir(run_root: Path, parts: tuple[str, ...]) -> Path:
    directory = Path(run_root).joinpath(*parts)
    if not directory.is_dir():
        raise EdgeArtifactError(
            f"Frozen run directory {directory} does not exist. The edge runtime "
            "loads retained artifacts; it never creates them."
        )
    return directory


def load_frozen_artifacts(
    run_root: Path | str = DEFAULT_RUN_ROOT,
    *,
    runtime_manifest: _RuntimeBundleManifest | None = None,
) -> FrozenArtifacts:
    """Load the retained encoder and physiology transform, digests checked.

    Both loaders raise if the artifact is not the selected one, so a wrong or
    tampered checkpoint fails here rather than producing a plausible number
    downstream.
    """
    root = Path(run_root)
    b4b = resolve_run_dir(root, B4B_RUN)
    p1b = resolve_run_dir(root, P1B_RUN)
    lock_path = p1b / "EXPERIMENT_LOCK.json"
    if not lock_path.is_file():
        raise EdgeArtifactError(
            f"No EXPERIMENT_LOCK.json under {p1b}. The runtime reports its "
            "test-access attestation from that lock and will not invent one."
        )
    lock = (
        json.loads(lock_path.read_text(encoding="utf-8"))
        if runtime_manifest is not None
        else validate_p1_lock(p1b)
    )
    for field in ("test_accessed", "sealed_test_state"):
        if field not in lock:
            raise EdgeArtifactError(
                f"P1-B lock at {lock_path} carries no {field!r}. Refusing "
                "rather than substituting a default: a provenance field that "
                "falls back to a constant is the defect this read replaced."
            )
    b4_checkpoint = b4b / "model_selected.pt"
    p1_transform = p1b / "PHYSIOLOGY_TRANSFORM.json"
    if runtime_manifest is not None:
        b4_verification = _manifest_verification(
            runtime_manifest,
            component="encoder",
            relative="runs/" + "/".join((*B4B_RUN, "model_selected.pt")),
        )
        p1_verification = _manifest_verification(
            runtime_manifest,
            component="physiology",
            relative="runs/" + "/".join((*P1B_RUN, "PHYSIOLOGY_TRANSFORM.json")),
        )
    else:
        b4_verification = _verification(
            component="encoder",
            logical_artifact_id="B4-B/model_selected.pt",
            path=b4_checkpoint,
            expected_sha256=B4B_CHECKPOINT_SHA256,
            expected_digest_source=str(b4b / "EXPERIMENT_LOCK.json"),
            verification_mechanism="experiment_lock",
        )
        p1_expected = dict(lock.get("artifact_sha256") or {}).get(
            "PHYSIOLOGY_TRANSFORM.json"
        )
        p1_verification = _verification(
            component="physiology",
            logical_artifact_id="P1-B/PHYSIOLOGY_TRANSFORM.json",
            path=p1_transform,
            expected_sha256=p1_expected,
            expected_digest_source=str(lock_path),
            verification_mechanism="experiment_lock",
        )
    return FrozenArtifacts(
        encoder=load_official_b4b_encoder(b4b),
        physiology=load_frozen_physiology_transform(p1b),
        b4b_run_dir=b4b,
        p1b_run_dir=p1b,
        p1b_lock=lock,
        integrity=(b4_verification, p1_verification),
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
    verification: RuntimeArtifactVerification

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
            "t1_selection_sha256": self.verification.observed_sha256,
            "t1_selection_digest_source": (
                self.verification.expected_digest_source
            ),
            "t1_thresholds_generated_here": False,
            "t1_held_out_labels_opened": False,
        }


def resolve_t1_policy(
    subject_id: str,
    run_root: Path | str = DEFAULT_RUN_ROOT,
    *,
    runtime_manifest: _RuntimeBundleManifest | None = None,
) -> T1FoldPolicy:
    """The promoted policy for one held-out subject, or a refusal.

    Refusing is the point. A record outside the twelve validation subjects has
    **no validated operating point**, and serving it another subject's
    thresholds would produce a demo that looks right and means nothing.
    """
    from ..neural.t1_continuation_spec import PREDECESSOR_FOLD_SELECTIONS
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
    matches = [
        (int(fold), str(policy), str(digest))
        for fold, (held_out, policy, digest) in PREDECESSOR_FOLD_SELECTIONS.items()
        if held_out == subject_id
    ]
    if len(matches) != 1:
        raise EdgeArtifactError(
            f"The frozen T1 selection receipt does not identify exactly one fold "
            f"for {subject_id!r}."
        )
    fold_index, receipt_policy, receipt_digest = matches[0]
    name = f"T1_FOLD_{fold_index:02d}_SELECTION.json"
    directory = resolve_run_dir(Path(run_root), T1_RUN) / "fold_selections"
    path = directory / name
    if runtime_manifest is not None:
        verification = _manifest_verification(
            runtime_manifest,
            component="episode",
            relative="runs/" + "/".join((*T1_RUN, "fold_selections", name)),
        )
    else:
        verification = _verification(
            component="episode",
            logical_artifact_id=f"T1/{name}",
            path=path,
            expected_sha256=receipt_digest,
            expected_digest_source=(
                "t1_continuation_spec.PREDECESSOR_FOLD_SELECTIONS "
                "(T1 recovery amendment section 1.4)"
            ),
            verification_mechanism="selection_receipt",
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("held_out_subject") != subject_id:
        raise EdgeArtifactError(
            f"Verified T1 fold {fold_index} names held-out subject "
            f"{payload.get('held_out_subject')!r}, not {subject_id!r}."
        )
    if receipt_policy != PROMOTED_T1_POLICY_ID:
        raise EdgeArtifactError(
            f"The T1 selection receipt promotes {receipt_policy!r}, not the "
            f"runtime policy {PROMOTED_T1_POLICY_ID!r}."
        )
    if payload.get("selected_policy_id") != receipt_policy:
        raise EdgeArtifactError(
            f"Fold for {subject_id} promoted "
            f"{payload.get('selected_policy_id')!r}, not the receipt-bound "
            f"{receipt_policy!r}."
        )
    profile_name = str(payload["persistence_profile"])
    profiles = {profile.name: profile for profile in T1_PERSISTENCE_PROFILES}
    if profile_name not in profiles:
        raise EdgeArtifactError(f"Unknown persistence profile {profile_name!r}.")
    return T1FoldPolicy(
        held_out_subject=subject_id,
        fold_index=fold_index,
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
        verification=verification,
    )


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
    integrity: tuple[RuntimeArtifactVerification, ...]
    m2_arm: str = RETAINED_M2_ARM

    def provenance(self) -> dict[str, Any]:
        payload = dict(self.frozen.provenance())
        verified = (*self.frozen.integrity, *self.integrity)
        by_component = {item.component: item for item in verified}
        payload.update(
            {
                "runtime_integrity_verified": all(
                    item.verification_status == "verified" for item in verified
                ),
                "runtime_artifacts": [item.as_dict() for item in verified],
                "m2_arm": self.m2_arm,
                "m1l_checkpoint_sha256": by_component[
                    "memory"
                ].observed_sha256,
                "m1l_classification_threshold": (
                    self.m1l_scorer.classification_threshold
                ),
                "u1_family": self.calibrator.family,
                "u1_artifact_sha256": by_component[
                    "calibration"
                ].observed_sha256,
                "u1_a": self.calibrator.a,
                "u1_b": self.calibrator.b,
                "u1_clamp_delta": self.calibrator.clamp_delta,
                "t2_arm": type(self.temporal_model).__name__,
                "t2_checkpoint_sha256": by_component[
                    "temporal"
                ].observed_sha256,
                "score_is_calibrated_probability": False,
                "selective_router_retained": False,
            }
        )
        payload.update(self.t1_policy.provenance())
        return payload


def _u1_artifact_verification(
    run_dir: Path, runtime_manifest: _RuntimeBundleManifest | None
) -> RuntimeArtifactVerification:
    artifact = Path(run_dir) / "U1_DEPLOYMENT_CALIBRATOR.json"
    if runtime_manifest is not None:
        return _manifest_verification(
            runtime_manifest,
            component="calibration",
            relative="runs/" + "/".join((*U1_RUN, artifact.name)),
        )
    lock_path = Path(run_dir) / "U1_EXPERIMENT_LOCK.json"
    if not lock_path.is_file():
        raise EdgeArtifactError(
            f"No authoritative U1 experiment lock at {lock_path}; the runtime "
            "will not use whatever calibrator happens to exist."
        )
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EdgeArtifactError(
            f"U1 experiment lock {lock_path} is invalid."
        ) from error
    if not verify_experiment_lock(lock):
        raise EdgeArtifactError(
            f"U1 experiment lock {lock_path} failed its canonical digest."
        )
    expected = dict(lock.get("artifact_sha256") or {}).get(artifact.name)
    if expected != lock.get("final_deployment_calibrator_sha256"):
        raise EdgeArtifactError(
            "The U1 experiment lock does not bind one unambiguous deployment "
            "calibrator digest."
        )
    return _verification(
        component="calibration",
        logical_artifact_id="U1/U1_DEPLOYMENT_CALIBRATOR.json",
        path=artifact,
        expected_sha256=expected,
        expected_digest_source=str(lock_path),
        verification_mechanism="experiment_lock",
    )


def _t2_artifact_verification(
    run_dir: Path, runtime_manifest: _RuntimeBundleManifest | None
) -> tuple[RuntimeArtifactVerification, dict[str, Any]]:
    from ..neural.t2_persistence import load_checkpoint, read_checkpoint_lock
    from ..neural.t2_protocol import T2_ARM_S4D

    artifact = Path(run_dir) / "T2_S4D_BEST_CHECKPOINT.pt"
    if runtime_manifest is not None:
        verification = _manifest_verification(
            runtime_manifest,
            component="temporal",
            relative="runs/" + "/".join((*T2_RUN, artifact.name)),
        )
    else:
        try:
            lock = read_checkpoint_lock(Path(run_dir), T2_ARM_S4D)
        except Exception as error:  # noqa: BLE001 - normalize a frozen-loader refusal
            raise EdgeArtifactError(
                f"The authoritative T2 checkpoint lock under {run_dir} failed "
                "verification."
            ) from error
        verification = _verification(
            component="temporal",
            logical_artifact_id="T2/T2_S4D_BEST_CHECKPOINT.pt",
            path=artifact,
            expected_sha256=lock.get("checkpoint_sha256"),
            expected_digest_source=str(
                Path(run_dir) / "T2_S4D_CHECKPOINT_LOCK.json"
            ),
            verification_mechanism="checkpoint_lock",
        )
    try:
        checkpoint = load_checkpoint(
            artifact, expected_sha256=verification.expected_sha256
        )
    except Exception as error:  # noqa: BLE001 - normalize a frozen-loader refusal
        raise EdgeArtifactError(
            f"Verified T2 checkpoint {artifact} could not be safely loaded."
        ) from error
    return verification, checkpoint


def _m1_artifact_verification(
    scorer: Any,
    run_dir: Path,
    runtime_manifest: _RuntimeBundleManifest | None,
) -> RuntimeArtifactVerification:
    artifact = Path(run_dir) / "M1L_long_memory_v2" / "model_selected.pt"
    if runtime_manifest is not None:
        return _manifest_verification(
            runtime_manifest,
            component="memory",
            relative="runs/" + "/".join(
                (*M1_RUN, "M1L_long_memory_v2", "model_selected.pt")
            ),
        )
    identity = scorer.identity()
    return _verification(
        component="memory",
        logical_artifact_id="M1L/model_selected.pt",
        path=artifact,
        expected_sha256=identity.get("retained_checkpoint_sha256"),
        expected_digest_source=str(
            Path(run_dir) / "M1L_long_memory_v2" / "EXPERIMENT_LOCK.json"
        ),
        verification_mechanism="experiment_lock",
    )


def _standardizer_artifact_verification(
    *,
    path: Path,
    payload: dict[str, Any],
    scorer: Any,
    runtime_manifest: _RuntimeBundleManifest | None,
) -> RuntimeArtifactVerification:
    bound = dict(scorer.lock.get("distance_standardizer") or {}).get(
        "standardizer_sha256"
    )
    observed_canonical = payload.get("standardizer_sha256")
    expected_canonical = _require_sha256(
        "M1 lock standardizer digest", bound
    )
    if observed_canonical != expected_canonical:
        raise EdgeArtifactError(
            "The M1 standardizer canonical digest differs from the retained "
            "M1 experiment lock."
        )
    if runtime_manifest is not None:
        record = _manifest_verification(
            runtime_manifest,
            component="standardizer",
            relative="features/" + "/".join(STANDARDIZER_PATH),
        )
        return RuntimeArtifactVerification(
            **{
                **record.as_dict(),
                "verification_mechanism": (
                    "runtime_bundle_manifest+canonical_payload+experiment_lock"
                ),
            }
        )
    return RuntimeArtifactVerification(
        component="standardizer",
        logical_artifact_id="M1/M1_DISTANCE_STANDARDIZER.json",
        canonical_path=str(path),
        expected_sha256=expected_canonical,
        observed_sha256=str(observed_canonical),
        expected_digest_source=(
            str(Path(scorer.lock.get("experiment_id", "M1L_long_memory_v2")))
            + "/EXPERIMENT_LOCK.json:distance_standardizer.standardizer_sha256"
        ),
        verification_mechanism="canonical_payload+experiment_lock",
    )


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
    from ..neural.m2_scorer import load_frozen_m1l_scorer
    from ..neural.patient_memory import M1DistanceStandardizer
    from ..neural.t2_protocol import T2_ARM_S4D
    from ..neural.t2_training import restore_model_state
    from ..neural.u1_calibration import U1Calibrator
    from ..neural.u1_selection import (
        U1_DEPLOYMENT_CALIBRATOR_A,
        U1_DEPLOYMENT_CALIBRATOR_B,
        U1_RETAINED_CALIBRATOR_FAMILY,
    )

    root = Path(run_root)
    features = Path(feature_root)
    runtime_manifest = _discover_runtime_bundle_manifest(root, features)
    frozen = load_frozen_artifacts(root, runtime_manifest=runtime_manifest)
    m1_run_dir = resolve_run_dir(root, M1_RUN)
    m1l_scorer = load_frozen_m1l_scorer(m1_run_dir)
    m1_verification = _m1_artifact_verification(
        m1l_scorer, m1_run_dir, runtime_manifest
    )

    standardizer_path = features.joinpath(*STANDARDIZER_PATH)
    try:
        standardizer_payload = json.loads(
            standardizer_path.read_text(encoding="utf-8")
        )
        standardizer = M1DistanceStandardizer.from_dict(standardizer_payload)
    except Exception as error:  # noqa: BLE001 - normalize a frozen-loader refusal
        raise EdgeArtifactError(
            f"M1 standardizer {standardizer_path} failed identity validation."
        ) from error
    standardizer_verification = _standardizer_artifact_verification(
        path=standardizer_path,
        payload=standardizer_payload,
        scorer=m1l_scorer,
        runtime_manifest=runtime_manifest,
    )

    u1_run_dir = resolve_run_dir(root, U1_RUN)
    u1_verification = _u1_artifact_verification(u1_run_dir, runtime_manifest)
    try:
        deployment = json.loads(
            (u1_run_dir / "U1_DEPLOYMENT_CALIBRATOR.json").read_text(
                encoding="utf-8"
            )
        )
    except (OSError, json.JSONDecodeError) as error:
        raise EdgeArtifactError(
            "The verified U1 calibrator is invalid JSON."
        ) from error
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
    if calibrator.family != U1_RETAINED_CALIBRATOR_FAMILY:
        raise EdgeArtifactError("The U1 calibrator is not the retained family.")
    if (calibrator.a, calibrator.b) != (
        U1_DEPLOYMENT_CALIBRATOR_A,
        U1_DEPLOYMENT_CALIBRATOR_B,
    ):
        raise EdgeArtifactError(
            "The U1 calibrator parameters do not match the retained deployment "
            "identity."
        )

    t2_run_dir = resolve_run_dir(root, T2_RUN)
    t2_verification, checkpoint = _t2_artifact_verification(
        t2_run_dir, runtime_manifest
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

    t1_policy = resolve_t1_policy(
        subject_id, root, runtime_manifest=runtime_manifest
    )
    return RuntimeArtifacts(
        frozen=frozen,
        standardizer=standardizer,
        m1l_scorer=m1l_scorer,
        calibrator=calibrator,
        temporal_model=temporal,
        t1_policy=t1_policy,
        integrity=(
            m1_verification,
            standardizer_verification,
            u1_verification,
            t2_verification,
            t1_policy.verification,
        ),
    )
