# B4-B Sealed Test Post-hoc Failure Mode Analysis, V1

**POST-HOC ANALYSIS. This document was written after the sealed-test values were
read.** It is not part of the pre-registration in `B4_PROTOCOL_V1` and carries
none of that document's authority. Every quantity here that is not already
registered in `TEST_METRICS.json` or `VALIDATION_METRICS.json` is arithmetic on
published values and is labelled **post-hoc descriptive** where it appears.

**§6.4 of `B4_TEST_AUTHORIZATION_V1.md` fixed the reporting commitment before
access, and §9.8 of `PAPER_S9_DISCUSSION_SKELETON.md` binds what may change
because of the result: the number goes in §7, one sentence goes in §9.1, and no
thesis in §9 moves.** This document adds neither. It is new explanatory
material, on the precedent of `T1_POST_HOC_ANALYSIS_V1.md`, and it must not be
cited as a revision of anything pre-registered.

## What this document does not do

| | |
|---|---|
| Changes the primary endpoint | **No.** The registered primary remains pooled-window AUPRC |
| Changes the primary value | **No.** `0.0935334` is unchanged and is not recomputed anywhere here |
| Changes the threshold | **No.** `0.8329097628593445` is frozen, validation-selected, `test_informed: false` |
| Presents an alternative headline | **No.** No corrected, adjusted or re-scored figure is computed or implied |
| Reads test predictions | **No.** `TEST_PREDICTIONS.npz` was not opened. Only registered values in `TEST_METRICS.json` are quoted |
| Recomputes any test metric | **No** |
| Alters any artifact | **No.** All four digests re-verify unchanged (§7.1) |
| Revises §9 | **No.** §9 was drafted and merged **before** the test opened, and that ordering is the claim |

The registered result stands exactly as reported:

```
Pooled-window AUPRC            0.0935334      prevalence 0.0460529
AUROC                          0.7332374
Subject-macro AUPRC            0.354901       over 8 of 12 subjects
95% subject-bootstrap AUPRC    [0.033058, 0.239284]
```

This analysis explains **what that number is made of**. It does not adjust it,
and a reader who wants a single figure should continue to use the registered one.

---

## 1. What was scored — and why that is correct, not a near-miss

**The sealed test evaluated the B4-B encoder alone, as a raw-waveform window
classifier. That is exactly what it was pre-registered to evaluate.**

From `TEST_ATTEMPT.json`:

```
input_contract    [B, 1, 2500] · 1 channel · raw mV · 250 Hz
                  processing_profile "raw" · handcrafted_features_used false
model             B4BTransformerCNN  <-  model_selected.pt
                  experiment_id B4B_cnn_transformer_v1  (Phase 3B-2)
score_semantics   uncalibrated sigmoid model score; not calibrated probability
```

`B4BTransformerCNN` has 309,809 parameters, and its submodule classes are
`Conv1d`, `DepthwiseSeparableBlock`, `MultiheadAttention`, `LayerNorm`,
`GroupNorm`, `Linear` and pooling. No state-space block, no memory, no
calibrator.

**`B4_PROTOCOL_V1.md` §Scope, frozen prospectively in Phase 3B-2, says so in its
own words:**

> B4 is a global, single-channel comparator to the frozen B0–B3 classical
> baselines. **It is not the CardioSentinel contribution and contains no
> personalization, temporal episode reasoning, foundation-model knowledge, or
> cloud inference.**

And the registered research question:

> Does a compact end-to-end neural representation learned directly from the same
> causal single-channel ECG windows **improve subject-disjoint discrimination
> relative to the frozen global classical baselines**, without personalization,
> temporal episode reasoning, foundation-model knowledge, or cloud inference?

**An earlier revision of this section presented the encoder-only scope as a
discovery and a near-miss. That was wrong and is corrected here.** The scope was
declared before the experiment ran, the input contract matches it exactly, and
nothing was lost. What was wrong was a later description that listed the
sealed-test subject as `B4BTransformerCNN + T2 S4D + M1L + M2-G + U1`; the
protocol never did.

**Two things that remain true and matter for the manuscript.**

1. **§7 must name the scored artifact** — *B4-B window-level encoder,
   uncalibrated, at the frozen validation threshold* — and must not imply the
   number characterises the assembled IPS. The IPS has no sealed-test result and
   never did, because the phases that built it came after this budget was
   defined.
2. **The registered comparison is to B0–B3, and §1.1 makes it.**

### 1.1 The pre-registered comparison

All five models were scored on the **identical** test population — 453,804
windows, 20,899 positive, 432,905 negative, prevalence
`0.0460529215255925` to sixteen places — and all five report subject-macro
discrimination over the same **8 of 12** subjects.

| Model | Pooled AUPRC | AUROC | Sensitivity | Specificity | Subject-macro AUPRC |
|---|---|---|---|---|---|
| B0 constant prior | 0.0460529 | 0.5000 | 1.0000 | 0.0000 | 0.042561 |
| B1 signal logreg | 0.1172989 | 0.7900 | 0.1320 | 0.9606 | 0.334247 |
| B2 morphology logreg | 0.1640117 | 0.8227 | 0.1575 | 0.9685 | 0.405035 |
| **B3 morphology HGB** | **0.1682901** | **0.8360** | 0.1639 | 0.9674 | **0.436410** |
| **B4-B neural** | **0.0935334** | **0.7332** | 0.0706 | 0.9526 | 0.354901 |

**The answer to the registered research question is no.** B4-B does not improve
subject-disjoint discrimination relative to the frozen classical baselines. It
is below B1, B2 and B3 on pooled AUPRC and on AUROC, and above only B0, the
constant prior.

**This was already visible on validation, and the sealed test agreed with it.**

| Model | Validation pooled AUPRC | Test pooled AUPRC | Retained |
|---|---|---|---|
| B1 signal logreg | 0.4211965 | 0.1172989 | 27.8% |
| B2 morphology logreg | 0.4771071 | 0.1640117 | 34.4% |
| B3 morphology HGB | 0.6800929 | 0.1682901 | 24.7% |
| B4-B neural | 0.3805350 | 0.0935334 | **24.6%** |

B3 led B4-B on validation (0.680 against 0.381) and leads it on test. **The
sealed test confirmed the development ordering rather than reversing it**, which
is the outcome a well-run firewall is supposed to produce. There was no
surprise, no anomaly, and no reason to doubt the measurement.

**This is a clean pre-registered negative finding**, of the same class as RQ3's
rejected router, and the programme already treats those as results.

## 2. Validation and test, side by side

Both columns are registered values. `VALIDATION_METRICS.json` carries
`evidence_class: development_validation_result`; `TEST_METRICS.json` carries
`evidence_class: sealed_one_shot_test_result`.

| | Validation | Test |
|---|---|---|
| Subjects · windows | 12 · 473,897 | 12 · 453,804 |
| Positives · negatives | 21,628 · 452,269 | 20,899 · 432,905 |
| **Prevalence** | **0.045639** | **0.046053** |
| Pooled AUPRC | 0.380535 | 0.093533 |
| Pooled AUROC | 0.892762 | 0.733237 |
| Pooled sensitivity | 0.410533 | 0.070578 |
| Pooled specificity | 0.967155 | 0.952572 |
| Pooled PPV | 0.374105 | 0.067024 |
| Pooled F1 | 0.391473 | 0.068755 |
| Pooled MCC | 0.361384 | 0.022588 |
| TP · FP · FN · TN | 8,879 · 14,855 · 12,749 · 437,414 | 1,475 · 20,532 · 19,424 · 412,373 |
| Subject-macro AUPRC | 0.400636 (9/12) | 0.354901 (8/12) |
| Subject-macro AUROC | 0.841039 (9/12) | 0.780837 (8/12) |
| Subject-macro sensitivity | 0.285845 (9/12) | 0.169043 (8/12) |
| **Subject-macro PPV** | **0.337366 (12/12)** | **0.332849 (12/12)** |
| Subject-macro specificity | 0.958234 (12/12) | 0.947705 (12/12) |

Threshold `0.8329097628593445` in both columns — validation-selected by maximum
validation F1, applied unchanged to test.

**Prevalence is matched to within 0.9%.** Whatever happened, it is not a
prevalence shift.

---

## 3. The diagnosis — corrected against the classical baselines

**An earlier revision of this section diagnosed a cross-subject score-scale
failure specific to B4-B. That diagnosis does not survive comparison with the
classical baselines, and is withdrawn.** What follows is what the evidence
supports.

### 3.1 The pooling penalty is a property of the partition, not of B4-B

Pooling penalty, `1 − pooled / subject-macro` on AUPRC. **Post-hoc
descriptive**, computed from published values.

| Model | Validation penalty | Test penalty |
|---|---|---|
| B1 signal logreg | −72.7% | **+64.9%** |
| B2 morphology logreg | −58.7% | **+59.5%** |
| B3 morphology HGB | −52.8% | **+61.4%** |
| B4-B neural | +5.0% | **+73.6%** |

**Every model reverses.** On validation the classical baselines score *higher*
pooled than subject-macro; on test all four sit far below it. A handcrafted-
feature logistic regression has no learned per-subject representation to
mis-scale, and it shows a 65-point swing.

**The dominant effect is the test partition** — twelve subjects, four of them
single-class, contributing only negatives to the pooled ranking while excluded
from macro discrimination. B4-B carries roughly ten points more penalty than the
classical models, which is real but is a second-order term.

### 3.2 Degradation is the same for the neural model and the best classical one

Validation → test pooled AUPRC retention: **B3 24.7%, B4-B 24.6%.** They are
indistinguishable. B4-B did not generalize worse than the classical baselines;
**it generalized the same amount from a lower starting point.**

That is the correction that matters. The earlier account said the encoder
"generalized its ordering and failed to generalize its scale". The scale
behaviour it described is shared by models with no learned scale at all, so it
cannot be a property of the encoder.

### 3.3 What is left that is genuinely about B4-B

Two things, both modest and both visible without the sealed test:

- **B4-B is weaker than B2 and B3 in absolute terms, on both partitions.**
  Validation pooled 0.3805 against B3's 0.6801; test pooled 0.0935 against
  0.1683. The raw-waveform representation did not match handcrafted ST
  morphology on this dataset at this scale.
- **Subject-macro discrimination fell more for B4-B than for B3** — 0.400636 →
  0.354901 (−11.4%) against B3's 0.445052 → 0.436410 (−2.0%). This is the one
  place a model-specific transfer weakness shows, and it is a 9-point gap, not
  the 75-point collapse the headline suggested.

### 3.4 What the fixed threshold did, which is still true

Subject-macro PPV moved **0.337366 → 0.332849**, a 1.3% change: when B4-B fires
on a test subject it is right about as often as on validation. Pooled
sensitivity fell **0.410533 → 0.070578** at a fixed cut, with specificity nearly
unchanged. The score distribution moved relative to a subject-absolute
threshold. **That observation stands** — it is simply not unique to B4-B, and it
does not explain the ranking against B0–B3, which is threshold-free.

## 4. The six hypotheses, assessed

| | Hypothesis | Verdict |
|---|---|---|
| A | Representation encoder weakness (B4-B) | **Supported, and the primary finding.** B4-B is below B1, B2 and B3 on pooled AUPRC and AUROC on the same partition, and was below B3 on validation too. The registered research question is answered **no** (§1.1) |
| B | Temporal modelling weakness (S4D) | **Not assessable.** Not in the scored path (§1). Separately, the T2 selection contrast **[−0.015229, 0.148951]** spans zero, so no temporal gain was ever established to have been lost |
| C | Personalization failure (M1/M2) | **Not assessable.** Not in the scored path (§1) |
| D | Calibration / threshold / score scale | **Real but not the explanation.** §3.4 holds, but the B0–B3 ranking is threshold-free and B4-B loses it anyway. **Downgraded from *primary* in an earlier revision** |
| E | Dataset / domain shift | **Weak, and partly falsified.** Prevalence matched to 0.9%; confounder strata *improved* (§5) |
| F | Insufficient cohort size | **Dominant for the validation→test drop, and shared by every model.** §3.1. The bootstrap interval **[0.033058, 0.239284]** is more than twice the width of its own point estimate |

**On A, D and F together.** F explains why *every* model lost ~75% of its
pooled AUPRC between the two partitions. D describes a threshold-transfer effect
that is real and shared. **A is what distinguishes B4-B**, and it is the answer
to the registered question: the neural representation did not beat the classical
one, on either partition.

**A descriptive note on F, not a hypothesis test.** The validation pooled AUPRC
point estimate, 0.380535, lies **above** the upper bound of the test bootstrap
interval, 0.239284. Resampling test subjects does not reach the validation
figure. §46 forbids significance language and none is claimed; this is stated as
a descriptive relationship between a point estimate and an interval, and it is
**not** a paired test between partitions, which does not exist and cannot now be
constructed.

---

## 5. The confounder controls held — report this as a finding

Registered challenge-stratum values at the frozen threshold. Share-of-total-FP
is **post-hoc descriptive**.

| Stratum | Validation FP fraction | Test FP fraction | Share of all FPs, validation → test |
|---|---|---|---|
| Rate-related | 0.331188 (1,647/4,973, 4 subj) | 0.229282 (1,162/5,068, 4 subj) | 11.09% → 5.66% |
| Axis-shift | 0.061667 (185/3,000, 8 subj) | 0.038914 (119/3,058, 8 subj) | 1.25% → 0.58% |

Meanwhile the overall false-positive rate **rose 44%** (1 − specificity:
0.032845 → 0.047428, post-hoc descriptive).

**More false positives overall, proportionally fewer of them in the strata the
architecture was selected to resist.** The confounder robustness B4-B was chosen
for — it beat B4-A at 0.345667 and B4-C at 0.465112 on validation rate-related
FP fraction — transferred to held-out subjects. **The new false positives are
diffuse and currently uncharacterised.**

Conduction-change evidence is **exploratory and descriptive**: 8 of 10 windows,
one subject. It is not bootstrapped, is not a headline, and is quoted here only
to state that it was not used.

---

## 6. Why U1 as retained could not have addressed this

`U1_DEPLOYMENT_CALIBRATOR.json` records **one** deployment calibrator —
`selected_family: platt_logistic_on_recovered_logit`, `calibrated_boundary:
0.20631829355583678`. Its digest `acec97c1…` matches
`final_deployment_calibrator_sha256` in `U1_EXPERIMENT_LOCK.json`. The
`calibrator_count: 12` in `U1_OOF_CALIBRATION.json` is **twelve out-of-fold
calibrators for honest OOF evaluation**, not twelve per-subject deployment
calibrators.

**A single global Platt is a monotone transform of the score, and a monotone
transform is rank-preserving.** Applied to the sealed-test scores it would have
returned pooled AUPRC `0.0935334` and AUROC `0.7332374` **exactly** — those
metrics depend only on ordering. It would have moved the threshold-dependent
metrics, because the decision boundary would be 0.206318 on calibrated
probability rather than 0.832910 on raw sigmoid.

**So U1 is not a missed fix for the headline.** The diagnosed defect is a
*cross-subject rank* problem, and only a calibrator that applies a **different**
transform per subject changes cross-subject ranks. No such calibrator exists in
this programme.

This is worth stating plainly because the opposite inference is the natural one
and it is wrong: *"we built a calibrator and forgot to use it"* would be a
tidier story than *"the calibrator we built is the wrong kind for the failure we
found"*, and the second is what the artifacts say.

The runtime does apply the global calibrator — `DEMO_SCENARIO.md` §4 records
`calibrator: platt_logistic_on_recovered_logit` with a peak calibrated
probability of 0.545613 — so the deployed path and the evaluated path differ in
that respect. Neither carries a per-subject transform.

---

## 7. Boundary

| Boundary | Result |
|---|---|
| Test predictions read | **None.** `TEST_PREDICTIONS.npz` was not opened |
| Classical test results read | **Yes, and permitted.** `RESULTS_SUMMARY.json` under `phase3b-classical-v3/`. That chain was consumed in Phase 3B-1 and `B4_PROTOCOL_V1` records that its results are *"historically observed"*; comparing to them is the registered research question, not a new access |
| New test metrics generated | **None.** Only registered values from `TEST_METRICS.json` are quoted; all ratios are labelled post-hoc descriptive |
| New experiments executed | **None.** No run was started; none is authorized |
| Threshold changes | **None.** `0.8329097628593445` remains frozen, `test_informed: false` |
| Model retraining | **None.** No checkpoint was read or written |
| Artifact modification | **None.** All four digests re-verify (§7.1) |
| §9 revision | **None.** §9 was merged 2026-08-24; the test ran 2026-08-25 |
| Second attempt | **Impossible.** `repeat_attempt_permitted: false` |

### 7.1 Artifact digests at the time of writing

| Artifact | SHA-256 | Unchanged |
|---|---|---|
| `TEST_ATTEMPT.json` | `7db48a2750729dc2cc53eafd731e1e7e4e5e52d65b30b7a1bc1547523b7882a2` | ✅ |
| `TEST_METRICS.json` | `b117da896d94dd11cfb05e156211a79dee6db6ee18b25783b2bbe0e4440ef8b0` | ✅ |
| `TEST_PREDICTIONS.npz` | `8233d3cb70fdea976c26e9a33e1bc60caaa1fe60025f0c81b737d15f3cd53592` | ✅ |
| `TEST_AUDIT.json` | `2f6af19c47d04bfe745cd6d6d367d46555841bb4afcfccd961df0e1faa61a4bf` | ✅ |

All four retain their 2026-08-25 00:43 modification times from the run itself.
Nothing has written to that directory.

**Note on the two digests named `test_audit_sha256`.** The value above is the
SHA-256 of the `TEST_AUDIT.json` **file bytes**, which is what `TEST_ATTEMPT.json`
records under that name. `TEST_AUDIT.json`'s own field of the same name is
`79447d4da551d88f3c97389953c98e8edd3be2a682930cbcdde25525d7efb905`, which is
**self-referential** — the SHA-256 of the audit payload with that field removed,
`sort_keys=True`, `separators=(",", ":")`, the same rule the experiment locks
use. Both were recomputed and both match. **They are different numbers and both
are correct about themselves; say which one you mean.**

### 7.2 Development artifacts cited

| Artifact | SHA-256 |
|---|---|
| `VALIDATION_METRICS.json` | `87852fa5c3dcb0d05d2fe3124a384e408846f6b3fb8522a9cccd203ba5f26d06` |
| `EXPERIMENT_LOCK.json` (B4-B) | `5bf251780f469115164d61a3f3cef2eecfc9ef9765af3f544479e961da00e7bc` |
| `docs/experiments/b4/B4_GLOBAL_ENCODER_SELECTION_V1.json` | `b40796848e8a28d5fc489101fe6ed2d04eb760ee1a354ff8dc9f182eb60df638` |
| `VALIDATION_CHALLENGE_RESULTS.json` | `8127f5a4a2a501f92fb47d100c561e15b4129670ef1d25acc236a1c0580ec672` |
| `U1_DEPLOYMENT_CALIBRATOR.json` | `acec97c1ebd3bed459ad2d75204b6c82f274b248edbb1d779b844bd46c62fdc1` |

---

## 8. What follows from this

Nothing in this document authorizes an experiment. The forward plan is
`docs/control-plane/IMPROVEMENT_ROADMAP_V1.md`, which grants no permission either.

The one-line summary, for anyone who reads no further: **the B4 neural baseline
did not beat the classical baselines it was pre-registered against, on either
partition, and the sealed test confirmed the ordering development had already
shown.**

### 8.1 Revision note

An earlier revision of this document, merged in #118, made two claims that do
not survive the comparison in §1.1 and are withdrawn here:

| Withdrawn | Replaced by |
|---|---|
| The encoder-only scope was a **discovery** and a reporting-layer near-miss | It was **pre-registered** in `B4_PROTOCOL_V1` §Scope, and the mismatch was in a later description, not in the experiment (§1) |
| B4-B suffered a **cross-subject score-scale generalization failure** | Every model reverses the same way; B4-B and B3 retain 24.6% and 24.7% of validation pooled AUPRC. The effect is the partition's, not the encoder's (§3.1, §3.2) |

**Both were written from B4-B's numbers alone.** The classical baselines were
scored on the identical partition, are already consumed, and were sitting in
`cardiosentinel-runs/phase3b-classical-v3/` the whole time. **A comparison
against a comparator that already exists is not optional**, and the failure to
make it is the more useful methodological lesson of the two.
