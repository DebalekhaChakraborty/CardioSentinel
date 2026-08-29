# B4 · E2 Selection-Variance Audit and E3 Prior-Mismatch Correction — Preregistered Analysis Plan, V1

**Pre-registration. No result of either analysis has been computed in preparing
this document.** Everything below is derived from artifact *structure* — file
inventories, `.npz` column names, dtypes and shapes, `score_semantics` strings —
and from values already published in
`docs/experiments/b4/B4_IMPROVEMENT_INVESTIGATION_BRIEF_V1.md`,
`docs/experiments/b4/B4_GLOBAL_ENCODER_SELECTION_V1.md` and
`docs/experiments/b4/B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md`.

**This plan authorizes nothing, and needs nothing.** E2 and E3 are derived
analyses over existing development artifacts. **No model is loaded, no training
runs, no budget is opened, and no sealed artifact is opened.** The brief records
both as *"New authorization: none"*, and this plan does not widen that.

| | |
|---|---|
| Experiments | **E2** selection-variance audit · **E3** prior-mismatch correction |
| Source | `B4_IMPROVEMENT_INVESTIGATION_BRIEF_V1.md` §6, §7 day 1 |
| Partition | **development validation only.** Train counts are read from published metadata; **no test artifact is opened** |
| Evidence class | `development_validation_result` — the same class the inputs carry |
| Authorization | **none required, none requested, none granted** |

---

## 0. What is deliberately not touched

`cardiosentinel-runs/phase3b2-architecture-v1/B4B_cnn_transformer_v1/` holds
four sealed-test artifacts — `TEST_PREDICTIONS.npz`, `TEST_METRICS.json`,
`TEST_ATTEMPT.json`, `TEST_AUDIT.json`. **They are not opened by this plan or by
the code that executes it**, not read for shape, not read for schema, and not
counted. §8 of the brief says *"do not access, modify, infer from or attempt to
re-run"* them, and *access* is the binding word.

The sealed result is a fixed historical finding. **Neither analysis is selected,
tuned, or reported by its fit to that result.**

---

## 1. A correction to the brief, recorded before it causes an error

The brief's §5 lists `EPOCH_HISTORY.json` as an available asset without saying
where each candidate's lives. **They are not co-located:**

```
cardiosentinel-runs/phase3b2-architecture-v1/B4B_cnn_transformer_v1/EPOCH_HISTORY.json
cardiosentinel-runs/phase3b2-architecture-v1/B4C_cnn_ssm_v1/EPOCH_HISTORY.json
cardiosentinel-runs/phase3b2-b4-v1/B4_raw_compact_cnn_v1/EPOCH_HISTORY.json   ← B4-A
```

**B4-A is under a different phase root.** An implementation that enumerated
`phase3b2-architecture-v1/*/EPOCH_HISTORY.json` — the obvious glob, and the one
the brief's own asset table invites — would load two candidates, compute a
plausible number, and answer *"does the evidence separate B4-A/B/C?"* with B4-A
silently absent.

**E2 therefore names all three paths explicitly and asserts three loaded before
computing anything.** That assertion is registered here as a required part of the
analysis, not an implementation detail. This is trap 2 of the brief's §9 in a
different costume, and it is the failure class
`PAPER_S9_DISCUSSION_DRAFT.md` §9.5.5 catalogues.

---

## 2. E2 — selection-variance audit

### 2.1 Question

> How much of each candidate's reported validation AUPRC is argmax-over-epochs
> bias, and **does the evidence separate B4-A, B4-B and B4-C at all?**

### 2.2 Data

The three `EPOCH_HISTORY.json` files named in §1, and nothing else. Each carries
`epochs: [{epoch, mean_training_loss, validation_auprc, checkpoint_saved,
early_stopping_patience}]`.

### 2.3 Registered statistics — fixed before execution

For each candidate, over its **completed** epochs:

| Statistic | Definition |
|---|---|
| `selected_auprc` | the value at the selected epoch, by the frozen rule: **maximum validation AUPRC, earliest epoch wins an exact tie** |
| `spread` | `max − min` of `validation_auprc` |
| `argmax_bias` | `selected_auprc − mean(validation_auprc)` |
| `epoch_bootstrap` | resample the completed epochs with replacement, **1,000** draws, seed **2026**; recompute the selection rule on each draw; report the 2.5th/50th/97.5th percentiles of the selected value |

Pairwise between candidates: `margin = selected_auprc(i) − selected_auprc(j)`.

**The registered comparison** is `margin` against the two candidates' `spread`
and against the width of their `epoch_bootstrap` intervals.

### 2.4 Registered predictions

Stated now so they can be wrong.

1. **The B4-B/B4-C margin will be smaller than B4-B's own epoch spread.** The
   brief already reports 0.0428 against 0.0777 from the published traces; E2
   restates it with an interval rather than a point.
2. **All three `epoch_bootstrap` intervals will overlap each other.**
3. **`argmax_bias` will be positive for all three**, necessarily — the maximum of
   a set is not below its mean. **This statistic cannot come out negative, and
   reporting it as a finding would be reporting arithmetic.** Its magnitude
   relative to `spread` is the only informative part.

### 2.5 What would refute the motivating claim

If the pairwise margins were **larger** than the epoch spreads and the bootstrap
intervals were disjoint, the selection would be separable at n=12 and §3.2 of
the brief would be overstated. That outcome is reported as written if it occurs.

### 2.6 The bound this analysis cannot escape

Six or fewer epochs per candidate. **A bootstrap over six values estimates
almost nothing well**, and its interval is a description of those six numbers
rather than of the sampling distribution of the training procedure. E2 reports
the interval **with its n stated beside it every time**, and does not claim it as
an estimate of run-to-run variance — which would require repeated training runs
and therefore a budget that does not exist.

---

## 3. E2b — subject-level separation, registered as an addition

**This is not in the brief and is registered as an extension**, with its
justification, rather than smuggled into E2.

E2 as scoped answers *"is the margin smaller than epoch noise?"* It does not
answer *"is the margin smaller than **subject** noise?"*, which is the question
that decides whether a 12-subject validation set can rank architectures at all —
and the necessary data is already on disk in the three
`validation_predictions.npz` files.

**Registered method.** Paired subject bootstrap, **1,000** draws, seed **2026**,
resampling the **12 validation subjects** with replacement; on each draw
recompute each candidate's pooled validation AUPRC on the resampled rows and
take the paired differences B4-B−B4-A, B4-B−B4-C, B4-A−B4-C. Report each
difference's 2.5th/50th/97.5th percentiles. **Paired**, because the same subjects
are resampled for every candidate — the T2 arm comparison used the same
construction and it is the reason its interval is honest.

**Registered prediction.** All three paired intervals will include zero.

**Registered invariance.** With 12 subjects the bootstrap can draw at most 12
distinct subjects; **the reported interval is a subject-resampling interval and
not a confidence interval for a new cohort.** Stated here so the report cannot
quietly upgrade it.

---

## 4. E3 — prior-mismatch correction

### 4.1 Question

> How much of B4-B's operating point is explained by the **5.478×** train/
> validation prior mismatch, and what does correcting it analytically move?

### 4.2 The mismatch, from published metadata

```
train        93,613 / 374,452  =  0.250000    (56 subjects)
validation   21,628 / 473,897  =  0.045639    (12 subjects)
```

### 4.3 Registered method

`score` is documented in `VALIDATION_METRICS.json` as *"uncalibrated sigmoid
model score; not calibrated probability"*, so the logit is recoverable:

```
z       = log(score / (1 - score))
offset  = log( (0.25/0.75) / (0.045639/0.954361) )
z'      = z - offset
score'  = 1 / (1 + exp(-z'))
```

Scores are clipped to `[eps, 1-eps]` with `eps = 1e-12` before the logit, and
the clip count is **reported**, not silently applied.

### 4.4 THE REGISTERED INVARIANCE — the reason this plan exists

`z' = z - offset` with `offset` constant is a **strictly monotone increasing**
transform of `score`. Therefore:

> **AUPRC, AUROC and every rank-based statistic are numerically invariant under
> this correction. They cannot move. If they move, the implementation is wrong.**

This is registered as a **correctness check on the code**, not as a finding. It
is written here, before execution, because the brief's §9 trap 1 records that
this exact error was made once already about U1 — a global Platt fit is also
monotone and also cannot move AUPRC — and because a ranking gain claimed from a
monotone map is arithmetically impossible rather than merely unsupported.

**What may legitimately move:** the F1-optimal threshold's *value*; calibration
metrics (NLL, Brier); and the confusion matrix at a **fixed** probability
threshold. Nothing else.

### 4.5 Registered predictions

1. **AUPRC and AUROC will be identical to `VALIDATION_METRICS.json` to at least
   1e-12**, in both directions.
2. `offset` ≈ **1.94** nats, so corrected scores are uniformly lower.
3. The F1-optimal threshold on corrected scores will be **below** 0.8329097628593445,
   and the **set of windows** it selects will be **identical** to the set selected
   by the original threshold — because the threshold and the scores move under
   the same monotone map. **If the selected sets differ, the implementation is
   wrong.**
4. Calibration will improve — corrected scores are nearer the evaluation prior —
   and **that is the only substantive result E3 can produce.**

### 4.6 What E3 explicitly does not establish

**Nothing about performance.** A monotone correction cannot improve detection. E3
answers *"is the operating point explained by a prior offset?"* and its answer is
about **threshold semantics and calibration**, never about ranking quality.

---

## 4a. Amendment 1 — replicate count, made before execution

**As first drafted this plan registered 10,000 bootstrap replicates. It now
registers 1,000.** `evaluation/protocol.py` fixes
`BOOTSTRAP_REPLICATES = 1000`, `BOOTSTRAP_SEED = 2026`, and **every experiment in
the programme uses those values** — T1, T2, U1 and W1 without exception. A
derived analysis reporting an interval computed at a different replicate count
than the intervals it will be read beside is a gratuitous inconsistency, and
E2b's whole purpose is to be comparable to T2's published paired interval.

**The amendment is recorded rather than silently applied**, and it was made
before either analysis ran. E2b reuses
`neural.t2_paired_bootstrap.paired_subject_bootstrap_difference` and
`evaluation.metrics.subject_bootstrap_plan` directly rather than reimplementing
the construction, so the comparison to T2 is exact by construction and not by
resemblance.

---

## 5. Reporting rules, binding on the report that follows

- Every number is **development evidence**. Report as *"mechanism understood"*,
  never *"performance improved"* — brief §8.
- **No held-out estimate is obtainable within LTSTDB, permanently.** No sentence
  may imply one.
- The `n` behind every interval is stated beside it: **6 or fewer epochs** for
  E2, **12 subjects** for E2b.
- Refuted predictions are reported as refuted, in the form registered here.
- **No sealed-test artifact is opened, quoted, or compared against.**
- Scratch files live outside the repository.
