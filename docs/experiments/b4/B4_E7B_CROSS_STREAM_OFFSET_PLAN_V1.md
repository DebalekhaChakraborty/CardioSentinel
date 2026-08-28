# B4 · E7b Cross-Stream Offset Mechanism Analysis — Preregistered Plan, V1

**Pre-registration. No decomposition has been computed.** Derived from artifact
structure and from values already published in `B4_E1_…REPORT_V1.md` and
`B4_E7A_…REPORT_V1.md`.

**Read-only. No retraining, no sealed artifact, no threshold tuning, no
validation-driven transformation selection.** The only transform used is the
stream oracle already defined and executed in E7a; **nothing is chosen here on
the basis of a validation outcome.**

| | |
|---|---|
| Question | Within a patient, are B4 ranking errors materially attributable to **score-scale differences between streams** rather than within-stream discrimination? |
| Partition | development validation — 473,897 rows, 12 subjects, **30 streams**, 9 evaluable |
| Stream identity | **`(record_id, channel_index)`** — exactly M1L's memory scope |
| Evidence class | **mechanism evidence only.** Not generalization |

---

## 1. The decomposition, and why it isolates the mechanism exactly

AUROC is concordance over positive–negative pairs. Within one subject, every
such pair is **either** within-stream **or** cross-stream, and the two sets are
disjoint and exhaustive. Concordance counts are therefore additive:

```
C_total  = AUROC_subject x P_total          P_total = n_pos * n_neg
C_within = SUM_s AUROC_s x P_s              P_s     = n_pos_s * n_neg_s
C_cross  = C_total - C_within               P_cross = P_total - P_within

AUROC_within = C_within / P_within      AUROC_cross = C_cross / P_cross
```

Ties receive 0.5 credit throughout, consistently with `roc_auc_score`. Streams
with no positive or no negative contribute `P_s = 0` and are excluded from the
within-stream term only.

### 1.1 The registered invariance that makes attribution provable

**A per-stream monotone transform cannot change any within-stream pair's
ordering.** Therefore:

> **`AUROC_within` must be numerically identical between R0 and the stream
> oracle, for every evaluable subject and every stream.** Any change in
> subject-level AUROC is then attributable **entirely and by construction** to
> cross-stream pairs.

**This is a correctness gate.** Tolerance `< 1e-9`. **If it fails, the
implementation is wrong and E7b stops.** It is also the direct answer to
objective 4: attribution here is not inferred from a correlation, it is forced
by the algebra.

---

## 2. Arms

| Arm | Definition |
|---|---|
| **R0** | frozen raw B4-B validation score |
| **S-oracle** | per-`(record_id, channel_index)` whole-stream z-normalization, `z = (s - mu_stream)/sigma_stream`, `ddof=0` |

**S-oracle is non-causal, label-free, and was defined and executed in E7a as
`P1_stream`.** It is reused unchanged. **No alternative normalization is tried,
compared, or selected** — that would be validation-driven transformation
selection, which the constraints forbid.

**It is not deployable.** It uses each stream's whole history including future
windows. It is a mechanism ceiling for *static within-subject cross-stream
correction*, and — per E7a's boundary 1 — it bounds neither time-varying nor
representation-space personalization.

---

## 3. Ordering precondition

`stable_id` encodes `dataset:record:channel:start_sample:end_sample`. The array
is sorted **lexicographically, not chronologically** (`0`, `10000000`,
`1000000`). E7b therefore parses `start_sample` **numerically** and asserts
strict chronological ordering within each stream.

**Stated honestly: E7b's primary analysis is order-free.** Pair concordance and
stream statistics do not depend on window order. The parse and assertion are run
anyway, as a **precondition check for any successor experiment that would need
causal ordering**, and because a silent lexicographic-order assumption is
exactly the defect class this programme keeps finding. Its result is reported;
it gates nothing in E7b.

---

## 4. Descriptive per-stream table

For each of the 30 streams: window count, prevalence, mean and median negative
score, mean and median positive score, score spread (SD and IQR), and AUROC /
AUPRC where defined — with **"where defined" made explicit**, since a stream
with no positives supports neither.

### 4.1 Registered discriminator between the two explanations

| Signature | Reading |
|---|---|
| Across-stream SD of **mean negative score** large, while SD of **separation** (`mean_pos - mean_neg`) and SD of **stream AUROC** are small | **(a) common location/scale shift** affecting both classes — the offset hypothesis |
| Across-stream SD of **stream AUROC** large | **(b) differences in discriminative quality** — not an offset problem, and not repairable by any monotone per-stream map |

Both statistics are reported regardless of which is larger. **No composite score
is formed across them.**

---

## 5. Secondary endpoints

Subject-macro AUPRC and AUROC (denominator printed), pooled AUPRC and AUROC, and
**per-subject** change from R0 to S-oracle.

**E7a's `+0.0154` subject-macro AUPRC observation is explicitly NOT treated as
established.** It was unbootstrapped, rested on nine subjects, and is carried
here only as the exploratory observation that motivated E7b. **E7b may not cite
it as support for anything.**

---

## 6. Heterogeneity

Per-subject results are reported individually, never only as a mean. Registered
in advance: **if the change from R0 to S-oracle is concentrated in a small
number of subjects — operationally, if the majority of the total absolute
subject-macro change is contributed by two or fewer of the nine evaluable
subjects — E7b reports heterogeneity and must NOT recommend a universal
correction.**

---

## 7. Registered predictions

1. **`AUROC_within` identical between arms to `< 1e-9`** for every subject.
   *(Gate.)*
2. Under R0, **`AUROC_cross < AUROC_within`** for a majority of evaluable
   subjects — the offset hypothesis. *Falsifiable: cross >= within.*
3. S-oracle **raises `AUROC_cross`**, and by construction changes nothing else.
4. **Effects will be heterogeneous.** Prevalence spans `0.00000`–`0.19784` and
   stream counts span 2–6, so a uniform effect would be surprising.
5. **Pooled AUPRC will fall** under S-oracle, as it did in E7a
   (`0.380535 -> 0.333518`), because the pooled metric rewards between-subject
   level that any normalization removes. **This is expected and is not evidence
   against the mechanism** — pooled is not the deployment-relevant statistic.

---

## 8. Interpretation rules, registered before results

| Outcome | Recommendation |
|---|---|
| `AUROC_cross` consistently **below** `AUROC_within` **and** S-oracle materially repairs the cross component | **Recommend E7c**, a preregistered **causal** stream-baseline approximation |
| Mechanism not supported | **Close score-normalization personalization.** Recommend the **representation-space M1L/M2-G memory ablation** instead |
| Effects concentrated in <= 2 subjects | **Report heterogeneity. Do not recommend a universal correction**, whatever the mean says |

**"Materially repairs" is defined before execution** as: the S-oracle increase in
`AUROC_cross` recovers **at least half** of the R0 gap `AUROC_within -
AUROC_cross`, in a majority of evaluable subjects. **No threshold is tuned and
this number is not revisited after results.**

---

## 9. Bounds

- **Mechanism evidence only.** Not development performance, not generalization.
- **Nine of twelve subjects are evaluable**; `s2005`, `s2020`, `s2023` carry no
  positive window. Every macro figure prints its denominator.
- **Twelve subjects.** E6a applies: this cohort cannot resolve small contrasts,
  and any interval reported will be wide.
- The sealed test is consumed; no held-out estimate is obtainable within LTSTDB,
  permanently.
