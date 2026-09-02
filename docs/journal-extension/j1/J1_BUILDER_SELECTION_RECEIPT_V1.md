# J1 — Builder Selection Receipt, V1

# `BUILDER CANDIDATE SELECTED — HUMAN AUTHORIZATION PENDING`

**Date:** 2026-09-02
**Selected against:** `master` at `6ed8af52f74eaf462f836eaa0285fe2105695c8d`
**Governing mechanism:** [`J1_ENVIRONMENT_ARTIFACT_BUILD_AUTHORITY_SPEC_V1.md`](J1_ENVIRONMENT_ARTIFACT_BUILD_AUTHORITY_SPEC_V1.md)
**Build protocol:** [`J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V1.md`](J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V1.md)

**No image was built. No artifact digest exists. No builder is authorized.**

---

## 1. Builders evaluated

Read-only audit of what is actually available to this repository.

| Builder | Verdict |
|---|---|
| **GitHub Actions hosted runner** | **selected as candidate** |
| Existing repository CI (`.github/workflows/ci.yml`) | present, but **not** a build pipeline — it installs Python 3.11 from unpinned ranges and runs lint and tests. It must not be reused: its purpose is to prove code correct, and pinning it for artifact builds would confuse two different jobs |
| Local Docker on this machine | **rejected as authority.** The daemon is unreachable here, but the disqualifying reason is structural: a machine cannot vouch for an artifact it produced. Retained only as a **non-authoritative reference** |
| Jenkins / GitLab CI / Azure Pipelines / Buildkite / CircleCI | **none present.** Connecting one is out of scope for this task |

### Assessment of the selected candidate

| Requirement | GitHub Actions |
|---|---|
| Immutable workflow identity | ✅ workflow file addressed by commit SHA |
| Builder provider identity | ✅ named provider, hosted runner |
| Runner environment identity | ✅ pinned runner label (e.g. `ubuntu-24.04`), not `ubuntu-latest` |
| Pin build tooling | ✅ third-party actions by commit SHA — four resolved in §5 below |
| Pin base image by digest | ✅ the build controls this, not the runner |
| Clean-checkout guarantee | ✅ ephemeral runner, fresh checkout each run |
| Provenance / attestation support | ✅ available; the protocol requires retained provenance regardless |
| Artifact export / storage | ✅ registry push and/or artifact upload |
| Two independent builds from identical inputs | ✅ two separate jobs or runs, no shared cache |
| Reproducibility implications | ⚠️ **unproven.** See §6 |
| Requires trust outside the repository | ⚠️ **yes.** See §6 |

---

## 2. Builder identity model

**"GitHub Actions" is not an identity.** Authorizing that phrase would authorize
every future workflow it covers, including ones written after the review.

The authorizable identity is a **workflow file at a commit, on a named runner
class**:

The authorizable object is the **reviewed workflow file**:

| Field | Value |
|---|---|
| `provider` | `github-actions` |
| `repository` | `DebalekhaChakraborty/CardioSentinel` |
| `workflow_path` | `.github/workflows/j1-environment-artifact-build.yml` |
| `workflow_review_commit` | the historical commit at which the bytes were reviewed |
| `workflow_sha256` | SHA-256 over the **raw committed bytes** at that commit |
| `runner_class` | `ubuntu-24.04` — pinned, **not** `ubuntu-latest` |

### Correction, 2026-09-02: the previous identity rule was unsatisfiable

An earlier version required the running commit to equal a `workflow_commit`
field. **The authorization lives in the repository**, so the commit that adds it
is the commit the workflow then runs at, and the document would have had to
contain the SHA of the commit containing itself. It could never have been
written, and no build could ever have been authorized.

What a human reviews is a **file**, so that is what the authorization names.
The authorization may live in a **later** commit than the workflow — the
ordinary case. Execution from a later commit is permitted **only while the
workflow bytes are unchanged**; one differing byte is a hard refusal.

Two failures, reported separately because they mean different things:
**reviewed historical workflow drift** (the reviewed commit never held those
bytes) and **current workflow differs from the authorized reviewed bytes**.

### Update, 2026-09-02: the workflow has been materialized

`.github/workflows/j1-environment-artifact-build.yml` now exists. The identity a
human can authorize is therefore a real object rather than a description.

**It is inert.** Its only trigger is `workflow_dispatch`, with **no inputs at
all** — an input is a value a caller supplies, and no supplied value may
contribute to authorization. Its first job verifies a builder authorization that
does not exist and exits non-zero; every artifact-producing job depends on that
job. Invoking the workflow is not authorization.

**The workflow still does not name its own commit, and no placeholder was
written into it.** A workflow cannot contain the commit that contains it. The
self-reference is resolved from the other direction: the workflow reports the
identity it is *running as* — `github.workflow_ref` and `github.sha` — and the
authorization must already name exactly that. A run at a commit no human named
is refused.

**The `workflow_commit` field above stays `PENDING` in this receipt** because
this receipt is not the authorization. The merge commit containing the reviewed
workflow bytes binds them externally, and the future authorization names it.

`require_specific_builder_identity` refuses `GitHub Actions`, `github`,
`actions`, `CI`, `the builder`, `build server` and `pipeline` as repository
identities, and refuses a `workflow_commit` that is not a full 40-character SHA.

---

## 3. What the candidate consumes, and what it may not redefine

| | |
|---|---|
| Source checkout | exact commit, clean worktree, no floating ref |
| Build-tool authority | third-party actions pinned by commit SHA |
| **Target runtime authority** | `CPython-3.12.6` and the approved 335-package set, from [`J1_RUNTIME_AND_DEPENDENCY_LOCK_V1.md`](J1_RUNTIME_AND_DEPENDENCY_LOCK_V1.md) — **imported, never retyped** |

### The host is not the target

The runner orchestrates the build under whatever interpreter GitHub provides —
today CI uses Python 3.11. **That does not redefine the target.** What the
artifact must contain is fixed by frozen V1 evidence.

`require_host_does_not_redefine_target` permits a differing host and refuses a
declared *target* that is not the approved runtime. A build that installed the
runner's interpreter, or resolved its own dependency versions, would have
produced something else.

---

## 4. Provenance and reproducibility capability

Provenance is retained per §19 of the build protocol regardless of whether
GitHub's attestation feature is used, because the protocol must not depend on a
provider feature remaining available.

Two independent builds are required. `require_independent_builds` refuses one
build recorded twice, two builds sharing a run identity — a shared cache can
make two invocations agree without the build being reproducible — and a second
build that consumed the first build's artifact, which would reproduce a copy
rather than the build.

---

## 5. Build tooling, resolved to immutable commits

Resolved read-only from the GitHub API on 2026-09-02. Version tags are
descriptive; the SHA is what gets pinned.

| Action | Tag | Immutable commit |
|---|---|---|
| `actions/checkout` | v4 | `11d5960a326750d5838078e36cf38b85af677262` |
| `actions/setup-python` | v5 | `a26af69be951a213d495a4c3e4e4022e16d87065` |
| `docker/setup-buildx-action` | v3 | `8d2750c68a42422c14e847fe6c8ac0403b4cbd6f` |
| `actions/upload-artifact` | v4 | `ea165f8d65b6e75b540449e92b4886f43607fa02` |
| `actions/download-artifact` | v4 | `d3f86a106a0bac45b974a628896c90dbdf5c8093` |

### Four build-tool identities, deliberately not collapsed

**Pinning the action pins the action.** It pins neither the Buildx binary the
action installs nor the BuildKit daemon image that binary starts.

| Identity | Value | Evidence |
|---|---|---|
| `setup_buildx_action_commit` | `8d2750c68a42422c14e847fe6c8ac0403b4cbd6f` | GitHub API, tag `v3` |
| `buildx_version` | **`v0.36.1`** | `docker/buildx` releases API |
| `buildkit_image_digest` | **`sha256:28a898719c18a33f4e8000685287fa36fd0dd9560c6440227d3a732d79bb41d8`** | Docker Hub registry API, tag `buildx-stable-1`, digest recomputed from the fetched bytes |
| `runner_class` | `ubuntu-24.04` | pinned label |

**Why `v0.36.1` and not `v0.37.0`.** `v0.37.0` was published 2026-09-02T17:20Z
— roughly an hour before this was written — and has no field exposure at all.
`v0.36.1` (2026-08-04) is the prior stable release. **This is a judgement, not a
resolution**, and a reviewer who prefers the newest release should say so; both
are authoritative upstream values and the choice is one line.

The BuildKit reference is the **index** digest, not a single-platform manifest.
That is deliberate and is the opposite of the rule for the *artifact*: the
daemon image is a tool the runner pulls for its own platform, whereas the
artifact is the object J1 freezes and executes. Its linux/amd64 manifest is
`sha256:040d34121c27906c4ff9ac152a30d52bf2c5d328d3bb748916bb3d2743c02528`,
recorded as evidence.

These are **recorded resolutions**, not a commitment to use every action. The
workflow author pins from this table or re-resolves and records the new values.

---

## 6. Known limitations — stated, not minimised

1. **Reproducibility is unproven.** Container builds are frequently not
   bit-reproducible: base image layer ordering, build timestamps and
   `apt`/`pip` metadata all commonly vary. The protocol makes the claim
   falsifiable and **stops** on divergence rather than assuming either outcome.
2. **The builder requires trust outside the repository.** GitHub controls the
   runner image, the hosted hardware and the action implementations behind
   those commits. Pinning by SHA constrains *what code runs*; it does not
   constrain *what executes it*. **This is the residual trust the human
   authorization is actually accepting**, and it should be accepted knowingly
   rather than inherited from the fact that the source already lives there.
3. **Network access is required** (§17 of the protocol) — no offline mirror of
   the approved package set exists.
4. **`ubuntu-latest` is mutable.** The runner label must be pinned, and even a
   pinned label is a moving image over long periods.

---

## 7. Status

| | |
|---|---|
| `builder_candidate_id` | `github-actions:DebalekhaChakraborty/CardioSentinel//.github/workflows/j1-environment-build.yml@PENDING#<pinned runner>` |
| Provider | GitHub |
| Builder class | hosted ephemeral runner |
| Builder state | **`CANDIDATE`** |
| Workflow object | **materialized 2026-09-02, inert, manual-only** |
| Machine qualification | mechanism qualified; **no builder instance qualified** |
| **Human authorization status** | **`PENDING`** |

**The single human decision this receipt is asking for:**

> Approve the named controlled builder and workflow as the authorized producer
> of the J1 environment artifact under the frozen build protocol.

**That decision is not performed in code, and no code path in this package
produces `BuilderState.AUTHORIZED`.**

`environment_authority_record = NOT SUBMITTED` · `authorization = ABSENT` ·
J1 = **`PRE-REGISTERED — NOT AUTHORIZED`**
