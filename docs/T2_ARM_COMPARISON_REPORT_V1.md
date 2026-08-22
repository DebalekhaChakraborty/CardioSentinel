# T2 Arm Comparison — Report, V1

**Step 3 of `docs/T2_ARM_COMPARISON_ANALYSIS_PLAN_V1.md`: the first read of T2 outer-validation measured
values.** Produced under explicit human authorization, to the reporting
shape fixed in §2–§5 of that plan before any value was visible.

**The plan itself is unedited** and still digests
`84adf43b885d6dd3ecef3b678d1a2b89fc6e94f48ffdf8d2f0dc2bb0a7eba973`. Its estimands, its derived analysis and its claim
boundaries are exactly as approved before the first read.

**An amendment postdates that read.** `docs/T2_ARM_COMPARISON_ANALYSIS_PLAN_AMENDMENT_V1_1.md`
(`859b07c15d160cd5610a52f1b101f4b63fe45efffb32c3938f98cef30fbf52fb`) was written on 2026-08-22,
**after** the values were visible, and is stated here rather than left to
be inferred. It repairs an unreconciled conflict between plan §5.3, which
required cold-start strata verbatim, and plan §3, which constrained
absolute figures — a conflict the first execution resolved silently by
dropping values. **The amendment only ever adds reporting.** It changes no
estimand, authorizes no new computation, and revises no number: the
primary contrast and the derived interval below are identical to those
produced before it existed.

**Every number below is read verbatim from a promoted artifact, with one
exception** named and authorized in advance by plan §4 and labelled
**DERIVED ANALYSIS** wherever it appears: the paired subject-level
bootstrap of the S4D − GRU pooled primary AUPRC difference, which no
artifact stores.

---

## 1. Evidence and firewall

| | |
|---|---|
| Run | `t2-v1-outer-validation` |
| Authorized git SHA of the run | `b0f189a57bea8bd28884e7e40be50136fd6e2927` |
| Analysis executed at commit | `4faaf131315f3a612b7c9baf976229ee7c0e62de` |
| Partition | `validation` |
| Attempts permitted | 1 |
| Automatic retry performed | `false` |
| `git_dirty` at run time | `false` |
| `test_accessed` | `false` |
| `sealed_test_state` | `unopened` |
| `test_rows_present` in the row store | `false` |

Artifact digests, verified before any value was read:

- `T2_OUTER_VALIDATION_RESULT.json` — `c58ed40dac753157b00ce6c70eb52fe903ecee72a5ef84e40932c1a80e259dbf`
- `T2_OUTER_ROW_EVIDENCE.json` — `c76453b8970a06c6beb3c280ab6e0518fa4cf81fcb304f6f9aa9c569d2634949`
- `t2_outer_row_identity.npz` — `1014357cd25d347c7a760e38dbf7ae93c71d56717d13a40e315bb9cb79b220dc`
- `t2_outer_scores_s4d.npz` — `5c7f9763713c66759cf7e3752cda2a71dacb6cc3f962c5bdd5247017447a7a32`
- `t2_outer_scores_gru.npz` — `2dbfa5da02f0d96065d72f272875f805f5dceb28410b90582df34c8f6fc17f2d`

### 1.1 Pairing — plan §0.1

| | |
|---|---|
| Rows in the shared identity store | 492,904 |
| Primary-mask rows | 473,897 |
| Primary rows scored and available | 473,897 |
| Primary rows unavailable, no score | 0 |
| Score invented for an unavailable row | `false` |
| `full_timeline_ordering` | `stream_then_start_sample` |
| `ordered_stable_id_sha256` | `a5453f4c2e29a1fdb9f117d5e4ccbed75cf8c908ca164cef9d8266a2337d92ba` |
| `ordered_chronology_sha256` | `89f0b08bcd518fe0017c50bac0e198a1d9b61bc69fc1e3c6e06c148bbcb6960f` |
| `lossy_conversion_applied` | `false` |

One identity array and **one label vector** serve both arms, so the
comparison is paired by construction rather than by reconstruction here.
This report additionally verified that each arm's `score_present` agrees
with the identity store's over the primary mask; it does.

Per-arm single-pass flags:

| Arm | `single_causal_pass` | 2nd temporal replay | 2nd challenge replay | threshold altered by outer validation |
|---|---|---|---|---|
| `causal_s4d_longitudinal_v1` | `true` | `false` | `false` | `false` |
| `causal_gru_longitudinal_v1` | `true` | `false` | `false` | `false` |

---

## 2. Primary result — the predefined selection criterion

**This difference is the criterion by which the arm was chosen.** It is not
an independent discovery, and plan §2 requires that sentence to appear in
the same passage as the number.

| | |
|---|---|
| `selection_basis` | `pooled_primary_validation_auprc` |
| `selected_arm` | `causal_s4d_longitudinal_v1` |
| **`pooled_auprc_difference`** | **0.093215** |
| `tie_tolerance` | 0.002000 |
| `challenge_evidence_used` | `false` |
| `latency_used` | `false` |
| `weighted_composite_used` | `false` |

Read verbatim from `selection_decision.pooled_auprc_difference`.

**Sign convention.** The artifact stores an unsigned magnitude:
`t2_protocol.select_t2_arm` computes `abs(gru − s4d)` and carries the
direction separately in `selected_arm`. The direction is therefore read
from `selected_arm`, not inferred from the number.

The predefined selection rule selected
`causal_s4d_longitudinal_v1` based on the observed validation contrast,
by a margin of 0.093215 on pooled primary
validation AUPRC, against a tie tolerance of 0.002000.

### 2.1 Selection conditioning — plan §3

| | |
|---|---|
| **The paired contrast is unbiased** | Both arms were evaluated on the same held-out rows under a rule fixed in advance. Selecting on the outcome does not bias the *difference*. |
| **The winner's absolute figure is not** | The selected arm's own AUPRC on this set is optimistically biased, because it was chosen for having the higher value **on this very set**. The bias attaches to the maximum, not to the contrast. |

### 2.2 Arm-level absolute AUPRC — descriptive (amendment §3)

> Absolute arm-level values are descriptive because the selected arm was chosen using the same criterion. They are reported to give the primary contrast a scale, not as unbiased estimates of either arm's performance.

| Arm | pooled primary AUPRC | subject-macro AUPRC | contributing subjects | non-contributing |
|---|---:|---:|---:|---:|
| `causal_s4d_longitudinal_v1` | 0.388085 | 0.428152 | 9 | 3 |
| `causal_gru_longitudinal_v1` | 0.294870 | 0.409737 | 9 | 3 |

**The subject-macro figure is a mean over 9 of 12
subjects, not 12.** The artifact records 3
non-contributing subjects for both arms, and it is the artifact's own
count, not a derivation. A subject-macro mean quoted without that
denominator reads as an average over the cohort when it is an average
over the subset of it for which the metric is defined.

This is the same distinction the T1 analysis had to make after the
fact — `episode_f1` was *defined* for 12/12 subjects while three of
them had zero reference episodes. **Defined is not meaningful.** It is
stated here because the amendment surfaced the value; the
pre-amendment report, which omitted the absolute, also omitted this.

No claim is made about **which** subjects those are, or why. That
would be a subgroup analysis and plan §5.3 forbids one.

These give §2's contrast a scale. Reporting them does not license any
sentence plan §3 forbids: *"S4D achieved superior AUPRC"* and *"S4D was
found to outperform GRU"* remain prohibited, and the selected arm's
absolute figure remains optimistically biased for the reason in §2.1.

The remaining pooled and subject-macro metrics (`auroc`,
`balanced_accuracy`, `f1`, `mcc`, `npv`, `ppv`, `sensitivity`,
`specificity`) exist in the artifact and are **not** reported: no
registered estimand is computed from them, and adding them after the
values are visible would be the scope creep the amendment objects to.
That boundary is a decision, not an accident.

---

## 3. DERIVED ANALYSIS — paired subject-level bootstrap

**No artifact stores this quantity.** The artifacts carry a
`subject_bootstrap` per arm and no interval on the difference, so the §2
contrast had a point estimate and no uncertainty. Plan §4 authorizes
exactly this one computation (T2_ARM_COMPARISON_ANALYSIS_PLAN_V1 §4).

Registered design, verified against the artifact's own
`subject_bootstrap` block for **both** arms before running:

| Parameter | Value |
|---|---|
| Resampling unit | `subject` (12 subjects) |
| Rows | same resampled rows both arms — 473,897 primary rows |
| Statistic | `pooled_primary_auprc_s4d_minus_pooled_primary_auprc_gru` |
| Model refitting | `false` |
| Threshold changes | `false` |
| Reselection | `false` |
| Window bootstrap | `false` |
| Seed | 2,026 |
| Requested replicates | 1,000 |

**Result:**

| | |
|---|---|
| Point estimate, signed S4D − GRU | **0.093215** |
| **95% paired subject-bootstrap interval** | **[-0.015229, 0.148951]** |
| Successful replicates | 1,000 |
| Undefined replicates | 0 |
| Undefined replicates zero-filled | `false` |

Undefined replicates are preserved and reported as undefined, never
zero-filled, per plan §4.

### 3.1 Agreement with the recorded selection margin

| | |
|---|---|
| Stored magnitude, `pooled_auprc_difference` | 0.093215 |
| Derived signed difference | 0.093215 |
| Absolute agreement error | 0.000000000000 |
| Agrees within 1e-9 | `true` |

The derived point estimate recomputes the same statistic the selection
recorded, from the persisted row stores. Agreement is evidence that the
bootstrap was handed the rows the selection actually saw. Disagreement
would have stopped the analysis rather than produced a second number.

### 3.2 Where the interval sits relative to zero

Stated because omitting it would leave the reader to notice it, and this
is the fact the derived analysis was authorized to establish.

**The 95% paired subject-bootstrap interval [-0.015229, 0.148951]
includes zero.** The point estimate is the recorded selection margin, and
the predefined rule selected on it correctly — the margin
(0.093215) exceeds the tie tolerance
(0.002000) by more than an order of magnitude.
What the interval adds is that **between-subject variation in this
contrast spans zero**: resampling the 12 validation subjects produces
replicates in which the ordering of the two arms reverses.

**This is not a significance statement and must not be converted into
one.** Plan §4 forbids p-values and significance language, and the
interval is not a confidence interval for a population parameter. It
says the contrast is not stable across subjects at this resampling
resolution. It does not say the two arms are equivalent, and it does not
retract the selection — the rule was fixed in advance and applied to the
value it was defined on.

The 12-member resampling unit is the binding constraint on how much this
can say either way; see the resolution caveat below.

### 3.3 Claim scope — plan §4

`between_subject_variation_in_the_paired_arm_difference_conditional_on_two_fitted_temporal_models_and_frozen_thresholds`

The interval describes **between-subject variation in the paired contrast,
conditional on the fitted temporal models**. It is not a confidence
interval for a population parameter and it is not a hypothesis test. **No
p-value and no significance language appears anywhere in this analysis.**

**Resolution caveat, registered before execution.** The resampling unit has
12 members, so the percentile interval is coarse by construction and its
tails are governed by a handful of subjects. It indicates between-subject
spread, not precision.

---

## 4. Secondary — subject-macro AUPRC difference (plan §5.1)

Reported **separately** from the primary contrast and never merged into it.

| | |
|---|---|
| `subject_macro_auprc_difference` | 0.018415 |

Subject-weighted rather than row-weighted, so it is a **different estimand**
from §2 and need not agree with it. It was **not** the selection basis
(`selection_basis: pooled_primary_validation_auprc`), but it is computed on the
same evidence the selection consumed, so it is a companion to the primary
contrast rather than independent corroboration. Stored as an unsigned
magnitude on the same convention as §2.

---

## 5. Secondary — selection-independent temporal descriptors (plan §5.2)

**These are the only comparisons in this report free of selection
conditioning.** The artifacts state it directly for both arms.

| Descriptor | S4D | GRU |
|---|---:|---:|
| `prediction_persistence_around_labelled_ischemic_intervals` | 0.287960 | 0.238533 |
| `transition_count` | 3,571 | 2,161 |
| `transition_count_per_hour` | 5.216269 | 3.156639 |
| `median_positive_run_duration_seconds` | 10.000000 | 25.000000 |
| `positive_prediction_run_count` | 1,787 | 1,081 |
| `isolated_single_window_positive_fraction` | 0.496363 | 0.159112 |

Context carried with the numbers:

| | S4D | GRU |
|---|---|---|
| `stream_count` | 30 | 30 |
| `physical_exposure_seconds` | 2464520.000000 | 2464520.000000 |
| `labelled_positive_window_count` | 21,628 | 21,628 |

The artifact's own qualifiers, which travel with these descriptors:

| Qualifier | S4D | GRU |
|---|---|---|
| `episode_grouping_performed` | `false` | `false` |
| `prediction_persistence_is_episode_onset_offset_measurement` | `false` | `false` |
| `runs_cross_stream_boundaries` | `false` | `false` |
| `run_segmentation_key` | record_id_channel_index | record_id_channel_index |
| `is_selection_input` | `false` | `false` |
| `may_alter_threshold` | `false` | `false` |
| `formal_episode_reasoning_belongs_to` | t1 | t1 |
| `transition_denominator` | full_physical_timeline_exposure | full_physical_timeline_exposure |
| `prediction_persistence_unit` | window | window |

`prediction_persistence_definition`:

> fraction_of_labelled_positive_windows_predicted_positive

**These must remain separate from the selection criterion.** They are
descriptive comparisons of temporal behaviour, they were not inputs to the
choice of arm, and they are not aggregated into, or presented as support
for, the §2 contrast. `episode_grouping_performed` is false for both arms:
**no episode reasoning happens here.**

---

## 6. Secondary — challenge and cold-start evidence (plan §5.3)

Descriptive. No subgroup claim is made from either, and no stratum or
subset is compared across arms as a finding.

**`causal_s4d_longitudinal_v1` — challenge**

| | |
|---|---|
| `is_selection_input` | `false` |
| `arm_selection_input` | `false` |
| `checkpoint_selection_input` | `false` |
| `merged_into_primary` | `false` |
| `challenge_label_model_input` | `false` |
| `challenge_identity_model_input` | `false` |
| `direct_training_loss_received` | `false` |

| Subset | Rows | False positives | False-positive rate | Evidence level |
|---|---:|---:|---:|---|
| `axis_shift` | 3,000 | 55 | 0.018333 | `quantitative_secondary` |
| `conduction_change` | 164 | 0 | 0.000000 | `exploratory_descriptive` |
| `rate_related` | 4,973 | 1,022 | 0.205510 | `quantitative_secondary` |

**`causal_gru_longitudinal_v1` — challenge**

| | |
|---|---|
| `is_selection_input` | `false` |
| `arm_selection_input` | `false` |
| `checkpoint_selection_input` | `false` |
| `merged_into_primary` | `false` |
| `challenge_label_model_input` | `false` |
| `challenge_identity_model_input` | `false` |
| `direct_training_loss_received` | `false` |

| Subset | Rows | False positives | False-positive rate | Evidence level |
|---|---:|---:|---:|---|
| `axis_shift` | 3,000 | 87 | 0.029000 | `quantitative_secondary` |
| `conduction_change` | 164 | 0 | 0.000000 | `exploratory_descriptive` |
| `rate_related` | 4,973 | 944 | 0.189825 | `quantitative_secondary` |

**`causal_s4d_longitudinal_v1` — cold start**

| | |
|---|---|
| `cold_start_repair_applied` | `false` |
| `warmup_threshold_applied` | `false` |
| `alternative_state_initialization` | `false` |

> Cold-start strata are reported as descriptive stratification summaries. They do not constitute independent performance estimates and are not used to support absolute model superiority claims.

| Stratum | Rows | `auprc` | `auroc` | `balanced_accuracy` | `f1` | `false_negative` | `false_positive` | `mcc` | `negative_count` | `npv` | `positive_count` | `positive_prevalence` | `ppv` | `sensitivity` | `specificity` | `true_negative` | `true_positive` | `window_count` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `0_5_minutes` | 1,798 | 0.001511 | 0.632165 | 0.500000 | 0.000000 | 1 | 0 | *undefined* | 1,797 | 0.999444 | 1 | 0.000556 | *undefined* | 0.000000 | 1.000000 | 1,797 | 0 | 1,798 |
| `5_60_minutes` | 19,637 | 0.543960 | 0.909837 | 0.590877 | 0.303132 | 1,581 | 88 | 0.362371 | 17,693 | 0.917596 | 1,944 | 0.098997 | 0.804878 | 0.186728 | 0.995026 | 17,605 | 363 | 19,637 |
| `over_60_minutes` | 452,462 | 0.384040 | 0.930908 | 0.641641 | 0.367642 | 13,818 | 6,358 | 0.356422 | 432,779 | 0.968613 | 19,683 | 0.043502 | 0.479833 | 0.297973 | 0.985309 | 426,421 | 5,865 | 452,462 |

**`causal_gru_longitudinal_v1` — cold start**

| | |
|---|---|
| `cold_start_repair_applied` | `false` |
| `warmup_threshold_applied` | `false` |
| `alternative_state_initialization` | `false` |

> Cold-start strata are reported as descriptive stratification summaries. They do not constitute independent performance estimates and are not used to support absolute model superiority claims.

| Stratum | Rows | `auprc` | `auroc` | `balanced_accuracy` | `f1` | `false_negative` | `false_positive` | `mcc` | `negative_count` | `npv` | `positive_count` | `positive_prevalence` | `ppv` | `sensitivity` | `specificity` | `true_negative` | `true_positive` | `window_count` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `0_5_minutes` | 1,798 | 0.001946 | 0.714524 | 0.496105 | 0.000000 | 1 | 14 | -0.002090 | 1,797 | 0.999439 | 1 | 0.000556 | 0.000000 | 0.000000 | 0.992209 | 1,783 | 0 | 1,798 |
| `5_60_minutes` | 19,637 | 0.489608 | 0.926041 | 0.562962 | 0.221390 | 1,678 | 193 | 0.248912 | 17,693 | 0.912504 | 1,944 | 0.098997 | 0.579521 | 0.136831 | 0.989092 | 17,500 | 266 | 19,637 |
| `over_60_minutes` | 452,462 | 0.289255 | 0.917619 | 0.610490 | 0.267926 | 14,790 | 11,949 | 0.238112 | 432,779 | 0.966048 | 19,683 | 0.043502 | 0.290524 | 0.248590 | 0.972390 | 420,830 | 4,893 | 452,462 |

---

## 7. Calibration wording — plan §7

Both statements are true and travel together:

> U1 Platt calibration exists in the pipeline.

> T2 scores are **uncalibrated temporal model scores**, not calibrated
> probabilities.

| | |
|---|---|
| `score_semantics` | uncalibrated_temporal_model_score |
| `score_definition` | sigmoid(current_window_t2_logit) |
| `score_is_calibrated_probability` | `false` |
| `score_is_confidence` | `false` |
| `score_is_uncertainty` | `false` |

A `sigmoid` output is bounded in [0, 1]; that does not make it a
probability. **No metric in this report is described as calibrated, as a
probability, as a confidence, or as an uncertainty.** U1's retention is a
separate decision about a separate object, and it was a **split** retention:
calibration retained, selective routing **not** retained.

---

## 8. What this analysis does not evaluate — plan §6

None of these is a gap discovered in the evidence. Each is a boundary fixed
by what was run.

- **T1 episode detection** — a different task at a different granularity
- **Episode F1** — belongs to T1 and is not computed here
- **Memory contribution** — no no-memory arm exists in this evidence
- **Encoder contribution** — B4 selection is a separate, earlier decision
- **Calibration contribution** — see §7
- **Clinical utility** — research software, public-dataset validation only
- **External generalization** — one dataset, 12 validation subjects
- **Deployment latency** — `latency_used: false`; no serving path exists
- **Causal inference** — *causal* here means temporal non-anticipation,
  never a treatment effect, intervention or counterfactual
- **Test performance** — the sealed test is unopened and stays so

## 9. Validation firewall — plan §8

| Constraint | Maintained |
|---|---|
| TEST partition | not accessed; `sealed_test_state: unopened`, `test_rows_present: false` |
| New model training | none; no checkpoint loaded, written or refitted |
| Rerun of outer validation | none; this is a consumed one-shot artifact |
| Threshold generation | none; thresholds read as frozen, no sweep, no ROC exploration |
| Artifact modification | none; the run directory was opened read-only |
| Re-scoring | none; scores read from the persisted row stores |
