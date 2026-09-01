"""Qualification of the frozen J1 selection order, protocol section 6.5.

NON-SCIENTIFIC QUALIFICATION FIXTURE. Every metric below is fabricated. No fold,
no real candidate evidence, and nothing here selects anything for J1.
"""

from __future__ import annotations

import pytest

from cardiosentinel.journal_extension.j1.candidates import (
    PERSISTENCE_PROFILES,
    MemorylessCandidate,
    StatefulCandidate,
    memoryless_registry,
    stateful_registry,
)
from cardiosentinel.journal_extension.j1.selection import (
    PROFILE_ALIASES,
    J1SelectionRanker,
    SelectionOrderError,
    memoryless_sort_key,
    persistence_rank,
    stateful_sort_key,
)

BASE = {
    "episode_f1": 0.50,
    "window_mcc": 0.40,
    "false_onsets_per_hour": 2.0,
    "event_exposure_fraction": 0.10,
}


def _metrics(**overrides: float) -> dict[str, float]:
    out = dict(BASE)
    out.update(overrides)
    return out


# -- the profile tie-break, which reverses if taken from the wrong tuple ----


def test_the_profile_tie_break_follows_v1_most_cautious_first() -> None:
    """SLOW before MED before FAST. J1's own registry tuple is the reverse."""
    assert persistence_rank("SLOW") < persistence_rank("MED")
    assert persistence_rank("MED") < persistence_rank("FAST")


def test_the_registry_enumeration_order_is_not_the_tie_break_order() -> None:
    """The trap this module exists to avoid, asserted rather than described.

    Both tuples hold three profile labels and both accept `.index()`. Taking
    the tie-break from the enumeration tuple would invert the preference among
    tied candidates, and nothing downstream would look wrong.
    """
    enumeration = [PERSISTENCE_PROFILES.index(p) for p in ("SLOW", "MED", "FAST")]
    frozen = [persistence_rank(p) for p in ("SLOW", "MED", "FAST")]
    assert enumeration == sorted(enumeration, reverse=True)
    assert frozen == sorted(frozen)
    assert enumeration != frozen


def test_the_alias_table_matches_the_inherited_frozen_tuple() -> None:
    from cardiosentinel.neural.t1_protocol import T1_PERSISTENCE_PROFILES

    inherited = [profile.name for profile in T1_PERSISTENCE_PROFILES]
    assert sorted(PROFILE_ALIASES.values()) == sorted(inherited)
    for label, name in PROFILE_ALIASES.items():
        assert persistence_rank(label) == inherited.index(name)


def test_an_unknown_profile_is_refused() -> None:
    with pytest.raises(SelectionOrderError, match="not a J1 persistence profile"):
        persistence_rank("MEDIUM")


# -- the four shared terms -------------------------------------------------


def test_the_shared_terms_rank_before_any_arm_specific_term() -> None:
    candidate = StatefulCandidate(q_watch=0.90, q_event=0.99, profile="FAST")
    better = stateful_sort_key(candidate, _metrics(episode_f1=0.80))
    worse = stateful_sort_key(candidate, _metrics(episode_f1=0.10))
    assert better < worse


@pytest.mark.parametrize(
    "term,better,worse",
    [
        ("episode_f1", 0.9, 0.1),
        ("window_mcc", 0.9, 0.1),
        ("false_onsets_per_hour", 0.5, 9.0),
        ("event_exposure_fraction", 0.01, 0.90),
    ],
)
def test_each_term_points_the_frozen_direction(
    term: str, better: float, worse: float
) -> None:
    candidate = MemorylessCandidate("A", ("pt",), (0.9,))
    assert memoryless_sort_key(candidate, _metrics(**{term: better})) < (
        memoryless_sort_key(candidate, _metrics(**{term: worse}))
    )


def test_a_missing_term_is_refused_rather_than_defaulted() -> None:
    """A default would silently promote the next term to rank 1."""
    incomplete = {k: v for k, v in BASE.items() if k != "window_mcc"}
    with pytest.raises(SelectionOrderError, match="Missing: window_mcc"):
        memoryless_sort_key(MemorylessCandidate("A", ("pt",), (0.9,)), incomplete)


# -- arm-specific tie-breaks -----------------------------------------------


def test_the_stateful_tie_break_prefers_the_higher_quantiles_then_caution() -> None:
    tied = _metrics()
    ranked = J1SelectionRanker().rank(
        (candidate, tied) for candidate in stateful_registry()
    )
    first = ranked[0].candidate
    assert isinstance(first, StatefulCandidate)
    assert first.q_event == max(c.q_event for c in stateful_registry())
    assert first.q_watch == max(
        c.q_watch for c in stateful_registry() if c.q_event == first.q_event
    )
    assert first.profile == "SLOW"


def test_the_memoryless_tie_break_is_the_ascending_rule_id() -> None:
    tied = _metrics()
    ranked = J1SelectionRanker().rank(
        (candidate, tied) for candidate in memoryless_registry()
    )
    ids = [entry.candidate_id for entry in ranked]
    assert ids == sorted(ids)


def test_ranking_is_independent_of_input_order() -> None:
    registry = list(stateful_registry())
    scored = [(c, _metrics(episode_f1=0.5)) for c in registry]
    forward = [e.candidate_id for e in J1SelectionRanker().rank(scored)]
    backward = [e.candidate_id for e in J1SelectionRanker().rank(scored[::-1])]
    assert forward == backward


# -- what the ranker refuses ------------------------------------------------


def test_the_two_arms_may_not_be_ranked_together() -> None:
    """Section 5.7 promotes one identity per arm, selected independently."""
    mixed = [
        (StatefulCandidate(q_watch=0.90, q_event=0.99, profile="FAST"), _metrics()),
        (MemorylessCandidate("A", ("pt",), (0.9,)), _metrics()),
    ]
    with pytest.raises(SelectionOrderError, match="may not mix"):
        J1SelectionRanker().rank(mixed)


def test_a_repeated_candidate_identity_is_refused() -> None:
    candidate = MemorylessCandidate("A", ("pt",), (0.9,))
    with pytest.raises(SelectionOrderError, match="appears twice"):
        J1SelectionRanker().rank([(candidate, _metrics()), (candidate, _metrics())])


def test_an_empty_pool_is_refused() -> None:
    with pytest.raises(SelectionOrderError, match="needs candidates"):
        J1SelectionRanker().rank([])


def test_the_ranker_attests_execution_capability() -> None:
    attestation = J1SelectionRanker().j1_execution_capability()
    assert attestation.execution_capable is True
    assert attestation.collaborator == "selection_ranker"
