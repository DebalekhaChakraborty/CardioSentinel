# B4 · E7b Cross-Stream Offset Mechanism Analysis — Report, V1

Executed under `B4_E7B_CROSS_STREAM_OFFSET_PLAN_V1.md`. **Development validation
only. Read-only: no retraining, no sealed artifact, no threshold tuning, no
validation-driven transformation selection.** **Mechanism evidence only.**

**Headline: the cross-stream offset mechanism is NOT supported.** Cross-stream
discrimination is not consistently worse than within-stream, the stream oracle
does not repair it, and the across-stream variation is **discriminative quality,
not location/scale shift**. Both registered interpretation rules point the same
way: **close score-normalization personalization.**

---

## 1. Correctness gate — PASSED exactly

`max |ΔAUROC_within|` between R0 and S-oracle, across all evaluable subjects:
**`0.0`**.

**Exactly zero.** The per-stream monotone map left every within-stream pair
ordering untouched, so **every change in subject-level AUROC is attributable to
cross-stream pairs by construction, not by inference.** Objective 4 is answered
algebraically.

## 2. Ordering precondition

All 30 streams have strictly increasing `start_sample` after **numeric** parse.

> **0 of 30 streams were already in chronological order in the array.**

Every stream is stored lexicographically. **A causal replay trusting array order
would process all thirty streams out of sequence** — and would return plausible
numbers. E7b's analysis is order-free so nothing here depends on it, but the
precondition is now measured rather than assumed for any successor.

---

## 3. Primary decomposition

| subject | prev | streams | cross-pair share | AUROC within | AUROC cross | gap | cross under S-oracle | Δ cross |
|---|---|---|---|---|---|---|---|---|
| s2004 | 0.1978 | 2 | 0.502 | 0.8300 | 0.8200 | +0.0100 | 0.8108 | −0.0092 |
| s3068 | 0.1955 | 3 | 0.668 | 0.9784 | 0.9799 | −0.0016 | 0.9636 | −0.0163 |
| s2059 | 0.0381 | 2 | 0.520 | 0.9025 | 0.7766 | **+0.1259** | 0.8779 | **+0.1013** |
| s2031 | 0.0272 | 2 | 0.496 | 0.6450 | 0.6562 | −0.0112 | 0.5079 | **−0.1483** |
| s3073 | 0.0235 | 6 | 0.834 | 0.9594 | 0.9665 | −0.0071 | 0.9474 | −0.0191 |
| s2057 | 0.0137 | 2 | 0.512 | 0.8657 | 0.9998 | **−0.1340** | 0.8716 | −0.1282 |
| s2019 | 0.0040 | 2 | 0.500 | 0.5026 | 0.4938 | +0.0088 | 0.4899 | −0.0039 |
| s2058 | 0.0031 | 2 | 0.500 | 0.9908 | 0.9915 | −0.0007 | 0.9910 | −0.0005 |
| s3072 | 0.0009 | 3 | 0.666 | 0.8911 | 0.8869 | +0.0042 | 0.8899 | +0.0029 |

**Cross-stream worse than within-stream in only 4 of 9 subjects** — not a
majority. For five subjects cross-stream concordance is *better*, and for
`s2057` it is **0.9998 against a within-stream 0.8657**: cross-stream ordering is
essentially perfect while within-stream ordering is not.

**The stream oracle repairs ≥50% of the gap in 2 of 9 subjects** — the
pre-registered "materially repairs" bar, not met. It **lowers** cross-stream
concordance in 7 of 9, twice by more than 0.12.

**Both conjuncts of interpretation rule 1 fail.**

---

## 4. The registered discriminator — signature (b), not (a)

| Statistic across streams | Value |
|---|---|
| SD of **mean negative score** (location) | **0.1573** |
| SD of **separation** (`mean_pos − mean_neg`) | **0.2938** |
| SD of **stream AUROC** (quality) | **0.2051** |

Signature (a) — a common location/scale shift — required **large location SD
with small separation and AUROC SD**. The observed ordering is the **opposite**:
separation varies most, quality next, location least.

> **This is signature (b): streams differ in discriminative quality, not in
> offset.** No monotone per-stream transform can repair that.

**The extremes make it concrete.** Across the 19 streams carrying both classes,
AUROC ranges **0.2119 to 0.9948**:

| stream | subject | windows | prev | neg mean | pos mean | separation | AUROC |
|---|---|---|---|---|---|---|---|
| `s20311:1` | s2031 | 14,573 | 0.0255 | 0.5941 | 0.2777 | **−0.3163** | **0.2119** |
| `s20191:0` | s2019 | 17,269 | 0.0041 | 0.0311 | 0.0200 | −0.0111 | 0.4822 |
| `s30681:1` | s3068 | 17,008 | 0.1628 | 0.0233 | 0.7835 | +0.7602 | 0.9926 |
| `s20581:0` | s2058 | 15,812 | 0.0040 | 0.0021 | 0.6554 | +0.6532 | **0.9948** |

**`s20311:1` is anti-correlated: its positives score *lower* than its
negatives.** That is a sign error, not a scale error. Z-normalizing a stream
cannot flip a sign, which is precisely why `s2031` is the subject the oracle
damages most (Δ cross −0.1483). **Eleven of thirty streams carry no positives at
all.**

---

## 5. Heterogeneity — concentrated, and mostly cancellation

| subject | AUPRC R0 | AUPRC S | Δ AUPRC | AUROC R0 | AUROC S | Δ AUROC |
|---|---|---|---|---|---|---|
| s2031 | 0.0428 | 0.3270 | **+0.2842** | 0.6505 | 0.5770 | **−0.0736** |
| s2059 | 0.1326 | 0.3523 | **+0.2197** | 0.8371 | 0.8897 | +0.0526 |
| s3073 | 0.7941 | 0.6119 | **−0.1822** | 0.9654 | 0.9494 | −0.0159 |
| s2057 | 0.2616 | 0.1059 | **−0.1557** | 0.9343 | 0.8687 | −0.0656 |
| s2058 | 0.8373 | 0.8177 | −0.0195 | 0.9912 | 0.9909 | −0.0002 |
| s3068 | 0.9432 | 0.9377 | −0.0055 | 0.9794 | 0.9685 | −0.0109 |
| s2019 | 0.0073 | 0.0043 | −0.0029 | 0.4982 | 0.4962 | −0.0019 |
| s3072 | 0.0069 | 0.0081 | +0.0013 | 0.8883 | 0.8903 | +0.0020 |
| s2004 | 0.5800 | 0.5792 | −0.0008 | 0.8249 | 0.8203 | −0.0046 |

**Total absolute change 0.8719; the top two subjects contribute 0.5039 —
57.8%.** The registered concentration criterion (majority from ≤2 subjects) is
**met**, so **interpretation rule 3 binds: report heterogeneity and do not
recommend a universal correction.**

**The net `+0.015387` is the residue of four changes between 0.156 and 0.284
that very nearly cancel.** `s2031` alone moves AUPRC by +0.2842 — a sevenfold
rise from 0.0428 — **while its AUROC falls by 0.0736.**

### 5.1 E7a's exploratory `+0.0154` does not survive

The plan forbade treating it as established, and it does not hold up. **Macro
AUROC moves the other way: `0.841039 → 0.827903`, a change of `−0.013136`.**
The same transform improves the macro AUPRC and degrades the macro AUROC. There
is no consistent improvement to attribute to cross-stream correction.

### 5.2 Secondary endpoints

| | R0 | S-oracle |
|---|---|---|
| pooled AUPRC | 0.380535 | 0.333518 |
| pooled AUROC | 0.892762 | 0.820225 |
| subject-macro AUPRC (9/12) | 0.400636 | 0.416023 |
| subject-macro AUROC (9/12) | 0.841039 | 0.827903 |

---

## 6. Registered predictions

| # | Prediction | Outcome |
|---|---|---|
| 1 | `AUROC_within` identical to `< 1e-9` | **Confirmed** — exactly `0.0` |
| 2 | `AUROC_cross < AUROC_within` for a majority | **REFUTED** — 4 of 9 |
| 3 | S-oracle raises `AUROC_cross` | **REFUTED** — lowers it in 7 of 9 |
| 4 | Effects heterogeneous | **Confirmed** — 57.8% from two subjects |
| 5 | Pooled AUPRC falls | **Confirmed** — 0.380535 → 0.333518 |

---

## 7. Decision

**Interpretation rule 1 does not fire** — neither conjunct holds. **Rule 3 fires
independently.** **E7c is not recommended.** A causal approximation of a
transform that lowers cross-stream concordance in seven of nine subjects, and
whose net effect is cancellation among two outliers, would be approximating
something that does not work.

> **Score-normalization personalization is closed.** E7a closed the static
> subject-wise form; E7b closes the static stream-wise form. **The limiting
> factor on this cohort is not score scale — it is that streams differ in
> discriminative quality**, including one stream that is worse than chance.

**Recommended next: the representation-space M1L/M2-G memory ablation.** Per
E7a's boundary 1, representation-space and time-varying personalization are
untouched by anything E7a or E7b did — they are strictly larger classes acting
on objects these experiments never manipulated. M1L's memory features
(`d_short`, `d_long`, `prototype_disagreement`) and M2-G's 21.84% admission rate
are already materialised on disk, so that ablation is also read-only.

**A prior that should bind its design.** `s20311:1`'s AUROC of 0.2119 and the
19-stream AUROC SD of 0.2051 say the variation is in *quality*. An ablation
should therefore ask whether memory features **identify** low-quality streams —
not whether they rescale them.

---

## 8. Bounds

- **Mechanism evidence only.** Not development performance, not generalization.
- **9 of 12 subjects evaluable**; `s2005`, `s2020`, `s2023` carry no positives.
- **Twelve subjects.** E6a applies; no contrast here is bootstrapped and none
  should be read as resolved.
- **S-oracle is non-causal** and was never deployable; it is a ceiling for
  static stream-wise correction only.
- The sealed test is consumed. **No result here bears on it.**
