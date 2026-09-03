# J1 — Builder Authorization Review Packet, V3

# `READY FOR EXPLICIT HUMAN BUILDER-AUTHORIZATION DECISION`

**Date:** 2026-09-03
**Re-derived against:** `master` at `1983616f2021fa5587b7f6cec716501c610e4bf6` — the #152 merge commit
**Governing protocol:** [`J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2.md`](J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2.md)
**Scientific interpreter used for every recomputation:** `/home/AI_POC/venvs/tactics/bin/python` — CPython 3.12.6, 335 packages

**No image was built. No workflow was dispatched. No builder is authorized. No
scientific data was accessed.**

**`BLOCKED = 0`.** Every machine-resolvable field is resolved against a commit
that now exists. What remains is a human act.

---

## 0. Lineage — nothing before this was rewritten

```text
V1 review packet          READY, over values that were not what they claimed
        ↓
#151 adversarial findings F1–F5: an unbound build input, a control that existed
        ↓                 only in prose, a selectable qualification pair
#152 remediation          Protocol V2, plus F6 found while tracing, plus R1/R2
        ↓                 found reviewing the remediation itself
V3 (this packet)          final re-derivation, because the reviewed object now
                          exists at a commit
```

**Historical stale values remain historical evidence, not current authority.**
The V1 packet, the V2 packet, the V1 build protocol and the builder selection
receipt keep their bytes and their digests. A reader who finds a superseded
digest in one of them is meant to arrive here.

| Retained receipt | SHA-256 | Status |
|---|---|---|
| `J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V1.md` | `86c298efd424d5dd2e86802d015f3f1d90690c78311cc99c18f6cb8a604243c2` | byte-unchanged |
| `J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V2.md` | `b1390c3512b37f81966cc226a552dfb0c4673cbcab5aae10735e6ac74059c992` | byte-unchanged |
| `J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V1.md` | `e980d0f7b22851a6dadd1158ba979cb95395ebc765c71ce5b068ce55fcb651aa` | byte-unchanged |
| `J1_BUILDER_SELECTION_RECEIPT_V1.md` | `3130fac6e8198fb28fff55682bd93af47f81df921ab5919aafb8d36d42aa58cc` | byte-unchanged, typo intact by design |

**What V3 changes relative to V2.** V2 was `NOT READY` because three fields were
blocked on a merge that had not happened. It has happened. Nothing was
remediated in producing this packet; the values were re-derived.

---

## 1. Preconditions, verified read-only before anything was written

| Condition | Method | Result |
|---|---|---|
| #152 merged | `gh pr view 152` | `MERGED` 2026-09-03T18:48:43Z |
| Merge commit | provider record | `1983616f2021fa5587b7f6cec716501c610e4bf6` |
| `master` contains it | `git rev-parse origin/master` | **is** that commit |
| Merged-master CI | `gh run view 33792720330` | `success` |
| Worktree clean | `git status --porcelain` | empty |
| Frozen protocol | SHA-256 over bytes | `cedb152eef187fd573212daaad7492242d6963d9b9de897ed1312cde0a976cf0` |
| Frozen pre-registration | SHA-256 over bytes | `1b6eb6645bf2449e4b76fb40b5ee7e44250474bd08c4a1c42ba79c00dc45fcd1` |
| Freeze receipt | SHA-256 over bytes | `d116199affdc8488fefc765fee86efcd1aae23dee68b0bd302d4e055b08ee107` |
| Authorization contract | SHA-256 over bytes | `9aae5a98475444bc8afa50779a4aaf59449a25ae7fbdb8024f4a0d6d8a048d80` |
| Builder authorization | filesystem + index | **absent** |
| Controlled-build runs | provider API | **0** |
| Actions artifacts | provider API | **0** |
| Evidence directory | filesystem | does not exist |

```text
J1                        = PRE-REGISTERED — NOT AUTHORIZED
builder                   = CANDIDATE
builder authorization     = ABSENT
environment artifact      = ABSENT
environment authority     = ABSENT
J1 authorization          = ABSENT
scientific attempts used  = 0
```

---

## 2. The reviewed workflow object

| | |
|---|---|
| `workflow_path` | `.github/workflows/j1-environment-artifact-build.yml` |
| `workflow_review_commit` | `1983616f2021fa5587b7f6cec716501c610e4bf6` |
| **`workflow_sha256`** | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` |
| Byte count | 21,719 |
| **Git blob identity** | `f3bb13daac12a1d457b2096239b902e29a5cb9ba` |

Three independent digests over raw bytes — no YAML parse, no re-render, no
newline normalisation:

| Source | SHA-256 |
|---|---|
| git object store at the review commit | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` |
| git object store at `origin/master` | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` |
| working-tree checkout | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` |

**All three resolve to one blob object**, which is a stronger statement than
digest equality: it is git's own identity for the content. The commit was not
trusted because the provider labelled it a merge — it was confirmed to exist and
to contain this path before anything was hashed.

**V2's weakness is gone.** V2 could offer only a working-tree digest, because no
commit held those bytes as merged history. One now does.

---

## 3. Authorized source commit

`1983616f2021fa5587b7f6cec716501c610e4bf6` — the same commit, verified to
contain every tracked build input and every module the build path executes:

```text
containers/j1-environment/Containerfile                     TRACKED
containers/j1-environment/Containerfile.dockerignore        TRACKED
containers/j1-environment/build.sh                          TRACKED
containers/j1-environment/validate_artifact.sh              TRACKED
.github/workflows/j1-environment-artifact-build.yml         TRACKED
src/.../j1/builder_authorization.py                         TRACKED
src/.../j1/builder_protocol.py                              TRACKED
src/.../j1/controlled_build.py                              TRACKED
src/.../j1/qualification.py                                 TRACKED
docs/journal-extension/j1/J1_CONTROLLED_..._PROTOCOL_V2.md  TRACKED
reproducibility/.../B4B_cnn_transformer_v1/EXPERIMENT_LOCK.json  TRACKED
```

**No later commit is required.** `origin/master` *is* the merge commit: no
commit touching `containers/`, `.github/workflows/` or the J1 package exists
after it. Authority was not moved forward silently, because there was nowhere
to move it.

---

## 4. Builder candidate identity

```text
github-actions:DebalekhaChakraborty/CardioSentinel//.github/workflows/j1-environment-artifact-build.yml@1983616f2021fa5587b7f6cec716501c610e4bf6#ubuntu-24.04
```

Composed by the repository's own `ControlledBuilderIdentity` and passed through
`require_specific_builder_identity`, not typed. It binds provider, repository,
workflow path, review commit and runner class — five facts, none of which is
"GitHub Actions".

**The historical typo is not used.** `J1_BUILDER_SELECTION_RECEIPT_V1.md` §7
records `j1-environment-build.yml`, a filename that has never existed at any
commit. `verify_builder_authorization` accepts only
`CONTROLLED_BUILD_WORKFLOW_PATH`, so an authorization copied from that receipt
is refused rather than pinning nothing.

---

## 5. Controlled build protocol

| | |
|---|---|
| `controlled_build_protocol_identity` | `J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2` |
| **`controlled_build_protocol_digest`** | `3454c4096fe025a5c88f744cc92b15c1975a9ddf3d2e2e59259770b5b4dea412` |
| Byte count | 22,351 |
| Git blob identity | `18ffa6c93e1b0e6b71f804f8650c8d3f7cf683af` |

**Recomputed from the merge object**, not carried over from V2's report. It
happens to agree, and that agreement is a result rather than an assumption.

---

## 6. Build configuration — seven members, one canonical digest

```text
build_configuration_digest = c9e9b5a636e65957c19103c22d29fdaf7d0dc8b9ed073a2aab146a86b2adf12c
```

| Role | Path / derived identity | SHA-256 | Status | Authority | Affects artifact bytes |
|---|---|---|---|---|---|
| `containerfile` | `containers/j1-environment/Containerfile` | `44b755cb2f43ad8966c981252b98a6483e9690e5e396de3c9c5866d38d686ee7` | tracked | source commit | yes |
| `containerfile_dockerignore` | `containers/j1-environment/Containerfile.dockerignore` | `ddb6843539148f5bed1cb764c582abf6e58badf36b513bced7242547c9de3d1b` | tracked | source commit | yes |
| `dependency_input_pypi` | `containers/j1-environment/requirements.pypi.txt` | `550b79b43c28ef2f09468f8a23cdacb34dabb993afc3e176a55bc2091c5506d9` | `DERIVED_BUILD_INPUT` | frozen V1 lock, via the pinned generator | yes |
| `dependency_input_pytorch` | `containers/j1-environment/requirements.pytorch-cpu.txt` | `a6436381cc2a0315c00c8d4bc80aa47607790dcce709e472b675bffc73ae952b` | `DERIVED_BUILD_INPUT` | frozen V1 lock, via the pinned generator | yes |
| `build_script` | `containers/j1-environment/build.sh` | `06b1e4568c8228df91217f2c4ddf8b16864c9c9432df0048d53dff2e54b2a7d8` | tracked | source commit | yes |
| `workflow` | `.github/workflows/j1-environment-artifact-build.yml` | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` | tracked | source commit | yes |
| `artifact_validation_script` | `containers/j1-environment/validate_artifact.sh` | `84d0f2fae0ded1cc9a77b2c3df6131352446533a4ca44c3b57c256aab5c15a52` | tracked | source commit | no — it decides acceptance |

**The `workflow` member equals `workflow_sha256` in §2.** The digested workflow
is provably the reviewed workflow, not merely a file of the same name.

**Both derived inputs were regenerated twice**, into two separate directories,
from the frozen experiment lock, and the bytes were compared. They are identical.
`require_derived_input_properties` asserted all eight derived-input properties;
`require_derived_input_matches_authority` proved the mapping is exactly the
frozen 335-package set before either file was written.

---

## 7. Runtime and dependency authority — consumed, never redefined

| | |
|---|---|
| `python_runtime_identity` | `CPython-3.12.6` |
| Operating system identity | `Linux-x86_64` |
| `package_count` | **335** |
| `dependency_lock_identity` | `v1-frozen-experiment-lock-335-packages` |
| `dependency_authority_identity` | `v1-frozen-experiment-lock-335-packages` |
| **`dependency_digest`** | `b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a` |

Resolved by calling `approved_runtime_fields()`, not retyped from prose.
`verify_builder_authorization` refuses any authorization naming a different
`dependency_digest`, so this field cannot be varied by the authorization at all.

**The live `tactics` interpreter still matches — as an observation.** Frozen V1
evidence is the authority and survives the venv. Nothing here would repair a
drift; a drift would be a finding.

---

## 8. Base image

| | |
|---|---|
| Descriptive tag — **historical metadata only** | `python:3.12.6-slim-bookworm` |
| **Authority** | `python@sha256:c0d63ec61d3a1321f8dc2d46ab6bd38465e005237c0a463712020e5d338eae25` |
| Object | the linux/amd64 **image manifest** |

**The tag was not re-resolved, and no registry was contacted to see whether it
moved.** The authorization binds the digest-addressed object already reviewed;
asking Docker Hub what the tag points at today would answer a question about
their release schedule. The digest reaches the build from the **verified
authorization** — the workflow declares no `BASE_IMAGE_DIGEST` of its own — and
`build.sh` refuses any reference that is not `repository@sha256:<64 hex>`.

---

## 9. Build tooling — verified in the committed workflow bytes

| | |
|---|---|
| `setup_buildx_action_commit` | `8d2750c68a42422c14e847fe6c8ac0403b4cbd6f` |
| Buildx version | `v0.36.1` — settled, not upgraded |
| BuildKit authority object | single-platform **linux/amd64 OCI image manifest** |
| BuildKit manifest digest | `sha256:040d34121c27906c4ff9ac152a30d52bf2c5d328d3bb748916bb3d2743c02528` |
| `runner_class` | `ubuntu-24.04` — no `ubuntu-latest` anywhere |

Each confirmed present verbatim in the committed bytes. No upgrade, no tag
re-resolution. **What these pins do not constrain is in §15.**

---

## 10. Target and artifact semantics

```text
target_platform      linux/amd64
compute              cpu
accelerator          none
libc                 glibc 2.36
artifact_type        oci_single_platform_image_manifest
artifact_media_type  application/vnd.oci.image.manifest.v1+json
```

**Two digests, never conflated:**

| Digest | What it is |
|---|---|
| OCI **manifest** SHA-256 | the **artifact identity**. What J1 would freeze and later promote |
| OCI **archive** SHA-256 | **transport integrity** only. Two archives of one image differ in tar framing and name the same manifest |

`read_oci_archive_manifest` records both and marks the archive digest as not
being the identity.

---

## 11. Qualification policy — two rules, and what they do not claim

```text
qualification_policy = FIRST_AUTHORIZED_QUALIFICATION_RUN_IS_CANONICAL
frozen governance    = THE_CURRENT_BUILDER_AUTHORIZATION_IS_SINGLE_CLAIM
```

Exactly how they compose:

1. The authorization gate passes, or nothing else runs.
2. **One** qualification claim may be recorded, in its own job, after the gate
   and before any artifact-producing step.
3. Claim identity includes `(run_id, run_attempt)` — provider-assigned and
   monotonic.
4. **A later dispatch under the same authorization cannot replace it.** Its
   claim sorts later; `require_canonical_qualification_run` refuses its evidence.
5. **A re-run attempt cannot replace it.** A re-run keeps its `run_id`, which is
   why `run_attempt` is in the key: without it, re-running *after seeing a
   result* would produce an indistinguishable second pair.
6. **A post-claim failure terminates that authorization's lineage.**
   `require_retry_permitted` permits automatic retry only for
   `PRE_ARTIFACT_INFRASTRUCTURE`, and only while no claim exists. Its
   `claim_recorded` argument has no default, because the permissive value is the
   dangerous one.
7. A further attempt requires **human review + a new `builder_authorization_id`
   + a new lineage**. `require_new_lineage` refuses a reused id.

**This is not dispatch prevention, and it is not described as such.** Nothing
stops a second dispatch. Under `contents: read` with no credentials there is no
persistent, race-free, runner-writable store in which a first run could leave a
lock a second run would find — and a lock built from the Actions cache or from
artifacts would be a process convention wearing the costume of a technical
control. The control is **detection at evidence preservation, plus single-claim
governance**.

---

## 12. Reproducibility procedure — structurally verified

```text
builder-authorization
        ↓
qualification-claim                    (needs: builder-authorization)
        ↓
build-a / build-b                      (needs: builder-authorization,
        ↓                                      qualification-claim,
collect build records and the claim             build-capability)
        ↓
compute the reproducibility record     divergence is an outcome, and does not raise
        ↓
validate present, non-empty, complete
        ↓
upload the record                      if-no-files-found: error
        ↓
enforce the result                     DIVERGED exits non-zero
```

| Outcome | `reproducibility_class` | `failure_class` | Gate |
|---|---|---|---|
| digests agree | `BIT_REPRODUCIBLE` | `COMPLETED_QUALIFICATION` | may pass |
| digests differ | `DIVERGED` | `ARTIFACT_VISIBLE` | **fails, after the record exists** |

**On divergence the complete record — carrying both artifact digests and the
whole frozen provenance — is written, validated and uploaded before the gate
fails.** Enforcement reads that file rather than recomputing, so the failure and
the retained evidence are the same object.

**Invalid inputs are not divergences.** Differing contract inputs, one build id
presented twice, or malformed provenance raise in `require_comparable_builds`
and are never classified `DIVERGED`.

---

## 13. Transient evidence — transport, not authority

| Artifact name | Contents | On absence |
|---|---|---|
| `j1-qualification-claim` | `j1-qualification-claim.json` | error |
| `j1-build-a-provenance` | `build-a.json` | error |
| `j1-build-b-provenance` | `build-b.json` | error |
| `j1-build-a-oci-archive` | `build-a.oci.tar` | error |
| `j1-build-b-oci-archive` | `build-b.oci.tar` | error |
| `j1-reproducibility-record` | `j1-reproducibility.json` | error |

Names are deterministic and defined in `qualification.py`, not chosen per run.
**No registry push. No credentials. No `packages: write`.** Workflow permissions
are `contents: read` and gained nothing across #152.

GitHub Actions storage expires under an account-level retention policy. It moves
bytes; it does not preserve them.

---

## 14. Durable provenance destination

```text
provenance_destination = durable_evidence_destination(builder_authorization_id)
                       = docs/journal-extension/j1/evidence/environment-build/<builder_authorization_id>/
```

**This field is `HUMAN-DERIVED`, not `BLOCKED`.** Its rule is fully determined
and mechanically enforced — `verify_builder_authorization` refuses any value
that is not the one the authorization's own id derives. The human does **not**
choose the destination; the human chooses the id, and the destination follows
with no further judgement.

No placeholder literal appears in this packet, and none may appear in the
authorization.

Evidence becomes durable only through a later **human-reviewed pull request**.
The workflow cannot write it, deliberately.

---

## 15. Residual trust the human is being asked to accept

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

Neither statement is softened. **Pinning by SHA constrains what code runs, not
what executes it.** Note especially that run ordering and run-list completeness
appear in that list: the qualification control in §11 is decided on facts GitHub
supplies.

---

## 16. Scope of the decision

The human is **not** being asked to authorize J1 science. The question is only:

> May this exact builder object perform its single canonical environment-
> qualification lineage under Protocol V2?

Explicitly excluded:

```text
TRAIN access                    validation / test access
reference episode access        candidate evaluation
threshold selection             scientific attempt claim
J1 execution                    environment authority record
artifact promotion              J1 authorization
```

A builder authorization is a statement about a build. It creates no data
authority, no attempt budget, and no permission to see a scientific result.

---

## 17. The complete 22-field authorization table

| Field | Candidate value | Authority source | Verification | Status |
|---|---|---|---|---|
| `builder_authorization_id` | — | human assignment; the schema derives nothing | none available; constraints in §18 | HUMAN-DECISION-REQUIRED |
| `builder_candidate_id` | `github-actions:DebalekhaChakraborty/CardioSentinel//.github/workflows/j1-environment-artifact-build.yml@1983616f2021fa5587b7f6cec716501c610e4bf6#ubuntu-24.04` | `builder_protocol.ControlledBuilderIdentity` | composed by the repository implementation, passed through `require_specific_builder_identity` | MACHINE-VERIFIED |
| `provider` | `github-actions` | `J1_BUILDER_SELECTION_RECEIPT_V1.md` §2 | read from the committed receipt | MACHINE-VERIFIED |
| `repository` | `DebalekhaChakraborty/CardioSentinel` | git remote and provider API | `git remote -v`; refused if generic | MACHINE-VERIFIED |
| `workflow_path` | `.github/workflows/j1-environment-artifact-build.yml` | the controlled-build workflow | equals `CONTROLLED_BUILD_WORKFLOW_PATH`, which the verifier enforces | MACHINE-VERIFIED |
| `workflow_review_commit` | `1983616f2021fa5587b7f6cec716501c610e4bf6` | #152 merge commit | confirmed to exist and to contain the path before hashing | MACHINE-VERIFIED |
| `workflow_sha256` | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` | raw committed workflow bytes | three sources agree and resolve to one git blob `f3bb13da…` | MACHINE-VERIFIED |
| `runner_class` | `ubuntu-24.04` | the committed workflow | literal `runs-on`; no `ubuntu-latest` present | MACHINE-VERIFIED |
| `controlled_build_protocol_identity` | `J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2` | the committed protocol document | derived from the committed path | MACHINE-VERIFIED |
| `controlled_build_protocol_digest` | `3454c4096fe025a5c88f744cc92b15c1975a9ddf3d2e2e59259770b5b4dea412` | raw committed protocol bytes | recomputed from the merge object, not carried from V2 | MACHINE-VERIFIED |
| `source_repository` | `DebalekhaChakraborty/CardioSentinel` | git remote | `git remote -v` | MACHINE-VERIFIED |
| `authorized_source_commit` | `1983616f2021fa5587b7f6cec716501c610e4bf6` | #152 merge commit | every tracked build input proven present; no later commit touches any | MACHINE-VERIFIED |
| `target_platform` | `linux/amd64` | `builder_protocol.TARGET_PLATFORM`, traced to V1 locks | constant; the verifier refuses any other value | MACHINE-VERIFIED |
| `artifact_type` | `oci_single_platform_image_manifest` | `builder_protocol.ARTIFACT_KIND` | constant; the verifier refuses any other value | MACHINE-VERIFIED |
| `base_image_digest` | `python@sha256:c0d63ec61d3a1321f8dc2d46ab6bd38465e005237c0a463712020e5d338eae25` | protocol V2 §6 | present in the committed protocol; digest-addressed form enforced by the verifier and by `build.sh` | MACHINE-VERIFIED |
| `dependency_authority_identity` | `v1-frozen-experiment-lock-335-packages` | `approved_runtime.approved_runtime_fields()` | resolved by calling the authority mechanism | MACHINE-VERIFIED |
| `dependency_digest` | `b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a` | `FROZEN_DEPENDENCY_DIGEST` compiled into V1 | the verifier refuses any other value | MACHINE-VERIFIED |
| `build_configuration_digest` | `c9e9b5a636e65957c19103c22d29fdaf7d0dc8b9ed073a2aab146a86b2adf12c` | `controlled_build.configuration_digest` over all seven members | recomputed from two independent regenerations; workflow member equals `workflow_sha256` | MACHINE-VERIFIED |
| `provenance_destination` | `durable_evidence_destination(builder_authorization_id)` | `qualification.durable_evidence_destination` | rule fully determined; the verifier refuses any other value once the id exists | HUMAN-DERIVED |
| `qualification_policy` | `FIRST_AUTHORIZED_QUALIFICATION_RUN_IS_CANONICAL` | `qualification.QUALIFICATION_POLICY` | constant; the verifier refuses any other value | MACHINE-VERIFIED |
| `authorization_timestamp` | — | the moment of the human act | none available; must not be predated | HUMAN-DECISION-REQUIRED |
| `human_authorizer_identity` | — | the human signing | none available | HUMAN-DECISION-REQUIRED |

```text
MACHINE-VERIFIED          18
HUMAN-DECISION-REQUIRED    3
HUMAN-DERIVED              1
BLOCKED                    0
```

**Every machine requirement was proven satisfiable**, not merely resolved: a
synthetic authorization built from all eighteen machine values, an unmistakably
synthetic id, the derived destination, a synthetic identity and a synthetic
timestamp passes `verify_builder_authorization` over all 22 fields and
`verify_workflow_identity` against real git history, with ancestry `verified`.

**That proves machine sufficiency. It does not create human authorization**, and
the two claims are asserted by separate tests so neither can be mistaken for the
other.

---

## 18. `HUMAN DECISION REQUIRED`

Not answered here, and not answerable by any mechanism in this repository.

1. **Do you authorize this exact GitHub Actions builder object** — the workflow
   at `.github/workflows/j1-environment-artifact-build.yml`, reviewed at
   `1983616f2021fa5587b7f6cec716501c610e4bf6`, digest
   `6bf187e2…`, on `ubuntu-24.04`?
2. **Do you accept the disclosed GitHub residual trust** stated verbatim in §15,
   including run ordering, run-attempt identity and run-list completeness?
3. **Do you accept the single-claim qualification policy** in §11 — one claim
   per authorization, terminal on any post-claim failure, and a control that is
   detection rather than dispatch prevention?
4. **What `builder_authorization_id` do you approve?** Constraints:
   3–64 characters, letters, digits, dot, underscore or hyphen, starting
   alphanumeric, and it becomes a path segment. It also fixes
   `provenance_destination`.
5. **What identity should be recorded as `human_authorizer_identity`?**
6. **Do you approve the scope as environment qualification only**, per §16?

`authorization_timestamp` is recorded when the authorization act occurs, and is
**not** predated.

---

## 19. Negative capability

```text
J1_BUILDER_AUTHORIZATION_V1.json    ABSENT
controlled workflow gate            REFUSES — "builder authorization absent", exit 1
BUILD_A                             UNREACHABLE
BUILD_B                             UNREACHABLE
controlled workflow real runs       0
controlled workflow artifacts       0
environment artifact                ABSENT
environment authority record        ABSENT
J1 authorization                    ABSENT
evidence directory                  does not exist
```

The controlled-build workflow was not dispatched. Nothing in this branch can
dispatch it.

J1 remains **`PRE-REGISTERED — NOT AUTHORIZED`**.
