"""Contract tests for the E12d six-fit orchestrator.

E12d is not authorized. These tests prove the orchestrator would run exactly the
six preregistered fits and nothing else, and that its dry-run mode describes
that plan without training anything.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import torch
from torch import nn

from cardiosentinel.neural.candidates import B4BTransformerCNN
from cardiosentinel.neural.e11_data_binding import E11Sources, bind_e11_data
from cardiosentinel.neural.e12d_orchestrator import (
    E12D_AUX_LAMBDA,
    E12D_AUX_SEED,
    E12D_FIT_ORDER,
    E12dFitPlan,
    E12dOrchestratorError,
    build_plan,
    run_e12d_phase1,
    write_dry_run_plan,
)
from cardiosentinel.neural.protocol import SEED
from cardiosentinel.neural.training import (
    EARLY_STOPPING_DELTA,
    EARLY_STOPPING_PATIENCE,
    MAX_EPOCHS,
)

SUBJECTS = [f"s00{i}" for i in range(1, 7)]
STREAMS_PER_SUBJECT = 2
ROWS_PER_STREAM = 4
ROWS = len(SUBJECTS) * STREAMS_PER_SUBJECT * ROWS_PER_STREAM


@pytest.fixture()
def binding(tmp_path: Path):
    cache, protocol = tmp_path / "cache", tmp_path / "protocol"
    cache.mkdir()
    protocol.mkdir()
    subjects, streams, stable_ids, labels, folds = [], [], [], [], []
    for index, subject in enumerate(SUBJECTS):
        for channel in range(STREAMS_PER_SUBJECT):
            for row in range(ROWS_PER_STREAM):
                start = (index * 100 + channel * 10 + row) * 2500
                subjects.append(subject)
                streams.append(f"{subject}:{channel}")
                stable_ids.append(f"ltstdb:{subject}1:{channel}:{start}:{start + 2500}")
                labels.append(1.0 if row % 2 == 0 else 0.0)
                folds.append(index // 2)
    rng = np.random.default_rng(2026)
    auxiliary = rng.normal(size=ROWS)
    auxiliary[3] = np.nan
    np.save(cache / "train_stable_ids.npy", np.array(stable_ids))
    np.save(protocol / "e11_train_y.npy", np.array(labels))
    np.save(protocol / "e11_train_subj.npy", np.array(subjects))
    np.save(protocol / "e11_train_stream.npy", np.array(streams))
    np.save(protocol / "e11_train_fold.npy", np.array(folds))
    np.save(protocol / "e11_aux_target.npy", auxiliary)
    assignment = {s: i // 2 for i, s in enumerate(SUBJECTS)}
    (protocol / "e11_folds.json").write_text(
        json.dumps({"assignment": assignment, "prevalence": {s: 0.5 for s in SUBJECTS}})
    )
    digest = hashlib.sha256(
        json.dumps(assignment, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return bind_e11_data(
        sources=E11Sources(waveform_cache=cache, protocol_dir=protocol),
        expected_split_digest=digest,
        experiment_id="E12D_TEST",
        expected_subject_count=len(SUBJECTS),
    )


# --------------------------------------------------------------------------
# the plan is exactly the six preregistered configurations
# --------------------------------------------------------------------------


def test_fit_order_is_the_six_preregistered_fits_in_historical_order() -> None:
    assert E12D_FIT_ORDER == (
        (0, "B0"), (0, "B1"), (1, "B0"), (1, "B1"), (2, "B0"), (2, "B1"),
    )
    assert isinstance(E12D_FIT_ORDER, tuple)  # frozen, not reorderable in place


def test_dry_run_plan_matches_the_six_preregistered_configurations(
    binding, tmp_path: Path
) -> None:
    plans = build_plan(binding)
    assert len(plans) == 6
    assert tuple((p.fold, p.arm) for p in plans) == E12D_FIT_ORDER
    for index, plan in enumerate(plans):
        assert plan.order_index == index
        assert plan.seed == SEED
        assert plan.max_epochs == MAX_EPOCHS
        assert plan.patience == EARLY_STOPPING_PATIENCE
        assert plan.early_stopping_delta == EARLY_STOPPING_DELTA
        assert plan.split_digest == binding.split_digest
        assert plan.selection_rule == (
            "max inner pooled AUPRC, earliest epoch wins an exact tie"
        )
        assert plan.phase2_included is False
        assert plan.outer_scoring_included is False


def test_b0_carries_semantic_null_and_b1_carries_the_frozen_auxiliary(
    binding,
) -> None:
    plans = {(p.fold, p.arm): p for p in build_plan(binding)}
    for fold in (0, 1, 2):
        b0, b1 = plans[(fold, "B0")], plans[(fold, "B1")]
        assert b0.aux_lambda is None
        assert b0.aux_target is None
        assert b0.aux_seed is None
        assert b0.scaler_source_partition is None
        assert b0.scaler_median is None and b0.scaler_iqr is None
        assert b1.aux_lambda == E12D_AUX_LAMBDA == 0.1
        assert b1.aux_target == "post_r_80ms_delta_mv"
        assert b1.aux_seed == E12D_AUX_SEED
        assert b1.scaler_source_partition == "inner_train"


def test_paired_arms_share_identical_partitions(binding) -> None:
    """B0 and B1 of a fold must see exactly the same rows and subjects."""
    plans = {(p.fold, p.arm): p for p in build_plan(binding)}
    for fold in (0, 1, 2):
        b0, b1 = plans[(fold, "B0")], plans[(fold, "B1")]
        assert b0.inner_train_rows == b1.inner_train_rows
        assert b0.inner_validation_rows == b1.inner_validation_rows
        assert b0.authority_identity_digest == b1.authority_identity_digest
        assert b0.inner_validation_prevalence == b1.inner_validation_prevalence


def test_the_plan_never_reports_held_out_quantities(binding) -> None:
    """Phase-1 scope: the plan has no field describing outer-held-out data."""
    fields = set(E12dFitPlan.__dataclass_fields__)
    for forbidden in (
        "held_out_rows", "outer_held_out_rows", "held_out_subjects",
        "outer_train_rows", "held_out_prevalence", "test_rows",
    ):
        assert forbidden not in fields, forbidden


def test_dry_run_writes_a_plan_and_trains_nothing(binding, tmp_path: Path) -> None:
    plans = build_plan(binding)
    path = tmp_path / "e12d_dry_run.json"
    digest = write_dry_run_plan(plans, path)

    payload = json.loads(path.read_text())
    assert payload["mode"] == "DRY_RUN"
    assert payload["trained"] is False
    assert payload["authorized"] is False
    assert payload["scope"] == "phase_1_only"
    assert payload["phase2_included"] is False
    assert payload["outer_scoring_included"] is False
    assert payload["outer_geometry_included"] is False
    assert payload["operating_point_on_held_out_included"] is False
    assert payload["fit_count"] == 6
    assert payload["fit_order"] == [[f, a] for f, a in E12D_FIT_ORDER]
    assert len(digest) == 64

    # nothing was trained: no checkpoint or evidence file anywhere
    assert list(tmp_path.rglob("*.pt")) == []
    assert list(tmp_path.rglob("*epochs.json")) == []


def test_dry_run_plan_is_deterministic(binding, tmp_path: Path) -> None:
    first = write_dry_run_plan(build_plan(binding), tmp_path / "a.json")
    second = write_dry_run_plan(build_plan(binding), tmp_path / "b.json")
    assert first == second


# --------------------------------------------------------------------------
# the orchestrator contains no intelligence of its own
# --------------------------------------------------------------------------


def test_orchestrator_exports_no_selection_or_threshold_machinery() -> None:
    import cardiosentinel.neural.e12d_orchestrator as module

    for forbidden in (
        "select_epoch", "select_checkpoint", "choose", "best_epoch",
        "f1_optimal_threshold", "threshold", "retry", "relaunch",
        "resume", "sweep", "search", "lambda_sweep", "evaluate_outer_held_out",
        "run_phase2",
    ):
        assert not hasattr(module, forbidden), forbidden


def test_orchestrator_refuses_a_plan_outside_the_frozen_order(binding) -> None:
    plans = list(build_plan(binding))
    plans.reverse()
    with pytest.raises(E12dOrchestratorError, match="frozen E12d fit order"):
        run_e12d_phase1(
            binding=binding,
            plans=plans,
            model_factory=lambda arm: None,
            optimizer_factory=lambda m: None,
            primary_loss_factory=lambda: None,
            auxiliary_loss=None,
            batch_provider=lambda rows, arm, scaler: [],
            git_commit="0" * 40,
            evidence_root=Path("."),
        )


def test_orchestrator_refuses_a_truncated_plan(binding) -> None:
    with pytest.raises(E12dOrchestratorError, match="frozen E12d fit order"):
        run_e12d_phase1(
            binding=binding,
            plans=build_plan(binding)[:4],
            model_factory=lambda arm: None,
            optimizer_factory=lambda m: None,
            primary_loss_factory=lambda: None,
            auxiliary_loss=None,
            batch_provider=lambda rows, arm, scaler: [],
            git_commit="0" * 40,
            evidence_root=Path("."),
        )


# --------------------------------------------------------------------------
# execution shape on a tiny fixture (not a scientific run)
# --------------------------------------------------------------------------


def _shortened(plans, max_epochs: int = 1):
    """One epoch per fit: the fixture proves the shape, not any science."""
    return tuple(
        E12dFitPlan(
            **{
                **{f: getattr(p, f) for f in E12dFitPlan.__dataclass_fields__},
                "max_epochs": max_epochs,
            }
        )
        for p in plans
    )


class _B1(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.base = B4BTransformerCNN()
        generator = torch.Generator().manual_seed(E12D_AUX_SEED)
        weight, bias = torch.empty(1, 128), torch.empty(1)
        nn.init.kaiming_uniform_(weight, a=5**0.5, generator=generator)
        nn.init.uniform_(bias, -1 / 128**0.5, 1 / 128**0.5, generator=generator)
        self.aux = nn.Linear(128, 1)
        with torch.no_grad():
            self.aux.weight.copy_(weight)
            self.aux.bias.copy_(bias)

    def forward(self, waveforms: torch.Tensor):
        embedded = self.base.encode(waveforms)
        return (
            self.base.classifier.head(embedded).squeeze(-1),
            self.aux(embedded).squeeze(-1),
        )


def test_orchestrator_runs_exactly_six_phase1_fits(binding, tmp_path: Path) -> None:
    generator = torch.Generator().manual_seed(11)
    waveforms = torch.randn(ROWS, 1, 2500, generator=generator)

    def provider(rows, arm, scaler):
        labels = torch.tensor(binding.labels[rows], dtype=torch.float32)
        piece = [waveforms[rows], labels]
        if arm == "B1":
            target = binding.auxiliary_target[rows]
            mask = np.isfinite(target).astype(np.float32)
            scaled = (np.nan_to_num(target, nan=0.0) - scaler[0]) / scaler[1]
            piece += [torch.tensor(scaled, dtype=torch.float32), torch.tensor(mask)]
        return [tuple(piece)]

    def make(arm):
        torch.manual_seed(SEED)
        return B4BTransformerCNN() if arm == "B0" else _B1()

    plans = _shortened(build_plan(binding))

    results = run_e12d_phase1(
        binding=binding,
        plans=plans,
        model_factory=make,
        optimizer_factory=lambda m: torch.optim.AdamW(
            m.parameters(), lr=1e-3, weight_decay=1e-4
        ),
        primary_loss_factory=nn.BCEWithLogitsLoss,
        auxiliary_loss=nn.functional.smooth_l1_loss,
        batch_provider=provider,
        git_commit="0" * 40,
        evidence_root=tmp_path / "evidence",
    )

    assert len(results) == 6
    for (fold, arm), result in zip(E12D_FIT_ORDER, results):
        directory = tmp_path / "evidence" / f"fold{fold}_{arm}"
        assert (directory / f"phase1_fold{fold}_{arm}_epochs.json").exists()
        assert list((directory / "checkpoints").glob("*.pt"))
        assert result.selected_epoch >= 1
        # phase 1 only: no phase-2 or outer artifact anywhere
        assert not list(directory.glob("phase2_*"))
        assert not list(directory.glob("outer_*"))


def test_orchestrator_produces_no_phase2_or_outer_artifacts(
    binding, tmp_path: Path
) -> None:
    generator = torch.Generator().manual_seed(11)
    waveforms = torch.randn(ROWS, 1, 2500, generator=generator)

    def provider(rows, arm, scaler):
        labels = torch.tensor(binding.labels[rows], dtype=torch.float32)
        piece = [waveforms[rows], labels]
        if arm == "B1":
            target = binding.auxiliary_target[rows]
            mask = np.isfinite(target).astype(np.float32)
            scaled = (np.nan_to_num(target, nan=0.0) - scaler[0]) / scaler[1]
            piece += [torch.tensor(scaled, dtype=torch.float32), torch.tensor(mask)]
        return [tuple(piece)]

    plans = _shortened(build_plan(binding))
    run_e12d_phase1(
        binding=binding,
        plans=plans,
        model_factory=lambda arm: (
            B4BTransformerCNN() if arm == "B0" else _B1()
        ),
        optimizer_factory=lambda m: torch.optim.AdamW(m.parameters(), lr=1e-3),
        primary_loss_factory=nn.BCEWithLogitsLoss,
        auxiliary_loss=nn.functional.smooth_l1_loss,
        batch_provider=provider,
        git_commit="0" * 40,
        evidence_root=tmp_path / "e",
    )
    root = tmp_path / "e"
    assert list(root.rglob("phase2_*")) == []
    assert list(root.rglob("outer_*")) == []
    assert list(root.rglob("*outer_geometry*")) == []
