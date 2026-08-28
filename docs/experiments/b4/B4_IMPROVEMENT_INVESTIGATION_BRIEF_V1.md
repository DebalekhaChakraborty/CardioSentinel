# B4 Improvement Investigation — Read-Only Audit and Experiment Brief, V1

**Paste this file as the first message of a new chat, or say:**
*"Read `docs/experiments/b4/B4_IMPROVEMENT_INVESTIGATION_BRIEF_V1.md` and continue. Remember to
use ONLY the tactics venv, not any other venv."*

**This document grants no scientific permission and authorizes no execution.**
Every experiment in §6 requires its own pre-registration and its own human
authorization before anything runs, exactly as T1, T2, U1 and W1 each did.
**Fifteen of fifteen one-shot budgets are spent**, so there is no budget to draw
on and every retraining item needs a fresh one.

| | |
|---|---|
| Class | read-only audit + forward plan, post-hoc derived |
| Authorizes | **nothing** |
| Scope | the **B4 encoder**, Phase 3B-2. Not the IPS |
| Companions | `B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md`, `IMPROVEMENT_ROADMAP_V1.md` |

---

## 0. READ FIRST — environment and shared checkout

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do NOT use) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| GitHub remote | `DebalekhaChakraborty/CardioSentinel` |

**Never install, upgrade or downgrade anything in `tactics`.**

**You share this checkout with other sessions and with the user at the keyboard.**
`HEAD` moves under you between commands, and the working tree frequently holds
other people's uncommitted files. Run `git status` immediately before anything
that assumes a branch or a clean tree, **stage explicit paths only**, never
`git add -A`, and **do not clean up untracked files you did not create.**

**Read the highest-numbered `handoffs/CARDIOSENTINEL_HANDOFF_ECG<N>.md` first.**
That chain carries session state and is often owned by a live session; this
document carries subject matter and does not move with it.

---

## 1. Scope — what "improving B4" means, precisely

`B4_PROTOCOL_V1` §Scope, frozen prospectively in Phase 3B-2:

> B4 is a global, single-channel comparator to the frozen B0–B3 classical
> baselines. **It is not the CardioSentinel contribution and contains no
> personalization, temporal episode reasoning, foundation-model knowledge, or
> cloud inference.**

So **the improvement target is the encoder.** P1-B fusion, M1L memory, M2-G
gating, U1 calibration, T2/S4D and the T1 state machine are downstream
consumers, each with its own separate experiment record and its own
development-only evidence. They were never part of the B4 sealed evaluation and
cannot be improved or blamed through it.

### 1.1 The result this work follows, as fixed historical finding

```
B4-B sealed test, 2026-08-25, attempt 1 of 1, repeat_attempt_permitted false
pooled-window AUPRC  0.0935334   at prevalence 0.0460529
```

**Treat it as a fixed historical finding.** Do not access, modify, infer from or
attempt to re-run the sealed artifacts. Do not optimise against it. Do not
select among the experiments in §6 by their fit to it — that is test-informed
selection, and it is the one failure this whole apparatus exists to prevent.

The registered comparison it answers is to B0–B3, on the identical partition:

| Model | Pooled AUPRC | AUROC | Subject-macro AUPRC |
|---|---|---|---|
| B0 constant prior | 0.0460529 | 0.5000 | 0.042561 |
| B1 signal logreg | 0.1172989 | 0.7900 | 0.334247 |
| B2 morphology logreg | 0.1640117 | 0.8227 | 0.405035 |
| **B3 morphology HGB** | **0.1682901** | **0.8360** | **0.436410** |
| B4-B neural | 0.0935334 | 0.7332 | 0.354901 |

**The registered research question is answered *no*.** B4-B was also below B3 on
validation (0.3805 against 0.6801), so the sealed test confirmed the development
ordering rather than reversing it.

---

## 2. B4-B architecture, exactly as built

```
SharedLocalFrontEnd          Conv1d(1→32, k=15, s=2, pad=7, bias=False)
  26,160 params, shared      GroupNorm(8, 32, eps=1e-5) → SiLU
                             DepthwiseSeparableBlock(32→48,  k=9)
                             DepthwiseSeparableBlock(48→64,  k=7)
                             DepthwiseSeparableBlock(64→96,  k=5)
                             DepthwiseSeparableBlock(96→128, k=5)
positional_embedding         [79, 128] learned, init N(0, 0.02)
2 × PreNormTransformerBlock  MHA(d=128, heads=4, head_dim=32, attn_dropout=0.0)
                             FF(128→256→128, GELU)
                             Dropout(0.10) ×2 — one site per residual branch
final_norm                   LayerNorm(128, eps=1e-5)
SharedClassifierHead         AdaptiveAvgPool1d(1) → Dropout(0.10)
  8,321 params, shared       → Linear(128→64) → SiLU → Dropout(0.10) → Linear(64→1)
```

**309,809 trainable parameters**, 1,239,236 FP32 bytes.

**Input** `[B, 1, 2500]`, 250 Hz, raw mV, `processing_profile: raw identity`. No
filtering, no notch, no `filtfilt`, no per-window z-scoring, no amplitude
normalisation, no R-peaks, J-points, ST measurements or handcrafted features.

**`encode()`** returns the pooled `[B, 128]` representation after the final
LayerNorm and pooling, before the head's first dropout. This is the tap P1
fusion and M1 memory consume, and it is exposed explicitly so callers cannot
reconstruct it differently.

**Attention is fully bidirectional inside the window** — `attn_mask=None`,
`key_padding_mask=None`. Causality is enforced at the *window* level, on
completed 10-second windows with 5-second stride, not within a window.

### 2.1 The frozen training recipe

| | |
|---|---|
| Loss | `BCEWithLogitsLoss(reduction=mean)` · **`class_weighting: null`** |
| Optimizer | AdamW, one parameter group · lr `1e-3` · wd `1e-4` · β (0.9, 0.999) · eps `1e-8` · no amsgrad |
| Scheduler | **none** |
| Batch | 256 · `drop_last=False` |
| Epochs | max 15 · early stop patience 4, δ `1e-6` |
| **Augmentation** | **`null`** — no noise, amplitude scaling or lead dropout, explicitly forbidden |
| Seed | 2026 · no mixed precision |
| Checkpoint | maximum pooled validation AUPRC; earliest epoch wins an exact tie |
| Threshold | validation F1-optimal, after restoring the checkpoint |
| **Cost** | **5,458 s/epoch → a full 15-epoch run is 22.7 h** |

---

## 3. The two findings that should drive the work

Both are measurable from development artifacts alone and were measurable before
any test access.

### 3.1 The training prior is mismatched by 5.478×, uncorrected

```
train        93,613 / 374,452  =  0.250000   (56 subjects)   ← exactly 25%
validation   21,628 / 473,897  =  0.045639   (12 subjects)
```

The model is fitted to a 25% base rate under **unweighted** BCE and scored at
4.6%. That is a systematic logit offset, and it is why the F1-optimal threshold
sits at **0.8329097628593445** rather than anywhere near the prior.

### 3.2 Every candidate was selected on the peak of a noisy oscillation, while overfitting

| | selected epoch | completed | val AUPRC spread | argmax-over-epochs bias |
|---|---|---|---|---|
| B4-A | **4** | 8 | 0.11715 | +0.05456 |
| B4-B | **2** | 6 | 0.07770 | +0.03211 |
| B4-C | **2** | 6 | 0.10164 | +0.05393 |

B4-B's trace, against a monotonically falling training loss `0.198 → 0.101`:

```
ep1 0.37949   ep2 0.38053 ←selected   ep3 0.30284
ep4 0.37282   ep5 0.32043             ep6 0.33443
```

**Loss down, validation AUPRC flat-to-down from epoch 2.** All three candidates
overfit inside two to four epochs of a fifteen-epoch budget, and the validation
set — 12 subjects — is too small to measure it stably.

**The consequence for selection.** B4-B beat B4-C on the dominance metric by
**0.0428**, while B4-B's own epoch-to-epoch spread on that metric is **0.0777**.
**The evidence does not separate the three candidates at this validation size.**

---

## 4. The B4 family, and why B4-B was selected

| | B4-A `B4CompactCNN` | **B4-B `B4BTransformerCNN`** | B4-C `B4CSSMCNN` |
|---|---|---|---|
| Params | 87,089 | **309,809** | 155,313 |
| FP32 bytes | 348,356 | 1,239,236 | 621,252 |
| Median latency ms/window | 3.275 | **4.161** | 14.436 |
| p95 latency ms/window | 3.528 | 4.337 | 15.315 |
| **Val pooled AUPRC** | 0.31560 | **0.38053** | 0.33777 |
| Val subject-macro AUPRC | 0.36582 | 0.40064 | **0.40332** |
| Rate-related FPR | 0.34567 | **0.33119** | 0.46511 |
| Axis-shift FPR | 0.10200 | **0.06167** | 0.11767 |

`B4_ARCHITECTURE_SELECTION_PROTOCOL_V1` defines a **Pareto dominance** test over
pooled validation AUPRC plus a resource vector (parameters, bytes, latency,
memory). B4-B leads pooled AUPRC and both challenge FPRs; B4-C is slower *and*
lower on pooled AUPRC, so it is dominated. **Subject-macro AUPRC and the
challenge fractions are mandatory review dimensions and deliberately excluded
from the dominance test** — the protocol says so explicitly, and forbids
folding them into a post-hoc scalar score.

**The rule was applied correctly.** The observation in §3.2 is that the margin
it decided by is smaller than the noise it was measured against — a property of
the evidence, not a violation of the protocol.

---

## 5. Available development assets

| | |
|---|---|
| Training entry points | `neural/candidate_experiment.py`, `neural/training.py` |
| Checkpoints | `model_selected.pt`, `training_checkpoint.pt` per candidate |
| Locks | `EXPERIMENT_LOCK.json` ×3 · self-referential digest · `neural.integrity.verify_experiment_lock()` |
| Validation metrics | `VALIDATION_METRICS.json` (B4-B); `RESULTS_SUMMARY.json` validation blocks (B0–B3) |
| Challenge evidence | `VALIDATION_CHALLENGE_RESULTS.json` — all three candidates × all strata |
| Resource benchmark | `RESOURCE_BENCHMARK_RESULTS.json` |
| **Cached B4-B embeddings** | `cardiosentinel-features/p1-b4b-embeddings-v1/{train,validation}` — **already materialised** |
| Morphology corpus | `cardiosentinel-features/ltstdb-baseline-v1` |
| **Ablations** | **none exist** |
| **Unused budgets** | **zero** |

The cached embeddings matter: the highest-value experiment below needs **no
retraining**.

---

## 6. Experiment slate

**Budget arithmetic: four days ≈ 96 h ≈ four 15-epoch retrains.** No-retraining
experiments come first on merit *and* on arithmetic.

### E1 · Representation gap probe — run this first
- **Research question.** Does B4-B's 128-d embedding contain the ST-morphology
  information B2/B3 use, or is it absent?
- **Change.** None to any model. Probe from the **cached** B4-B embedding to B3's
  morphology features on identical windows; then both feature sets into a common
  classifier.
- **Why justified.** The registered comparison asked whether the learned
  representation beats handcrafted morphology. This decomposes *"it lost"* into
  **information absent** versus **information present but unused by the head** —
  which imply opposite fixes.
- **Data allowed.** Train + validation embeddings and morphology corpus, both
  cached. No test.
- **Expected impact.** High — it selects between E4/E5 and a representation
  change. **Risk:** low. **Effort:** ~1 day.
- **New authorization.** No new budget; derived analysis on existing development
  artifacts. Pre-register per §47.

### E2 · Selection-variance audit
- **RQ.** How much of each candidate's reported validation AUPRC is
  argmax-over-epochs bias, and does the evidence separate B4-A/B/C at all?
- **Change.** None. Bootstrap epoch-to-epoch variance from `EPOCH_HISTORY.json`;
  compare the selection margin against it.
- **Why justified.** A selection margin smaller than its own measurement noise is
  not a selection. Determines whether future architecture comparisons are
  resolvable at n=12 at all.
- **Data.** Existing artifacts only. **Impact:** high, methodological.
  **Risk:** none. **Effort:** hours. **New authorization:** none.

### E3 · Prior-mismatch correction
- **RQ.** How much of the operating point is explained by the 5.478× mismatch?
- **Change.** Analytic logit adjustment on frozen validation scores; re-derive
  threshold and operating-point metrics.
- **Why justified.** Prior shift under unweighted BCE is analytically
  correctable. **Pre-register the invariance up front: the correction is
  monotone, so AUPRC and AUROC cannot move.** Its value is threshold behaviour
  and calibration, never ranking. *(This exact error was made once already about
  U1 — a global Platt is also monotone and also cannot move AUPRC.)*
- **Data.** Validation only. **Impact:** medium. **Risk:** low. **Effort:** hours.
  **New authorization:** none.

### E4 · Class-prior and loss arm — first retraining experiment
- **RQ.** Does training at the evaluation prior, or with `pos_weight` / focal
  loss, improve subject transfer?
- **Change.** One retrain arm with corrected prior handling; everything else
  frozen.
- **Why justified.** `B4_PROTOCOL_V1` *forbade* this axis, so it is genuinely
  unexplored — **a new experiment, not a B4 re-run.**
- **Data.** Train + validation. **Impact:** medium. **Risk:** medium — may move
  only the operating point. **Effort:** ~1 day (one run).
  **New authorization: yes.**

### E5 · Regularisation and checkpoint averaging
- **RQ.** Does averaging checkpoints across epochs, instead of taking the argmax,
  reduce selection variance and improve transfer?
- **Change.** Average the epoch checkpoints already on disk; optionally one
  regularised retrain.
- **Why justified.** All three candidates overfit by epoch 2–4; averaging attacks
  the argmax bias E2 quantifies **without new compute**.
- **Data.** Train + validation. **Impact:** medium-high. **Risk:** low.
  **Effort:** hours for averaging, ~1 day for a retrain.
  **New authorization:** none for averaging; **yes** for the retrain.

### E6 · Cross-fitted subject-transfer instrument
- **RQ.** What is subject-transfer variance over the 68-subject development pool,
  and what is the fold-to-fold threshold-transfer penalty?
- **Change.** Leave-subjects-out cross-fitting; report pooled **and** subject-macro
  per fold, plus their divergence, as first-class metrics.
- **Why justified.** A single 12-subject draw cannot estimate transfer variance —
  §3.2 demonstrates this from the epoch traces alone. Every later claim depends
  on this instrument.
- **Data.** Train + validation. **Impact:** highest long-term. **Risk:** low.
  **Effort:** **exceeds four days at full scale** (5 folds × 6 epochs ≈ 45 h plus
  scoring). Run a 3-fold reduced version inside the window.
  **New authorization: yes.**

### Deprioritised, with reasons — so nobody re-proposes them
- **Larger encoder / architecture search.** B4-B carries 3.6× B4-A's parameters
  and overfits inside two epochs. **Capacity is not the binding constraint;
  effective sample size is.** E1 must come first — searching architectures before
  knowing what B3's features carry that the embedding does not is guessing.
- **Temporal-context changes.** Out of scope for B4 by protocol, and T2's own
  selection contrast **[-0.015229, 0.148951]** spans zero, so there is no
  established temporal gain to improve on.
- **Augmentation.** Worth doing eventually; E1 should first establish whether the
  missing signal is representational.

---

## 7. Suggested four-day sequence

| Day | |
|---|---|
| 1 | **E2** and **E3** — both hours, both zero-risk, both zero-authorization |
| 1–2 | **E1**, the decisive question |
| 3 | **E5** checkpoint averaging, then launch one retrain arm — **E4 or E5 chosen by what E1 says** |
| 4 | **E6**, three-fold reduced |

**Do not launch a retrain before E1 reports.** Choosing the arm first and
justifying it afterwards is the same error as diagnosing before comparing.

---

## 8. Standing constraints that bind this work

- **The sealed test is consumed.** No second attempt exists or can.
  `repeat_attempt_permitted: false`. The four artifacts are immutable — do not
  regenerate, amend or "fix" any of them.
- **Do not optimise against the sealed-test result**, and do not select among
  §6's experiments by their fit to it.
- **NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.** Never add `--force`, `--retry`,
  `--reset`, `--overwrite` or `--fresh-seed`.
- **Every retraining item needs a fresh human authorization.** Fifteen of fifteen
  budgets are spent; there is nothing to draw on.
- **No held-out estimate is obtainable within LTSTDB, permanently.** Test subjects
  are consumed and the development subjects have all been used for selection.
  Every result from §6 is **development evidence**; report it as *"mechanism
  understood"*, never *"performance improved"*.
- Keep scratch files **outside the repo**.
- Patient identity selects a state namespace and a calibrator; **never** a
  predictive feature.
- Labels never determine memory-stream membership, ordering or update
  eligibility.

---

## 9. Three traps specific to this material

1. **A monotone transform cannot change AUPRC or AUROC.** Global Platt
   calibration and analytic prior correction are both monotone. They move
   thresholds and probabilities, never ranking metrics. Pre-register that
   invariance or someone will claim a ranking gain that is arithmetically
   impossible.
2. **`grep -r` from the repository root silently skips the evidence trees**,
   because they are gitignored. Any count of files or occurrences must pass
   explicit paths or walk the tree in Python, and must state its exclusions.
3. **Compare against comparators that already exist before diagnosing.** The
   B0–B3 results sat consumed and unread while a diagnosis was written from
   B4-B's numbers alone; two claims had to be withdrawn. See
   `B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md` §8.1.
