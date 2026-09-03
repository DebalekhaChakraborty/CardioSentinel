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

---

## The import boundary, and why it is drawn here

**Importing this module must not require the scientific stack.** It used to,
and that defect stopped the first authorized controlled build before it could
begin: the builder authorization gate installs workflow tooling only -- base
dependencies, deliberately, because the gate is not the scientific environment
-- and the gate's own import chain reached through here into
`cardiosentinel.neural`, which imports numpy and torch at module scope.

```text
builder_authorization -> approved_runtime -> neural.p1_experiment -> numpy, torch
                                          -> neural.provenance    -> numpy
```

Run 33800630377 died on the first of those with `ModuleNotFoundError: No module
named 'numpy'`, having verified nothing. The workflow's intent was right and
this module's implementation disagreed with it, so the implementation moved.

Two paths, and the distinction is deliberate:

```text
approved_runtime_fields, APPROVED_DEPENDENCY_DIGEST, the gate
    NO  -- standard library only

observed_dependency_digest, require_approved_dependencies
    YES -- they observe the live scientific environment, so they need it
```

The second pair imports lazily, inside the call. Asking *what was approved* is a
question about frozen bytes on disk. Asking *what is installed here* is a
question about this interpreter, and only that question needs the interpreter to
be the scientific one.

**Nothing here is observed and then trusted.** Every value below comes from
frozen V1 artifacts. `observe_runtime` in `environment_authority/verifier.py`
reads platform facts for *comparison* only, and this module keeps that
discipline: it names what was approved, and offers a comparison against it.

**What this module does not do.** It does not build an environment, submit one,
or make one authoritative. An Environment Authority Record still needs a
`container_image_digest` and an `immutable_artifact_location` -- a reproducibly
built artifact addressed by digest, which cannot be produced on the machine
that would be its own subject. This module supplies the four fields that frozen
evidence already determines, and no others.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

#: Repository root, from this file's location. `src/cardiosentinel/journal_-
#: extension/j1/approved_runtime.py` -> four parents up.
REPOSITORY_ROOT: Final = Path(__file__).resolve().parents[4]

#: Recorded identically by the B4B, P1B and M1L experiment locks.
APPROVED_PYTHON_RUNTIME_IDENTITY: Final = "CPython-3.12.6"
APPROVED_OPERATING_SYSTEM_IDENTITY: Final = "Linux-x86_64"

#: The required population. This is the *requirement*; the locks below are the
#: evidence. A lock disagreeing with it is a refusal, not a new requirement.
APPROVED_PACKAGE_COUNT: Final = 335

#: The V1 locks the approved environment was established from. Named so a
#: reader can check, and now also read, because the digest is resolved from
#: them rather than copied out of them.
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


def _resolve_approved_dependency_digest(
    repository_root: Path | None = None,
) -> str:
    """Read the approved digest out of the frozen locks. Standard library only.

    **Not a second authority.** V1 compiled this digest into
    `neural.p1_experiment.FROZEN_DEPENDENCY_DIGEST`, and that constant remains
    the historical one; this reads the same fact from the same frozen evidence
    that constant was derived from, without importing the module that carries
    it. A test proves the two agree by parsing V1's source with `ast`, so the
    equality is checked rather than assumed -- and checked without importing
    numpy or torch.

    **Every establishing lock must agree.** No majority vote, no first-file-wins,
    no fallback literal: three locks that disagree about which environment the
    scaffold was built in mean the question has no answer, and answering it
    anyway would invent one.
    """
    root = repository_root or REPOSITORY_ROOT
    observed: dict[str, list[str]] = {}
    for relative in ESTABLISHING_EXPERIMENT_LOCKS:
        path = root / relative
        if not path.is_file():
            raise ApprovedRuntimeError(
                f"the establishing experiment lock {relative} is missing. The "
                "approved dependency authority is read from frozen evidence, "
                "and absent evidence is a refusal rather than a default."
            )
        dependencies = json.loads(path.read_text(encoding="utf-8"))[
            "environment"
        ]["dependencies"]
        count = dependencies["installed_package_count"]
        listed = len(dependencies["installed_packages"])
        if count != APPROVED_PACKAGE_COUNT or listed != APPROVED_PACKAGE_COUNT:
            raise ApprovedRuntimeError(
                f"{relative} records {count} packages and lists {listed}; the "
                f"approved set is {APPROVED_PACKAGE_COUNT}."
            )
        observed.setdefault(dependencies["installed_packages_sha256"], []).append(
            relative
        )

    if len(observed) != 1:
        detail = "\n".join(
            f"  {digest}  <- {', '.join(locks)}" for digest, locks in observed.items()
        )
        raise ApprovedRuntimeError(
            "the establishing experiment locks do not agree on the approved "
            f"dependency digest:\n{detail}\n"
            "There is no majority rule and no preferred lock. Disagreement here "
            "means the environment the inherited scaffold was built in is not "
            "determined, and no value may be resolved from it."
        )
    return next(iter(observed))


#: Resolved from frozen evidence at import, using the standard library only.
#: Importing this module must not require numpy, torch, or anything else the
#: scientific environment carries -- the authorization gate depends on it.
APPROVED_DEPENDENCY_DIGEST: Final = _resolve_approved_dependency_digest()


def approved_runtime_fields() -> dict[str, str]:
    """The Environment Authority Record fields frozen evidence determines.

    Four of twelve. The record's `container_image_digest`,
    `immutable_artifact_location`, `base_image_identity` and the rest still
    require an artifact that does not exist, and this function deliberately
    returns nothing for them rather than a placeholder.

    Standard library only: this is on the authorization gate's path.
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

    **Imports the scientific stack, deliberately and lazily.** Observing this
    interpreter's environment requires the environment; asking what was approved
    does not. Calling this from the authorization gate would reintroduce the
    coupling that stopped run 33800630377.
    """
    from cardiosentinel.neural.provenance import dependency_environment

    return str(dependency_environment()["installed_packages_sha256"])


def require_approved_dependencies() -> str:
    """Refuse unless the running interpreter is V1's scientific environment.

    Returns the digest so a caller cannot pass the check and then use a
    different value. Requires the scientific stack, through
    `observed_dependency_digest`.
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
