# B4 · E6 Cross-Fitted Transfer Instrument — Read-Only Feasibility Audit and Design, V1

**This document audits and designs. It authorizes nothing, implements nothing,
and no model was modified, trained, loaded or scored in producing it.** Every
statement below comes from reading source, manifests and already-published
results.

**Verdict in one line: E6 is scientifically justified and is the correct target,
but it must not be the next action.** A one-hour read-only precision analysis
(§7, "E6a") should gate it, because E6 proper costs ~30 h of compute, needs a
fresh human authorization, and — as scoped in the brief — **cannot narrow the
confidence interval on B4-B at all.** §5.3 explains why, and it is the finding
most likely to be misread.

---

## 1. The exact statistical limitation E1/E2/E2b exposed

### 1.1 The limitation is the cohort, not the models

Three experiments have now failed to separate things that differ substantially
in point estimate:

| Experiment | Contrast | Point | 95% interval | Verdict |
|---|---|---|---|---|
| E2b | B4-B − B4-A | +0.0492 | [−0.03197, +0.13060] | includes zero |
| E2b | B4-B − B4-C | +0.0374 | [−0.03402, +0.10765] | includes zero |
| E1 | A2 − A1 | −0.0601 | [−0.13858, +0.02258] | includes zero |
| E1 | A4 − A2 | +0.1546 | [−0.21502, +0.43390] | includes zero |
| E1 | A5 − A2 | +0.0631 | [−0.01084, +0.09868] | includes zero |

**Every contrast in the programme's development evidence includes zero.** The
common factor is not the estimator, the metric or the architecture. It is that
**the bootstrap unit is the subject and there are twelve of them.**

### 1.2 Why twelve is the binding number

The evaluation resamples **subjects**, not windows, because windows within a
subject are not independent — the split policy fixes the subject as the unit and
`subject_bootstrap_plan` enforces it. Four hundred and seventy-three thousand
windows therefore buy **no** additional resolving power over twelve subjects.
A subject-resampling interval over 12 units cannot be narrow.

**Three consequences already observed:**

1. **E2's epoch bootstrap was not a valid separation instrument.** Bootstrapping
   an *argmax* concentrates on the observed maximum: for n=6, the max is redrawn
   in 66.5% of resamples, so the median and 97.5th percentile both pin to it and
   the interval is one-sided by construction. It looked separating and could not
   separate.
2. **Subject-macro AUPRC is computed over 9 of 12 subjects** in every E1 arm,
   because three validation subjects carry no positive window. The effective
   unit count for that metric is **nine**.
3. **Two metrics disagree about direction.** A4 is +0.0945 above the head on
   pooled AUPRC and −0.1002 below it on subject-macro, on identical scores. With
   9–12 units there is no power to adjudicate which weighting is right.

### 1.3 What this does *not* mean

It does **not** mean the arms are equivalent. It means the experiment is
uninformative about their ordering. Reporting "no significant difference" as
equivalence would be the standard error this programme exists to prevent, and
the E1 report states that explicitly.

---

## 2. Audit: what cross-fitting infrastructure exists

| Component | Status | Bearing on E6 |
|---|---|---|
| `evaluation.metrics.subject_bootstrap_plan` | **exists**, seed 2026, subject-unit | reusable unchanged |
| `neural.t2_paired_bootstrap.paired_subject_bootstrap_difference` | **exists**, paired construction | reusable unchanged |
| `neural.u1_evidence_store` | **exists**, carries `fold_index` | fold-aware store **for calibration over frozen scores** |
| `neural.t1_fold_authority` | **exists** — a label-access security boundary | see §2.2; a safety asset |
| `sklearn.model_selection.GroupKFold` | available in `tactics` | used by E1; no new dependency |
| **Encoder-level cross-fitting** | **DOES NOT EXIST** | **E6 must build it** |
| **Per-fold training driver** | **DOES NOT EXIST** | **E6 must build it** |

**The pattern exists at the wrong layer.** U1 and T1 cross-fit *downstream*
components over a frozen encoder's outputs. Nothing in the repository trains
more than one encoder, and `neural/training.py` has a single-run shape:
one checkpoint selector, one threshold selection, one run directory.

### 2.1 What `training.py` does, and why it matters

`CheckpointSelector.update()` selects on `validation_auprc`; the threshold comes
from `select_validation_f1_threshold`. **Both are single-partition constructs.**
A per-fold driver cannot reuse them unchanged without pointing them at the
fold's own held-out subjects — which would be leakage. §5.2 registers the fix.

### 2.2 `t1_fold_authority` is a safety asset and should be reused

It binds a fold identity, a scope, an explicit subject set and a **sealed
partition** at construction, exposes exactly one single-subject accessor, and
**hard-codes VALIDATION so that TEST cannot be requested — there is no parameter
that could carry it.** For an experiment whose main risk is accidental scope
widening, that is exactly the right pattern to extend rather than reinvent.

---

## 3. The decisive finding: all 68 development subjects have already touched the frozen encoder

**This is why E6 cannot be done cheaply over the cached embeddings.**

| Group | Count | How it influenced the frozen B4-B |
|---|---|---|
| Train subjects | **56** | **Gradient exposure.** The encoder was fitted to their windows |
| Validation subjects | **12** | **Model selection.** The checkpoint is the max-validation-AUPRC epoch (epoch 2 of 6) and the operating threshold is validation-F1-optimal |

**There is no clean subject left in the development pool.** The 12 test subjects
are sealed, consumed, and permanently unavailable.

**The practical consequence, already visible in E1.** The A2 probe scored
**0.9676** pooled AUPRC on subject-grouped CV *within train* and **0.3205** on
validation. Those two numbers are not directly comparable — the train folds sit
at 25% prevalence and validation at 4.56%, and AUPRC is bounded below by
prevalence — so **this audit does not quantify the contamination**, and E6a
(§7) is where a prevalence-independent measurement would go. What is structural
rather than measured is the direction: **the encoder was fitted to those rows,
so its embeddings for them are in-sample.**

**Therefore:** any cross-fit over the *existing* cached embeddings would place
in-sample subjects in held-out folds and produce an optimistic, invalid transfer
estimate. **A valid E6 must retrain the encoder inside each fold.** There is no
read-only path to a 68-subject transfer estimate.

---

## 4. Feasibility against the four constraints

| Constraint | Verdict | Basis |
|---|---|---|
| **No sealed data access** | ✅ **Satisfiable** | E6 uses only the 68 development subjects. The 12 test subjects are never enumerated. `t1_fold_authority`'s pattern makes TEST unrequestable by construction |
| **No experiment-lock changes** | ✅ **Satisfiable** | E6 writes a **new run root**. `B4B_cnn_transformer_v1`'s lock, checkpoint and the four sealed artifacts are read-only inputs at most, and the fold models are not candidates for promotion |
| **No leakage** | ⚠️ **Satisfiable only with nested selection** | The single-partition checkpoint/threshold selectors in `training.py` must not see a fold's held-out subjects. §5.2 registers an inner split. **This is the primary technical risk** |
| **No new model-selection loop** | ⚠️ **Satisfiable only if forbidden explicitly** | Cross-fitting produces K models and K per-fold metrics. Nothing structurally stops someone comparing architectures across folds or picking a best fold. §5.5 must forbid it in writing |
| *(implicit)* **No retraining** | ❌ **NOT satisfiable** | §3. A valid instrument requires per-fold encoder training, hence a **fresh human authorization** |

---

## 5. E6 design

### 5.1 Research question

> Over the 68-subject development pool, what is the **subject-transfer variance
> of the B4 training procedure**, and what is the **fold-to-fold
> threshold-transfer penalty** when an operating point selected inside one fold
> is applied to unseen subjects?

### 5.2 Split strategy — nested, and the nesting is the leakage control

```
68 development subjects
   └── outer: GroupKFold(K), subject-disjoint
         ├── outer-test  fold subjects        → OOF predictions ONLY, never selection
         └── outer-train remaining subjects
               └── inner: subject-disjoint holdout carved from OOUTER-TRAIN ONLY
                     ├── inner-fit    → gradients
                     └── inner-select → checkpoint epoch AND F1 threshold
```

**Registered rules:**

1. **The outer-test fold is touched exactly once per fold, to emit predictions.**
   It never informs a checkpoint, a threshold, a hyperparameter or a stopping
   decision.
2. **Checkpoint and threshold are selected on the inner-select split**, never on
   the outer-test fold. This is the specific change from `training.py`'s
   single-partition shape and it is the leakage control.
3. **The frozen recipe is not re-tuned.** Loss, optimiser, lr, weight decay,
   batch, seed 2026, `class_weighting: null`, `augmentation: null` are inherited
   verbatim from `B4_PROTOCOL_V1` §2.1. **E6 measures a procedure; changing the
   procedure would make it measure something else.**
4. **Folds are fixed before execution** by a recorded, seeded assignment, and
   published in the pre-registration.
5. **Test subjects are never enumerated**, and the fold assigner is constructed
   over the development pool only.

### 5.3 The estimand, and the misreading to pre-empt

**E6 does not produce a narrower confidence interval for B4-B.** Each fold
trains a *different* model. The estimand is:

> the expected transfer performance, and its subject-level variance, **of the
> B4 training procedure** — not of the specific frozen artifact `B4B_cnn_transformer_v1`.

**These are different quantities and the pre-registration must say so on its
first page.** A reader who takes E6's interval as a CI for the sealed-test
number has made exactly the error §9.2 and §9.5 of the discussion draft
catalogue. B4-B's own interval cannot be narrowed: it was evaluated once, on a
sealed partition, and that access is spent.

### 5.4 Allowed metrics

Reported per fold **and** pooled over out-of-fold predictions, always together:

| Metric | Role |
|---|---|
| Pooled window AUPRC | primary — the frozen checkpoint objective |
| **Subject-macro AUPRC** | co-primary, **with its contributing-subject count** |
| AUROC | secondary, prevalence-independent, useful precisely because prevalence differs per fold |
| **Threshold-transfer penalty** | the E6-specific quantity: F1 at the inner-selected threshold on outer-test, minus F1 at the outer-test-optimal threshold |

**Forbidden:** any composite scalar across metrics; any metric added after
results are seen; any per-fold ranking of architectures.

**Prevalence must be reported per fold.** Folds will differ in prevalence, and
AUPRC is bounded below by it — cross-fold AUPRC comparison without prevalence
beside it is the E1 CV trap repeated.

### 5.5 Bootstrap method

**Paired subject bootstrap over the pooled out-of-fold predictions**, 1,000
replicates, seed 2026, reusing `subject_bootstrap_plan` and
`paired_subject_bootstrap_difference` unchanged. **The unit count rises from 12
to 68** — that is the entire point of the experiment.

**A second, distinct interval is required and is easy to omit:** a
**between-fold** interval describing how much the *procedure* varies fold to
fold. The subject bootstrap does not capture it, because it resamples subjects
within a fixed set of fold models. Both must be reported, and the report must
not present the narrower one as the headline.

**Explicitly forbidden:** using E6's folds to select an architecture, a
checkpoint, a threshold or a hyperparameter for any downstream use. E6 is an
instrument, not a selection procedure. **Any such use would create the
model-selection loop the audit was asked to prevent.**

### 5.6 Interpretation boundaries

- **Development evidence only.** No held-out estimate is obtainable within
  LTSTDB, permanently. E6 does not change that and must not be described as
  recovering it.
- **68 subjects, one cohort, one dataset.** Not a confidence interval for a new
  cohort or a new site.
- E6 **cannot** revise the sealed-test result, B4-B's selection, or any
  registered finding. The sealed artifacts are immutable.
- A wide E6 interval is an instrument result, not evidence of equivalence — the
  same rule E1's report applied to itself.

---

## 6. Expected scientific value — **WITHDRAWN 2026-08-26**

> **This section is withdrawn in full.** It projected that four of five of E1's
> unresolved contrasts would resolve at 68 subjects, by assuming interval width
> scales as `1/√n`. **E6a measured that assumption and did not find it.**
> Neither pooled AUPRC nor the prevalence-independent AUROC control produces an
> exponent near `−0.500`; AUROC over `n=6…12` averages about `−0.15`, and the
> AUPRC curves are dominated by a prevalence artefact (`r ≈ +0.5 … +0.8`).
>
> **The projection was the scientific case for E6, and it no longer stands.**
> `B4_E6A_PRECISION_ANALYSIS_REPORT_V1.md` §3 explains why E6a could not replace
> it with a measured estimate either — subsetting removes heterogeneity along
> with units, and the bootstrap is unreliable below ~8 subjects, leaving a
> two-fold usable range from which no six-fold extrapolation is supportable.
>
> **§7's recommendation is superseded by that report's §6: do not request
> authorization for E6 on current evidence.** §3's finding — that all 68
> development subjects have already influenced the frozen encoder, so no
> read-only path to a transfer estimate exists — is unaffected and still stands.
>
> The original text is retained below, struck through, because deleting a
> withdrawn claim would remove the evidence that it was made.

## ~~6. Expected scientific value, quantified~~

**Read-only projection from E1's published intervals.** If subject-bootstrap
width scales as `1/√n`, moving from 12 to 68 units narrows intervals by
`√(12/68) = 0.4201`:

| Contrast | Point | Width @12 | Projected @68 | Projected interval | Would resolve? |
|---|---|---|---|---|---|
| A2 − A1 | −0.0601 | 0.1612 | 0.0677 | [−0.0939, −0.0262] | **yes** |
| A3 − A1 | −0.0534 | 0.1706 | 0.0717 | [−0.0892, −0.0175] | **yes** |
| A4 − A2 | +0.1546 | 0.6489 | 0.2726 | [+0.0183, +0.2909] | yes, marginal |
| A5 − A2 | +0.0631 | 0.1095 | 0.0460 | [+0.0401, +0.0861] | **yes** |
| A5 − A4 | −0.0915 | 0.5570 | 0.2340 | [−0.2085, +0.0255] | no |

**Four of five of E1's unresolved contrasts would plausibly resolve.** That is
the case for E6, and it is a real one.

**Three reasons this is an optimistic upper bound**, and the pre-registration
must carry all three:

1. **`1/√n` is assumed, not measured.** §7 measures it instead.
2. **Cross-fitting adds between-fold model variance** that a fixed-model
   bootstrap does not have. Real E6 intervals will be **wider** than projected.
3. **The estimand changes** (§5.3). These projected intervals are for the frozen
   model; E6's are for the procedure. They are not the same quantity, and the
   table above is an argument about *resolving power*, not a prediction of E6's
   output.

---

## 7. Recommendation: gate E6 behind a one-hour read-only precision analysis

**E6 should proceed — but not next.** Before spending ~30 h and a human
authorization, run **E6a**, which needs neither:

> **E6a — empirical precision scaling.** Using the existing E1 validation scores
> and the 12 validation subjects, subsample subject sets of size 4, 6, 8, 10, 12
> and measure how paired-bootstrap interval width actually scales with unit
> count. Fit the observed exponent instead of assuming `1/√n`, and extrapolate
> to 68.

- **Cost:** ~1 hour, read-only, no training, **no authorization**, no new data.
- **Decides:** whether 68 units plausibly resolve differences of the size E1
  observed. If the measured exponent is materially worse than `1/√n` — which is
  possible, since subject-level heterogeneity does not have to behave like
  independent sampling — then **E6 would spend the remaining window and answer
  nothing**, and that is worth one hour to find out.
- **Precedent:** this is the same discipline that produced the negative
  external-validation audit before any cohort was downloaded.

---

## 8. Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| 1 | **Leakage via per-fold checkpoint/threshold selection.** `training.py` selects on a single validation partition; naively reused, it would select on the outer-test fold | **High** | Nested inner split, §5.2. Assert outer-test subject ids are absent from every selection call |
| 2 | **E6's interval read as a CI for B4-B** | **High** | §5.3 on page one of the pre-registration; the estimand named in every table caption |
| 3 | **A new model-selection loop emerges**, e.g. comparing architectures across folds | **High** | §5.5 forbids it in writing before execution |
| 4 | **The instrument still cannot resolve**, and ~30 h is spent for a null | Medium | **E6a gates it** (§7) |
| 5 | **Between-fold variance omitted**, narrower subject interval reported as the headline | Medium | Both intervals required, §5.5 |
| 6 | Prevalence differs per fold; cross-fold AUPRC compared without it | Medium | Prevalence reported per fold, §5.4 |
| 7 | Fold models mistaken for promotable candidates | Low | New run root; no lock; fold models explicitly non-promotable |
| 8 | Compute overruns the window | Medium | 3-fold reduced variant; decide K **after** E6a |

---

## 9. Estimated effort

| Item | Estimate | Authorization |
|---|---|---|
| **E6a precision analysis** | **~1 hour** | **none** |
| E6 pre-registration | ~2–3 hours | none |
| Per-fold training driver + nested selection + assertions | ~1 day | none (code only) |
| **3-fold cross-fit execution** | **~27–30 h wall clock** (3 × ~6 epochs × ~5,458 s/epoch, plus scoring) | **REQUIRED — fresh human authorization** |
| 5-fold execution | ~45 h+ | **REQUIRED** — exceeds a four-day window alongside everything else |
| Analysis + report | ~0.5 day | none |

**Fifteen of fifteen one-shot budgets are spent.** Every training item above
needs a new authorization that does not currently exist.

---

## 10. Answers to the four questions asked

1. **Should E6 proceed?** **Yes in principle, no as the next action.** It is the
   only path past the n=12 ceiling — §3 shows no read-only path exists, because
   all 68 development subjects have already influenced the frozen encoder.
   **Gate it behind E6a (§7),** which costs an hour and no authorization.
2. **Expected scientific value.** **High, and quantified in §6:** four of five of
   E1's unresolved contrasts would plausibly resolve at 68 units. E6 also
   produces the threshold-transfer penalty, which no existing experiment
   measures and which the operating-point findings in T1/W1 all depend on.
3. **Risks.** Eight, in §8. Three are high: per-fold selection leakage, the
   estimand misreading, and an emergent model-selection loop. **All three are
   controllable by pre-registration and are why this design exists before any
   code.**
4. **Estimated effort.** **~1 hour for E6a**; ~1.5 days of implementation; and
   **27–30 h of authorized compute** for a 3-fold execution. **The compute
   cannot start without a fresh human authorization.**
