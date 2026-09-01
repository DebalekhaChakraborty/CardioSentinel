"""The J1 authorization schema. This module instantiates nothing.

Authorization is a human act. This file says what that act must contain and
refuses everything that falls short; it does not contain an authorization, and
the repository contains no J1 authorization document.

Every field is required. There are no permissive defaults, because a default is
a decision made by whoever wrote the code rather than by whoever is accountable
for the run. In particular `attempt_budget` has no default: a blank, zero or
unknown budget is a refusal, never "one attempt".
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from .partition_authority import V1_TRAIN_ONLY

REQUIRED_FIELDS: Final = (
    "authorization_id",
    "protocol_sha256",
    "pre_registration_sha256",
    "freeze_receipt_sha256",
    "authorized_execution_git_sha",
    "evidence_class",
    "data_authority",
    "split_sha256",
    "environment_sha256",
    "provenance_sink",
    "attempt_budget",
    "apparatus_after_visibility_authority",
    "authorized_at",
    "human_authorization_identity",
)


class AuthorizationError(RuntimeError):
    """No authorization, or one that does not say what it must say."""


@dataclass(frozen=True)
class J1Authorization:
    """A verified authorization. Only `verify_authorization` may build one."""

    authorization_id: str
    protocol_sha256: str
    pre_registration_sha256: str
    freeze_receipt_sha256: str
    authorized_execution_git_sha: str
    evidence_class: str
    data_authority: str
    split_sha256: str
    environment_sha256: str
    provenance_sink: str
    attempt_budget: int
    apparatus_after_visibility_authority: str
    authorized_at: str
    human_authorization_identity: str

    def as_attestation(self) -> dict[str, object]:
        return {
            "authorization_id": self.authorization_id,
            "authorized_execution_git_sha": self.authorized_execution_git_sha,
            "data_authority": self.data_authority,
            "attempt_budget": self.attempt_budget,
            "human_authorization_identity": self.human_authorization_identity,
        }


def verify_authorization(document: Any) -> J1Authorization:
    """Refuse unless every field is explicitly present and admissible.

    `document` is whatever a future loader produces. `None` -- the repository's
    current state -- is the ordinary case and is refused first.
    """
    if document is None:
        raise AuthorizationError(
            "J1 authorization absent. J1 is PRE-REGISTERED, not AUTHORIZED: no "
            "authorization document exists, and none is created by running this."
        )
    if not isinstance(document, dict):
        raise AuthorizationError(
            f"a J1 authorization must be a mapping of explicit fields, got "
            f"{type(document).__name__}."
        )

    missing = [name for name in REQUIRED_FIELDS if name not in document]
    if missing:
        raise AuthorizationError(
            "J1 authorization is incomplete; no field has a default. Missing: "
            + ", ".join(sorted(missing))
        )
    blank = [
        name
        for name in REQUIRED_FIELDS
        if document[name] is None
        or (isinstance(document[name], str) and not document[name].strip())
    ]
    if blank:
        raise AuthorizationError(
            "a blank J1 authorization field is a refusal, not a permissive "
            "default. Blank: " + ", ".join(sorted(blank))
        )

    budget = document["attempt_budget"]
    if not isinstance(budget, int) or isinstance(budget, bool) or budget < 1:
        raise AuthorizationError(
            f"attempt_budget must be an explicit integer of at least 1, got "
            f"{budget!r}. A zero, blank or unknown budget is never read as one "
            "attempt."
        )
    if document["data_authority"] != V1_TRAIN_ONLY:
        raise AuthorizationError(
            "J1's permitted physiological partition is "
            f"{V1_TRAIN_ONLY}; the authorization names "
            f"{document['data_authority']!r}."
        )
    if document["evidence_class"] != "V2_DEVELOPMENT":
        raise AuthorizationError(
            "J1 produces V2_DEVELOPMENT evidence; the authorization names "
            f"{document['evidence_class']!r}."
        )
    return J1Authorization(**{name: document[name] for name in REQUIRED_FIELDS})
