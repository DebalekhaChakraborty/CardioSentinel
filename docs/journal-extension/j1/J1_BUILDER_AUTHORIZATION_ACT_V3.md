# J1 — Builder Authorization Act V3

# `BUILDER AUTHORIZED AS 003 FOR ENVIRONMENT QUALIFICATION — NO BUILD DISPATCHED`

**Authorization ID:** `J1-ENV-BUILDER-AUTH-003`  
**Authorization timestamp:** `2026-09-04T22:40:57Z`  
**Human authorizer identity:** `DebalekhaChakraborty`

This receipt records the explicit human authorization instruction given after
review of `J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V5.md`, SHA-256
`f27085c39fe518c315f3f2c405e938d45ab70281a40806635aec8932ca8f1f7a`.

The authorized object is exactly the builder described by the canonical JSON
authorization at `J1_BUILDER_AUTHORIZATION_V1.json` and by the V5 packet. The
human instruction delegated execution of the reviewed authorization decision
while retaining the human authorizer identity above; the assistant/tooling is
not recorded as the human authorizer.

# `THIS AUTHORIZATION APPLIES ONLY TO ENVIRONMENT QUALIFICATION.`

# `THIS IS NOT J1 SCIENTIFIC AUTHORIZATION.`

# `NO CONTROLLED BUILD WAS DISPATCHED BY THIS AUTHORIZATION ACT.`

---

## 1. The decision was taken against a packet with nothing outstanding

V5 established, before this act:

```text
MACHINE-VERIFIED           18
HUMAN-DECISION-REQUIRED     3
HUMAN-DERIVED               1
BLOCKED                     0
```

`BLOCKED = 0` is what made this a decision rather than a deferral. The three
`HUMAN-DECISION-REQUIRED` fields — the id, the timestamp and the authorizer
identity — are supplied by this act and by nothing else.

---

## 2. What was accepted, stated without softening

The authorization accepts, explicitly:

1. **the exact builder object reviewed in V5** — the workflow at
   `.github/workflows/j1-environment-artifact-build.yml`, reviewed at
   `1983616f2021fa5587b7f6cec716501c610e4bf6`, digest `6bf187e2…`, on
   `ubuntu-24.04`, building from source commit
   `bc9337aed38b7ce3f48a47f917a2f4e320e7368a`;
2. **GitHub Actions hosted infrastructure** as the controlled builder substrate;
3. **the disclosed residual trust** in provider runner provisioning, underlying
   hardware, execution service, run identity, run ordering and run-list
   completeness;
4. **the frozen single-claim / canonical qualification policy** —
   `FIRST_AUTHORIZED_QUALIFICATION_RUN_IS_CANONICAL` and
   `THE_CURRENT_BUILDER_AUTHORIZATION_IS_SINGLE_CLAIM`;
5. **terminal treatment of post-claim failure** — once a qualification claim is
   recorded, this authorization is spent whatever follows, exactly as 002 was;
6. **that GitHub-hosted execution is not cryptographically reproducible**;
7. **BUILD_A/BUILD_B as a falsifiable reproducibility test, not a guarantee**;
8. **that exact `name==version` dependency pins are not wheel-byte authority** —
   they fix which distribution is requested, not the bytes that arrive;
9. **the absence of `--require-hashes`, of a wheel-hash manifest and of a
   governed wheelhouse**, so an index serving different bytes for the same name
   and version would be detected by no digest in this authorization;
10. **that `build.sh` and `validate_artifact.sh` are still governed by
    digest and structural controls only**, with no end-to-end executable
    preflight equivalent to the one that now covers the Containerfile's pip
    invocation.

**None of these limitations is softened or omitted.** Items 8, 9 and 10 in
particular are the ones a future reader is most likely to assume away, and they
are accepted as they stand rather than resolved.

---

## 3. Why the source commit is not the #160 merge

```text
authorized_source_commit = bc9337aed38b7ce3f48a47f917a2f4e320e7368a
```

# NOT `709d980d086a0d0a03c8df3473645881f1958a8c`.

V5 machine-verified the corrected build candidate at `bc9337ae`. PR #160 merged
the review packet and its tests; it did **not** redefine the candidate object.
Verified rather than asserted: between `bc9337ae` and the #160 merge, the only
changed paths are

```text
docs/journal-extension/j1/J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V5.md
tests/journal_extension/test_j1_builder_authorization_review_packet.py
```

and `git log bc9337ae..HEAD -- containers/ .github/workflows/
src/cardiosentinel/journal_extension/j1/` is empty. No build input moved.

The controlled workflow must build the exact tree V5 verified. Naming the merge
commit would authorize a source object no packet ever machine-verified — the
class of error that retired `J1-ENV-BUILDER-AUTH-001`.

---

## 4. Machine verification of this authorization

Performed against the document as written, not against the packet:

```text
field set                        exactly the 22 schema fields, no extras
verify_builder_authorization     PASS
verify_workflow_identity         PASS
running_commit_descends_from_review_commit   verified
provenance_destination           equals durable_evidence_destination(
                                   "J1-ENV-BUILDER-AUTH-003")
```

The workflow digest agrees across three independently recomputed sources — the
reviewed commit, the checkout, and the authorization's declared value:
`6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53`.

Every load-bearing value was recomputed from the repository's own mechanisms
before the document was written:

```text
authorized_source_commit          bc9337aed38b7ce3f48a47f917a2f4e320e7368a
workflow_sha256                   6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53
controlled_build_protocol_digest  3454c4096fe025a5c88f744cc92b15c1975a9ddf3d2e2e59259770b5b4dea412
dependency_digest                 b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a
build_configuration_digest        54f40d3136e17d6db11be975b209087d329f30019d9ecaa05cc38e69dda5d80f
base_image_digest                 python@sha256:c0d63ec61d3a1321f8dc2d46ab6bd38465e005237c0a463712020e5d338eae25
```

`authorization_timestamp` was captured from the UTC clock at the moment of this
act. It is not predated, and neither 001's nor 002's timestamp was reused.

---

## 5. Lineage — 003 is a new qualification lineage

```text
001   gate refused, no claim        PRE_ARTIFACT_INFRASTRUCTURE
                                    RETIRED, NOT SPENT

002   claim recorded, builds failed POST_CLAIM_PRE_ARTIFACT
                                    reproducibility_classification = NONE
                                    SPENT, RETIRED, NOT REUSABLE

003   authorized by this act        ACTIVE, AUTHORIZED, UNSPENT
```

**003 is not a retry of 001 or of 002.** `require_retry_permitted` refuses a
retry of 002 and requires all three of: human review, a new
`builder_authorization_id`, and a new qualification lineage. This act supplies
the second; V5 supplied the evidence for the first; the third begins only if a
controlled build is later dispatched under 003.

Canonical qualification is scoped by `builder_authorization_id` in code —
`require_canonical_qualification_run` filters observed claims on
`authorization_id` before taking the earliest — so neither 001's absent claim nor
002's recorded claim can compete with a future 003 canonical run, and a 003 run
cannot inherit 002's claim.

---

## 6. State this act creates, and does not

```text
authorization 003 qualification claim   ABSENT
BUILD_A                                 ABSENT
BUILD_B                                 ABSENT
003 evidence destination                NOT POPULATED
environment artifact                    ABSENT
environment authority record            ABSENT
J1 scientific authorization             ABSENT
J1 attempt budget                       NOT ESTABLISHED
scientific attempts                     0
scientific data accessed                NO
controlled-build runs                   2  (33800630377, 33902875021)
```

**Authorization 003 is authorized but not spent.** It becomes spent only if its
canonical qualification claim is actually recorded by a dispatched run.

The provenance destination
`docs/journal-extension/j1/evidence/environment-build/J1-ENV-BUILDER-AUTH-003/`
is derived by rule and **has not been created**. A prospective path is not
evidence.

## 7. Scope

The authorization scope is **environment qualification only**: authorization
gate, qualification claim, BUILD_A, BUILD_B, reproducibility comparison, and
preservation of their evidence.

It does **not** authorize TRAIN access, validation/test access, external-data
access, reference-episode access, candidate evaluation, threshold selection, a
scientific attempt claim, J1 scientific execution, artifact promotion,
environment authority, or J1 authorization.

No controlled-build workflow was dispatched by this authorization act.
