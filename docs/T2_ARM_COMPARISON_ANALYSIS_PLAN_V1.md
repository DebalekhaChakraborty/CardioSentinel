# T2 Arm Comparison — Preregistered Analysis Plan, V1

**Pre-registration. No measured value has been read, reported or interpreted in
preparing this document.** Everything below was derived from artifact *structure*
— key names, array shapes, dtypes, protocol flags, identity digests and
resampling parameters — never from a metric.

**Analysis has not been authorized.** This is the plan to be approved, not the
analysis. It follows the ordering established for T1 in
`docs/T1_EVIDENCE_ANALYSIS_PLAN_V1.md`: the reporting shape is fixed before the
values are visible, so that it is a pre-registration rather than a
rationalization.

| | |
|---|---|
| Evidence | `cardiosentinel-runs/phase8-t2-development-v1/t2-v1-outer-validation` |
| Result artifact | `T2_OUTER_VALIDATION_RESULT.json` · `c58ed40dac753157b00ce6c70eb52fe903ecee72a5ef84e40932c1a80e259dbf` |
| Authorized git SHA of the run | `b0f189a57bea8bd28884e7e40be50136fd6e2927` |
| Retained arm | `causal_s4d_longitudinal_v1` |
| Comparator arm | `causal_gru_longitudinal_v1` |
| Partition | `validation` (12 subjects, 13 records, 30 streams) |
| Sealed test state | `unopened` |
| Prepared | 2026-08-22, from structure only |

---

## 0. What exists

Confirmed present by structural inspection. **Both arms carry every structure;
none is one-sided.**

| Structure | S4D | GRU | Notes |
|---|---|---|---|
| `per_arm_evidence` | ✅ | ✅ | 19 keys per arm |
| `pooled` metrics | ✅ | ✅ | identical names: `auprc`, `auroc`, `balanced_accuracy`, `f1`, `mcc`, `npv`, `ppv`, `sensitivity`, `specificity` |
| `subject_macro` metrics | ✅ | ✅ | identical names: `auprc`, `auroc`, `mcc`, `sensitivity`, `specificity` |
| `subject_bootstrap` | ✅ | ✅ | 9 metric intervals each, `unit: subject`, seed `2026`, `1000` replicates, `model_refitted_per_replicate: false` |
| `temporal_descriptors` | ✅ | ✅ | 25 keys each, identical key sets |
| `challenge` evidence | ✅ | ✅ | with subsets |
| `cold_start` evidence | ✅ | ✅ | with strata |
| `internal_dev_thresholds` | ✅ | ✅ | `derived_before_outer_validation: true` |
| `selection_decision` | — | — | single object; records the basis, the selected arm and the margins |
| `row_evidence_store` | ✅ | ✅ | paired, see §0.2 |

### 0.1 Pairing guarantees

The comparison is **paired by construction**, verified from protocol flags and
identity digests:

| Guarantee | Evidence |
|---|---|
| Identical rows | one `t2_outer_row_identity.npz` of **492,904** rows serves both arms; each arm's score array is `(492904,)` `float64` |
| Identical ordering | `full_timeline_ordering: stream_then_start_sample`; shared `ordered_stable_id_sha256 a5453f4c…` and `ordered_chronology_sha256 89f0b08b…` |
| Identical subjects | 12 subjects, 13 records, 30 streams, `partition: validation`, shared `stream_cache_sha256 a3e39137…` |
| Identical labels | a single `label` vector lives in the identity store, not per arm |
| Frozen thresholds | both arms `derived_before_outer_validation: true`, `outer_validation_may_alter: false`, `threshold_altered_by_outer_validation: false`, same rule `exact_maximum_f1_highest_threshold_tie_break` on `t2_internal_dev_8_subjects` |
| One pass each | `single_causal_pass: true`, `second_temporal_replay_performed: false`, `second_challenge_replay_performed: false` for both arms |
| Every row accounted | `every_row_resolved_exactly_once: true`; `primary_mask` covers **473,897** rows |

### 0.2 Row evidence store

| File | SHA-256 |
|---|---|
| `T2_OUTER_ROW_EVIDENCE.json` | `c76453b8970a06c6beb3c280ab6e0518fa4cf81fcb304f6f9aa9c569d2634949` |
| `t2_outer_row_identity.npz` | `1014357cd25d347c7a760e38dbf7ae93c71d56717d13a40e315bb9cb79b220dc` |
| `t2_outer_scores_s4d.npz` | `5c7f9763713c66759cf7e3752cda2a71dacb6cc3f962c5bdd5247017447a7a32` |
| `t2_outer_scores_gru.npz` | `2dbfa5da02f0d96065d72f272875f805f5dceb28410b90582df34c8f6fc17f2d` |

`content_sha256: 2240ca683fbcb790609c47f4a82af85250abb281fbbb9751dc74607a4eb591ca`,
`lossy_conversion_applied: false`, `nan_is_ever_a_model_score: false`,
`test_rows_present: false`.

---

## 1. Scientific question

**The question this plan authorizes:**

> Does the retained S4D longitudinal model differ from the GRU comparator in
> **window-level temporal score modelling** under the predefined
> outer-validation protocol?

**The question this plan does not authorize:**

> ~~Does S4D improve episode detection?~~

Episode reasoning belongs to T1, and the artifacts say so themselves:

```
temporal_descriptors.episode_grouping_performed           : false
temporal_descriptors.formal_episode_reasoning_belongs_to  : 't1'
temporal_descriptors.prediction_persistence_is_episode_onset_offset_measurement : false
```

T2 measures a window-level score. T1 measures episode-level alerting. No result
from this analysis may be carried across that boundary, in either direction.

---

## 2. Primary estimand

**S4D − GRU pooled primary validation AUPRC difference**, read verbatim from
`selection_decision.pooled_auprc_difference`.

Window-level, over the primary-mask rows of the 12 validation subjects, both
arms scored on identical rows under thresholds frozen before outer validation.

**Required wording.** This difference **is the predefined selection criterion**
(`selection_decision.selection_basis: pooled_primary_validation_auprc`). It must
never be described as an independent discovery. Every report of it states, in
the same passage, that it is the criterion by which the arm was chosen.

---

## 3. Selection conditioning disclosure

**The S4D arm was selected using this very comparison.** The artifact records
`selected_arm: causal_s4d_longitudinal_v1` and
`selection_basis: pooled_primary_validation_auprc` in the same object as the
margins.

This has a precise statistical consequence, and stating it imprecisely is the
main failure mode this section exists to prevent:

| | |
|---|---|
| **The paired contrast is unbiased** | Both arms were evaluated on the same held-out rows under a rule fixed in advance. Selecting on the outcome does not bias the *difference* between the two arms. |
| **The winner's absolute figure is not** | S4D's own AUPRC on this set is optimistically biased, because S4D was chosen for having the higher value **on this very set**. The bias attaches to the maximum, not to the contrast. |

**Allowed**

- Report the contrast.
- Report the selection margin.
- Discuss the selection rule, its tie tolerance, and the fact that it was fixed
  before the outer validation ran.

**Not allowed**

- Any claim of unbiased absolute S4D performance on this validation set.
- Any presentation of the margin as a finding that emerged from the analysis.

**Prohibited phrasing:**

| ❌ Never | ✅ Instead |
|---|---|
| "S4D achieved superior AUPRC" | "The predefined selection rule selected S4D based on the observed validation contrast." |
| "S4D was found to outperform GRU" | "The pre-specified criterion favoured S4D by the recorded margin." |
| "S4D achieves AUPRC = *x* on validation" | Report the contrast; do not present the selected arm's absolute value as an unbiased estimate. |

---

## 4. Authorized derived analysis

**Exactly one new computation is authorized.** Everything else in this plan is a
verbatim read.

### DERIVED ANALYSIS — paired subject-level bootstrap of the S4D − GRU AUPRC difference

The artifacts carry a `subject_bootstrap` **per arm** and **no interval on the
difference**. The contrast in §2 therefore has a point estimate and no
uncertainty. This computation supplies exactly that, and nothing else.

**Registered design, fixed before execution:**

| Parameter | Value |
|---|---|
| Resampling unit | **subject** (12 subjects) |
| Rows | the **same** resampled rows for both arms, from the shared identity store |
| Statistic per replicate | pooled primary AUPRC(S4D) − pooled primary AUPRC(GRU) |
| Model refitting | **none** |
| Threshold changes | **none** — frozen internal-dev thresholds are used as recorded |
| Reselection | **none** — the arm identities are fixed; no arm is re-chosen inside the bootstrap |
| Seed | **2026** |
| Requested replicates | **1000** |
| Interval | percentile, `lower_95` / `upper_95` |
| Undefined replicates | preserved and reported as undefined, never zero-filled |

Seed and replicate count are bound to the design already registered in the
artifact's own `subject_bootstrap` (`seed: 2026`, `replicates: 1000`,
`unit: subject`, `model_refitted_per_replicate: false`) so that the derived
interval is commensurable with the per-arm intervals rather than a parallel
construction.

**Labelling.** Every appearance of this quantity carries the label
**DERIVED ANALYSIS**, together with the statement that no artifact stores it.

**Claim scope.** The interval describes between-subject variation in the paired
contrast, conditional on the fitted temporal models. It is **not** a confidence
interval for a population parameter, and it is **not** a hypothesis test. No
p-value and no significance language is produced anywhere in this analysis.

**Resolution caveat, registered now.** The resampling unit has 12 members, so
the percentile interval is coarse by construction and its tails are governed by
a handful of subjects. It indicates between-subject spread, not precision.

---

## 5. Secondary analyses

Reported **separately** from the primary contrast, never merged into it.

### 5.1 Subject-macro AUPRC difference

Read verbatim from `selection_decision.subject_macro_auprc_difference`.

Subject-weighted rather than row-weighted. It is a **different estimand** from
§2 and need not agree with it. It was **not** the selection basis, but it is
computed on the same evidence the selection consumed, so it is reported as a
companion to the primary contrast rather than as independent corroboration.

### 5.2 Selection-independent temporal descriptors

These are the **only comparisons in this plan that are free of selection
conditioning**. The artifacts state it directly for both arms:

```
temporal_descriptors.is_selection_input   : false
temporal_descriptors.may_alter_threshold  : false
challenge_used_in_selection               : false
latency_used_in_selection                 : false
```

Reported per arm, verbatim, with identical key sets across arms:

- run persistence (`prediction_persistence_around_labelled_ischemic_intervals`,
  with its stated definition and `window` unit)
- transition frequency (`transition_count`, `transition_count_per_hour`, over
  `transition_denominator: full_physical_timeline_exposure`)
- positive run duration (`median_positive_run_duration_seconds`,
  `positive_prediction_run_count`, `isolated_single_window_positive_fraction`)

**These must remain separate from the selection criterion.** They are descriptive
comparisons of temporal behaviour, they were not inputs to the choice of arm, and
they must not be aggregated into, or presented as support for, the §2 contrast.

Each carries the artifact's own qualifiers: `episode_grouping_performed: false`,
`prediction_persistence_is_episode_onset_offset_measurement: false`,
`runs_cross_stream_boundaries: false`,
`run_segmentation_key: record_id_channel_index`.

### 5.3 Challenge and cold-start evidence

Reported per arm, verbatim, with `is_selection_input: false` stated alongside.
Challenge subsets and cold-start strata are descriptive; no subgroup claim is
made from them.

---

## 6. Explicit exclusions

**This analysis does not evaluate:**

- **T1 episode detection** — a different task at a different granularity
- **Episode F1** — belongs to T1 and is not computed here
- **Memory contribution** — no no-memory arm exists in this evidence
- **Encoder contribution** — B4 selection is a separate, earlier decision
- **Calibration contribution** — see §7
- **Clinical utility** — research software, public-dataset validation only
- **External generalization** — one dataset, 12 validation subjects
- **Deployment latency** — `latency_used_in_selection: false`; no serving path exists
- **Causal inference** — "causal" here means temporal non-anticipation, never a
  treatment effect, intervention or counterfactual
- **Test performance** — the sealed test is unopened and stays so

None of these is a gap discovered in the evidence. Each is a boundary fixed by
what was run.

---

## 7. Calibration wording

Both statements are true and must travel together:

> U1 Platt calibration exists in the pipeline.

> T2 scores are **uncalibrated temporal model scores**, not calibrated
> probabilities.

The artifacts are explicit:

```
score_semantics                : 'uncalibrated_temporal_model_score'
score_definition               : 'sigmoid(current_window_t2_logit)'
score_is_calibrated_probability: false
score_is_confidence            : false
score_is_uncertainty           : false
```

A `sigmoid` output is bounded in [0, 1]; that does not make it a probability.

**Do not combine calibration claims with T2 score metrics.** No metric in this
analysis may be described as calibrated, as a probability, as a confidence, or
as an uncertainty. U1's retention is a separate decision about a separate
object, and per
`docs/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` it was a **split**
retention: calibration retained, selective routing **not** retained.

---

## 8. Validation firewall

Preserved without exception:

| Constraint | Status to be maintained |
|---|---|
| TEST partition | **Not accessed.** `sealed_test_state: unopened`, `test_accessed: false`, `test_rows_present: false` |
| New model training | **None.** No checkpoint is loaded, written or refitted |
| Rerun of outer validation | **None.** `validation_accessed: true` — this is a consumed one-shot artifact and is not repeatable |
| Threshold generation | **None.** Thresholds are read as frozen; no sweep, no ROC exploration, no operating-point search |
| Artifact modification | **None.** The run directory is read-only for this analysis |
| Re-scoring | **None.** Scores are read from the persisted row stores; no model is evaluated |

---

## 9. Sequence

| # | Step | Gate |
|---|---|---|
| 1 | Approve this plan | **human** |
| 2 | Merge the plan | PR |
| 3 | Execute §4 and produce the report | first read of T2 values |
| 4 | Manuscript positioning | separate decision |

**Step 3 is the first time anyone reads a measured value from this evidence.**
As with T1, it should be a human reading them or an explicitly authorized
analysis — never a side effect of a status check.

---

## 10. Risks carried into this analysis

**The evidence is unrepeatable and unbacked.** The outer validation was a
one-shot consumed artifact and no rerun is authorized. The row stores are
gitignored and exist on a single disk alongside every other run artifact. This
analysis increases the value of that evidence without increasing its safety.

**The selection-conditioning framing is the whole risk of this analysis.** The
contrast is legitimate and the margin is real; the failure mode is describing
either as a discovery. §3 exists because that sentence is easy to write by
accident and hard to retract once published.
