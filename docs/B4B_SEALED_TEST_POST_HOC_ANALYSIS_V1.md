# B4-B Sealed Test Post-hoc Failure Mode Analysis, V1

**POST-HOC ANALYSIS. This document was written after the sealed-test values were
read.** It is not part of the pre-registration in `B4_PROTOCOL_V1` and carries
none of that document's authority. Every quantity here that is not already
registered in `TEST_METRICS.json` or `VALIDATION_METRICS.json` is arithmetic on
published values and is labelled **post-hoc descriptive** where it appears.

**§6.4 of `B4_TEST_AUTHORIZATION_V1.md` fixed the reporting commitment before
access, and §9.8 of `PAPER_S9_DISCUSSION_SKELETON.md` binds what may change
because of the result: the number goes in §7, one sentence goes in §9.1, and no
thesis in §9 moves.** This document adds neither. It is new explanatory
material, on the precedent of `T1_POST_HOC_ANALYSIS_V1.md`, and it must not be
cited as a revision of anything pre-registered.

## What this document does not do

| | |
|---|---|
| Changes the primary endpoint | **No.** The registered primary remains pooled-window AUPRC |
| Changes the primary value | **No.** `0.0935334` is unchanged and is not recomputed anywhere here |
| Changes the threshold | **No.** `0.8329097628593445` is frozen, validation-selected, `test_informed: false` |
| Presents an alternative headline | **No.** No corrected, adjusted or re-scored figure is computed or implied |
| Reads test predictions | **No.** `TEST_PREDICTIONS.npz` was not opened. Only registered values in `TEST_METRICS.json` are quoted |
| Recomputes any test metric | **No** |
| Alters any artifact | **No.** All four digests re-verify unchanged (§7.1) |
| Revises §9 | **No.** §9 was drafted and merged **before** the test opened, and that ordering is the claim |

The registered result stands exactly as reported:

```
Pooled-window AUPRC            0.0935334      prevalence 0.0460529
AUROC                          0.7332374
Subject-macro AUPRC            0.354901       over 8 of 12 subjects
95% subject-bootstrap AUPRC    [0.033058, 0.239284]
```

This analysis explains **what that number is made of**. It does not adjust it,
and a reader who wants a single figure should continue to use the registered one.

---

## 1. What was actually scored — read this before any other section

**The sealed test evaluated the B4-B encoder alone, as a raw-waveform window
classifier.** It did not evaluate the assembled Intelligent Physical System.

From `TEST_ATTEMPT.json`:

```
input_contract    [B, 1, 2500] · 1 channel · raw mV · 250 Hz
                  processing_profile "raw" · handcrafted_features_used false
model             B4BTransformerCNN  <-  model_selected.pt
                  experiment_id B4B_cnn_transformer_v1  (Phase 3B-2)
score_semantics   uncalibrated sigmoid model score; not calibrated probability
```

The full `TEST_AUDIT.json` payload contains **no** occurrence of `s4d`, `t2`,
`m1l`, `m2`, `u1`, `platt`, `calibrat`, `memory`, `physiolog`, `p1`, `episode`
or `t1`. The scored path is 2,500 samples in, one sigmoid out, thresholded at a
frozen constant.

**Three consequences, all binding on the manuscript.**

1. **S4D, M1L, M2-G, P1-B and U1 cannot be implicated or exonerated by this
   result.** None was in the scored path. Any failure analysis attributing the
   number to them is unsupported.
2. **The result is a floor on the encoder, not a ceiling on the system.** It
   does not bound the assembled pipeline — and because the budget is spent, the
   assembled pipeline's held-out performance is now **permanently
   unmeasurable** on this dataset.
3. **§7 must name the scored artifact**, not the architecture list: *B4-B
   window-level encoder, uncalibrated, at the frozen validation threshold.* A
   sentence implying otherwise would be wrong on the record.

**This is the §43.2 pattern recurring at the reporting layer.** There, two files
were each correct about themselves — the evaluator and the authorization — and
nothing compared them. Here, the architecture inventory in §48 and the sealed
evaluator's `input_contract` are each correct about themselves, and nothing
compared them either. **It was found by reading the input contract, not by any
check.**

---

## 2. Validation and test, side by side

Both columns are registered values. `VALIDATION_METRICS.json` carries
`evidence_class: development_validation_result`; `TEST_METRICS.json` carries
`evidence_class: sealed_one_shot_test_result`.

| | Validation | Test |
|---|---|---|
| Subjects · windows | 12 · 473,897 | 12 · 453,804 |
| Positives · negatives | 21,628 · 452,269 | 20,899 · 432,905 |
| **Prevalence** | **0.045639** | **0.046053** |
| Pooled AUPRC | 0.380535 | 0.093533 |
| Pooled AUROC | 0.892762 | 0.733237 |
| Pooled sensitivity | 0.410533 | 0.070578 |
| Pooled specificity | 0.967155 | 0.952572 |
| Pooled PPV | 0.374105 | 0.067024 |
| Pooled F1 | 0.391473 | 0.068755 |
| Pooled MCC | 0.361384 | 0.022588 |
| TP · FP · FN · TN | 8,879 · 14,855 · 12,749 · 437,414 | 1,475 · 20,532 · 19,424 · 412,373 |
| Subject-macro AUPRC | 0.400636 (9/12) | 0.354901 (8/12) |
| Subject-macro AUROC | 0.841039 (9/12) | 0.780837 (8/12) |
| Subject-macro sensitivity | 0.285845 (9/12) | 0.169043 (8/12) |
| **Subject-macro PPV** | **0.337366 (12/12)** | **0.332849 (12/12)** |
| Subject-macro specificity | 0.958234 (12/12) | 0.947705 (12/12) |

Threshold `0.8329097628593445` in both columns — validation-selected by maximum
validation F1, applied unchanged to test.

**Prevalence is matched to within 0.9%.** Whatever happened, it is not a
prevalence shift.

---

## 3. The diagnosis — ordering generalized, scale did not

### 3.1 The pooling penalty

**Post-hoc descriptive**, computed as `1 − pooled / subject-macro` on the
published AUPRC values:

| | Subject-macro AUPRC | Pooled AUPRC | Pooling penalty |
|---|---|---|---|
| Validation | 0.400636 | 0.380535 | **5.0%** |
| Test | 0.354901 | 0.093533 | **73.6%** |

On validation, pooling cost almost nothing: subject scores were comparable
enough that ranking them together barely hurt. On test, pooling destroys three
quarters of the AUPRC.

**The denominators are not identical and the comparison is descriptive, not
inferential.** Macro is over 9 of 12 subjects on validation and 8 of 12 on test,
while pooled includes every subject's windows in both. Part of the divergence is
mechanical: test carries **four** all-negative subjects against validation's
three, and those subjects contribute only negatives to the pooled ranking while
being excluded from macro discrimination. Elevated-but-non-ischemic scores from
them enter the top of the pooled list without any positive to justify them.

That mechanism *is* the finding rather than a confound to it: it is one of the
ways a subject-relative score fails when pooled.

### 3.2 What was retained, and what was not

**Post-hoc descriptive**, ratios of published values. AUROC is expressed as
skill above chance, `(AUROC − 0.5)`, because a raw ratio of AUROCs understates
loss.

| Quantity | Retained on test |
|---|---|
| Subject-macro PPV | **98.7%** |
| Subject-macro AUPRC | **88.6%** |
| Subject-macro AUROC skill | **82.4%** |
| Pooled AUROC skill | 59.4% |
| Subject-macro sensitivity | 59.1% |
| **Pooled AUPRC** | **24.6%** |
| Pooled sensitivity | 17.2% |

Read down that column. **Within-subject discrimination and precision-when-firing
are largely intact. Only the pooled, cross-subject view collapses.**

### 3.3 The mechanism

Three registered facts, taken together, admit one reading:

- Subject-macro PPV moved **0.337366 → 0.332849**, a 1.3% change. When the model
  fires on a test subject, it is right about as often as on validation.
- Pooled sensitivity fell **0.410533 → 0.070578** at a **fixed** threshold.
- Pooled specificity barely moved, **0.967155 → 0.952572**.

Precision preserved, firing rate collapsed, cut unchanged. That is the signature
of the **score distribution shifting relative to a fixed absolute cut** — not of
degraded features. A model that had failed to represent ischemia would have lost
within-subject ranking too, and it largely did not.

**The model learned a subject-relative decision function and was evaluated with
a subject-absolute threshold.** Twelve subjects, four of them all-negative, is
too few for per-subject offsets to average out.

### 3.4 The sharpest single number

On positives carrying no axis and no conduction context — the *clean* positives,
at near-identical window counts. Both rows are registered counts from the
`positive_context` block; the sensitivities are **post-hoc descriptive** division.

| | TP | Windows | Sensitivity | Subjects |
|---|---|---|---|---|
| Validation | 8,879 | 21,626 | 0.410571 | 9 |
| Test | 1,471 | 20,856 | 0.070531 | 8 |

**83% of detection lost on the easy positives.** Whatever failed, it is not
confounder handling.

---

## 4. The six hypotheses, assessed

| | Hypothesis | Verdict |
|---|---|---|
| A | Representation encoder weakness (B4-B) | **Partial, modest.** Real: macro AUROC skill lost 17.6%, macro AUPRC lost 11.4%. Not sufficient to explain a 75.4% pooled AUPRC loss |
| B | Temporal modelling weakness (S4D) | **Not assessable.** Not in the scored path (§1). Separately, the T2 selection contrast **[−0.015229, 0.148951]** spans zero, so no temporal gain was ever established to have been lost |
| C | Personalization failure (M1/M2) | **Not assessable.** Not in the scored path (§1) |
| D | Calibration / threshold / score scale | **Primary.** §3.3 |
| E | Dataset / domain shift | **Weak, and partly falsified.** Prevalence matched to 0.9%; confounder strata *improved* (§5) |
| F | Insufficient cohort size | **Strong contributor, compounding D.** §3.1, and the bootstrap interval **[0.033058, 0.239284]** is more than twice the width of its own point estimate |

**On D and F together.** These are not competing explanations. A per-subject
score offset is a nuisance parameter; with enough subjects it averages out of a
pooled estimate, and with twelve it does not. D is the mechanism, F is why it
was not absorbed.

**A descriptive note on F, not a hypothesis test.** The validation pooled AUPRC
point estimate, 0.380535, lies **above** the upper bound of the test bootstrap
interval, 0.239284. Resampling test subjects does not reach the validation
figure. §46 forbids significance language and none is claimed; this is stated as
a descriptive relationship between a point estimate and an interval, and it is
**not** a paired test between partitions, which does not exist and cannot now be
constructed.

---

## 5. The confounder controls held — report this as a finding

Registered challenge-stratum values at the frozen threshold. Share-of-total-FP
is **post-hoc descriptive**.

| Stratum | Validation FP fraction | Test FP fraction | Share of all FPs, validation → test |
|---|---|---|---|
| Rate-related | 0.331188 (1,647/4,973, 4 subj) | 0.229282 (1,162/5,068, 4 subj) | 11.09% → 5.66% |
| Axis-shift | 0.061667 (185/3,000, 8 subj) | 0.038914 (119/3,058, 8 subj) | 1.25% → 0.58% |

Meanwhile the overall false-positive rate **rose 44%** (1 − specificity:
0.032845 → 0.047428, post-hoc descriptive).

**More false positives overall, proportionally fewer of them in the strata the
architecture was selected to resist.** The confounder robustness B4-B was chosen
for — it beat B4-A at 0.345667 and B4-C at 0.465112 on validation rate-related
FP fraction — transferred to held-out subjects. **The new false positives are
diffuse and currently uncharacterised.**

Conduction-change evidence is **exploratory and descriptive**: 8 of 10 windows,
one subject. It is not bootstrapped, is not a headline, and is quoted here only
to state that it was not used.

---

## 6. Why U1 as retained could not have addressed this

`U1_DEPLOYMENT_CALIBRATOR.json` records **one** deployment calibrator —
`selected_family: platt_logistic_on_recovered_logit`, `calibrated_boundary:
0.20631829355583678`. Its digest `acec97c1…` matches
`final_deployment_calibrator_sha256` in `U1_EXPERIMENT_LOCK.json`. The
`calibrator_count: 12` in `U1_OOF_CALIBRATION.json` is **twelve out-of-fold
calibrators for honest OOF evaluation**, not twelve per-subject deployment
calibrators.

**A single global Platt is a monotone transform of the score, and a monotone
transform is rank-preserving.** Applied to the sealed-test scores it would have
returned pooled AUPRC `0.0935334` and AUROC `0.7332374` **exactly** — those
metrics depend only on ordering. It would have moved the threshold-dependent
metrics, because the decision boundary would be 0.206318 on calibrated
probability rather than 0.832910 on raw sigmoid.

**So U1 is not a missed fix for the headline.** The diagnosed defect is a
*cross-subject rank* problem, and only a calibrator that applies a **different**
transform per subject changes cross-subject ranks. No such calibrator exists in
this programme.

This is worth stating plainly because the opposite inference is the natural one
and it is wrong: *"we built a calibrator and forgot to use it"* would be a
tidier story than *"the calibrator we built is the wrong kind for the failure we
found"*, and the second is what the artifacts say.

The runtime does apply the global calibrator — `DEMO_SCENARIO.md` §4 records
`calibrator: platt_logistic_on_recovered_logit` with a peak calibrated
probability of 0.545613 — so the deployed path and the evaluated path differ in
that respect. Neither carries a per-subject transform.

---

## 7. Boundary

| Boundary | Result |
|---|---|
| Test predictions read | **None.** `TEST_PREDICTIONS.npz` was not opened |
| New test metrics generated | **None.** Only registered values from `TEST_METRICS.json` are quoted; all ratios are labelled post-hoc descriptive |
| New experiments executed | **None.** No run was started; none is authorized |
| Threshold changes | **None.** `0.8329097628593445` remains frozen, `test_informed: false` |
| Model retraining | **None.** No checkpoint was read or written |
| Artifact modification | **None.** All four digests re-verify (§7.1) |
| §9 revision | **None.** §9 was merged 2026-08-24; the test ran 2026-08-25 |
| Second attempt | **Impossible.** `repeat_attempt_permitted: false` |

### 7.1 Artifact digests at the time of writing

| Artifact | SHA-256 | Unchanged |
|---|---|---|
| `TEST_ATTEMPT.json` | `7db48a2750729dc2cc53eafd731e1e7e4e5e52d65b30b7a1bc1547523b7882a2` | ✅ |
| `TEST_METRICS.json` | `b117da896d94dd11cfb05e156211a79dee6db6ee18b25783b2bbe0e4440ef8b0` | ✅ |
| `TEST_PREDICTIONS.npz` | `8233d3cb70fdea976c26e9a33e1bc60caaa1fe60025f0c81b737d15f3cd53592` | ✅ |
| `TEST_AUDIT.json` | `2f6af19c47d04bfe745cd6d6d367d46555841bb4afcfccd961df0e1faa61a4bf` | ✅ |

All four retain their 2026-08-25 00:43 modification times from the run itself.
Nothing has written to that directory.

**Note on the two digests named `test_audit_sha256`.** The value above is the
SHA-256 of the `TEST_AUDIT.json` **file bytes**, which is what `TEST_ATTEMPT.json`
records under that name. `TEST_AUDIT.json`'s own field of the same name is
`79447d4da551d88f3c97389953c98e8edd3be2a682930cbcdde25525d7efb905`, which is
**self-referential** — the SHA-256 of the audit payload with that field removed,
`sort_keys=True`, `separators=(",", ":")`, the same rule the experiment locks
use. Both were recomputed and both match. **They are different numbers and both
are correct about themselves; say which one you mean.**

### 7.2 Development artifacts cited

| Artifact | SHA-256 |
|---|---|
| `VALIDATION_METRICS.json` | `87852fa5c3dcb0d05d2fe3124a384e408846f6b3fb8522a9cccd203ba5f26d06` |
| `EXPERIMENT_LOCK.json` (B4-B) | `5bf251780f469115164d61a3f3cef2eecfc9ef9765af3f544479e961da00e7bc` |
| `docs/B4_GLOBAL_ENCODER_SELECTION_V1.json` | `b40796848e8a28d5fc489101fe6ed2d04eb760ee1a354ff8dc9f182eb60df638` |
| `VALIDATION_CHALLENGE_RESULTS.json` | `8127f5a4a2a501f92fb47d100c561e15b4129670ef1d25acc236a1c0580ec672` |
| `U1_DEPLOYMENT_CALIBRATOR.json` | `acec97c1ebd3bed459ad2d75204b6c82f274b248edbb1d779b844bd46c62fdc1` |

---

## 8. What follows from this

Nothing in this document authorizes an experiment. The forward plan is
`docs/IMPROVEMENT_ROADMAP_V1.md`, which grants no permission either.

The one-line summary, for anyone who reads no further: **the encoder generalized
its ordering and failed to generalize its scale, and the component that would
bridge the two — a per-subject calibrator — does not exist in this programme.**
