"""The J1 authorization contract. This module authorizes nothing.

`authorization.py` says what the *execution* schema must contain at the moment
an attempt is claimed. This module says what the **permission boundary** is:
the complete set of fields a future human authorization action must populate,
the rules each one is held to, and the state ladder that action moves along.

**A contract is not a permission.** Nothing here creates an authorization, and
no function in this module returns an `AUTHORIZED` state -- `verify_contract`
returns `DRAFT` and there is no transition function past it, for the same reason
`environment_authority/states.py` has none: that transition is not code's to
make. The repository contains no J1 authorization document, and running any of
this does not create one.

**Why the contract is a superset of the execution schema.** The execution schema
is what preflight must check in the seconds before a claim. The contract is what
a person must decide, days earlier, and includes questions preflight has no
opinion about -- who may declare a result inconclusive, which commit's
collaborator implementations were reviewed. `EXECUTION_SCHEMA_COVERAGE` maps
every execution field to the contract field that carries it, and a qualification
test asserts the map is total, so the two vocabularies cannot drift apart
silently.

**The one place this module deliberately disagrees with preflight.**
`attempt_budget = 0` is a valid contract value and an invalid execution value.
Zero is an explicit human decision -- *authorized, and permitted no attempts* --
which is a different state from a budget that is absent, blank or unknown, and
the difference is exactly what the frozen documents insist must never be
collapsed. So the contract records zero and `permits_attempt` reports `False`;
preflight's own gate still refuses to start a run on a budget below one. A
contract that refused to record zero would leave a person no way to write down
the decision they actually made.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Final, Mapping

from .partition_authority import V1_TRAIN_ONLY

#: Section 1. What science this authorization is over. All immutable.
FROZEN_SCIENTIFIC_IDENTITY_FIELDS: Final[tuple[str, ...]] = (
    "protocol_sha256",
    "preregistration_sha256",
    "freeze_receipt_sha256",
    "execution_instrument_commit",
    "collaborator_implementation_commit",
    "authorized_execution_git_sha",
    "evidence_class",
)

#: Section 2. Which approved runtime. Never the one that happens to be running.
ENVIRONMENT_AUTHORITY_FIELDS: Final[tuple[str, ...]] = (
    "environment_authority_id",
    "environment_sha256",
)

#: Section 3. TRAIN and nothing else.
DATA_AUTHORITY_FIELDS: Final[tuple[str, ...]] = (
    "allowed_partition",
    "train_data_authority_id",
    "train_manifest_digest",
    "split_sha256",
)

#: Section 4. One integer, and no reading of absence as one.
ATTEMPT_BUDGET_FIELDS: Final[tuple[str, ...]] = ("attempt_budget",)

#: Section 5. Where the record goes, chosen by a person, not by the runtime.
PROVENANCE_SINK_FIELDS: Final[tuple[str, ...]] = (
    "provenance_sink_id",
    "provenance_sink_destination",
)

#: Section 6. Who may declare each outcome. Never the runtime.
DECISION_AUTHORITY_FIELDS: Final[tuple[str, ...]] = (
    "scientific_success_authority",
    "scientific_failure_authority",
    "inconclusive_outcome_authority",
    "apparatus_failure_authority",
    "apparatus_after_visibility_authority",
)

#: Section 7. The human act itself.
HUMAN_ACT_FIELDS: Final[tuple[str, ...]] = (
    "authorization_id",
    "authorized_at",
    "human_authorization_identity",
)

CONTRACT_FIELDS: Final[tuple[str, ...]] = (
    *FROZEN_SCIENTIFIC_IDENTITY_FIELDS,
    *ENVIRONMENT_AUTHORITY_FIELDS,
    *DATA_AUTHORITY_FIELDS,
    *ATTEMPT_BUDGET_FIELDS,
    *PROVENANCE_SINK_FIELDS,
    *DECISION_AUTHORITY_FIELDS,
    *HUMAN_ACT_FIELDS,
)

#: Every `authorization.REQUIRED_FIELDS` entry, and the contract field carrying
#: it. Total by test: a new execution field with no contract home is a drift.
EXECUTION_SCHEMA_COVERAGE: Final[dict[str, str]] = {
    "authorization_id": "authorization_id",
    "protocol_sha256": "protocol_sha256",
    "pre_registration_sha256": "preregistration_sha256",
    "freeze_receipt_sha256": "freeze_receipt_sha256",
    "authorized_execution_git_sha": "authorized_execution_git_sha",
    "evidence_class": "evidence_class",
    "data_authority": "allowed_partition",
    "split_sha256": "split_sha256",
    "environment_sha256": "environment_sha256",
    "provenance_sink": "provenance_sink_destination",
    "attempt_budget": "attempt_budget",
    "apparatus_after_visibility_authority": "apparatus_after_visibility_authority",
    "authorized_at": "authorized_at",
    "human_authorization_identity": "human_authorization_identity",
}

#: The evidence class J1 produces. Not a default -- a value that must match.
REQUIRED_EVIDENCE_CLASS: Final = "V2_DEVELOPMENT"

#: Partitions that may not appear anywhere in a J1 authorization, in any field.
FORBIDDEN_PARTITION_TOKENS: Final[tuple[str, ...]] = (
    "validation",
    "v1_test",
    "test_partition",
    "sealed_test",
    "heldout_test",
    "all_subjects",
)

#: Values that describe finding data rather than being given it.
FORBIDDEN_DISCOVERY_TOKENS: Final[tuple[str, ...]] = (
    "discover",
    "autodetect",
    "auto-detect",
    "glob",
    "scan",
    "whatever is present",
)

#: Values naming a machine rather than an approved artifact.
FORBIDDEN_LOCAL_TOKENS: Final[tuple[str, ...]] = (
    "localhost",
    "/home/",
    "/users/",
    "$home",
    "current-machine",
    "developer-laptop",
    "workstation",
    "unbound",
    "unknown",
    "tbd",
    "n/a",
)

#: Values naming the runtime as the decider.
FORBIDDEN_DECIDER_TOKENS: Final[tuple[str, ...]] = (
    "runtime",
    "automatic",
    "the instrument",
    "the pipeline",
    "the code",
    "self",
    "none",
)

#: A destination must be an immutable, non-local reference addressed by scheme.
_SCHEME = re.compile(r"^(?P<scheme>[a-z][a-z0-9+.-]*)://")
FORBIDDEN_SINK_SCHEMES: Final[tuple[str, ...]] = ("file", "http", "ftp")

#: 64 hex for a digest, 40 hex for a git commit. Abbreviations are refused:
#: an authorization names one object, and a prefix names a set of them.
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")

DIGEST_FIELDS: Final[tuple[str, ...]] = (
    "protocol_sha256",
    "preregistration_sha256",
    "freeze_receipt_sha256",
    "environment_sha256",
    "train_manifest_digest",
    "split_sha256",
)

COMMIT_FIELDS: Final[tuple[str, ...]] = (
    "execution_instrument_commit",
    "collaborator_implementation_commit",
    "authorized_execution_git_sha",
)


class AuthorizationContractError(RuntimeError):
    """A contract that cannot serve as a permission boundary."""


class AuthorizationState(str, Enum):
    """The ladder a human authorization moves along.

        ABSENT -> DRAFT -> AUTHORIZED

    `ABSENT` is the repository's current and ordinary state. `DRAFT` is a
    complete, admissible contract that nobody has signed. `AUTHORIZED` is
    reached only by a human act naming the contract, and there is no transition
    function to it anywhere in this package.
    """

    ABSENT = "ABSENT"
    DRAFT = "DRAFT"
    AUTHORIZED = "AUTHORIZED"

    @classmethod
    def reachable_without_human_action(cls) -> tuple[AuthorizationState, ...]:
        return (cls.ABSENT, cls.DRAFT)


def _tokens_in(value: str, tokens: tuple[str, ...]) -> str | None:
    """Substring match. For path- and host-shaped markers, which have no
    word boundaries: `/home/` must match inside a longer path."""
    lowered = value.lower()
    for token in tokens:
        if token in lowered:
            return token
    return None


def _words_in(value: str, tokens: tuple[str, ...]) -> str | None:
    """Whole-word match, for markers that are ordinary English.

    Substring matching here produces false refusals a person cannot work
    around: `self` appears inside `herself`, `none` inside `Nonesuch`, and
    `scan` inside `scanner`. A contract that refuses a real reviewer's name is
    not stricter, it is broken.
    """
    lowered = value.lower()
    for token in tokens:
        if re.search(rf"\b{re.escape(token)}\b", lowered):
            return token
    return None


def _require_text(document: Mapping[str, Any], name: str) -> str:
    value = document[name]
    if not isinstance(value, str) or not value.strip():
        raise AuthorizationContractError(
            f"{name!r} must be explicit text; a blank field is a refusal, not "
            "a permissive default."
        )
    if value != value.strip():
        raise AuthorizationContractError(
            f"{name!r} carries leading or trailing whitespace; an identifier "
            "that differs only by padding is two identifiers."
        )
    return value


def _check_identity(document: Mapping[str, Any]) -> None:
    """Section 1. Exact immutable identifiers, never abbreviations."""
    for name in DIGEST_FIELDS:
        value = _require_text(document, name)
        if not _SHA256.match(value):
            raise AuthorizationContractError(
                f"{name}={value!r} is not a full lowercase SHA-256. An "
                "authorization names one object; a prefix names a set of them."
            )
    for name in COMMIT_FIELDS:
        value = _require_text(document, name)
        if not _GIT_SHA.match(value):
            raise AuthorizationContractError(
                f"{name}={value!r} is not a full 40-character commit SHA. An "
                "abbreviated commit is not an immutable identifier."
            )
    if document["evidence_class"] != REQUIRED_EVIDENCE_CLASS:
        raise AuthorizationContractError(
            f"J1 produces {REQUIRED_EVIDENCE_CLASS} evidence; this contract "
            f"names {document['evidence_class']!r}."
        )


def _check_environment(document: Mapping[str, Any]) -> None:
    """Section 2. The digest names an approved record, not a running machine."""
    for name in ENVIRONMENT_AUTHORITY_FIELDS:
        value = _require_text(document, name)
        marker = _tokens_in(value, FORBIDDEN_LOCAL_TOKENS)
        if marker:
            raise AuthorizationContractError(
                f"{name}={value!r} names mutable local state ({marker!r}). An "
                "environment authority is a qualified record; it cannot be "
                "generated by the execution runtime or inferred from the "
                "machine the runtime happens to be on."
            )


def _check_data_authority(document: Mapping[str, Any]) -> None:
    """Section 3. TRAIN only, supplied, never discovered."""
    partition = _require_text(document, "allowed_partition")
    if partition != V1_TRAIN_ONLY:
        raise AuthorizationContractError(
            f"J1's only permitted partition is {V1_TRAIN_ONLY}; this contract "
            f"names {partition!r}. TRAIN authority does not expand."
        )
    for name in CONTRACT_FIELDS:
        value = document.get(name)
        if not isinstance(value, str):
            continue
        forbidden = _tokens_in(value, FORBIDDEN_PARTITION_TOKENS)
        if forbidden:
            raise AuthorizationContractError(
                f"{name}={value!r} names a forbidden partition ({forbidden!r}). "
                "V1 VALIDATION is historical-only and V1 TEST was consumed; "
                "neither can be reached by any field of an authorization."
            )
        discovery = _words_in(value, FORBIDDEN_DISCOVERY_TOKENS)
        if discovery:
            raise AuthorizationContractError(
                f"{name}={value!r} describes discovering data ({discovery!r}). "
                "The TRAIN manifest is supplied by the authorization and is "
                "never found by the instrument."
            )


def _check_attempt_budget(document: Mapping[str, Any]) -> int:
    """Section 4. Absent refuses. Zero is a decision. Nothing defaults to one."""
    if "attempt_budget" not in document:
        raise AuthorizationContractError(
            "attempt_budget is absent. An absent budget is a refusal and is "
            "never read as one attempt."
        )
    budget = document["attempt_budget"]
    if isinstance(budget, bool) or not isinstance(budget, int):
        raise AuthorizationContractError(
            f"attempt_budget must be an explicit integer, got {budget!r}."
        )
    if budget < 0:
        raise AuthorizationContractError(
            f"attempt_budget must not be negative, got {budget}."
        )
    return budget


def _check_provenance_sink(document: Mapping[str, Any]) -> None:
    """Section 5. An immutable destination, supplied before execution."""
    _require_text(document, "provenance_sink_id")
    destination = _require_text(document, "provenance_sink_destination")
    match = _SCHEME.match(destination)
    if not match:
        raise AuthorizationContractError(
            f"provenance_sink_destination={destination!r} is not an addressed "
            "immutable destination. A bare filesystem path is insufficient "
            "authority: it names a location on one machine, not a durable "
            "destination the record can be found at later."
        )
    scheme = match.group("scheme")
    if scheme in FORBIDDEN_SINK_SCHEMES:
        raise AuthorizationContractError(
            f"provenance_sink_destination uses the {scheme!r} scheme, which "
            "addresses a local or mutable location. The sink must be supplied "
            "before execution and must outlive the machine that writes to it."
        )
    marker = _tokens_in(destination, FORBIDDEN_LOCAL_TOKENS)
    if marker:
        raise AuthorizationContractError(
            f"provenance_sink_destination={destination!r} names mutable local "
            f"state ({marker!r}); the runtime cannot choose its own sink."
        )


def _check_decision_authority(document: Mapping[str, Any]) -> None:
    """Section 6. Four outcomes, each declared by a person."""
    for name in DECISION_AUTHORITY_FIELDS:
        value = _require_text(document, name)
        decider = _words_in(value, FORBIDDEN_DECIDER_TOKENS)
        if decider:
            raise AuthorizationContractError(
                f"{name}={value!r} names {decider!r} as the decider. The "
                "runtime never decides a publication outcome: success, "
                "failure, inconclusive and apparatus failure are declarations "
                "a person makes."
            )


@dataclass(frozen=True)
class J1AuthorizationContract:
    """A complete, admissible contract that nobody has signed.

    Only `verify_contract` builds one, and it is always `DRAFT`. The class
    carries no method, classmethod or field that yields `AUTHORIZED`.
    """

    fields: Mapping[str, Any]
    state: AuthorizationState

    @property
    def attempt_budget(self) -> int:
        return int(self.fields["attempt_budget"])

    @property
    def permits_attempt(self) -> bool:
        """Always `False` for a draft. A contract is not a permission.

        Even a signed authorization permits an attempt only when its budget is
        at least one; a budget of zero is an explicit decision that no attempt
        is authorized, which preflight enforces separately.
        """
        return False

    def as_attestation(self) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "authorization_id": self.fields["authorization_id"],
            "allowed_partition": self.fields["allowed_partition"],
            "attempt_budget": self.attempt_budget,
            "permits_attempt": self.permits_attempt,
            "execution_authorized": False,
        }


def verify_contract(document: Any) -> J1AuthorizationContract:
    """Refuse unless every contract field is present and admissible.

    Returns a `DRAFT`. It never returns `AUTHORIZED`, and there is no argument
    that makes it do so: no `dev_mode`, no `force`, no `skip_checks`, no
    `state` parameter. Signing is a human act performed outside this package.
    """
    if document is None:
        raise AuthorizationContractError(
            "no J1 authorization contract. J1 is PRE-REGISTERED, not "
            "AUTHORIZED: no contract exists, and none is created by running "
            "this."
        )
    if not isinstance(document, Mapping):
        raise AuthorizationContractError(
            "a J1 authorization contract must be a mapping of explicit "
            f"fields, got {type(document).__name__}."
        )
    # The budget is checked for presence before the generic sweep, so an
    # absent budget refuses in its own words. It is the one field whose
    # absence has repeatedly been read as a permissive default, and a generic
    # "missing field" message is the wrong thing to find in that receipt.
    if "attempt_budget" not in document:
        _check_attempt_budget(document)
    missing = [name for name in CONTRACT_FIELDS if name not in document]
    if missing:
        raise AuthorizationContractError(
            "the contract is incomplete; no field has a default. Missing: "
            + ", ".join(sorted(missing))
        )
    unknown = [name for name in document if name not in CONTRACT_FIELDS]
    if unknown:
        raise AuthorizationContractError(
            "the contract carries fields it does not define, which cannot be "
            "held to any rule: " + ", ".join(sorted(unknown))
        )
    _check_attempt_budget(document)
    for name in CONTRACT_FIELDS:
        if name not in ATTEMPT_BUDGET_FIELDS:
            _require_text(document, name)
    _check_identity(document)
    _check_environment(document)
    _check_data_authority(document)
    _check_provenance_sink(document)
    _check_decision_authority(document)
    return J1AuthorizationContract(
        fields=dict(document), state=AuthorizationState.DRAFT
    )
