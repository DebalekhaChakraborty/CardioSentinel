# W1 Window-Only Comparator — Preregistered Analysis Plan, V1

**Pre-registration. No measured value has been read in preparing this document.**
Everything below was derived from artifact *structure* — column names, dtypes,
protocol constants and frozen thresholds — and from values already published in
`docs/T1_DESCRIPTIVE_REPORT_V1.md`.

**This plan authorizes nothing on its own.** §6 describes an authorization gate
that has not been given and that this document does not grant.

---

## 0. Why this experiment exists

Handbook §24 records **RQ4 — "Does longitudinal/episode reasoning improve
monitoring quality?" — as unanswered**, and gives the reason: the T1 measurement
is one-armed. `T1_DESCRIPTIVE_REPORT_V1.md` reports a subject-macro mean
`episode_f1` of **0.2524**, 95% subject-bootstrap **[0.0826, 0.4415]**, and there
is nothing to compare it against. A number without a comparator cannot answer a
question of the form *"does X improve Y?"*, however carefully it was measured.

This plan registers the missing arm.

### 0.1 The feasibility finding that shapes everything below

Structural inspection of the persisted T1 evidence, 2026-08-22:

`cardiosentinel-runs/phase9-t1-development-v1/t1-v1-development/t1_oof_state_evidence.npz`
carries 492,904 rows × 23 columns, and it contains **every input the comparator
needs**:

| Available | Columns |
|---|---|
| Per-row model inputs | `m2g_detector_score`, `detector_decision_d_t`, `oof_calibrated_probability_p_t`, `decision_error_uncertainty_u_t`, `s4d_temporal_evidence_s_t`, `elapsed_stream_seconds` |
| Per-row **frozen** thresholds | `p_watch`, `s_watch`, `p_event`, `s_event` |
| Identity and fold | `stable_id`, `record_id`, `channel_index`, `start_sample`, `subject_id`, `fold_index`, `selected_policy_id`, `score_present` |
| The T1 arm's own output | `emitted_state`, `state_elapsed_seconds`, `transition_from`, `transition_to`, `transition_occurred` |

**It contains no labels.** A search of every `.npz` under `phase9-t1-*` for a
column matching `label`, `target` or `episode` returns **none**. The T1
continuation opened held-out labels one fold at a time at run time, through the
§16 authority, and did not persist them.

**Consequence.** The comparator's *predictions* are computable from persisted
evidence with no new authorization. Its *score* is not: `episode_f1` needs
reference episodes, and those require re-opening held-out labels. That is §6, and
it is the whole gate.

---

## 1. Scientific question

> Does the T1 causal episode state machine produce better episode-level alerting
> than a memoryless window-level rule applied to the same signals, on the same
> rows, under the same frozen thresholds?

**Not** whether T1 is good in absolute terms — that is already published and
weak. Whether the *temporal state logic specifically* contributes anything.

---

## 2. The two arms

Both arms consume the identical 492,904-row store, the identical per-row frozen
thresholds, and the identical held-out label reads. **The only difference is the
transition logic.**

### 2.1 Arm T1 — already measured, not recomputed

The frozen `t1_protocol.next_state` state machine: `NORMAL / WATCH / EVENT /
RECOVERY`, with the `FAST` persistence profile's confirmation and release streak
requirements, WATCH gating before EVENT, and RECOVERY on release. Its per-row
output is the persisted `emitted_state` column.

**This arm is read, never re-run.** The T1 authorization is spent, its directory
is immutable, and nothing in this plan invokes the state machine.

### 2.2 Arm W — the window-only comparator, new

A memoryless rule with no state, no streaks and no gating:

```
alert(row) := is_event_evidence(row, thresholds)
```

using `t1_protocol.is_event_evidence` **unchanged**, including its documented
cold-start relaxation before `T1_COLD_START_SECONDS`, and the same per-row frozen
`p_event` / `s_event`. Contiguous alert rows within a stream form predicted event
runs, segmented on the same key the T1 arm uses.

Arm W therefore differs from Arm T1 in exactly three respects, all of them
"episode reasoning":

1. no confirmation streak — one qualifying row raises an alert;
2. no state carried across rows;
3. no WATCH gating and no RECOVERY hysteresis.

### 2.3 Why this is an ablation and not a strawman

Arm W is **not** a weaker model. It shares the encoder (B4-B), the physiology
fusion (P1-B), the memory (M1L, M2-G), the calibration (U1 Platt), the temporal
score (T2 S4D) and — critically — **the same thresholds, which were frozen per
fold before any held-out label was opened**. No threshold is swept, tuned or
regenerated for Arm W. A comparator given its own tuned operating point would
make the contrast uninterpretable in the direction that flatters whichever arm
got the tuning.

---

## 3. What this isolates, and what it does not

**Isolates.** The contribution of temporal state logic to episode-level alerting,
holding every upstream component and every threshold fixed.

**Does not isolate, and no claim may be made about:** the encoder, physiology
fusion, memory, calibration, the T2 temporal score, or the choice of threshold.
Each is common to both arms by construction. **Memory in particular is not
ablated here** — RQ1 remains unanswered and this plan does not touch it.

**Does not evaluate:** TEST performance, generalisation beyond LTSTDB, clinical
utility, deployment latency, or anything at window level as an endpoint. The
endpoint is episode-level by design, because that is where RQ4 lives.

---

## 4. Endpoint and uncertainty

### 4.1 Primary

**Subject-macro mean `episode_f1`, Arm T1 − Arm W**, over the same 12 held-out
subjects, computed with the identical episode-matching implementation the T1
continuation used.

Subject-macro is chosen because it is T1's own registered primary, so Arm T1's
value must reproduce the published **0.2524** exactly. If it does not, the
comparator is reading different rows and the analysis stops — the same
self-check the T2 analysis used, and the same stopping rule.

### 4.2 Uncertainty — paired subject bootstrap of the difference

Same design as the T2 derived analysis and for the same reason:

| Parameter | Value |
|---|---|
| Unit | **subject** (12) |
| Rows | the **same** resampled subjects for both arms |
| Statistic | subject-macro `episode_f1`(T1) − subject-macro `episode_f1`(W) |
| Refitting / threshold change / reselection | **none** |
| Seed | **2026** |
| Replicates | **1000** |
| Interval | percentile, `lower_95` / `upper_95` |
| Undefined replicates | preserved, never zero-filled |

**Claim scope.** Between-subject variation in the paired contrast, conditional on
the fitted upstream models and frozen thresholds. **Not** a confidence interval
for a population parameter and **not** a hypothesis test. No p-value and no
significance language, anywhere.

**Resolution caveat, registered now.** Twelve subjects. The interval will be
coarse and its tails governed by a handful of subjects. The T1 primary's own
interval spans **[0.0826, 0.4415]** on the same unit; a difference interval on
the same 12 subjects should be expected to straddle zero, and that expectation is
recorded here so it cannot later be presented as a discovery or as a
disappointment.

### 4.3 Secondary, reported separately

Per-subject `episode_f1` for both arms; predicted event runs, matched episodes
and unmatched runs per arm; and the window-level confusion counts. Descriptive,
never aggregated into §4.1.

---

## 5. Registered directional predictions

Recorded **before** any comparator value exists, so they cannot be discovered
afterwards. `T1_POST_HOC_ANALYSIS_V1.md` established two incomparable failure
modes among the seven zero-scoring subjects:

| Group | Subjects | Ref. episodes | T1 predicted runs |
|---|---|---|---|
| **A — episode-free** | `s2005`, `s2020`, `s2023` | 0 | 7, 8, 1 |
| **B — missed** | `s2019`, `s2058`, `s2059`, `s3072` | 6, 3, 47, 1 | 0, 0, 0, 1 |

Arm W removes the confirmation requirement, so it must produce **at least as many
alert rows as Arm T1 on every row where the event condition holds**, and
therefore weakly more predicted runs.

**Predictions, registered:**

1. **Group A gets worse or stays at zero.** These subjects have no reference
   episodes, so every predicted run is a false alarm and `episode_f1` is already
   0.0. More runs cannot improve a score that is already zero; it can only
   worsen the pooled and window-level false-positive picture.
2. **Group B may improve.** These subjects were missed entirely. A rule that
   alerts without confirmation may surface episodes the streak requirement
   suppressed.
3. **The two groups push the subject-macro mean in opposite directions**, exactly
   as they did for T1. A near-zero difference is therefore the *expected* outcome
   and would be **uninformative rather than reassuring** — it can arise from
   genuine equivalence or from two real effects cancelling. §4.3's per-subject
   table is the only thing that distinguishes those, and it is reported for that
   reason, not as decoration.

**If the observed direction contradicts these predictions, the contradiction is
reported as written, not reconciled.**

---

## 6. The authorization gate — held-out labels

**This is the gate, and this plan does not grant it.**

Computing `episode_f1` for Arm W requires reference episodes for the 12 held-out
subjects. They are not persisted (§0.1), so they must be re-opened through
`t1_fold_evaluation.T1CorpusTargetSource`, sponsored by
`t1_fold_authority.FoldScopedEvaluationAuthority` — the §16 authority, the same
door the T1 continuation used.

**What this is not:**

- **Not a T1 rerun.** The state machine is never invoked. No fold is retried, no
  policy is selected, no threshold is generated, no attempt is claimed, and
  nothing is written into either immutable T1 run directory.
- **Not a second continuation.** No continuation identity is claimed and
  `T1_CONTINUATION_AUTHORIZED` is not consulted.
- **Not TEST access.** These are held-out subjects of the T1 out-of-fold
  development design. The B4/neural sealed test is untouched and stays so.

**What it is:** a **second read of labels that have already been opened once**,
for a different analysis arm. That is a smaller thing than a first read of sealed
data and it is not nothing — the seam suite's own docstring records that opening
real held-out labels outside an authorized measurement *"would create exactly the
ambiguity the amendment exists to prevent."*

So it needs its own explicit human authorization, naming this plan, before the
execution step runs. §8 sequences it.

---

## 7. Explicit exclusions

Not done, and not to be added as a follow-up without a separate decision:

- Any invocation of `t1_protocol.next_state` or any T1 runner
- Any threshold sweep, ROC exploration or operating-point search for either arm
- Any alternative comparator rule chosen after seeing Arm W's result — **one
  comparator is registered here and one is permitted**
- Any per-subject narrative explaining an individual subject's score
- Any window-level endpoint promoted to primary
- Any comparison to T2, B0–B3 or B4 numbers, which are different tasks
- Any claim about memory, encoder, fusion or calibration
- Any TEST access

---

## 8. Sequence

| # | Step | Gate |
|---|---|---|
| 1 | Merge this plan **together with a reviewed implementation and synthetic tests** | PR |
| 2 | Human authorizes the held-out label re-read, naming this plan | **human** |
| 3 | Execute against a merged commit; produce `docs/W1_WINDOW_COMPARATOR_REPORT_V1.md` | first read of comparator values |
| 4 | Manuscript positioning | separate decision |

Step 1 pairs the plan with the implementation deliberately. The T2 analysis found
a real defect in its own derived-analysis helper at execution — a guard that
raised on real inputs while every synthetic test passed lists — and it cost
nothing only because the implementation had been merged and exercised first. The
same ordering applies here.

The plan is not modified after step 3. If the shape fixed here proves wrong, that
is recorded in the report as a limitation.

---

## 9. Risks

- **The unrepeatable evidence gets read again.** Every additional read of the T1
  held-out labels increases the number of analyses conditioned on one consumed
  measurement. This plan adds one. It should be the last one that needs those
  labels without a new measurement.
- **A null result is the likely outcome and is easy to over-read** in either
  direction. §5 registers that in advance.
- **Arm W is a rule, not a tuned model**, and a reader may mistake "no
  improvement over a memoryless rule" for "the state machine is useless". The
  correct reading is narrower: at these frozen thresholds, on these 12 subjects,
  the state logic did or did not change episode-level agreement.
- **RQ4 will remain only partially answered even so.** This compares episode
  reasoning against no episode reasoning at the alerting layer. It does not
  compare the T2 longitudinal score against a window-only score upstream, which
  is a separate missing arm and a separate experiment.
