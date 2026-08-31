# B4 · E11 Morphology-Aware Representation Generalization — Report, V1

Executed under `B4_E11_MORPHOLOGY_AWARE_REPRESENTATION_PLAN_V1.md` and its
approved pre-execution amendments A1–A8. **Development evidence only. The
sealed TEST partition was not opened and the historical 12-subject VALIDATION
partition was not used.** **Mechanism evidence only — no medical or diagnostic
claim follows from anything here.**

**Headline: the registered mechanism is NOT ESTABLISHED.** All three primary
geometry endpoints moved in the predicted pooled direction, and all three
paired confidence intervals include zero. Per-fold effects are heterogeneous in
sign. **Registered interpretation: Category C.**

**The replication is the durable result.** E10's central geometry finding
reproduces on **44 evaluable held-out subjects** under a prospective
subject-disjoint design, against the 9 subjects E1–E10 were confined to.

---

## 1. Research question and registered hypothesis

**Hypothesis, as registered:** a training-only auxiliary objective preserving
signed ST morphology improves the stability and magnitude of the ischemia class
direction on unseen subjects, versus the otherwise identical B4-B recipe.

E11 exists because of E10, which established two distinct held-out failure
modes — **direction reversal** and **direction collapse** — and showed the
frozen head to be faithful: the head maps whatever direction the representation
supplies. **The representation, not the head, is the failure surface.** E11 asks
whether a morphology-aware auxiliary term repairs that surface.

**The primary endpoint is geometry, not AUPRC** (§4). Performance is secondary
(§5), and §7 registers Outcome B — mechanism support without established
predictive gain — as the most likely outcome in advance.

---

## 2. Authorization / execution provenance

| | |
|---|---|
| Attempt | **E11 ATTEMPT 2** |
| Started / finished | 2026-08-26T19:54:43Z → **2026-08-27T00:57:30Z** |
| Total arm wall time | 18,160.8 s = **5.04 h** |
| `failure_state` | **null** |
| Repository commit | `1037ea18830a`, working tree **clean** |
| Split digest | `ce037309cc2d67944acbee76e82700e5a54c9d2ff69bf54a121ab1b8940206c3` — verified before launch |
| `morphology.py` sha256 | `1cdfe3ed1bc23893d250c7b38da3a9341e9f8a34823c135a5ff10ca93d676e21` |
| `test_partition_opened` | **false** |
| `test_authority_constructed` | **false** |
| Historical VALIDATION subjects used | **0** |

**ATTEMPT 1 was an experimental-apparatus failure**, classified as such by the
authorizing human, with **no scientific attempt consumed**. Its root cause is
recorded in `B4_E11_ATTEMPT_1_FAILURE_RECEIPT_V1.md`: the auxiliary loss masked
invalid rows by multiplication, and **`NaN * 0 == NaN`**. ATTEMPT 2 applies that
receipt's §4 correction — index selection rather than multiplicative masking —
plus an `isfinite(loss)` assertion after every batch. **No scientific parameter
changed:** target, λ, seed, architecture, split and nested protocol are
identical.

**Reproduction gate.** ATTEMPT 2 was required to reproduce ATTEMPT 1's fold-0
B0 held-out values before proceeding. It did so **bit-for-bit**:

```
observed AUPRC 0.6890742403094241    delta 0.0
observed AUROC 0.8171366847505979    delta 0.0
bitwise_identical: true
```

**ATTEMPT 1's fold-0 B0 result is QUARANTINED** and is used nowhere in this
report except as that apparatus gate.

**Artifact preservation.** All six fold/arm NPZ artifacts, both receipts, the
complete execution log and the protocol metadata are preserved under
`cardiosentinel-runs/b4-e11-morphology-aware-v1/E11_ATTEMPT_2/`,
**17 files, 1,095,951,778 bytes, every source/destination SHA-256 pair equal**.

```
manifest digest: 5d357209005bf1571e3a740219dd89f6cd770ea62ee00b17c6c9806985f49359
```

---

## 3. Dataset and prospective 3-fold subject-disjoint design

All E11 evaluation happens **inside the original 56 TRAIN subjects**. The
historical 12-subject VALIDATION partition is spent for confirmatory purposes
and is not used at all.

The assignment is deterministic and independent of any model outcome: subjects
sorted by TRAIN-side ischemic window prevalence, ties by subject id, then
serpentine-assigned to 3 folds. **56 subjects, 12 of them zero-positive, 44
evaluable.**

| fold | subjects | evaluable | held-out rows | prevalence | evaluable held-out streams |
|---|---|---|---|---|---|
| 0 | 19 | 15 | 149,042 | 0.2935 | 30 |
| 1 | 19 | 15 | 118,628 | 0.2601 | 26 |
| 2 | 18 | 14 | 106,782 | 0.1781 | 23 |

**Totals: 44 evaluable subjects, 79 evaluable held-out streams** — matching the
A6 preflight (15/15/14) exactly.

**Prevalence differs materially across folds (1.65×) and is registered, not
hidden.** AUPRC is bounded below by prevalence, so per-fold AUPRC is reported
with its prevalence beside it and **is never compared across folds**.

**Nested selection (§3.3, A2).** Fixed epoch counts were rejected as
contaminated: B4-A/B/C selected epochs 4/2/2 by maximum AUPRC on the very
partition E11 exists to avoid. Within each fold's outer-training subjects, the
lowest third by the frozen serpentine order is held out for checkpoint
selection only, by the frozen B4 rule (maximum inner pooled AUPRC, earliest
epoch wins ties), applied identically to both arms.

**Note on scale.** The run operates on the registered `b4-waveform-v1` cached
window set (374,452 rows). Its prevalences are therefore not those of the raw
corpus, and **no absolute AUPRC here is comparable to any historical B4
figure** — §3.3 forbids that comparison independently.

---

## 4. Intervention: B0 vs B1

| Arm | Definition |
|---|---|
| **B0** | the original B4-B recipe under the nested subject-disjoint E11 protocol |
| **B1** | B0 **+** `Linear(128→1)` auxiliary head on the `encode()` tap, target **`post_r_80ms_delta_mv`**, **λ = 0.1**, fold-training median/IQR scaling. **Training-only — the head is discarded before any held-out evaluation** |

**Auxiliary-target provenance (A1, HARD GATE PASSED):**
`extract_morphology_features` takes one `CausalWindow`, never imports
`STEvent`, and bounds every index inside the window. The target is
**label-free, annotation-free and causal**. Four of 374,452 TRAIN rows have a
non-finite target; these are excluded from the auxiliary loss by index
selection.

**Pairing (A3).** Encoder initialization, primary-head initialization, batch
order, optimizer, primary loss, epoch budget and subject split are all paired.
B1 constructs the base model first with byte-identical RNG draws, then
initializes its auxiliary head from an isolated generator consuming **zero**
global RNG.

**What cannot be paired, stated rather than approximated:** weight trajectories
diverge from the first optimizer step, because B1's gradient includes the
auxiliary term — that is the intervention, not a pairing defect. **E11 V1 uses
one seed per arm per fold with no repeats, so an arm difference cannot be
separated from single-seed training variance.** Registered as a V1 limitation.

---

## 5. Primary geometry endpoints

Per fold and arm, the class-direction consensus is built from **that arm's own
outer-train embeddings only**, by E10's frozen aggregation — unit-normalise each
evaluable training stream's `delta`, average with equal weight per stream,
renormalise — and **frozen before any held-out row is embedded**.

### 5.1 TRAIN-side coherence — the replication

| fold | arm | train streams | cos min | cos med | cos < 0 | ‖delta‖ med |
|---|---|---|---|---|---|---|
| 0 | B0 | 49 | +0.9765 | +0.9944 | 0 | 9.609 |
| 0 | B1 | 49 | +0.8561 | +0.9927 | 0 | 8.649 |
| 1 | B0 | 53 | +0.9177 | +0.9935 | 0 | 9.241 |
| 1 | B1 | 53 | +0.8864 | +0.9892 | 0 | 8.307 |
| 2 | B0 | 56 | +0.9727 | +0.9941 | 0 | 8.980 |
| 2 | B1 | 56 | **−0.4625** | +0.9911 | **1** | 8.832 |

**B0 reproduces E10's TRAIN geometry** (E10: min +0.971, median +0.993, 0/79
negative). Registered prediction 1 is **confirmed**, now on a prospective
3-fold design rather than a single LOSO pass.

### 5.2 Held-out geometry — the primary endpoints

| fold | arm | streams | cos med | cos min | neg n | neg frac | ‖delta‖ med | within-subj med | subj |
|---|---|---|---|---|---|---|---|---|---|
| 0 | B0 | 30 | +0.9857 | −0.3626 | 1 | 0.0333 | 7.115 | +0.9921 | 9 |
| 0 | B1 | 30 | +0.9891 | −0.3502 | 1 | 0.0333 | 6.375 | +0.9940 | 9 |
| 1 | B0 | 26 | +0.9736 | −0.7449 | 1 | 0.0385 | 6.254 | +0.9721 | 10 |
| 1 | B1 | 26 | +0.9525 | **+0.1783** | **0** | **0.0000** | 6.380 | +0.9633 | 10 |
| 2 | B0 | 23 | +0.9777 | −0.9033 | 1 | 0.0435 | 5.704 | +0.9864 | 7 |
| 2 | B1 | 23 | +0.9693 | −0.6253 | 1 | 0.0435 | 5.950 | +0.9862 | 7 |

**Pooled across folds: B0 median cosine +0.9777 with 3/79 negative;
B1 median cosine +0.9807 with 2/79 negative.**

**The reduction is one stream, and it is unresolved.** The negative-direction
streams are identified:

| arm | fold | stream | subject | cos | ‖delta‖ |
|---|---|---|---|---|---|
| B0 | 0 | `s20171:0` | s2017 | −0.3626 | 1.076 |
| B0 | 1 | `s20101:1` | s2010 | −0.7449 | 2.589 |
| B0 | 2 | `s20021:1` | s2002 | −0.9033 | 2.246 |
| B1 | 0 | `s20171:0` | s2017 | −0.3502 | 2.185 |
| B1 | 2 | `s20021:1` | s2002 | −0.6253 | 3.198 |

**Both arms fail on the same two streams.** The single difference is
`s20101:1`, which B1 moves from −0.7449 to +0.1783. **Representation reversal
remains a minority unseen-stream phenomenon under both arms** — 3.8% and 2.5%
of evaluable held-out streams respectively.

### 5.3 Observed secondary diagnostic — B1's fold-2 TRAIN stream

**B1's fold-2 consensus contains one negative-cosine TRAIN stream**, where B0
has none negative in any fold:

```
stream s20471:1   subject s2047   cos -0.4625   ||delta|| 2.582
                  2,917 windows,  12 positives
```

**This is an observed diagnostic, not a registered mechanism endpoint**, and it
is not used in any contrast. Recorded because it is the only TRAIN-side
negative direction anywhere in the run, and because the stream's delta is
estimated from **12 positive windows**, which is stated as a property of the
stream rather than as an explanation of the value.

### 5.4 The deleted category

**"Class-direction collapse" was NOT computed, and was not missing.**
Amendment **A4 explicitly deleted the categorical collapse endpoint from §4**
before ATTEMPT 2, on the ground that no defensible TRAIN-only threshold exists:
a single order statistic over ~50 fold-training streams is unstable, and E10
showed held-out `‖delta‖` medians run about half of TRAIN's for distributional
reasons unrelated to collapse. **`‖delta‖` is retained as a continuous
endpoint** and is reported above. **No geometry threshold was introduced after
ATTEMPT 2 outcomes existed.**

---

## 6. Paired uncertainty

Registered §6 construction: **subject-level paired bootstrap over the 44
evaluable TRAIN subjects, 1,000 replicates, seed 2026**, each subject appearing
in exactly one held-out fold. **Windows are never treated as independent
replicates, and neither are streams.**

| primary endpoint (B1 − B0) | point | 95% CI | verdict |
|---|---|---|---|
| median cosine | **+0.0030** | [−0.0178, +0.0073] | **includes zero** |
| median ‖delta‖ | **+0.1217** | [−0.5993, +0.5617] | **includes zero** |
| negative-cosine fraction | **−0.0127** | [−0.0406, +0.0000] | **includes zero** |

**All three primary geometry endpoints fail to separate.** All three point
estimates lie in the direction predicted by registered predictions 2 and 3.

**The intervals are wide, exactly as E6a anticipated.** The `‖delta‖` interval
spans roughly ±0.6 around a point estimate of +0.12 — the instrument cannot
resolve an effect of this size at 44 subjects. The negative-fraction interval's
upper bound sits **exactly at zero** because the statistic is a count over 79
streams: one stream is ≈0.0127, so the endpoint is quantized at approximately
the size of the observed effect.

---

## 7. Secondary predictive endpoints

**Prevalence accompanies every AUPRC. Cross-fold AUPRC comparison is invalid
and is not performed.**

| fold | arm | prev | pooled AUPRC | pooled AUROC | subj-macro AUPRC | subj-macro AUROC | denom | stream AUROC med | streams |
|---|---|---|---|---|---|---|---|---|---|
| 0 | B0 | 0.2935 | 0.6891 | 0.8171 | 0.6617 | 0.8966 | 15/19 | 0.9293 | 30 |
| 0 | B1 | 0.2935 | 0.6795 | 0.8136 | 0.6747 | 0.8740 | 15/19 | 0.9273 | 30 |
| 1 | B0 | 0.2601 | 0.7843 | 0.8687 | 0.6715 | 0.8816 | 15/19 | 0.9395 | 26 |
| 1 | B1 | 0.2601 | 0.7940 | 0.8763 | 0.7117 | 0.9044 | 15/19 | 0.9402 | 26 |
| 2 | B0 | 0.1781 | 0.6599 | 0.9004 | 0.6725 | 0.9017 | 14/18 | 0.9163 | 23 |
| 2 | B1 | 0.1781 | 0.6902 | 0.8949 | 0.6967 | 0.9054 | 14/18 | 0.9303 | 23 |

Paired subject bootstrap, same construction (44 subjects, 1,000 replicates,
seed 2026):

| secondary endpoint (B1 − B0) | point | 95% CI | verdict |
|---|---|---|---|
| **subject-macro AUPRC** | **+0.0258** | **[+0.0002, +0.0562]** | **nominally excludes zero** |
| subject-macro AUROC | +0.0013 | [−0.0182, +0.0180] | includes zero |

B1 exceeded B0 on subject-macro AUPRC for **29 of 44 subjects**.

**This result is, explicitly:**

- **secondary** — not the registered primary mechanism endpoint;
- **nominally separated** — the interval excludes zero as computed;
- **fragile** — the lower bound is **+0.0002**, two ten-thousandths from zero,
  and is the 25th ordered value of 1,000 bootstrap replicates;
- **unsupported by the registered primary mechanism**, all three of whose
  endpoints include zero.

**It is not the headline result of E11 and must not be reported as one.**

---

## 8. Fold heterogeneity

**Per-fold effects are heterogeneous in sign on every endpoint, and are
reported exactly as observed.**

| fold | Δ cos median | Δ ‖delta‖ median | Δ neg fraction | Δ pooled AUPRC | Δ pooled AUROC |
|---|---|---|---|---|---|
| 0 | +0.0035 | **−0.7401** | 0.0000 | −0.0096 | −0.0035 |
| 1 | −0.0211 | +0.1260 | **−0.0385** | +0.0097 | +0.0076 |
| 2 | −0.0084 | +0.2457 | 0.0000 | +0.0303 | −0.0055 |

**Fold 0's `‖delta‖` moved against the registered prediction**, and folds 1 and
2 moved with it. **Median cosine improved only in fold 0** and declined in the
other two, while the pooled median cosine improved — pooled and per-fold
directions do not agree.

**Training dynamics also varied materially:**

| fold | arm | phase-1 epochs | selected epoch | phase-2 epochs | wall (s) |
|---|---|---|---|---|---|
| 0 | B0 | 5 | 1 | 1 | 2,180.3 |
| 0 | B1 | 5 | 1 | 1 | 2,207.9 |
| 1 | B0 | 5 | 1 | 1 | 2,486.2 |
| 1 | B1 | 6 | 2 | 2 | 3,326.0 |
| 2 | B0 | 8 | **4** | 4 | 5,247.7 |
| 2 | B1 | 5 | 1 | 1 | 2,712.7 |

**Four of six fits selected epoch 1**, reproducing the overfit-within-2-4-epochs
signature E2 measured on this recipe. **Most of this contrast is therefore
between one-epoch encoders**, which is a property of the frozen B4-B recipe and
not of E11. Fold 2 B0 is the exception at epoch 4, and cost 2.4× the wall time
of the cheapest fit.

---

## 9. Protocol deviations

### 9.1 The registered operating-point endpoint could not be computed

**This is a runner / protocol implementation gap, and it is the one real
deviation in E11 ATTEMPT 2.**

§5 registers sensitivity and specificity **only at a training-derived frozen
operating point** — the inner split's F1-optimal threshold, fixed before the
outer fold is scored and never re-derived. **The ATTEMPT 2 runner did not
persist what that endpoint requires:**

- the **inner-validation F1-optimal threshold** was never written to the
  execution receipt (per-arm keys are `held_out_auprc`, `held_out_auroc`,
  `inner_auprc`, `phase1_history`, `phase2_history`, `scaler_inner`,
  `scaler_outer`, `selected_epoch`, `wall_seconds`);
- the **inner-validation predictions** needed to reconstruct it were not saved
  (NPZ keys are `emb_ho`, `score_ho`, `emb_ot`, `idx_ho`, `idx_ot`);
- the phase-1 model is discarded by construction.

**The endpoint is therefore not computable from the preserved artifacts, and
was not computed.** Specifically, and deliberately:

- **no threshold was derived from held-out scores** — that would be circular
  and is forbidden by §3.2;
- **the discarded phase-1 model was not reconstructed**;
- **no substitute operating point was introduced.**

The gap is inherited from the ATTEMPT 1 runner and **was not introduced by the
masking correction**. Any future E11-class runner must persist the inner
threshold at selection time.

### 9.2 The collapse endpoint was deleted, not missing

**The categorical collapse endpoint is absent by registration, not by
omission.** Amendment **A4 deleted the category from §4 before ATTEMPT 2
existed**, and `‖delta‖` was retained as a continuous endpoint in its place.
This is recorded here so that no future reader treats its absence as an
analysis failure or a post-hoc exclusion.

### 9.3 Recorded, not deviations

- **Fold prevalences reflect the registered `b4-waveform-v1` cached window
  set**, not the raw corpus. Execution is correct; the consequence is that
  absolute AUPRC values here are not comparable to raw-corpus or historical B4
  figures.
- **No sealed TEST artifact was opened**; `test_partition_opened` and
  `test_authority_constructed` are both `false` in the receipt.
- **No historical VALIDATION subject was used.**
- **No endpoint definition, threshold or exclusion was introduced after
  outcomes existed.**

---

## 10. Interpretation against the preregistered A–E categories

| Outcome | Registered reading |
|---|---|
| A | geometry **and** performance improve |
| B | geometry improves, performance does not resolve |
| **C** | **performance changes without geometry improvement — does NOT support the registered mechanism** |
| D | neither improves |
| E | harm |

### **FORMAL INTERPRETATION: CATEGORY C — performance changes without established geometry improvement.**

The classification rests on four statements, each of which must be carried
together:

1. **All three primary geometry point estimates moved in the predicted pooled
   direction** — median cosine +0.0030, median `‖delta‖` +0.1217,
   negative-cosine fraction −0.0127.
2. **All three confidence intervals include zero.**
3. **Per-fold effects are heterogeneous in sign**, and fold 0's `‖delta‖` moved
   against the prediction.
4. **Therefore the registered mechanism is NOT ESTABLISHED.**

**Category C here means *failed to establish*, not *evidence against*.** The
directional agreement of all three point estimates is recorded, and it is not
sufficient — under the registered uncertainty construction, none of it
separates.

**The result must not be generalized.** Per A5, a null in E11 means exactly:
**"no established benefit for this preregistered morphology-aware formulation
at λ = 0.1."** **It is not evidence that morphology-aware representation
learning is ineffective in general.**

Registered predictions, scored:

| # | Prediction | Outcome |
|---|---|---|
| 1 | B0 reproduces E10's qualitative geometry | **Confirmed** |
| 2 | B1 shows fewer negative-cosine held-out streams | **Directionally right (3→2), unresolved** |
| 3 | B1's median `‖delta‖` exceeds B0's | **Directionally right pooled, unresolved, reversed in fold 0** |
| 4 | Pooled AUPRC will not separate | **Partially contradicted** — subject-macro AUPRC nominally separated |
| 5 | Collapse streams respond less than reversal streams | **Not applicable** — endpoint deleted by A4 |

---

## 11. Scientific conclusion

**E11 ATTEMPT 2 executed the registered protocol cleanly and did not establish
the registered mechanism.** A signed-morphology auxiliary objective at λ = 0.1,
applied training-only to the B4-B encoder, produced no resolvable improvement in
unseen-stream class-direction stability under a prospective 3-fold
subject-disjoint design.

**What E11 does establish is a replication.** E10's central geometry finding —
the class direction is highly coherent across training streams while a minority
of held-out streams reverse — reproduces on **44 evaluable subjects and 79
evaluable held-out streams**, against the 9 subjects E1–E10 were confined to.
TRAIN-side median cosine is ≈ +0.99 with **zero** negative streams in 49–56
streams per fold under B0, and held-out reversal affects **3 of 79 streams for
B0 and 2 of 79 for B1**. **The head is faithful; the representation fails on a
minority of unseen streams — and this auxiliary objective did not measurably
repair that.**

**This is the largest honest unit count the programme has had, and it is still
small.** E6a's finding applies directly: the intervals are wide, and E11's
inability to resolve a geometry effect is as much a statement about the
instrument as about the intervention.

---

## 12. Explicit non-claims

**E11 does not claim, and must not be cited as claiming:**

1. **Any medical or diagnostic performance.** This is development evidence on a
   research corpus. No clinical claim of any kind follows.
2. **That morphology-aware representation learning does not work.** The
   registered scope of this null is one target, one λ, one architecture, one
   seed per arm per fold. Per A5: *"no established benefit for this
   preregistered morphology-aware formulation at λ = 0.1."*
3. **That B1 improves predictive performance.** The subject-macro AUPRC
   interval nominally excludes zero with a lower bound of +0.0002. It is
   secondary, fragile, and unsupported by the primary mechanism endpoints.
4. **That B1 improves held-out geometry.** All three primary intervals include
   zero. Directional agreement of point estimates is not establishment.
5. **That B0 and B1 differ beyond single-seed training variance.** A3 registers
   that E11 V1 cannot separate the two — one seed per arm per fold, no repeats.
6. **Any held-out generalization estimate for LTSTDB.** No held-out estimate is
   obtainable within LTSTDB, permanently. The sealed B4-B test is consumed and
   is not re-openable.
7. **Anything about the historical 12-subject VALIDATION partition.** It was not
   used in E11.
8. **That fold-2's B1 TRAIN stream `s20471:1` indicates a mechanism.** It is an
   observed diagnostic on a stream with 12 positive windows, outside every
   registered endpoint.

**Nothing in E1–E10 is revised by this report.**
