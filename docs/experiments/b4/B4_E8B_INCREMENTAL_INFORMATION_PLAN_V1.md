# B4 · E8b Conditional Memory-Information Audit and Preregistered Plan, V1

**Read-only. No retraining, no model loaded, no sealed artifact, no threshold
optimized, no classifier fitted, no score transformed.** §1 is the audit,
completed **before** any conditional relationship was computed. §3 onward is the
pre-registration.

**E8b is not a score-normalization experiment and not a new production
classifier.** The fitted probe in §6 is **proposed and not executed.**

---

## 1. Audit — all four objectives resolved

### 1.1 TRAIN-side M1 features exist with verified causal provenance

| | TRAIN | VALIDATION |
|---|---|---|
| Rows | **2,208,431** | 492,904 |
| Streams | **132** | 30 |
| Chronological in persisted array order | **132 / 132** | 30 / 30 |
| `ordered_chronology_sha256` recorded | `99dff218c7ace0133800109bf0120963569534c3a62b2c6d7d7ee6cc96de3c1b` | `89f0b08b…` |
| **Recomputed from persisted arrays** | **match: True** | match: True |
| `d_short` / `d_long` / `prototype_disagreement` non-finite | **0 / 0 / 0** | 0 in scored subset |

Both partitions share `α_short = 0.011485979647`, `α_long = 0.000962241166`,
encoder checkpoint `b1301723…`, standardizer `f3b640ad…`, embedding tap
`B4BTransformerCNN.encode:pooled_post_final_norm`, and update policy
`available_finite_observation_always_update`.

**Objective 1: yes.** TRAIN memory features are persisted with the same
digest-verified causal provenance as VALIDATION.

### 1.2 What would have to be recreated, and how

**The memory features need no recreation.** What is *not* persisted is the **B4
score on TRAIN** — only validation and sealed-test predictions exist.

**It is exactly recreatable without retraining and without labels.**
`representation.npy` is `(2208431, 146)` float32, and its **128-d prefix was
verified equal to the frozen embedding cache** (`allclose`, atol 1e-5, on a
2,000-row sample). E1 established that `classifier.head(embedding)` reproduces
the deployed score exactly — `forward` is literally
`classifier.head(encode(x))`. So a TRAIN score column is a **head-only forward
pass over frozen cached embeddings**: no encoder invocation, no training, no
label.

**Objective 2: yes**, and the recreation is a reproduction with a checkable
identity, not a re-derivation.

### 1.3 Row alignment map

```
M1 TRAIN cache            2,208,431 rows, 132 streams, chronological
  └─ B4 sampled TRAIN set   374,452 rows, 56 subjects, prevalence 0.250000
       strict subset: True      join complete: True      non-finite joined: 0
       M1-only rows: 1,833,979   (full stream beyond B4's sampled training set)

M1 VALIDATION cache         492,904 rows, 30 streams, chronological
  └─ M2-G row evidence      492,904 rows, stable_id order ELEMENT-WISE IDENTICAL
       └─ B4 validation      473,897 rows, strict subset, 0 non-finite memory rows
```

**Keys.** `stable_id` = `dataset:record:channel:start_sample:end_sample`;
stream = `(record_id, channel_index)`; labels come from the B4 prediction
artifact on validation and from the embedding cache on train.

**Objective 3: mapped**, and every join above was executed and asserted, not
assumed.

### 1.4 M2-G held separate

**Objective 4: honoured.** `update_admitted` is **excluded from the primary M1
question** throughout, because it embeds **G3 (waveform SQI)** and **G6
(morphology computability)** — E8a showed its stream-quality correlation
(ρ = +0.682) is confounded with signal quality by exactly that route. M2-G
variables appear in E8b only where explicitly labelled as a separate secondary.

---

## 2. The design point that makes §3A well-posed

At a frozen threshold, **the prediction is a deterministic function of the
score.** So within any score stratum lying wholly below the threshold, every
positive is an FN and every negative a TN; wholly above, every positive is a TP
and every negative an FP.

**Therefore "positive vs negative within a score stratum" *is* the FP/TN and
FN/TP comparison, correctly conditioned.** Computing the error-type contrasts
separately inside strata would be degenerate. E8b reports the label contrast
within strata and labels each stratum by which error types it can contain.

---

## 3. Preregistered strata — fixed constants, not data-derived

```
[0, 1e-4, 1e-3, 1e-2, 0.05, 0.10, 0.25, 0.50, 0.7554003000259399, 0.90, 1.0]
```

Ten bins. **These are fixed numbers chosen for interpretability, not quantiles
of an observed distribution and not selected from any outcome.** The frozen B4
decision threshold `0.7554003000259399` is a bin edge so that error-type
membership is exact. Bin counts and positive counts are reported, including
empty and single-class bins.

---

## 4. Analyses — no model is fitted

**A · Within-stratum label contrast.** For each stratum, rank concordance of
`d_short`, `d_long`, `prototype_disagreement` separating positives from
negatives, with counts. 0.5 = no conditional information.

**B · Does the label-conditioned `d_long` relationship survive conditioning?**
A **stratified concordance**: the within-stratum concordances combined as a
pair-count-weighted average over strata. Compared against the **unconditional**
concordance. **If stratified ≈ 0.5 while unconditional is large, the E8a
relationship was score, not memory.**

**C · Subject-level summaries.** The same stratified concordance computed
**per subject**, so window count cannot masquerade as independent evidence.
Reported for all 9 evaluable subjects individually, never only as a mean.

**D · E8a's stream-level negative finding is preserved, not re-litigated.**
Restated: p90 `d_long` vs stream AUROC ρ = **−0.028**, and the polarity-reversed
stream `s20311:1` carries *lower* distances than its healthy sibling. **E8b does
not re-test it and does not soften it.**

---

## 5. Registered predictions

1. **Unconditional `d_long` concordance for positive vs negative will be high**,
   reproducing E8a.
2. **Stratified concordance will be substantially lower.** E8a measured
   ρ(score, `d_long`) = +0.727 within positives, so much of the apparent memory
   signal is expected to be score.
3. **It will not fall all the way to 0.5.** TP `d_long` median 1.215 against FP
   0.506 suggests some separation survives at comparable scores.
4. **Subject-level results will be heterogeneous**, as in E7a, E7b and E8a.
5. **The highest strata will carry the least conditional information**, because
   a high B4 score already implies atypicality.

---

## 6. Proposed — NOT executed — incremental probe

Justified **only if** §4 shows broad conditional information (decision rule 2).

| Arm | Features |
|---|---|
| **C0** | frozen B4 scalar score |
| **C1** | B4 score + `d_short` + `d_long` + `prototype_disagreement` |

Fixed-capacity classifier, **trained only on the 374,452-row sampled TRAIN set,
evaluated once on VALIDATION**, all hyperparameters fixed in advance, **no
validation selection of any kind**. Its purpose is to test **incremental
information**, never to claim a new model. TRAIN B4 scores would be produced by
the §1.2 head-only reproduction with its identity checked against the published
validation figure first.

---

## 7. Decision rules, registered before results

| Outcome | Action |
|---|---|
| M1 relationships **largely disappear** after conditioning on B4 score | **Close M1 as a predictive augmentation mechanism.** Retain it as patient-state / evidence context only |
| M1 retains **broad conditional information across subjects** | Recommend the §6 TRAIN→VALIDATION probe, preregistered separately |
| Effects **concentrated in a few subjects** | Report heterogeneity; **do not build a universal memory-aware head** |

**Concentration test, as in E7b and E8a:** majority of the effect contributed by
two or fewer of the nine evaluable subjects.

**Bounds.** Mechanism evidence only. Development validation. 9 of 12 subjects
evaluable. No generalization claim available, permanently.
