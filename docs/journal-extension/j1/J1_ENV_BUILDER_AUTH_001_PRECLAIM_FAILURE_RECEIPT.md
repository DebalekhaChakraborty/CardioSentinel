# J1 — `J1-ENV-BUILDER-AUTH-001` Pre-Claim Failure Receipt

# `PRE-CLAIM FAILURE — RETRY-ELIGIBLE UNDER ORIGINAL OBJECT, BUT RETIRED BECAUSE THE AUTHORIZED OBJECT IS BEING REMEDIATED`

**Date:** 2026-09-03
**Recorded against:** `master` at `ffe6169fd6a733b908b97c76390801a9c6a63146`

The first — and only — controlled build dispatched under the first human builder
authorization. It failed in its authorization gate, before verifying anything,
before recording a qualification claim, and before any artifact existed.

**No image was built. No qualification claim was recorded. No scientific data
was accessed.**

---

## 1. The authorized run

```text
builder_authorization_id = J1-ENV-BUILDER-AUTH-001
workflow_run_id          = 33800630377
workflow_run_number      = 1
workflow_run_attempt     = 1
failure_class            = PRE_ARTIFACT_INFRASTRUCTURE
claim_recorded           = false
BUILD_A                  = absent
BUILD_B                  = absent
Actions artifacts        = 0
scientific data accessed = no
scientific attempts      = 0
```

| | |
|---|---|
| Dispatch issued | `2026-09-03T20:09:44Z`, exactly once |
| Run created | `2026-09-03T20:09:45Z` |
| Event / ref / head | `workflow_dispatch` · `master` · `ffe6169fd6a733b908b97c76390801a9c6a63146` |
| Run conclusion | `failure` |
| Retired authorization JSON | SHA-256 `86c32cfd4d3e2a48f903f9c61d25dfb377937cd5d9220e4ac9718dd66f84b5e7` |

### Jobs

| Job | Id | Runner | Result | Window (UTC) |
|---|---|---|---|---|
| Builder authorization gate | `100798999349` | GitHub Actions 1000000802, `ubuntu-24.04` | **failure** | 20:09:49 → 20:10:02 |
| Build capability | `100798999734` | GitHub Actions 1000000803, `ubuntu-24.04` | success | 20:09:56 → 20:11:39 |
| Qualification claim | `100799082262` | — | **skipped** | — |
| BUILD_A | `100799608748` | — | skipped | — |
| BUILD_B | `100799609909` | — | skipped | — |
| Reproducibility gate | `100799609827` | — | skipped | — |

The capability job passed: the derived dependency input reconstructed the frozen
authority and the seven-member configuration digest covered every input. **The
build path was capable. The gate could not ask whether it was permitted.**

---

## 2. The failure

```text
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File ".../src/cardiosentinel/journal_extension/j1/builder_authorization.py",
    line 54, in <module>
    from .approved_runtime import APPROVED_DEPENDENCY_DIGEST
  File ".../src/cardiosentinel/journal_extension/j1/approved_runtime.py",
    line 40, in <module>
    from cardiosentinel.neural.p1_experiment import FROZEN_DEPENDENCY_DIGEST
  File ".../src/cardiosentinel/neural/p1_experiment.py", line 27, in <module>
    import numpy as np
ModuleNotFoundError: No module named 'numpy'
##[error]Process completed with exit code 1.
```

**The gate did not refuse. It never loaded.** Steps 1–4 of the job succeeded —
checkout with `fetch-depth: 0`, Python 3.12.14, and the tooling install. Step 5
died during import.

### Both module-scope chains were broken, not only the one in the traceback

```text
approved_runtime -> neural.p1_experiment -> numpy, torch     (line 27, 28)
approved_runtime -> neural.provenance    -> numpy            (line 13)
```

The traceback names the first because Python stops there. The second would have
failed identically. A repair addressed only to the visible line would have moved
the failure one line down.

### Why the environment was right and the code was wrong

The gate job installs `pip install -e "."` — base dependencies, which is
`PyYAML` alone — and its comment says why: *"Workflow tooling only. This is not
the artifact's 335-package set."* That intent is correct. The gate is not the
scientific environment and must not need it.

`approved_runtime` disagreed with that intent by importing
`cardiosentinel.neural` at module scope, to read a 64-hex string constant.

**No test caught it.** Every existing test — including one written specifically
to exercise the gate as a subprocess — ran inside the 335-package `tactics`
interpreter, where numpy is present. CI installs `.[dev,signal,ml,neural,llm]`,
so CI could not catch it either. The only environment where it mattered was the
gate job's minimal one, and nothing exercised that.

---

## 3. Status of `J1-ENV-BUILDER-AUTH-001`

Two statements, both true, and they are not in tension.

> **AUTHORIZATION 001 WAS NOT SPENT BY QUALIFICATION CLAIM**

The claim job was skipped. `require_retry_permitted(PRE_ARTIFACT_INFRASTRUCTURE,
claim_recorded=False)` returns without raising: under Protocol V2 §9 this is the
one class that remains retry-eligible, precisely because nothing was reserved
and no digest was ever seen. The single-claim rule protected the lineage by not
starting it.

> **AUTHORIZATION 001 WILL NOT BE REUSED AFTER SOURCE REMEDIATION**

It authorizes a specific `authorized_source_commit`. Repairing the import
boundary changes the source tree, and the Containerfile ends with
`COPY . /opt/cardiosentinel/src-tree` — **the repository source is image
content**. A build under 001 would check out `1983616f` and reproduce the broken
gate inside the artifact.

So 001 is neither `SPENT` nor `ACTIVE`. Its canonical file is removed from the
working tree in the remediation that accompanies this receipt, so no accidental
second dispatch can use it to check out the superseded source commit. **Its
bytes are not erased**: they remain in git history, in
`J1_BUILDER_AUTHORIZATION_ACT_V1.md`, and by digest above.

`J1-ENV-BUILDER-AUTH-001` will not be reused for the corrected object. The next
authorization takes a new identity, and this receipt does not create it.

---

## 4. What did not happen

```text
second dispatch              NO      run count remains 1
re-run / re-run failed jobs  NO      run_attempt remains 1
local substitute build       NO
BUILD_A / BUILD_B            NONE
environment artifact         ABSENT
environment authority record ABSENT
artifact promoted            NO
J1 scientific authorization  ABSENT
J1 attempt budget            NOT ESTABLISHED
scientific attempts used     0
V1 TRAIN accessed for J1     NO
```

The controlled workflow's bytes are unchanged at
`6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53`. The failure
was in the source the gate imports, not in the workflow, and the repair does not
touch it.

J1 remains **`PRE-REGISTERED — NOT AUTHORIZED`**.
