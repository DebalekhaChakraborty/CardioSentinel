# J1 — `J1-ENV-BUILDER-AUTH-003` Post-Claim Failure Receipt

# `AUTHORIZATION 003 IS SPENT AND MUST NEVER BE REUSED`

# `POST-CLAIM PRE-ARTIFACT FAILURE — DEPENDENCY RECONSTRUCTION — NO RETRY`

**Date:** 2026-09-05
**Recorded against:** `master` at `36e0854c5a74fd5e5a354b2d23dfbe12e9b93b55`

The second controlled build to pass its authorization gate. It recorded the
canonical qualification claim, then failed in **both** independent builds before
either produced an OCI artifact — this time on a dependency that cannot be
resolved from any public index.

**No image was produced. No OCI manifest exists. No reproducibility comparison
was performed. No scientific data was accessed.**

---

## 1. The canonical run

```text
builder_authorization_id       = J1-ENV-BUILDER-AUTH-003
workflow_run_id                = 33984680149
workflow_run_number            = 3
workflow_run_attempt           = 1
head_sha                       = 36e0854c5a74fd5e5a354b2d23dfbe12e9b93b55
authorized_source_commit       = bc9337aed38b7ce3f48a47f917a2f4e320e7368a
dispatched                     = 2026-09-05T18:38:13Z   (one command, never re-issued)

qualification claim            = RECORDED  (claimed_at 2026-09-05T18:38:36Z)
claim canonicality             = VERIFIED
claims_observed under 003      = 1

BUILD_A                        = FAILED PRE-ARTIFACT
BUILD_B                        = FAILED PRE-ARTIFACT
manifest A                     = ABSENT
manifest B                     = ABSENT
OCI archive A                  = ABSENT
OCI archive B                  = ABSENT
BUILD_A provenance             = ABSENT
BUILD_B provenance             = ABSENT
artifact validation            = NOT REACHED
reproducibility record         = ABSENT
reproducibility classification = NONE

failure_class                  = POST_CLAIM_PRE_ARTIFACT
claim_recorded                 = true
authorization_spent            = true

scientific data accessed       = no
scientific attempts            = 0
```

### Terminal job graph

```text
Builder authorization gate   completed / success
Build capability             completed / success
Qualification claim          completed / success
BUILD_A                      completed / failure
BUILD_B                      completed / failure
Reproducibility gate         completed / skipped
```

Exactly one dispatch was issued and no run was ever re-run. All three runs in
the controlled-build history stand at `run_attempt = 1`.

---

## 2. Why this is not a reproducibility outcome

# `reproducibility_classification = NONE`

It is **not** `BIT_REPRODUCIBLE`, **not** `DIVERGED`, and **not**
`ARTIFACT_VISIBLE`. Both builds failed before any image was assembled, so no OCI
manifest existed on either side and there were never two things to compare. The
reproducibility gate did not execute.

It is also **not** `PRE_ARTIFACT_INFRASTRUCTURE`. That class describes 001, whose
gate refused and which recorded no claim. Here the claim had already been
recorded, which is what makes this authorization spent.

```text
J1-ENV-BUILDER-AUTH-001   run 33800630377
  gate refused           -> no claim      -> PRE_ARTIFACT_INFRASTRUCTURE
                                          -> RETIRED, NOT SPENT

J1-ENV-BUILDER-AUTH-002   run 33902875021
  gate admitted, claimed -> builds failed -> POST_CLAIM_PRE_ARTIFACT
                                          -> SPENT, RETIRED

J1-ENV-BUILDER-AUTH-003   run 33984680149
  gate admitted, claimed -> builds failed -> POST_CLAIM_PRE_ARTIFACT
                                          -> SPENT, RETIRED
```

**002 and 003 share a failure class and do not share a cause.** Conflating them
would lose the only thing this run actually established.

---

## 3. Root cause — a dependency that cannot be obtained

Both builds failed at the step `Build the artifact as an OCI layout archive`,
independently, with the identical error:

```text
ERROR: Could not find a version that satisfies the requirement
       incident-management==0.1.0 (from versions: none)
ERROR: No matching distribution found for incident-management==0.1.0
```

`from versions: none` — the configured index offers **no version at all**, not a
different one.

The requirement is line **126** of the generated `requirements.pypi.txt`
(332 lines):

```text
incident-management==0.1.0
```

BUILD_A reached the error at `t+15.97s` and BUILD_B at `t+18.17s`, each after
independently collecting **128** earlier packages. Both failures occur strictly
before manifest digest computation, provenance upload, OCI archive upload,
artifact validation and the reproducibility comparison. **Both logs are retained;
neither was truncated because the other matched.**

---

## 4. The 002 remediation worked — this is a different defect

Run `33902875021` under `J1-ENV-BUILDER-AUTH-002` failed at pip *argument
parsing*, at `t+0.7s`, having installed nothing:

```text
--require-hashes option does not take a value
```

That defect is **absent** from run `33984680149`: the string `--require-hashes`
does not occur anywhere in its logs. pip parsed its arguments, contacted the
index, and resolved 128 packages before stopping.

```text
002 root cause = invalid pip CLI syntax          (apparatus)
003 root cause = dependency-source authority     (reconstruction)
```

**These must not be conflated.** The apparatus repair in #159 did what it
claimed; it moved the failure from the parser to the resolver, which is where the
next defect was waiting.

---

## 5. The requirement is in the historical evidence, not invented by the generator

All three establishing frozen experiment locks were read **without
modification**. Each contains 335 packages and each carries the requirement at
index **127**:

| Lock | SHA-256 | `incident-management` |
|---|---|---|
| `B4B_cnn_transformer_v1` | `5bf251780f469115164d61a3f3cef2eecfc9ef9765af3f544479e961da00e7bc` | index 127, `0.1.0` |
| `P1B_phys_fusion_v1` | `fdde6475a02e0249e0238b89168e6b043b3ade1ec2bfd75922628127fb27d2ca` | index 127, `0.1.0` |
| `M1L_long_memory_v2` | `6aa199ea5410dde860fd3fcce9ceef0194a364ed2ed5b01678e0648fea60a452` | index 127, `0.1.0` |

**The V2 generator did not invent this requirement.** It is present in the
historical environment snapshot from which the generator derives its inputs, and
the generator faithfully emitted it.

### The first-party classifier recognised only one package

The build-source classification treats exactly one distribution as first-party
for this authority — `cardiosentinel`, which the Containerfile installs from the
source tree rather than from an index, and which the generator therefore excludes
from `requirements.pypi.txt`. `incident-management` is not recognised, so it is
emitted as an ordinary index pin.

---

## 6. What this does and does not say about the dependency digest

# `b0fd6eaa…` remains the valid digest of the historical package-list evidence.

The digest is not falsified by this failure. All three locks still agree, still
carry 335 packages, and still hash as they did.

**What the failure demonstrates is narrower and more useful:**

```text
the package-list evidence is not, by itself,
a reconstructible dependency-source authority for V2
```

A list of `name==version` pairs records *what was present*. It does not
establish that each member is *obtainable*, and one member is not. This is the
sharper form of the limitation V5 §12 disclosed: V5 recorded that pins are not
wheel-byte authority — that they fix which distribution is requested rather than
the bytes that arrive. Run `33984680149` shows that for at least one pin, no
distribution is requested successfully at all.

---

## 7. `incident-management` is NOT yet declared extraneous

# `THIS RECEIPT DOES NOT CONCLUDE THAT THE PACKAGE MAY BE REMOVED.`

The available evidence is consistent with contamination from a different project,
and a separate read-only diagnostic
(`J1_ENV_BUILDER_AUTH_003_LOCAL_ORIGIN_DIAGNOSTIC.md`) preserves what was
observed locally. **That is a local observation, not repository-proven
provenance, and it is recorded separately for exactly that reason.**

What this receipt states is only:

```text
incident-management==0.1.0 is an unresolved non-reconstructible member
of the historical V1 environment snapshot.

Its scientific necessity to CardioSentinel has not yet been established.
```

Whether it may be removed, and how a clean V2 dependency authority should be
established, is the next audit's question. Deciding it here — from a build log
and a filesystem observation — would be exactly the shortcut this programme
exists to refuse.

---

## 8. Evidence preserved

The canonical qualification claim, and nothing else, because nothing else exists.

```text
provider artifact id     = 9974785387
provider artifact name   = j1-qualification-claim
provider digest          = sha256:86bb1e8c2f3bc54ed8300aa78b0c9074c7f4d4f3390690c153b4c0757bf44a07
size                     = 544 bytes
expires_at               = 2026-12-04T18:38:16Z
downloaded ZIP sha256    = 86bb1e8c2f3bc54ed8300aa78b0c9074c7f4d4f3390690c153b4c0757bf44a07
contained filenames      = j1-qualification-claim.json
claim JSON sha256        = a1b5e0ac035b1d1cf37e2959466c8b4eb52124c90dbadefad0b42a2d2198df13
claim JSON size          = 569 bytes
```

The downloaded archive hashes to the digest the provider declares, **recomputed
locally rather than accepted**. That is a transport digest — **it is not an OCI
digest, and no OCI digest exists.**

Committed byte-identical at the destination
`durable_evidence_destination("J1-ENV-BUILDER-AUTH-003")` returns:

```text
docs/journal-extension/j1/evidence/environment-build/J1-ENV-BUILDER-AUTH-003/j1-qualification-claim.json
```

### Deliberately absent

No `build-a.json`, no `build-b.json`, no `*.oci.tar`, no reproducibility record.
**They never existed**, and a placeholder for any of them would turn an honest
absence into a false record.

---

## 9. Lifecycle

```text
AUTHORIZED
  -> CANONICAL CLAIM RECORDED
  -> POST_CLAIM_PRE_ARTIFACT FAILURE
  -> SPENT
  -> RETIRED
```

The canonical file `docs/journal-extension/j1/J1_BUILDER_AUTHORIZATION_V1.json`
is removed in the same change that records this receipt. Its exact bytes survive
in git history, in `J1_BUILDER_AUTHORIZATION_ACT_V3.md`, in
`J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V5.md`, in this receipt, and in the
committed claim.

`require_retry_permitted(POST_CLAIM_PRE_ARTIFACT, claim_recorded=True)` refuses,
in the repository's own words: a further attempt requires **all three** of human
review, a new `builder_authorization_id`, and a new qualification lineage.

**003 is not retry-eligible. It is spent.**

---

## 10. What must happen next, and what must not

A further environment-qualification attempt is **blocked on a question this
receipt does not answer**: whether the V1 package-list evidence can serve as a
dependency-source authority at all, and if not, what supersedes it.

**Not done here, and not permitted here:** no edit to any frozen lock, no edit to
`approved_runtime.py`, `builder_protocol.py`, `controlled_build.py`, the
requirements generators, Protocol V2, the Containerfile, `build.sh` or the
workflow. No authorization 004. No dispatch. No rerun.

State after this change:

```text
active builder authorization = ABSENT
authorization 001            = RETIRED, NOT SPENT
authorization 002            = SPENT, RETIRED
authorization 003            = SPENT, RETIRED
Environment Authority Record = ABSENT
J1 scientific authorization  = ABSENT
J1 attempt budget            = NOT ESTABLISHED
scientific attempts          = 0
controlled-build runs        = 3
```
