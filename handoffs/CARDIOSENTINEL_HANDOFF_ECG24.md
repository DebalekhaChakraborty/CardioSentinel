# CardioSentinel — handoff to session "ECG 25"

Paste this whole file as the first message of the new chat, or say:
"Read handoffs/CARDIOSENTINEL_HANDOFF_ECG24.md in the repo and continue.
Remember to use ONLY the tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do NOT use) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| Branch | `feat/e11-e13a-instrumentation-and-paper-readiness` |
| GitHub | `DebalekhaChakraborty/CardioSentinel`, PR #128 open |

`tactics` holds 335 packages, Python 3.12.6. **Never install, upgrade or
downgrade anything in it.** **The Bash working directory silently resets** — put
`cd` in the same command as the work. **Never `git add -A`.**

---

## 1. THE ONE THING THAT MATTERS — RESOLVED 2026-08-28

**The reorganisation is finished and the tree is green.** Option A of §3 was
applied in full.

```
ruff check .        All checks passed!
pytest tests        3542 passed, 1 skipped, 0 failed     (18:01)
```

The 16 failures were one thing — the T1 execution sources are frozen by
SHA-256 and four of them had been repointed — and §3 records how it was closed.
Nothing scientific was wrong at any point. No result changed. No evidence was
lost.

---

## 2. WHAT WAS BEING DONE, AND WHY IT WENT WRONG

The owner asked for `docs/` to be organised into folders instead of 127 flat
files. That is cosmetic. **The coupling is not**, and I discovered it one layer
at a time instead of up front. In order:

1. **48 documents are addressed by path from `src/`, `tests/`, `scripts/`.**
   Four different construction forms, each found only after the previous fix:
   literal `"docs/NAME"`, `"docs" / "NAME"`, `DOCS / "NAME"`, and
   `"docs" / f"{NAME}.md"`.
2. **8 documents are named by path inside immutable artifacts** under
   `cardiosentinel-runs/`, including the sealed `TEST_ATTEMPT.json` and
   `TEST_AUDIT.json`. Those cannot be edited. Handled by a translation table
   (§4), not by rewriting evidence.
3. **~37 documents are content-digest-frozen.** I rewrote paths *inside* them
   and broke `sha256(document)` assertions. Restored byte-identical from HEAD.
   **Never edit the content of a document under `docs/`; only move it.**
4. **The T1 execution sources are themselves SHA-frozen.** Closed by leaving
   the seven T1 documents flat. See §3.

**Three mistakes of mine that cost the most time, recorded so they are not
repeated:**

- **I ran `ruff format` repo-wide.** This repo is ruff-*checked*, not
  ruff-*formatted* — CI is `python -m ruff check .`. The format pass reflowed
  **128 unrelated files** and turned a dict of sealed-test SHA-256 constants in
  `m1_experiment.py` into over-length lines. **Never run `ruff format` here.**
- **I twice broke syntax with heuristic line-wrapping** — splitting a `lambda`
  across lines, and turning `==` into `=(` + `=`. Any rewrap must be
  AST-checked before it is written.
- **I rewrote paths inside four historical handoffs and three superseded
  handbook versions.** Reverted; all are byte-identical to HEAD again. History
  is preserved and corrections go in the current control plane.

---

## 3. THE T1 BLOCKER — CLOSED, OPTION A

`tests/neural/test_t1_*.py` assert that named files under
`src/cardiosentinel/neural/` are **byte-identical to a frozen SHA-256**:

```python
path = REPOSITORY_ROOT / "docs" / "experiments" / "t1" / name
assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
```

Four of them had been repointed at `docs/experiments/t1/`. **That guard is
working correctly, not failing:** the T1 canonical driver's source is frozen on
purpose, and a correct path fix is still a byte change. Amending the digests
needs a human authorisation and an amendment document — the route
`T1_EXECUTION_RECOVERY_AMENDMENT_V1_1.md` took — and tidying a directory does
not justify one.

**What was done instead:**

1. Reverted the four T1 sources to HEAD:
   `t1_development_run.py`, `t1_execution_spec.py`, `t1_protocol.py`,
   `t1_recovery_amendment.py`.
2. Moved the seven T1 documents back to flat `docs/` with `git mv`. All seven
   were byte-identical to HEAD before and after the move.
3. Repointed the remaining `docs/experiments/t1/` references in non-frozen
   files: `README.md`, `paper/figures/README.md`, `scripts/provenance/README.md`,
   both `gen_t1_*.py`, and `tests/neural/test_t1_canonical_driver.py`. Both
   `gen_t1_*.py` and the test are byte-identical to HEAD again.
4. Removed the seven T1 rows from
   `docs/provenance/DOCUMENT_PATH_TRANSLATION_V1.md` and added a section saying
   T1 was deliberately not moved, and why. `docs/README.md` says the same.

**Fourteen of fifteen categories hold. T1 is flat, with the reason recorded in
two places.** If T1 source ever has to change for a scientific reason, move the
seven documents in that same amendment and add their rows to the table.

---

## 4. WHAT IS DONE AND GOOD

**Repository layout** — four categories hoisted to the root, `docs/` organised
into 14 folders, with T1 flat for the reason in §3:

```
paper/      31   manuscript, drafts, figures, tables, submission metadata
audits/      6   readiness audit, Related Work V1/V2, format review, handoff, requirements
handbook/   10   all handbook versions, .md and .docx
handoffs/   22   ECG3-ECG24
docs/      103   experiments/{b4,m1,m2,p1,t2,u1,w1}, contracts, control-plane,
                 provenance, explanation, external-validation, literature,
                 baselines, and the seven T1 documents flat (see §3)
```

**`docs/provenance/DOCUMENT_PATH_TRANSLATION_V1.md`** — all 95 old→new paths,
with the 8 named inside frozen evidence listed separately. This follows the
repo's own `COMMIT_PIN_TRANSLATION_V1` precedent and is how a stale pointer in
an immutable artifact resolves. **If you move anything else, add it there.**

**Verified byte-identical to HEAD:** all 22 handoffs, superseded handbook
versions v1.2/v1.3/v1.4, and every digest-bound document.

**The digest-bound set is 38.** Measured, not estimated: hash every file under
`docs/`, `paper/`, `audits/`, `handbook/`, then look for that digest anywhere
else in the repository. 29 are pinned by code, evidence receipts or configs —
**the other nine are pinned only by other documents**, where a decision record
quotes the SHA-256 of the protocol it decided on. **Nothing fails when one of
those nine is edited.** Four of them still carry pre-move paths and were left
alone; `docs/README.md` and the translation table both name them.

Five more documents — the T1 descriptive and post-hoc reports and the T2/U1/W1
reports — are frozen not by digest but by **regeneration**. See trap 8.

**Deliberately not corrected:** `docs/literature/LITERATURE_SEARCH_V2.json`
records `"supersedes": "docs/LITERATURE_SEARCH_V1.json"` inside its **hashed
payload**. Fixing that string would change `payload_sha256` and destroy the
digest that makes it evidence. The translation table resolves it.

**Two intentional source changes that must survive any revert:**

| file | change |
|---|---|
| `src/cardiosentinel/agents/claims.py` | `find_violations` uses `re.finditer`, so **every** occurrence is reported, not the first per pattern. `ClaimViolation` gained an optional `start` offset |
| `scripts/literature_search.py` | multi-key bracket extraction, arXiv 3.0 s pacing with 429 retry, the V2 query set, union-of-records `verify` |

Plus two new test files: `tests/agents/test_claim_occurrence_counting.py` (13
tests) and `tests/reproducibility/test_literature_citation_extraction.py` (22
tests).

---

## 5. THE MANUSCRIPT IS FINISHED AND UNAFFECTED

None of the above touched the science or the paper.

| | |
|---|---|
| Submission source | `paper/CARDIOSENTIN_TACTICS_SUBMISSION_CANDIDATE_V1_FORMAT_PENDING.md` |
| Words | 14,415 total · 13,854 body · **279 abstract** |
| Figures / tables / works | 5 · 4 · **87** |
| Claim guard | 18 patterns · 17 occurrences · **0 genuine overclaims** |
| Citation verifier | 108 keys · 87 unique · 87 works · **0 unresolved** |

**Note:** the hash recorded in the audits (`72a8d738…`) is stale — the file
changed by one line when the reorganisation repointed a path in its banner.
Re-hash before treating any recorded digest as current.

**Status: content frozen. Format blocked** on the official TACTiCS 2026 author
instructions and template, which do not exist in the repository and were not
found in three web searches. `audits/TACTICS_2026_SUBMISSION_REQUIREMENTS_V1.md`
records all 22 requirements as `NOT SPECIFIED`. **Do not infer any of them.**
The questions to ask are written out in
`paper/TACTICS_OFFICIAL_INSTRUCTIONS_NEEDED.md`; fourteen human metadata fields
are in `paper/TACTICS_SUBMISSION_METADATA_TO_COMPLETE.md`.

---

## 6. EVIDENCE IS SAFE

`cardiosentinel-runs/` — **3.4 GB, intact**, and the E11/E12d/E13a delta is
mirrored at
`s3://cardiosentinel-evidence-341181499761/snapshot-2026-08-28-4c59ff1/`:
196 objects, 1,193,258,795 bytes, GOVERNANCE lock until **2027-08-28**, SSE-S3.
Verified by object count, exact byte total, manifest round-trip
(`07fd04be…`) and 16/16 sample re-hash. **All fifteen one-shot budgets remain
spent; nothing was reopened.**

---

## 7. TRAPS

1. **Never `ruff format`.** The repo is check-only. It reflows unrelated files
   and lengthens frozen constant tables.
2. **Never edit a document's content to fix a path.** ~37 are digest-bound.
   Move them; update the code that points at them.
3. **T1 sources are SHA-frozen.** So are some baseline sources
   (`tests/baseline/test_source_verification.py`). Check before editing
   anything under `src/cardiosentinel/neural/t1_*`.
4. **Four path-construction forms exist.** Grep for all of them, not just the
   literal: `"docs/NAME"`, `"docs" / "NAME"`, `DOCS / "NAME"`,
   `"docs" / f"{NAME}.md"`.
5. **`git status` shows `D` for a `mv` that was not staged.** The 2026-08-28
   move of `paper/` and `handoffs/` looked like a deletion and I raised a false
   alarm about data loss. Check `docs/` and the root before concluding anything
   is gone.
6. **pgrep -f self-matches** — a monitoring command that greps its own command
   line will always report ALIVE.
7. **The full suite takes ~18 minutes.** Run it in the background; do not poll
   with short sleeps.
8. **A provenance generator is a document's content.** `scripts/provenance/gen_*.py`
   emit path strings *into* reports that must regenerate byte-for-byte. Repointing
   an emitted string silently breaks that reproduction even though no test fails.
   Where a constant is both emitted and opened — `AMENDMENT` in
   `gen_t2_arm_comparison_report.py` — it now has two forms: the recorded path
   that is emitted, and `AMENDMENT_PATH`, which is what is read. All five
   generators were re-run and diffed against their reports; the only difference
   is the `executed at commit` stamp, which is expected.
9. **`git ls-files` beats grep for a reference sweep.** Enumerate
   tracked+untracked files, extract every repo-relative path, test it for
   existence — then classify by whether the containing file is digest-pinned,
   regenerated, or history *before* touching anything. That sweep found 69 real
   stale pointers (the raw number looks like 193; the two translation tables
   list old paths by design). 54 were repointed, 15 deliberately left.
10. **Beware the empty-string digest.** `M1_STAGE1_ATTEMPT1_FAILURE.md` records
    `e3b0c442…`, the SHA-256 of nothing. A naive "is this file's digest quoted
    anywhere?" check reports a false pin for every file it cannot read.

---

## 8. WHAT THIS SESSION DID, INCLUDING THE PART THAT WENT BADLY

It mirrored 1.11 GiB of irreplaceable evidence to S3 with hash verification;
fixed a citation verifier that had been silently skipping 16 keys inside shared
brackets and a claim guard that reported one violation per pattern instead of
every occurrence; ran a falsification search that **cost the paper its novelty
claim** and narrowed it to the two-surface coupling; confirmed all 19 citation
venues; assembled, froze and titled a 14,415-word manuscript with a 279-word
abstract; and produced the submission-format review that found no TACTiCS rules
exist to comply with.

**Then it spent the last stretch breaking a working repository to tidy a
directory.** The suite went from 3541/1 to 154 failures and back to 16. Every
regression was self-inflicted, and each was found by running the tests rather
than by reasoning about the change first. **The reorganisation should have
started by enumerating the digest-bound and artifact-named files — the exact
list that now sits in the translation table — instead of ending with it.**
