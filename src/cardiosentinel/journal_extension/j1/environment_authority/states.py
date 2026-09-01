"""The environment authority state ladder.

    CANDIDATE -> QUALIFIED -> AUTHORIZED

A local machine may *generate* a candidate record. It cannot promote itself:
`QUALIFIED` is reached by passing verification, and `AUTHORIZED` only by a human
authorization naming the digest. There is no transition function to AUTHORIZED
in this package, because that transition is not code's to make.
"""

from __future__ import annotations

from enum import Enum


class EnvironmentAuthorityState(str, Enum):
    """Three states. Only the first two are reachable from here."""

    CANDIDATE = "CANDIDATE"
    QUALIFIED = "QUALIFIED"
    AUTHORIZED = "AUTHORIZED"

    @classmethod
    def reachable_without_human_authorization(
        cls,
    ) -> tuple[EnvironmentAuthorityState, ...]:
        return (cls.CANDIDATE, cls.QUALIFIED)
