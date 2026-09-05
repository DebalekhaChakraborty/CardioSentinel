# J1 — V2 Dependency Authority Apparatus Qualification V1

# `APPARATUS QUALIFICATION ONLY — NO DEPENDENCY AUTHORITY ACTIVATED — NO BUILD DISPATCH`

# `THIS DOCUMENT DOES NOT AUTHORIZE THE DEPENDENCY AUTHORITY.`

**Date:** 2026-09-05
**Derived from commit:** `76ebcca9bc618b187434b029de2fa01ece962bf8`
**Candidate under qualification:**

```text
candidate_id  J1-V2-DEPENDENCY-AUTHORITY-CANDIDATE-V2
digest        cb4ec16d399db7c85095ab9a6410afd226092d718b2e45497865aee8c9c2d94f
```

PR #165 bound 47 external dependencies to exact artifact bytes and then could
not qualify the environment it had built, because the only runtime gate J1 had
was V1's. This repairs the apparatus. **It does not rewrite #165's record**: the
blocked candidate file is untouched, and #165 remains the PR that discovered the
blockers.

```text
V2-BLOCKER-1   CLEARED
V2-BLOCKER-2   CLEARED
V2-CHECK-3     RECONCILED TO THE LIMIT OF COMMITTED EVIDENCE
```

---

## 1. The design decision

`APPROVED_RUNTIME` meant *the environment V1's scaffold was built in*. It was
also, by default, the only thing J1 could check a runtime against — so it had
silently come to mean *the environment anything must execute in*. Those are two
different claims and only one of them is a historical fact.

```text
V1 historical runtime   CPython-3.12.6 · Linux-x86_64 · 335 recorded packages
                        digest b0fd6eaa…              approved_runtime
                        immutable evidence, reproduce-only

V2 governed runtime     47 governed external distributions + first-party source
                        checked against an authority the caller supplies
                        v2_runtime_authority
```

**V1 is not upgraded into V2, and V2 does not pretend to be V1.** A V2
environment failing V1's gate is the programme's environment boundary working.

Nothing was renamed underneath a merged receipt. `APPROVED_DEPENDENCY_DIGEST`
and `require_approved_dependencies` keep their names and their meanings, are
documented `V1_HISTORICAL_ONLY`, and now sit beside clearer aliases —
`V1_HISTORICAL_DEPENDENCY_DIGEST`, `require_v1_historical_dependencies` — which
new code should prefer.

---

## 2. V2-BLOCKER-2 — evidence location

### Before

```python
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
APPROVED_DEPENDENCY_DIGEST = _resolve_approved_dependency_digest()   # at import
```

From `site-packages/cardiosentinel/journal_extension/j1/`, those four parents
land on `<venv>/lib/python3.12`. The three establishing locks are not there, the
module-level resolution raised, and five gate modules became unimportable.

### After

The digest is an explicit constant. **The resolution did not become an
assumption; it became a test.** `verify_v1_historical_runtime_evidence(root)`
still reads all three locks, still requires them to agree, and now requires the
agreement to equal the constant — called by a repository test with an explicit
root, because that is where a repository exists.

`REPOSITORY_ROOT` is gone from the module. An audit function called with no root
**refuses**; it does not guess.

### Demonstrated

A fresh venv, `pip install --no-deps` of the tracked source, no scientific stack,
no repository checkout, no `reproducibility/demo_bundle`, no fabricated tree:

```text
reproducibility present beside site-packages?  False
numpy available?                               False

OK  approved_runtime          OK  builder_protocol
OK  build_authority           OK  controlled_build
OK  builder_authorization     OK  v2_runtime_authority

hasattr(approved_runtime, "REPOSITORY_ROOT")   False
verify_v1_historical_runtime_evidence(None)    ApprovedRuntimeError
```

# V2-BLOCKER-2 CLEARED.

---

## 3. V2-BLOCKER-1 — the runtime gate

V1's digest hashes **every installed distribution**, `pip` included — and `pip`
is one of the historical 335. Correct for V1, whose question is *what was
installed*. Wrong for V2, whose question is *are the governed scientific
dependencies exactly what the authority names*.

`governed_dependency_inventory_digest` covers only the authority-declared
external distributions, PEP 503 normalized, sorted, name and exact version.

**Named deliberately weaker than it could be.** An installed name/version
inventory says which distributions are present, never which bytes arrived. The
byte claim stays where #165 put it — the artifact manifest, the wheelhouse
manifest, the hash-locked requirements — and this digest does not stand in for
any of them.

### The key test

Two clean rooms, identical but for the pip bootstrap:

```text
                                    A (network up)        B (network sealed)
pip                                 26.2.1                24.2
governed_dependency_inventory_digest c4f18b4b…            c4f18b4b…      IDENTICAL
substrate_inventory                 {"pip": "26.2.1"}     {"pip": "24.2"}  REPORTED, DIFFERENT
governed package count              47                    47
first-party observed                0.1.0                 0.1.0
```

Under V1's method the same two environments produced **different** identities —
`6f00be4d…` and `c8abc327…` in PR #165. That was the blocker.

# V2-BLOCKER-1 CLEARED.

### Substrate is excluded from identity, not hidden

```text
allowlist (default)   ("pip",)
```

A documented default, not a permanent assumption; the value used is recorded in
every receipt, and a base image that demonstrably ships a different bootstrap
gets a different allowlist passed in. Anything installed that the authority does
not govern, that is not first-party, and that is not on the allowlist is a
**refusal**. Qualification refuses a missing governed member, a wrong governed
version, a duplicated governed member, and an unexpected extra package — each
proven by its own test.

---

## 4. A candidate is not an authority

```text
qualify_v2_dependency_candidate(candidate)   PASS   classification QUALIFICATION_ONLY
require_authorized_v2_runtime(candidate)     REFUSED  V2AuthorityNotAuthorizedError
require_v1_historical_dependencies()         REFUSED  ApprovedRuntimeError
```

All three simultaneously, in both clean rooms. The production gate refuses an
environment that qualifies **perfectly**, because being parseable, complete and
correct is not the same as being authorized, and no human dependency-authority
act exists. A test proves no object anywhere in `docs/journal-extension/j1`
carries `authorization_status = AUTHORIZED`.

The V1 gate was not weakened to let V2 pass. It still refuses, for the right
reason, and its two V1-reproduction tests are **deselected in a V2 clean room,
never deleted** — a test whose purpose is *"this interpreter must equal V1"*
keeps meaning that in the environment it was written for.

---

## 5. Clean-room qualification

```text
install   --no-index --find-links=<wheelhouse> --require-hashes   PASS
          first-party --no-deps --no-build-isolation             PASS
pip check                                                        PASS

installed-runtime import qualification            118 / 118
six direct scientific roots                       numpy 2.3.2 · scipy 1.18.0
                                                  sklearn 1.9.0 · torch 2.13.0+cpu
                                                  wfdb 4.3.1 · yaml 6.0.2
real data paths mounted                           false
```

All 118 reconciled modules import, including the five that refused in #165.

### Test classification (§18)

```text
V1_HISTORICAL_RUNTIME_TEST     marked `v1_historical_runtime`, deselected in a V2 clean room
V2_RUNTIME_AUTHORITY_TEST      run
ENVIRONMENT_NEUTRAL_J1_TEST    run
DATA_BEARING_SCIENTIFIC_TEST   not present in the selected suite; the tree carries no data
```

```text
tests/journal_extension in the V2 clean room:  881 passed · 6 skipped · 2 deselected · 0 failed
PR #165's clean room, for comparison:          854 passed · 6 skipped · 1 failed
```

The 2 deselected are the V1-reproduction tests, named in the run. The 6 skips are
the pre-existing shallow-checkout packet skips (ECG 29), unchanged. **No failure
was converted into a skip.**

### Dependency install replay (§20)

Repeated in a second fresh environment with the network removed
(`unshare -rn`; an outbound connection attempt failed under the seal). Governed
names and versions, governed digest, first-party source identity and artifact
manifest identity all identical; substrate differed and was reported separately.

Classified `DEPENDENCY_INSTALL_REPLAY`. **Not** `BIT_REPRODUCIBLE_ENVIRONMENT` —
no OCI image has been built, once or twice.

---

## 6. V2-CHECK-3 — the closure reconciliation

Full detail in `J1_V2_MODULE_CLOSURE_RECONCILIATION_V1.md`.

**#165's traversal was the defective one.** It followed import statements only,
so it never executed the parent-package edge that `import a.b.c` performs, never
parsed `features/__init__.py`, and never reached `features.morphology` — which
is why it saw 37 external roots where #164 recorded 38.

```text
new external distribution roots      NONE
third-party roots, all three closures numpy · scipy · sklearn · torch · wfdb · yaml
positive residual against #164        NONE on any root
reconciled closure                    118 modules, committed, every one classified
```

**What is not achieved:** an element-by-element comparison against #164's set.
PR #164 committed the count and the per-root site table but **no module list and
no generator**, so that set is not present in any committed artifact and cannot
be recovered — the two closures differ in both directions and no subset
reproduces #164's vector. This document commits the module list so the next
reconciliation has two sets to compare.

```text
V2-CHECK-3 = RECONCILED TO THE LIMIT OF COMMITTED EVIDENCE
```

The mandatory question — *does any discrepancy introduce a new external
distribution root?* — is answered **NO**, positively and by construction. The
47-member artifact-bound set is unaffected and needs no regeneration.

---

## 7. Artifact byte authority, unchanged

Nothing was regenerated. Verified byte-identical at this commit:

```text
artifact-derived package count   48   (47 external + 1 first-party)
PyPI 46 · PyTorch CPU 1 · first-party 1
seed-only [] · artifact-only [] · version conflicts [] · sdist required []

candidate_v2_dependency_authority_digest  cb4ec16d399db7c85095ab9a6410afd226092d718b2e45497865aee8c9c2d94f
```

---

## 8. Readiness

```text
V2-BLOCKER-1 cleared                                        YES
V2-BLOCKER-2 cleared                                        YES
108-vs-113 closure fully reconciled                         NO  — see §6
no new external dependency root                             YES
47 artifact bindings unchanged                              YES
candidate digest unchanged                                  YES
clean-room governed inventory PASS                          YES
substrate difference does not alter the governed digest      YES
installed-package imports PASS                              YES
V2 candidate tests PASS                                     YES
V2 production gate rejects the unapproved candidate         YES
V1 historical gate remains intact                           YES
scientific data access = NO                                 YES
scientific attempts = 0                                     YES
```

# `V2 DEPENDENCY CANDIDATE APPARATUS STILL BLOCKED — REVIEW REQUIRED`

**One item, and it is not an apparatus defect.** Both blockers this task existed
to clear are cleared and demonstrated. What remains is an evidence gap in a
merged PR: #164's module set was never written down, so "fully reconciled"
cannot be asserted against it without inventing the comparison. The honest state
is recorded rather than rounded up.

---

## 9. Governance state at completion

```text
active builder authorization  ABSENT
authorization 004             ABSENT
Environment Authority Record  ABSENT
J1 scientific authorization   ABSENT
J1 attempt budget             NOT ESTABLISHED
J1 scientific attempts        0
scientific data accessed      NO
controlled-build run count    3      (no rerun, no fourth dispatch)
```

No `J1_V2_DEPENDENCY_AUTHORITY_V1.json` was created. No human authorization
timestamp was recorded. The candidate is not described as authorized, approved
or active anywhere.

The builder configuration digest, builder candidate identity and builder
authorization object were **not** regenerated. Changing runtime apparatus will
change the future builder candidate, and that re-derivation belongs after the
dependency authority is explicitly authorized:

```text
#165 evidence -> apparatus remediation -> HUMAN V2 DEPENDENCY-AUTHORITY DECISION
   -> authority materialization -> V6 builder re-derivation
   -> builder authorization 004 -> ONE controlled qualification
```

```text
candidate != authority
```
