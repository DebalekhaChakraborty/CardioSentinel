# U1 Calibration Reliability — Descriptive Report, V1

**Step 3 of `docs/U1_CALIBRATION_RELIABILITY_ANALYSIS_PLAN_V1.md`: the
first read of the per-bin reliability evidence.** The reporting shape was
fixed in §3 and §4 of that plan before any bin was visible, and nothing in
the plan was changed after the values became readable.

Every number is read verbatim from a promoted artifact, with the single
exception plan §3.1 names and authorizes in advance: the signed gap
`empirical − mean`, arithmetic on two published numbers. No `.npz` store
was opened and no metric was recomputed.

**This report changes nothing.** The U1 retention decision is frozen and
was taken on evidence that already included these bins' summary. Reading
the bins adds description, not support. The retention remains **split**:
Platt calibration retained, the selective router at `c_star = 0.90` **not**
retained.

---

## 1. Provenance

| | |
|---|---|
| Run | `cardiosentinel-runs/phase7-u1-development-v1/u1-v1-development` |
| Selected family | `platt_logistic_on_recovered_logit` |
| Selection criterion | `pooled_out_of_fold_negative_log_likelihood` |
| Out-of-fold | `true` |
| Development evidence | `true` |
| Development optimistic | `true` |
| `test_accessed` | `false` |
| `sealed_test_state` | `unopened` |
| Generated at commit | `de4ccf7d1325374923b9d44f45d394bbc24afb8d` |

- `U1_OOF_CALIBRATION.json` — SHA-256 `c6a48fcd5e14cbe9d543eaa1d81328a8eade41343cc9629c8f3f8b78eee47da2`
- `U1_FAMILY_SELECTION.json` — SHA-256 `cbf8dec21defa18143050cd74b5c08916a17f07279578541e234fac3cdce70d1`
- `U1_OOF_RESULT.json` — SHA-256 `dbe546ecb4da1b6a974ace6549803ac9a6894db321707da25cff39d9bca0e7e6`
- `U1_EXPERIMENT_LOCK.json` — SHA-256 `eca664ced24cdbc3f28b1ef339c99f0e37ec7185a034a7c7ed28b7f773d1ebfc`

> tau was itself selected on VALIDATION; cross-fitting removes subject self-calibration only and does not make VALIDATION an independent holdout

---

## 2. Family-level scalars — all three families

Restated from the retention decision as context for the bins, not as a
new finding. The uncalibrated baseline is the raw score treated as a
probability; it is what the question "did calibration help?" is asked
against, subject to the qualification recorded immediately below.

| Family | NLL | Brier | ECE equal-width | ECE equal-mass | Rows | `clamp_delta` | `out_of_fold` |
|---|---:|---:|---:|---:|---:|---:|---|
| `platt_logistic_on_recovered_logit` | 0.143708 | 0.040344 | 0.016991 | 0.018604 | 473,897 | 1e-07 | `true` |
| `temperature_only_on_recovered_logit` | 0.191692 | 0.058647 | 0.074040 | 0.074040 | 473,897 | 1e-07 | `true` |
| `uncalibrated_baseline` | 0.231705 | 0.063567 | 0.063844 | 0.062464 | 473,897 | 1e-07 | `false` |

**The baseline row is not a matched comparison, and the retention
decision already said so.** `U1_OOF_CALIBRATION.json` carries the
qualification in the artifact itself:

> `uncalibrated_baseline.baseline_semantics` — the raw persisted M2-G score treated as a probability; it is a reference, not an out-of-fold artifact

Its `out_of_fold` and `development_evidence` are both `false`, against `true` for the retained family. Every comparison below inherits that asymmetry.

The temperature-only row is **approximate**: `comparator_is_approximate` is `true` and `true_logit_temperature_scaling_performed` is `false`,
because true logits were never persisted. Its two ECEs are identical for
the reason the retention decision recorded: it over-predicts in every bin
of both binnings, so both collapse to the same global mean gap.

### 2.1 Protocol §16 condition 2 — restated, not re-decided

Plan §3.2 requires the prespecified condition to appear beside the bins as
context. U1 protocol §16 condition 2 is that **pooled OOF Brier and NLL
are both lower than the uncalibrated baseline**.

| Scalar | Retained Platt | Uncalibrated baseline | Condition 2 |
|---|---:|---:|---|
| NLL | 0.143708 | 0.231705 | lower |
| Brier | 0.040344 | 0.063567 | lower |

Both scalars are already published in
`U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` §3, and the human
retention decision recorded in its §2 was taken with them in hand:
**calibration retained, the selective router at `c_star = 0.90` not
retained.** This table restates that record. It does not re-decide it, and
the baseline asymmetry noted above applies to both rows.

**Improved ECE alone is not a success criterion.** The U1 protocol §16 says
so, and the family selection used NLL, not ECE: `ece_used` is
`false` and `brier_used` is
`false` in the frozen decision.

---

## 3. Per-bin reliability — the retained calibrator

`platt_logistic_on_recovered_logit`. Fifteen bins per binning, constructed exactly as U1 protocol
§10.3 froze in advance. Gap is `empirical − mean`; **positive means the
observed positive rate exceeded the predicted probability**, i.e. the
calibrator was under-confident in that bin.

### 3.1 Equal-width

| Bin | Rows | Mean probability | Empirical positive fraction | Gap |
|---|---:|---:|---:|---:|
| 0 | 398,513 | 0.012886 | 0.016524 | 0.003638 |
| 1 | 29,840 | 0.094577 | 0.149497 | 0.054920 |
| 2 | 15,088 | 0.163927 | 0.220573 | 0.056645 |
| 3 | 9,737 | 0.230801 | 0.214029 | -0.016772 |
| 4 | 6,378 | 0.297707 | 0.203512 | -0.094195 |
| 5 | 4,298 | 0.364191 | 0.196138 | -0.168053 |
| 6 | 2,982 | 0.432152 | 0.229376 | -0.202776 |
| 7 | 2,075 | 0.497746 | 0.248193 | -0.249553 |
| 8 | 1,497 | 0.564645 | 0.313961 | -0.250683 |
| 9 | 1,290 | 0.633209 | 0.364341 | -0.268868 |
| 10 | 990 | 0.698371 | 0.365657 | -0.332714 |
| 11 | 587 | 0.763888 | 0.403748 | -0.360140 |
| 12 | 478 | 0.832594 | 0.575314 | -0.257280 |
| 13 | 128 | 0.895848 | 0.125000 | -0.770848 |
| 14 | 16 | 0.941428 | 0.000000 | -0.941428 |

Gap is positive in bin(s) **0-2** — observed positive rate above predicted probability — and negative in bin(s) **3-14**. The widest gap is -0.941428 at bin 14, which carries 16 rows. Bin counts run from 16 to 398,513 across the family's 473,897 rows, the heaviest being bin 0.

### 3.2 Equal-mass

| Bin | Rows | Mean probability | Empirical positive fraction | Gap |
|---|---:|---:|---:|---:|
| 0 | 31,594 | 0.000903 | 0.000158 | -0.000744 |
| 1 | 31,594 | 0.001637 | 0.000411 | -0.001225 |
| 2 | 31,593 | 0.002476 | 0.000506 | -0.001970 |
| 3 | 31,593 | 0.003487 | 0.001804 | -0.001682 |
| 4 | 31,593 | 0.004656 | 0.002596 | -0.002060 |
| 5 | 31,593 | 0.006027 | 0.004020 | -0.002007 |
| 6 | 31,593 | 0.007699 | 0.006077 | -0.001622 |
| 7 | 31,593 | 0.009845 | 0.008515 | -0.001331 |
| 8 | 31,593 | 0.012795 | 0.012883 | 0.000088 |
| 9 | 31,593 | 0.017197 | 0.019308 | 0.002111 |
| 10 | 31,593 | 0.024334 | 0.033425 | 0.009091 |
| 11 | 31,593 | 0.037147 | 0.060393 | 0.023246 |
| 12 | 31,593 | 0.063658 | 0.106099 | 0.042442 |
| 13 | 31,593 | 0.131214 | 0.191150 | 0.059936 |
| 14 | 31,593 | 0.366736 | 0.237236 | -0.129500 |

Gap is positive in bin(s) **8-13** — observed positive rate above predicted probability — and negative in bin(s) **0-7, 14**. The widest gap is -0.129500 at bin 14, which carries 31,593 rows. Bin counts run from 31,593 to 31,594 across the family's 473,897 rows, the heaviest being bin 0.

---

## 4. Per-bin reliability — the uncalibrated baseline

Plan §4 rule 3: a calibration number without its baseline is not
interpretable, so the baseline is reported at the same resolution.

### 4.1 Equal-width

| Bin | Rows | Mean probability | Empirical positive fraction | Gap |
|---|---:|---:|---:|---:|
| 0 | 391,812 | 0.003913 | 0.011855 | 0.007942 |
| 1 | 13,225 | 0.095773 | 0.092628 | -0.003145 |
| 2 | 7,469 | 0.164350 | 0.105235 | -0.059115 |
| 3 | 5,494 | 0.231312 | 0.110666 | -0.120646 |
| 4 | 4,336 | 0.298884 | 0.133072 | -0.165812 |
| 5 | 3,688 | 0.366363 | 0.136117 | -0.230246 |
| 6 | 3,653 | 0.433416 | 0.154394 | -0.279022 |
| 7 | 3,188 | 0.500302 | 0.165307 | -0.334994 |
| 8 | 3,336 | 0.566594 | 0.167266 | -0.399328 |
| 9 | 3,412 | 0.633481 | 0.176143 | -0.457337 |
| 10 | 3,676 | 0.699792 | 0.178183 | -0.521609 |
| 11 | 4,031 | 0.767362 | 0.209625 | -0.557736 |
| 12 | 4,781 | 0.834898 | 0.229868 | -0.605030 |
| 13 | 6,326 | 0.902231 | 0.271578 | -0.630653 |
| 14 | 15,470 | 0.977391 | 0.434260 | -0.543131 |

Gap is positive in bin(s) **0** — observed positive rate above predicted probability — and negative in bin(s) **1-14**. The widest gap is -0.630653 at bin 13, which carries 6,326 rows. Bin counts run from 3,188 to 391,812 across the family's 473,897 rows, the heaviest being bin 0.

### 4.2 Equal-mass

| Bin | Rows | Mean probability | Empirical positive fraction | Gap |
|---|---:|---:|---:|---:|
| 0 | 31,594 | 0.000001 | 0.000032 | 0.000031 |
| 1 | 31,594 | 0.000004 | 0.000253 | 0.000250 |
| 2 | 31,593 | 0.000010 | 0.000443 | 0.000434 |
| 3 | 31,593 | 0.000022 | 0.001076 | 0.001054 |
| 4 | 31,593 | 0.000049 | 0.001361 | 0.001312 |
| 5 | 31,593 | 0.000101 | 0.002152 | 0.002051 |
| 6 | 31,593 | 0.000205 | 0.003767 | 0.003561 |
| 7 | 31,593 | 0.000419 | 0.006900 | 0.006481 |
| 8 | 31,593 | 0.000887 | 0.009211 | 0.008323 |
| 9 | 31,593 | 0.002068 | 0.015985 | 0.013917 |
| 10 | 31,593 | 0.005629 | 0.026778 | 0.021149 |
| 11 | 31,593 | 0.019291 | 0.048872 | 0.029580 |
| 12 | 31,593 | 0.087966 | 0.087773 | -0.000193 |
| 13 | 31,593 | 0.422528 | 0.146108 | -0.276419 |
| 14 | 31,593 | 0.906085 | 0.333871 | -0.572214 |

Gap is positive in bin(s) **0-11** — observed positive rate above predicted probability — and negative in bin(s) **12-14**. The widest gap is -0.572214 at bin 14, which carries 31,593 rows. Bin counts run from 31,593 to 31,594 across the family's 473,897 rows, the heaviest being bin 0.

---

## 5. Bin degeneracy — plan §3.3

An ECE whose weight sits in two bins says something different from one
spread across fifteen. Bins below
30 rows are counted as sparse: their empirical positive
fraction is reported, and it should not be read as an estimate.

| Family | Binning | Bins | Empty | Sparse | Smallest | Largest |
|---|---|---:|---:|---:|---:|---:|
| `platt_logistic_on_recovered_logit` | equal-width | 15 | 0 | 1 | 16 | 398,513 |
| `platt_logistic_on_recovered_logit` | equal-mass | 15 | 0 | 0 | 31,593 | 31,594 |
| `temperature_only_on_recovered_logit` | equal-width | 15 | 0 | 0 | 5,118 | 332,714 |
| `temperature_only_on_recovered_logit` | equal-mass | 15 | 0 | 0 | 31,593 | 31,594 |
| `uncalibrated_baseline` | equal-width | 15 | 0 | 0 | 3,188 | 391,812 |
| `uncalibrated_baseline` | equal-mass | 15 | 0 | 0 | 31,593 | 31,594 |

This is the U1 analogue of the T1 lesson that **defined is not meaningful**.

---

## 6. A limitation of the shape this plan fixed

Plan §5 step 4: if the shape fixed in advance turns out to be wrong, that
is recorded here as a limitation, not repaired by editing the plan. The
plan is not modified.

Plan §3.3 chose four degeneracy statistics — empty bins, bins under 30 rows, smallest and largest — to surface the fact that equal-width binning on a low-prevalence detector score concentrates mass at one end. On the retained calibrator's equal-width binning those statistics read 0 empty and 1 sparse, which on its own reads as a healthy curve. The concentration is visible only in the smallest and largest columns: 16 rows against 398,513.

**A count of sparse bins is the wrong summary for this evidence.** The
share of mass in the heaviest bin would have been the right one, and the
plan did not name it. It is not added here: choosing a statistic after
seeing the values is the error the plan exists to prevent, and the two
numbers a reader needs are both already in the table above. This is
recorded so a future plan names the share in advance.

---

## 7. What this report does not support

- **Nothing about TEST.** `test_accessed` is false and the B4/neural sealed
  test is unopened.
- **No generalisation claim.** Development, out-of-fold, one cohort, and the
  artifact records its own optimism. Subject-disjoint folds control for
  subject leakage within LTSTDB and say nothing about another cohort.
- **No clinical safety claim.** U1 protocol §16 forbids it explicitly.
- **No routing claim.** The selective router is not retained. Reliability of
  a probability and the behaviour of a policy built on it are different
  questions.
- **No support for the retention decision.** It was already taken on
  evidence including these bins' summary.
- **No T2 calibration language.** T2 scores carry
  `score_is_calibrated_probability: false`; a bounded sigmoid is not a
  probability, and nothing in this report may be attached to one.

## 8. Excluded analyses — plan §3.5

Not done, and not to be done as a follow-up without a separate decision:

- Re-deriving any metric from the `.npz` evidence stores
- Any re-binning, alternative bin count or third binning scheme
- Any recalibration, refit, temperature search or clamp-delta variation
- Any routing, coverage or `c_star` analysis
- Any per-subject reliability decomposition
- Any comparison to B0–B3, B4 or T2 scores
