# B4 · E7a Non-Causal Score-Scale Mechanism Probe — Preregistered Plan, V1

**Pre-registration. No arm has been computed.** Everything below derives from
artifact structure and from values already published in
`B4_E1_REPRESENTATION_PROBE_REPORT_V1.md` and `VALIDATION_METRICS.json`.

**No retraining. No sealed artifact. No threshold optimization. No selection
among oracles.** E7a applies fixed transforms to a frozen score column and
measures geometry.

| | |
|---|---|
| Partition | development **validation** only — 473,897 rows, 12 subjects, 30 streams |
| Arms | **R0** raw · **P1** subject-wise z · **P2** subject-wise ECDF *(amendment 1)* |
| Authorization | none required, none requested |
| Evidence class | **mechanism evidence only** — see §2 |

---

## 0. Correction to `B4_E7_PERSONALIZATION_AUDIT_V1.md` §10, H5

**The audit over-claimed and the claim is withdrawn here, before it could
influence a design.** H5 read: *"P-oracle bounds P-causal and P-gated. If
P-oracle's pooling penalty reduction is small, the mechanism is not the limiting
factor and no causal variant can rescue it."*

**That is false.** A static per-subject transform preserves within-subject
ranking; a time-varying one does not. Time-varying transforms are a **strictly
larger class** — they can reorder windows within a stream, which no static
transform can. A static oracle therefore **cannot** upper-bound a time-varying
personalizer, and it cannot bound representation-space adaptation either, which
does not act on the score at all.

**Corrected scope, and it is interpretation boundary 1:**

> **P1 and P2 are a ceiling and reference for *static, subject-wise score
> normalization only*.** They do **not** upper-bound M1L/M2-G
> representation-space personalization, and they do **not** upper-bound
> time-varying score personalization. A null E7a result closes exactly one
> mechanism and leaves those two open.

---

## 1. Arms

| Arm | Transform | Registered property |
|---|---|---|
| **R0** | frozen raw B4-B score `s` | reference |
| **P1** | `z_i = (s − μ_i) / σ_i`, with `μ_i`, `σ_i` the mean and SD of `s` over **all rows of subject `i`** | strictly increasing affine per subject |
| **P2** | `p_i = ECDF_i(s)`, the within-subject percentile rank | non-decreasing per subject |

**Both are non-causal and label-free.** They use every row of a subject
including future ones — which is why they are a mechanism ceiling and **not
deployable** — and they never touch a label.

**Amendment 1, made before execution.** P2 is added at the reviewer's explicit
instruction as a pre-execution amendment. It is included **because rank
normalization removes distributional shape as well as location and scale**,
which P1 cannot; the two answer different questions and both are reported.

**No oracle is selected.** P1 and P2 are both reported in full whatever they
show. Neither is promoted, dropped, or described as "the" oracle.

**Registered constants.** `σ_i` uses the population SD (`ddof=0`). A subject
with `σ_i = 0` is left untransformed and reported. P2 uses `scipy`-free average
ranking with ties resolved by mean rank, mapped to `(rank − 0.5)/n_i`. Nothing
here is tuned and there is no grid.

### 1.1 Normalization unit — subject primary, stream secondary

The hypothesis concerns **cross-subject** transfer, so the **subject** is the
primary unit. The **stream** (`record_id`, `channel_index`) is reported as a
registered secondary because it is the only unit a deployable mechanism could
use: **M1 resets memory at every recording boundary**, so a per-subject
normalizer is *not implementable* under the current stream scope. The
subject-level result is therefore a ceiling above a ceiling, and §5 says so.

Validation holds **30 streams across 12 subjects** — nine subjects with two
streams, two with three, one with six.

---

## 2. Interpretation boundaries — binding on the report

**Boundary 1 — scope of the ceiling.** §0 above.

**Boundary 2 — a null result here refutes nothing about the sealed finding.**
Development validation exhibits only a **small pooling gap**: pooled AUPRC
`0.380535` against subject-macro `0.400636`, a gap of **`+0.020101`**. **There
is very little for a score-scale correction to recover on this cohort.** E7a
therefore characterises the mechanism **on development data only**, and **cannot
refute the post-hoc sealed cross-subject-scale hypothesis** — that hypothesis
concerns a partition E7a is forbidden to touch and which is permanently
consumed. A null E7a is evidence about this cohort's geometry, nothing more.

**Boundary 3 — within-subject ranking must be preserved exactly.** P1 and P2 are
monotone within subject by construction, so **per-subject AUROC and per-subject
AUPRC must be numerically unchanged from R0**. This is asserted, not assumed:

> For every contributing subject, `|AUROC_arm − AUROC_R0| < 1e-9` and
> `|AUPRC_arm − AUPRC_R0| < 1e-9`. **A violation means the implementation is
> wrong, and E7a stops.**

This is a correctness gate of the same shape as E3's monotone-invariance check,
which held at exactly `0.0`.

**Boundary 4 — evidence class.** Mechanism evidence. **Not** development
performance, **not** generalization. No sentence may say "improves detection".
Permitted phrasing: *"reduces between-subject dispersion"*, *"narrows the
pooling gap"*.

---

## 3. Endpoints

| # | Endpoint | Definition |
|---|---|---|
| 1 | Pooled AUPRC, AUROC | over all 473,897 rows |
| 2 | Subject-macro AUPRC, AUROC | mean over contributing subjects, **denominator printed** |
| 3 | **Pooling gap** | `subject_macro − pooled`, per metric |
| 4 | Location dispersion | SD across subjects of the per-subject **median** score |
| 5 | Scale dispersion | SD across subjects of the per-subject **IQR** |
| 6 | Within-subject ranking invariance | boundary 3's assertion, reported per subject |
| 7 | **Cross-subject interleaving** | SD across subjects of the subject's **mean global percentile rank**, plus its range. Perfect interleaving → every subject's mean rank ≈ 0.5 → SD ≈ 0 |

**Denominator, fixed in advance.** Three of twelve subjects — `s2005`, `s2020`,
`s2023` — carry **zero positive windows**, so per-subject AUPRC and AUROC are
undefined for them. **Every subject-macro figure is over 9 of 12** and is
printed that way. Per-subject prevalence spans `0.00000` to `0.19784` and is
reported beside every per-subject metric, per E6a's finding that AUPRC width
tracks prevalence at `r ≈ +0.5…+0.8`.

**Uncertainty.** Paired subject bootstrap, 1,000 replicates, seed 2026, on the
pooled contrasts `P1 − R0` and `P2 − R0`. **E6a applies: 12 units, and the
intervals will be wide.** They are reported as instrument limits, never as
equivalence.

---

## 4. Registered predictions

1. **Per-subject AUROC and AUPRC will be identical to R0 to `< 1e-9`** for both
   arms, all 9 contributing subjects. *(Correctness gate.)*
2. **Location and scale dispersion will fall sharply** under both arms — P1 sets
   every subject's mean to 0 and SD to 1 by construction, so its *mean/SD*
   dispersion is zero identically; the informative figures are **median** and
   **IQR** dispersion, which are not forced to zero.
3. **Interleaving dispersion will fall** under both arms.
4. **Pooled AUPRC will move by less than the pooling gap of `0.020101`**, simply
   because that gap bounds what closing it can recover on this cohort.
5. **P2 will change pooled ranking more than P1**, because rank normalization
   discards distributional shape that an affine map preserves.

**Prediction 4 is the one that makes E7a nearly uninformative in the positive
direction on this cohort, and it is registered before the run rather than
offered afterwards as an excuse.**

---

## 5. Decision rules, registered before results

| Outcome | What follows |
|---|---|
| **P1 or P2 materially alters pooled ranking** | **Stop after reporting.** Design the causal approximation as a separate pre-registered experiment. Do not implement anything in this one |
| **Neither materially alters pooled ranking** | **Do not implement a score-normalization personalization mechanism.** Recommend the next mechanistic question instead — and note that boundary 1 leaves representation-space and time-varying personalization untouched by this result |
| Invariance assertion fails | **Stop.** Implementation error; no result is interpretable |

**In no branch does E7a justify retraining, a sealed-test access, or a new
authorization.**
