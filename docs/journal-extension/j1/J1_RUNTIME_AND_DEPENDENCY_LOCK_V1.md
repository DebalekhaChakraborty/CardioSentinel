# J1 — Approved Runtime and Dependency Lock, V1

# `ESTABLISHED FROM FROZEN EVIDENCE — NO ENVIRONMENT SUBMITTED`

**Date:** 2026-09-02
**Established against:** `master` at `8b2cad1`
**Implemented by:** `src/cardiosentinel/journal_extension/j1/approved_runtime.py`
**Qualified by:** `tests/journal_extension/test_j1_approved_runtime.py` — 11 tests

---

## 0. What this settles, and what it does not

The environment-authority step was blocked on three things. This document
closes two of them and **states plainly that it does not close the third.**

| Blocker | State |
|---|---|
| Which interpreter is the approved scientific runtime? | **closed** — §1 |
| Is there a dependency lock? | **closed** — §2. It already existed. |
| Is there a reproducibly built, digest-addressed artifact? | **open** — §4 |

---

## 1. The runtime was not a preference. It was a recoverable fact.

J1 inherits the **B4 / P1 / M1 / M2 / T2** scaffold. V1's frozen experiment
locks record the environment that scaffold was *built in*, and all three agree:

| | B4B | P1B | M1L |
|---|---|---|---|
| `python_version` | `3.12.6` | `3.12.6` | `3.12.6` |
| `installed_package_count` | 335 | 335 | 335 |
| `environment_dependency_digest` | `b0fd6eaa…` | `b0fd6eaa…` | `b0fd6eaa…` |

`platform`: `Linux-6.1.0-52-cloud-amd64-x86_64-with-glibc2.36`.
`numpy 2.3.2` · `torch 2.13.0+cpu` · `scikit-learn 1.9.0` · `scipy 1.18.0` ·
`wfdb 4.3.1`.

**So the approved runtime is CPython 3.12.6 with that 335-package set.** Not
because it is the interpreter the handoffs happen to name, but because the
scaffold's nuisance quantities were estimated in it, and J1 estimates a
*conditional* contrast **given that scaffold**. Running it elsewhere changes the
thing being conditioned on.

### The CI interpreter is not the scientific interpreter, and never was

`.github/workflows/ci.yml` installs **Python 3.11** from unpinned `pyproject`
ranges (`numpy>=1.26,<3`). That is the correct environment for proving the code
is correct and the wrong one for producing evidence. **Both are true at once,
and a green badge on a pull request says nothing about the second.**

A test asserts this discrepancy as a recorded fact rather than leaving it to be
rediscovered.

---

## 2. The dependency lock already existed. I looked for the wrong thing.

My first reading was *"there is no dependency lock — `pyproject` uses ranges and
the only lock files in the repository are experiment locks."* That was wrong,
and the way it was wrong is worth recording: **I searched for a lockfile by
filename.**

The lock exists as **frozen V1 evidence**, and it is stronger than a lockfile:

- the exact 335-package set, name and version, is recorded *inside* each
  experiment lock;
- names are normalised **PEP 503**, resolved from `importlib.metadata`;
- the digest is compiled into V1's own source as `FROZEN_DEPENDENCY_DIGEST`;
- `require_exact_scientific_environment` already **refuses** a canonical run
  outside it, with a message ending *"Do not change packages to satisfy this
  check."*

### The canonical form, recomputed rather than trusted

```
sha256(json.dumps(installed_packages, sort_keys=True,
                  separators=(",", ":")).encode("utf-8"))
```

Recomputing it from the B4B lock's own package list reproduces
`b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a` exactly. A
test pins the **method**, so a change to the canonical form breaks here before
it breaks a run.

### The live scientific environment has not drifted

The `tactics` interpreter, checked through V1's own `dependency_environment()`,
reports **335 packages** and digest **`b0fd6eaa…`** — identical to what V1's
scaffold was built in. **Re-verified by a dated check on 2026-09-02**, not
inherited from the previous day's run.

**J1 imports the digest; it never retypes it.** A second literal of a frozen
digest is a second authority, and the two eventually disagree. A test walks the
module's AST and fails on any 64-hex string constant.

---

## 3. What this determines for the Environment Authority Record

**Four fields of twelve.**

| Field | Value |
|---|---|
| `python_runtime_identity` | `CPython-3.12.6` |
| `operating_system_identity` | `Linux-x86_64` |
| `dependency_digest` | `b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a` |
| `dependency_lock_identity` | `v1-frozen-experiment-lock-335-packages` |

`approved_runtime_fields()` returns exactly these and **nothing for the other
eight**. A placeholder in `container_image_digest` or
`immutable_artifact_location` is precisely the artifact a later reader — or a
later piece of code — would mistake for authority, which is what
`J1_ENVIRONMENT_AUTHORITY_SPEC_V1` exists to prevent.

---

## 4. What is still missing, and why it cannot be produced here

An Environment Authority Record still needs `base_image_identity`,
`container_image_digest`, `immutable_artifact_location`, `creation_method`,
`hardware_profile`, `accelerator_identity`, `environment_id` and
`environment_version` — that is, **a reproducibly built artifact addressed by
digest, existing somewhere that outlives this machine.**

It cannot be produced on this machine, for two reasons, one practical and one
structural:

1. **Practical.** Docker is installed but its daemon is unreachable here.
2. **Structural, and the one that matters.** The environment-authority package's
   whole thesis is that **a local machine may generate a candidate; it cannot
   promote itself.** An image built here, by this session, to satisfy a check
   this session also wrote, would be a snapshot wearing an artifact's clothes.

Note the asymmetry that makes §1 and §2 legitimate where §4 is not: the runtime
and the dependency set are **read out of frozen V1 evidence that predates this
session**. The artifact would have to be *created* by it.

**Producing that artifact, or authorizing its construction, is an owner
decision.**

---

## Status

| | |
|---|---|
| Approved runtime | **established** — CPython 3.12.6, 335 packages, `b0fd6eaa…` |
| Dependency lock | **established** — frozen V1 experiment locks, digest recomputed |
| Live environment drift | **none**, dated check 2026-09-02 |
| Environment authority record | **NOT SUBMITTED** — 4 of 12 fields determined |
| Authorization | **ABSENT** |
| J1 | **`PRE-REGISTERED — NOT AUTHORIZED`** |

`real_data_authority = NONE` · `attempt_budget = NOT ESTABLISHED` ·
`scientific_attempts_used = 0` · `execution_authorized = FALSE`

No physiological data, annotation, reference-episode count, fold, calibrator,
threshold, candidate selection or result was accessed or generated. No package
was installed, upgraded or removed. Frozen protocol, pre-registration, freeze
receipt and authorization contract are byte-unchanged.
