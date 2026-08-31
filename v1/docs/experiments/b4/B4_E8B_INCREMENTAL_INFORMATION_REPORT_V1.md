# B4 · E8b Conditional Memory-Information Report, V1

Executed under `B4_E8B_INCREMENTAL_INFORMATION_PLAN_V1.md`. **Read-only. No
retraining, no model loaded, no sealed artifact, no threshold optimized, no
classifier fitted, no score transformed.** **Mechanism evidence only.**

**Headline: M1 information largely survives conditioning on the B4 score.**
Pooled `d_long` concordance falls from **0.8362** unconditional to **0.7119**
score-stratified — a real drop, but nowhere near 0.5. The effect is **broad**:
7 of 9 evaluable subjects retain stratified concordance ≥ 0.62. **Decision rule
2 fires** — the TRAIN→VALIDATION incremental probe is recommended, with a
caveat in §6 that materially limits what it can show.

---

## 1. Audit outcome

| Objective | Result |
|---|---|
| 1 · TRAIN-side memory features with verified causal provenance | **Yes.** 2,208,431 rows, 132 streams, **132/132 chronological**, `ordered_chronology_sha256 = 99dff218…` **recomputed and matched**. Zero non-finite |
| 2 · Recreatable without retraining or labels | **Not needed for memory features.** The missing piece is the TRAIN B4 score, and it is **exactly recreatable**: `representation.npy`'s 128-d prefix was verified equal to the frozen embedding cache, and `forward = classifier.head(encode(x))` |
| 3 · Row alignment | **Mapped and asserted** — see §1.1 |
| 4 · M2-G kept separate | **Honoured.** `update_admitted` excluded from the primary question; reported once, labelled, in §5 |

### 1.1 Alignment

```
M1 TRAIN     2,208,431 rows / 132 streams   ⊃  B4 sampled TRAIN  374,452 rows / 56 subjects
                                                 prevalence 0.250000, join complete, 0 non-finite
M1 VALIDATION  492,904 rows /  30 streams   ≡  M2-G row evidence (element-wise identical order)
                                            ⊃  B4 VALIDATION     473,897 rows / 12 subjects
```

Both partitions share `α_short = 0.011485979647`, `α_long = 0.000962241166`,
encoder `b1301723…`, standardizer `f3b640ad…`.

---

## 2. A · Within-stratum label contrast

Preregistered fixed strata; the frozen threshold `0.7554003000259399` is a bin
edge. Concordance of `d_long` separating positives from negatives:

| B4 score stratum | n | positives | concordance | error types possible |
|---|---|---|---|---|
| [0, 1e-4) | 43,028 | **8** | 0.9732 | FN / TN |
| [1e-4, 1e-3) | 120,232 | 255 | 0.8320 | FN / TN |
| [1e-3, 0.01) | 131,551 | 1,352 | 0.6567 | FN / TN |
| [0.01, 0.05) | 68,370 | 2,007 | **0.6368** | FN / TN |
| [0.05, 0.10) | 22,725 | 1,174 | 0.6431 | FN / TN |
| [0.10, 0.25) | 25,443 | 2,172 | 0.6744 | FN / TN |
| [0.25, 0.50) | 18,233 | 2,288 | 0.7383 | FN / TN |
| [0.50, 0.7554) | 14,969 | 2,408 | 0.7799 | FN / TN |
| **[0.7554, 0.90)** | 11,599 | 2,448 | **0.8181** | **TP / FP** |
| **[0.90, 1.0]** | 17,747 | 7,516 | **0.8968** | **TP / FP** |

**The relationship is U-shaped, and registered prediction 5 is refuted.** I
predicted the highest strata would carry the *least* conditional information;
they carry the **most**. Information is minimum in the mid-range (~0.64) and
rises at both ends. The lowest bin's 0.9732 rests on **8 positives** and is
reported but carries no weight.

**The operationally interesting cell is the top stratum.** Among the 17,747
windows B4 scores above 0.90, `d_long` separates the 7,516 true positives from
the 10,231 false positives with concordance **0.8968** — **at effectively equal
B4 score.**

## 3. B · Does the relationship survive conditioning?

| quantity | unconditional | score-stratified | drop |
|---|---|---|---|
| **`d_long`** | 0.8362 | **0.7119** | +0.1243 |
| `d_short` | 0.7780 | **0.7392** | +0.0388 |
| `prototype_disagreement` | 0.8328 | **0.7559** | +0.0770 |

**Registered prediction 2 confirmed** — a substantial drop, consistent with
E8a's ρ(score, `d_long`) = +0.727 within positives. **Registered prediction 3
confirmed** — it does not fall to 0.5. **Roughly 70–76% of the concordance
survives conditioning on the score.**

`d_short` drops least, so its information is the most nearly orthogonal to the
score, despite being the weaker signal unconditionally.

## 4. C · Subject-level summaries

| subject | prevalence | uncond | **stratified** | drop | strata with both classes |
|---|---|---|---|---|---|
| s2031 | 0.0272 | 0.9239 | **0.9228** | +0.0011 | 10 |
| s2019 | 0.0040 | 0.8722 | **0.8980** | −0.0258 | 5 |
| s2058 | 0.0031 | 0.9921 | **0.8872** | +0.1049 | 4 |
| s2059 | 0.0381 | 0.8232 | **0.7751** | +0.0481 | 8 |
| s3072 | 0.0009 | 0.8364 | **0.7580** | +0.0784 | 4 |
| s2057 | 0.0137 | 0.8459 | **0.6674** | +0.1785 | 7 |
| s3073 | 0.0235 | 0.8922 | **0.6216** | +0.2706 | 9 |
| s2004 | 0.1978 | 0.6871 | 0.5880 | +0.0991 | 9 |
| s3068 | 0.1955 | 0.8594 | 0.5549 | +0.3046 | 9 |

**Seven of nine subjects retain stratified concordance ≥ 0.62; all nine exceed
0.55.** **The concentration test does not fire** — this is a broad effect, not
two outliers, unlike E7b.

**A pattern worth recording:** the two subjects where conditional information
nearly vanishes — `s3068` (0.5549) and `s2004` (0.5880) — are **the two
high-prevalence subjects** (0.1955, 0.1978). Where disease burden is high, the
score already carries what memory would add. Where it is low, memory adds most.

**`s2031` — the polarity-reversal subject — has the highest stratified
concordance (0.9228) and essentially no drop (+0.0011)**, so for that subject
memory carries information almost entirely independent of the score. That is
consistent with E8a, where s2031 was the one subject whose *error* association
with memory was at chance: memory tracks something real there that the score
does not, and neither identifies the stream defect.

## 5. D · E8a's stream-level negative finding, preserved

**Restated, not re-tested and not softened:** p90 `d_long` vs stream AUROC
ρ = **−0.028**, and the polarity-reversed stream `s20311:1` carries **lower**
distances than its healthy sibling. **Memory distance does not identify stream
discrimination quality.** E8b's window-level result does not overturn this;
they are different questions at different units.

**Secondary, kept separate as registered.** M2-G `update_admitted`:
unconditional concordance **0.3824**, stratified **0.4726** — near-null after
conditioning. Consistent with it being a contamination gate rather than a
label-informative feature. **It embeds G3 SQI and G6 morphology and is excluded
from the primary M1 conclusion.**

---

## 6. Decision — rule 2, with a caveat that constrains it

**Rule 1 does not fire** (relationships did not largely disappear). **Rule 3
does not fire** (not concentrated). **Rule 2 fires: recommend the preregistered
TRAIN→VALIDATION incremental probe.**

### 6.1 The caveat, stated before the probe is written

**Conditional association is not incremental predictive value.** A stratified
concordance of 0.71 shows `d_long` separates labels at fixed score; it does not
show a fitted model gains from it, because the two features are strongly
coupled (ρ = 0.727 within positives).

**And the instrument cannot resolve the performance difference.** E8a's
already-persisted ON/OFF comparison gives **M1L − P1B = +0.009548 pooled
AUPRC**, against E6a's measured interval widths of ~0.11–0.16 at n = 12.
**Any probe's validation contrast will almost certainly include zero.**

**Therefore the probe is justified as a mechanism test and must be
preregistered as one** — with its expected non-resolution stated in advance, so
a wide interval is reported as an instrument limit and not as refutation. **A
probe framed as a performance test would be a probe designed to fail.**

### 6.2 Proposed arms — NOT executed

| Arm | Features |
|---|---|
| **C0** | frozen B4 scalar score |
| **C1** | B4 score + `d_short` + `d_long` + `prototype_disagreement` |

Fixed-capacity classifier, **trained only on the 374,452-row sampled TRAIN set**
(matching B4's own training distribution), **evaluated once on VALIDATION**, all
hyperparameters fixed in advance, **no validation selection**. TRAIN B4 scores
produced by the §1 head-only reproduction, its identity checked against the
published validation figure first. **`update_admitted` is excluded** — it would
import SQI and morphology gate information and answer a different question.

---

## 7. E9 evidence audit — read-only, not implemented

**Substantial material exists, and one gap closes unexpectedly.**

| Axis | Status |
|---|---|
| **SQI** | **10 quality features** in `combined_v1`; M2-G's G3 uses 6 with train-only Q99 bounds and **explicitly excludes** `robust_amplitude_range_mv` and `robust_derivative_scale_mv_per_s` as legitimately patient-varying |
| **Morphology direction / polarity** | **8 signed features** — `post_r_{80,120,160,200}ms_delta_mv`, `post_r_80_160_slope_mv_per_s`, `post_r_80_200_area_mv_s`, `pre_r_baseline_median_mv`, `qrs_proxy_peak_to_peak_mv`. **Signed, so ST direction is directly testable** |
| **Beat / template** | 9 features including `morphology_valid`, `usable_beat_count`, RR statistics, `beat_template_correlation_median` |
| **Preprocessing metadata** | `processing_profile: raw`, 10 s / 5 s, `generation_command`, `git_sha`, per-record `morphology_quality` |
| **Channel identity** | `channel_index` per row |
| **Lead identity** | **`lead_names` in the feature corpus is degenerate** — a single constant `'ECG'`. **But the WFDB `.hea` headers retain true lead names**, and they are heterogeneous |

### 7.1 The finding that should shape E9

Reading the development-partition headers only, lead assignments vary widely —
`MLIII/V3`, `MLIII/V4`, `V5/MLIII`, `V5/V2`, `V2/MLIII`, `V6/II/V5`, and EASI
`E-S/A-S/A-I` for `s3072`/`s3073`.

**And `s20311.hea` — the record E7b flagged — documents the defect in the
dataset's own words:**

> *"Lead 0 shows numerous ST-elevations. These are mirrored in lead 1 by slight
> decrease in baseline ST elevation."*

`s20311:1` is **V3**. E7b measured that stream at AUROC **0.2119** with
separation **−0.3163** — positives scoring *below* negatives. **The source
header describes exactly that inversion.** The stream-quality failure that
resisted score normalization (E7b) and memory distance (E8a) appears to be
**lead-dependent ST polarity**, and it is annotated at source.

**E9 is therefore well-founded and cheap**: lead identity is recoverable from
headers, signed ST-direction features already exist per window, and the failure
case has a documented ground truth. **It is not implemented here.**

---

## 8. Bounds

- **Mechanism evidence only.** Not development performance, not generalization.
- **9 of 12 subjects evaluable**; `s2005`, `s2020`, `s2023` carry no positives.
- The `[0, 1e-4)` stratum rests on **8 positives** and carries no weight.
- **No contrast in this report is bootstrapped.** E6a applies throughout.
- **Only development-partition headers were read.** No sealed-test record was
  opened, and no waveform data was read at all.
- The sealed test is consumed; no held-out estimate is obtainable, permanently.
