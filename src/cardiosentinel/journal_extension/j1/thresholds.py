"""Fold-specific numeric threshold derivation, protocol section 5.4.

A candidate ID fixes rule structure and quantile level(s). Its numeric
thresholds are **fold-specific FIT-derived quantities**, so they belong here and
not in the registry.

**The population rule, §5.4.** Every threshold used to evaluate a candidate on
`INNER_HELDOUT_j` is derived only from `INNER_FIT_j`, using the inherited T1
threshold-population principle: PRIMARY, background-negative, scored rows, from
the fit subjects only. No inner-held-out row contributes to its own threshold.
The fit population is therefore an explicit argument and membership is checked,
not assumed from the rows handed in.

**Why the order statistic is re-implemented rather than imported.** §5.4 says to
preserve the inherited empirical-order-statistic method, and
`t1_protocol.empirical_order_statistic` is that method. But `t1_protocol`'s
operating-point entry points are forbidden to J1 by name -- T1/W1 were developed
on the 12 VALIDATION subjects, which J1 may not reopen, and a J1 module reaching
`candidate_policies`, `policy_sort_key`, `next_state` or
`empirical_order_statistic` is a `v1_validation_operating_point_resolution`.
Read together, the two frozen constraints admit exactly one implementation: the
same arithmetic, computed inside J1, over J1's own fit population.

So this is a deliberate re-statement of a frozen rule, not a second opinion
about it: `k = ceil(q * N)`, one-based, no interpolation, ties broken by
`stable_id` so the result does not depend on input order. A library quantile
would interpolate between neighbours and would not be reproducible across
versions. `tests/journal_extension` asserts this agrees with the inherited
implementation on shared inputs, which is what keeps the re-statement honest.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Sequence

from .candidates import MemorylessCandidate, StatefulCandidate
from .capability_gate import J1CapabilityAttestation

#: Signal key -> the threshold-population attribute it is drawn from.
SIGNAL_SOURCE: dict[str, str] = {
    "pt": "fit_calibrated_probability",
    "st": "s4d_temporal_evidence_s_t",
    "m2g": "m2g_detector_score",
}


class ThresholdDerivationError(RuntimeError):
    """A threshold population that §5.4 does not admit."""


@dataclass(frozen=True)
class ThresholdRow:
    """One admissible row of a fold's FIT-side threshold population.

    `fit_calibrated_probability` is a fit-side value by construction (§5.3.2).
    It derives thresholds and is never persisted as evidence, which is why this
    field is not named `oof_calibrated_probability_p_t`.
    """

    stable_id: str
    subject_id: str
    is_primary: bool
    is_background_negative: bool
    score_present: bool
    fit_calibrated_probability: float
    s4d_temporal_evidence_s_t: float
    m2g_detector_score: float

    @property
    def admissible(self) -> bool:
        """The inherited T1 threshold-population principle, all three terms."""
        return self.is_primary and self.is_background_negative and self.score_present


def empirical_order_statistic(
    values: Sequence[float], stable_ids: Sequence[str], quantile: float
) -> float:
    """`k = ceil(q * N)`, one-based, no interpolation, ties by `stable_id`."""
    if len(values) != len(stable_ids):
        raise ThresholdDerivationError("values and stable ids must align one to one.")
    if not values:
        raise ThresholdDerivationError(
            "an order statistic needs a non-empty population."
        )
    if not 0.0 < quantile <= 1.0:
        raise ThresholdDerivationError(f"quantile {quantile!r} is outside (0, 1].")
    ordered = sorted(zip(values, stable_ids, strict=True))
    position = math.ceil(quantile * len(ordered))
    return float(ordered[position - 1][0])


def threshold_population(
    rows: Iterable[ThresholdRow], *, fit_subjects: Iterable[str]
) -> tuple[ThresholdRow, ...]:
    """Filter to §5.4's population, refusing any row from outside the fit set.

    A row belonging to a held-out subject is a hard failure rather than a
    silent drop: its presence means the caller assembled the wrong population,
    and quietly discarding it would hide that at exactly the point the
    protocol's guarantee is established.
    """
    permitted = frozenset(fit_subjects)
    if not permitted:
        raise ThresholdDerivationError(
            "a threshold population needs an explicit fit-subject set; without "
            "one there is nothing to prove a row belongs to."
        )
    admissible: list[ThresholdRow] = []
    for row in rows:
        if row.subject_id not in permitted:
            raise ThresholdDerivationError(
                f"row {row.stable_id!r} belongs to {row.subject_id!r}, which is "
                "not in the fit population. No held-out row may contribute to "
                "its own threshold."
            )
        if row.admissible:
            admissible.append(row)
    if not admissible:
        raise ThresholdDerivationError(
            "no PRIMARY, background-negative, scored rows in the fit "
            "population; a threshold cannot be derived from an empty set."
        )
    return tuple(admissible)


def _column(
    rows: tuple[ThresholdRow, ...], attribute: str
) -> tuple[list[float], list[str]]:
    return (
        [float(getattr(row, attribute)) for row in rows],
        [row.stable_id for row in rows],
    )


def _levels_by_signal(candidate: MemorylessCandidate) -> dict[str, float]:
    """One level per named signal, broadcasting the matched-level families.

    Families G and H name three signals at a single frozen level (§6.2), so a
    strict `zip` would silently derive one threshold and leave two missing.
    """
    signals = candidate.signals
    levels = candidate.levels
    if not signals:
        return {}
    if len(levels) == 1 and len(signals) > 1:
        return {signal: float(levels[0]) for signal in signals}
    if len(levels) != len(signals):
        raise ThresholdDerivationError(
            f"candidate {candidate.candidate_id!r} names {len(signals)} signals "
            f"and {len(levels)} levels; they must correspond."
        )
    return {signal: float(level) for signal, level in zip(signals, levels)}


class J1ThresholdDeriver:
    """The `threshold_deriver` collaborator the capability gate requires.

    One `derive` for both arms, because the population rule and the order
    statistic are identical; only which quantities are drawn differs, and that
    is a property of the candidate, not of the caller.
    """

    def j1_execution_capability(self) -> J1CapabilityAttestation:
        return J1CapabilityAttestation(
            collaborator="threshold_deriver",
            execution_capable=True,
            detail="fit-population-only empirical order statistic, k = ceil(qN)",
        )

    def derive(
        self,
        candidate: StatefulCandidate | MemorylessCandidate,
        *,
        rows: Iterable[ThresholdRow],
        fit_subjects: Iterable[str],
    ) -> dict[str, float]:
        """Fold-specific numeric thresholds for one candidate identity."""
        population = threshold_population(rows, fit_subjects=fit_subjects)
        if isinstance(candidate, StatefulCandidate):
            return self._derive_stateful(candidate, population)
        if isinstance(candidate, MemorylessCandidate):
            return self._derive_memoryless(candidate, population)
        raise ThresholdDerivationError(
            f"{type(candidate).__name__} is not a J1 candidate identity."
        )

    def _derive_stateful(
        self, candidate: StatefulCandidate, population: tuple[ThresholdRow, ...]
    ) -> dict[str, float]:
        """§5.4, J1-S: `p_watch`, `s_watch`, `p_event`, `s_event`."""
        probabilities, ids = _column(population, "fit_calibrated_probability")
        temporal, _ = _column(population, "s4d_temporal_evidence_s_t")
        return {
            "p_watch": empirical_order_statistic(probabilities, ids, candidate.q_watch),
            "s_watch": empirical_order_statistic(temporal, ids, candidate.q_watch),
            "p_event": empirical_order_statistic(probabilities, ids, candidate.q_event),
            "s_event": empirical_order_statistic(temporal, ids, candidate.q_event),
        }

    def _derive_memoryless(
        self, candidate: MemorylessCandidate, population: tuple[ThresholdRow, ...]
    ) -> dict[str, float]:
        """§5.4, J1-W: one threshold per continuous signal the rule ID names.

        `d_t` is the inherited binary detector decision and needs no new
        quantile threshold, so a family that reads only `d_t` derives none.
        """
        derived: dict[str, float] = {}
        for signal, level in _levels_by_signal(candidate).items():
            values, ids = _column(population, SIGNAL_SOURCE[signal])
            derived[signal] = empirical_order_statistic(values, ids, level)
        return derived
