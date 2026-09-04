# J1 — `J1-ENV-BUILDER-AUTH-002` Post-Claim Failure Receipt

# `AUTHORIZATION 002 IS SPENT AND MUST NEVER BE REUSED`

# `POST-CLAIM PRE-ARTIFACT FAILURE — NO RETRY, NO RERUN, NO RESUME`

**Date:** 2026-09-04
**Recorded against:** `master` at `8e3f9023ac173bacc5731b476007cad056bf6100`

The second controlled build, and the first ever to pass its authorization gate.
It recorded the canonical qualification claim, then failed in **both** builds
before either produced an artifact.

**No image was produced. No OCI manifest exists. No reproducibility comparison
was ever performed. No scientific data was accessed.**

Unlike `J1-ENV-BUILDER-AUTH-001`, which was retired *without being spent*, this
authorization **is spent**. A claim was recorded under it, and a builder
authorization is single-claim.

---

## 1. The canonical run

```text
builder_authorization_id       = J1-ENV-BUILDER-AUTH-002
workflow_run_id                = 33902875021
workflow_run_number            = 2
workflow_run_attempt           = 1
head_sha                       = 8e3f9023ac173bacc5731b476007cad056bf6100
dispatched                     = 2026-09-04T17:52:26Z
event                          = workflow_dispatch

qualification claim            = RECORDED  (2026-09-04T17:52:46Z)
claim canonicality             = VERIFIED
claims_observed                = 1

BUILD_A                        = failed pre-artifact
BUILD_B                        = failed pre-artifact
manifest A                     = absent
manifest B                     = absent
OCI archive A                  = absent
OCI archive B                  = absent
reproducibility record         = absent / gate skipped

failure_class                  = POST_CLAIM_PRE_ARTIFACT
claim_recorded                 = true
authorization_spent            = true
reproducibility_classification = NONE

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

**Exactly one dispatch was issued and no run was ever re-run.** Both runs in the
controlled-build history stand at `run_attempt = 1`.

---

## 2. Why this is not a reproducibility outcome

# `reproducibility_classification = NONE`

It is **not** `BIT_REPRODUCIBLE` and it is **not** `DIVERGED`.

Both builds failed at the same step, before any image was assembled, so no OCI
manifest was ever produced on either side. There were no two things to compare.
`DIVERGED` would assert that two artifacts existed and disagreed, which is false
and would misdirect every future reader toward a reproducibility investigation
that has nothing to investigate.

It is also **not** `PRE_ARTIFACT_INFRASTRUCTURE`. That class describes 001,
whose gate never admitted and which therefore recorded no claim. Here the claim
had already been recorded when the failure occurred, and that difference is
exactly what makes this authorization spent rather than retryable.

```text
001   gate refused          -> no claim  -> PRE_ARTIFACT_INFRASTRUCTURE -> RETIRED, NOT SPENT
002   gate admitted, claimed -> builds failed -> POST_CLAIM_PRE_ARTIFACT  -> SPENT, RETIRED
```

**The two outcomes must never be conflated.** They differ in the one fact that
determines whether an authorization can ever be used again.

---

## 3. Root cause — a deterministic defect inside the authorized object

Both builds failed at the step `Build the artifact as an OCI layout archive`,
the only failing step in the run, with the identical error:

```text
--require-hashes option does not take a value
```

```text
ERROR: process "/bin/sh -c python -m pip install --no-deps --require-hashes=false
        --index-url https://pypi.org/simple -r requirements.pypi.txt && ..."
        did not complete successfully: exit code: 2
```

The defective line, at the **authorized source commit**
`8c7a385ddd60072abaf8fd2cfe493f1cefe12885`, in
`containers/j1-environment/Containerfile` **line 38**:

```dockerfile
RUN python -m pip install --no-deps --require-hashes=false \
```

`--require-hashes` is a **boolean flag** in pip. It accepts no value, so pip
exits 2 on argument parsing before installing anything at all.

**This is deterministic.** It fails identically on every runner, every attempt,
every time. The symmetry between BUILD_A and BUILD_B is therefore consistent
evidence, not a contradiction: two independent builds reached the same defect
and stopped at the same place.

The Containerfile is a declared `BUILD_CONFIGURATION_MEMBER`, so this defect sits
**inside the authorized configuration**, not beside it. Its blob at the
authorized source commit is
`44b755cb2f43ad8966c981252b98a6483e9690e5e396de3c9c5866d38d686ee7`, the value
`J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V4.md` §7 records for the `containerfile`
member.

### Why review did not catch it

No build had ever executed this layer. Run `33800630377` died in its
authorization gate on a `numpy` import, so the `RUN` instruction had never once
been reached. Every check that existed examined the apparatus *around* the
build — the gate, the digests, the job graph, the trigger model — and every one
of them passed. **The build itself had never run.**

**This receipt does not repair the defect.** It records the failure of that exact
object. Remediation is a separate act requiring a new authorization.

---

## 4. Evidence preserved

The canonical qualification claim, and nothing else, because nothing else exists.

```text
provider artifact id     = 9948308402
provider artifact name   = j1-qualification-claim
provider digest          = sha256:79c9303047d28546df92a7dfb7cbeba4061e8feec79f25284cb6e8d83370ad97
created_at               = 2026-09-04T17:52:47Z
expires_at               = 2026-12-03T17:52:28Z
downloaded ZIP sha256    = 79c9303047d28546df92a7dfb7cbeba4061e8feec79f25284cb6e8d83370ad97
contained filenames      = j1-qualification-claim.json
claim JSON sha256        = 75716bd87552c3a36d2b1f8915778621d2409eac9e66179c13cb1c1b8c6a0236
claim JSON size          = 569 bytes
```

The downloaded archive hashes to the digest the provider declares, recomputed
locally rather than accepted.

**The ZIP digest is a transport digest. It is not an OCI digest, and no OCI
digest exists** — neither build produced a manifest.

Committed, byte-identical to the provider's bytes, at the destination
`durable_evidence_destination("J1-ENV-BUILDER-AUTH-002")` returns:

```text
docs/journal-extension/j1/evidence/environment-build/J1-ENV-BUILDER-AUTH-002/j1-qualification-claim.json
```

The filename is the one the workflow itself uploads
(`path: j1-qualification-claim.json`, matching
`QUALIFICATION_CLAIM_ARTIFACT`), not a name chosen here.

### Deliberately absent

No BUILD_A record, no BUILD_B record, no OCI archive, no reproducibility record
is committed. **They never existed**, and fabricating a placeholder for any of
them would turn an honest absence into a false record.

---

## 5. Lifecycle

```text
AUTHORIZED
  -> CLAIM RECORDED
  -> POST_CLAIM_PRE_ARTIFACT FAILURE
  -> SPENT
  -> RETIRED
```

The canonical file `docs/journal-extension/j1/J1_BUILDER_AUTHORIZATION_V1.json`
is removed in the same change that records this receipt. Its exact bytes survive
in git history, in `J1_BUILDER_AUTHORIZATION_ACT_V2.md`, in
`J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V4.md`, in this receipt, and in the
committed claim above. **Nothing is rewritten to a future value.**

`require_retry_permitted(POST_CLAIM_PRE_ARTIFACT, claim_recorded=True)` refuses,
in the repository's own words:

> retry is not permitted after `POST_CLAIM_PRE_ARTIFACT`, automatically or by
> hand. […] A further attempt requires all three of: human review, a new
> `builder_authorization_id`, and a new qualification lineage. No rerun of the
> same authorization can become qualification evidence.

**002 is not retry-eligible.** It is spent.

---

## 6. What must happen next, and what must not

A further environment-qualification attempt requires **all three**:

1. human review of the remediated object;
2. a **new** `builder_authorization_id` — 003, never 001, never 002;
3. a new qualification lineage.

Remediating the Containerfile changes the `containerfile` member digest and
therefore `build_configuration_digest`, so the authorized object genuinely
changes and a new review packet must be re-derived against the new source commit.

**Not done here, and not permitted here:** no Containerfile change, no rerun, no
dispatch, no authorization 003, no environment authority record, no promotion of
anything.

State after this change:

```text
active builder authorization = ABSENT
authorization 001            = RETIRED, NOT SPENT
authorization 002            = SPENT, RETIRED
Environment Authority Record = ABSENT
J1 scientific authorization  = ABSENT
J1 attempt budget            = NOT ESTABLISHED
scientific attempts          = 0
controlled-build runs        = 2
```
