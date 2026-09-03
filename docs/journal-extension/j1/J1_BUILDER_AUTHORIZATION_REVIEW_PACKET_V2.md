# J1 — Builder Authorization Review Packet, V2

# `NOT READY FOR HUMAN DECISION — REMEDIATION PENDING MERGE — BUILDER NOT AUTHORIZED`

**Date:** 2026-09-02
**Supersedes:** [`J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V1.md`](J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V1.md) — `86c298efd424d5dd2e86802d015f3f1d90690c78311cc99c18f6cb8a604243c2`, **byte-unchanged, retained as the audit receipt**
**Governing protocol:** [`J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2.md`](J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2.md)
**Scientific interpreter used for every recomputation:** `/home/AI_POC/venvs/tactics/bin/python` — CPython 3.12.6, 335 packages

**No image was built. No workflow was dispatched. No builder is authorized. No
scientific data was accessed.**

---

## 0. Why this packet's status is weaker than V1's

V1 said `READY FOR HUMAN DECISION`. This one does not, and that is not a
regression — it is V1's finding being taken seriously.

V1's own review found that `build_configuration_digest` did not cover an input
that changes the image, that a documented control did not exist in code, and
that the qualification pair was selectable. **A decision taken over V1's values
would have been a decision over an object that was not what it claimed to be.**

The remediation changes the workflow bytes. The reviewed object therefore does
not exist at a commit yet: **the review commit is established by the merge of
this remediation pull request**, and three fields below are `BLOCKED` on exactly
that. They become resolvable the moment it merges, and a V3 packet — or an
amendment to this one — will carry them.

**This packet must not be signed as it stands.** Three of its fields have no
values.

---

## 1. What changed since V1, finding by finding

| Finding | Resolution | Mechanical proof | Remaining limitation |
|---|---|---|---|
| **F1** — `requirements.pytorch-cpu.txt` outside the configuration digest | one member per file; `dependency_input_pypi` and `dependency_input_pytorch` are both members | a test alters the PyTorch pin and requires the digest to change | none |
| **F2** — a member is generated and gitignored | `DERIVED_BUILD_INPUT` formalised with eight required properties | generation runs twice into separate directories and bytes are compared; `require_derived_input_properties` refuses an unstated property | the input stays derived; if any property lapses it must become tracked |
| **F3** — the workflow did not re-resolve the base image as claimed | the **claim is withdrawn**; the digest is consumed directly from the verified authorization | `build.sh` refuses any non-digest reference; a test refuses a tag | the base image remains upstream's object; the digest bounds which one |
| **F4** — selection receipt names `j1-environment-build.yml` | correction record C1; the correct path is enforced, not just written | `verify_builder_authorization` refuses any other `workflow_path` | the receipt's historical bytes still contain the typo, by design |
| **F5** — V1 protocol §12 stale since #150 | superseded by protocol V2 with an explicit lineage | V1's digest is unchanged and asserted by test | a reader must follow the lineage to reconcile the two |
| **F6** — no `.dockerignore`; `COPY .` would have ingested `.git` | `Containerfile.dockerignore` added and made a configuration member | a test requires the file to exist, to exclude `.git`, and to be a member | context exclusion is a denylist; a new artifact-affecting path must be added to it |

**F6 was not in V1's list.** It was found while tracing the build-input graph
this task required, and it is the most consequential of the six: BUILD_A and
BUILD_B would very likely have diverged because of git pack-file bytes, and the
protocol would have correctly refused to promote either while the diagnosis
pointed at the wrong thing entirely.

---

## 2. Machine-resolved facts

### The reviewed workflow bytes

| Source | SHA-256 |
|---|---|
| working tree (this branch) | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` |
| git object store at a review commit | **not yet — established by this PR's merge** |

V1's three-way agreement cannot be reproduced here, and saying so is the point:
the bytes are new, no commit contains them as merged history yet, and a digest
taken only from a working tree is a weaker fact than one taken from git. It is
recorded as what it is.

### Controlled build protocol

| | |
|---|---|
| Identity | `J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2` |
| Digest | `3454c4096fe025a5c88f744cc92b15c1975a9ddf3d2e2e59259770b5b4dea412` |
| Supersedes | V1 at `e980d0f7b22851a6dadd1158ba979cb95395ebc765c71ce5b068ce55fcb651aa`, byte-unchanged |

### Build configuration digest — seven members, was five

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

The `workflow` member equals the reviewed-bytes digest above. The V1 value
`ff992b1c…` is superseded and must not be carried forward.

### Runtime authority — unchanged, and re-resolved rather than copied

| | |
|---|---|
| `python_runtime_identity` | `CPython-3.12.6` · 335 packages |
| `dependency_authority_identity` | `v1-frozen-experiment-lock-335-packages` |
| `dependency_digest` | `b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a` |

Three agreeing readings: the constant V1 compiled, the frozen B4B experiment
lock, and the live `tactics` interpreter. No new authority was established.

### Base image and tooling — unchanged, re-verified against committed bytes

| | |
|---|---|
| Descriptive tag, metadata only | `python:3.12.6-slim-bookworm` |
| Authority | `python@sha256:c0d63ec61d3a1321f8dc2d46ab6bd38465e005237c0a463712020e5d338eae25` |
| `setup_buildx_action_commit` | `8d2750c68a42422c14e847fe6c8ac0403b4cbd6f` |
| Buildx | `v0.36.1` — settled, not upgraded |
| BuildKit linux/amd64 manifest | `sha256:040d34121c27906c4ff9ac152a30d52bf2c5d328d3bb748916bb3d2743c02528` |
| `runner_class` | `ubuntu-24.04` |
| Target | `linux/amd64` · cpu · no accelerator |
| Artifact | `oci_single_platform_image_manifest` · `application/vnd.oci.image.manifest.v1+json` |

The base image digest now reaches the build from the **verified authorization**,
not from the workflow's environment block. One authority, not two copies.

---

## 3. Provenance destination — resolvable, and enforced

V1 recorded this as `BLOCKED` because nothing determined it. It is determined
now:

```text
docs/journal-extension/j1/evidence/environment-build/<builder_authorization_id>/
```

A pure function of the authorization's own id, computed by
`qualification.durable_evidence_destination`, and **refused by
`verify_builder_authorization` if it is anything else**. The destination cannot
be chosen after the evidence is in hand.

It is listed below as `HUMAN-DECISION-REQUIRED` rather than machine-verified for
one reason only: it is derived from `builder_authorization_id`, which no
mechanism assigns. Choose the id and the destination follows with no further
judgement.

**Transport is not evidence.** GitHub Actions artifacts carry the claim, both
provenance records, both OCI archives and the reproducibility record out of the
run; the durable record is a later human-reviewed evidence PR into the path
above. The workflow has `contents: read` and cannot write it, which is
deliberate.

---

## 3a. Two corrections after adversarial review of the remediation

Both were found by review of this PR, not of #151, and both are recorded rather
than quietly fixed.

### R1 — the post-claim retry rule contradicted the canonical identity

The failure table said a post-claim failure left the claim standing "so a retry
runs under it". **No such mechanism exists or could.** Canonical identity is
`(run_id, run_attempt)`, so any retry — a re-run of the same GitHub run or a
fresh dispatch — produces a *later* claim, which the canonical-run rule refuses.
Permitting a retry that can never become evidence is not a permission; it is an
invitation to attempt an authorization until one attempt looks right.

# `THE CURRENT BUILDER AUTHORIZATION IS SINGLE-CLAIM`

Once a claim is recorded, that authorization is spent. Automatic retry survives
only for `PRE_ARTIFACT_INFRASTRUCTURE`, and only while no claim exists;
`require_retry_permitted` now takes `claim_recorded` as a required argument with
**no default**, because the permissive value is the dangerous one. A further
attempt needs human review **and** a new `builder_authorization_id` **and** a new
lineage — ids are not interchangeable, since the evidence destination is derived
from the id.

`run_attempt` stays in the identity. It is what stops a run being re-run *after
its result is visible* and presented as the qualifying pair.

### R2 — a divergence produced no record at all

The comparison computed and refused in one call, raising on disagreement before
writing anything. **The single outcome the two-build procedure exists to detect
was the one outcome that left no evidence** — it survived only as a line in an
expiring run log, which is the same defect #151 found in the old workflow, one
layer down.

Recording is now separate from enforcement:

```text
PHASE A  reproducibility-record    a divergence is an outcome, and does not raise
         validate present/non-empty/complete
         upload                    if-no-files-found: error
PHASE B  enforce-reproducibility   reads the retained record; DIVERGED exits non-zero
```

| Outcome | `reproducibility_class` | `failure_class` |
|---|---|---|
| digests agree | `BIT_REPRODUCIBLE` | `COMPLETED_QUALIFICATION` |
| digests differ | `DIVERGED` | `ARTIFACT_VISIBLE` |

**Invalid inputs are not divergences.** Differing contract inputs, one build id
twice, or malformed provenance raise in `require_comparable_builds` and are never
classified `DIVERGED`: two builds from different inputs disagreeing says nothing
about reproducibility, and recording it as a finding would manufacture one out of
a mistake.

---

## 4. The qualification pair, and what kind of control it is

# `FIRST AUTHORIZED QUALIFICATION RUN IS CANONICAL`

The earliest run, by provider run ordering, that passed the gate and recorded a
claim before any artifact work. Later runs may execute; their evidence may not
replace the canonical run's.

**This is detection, not prevention.** Nothing stops a second dispatch. Under
`contents: read` with no credentials, GitHub Actions offers no persistent,
race-free, runner-writable store for a lock — and a lock built from the Actions
cache or from artifacts would be a process convention dressed as a technical
control, which is worse than none. What the provider does supply is an
immutable monotonic `run_id`; nobody can create a run that sorts before one that
exists. `require_canonical_qualification_run` refuses any non-earliest claim's
evidence where evidence becomes durable.

**Limitation:** the ordering and the completeness of the run listing are
GitHub's, and a filtered claim set would defeat the check. That authority is
already inside the disclosed residual trust; it is repeated here so nobody has
to rediscover it.

`qualification_pair_count` was **not** added to the schema. A field asserting
"exactly one pair" that no mechanism enforces at dispatch time would be intent
wearing the costume of a control, and §16 of the remediation brief forbids
exactly that. `qualification_policy` was added instead, because it is enforced.

---

## 5. Residual trust — unchanged, and not softened

> The authorization accepts GitHub Actions hosted infrastructure as the
> controlled builder substrate. Repository controls pin the workflow bytes,
> action commits, Buildx version, BuildKit linux/amd64 manifest, source commit,
> dependency authority and build configuration, but GitHub remains the external
> authority for the hosted runner image, underlying hardware and execution
> service.

Pinning by SHA constrains what code runs, not what executes it. GitHub-hosted
execution **is not cryptographically reproducible**. Reproducibility here remains
**falsifiable, not proven**: nothing has been built twice.

---

## 6. Scope

Authorizes only `BUILD_A`, `BUILD_B` and their reproducibility comparison, under
the frozen protocol, for the specifically reviewed workflow bytes, source commit
and build configuration.

Does **not** authorize TRAIN access, annotation access, J1 candidate evaluation,
scientific execution, a J1 attempt claim, scientific result visibility, an
environment authority record, artifact promotion, or J1 authorization.

---

## 7. The complete future authorization field table

22 fields — `qualification_policy` was added since V1. Statuses are only
`MACHINE-VERIFIED`, `HUMAN-DECISION-REQUIRED` or `BLOCKED`.

| Field | Resolved value | Source of authority | Verification method | Status |
|---|---|---|---|---|
| `builder_authorization_id` | — | human assignment; no mechanism derives it | none available | HUMAN-DECISION-REQUIRED |
| `builder_candidate_id` | — | composed from the review commit, which does not exist yet | deferred to the merge of this PR | BLOCKED |
| `provider` | `github-actions` | `J1_BUILDER_SELECTION_RECEIPT_V1.md` §2 | read from the committed receipt | MACHINE-VERIFIED |
| `repository` | `DebalekhaChakraborty/CardioSentinel` | git remote | `git remote -v` | MACHINE-VERIFIED |
| `workflow_path` | `.github/workflows/j1-environment-artifact-build.yml` | the controlled-build workflow | compared against `CONTROLLED_BUILD_WORKFLOW_PATH`, which the verifier enforces | MACHINE-VERIFIED |
| `workflow_review_commit` | — | established by the merge of this remediation PR | deferred; a working tree is not a commit | BLOCKED |
| `workflow_sha256` | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` | the workflow bytes on this branch | SHA-256 over raw bytes; re-verified through the real verifier in a seeded repository | MACHINE-VERIFIED |
| `runner_class` | `ubuntu-24.04` | the workflow | literal `runs-on` in the bytes; no `ubuntu-latest` present | MACHINE-VERIFIED |
| `controlled_build_protocol_identity` | `J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2` | the superseding protocol document | derived from the committed path | MACHINE-VERIFIED |
| `controlled_build_protocol_digest` | `3454c4096fe025a5c88f744cc92b15c1975a9ddf3d2e2e59259770b5b4dea412` | raw protocol V2 bytes | SHA-256 over raw bytes | MACHINE-VERIFIED |
| `source_repository` | `DebalekhaChakraborty/CardioSentinel` | git remote | `git remote -v` | MACHINE-VERIFIED |
| `authorized_source_commit` | — | must contain the remediated build inputs, which are not merged yet | deferred to the merge of this PR | BLOCKED |
| `target_platform` | `linux/amd64` | `builder_protocol.TARGET_PLATFORM`, traced to V1 locks | constant, compared against the workflow | MACHINE-VERIFIED |
| `artifact_type` | `oci_single_platform_image_manifest` | `builder_protocol.ARTIFACT_KIND` | constant; the verifier refuses any other value | MACHINE-VERIFIED |
| `base_image_digest` | `python@sha256:c0d63ec61d3a1321f8dc2d46ab6bd38465e005237c0a463712020e5d338eae25` | protocol V2 §6 | present in the protocol; digest-addressed form enforced by `build.sh` and the verifier | MACHINE-VERIFIED |
| `dependency_authority_identity` | `v1-frozen-experiment-lock-335-packages` | `approved_runtime.approved_runtime_fields()` | resolved by calling the authority mechanism | MACHINE-VERIFIED |
| `dependency_digest` | `b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a` | `FROZEN_DEPENDENCY_DIGEST` compiled into V1 | three agreeing readings; the verifier refuses any other value | MACHINE-VERIFIED |
| `build_configuration_digest` | `c9e9b5a636e65957c19103c22d29fdaf7d0dc8b9ed073a2aab146a86b2adf12c` | `controlled_build.configuration_digest` over all seven members | recomputed from two independent generations of the derived inputs | MACHINE-VERIFIED |
| `provenance_destination` | — | derived from `builder_authorization_id` by `durable_evidence_destination` | enforced by the verifier once the id exists | HUMAN-DECISION-REQUIRED |
| `qualification_policy` | `FIRST_AUTHORIZED_QUALIFICATION_RUN_IS_CANONICAL` | `qualification.QUALIFICATION_POLICY` | constant; the verifier refuses any other value | MACHINE-VERIFIED |
| `authorization_timestamp` | — | the moment of the human act | none available | HUMAN-DECISION-REQUIRED |
| `human_authorizer_identity` | — | the human signing | none available | HUMAN-DECISION-REQUIRED |

**15 machine-verified · 4 human · 3 blocked on this PR's merge.**

---

## 8. `HUMAN DECISION REQUIRED` — but not yet

The questions are unchanged from V1 §14 and are **not asked again here**,
because the object is not fully specified. What is being asked for now is
review of the remediation, not authorization of a builder.

When the three blocked fields resolve at merge, the outstanding human questions
will be:

1. Do you approve this exact workflow object as the controlled J1 environment
   builder?
2. Do you accept the disclosed residual GitHub runner, hardware and execution
   trust in §5?
3. Do you accept that the one-pair bound is enforced as **detection at evidence
   preservation**, not prevention at dispatch, with the provider-ordering
   limitation named in §4?
4. What identity should be recorded as `human_authorizer_identity`?
5. What `builder_authorization_id` should be recorded? — it also fixes
   `provenance_destination`.

None of them is answered here.

---

## 9. Negative capability

```text
canonical builder authorization   ABSENT
controlled workflow permission    REFUSED — "builder authorization absent"
BUILD_A / BUILD_B                 UNREACHABLE
image / OCI archive               NONE
environment artifact digest       NONE
environment authority record      NONE
workflow runs at the provider     0
Actions artifacts at the provider 0
```

The J1 scientific protocol, pre-registration, freeze receipt and authorization
contract are **byte-unchanged**. The V1 build protocol and the V1 review packet
are **byte-unchanged** and retained as receipts.

J1 remains **`PRE-REGISTERED — NOT AUTHORIZED`**.
