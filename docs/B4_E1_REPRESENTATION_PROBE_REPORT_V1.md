# B4 · E1 Representation Gap Probe — Report, V1

Executed under `docs/B4_E1_REPRESENTATION_PROBE_ANALYSIS_PLAN_V1.md`, whose §5
reporting rules govern every sentence below. **Development validation evidence
only. No sealed-test artifact was opened, no model was retrained, no lock was
modified, and no budget was opened.**

**The headline is negative and should be read first. E1 does not answer its own
question, and the reason is the answer.** Every one of the five registered
contrasts includes zero. **The 12-subject validation cohort cannot separate a
frozen-embedding probe from the deployed head, nor either from a morphology
probe** — so *"information absent"* and *"information present but unused"*
remain both consistent with the evidence. §6 states what follows, and it is a
recommendation **against** spending the remaining days on either branch.

| | |
|---|---|
| Executed | 2026-08-25 |
| Rows | **473,897** validation windows, **12** subjects, prevalence 0.045639 |
| Bootstrap | paired subject, **1,000** replicates, seed **2026**, **0 undefined** |
| Fitted on | 374,452 train rows, **56** subjects, disjoint from validation (asserted) |

---

## 1. A0 — the bridge reproduces

| | |
|---|---|
| A0 pooled AUPRC | 0.3805360912735439 |
| Published | 0.38053499010488423 |
| max abs score difference | **8.772e-08** · `allclose(atol=1e-6) → True` |

**PASS.** The cached embedding is the tensor the deployed head consumes;
`classifier.head(embedding)` reproduces `validation_predictions.npz`.

**The gate failed on its first execution and the gate was wrong, not the
bridge.** As registered it demanded float32 agreement on scores *and* exact
equality of pooled AUPRC — mutually unsatisfiable, because AUPRC is a rank
statistic over those very scores. Amendment 2 of the plan records the empirical
calibration: perturbing the published scores by ±8.772e-08 moves AUPRC by
1.095e-08 to 2.417e-06 over 20 draws, and A0's observed 1.101e-06 sits near that
median. The substantive criterion passed unamended on the first run.

---

## 2. Results

**Validation, all arms on the identical 473,897 rows.**

| Arm | Input · model | Pooled AUPRC | Subject-macro AUPRC | AUROC |
|---|---|---|---|---|
| **A1** | deployed head (published) | 0.380535 | **0.400636** | 0.892762 |
| **A2** | embedding · linear probe | 0.320474 | 0.384148 | 0.881920 |
| **A3** | embedding · `128→64 SiLU→1` | 0.327163 | 0.389497 | 0.889298 |
| **A4** | morphology (40) · linear probe | **0.475070** | **0.300422** | 0.797569 |
| **A5** | embedding ⊕ morphology · linear | 0.383583 | 0.391135 | **0.902648** |

**Subject-macro AUPRC is computed over 9 of 12 subjects in every arm.** Three
validation subjects carry no positive window, so the statistic is undefined for
them. **This is the same 9-of-12 denominator that concealed itself in T2** and
that §9.2 of the discussion draft was written about. It is stated here beside
every macro figure rather than in a footnote.

**Registered paired subject-bootstrap contrasts.**

| Contrast | Point | 95% interval | Width | Share > 0 |
|---|---|---|---|---|
| **A2 − A1** | −0.060061 | [−0.138581, +0.022577] | 0.161 | 0.236 |
| **A3 − A1** | −0.053372 | [−0.121862, +0.048778] | 0.171 | 0.278 |
| **A4 − A2** | +0.154596 | [−0.215019, +0.433902] | **0.649** | 0.576 |
| **A5 − A2** | +0.063109 | [−0.010838, +0.098684] | 0.110 | **0.925** |
| **A5 − A4** | −0.091487 | [−0.341341, +0.215671] | **0.557** | 0.475 |

**All five include zero.** Selected hyperparameters: A2 `C=0.1`, A3 `epochs=4`,
A4 `C=10.0`, A5 `C=0.1`.

---

## 3. Registered predictions, reported as written

| # | Prediction | Outcome |
|---|---|---|
| 0 | A0 reproduces the published AUPRC | **PASS**, after the gate's own specification was corrected |
| 1 | A2 − A1 negative, interval includes zero | **Confirmed** — −0.060061, [−0.1386, +0.0226] |
| 2 | A3 − A1 includes zero | **Confirmed** — [−0.1219, +0.0488] |
| 3 | A4 strongest single-feature-set arm **on subject-macro AUPRC** | **REFUTED.** A4 is the **weakest** on subject-macro (0.300422) and the **strongest** on pooled (0.475070) |
| 4 | A5 does not beat A4 by an interval excluding zero | **Confirmed** — and A5 is *below* A4 in point estimate |
| 5 | At least three of five contrasts include zero | **Confirmed** — **five** of five |

**Prediction 3 was wrong in a specific and informative way, and §4 is about it.**

---

## 4. The finding that survives: one score set, two metrics, opposite verdicts

**A4 is +0.094535 above the head on pooled AUPRC and −0.100214 below it on
subject-macro AUPRC.** The same scores, on the same rows, against the same
labels. The ranking of morphology against every other arm **inverts** depending
on which of two registered metrics is read.

**This is not a sampling artifact and does not depend on the bootstrap.** It is
an arithmetic property of the two statistics: pooled AUPRC weights each subject
by its window count, subject-macro weights subjects equally. A4's advantage is
concentrated in subjects that contribute many windows and does not survive equal
weighting. **A4's AUROC — 0.797569, the lowest of the five — is consistent with
that reading and not with better discrimination.**

**This is §9.2's denominator finding, reproduced in a new experiment by
accident.** The paper predicted that population-level scalars conceal their
contributing units; E1 produced a case where two such scalars disagree about the
direction of an effect. It is the strongest single result in this experiment and
it is methodological rather than about ECG.

---

## 5. What the experiment does and does not license

**Does not license: any statement that the embedding lacks the information.**
`A4 − A2` spans **[−0.215, +0.434]**, a width of 0.649 on a metric whose entire
region of interest is roughly 0.05 to 0.50. The interval is consistent with
morphology being far better, far worse, or identical. **Plan §8.1 governs this:
a null or a positive here is a statement about decodability under one probe on
one cohort**, and the four alternative explanations listed there — noisy
features, weak extraction, insufficient probe capacity, fusion strategy — are
all still open.

**Does not license: any statement that information is present but unused.**
Both embedding probes sit below the head. **A2 − A1 = −0.060** and
**A3 − A1 = −0.053**, and §5.1 of the plan registered in advance that the head
carries an argmax-over-epochs advantage measured by E2 at **+0.03211** which the
probes do not enjoy. **More than half of each gap is that advantage**, so the
head's margin is not interpretable in its favour — but neither is it evidence
against it.

**Does license, and this one is robust: the head's non-linearity is not the
differentiator.** A3 has the deployed head's exact architecture — same hidden
width, same activation, same parameter count — fitted to the same frozen
features. It scores 0.327163 against A2's 0.320474, a difference of **0.0067**.
**Whatever separates the head from a probe on its own frozen output, it is not
the capacity of the head.** The remaining candidates are the validation
selection advantage and the fact that the encoder was optimised jointly with
that specific head, so the representation is shaped for it.

**Suggestive but below the registered bar: morphology adds to the embedding.**
`A5 − A2` is the tightest contrast in the experiment (width 0.110) with
**92.5%** of replicate mass above zero, and A5 achieves the highest AUROC of any
arm (0.902648) with no end-to-end training at all. **It still includes zero, so
it does not separate**, and it is reported as suggestive rather than as a
result. It is the contrast a larger cohort would resolve first.

---

## 6. What follows — a recommendation against both branches

The plan's §11 fork asked which of two directions E1 justifies. **On this
evidence, neither.**

```
                        E1
                         |
          ---------------------------------
          |                               |
  embedding carries signal         embedding lacks signal
          |                               |
     not established                 not established
```

- **E4 — the class-prior and loss retraining arm — is not justified by E1.**
  It would need a fresh human authorization, would cost roughly a day, and E1
  supplies no evidence that the representation is the binding constraint.
  Launching it now would be choosing an arm and justifying it afterwards, which
  the brief's §7 explicitly forbids.
- **A confident "improve the IPS instead" is equally unsupported.** E1 does not
  establish that the embedding carries the signal; it establishes that this
  cohort cannot tell.

**What E1 does support is an instrument conclusion, and it is the same one E2b
reached.** E2b could not separate three architectures whose validation AUPRCs
differ by 0.043. E1 cannot separate feature representations whose pooled AUPRCs
differ by 0.155. **Twelve validation subjects cannot adjudicate questions of
this size, and no amount of modelling effort changes that.** The brief's **E6 —
the cross-fitted subject-transfer instrument over the 68-subject development
pool** — is the item that addresses the actual blocker, and E1 is evidence for
prioritising it over E4 and E5.

---

## 7. Bounds, restated

- **Development evidence only.** Mechanism understood; **no performance claim is
  made or implied.**
- **No held-out estimate is obtainable within LTSTDB, permanently.**
- **Twelve subjects.** Every interval is a subject-resampling interval over a
  fixed development cohort and **is not a confidence interval for a new cohort**.
- **Nine of twelve** subjects contribute to every subject-macro figure.
- **Cross-validation numbers are not results.** The train-fold CV AUPRCs
  (A2 0.9676, A3 0.9677, A4 0.7311, A5 0.9677) were used **only** to select one
  hyperparameter per arm. They sit at 25% train prevalence, where the random
  baseline is 0.25 rather than 0.046, **and the encoder was trained on all 56
  training subjects — so even held-out CV folds contain rows it has already
  seen.** The embedding arms are inflated by memorisation the morphology arm
  does not enjoy. **These numbers must never be quoted as a comparison between
  arms.**
- **A3 selected 4 epochs of 15.** Consistent with the brief's §3.2 observation
  that every B4 candidate overfits within two to four epochs — reported as
  corroboration of that pattern, not as a new finding.
