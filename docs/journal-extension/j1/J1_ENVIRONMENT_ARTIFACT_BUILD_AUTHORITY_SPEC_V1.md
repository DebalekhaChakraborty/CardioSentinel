# J1 — Environment Artifact Build Authority Specification, V1

# `QUALIFICATION CANDIDATE — NOT AUTHORIZED`

**This specification builds nothing.** It defines the process by which a future
environment artifact *may* become authoritative. It does not authorize J1
execution, does not create a J1 authorization, does not create an environment
authority record, and does not submit an artifact digest.

**Date:** 2026-09-02
**Established against:** `master` at `38f8b58bffe3aea0c39743eacf9d1a6133f83188`
**Implemented by:** `src/cardiosentinel/journal_extension/j1/build_authority.py`
**Qualified by:** `tests/journal_extension/test_j1_build_authority.py` — 83 tests

---

## 1. The principle

An artifact is not authoritative because it exists, because Docker built it,
because a developer produced it, or because its digest was written down.

**Authority is a provenance chain**, and every link must be immutable:

```text
frozen runtime evidence
        │
        ▼
build specification            ← this document
        │
        ▼
controlled build process
        │
        ▼
artifact digest
        │
        ▼
environment authority record   ← not created here
        │
        ▼
future authorization           ← a human act
```

This document specifies links two through four. It stops before the fifth.

---

## 2. Build authority identity

Every field is required. **No field may silently default**, and
`require_build_authority_declaration` refuses a declaration missing any of them.

| Field | What it answers |
|---|---|
| `build_authority_id` | which authority governed this build |
| `builder_identity` | which builder ran it |
| `builder_version` | which version of that builder |
| `build_method` | how it was built |
| `build_timestamp` | when — recorded, never hashed (§6) |
| `source_repository_identity` | which repository |
| `source_commit` | which exact commit |
| `build_configuration_identity` | which configuration |
| `base_image_identity` | what it was built from |
| `output_artifact_identity` | what came out |
| `artifact_digest_method` | how the digest was taken |
| `provenance_location` | where the record lives |

---

## 3. Approved build inputs

### 3.1 Source identity

| Requirement | Rule |
|---|---|
| `repository` | named explicitly |
| `source_commit` | **full 40-character SHA** |
| worktree | **must be clean** |

**Refused:** an abbreviated commit (it names a set, not an object); a dirty
worktree (what was built is then not what the commit describes, and no digest
recovers the difference); a floating ref — `latest`, `main`, `master`, `HEAD`,
`rolling`, `stable`, `edge`, `nightly`, `dev`, `current`; a tag without an
immutable SHA behind it.

### 3.2 Runtime identity

The build **consumes** the runtime authority established by
[`J1_RUNTIME_AND_DEPENDENCY_LOCK_V1.md`](J1_RUNTIME_AND_DEPENDENCY_LOCK_V1.md).

| Field | Rule |
|---|---|
| `runtime_authority_id` | must be named; blank is refused |
| `dependency_digest` | must equal the approved digest exactly |
| `dependency_lock_identity` | inherited, not redefined |

**A build may reference the qualified runtime. It may not define a new one.** A
manifest declaring any other dependency digest is refused with both values
shown.

### 3.3 Base image identity

Must be `name@sha256:<64 hex>`.

**Refused:** `latest`, `main`, `rolling`, unversioned references, and any tag.
A tag can be repointed at different bytes tomorrow, so it names an intention
rather than an artifact.

---

## 4. Build host authority

### What makes the builder trustworthy?

**Not that it ran the command.** That is the whole question, and the answer
cannot be "it produced the thing", because then the thing being vouched for is
also the voucher.

A builder must declare:

| Field |
|---|
| `builder_id` |
| `builder_environment_identity` |
| `build_tool_version` |
| `container_runtime_version` |
| `build_command_identity` |
| `provenance_output` |

### The builder ladder

```text
CANDIDATE  ──►  QUALIFIED  ──►  AUTHORIZED
```

| State | Reached by |
|---|---|
| `CANDIDATE` | a machine ran a build |
| `QUALIFIED` | its declaration passed `verify_builder` |
| `AUTHORIZED` | **a human act naming that builder** |

**A local developer machine is a candidate builder, never an authorized one.**
A declaration whose fields name `localhost`, a home path, `current-machine`,
`developer-laptop`, `workstation`, `my-machine`, `unknown` or `TBD` is refused
with the reason stated.

**There is no transition function to `AUTHORIZED` in this package**, and a
`BuilderDeclaration` refuses to be constructed asserting it. Proven by an AST
walk that fails if `BuilderState.AUTHORIZED` appears in any return or
assignment — not by a text scan, since this document and that enum necessarily
name the state they forbid producing.

---

## 5. The reproducibility contract

Given identical `source_commit`, `base_image_digest`, `dependency_digest` and
`build_configuration_digest`, the build must produce an identical
`output_artifact_digest` — **or explicitly document why not.**

| Class | Meaning |
|---|---|
| `BIT_REPRODUCIBLE` | the default; identical inputs must give identical bytes |
| `NOT_REPRODUCIBLE_DOCUMENTED` | they do not, and a written reason says why |

**Reproducibility is not assumed and is not proven.** Nothing in this
repository has built the artifact twice. What the contract does is make the
claim **falsifiable**: when two builds exist, an unexplained divergence is a
refusal, not a discrepancy someone reconciles afterwards by choosing a digest.

Two builds that do not share the four inputs are refused outright — they say
nothing about reproducibility either way.

---

## 6. Artifact digest authority

`artifact_sha256` identifies the **final artifact bytes**.

It is **not** metadata, **not** a tag, and **not** a mutable registry
reference.

| | |
|---|---|
| Invalid | `cardiosentinel:j1-latest` |
| Invalid | `registry.invalid/j1@sha256:<64 hex>` — carries a location |
| Valid | `sha256:<64 hex>` |

The second invalid case is the subtle one. Where a copy currently lives is
**provenance**, not identity; an artifact that is mirrored to a second registry
has two locations and one digest.

---

## 7. The build manifest

`J1EnvironmentBuildManifest` carries the chain:

| Field | In digest |
|---|---|
| `build_id` | ✓ |
| `source_commit` | ✓ |
| `runtime_authority_id` | ✓ |
| `dependency_digest` | ✓ |
| `base_image_digest` | ✓ |
| `builder_identity` | ✓ |
| `build_configuration_digest` | ✓ |
| `output_artifact_digest` | ✓ |
| `provenance_reference` | ✓ |
| `creation_timestamp` | ✗ — recorded, never hashed |

### Why the timestamp is excluded

If the moment of writing were hashed, **no two builds could ever produce the
same manifest digest**, and §5's contract would be untestable by construction
rather than merely unproven.

### One canonical form, two record types

`manifest_sha256` uses the **same line form and the same refusal of structural
characters** that `environment_authority.record` froze — imported, not
restated. A second canonical serialization would be a second authority, and the
two would eventually disagree on some value neither author considered. A test
asserts the rule is the same object.

---

## 8. What this specification does not do

It creates **no** environment authority record. A verified build manifest is
provenance *for an artifact*; turning one into an `EnvironmentAuthorityRecord`
is the next task, and an AST test asserts this module never constructs one,
calls `verify_authority_record`, or computes an `environment_sha256`.

```text
build candidate   ≠   qualified environment
```

**The environment state is not transitioned. No artifact digest is promoted.
No authorization field is populated. J1 remains `PRE-REGISTERED — NOT
AUTHORIZED`.**
