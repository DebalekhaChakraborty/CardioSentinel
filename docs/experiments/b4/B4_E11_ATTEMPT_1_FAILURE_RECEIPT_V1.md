# E11 ATTEMPT 1 — Failure Receipt, V1

**Written under the §A8 failure policy and the ATTEMPT 1 authorization's retry
rule: the failure state is recorded, execution has STOPPED, and no relaunch,
reseed or fold rerun has been performed.**

| | |
|---|---|
| Attempt | **E11_ATTEMPT_1** |
| Started | 2026-08-26 17:31:46 UTC |
| Failed | 2026-08-26 ~18:49 UTC, during fold 0 arm B1 phase 2 |
| Cause | **implementation defect in the E11 runner** — not a scientific result |
| Scientific attempt consumed | **see §5 — for a human to classify, not me** |

---

## 1. What completed

**Fold 0 · B0 — COMPLETED and clean.**

```
phase 1 (inner selection, inner-train 195,043 / inner-val 30,367)
  ep01 loss 0.19608  inner AUPRC 0.41281   <- selected
  ep02 loss 0.12775  inner AUPRC 0.39119
  ep03 loss 0.10819  inner AUPRC 0.35697
  ep04 loss 0.09782  inner AUPRC 0.35101
  ep05 loss 0.09129  inner AUPRC 0.39412   early stop (patience 4)
selected_epoch = 1
phase 2 (all outer-train 225,410, 1 epoch)  loss 0.17628
held-out (149,042 rows, prevalence 0.2935):  AUPRC 0.689074   AUROC 0.817137
artifacts: e11_fold0_B0.npz  (0 NaN in 149,042 scores and 19,077,376 embedding cells)
```

**Fold 0 · B1 — phase 1 completed, phase 2 diverged.**

```
phase 1  ep01 loss 0.20448  inner AUPRC 0.46056   <- selected
         ep02 loss 0.12959  inner AUPRC 0.40007
         ep03 loss 0.11087  inner AUPRC 0.37407
         ep04 loss 0.09899  inner AUPRC 0.29914
         ep05 loss 0.09292  inner AUPRC 0.40098   early stop
selected_epoch = 1
phase 2  ep01 loss = NaN
held-out: 149,042 / 149,042 scores NaN; 19,077,376 / 19,077,376 embedding cells NaN
crash: ValueError: Input contains NaN  (average_precision_score)
```

**Folds 1 and 2: never started.**

## 2. Root cause — a masking defect in the runner

The registered plan (§1.3 / A1) requires windows with `morphology_valid == 0` or
a non-finite target to be **excluded from the auxiliary loss only**. The runner
implemented that exclusion by **multiplication with a 0/1 mask**:

```python
smooth_l1_loss(a * m, at * m, reduction="sum") / m.sum()
```

**`NaN * 0 == NaN`.** Multiplication does not neutralise a non-finite target; it
propagates it. One masked row in a batch makes the batch loss NaN, which makes
every weight NaN on the optimizer step, which makes every downstream embedding
and score NaN.

**Why phase 1 survived and phase 2 did not — verified, not inferred:**

```
non-finite auxiliary rows, whole TRAIN set: 4
  indices 64573, 262447, 360094, 369943
  subjects s2017, s2049, s3078, s3080   folds 0, 0, 1, 2

fold 0 inner-train  (it): 0 masked rows   -> phase 1 clean
fold 0 outer-train  (ot): 2 masked rows   -> phase 2 poisoned
```

Phase 1 trains on inner-train, which happened to contain none of the four. Phase
2 trains on all of outer-train, which contains two. **The defect was latent for
exactly one phase and then fired.**

## 3. What this is NOT

- **Not a scientific finding about B1.** B1's phase-1 learning was healthy and
  its inner AUPRC at the selected epoch (**0.46056**) was *higher* than B0's
  (**0.41281**). Nothing about the morphology auxiliary objective failed.
- **Not a λ problem, not a target problem, not a protocol problem.**
- **Not attributable to the authorized harness corrections** — those addressed
  process detachment and split assertions, none of which touch loss masking.

## 4. The correction required before any future attempt

Replace multiplicative masking with **index selection**, so non-finite targets
never enter the loss computation:

```python
sel = m.bool()
if sel.any():
    loss = loss + LAMBDA * smooth_l1_loss(a[sel], at[sel], reduction="mean")
```

**Registered additional guard:** assert `torch.isfinite(loss)` after every batch
and fail fast with the batch index, rather than allowing NaN to reach the
optimizer. This is the defect class the programme has catalogued repeatedly — a
check that appears to neutralise a row and does not.

**This is a bug fix in the runner, not a change to the registered experiment.**
The estimand, arms, λ, target, split digest and nested protocol are untouched.

## 5. Classification is a human decision

Unlike ATTEMPT 0, **ATTEMPT 1 produced a real scientific outcome**: fold 0 B0
completed under the registered protocol and its held-out numbers were computed
and observed (AUPRC 0.689074, AUROC 0.817137). **I have not classified this
attempt and have not relaunched anything.**

The §A8 rule states that any re-execution after a failure is a **new attempt
requiring new human authorization**, and that a fold where one arm completed and
the other did not **contributes nothing to the paired contrast**. Under that
rule fold 0 is an incomplete pair.

**Stopped, pending review.**
