# J1 — Builder Authorization Act V2

# `BUILDER AUTHORIZED AS 002 — NO BUILD DISPATCHED`

**Authorization ID:** `J1-ENV-BUILDER-AUTH-002`  
**Authorization timestamp:** `2026-09-03T23:07:13Z`  
**Human authorizer identity:** `DebalekhaChakraborty`

This receipt records the explicit human authorization instruction given after review of `J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V4.md`, SHA-256 `0658525ec29c00eef2d0e0eca7009cbc9c8e325fc61d7eef38f1932de8202c13`.

The authorized object is exactly the builder described by the canonical JSON authorization at `J1_BUILDER_AUTHORIZATION_V1.json` and by the V4 packet. The human instruction delegated execution of the reviewed authorization decision while retaining the human authorizer identity above; the assistant/tooling is not recorded as the human authorizer.

The authorization accepts the disclosed residual trust in GitHub Actions hosted infrastructure, including the hosted runner image, underlying hardware, run ordering, run-attempt identity, run-list completeness, and execution service.

It accepts both frozen qualification rules:

- `FIRST_AUTHORIZED_QUALIFICATION_RUN_IS_CANONICAL`
- `THE_CURRENT_BUILDER_AUTHORIZATION_IS_SINGLE_CLAIM`

The authorization scope is **environment qualification only**: authorization gate, qualification claim, BUILD_A, BUILD_B, reproducibility comparison, and preservation of their evidence.

It does **not** authorize TRAIN access, validation/test access, external-data access, candidate evaluation, threshold selection, a scientific attempt claim, J1 scientific execution, artifact promotion, environment authority, or J1 authorization.

No controlled-build workflow was dispatched by this authorization act.

---

## Why this is 002 and not a reuse of 001

`J1-ENV-BUILDER-AUTH-001` is **retired and must never be reused.** It was never
spent — its one dispatched run, `33800630377`, failed in the pre-claim gate on a
`ModuleNotFoundError` before any qualification claim was recorded, so
`require_retry_permitted(PRE_ARTIFACT_INFRASTRUCTURE, claim_recorded=False)`
returns without raising. Retirement is not about a spent budget.

001 names `authorized_source_commit` `1983616f2021fa5587b7f6cec716501c610e4bf6`,
whose tree contains the broken import boundary. The Containerfile ends with
`COPY .`, so the source tree is image content: dispatching 001 would build the
defect into the artifact. The failure is recorded in
`J1_ENV_BUILDER_AUTH_001_PRECLAIM_FAILURE_RECEIPT.md`, SHA-256
`b02e61c14e0384775d586538e9b9dec5ef62a3922177e0dee469f17bb0599460`.

**Exactly one field differs between the object 001 authorized and the object
authorized here: `authorized_source_commit`.** The workflow digest, the protocol
digest, the dependency digest and the seven-member build configuration digest
`c9e9b5a636e65957c19103c22d29fdaf7d0dc8b9ed073a2aab146a86b2adf12c` are
byte-identical across both, because `approved_runtime.py` is not a
build-configuration member.

```text
unchanged build_configuration_digest  ≠  unchanged artifact input
```

The source commit is separately load-bearing. V4 §2 states this at length.

## Preconditions verified immediately before this act

```text
master == origin/master, worktree clean
builder authorization                ABSENT at write time
controlled-build run history         1  (33800630377, attempt 1, FAILED pre-claim)
qualification claims                 0
Actions artifacts                    0
BUILD_A / BUILD_B                    NONE
environment artifact                 ABSENT
environment authority record         ABSENT
J1 authorization                     ABSENT
J1 attempt budget                    NOT ESTABLISHED
scientific attempts used             0
```

The five tracked build-configuration members were recomputed from git's object
store at `8c7a385ddd60072abaf8fd2cfe493f1cefe12885` and agree with the V4 packet;
the seven-member configuration digest was recomputed and agrees; no commit
between that source commit and the authorizing branch point touches any build
input.

## What this act does not do

No controlled build was dispatched. No qualification claim was recorded. No
artifact, environment authority record or J1 authorization exists as a result of
this act, and nothing here shortens the sequence that must precede them.
