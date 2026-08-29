# U1 Calibration Reliability — Preregistered Analysis Plan, V1

This plan fixes the reporting shape for the **per-bin reliability evidence** of
the canonical U1 development run, before any of it is read.

It is a plan for a **report**, not for an experiment. No run is authorized here,
no artifact is produced, no metric is computed that the U1 canonical run did not
already compute and persist, and no retention decision is revisited.

---

## 0. Why this plan exists at all

U1's headline calibration values have been read and published.
`U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` §3 reports NLL, Brier and both
ECE binnings per calibrator family, and a human retention decision was taken on
that evidence: Platt calibration retained, the selective router at
`c_star = 0.90` not retained.

**What has never been read is the layer underneath those numbers.** The U1
protocol §10.2 required per-bin reliability evidence, §10.3 froze the exact bin
construction, and the canonical run persisted all of it. Fifteen bins, two
binnings, three families including the uncalibrated baseline, each bin carrying
`count`, minimum, maximum and mean probability and empirical positive fraction.

No document in this repository has ever cited a single one of those bins. A
tree-wide search for `reliability_equal_width`, `reliability_equal_mass`,
`bin_count` or "per-bin" across `docs/` returns nothing as of 2026-08-22.

So this is a **first read of the per-bin evidence** on an experiment whose
summary values are already public. That is a narrower gate than T1's or T2's,
and it is still a gate: a scalar ECE is compatible with many different reliability
curves, and choosing which bins to show after seeing them is the same error
pre-registration exists to prevent, in miniature. The shape is fixed here first.

---

## 1. What exists

All of it already on disk, from the single canonical U1 development run
`cardiosentinel-runs/phase7-u1-development-v1/u1-v1-development/`.

| Artifact | Carries |
|---|---|
| `U1_OOF_CALIBRATION.json` | three families, each with `brier`, `negative_log_likelihood`, `clamp_delta`, `row_count`, `reliability_equal_width`, `reliability_equal_mass` |
| `U1_FAMILY_SELECTION.json` | the frozen family-selection decision and its criterion |
| `U1_OOF_RESULT.json` | subject evidence, subject bootstrap, risk–coverage, routing guards, `u_star_dev` |
| `U1_EXPERIMENT_LOCK.json` | the lock the above are bound by |

The three families are
`platt_logistic_on_recovered_logit`, `temperature_only_on_recovered_logit`, and
`uncalibrated_baseline` — the last being the raw score treated as a probability,
which is what makes "did calibration help?" answerable at all.

**No new computation is authorized by this plan.** Every number in the report is
read verbatim from these artifacts.

---

## 2. What the evidence can and cannot support

**Can.** A description of how well the retained calibrator's probabilities match
observed frequencies, out-of-fold, on the LTSTDB development partition, at the
bin resolution the protocol froze in advance — and the same description for the
uncalibrated baseline and the rejected temperature family, so the retained one is
readable against something.

**Cannot.**

- **Anything about TEST.** `test_accessed: false`, `sealed_test_state: unopened`.
  The B4/neural sealed test is the last firewall and is unopened.
- **Generalisation.** These are development, out-of-fold values on one cohort.
  `U1_OOF_RESULT.json` carries `development_optimistic: true` and its own
  `development_optimism_note`; the report must carry that forward, not drop it.
- **Clinical safety.** Protocol §16 is explicit: no U1 result may be described as
  clinical safety, statistical significance, or generalisation.
- **A retention decision.** The decision is made and frozen. This report describes
  evidence that decision was already taken on. It cannot ratify, strengthen or
  reopen it, and a reliability curve that looks better or worse than expected
  changes nothing.
- **Routing.** The selective router is not retained. Reliability of a probability
  is a separate question from what a policy built on that probability does, and
  the report may not drift from one into the other.

---

## 3. Pre-specified analysis

### 3.1 Primary descriptive — the retained calibrator

For `platt_logistic_on_recovered_logit`, both binnings, all 15 bins each,
reported verbatim: `count`, `mean probability`, `empirical positive fraction`,
and the signed gap `empirical − mean`. Plus the family-level
`expected_calibration_error`, `brier`, `negative_log_likelihood`, `row_count`
and `clamp_delta`.

The signed gap is arithmetic on two published numbers, not a new estimator. It is
named here so the direction of miscalibration is reported rather than left to the
reader to subtract — and so the sign convention is fixed before the values are
visible: **positive means the bin's observed positive rate exceeded its predicted
probability**, i.e. the calibrator was under-confident there.

### 3.2 Comparison against the uncalibrated baseline

The same table for `uncalibrated_baseline`, and the three family-level scalars
side by side for all three families. Protocol §16 condition 2 — pooled OOF Brier
and NLL both lower than the uncalibrated baseline — is restated with its
already-published verdict, as context for the bins, not as a new finding.

**Improved ECE alone is not a success criterion** (protocol §16) and the report
must say so where the ECE numbers appear, not in a footnote.

### 3.3 Bin degeneracy

For each binning and family: how many bins are empty, how many carry fewer than
30 rows, and the smallest and largest bin count. Equal-width binning on a
low-prevalence detector score concentrates mass at one end, and an ECE whose
weight sits in two bins says something different from one spread across fifteen.

This is the U1 analogue of the T1 lesson that **defined is not meaningful**:
availability analysis reported `episode_f1` defined for 12/12 subjects while
three of those were zero-reference degenerate. Bin counts are reported for the
same reason.

### 3.4 Provenance

SHA-256 of every artifact read, the experiment lock, the frozen dependency
digest, and the `git` commit the report was generated at.

### 3.5 Explicitly excluded

Not done, and not to be added as a follow-up without a separate decision:

- Re-deriving any metric from `u1_oof_primary_evidence.npz` or
  `u1_oof_challenge_evidence.npz`. The `.npz` stores are not opened.
- Any re-binning, alternative bin count, or alternative binning scheme. §10.3
  froze 15 bins and two constructions; a third would be a new analysis chosen
  after seeing the first two.
- Any recalibration, refit, temperature search or clamp-delta variation.
- Any routing, coverage, or `c_star` analysis. Different question, rejected
  component.
- Any per-subject reliability decomposition. It is a reasonable future analysis
  and it is not this one; adding it after seeing the pooled curve is exactly the
  move this plan forecloses.
- Any comparison to B0–B3, B4 or T2 scores. Those are different tasks with
  different score semantics, and T2 scores are not calibrated probabilities at
  all.

---

## 4. Reporting rules

1. Every number is quoted verbatim from a promoted artifact, except the signed
   gap of §3.1, which is named here as the one arithmetic derivation.
2. `None` is undefined and is never filled.
3. The uncalibrated baseline is reported with the retained calibrator every time
   the retained one's reliability is characterised. A calibration number without
   its baseline is not interpretable.
4. No comparative verb — improved, better, well-calibrated, reliable — without
   the baseline value in the same sentence or table row.
5. The words "calibrated probability" apply to U1 outputs only. They may not be
   attached to a T2 score anywhere in the report:
   `score_is_calibrated_probability: false`.
6. The split retention is restated wherever the report could be read as
   endorsing the U1 component as a whole: **calibration retained, router not.**

---

## 5. Sequence

1. This plan is merged. *(Nothing has been read at this point.)*
2. The generator, merged with this plan, is run against the promoted artifacts.
3. `docs/experiments/u1/U1_CALIBRATION_RELIABILITY_REPORT_V1.md` is produced and opened as a
   separate pull request, in the same shape T1 used — plan first, report second.
4. The plan is not modified after step 2. If the shape fixed here turns out to be
   wrong, that is recorded in the report as a limitation, not repaired by editing
   this file.

---

## 6. Risks carried into this analysis

- **This is development evidence and it is optimistic.** The artifact says so
  itself. A reliability curve on development data is the most flattering
  reliability curve this system will ever produce.
- **Out-of-fold is not out-of-cohort.** Subject-disjoint folds control for
  subject leakage within LTSTDB. They say nothing about another hospital, another
  recording era, or another electrode placement.
- **A good reliability curve is not a good detector.** ECE can be driven low by a
  calibrator that maps everything near the base rate. The Brier and NLL columns,
  and the fact that the family selection used NLL rather than ECE, are the guard
  against reading it that way.
- **The temptation this plan is most exposed to** is presenting the per-bin
  evidence as if it strengthened the retention decision. It does not. The decision
  was taken on evidence that already included these bins' summary; reading the
  bins adds description, not support.

---

## 7. Approval record

| | |
|---|---|
| Plan status | preregistered, values unread at time of writing |
| Authorizes a run | **no** |
| Authorizes a new metric | **no** |
| Opens TEST | **no** |
| Reopens a retention decision | **no** |
| Artifacts read | four JSON files listed in §1 |
| `.npz` stores opened | **none** |
