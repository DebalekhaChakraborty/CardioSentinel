# B4 · E9 Lead / Polarity / Label-Semantics Audit — Report, V1

Executed under `B4_E9_LEAD_POLARITY_AUDIT_PLAN_V1.md`. **Read-only, development
data only. No retraining, no corrective model, no sealed-test artifact and no
test header opened.** **Mechanism evidence only.**

**Two headlines, and the second invalidates part of the requested design.**

1. **The binary target is polarity-agnostic**, and that is a
   **target-definition** property established from source: elevation and
   depression ischemic episodes receive the identical positive label.
2. **The TRAIN partition contains no stream-quality failures to characterise.**
   All 79 TRAIN streams score AUROC **≥ 0.8975** (median 0.9850). **B4
   memorised its training subjects**, so the requested
   TRAIN→VALIDATION mechanism design **cannot be executed for this question**.

**Polarity does not broadly explain the failures**, SQI does not explain them,
and they are confined to **3 streams in 2 subjects**. §7 recommends closing the
lead/polarity modelling branch while retaining the target-definition finding.

---

## 1. Reproduction gate — PASSED

| check | result |
|---|---|
| `classifier.head(embedding)` vs published validation scores | `max abs Δ = 1.192e-07` — **PASS** |
| `target_families == "ischemic_positive"` ≡ `label` | **True** |
| TRAIN scores reproduced | **2,208,431** |

TRAIN scores were produced **only after** the validation reproduction passed, by
the identical head-only path. No encoder invoked, nothing trained, no label used.

## 2. Audit outcomes

**Label semantics — channel-specific, polarity-agnostic.** `STEvent.lead` is
`int`, never optional; every `.stb` regex captures `(?P<lead>[0-2])` with a
signed deviation; `targets._same_lead` filters events per channel. **Labels are
not broadcast.** But `direction` and `peak_deviation_uv` are **discarded** when
the target is reduced to `ischemic_positive`, so **two channels with reciprocal
ST morphology can both be positive** — each annotated on its own merits, both
collapsed into one class.

**True lead identity — recovered, with a residual gap.** 162
`(record, channel)` entries across all 73 development records; the 13 test
records were enumerated only to exclude them. **42 of 162 channels carry the
generic name `ECG` in the WFDB header itself**, so the degeneracy is not only a
corpus artifact and those channels are reported as `UNKNOWN`, never pooled.

**Signed morphology — sign comparable, magnitude not.** Eight baseline-relative
mV features; positive = elevation. `processing_profile: raw`, no amplitude
normalisation, so **magnitudes are not comparable across lead types** and only
signs and within-stream contrasts are used.

---

## 3. The finding that blocks the requested design

| partition | streams with AUROC | min | median | max | **< 0.8** | **< 0.6** |
|---|---|---|---|---|---|---|
| **TRAIN** | 79 | **0.8975** | 0.9850 | 0.9995 | **0** | **0** |
| VALIDATION | 19 | 0.2235 | 0.9045 | 0.9948 | 3 | 3 |

**There is no failure on TRAIN to characterise.** B4 was fitted on those 56
subjects, and its per-stream discrimination there is uniformly excellent. **A
mechanism for stream failure cannot be derived from a partition in which the
failure does not occur**, so §2's TRAIN→VALIDATION discipline is unexecutable
here — not violated, but inapplicable.

**Consequence, stated plainly: everything below is validation-side
*description*, not a rule derived on TRAIN and confirmed on VALIDATION.** It
must not be read as though it had survived that test.

---

## 4. Per-stream description (VALIDATION, 19 streams)

| record:ch | lead | AUROC | separation | prevalence | ischemic episodes | depression fraction | ST contrast | HF p95 |
|---|---|---|---|---|---|---|---|---|
| **s20311:1** | **V3** | **0.2235** | **−0.3057** | 0.0215 | 10 | **0.800** | −0.0475 | 0.0026 |
| **s20191:0** | **MLIII** | **0.4821** | −0.0111 | 0.0041 | 3 | **0.000** | +0.1137 | 0.0119 |
| **s20191:1** | **V4** | **0.5241** | +0.0349 | 0.0039 | 3 | **0.000** | +0.1325 | 0.0118 |
| s20591:1 | MLIII | 0.8194 | +0.4545 | 0.0029 | 1 | 1.000 | −0.0925 | 0.0157 |
| s20041:1 | ECG | 0.8236 | +0.2512 | 0.2220 | 21 | 1.000 | −0.0750 | 0.0058 |
| s20041:0 | ECG | 0.8360 | +0.3482 | 0.1703 | 17 | 1.000 | −0.0750 | 0.0035 |
| s20571:0 | V5 | 0.8535 | +0.4400 | 0.0181 | 5 | 1.000 | −0.1175 | 0.0011 |
| s30732:1 | A-S | 0.8544 | +0.3729 | 0.0251 | 1 | 1.000 | −0.0900 | 0.0059 |
| s30721:1 | A-S | 0.8904 | +0.1629 | 0.0028 | 1 | 1.000 | −0.0850 | 0.0209 |
| s20591:0 | V2 | 0.9045 | +0.1870 | 0.0728 | 46 | 0.065 | +0.1150 | 0.0037 |
| **s20311:0** | **MLIII** | **0.9379** | +0.4097 | 0.0277 | 8 | **0.000** | +0.0725 | 0.0135 |
| s30732:2 | A-I | 0.9398 | +0.5569 | 0.0248 | 1 | 1.000 | −0.1031 | 0.0050 |
| s30681:2 | V5 | 0.9645 | +0.6701 | 0.2285 | 17 | 1.000 | −0.1300 | 0.0269 |
| s30681:0 | V6 | 0.9805 | +0.6986 | 0.1938 | 11 | 1.000 | −0.1975 | 0.0101 |
| s20581:1 | V2 | 0.9839 | +0.4105 | 0.0023 | 1 | 1.000 | −0.0944 | 0.0029 |
| s30731:1 | A-S | 0.9851 | +0.7399 | 0.0426 | 4 | 1.000 | −0.1837 | 0.0071 |
| s30681:1 | II | 0.9924 | +0.7595 | 0.1626 | 7 | 1.000 | −0.1137 | 0.0298 |
| s30731:2 | A-I | 0.9932 | +0.8396 | 0.0443 | 4 | 1.000 | −0.1650 | 0.0048 |
| **s20581:0** | **V5** | **0.9948** | +0.6532 | 0.0040 | 2 | **0.000** | +0.1675 | 0.0023 |

Spearman against AUROC, **`s2031` excluded** (n = 17): depression fraction
**+0.208**, ST contrast **−0.451**, HF-power p95 **−0.172**, derivative-outlier
p95 **−0.036**, prevalence +0.159. `morphology_valid` is **1.000 everywhere**
and cannot discriminate anything.

---

## 5. The four mechanisms, kept separate

**M-pol · polarity / sign reversal — NOT supported as a general mechanism.**
Registered prediction 2 said depression-predominant streams would show *lower*
AUROC. **The pooled sign is the opposite** (+0.208 validation, +0.133 train) and
weak. **Decisively, elevation-only streams span the entire range**: `s20581:0`
(depression fraction 0.000) scores **0.9948**, while `s20191:0` (also 0.000)
scores **0.4821**. **Polarity alone predicts nothing.**

**M-inf · weak lead informativeness — supported for `s2019`.** Both channels
carry **3 ischemic episodes** at prevalence ~0.004, with separations of
**−0.011** and **+0.035** — essentially no class contrast in either direction.
This is an uninformative lead pair, not an inverted one.

**M-sqi · signal quality — NOT supported.** Registered prediction 3 holds.
`s20311:1`'s HF-power p95 is **0.0026**, among the *cleanest* in the cohort,
while the best-discriminating stream `s30681:1` has the *highest* at **0.0298**.
The correlation is −0.172 and runs the wrong way for an SQI explanation.

**M-sem · label / lead semantic mismatch — supported, and it is a
target-definition property.** `s20311` carries **8 ischemic elevation episodes
on lead 0 (MLIII) and 8 depression episodes on lead 1 (V3)** — reciprocal
morphology, identical binary label. The WFDB header states it independently:
*"Lead 0 shows numerous ST-elevations. These are mirrored in lead 1 by slight
decrease in baseline ST elevation."* **This is real and documented at source.**

## 6. Within-subject paired view, and `s2031` as case only

`s2031` is the **only** subject showing a dramatic within-subject split
(0.9379 vs **0.2235**). `s2019` fails on **both** channels (0.4821, 0.5241), so
its failure is not a within-subject polarity contrast. Every other multi-stream
subject is internally consistent: `s2004` 0.8360/0.8236, `s2058` 0.9948/0.9839,
`s2059` 0.9045/0.8194, `s3068` 0.9805/0.9924/0.9645, `s3073` 0.9851/0.9932.

**`s2031` was excluded from every pooled statistic in §4**, and it remains the
motivating case rather than the estimand — which matters, because **the pooled
polarity trend runs opposite to it.**

---

## 7. Recommendation

**Two of the registered interpretation rules apply, and they are reported
together rather than one being chosen.**

**Rule 3 — label semantics.** The target **is** polarity-agnostic across
channels. That is a **target-definition** property, established from source
annotations and independently corroborated by the record header. **It should be
recorded as such and not treated as a model-capacity problem.** It does not
require a modelling change to be true, and it is the most durable finding here.

**Rule 4 — close the lead/polarity modelling branch.** Nothing reproduces
beyond isolated subjects: failures are **3 streams in 2 subjects of 19**, the
polarity association is weak and **signed opposite to the hypothesis**, SQI is
excluded, and **the TRAIN partition cannot corroborate anything because it
contains no failures at all**. **E9b — a lead-aware or polarity-aware
representation experiment — is NOT recommended on this evidence.**

**Return to the M1 incremental-value branch** (E8b's C0/C1 probe, still
unexecuted) **or to broader representation learning**, with E8b's caveat intact:
the instrument cannot resolve the resulting performance differences.

### 7.1 A constraint any future work inherits

**B4's TRAIN-side per-stream AUROC has a floor of 0.8975.** Any future attempt
to characterise B4 failure modes on TRAIN will find none. **Failure-mode work on
this system is confined to 19 validation streams in 9 subjects**, which is the
same instrument limit E6a measured — now reappearing as an inability to even
*observe* the phenomenon on the larger partition.

---

## 8. Bounds

- **Mechanism evidence only.** Not development performance, not generalization.
- **Validation-side description**, not a TRAIN-derived rule confirmed on
  VALIDATION — §3 explains why that design was unexecutable.
- **19 streams in 9 subjects**; 3 failures in 2 subjects. **No contrast is
  bootstrapped**; E6a applies to all of them.
- **42 of 162 development channels have no recoverable lead identity.**
- ST magnitudes are **not comparable across lead types**; only signs and
  within-stream contrasts were used.
- **No test record, header or artifact was opened**, and no waveform sample was
  read outside the frozen feature corpus.
