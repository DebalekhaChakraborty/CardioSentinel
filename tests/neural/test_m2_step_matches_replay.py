"""`m2_policy.step` is the frozen M2 order, and `replay_stream` is a loop over it.

The batch research path and the streaming edge runtime now share one
implementation of that order. This pins the property that made the extraction
safe: driving `step` by hand, threading the state, produces exactly what
`replay_stream` produces -- values, gate decisions, counters and refractory
alike.

If someone reintroduces a second copy of the ordering, this test does not catch
it. What it catches is the two paths disagreeing, which is the failure that
would actually corrupt a demo: an alert whose gate provenance does not match
what the research pipeline would have recorded for the same row.
"""

from __future__ import annotations

import numpy as np
import pytest

from cardiosentinel.neural import m2_policy as P
from cardiosentinel.neural.m2_gate import G3_SQI_COLUMNS
from cardiosentinel.neural.patient_memory import M1DistanceStandardizer

DIM = P.REPRESENTATION_DIM


def standardizer() -> M1DistanceStandardizer:
    return M1DistanceStandardizer(
        means=tuple(0.0 for _ in range(DIM)),
        scales=tuple(1.0 for _ in range(DIM)),
        prior=tuple(0.0 for _ in range(DIM)),
        zero_variance_dimensions=(),
        fitted_rows=1000,
        fitted_population="synthetic_fixture",
        input_identities={"fixture": True},
    )


def scorer(representation: np.ndarray, d_long: float) -> float:
    """A deterministic stand-in for the frozen M1L head.

    Real numpy in, real float out, varying with **both** arguments so the
    ordering under test -- `d_long` computed against the pre-update prototype
    *before* the score -- is exercised rather than incidentally satisfied.

    Calibrated against the real gate rather than chosen arbitrarily. G4 admits
    a row into the patient baseline only when its score is **below**
    `NORMAL_EVIDENCE_THRESHOLD` (~3e-4): contamination-safety means an abnormal
    window must not move "this patient's normal". A fixture scoring ~0.75
    everywhere would therefore admit nothing and make the equivalence test
    vacuous, which is exactly what the first version of this file did.
    """
    magnitude = float(np.mean(np.abs(representation)))
    return float(1.0 / (1.0 + np.exp(-(12.0 * magnitude - 18.0 + d_long))))


def rows(
    count: int = 40,
    *,
    unavailable_at: tuple[int, ...] = (7, 8, 19),
    elevated_at: tuple[int, ...] = (12, 13, 14, 27, 28),
):
    """A stream with normal rows, elevated rows, and unavailable rows.

    Normal rows score below the G4 threshold and are admitted. Elevated rows
    score above it, are refused, and arm the 60 s refractory -- which then
    suppresses the rows following them. All three paths matter.
    """
    generator = np.random.default_rng(2026)
    out = []
    for index in range(count):
        available = index not in unavailable_at
        scale = 2.0 if index in elevated_at else 0.55
        out.append(
            P.M2TimelineRow(
                record_id="s20041",
                channel_index=0,
                start_sample=index * 1250,
                observation_state=(
                    P.OBSERVATION_AVAILABLE
                    if available
                    else P.OBSERVATION_UNAVAILABLE_EXACT_FLAT
                ),
                representation=(
                    generator.normal(size=DIM) * scale if available else None
                ),
                finite_sample_fraction=1.0 if available else None,
                sqi={column: 0.0 for column in G3_SQI_COLUMNS},
                morphology_valid=1.0,
            )
        )
    return out


@pytest.mark.parametrize("arm", ["M2-G", "M2-0"])
def test_stepping_by_hand_reproduces_replay_stream(arm):
    """The property the extraction rests on, for both arms."""
    sequence = rows()
    transform = standardizer()

    batch = P.replay_stream(
        sequence, arm=arm, standardizer=transform, scorer=scorer
    )

    state = P.M2StreamState.cold_start(transform.prior_vector(), arm=arm)
    streamed = [
        P.step(state, row, arm=arm, standardizer=transform, scorer=scorer)
        for row in sequence
    ]

    assert len(batch) == len(streamed) == len(sequence)
    for index, (expected, actual) in enumerate(zip(batch, streamed, strict=True)):
        assert actual.as_dict() == expected.as_dict(), f"row {index} diverged"


def test_the_order_is_exercised_not_merely_satisfied():
    """Guard the guard: the fixture must actually admit and re-arm.

    A stream where nothing is ever admitted and no refractory ever arms would
    make the test above pass vacuously.
    """
    transform = standardizer()
    evidence = P.replay_stream(
        rows(), arm="M2-G", standardizer=transform, scorer=scorer
    )
    assert any(item.update_admitted for item in evidence), "no update was admitted"
    assert any(
        not item.update_admitted and item.decision.score is not None
        for item in evidence
    ), "no scored row was refused"
    assert any(
        item.refractory_rearmed_after_decision for item in evidence
    ), "the refractory never armed"
    assert any(
        not item.decision.g5_not_in_refractory for item in evidence
    ), "no row was suppressed by an armed refractory"
    assert any(
        item.observation_state != P.OBSERVATION_AVAILABLE for item in evidence
    ), "no unavailable row was exercised"
    scored = [item for item in evidence if item.decision.score is not None]
    assert len(scored) >= 30, "too few scored rows to exercise the ordering"


def test_step_mutates_the_state_it_is_given():
    """Streaming depends on this: the caller owns the state across windows."""
    transform = standardizer()
    state = P.M2StreamState.cold_start(transform.prior_vector(), arm="M2-G")
    before = int(state.past_observed_count)
    P.step(state, rows(1)[0], arm="M2-G", standardizer=transform, scorer=scorer)
    assert state.past_observed_count == before + 1
