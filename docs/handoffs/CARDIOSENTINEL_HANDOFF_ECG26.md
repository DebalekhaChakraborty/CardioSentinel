# CardioSentinel — handoff to session "ECG 27"

Paste this whole file as the first message of the new chat, or say:
"Read `docs/handoffs/CARDIOSENTINEL_HANDOFF_ECG26.md` in the repo and continue.
Remember to use ONLY the tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do **not** use) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/CardioSentinel` |
| Branch | `master` at `183c17d`, **green**. **PR #143 open.** |

`tactics` holds 335 packages, Python 3.12.6. **Never install, upgrade or
downgrade anything in it.** **The Bash working directory silently resets** — put
`cd` in the same command as the work. **Never `git add -A`.**

### Two environment traps, one new

**The ECG25 symlink still matters.** Without it nine governance tests fail as
`DID NOT RAISE` and look like disabled safety guards. It exists now; a fresh
clone will not have it.

```bash
ln -s /home/AI_POC/tactics/CardioSentinel \
      /home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal
```

**NEW — this machine's disk is nearly full, and it looks like a code
regression.** ~1.2 GB free against a 2 GB guard, so **~32 `tests/neural` tests
fail locally on every branch, including clean `master`**:

```
ValueError: B4 run requires 2147483648 free output bytes,
            but only 1264009216 are available.
```

**CI is green on the same commits.** Do not chase it, and do not "fix" it inside
a scoped task. The 25 GB under `cardiosentinel-data/`, `-features/` and `-runs/`
is the obvious candidate and is fully mirrored to S3, but deleting it is an
owner decision.

---

## 1. STATE — V1 frozen, V2 running, J1 pre-registered

**V1 is complete.** All fifteen one-shot budgets are spent; the B4 neural sealed
test was consumed 2026-08-25, attempt 1 of 1. Nothing in this session
recomputed, re-scored or re-selected anything.

**J1 is `PRE-REGISTERED — NOT AUTHORIZED`.**

```text
QUESTION           complete
PROTOCOL           FROZEN   cedb152eef187fd573212daaad7492242d6963d9b9de897ed1312cde0a976cf0
PRE-REGISTRATION   FROZEN   1b6eb6645bf2449e4b76fb40b5ee7e44250474bd08c4a1c42ba79c00dc45fcd1
AUTHORIZATION      ABSENT
EXECUTION          NOT PERMITTED
REPORT / DECISION  nonexistent
```

`real_data_authority = NONE` · `attempt_budget = NOT ESTABLISHED` · zero
authorization documents · zero attempt directories.

Both digests are bound by `docs/journal-extension/j1/J1_FREEZE_RECEIPT_V1.md`
and guarded by `tests/reproducibility/test_j1_freeze_binding.py`, which fails if
either document drifts.

---

## 2. WHAT THIS SESSION DID

**Merged: #136, #137, #139, #140, #141, #142. Open: #143.**

**Retired the V1 publication workspace (#136).** `docs/paper/` gitignored,
preserved locally at `../publications/CardioSentinel/historical-v1/` and in the
versioned S3 drafts bucket. Its five evidence figures were relocated beside the
evidence they depict — F1/F2 to `docs/control-plane/figures/`, F3 to
`docs/experiments/w1/`, F4 to `docs/experiments/b4/`, F5 to
`docs/explanation/` — with both generators in `scripts/provenance/`.
`docs/provenance/V1_PUBLICATION_WORKSPACE_RETIREMENT_V1.md` has the inventory.

**Handbook split by programme (#139).** `docs/handbook/v1/` (v1.0–v1.5) and
`docs/handbook/v2/` (a pointer only). The canonical journal-extension blueprint
lives at `docs/journal-extension/`; `v2/` carries no independent authority.
Recorded append-only in `DOCUMENT_PATH_TRANSLATION_V3.md`.

**Bootstrapped the V2 control plane (#137)** — blueprint, charter, evidence
authority, experiment ledger under `docs/journal-extension/`.

**Designed, froze and pre-registered J1 (#140, #141).**

**Built the J1 execution instrument (#142)** — `src/cardiosentinel/journal_extension/j1/`,
13 modules, 61 synthetic qualification tests.

**Defined the environment authority (#143, open)** — `environment_authority/`,
34 tests.

---

## 3. J1 — the frozen science. Do not re-derive it.

| | |
|---|---|
| Question | does stateful episode reasoning retain an advantage against an **independently tuned** memoryless comparator |
| Population | 56 V1 TRAIN subjects |
| Primary F1 cohort | `reference_episode_count > 0` — reference-defined, identical for both arms |
| Arm-neutral row | **8 fields**. `elapsed_state_seconds` is J1-S-endogenous and is *not* in it |
| Inherited scaffold | B4 / P1 / M1 / M2 / T2, frozen |
| Cross-fit upstream | **U1 calibration only** |
| Geometry | outer 7 × 8, inner 6 × 8 over 48; seed 2026 |
| J1-S | **12** candidates, `NO EXPANSION` |
| J1-W | **206** candidates |
| Primary contrast | `Δ = mean(F1_S,i − F1_W,i)` |
| Interval | percentile paired subject bootstrap, 1000 replicates, seed 2026, 2.5 / 97.5 |
| Gate A | PASS = `Δ > 0` **and** 95% lower bound `> 0` |

**Two facts that shaped the design and are easy to lose.** T1/W1 were developed
on the **12 VALIDATION** subjects, which J1 may not reopen — hence TRAIN, with
**zero overlap**. And **B4 was trained on all 56 TRAIN subjects** (verified from
its experiment lock), so J1 estimates a *conditional* episode-policy contrast
given the inherited scaffold; it is **not** a fully out-of-sample evaluation,
and absolute values are development evidence only.

---

## 4. TRAPS

1. **Verify on a clean checkout, not a subset.** This cost the session twice.
   `docs/paper/` was *gitignored, not deleted*, so three tests reading it from
   disk passed locally and failed CI — **master was red for 18 hours**. Then a
   J1 test asserted `b4b_sealed_test not in sys.modules`, true in isolation and
   false in the full suite. Reproduce CI cheaply:
   `pytest tests/neural/test_b4b_sealed_test_identity.py tests/journal_extension tests/reproducibility`
2. **A string search is not a dependency analysis.** The pre-retirement audit
   missed two tests: one asserted *directory existence*, the other built its path
   across five lines (`/ "docs" / "paper" / …`). `git grep` saw neither. Both
   negative-capability modules encode the mirror rule: prove by **AST and import
   graph, never source text** — a guard's own refusal list contains the words it
   refuses. V1 recorded that false positive five times.
3. **`git commit` sweeps the whole index.** An earlier `git add`/`git rm` will
   ride along. One commit had to be unwound with `git reset --soft`. Stage
   explicit paths, or `git add -u <path>`.
4. **`grep` is ugrep here** and skips gitignored paths. Use `git grep` /
   `git ls-files` for anything authoritative.
5. **`gh pr checks` has no `--json`** (gh 2.23.0). Read failures with
   `gh api repos/.../actions/jobs/<id>/logs`.
6. **Never `ruff format`.** `ruff check` only. `scripts/provenance` is in
   `extend-exclude`, so its 116 pre-existing errors are out of scope.
7. **Poll CI in a background waiter**, never one long blocking wait.

---

## 5. WHAT IS OPEN

1. **Review and merge PR #143.** One judgement call needs a decision: the
   qualification receipt names **no** `environment_sha256`, recording
   `NOT YET SUBMITTED`, because the task defined the mechanism but was scoped
   not to select an environment. A receipt carrying a plausible digest is
   exactly what a later reader — or a later piece of code — could mistake for
   authority.
2. **No environment has been built or submitted.** #143 defines what an
   authoritative one *is*. A real one gets a **V2 receipt**, never an edit to V1.
3. **Then `J1_AUTHORIZATION_V1`** naming: frozen protocol digest, frozen
   pre-registration digest, execution Git SHA, environment authority digest,
   `V1_TRAIN_ONLY`, provenance sink, attempt budget, post-visibility decision
   authority, human approval. **Authorization is a human act — do not perform it
   autonomously.**
4. **J1 collaborators are qualification fixtures.** The real fold evaluator,
   calibration fitter and threshold deriver are unwritten.
5. **The provenance sink is an interface**; its value comes from the
   authorization. The **TRAIN manifest is supplied by** the authorization, never
   discovered by the instrument.
6. **Three frozen records name the retired `docs/paper/` files in prose** —
   handoff ECG16 and two audits. Historical, not edited to follow a path.
   Expected, not drift.
7. **The symlink is untracked infrastructure** (§0). Deciding between renaming
   the directory back and a controlled reinstall is still open.
8. **Everything outside git is mirrored to S3** — evidence bucket, Object Lock
   to 2027; drafts bucket, versioned, no lock. 994 files checked by path,
   zero unmirrored. **Re-verify with a dated check rather than inheriting
   2026-08-31.** The evidence retention expires **2027-08-22**, which is the
   first date those objects become movable.

---

## 6. THE SCIENCE IS UNCHANGED

**All fifteen V1 one-shot budgets remain spent.** No frozen artifact, attempt
receipt, threshold or experiment identity was touched this session. No
physiological data, annotation or reference-episode count was accessed. No fold,
calibrator, threshold, candidate selection or scientific result was generated.
No scientific attempt was claimed.

RQ4 **Supported (bounded)** — the parenthesis is part of the claim. RQ3 is a
**negative finding** reported as a result. RQ1, RQ2 (partial), RQ5, RQ6 and RQ7
are open, and every one needs a run.
