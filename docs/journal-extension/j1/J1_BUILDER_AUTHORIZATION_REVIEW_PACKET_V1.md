# J1 — Builder Authorization Review Packet, V1

# `READY FOR HUMAN DECISION — BUILDER NOT AUTHORIZED`

**Date:** 2026-09-02
**Prepared against:** `master` at `e310a5b75aa8359301de6f0b26cc1a7b3279bbb5`
**Reviewed builder object:** the workflow merged by **#150**, `675fd765…`
**Scientific interpreter used for every recomputation:** `/home/AI_POC/venvs/tactics/bin/python` — CPython 3.12.6, 335 packages

**No image was built. No artifact digest exists. No builder is authorized. The
controlled-build workflow has never run. No scientific data was accessed.**

---

## 0. What this document is, and what it is not

This packet resolves every **mechanically determinable** field of a future
`J1_BUILDER_AUTHORIZATION_V1.json`, so that the human decision is taken over a
fully specified object rather than over placeholders.

```text
review packet   ≠   builder authorization
```

**This file is not loadable as an authorization.** The runtime loader reads
exactly one path — `docs/journal-extension/j1/J1_BUILDER_AUTHORIZATION_V1.json`
— and that file does not exist. Creating it is a human act, and nothing in this
branch performs it.

Three fields below are deliberately empty. **They are not omissions.** A field
completed after review is a field nobody reviewed, and a plausible string
written into a human field by a machine is the exact failure this programme
exists to prevent.

---

## 1. Preconditions, verified read-only before anything was written

| Condition | Method | Result |
|---|---|---|
| PR #150 merged | `gh pr view 150` | `MERGED` 2026-09-02T18:21:22Z, merge commit `675fd765…` |
| Merge commit on `master` | `git merge-base --is-ancestor` | ancestor of `origin/master` |
| Merged-master CI green | `gh run list --branch master` | `success` at `675fd765…` and at `e310a5b7…` |
| Worktree clean | `git status --porcelain` | empty |
| Frozen protocol digest | SHA-256 over committed bytes | `cedb152eef187fd573212daaad7492242d6963d9b9de897ed1312cde0a976cf0` (42,863 bytes) — **unchanged** |
| Frozen pre-registration digest | SHA-256 over committed bytes | `1b6eb6645bf2449e4b76fb40b5ee7e44250474bd08c4a1c42ba79c00dc45fcd1` (13,658 bytes) — **unchanged** |
| Canonical builder authorization | `git ls-files`, filesystem | **absent** from both the index and the working tree |
| Controlled-build workflow runs | `gh api …/workflows/348674676/runs` | `total_count = 0` |
| Repository Actions artifacts | `gh api …/actions/artifacts` | `total_count = 0` |

Current governance state, unchanged by this branch:

```text
J1                        = PRE-REGISTERED — NOT AUTHORIZED
builder                   = CANDIDATE
builder authorization     = ABSENT
environment artifact      = ABSENT
environment authority     = ABSENT
J1 authorization          = ABSENT
attempt budget            = NOT ESTABLISHED
scientific attempts used  = 0
J1 run directories        = 0
```

---

## 2. Workflow review identity — the reviewed bytes

The authorization names a **file**, not a commit equality. Three independent
digests were taken over the raw bytes, with no YAML parse, no re-render and no
newline normalisation:

| Source of bytes | SHA-256 |
|---|---|
| git object store at `675fd765…` | `32ffdfc28bf8f3044f069190b1f0b15617733487de985f3e0e477ce7af02ec6d` |
| git object store at `origin/master` | `32ffdfc28bf8f3044f069190b1f0b15617733487de985f3e0e477ce7af02ec6d` |
| working-tree checkout | `32ffdfc28bf8f3044f069190b1f0b15617733487de985f3e0e477ce7af02ec6d` |

All three agree, and git resolves the reviewed commit and `origin/master` to the
**same blob object** `5fa12ab9016ee6527583cbeba1d1026eca524b2a` — a stronger
statement than digest equality, because it is git's own identity for the
content. Size 12,490 bytes.

The supplied review commit was **not** taken on trust: `675fd765…` was confirmed
to exist, to be the recorded merge commit of #150, and to contain this path.

---

## 3. Authorized source commit

`675fd7656b333bdf950a63222ecba214d1c4d8b1` — the same commit, verified
mechanically to contain every build-configuration input the frozen protocol
requires:

| Build input | Present at `675fd765…` |
|---|---|
| `containers/j1-environment/Containerfile` | tracked |
| `containers/j1-environment/build.sh` | tracked |
| `containers/j1-environment/validate_artifact.sh` | tracked |
| `.github/workflows/j1-environment-artifact-build.yml` | tracked |
| `reproducibility/…/B4B_cnn_transformer_v1/EXPERIMENT_LOCK.json` (dependency authority) | tracked |

**No later commit is required.** `origin/master` (`e310a5b7…`) differs from the
review commit only in `docs/handoffs/`, which influences no build input.

---

## 4. Controlled build protocol identity

| | |
|---|---|
| Path | `docs/journal-extension/j1/J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V1.md` |
| `controlled_build_protocol_identity` | `J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V1` |
| `controlled_build_protocol_digest` | `e980d0f7b22851a6dadd1158ba979cb95395ebc765c71ce5b068ce55fcb651aa` |
| Byte count | 12,106 |

Computed from committed bytes at the review commit and independently at
`origin/master`; the two agree. **No digest was copied from prose** — the
protocol document does not state its own digest, and could not.

---

## 5. Build configuration digest

Computed with the repository's own canonical implementation —
`controlled_build.configuration_digest`, which delegates to
`builder_protocol.build_configuration_digest`. **No second algorithm was
written.** Every member, with the digest actually fed into the combination:

| Member | Source | SHA-256 |
|---|---|---|
| `containerfile` | committed at `675fd765…` | `44b755cb2f43ad8966c981252b98a6483e9690e5e396de3c9c5866d38d686ee7` |
| `dependency_input` | **generated** — `requirements.pypi.txt` | `550b79b43c28ef2f09468f8a23cdacb34dabb993afc3e176a55bc2091c5506d9` |
| `build_script` | committed at `675fd765…` | `8d3a840dd41d1b3430b0762214e1029ef134ac6145e036a11bae769e2089c54d` |
| `workflow` | committed at `675fd765…` | `32ffdfc28bf8f3044f069190b1f0b15617733487de985f3e0e477ce7af02ec6d` |
| `artifact_validation_script` | committed at `675fd765…` | `84d0f2fae0ded1cc9a77b2c3df6131352446533a4ca44c3b57c256aab5c15a52` |

```text
build_configuration_digest = ff992b1c6381e786d1320290c14c946dcabc91961b88eae5ba362134125aec49
```

The `workflow` member's digest equals the reviewed-bytes digest in §2 — an
internal cross-check that the digested workflow is the reviewed workflow.

**Determinism was demonstrated, not assumed.** The derived dependency input was
generated twice into two separate directories from the frozen lock, and both the
per-file digests and the combined configuration digest were identical.

Derived dependency input, reconstructed from frozen V1 evidence:

```text
PYPI                 332 packages
PYTORCH_CPU_INDEX      2 packages   torch==2.13.0+cpu, torchvision==0.28.0+cpu
FIRST_PARTY_SOURCE     1 package    cardiosentinel (pinned by source commit, not version)
derived_input_digest   46bedd1545722d717c35ea4065258595d4d3eba5cc69cff920463883fe969ce9
```

**Two defects in what this digest covers are recorded as findings F1 and F2 in
§9. They must be answered before signing.**

---

## 6. Runtime and dependency authority

Resolved from the approved runtime authority established in #147 — **imported,
never retyped**:

| Field | Value | Origin |
|---|---|---|
| `python_runtime_identity` | `CPython-3.12.6` | `APPROVED_PYTHON_RUNTIME_IDENTITY` |
| Operating system identity | `Linux-x86_64` | `APPROVED_OPERATING_SYSTEM_IDENTITY` |
| Package population | **335** | `APPROVED_PACKAGE_COUNT`, cross-checked against the frozen lock |
| `dependency_authority_identity` | `v1-frozen-experiment-lock-335-packages` | `approved_runtime_fields()["dependency_lock_identity"]` |
| `dependency_digest` | `b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a` | `FROZEN_DEPENDENCY_DIGEST`, compiled into V1 source |

Three independent readings of the dependency digest agree: the constant V1
compiled, the `installed_packages_sha256` recorded in the frozen B4B experiment
lock, and the live `tactics` interpreter observed by V1's own method.

**No new dependency authority was established.** `verify_builder_authorization`
refuses any authorization naming a `dependency_digest` other than the approved
one, so this field cannot be varied by the authorization at all.

**The `tactics` witness still holds.** Observed digest equals the approved digest
as of this packet. It is a convenience, not the authority: the authority is the
frozen lock and the compiled constant, and both survive the venv.

---

## 7. Base image, build tooling, and target

Every value below was read from the **committed** workflow and the **committed**
protocol and checked for agreement between them. They agree.

### Base image

| | |
|---|---|
| Descriptive tag (metadata only) | `python:3.12.6-slim-bookworm` |
| **Authoritative reference** | `python@sha256:c0d63ec61d3a1321f8dc2d46ab6bd38465e005237c0a463712020e5d338eae25` |
| Object | the **linux/amd64 image manifest**, not the index |
| Index it was resolved from (evidence only) | `sha256:ad48727987b259854d52241fac3bc633574364867b8e20aec305e6e7f4028b26` |

A tag is not authority. An index digest is not authority either: it identifies a
list of manifests, not the image that would execute.

### Build tooling — four identities, not one

| | |
|---|---|
| `setup_buildx_action_commit` | `8d2750c68a42422c14e847fe6c8ac0403b4cbd6f` |
| Buildx version | `v0.36.1` — a settled programme decision, not a recency choice |
| BuildKit authority object | single-platform **linux/amd64 OCI image manifest** |
| BuildKit manifest digest | `sha256:040d34121c27906c4ff9ac152a30d52bf2c5d328d3bb748916bb3d2743c02528` |
| BuildKit index (evidence only) | `sha256:28a898719c18a33f4e8000685287fa36fd0dd9560c6440227d3a732d79bb41d8` |
| `runner_class` | `ubuntu-24.04` — pinned, never `ubuntu-latest` |

Each string was confirmed present **verbatim in the committed workflow bytes**,
not accepted because #150's prose asserts it. No registry was contacted for this
packet, and no image was pulled: every claim above is decidable from committed
evidence.

### Target execution identity

```text
target_platform      linux/amd64
compute              cpu
accelerator          none
libc                 glibc 2.36 (Debian 12 bookworm)
artifact_type        oci_single_platform_image_manifest
artifact_media_type  application/vnd.oci.image.manifest.v1+json
digest algorithm     sha256
```

Traced from frozen evidence, not chosen: all three V1 experiment locks record
`device=cpu`, `cuda_version=None` and `torch==2.13.0+cpu` — a CPU-only wheel that
cannot use CUDA, so a GPU target would change the approved dependency digest.

---

## 8. Provenance destination — `BLOCKED`

# `HUMAN DECISION REQUIRED — the committed documents do not determine this field`

`provenance_destination` is a required, non-defaultable field of the
authorization schema. **No committed document determines a value for it.** The
only occurrence anywhere in the repository is a synthetic string inside a test
fixture, which is evidence about the fixture and about nothing else.

What the merged workflow actually does:

| Question | Answer, read from the committed workflow |
|---|---|
| Where is BUILD_A provenance retained? | GitHub Actions artifact `j1-build-a-provenance`, containing `build-a.json` |
| Where is BUILD_B provenance retained? | GitHub Actions artifact `j1-build-b-provenance`, containing `build-b.json` |
| Where is the reproducibility comparison retained? | **Nowhere durable.** The `reproducibility` job prints `compare-builds` output to the run log and uploads nothing |
| Is that destination temporary or durable? | **Temporary.** GitHub Actions artifacts and run logs both expire under a retention policy that is an account setting, not a repository control |
| What later step preserves qualified evidence beyond that retention? | **No committed document defines one** |

Two further facts the human should have before answering:

- **The built artifacts themselves are never uploaded.** `build.sh` writes
  `build-a.oci.tar` / `build-b.oci.tar` to the runner; only the small JSON
  provenance records are retained. The OCI archives are destroyed with the
  runner.
- **The Environment Authority Record requires an `immutable_artifact_location`.**
  Nothing in the current build path produces one — deliberately, since `build.sh`
  pushes to no registry and no credentials exist.

**This gap is reported, not filled.** A plausible destination string written here
would be a value nobody chose.

---

## 9. Findings that must be resolved before signing

### F1 — the build configuration digest omits a file that changes the image

`REQUIRED_BUILD_CONFIGURATION_INPUTS` provides a single `dependency_input` slot,
but the build materialises **two** requirements files and the Containerfile
copies and installs both. The workflow passes only `requirements.pypi.txt` to
the digest step, so `requirements.pytorch-cpu.txt`
(`a6436381cc2a0315c00c8d4bc80aa47607790dcce709e472b675bffc73ae952b`, pinning
`torch==2.13.0+cpu` and `torchvision==0.28.0+cpu`) is **not covered by
`build_configuration_digest` at all**.

Two builds whose PyTorch pins differed would carry the **same** configuration
digest. The frozen protocol's own §7 states the digest covers *every*
build-affecting file; the implementation covers four of five classes and one of
two files in the fifth.

This is contained today by `require_derived_input_matches_authority`, which
proves the derived mapping is exactly the frozen 335-package set — so the file
cannot currently vary without that check failing first. **The containment is
real but it is a different mechanism than the one the authorization names.**

### F2 — a digest member is a generated, gitignored file

`dependency_input` is not committed. `.gitignore:86` ignores
`containers/j1-environment/requirements.*.txt` deliberately, because the file is
derived from the frozen lock rather than authored. The value is reproducible —
demonstrated twice in §5 — but a strict reading of the build-input rule
("a required build input that is absent or untracked is a stop") is not
satisfied by a file that exists only after a generation step.

The human should decide whether the authorization pins a digest over a file the
repository does not store.

### F3 — the workflow does not re-resolve the base image digest

The workflow comment beside `BASE_IMAGE_DIGEST` reads *"the build re-resolves and
verifies it rather than trusting this file"*, and the protocol's §4 says the
recorded digest "is a resolution, not a commitment" that "must be verified by
recomputation before use". **The committed workflow performs no re-resolution.**
It passes the literal env value to `build.sh`, which passes it to the
Containerfile's `FROM`.

The pinned digest is immutable, so the build is deterministic and the
*reproducibility* claim is unaffected. What is affected is the claim written
beside it. This is prose stronger than code, in a document whose value depends on
those two agreeing.

### F4 — the selection receipt's `builder_candidate_id` names a path that does not exist

`J1_BUILDER_SELECTION_RECEIPT_V1.md` §7 records the candidate id as
`…//.github/workflows/j1-environment-build.yml@PENDING#<pinned runner>`. The
workflow that exists is `j1-environment-artifact-build.yml`. The `@PENDING`
form is deliberate and explained in that receipt; **the filename is a typo**.
The resolved value in §10 below was derived from the repository's own
`ControlledBuilderIdentity.builder_id`, not copied from the receipt.

### F5 — the frozen protocol's §12 is now stale

`J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V1.md` §12 states "No workflow file was
added to the repository" and "A test asserts `ci.yml` remains the only workflow".
Both were true when that document was frozen at `6ed8af52…`; #150 then shipped
the workflow as a separate reviewed act. **The protocol was not modified by this
branch** — it is digest-bound, and correcting it is a separate decision.

---

## 10. The complete future authorization field table

All 21 fields of `BUILDER_AUTHORIZATION_FIELDS`. Status is one of
`MACHINE-VERIFIED`, `HUMAN-DECISION-REQUIRED`, `BLOCKED`. **There is no
`PENDING` status**, because a pending value in an authorization is a value
nobody reviewed.

| Field | Resolved value | Source of authority | Verification method | Status |
|---|---|---|---|---|
| `builder_authorization_id` | — | human assignment; the schema derives nothing | none available | HUMAN-DECISION-REQUIRED |
| `builder_candidate_id` | `github-actions:DebalekhaChakraborty/CardioSentinel//.github/workflows/j1-environment-artifact-build.yml@675fd7656b333bdf950a63222ecba214d1c4d8b1#ubuntu-24.04` | `builder_protocol.ControlledBuilderIdentity` | derived by the repository's own implementation, then passed through `require_specific_builder_identity` | MACHINE-VERIFIED |
| `provider` | `github-actions` | `J1_BUILDER_SELECTION_RECEIPT_V1.md` §2 | read from the committed receipt | MACHINE-VERIFIED |
| `repository` | `DebalekhaChakraborty/CardioSentinel` | git remote and provider API | `git remote -v`, `gh pr view 150` | MACHINE-VERIFIED |
| `workflow_path` | `.github/workflows/j1-environment-artifact-build.yml` | the merged #150 workflow | path exists at the review commit and at `origin/master` | MACHINE-VERIFIED |
| `workflow_review_commit` | `675fd7656b333bdf950a63222ecba214d1c4d8b1` | #150 merge commit | `gh pr view 150` merge commit, confirmed ancestor of `origin/master` | MACHINE-VERIFIED |
| `workflow_sha256` | `32ffdfc28bf8f3044f069190b1f0b15617733487de985f3e0e477ce7af02ec6d` | raw committed workflow bytes | SHA-256 over git blob bytes at the review commit, at `origin/master` and over the checkout; identical blob oid | MACHINE-VERIFIED |
| `runner_class` | `ubuntu-24.04` | the committed workflow | literal `runs-on` in the committed bytes, 5 occurrences, no `ubuntu-latest` | MACHINE-VERIFIED |
| `controlled_build_protocol_identity` | `J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V1` | the committed protocol document | derived from the committed path; the document is digest-bound below | MACHINE-VERIFIED |
| `controlled_build_protocol_digest` | `e980d0f7b22851a6dadd1158ba979cb95395ebc765c71ce5b068ce55fcb651aa` | raw committed protocol bytes | SHA-256 over git blob bytes at the review commit and at `origin/master` | MACHINE-VERIFIED |
| `source_repository` | `DebalekhaChakraborty/CardioSentinel` | git remote | `git remote -v` | MACHINE-VERIFIED |
| `authorized_source_commit` | `675fd7656b333bdf950a63222ecba214d1c4d8b1` | the merged #150 commit | every required build input proven present at that commit; later commits touch only `docs/handoffs/` | MACHINE-VERIFIED |
| `target_platform` | `linux/amd64` | `builder_protocol.TARGET_PLATFORM`, traced to V1 locks | constant compared against the committed workflow | MACHINE-VERIFIED |
| `artifact_type` | `oci_single_platform_image_manifest` | `builder_protocol.ARTIFACT_KIND` | constant; `verify_builder_authorization` refuses any other value | MACHINE-VERIFIED |
| `base_image_digest` | `python@sha256:c0d63ec61d3a1321f8dc2d46ab6bd38465e005237c0a463712020e5d338eae25` | committed workflow `BASE_IMAGE_DIGEST` and protocol §4 | present verbatim in both; digest-addressed form checked by `require_immutable_base_image` | MACHINE-VERIFIED |
| `dependency_authority_identity` | `v1-frozen-experiment-lock-335-packages` | `approved_runtime.approved_runtime_fields()` | resolved by calling the authority mechanism, not retyped | MACHINE-VERIFIED |
| `dependency_digest` | `b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a` | `FROZEN_DEPENDENCY_DIGEST`, compiled into V1 | three agreeing readings: the compiled constant, the frozen lock, the live `tactics` interpreter | MACHINE-VERIFIED |
| `build_configuration_digest` | `ff992b1c6381e786d1320290c14c946dcabc91961b88eae5ba362134125aec49` | `controlled_build.configuration_digest` over committed inputs | recomputed twice from independent generations; see findings F1 and F2 | MACHINE-VERIFIED |
| `provenance_destination` | — | no committed document determines it | none available; see §8 | BLOCKED |
| `authorization_timestamp` | — | the moment of the human act | none available | HUMAN-DECISION-REQUIRED |
| `human_authorizer_identity` | — | the human signing | none available | HUMAN-DECISION-REQUIRED |

**17 machine-verified · 3 human · 1 blocked.**

---

## 11. Residual trust the human is being asked to accept

> The authorization accepts GitHub Actions hosted infrastructure as the
> controlled builder substrate. Repository controls pin the workflow bytes,
> action commits, Buildx version, BuildKit linux/amd64 manifest, source commit,
> dependency authority and build configuration, but GitHub remains the external
> authority for the hosted runner image, underlying hardware and execution
> service.

**Pinning by SHA constrains what code runs. It does not constrain what executes
it.** GitHub-hosted execution is **not** cryptographically reproducible, and
nothing in this packet should be read as claiming otherwise. Reproducibility
here is **falsifiable, not proven**: nothing has been built twice, and the
two-build procedure exists precisely to test a claim that is currently untested.

This residual trust is accepted knowingly, by the human, or not at all.

---

## 12. Scope of the authorization under review

### What it would authorize

```text
BUILD_A
BUILD_B
the reproducibility comparison of the two
```

under the frozen controlled-build protocol, for the specifically reviewed
workflow bytes and the specifically named source commit and build configuration.

### What it would not authorize

```text
TRAIN subject access            annotation access
J1 candidate evaluation         scientific execution
J1 attempt claim                scientific result visibility
environment authority record    J1 authorization
```

A builder authorization is a statement about a build. It creates no data
authority, no attempt budget, and no permission to look at a scientific result.

### It is not open-ended builder authority

It does **not** mean "GitHub Actions may build future J1 environments". It means:

> the specifically reviewed workflow object may perform the specifically defined
> two-build environment qualification for the specifically authorized source
> commit and build configuration.

**The schema enforces most of that boundary, and one part of it is not
enforced.** Recorded plainly rather than reinterpreted:

| Boundary | Enforced by |
|---|---|
| not a provider name | `GENERIC_BUILDER_IDENTITIES` refuses `github actions`, `github`, `actions`, `ci`, … |
| exact workflow bytes | `workflow_sha256` recomputed from git and from the checkout; one differing byte refuses |
| a commit, never a moving ref | 40-hex required for both commit fields |
| exact build inputs | `build_configuration_digest`, subject to findings F1 and F2 |
| the approved runtime | `dependency_digest` must equal the approved digest |
| platform and artifact type | compared against frozen constants |
| **exactly one BUILD_A/BUILD_B pair** | **nothing** |

**There is no build-count bound anywhere in the builder authorization layer.**
No `attempt_budget`, `build_budget` or run-count field exists in
`BUILDER_AUTHORIZATION_FIELDS`, and `workflow_dispatch` may be invoked
repeatedly; once an authorization exists, the gate would pass on every
invocation of the reviewed workflow.

The authorization is therefore bounded in **what** it builds and unbounded in
**how many times**. That is narrower than "GitHub Actions may build anything" and
wider than "one pair". **The human should not assume question 3 below is
enforced by the schema — today it is a statement of intent, not a control.**

---

## 13. Negative capability, at the time this packet was written

```text
canonical builder authorization   ABSENT   (absent from the git index and the working tree)
controlled workflow permission    REFUSED  (gate exits non-zero: "builder authorization absent")
BUILD_A                           UNREACHABLE
BUILD_B                           UNREACHABLE
image                             NONE
OCI archive                       NONE
environment artifact digest       NONE
environment authority record      NONE
workflow runs at the provider     0
Actions artifacts at the provider 0
```

The controlled-build workflow was **not** dispatched. Nothing in this branch can
dispatch it.

---

## 14. `HUMAN DECISION REQUIRED`

These questions are **not** answered in this repository, and were not answered by
the preparation of this packet.

1. **Do you approve this exact GitHub Actions workflow object** — path
   `.github/workflows/j1-environment-artifact-build.yml`, reviewed at
   `675fd7656b333bdf950a63222ecba214d1c4d8b1`, digest
   `32ffdfc28bf8f3044f069190b1f0b15617733487de985f3e0e477ce7af02ec6d`, runner
   class `ubuntu-24.04` — **as the controlled J1 environment builder?**

2. **Do you accept the disclosed residual GitHub runner, hardware and execution
   service trust** stated verbatim in §11?

3. **Do you authorize exactly one BUILD_A/BUILD_B reproducibility pair** under
   the frozen protocol? — noting §12: the schema does not currently enforce a
   build count, so this bound would be intent rather than a control.

4. **What identity should be recorded as `human_authorizer_identity`?**

5. **What `builder_authorization_id` should be recorded?** The schema does not
   derive it; it requires only that it is explicit and not a placeholder.

6. **What `provenance_destination` should be recorded**, given §8 — the
   committed documents determine no value, the current destination is temporary
   GitHub Actions artifact storage, the reproducibility comparison is retained
   nowhere durable, and the OCI archives are not retained at all?

7. **Findings F1–F5 in §9**: are they accepted as-is, or corrected before the
   authorization is signed? F1 and F2 change what
   `build_configuration_digest` actually pins.

---

## 15. What this branch did not do

No image built. No image pushed. No artifact digest created or promoted. No
workflow dispatched. No builder authorized. No `EnvironmentAuthorityRecord`. No
`environment_sha256`. No `J1_AUTHORIZATION_V1`. No attempt budget. No TRAIN
authority. No execution SHA. **No physiological data, annotation or
reference-episode count was accessed**, and no fold, calibrator, threshold,
candidate selection or scientific result was generated.

The J1 scientific protocol, pre-registration, freeze receipt and authorization
contract are **byte-unchanged**, and their digests were recomputed to prove it.

```text
builder candidate  ≠  builder qualified  ≠  builder human-authorized
                   ≠  environment authorized  ≠  J1 execution authorized
```

J1 remains **`PRE-REGISTERED — NOT AUTHORIZED`**.
