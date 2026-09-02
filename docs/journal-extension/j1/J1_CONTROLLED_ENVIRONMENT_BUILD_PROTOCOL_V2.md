# J1 — Controlled Environment Build Protocol, V2

# `FROZEN BUILD CANDIDATE — NOT EXECUTED — BUILDER NOT AUTHORIZED`

**Date:** 2026-09-02
**Supersedes:** [`J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V1.md`](J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V1.md) — `e980d0f7b22851a6dadd1158ba979cb95395ebc765c71ce5b068ce55fcb651aa`, **byte-unchanged**
**Cause:** [`J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V1.md`](J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V1.md) findings F1–F5, plus F6 found while tracing the build-input graph
**Implemented by:** `builder_protocol.py`, `qualification.py`, `controlled_build.py`, `builder_authorization.py`

**No image was built. No artifact digest exists. No workflow was dispatched. No
builder is authorized. No scientific data was accessed.**

---

## 1. Supersession, and why V1's bytes were not touched

V1 was frozen on 2026-09-02 against `master` at `6ed8af52…`. Its §12 says:

> No workflow file was added to the repository. … A test asserts `ci.yml`
> remains the only workflow.

**That was true when it was written and is false now.** #150 shipped
`.github/workflows/j1-environment-artifact-build.yml` as a separate reviewed
act. The contradiction is real and is resolved here rather than hidden:

```text
V1 build protocol frozen                 6ed8af52…   "no workflow exists"  ← true then
        ↓
#150 materializes the workflow           675fd765…   the workflow exists   ← the change
        ↓
#151 adversarial review packet           3835895f…   F1–F5 recorded
        ↓
V2 build protocol (this document)                    supersedes V1 prospectively
```

**Historical accuracy is not repaired by rewriting history.** V1 keeps its
bytes and its digest; a reader who finds its §12 puzzling is meant to arrive
here. Where V1 and V2 disagree, **V2 governs prospectively and V1 remains the
accurate record of what was frozen on its date.**

V1's §1–§11 stand except where a section below explicitly replaces them.

---

## 2. Correction records

Neither correction modifies the bytes of the document it corrects.

### C1 — the builder candidate id names a file that has never existed

| | |
|---|---|
| Document | `J1_BUILDER_SELECTION_RECEIPT_V1.md` §7 |
| Historical recorded value | `github-actions:DebalekhaChakraborty/CardioSentinel//.github/workflows/`**`j1-environment-build.yml`**`@PENDING#<pinned runner>` |
| Correct current value | `.github/workflows/`**`j1-environment-artifact-build.yml`** |
| Reason | transcription error. The workflow shipped by #150 has always carried the longer name; no file of the shorter name exists at any commit |
| Retroactive byte modification | **none** — the receipt is unchanged |

The `@PENDING` element of that same string is **not** an error and is not
corrected: the receipt explains that it is not the authorization and cannot name
the commit that will contain it.

**The correct path is now enforced, not merely written down.**
`builder_authorization.CONTROLLED_BUILD_WORKFLOW_PATH` is the only value
`verify_builder_authorization` accepts for `workflow_path`, so an authorization
copied from the receipt is refused rather than pinning nothing.

### C2 — V1 §4 promised a re-resolution the implementation never performed

| | |
|---|---|
| Document | `J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V1.md` §4, and the merged workflow's `BASE_IMAGE_DIGEST` comment |
| Historical claim | "The build **re-resolves and records**, and the recorded value must be verified by recomputation before use" |
| What the code did | passed a literal digest through to `FROM`. No resolution step existed |
| Resolution | **the claim is withdrawn, not implemented.** See §6 |
| Retroactive byte modification | **none** to V1; the workflow comment is corrected, because the workflow is the object under review and this PR changes its bytes anyway |

---

## 3. The build-input graph

Traced from the Containerfile and build script rather than inherited. Every leaf
capable of changing the produced artifact's bytes, and what binds it.

```text
OCI image manifest bytes
├── base image                         python@sha256:c0d63ec6…
│     └── bound: authorization field base_image_digest, consumed directly
├── Containerfile                      → configuration member  (tracked)
├── Containerfile.dockerignore         → configuration member  (tracked)   [F6]
│     └── decides what `COPY .` puts in a layer
├── requirements.pypi.txt              → configuration member  (derived)
├── requirements.pytorch-cpu.txt       → configuration member  (derived)   [F1]
├── build.sh                           → configuration member  (tracked)
│     └── --platform, --provenance=false, --sbom=false, --no-cache,
│         --output type=oci rewrite-timestamp=true, SOURCE_DATE_EPOCH=0
├── workflow file                      → configuration member  (tracked)
│     └── carries BuildKit image digest, Buildx version, runner class
├── whole source tree at the commit    → bound: authorized_source_commit
│     └── `COPY . /opt/cardiosentinel/src-tree`, then pip install
├── dependency-input generator         → in the source tree; bound by the commit
└── frozen B4B EXPERIMENT_LOCK.json    → in the source tree; bound by the commit
```

Two leaves are bound by a **parent authority** rather than by a configuration
member, and in both cases the parent is a git commit — a Merkle root over the
whole tree, so changing the leaf necessarily changes the parent. That is a
mechanical implication, not an "also validated elsewhere" handwave.

`validate_artifact.sh` is a member although it cannot change the artifact: it
decides whether the artifact is accepted, and an unbound acceptance test is as
consequential as an unbound build step.

### F6 — the build context was unbounded, and would have failed the two-build test

Found while tracing, not reported by #151. There was **no `.dockerignore`**, and
the Containerfile ends with `COPY . /opt/cardiosentinel/src-tree`. The build
context was therefore "whatever is in the runner's working directory", which
includes `.git` — a directory of pack files whose bytes depend on how and when
the clone happened. Two clean checkouts of the *same commit* routinely differ
inside `.git`.

**BUILD_A and BUILD_B would very likely have diverged**, and the two-build
procedure would have reported a reproducibility failure about git's packing
strategy while the environment itself was perfectly reproducible. The finding
would have been real, the diagnosis would have been wrong, and the protocol's
"promote neither, do not rebuild" rule would have stopped the programme on a
false negative.

`containers/j1-environment/Containerfile.dockerignore` now bounds the context
and is a configuration member, so the exclusion set cannot change silently.

---

## 4. Build configuration — replaces V1 §7

V1 named five file classes with a single `dependency_input` slot. That was an
undercount, not an abstraction: the build materialises **two** requirements
files and installs from both, so a change from `torch==2.13.0+cpu` to anything
else left the configuration digest unmoved.

**One canonical digest.** `build_configuration_digest` remains the only
algorithm — no extended variant, no second manifest. What changed is its
membership.

| Role | Path | Status | Authority | Affects bytes |
|---|---|---|---|---|
| `containerfile` | `containers/j1-environment/Containerfile` | tracked | source commit | yes |
| `containerfile_dockerignore` | `containers/j1-environment/Containerfile.dockerignore` | tracked | source commit | yes |
| `dependency_input_pypi` | `containers/j1-environment/requirements.pypi.txt` | derived | frozen lock | yes |
| `dependency_input_pytorch` | `containers/j1-environment/requirements.pytorch-cpu.txt` | derived | frozen lock | yes |
| `build_script` | `containers/j1-environment/build.sh` | tracked | source commit | yes |
| `workflow` | `.github/workflows/j1-environment-artifact-build.yml` | tracked | source commit | yes |
| `artifact_validation_script` | `containers/j1-environment/validate_artifact.sh` | tracked | source commit | no |

Every role is required; a missing one is a refusal, and an undeclared one is
also a refusal — an input held to no rule is worse than an absent one. The CLI
derives one flag per role from the member tuple, so adding a member makes an
un-updated workflow fail loudly rather than digest a smaller set.

---

## 5. `DERIVED_BUILD_INPUT` — replaces V1 §5's informal treatment

#151's F2 observed that a configuration member is generated and gitignored. The
fix is **not** to commit it: a generated file committed by hand is a copy, and a
copy drifts. A derived input is acceptable when it *cannot* differ from the
authority it derives from, which requires all eight of:

```text
generator_pinned_by_source_commit     generator_inputs_authority_bound
generation_is_deterministic           output_sha256_computed
output_matches_frozen_authority       build_consumes_verified_bytes
regeneration_mismatch_hard_fails      output_digest_in_provenance
```

`require_derived_input_properties` refuses unless every one is asserted, and
refuses an unstated property as loudly as a false one.

**Determinism is demonstrated, not declared.** `write_dependency_input`
recomputes the entire grouping from the frozen lock a second time and compares
it against the bytes it just wrote, raising on any difference. Tests generate
into two separate directories and require byte equality.

> If these properties ever cease to hold, the input stops being derived and must
> become an immutable tracked file. That is a decision to take deliberately, not
> a default to fall into.

---

## 6. Base image — replaces V1 §4

| | |
|---|---|
| Descriptive tag, historical metadata only | `python:3.12.6-slim-bookworm` |
| **Authority** | `python@sha256:c0d63ec61d3a1321f8dc2d46ab6bd38465e005237c0a463712020e5d338eae25` |
| Object | the **linux/amd64 image manifest** |
| Index it was resolved from, evidence only | `sha256:ad48727987b259854d52241fac3bc633574364867b8e20aec305e6e7f4028b26` |

> **The build uses the immutable approved base-image manifest digest directly.
> The descriptive tag is retained only as historical metadata and is not
> re-resolved as a prerequisite for execution.**

V1 said the build re-resolves the tag and verifies the result. It did not, and
**it should not**. A tag moves when the upstream image is rebuilt, so
re-resolving it at build time yields one of two outcomes, both wrong: build
something the authorization never named, or fail for a reason with no connection
to this repository. Comparing a mutable tag against a historical digest is a
test of Docker Hub's release schedule.

**What the build does verify** is that the object it consumes is digest-
addressed and is the authorized digest. The digest reaches the build from the
**verified authorization** — `needs.builder-authorization.outputs.base_image_digest`
— not from the workflow's environment block, so there is one authority rather
than two copies that can drift. `build.sh` additionally refuses any reference
that is not `repository@sha256:<64 hex>`, so a tag cannot reach `FROM`.

---

## 7. Provenance — transport is not evidence

V1 required retained provenance without naming a destination, and #151 found
that `provenance_destination` could not be populated at all. Two concepts,
separated:

| | Transient build transport | Durable canonical evidence |
|---|---|---|
| What | GitHub Actions workflow artifacts | this repository, under version control |
| Lifetime | account-level retention policy; expires | permanent, reviewable, digest-addressed |
| Written by | the controlled workflow | a **later human-reviewed evidence PR** |
| Authority | none — it moves bytes | this is the record |

### The canonical destination

```text
docs/journal-extension/j1/evidence/environment-build/<builder_authorization_id>/
```

Mechanically derived by `qualification.durable_evidence_destination`, and
**enforced**: `verify_builder_authorization` refuses any `provenance_destination`
that is not the value this authorization's own id derives. The destination
cannot be chosen after the evidence is in hand.

The durable package must contain:

```text
qualification_claim.json      build_a_provenance.json     build_b_provenance.json
reproducibility.json          build_a.oci.tar.sha256      build_b.oci.tar.sha256
```

**The workflow never commits this.** It has `contents: read` and no token that
could write. Preservation is a human-reviewed pull request, which is the point:
evidence entering the permanent record should be seen by a person.

### Retained transiently by the run

| Artifact | Contents |
|---|---|
| `j1-qualification-claim` | the claim, written before any build |
| `j1-build-a-provenance` / `j1-build-b-provenance` | recomputed artifact digests and build manifests |
| `j1-build-a-oci-archive` / `j1-build-b-oci-archive` | **the OCI archives themselves** |
| `j1-reproducibility-record` | the comparison outcome, uploaded on success *and* on divergence |

V1's workflow discarded the archives and left the comparison in a run log.
Nothing would have survived to become the environment artifact, and the outcome
of the two-build procedure would have expired with the run.

**Archive digest is not artifact identity.** `archive_sha256` is recorded
separately over the tar bytes so a retained archive can be checked end to end.
The environment artifact's identity remains the OCI **image manifest** digest:
two archives of one image differ in tar framing and name the same manifest.

---

## 8. The qualification pair — replaces nothing in V1, because V1 had no rule

#151 found that the authorization bounds *what* may be built and not *which*
BUILD_A/BUILD_B pair is the qualification evidence. Under `workflow_dispatch` an
authorized workflow may be invoked repeatedly, so without a rule the evidence is
whichever pair someone kept — and choosing among pairs after seeing their
digests is exactly the decision the two-build procedure exists to prevent.

# `FIRST AUTHORIZED QUALIFICATION RUN IS CANONICAL`

**The canonical qualification run** is the earliest run, by provider run
ordering, that

1. passed the builder authorization gate, and
2. recorded a qualification claim before any artifact-producing step.

Later runs under the same authorization may execute. Their BUILD_A/BUILD_B
evidence **may never replace** the canonical run's.

### The claim

Recorded by its own job, after the gate and before `build-a`/`build-b`, carrying
`builder_authorization_id`, the frozen policy, provider run id / number /
attempt, `workflow_sha256`, `authorized_source_commit`,
`build_configuration_digest` and a timestamp. The ordering both matters:

- a claim **before** the gate would let an unauthorized run reserve the slot;
- a claim **after** an artifact exists would let a run decide whether to claim
  once it had seen its own result.

`run_attempt` is part of the ordering key because a re-run keeps its `run_id`;
without it, re-running the canonical run after seeing a divergence would produce
a second pair indistinguishable from the first.

### What kind of control this is — stated plainly

**It is detection, not prevention, and the distinction is not a technicality.**

Nothing stops a second dispatch. Under `permissions: contents: read` with no
credentials, GitHub Actions offers this repository no persistent, race-free,
runner-writable store where a first run could leave a lock a second run would
find. The Actions cache is evictable and mutable; artifacts are deletable; a
file on a runner dies with it. **A "lock" built from any of those would be a
process convention wearing the costume of a technical control**, and the
programme is worse off with one of those than with none.

What the provider does supply is an immutable, monotonic, provider-assigned
ordering — `run_id`. Nobody can create a run that sorts before one that already
exists. So the rule is decidable after the fact and cannot be gamed by choosing
which evidence to keep. `require_canonical_qualification_run` refuses any
non-earliest claim's evidence **at the point where evidence becomes durable**.

**The limitation, disclosed rather than papered over:** the ordering, and the
completeness of the run listing the check reads, are GitHub's. Supplying a
filtered subset of claims would defeat the check. That authority is already
inside the residual trust the builder authorization discloses and adds nothing
new — but a reader should not have to rediscover it.

`concurrency: j1-environment-artifact-build` serialises dispatches. That is
ordering hygiene, not the control.

---

## 9. Failure classes — frozen before the first failure

```text
PRE_ARTIFACT_INFRASTRUCTURE   nothing claimed, nothing seen
POST_CLAIM_PRE_ARTIFACT       claim stands, no artifact digest produced
ARTIFACT_VISIBLE              at least one artifact digest has been seen
COMPLETED_QUALIFICATION       both builds completed and were compared
PROTOCOL_VIOLATION            the run did something the protocol forbids
```

**Automatic re-dispatch is permitted for exactly one class:**
`PRE_ARTIFACT_INFRASTRUCTURE`. `require_retry_permitted` refuses the rest.

Past artifact visibility, a retry is a decision taken with knowledge of a
result. **If the canonical run reached artifact visibility and diverged, the
divergence is the finding.** Promote neither digest, do not rebuild until two
agree, and do not reclassify to `NOT_REPRODUCIBLE_DOCUMENTED`. A further attempt
requires explicit human review, and a new authorization and qualification
lineage where the inputs change.

"Rerun until two images match" is the failure mode this table exists to make
unreachable.

---

## 10. Promotion is a later phase

```text
controlled reproducibility build
        ↓
human review of BUILD_A / BUILD_B evidence
        ↓
artifact qualification
        ↓
separate artifact promotion
        ↓
immutable_artifact_location
```

**No registry push, and no credential to perform one.** The workflow's
permissions are `contents: read` and gained nothing in this revision.
Provenance retention was solved by keeping evidence, **not** by acquiring the
ability to push images — a build job that can write to a package registry is a
different trust proposition, and solving a storage problem is not a reason to
accept it.

`immutable_artifact_location` remains unpopulated, and the Environment Authority
Record remains impossible, until promotion happens as its own reviewed act.

---

## 11. What this protocol does not do

No image built. No image pushed. No workflow dispatched. No artifact digest
created or promoted. No build manifest for a real artifact. No environment
promoted. **No builder authorized.** No `EnvironmentAuthorityRecord`, no
`environment_sha256`, no `J1_AUTHORIZATION_V1`, no attempt budget, no TRAIN
authority, no execution SHA, no scientific data accessed.

```text
builder candidate  ≠  builder qualified  ≠  builder human-authorized
                   ≠  environment authorized  ≠  J1 execution authorized
```

J1 remains **`PRE-REGISTERED — NOT AUTHORIZED`**.
