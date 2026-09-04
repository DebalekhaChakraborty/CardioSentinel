# J1 — Builder Authorization Review Packet, V5

# `READY FOR EXPLICIT HUMAN BUILDER-AUTHORIZATION DECISION`

# `AUTHORIZATION 003 DOES NOT EXIST — NOTHING HERE CREATES IT`

**Date:** 2026-09-04
**Re-derived against:** `master` at `bc9337aed38b7ce3f48a47f917a2f4e320e7368a` — the #159 merge commit
**Supersedes:** `J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V4.md`, whose object was spent

**No builder is authorized by this document.** It resolves every machine-derivable
field of a prospective authorization and stops. The canonical path
`docs/journal-extension/j1/J1_BUILDER_AUTHORIZATION_V1.json` is empty and reading
this does not fill it.

---

## 0. Why there is a V5

V4 described the object that `J1-ENV-BUILDER-AUTH-002` authorized. That
authorization **was spent** — run `33902875021` recorded the canonical
qualification claim — and then both builds failed on a syntax defect inside the
authorized Containerfile. PR #159 repaired the defect, which changed the
Containerfile, which changed the build configuration.

# The authorized object is different. V4 cannot describe it.

V4 is **not** re-pointed at the corrected source. Its bytes remain the record of
what 002 reviewed and what run `33902875021` actually built.

---

## 1. Lineage — three outcomes that must never be conflated

```text
J1-ENV-BUILDER-AUTH-001        run 33800630377 (run 1 / attempt 1)
  gate refused (ModuleNotFoundError: numpy), before verifying anything
  -> claim_recorded = false
  -> failure_class = PRE_ARTIFACT_INFRASTRUCTURE
  -> RETIRED, NOT SPENT

J1-ENV-BUILDER-AUTH-002        run 33902875021 (run 2 / attempt 1)
  gate admitted; canonical qualification claim recorded 2026-09-04T17:52:46Z
  -> claim_recorded = true
  BUILD_A and BUILD_B both failed before producing an OCI manifest
  -> failure_class = POST_CLAIM_PRE_ARTIFACT
  -> reproducibility_classification = NONE
  -> SPENT, RETIRED

PR #159  (merge bc9337ae)
  corrected Containerfile (one line)
  added the executable pip-parser preflight
  -> no authorization, no dispatch, no artifact
```

# 003 IS A NEW QUALIFICATION LINEAGE.

# IT IS NOT A RETRY OF 001 OR OF 002.

# `J1-ENV-BUILDER-AUTH-001` AND `J1-ENV-BUILDER-AUTH-002` MUST NOT BE REUSED.

`require_retry_permitted(POST_CLAIM_PRE_ARTIFACT, claim_recorded=True)` refuses a
retry of 002 in the repository's own words, and requires **all three** of: human
review, a new `builder_authorization_id`, and a new qualification lineage. This
packet supplies only the first ingredient's evidence.

---

## 2. Preconditions, verified read-only before anything was written

| | |
|---|---|
| master | `bc9337aed38b7ce3f48a47f917a2f4e320e7368a`, worktree clean |
| PR #159 | MERGED 2026-09-04T21:51:00Z |
| merged-master CI | run `33922957592` — **completed / success** (4223 passed, 140 skipped) |
| controlled-build runs | **2** — `33800630377` (r1/a1), `33902875021` (r2/a1). No third, no rerun |
| active builder authorization | **ABSENT** |
| 002 canonical claim | preserved, `75716bd8…`, `verify_qualification_claim` PASS |
| Environment Authority Record | ABSENT |
| J1 scientific authorization | ABSENT |
| scientific attempts | 0 |

### Retained receipts, byte-unchanged and never re-pointed

Each carries values or statements that later work superseded. Their bytes record
what was believed and when; re-pointing one at current values would delete the
discrepancy that justified the next round.

| Receipt | SHA-256 |
|---|---|
| `J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V1.md` | `86c298efd424d5dd2e86802d015f3f1d90690c78311cc99c18f6cb8a604243c2` |
| `J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V2.md` | `b1390c3512b37f81966cc226a552dfb0c4673cbcab5aae10735e6ac74059c992` |
| `J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V3.md` | `209cd8689749bdf422d134d974ef0f2a0f286b31478716accce6263c6cb22115` |
| `J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V4.md` | `0658525ec29c00eef2d0e0eca7009cbc9c8e325fc61d7eef38f1932de8202c13` |
| `J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V1.md` | `e980d0f7b22851a6dadd1158ba979cb95395ebc765c71ce5b068ce55fcb651aa` |
| `J1_BUILDER_SELECTION_RECEIPT_V1.md` | `3130fac6e8198fb28fff55682bd93af47f81df921ab5919aafb8d36d42aa58cc` |
| `J1_BUILDER_AUTHORIZATION_ACT_V1.md` | `7643a81062db0b0294c35334a425509aabfc74f6fc834a64afad7afb242528d6` |
| `J1_BUILDER_AUTHORIZATION_ACT_V2.md` | `c37209a901599f76061046049e50adfde8a207a64a10081be1f61d0acd539719` |
| `J1_ENV_BUILDER_AUTH_001_PRECLAIM_FAILURE_RECEIPT.md` | `b02e61c14e0384775d586538e9b9dec5ef62a3922177e0dee469f17bb0599460` |
| `J1_ENV_BUILDER_AUTH_002_POSTCLAIM_FAILURE_RECEIPT.md` | `9dace21e089c3f745cda4452f3c793a57a088a545000d2d30a705a1c5c64daa7` |

**V4 joins them here.** It was the live packet until the authorization it
described was spent by run `33902875021` and the remediation changed the source
tree it names. Its bytes record the object `J1-ENV-BUILDER-AUTH-002` reviewed,
and are not rewritten to the corrected Containerfile.

**`J1_BUILDER_AUTHORIZATION_ACT_V2.md` is retained unedited even though its
headline says no build was dispatched.** That was true when it was written. A
later dispatch does not make the act false; it makes it the record of a moment.

### The candidate source commit contains everything the object needs

Verified present at `bc9337ae` by `git cat-file -e`: the corrected Containerfile,
the executable pip preflight, the ECG 30 handoff, the unchanged controlled
workflow, Protocol V2, and all seven build-configuration inputs.

**The source commit is separately load-bearing.** The Containerfile ends with
`COPY . /opt/cardiosentinel/src-tree` and `Containerfile.dockerignore` does not
exclude `docs/` or `.github/`, so the repository source *is* image content. Two
different source commits are two different artifacts even when every other field
matches — the lesson V4 §2 recorded, and the reason 001 could not be reused.

---

## 3. The corrected Containerfile

```text
containerfile sha256 = a6c914b0f3b57b136c686b521ca53e67653f092ea811b056be3bb2139f254279
```

Recomputed from git's object store at `bc9337ae`, not from the working tree.

```diff
-RUN python -m pip install --no-deps --require-hashes=false \
+RUN python -m pip install --no-deps \
```

The historical defect `--require-hashes=false` is **absent** at the candidate
commit. `--require-hashes` is a boolean flag; giving it a value made pip exit 2
during argument parsing, before installing anything.

**Hash checking was omitted, not disabled a second way.** `--no-require-hashes`
does not exist, and adding `--require-hashes` would demand a hash for every pin —
a different guarantee than the frozen mapping currently provides, and not a
change to make while repairing a syntax defect. Both forms are refused by test.

---

## 4. The boundary that was never crossed, now crossed

**This is the substantive difference between V4 and V5, and it is not a digest.**

V4 proved everything *about* the Containerfile — its SHA-256, its membership in
the build configuration, its presence at the authorized source commit, its `COPY`
lines, its base-image pin. **It did not prove that the command inside it was a
command pip would accept**, because no build had ever executed that layer: run
`33800630377` died in its gate before the `RUN` instruction was reached.

`tests/journal_extension/test_j1_containerfile_pip_invocation.py` executes that
boundary. Against the candidate commit:

```text
23 passed, 0 skipped
```

- All **three** production pip invocations are extracted from the committed
  Containerfile bytes — two in the dependency `RUN`, one installing the source
  tree — never retyped, so no second copy can drift.
- **Option grammar is preserved; only values are replaced.** A requirement path
  becomes a controlled empty file; an index location becomes a `file://` URI of
  an empty directory. Every option the Containerfile writes reaches pip.
- **No external location survives** into any executed argv: `pypi.org`,
  `download.pytorch.org`, `http://` and `https://` are asserted absent, and
  `--no-index` is always present.
- Each of the three parses with **exit 0**.
- **The historical defect is still detected.** `--require-hashes=false` passed
  through the *same sanitizer* is still rejected by pip with
  `--require-hashes option does not take a value`. A sanitizer that erased
  grammar would return a valid command here and the guard would be worthless.
- **Malformed value-taking options fail closed** before pip is invoked: an option
  at the end of a command, one followed by another option
  (`--index-url -r requirements.txt` must not swallow `-r`), one with no defined
  safe test value, and any unknown option all raise.

Nothing is installed, no index is contacted, no image is built.

---

## 5. Reviewed workflow object — deliberately unchanged

```text
workflow_path          = .github/workflows/j1-environment-artifact-build.yml
workflow_review_commit = 1983616f2021fa5587b7f6cec716501c610e4bf6
workflow_sha256        = 6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53
```

| Source | Recomputed digest |
|---|---|
| git at `workflow_review_commit` `1983616f…` | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` |
| git at candidate commit `bc9337ae…` | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` |
| working checkout | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` |

Three sources, byte-identical. **A declared digest is never trusted**; all three
are recomputed. All three resolve to one git blob,
`f3bb13daac12a1d457b2096239b902e29a5cb9ba`.

`1983616f` remains the legitimate review commit. The workflow bytes were reviewed
there and have not changed since. **Reviewing bytes is not building a tree** —
that is why this field may keep a value the `authorized_source_commit` must not.

---

## 6. Protocol V2

```text
controlled_build_protocol_identity = J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2
controlled_build_protocol_digest   = 3454c4096fe025a5c88f744cc92b15c1975a9ddf3d2e2e59259770b5b4dea412
```

Recomputed from the committed bytes. Unchanged from V4.

---

## 7. Frozen dependency authority — unchanged, and re-resolved

The digest is resolved from the three frozen establishing locks with the standard
library, requiring **unanimity**. No majority vote, no fallback literal.

| Establishing lock | Listed | Recorded | Digest |
|---|---|---|---|
| `B4B_cnn_transformer_v1` | 335 | 335 | `b0fd6eaa…` |
| `P1B_phys_fusion_v1` | 335 | 335 | `b0fd6eaa…` |
| `M1L_long_memory_v2` | 335 | 335 | `b0fd6eaa…` |

```text
dependency_digest             = b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a
dependency_authority_identity = v1-frozen-experiment-lock-335-packages
python_runtime_identity       = CPython-3.12.6
operating_system_identity     = Linux-x86_64
```

`require_approved_dependencies()` resolves the same digest from evidence.

### The derived inputs are unmoved by the repair

Regenerated into **two separate directories** and compared byte for byte:

```text
requirements.pypi.txt         identical   550b79b43c28ef2f09468f8a23cdacb34dabb993afc3e176a55bc2091c5506d9
requirements.pytorch-cpu.txt  identical   a6436381cc2a0315c00c8d4bc80aa47607790dcce709e472b675bffc73ae952b
```

Both match the pre-remediation authority exactly. **The repair changed how pip is
invoked, not what it installs.**

---

## 8. Build configuration — recomputed, and exactly one member moved

```text
build_configuration_digest = 54f40d3136e17d6db11be975b209087d329f30019d9ecaa05cc38e69dda5d80f
```

| Role | Status | SHA-256 |
|---|---|---|
| `containerfile` | tracked | `a6c914b0f3b57b136c686b521ca53e67653f092ea811b056be3bb2139f254279` |
| `containerfile_dockerignore` | tracked | `ddb6843539148f5bed1cb764c582abf6e58badf36b513bced7242547c9de3d1b` |
| `dependency_input_pypi` | derived | `550b79b43c28ef2f09468f8a23cdacb34dabb993afc3e176a55bc2091c5506d9` |
| `dependency_input_pytorch` | derived | `a6436381cc2a0315c00c8d4bc80aa47607790dcce709e472b675bffc73ae952b` |
| `build_script` | tracked | `06b1e4568c8228df91217f2c4ddf8b16864c9c9432df0048d53dff2e54b2a7d8` |
| `workflow` | tracked | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` |
| `artifact_validation_script` | tracked | `84d0f2fae0ded1cc9a77b2c3df6131352446533a4ca44c3b57c256aab5c15a52` |

**Only `containerfile` moved.** The other six are byte-identical to what V4
recorded.

`member_count = 7`. Computed with the repository's own `configuration_digest`,
not typed by hand.

```text
V4 configuration : c9e9b5a636e65957c19103c22d29fdaf7d0dc8b9ed073a2aab146a86b2adf12c
V5 configuration : 54f40d3136e17d6db11be975b209087d329f30019d9ecaa05cc38e69dda5d80f
```

**The entire difference is attributable to `containerfile`.** Six of seven members
are byte-identical to what V4 recorded; the seventh is the one-line pip repair.

### Note for whoever reads V4 and V5 side by side

V4 §4 warned that an `unchanged build_configuration_digest` did not imply an
unchanged artifact input, because the source commit is separately load-bearing. **V5 is the
mirror case and needs saying just as plainly:** the configuration digest has
moved, and it has moved for exactly one reason. A second member drifting here
would mean this was not the single-defect repair it claims to be.

---

## 9. Base image and toolchain — unchanged, re-verified

| | |
|---|---|
| Descriptive tag, historical metadata only | `python:3.12.6-slim-bookworm` |
| **Authority** | `python@sha256:c0d63ec61d3a1321f8dc2d46ab6bd38465e005237c0a463712020e5d338eae25` |
| `artifact_type` | `oci_single_platform_image_manifest` |
| Artifact media type | `application/vnd.oci.image.manifest.v1+json` |
| `target_platform` | `linux/amd64` |
| `runner_class` | `ubuntu-24.04` (literal `runs-on`; no `ubuntu-latest`) |
| `setup_buildx_action_commit` | `8d2750c68a42422c14e847fe6c8ac0403b4cbd6f` |
| Buildx | `v0.36.1` — no upgrade |
| BuildKit linux/amd64 manifest | `sha256:040d34121c27906c4ff9ac152a30d52bf2c5d328d3bb748916bb3d2743c02528` |

No upgrades. Read from the committed protocol and the committed workflow.

---

## 10. Qualification policy, and why 001 and 002 do not compete

```text
qualification_policy = FIRST_AUTHORIZED_QUALIFICATION_RUN_IS_CANONICAL
single-claim rule    = THE_CURRENT_BUILDER_AUTHORIZATION_IS_SINGLE_CLAIM
```

Both frozen and unchanged.

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
set would defeat it. That authority is already inside the residual trust in §12.

**002 is the demonstration.** Its claim was recorded and its builds then failed;
no control prevented the dispatch, and none was supposed to. What the mechanism
did was make the outcome undeniable afterwards.

**Canonical qualification is scoped by `builder_authorization_id`, in code.**
`require_canonical_qualification_run` builds `same_authorization` by filtering
`observed_claims` on `authorization_id` before taking the earliest, so the
scoping is a property of the implementation rather than of this sentence.
Demonstrated both ways: 002's earlier claim pooled with a prospective 003 claim
leaves `claims_observed = 1` and 003 canonical, while two claims under the *same*
authorization still refuse the later one — the ordering rule keeps biting where
it should. 001 recorded no claim at all. 002's claim
names `J1-ENV-BUILDER-AUTH-002`. Neither is a claim under a future 003, so
neither competes with a future 003 canonical run — and equally, **a future 003
run cannot inherit 002's claim or reuse its lineage.**

---

## 11. The complete 22-field authorization table

| Field | Candidate value | Authority | Verification | Status |
|---|---|---|---|---|
| `builder_authorization_id` | — | human assignment; the schema derives nothing | none available; constraints in §13 | HUMAN-DECISION-REQUIRED |
| `builder_candidate_id` | `github-actions:DebalekhaChakraborty/CardioSentinel//.github/workflows/j1-environment-artifact-build.yml@1983616f2021fa5587b7f6cec716501c610e4bf6#ubuntu-24.04` | `builder_protocol.ControlledBuilderIdentity` | constructed by the implementation, passed through `require_specific_builder_identity` | MACHINE-VERIFIED |
| `provider` | `github-actions` | `J1_BUILDER_SELECTION_RECEIPT_V1.md` §2 | read from the committed receipt | MACHINE-VERIFIED |
| `repository` | `DebalekhaChakraborty/CardioSentinel` | git remote and provider API | `git remote -v`; generic identities refused | MACHINE-VERIFIED |
| `workflow_path` | `.github/workflows/j1-environment-artifact-build.yml` | the controlled-build workflow | equals `CONTROLLED_BUILD_WORKFLOW_PATH`, enforced by the verifier | MACHINE-VERIFIED |
| `workflow_review_commit` | `1983616f2021fa5587b7f6cec716501c610e4bf6` | the commit at which the bytes were reviewed | unchanged: #159 did not touch the workflow | MACHINE-VERIFIED |
| `workflow_sha256` | `6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53` | raw committed workflow bytes | three sources agree, all recomputed | MACHINE-VERIFIED |
| `runner_class` | `ubuntu-24.04` | the committed workflow | literal `runs-on`; no `ubuntu-latest` | MACHINE-VERIFIED |
| `controlled_build_protocol_identity` | `J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2` | the committed protocol | derived from the committed path | MACHINE-VERIFIED |
| `controlled_build_protocol_digest` | `3454c4096fe025a5c88f744cc92b15c1975a9ddf3d2e2e59259770b5b4dea412` | raw committed protocol bytes | recomputed from disk | MACHINE-VERIFIED |
| `source_repository` | `DebalekhaChakraborty/CardioSentinel` | git remote | `git remote -v` | MACHINE-VERIFIED |
| `authorized_source_commit` | `bc9337aed38b7ce3f48a47f917a2f4e320e7368a` | the #159 merge commit — **moved, see §2 and §8** | every build input and the corrected Containerfile proven present at it | MACHINE-VERIFIED |
| `target_platform` | `linux/amd64` | `builder_protocol.TARGET_PLATFORM`, traced to V1 locks | constant; verifier refuses any other | MACHINE-VERIFIED |
| `artifact_type` | `oci_single_platform_image_manifest` | `builder_protocol.ARTIFACT_KIND` | constant; verifier refuses any other | MACHINE-VERIFIED |
| `base_image_digest` | `python@sha256:c0d63ec61d3a1321f8dc2d46ab6bd38465e005237c0a463712020e5d338eae25` | protocol V2 §6 | present in the committed protocol; digest form enforced by verifier and `build.sh` | MACHINE-VERIFIED |
| `dependency_authority_identity` | `v1-frozen-experiment-lock-335-packages` | `approved_runtime.approved_runtime_fields()` | resolved by calling the authority mechanism | MACHINE-VERIFIED |
| `dependency_digest` | `b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a` | three frozen establishing locks, unanimous | resolved from evidence; 335/335 in each lock | MACHINE-VERIFIED |
| `build_configuration_digest` | `54f40d3136e17d6db11be975b209087d329f30019d9ecaa05cc38e69dda5d80f` | `controlled_build.configuration_digest` over all seven members | recomputed; derived inputs regenerated twice and compared | MACHINE-VERIFIED |
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

**Every field was re-verified against the candidate commit, not carried over from
V4.** Two machine values moved — `authorized_source_commit` and
`build_configuration_digest` — and the check that established each is the same
check either way.

### Machine satisfiability was proven, and it is not authorization

A synthetic document over all 22 fields — unmistakably synthetic id, timestamp
and authorizer, destination derived from the synthetic id, the corrected source
commit — passes `verify_builder_authorization` and `verify_workflow_identity`
with `running_commit_descends_from_review_commit = verified`, while the canonical
path stays empty.

```text
MACHINE SATISFIABLE   yes
AUTHORIZED            no
```

---

## 12. Residual trust — unchanged, and not softened

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

Runs `33800630377` and `33902875021` are both reminders that this list is not
decorative. The first failed inside GitHub's runner image, on its interpreter and
its installed packages. The second failed inside the authorized object itself —
and **reproducibility remains falsifiable rather than tested, because nothing has
ever been built even once.**

The apparatus remediation does not reduce this. It closed one defect inside the
authorized object; it changed nothing about who executes the build.

**What #159 did change is the class of defect that can still reach a dispatch.**
The pip invocation is now executed by a test before it is executed by a builder.
Nothing analogous yet covers `build.sh` or `validate_artifact.sh` end to end —
those are proven by digest and by structure, exactly as the Containerfile was
when 002 was authorized. **That is a disclosed limit, not a resolved one.**

### The pins are name-and-version authority, not wheel-byte authority

# `NO HERMETIC WHEEL-LEVEL REPRODUCIBILITY IS CLAIMED`

`requirements.pypi.txt` and `requirements.pytorch-cpu.txt` are exact
`name==version` pins, mechanically derived from the frozen mapping and proven
byte-identical across regenerations. **That fixes which distribution is
requested. It does not fix the bytes that arrive.**

There is no `--require-hashes` input, no wheel-hash manifest and no local
wheelhouse in this build. What a pin resolves to is whatever the index serves
for that name and version at build time. So:

- an index that served different bytes for the same `name==version` would not be
  detected by any digest in this packet;
- `dependency_digest` `b0fd6eaa…` is authority over the **approved package set**,
  not over the wheel bytes installed;
- `build_configuration_digest` covers the requirements *files*, not their
  resolved artifacts.

This is exactly why the repair omitted the flag rather than turning hash checking
on: **adding `--require-hashes` would demand a hash for every pin, which is a
different and stronger guarantee than the frozen mapping currently supports.**
Supplying that authority — a wheelhouse, or hashes carried in the frozen lock —
is separate work that no one has done, and it must not be implied by silence.

`BUILD_A`/`BUILD_B` is a **falsifiable reproducibility test**, not a guarantee.
Two builds close together in time will usually resolve identical wheels and
agree; that agreement is evidence, and it is not proof of hermeticity.

---

## 13. `HUMAN DECISION REQUIRED`

Not answered here. The expected next identity is **`J1-ENV-BUILDER-AUTH-003`**,
and naming it in this sentence is a statement about numbering, **not an
authorization act**.

1. **Do you authorize this exact builder object** — the workflow at
   `.github/workflows/j1-environment-artifact-build.yml`, reviewed at
   `1983616f…`, digest `6bf187e2…`, on `ubuntu-24.04`, building from
   **`bc9337ae…`**, whose Containerfile is `a6c914b0…`?
2. **Do you accept the disclosed GitHub residual trust** in §12, including run
   ordering, run-attempt identity and run-list completeness?
3. **Do you accept the single-claim qualification policy** — one claim per
   authorization, terminal on any post-claim failure, detection rather than
   dispatch prevention, exactly as it was terminal for 002?
4. **Do you accept the disclosed limit in §12** — that the pip invocation is now
   executed by a test before a builder executes it, while `build.sh` and
   `validate_artifact.sh` are still proven only by digest and structure, which is
   precisely how the Containerfile was proven when 002 was authorized?
5. **What `builder_authorization_id` do you approve?** 3–64 characters, letters,
   digits, dot, underscore or hyphen, starting alphanumeric; it becomes a path
   segment and fixes `provenance_destination`. It **must not** be
   `J1-ENV-BUILDER-AUTH-001` or `J1-ENV-BUILDER-AUTH-002`.
6. **What identity should be recorded as `human_authorizer_identity`?**
7. **Do you approve the scope as environment qualification only** — the gate, one
   claim, BUILD_A, BUILD_B, the reproducibility comparison and its evidence, and
   nothing else?

`authorization_timestamp` is recorded when the act occurs, and is **not**
predated. 002's timestamp must not be reused.

The prospective destination, derived rather than chosen, would be:

```text
docs/journal-extension/j1/evidence/environment-build/J1-ENV-BUILDER-AUTH-003/
```

**That directory has not been created.** A prospective path is not evidence.

### Excluded, as before

```text
TRAIN access                validation / test access      reference episode access
candidate evaluation        threshold selection           scientific attempt claim
J1 execution                environment authority record  artifact promotion
J1 authorization
```

---

## 14. Negative capability

Recorded because it is the point of this document:

```text
active builder authorization   ABSENT
authorization 003              DOES NOT EXIST
controlled-build runs          2   (33800630377, 33902875021 — both attempt 1)
new dispatch                   NONE
environment artifact           ABSENT
environment authority record   ABSENT
J1 scientific authorization    ABSENT
J1 attempt budget              NOT ESTABLISHED
scientific attempts            0
scientific data accessed       NO
```

No workflow was dispatched, no image was built, no OCI archive was produced, and
no qualification claim was recorded in the course of writing this packet. The
frozen protocol, pre-registration, freeze receipt and authorization contract are
byte-unchanged, as are all retained receipts — including V4, both authorization
acts, both failure receipts and the canonical 002 claim.

J1 remains **`PRE-REGISTERED — NOT AUTHORIZED`**.
