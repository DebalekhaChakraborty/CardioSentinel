"""Regression tests for the E12d ATTEMPT 1 loader-reuse defect.

ATTEMPT 1 failed its historical replication gate because one inner-validation
DataLoader was shared across each fold's B0 and B1 fits. A DataLoader with
`generator=None` draws its worker `base_seed` from the **global** RNG when its
iterator is first created; sharing the object skips that draw for the second
arm and shifts every subsequent dropout mask. These tests pin the fix.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch
from torch.utils.data import DataLoader, TensorDataset

from cardiosentinel.neural.e12d_orchestrator import (
    E12D_FIT_ORDER,
    E12dOrchestratorError,
    FitScopedLoaderCache,
)

TRAIN_ROWS = np.arange(0, 40)
VALIDATION_ROWS = np.arange(40, 60)


def _dataset(n: int) -> TensorDataset:
    return TensorDataset(torch.zeros(n, 2), torch.zeros(n))


def _real_loader(rows, arm, scaler, shuffle):
    """A real DataLoader with the E11 convention, including persistent workers.

    shuffle      -> dedicated generator, isolated from the global RNG
    not shuffle  -> generator=None, so its iterator draws from the GLOBAL RNG

    `persistent_workers=True` is load-bearing and is why the ATTEMPT 1 defect
    was possible at all: with it, a loader creates its iterator -- and takes its
    one `base_seed` draw -- exactly once, no matter how many epochs iterate it.
    With `num_workers=0` a fresh iterator is built on every `iter()` call, so
    sharing a loader costs no draws and the defect cannot reproduce.
    """
    generator = torch.Generator().manual_seed(2026) if shuffle else None
    return DataLoader(
        _dataset(int(np.asarray(rows).size)),
        batch_size=8,
        shuffle=shuffle,
        num_workers=1,
        persistent_workers=True,
        generator=generator,
    )


def _cache() -> FitScopedLoaderCache:
    validation_start = int(VALIDATION_ROWS[0])
    return FitScopedLoaderCache(
        build=_real_loader,
        is_validation=lambda rows: int(np.asarray(rows)[0]) == validation_start,
    )


def _run_six_fits(cache: FitScopedLoaderCache) -> list[tuple[object, object]]:
    """Simulate the orchestrator: begin_fit, then train loader, then validation."""
    pairs = []
    for _, arm in E12D_FIT_ORDER:
        cache.begin_fit()
        train = cache(TRAIN_ROWS, arm, (0.0, 1.0) if arm == "B1" else None)
        validation = cache(VALIDATION_ROWS, "B0", None)
        pairs.append((train, validation))
    return pairs


# --------------------------------------------------------------------------
# gate 1: six fits construct six distinct inner-validation loaders
# --------------------------------------------------------------------------


def test_six_fits_build_six_distinct_validation_loaders() -> None:
    cache = _cache()
    pairs = _run_six_fits(cache)
    validation_ids = [id(validation) for _, validation in pairs]
    assert len(pairs) == 6
    assert len(set(validation_ids)) == 6, "a validation loader was shared between fits"


def test_six_fits_build_six_distinct_train_loaders() -> None:
    cache = _cache()
    pairs = _run_six_fits(cache)
    assert len({id(train) for train, _ in pairs}) == 6


def test_audit_reports_no_object_shared_between_fits() -> None:
    cache = _cache()
    _run_six_fits(cache)
    audit = cache.audit()
    assert audit["fits"] == 6
    assert audit["loaders_built"] == 12
    assert audit["train_loaders"] == 6
    assert audit["validation_loaders"] == 6
    assert audit["distinct_objects"] == 12
    assert audit["any_object_shared_between_fits"] is False
    assert set(audit["per_fit_loader_counts"].values()) == {2}


def test_within_a_fit_the_same_loader_is_reused_across_epochs() -> None:
    """Rebuilding per epoch would reset the data-order generator; E11 did not."""
    cache = _cache()
    cache.begin_fit()
    first = cache(TRAIN_ROWS, "B0", None)
    second = cache(TRAIN_ROWS, "B0", None)
    assert first is second


def test_a_new_fit_never_returns_the_previous_fits_loader() -> None:
    cache = _cache()
    cache.begin_fit()
    first = cache(VALIDATION_ROWS, "B0", None)
    cache.begin_fit()
    second = cache(VALIDATION_ROWS, "B0", None)
    assert first is not second


def test_requesting_a_loader_before_begin_fit_is_refused() -> None:
    with pytest.raises(E12dOrchestratorError, match="begin_fit"):
        _cache()(TRAIN_ROWS, "B0", None)


# --------------------------------------------------------------------------
# gate 2: global RNG progression matches the historical construction
# --------------------------------------------------------------------------


def _global_rng_draws_during(fn) -> int:
    """Count how many int64 draws fn takes from the global RNG."""
    torch.manual_seed(2026)
    before = torch.random.get_rng_state()
    fn()
    after = torch.random.get_rng_state()
    if torch.equal(before, after):
        return 0
    # replay: how many single draws reproduce the same end state?
    for count in range(1, 32):
        torch.manual_seed(2026)
        for _ in range(count):
            torch.empty((), dtype=torch.int64).random_()
        if torch.equal(torch.random.get_rng_state(), after):
            return count
    return -1


def test_fresh_per_fit_draws_once_per_fit_from_the_global_rng() -> None:
    """Each fit's unshuffled validation loader must consume exactly one draw."""

    def fresh():
        cache = _cache()
        for _, arm in E12D_FIT_ORDER:
            cache.begin_fit()
            next(iter(cache(TRAIN_ROWS, arm, None)))
            next(iter(cache(VALIDATION_ROWS, "B0", None)))

    assert _global_rng_draws_during(fresh) == 6


def test_the_attempt_1_sharing_pattern_loses_global_rng_draws() -> None:
    """The defect, pinned: one shared validation loader takes one draw, not six."""

    shared: dict[tuple, object] = {}

    def broken():
        for _, arm in E12D_FIT_ORDER:
            key_t = (int(TRAIN_ROWS[0]), TRAIN_ROWS.size, arm)
            if key_t not in shared:
                shared[key_t] = _real_loader(TRAIN_ROWS, arm, None, True)
            # ATTEMPT 1 keyed on rows + arm, and the orchestrator always passes
            # arm="B0" for validation -> both arms of a fold collide on one object
            key_v = (int(VALIDATION_ROWS[0]), VALIDATION_ROWS.size, "B0")
            if key_v not in shared:
                shared[key_v] = _real_loader(VALIDATION_ROWS, "B0", None, False)
            next(iter(shared[key_t]))
            next(iter(shared[key_v]))

    draws = _global_rng_draws_during(broken)
    assert draws < 6, (
        "the ATTEMPT 1 pattern must consume FEWER global draws than the correct "
        f"construction; got {draws}"
    )
    assert draws == 1, (
        f"one shared validation loader should take exactly one draw, got {draws}"
    )


def test_train_loader_is_built_before_the_validation_loader_in_every_fit() -> None:
    """The frozen historical order: train loader, then inner-validation loader."""
    cache = _cache()
    _run_six_fits(cache)
    for fit_index in range(6):
        records = [r for r in cache.built if r["fit_index"] == fit_index]
        assert len(records) == 2
        assert records[0]["shuffle"] is True, "train loader must be built first"
        assert records[1]["shuffle"] is False, "validation loader must be built second"


def test_b0_and_b1_fits_follow_the_same_construction_sequence() -> None:
    cache = _cache()
    _run_six_fits(cache)
    shapes = [
        tuple(r["shuffle"] for r in cache.built if r["fit_index"] == i)
        for i in range(6)
    ]
    assert shapes == [(True, False)] * 6
    arms = [r["arm"] for r in cache.built if r["shuffle"]]
    assert arms == [arm for _, arm in E12D_FIT_ORDER]
