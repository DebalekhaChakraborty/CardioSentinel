# CardioSentinel — handoff to session "ECG 29"

Paste this whole file as the first message of the new chat, or say:
"Read `docs/handoffs/CARDIOSENTINEL_HANDOFF_ECG28.md` in the repo and continue.
Remember to use ONLY the tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do **not** use) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/CardioSentinel` |
| Branch at handoff | `master` at `0d2a3d773c63256f6b2a5d03851e11e2827cca46`, clean |

`tactics` holds 335 packages, Python 3.12.6. **Never install, upgrade or
downgrade anything in it.** **Never `git add -A`.**

### The working directory drifts. Prefix every command.

`cd /home/AI_POC/tactics/CardioSentinel &&` in **every** command. It bit me
three times this session. Once it silently swallowed a heredoc that was writing
a test file — the file simply did not appear. Twice `gh` failed with *"none of
the git remotes point to a known GitHub host"*, which is the cheapest tell you
have drifted to `/home/AI_POC`.

Worse: one `ruff check .` ran against the **outer monorepo** instead of
CardioSentinel and returned hundreds of unrelated errors from other projects.
If lint output mentions `adk-*` or `rag_agent`, you are in the wrong directory.

### The symlink existed this session. Check anyway.

```bash
ls -ld /home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal
ln -sfn /home/AI_POC/tactics/CardioSentinel \
        /home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal
```

### Disk is tighter than ECG27 left it

**2.5 GB free at 98%** at handoff, against ECG27's 7.0 GB. The B4 neural path
needs 2,147,483,648 free output bytes, so you are close to the failure ECG26
chased. Clear only pure cache — `~/.cache/pip`, `~/.npm/_cacache`,
`/tmp/pytest-of-*`. **Do not delete `~/.cache/hf-bench` (13 GB)** or the 25 GB
under `cardiosentinel-data/`, `-features/`, `-runs/`.

Full local suite is currently **807 passed** in ~45s:

```bash
pytest tests/neural/test_b4b_sealed_test_identity.py tests/journal_extension tests/reproducibility
```

### The execution guard blocks things, and that is fine

The auto-mode classifier refused several commands this session: invoking
`builder_authorization` as a CLI directly, a heredoc that rewrote source files,
and some `gh`+loop combinations. **Do not route around it.** Use the Edit/Write
tools for files, and let pytest exercise the gate CLI. If it ever blocks
`gh workflow run`, report `DISPATCH BLOCKED BY EXECUTION GUARD — NO DISPATCH
OCCURRED` and stop — the owner explicitly agreed that is safer than an ambiguous
one-shot lineage.

---

## 1. STATE — you are mid-task, and the task is one file

**J1 science is unchanged and still not authorized.** Everything below is about
the *build environment*, not the experiment.

```text
J1                           PRE-REGISTERED — NOT AUTHORIZED
builder authorization        ABSENT   (001 retired; 002 not yet written)
controlled-build runs        1        (33800630377, attempt 1, FAILED pre-claim)
qualification claims         0
Actions artifacts            0
BUILD_A / BUILD_B            NONE
environment artifact         ABSENT
environment authority record ABSENT
J1 attempt budget            NOT ESTABLISHED
scientific attempts used     0
```

### THE IMMEDIATE NEXT ACTION

The owner has instructed: **create `J1-ENV-BUILDER-AUTH-002`.**

**The full hard gate passed.** #156 merged at `0d2a3d77…`, master is that commit,
worktree clean, authorization absent, one run / attempt 1 / zero claims / zero
artifacts, environment authority absent, J1 authorization absent — and
merged-master CI (run `33815076842`) finished **`completed / success`** at the
end of this session. **Nothing blocks the write.**

Re-check the two volatile facts before writing, because time has passed:

```text
controlled-build run history == 1  (still only 33800630377, attempt 1)
qualification claims         == 0
```

If either has moved, STOP — someone dispatched in between.

**This is a transcription, not a decision.** The owner has already answered all
six questions from V4 §12: the object, the residual trust, the single-claim
policy, the id `J1-ENV-BUILDER-AUTH-002`, the identity `DebalekhaChakraborty`,
and environment-qualification-only scope. Word the act receipt the way
`J1_BUILDER_AUTHORIZATION_ACT_V1.md` words it — the human decided, the assistant
recorded, and **the assistant is not the authorizer**.

The 22 fields, all re-derived and verified this session against merged master:

```text
builder_authorization_id            J1-ENV-BUILDER-AUTH-002
builder_candidate_id                github-actions:DebalekhaChakraborty/CardioSentinel//
                                    .github/workflows/j1-environment-artifact-build.yml@
                                    1983616f2021fa5587b7f6cec716501c610e4bf6#ubuntu-24.04
provider                            github-actions
repository                          DebalekhaChakraborty/CardioSentinel
workflow_path                       .github/workflows/j1-environment-artifact-build.yml
workflow_review_commit              1983616f2021fa5587b7f6cec716501c610e4bf6
workflow_sha256                     6bf187e25367a9cdd267f19cec27b0c0bb58dd6cc0142b26d670df3998ad5f53
runner_class                        ubuntu-24.04
controlled_build_protocol_identity  J1_CONTROLLED_ENVIRONMENT_BUILD_PROTOCOL_V2
controlled_build_protocol_digest    3454c4096fe025a5c88f744cc92b15c1975a9ddf3d2e2e59259770b5b4dea412
source_repository                   DebalekhaChakraborty/CardioSentinel
authorized_source_commit            8c7a385ddd60072abaf8fd2cfe493f1cefe12885   <- NOT 1983616f
target_platform                     linux/amd64
artifact_type                       oci_single_platform_image_manifest
base_image_digest                   python@sha256:c0d63ec61d3a1321f8dc2d46ab6bd38465e005237c0a463712020e5d338eae25
dependency_authority_identity       v1-frozen-experiment-lock-335-packages
dependency_digest                   b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a
build_configuration_digest          c9e9b5a636e65957c19103c22d29fdaf7d0dc8b9ed073a2aab146a86b2adf12c
provenance_destination              docs/journal-extension/j1/evidence/environment-build/J1-ENV-BUILDER-AUTH-002/
qualification_policy                FIRST_AUTHORIZED_QUALIFICATION_RUN_IS_CANONICAL
authorization_timestamp             <capture from the UTC clock AT WRITE TIME — never predate, never reuse 001's>
human_authorizer_identity           DebalekhaChakraborty
```

Authority for the decision: `J1_BUILDER_AUTHORIZATION_REVIEW_PACKET_V4.md`,
SHA-256 `0658525ec29c00eef2d0e0eca7009cbc9c8e325fc61d7eef38f1932de8202c13`.

Then: branch `research/j1-builder-authorization-v2`, PR titled *"J1: record
corrected human builder authorization"*, body heading
`BUILDER AUTHORIZED AS 002 — NO BUILD DISPATCHED`. **Do not auto-merge. Do not
dispatch.**

---

## 2. WHAT THIS SESSION DID

Six PRs merged: **#151 → #156**. The programme went from "builder not yet
authorized" through a real authorized build attempt, a failure, a repair, and
back to the edge of a second authorization.

### #151 — the adversarial review packet (V1)

Resolved 17 of 21 machine fields. Its value was the five findings:
**F1** the config digest omitted `requirements.pytorch-cpu.txt`; **F2** a digest
member was generated and gitignored; **F3** the workflow claimed a base-image
re-resolution it never performed; **F4** the selection receipt names a workflow
filename that has never existed; **F5** Protocol V1 §12 stale since #150. Plus
`provenance_destination` **BLOCKED** — the schema required it and nothing
determined it.

### #152 — remediation, and F6

Seven-member configuration model, `DERIVED_BUILD_INPUT` with eight proven
properties, the base-image claim withdrawn rather than implemented, correction
record C1, Protocol **V2** superseding V1 without touching its bytes.

**F6 was found while tracing, not reported by #151, and was the most
consequential.** There was no `.dockerignore` and the Containerfile ends with
`COPY .` — so `.git`, whose pack bytes differ between clones of one commit,
would have entered a layer. BUILD_A and BUILD_B would very likely have diverged,
the protocol would correctly have refused to promote either, and the diagnosis
would have pointed at the environment.

Then adversarial review of the remediation found two more: **R1** the post-claim
retry prose contradicted the canonical identity (fixed by freezing
`THE_CURRENT_BUILDER_AUTHORIZATION_IS_SINGLE_CLAIM`), and **R2** a divergence
produced **no record at all** because compare-and-refuse were one call. Split
into `reproducibility-record` (never raises on divergence) then
`enforce-reproducibility`.

### #153 — V3 packet, `BLOCKED = 0`

### #154 — the human builder authorization 001

### #155 — the pre-claim gate import failure, remediated

**The first authorized dispatch happened, and it failed.** See §3.

### #156 — V4 packet, re-derived against the corrected source

Only one field moved: `authorized_source_commit`.

---

## 3. THE FAILED BUILD — read this before touching the gate

```text
run 33800630377 · run_number 1 · run_attempt 1 · dispatched 2026-09-03T20:09:44Z
gate job FAILED at 13s.  Qualification claim SKIPPED.  BUILD_A/B SKIPPED.
```

```text
builder_authorization.py:54  from .approved_runtime import APPROVED_DEPENDENCY_DIGEST
approved_runtime.py:40       from cardiosentinel.neural.p1_experiment import FROZEN_DEPENDENCY_DIGEST
p1_experiment.py:27          import numpy as np
ModuleNotFoundError: No module named 'numpy'
```

**The gate did not refuse. It never loaded.** The gate job installs
`pip install -e "."` — base deps, `PyYAML` alone — deliberately, because the gate
is not the scientific environment. `approved_runtime` reached through it anyway.

**Both module-scope chains were broken**, not just the one in the traceback:
`p1_experiment` (numpy, torch) and `neural.provenance` (numpy). Python stops at
the first.

**No test could have caught it.** Every test ran in the 335-package `tactics`
interpreter; CI installs `[dev,signal,ml,neural,llm]`. The only environment where
it mattered was the gate job's minimal one, and nothing exercised that.

Fixed in #155 by moving the boundary, **not** by installing the ML extras:
`APPROVED_DEPENDENCY_DIGEST` is now resolved from the three frozen experiment
locks with the standard library, requiring unanimity; `observed_dependency_digest`
imports the neural stack lazily inside the call. Agreement with V1's compiled
`FROZEN_DEPENDENCY_DIGEST` is proven by **`ast`** parsing, never import.

The proof that mattered lives in
`tests/journal_extension/test_j1_approved_runtime_import_boundary.py` (11 tests):
`python -S` with `PYTHONPATH=src`, proving numpy/torch/scipy/sklearn/pandas/wfdb
are unreachable **first**, then that the gate imports and the CLI reaches its own
logic anyway.

### Authorization 001: retired, not spent

Both are true and they are not in tension. No claim was recorded, so
`require_retry_permitted(PRE_ARTIFACT_INFRASTRUCTURE, claim_recorded=False)`
returns without raising. But it names source commit `1983616f`, whose tree
contains the broken gate, and `COPY .` makes the tree image content. Its
canonical file was removed; its bytes survive in git history and in
`J1_ENV_BUILDER_AUTH_001_PRECLAIM_FAILURE_RECEIPT.md`
(`b02e61c14e0384775d586538e9b9dec5ef62a3922177e0dee469f17bb0599460`).

**001 must never be reused.**

---

## 4. THE TRAP THAT WILL CATCH ECG 29

# Every digest except the source commit is identical between V3 and V4.

`approved_runtime.py` is **not** a build-configuration member, so the
seven-member digest is byte-identical to what 001 authorized:
`c9e9b5a6…` before and after the remediation. So is the workflow digest, the
protocol digest and the dependency digest.

A reader comparing configuration digests would conclude nothing changed and
could reuse 001 — and build the broken gate into the artifact.

```text
unchanged build_configuration_digest  ≠  unchanged artifact input
```

The source commit is separately load-bearing. V4 §2 says this at length; do not
let a future packet quietly drop it.

---

## 5. TRAPS (ECG27's still apply — these are new or sharpened)

1. **A test that passes locally proves things about your interpreter.** This is
   the session's whole lesson. The gate failure, and two of my own CI failures,
   were all "the rich environment could answer a question the real one could
   not."
2. **`ci.yml` checks out at default depth.** Any assertion needing a historical
   commit fails there with git error **128 — "Not a valid commit name"**, which
   is *not* an ancestry verdict. Guard with the `_require_commit` pattern and
   skip loudly. **I made this mistake twice**, in #154 and #156.
3. **Grep on a document that explains the thing it forbids will fail.** A
   workflow explaining it has no `packages: write` fails a grep for
   `packages: write`; `approved_runtime.py`'s docstring mentions `numpy`
   repeatedly. **Use AST or the parsed structure.** Recorded six times now.
4. **A markdown table cell wrapped in `**bold**` breaks the packet parser.** The
   parser strips backticks, not asterisks. Cost one CI cycle.
5. **`ast.Assign` is not `ast.AnnAssign`.** `FROZEN_DEPENDENCY_DIGEST` is an
   annotated `Final`; an ad-hoc walk that only handles `Assign` finds nothing and
   reports "0 assignments". The frozen test handles both — trust it over a
   throwaway script.
6. **A prose assertion must normalise whitespace**, or it fails on the line-wrap
   point rather than the claim.
7. **The workflow's own comment can be wrong.** F3 was exactly that: prose
   promising a re-resolution the code never did. Read the code against the
   invariant.
8. **Exit code 1 from the gate means two completely different things.** Run
   33800630377 exited 1 with *"builder authorization absent"* on stderr while
   having crashed during import. Always assert `ModuleNotFoundError` is **not**
   in the output.
9. **`gh pr checks` has no `--json`** (gh 2.23.0); **`gh pr edit` fails
   silently** — use `gh api -X PATCH`; **`grep` is ugrep** and skips gitignored
   paths.
10. **Never `ruff format`.** `ruff check` only.
11. **Poll CI in a background waiter.** Chained short sleeps are blocked; use one
    `sleep N; gh run view ...` with `run_in_background`.

---

## 6. WHAT IS OPEN

```text
authorization 002              <- NEXT, and the owner has already decided it
        v
ONE dispatch of the controlled workflow
        v
qualification claim (canonical, single-claim)
        v
BUILD_A + BUILD_B
        v
reproducibility record  ->  BIT_REPRODUCIBLE or DIVERGED
        v
durable evidence PR (human-reviewed, separate task)
        v
environment authority record
        v
J1_AUTHORIZATION_V1
        v
ONE J1 attempt
```

**Reproducibility is still falsifiable, not proven — nothing has been built
twice.** The first attempt never reached BUILD_A.

Known-unresolved, carried from ECG27:

- **The S3 mirror re-check is still owed and still blocked.**
  `aws sts get-caller-identity` returns session expired. Object Lock retention
  expires 2027-08-22.
- **`tactics` is a witness, not an authority.** It still matches the frozen V1
  environment exactly. One `pip install` destroys that match.

One defect I found and deliberately did **not** fix, because it was outside the
scope the owner set:

> `builder_authorization.main()` prints the fixed headline *"controlled build
> refused: builder authorization absent"* for **every** exception type. When the
> real cause was missing git history, the headline named a missing authorization
> that was sitting right there. One line in `main()`. Ask before changing it —
> it alters gate output that receipts quote.

---

## 7. THE SCIENCE IS UNCHANGED

All fifteen V1 one-shot budgets remain spent. No frozen artifact, attempt
receipt, threshold or experiment identity was touched. **No physiological data,
annotation or reference-episode count was accessed at any point this session.**
No fold, calibrator, threshold, candidate selection or scientific result was
generated. No scientific attempt was claimed.

Frozen and byte-unchanged, verified every session:

```text
J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1  cedb152eef187fd573212daaad7492242d6963d9b9de897ed1312cde0a976cf0
J1_PRE_REGISTRATION_V1                  1b6eb6645bf2449e4b76fb40b5ee7e44250474bd08c4a1c42ba79c00dc45fcd1
J1_FREEZE_RECEIPT_V1                    d116199affdc8488fefc765fee86efcd1aae23dee68b0bd302d4e055b08ee107
J1_AUTHORIZATION_CONTRACT_V1            9aae5a98475444bc8afa50779a4aaf59449a25ae7fbdb8024f4a0d6d8a048d80
```

Retained receipts, never re-pointed: V1/V2/V3/V4 review packets, authorization
act V1, the 001 failure receipt, Protocol V1, Protocol V2, the builder selection
receipt (whose `j1-environment-build.yml` typo stays, by design, and is refused
by the verifier).

RQ4 **Supported (bounded)**. RQ3 a **negative finding**. RQ1, RQ2 (partial),
RQ5, RQ6, RQ7 open — every one needs a run.

---

**The characteristic failure of this session:** *a test that passes tells you
about the environment it ran in.*

ECG27's version was "writing the guarantee in prose and the weaker check in
code." This session's is one layer down and cost a real authorized build. The
gate had a test that ran it as a subprocess. That test passed. It passed in a
335-package interpreter, and the gate runs in a one-package one. CI could not
catch it either, because CI installs the ML extras.

The fix was not a better assertion — it was **running the real thing in the real
shape**: `python -S`, negatives proven first, then the positive. When ECG 29
writes a check, ask *which interpreter, which checkout depth, which permission
set* will actually execute it — and whether the environment you are testing in
can even express the failure you are guarding against.
