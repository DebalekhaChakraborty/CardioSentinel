# CardioSentinel — handoff to session "ECG 24"

Paste this whole file as the first message of the new chat, or say:
"Read handoffs/CARDIOSENTINEL_HANDOFF_ECG23.md in the repo and continue.
Remember to use ONLY tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do NOT use) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| Scratch (outside the repo) | `/tmp/claude-1000/-home-AI-POC/<session>/scratchpad` |

`tactics` holds 335 packages, Python 3.12.6. **Never install, upgrade or
downgrade anything in it.** **The Bash working directory silently resets to
`/home/AI_POC`** — put `cd` in the same command as the work. **Never
`git add -A`.** Several sessions share this checkout.

---

## 1. THE HEADLINE — E11 is DONE. Do not describe it as pending.

**E11 ATTEMPT 2 completed cleanly on 2026-08-27T00:57:30Z**, 5.04 h, six of six
arms, `failure_state: null`, zero non-finite values anywhere in the artifacts.

> **E11: COMPLETED — ATTEMPT 2**
> **Primary mechanism: NOT ESTABLISHED**
> **Interpretation: Category C**

**Primary geometry paired contrasts** (B1 − B0; subject bootstrap, 44 evaluable
subjects, 1,000 replicates, seed 2026):

| endpoint | point | 95% CI |
|---|---|---|
| median cosine | **+0.0030** | [−0.0178, +0.0073] |
| median `‖delta‖` | **+0.1217** | [−0.5993, +0.5617] |
| negative-cosine fraction | **−0.0127** | [−0.0406, 0.0000] |

**All three include zero.** All three point estimates moved in the predicted
pooled direction; per-fold effects are heterogeneous in sign; fold 0's
`‖delta‖` moved against the prediction.

**Secondary subject-macro AUPRC: +0.0258, 95% CI [+0.0002, +0.0562].**
Secondary, nominally separated, **fragile** (lower bound +0.0002), and
**unsupported by the primary mechanism**. **Do not report it as the headline.**

**Sealed TEST: untouched.** **Historical 12-subject VALIDATION: untouched by
E11.** **44 evaluable held-out subjects — prospective development evidence.**

**Category C means *failed to establish*, not *evidence against*.** Per A5 the
null means exactly: *"no established benefit for this preregistered
morphology-aware formulation at λ = 0.1."* **It must not be generalized to
"morphology-aware representation learning does not work."**

Full record: **`docs/B4_E11_MORPHOLOGY_AWARE_REPRESENTATION_REPORT_V1.md`.**

---

## 2. Where the evidence lives

```
cardiosentinel-runs/b4-e11-morphology-aware-v1/E11_ATTEMPT_2/
  artifacts/e11_fold{0,1,2}_{B0,B1}.npz      six fold/arm artifacts
  E11_ATTEMPT_2_EXECUTION_RECEIPT.json       A7 receipt, finished_utc set
  E11_ATTEMPT_2_LAUNCH_RECEIPT.json          written BEFORE training
  E11_ATTEMPT_2_ARTIFACT_MANIFEST.json       17 files, all SHA-256 verified
  logs/E11_ATTEMPT_2_EXECUTION.log
  protocol/                                  split, both runners, row arrays
  analysis/E11_ATTEMPT_2_GEOMETRY.json
  analysis/E11_ATTEMPT_2_PAIRED_AND_SECONDARY.json
```

**Manifest digest:** `5d357209005bf1571e3a740219dd89f6cd770ea62ee00b17c6c9806985f49359`
**17 files, 1,095,951,778 bytes, every source/destination hash pair equal.**
The `/tmp` originals still exist but **`/tmp` is not durable — the repo copy is
now the record.**

---

## 3. ATTEMPT 1 — apparatus failure, no attempt consumed

ATTEMPT 1 died on `NaN * 0 == NaN` in the auxiliary loss mask. The human
classified it **EXPERIMENTAL-APPARATUS FAILURE, scientific attempt consumed:
NO**, and **quarantined** its fold-0 B0 values. They were used in ATTEMPT 2
**only** as a reproduction gate, which passed **bit-for-bit** (deltas exactly
0.0 on both AUPRC and AUROC). `docs/B4_E11_ATTEMPT_1_FAILURE_RECEIPT_V1.md`.

**Do not use ATTEMPT 1's fold-0 B0 numbers in any analysis.**

---

## 4. The one open protocol gap — fix it before any E11-class rerun

**The registered operating-point endpoint (§5) could not be computed.** The
runner persisted neither the inner-validation F1-optimal threshold nor the
inner-validation predictions needed to reconstruct it, and the phase-1 model is
discarded by construction.

**No threshold was derived from held-out scores** (circular, forbidden by §3.2),
**no phase-1 model was reconstructed**, **no substitute operating point was
used.** Report §9.1.

> **Any future E11-class runner MUST persist the inner threshold at selection
> time.** This gap is inherited from the ATTEMPT 1 runner and was not introduced
> by the masking fix.

**Separately: the categorical collapse endpoint is absent by registration, not
by omission** — amendment A4 deleted it before ATTEMPT 2 existed. Do not read
its absence as an analysis failure.

---

## 4b. E12a — COMPLETE. Also not pending.

**E12a: COMPLETE — read-only training-dynamics / checkpoint-selection audit.**
**E11 remains CATEGORY C, unchanged. E12a decision: C — NO FURTHER CONCLUSION.**
`docs/B4_E12A_TRAINING_DYNAMICS_SELECTION_AUDIT_V1.md`.

**Established:** checkpoint selection is **not** demonstrably stable; **four of
six selected epochs are epoch 1**; **four of six best-vs-second-best AUPRC
margins fall below the documented +0.032 argmax bias**; **fold 1 B1's margin is
+0.00029213**; **training-loss and AUPRC epoch ordering disagree in all six
fits**; **inner-validation prevalence is 8.4×–12.1× below inner-train**.

**Unobservable:** separate BCE trajectory; auxiliary-loss trajectory;
morphology prediction trajectory; inner-validation AUROC trajectory; per-epoch
representation geometry; whether the auxiliary task was mature at selection;
when the fold-2 B1 negative TRAIN stream emerged.

**Interpretation.** E11 tested the registered morphology auxiliary objective
through a **noisy early-selection regime**, but persisted evidence **cannot
distinguish a weak objective from a weak delivery/selection instrument**.

> **E12a does NOT invalidate E11.** **Nothing in E12a says a later epoch would
> have improved E11.** The decision is C because one scalar per epoch was never
> written to disk — an instrumentation gap, not a scientific ambiguity.

---

## 4c. The instrumentation hardening — implemented, untested against real data

**Implementation-only. No model was trained. E11 ATTEMPT 2 is byte-unchanged
(all 17 manifest hashes re-verified after the work).**

- `src/cardiosentinel/neural/e11_instrumentation.py` — per-epoch observability
  for **future** E11-class runs: loss decomposition (BCE / raw aux / λ·aux /
  total / LR / runtime), inner-validation record (AUPRC, AUROC, F1-optimal
  threshold, prevalence, ±counts), compact stream geometry summaries,
  selection evidence, a fail-closed digest-sealed epoch log, and
  `E11FoldAuthority` (no partition parameter — TEST unreachable by
  construction, per A6).
- `tests/neural/test_e11_instrumentation.py` — **28 tests, all passing.**

**Key contracts, enforced not documented:** `total_loss == bce + λ·aux` is
asserted on construction; **B0 records auxiliary as `None`, never a fabricated
`0.0`**; a consensus built from `inner_validation` is **refused**; a
single-class stream is **preserved with undefined fields**, never dropped; the
retention policy **must** keep the selected checkpoint.

**Storage audit decided the schema.** Full per-epoch embeddings would cost
**~11 GB** worst case (1.24 GB inner-val + 9.73 GB inner-train). Scores +
labels + geometry summaries cost **13.4 MB**. Embeddings are therefore **not**
persisted per epoch.

**Nothing is wired into a runner yet, deliberately** — §7 of the hardening task
said do not start E12.

---

## 4d. E12b — future-runner observability integration (implementation only)

**No model trained. No experiment authorized. E11 ATTEMPT 2 re-verified
byte-identical afterwards (17/17 hashes, manifest digest unchanged).**

- `src/cardiosentinel/neural/e11_checkpoints.py` — identity-bound, fail-closed
  phase-1 checkpoints.
- `src/cardiosentinel/neural/e11_geometry_trajectory.py` — read-only post-hoc
  geometry; **outer-held-out has no parameter that could carry it.**
- `src/cardiosentinel/neural/e11_future_runner.py` — the wired phase-1 loop.
- `tests/neural/test_e11_future_runner.py` — **22 tests**, real
  `B4BTransformerCNN`.

**The two audits that decided the design:**

1. **A checkpoint is 1.20 MB.** Retaining *every* phase-1 epoch, model state
   only, costs **41 MB** at observed epoch counts (108 MB worst case). Policy:
   **all epochs, model state only.** Optimizer state is **not** persisted — it
   triples the cost and buys only deterministic continuation, which is restart,
   which is a **separate authorization**. Persisting a checkpoint does **not**
   enable restart; there is no function that resumes training.
2. **The 40% geometry cost is avoidable.** Synchronous per-epoch geometry costs
   **+1.38 h (+40%)**. Checkpoint-then-post-hoc costs **0.6 s** of training time
   total (measured: 16.6 ms per checkpoint write) and retains the **full**
   trajectory, because embedding a checkpoint under `eval()`/`no_grad()` is
   deterministic and consumes no RNG. **Diagnostics are decoupled from
   training.**

**Equivalence is proven, not asserted:** instrumentation ON vs OFF gives
bit-identical parameters, outputs, selected epoch, loss/metric history and RNG
state, for both arms, against the real model class. `backward()` receives the
identical tensor; the decomposition is `.detach()`-ed from components already
computed.

**E11 report §9.1 is closed prospectively:** the F1-optimal threshold, its
source partition and its derivation version are persisted at selection time, and
`evaluate_at_frozen_threshold` **refuses** a threshold sourced from
outer-held-out as circular.

**Still not wired to real data, and still not authorized.**

---

## 4e. E12c — end-to-end observability integration (implementation only)

**No model trained on the scientific dataset. No experiment authorized. E11
ATTEMPT 2 re-verified: 17/17 hashes, manifest digest
`5d357209005bf157…f49359` unchanged.**

New: `e11_authority.py`, `e11_data_binding.py`, `e11_run_state.py`,
`e11_outer_geometry.py`; extended: `e11_future_runner.py` (phase 2 + outer
evaluation), `e11_geometry_trajectory.py` (driver), `e11_instrumentation.py`
(fail-closed threshold). Tests: `test_e11_end_to_end.py` (22).
**78 focused tests pass, repo-wide ruff clean.**

**The authority is the boundary.** Four accessors — `inner_train_rows`,
`inner_validation_rows`, `outer_train_rows`, `outer_held_out_rows` — and **none
takes an argument**. `E11Partition` has no member for TEST or historical
VALIDATION, and is not a `str` subclass, so a bare string cannot stand in.
Subjects are admitted by **whitelist** against the authorized population, which
is how a historical VALIDATION subject is excluded without ever naming that
partition.

**The binding reproduces ATTEMPT 2's splits exactly** against the real
registered inputs (read-only, no training): fold 0 inner-train **195,043** /
inner-val **30,367** / outer-train **225,410** / held-out **149,042** — matching
the ATTEMPT 2 receipt. Binding digest
`c9a53b0f7cb600cca1a0687c603b50fe4ce0d5b1d71b27701192ad5739d4dd10`.

**Phase 2 performs no selection** — it runs exactly `selected_epoch` epochs and
records `phase2_selection_performed: false`.

**The operating point is closed end-to-end.** `f1_optimal_threshold` now
**fails closed** on `source_partition`, and the outer evaluator refuses any
non-inner threshold source. A test proves inverting every held-out label leaves
phase-1 selection bit-identical.

**Run state is a hash chain:** AUTHORIZED → DATA_BOUND → PHASE1_COMPLETE →
SELECTION_FROZEN → PHASE2_COMPLETE → OUTER_SCORED → GEOMETRY_COMPLETE →
ANALYSIS_READY. Each stage seals over its predecessor's seal, so **a later
state cannot be forged by dropping a file in the directory**. Failure writes
`failure_state` and refuses further transitions — no automatic retry.

**Cost, separated honestly:** instrumented **training** wall time is
**+0.004%** (0.7 s of checkpoint writes). The geometry driver's **1.38 h** is
**post-hoc diagnostic time, not training time**, and is re-runnable. Total
prospective storage **60 MB** (136 MB worst case).

**Two geometry namespaces, deliberately:** `e11-outer-geometry-v1` (scientific
endpoint, consensus from outer-train) versus `e11-geometry-trajectory-v1`
(inner diagnostic, consensus from inner-train). They must never be pooled.

---

## 4f. E12d — PREREGISTERED, NOT AUTHORIZED, NOT RUN

**`docs/B4_E12D_INSTRUMENTED_PHASE1_REPLICATION_PLAN_V1.md`** (394 lines).
Diagnostic replication of **E11 phase 1 only**, under E12c instrumentation. No
scientific parameter changes. **E11 stays Category C.**

> **DO NOT LAUNCH E12d WITHOUT A NEW HUMAN AUTHORIZATION.**

**Review caught a structural defect and it is recorded, not quietly edited.**
The V1 draft's `R(x) = (x(s)-x(E))/(x(1)-x(E))` is **degenerate at s = 1** —
it equals exactly 1 by construction, measuring the selected epoch's index rather
than the trajectory. **Four of six historical fits selected epoch 1**, and on
the historical total-loss trajectories `R` is identically `1.0000` in all four.
**D1 is WITHDRAWN IN PLACE** (plan §7.0, with the table) and replaced by
`F(x) = (x(s)-x(E)) / (|x(s)| + 1e-12)`, plus a descriptive volatility
`V(x)`. `V` equals `F` exactly for monotone trajectories, so divergence between
them *is* the non-monotonicity signal.

**Also amended:** normalised B1 auxiliary loss is no longer compared against B0
BCE as if interchangeable — they are different losses on different scales. Three
trajectories are now reported separately per fold (B0 BCE, B1 BCE, B1 auxiliary);
auxiliary maturity is a **within-B1** question, and only **geometry** is used for
the arm comparison. The `R > 0.5` rule is **removed** as structurally biased by
s = 1.

**Orchestrator built (implementation only):**
`src/cardiosentinel/neural/e12d_orchestrator.py` + 12 tests. Runs exactly the six
fits `(0,B0) (0,B1) (1,B0) (1,B1) (2,B0) (2,B1)` in historical order. Contains
**no** selection, threshold, metric-branching, retry, or alternative-parameter
logic — asserted by test. **Dry-run mode emits the full plan without training.**

**The dry run reproduces ATTEMPT 2 bit-exactly** against the real inputs:
fold-0 inner scaler `(-0.07500000000000001, 0.14625000000000002)` and all 12
inner-validation subjects — **exact match** to the historical receipt.

**Cost if authorized:** training **3.52 h** (+0.004%), post-hoc diagnostics
**1.38 h** (separate), storage **46.1 MB**.

---

## 4g. E12d — EXECUTED AND COMPLETE (ATTEMPT 2). Decision D.

**Authorized and run 2026-08-27. E11 ATTEMPT 2 re-verified afterwards: 17/17
hashes, manifest digest `5d357209…f49359` unchanged.**
`docs/B4_E12D_INSTRUMENTED_PHASE1_REPLICATION_REPORT_V1.md`.

> **HISTORICAL REPLICATION GATE: PASSED**
> **E12d DECISION = D — NO FURTHER CONCLUSION**
> **E12d does NOT revise E11. E11 remains Category C.**

### ATTEMPT 1 — quarantined, do not use

**HARNESS / RNG-REPLICATION FAILURE. SCIENTIFIC RESULT INTERPRETABLE: NO.**
The driver cached the inner-validation DataLoader on rows+arm; the orchestrator
requests it with `arm="B0"` for **both** arms, so each fold's B1 fit reused the
B0 fit's object. With `persistent_workers=True` a loader takes its one global
`base_seed` draw at first iteration, so reuse **skipped one global RNG draw per
fold** and shifted every subsequent dropout mask. **All three B0 fits reproduced
E11 bit-identically; all three B1 fits matched at epoch 1 and diverged.** The
receipt never passed `DATA_BOUND`; nothing was interpreted.
Preserved at `E12D_PHASE1_REPLICATION/` +
`E12D_ATTEMPT_1_CLASSIFICATION.md`. **Its B1 evidence must never enter an E12d
calculation.**

**The fix, now in the repo and tested:** `FitScopedLoaderCache` puts the fit
index in the key, so a loader cannot cross a fit boundary.
`tests/neural/test_e12d_loader_scoping.py` (10 tests) pins the mechanism —
fresh-per-fit takes **6** global draws, the ATTEMPT 1 pattern takes **1**.
**`num_workers=0` will not reproduce the defect**; `persistent_workers=True` is
load-bearing. The driver now aborts mid-run if its loader audit shows sharing.

### ATTEMPT 2 — the only scientific E12d execution

Six fits, 3.60 h training + 0.91 h post-hoc geometry, 34 checkpoints, 45 MB.
Run state ends at **`SELECTION_FROZEN`** — the chain stopping there is the proof
phase 2 was never executed.

**Gate: all six AUPRC trajectories bit-identical (max Δ 0.0); selected epochs
1,1,1,2,4,1; counts 5,5,5,6,8,5; B0 `train_loss` bit-identical; B1 loss differs
only by the preregistered ≈1.3–1.8 × 10⁻⁹ accumulation effect.**

**Key findings:**

- **The morphology auxiliary loss had NOT plateaued at the AUPRC-selected epoch**
  — continued decrease in **all three folds**, `F_aux` = **+0.6208 / +0.2556 /
  +0.5378**, and `V == F` so every post-selection trajectory is monotone.
- **5 of 6 fits selected an epoch before the largest geometry movement.**
- **No coherent B1-specific geometry continuation.** B1 > B0 on cosine travel in
  1/3 folds, on delta-norm travel in 1/3 folds, and **different folds**.
- AUROC and AUPRC peak at different epochs in every fit (newly observable).

**Do NOT say** a later epoch would have performed better, that selection
truncated a beneficial representation, or that longer training would improve
outer performance. **Outer-held-out was never evaluated in E12d.**

**Protocol deviations:** (1) epoch runtime not captured — driver used the no-op
clock, `seconds=0.0` throughout; logging omission, not a replication defect,
durations recoverable from the log. (2) inner-validation geometry denominators
are small — **8, 8, 6, 6, 6, 6** evaluable streams — so median and travel
quantities are **coarse descriptive instruments**. Not smoothed or altered.

### Where this leaves the science

**The next scientific question is UNDECIDED.** E12a asked whether E11's null
came from a weak objective or a weak delivery mechanism. E12d shows the
objective was still learning when delivery stopped — but **cannot show that
distinguishes B1 from B0**. That question remains open, and **no E13 is
designed, proposed or authorized.**

---

## 5. Standing constraints — still in force, verbatim

- **All fifteen one-shot budgets are spent.** Every training run needs a fresh
  human authorization.
- **The sealed B4-B test is CONSUMED**, `repeat_attempt_permitted: false`. The
  four sealed artifacts are immutable. **Never open them.**
- **The historical 12-subject VALIDATION partition is spent for confirmatory
  purposes.** Any future model experiment must use a fresh subject-disjoint
  split inside the 56 TRAIN subjects.
- **No held-out estimate is obtainable within LTSTDB, permanently.**
- **NO AUTOMATIC RETRY.** Never add `--force` / `--retry` / `--reset` /
  `--overwrite` / `--fresh-seed`.
- Development evidence only. **Never claim medical or diagnostic performance.**
- Do not change code in response to scientific results.
- Keep scratch outside the repo.
- **Do not change any E1–E10 conclusion.** E11 revises none of them.

---

## 6. Traps this programme has actually hit

1. **`NaN * 0 == NaN`.** Masking by multiplication does not exclude a row. This
   killed E11 ATTEMPT 1. Use index selection.
2. **B4 arrays are sorted lexicographically, not chronologically.** The M1 cache
   *is* chronological (digest-verified).
3. **`grep -r` here is ugrep and skips gitignored paths** — the evidence trees
   are gitignored. Pass explicit paths or walk in Python.
4. **The Bash cwd resets silently.** A sweep that "found nothing" may have run
   in `/home/AI_POC`.
5. **AUPRC is bounded below by prevalence.** E11's fold prevalences are
   **0.2935 / 0.2601 / 0.1781** — a 1.65× spread. **Never compare AUPRC across
   folds.**
6. **Subject-macro denominators are 15/19, 15/19, 14/18** on E11's folds. Print
   the denominator every time.
7. **A tool-call timeout can SIGTERM a background job.** Launch long runs with
   `setsid nohup … &` and no timeout-linked `sleep`. This killed E11 ATTEMPT 0.
8. **`/tmp` scratchpads are per-session and not durable.** E11's artifacts sat
   there for seven hours after the run finished with no backup.

---

## 7. What ECG 24 should do

**No model experiment is authorized. Do not design or launch one.**
**E11 and E12a are both COMPLETE. Neither is pending.**

A **read-only next-question audit** was performed at the end of ECG 23 and its
ranked recommendation is in §8 below. **Its top recommendation is that no new
model experiment is yet justified**, and that the highest-value work is the
manuscript.

**§4 and §4.6 — the actual contribution — still have no draft**, and every
source for them is now on disk, E11 included.

**Correction (2026-08-28, paper-readiness audit):** ECG22 asserted that
`PAPER_S2_RELATED_WORK_DRAFT.md` existed and this handoff repeated the
assertion without checking. **It did not exist.** It was then written the same
day, so the file now exists — but for a different reason than the earlier
claim supposed, and the record should show the correction rather than a
coincidence.

**Manuscript drafts now on disk:** `PAPER_S2_RELATED_WORK_DRAFT.md` (new),
`PAPER_S4_EVIDENCE_FRAMEWORK_DRAFT.md` (new),
`PAPER_TABLES_T1_T4_DRAFT.md` (new), `PAPER_S5_6_CLAIM_BOUNDARY_DRAFT.md`,
`PAPER_S9_DISCUSSION_DRAFT.md`, `PAPER_S9_DISCUSSION_SKELETON.md`.
Figures F1–F5 in `paper/figures/`; **F6 deliberately not drawn.**

**§2's search was five targeted queries, NOT a systematic review.** One
citation is VERIFIED (LTSTDB, fetched from PhysioNet); the rest are
SEARCH-RETURNED and **must be fetched and confirmed before submission**. The
draft's gap statement is qualified accordingly and that qualification must not
be quietly deleted.

---

## 8. The next-question audit, in one line each

Ranked in ECG 23, read-only, nothing implemented:

1. **None is yet justified — write §4.** The programme has eleven correct
   mechanism findings and no manuscript.
2. **Loss dynamics / gradient interference** — the only candidate that is
   diagnosable *without* a new training budget, from the six preserved artifacts.
3. **Class-direction stability regularization** — the direct successor to E11's
   hypothesis, but it needs 2 to be informative first.
4. **Multi-task target formulation** — premature; E11 tested one target.
5. **Broader representation generalization** — the real question, and the one
   this corpus can no longer answer.

**Explicitly not recommended: another λ.** λ = 0.1 being null is not a reason to
try λ = 0.05 or 0.2, and A5 does not authorize a sweep.

---

## 9. The danger this handoff names

**The programme now has eleven well-recorded mechanism findings, a consumed
sealed test, a completed prospective 3-fold experiment — and still no §4.**
E11 was the last thing on the board that could be *run*. Everything remaining
is writing, and this session ends with the same gap ECG 17, 19, 20 and 22 each
named and did not close.

**The characteristic failure of ECG 23: it executed a clean experiment,
audited it, hardened the harness around it, and documented all three
thoroughly — four kinds of defensible work, none of which is the manuscript.**

**The instrumentation now exists for a representation experiment that is not
authorized and may never be run.** That is worth noticing before building any
more of it.
