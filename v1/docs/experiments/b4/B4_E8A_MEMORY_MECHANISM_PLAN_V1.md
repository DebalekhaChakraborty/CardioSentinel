# B4 · E8a Representation-Space Memory Mechanism Analysis — Audit and Preregistered Plan, V1

**Read-only. No retraining, no sealed artifact, no threshold optimization, no
model fitted, no score transformed.** §1 is the provenance audit, completed
**before** any outcome relationship was computed. §3 onward is the
pre-registration.

**E8a is not a score-normalization experiment.** No memory quantity is used to
transform a B4 score, and no classifier is fitted to predict errors.

---

## 1. Provenance audit — PASSED

### 1.1 Semantics

| Quantity | Definition | Source |
|---|---|---|
| `d_short` | `RMS(x_t − μ_short)`, pre-update prototype | `patient_memory.deviations` |
| `d_long` | `RMS(x_t − μ_long)`, pre-update prototype | same |
| `prototype_disagreement` | `RMS(μ_short − μ_long)` | same |
| `past_observed_count` / `past_update_count` | prior admitted observations / updates | counters |
| `update_admitted` | M2-G verdict: this window may enter memory | M2-G row evidence |
| `scored` | a B4/M1L score exists for the row | M2-G row evidence |
| M2-G gates | **G3** SQI bounds (train-only Q99, 5 constraints; amplitude columns excluded as legitimately patient-varying) · **G4** normal-evidence margin (q=0.50) · **G5** memory-update refractory · **G6** morphology computability | `m2_gate.py` |

`x_t` is the **146-d** fused representation (128-d frozen B4-B embedding ⊕ 18-d
physiology), standardized by a frozen standardizer
(`f3b640ad…`). `α_short = 0.011485979647`, `α_long = 0.000962241166`.

### 1.2 Causal generation — verified in source

| Requirement | Evidence |
|---|---|
| **State scored before update** | `observe()` calls `deviations()` on pre-update prototypes, *then* `update()`. Docstring: *"a window can never influence the state used to compute its own distance."* |
| **No future information** | prototypes are EMAs over strictly earlier windows only |
| **No labels** | `update()` accepts one argument. Protocol §5.1 forbids gating on any label, score, threshold or state |
| **Reset boundary** | `DualTimescaleMemory(prior)` re-instantiated per `(record_id, channel_index)` — exactly M1L's scope |
| **Chronological ordering** | `build_causal_streams` sorts by `int(item.start_sample)` — **numeric**, and raises `"the causal order is ambiguous"` on non-strictly-increasing starts |

### 1.3 The ordering proof E7b demanded

E7b established that the **B4** arrays are lexicographic and **0 of 30** streams
are chronological in array order. That defect does **not** carry into the memory
cache:

| Check | Result |
|---|---|
| Persisted M1 array order strictly chronological within stream | **30 / 30 streams** |
| `ordered_chronology_sha256` recorded in manifest | `89f0b08bcd518fe0017c50bac0e198a1d9b61bc69fc1e3c6e06c148bbcb6960f` |
| **Recomputed from the persisted arrays** | `89f0b08bcd518fe0017c50bac0e198a1d9b61bc69fc1e3c6e06c148bbcb6960f` |
| **Match** | **True** |

**Causality is proven from an order-sensitive digest recomputed from the stored
data, not inferred from file order.** The gate passes and E8a may proceed.

### 1.4 Row alignment

```
M1 stream cache        492,904
M2-G row evidence      492,904     stable_id order element-wise IDENTICAL to M1
B4 validation scores   473,897     a strict SUBSET of both
M1/M2 rows with no B4 score  19,007
scored (M2-G)          492,898     matches M1 available_row_count
```

**Denominator rule.** Any analysis requiring a score or a label uses the
**473,897**-row intersection and says so. Analyses of gate behaviour may use all
492,904 and say so. `contamination_safe` is **False** on the M1 cache by design —
M1 alone is not contamination-safe; M2-G supplies that.

---

## 2. What E8a may not do

- **No memory quantity may transform a B4 score.**
- **No classifier is fitted.** Rank-association statistics are descriptive
  summaries of already-frozen columns, not fitted models, and are labelled as
  such.
- **No memory threshold is selected from validation outcomes.** Where a split on
  a memory quantity is needed, **fixed distribution-free quantiles of that
  quantity itself** are used — never a cut chosen to separate outcomes.
- **Only the frozen B4 decision threshold `0.7554003000259399`** is used. It is
  not re-derived, re-optimized or varied.

---

## 3. Analyses

**A · Window-level error association.** At the frozen threshold, compare
`d_short`, `d_long`, `prototype_disagreement` and the `update_admitted` rate
across **FP vs TN**, **FN vs TP**, and **incorrect vs correct**. Reported as
median with IQR per group, plus a **rank-concordance** statistic (the AUC of the
memory quantity separating the two groups) as a descriptive effect size.
Per-subject and pooled, denominators printed.

**B · Label-conditioned behaviour.** Within positives and negatives
**separately**, characterize B4 score against each memory quantity —
Spearman correlation, and mean/median B4 score by `update_admitted`.
Conditioning on label separately is the point: a pooled association would be
confounded by prevalence.

**C · Stream-quality analysis.** For the **19 streams with both classes**,
compare frozen B4 stream AUROC and separation against per-stream median and
90th-percentile `d_short`/`d_long`, median `prototype_disagreement`, and M2
admission fraction. **n = 19**; Spearman only, no fitting, and the small n is
stated with every coefficient. `s20311:1` (AUROC 0.2119) is inspected
explicitly **as an illustrative case and never as the estimand**.

**D · M2 contamination mechanism.** Admitted vs refused windows compared on B4
error burden, memory-distance regime, and label composition. **Interpreted only
as contamination-control evidence**, never as classification improvement.

Subject-level summaries carry a paired subject bootstrap (1,000, seed 2026)
where a pooled contrast is reported. **E6a applies: 12 subjects, wide
intervals.**

---

## 4. Registered predictions

1. **Errors will sit at larger memory distances than correct windows** —
   positive rank-concordance for `d_short`/`d_long` on incorrect vs correct.
   *Falsifiable: concordance ≈ 0.5 or below.*
2. **FP will be more distinctive than FN.** A false positive is an atypical
   window scored high; a false negative may be perfectly typical.
3. **Stream AUROC will correlate negatively with upper-tail `d_long`** — worse
   streams sit further from their own prototypes. *This is the core mechanism
   claim of E8a and the one most likely to fail.*
4. **Admission fraction will not track stream quality.** M2-G was built for
   contamination control, not quality detection, and expecting otherwise would
   be reading it as a classifier.
5. **Effects will be heterogeneous across subjects**, as in E7a and E7b.

---

## 5. Decision rules, registered before results

| Outcome | Recommendation |
|---|---|
| Memory quantities identify unreliable windows **and** streams with credible, non-concentrated effects | **(1)** Proceed to a preregistered RQ1 M1L/M2-G ON-vs-OFF episode ablation |
| Only one of M1 (distances) or M2 (admission) shows mechanism evidence | **(2)** Separate the M1 and M2 questions |
| Neither identifies the observed quality failures | **(3)** Close the memory mechanism branch; recommend representation-learning investigation |

**Concentration test, as in E7b:** if the majority of an effect is contributed by
two or fewer of the nine evaluable subjects, it is reported as heterogeneous and
does not by itself support recommendation (1).

**Bounds.** Mechanism evidence only. Development validation only. 9 of 12
subjects evaluable. No generalization claim is available, permanently.
