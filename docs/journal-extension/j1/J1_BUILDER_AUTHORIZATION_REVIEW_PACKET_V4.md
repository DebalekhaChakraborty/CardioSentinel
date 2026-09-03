# J1 — Builder Authorization Review Packet, V4

# `READY FOR EXPLICIT HUMAN BUILDER-AUTHORIZATION DECISION`

**Date:** 2026-09-03
**Re-derived against:** `master` at `8c7a385ddd60072abaf8fd2cfe493f1cefe12885` — the #155 merge commit
**Governing protocol:** [`J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2.md`](J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2.md)
**Prospective next identity:** `J1-ENV-BUILDER-AUTH-002` — **not created here**
**Scientific interpreter used for every recomputation:** `/home/AI_POC/venvs/tactics/bin/python` — CPython 3.12.6, 335 packages

**No image was built. No workflow was dispatched. No builder is authorized. No
scientific data was accessed.**

**`BLOCKED = 0`.**

---

## 0. Why there is a V4

V3 was ready, and a human signed it. The build that followed never started.

```text
J1-ENV-BUILDER-AUTH-001
        ↓
one dispatch                     run 33800630377, run 1, attempt 1
        ↓
PRE_ARTIFACT_INFRASTRUCTURE      gate died on ModuleNotFoundError: numpy
        ↓
claim_recorded = false           the qualification-claim job was skipped
        ↓
source remediation               #155 -- the import boundary moved
        ↓
001 RETIRED, NOT SPENT
```

# `J1-ENV-BUILDER-AUTH-001 MUST NOT BE REUSED`

**Not spent**, because no qualification claim ever existed:
`require_retry_permitted(PRE_ARTIFACT_INFRASTRUCTURE, claim_recorded=False)`
returns without raising, and under Protocol V2 §9 that is the one class that
stays retry-eligible.

**Retired anyway**, because it names `authorized_source_commit`
`1983616f2021fa5587b7f6cec716501c610e4bf6` — the tree containing the broken
gate. The corrected builder therefore requires a **new authorization identity**,
and this packet does not create it.

Full account: [`J1_ENV_BUILDER_AUTH_001_PRECLAIM_FAILURE_RECEIPT.md`](J1_ENV_BUILDER_AUTH_001_PRECLAIM_FAILURE_RECEIPT.md)
— `b02e61c14e0384775d586538e9b9dec5ef62a3922177e0dee469f17bb0599460`.

---

## 1. Preconditions, verified read-only before anything was written

| Condition | Result |
|---|---|
| #155 merged | `MERGED` 2026-09-03T21:29:46Z |
| Merge commit | `8c7a385ddd60072abaf8fd2cfe493f1cefe12885` |
| `master` contains it | master **is** that commit |
| Merged-master CI | `completed / success` (run `33808249245`) |
| Worktree clean | yes |
| Controlled-build history | **1 run** — `33800630377`, run 1, **attempt 1** |
| Qualification claims | **0** |
| Actions artifacts | **0** (run-scoped and repo-wide) |
| BUILD_A / BUILD_B | absent |
| Second dispatch or rerun | **none** |
| `J1_BUILDER_AUTHORIZATION_V1.json` | **ABSENT** — no JSON under `docs/journal-extension/j1/` |
| Failure receipt | present, records 001 as retired-not-spent |

### Retained history, byte-unchanged and never re-pointed

| Receipt | SHA-256 |
|---|---|
| `J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V1.md` | `86c298efd424d5dd2e86802d015f3f1d90690c78311cc99c18f6cb8a604243c2` |
| `J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V2.md` | `b1390c3512b37f81966cc226a552dfb0c4673cbcab5aae10735e6ac74059c992` |
| `J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V3.md` | `209cd8689749bdf422d134d974ef0f2a0f286b31478716accce6263c6cb22115` |
| `J1_BUILDER_AUTHORIZATION_ACT_V1.md` | `7643a81062db0b0294c35334a425509aabfc74f6fc834a64afad7afb242528d6` |
| `J1_ENV_BUILDER_AUTH_001_PRECLAIM_FAILURE_RECEIPT.md` | `b02e61c14e0384775d586538e9b9dec5ef62a3922177e0dee469f17bb0599460` |
| `J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V1.md` | `e980d0f7b22851a6dadd1158ba979cb95395ebc765c71ce5b068ce55fcb651aa` |
| `J1_BUILDER_SELECTION_RECEIPT_V1.md` | `3130fac6e8198fb28fff55682bd93af47f81df921ab5919aafb8d36d42aa58cc` |

V3 records what 001 reviewed. Its values are not rewritten to this commit.

---

## 2. The one field that moves

# The source commit is separately load-bearing

> **The seven-member build-configuration digest is unchanged, but the authorized
> source commit changes, because repository source is copied into the OCI
> artifact by the Containerfile.**

```text
unchanged build_configuration_digest  ≠  unchanged artifact input
```

The Containerfile ends with `COPY . /opt/cardiosentinel/src-tree`, then
`pip install` of that tree. **The repository source is image content.** None of
the seven configuration members changed in #155 — the remediation touched
`approved_runtime.py`, which is not a member — so the configuration digest is
byte-for-byte what V3 recorded.

That is precisely the trap. A reader comparing configuration digests would
conclude nothing had changed and could reuse 001. An artifact built under 001
would contain the **broken gate**, because it would check out `1983616f`.

```text
authorized_source_commit  V3: 1983616f2021fa5587b7f6cec716501c610e4bf6
                          V4: 8c7a385ddd60072abaf8fd2cfe493f1cefe12885   ← the only change
```

---

## 3. Corrected source commit

`8c7a385ddd60072abaf8fd2cfe493f1cefe12885`, verified to contain:

```text
src/.../j1/approved_runtime.py                            the corrected boundary
tests/.../test_j1_approved_runtime_import_boundary.py     the stripped-interpreter proofs
.github/workflows/j1-environment-artifact-build.yml       unchanged
containers/j1-environment/Containerfile                   ┐
containers/j1-environment/Containerfile.dockerignore      │ all seven
containers/j1-environment/build.sh                        │ configuration
containers/j1-environment/validate_artifact.sh            ┘ members
J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2.md            the governing protocol
J1_ENV_BUILDER_AUTH_001_PRECLAIM_FAILURE_RECEIPT.md       the lineage record
B4B_cnn_transformer_v1/EXPERIMENT_LOCK.json               the dependency authority
```

and verified **not** to contain `J1_BUILDER_AUTHORIZATION_V1.json`.

**No later commit is required.** `origin/master` *is* the merge commit; nothing
after it touches `containers/`, `.github/workflows/` or the J1 package.

---

## 4. Reviewed workflow object — deliberately unchanged

The remediation did not touch the workflow, so the reviewed object is the one
V3 reviewed and the review commit does not move.

| Source of bytes | SHA-256 |
|---|---|
| git at `workflow_review_commit` `1983616f…` | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` |
| git at the new source commit `8c7a385d…` | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` |
| working-tree checkout | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` |

**All three resolve to one git blob `f3bb13daac12a1d457b2096239b902e29a5cb9ba`.**
The builder workflow was not silently redefined: an import-boundary repair stayed
an import-boundary repair.

---

## 5. The remediation, verified as part of the corrected source identity

This is what makes `8c7a385d` a different object from `1983616f`, and it is
checked rather than asserted.

### Stripped interpreter — negatives proven first

```text
python -S  with PYTHONPATH=src

numpy  torch  scipy  sklearn  pandas  wfdb        all unimportable
builder_authorization                              imports OK
approved_runtime_fields()                          b0fd6eaa…
numpy in sys.modules                               False
cardiosentinel.neural modules loaded               none
```

### The gate CLI in that same interpreter

```text
exit code 1
stderr:  controlled build refused: builder authorization absent

GOOD  (authorization refusal)  : True
BAD   (ModuleNotFoundError / ImportError / scientific import) : False
```

**The distinction is the whole point.** Run 33800630377 also exited non-zero
with the words *"builder authorization absent"* on stderr — while the gate had
crashed during import, having verified nothing. An exit code cannot tell those
apart. The gate now **decides**; previously it **died**.

---

## 6. Frozen dependency authority

Resolved by the corrected production implementation, which reads the frozen
locks with the standard library only.

| Establishing lock | `installed_package_count` | listed | `installed_packages_sha256` |
|---|---|---|---|
| `B4B_cnn_transformer_v1` | 335 | 335 | `b0fd6eaa…` |
| `P1B_phys_fusion_v1` | 335 | 335 | `b0fd6eaa…` |
| `M1L_long_memory_v2` | 335 | 335 | `b0fd6eaa…` |

**Unanimous.** No fallback, no majority vote, no embedded alternative authority —
disagreement, a missing lock, or a wrong population each raise.

```text
dependency_digest = b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a
python_runtime    = CPython-3.12.6        packages = 335
lock identity     = v1-frozen-experiment-lock-335-packages
```

### Agreement with V1's compiled constant — verification only

`cardiosentinel.neural.p1_experiment.FROZEN_DEPENDENCY_DIGEST` read **by `ast`
from source, never imported**: it is an annotated `Final`, so the syntax tree
carries the literal.

```text
V1 compiled constant  b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a
lock-derived digest   b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a
AGREE
```

**The production authority is the frozen experiment-lock evidence.** The AST
check is a test that the two readings agree; it is not a second authority path,
and it deliberately avoids the import that broke the gate.

---

## 7. Build configuration — recomputed, not assumed

```text
build_configuration_digest = c9e9b5a636e65957c19103c22d29fdaf7d0dc8b9ed073a2aab146a86b2adf12c
```

| Role | Status | SHA-256 |
|---|---|---|
| `containerfile` | tracked | `44b755cb2f43ad8966c981252b98a6483e9690e5e396de3c9c5866d38d686ee7` |
| `containerfile_dockerignore` | tracked | `ddb6843539148f5bed1cb764c582abf6e58badf36b513bced7242547c9de3d1b` |
| `dependency_input_pypi` | derived | `550b79b43c28ef2f09468f8a23cdacb34dabb993afc3e176a55bc2091c5506d9` |
| `dependency_input_pytorch` | derived | `a6436381cc2a0315c00c8d4bc80aa47607790dcce709e472b675bffc73ae952b` |
| `build_script` | tracked | `06b1e4568c8228df91217f2c4ddf8b16864c9c9432df0048d53dff2e54b2a7d8` |
| `workflow` | tracked | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` |
| `artifact_validation_script` | tracked | `84d0f2fae0ded1cc9a77b2c3df6131352446533a4ca44c3b57c256aab5c15a52` |

Both derived inputs were regenerated into separate directories and compared byte
for byte. The `workflow` member equals the reviewed-bytes digest in §4.

**It matched what V3 recorded. That was not assumed — it was recomputed, and §2
explains why a match here means less than it appears to.**

---

## 8. Base image and toolchain — unchanged, re-verified

| | |
|---|---|
| Descriptive tag, historical metadata only | `python:3.12.6-slim-bookworm` |
| **Authority** | `python@sha256:c0d63ec61d3a1321f8dc2d46ab6bd38465e005237c0a463712020e5d338eae25` |
| `setup_buildx_action_commit` | `8d2750c68a42422c14e847fe6c8ac0403b4cbd6f` |
| Buildx | `v0.36.1` — no upgrade |
| BuildKit linux/amd64 manifest | `sha256:040d34121c27906c4ff9ac152a30d52bf2c5d328d3bb748916bb3d2743c02528` |
| `runner_class` | `ubuntu-24.04` — `ubuntu-latest` absent from the workflow |
| Target | `linux/amd64` · cpu · no accelerator |
| Artifact | `oci_single_platform_image_manifest` · `application/vnd.oci.image.manifest.v1+json` |

Each confirmed present verbatim in the committed workflow. **The tag was not
re-resolved and no registry was contacted** — the authorization binds the
digest-addressed object already reviewed.

---

## 9. Qualification policy, and why 001's failure does not compete

```text
qualification_policy = FIRST_AUTHORIZED_QUALIFICATION_RUN_IS_CANONICAL
frozen governance    = THE_CURRENT_BUILDER_AUTHORIZATION_IS_SINGLE_CLAIM
```

Both unchanged.

**Canonicality is scoped by `builder_authorization_id`.**
`require_canonical_qualification_run` filters the observed claim set to those
carrying the authorization under review, then takes the earliest by
`(run_id, run_attempt)`. Run 33800630377 recorded **no claim at all**, and any
claim it might have recorded would have named 001.

So a future run under 002 begins a fresh lineage with **zero** prior claims. The
failed run neither competes with it nor pre-empts it — and this is a property of
the mechanism, not a courtesy: a filtered claim set that ignored the scoping
would be the exact defeat the rule's disclosed limitation names.

### What kind of control this is — unchanged, and still not overstated

**It is detection, not dispatch prevention.** Nothing stops a second dispatch.
Under `permissions: contents: read` with no credentials, GitHub Actions offers
this repository no persistent, race-free, runner-writable store where a first run
could leave a lock a second would find — and a lock built from the Actions cache
or from artifacts would be a process convention wearing the costume of a
technical control. What the provider supplies is an immutable, monotonic
`run_id` that nobody can insert below, so
`require_canonical_qualification_run` refuses any non-earliest claim's evidence
where evidence becomes durable. The control class is **detection at evidence
preservation**, which is also what the mechanism reports about itself.

**The limitation, disclosed rather than papered over:** the ordering, and the
completeness of the run listing the check reads, are GitHub's. A filtered claim
set would defeat it. That authority is already inside the residual trust in §11.

---

## 10. The complete 22-field authorization table

| Field | Candidate value | Authority | Verification | Status |
|---|---|---|---|---|
| `builder_authorization_id` | — | human assignment; the schema derives nothing | none available; constraints in §12 | HUMAN-DECISION-REQUIRED |
| `builder_candidate_id` | `github-actions:DebalekhaChakraborty/CardioSentinel//.github/workflows/j1-environment-artifact-build.yml@1983616f2021fa5587b7f6cec716501c610e4bf6#ubuntu-24.04` | `builder_protocol.ControlledBuilderIdentity` | constructed by the implementation, passed through `require_specific_builder_identity` | MACHINE-VERIFIED |
| `provider` | `github-actions` | `J1_BUILDER_SELECTION_RECEIPT_V1.md` §2 | read from the committed receipt | MACHINE-VERIFIED |
| `repository` | `DebalekhaChakraborty/CardioSentinel` | git remote and provider API | `git remote -v`; generic identities refused | MACHINE-VERIFIED |
| `workflow_path` | `.github/workflows/j1-environment-artifact-build.yml` | the controlled-build workflow | equals `CONTROLLED_BUILD_WORKFLOW_PATH`, enforced by the verifier | MACHINE-VERIFIED |
| `workflow_review_commit` | `1983616f2021fa5587b7f6cec716501c610e4bf6` | the commit at which the bytes were reviewed | unchanged: #155 did not touch the workflow | MACHINE-VERIFIED |
| `workflow_sha256` | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` | raw committed workflow bytes | three sources agree, one git blob `f3bb13da…` | MACHINE-VERIFIED |
| `runner_class` | `ubuntu-24.04` | the committed workflow | literal `runs-on`; no `ubuntu-latest` | MACHINE-VERIFIED |
| `controlled_build_protocol_identity` | `J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2` | the committed protocol | derived from the committed path | MACHINE-VERIFIED |
| `controlled_build_protocol_digest` | `3454c4096fe025a5c88f744cc92b15c1975a9ddf3d2e2e59259770b5b4dea412` | raw committed protocol bytes | recomputed from disk and from the merge object | MACHINE-VERIFIED |
| `source_repository` | `DebalekhaChakraborty/CardioSentinel` | git remote | `git remote -v` | MACHINE-VERIFIED |
| `authorized_source_commit` | `8c7a385ddd60072abaf8fd2cfe493f1cefe12885` | the #155 merge commit — **this is the field that moved, see §2** | every build input and remediated module proven present; no later commit touches any | MACHINE-VERIFIED |
| `target_platform` | `linux/amd64` | `builder_protocol.TARGET_PLATFORM`, traced to V1 locks | constant; verifier refuses any other | MACHINE-VERIFIED |
| `artifact_type` | `oci_single_platform_image_manifest` | `builder_protocol.ARTIFACT_KIND` | constant; verifier refuses any other | MACHINE-VERIFIED |
| `base_image_digest` | `python@sha256:c0d63ec61d3a1321f8dc2d46ab6bd38465e005237c0a463712020e5d338eae25` | protocol V2 §6 | present in the committed protocol; digest form enforced by verifier and `build.sh` | MACHINE-VERIFIED |
| `dependency_authority_identity` | `v1-frozen-experiment-lock-335-packages` | `approved_runtime.approved_runtime_fields()` | resolved by calling the corrected authority mechanism | MACHINE-VERIFIED |
| `dependency_digest` | `b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a` | three frozen establishing locks, unanimous | resolved from evidence; AST-checked against V1's constant | MACHINE-VERIFIED |
| `build_configuration_digest` | `c9e9b5a636e65957c19103c22d29fdaf7d0dc8b9ed073a2aab146a86b2adf12c` | `controlled_build.configuration_digest` over all seven members | recomputed from two independent regenerations | MACHINE-VERIFIED |
| `provenance_destination` | `durable_evidence_destination(builder_authorization_id)` | `qualification.durable_evidence_destination` | rule total and enforced; refused if it is anything else | HUMAN-DERIVED |
| `qualification_policy` | `FIRST_AUTHORIZED_QUALIFICATION_RUN_IS_CANONICAL` | `qualification.QUALIFICATION_POLICY` | constant; verifier refuses any other | MACHINE-VERIFIED |
| `authorization_timestamp` | — | the moment of the human act | none available; must not be predated | HUMAN-DECISION-REQUIRED |
| `human_authorizer_identity` | — | the human signing | none available | HUMAN-DECISION-REQUIRED |

```text
MACHINE-VERIFIED          18
HUMAN-DECISION-REQUIRED    3
HUMAN-DERIVED              1
BLOCKED                    0
```

**Every field was re-verified, not carried over.** Seventeen machine values are
unchanged from V3 and one moved; the check that established that is the same
check either way.

**Machine satisfiability was proven, and it is not authorization.** A synthetic
document over all 22 fields — unmistakably synthetic id and identity, derived
destination, the corrected source commit — passes `verify_builder_authorization`
and `verify_workflow_identity` with ancestry `verified`, while the canonical path
stays empty.

---

## 11. Residual trust — unchanged, and not softened

> The authorization accepts GitHub Actions hosted infrastructure as the
> controlled builder substrate. Repository controls bind the workflow bytes,
> action commits, Buildx version, BuildKit linux/amd64 manifest, authorized
> source commit, dependency authority, build configuration, qualification policy
> and evidence structure. GitHub remains the external authority for the hosted
> runner image, underlying hardware, run ordering, run-attempt identity,
> run-list completeness and execution service.

> GitHub-hosted execution is not cryptographically reproducible. Reproducibility
> is a falsifiable property tested by the frozen independent BUILD_A/BUILD_B
> procedure.

Run 33800630377 is a reminder that this list is not decorative: the runner
image, its interpreter and its installed packages are GitHub's, and the failure
happened inside that boundary.

---

## 12. `HUMAN DECISION REQUIRED`

Not answered here. The expected next identity is **`J1-ENV-BUILDER-AUTH-002`**,
and naming it in this sentence is a statement about numbering, **not an
authorization act**.

1. **Do you authorize this exact builder object** — the workflow at
   `.github/workflows/j1-environment-artifact-build.yml`, reviewed at
   `1983616f…`, digest `6bf187e2…`, on `ubuntu-24.04`, building from
   **`8c7a385d…`**?
2. **Do you accept the disclosed GitHub residual trust** in §11, including run
   ordering, run-attempt identity and run-list completeness?
3. **Do you accept the single-claim qualification policy** — one claim per
   authorization, terminal on any post-claim failure, detection rather than
   dispatch prevention?
4. **What `builder_authorization_id` do you approve?** 3–64 characters, letters,
   digits, dot, underscore or hyphen, starting alphanumeric; it becomes a path
   segment and fixes `provenance_destination`. It **must not** be
   `J1-ENV-BUILDER-AUTH-001`.
5. **What identity should be recorded as `human_authorizer_identity`?**
6. **Do you approve the scope as environment qualification only** — the gate, one
   claim, BUILD_A, BUILD_B, the reproducibility comparison and its evidence, and
   nothing else?

`authorization_timestamp` is recorded when the act occurs, and is **not**
predated.

### Excluded, as before

```text
TRAIN access                validation / test access      reference episode access
candidate evaluation        threshold selection           scientific attempt claim
J1 execution                environment authority record  artifact promotion
J1 authorization
```

---

## 13. Negative capability

```text
J1_BUILDER_AUTHORIZATION_V1.json    ABSENT
controlled workflow gate            REFUSES -- and reaches its own logic to do so
BUILD_A / BUILD_B                   NONE
controlled workflow runs            1  (33800630377, attempt 1, failed pre-claim)
qualification claims                0
Actions artifacts                   0
environment artifact                ABSENT
environment authority record        ABSENT
J1 authorization                    ABSENT
J1 attempt budget                   NOT ESTABLISHED
scientific attempts used            0
evidence directory                  does not exist
```

No retry, no rerun, no second dispatch. The frozen scientific protocol,
pre-registration, freeze receipt and authorization contract are byte-unchanged,
as are all seven retained receipts.

J1 remains **`PRE-REGISTERED — NOT AUTHORIZED`**.
