"""The E12d six-fit orchestrator: phase 1 only, no decisions of its own.

E12d is a **diagnostic replication of E11 phase 1** under E12c instrumentation.
Its plan is `docs/B4_E12D_INSTRUMENTED_PHASE1_REPLICATION_PLAN_V1.md`.
**Nothing here is authorized to run.**

**This module deliberately contains no intelligence.** It has no model-selection
logic (the registered AUPRC rule lives inside `run_phase1` and is untouched), no
threshold logic, no branching on any metric, no retry, and no alternative
parameter path. It enumerates six fits in the historical order and calls the
runner. Everything that could constitute a scientific choice was frozen by E11
and is read from the binding, never computed here.

**Phase 1 only.** There is no phase-2 call, no outer scoring, no outer geometry,
and no operating-point evaluation. The authority's held-out accessor is never
invoked, so outer-held-out subjects are not merely unused -- they are not
reached.

**Dry-run first.** `build_plan` is pure: it mints authorities, reads the frozen
configuration, and emits the complete six-fit execution plan **without
constructing a model or taking an optimizer step**. That plan is what a human
reviews before deciding whether execution happens at all.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Final, Iterable, Sequence

import numpy as np

from cardiosentinel.baseline.cache import write_json_atomic
from cardiosentinel.neural.e11_authority import E11Partition
from cardiosentinel.neural.e11_data_binding import E11DataBinding, morphology_scaler
from cardiosentinel.neural.e11_future_runner import (
    Phase1Config,
    Phase1Result,
    run_phase1,
)
from cardiosentinel.neural.protocol import SEED
from cardiosentinel.neural.training import (
    EARLY_STOPPING_DELTA,
    EARLY_STOPPING_PATIENCE,
    MAX_EPOCHS,
)

__all__ = [
    "E12D_SCHEMA_VERSION",
    "E12D_FIT_ORDER",
    "E12D_AUX_LAMBDA",
    "E12D_AUX_SEED",
    "E12dOrchestratorError",
    "E12dFitPlan",
    "build_plan",
    "write_dry_run_plan",
    "run_e12d_phase1",
    "FitScopedLoaderCache",
]

E12D_SCHEMA_VERSION: Final[str] = "e12d-orchestrator-v1"

#: The six fits, in the historical E11 construction order: folds outer,
#: arms inner. Frozen as a tuple so it cannot be reordered or extended.
E12D_FIT_ORDER: Final[tuple[tuple[int, str], ...]] = (
    (0, "B0"),
    (0, "B1"),
    (1, "B0"),
    (1, "B1"),
    (2, "B0"),
    (2, "B1"),
)

#: Frozen by E11 and reproduced, never chosen here.
E12D_AUX_LAMBDA: Final[float] = 0.1
E12D_AUX_SEED: Final[int] = 20260826
E12D_AUX_TARGET: Final[str] = "post_r_80ms_delta_mv"


class E12dOrchestratorError(RuntimeError):
    """The orchestrator was asked to do something outside its remit."""


@dataclass(frozen=True, slots=True)
class E12dFitPlan:
    """One fit, fully specified before anything is constructed."""

    order_index: int
    fold: int
    arm: str
    aux_lambda: float | None
    aux_target: str | None
    aux_seed: int | None
    seed: int
    max_epochs: int
    patience: int
    early_stopping_delta: float
    selection_rule: str
    split_digest: str
    authority_identity_digest: str
    inner_train_rows: int
    inner_validation_rows: int
    inner_train_subjects: int
    inner_validation_subjects: int
    inner_validation_prevalence: float
    scaler_source_partition: str | None
    scaler_median: float | None
    scaler_iqr: float | None
    phase2_included: bool = False
    outer_scoring_included: bool = False


def build_plan(binding: E11DataBinding) -> tuple[E12dFitPlan, ...]:
    """Enumerate the six fits. Pure: constructs no model and trains nothing."""
    plans: list[E12dFitPlan] = []
    for index, (fold, arm) in enumerate(E12D_FIT_ORDER):
        authority = binding.authority(fold)
        inner_train = authority.inner_train_rows()
        inner_validation = authority.inner_validation_rows()
        scaler = morphology_scaler(binding, inner_train) if arm == "B1" else None
        plans.append(
            E12dFitPlan(
                order_index=index,
                fold=fold,
                arm=arm,
                aux_lambda=E12D_AUX_LAMBDA if arm == "B1" else None,
                aux_target=E12D_AUX_TARGET if arm == "B1" else None,
                aux_seed=E12D_AUX_SEED if arm == "B1" else None,
                seed=SEED,
                max_epochs=MAX_EPOCHS,
                patience=EARLY_STOPPING_PATIENCE,
                early_stopping_delta=EARLY_STOPPING_DELTA,
                selection_rule=(
                    "max inner pooled AUPRC, earliest epoch wins an exact tie"
                ),
                split_digest=binding.split_digest,
                authority_identity_digest=authority.identity_digest,
                inner_train_rows=authority.row_count(E11Partition.INNER_TRAIN),
                inner_validation_rows=authority.row_count(
                    E11Partition.INNER_VALIDATION
                ),
                inner_train_subjects=authority.subject_count(E11Partition.INNER_TRAIN),
                inner_validation_subjects=authority.subject_count(
                    E11Partition.INNER_VALIDATION
                ),
                inner_validation_prevalence=float(
                    binding.labels[inner_validation].mean()
                ),
                scaler_source_partition="inner_train" if arm == "B1" else None,
                scaler_median=scaler[0] if scaler else None,
                scaler_iqr=scaler[1] if scaler else None,
            )
        )
    return tuple(plans)


def write_dry_run_plan(plans: Sequence[E12dFitPlan], path: Path) -> str:
    """Emit the complete execution plan without training. Returns its digest."""
    payload = {
        "schema": E12D_SCHEMA_VERSION,
        "mode": "DRY_RUN",
        "trained": False,
        "authorized": False,
        "scope": "phase_1_only",
        "phase2_included": False,
        "outer_scoring_included": False,
        "outer_geometry_included": False,
        "operating_point_on_held_out_included": False,
        "plan_document": (
            "docs/B4_E12D_INSTRUMENTED_PHASE1_REPLICATION_PLAN_V1.md"
        ),
        "fit_count": len(plans),
        "fit_order": [[fold, arm] for fold, arm in E12D_FIT_ORDER],
        "fits": [asdict(plan) for plan in plans],
    }
    payload["plan_digest"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    write_json_atomic(Path(path), payload)
    return payload["plan_digest"]


def run_e12d_phase1(
    *,
    binding: E11DataBinding,
    plans: Sequence[E12dFitPlan],
    model_factory: Callable[[str], object],
    optimizer_factory: Callable[[object], object],
    primary_loss_factory: Callable[[], object],
    auxiliary_loss: object,
    batch_provider: Callable[[np.ndarray, str, tuple[float, float] | None], Iterable],
    git_commit: str,
    evidence_root: Path,
) -> list[Phase1Result]:
    """Execute the six phase-1 fits in the frozen order. No decisions taken here.

    Every factory is supplied by the caller so that the historical construction
    order -- `initialize_determinism()` then model, then optimizer, then loss,
    then loaders -- is reproduced by the driver rather than reinvented here.
    Dropout makes the RNG stream load-bearing, so that order is a correctness
    requirement, not a style choice.

    There is no loop over alternatives, no comparison of results, no retry, and
    no early exit on any metric. If a fit raises, the exception propagates: the
    run stops and re-execution is a human decision.
    """
    if tuple((plan.fold, plan.arm) for plan in plans) != E12D_FIT_ORDER:
        raise E12dOrchestratorError(
            "the plan does not match the frozen E12d fit order; the orchestrator "
            "runs exactly the six preregistered fits, in order"
        )
    evidence_root = Path(evidence_root)
    results: list[Phase1Result] = []
    for plan in plans:
        authority = binding.authority(plan.fold)
        inner_train = authority.inner_train_rows()
        inner_validation = authority.inner_validation_rows()
        scaler = (
            (plan.scaler_median, plan.scaler_iqr) if plan.arm == "B1" else None
        )
        model = model_factory(plan.arm)
        optimizer = optimizer_factory(model)
        results.append(
            run_phase1(
                config=Phase1Config(
                    fold=plan.fold,
                    arm=plan.arm,
                    git_commit=git_commit,
                    split_digest=plan.split_digest,
                    aux_lambda=plan.aux_lambda,
                    max_epochs=plan.max_epochs,
                    patience=plan.patience,
                    delta=plan.early_stopping_delta,
                ),
                model=model,
                optimizer=optimizer,
                primary_loss=primary_loss_factory(),
                auxiliary_loss=auxiliary_loss if plan.arm == "B1" else None,
                train_batches=lambda rows=inner_train, arm=plan.arm, sc=scaler: (
                    batch_provider(rows, arm, sc)
                ),
                inner_validation_batches=lambda rows=inner_validation: (
                    batch_provider(rows, "B0", None)
                ),
                evidence_dir=evidence_root / f"fold{plan.fold}_{plan.arm}",
                instrument=True,
            )
        )
    return results


# --------------------------------------------------------------------------
# fit-scoped loaders -- the E12d ATTEMPT 1 defect, fixed at its source
# --------------------------------------------------------------------------


@dataclass
class FitScopedLoaderCache:
    """Builds each fit's loaders fresh, and never shares one between fits.

    **This exists because sharing one cost E12d ATTEMPT 1.** E11 built its train
    and inner-validation loaders *inside* every `train()` call, so every fit's
    first inner-validation iteration drew a worker `base_seed` from the **global**
    RNG (`_BaseDataLoaderIter` draws from `loader.generator`, which is `None` for
    the unshuffled validation loader). ATTEMPT 1 cached the validation loader on
    row identity alone; because the orchestrator requests it with `arm="B0"` for
    both arms, each fold's B1 fit silently reused the B0 fit's object, skipped
    that global draw, and shifted every subsequent dropout mask. All three B0
    fits reproduced E11 bit-identically and all three B1 fits diverged from
    epoch 2 -- exactly the signature that implies.

    The fix is to reproduce the historical construction, not to compensate for
    the missing draw: **the fit index is part of the key**, so a loader from a
    previous fit can never be returned. Within a fit the object is reused across
    epochs, which is also what E11 did -- rebuilding per epoch would reset the
    data-order generator and break shuffling instead.

    `begin_fit()` must be called once per fit, before any loader is requested.
    """

    build: Callable[[np.ndarray, str, tuple[float, float] | None, bool], object]
    is_validation: Callable[[np.ndarray], bool]
    _fit_index: int = -1
    _cache: dict[tuple[int, int, int], object] = field(default_factory=dict)
    built: list[dict[str, object]] = field(default_factory=list)

    def begin_fit(self) -> int:
        """Open a new fit scope. Drops the previous fit's loaders."""
        self._fit_index += 1
        self._cache.clear()
        return self._fit_index

    def __call__(
        self,
        rows: np.ndarray,
        arm: str,
        scaler: tuple[float, float] | None,
    ) -> object:
        if self._fit_index < 0:
            raise E12dOrchestratorError(
                "begin_fit() must be called before any loader is requested"
            )
        rows = np.asarray(rows)
        key = (self._fit_index, int(rows[0]), int(rows.size))
        if key not in self._cache:
            shuffle = not self.is_validation(rows)
            loader = self.build(rows, arm, scaler, shuffle)
            self._cache[key] = loader
            self.built.append(
                {
                    "fit_index": self._fit_index,
                    "rows": int(rows.size),
                    "arm": arm,
                    "shuffle": shuffle,
                    "object_id": id(loader),
                }
            )
        return self._cache[key]

    def audit(self) -> dict[str, object]:
        """Evidence that no loader object was shared between fits."""
        by_fit: dict[int, list[int]] = {}
        for record in self.built:
            by_fit.setdefault(int(record["fit_index"]), []).append(
                int(record["object_id"])
            )
        validation = [r for r in self.built if not r["shuffle"]]
        train = [r for r in self.built if r["shuffle"]]
        ids = [int(r["object_id"]) for r in self.built]
        return {
            "fits": len(by_fit),
            "loaders_built": len(self.built),
            "train_loaders": len(train),
            "validation_loaders": len(validation),
            "distinct_objects": len(set(ids)),
            "any_object_shared_between_fits": len(set(ids)) != len(ids),
            "per_fit_loader_counts": {k: len(v) for k, v in by_fit.items()},
        }
