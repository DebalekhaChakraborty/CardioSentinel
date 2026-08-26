# CardioSentinel — handoff to session "ECG 22"

Paste this whole file as the first message of the new chat, or say:
"Read handoffs/CARDIOSENTINEL_HANDOFF_ECG22.md in the repo and continue.
Remember to use ONLY tactics venv, not any other venv."

---

## 0. READ FIRST — environment

| | |
|---|---|
| **Scientific interpreter (use this)** | `/home/AI_POC/venvs/tactics/bin/python` |
| Application interpreter (do NOT use) | `/home/AI_POC/venvs/debalekha/bin/python` |
| Repository | `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal` |
| GitHub remote | `DebalekhaChakraborty/CardioSentinel` |
| Scratch (outside the repo) | `/tmp/claude-1000/-home-AI-POC/<session>/scratchpad` |

`tactics` holds 335 packages, `installed_packages_sha256 = b0fd6eaa…`, Python
3.12.6. **Never install, upgrade or downgrade anything in it.**

**The Bash working directory silently resets to `/home/AI_POC`.** Put `cd` in
the same command as the work. **Never `git add -A`.** Several sessions share
this checkout.

---

## 1. THE HEADLINE — E11 ATTEMPT 1 failed on a runner bug, and it is STOPPED

A human authorized **E11 ATTEMPT 1** (a real training experiment). It ran for
~1h20m, completed **fold 0 arm B0 cleanly**, then **arm B1 diverged to NaN in
phase 2** and the process crashed. **Folds 1 and 2 never started.**

**Root cause is a defect in the runner, not in the science:** the auxiliary loss
masked invalid rows by *multiplication*, and **`NaN * 0 == NaN`**. Four TRAIN
rows have a non-finite morphology target; fold 0's inner-train contained none of
them (phase 1 fine) and its outer-train contained two (phase 2 poisoned).

**Full detail, including the exact fix: `docs/B4_E11_ATTEMPT_1_FAILURE_RECEIPT_V1.md`.**

> **DO NOT RELAUNCH E11 WITHOUT A NEW HUMAN AUTHORIZATION.**
> The registered §A8 policy and the ATTEMPT 1 authorization both state that any
> re-execution after a failure is a **new attempt requiring new authorization**.
> ATTEMPT 1 **did** produce an observed scientific outcome (fold 0 B0 held-out
> AUPRC 0.689074, AUROC 0.817137), so unlike ATTEMPT 0 it is **not** obviously a
> free launch failure. **That classification is the human's to make, not yours.**

---

## 2. What the B4 investigation established (E1 → E10), in order

All read-only, all development-only, all reported in `docs/`. **Every one of
these is a *mechanism* finding. None is generalization evidence.**

| Exp | Question | Result |
|---|---|---|
| **E1** | Is information absent from the B4 embedding, or present but unused? | **Unresolvable at n=12.** All 5 contrasts include zero. Morphology beat the head on pooled AUPRC (0.4751 vs 0.3805) and lost badly on subject-macro (0.3004 vs 0.4006) — **one score set, two metrics, opposite verdicts** |
| **E2 / E2b** | Do the B4-A/B/C candidates separate? | **No.** All paired subject-bootstrap intervals include zero. The epoch bootstrap was an invalid instrument (bootstrapping an argmax pins to the max) |
| **E3** | Is the operating point a prior artifact? | **Yes for calibration, no for ranking.** Prior correction moved Brier 0.0656→0.0421, NLL 0.2274→0.1654, and AUPRC/AUROC by **exactly 0.0** |
| **E6a** | Would more subjects resolve anything? | **Cannot tell.** Measured width-scaling exponents are ≈ **−0.15** (AUROC), not −0.5. **The `1/√n` projection in the E6 audit was withdrawn** |
| **E7a** | Static subject-wise score normalization? | **Refuted in direction.** Perfect normalization (ECDF) is the *worst* arm. Subject-macro is invariant by construction, so it cannot help single-patient monitoring at all |
| **E7b** | Static stream-wise normalization? | **Refuted.** Cross-stream discrimination is not consistently worse; stream variation is **discriminative quality**, not offset. One stream is anti-correlated (AUROC 0.2119) |
| **E8a** | Does M1 memory identify unreliable windows/streams? | **Windows yes, streams no.** Errors sit further from the patient prototype (concordance 0.691); FN sit *closer* than TP (0.126) — memory measures **atypicality** |
| **E8b** | Does M1 add information beyond the B4 score? | **Yes, and it survives conditioning.** `d_long` concordance 0.836 → **0.712** stratified; broad across 7/9 subjects. **C0/C1 probe proposed, NOT executed** |
| **E9** | Lead / polarity / label semantics? | **The target is channel-specific but polarity-agnostic** — elevation and depression collapse into one class. Polarity alone does **not** predict failure. SQI does not either |
| **E10** | Is the class direction stable on unseen subjects? | **The decisive one.** TRAIN LOSO cosine min **+0.971**, 0/79 negative. The 3 validation failures are the **3 lowest cosines, 3 smallest ‖delta‖, 3 lowest centroid separations**, with a clean gap. **The head is faithful; the representation fails.** Subject nuisance is *small* (between/class 0.038) |

**E10 is why E11 exists.** Two distinct failure modes: **direction reversal**
(`s20311:1`, cos −0.935) and **direction collapse** (`s20191:*`, ‖delta‖ ≈ 1.0
against a TRAIN minimum of 4.264).

---

## 3. What E11 is

**Hypothesis:** a training-only auxiliary objective preserving signed ST
morphology improves the stability and magnitude of the ischemia class direction
on unseen subjects, versus the otherwise identical B4-B recipe.

| Arm | Definition |
|---|---|
| **B0** | original B4-B recipe under the nested subject-disjoint E11 protocol |
| **B1** | B0 **+** `Linear(128→1)` auxiliary head on the `encode()` tap, target **`post_r_80ms_delta_mv`**, **λ = 0.1**, fold-training median/IQR scaling. **Training-only — discarded before evaluation** |

- **Registration:** `docs/B4_E11_MORPHOLOGY_AWARE_REPRESENTATION_PLAN_V1.md`
  (523 lines, includes the approved pre-execution amendments A1–A8).
- **Split digest (frozen):**
  `ce037309cc2d67944acbee76e82700e5a54c9d2ff69bf54a121ab1b8940206c3`
  — 56 TRAIN subjects, 3 folds (19/19/18), **44 evaluable**, 0 historical
  VALIDATION subjects, 0 TEST subjects.
- **Primary endpoint is geometry** (cosine to the fold-train consensus, ‖delta‖,
  negative-cosine fraction), **not** AUPRC.
- **Auxiliary-target provenance gate PASSED**: `extract_morphology_features`
  takes one `CausalWindow`, never imports `STEvent`, and bounds every index
  inside the window. It is label-free, annotation-free and causal.

---

## 4. Exact state of the E11 artifacts

In the **scratchpad** (outside the repo — copy anything you need to keep):

```
e11_runner.py                     the runner (CONTAINS THE NaN-MASK BUG)
e11_folds.json                    frozen assignment + digest
e11_train_{y,stream,subj,fold}.npy   aligned label/stream/subject/fold arrays
e11_aux_target.npy                post_r_80ms_delta_mv, 374,448/374,452 finite
E11_ATTEMPT_1_LAUNCH_RECEIPT.json provenance written BEFORE training
e11_attempt1.log                  full training log incl. the traceback
e11_fold0_B0.npz                  VALID — embeddings + scores, 0 NaN
e11_fold0_B1.npz                  ALL NaN — do not use
e11_receipt.json                  fold 0 B0 only
```

**The fix (one line, plus a guard) is written out in the failure receipt §4.**
It is a bug fix, not a design change: estimand, arms, λ, target, split and
protocol are untouched.

---

## 5. Standing constraints — still in force, verbatim

- **All fifteen one-shot budgets are spent.** Every training run needs a fresh
  human authorization.
- **The sealed B4-B test is CONSUMED**, `repeat_attempt_permitted: false`. The
  four sealed artifacts are immutable. **Never open them.**
- **NO AUTOMATIC RETRY.** Never add `--force` / `--retry` / `--reset` /
  `--overwrite` / `--fresh-seed`.
- **The historical 12-subject VALIDATION partition is spent for confirmatory
  purposes.** It has been used for hypothesis generation across E1–E10. Any
  future model experiment must use a fresh subject-disjoint split inside the 56
  TRAIN subjects.
- **No held-out estimate is obtainable within LTSTDB, permanently.**
- Development evidence only. **Never claim medical or diagnostic performance.**
- Do not change code in response to scientific results.
- Keep scratch outside the repo.

---

## 6. Traps this programme has actually hit — check these before trusting output

1. **`NaN * 0 == NaN`.** Masking by multiplication does not exclude a row. This
   killed E11 ATTEMPT 1.
2. **B4 arrays are sorted lexicographically, not chronologically** — `0`,
   `10000000`, `1000000`. **0 of 30 validation streams are in time order in the
   array.** The M1 cache *is* chronological (30/30, digest-verified).
3. **`grep -r` here is ugrep and skips gitignored paths** — the evidence trees
   are gitignored. Pass explicit paths or walk in Python.
4. **The Bash cwd resets silently.** A sweep that "found nothing" may have run
   in `/home/AI_POC`.
5. **AUPRC is bounded below by prevalence.** Never compare AUPRC across sets of
   differing prevalence without printing it. E6a measured width-vs-prevalence
   correlation at `r ≈ +0.5…+0.8`.
6. **Subject-macro is over 9 of 12** on validation (three subjects have zero
   positives) and **44 of 56** on train. Print the denominator every time.
7. **A tool-call timeout can SIGTERM a background job.** Launch long runs with
   `setsid nohup … &` and no timeout-linked `sleep` in the same command.
   This killed E11 ATTEMPT 0.

---

## 7. What ECG 22 should do

1. **Report the E11 ATTEMPT 1 failure to the user and ask them to classify it.**
   Do not decide it yourself, and **do not relaunch**.
2. If — and only if — they authorize **ATTEMPT 2**: apply the failure receipt
   §4 fix, re-verify the split digest, write a new launch receipt referencing
   ATTEMPT 1, and launch detached. Expect **~6–9 h** (measured 0.00165 s/window,
   ~321 s/epoch on 195k rows), not the 46 h originally estimated.
3. If they do not: the open branches are **E8b's C0/C1 incremental probe**
   (proposed, unexecuted) and broader representation learning.

**Two things worth telling them plainly.** Under the nested protocol **both arms
selected epoch 1** in fold 0 — training loss falls monotonically while inner
AUPRC peaks immediately, exactly the overfit-within-2-4-epochs signature E2
measured. A B0/B1 contrast between two one-epoch encoders is a weak instrument,
and that is a property of the frozen recipe, not of E11. And **inner-validation
prevalence is 0.024–0.030 against inner-train's 0.25–0.30** — preregistered,
retained deliberately, and explicitly **not** asserted to be harmless.

---

## 8. The danger this handoff names

**This programme is very good at producing true, well-recorded negative results
and has not yet produced a manuscript.** §2's ten experiments are all correct
and all mechanism-only. The paper's §2, §5.6, §9.3 and §9.5 are drafted
(`docs/PAPER_S2_RELATED_WORK_DRAFT.md`, `PAPER_S5_6_…`, `PAPER_S9_…`), **§4 and
§4.6 — the actual contribution — still have no draft**, and every source for
them is already on disk.

**If E11 is not authorized, the highest-value work is writing §4, not designing
E12.**

---

## 9. Monitoring a long E11 run — the practical protocol

**The run does not need a chat open.** It is launched with `setsid nohup`, so it
survives the session ending, the terminal closing, and any tool-call timeout.
**Do not keep a chat alive to babysit it.**

### 9.1 One command that answers "is it alive and where is it"

```bash
S=/tmp/claude-1000/-home-AI-POC/<session>/scratchpad
pgrep -f e11_runner.py >/dev/null && echo ALIVE || echo "NOT RUNNING"
grep -vE "UserWarning|w = torch|^\s*$" "$S/e11_attempt1.log" | tail -5
ls -la "$S"/e11_fold*.npz "$S"/e11_receipt.json 2>/dev/null
```

Anyone can run this, in any chat, at any time. **`NOT RUNNING` plus a receipt
without `finished_utc` means it died — go read the traceback before anything
else.**

### 9.2 What "healthy" looks like

- a new `ep..` line roughly every **5–6 minutes** (~321 s/epoch on ~195k rows);
- `train_loss` finite and falling — **any `nan` means the run is already dead**,
  even if the process is still up;
- a `FOLD k ARM: sel_ep=… held-out AUPRC=…` line roughly every **35–40 min**;
- `e11_fold{k}_{arm}.npz` appearing after each arm completes. **A B1 file
  dramatically smaller than its B0 sibling means all-NaN** — NaN compresses.

### 9.3 Expected shape of a complete ATTEMPT 2

6 model-fits: 3 folds × {B0, B1}, each phase 1 (≤15 epochs, early stop ~5) plus
phase 2 (selected epochs). **~6–9 h total.** Six `e11_fold*.npz`, and a receipt
ending with `finished_utc` and `failure_state: null`.

### 9.4 Do not

- **Do not poll every few minutes.** Every check costs a turn and tells you
  nothing new between epochs. Check once an hour at most.
- **Do not relaunch on failure.** §5 and the failure receipt govern: write the
  failure state, stop, report, wait for human authorization.
- **Do not inspect intermediate fold outcomes to make training decisions.** The
  nested selection procedure is the only permitted decision rule.
