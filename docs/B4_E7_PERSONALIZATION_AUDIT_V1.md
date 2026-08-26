# E7 · Cross-Subject Score-Scale Transfer — Read-Only Audit and Design, V1

**This document audits and designs. It authorizes nothing and implements
nothing.** No model was trained or loaded, no sealed-test artifact was opened,
no experiment lock was read for modification, and nothing was written into any
run directory. Every statement is traceable to a file inspected read-only.

**Verdict up front, because one premise in the research question does not hold
as stated.** The question asks whether *"the existing causal patient-
personalization machinery"* can reduce between-subject score-scale
heterogeneity. **There is no existing score-scale personalization machinery.**
`personalization/` is an empty package — a docstring reading *"Future
contamination-safe patient baseline and adaptation components."* What **does**
exist is a frozen, causal, label-free EMA primitive operating on the **146-d
representation**, not on the score. §2 states exactly what is reusable.

**E7 is nonetheless feasible entirely without retraining**, and more cheaply
than expected: the full `B4 → M1L → M2-G` causal replay over development
validation **has already been executed label-blind and its per-row output is on
disk** (§5).

---

## 1. B4 score path

| Property | Value | Source |
|---|---|---|
| Artifact | `phase3b2-architecture-v1/B4B_cnn_transformer_v1/validation_predictions.npz` | read-only |
| Rows · subjects | **473,897** · **12** | array shapes |
| Fields | `stable_id, subject_id, record_id, channel_index, target_family, context_flags, label, score` | npz keys |
| Score semantics | *"uncalibrated sigmoid model score; not calibrated probability"* | `VALIDATION_METRICS.json` |
| Classification threshold | `0.7554003000259399` | `VALIDATION_THRESHOLD.json` / M2 arm result |
| Encoder digest | `b1301723…` = `sha256(model_selected.pt)` | verified in E1 |

### 1.1 Timestamps and order — recoverable, but **not** the array order

**There is no timestamp column.** Ordering is encoded in `stable_id`:

```
ltstdb : s20041 : 0       : 0            : 2500
dataset  record   channel   start_sample   end_sample
```

**The array is sorted lexicographically, not chronologically** — the first three
rows are start samples `0`, `10000000`, `1000000`, in that order. **Any causal
replay that trusts array order would process windows out of sequence and
silently violate causality while producing a plausible result.** E7 must sort by
parsed `start_sample` within `(record_id, channel_index)` and assert
monotonicity.

A true elapsed-time column, `available_time`, exists in the M2-G evidence store
(§4) spanning `[10.0, 86400.0]` seconds, and is the preferred ordering key when
joining through that artifact.

### 1.2 Stream scope

`record_id` + `channel_index` defines a stream. M1's protocol states memory
**resets at every recording boundary** — there is no cross-record acquisition
chronology, so *"patient-adaptive"* in this programme means **within one
continuous recording/lead stream**, not across a subject's records.

---

## 2. M1L

| Property | Value |
|---|---|
| State | **two EMA prototypes** `μ_short`, `μ_long`, each `[146]` float64 |
| Representation | 128-d frozen B4-B embedding ⊕ 18-d physiology |
| Initialization | both prototypes set to a **frozen cold-start prior** vector; refuses non-finite |
| Update | `μ ← (1−α)·μ + α·x` |
| Constants | `α_short = 1 − 2^(−1/60)`, `α_long = 1 − 2^(−1/720)` (half-lives 300 s / 3600 s at 5 s stride) |
| Emitted features | `d_short`, `d_long` (RMS distance to each prototype), `past_observed_count`, `past_update_count`, `prototype_disagreement` |
| Causality | `observe()` computes deviations against **pre-update** prototypes, then updates — a window can never influence the state used to score itself |
| Scope | one instance per `(record_id, channel_index)`; rebuilt at every boundary |

### 2.1 Labels are never required — verified in source and protocol

`DualTimescaleMemory.update()` takes exactly one argument, the standardized
observation. Its docstring: *"There is deliberately no label, score, threshold,
uncertainty or event argument: M1-v1 cannot gate admission on any of them."*

The protocol §5.1 is explicit: the update *"MUST NOT be gated on
`morphology_valid`, the ischemic label, the background label, the rate label,
the axis label, the conduction label, the model score, uncertainty, a threshold,
WATCH/EVENT state, or any future information."*

**M1L is therefore label-free at inference and at update.** This is the single
strongest enabler for E7.

### 2.2 The warning M1 carries about itself

> **"THIS M1 UPDATE RULE IS INTENTIONALLY NOT CONTAMINATION-SAFE. AN ABNORMAL
> OR CONFOUNDED *AVAILABLE* WINDOW MAY ENTER MEMORY. M2 IS REQUIRED BEFORE ANY
> SAFE-ADAPTATION OR DEPLOYMENT-SAFE PERSONALIZATION CLAIM."**

**Any E7 arm claiming deployment-safe personalization must route its baseline
updates through M2-G.** An arm that updates on every available window is a
*mechanism* arm, not a deployment arm, and must be labelled as such.

### 2.3 What M1 is **not**

**M1 operates in representation space and emits distances.** It contains no
per-subject score statistic, no score normalisation and no location/scale model
of the score. **The primitive E7 needs — a causal per-stream running baseline —
exists and is frozen; the object it is applied to would be new.**

---

## 3. M2-G

| Gate | Meaning |
|---|---|
| G3 | waveform SQI bounds, **TRAIN-only Q99**; five independent constraints. Amplitude-like columns deliberately excluded because *"they vary legitimately with patient physiology"* |
| G4 | deterministic normal-evidence margin, derivation quantile 0.50 |
| G5 | memory-update safety refractory |
| G6 | morphology computability admission (`morphology_valid`) |

**Measured gate behaviour on development validation**, from the persisted row
evidence:

```
rows                492,904
scored              492,898   (99.9988%)
update_admitted     107,671   (21.84%)
refused among scored 385,227  (78.16%)
```

**The gate refuses roughly four of every five scored windows for memory
admission.** That is the contamination protection operating, and E7 must record
it per arm rather than assume it.

**It can operate entirely causally**, and did: `label_blind_replay_completed:
true`, `classifier_retrained: false`, `memory_selection_performed: false`,
`attempt1_test_accessed: false`.

**Interaction with M1L:** M2-G converts M1's *available → always update* into
*available → update only if admitted*, which is exactly the counter divergence
M1's §5.3 reserved (`past_observed_count` may exceed `past_update_count`).

---

## 4. U1

| Property | Value |
|---|---|
| Form | `g(s) = sigmoid(a·z(s) + b)`, `z` = recovered logit |
| Parameters | **a = 0.3715906808641229**, **b = −1.7662772879067046** |
| Family | `platt_logistic_on_recovered_logit` |
| **Scope** | **one global calibrator. There is no subject-specific variant** |
| **Fitted on** | **VALIDATION** — all 12 subjects, 473,897 rows |
| Monotonic | **yes**, asserted in `U1Calibrator.__post_init__` — *"Decision equivalence depends on monotonicity"* |
| Decision equivalence | `disagreement_count: 0` at the mapped boundary `0.20631829355583678` |

### 4.1 Two consequences for E7

1. **U1 cannot improve discrimination.** It is monotone by construction, so
   AUPRC and AUROC are invariant under it — the same invariance E3 established
   and measured at exactly `0.0`. U1 belongs in E7 as a **calibration
   endpoint**, never as a discrimination arm.
2. **U1's parameters were fitted on the partition E7 evaluates on.** Any E7 arm
   that applies U1 inherits parameters that have seen validation outcomes.
   **This is a leakage channel and §8 registers how it is handled.**

### 4.2 No subject-relative calibration exists anywhere

Searched: `personalization/` (empty), `uncertainty/` (empty), `u1_calibration.py`
(single global `(a, b)` with a `fit_subjects` provenance list, not per-subject
parameters). **A subject-relative mechanism would be new work.**

---

## 5. Existing integration — already replayed, on disk

**This is the decisive feasibility finding.**
`phase6-m2-development-v1/…recovery2__evidence/M2-G/row_evidence.npz` holds, for
**all 492,904 development-validation windows**:

```
stable_id  record_id  channel_index  start_sample
available_time   score   scored   update_admitted
```

with `partition_accessed: "validation"`, `label_blind_replay_completed: true`,
`classifier_retrained: false`.

**Row containment is exact and was verified:**

```
B4 rows                       473,897
M2-G scored                   492,898
intersection                  473,897     ← every B4 row is present
B4 rows not scored by M2-G          0
M2-G scored rows not in B4     19,001     ← windows B4 never scored
```

**Therefore `B4 → M1L/M2-G → U1` can be replayed on development validation with
no retraining, no encoder forward pass, and no new authorization.** The
integrated score and the per-row gate decision are already materialised; U1 is
two frozen scalars.

---

## 6. Feasibility verdict

| Requirement | Verdict |
|---|---|
| Without retraining | ✅ **Yes** — §5 |
| Without sealed data | ✅ **Yes** — development validation only; test never enumerated |
| Without altering the frozen encoder | ✅ **Yes** — no encoder invocation at all |
| Without experiment-lock changes | ✅ **Yes** — all artifacts read-only; outputs to a new derived path |
| Using *existing* personalization machinery | ❌ **No** — §2.3. The EMA primitive is reusable; a score-space baseline is **new code** (no training, ~hours) |

---

## 7. Proposed arms

All arms scored on the **same rows**, with the shared row set stated per
comparison. **No arm retrains anything.**

| Arm | Definition | Class |
|---|---|---|
| **R** | **frozen raw B4-B score** — the reference | reference |
| **C-prior** | E3 analytic global prior correction | **calibration control** |
| **C-u1** | U1 global Platt | **calibration control** |
| **P-causal** | causal per-stream score standardisation: `z_t = (s_t − μ_t)/σ_t`, EMA over `s_{<t}` only, M1's frozen `α_long` | mechanism, **deployment-shaped** |
| **P-gated** | P-causal, but the running baseline updates **only on `update_admitted` rows** | mechanism, **deployment-safe** |
| **P-oracle** | fixed whole-stream `μ`, `σ` per stream | **mechanism ceiling — NOT deployable** |
| **I** | the persisted M1L+M2-G integrated score | integrated reference |

**Both calibration controls are registered as ranking-invariant.** E3 measured
`ΔAUPRC = ΔAUROC = 0.0` exactly; U1 is monotone by construction. **If either
moves a ranking metric, the implementation is wrong** — the same gate-shaped
check E3 used.

**P-oracle is non-causal and can never be deployed.** It exists to bound how
much of the pooling penalty is removable by *any* per-stream location/scale
correction. Registering the ceiling before running the causal arms prevents
reading a small causal gain as a small opportunity.

**A registered asymmetry between P-oracle and P-causal.** P-oracle uses a fixed
per-stream `(μ, σ)`, so it is **monotone within a stream** and per-subject AUROC
is invariant by construction. P-causal's `(μ_t, σ_t)` vary with `t`, so it is
**not** monotone within a stream and per-subject ranking *can* change. **These
two arms therefore answer different questions and must not be compared as if
they were the same transform.**

---

## 8. Leakage risks

| # | Risk | Severity | Control |
|---|---|---|---|
| 1 | **U1's `(a, b)` were fitted on validation** | **High** | C-u1 is reported **only** as a calibration endpoint, never as evidence about discrimination, and its provenance is printed beside every number |
| 2 | **Array order is lexicographic, not chronological** (§1.1) | **High** | Sort by parsed `start_sample` within stream; **assert strict monotonicity before any EMA runs** |
| 3 | Per-stream statistics computed over the whole stream leaking future into past | **High** | Only P-oracle may do this, and it is labelled non-deployable in every table |
| 4 | Tuning `α`, warm-up length or clipping against validation outcome metrics | **High** | **All constants fixed before execution**: `α = α_long` inherited from M1, warm-up and floors registered in the plan, no grid, no selection |
| 5 | Subject separation | Medium | Streams never cross `record_id`/`channel_index`; assert no cross-stream state |
| 6 | Prevalence confounding of AUPRC comparisons | Medium | **Per-subject prevalence reported beside every per-subject metric** — E6a measured `r ≈ +0.5…+0.8` between width and prevalence |
| 7 | Subject-macro over a shifting denominator | Medium | **9 of 12** subjects contribute (three carry no positive window); the count is printed beside every macro figure |
| 8 | Reading gate behaviour as a result | Low | `update_admitted` share reported per arm as a **descriptor** |

**No arm may consult a label at inference or at update.** M1's §5.1 prohibition
is inherited verbatim by P-causal and P-gated.

---

## 9. Estimands

### 9.1 Primary — mechanism

1. **Between-subject location dispersion** — SD across subjects of the
   per-subject median score.
2. **Between-subject scale dispersion** — SD across subjects of the per-subject
   IQR.
3. **Within-subject ranking** — per-subject AUROC (prevalence-independent),
   reported with per-subject prevalence.
4. **Pooled versus subject-macro discrimination** — both AUPRC and AUROC.
5. **Pooling penalty** — `subject_macro − pooled`, per metric.

**The pooling penalty is the estimand the hypothesis is actually about.** For
the frozen B4 reference it is already known from E1: pooled AUPRC `0.380535`,
subject-macro `0.400636`, **penalty `+0.0201`** on nine contributing subjects.

### 9.2 Secondary

Calibration (Brier, NLL), false-positive burden at a fixed operating point,
sensitivity, and episode-level behaviour **only if** the persisted T1/W1 path
permits replay without new authorization — **to be verified before being
promised**.

---

## 10. Registered hypotheses

- **H1 (descriptive).** Per-stream B4 score distributions differ materially in
  location and scale across subjects. *Falsifiable: dispersion near zero.*
- **H2 (mechanism).** Causal per-stream standardisation reduces between-subject
  location and scale dispersion relative to R.
- **H3 (the actual claim).** Reducing that dispersion **narrows the pooling
  penalty** — pooled discrimination moves toward subject-macro.
- **H4 (invariance, a correctness gate).** C-prior and C-u1 leave pooled and
  per-subject AUROC/AUPRC **exactly** unchanged.
- **H5 (ceiling).** P-oracle bounds P-causal and P-gated. If P-oracle's pooling
  penalty reduction is small, **the mechanism is not the limiting factor** and
  no causal variant can rescue it.
- **H6 (cost of safety).** P-gated updates on ~21.84% of rows, so its baseline
  adapts more slowly than P-causal. **The difference is the measurable price of
  contamination safety**, and it may be negative.

**H5 is the hypothesis most likely to end this line of work, and it is the
cheapest to evaluate. It should be evaluated first.**

---

## 11. Three evidence classes, kept separate

| Class | What E7 can produce |
|---|---|
| **1. Mechanism evidence** | **Yes.** Dispersion, ranking invariance, pooling penalty are properties of transforms on fixed scores |
| **2. Development performance** | **Yes, bounded.** Twelve subjects, nine contributing to macro, one cohort. E6a showed this cohort cannot separate contrasts of the size seen so far |
| **3. Generalization evidence** | **No. Never.** The sealed test is consumed, `repeat_attempt_permitted: false`, and no held-out estimate is obtainable within LTSTDB **permanently** |

**No E7 result may be phrased as "improves detection".** The permitted phrasing
is *"reduces between-subject dispersion"* or *"narrows the pooling penalty"* —
statements about score geometry, not about clinical performance.

---

## 12. Decision rules for what follows E7

Registered now, so the follow-on is not chosen by whichever result looks best.

| E7 outcome | What follows |
|---|---|
| **P-oracle barely narrows the penalty** | **Stop this line.** Score-scale transfer is not the limiting factor. Do not build a causal personalizer to chase a ceiling that is not there |
| **P-oracle narrows it substantially, P-causal does not** | The information is there but not *causally* available. Investigate warm-up and stream length — **not** a new encoder |
| **P-causal ≈ P-oracle** | Mechanism confirmed and causally reachable. The next experiment is a **pre-registered per-subject calibration layer**, which is new development with its own plan |
| **P-gated ≪ P-causal** | Contamination safety is expensive here. That is a finding about M2-G's admission rate, and belongs in the paper beside §5.6 |
| **Everything within noise** | The expected outcome given E6a. **Report as an instrument limit, not as equivalence**, and do not escalate to a retraining experiment on the strength of it |

**In no branch does E7 justify launching E4, E5 or E6 by itself.** Every
retraining item still requires a fresh human authorization, and fifteen of
fifteen one-shot budgets are spent.

---

## 13. Effort

| Item | Estimate | Authorization |
|---|---|---|
| E7 pre-registration | ~2–3 h | none |
| Implementation (causal EMA over scores; no training) | ~0.5 day | none |
| Execution + bootstrap | ~1–2 h | none |
| Report | ~0.5 day | none |

**No training, no GPU, no new data, no budget.** The expensive part of E7 is
writing down what would count as a refutation before it runs.
