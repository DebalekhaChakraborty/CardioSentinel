"""Which build pair counts as qualification, and where its evidence lives.

The #151 review found that the builder authorization controls *what* may be
built and not *which* BUILD_A/BUILD_B pair constitutes qualification. Under
`workflow_dispatch` an authorized workflow may be invoked any number of times,
so without a rule the evidence is whichever pair someone chose to keep -- and
choosing between candidate pairs after seeing their digests is precisely the
decision the two-build procedure exists to prevent being made quietly.

**What this module is, stated plainly.** It is a *detection* control, not a
prevention control, and the distinction is not a technicality.

Nothing here stops a second dispatch. GitHub Actions, under
`permissions: contents: read` and with no credentials, offers this repository no
persistent, race-free, runner-writable store in which a first run could place a
lock that a second run would find. The Actions cache is evictable and mutable;
artifacts are deletable; a file written on a runner dies with it. A "lock"
built from any of those would be a process convention wearing the costume of a
technical control, and the programme is worse off with one of those than with
none.

What the provider *does* supply is an immutable, monotonic, provider-assigned
ordering: `run_id`. Nobody can create a run whose id is lower than one that
already exists. So the rule is decidable after the fact and cannot be gamed by
choosing which evidence to keep:

    the canonical qualification run is the earliest run, by provider run
    ordering, that passed the builder authorization gate and recorded a claim

and `require_canonical_qualification_run` refuses any other run's evidence at
the point where it would become durable. A later run may execute; its evidence
simply cannot become the qualification record while an earlier claim exists.

**The residual trust this rests on is already accepted.** The ordering, and the
completeness of the run listing the check reads, are GitHub's. That is inside
the residual trust the builder authorization discloses, and it adds nothing new.
It is stated here so nobody has to rediscover it.

**Nothing in this module builds, dispatches, claims or promotes anything.**
Every function is a rule applied to records supplied by a caller.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Final, Mapping, Sequence

# ---------------------------------------------------------------------------
# Provenance destinations -- transport is not evidence
# ---------------------------------------------------------------------------

#: Where a controlled run puts its outputs so a later step can collect them.
#: GitHub Actions artifact storage: convenient, provider-controlled, and
#: expiring under a retention policy that is an account setting rather than a
#: repository control. It moves bytes; it does not preserve them.
TRANSIENT_BUILD_TRANSPORT: Final = "github_actions_workflow_artifacts"

#: Where the evidence becomes durable: version control, through a reviewed pull
#: request. The repository is the only store in this system whose contents are
#: digest-addressed, reviewable, and not subject to someone else's expiry.
DURABLE_EVIDENCE_STORE: Final = "repository_version_control"

DURABLE_EVIDENCE_ROOT: Final = "docs/journal-extension/j1/evidence/environment-build"

#: Deterministic transient artifact names. A caller may not choose these: a
#: name a caller picks is a name a caller can collide with.
BUILD_A_PROVENANCE_ARTIFACT: Final = "j1-build-a-provenance"
BUILD_B_PROVENANCE_ARTIFACT: Final = "j1-build-b-provenance"
BUILD_A_ARCHIVE_ARTIFACT: Final = "j1-build-a-oci-archive"
BUILD_B_ARCHIVE_ARTIFACT: Final = "j1-build-b-oci-archive"
QUALIFICATION_CLAIM_ARTIFACT: Final = "j1-qualification-claim"
REPRODUCIBILITY_RECORD_ARTIFACT: Final = "j1-reproducibility-record"

#: Every file the durable evidence package must contain before an environment
#: artifact may be considered qualified. A package missing any of these does not
#: establish what it claims to establish.
DURABLE_EVIDENCE_CONTENTS: Final[tuple[str, ...]] = (
    "qualification_claim.json",
    "build_a_provenance.json",
    "build_b_provenance.json",
    "reproducibility.json",
    "build_a.oci.tar.sha256",
    "build_b.oci.tar.sha256",
)

_AUTHORIZATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,63}$")


class QualificationError(RuntimeError):
    """A qualification claim, pair or destination the protocol does not admit."""


def require_authorization_id(builder_authorization_id: str) -> str:
    """The id becomes a path segment, so it must be one -- and only one.

    Refused rather than sanitised. Silently rewriting an identifier produces a
    destination that does not match the authorization that named it.
    """
    if not isinstance(builder_authorization_id, str):
        raise QualificationError(
            "builder_authorization_id must be text, got "
            f"{type(builder_authorization_id).__name__}."
        )
    if not _AUTHORIZATION_ID.match(builder_authorization_id):
        raise QualificationError(
            f"builder_authorization_id={builder_authorization_id!r} is not a "
            "single safe path segment. It must be 3-64 characters of letters, "
            "digits, dot, underscore or hyphen, starting alphanumeric: the "
            "durable evidence destination is derived from it, and a value "
            "carrying a separator would name a directory nobody authorized."
        )
    return builder_authorization_id


def durable_evidence_destination(builder_authorization_id: str) -> str:
    """The exact canonical path this authorization's evidence must land at.

    Mechanically derived from the authorization's own id, so the destination
    cannot be a value someone chose afterwards to suit the evidence.
    """
    identifier = require_authorization_id(builder_authorization_id)
    return f"{DURABLE_EVIDENCE_ROOT}/{identifier}/"


def require_provenance_destination(
    *, declared: str, builder_authorization_id: str
) -> str:
    """Refuse a destination that is not the one this authorization derives.

    `provenance_destination` was BLOCKED in the #151 packet because nothing
    determined it. It is determined now, and determined *by the authorization
    itself*, which is why it can be checked rather than merely declared.
    """
    expected = durable_evidence_destination(builder_authorization_id)
    if declared != expected:
        raise QualificationError(
            "provenance_destination is not the destination this authorization "
            f"derives.\n  declared: {declared!r}\n  derived:  {expected!r}\n"
            "The destination is a function of builder_authorization_id, not a "
            "free choice, so evidence cannot be filed somewhere the "
            "authorization does not name."
        )
    return declared


# ---------------------------------------------------------------------------
# The qualification claim -- recorded before any artifact exists
# ---------------------------------------------------------------------------

QUALIFICATION_POLICY: Final = "FIRST_AUTHORIZED_QUALIFICATION_RUN_IS_CANONICAL"

#: The only policy value the authorization schema accepts. A second policy would
#: mean the rule is a choice, and the rule exists to remove a choice.
PERMITTED_QUALIFICATION_POLICIES: Final[tuple[str, ...]] = (QUALIFICATION_POLICY,)

CLAIM_FIELDS: Final[tuple[str, ...]] = (
    "builder_authorization_id",
    "qualification_policy",
    "provider",
    "workflow_run_id",
    "workflow_run_number",
    "workflow_run_attempt",
    "workflow_sha256",
    "authorized_source_commit",
    "build_configuration_digest",
    "claimed_at",
)

_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_DIGITS = re.compile(r"^[0-9]{1,19}$")


@dataclass(frozen=True)
class QualificationClaim:
    """One run's assertion that it intends to be the qualification pair.

    Made **after** the builder authorization gate passes and **before** any
    artifact-producing step runs. The ordering matters in both directions: a
    claim before the gate would let an unauthorized run reserve the slot, and a
    claim after an artifact exists would let a run decide whether to claim once
    it had seen its own result.
    """

    fields: Mapping[str, Any]

    @property
    def run_id(self) -> int:
        return int(self.fields["workflow_run_id"])

    @property
    def run_attempt(self) -> int:
        return int(self.fields["workflow_run_attempt"])

    @property
    def authorization_id(self) -> str:
        return str(self.fields["builder_authorization_id"])

    @property
    def ordering_key(self) -> tuple[int, int]:
        """Provider-assigned, monotonic, and not writable by a later run.

        `run_attempt` is part of the key because a re-run of an existing run
        keeps its `run_id`. Without it, re-running the canonical run after
        seeing a divergence would produce a second pair indistinguishable from
        the first.
        """
        return (self.run_id, self.run_attempt)

    def as_document(self) -> dict[str, Any]:
        return {name: self.fields[name] for name in CLAIM_FIELDS}


def verify_qualification_claim(document: Any) -> QualificationClaim:
    """Refuse a claim that is incomplete, mistyped, or names another policy."""
    if not isinstance(document, Mapping):
        raise QualificationError(
            "a qualification claim must be a mapping of explicit fields, got "
            f"{type(document).__name__}."
        )
    missing = [name for name in CLAIM_FIELDS if name not in document]
    if missing:
        raise QualificationError(
            "the qualification claim is incomplete; no field has a default. "
            "Missing: " + ", ".join(sorted(missing))
        )
    unknown = [name for name in document if name not in CLAIM_FIELDS]
    if unknown:
        raise QualificationError(
            "the claim carries fields it does not define: "
            + ", ".join(sorted(unknown))
        )
    for name in CLAIM_FIELDS:
        value = document[name]
        if not isinstance(value, (str, int)) or str(value).strip() == "":
            raise QualificationError(f"claim field {name!r} must be explicit.")

    require_authorization_id(str(document["builder_authorization_id"]))
    if document["qualification_policy"] not in PERMITTED_QUALIFICATION_POLICIES:
        raise QualificationError(
            f"qualification_policy={document['qualification_policy']!r} is not "
            f"the frozen policy {QUALIFICATION_POLICY}."
        )
    for name in ("workflow_run_id", "workflow_run_number", "workflow_run_attempt"):
        if not _DIGITS.match(str(document[name])):
            raise QualificationError(
                f"{name}={document[name]!r} is not a provider run number. The "
                "canonical-pair rule orders claims by these values, so a "
                "non-numeric one would make the ordering undecidable."
            )
    if not _SHA256_HEX.match(str(document["workflow_sha256"])):
        raise QualificationError("workflow_sha256 is not a full lowercase SHA-256.")
    if not _SHA256_HEX.match(str(document["build_configuration_digest"])):
        raise QualificationError(
            "build_configuration_digest is not a full lowercase SHA-256."
        )
    if not _GIT_SHA.match(str(document["authorized_source_commit"])):
        raise QualificationError(
            "authorized_source_commit is not a full 40-character commit SHA."
        )
    return QualificationClaim(fields=dict(document))


def require_canonical_qualification_run(
    *, claim: QualificationClaim, observed_claims: Sequence[QualificationClaim]
) -> dict[str, Any]:
    """Refuse evidence from any run but the earliest that claimed.

    Applied where evidence would become durable, not where a build starts. A
    later run is free to execute; what it may not do is have its BUILD_A/BUILD_B
    become the qualification record while an earlier claim under the same
    authorization exists.

    `observed_claims` must be the complete set of claims recorded under this
    authorization, read from the provider's run listing. Supplying a filtered
    subset defeats the check -- which is the honest limitation of a rule whose
    ordering authority is the provider, and is disclosed rather than papered
    over.
    """
    if claim not in observed_claims and claim.ordering_key not in {
        other.ordering_key for other in observed_claims
    }:
        raise QualificationError(
            "the claim under review is absent from the observed claim set, so "
            "the set is not the complete listing this rule requires."
        )
    same_authorization = [
        other
        for other in observed_claims
        if other.authorization_id == claim.authorization_id
    ]
    if not same_authorization:
        raise QualificationError(
            "no claim under this authorization was observed, which cannot be "
            "true of a claim under this authorization."
        )
    earliest = min(same_authorization, key=lambda other: other.ordering_key)
    if earliest.ordering_key != claim.ordering_key:
        raise QualificationError(
            "this is not the canonical qualification run.\n"
            f"  policy:    {QUALIFICATION_POLICY}\n"
            f"  earliest:  run {earliest.run_id} attempt {earliest.run_attempt}\n"
            f"  submitted: run {claim.run_id} attempt {claim.run_attempt}\n"
            "An earlier authorized run already claimed the qualification pair. "
            "Its BUILD_A/BUILD_B evidence stands, and this run's evidence may "
            "not replace it. Selecting between pairs after seeing their digests "
            "is the decision the two-build procedure exists to prevent."
        )
    return {
        "qualification_policy": QUALIFICATION_POLICY,
        "canonical_run_id": claim.run_id,
        "canonical_run_attempt": claim.run_attempt,
        "claims_observed": len(same_authorization),
        "ordering_authority": "provider_assigned_run_id",
        "control_class": "detection_at_evidence_preservation",
    }


# ---------------------------------------------------------------------------
# Failure classes -- frozen before the first failure, on purpose
# ---------------------------------------------------------------------------

#: The run failed before it claimed anything. Nothing was reserved and no
#: artifact existed, so re-dispatching starts a genuinely fresh attempt.
PRE_ARTIFACT_INFRASTRUCTURE: Final = "PRE_ARTIFACT_INFRASTRUCTURE"
#: The claim exists; no artifact digest was produced. The claim stands, so a
#: retry runs under it rather than creating a competing pair.
POST_CLAIM_PRE_ARTIFACT: Final = "POST_CLAIM_PRE_ARTIFACT"
#: At least one artifact digest became visible. From here a retry is a choice
#: informed by a result, so it is never automatic.
ARTIFACT_VISIBLE: Final = "ARTIFACT_VISIBLE"
#: Both builds completed and were compared. The outcome is the outcome.
COMPLETED_QUALIFICATION: Final = "COMPLETED_QUALIFICATION"
#: The run did something the protocol forbids. Never retried; escalated.
PROTOCOL_VIOLATION: Final = "PROTOCOL_VIOLATION"

QUALIFICATION_FAILURE_CLASSES: Final[tuple[str, ...]] = (
    PRE_ARTIFACT_INFRASTRUCTURE,
    POST_CLAIM_PRE_ARTIFACT,
    ARTIFACT_VISIBLE,
    COMPLETED_QUALIFICATION,
    PROTOCOL_VIOLATION,
)

#: Automatic re-dispatch is permitted for exactly one class: the one where
#: nothing has been claimed and nothing has been seen. "Rerun until two images
#: match" is the failure mode this table exists to make unreachable.
AUTOMATIC_RETRY_PERMITTED: Final[Mapping[str, bool]] = {
    PRE_ARTIFACT_INFRASTRUCTURE: True,
    POST_CLAIM_PRE_ARTIFACT: False,
    ARTIFACT_VISIBLE: False,
    COMPLETED_QUALIFICATION: False,
    PROTOCOL_VIOLATION: False,
}


def require_retry_permitted(failure_class: str) -> None:
    """Refuse an automatic retry that would let a run be attempted into agreement."""
    if failure_class not in QUALIFICATION_FAILURE_CLASSES:
        raise QualificationError(
            f"{failure_class!r} is not a declared qualification failure class. "
            "Known: " + ", ".join(QUALIFICATION_FAILURE_CLASSES)
        )
    if not AUTOMATIC_RETRY_PERMITTED[failure_class]:
        raise QualificationError(
            f"automatic retry is not permitted after {failure_class}. "
            "Once an artifact digest has been seen, a retry is a decision taken "
            "with knowledge of a result: if the canonical run reached artifact "
            "visibility and diverged, the divergence is the finding. Promote "
            "neither digest, do not rebuild until two agree, and do not "
            "reclassify. A further attempt requires human review and, where the "
            "inputs change, a new authorization and qualification lineage."
        )


def classify_divergence(*, build_a_digest: str, build_b_digest: str) -> str:
    """Name what happened. It does not decide what to do about it."""
    if build_a_digest == build_b_digest:
        return COMPLETED_QUALIFICATION
    return ARTIFACT_VISIBLE
