"""The runtime a V2 dependency authority governs — and the gate that refuses it.

`approved_runtime` answers *"is this the environment V1's scaffold was built
in?"*. That question has exactly one right answer and it is a historical fact.
It is not the question a V2 runtime asks.

**V2 is a new isolated environment with its own explicit authority.** The
programme's environment boundary says V1 is archival and reproduce-only, and
that V2 does not mutate it. So a V2 runtime that fails V1's gate is not a
defect: it is the boundary working. PR #165 demonstrated exactly that, and
recorded it as a blocker because the only gate J1 had was V1's.

Two concepts, kept apart on purpose:

```text
V1 historical runtime   CPython-3.12.6, Linux-x86_64, 335 recorded packages
                        digest b0fd6eaa...            approved_runtime
                        immutable evidence; reproduce-only

V2 governed runtime     47 governed external distributions + first-party source
                        checked against an authority the caller supplies
                        this module
```

---

## Why this module refuses to find its own authority

Nothing here is discovered. There is no default authority path, no search of
whichever files happen to exist, and no repository root inferred from
`__file__`. Every entry point takes the authority as an argument, because an
apparatus that can locate its own authority can also locate the wrong one, and
because the previous generation of this code was made unimportable by exactly
that habit.

## Why a candidate is not an authority

`qualify_v2_dependency_candidate` accepts an object marked `CANDIDATE_ONLY` and
`NOT_AUTHORIZED`, because its whole purpose is to exercise the apparatus before
anyone has decided anything. It returns `QUALIFICATION_ONLY` and says so.

`require_authorized_v2_runtime` refuses that same object. No human has performed
a dependency-authority act, so there is nothing for it to accept, and being able
to parse a candidate is not the same as being entitled to run under it.

## Why `pip` does not change the answer

V1's digest hashes every installed distribution, `pip` included -- and `pip` is
one of the historical 335. That is correct for V1, whose question is *what was
installed*. It is wrong for V2, whose question is *are the governed scientific
dependencies exactly what the authority names*. Two bootstraps shipping pip 24.2
and pip 26.2.1 are the same governed runtime, and PR #165's network-sealed
replay differed in precisely that way.

Substrate is excluded from the governed identity and **reported separately**.
It is not ignored: anything installed that the authority does not govern, that
is not first-party, and that is not on the substrate allowlist is a refusal.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

#: Distributions a Python bootstrap may contribute without being governed.
#: `pip` is what the PR #165 clean rooms actually carried. This is a documented
#: default, not a permanent assumption: a base image that demonstrably ships a
#: different bootstrap gets a different allowlist passed in, and the value used
#: is recorded in every receipt.
DEFAULT_SUBSTRATE_ALLOWLIST: Final[tuple[str, ...]] = ("pip",)

#: The status a candidate object carries before any human authority act.
CANDIDATE_STATUS: Final = "CANDIDATE_ONLY"
CANDIDATE_AUTHORIZATION_STATUS: Final = "NOT_AUTHORIZED"

#: The only value that makes an object a production authority. No object in the
#: repository carries it, and this task does not create one.
AUTHORIZED_STATUS: Final = "AUTHORIZED"

#: Canonical form of the governed inventory digest, recorded so a reader can
#: recompute it without reading this file.
GOVERNED_INVENTORY_DIGEST_METHOD: Final = (
    'sha256(json.dumps([{"name": n, "version": v}, ...], sort_keys=True, '
    'separators=(",", ":")).encode("utf-8")) over authority-governed external '
    "distributions only, PEP 503 normalized, sorted by name"
)

_NORMALIZE = re.compile(r"[-_.]+")


class V2RuntimeAuthorityError(RuntimeError):
    """The running environment is not what the supplied V2 authority governs."""


class V2AuthorityNotAuthorizedError(V2RuntimeAuthorityError):
    """The object supplied is a candidate. No human has authorized it."""


def normalize(name: str) -> str:
    """PEP 503 normalization. Collapses `-`, `_` and `.` alike."""
    return _NORMALIZE.sub("-", name).lower()


# --------------------------------------------------------------- authority ---
@dataclass(frozen=True)
class GovernedAuthority:
    """The part of a V2 authority object this module is entitled to act on."""

    identifier: str
    digest: str
    status: str
    authorization_status: str
    governed_versions: dict[str, str]
    first_party: dict[str, Any]
    artifact_manifest_digest: str | None
    wheelhouse_manifest_digest: str | None
    target_python: dict[str, Any]
    target_platform: dict[str, Any]

    @property
    def governed_names(self) -> frozenset[str]:
        return frozenset(self.governed_versions)

    @property
    def is_authorized(self) -> bool:
        return self.authorization_status == AUTHORIZED_STATUS


def load_authority_document(path: Path) -> dict[str, Any]:
    """Read an authority or candidate object. Explicit path; nothing is searched."""
    if path is None:
        raise V2RuntimeAuthorityError(
            "no authority path was supplied. This module does not look for an "
            "authority; a caller that cannot name one does not get a default."
        )
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_governed_authority(
    document: dict[str, Any],
    *,
    manifest: dict[str, Any] | None = None,
) -> GovernedAuthority:
    """Project an authority/candidate object onto what the gate needs.

    The governed external versions come from the artifact manifest when one is
    supplied, because the manifest is where exact versions and artifact bindings
    live. Without it, the candidate's own package list is used and the artifact
    digests are recorded as absent rather than invented.
    """
    for required in ("status", "authorization_status"):
        if required not in document:
            raise V2RuntimeAuthorityError(
                f"the supplied object carries no {required!r}. An object that "
                "does not say whether it is authorized is not one this gate may "
                "interpret."
            )

    if manifest is not None:
        governed = {
            normalize(entry["normalized_name"]): entry["version"]
            for entry in manifest["external_packages"]
        }
        first_party = dict(manifest["first_party_package"])
        artifact_digest = manifest.get("artifact_manifest_digest")
    else:
        names = [
            normalize(name)
            for name in document.get("artifact_derived_packages", [])
            if normalize(name) != "cardiosentinel"
        ]
        governed = dict.fromkeys(names, "")
        first_party = {"normalized_name": "cardiosentinel"}
        artifact_digest = document.get("artifact_manifest_digest")

    identifier = document.get("candidate_id") or document.get("authority_id") or ""
    digest = (
        document.get("candidate_v2_dependency_authority_digest")
        or document.get("dependency_authority_digest")
        or ""
    )
    return GovernedAuthority(
        identifier=identifier,
        digest=digest,
        status=document["status"],
        authorization_status=document["authorization_status"],
        governed_versions=governed,
        first_party=first_party,
        artifact_manifest_digest=artifact_digest,
        wheelhouse_manifest_digest=document.get("candidate_wheelhouse_manifest_digest"),
        target_python=document.get("target_python", {}),
        target_platform=document.get("target_platform", {}),
    )


# ------------------------------------------------------------- observation ---
def observe_installed_distributions() -> dict[str, list[str]]:
    """Every installed distribution, normalized name -> versions found.

    A list, not a string: two distributions normalizing to the same name is a
    condition to report, never one to silently resolve.
    """
    from importlib.metadata import distributions

    observed: dict[str, list[str]] = {}
    for dist in distributions():
        name = dist.metadata["Name"]
        if not name:
            continue
        observed.setdefault(normalize(name), []).append(dist.version)
    return observed


def governed_dependency_inventory_digest(
    authority: GovernedAuthority,
    observed: dict[str, list[str]] | None = None,
) -> str:
    """A deterministic digest over the governed scientific distributions only.

    **Weaker than artifact-byte authority, and named so.** An installed
    name/version inventory says which distributions are present, never which
    bytes arrived. The byte claim lives in the artifact manifest, the wheelhouse
    manifest and the hash-locked requirements, and this digest does not stand in
    for any of them.
    """
    observed = observe_installed_distributions() if observed is None else observed
    rows = []
    for name in sorted(authority.governed_names):
        versions = observed.get(name, [])
        exact = versions[0] if len(versions) == 1 else ""
        rows.append({"name": name, "version": exact})
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------- qualification ---
@dataclass(frozen=True)
class QualificationResult:
    """What a clean-room environment was observed to be. Never an authorization."""

    result: str
    classification: str = "QUALIFICATION_ONLY"
    authority_identifier: str = ""
    authority_digest: str = ""
    authority_status: str = ""
    authority_authorization_status: str = ""
    governed_package_count: int = 0
    governed_dependency_inventory_digest: str = ""
    substrate_inventory: dict[str, str] = field(default_factory=dict)
    substrate_allowlist: tuple[str, ...] = ()
    first_party_observed_version: str | None = None
    missing: tuple[str, ...] = ()
    version_mismatches: tuple[tuple[str, str, str], ...] = ()
    duplicated: tuple[str, ...] = ()
    ungoverned: tuple[str, ...] = ()
    refusals: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return self.result == "PASS"


def qualify_v2_dependency_candidate(
    document: dict[str, Any],
    *,
    manifest: dict[str, Any] | None = None,
    observed: dict[str, list[str]] | None = None,
    substrate_allowlist: tuple[str, ...] = DEFAULT_SUBSTRATE_ALLOWLIST,
) -> QualificationResult:
    """Exercise the apparatus against a candidate. Never an authorization.

    Accepts `CANDIDATE_ONLY` / `NOT_AUTHORIZED` deliberately -- qualification
    exists to test the machinery before anyone has decided anything. The result
    is `QUALIFICATION_ONLY` and carries no authorization of any kind.
    """
    authority = read_governed_authority(document, manifest=manifest)
    observed = observe_installed_distributions() if observed is None else observed

    missing: list[str] = []
    mismatches: list[tuple[str, str, str]] = []
    duplicated: list[str] = []

    for name in sorted(authority.governed_names):
        versions = observed.get(name)
        if not versions:
            missing.append(name)
            continue
        if len(versions) > 1:
            duplicated.append(name)
            continue
        expected = authority.governed_versions[name]
        if expected and versions[0] != expected:
            mismatches.append((name, expected, versions[0]))

    first_party_name = normalize(
        authority.first_party.get("normalized_name", "cardiosentinel")
    )
    first_party_versions = observed.get(first_party_name, [])

    allow = {normalize(n) for n in substrate_allowlist}
    substrate: dict[str, str] = {}
    ungoverned: list[str] = []
    for name in sorted(observed):
        if name in authority.governed_names or name == first_party_name:
            continue
        if name in allow:
            found = observed[name]
            substrate[name] = found[0] if len(found) == 1 else "AMBIGUOUS"
        else:
            ungoverned.append(name)

    refusals: list[str] = []
    if missing:
        refusals.append(f"governed member absent: {', '.join(missing)}")
    if mismatches:
        detail = ", ".join(f"{n} expected {e} observed {o}" for n, e, o in mismatches)
        refusals.append(f"governed version disagrees with authority: {detail}")
    if duplicated:
        refusals.append(
            f"governed member installed more than once: {', '.join(duplicated)}"
        )
    if ungoverned:
        refusals.append(
            "installed but neither governed, first-party, nor allowed substrate: "
            + ", ".join(ungoverned)
        )
    if not first_party_versions:
        refusals.append(f"first-party distribution {first_party_name} is not installed")

    return QualificationResult(
        result="PASS" if not refusals else "REFUSED",
        authority_identifier=authority.identifier,
        authority_digest=authority.digest,
        authority_status=authority.status,
        authority_authorization_status=authority.authorization_status,
        governed_package_count=len(authority.governed_names),
        governed_dependency_inventory_digest=governed_dependency_inventory_digest(
            authority, observed
        ),
        substrate_inventory=substrate,
        substrate_allowlist=tuple(substrate_allowlist),
        first_party_observed_version=(
            first_party_versions[0] if len(first_party_versions) == 1 else None
        ),
        missing=tuple(missing),
        version_mismatches=tuple(mismatches),
        duplicated=tuple(duplicated),
        ungoverned=tuple(ungoverned),
        refusals=tuple(refusals),
    )


def require_authorized_v2_runtime(
    document: dict[str, Any],
    *,
    manifest: dict[str, Any] | None = None,
    observed: dict[str, list[str]] | None = None,
    substrate_allowlist: tuple[str, ...] = DEFAULT_SUBSTRATE_ALLOWLIST,
) -> QualificationResult:
    """The production gate. Refuses anything a human has not authorized.

    Parsing an object is not entitlement to run under it. Until a
    dependency-authority act exists and the object it produces carries
    `AUTHORIZED`, this refuses -- including for a candidate that would otherwise
    qualify perfectly, which is the state the repository is in today.
    """
    authority = read_governed_authority(document, manifest=manifest)
    if not authority.is_authorized:
        raise V2AuthorityNotAuthorizedError(
            "this object is not an authorized V2 dependency authority.\n"
            f"  identifier           : {authority.identifier or '<unnamed>'}\n"
            f"  status               : {authority.status}\n"
            f"  authorization_status : {authority.authorization_status}\n"
            "A candidate becomes an authority through an explicit human "
            "dependency-authority act, never by being parseable, complete, or "
            "correct. No such act exists."
        )
    result = qualify_v2_dependency_candidate(
        document,
        manifest=manifest,
        observed=observed,
        substrate_allowlist=substrate_allowlist,
    )
    if not result.passed:
        raise V2RuntimeAuthorityError(
            "the running environment is not what this authority governs:\n  "
            + "\n  ".join(result.refusals)
        )
    return result


# ---------------------------------------------------------------- receipt ---
def dependency_install_receipt(
    result: QualificationResult,
    *,
    authority: GovernedAuthority,
    hash_locked_requirement_digests: dict[str, str],
    first_party_source_identity: dict[str, Any],
    installation_timestamp: str,
) -> dict[str, Any]:
    """Evidence that a clean-room install matching a candidate was exercised.

    **Not an authority.** It records what was installed and against which
    candidate, and it is data-free: no dataset path, no subject, no metric.
    """
    return {
        "receipt_kind": "J1_V2_DEPENDENCY_INSTALL_RECEIPT",
        "authority_or_candidate_id": result.authority_identifier,
        "authority_or_candidate_digest": result.authority_digest,
        "authority_status": result.authority_status,
        "authority_authorization_status": result.authority_authorization_status,
        "artifact_manifest_digest": authority.artifact_manifest_digest,
        "wheelhouse_manifest_digest": authority.wheelhouse_manifest_digest,
        "hash_locked_requirement_digests": dict(
            sorted(hash_locked_requirement_digests.items())
        ),
        "target_python": authority.target_python,
        "target_platform": authority.target_platform,
        "governed_dependency_inventory_digest": (
            result.governed_dependency_inventory_digest
        ),
        "governed_dependency_inventory_digest_method": GOVERNED_INVENTORY_DIGEST_METHOD,
        "governed_package_count": result.governed_package_count,
        "substrate_inventory": dict(sorted(result.substrate_inventory.items())),
        "substrate_allowlist": list(result.substrate_allowlist),
        "first_party_source_identity": first_party_source_identity,
        "first_party_observed_version": result.first_party_observed_version,
        "installation_timestamp": installation_timestamp,
        "qualification_result": result.result,
        "qualification_only": True,
        "scientific_data_accessed": False,
        "scientific_attempt": False,
    }
