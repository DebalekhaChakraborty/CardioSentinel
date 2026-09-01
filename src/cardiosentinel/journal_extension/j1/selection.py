"""The frozen lexicographic selection order, protocol section 6.5.

V1 already froze a complete deterministic order in `t1_protocol.policy_sort_key`,
whose docstring states the purpose: *no fold may be decided by dictionary order
or by a human preference expressed after the numbers were seen.* §6.5 says J1
**preserves** it rather than inventing one.

Preserving it means re-stating it here, for the same reason `thresholds.py`
re-states the order statistic: `policy_sort_key` is one of `t1_protocol`'s
forbidden entry points, because T1/W1 were developed on the 12 VALIDATION
subjects that J1 may not reopen. The rule is inherited; the call is not
available. So the arithmetic is repeated and the frozen *data* it depends on is
imported rather than copied, which is the part that cannot be allowed to drift.

Both arms share terms 1 to 4 — the same quantities, directions and eligibility.
Only the final arbitrary-but-deterministic tie-break differs, because the arms
are parameterised differently.

**The profile tie-break reverses if you take it from the wrong tuple.** J1's
registry enumerates profiles `("FAST", "MED", "SLOW")`, in that order, and V1's
frozen tie-break preference is `T1_PERSISTENCE_PROFILES`, ordered *most cautious
first* — `CONSERVATIVE, BALANCED, FAST`. The two are exact opposites, and both
are tuples of three profile labels that an `.index()` call accepts without
complaint. §6.5 names V1's, so V1's is what this module uses, by importing the
tuple and matching on profile name. A qualification test asserts the mapping,
because the failure is a silently inverted preference among tied candidates and
nothing downstream would look wrong.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from cardiosentinel.neural.t1_protocol import T1_PERSISTENCE_PROFILES

from .candidates import MemorylessCandidate, StatefulCandidate
from .capability_gate import J1CapabilityAttestation

#: J1's registry label -> the inherited T1 profile name it denotes. J1 names the
#: middle profile MED; V1 names it BALANCED. They are the same profile.
PROFILE_ALIASES: dict[str, str] = {
    "FAST": "FAST",
    "MED": "BALANCED",
    "SLOW": "CONSERVATIVE",
}

#: The four shared terms, in frozen rank order, with the direction each takes.
SHARED_TERMS: tuple[tuple[str, str], ...] = (
    ("episode_f1", "maximise"),
    ("window_mcc", "maximise"),
    ("false_onsets_per_hour", "minimise"),
    ("event_exposure_fraction", "minimise"),
)


class SelectionOrderError(RuntimeError):
    """A candidate or a metric set the frozen order cannot rank."""


def persistence_rank(profile: str) -> int:
    """V1's frozen tie-break index for a J1 profile label, most cautious first."""
    try:
        inherited_name = PROFILE_ALIASES[profile]
    except KeyError:
        raise SelectionOrderError(
            f"{profile!r} is not a J1 persistence profile; the frozen set is "
            f"{sorted(PROFILE_ALIASES)}."
        ) from None
    for index, candidate_profile in enumerate(T1_PERSISTENCE_PROFILES):
        if candidate_profile.name == inherited_name:
            return index
    raise SelectionOrderError(
        f"{inherited_name!r} is not among the inherited persistence profiles; "
        "J1's alias table and V1's frozen tuple have diverged."
    )


def _shared_terms(metrics: dict[str, float]) -> tuple[float, ...]:
    """Terms 1 to 4. Maximised terms are negated, because smaller sorts first."""
    missing = [name for name, _ in SHARED_TERMS if name not in metrics]
    if missing:
        raise SelectionOrderError(
            "the frozen selection order needs every term; a missing one would "
            "silently promote the next term to rank 1. Missing: "
            + ", ".join(sorted(missing))
        )
    return (
        -float(metrics["episode_f1"]),
        -float(metrics["window_mcc"]),
        float(metrics["false_onsets_per_hour"]),
        float(metrics["event_exposure_fraction"]),
    )


def stateful_sort_key(
    candidate: StatefulCandidate, metrics: dict[str, float]
) -> tuple[Any, ...]:
    """§6.5 for J1-S: the shared four, then `-q_event`, `-q_watch`, profile."""
    return (
        *_shared_terms(metrics),
        -float(candidate.q_event),
        -float(candidate.q_watch),
        persistence_rank(candidate.profile),
    )


def memoryless_sort_key(
    candidate: MemorylessCandidate, metrics: dict[str, float]
) -> tuple[Any, ...]:
    """§6.5 for J1-W: the shared four, then ascending rule ID.

    The rule ID is fixed at enumeration (§6.2), so this tie-break is decided
    before any number is seen, which is the property §6.5 is protecting.
    """
    return (*_shared_terms(metrics), candidate.candidate_id)


def sort_key(
    candidate: StatefulCandidate | MemorylessCandidate, metrics: dict[str, float]
) -> tuple[Any, ...]:
    if isinstance(candidate, StatefulCandidate):
        return stateful_sort_key(candidate, metrics)
    if isinstance(candidate, MemorylessCandidate):
        return memoryless_sort_key(candidate, metrics)
    raise SelectionOrderError(
        f"{type(candidate).__name__} is not a J1 candidate identity."
    )


@dataclass(frozen=True)
class RankedCandidate:
    """One candidate's place in the frozen order, with the key that put it there."""

    candidate: StatefulCandidate | MemorylessCandidate
    key: tuple[Any, ...]

    @property
    def candidate_id(self) -> str:
        return self.candidate.candidate_id


class J1SelectionRanker:
    """The `selection_ranker` collaborator the capability gate requires.

    One arm at a time. Ranking both registries together would be meaningless --
    §5.7 promotes exactly one J1-S identity and exactly one J1-W identity, from
    the same inner evidence, neither able to see the other's outcome -- and a
    ranker that accepted a mixed pool would make that mistake possible.
    """

    def j1_execution_capability(self) -> J1CapabilityAttestation:
        return J1CapabilityAttestation(
            collaborator="selection_ranker",
            execution_capable=True,
            detail="frozen section 6.5 lexicographic order, inherited tie-break",
        )

    def rank(
        self,
        scored: Iterable[
            tuple[StatefulCandidate | MemorylessCandidate, dict[str, float]]
        ],
    ) -> tuple[RankedCandidate, ...]:
        """Order one arm's candidates. The first is the promoted identity."""
        entries = list(scored)
        if not entries:
            raise SelectionOrderError("nothing to rank; a fold needs candidates.")
        arms = {type(candidate) for candidate, _ in entries}
        if len(arms) > 1:
            raise SelectionOrderError(
                "a single ranking may not mix J1-S and J1-W candidates; the "
                "arms are selected independently."
            )
        seen: set[str] = set()
        for candidate, _ in entries:
            if candidate.candidate_id in seen:
                raise SelectionOrderError(
                    f"{candidate.candidate_id!r} appears twice; a candidate "
                    "identity is ranked once."
                )
            seen.add(candidate.candidate_id)
        ranked = [
            RankedCandidate(candidate=candidate, key=sort_key(candidate, metrics))
            for candidate, metrics in entries
        ]
        ranked.sort(key=lambda entry: entry.key)
        return tuple(ranked)
