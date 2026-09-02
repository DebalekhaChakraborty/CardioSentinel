# J1 — Environment Artifact Qualification Receipt, V1

# `QUALIFICATION FRAMEWORK READY — ARTIFACT NOT SUBMITTED`

**Date:** 2026-09-02
**Specification:** [`J1_ENVIRONMENT_ARTIFACT_BUILD_AUTHORITY_SPEC_V1.md`](J1_ENVIRONMENT_ARTIFACT_BUILD_AUTHORITY_SPEC_V1.md), V1
**Verified against:** `master` at `38f8b58bffe3aea0c39743eacf9d1a6133f83188`

---

## What is qualified

**The build authority mechanism** — the build-authority field set, the builder
declaration and its state ladder, the input admissibility rules, the manifest
schema and its canonical digest, and the reproducibility contract.

## What is *not* qualified

**No artifact.** None has been built, submitted or verified.

| | |
|---|---|
| `output_artifact_digest` | **ARTIFACT NOT SUBMITTED** |
| `build_id` | **ARTIFACT NOT SUBMITTED** |
| `builder_id` | **ARTIFACT NOT SUBMITTED** |
| Environment authority record | **NOT SUBMITTED** |

**This receipt deliberately names no digest.** No image was built, and inventing
a plausible `sha256:` value here is exactly the artifact a later reader — or a
later piece of code — would mistake for authority. A dash is the honest state.

When an artifact is genuinely built and qualified, it is recorded in a **V2
receipt** naming its real `build_id`, `builder_id` and `output_artifact_digest`.
**This V1 receipt is not edited to add them.**

---

## Verification

| | |
|---|---|
| Build authority tests | `tests/journal_extension/test_j1_build_authority.py` — **83 passed** |
| Instrument tests | `tests/journal_extension/` — **400 passed** |
| Governance tests | `tests/reproducibility/` — **52 passed** |
| Sealed-test identity | `tests/neural/test_b4b_sealed_test_identity.py` — **23 passed** |
| Shared-interpreter condition | all three together — **475 passed** |
| Lint | `ruff check .` — clean |

The three suites are run in one interpreter as well as separately, because a J1
module previously asserted a `sys.modules` absence that held in isolation and
failed in the full suite.

### Checks exercised, against synthetic manifests only

**No mutable inputs**

- a base image by tag, unversioned, or with a malformed digest is refused;
- an artifact named by tag (`cardiosentinel:j1-latest`) is refused;
- an artifact reference carrying a **registry location** is refused — where a
  copy lives is provenance, not identity;
- an abbreviated, empty, uppercase or symbolic source commit is refused;
- a **dirty worktree** is refused;
- a floating source ref — `latest`, `main`, `HEAD`, `nightly`, `stable` — is
  refused;
- an unpinned build configuration is refused;
- a build declaring **any dependency digest but the approved one** is refused.

**No local self-promotion**

- a builder naming `current-machine`, `developer-laptop`, a home path,
  `localhost`, `unknown` or `TBD` is refused, and the refusal says *candidate
  builder*;
- a `BuilderDeclaration` cannot be constructed asserting `AUTHORIZED`;
- **no return or assignment in the module produces `BuilderState.AUTHORIZED`**,
  proven by AST rather than text scan;
- `verify_build_manifest` has no `force`, `dev_mode`, `skip_provenance` or
  `allow_dirty` parameter.

**No missing provenance**

- every manifest field is required; a blank one refuses;
- a builder that will not identify itself refuses;
- a manifest naming a **different builder** than the declaration refuses — the
  artifact and its builder must be one story;
- every build-authority field is required; none may silently default.

**Digest and canonical form**

- field-ordered, newline-terminated, one terminating newline;
- every digest-bearing field changes the digest;
- **`creation_timestamp` never reaches the digest**;
- a field carrying `\n` or `\r` is refused as canonical-form structure;
- **the canonical rule is the same object** the environment authority froze,
  asserted by identity, not by resemblance.

**Reproducibility contract**

- identical inputs with identical artifacts agree;
- identical inputs with **different** artifacts refuse under
  `BIT_REPRODUCIBLE`;
- a documented divergence is permitted **with a written reason**;
- an undocumented divergence refuses;
- builds not sharing the four inputs refuse — they say nothing either way;
- the **default class is the strict one**.

**Not an environment authority**

- the module never constructs an `EnvironmentAuthorityRecord`, calls
  `verify_authority_record`, or computes an `environment_sha256` — AST-proven;
- a verified manifest attests `environment_authority_submitted = false` and
  carries no `environment_sha256`.

---

## Status

| | |
|---|---|
| Build authority mechanism | **QUALIFIED** (the mechanism; no build has been) |
| Artifact | **NOT SUBMITTED** |
| Builder | **NONE AUTHORIZED** |
| Environment authority record | **NOT SUBMITTED** — 4 of 12 fields determined |
| Authorization | **ABSENT** |
| J1 | **`PRE-REGISTERED — NOT AUTHORIZED`** |

`real_data_authority = NONE` · `attempt_budget = NOT ESTABLISHED` ·
`scientific_attempts_used = 0` · `execution_authorized = FALSE`

**Environment artifact qualification is preparation, not authorization.** No
physiological data, annotation, reference-episode count, fold, calibrator,
threshold, candidate selection or result was accessed or generated by the work
this receipt records. No image was built. No package was installed, upgraded or
removed. Every manifest, builder and digest in the qualification tests is
fabricated and describes no real artifact, and none is written under a canonical
scientific run path.

The frozen protocol, pre-registration and freeze receipt are byte-unchanged.
