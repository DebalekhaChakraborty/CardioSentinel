"""Primary endpoint, percentile bootstrap and Gate A, all frozen.

Protocol section 7.1.0 fixes the interval construction, and the quantile
convention is inherited rather than chosen: `baseline/metrics.py` already
computes subject-bootstrap bounds with `np.percentile(values, 2.5)` and `97.5`,
so J1 uses the same call and therefore numpy's default `method="linear"`.

This is a percentile bootstrap over the frozen subject set. It is not a
population confidence interval, and no significance or p-value language attaches
to it.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

BOOTSTRAP_REPLICATES = 1000
BOOTSTRAP_SEED = 2026
LOWER_PERCENTILE = 2.5
UPPER_PERCENTILE = 97.5


class EndpointError(RuntimeError):
    """A cohort or pairing that the frozen endpoint does not admit."""


def episode_f1(matched: int, predicted: int, reference: int) -> float | None:
    """V1's convention, unmodified: `2TP/(2TP+FP+FN)`, None when undefined."""
    denominator = int(predicted) + int(reference)
    if denominator == 0:
        return None
    return 2.0 * int(matched) / denominator


def primary_f1_eligible(reference_episode_count: int) -> bool:
    """Eligibility depends on reference truth alone, never on arm output."""
    return int(reference_episode_count) > 0


@dataclass(frozen=True)
class PairedContrast:
    """The primary estimand and its percentile interval."""

    delta: float
    lower: float
    upper: float
    subjects: int

    def gate_a(self) -> str:
        """Frozen protocol section 9. Direction, plus interval support."""
        if self.delta <= 0:
            return "FAIL"
        return "PASS" if self.lower > 0 else "MIXED"


def paired_contrast(
    stateful: dict[str, float], memoryless: dict[str, float]
) -> PairedContrast:
    """Subject-macro mean paired difference, with the frozen bootstrap.

    Both arms must cover exactly the same subjects: the primary denominator is
    reference-defined, so an arm-dependent subject set would be a different
    estimand.
    """
    if set(stateful) != set(memoryless):
        raise EndpointError(
            "the primary cohort must be identical for both arms; a "
            "prediction-dependent denominator is not a subject-macro average."
        )
    subjects = sorted(stateful)
    if not subjects:
        raise EndpointError("the primary cohort is empty.")
    differences = np.array(
        [stateful[s] - memoryless[s] for s in subjects], dtype=float
    )
    delta = float(differences.mean())

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    n = len(subjects)
    replicates = np.empty(BOOTSTRAP_REPLICATES, dtype=float)
    for i in range(BOOTSTRAP_REPLICATES):
        # Paired: one index draw selects the same subject in both arms.
        picked = rng.integers(0, n, size=n)
        replicates[i] = float(differences[picked].mean())
    valid = replicates[np.isfinite(replicates)]
    return PairedContrast(
        delta=delta,
        lower=float(np.percentile(valid, LOWER_PERCENTILE)),
        upper=float(np.percentile(valid, UPPER_PERCENTILE)),
        subjects=n,
    )
