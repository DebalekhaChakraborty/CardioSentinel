"""The runtime J1 is bound to, established from frozen V1 evidence.

**This was a decision, and it turned out not to be one.** J1 inherits the
B4 / P1 / M1 / M2 / T2 scaffold, and V1's frozen experiment locks record the
environment that scaffold was *built in*: CPython 3.12.6, 335 packages, and a
dependency digest V1 compiled into its own code as a constant and enforced with
`require_exact_scientific_environment`, whose refusal message ends *"Do not
change packages to satisfy this check."*

So J1's approved runtime is not a preference between the two interpreters on
this machine. It is a **fact recovered from frozen evidence**: the scaffold's
nuisance quantities were estimated in that environment, and estimating a
conditional contrast given that scaffold in a different one changes the thing
being conditioned on.

**The CI interpreter is not the scientific interpreter, and never was.** The
repository's continuous integration installs Python 3.11 from unpinned
`pyproject` ranges. That is the right environment for proving the *code* is
correct and the wrong one for producing evidence. Both facts are true at once,
and the green badge on a pull request says nothing about the second.

**Nothing here is observed and then trusted.** Every value below comes from
frozen V1 artifacts or from a constant V1 already compiled. `observe_runtime`
in `environment_authority/verifier.py` reads platform facts for *comparison*
only, and this module keeps that discipline: it names what was approved, and
offers a comparison against it.

**What this module does not do.** It does not build an environment, submit one,
or make one authoritative. An Environment Authority Record still needs a
`container_image_digest` and an `immutable_artifact_location` -- a reproducibly
built artifact addressed by digest, which cannot be produced on the machine
that would be its own subject. This module supplies the four fields that frozen
evidence already determines, and no others.
"""

from __future__ import annotations

from typing import Final

from cardiosentinel.neural.p1_experiment import FROZEN_DEPENDENCY_DIGEST
from cardiosentinel.neural.provenance import dependency_environment

#: Recorded identically by the B4B, P1B and M1L experiment locks.
APPROVED_PYTHON_RUNTIME_IDENTITY: Final = "CPython-3.12.6"
APPROVED_OPERATING_SYSTEM_IDENTITY: Final = "Linux-x86_64"
APPROVED_PACKAGE_COUNT: Final = 335

#: Imported, never copied. A second literal of this digest would be a second
#: authority, and the two would eventually disagree.
APPROVED_DEPENDENCY_DIGEST: Final = FROZEN_DEPENDENCY_DIGEST

#: The V1 locks this was established from. Named so a reader can check.
ESTABLISHING_EXPERIMENT_LOCKS: Final[tuple[str, ...]] = (
    "reproducibility/demo_bundle/runs/phase3b2-architecture-v1/"
    "B4B_cnn_transformer_v1/EXPERIMENT_LOCK.json",
    "reproducibility/demo_bundle/runs/phase4-p1-physiology-v1/"
    "P1B_phys_fusion_v1/EXPERIMENT_LOCK.json",
    "reproducibility/demo_bundle/runs/phase5-m1-dual-memory-v2/"
    "M1L_long_memory_v2/EXPERIMENT_LOCK.json",
)

#: The canonical form V1 froze: PEP 503 names from `importlib.metadata`, then
#: `json.dumps(packages, sort_keys=True, separators=(",", ":"))` over UTF-8.
DEPENDENCY_DIGEST_METHOD: Final = (
    "sha256(json.dumps(installed_packages, sort_keys=True, "
    'separators=(",", ":")).encode("utf-8"))'
)


class ApprovedRuntimeError(RuntimeError):
    """The running interpreter is not the one J1's scaffold was built in."""


def approved_runtime_fields() -> dict[str, str]:
    """The Environment Authority Record fields frozen evidence determines.

    Four of twelve. The record's `container_image_digest`,
    `immutable_artifact_location`, `base_image_identity` and the rest still
    require an artifact that does not exist, and this function deliberately
    returns nothing for them rather than a placeholder.
    """
    return {
        "python_runtime_identity": APPROVED_PYTHON_RUNTIME_IDENTITY,
        "operating_system_identity": APPROVED_OPERATING_SYSTEM_IDENTITY,
        "dependency_digest": APPROVED_DEPENDENCY_DIGEST,
        "dependency_lock_identity": (
            f"v1-frozen-experiment-lock-{APPROVED_PACKAGE_COUNT}-packages"
        ),
    }


def observed_dependency_digest() -> str:
    """The running interpreter's dependency digest, by V1's own method.

    An observation for comparison. It is never an authority: a digest computed
    from whatever is installed answers *what happened to exist*, which is the
    question `environment_authority` exists to refuse.
    """
    return str(dependency_environment()["installed_packages_sha256"])


def require_approved_dependencies() -> str:
    """Refuse unless the running interpreter is V1's scientific environment.

    Returns the digest so a caller cannot pass the check and then use a
    different value.
    """
    observed = observed_dependency_digest()
    if observed != APPROVED_DEPENDENCY_DIGEST:
        raise ApprovedRuntimeError(
            "this interpreter is not the environment J1's inherited scaffold "
            "was built in.\n"
            f"  approved: {APPROVED_DEPENDENCY_DIGEST}\n"
            f"  observed: {observed}\n"
            "Do not change packages to satisfy this check. A different "
            "environment is a different environment, and the scaffold's "
            "nuisance quantities were estimated in the approved one."
        )
    return observed
