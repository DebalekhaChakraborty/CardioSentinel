# B4 · E6a Instrument Precision Analysis — Report, V1

**Instrument characterisation only.** No training, no checkpoint loaded, no
sealed artifact opened, nothing written into any run directory. Inputs are
`validation_predictions.npz` (read-only) and E1's derived probe scores.

**This report predicts nothing about E6 and says nothing about B4.** It measures
how the width of a subject-bootstrap interval responds to the number of
subjects, on fixed scores.

**Headline, and it is negative for the experiment it was built to gate:**
**E6a cannot determine whether more subjects would resolve E1/E2's ambiguities.**
Two independent artefacts dominate the measurement in the range available.
What it *does* establish is that the naive `1/√n` assumption has **no empirical
support here**, and §6 of `B4_E6_FEASIBILITY_AUDIT_V1.md` — which projected four
of five contrasts resolving at n=68 — **is withdrawn.**

---

## 1. Methodology

For each `n ∈ {4, 6, 8, 10, 12}`, eight random subsets of the twelve validation
subjects (seed 2026; `n=12` admits one subset). Within each subset, a paired
subject bootstrap resampling those `n` subjects with replacement, 400
replicates. The measured quantity is **interval width**, `p97.5 − p2.5`.

Three contrasts spanning E1's range: **A2−A1** (0.161 at n=12), **A5−A2**
(0.110, tightest), **A4−A2** (0.649, widest).

**Run twice, under two metrics**, and the second run is the control:

| Metric | Property |
|---|---|
| Pooled AUPRC | E1's primary metric — **bounded below by prevalence** |
| AUROC | **prevalence-independent** — isolates unit count from class balance |

### 1.1 The replicate count was reduced, and the reduction was checked

400 replicates rather than the programme's 1,000, as a compute parameter for an
instrument analysis rather than a protocol constant for a result. **Checked
rather than asserted**: at n=12 with 1,000 replicates this analysis reproduces
E1's published widths.

| Contrast | E6a @1000 | E1 published | Difference |
|---|---|---|---|
| A2−A1 | 0.1642 | 0.161158 | 0.0030 |
| A5−A2 | 0.1100 | 0.109522 | 0.0005 |
| A4−A2 | 0.6237 | 0.648921 | 0.0252 |

The residual is expected: E6a draws with `numpy.default_rng`, E1 with
`subject_bootstrap_plan`, so the resamples differ. **400-replicate widths run
~5–8% narrower**, roughly uniformly across `n`, so the scaling fits are not
materially distorted by the reduction.

---

## 2. Results

### 2.1 Pooled AUPRC — width *increases* with subject count

| n | A2−A1 | A5−A2 | A4−A2 |
|---|---|---|---|
| 4 | 0.0711 | 0.0654 | 0.4547 |
| 6 | 0.1234 | 0.1000 | 0.4895 |
| 8 | 0.1516 | 0.0812 | 0.4819 |
| 10 | 0.1597 | 0.1060 | 0.5716 |
| 12 | 0.1495 | 0.1071 | 0.6126 |

**Fitted exponents `+0.697`, `+0.397`, `+0.262`.** Naive `1/√n` is `−0.500`.

### 2.2 AUROC — width is approximately flat

| n | A2−A1 | A5−A2 | A4−A2 |
|---|---|---|---|
| 4 | 0.0316 | 0.0354 | 0.2474 |
| 6 | 0.0431 | 0.0427 | 0.2834 |
| 8 | 0.0540 | 0.0387 | 0.2878 |
| 10 | 0.0468 | 0.0348 | 0.2756 |
| 12 | 0.0436 | 0.0337 | 0.2674 |

| Contrast | Exponent, n=4–12 | Exponent, n=6–12 | AUPRC exponent |
|---|---|---|---|
| A2−A1 | +0.317 | −0.017 | +0.697 |
| A5−A2 | −0.084 | −0.357 | +0.397 |
| A4−A2 | +0.066 | −0.089 | +0.262 |

**Nothing approaches `−0.500`.** Excluding the smallest and least reliable
point, the three exponents average about **−0.15** against a naive **−0.50**.

### 2.3 The prevalence confound, measured

Correlation of interval width with subset prevalence, within each `n`:

| Contrast | AUPRC (mean) | AUROC (mean) |
|---|---|---|
| A2−A1 | **+0.794** | +0.275 |
| A5−A2 | **+0.555** | −0.099 |
| A4−A2 | **+0.485** | +0.393 |

**Subsets of four subjects span prevalence `[0.0076, 0.1213]` — a 16× range.**
AUPRC is bounded below by prevalence, so low-prevalence subsets compress the
metric's scale and mechanically produce narrow intervals. **Most of §2.1's
positive exponent is that artefact**, and switching to AUROC removes most of it.

---

## 3. Why this still cannot answer the question

Two artefacts remain, and both act in the range measured.

### 3.1 Subsetting removes heterogeneity as well as units

Bootstrap width scales roughly as `σ/√n`, where `σ` is between-subject
variability. **Subsampling reduces `n` and, by removing subjects, also narrows
the diversity `σ` is computed over.** The two effects act in opposite directions
on width and partially cancel — which is precisely what a flat curve looks like.

**Enlarging a cohort is not the inverse of this operation.** Going 12 → 68 adds
units *and* may add heterogeneity. So this measurement understates the shrinkage
that adding subjects would produce, and its flat exponent is best read as a
**lower bound** on the benefit, not an estimate of it.

### 3.2 The bootstrap is unreliable at the small end

At `n=4` the bootstrap resamples four units with replacement, so the resample
distribution is coarse and its tails are under-populated. **Percentile intervals
from very few units are known to be too narrow**, and n=4 is the narrowest point
in five of six curves here. That is consistent with small-sample bootstrap
failure rather than with a real precision gain.

**Consequence:** the usable range is roughly `n=6…12` — a two-fold span, from
which an exponent is being extrapolated **six-fold** out to 68. That
extrapolation is not supportable whatever the fitted value.

---

## 4. What this does establish

1. **The `1/√n` assumption has no empirical support in this cohort.** Neither
   metric, at any fitting range, produces anything near `−0.500`. **§6 of
   `B4_E6_FEASIBILITY_AUDIT_V1.md` is withdrawn** — it presented projected
   intervals as the scientific case for E6, and that projection rested on an
   assumption now contradicted by the only measurement available.
2. **AUPRC width is strongly prevalence-driven** (`r ≈ +0.5 … +0.8`). Any
   future analysis comparing AUPRC across subject sets of differing prevalence —
   including any per-fold reporting in a cross-fitted design — **must report
   prevalence beside every value**, or it will attribute to method what belongs
   to class balance.
3. **A practical instrument caution: do not report a subject bootstrap below
   roughly eight subjects.** Below that, widths here are anomalously narrow.
   **E1's subject-macro AUPRC is computed over nine of twelve subjects**, which
   sits near that boundary — a caveat E1's report did not carry and now should.

---

## 5. Interpretation limits

- **This does not predict E6's performance.** E6 retrains per fold, adding
  between-fold model variance absent here. Everything above concerns resampling
  a fixed set of scores.
- **This says nothing about B4.** No claim is made or implied that more subjects
  would improve any model. Interval width is not model quality.
- **This does not show that more subjects would fail to help.** §3.1 explains why
  the measurement is biased against detecting the benefit. **Both "it would
  help" and "it would not" are unsupported by this analysis**, and the second
  error is the tempting one now.
- **Twelve subjects, one cohort, one dataset**, three contrasts, eight subsets
  per point, 400 replicates.
- No held-out estimate is obtainable within LTSTDB, permanently. E6a does not
  change that.

---

## 6. Recommendation on E6

**Do not request authorization for E6 on the current evidence.**

The audit's case for E6 was §6's projection that four of five contrasts would
resolve at 68 subjects. **That projection is withdrawn**, and E6a could not
replace it with a measured one. Authorizing 27–30 h of compute — the last
scarce resource, requiring a fresh human authorization — on a precision claim
that no longer has support would be spending the budget on an assumption.

**This is not a recommendation against E6 in principle.** §3 of the audit still
stands: cross-fitting is the only path past the n=12 ceiling, because all 68
development subjects have already influenced the frozen encoder. What has
changed is that **the expected precision gain is unquantified and this cohort
cannot quantify it.**

If E6 is nonetheless pursued, it should be proposed honestly as **exploratory,
with no precision guarantee**, rather than as an instrument with a predicted
resolving power. A reader deciding whether to fund it deserves that distinction.
