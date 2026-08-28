# CardioSentinel — handoff to session "ECG 24"

Paste this whole file as the first message of the new chat, or say:
"Read handoffs/CARDIOSENTINEL_HANDOFF_ECG23.md in the repo and continue.
Remember to use ONLY the tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do NOT use) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| GitHub | `DebalekhaChakraborty/CardioSentinel` |
| Scratch (outside the repo) | `/tmp/claude-1000/-home-AI-POC/<session>/scratchpad` |

`tactics` holds 335 packages, Python 3.12.6. **Never install, upgrade or
downgrade anything in it.** **The Bash working directory silently resets to
`/home/AI_POC`** — put `cd` in the same command as the work. **Never
`git add -A`.** Several sessions share this checkout.

---

## 1. WHERE THE PROGRAMME IS

**Every experiment this corpus can support has been run. Nothing is authorized,
nothing is pending, and no experiment is designed.**

| | |
|---|---|
| **E11** morphology-aware representation | **CATEGORY C** — mechanism NOT ESTABLISHED |
| **E12a** training-dynamics audit | **DECISION C** — no further conclusion |
| **E12d** instrumented phase-1 replication | **DECISION D** — replication gate PASSED |
| **E13a** held-out geometry reliability | **DECISION D** — no coherent mechanism |
| **B4 representation-improvement branch** | **CLOSED on this corpus** |

**All fifteen one-shot budgets are spent.** Sealed TEST consumed 2026-08-25.
Historical VALIDATION spent for confirmatory purposes. **The E11 44-subject /
79-stream held-out geometry population is CONSUMED** (E13a, 2026-08-28).

**The remaining work is the manuscript.** It needs no authorization and no
compute.

---

## 2. GITHUB — and the evidence that is NOT on it

**PR #128 is open**, branch `feat/e11-e13a-instrumentation-and-paper-readiness`
→ `master`, **+10,120 / −8 across 42 files**, working tree clean, HEAD ==
origin.
<https://github.com/DebalekhaChakraborty/CardioSentinel/pull/128>

> ### ⚠ The scientific evidence is NOT in git and exists on ONE machine
>
> `cardiosentinel-runs/` is gitignored. That is where E11 ATTEMPT 2
> (**1.07 GB**, 17 hash-verified artifacts), E12d ATTEMPT 1 and 2 (**~90 MB**),
> and E13a live. **A disk failure loses all of it**, and none of it can be
> regenerated without a fresh human authorization, because every budget is
> spent.
>
> **If ECG 24 does one operational thing, make it this: get that evidence
> mirrored.** The programme already has an S3 evidence mirror (handbook §47);
> these runs are not in it.

---

## 3. The science, in the order it happened

**E11 ATTEMPT 2** — B0 vs B1 (`Linear(128→1)` auxiliary head,
`post_r_80ms_delta_mv`, λ = 0.1), prospective 3-fold, 44 evaluable subjects.
Primary geometry, B1 − B0, paired subject bootstrap:

| endpoint | point | 95% CI |
|---|---|---|
| median cosine | +0.0030 | [−0.0178, +0.0073] |
| median ‖delta‖ | +0.1217 | [−0.5993, +0.5617] |
| negative-cosine fraction | −0.0127 | [−0.0406, 0.0000] |

**All three include zero.** Secondary subject-macro AUPRC **+0.0258
[+0.0002, +0.0562]** — fragile, lower bound two ten-thousandths from zero,
**not the headline**.

**E12a** — selection is demonstrably weak: 4 of 6 margins below E2's documented
**+0.032** argmax bias, fold-1 B1 margin **+0.00029213**, AUPRC and loss epoch
ordering disagree **6/6**, inner-val prevalence **8.4–12.1×** below inner-train.
Auxiliary maturity **UNOBSERVABLE** — E11 never logged it.

**E12d ATTEMPT 2** — replication gate **PASSED**: six fits AUPRC bit-identical,
selected epochs **1,1,1,2,4,1**, counts **5,5,5,6,8,5**, B0 `train_loss`
bit-identical. **The auxiliary loss had NOT plateaued at selection**
(`F_aux` **+0.6208 / +0.2556 / +0.5378**, all post-selection trajectories
monotone), and **5 of 6** selections precede the largest geometry movement.
But **no coherent B1-specific geometry continuation** → D.

**E13a** — 79 streams / 44 subjects; **57 eligible** at K=2 after a raw-signal
overlap guard, **22 excluded** because a temporal half is single-class.
Within-stream direction is highly stable (median `cos_within` **+0.9935**, sign
agreement **56/57**). `s20171:0` reverses reproducibly (−0.4984, −0.3302);
`s20021:1` does **not** (+0.4514, −0.9537); `s20101:1` is not assessable — all
390 positives in one half. The frozen criterion required **both** → D.

---

## 4. Quarantined attempts — never use these

| Attempt | Cause | Interpretable |
|---|---|---|
| **E11 ATTEMPT 0** | tool-call timeout SIGTERM'd the job | **NO** |
| **E11 ATTEMPT 1** | `NaN * 0 == NaN` in the auxiliary mask | **NO** — fold-0 B0 quarantined, used only as ATTEMPT 2's gate (passed, delta exactly 0.0) |
| **E12d ATTEMPT 1** | one inner-validation `DataLoader` shared across each fold's B0/B1 fits deleted a global RNG draw per fold | **NO** — B1 trajectories must never enter any calculation |

**All three were harness defects caught by a gate before interpretation.** Each
gate existed because an earlier failure taught the programme to build it.

**The E12d defect is now pinned** by `tests/neural/test_e12d_loader_scoping.py`:
fresh-per-fit construction takes **6** global RNG draws, the shared pattern
takes **1**. **`persistent_workers=True` is load-bearing** — with
`num_workers=0` the defect does not reproduce at all.

---

## 5. Instrumentation — built, tested, not wired to a runner

`src/cardiosentinel/neural/`: `e11_authority`, `e11_data_binding`,
`e11_instrumentation`, `e11_checkpoints`, `e11_geometry_trajectory`,
`e11_outer_geometry`, `e11_run_state`, `e11_future_runner`, `e12d_orchestrator`.

**`E11FoldAuthority` has four accessors and none takes an argument**, so TEST
and historical VALIDATION cannot be named. Subjects are admitted by whitelist.
Checkpoints are 1.20 MB, identity-bound, hash-verified. The run-state machine is
hash-chained, so **a later state cannot be forged by dropping a file in the
directory**. Training overhead **+0.004%**; geometry runs post-hoc (synchronous
would have been **+40%**).

**Tests: 3,075 in `tests/neural`, ruff clean repo-wide.**

**Not wired to real data end-to-end.** The E12d driver that does the wiring
lives in a **scratchpad** (`e12d_driver.py`), not the repo — deliberate, matching
the E11 runner precedent, but it means the orchestration is not version
controlled.

---

## 6. Manuscript state

**Drafted:** §2 (`PAPER_S2_RELATED_WORK_DRAFT.md`), §4 / §4.6
(`PAPER_S4_EVIDENCE_FRAMEWORK_DRAFT.md`), §5.6, §9, tables T1–T4
(`PAPER_TABLES_T1_T4_DRAFT.md`), figures **F1–F5** in `paper/figures/`.

**Not drafted:** §1, §3, §5, §6, §7, §8, §10, §11, §12 — all of which
**assemble existing material** rather than create it.

**F6 was deliberately not drawn.** It rests on two values (~61× real time;
0 of 1079 windows admitted) and may not earn the space over a sentence. Decide
it against the final §9.

> ### The one real blocker in the manuscript
> **§2's citations are not verified.** The search was **five targeted queries,
> not a systematic review.** Exactly one citation is VERIFIED (LTSTDB, fetched
> from PhysioNet). **Every other reference is SEARCH-RETURNED and must be
> fetched and confirmed before submission** — the draft says so in its own
> header. The **85/86 → 70/68 EDB-to-LTSTDB** figures in §2.1 are the most
> load-bearing and must be traced to a primary source.
>
> §2 also carries the §6.3 condition of `B4_TEST_AUTHORIZATION_V1.md`:
> **it must not be shaped by the sealed-test result.** §2.0 records how that is
> honoured — the gap statement is independent of our number.

**Audit verdict:** `CARDIOSENTINEL_PAPER_READINESS_AUDIT_V1.md` returned
**B — READY TO DRAFT, WITH NON-EXPERIMENTAL GAPS**, and
**NO FURTHER SCIENTIFIC EXPERIMENT IS REQUIRED FOR THE CURRENT PAPER.**
External validity is **RED** and cannot be fixed by writing.

---

## 7. Standing constraints — verbatim, still in force

- **All fifteen one-shot budgets are spent.** Every training run needs a fresh
  human authorization.
- **The sealed B4-B test is CONSUMED**, `repeat_attempt_permitted: false`.
  **Never open the four sealed artifacts.**
- **Historical 12-subject VALIDATION is spent for confirmatory purposes.**
- **The E11 held-out geometry population is CONSUMED** for confirmatory geometry.
- **No held-out estimate is obtainable within LTSTDB, permanently.** External
  corroboration was declined in writing; no second cohort, ever.
- **NO AUTOMATIC RETRY.** Never add `--force` / `--retry` / `--reset` /
  `--overwrite` / `--fresh-seed`.
- Development evidence only. **Never claim medical or diagnostic performance.**
- Do not change code in response to a scientific result.
- **Do not change any E1–E13a conclusion.**

---

## 8. Traps this programme has actually hit

1. **`NaN * 0 == NaN`.** Masking by multiplication does not exclude a row. Use index selection.
2. **A shared `DataLoader` deletes a global RNG draw** when `persistent_workers=True`. Build loaders fresh per fit.
3. **B4 arrays are lexicographic, not chronological — 0 of 132 streams are in time order.** `start_sample` is recoverable from the stable id. The M1 cache *is* chronological.
4. **`grep -r` here is ugrep and skips gitignored paths** — the evidence trees are gitignored.
5. **The Bash cwd resets to `/home/AI_POC`.**
6. **AUPRC is bounded below by prevalence.** Never compare across differing prevalence. Print the denominator every time.
7. **A tool-call timeout can SIGTERM a background job.** Use `setsid nohup`, no timeout-linked sleep.
8. **`/tmp` scratchpads are per-session and not durable.**
9. **`pgrep -f <script>` matches its own bash wrapper** and will report a dead job as ALIVE. Use `ps -eo pid,cmd | grep | grep -v grep`.
10. **matplotlib eats `_` in `*_AUTHORIZED`**, and diagram text silently overflows its box unless the layout is computed. `paper/figures/make_f1_f2_f5.py` has a `panel()` helper that does it properly.

---

## 9. What ECG 24 should do

1. **Mirror the run evidence off this machine** (§2). Highest-value operational task; everything else survives in git.
2. **Verify §2's citations.** The only real blocker to submission.
3. **Assemble the remaining manuscript sections** — §1, §3, §5–§8, §10–§12. All are assembly, not research; §4 of the audit and the T1–T4 tables are the sources.
4. **Decide F6** against the final §9.
5. **Land PR #128.**

**Do not design an experiment.** The corpus cannot support one, and the audit
says none is required.

---

## 10. The danger this handoff names

**Thirteen mechanism findings, four decisions, three quarantined attempts, a
consumed sealed test, an instrumentation stack with 3,075 passing tests — and a
manuscript that is still mostly undrafted.**

Every session in this chain has been offered a defensible technical task and has
taken it, because the technical work is legible and the writing is not. **ECG 23
ran three experiments, audited two of them, built an observability stack, drew
five figures and wrote four documents.** All of it was authorized and all of it
was correct. **None of it was §7.**

**The characteristic failure of ECG 23: doing excellent work that was not the
work that finishes the paper.**
