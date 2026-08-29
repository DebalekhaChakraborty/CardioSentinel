# CardioSentinel — Canonical Experiment / Component Mapping

Read-only reference document. Nothing in the repository was modified, no experiment run, no model retrained, no sealed TEST accessed to produce this document. Every substantive claim below traces to a primary source cited in its own row or paragraph — code was read directly wherever a code-level fact is asserted, not inferred from prose summaries.

---

## 0. Repository state used

```
branch: chore/document-hierarchy-migration-v2
HEAD:   61cc553473180ce68f33bf9c3002addc74b20340
status: an in-progress, uncommitted documentation-hierarchy migration
        (paper/, handbook/, handoffs/ being moved under docs/); every
        content diff checked in prior sessions was a single-line path
        update, never a scientific change.
```

**This is a documentation-migration branch, and it does not change any scientific interpretation below.** Every number, class name, and decision cited here was read from the current file locations on this branch (mostly under `docs/experiments/*` and `src/cardiosentinel/neural/*`), which are the same underlying documents the migration is relocating, not rewriting.

---

## 1. Executive overview

CardioSentinel names its work using short family+number+suffix codes (`B4-B`, `M2-G`, `T1`, `G4`, `E11`) rather than descriptive names, because the codes are load-bearing identifiers in digest-bound experiment locks, run directories and test code — renaming them would break frozen provenance. This document exists because that convention, while precise for the system that enforces it, is opaque to a new reader.

**The single most important structural fact, stated once here and assumed everywhere below**: these codes name three genuinely different kinds of thing, and confusing the kinds is the most common way to misread the project:

1. **Experimental arms** — a specific configuration that was run once, evaluated, and compared against a sibling arm (`B4-A`, `M1S`, `M2-0`, `T2-GRU`). An arm is evidence, not necessarily code that runs today.
2. **Retained runtime components** — the specific arm that won its comparison and is the thing actually executing in the pipeline today (`B4-B`, `M1L`, `M2-G`, `T2-S4D`, `T1`). A retained component is *both* an experimental arm's name *and* a live module.
3. **Gate conditions and governance mechanisms** — sub-parts of a retained component that are not arms at all (`G1`–`G6` are six conditions inside the single retained `M2-G` policy, not six experiments).

Section 15 makes this classification exhaustive and explicit for every identifier in the project.

---

## 2. Naming convention

### 2.A. What the first letter denotes

| Letter | Practical meaning in this project | Official expansion found in source? |
|---|---|---|
| **B** | Baseline / representation-learning programme (B0–B4) | **Practical mnemonic only.** No file defines "B = Baseline" as a formal acronym; the repository always writes it out in prose ("classical baselines," "the neural representation family") rather than expanding the letter. |
| **P** | Physiology-fusion stage | **Practical mnemonic only.** Same pattern — `physiology_fusion.py`'s own docstring never glosses the letter itself. |
| **M** | Memory / personalization stage (two sub-stages, M1 and M2) | **Practical mnemonic only.** |
| **U** | Uncertainty / calibration stage | **Practical mnemonic only.** |
| **T** | Temporal-reasoning stage (two sub-stages, T2 then T1 — see §2.B) | **Practical mnemonic only.** |
| **W** | Window comparator (the memoryless ablation arm, W1) | **Practical mnemonic only.** |
| **E** | Experiment/investigation series (E1–E13a) | **Practical mnemonic only.** |
| **G** (in `M2-G`) | "Gated" | **Practical mnemonic only** — and see §2.C for why this is a *different* G from `G1`–`G6`. |
| **G1–G6** | Six numbered gate *conditions*, not a letter-family at all | Not an acronym; these are simply numbered items in a frozen ordered tuple, `CONDITION_ORDER = ("G1","G2","G3","G4","G5","G6")` (`m2_policy.py:120`). |

**No source document in this repository formally states "B stands for Baseline" or an equivalent for any letter above.** Every classification in this table was checked against the modules and protocols that define each family, and in every case the letter is used as a bare identifier prefix, glossed only by surrounding prose, never by an explicit "X = Y" acronym definition. Treat every letter meaning in this document as a **practical mnemonic supplied by this documentation effort**, not a project fact, unless a row says otherwise.

### 2.B. What the number means — and why T2 precedes T1

The number after a family letter identifies a **stage or generation within that family**, not a chronological execution rank across families. Two numbers from *different* families are not comparable at all — `T2`'s "2" and `M2`'s "2" do not mean "the second thing that happened."

**Why T2 (temporal score) feeds T1 (episode state) even though 2 > 1**: actual execution order is governed by the project's `phaseN-*` run-directory naming, not by the `T` family's internal numbering:

```
phase3b-classical-v3        (B0–B3)
phase3b2-b4-v1               (B4-A)
phase3b2-architecture-v1     (B4-B, B4-C selection)
phase4-p1-physiology-v1      (P1-A/B)
phase5-m1-dual-memory-v2     (M1S/M1D/M1L)
phase6-m2-development-v1     (M2-0/M2-G)
phase7-u1-development-v1     (U1 Platt / router)
phase8-t2-development-v1     (T2-GRU / T2-S4D)   <-- executes here
phase9-t1-development-v1     (T1)                <-- executes here, after T2
```

(Source: `docs/control-plane/EXPERIMENT_CATALOGUE.md` §1, "Where the experiments live.") T2 is **Phase 8**; T1 is **Phase 9**. T1's own transition function then takes T2's continuous output (`s4d_temporal_evidence_s_t`) as one of its nine allowed inputs (`t1_protocol.py:158–168`, verified directly — see §11). The "1" and "2" in `T1`/`T2` are a within-family generation label chosen by the authors, not a phase or execution-order number; the actual order is T2 (Phase 8) → T1 (Phase 9).

### 2.C. What suffixes mean — strictly local to each family

**This is the single most important disambiguation in this document, and it is stated explicitly because getting it wrong is the most common real confusion.**

| Suffix pattern | Family | What it means *in this family only* |
|---|---|---|
| `-A`, `-B`, `-C` | `B4-A/B/C` | Three **architecture candidates** compared under one protocol |
| `-A`, `-B` | `P1-A/B` | Two **matched experiment arms** (neural-only control vs. fusion arm) |
| `S`, `L`, `D` | `M1S/M1L/M1D` | **Short**, **Long**, **Dual** memory *timescale* variants |
| `-0`, `-G` | `M2-0/M2-G` | **N**aive control (0) vs. **G**ated policy — an entirely different use of the letter "G" from `G1`–`G6` |
| `1`–`6` | `G1`–`G6` | Six ordered **gate conditions** inside the one retained `M2-G` policy — not experiment arms at all |
| `-A`, `-a` | `E7a`, `E7b`, `E12a`, `E12d`, `E13a` | A **sub-investigation** of the numbered parent experiment, run later, not a competing arm |

**The letter "B" in `B4-B` does not mean the same thing as the letter "B" in `P1-B`.** `B4-B` is architecture candidate B (second of three: A, B, C). `P1-B` is experiment arm B (second of two: A, B — the fusion arm). They are alphabetically adjacent by coincidence of each family independently choosing to letter its second-listed arm "B."

**The "G" in `M2-G` is not `G4` and is not any of `G1`–`G6`.** `M2-G` is the name of the *retained policy as a whole* ("Gated"). `G1`–`G6` are the six *conditions evaluated inside* that policy every time it considers admitting an update. `M2-G`'s existence is a single retention decision (§8); `G4` passing or failing is a per-row, per-microsecond runtime event that happens continuously while `M2-G` runs (§9).

---

## 3. Baseline / representation family — B0 through B4

### 3.1 B0–B3 — classical, non-neural baselines

| | B0 | B1 | B2 | B3 |
|---|---|---|---|---|
| Plain-English name | Constant-prior predictor | Signal-only logistic regression | Signal + morphology logistic regression | Signal + morphology HistGradientBoosting |
| Input | none (predicts the training prevalence) | raw-signal-derived features only | signal + morphology features | signal + morphology features |
| Model family | constant | linear (logistic) | linear (logistic) | gradient-boosted trees |
| Output | one constant score | probability-like score | probability-like score | probability-like score |
| Stage | `phase3b-classical-v3` | same | same | same |
| Comparator role | the floor every other model must beat | — | — | **the strongest classical comparator; what B4-B is measured against on sealed TEST** |
| TEST status | sealed, consumed | sealed, consumed | sealed, consumed | sealed, consumed |
| Sealed pooled AUPRC | 0.0460529 | 0.1172989 | 0.1640117 | **0.1682901** |

Source: `docs/control-plane/CURRENT_STATE.md` §4 sealed-test comparator table; code at `src/cardiosentinel/models/` and `src/cardiosentinel/baseline/`.

### 3.2 B4 — the neural representation family, not a single model

**B4 is a stage name for a family of three architecture candidates, not one architecture.** The frozen protocol document, `docs/experiments/b4/B4_ARCHITECTURE_SELECTION_PROTOCOL_V1.md`, exists precisely because three distinct candidates had to be compared under identical rules before one could be called "the B4 encoder."

All three candidates share an **identical convolutional front end** (`SharedLocalFrontEnd` in `src/cardiosentinel/neural/candidates.py:71` — a strided stem convolution plus four depthwise-separable downsampling blocks, byte-identical to B4-A's own stem), so the *only* experimental variable across the three is the temporal block that consumes the resulting 79×128 token sequence. This shared-front-end design is itself deliberate engineering, not incidental.

---

## 4. B4-A / B4-B / B4-C — deep mapping

| | B4-A | **B4-B (retained)** | B4-C |
|---|---|---|---|
| Exact class | `B4CompactCNN` (`neural/model.py:66`) | `B4BTransformerCNN` (`neural/candidates.py:160`) | `B4CSSMCNN` (`neural/candidates.py:297`) |
| Human-readable architecture | Compact single-channel CNN (stem + 4 depthwise-separable blocks + 3 dilated residual context blocks) | Shared CNN front end + **2-block pre-norm Transformer encoder** (4 heads, model dim 128, feed-forward dim 256, learned positional embedding) | Shared CNN front end + **2-block diagonal gated state-space model, S4D-inspired** (complex64 diagonal linear recurrence, state dim 16, no positional embedding — order is inherent to the recurrence) |
| CNN front end | Own (B4-A is the historical frozen source the shared front end was rebuilt to match byte-for-byte) | Shared (`SharedLocalFrontEnd`) | Shared (`SharedLocalFrontEnd`) |
| Transformer / SSM content | None | `PreNormTransformerBlock` × 2, `nn.MultiheadAttention` | `DiagonalGatedSSMBlock` × 2 — explicitly **not Mamba**: "the state transition is diagonal, time-invariant and input-independent, so there is no selective mechanism" (module docstring, `candidates.py:205–212`) |
| Trainable parameters | 87,089 | 309,809 | 155,313 |
| FP32 payload | 348,356 B | 1,239,236 B | 621,252 B |
| Median latency (frozen benchmark host) | 3.274761 ms | 4.1613225 ms | 14.4363955 ms (deliberately unoptimized 79-step Python recurrence) |
| Development pooled validation AUPRC | 0.3156014611186772 | **0.38053499010488423** | 0.3377705149052735 |
| Subject-macro AUPRC (9 contributing) | 0.3658236963081271 | 0.40063630025780333 | **0.4033236569167703** (numerically highest of the three) |
| Rate-related challenge FPR | 0.3457 | **0.3312** (best) | 0.4651 |
| Axis-shift challenge FPR | 0.1020 | **0.0617** (best) | 0.1177 |
| Selected epoch (of how many trained) | 4 of 8 | 2 of 6 | 2 of 6 |
| Sealed TEST evaluated? | **No** | **Yes — the only candidate ever evaluated on sealed TEST** | **No** |
| Final status | Retained as "the efficient required CNN reference" | **Selected global encoder (development), then the sole sealed-TEST subject** | Retained as "a scientifically useful negative/alternative architecture result" |

**Primary source for every number above**: `docs/experiments/b4/B4_GLOBAL_ENCODER_SELECTION_V1.md` §5–§7 (the development-selection decision) — re-verified against source code across three prior review sessions.

### 4.1 Development selection vs. sealed generalization — kept strictly separate

**These are two different evidentiary events, in this order, and the paper and this document must never let them blur:**

1. **Development selection** (`B4_GLOBAL_ENCODER_SELECTION_V1.md`): all three candidates scored on the 12-subject **development/validation** partition, *before* any sealed-TEST access existed. B4-B won on pooled AUPRC and challenge robustness. `docs/experiments/b4/B4_GLOBAL_ENCODER_SELECTION_V1.md` §10 records explicitly: `test_evidence_used: false`, sealed B4 test **UNOPENED** at the time of this decision.
2. **Sealed generalization test** (`docs/control-plane/CURRENT_STATE.md` §4; `cardiosentinel-runs/phase3b2-architecture-v1/B4B_cnn_transformer_v1/TEST_*`): only B4-B, the already-selected architecture, was later evaluated once on the sealed TEST partition. Pooled AUPRC **0.0935334** at prevalence **0.0460529**, **below** B3's sealed 0.1682901.

**B4-B was not retrospectively chosen after seeing sealed evidence — it could not have been, because B4-A and B4-C were never granted sealed access at all.** The negative sealed result characterizes the one architecture that earned the one available sealed-test attempt; it says nothing about whether B4-A or B4-C would have generalized better or worse, because neither was ever tested.

---

## 5. Physiology family — P1

**Scientific question**: does adding explicit physiology/morphology information to the frozen neural embedding improve the development trade-off?

| | P1-A (matched control) | **P1-B (retained)** |
|---|---|---|
| Input | frozen 128-d B4-B embedding only | frozen 128-d B4-B embedding **+ 18-d transformed physiology vector** = 146-d fused representation |
| Architecture | `P1FusionHead(EMBEDDING_DIM)` | `P1FusionHead(EMBEDDING_DIM + PHYSIOLOGY_DIM)` — same class, wider input |
| Fusion type | n/a | **Late fusion**: concatenation before a shared small MLP head (`Linear → SiLU → Dropout → Linear → 1`), verified at `physiology_fusion.py:307–335` |
| Encoder fine-tuned? | No | No — `"encoder": "frozen B4-B; not fine-tuned"` (`p1_training_configuration()`) |
| Development pooled AUPRC | 0.3372201051523283 | **0.3752480844977594** |
| Descriptive difference | | **+0.03803** |
| Subject-macro AUPRC | ≈0.39403 | ≈0.40954 |
| Deployment parameter cost | | +1,152 parameters, +4,608 FP32 bytes |
| Rate-related challenge FPR | | **worsened by +0.006032575909913518** — carried forward as an explicit caveat |
| Evidence stage | Development validation only | Development validation only |

Source: `docs/experiments/p1/P1_PHYSIOLOGY_RETENTION_DECISION_V1.md`, re-verified line-by-line in the most recent review pass. **Why P1-B was retained**: the AUPRC gain was judged worth the FPR caveat and the negligible parameter cost; this is a bounded-Pareto human decision, not a significance claim — the retention document itself states no hypothesis test was run.

---

## 6. Memory family — M1

**Scientific question**: which patient-relative memory architecture best supports personalization?

All three variants are built on `DualTimescaleMemory` (`patient_memory.py:506`) — a **causal exponential-moving-average (EMA) prototype** per `(record_id, channel_index)` stream, standardized through a **TRAIN-only-fitted** distance transform (`M1DistanceStandardizer`). The `prototype_disagreement` distance feature is always computed **before** the current window's own update is applied — "a window can never influence the prototype used to compute its own distance" (class docstring, code-verified).

| Suffix | Official semantics? | Memory timescale | Distance feature(s) exposed |
|---|---|---|---|
| **M1S** (Short) | **Verified in code**: `M1_FEATURE_COLUMNS_BY_EXPERIMENT` maps `M1S_short_memory_v2 → ("d_short",)` | Short-timescale prototype only | `d_short` |
| **M1L** (Long) | **Verified in code**: maps to `("d_long",)` | Long-timescale prototype only | `d_long` |
| **M1D** (Dual) | **Verified in code**: maps to `("d_short", "d_long")` | Both prototypes | `d_short`, `d_long` |

("Short/Long/Dual" is the natural reading of the letters and is confirmed by the code's own feature-column mapping — this is as close to an official expansion as any letter in this document gets, though the repository never writes "S = Short" as a standalone glossary line.)

| | M1S | M1D | **M1L (retained)** |
|---|---|---|---|
| Pooled AUPRC | 0.365077 (below the P1-B global control) | 0.381417 | **0.384796** |
| Sensitivity | — | **0.477390** (highest) | 0.453532 |
| AUROC | — | **0.912372** (highest) | 0.907570 |
| MCC | — | **0.371579** (highest) | 0.368887 |
| Subject-level FP distribution (median/q75/IQR/p90/max) | worst of the three | — | **tightest of the three** (0.007099 / 0.095497 / 0.093919 / 0.140859 / 0.191831) |
| Decision | **Not retained** — pooled AUPRC fell below the global control and every principal false-alarm measure was the worst of the three | **Not retained, but explicitly "Pareto-relevant and not dominated"** | **Retained** |

**Why M1L over M1D — the exact reasoning, not a summary.** M1D genuinely wins on sensitivity, AUROC and MCC. It was not retained because the prespecified M1 objective was *patient-specific baseline modelling that reduces false alarms without an unacceptable sensitivity penalty* — and on that specific axis, M1L's tighter subject-level false-positive distribution is what M1 was actually for. `M1_MEMORY_RETENTION_DECISION_V1.md` §4 states this as a bounded-Pareto judgement, not a claim that M1L dominates M1D on every metric — because it does not.

**Inherited cold-start limitation**: all three arms show **zero sensitivity** in the 0–5 minute stratum at their frozen operating thresholds (n=1,798 rows) — a patient prototype has no patient-specific history in the first minutes of a stream. This is recorded as a real, unresolved limitation of the M1 line as a whole, not specific to the retained arm, and it is explicitly carried forward rather than tuned away (§8 below shows the same limitation persists through M2).

Source: `docs/experiments/m1/M1_MEMORY_RETENTION_DECISION_V1.md`.

---

## 7. Memory update policy — M2

**The distinction that must never blur**: **M1 chooses *what* patient-memory architecture exists** (a design/selection question, answered once, at the architecture level). **M2 chooses *when* that memory is allowed to update** (a per-row, continuously-evaluated runtime policy, layered on top of the already-selected M1L architecture). M2 does not re-open the M1 architecture choice — `m2_policy.py`'s own module docstring states the B4-B encoder, the 146-d fused representation, the M1L head weights and the M1 distance standardizer are "all inherited unchanged from the frozen M1-v2 system. No classifier is retrained here."

| | M2-0 (naive control) | **M2-G (retained)** |
|---|---|---|
| Update rule | every AVAILABLE finite observation updates the prototype (identical call sequence to raw M1L) | update **only if all six G1–G6 conditions pass** (§8) |
| Refractory state | **does not exist** — "the naive control's causal state stays exactly equivalent to naive M1L" | 60-second re-armable refractory (G5) |
| Admission fraction | 0.9999878272 (effectively always) | **0.2184421307 (21.84%)** — not a trivial never-update policy |
| Maximum peak drift, ischemic | 1.3088318203 | **0.0023193737 — 99.82% reduction** |
| Maximum peak drift, HR-related | 1.0076068363 | **0.0398963001 — 96.04% reduction** |
| Maximum peak drift, unreadable-quality | 1.1560887735 | **0.4041660010 — 65.0% reduction** |
| Primary AUPRC | 0.3847955698 | 0.3845274603 (essentially unchanged, Δ −0.0002681095) |
| Sensitivity | 0.4535324579 | 0.4683280932 (+0.0148 absolute) |
| Background FPR | 0.0393946965 | 0.0424879883 (worse — a real, recorded trade-off) |

**Prototype drift is a contamination *proxy*, not clinical safety.** The metric is `sqrt(mean((mu_long(t) − mu_ref)**2))` — a distance in feature space between the evolving prototype and its reference state, measured over source-defined stress intervals (163 ischemic, 36 heart-rate-related, 4 unreadable-quality). The retention document's own explicit non-claim: "must not be upgraded to clinical safety... elimination of contamination." All of this is **development evidence**; the sealed TEST partition is untouched by M2 (`test_accessed: false` in every M2 artifact).

Source: `docs/experiments/m2/M2_UPDATE_POLICY_RETENTION_DECISION_V1.md`.

---

## 8. G1–G6 — complete gate mapping

**Stated once, plainly: G1–G6 are six conditions evaluated inside the single retained M2-G policy, every time a row is considered for a memory update. They are not six experiments, not six arms, and not six models.** A memory update is admitted only if every *applicable* condition evaluates to `True` — the gate is fail-closed, so any `None` (not-applicable) or `False` blocks admission.

All definitions below are read directly from `src/cardiosentinel/neural/m2_gate.py` and `m2_policy.py`, not from a prose summary.

| Gate | Exact formal condition (from code) | Data source | Plain-English meaning | If it fails | Row still scored? | Re-arms the 60 s refractory? |
|---|---|---|---|---|---|---|
| **G1** | `observation_state == OBSERVATION_AVAILABLE` | physical observation state | Does a physical observation exist for this row at all? | **G2–G6 become not-applicable** — refused by G1 alone, never reported as a simultaneous multi-gate failure | No | No |
| **G2** | the 146-d fused representation has the correct shape and every value is finite | the fused representation itself | Is the representation numerically usable? | Blocks update; downstream conditions with their own inputs (G3/G5/G6) are still evaluated | Depends on downstream gates | No |
| **G3** | hard precondition `finite_sample_fraction == 1.0`, then each of 6 declared `SIGNAL_V1` waveform-quality columns at or below its **frozen TRAIN Q99 upper bound** (5 independent constraints — two columns are bitwise identical in the frozen corpus) | waveform signal-quality-index (SQI) features: `flatline_fraction`, `repeated_value_fraction`, `derivative_outlier_fraction`, `high_frequency_power_ratio`, `powerline_ratio_50hz`, `powerline_ratio_60hz` | Is the waveform itself clean enough (not noisy/artifact-laden) to trust? | Blocks update | Can still be scored if other gates pass | No |
| **G4** | `score <= NORMAL_EVIDENCE_THRESHOLD` (0.0002997174742631614, derived at the TRAIN-only median) | the M1L detector score | Does this row's score look "normal" by a **much stricter** threshold than the classification decision threshold? | Blocks update | Can still be scored | **Yes** — "if the score exceeds the normal-evidence threshold, the refractory is re-armed for future rows" (`m2_policy.py:481–482`) |
| **G5** | `available_time >= refractory_until_before`, evaluated against the refractory state **before** this row | physical elapsed time (`(start_sample + 2500) / 250.0` seconds), never a window count | Has enough real time passed since the last "suspicious" (G4-failing) row? | Blocks update | Can still be scored | n/a (this *is* the refractory check) |
| **G6** | `morphology_valid == 1.0` | the `morphology_valid` column | Could the morphology features be computed for this row at all? | Blocks update | Can still be scored | **No** — `G6_ARMS_REFRACTORY = False`, code-verified constant |

**G3 — explicit non-claim.** G3 screens **artifact/noise**, not physiological normality: amplitude and rhythm features are *deliberately excluded* from its column set "because they vary legitimately with patient physiology, and G3 screens artifact/noise rather than selecting a physiological phenotype" (`m2_policy.py:201–203`).

**G4 — explicit non-claim.** `G4_SCORE_SEMANTICS` in code: *"uncalibrated model score; not a probability, confidence, uncertainty or conformal score."* The **classification threshold** (0.7554003000259399, inherited from M1L) and the **memory-admission threshold** (0.0002997174742631614) are two different numbers for two different purposes — the admission threshold is far stricter, by roughly three orders of magnitude, because "normal enough to score a class label" and "normal enough to trust as a memory update" are different questions.

**G5 — explicit non-claim.** `REFRACTORY_SEMANTICS` in code: *"memory-update safety refractory; NOT NORMAL/WATCH/EVENT/RECOVERY, not episode reasoning, not clinical persistence logic."* This is a completely separate mechanism from T1's state machine (§11), even though both involve a notion of "elapsed time since something."

**G6 — explicit non-claim.** G6 checks whether the morphology **features could be computed**, not whether the SQI passed (that is G3's job) and not whether the morphology looks normal.

**The conceptual distinction that resolves most confusion about this section**: *"not safe enough to learn from" (a G3/G4/G5/G6 failure) does not mean "not valid enough to score."* A row can fail every applicable gate and still receive a full classification score from the frozen model chain — it is only excluded from **updating the patient prototype**, never from being classified and, if warranted, alerted on.

Source: `src/cardiosentinel/neural/m2_gate.py` (constants), `src/cardiosentinel/neural/m2_policy.py` (evaluation logic, `evaluate_gate()` and `step()`), independently read and quoted in this session.

---

## 9. Uncertainty / calibration — U1

**U1 held two separable sub-decisions under one experiment stage**, and the project's own evidence map calls this out explicitly as something not to collapse.

### 9.1 U1 Platt calibration — retained

| | Uncalibrated (reference) | **Platt (retained)** |
|---|---|---|
| NLL | 0.231705 | **0.143708** |
| Brier | 0.063567 | **0.040344** |
| ECE (equal-width) | 0.063844 | 0.016991 |
| Classification decisions | — | **0 inherited-decision disagreements** — a monotonic transform verified to change no classification outcome at the frozen threshold |
| Rows | 473,897 out-of-fold | same |

### 9.2 U1 selective router — rejected

| | Value |
|---|---|
| Operating point | `c* = 0.90` |
| Positive-label escalation fraction | 0.5167375624190864 |
| Negative-label escalation fraction | 0.0800696045937263 |
| **Escalation asymmetry ratio** | **6.453604523726777** |
| Prespecified guard | `asymmetric_abstention_ratio = 3.0` |
| Decision | **`Retained: false`** — the router disproportionately escalates true-ischemic (positive-label) windows far more than negative ones, more than double the tolerated asymmetry |

**U1 as a whole was not a failure.** One component was retained cleanly (calibration — the programme's single cleanest, unconditional positive result); the other was built, evaluated against a gate written *before* the result existed, and correctly rejected. Both outcomes are evidence that the retention machinery works in both directions.

Source: `docs/experiments/u1/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md`, `U1_CALIBRATION_SELECTIVE_ROUTING_PROTOCOL_V1.md`, `U1_CALIBRATION_RELIABILITY_REPORT_V1.md`.

---

## 10. Temporal family — T2 (learned) and T1 (explicit state)

**T2 produces a continuous learned temporal score. T1 is a separate, deterministic, parameter-free state machine that consumes that score (among other inputs) to produce discrete episode states. They answer different questions and must never be described as the same mechanism.**

### 10.1 T2 — GRU vs. S4D

| | `CausalGRULongitudinal` (T2-GRU) | **`CausalS4DLongitudinal` (T2-S4D, retained)** |
|---|---|---|
| Class | `neural/t2_models.py:109` | `neural/t2_models.py:262` |
| Architecture | `nn.GRU`, 2 layers, dropout 0.10 (applied once, between layer 1 and 2 — GRU's own semantics, not incidental), strictly non-bidirectional (enforced by a raised error if violated) | 2 stacked `LongitudinalDiagonalSSMBlock`s — **the identical parameterization, discretization and initialization as B4-C's within-window SSM block, reused verbatim**, with the one change that state now persists across window calls instead of being discarded (§10.2) |
| Pooled outer-validation AUPRC | 0.294870 | **0.388085** |
| Difference (S4D − GRU) | | **+0.093215** |
| 95% paired subject-bootstrap interval | | **[−0.015229, 0.148951] — includes zero** |
| Median positive-run duration | 25.0 s | **10.0 s (more fragmented)** |
| Isolated single-window positive fraction | 15.9% | **49.6% (more fragmented)** |
| Selection basis | | `pooled_primary_validation_auprc` — a **predefined rule**, not a superiority claim |

**Score semantics**: `score_is_calibrated_probability: false` — T2's output is a bounded sigmoid score, not a probability. **What the fragmentation evidence means**: even though S4D's AUPRC is higher, its thresholded predictions are chattier (more, shorter positive runs) than GRU's — this is exactly the mechanism reason the project keeps an explicit T1 state layer on top of the continuous T2 score rather than alerting directly on it.

### 10.2 B4-C's SSM and T2's SSM — same family, different temporal scope, verified at the code level

| | B4-C's `DiagonalGatedSSMBlock` | T2's `LongitudinalDiagonalSSMBlock` |
|---|---|---|
| Scope | Within one 10-second window (79 local tokens) | Across successive window embeddings, for an entire subject stream |
| State persistence | **Discarded after every forward call** — "nothing is carried between windows or between calls" (docstring, `candidates.py:266–267`) | **Explicitly threaded in and out** across calls (`forward(self, tokens, state=None) -> (output, next_state)`) |
| Parameterization / discretization / initialization | Original | **"Reused verbatim"** from B4-C — stated directly in `t2_models.py`'s own class docstring |
| Selected as? | **Not selected** as the B4 encoder | **Selected** as the T2 temporal arm |

**Is it legitimate to say CardioSentinel explored structured state-space modeling at two temporal scopes?** Yes, and this is not an inference — it is close to a direct quotation of the project's own decision record: *"Rejecting B4-C as the short-window global encoder does NOT reject state-space models from the CardioSentinel architecture... The planned T2 longitudinal SSM is a distinct experiment... It remains a core planned CardioSentinel component and is untouched by this decision"* (`B4_GLOBAL_ENCODER_SELECTION_V1.md` §8, "SSM interpretation — important").

### 10.3 T1 — explicit episode-state semantics

**T1 is not a neural network.** It is a deterministic, parameter-free causal state machine (`NORMAL → WATCH → EVENT → RECOVERY`) implemented in `src/cardiosentinel/neural/t1_protocol.py` plus 27 supporting modules.

**Exactly nine inputs are allowed to reach the transition function** (`T1_ALLOWED_ROW_INPUTS`, `t1_protocol.py:158`, code-verified): `stable_id`, `m2g_detector_score`, `detector_decision_d_t`, `oof_calibrated_probability_p_t`, `decision_error_uncertainty_u_t`, **`s4d_temporal_evidence_s_t`** (T2's continuous output — the only thing that crosses from T2 to T1), `score_present`, `elapsed_stream_seconds`, `elapsed_state_seconds`.

**Fifteen inputs are explicitly forbidden** (`T1_FORBIDDEN_TRANSITION_INPUTS`, `t1_protocol.py:170`), including — importantly — `gru_score` and `s4d_binary_decision` and `t2_frozen_reporting_threshold`. **T1 never receives a binarized T2 decision or T2's own reporting threshold, only T2's raw continuous score.** `stable_id` is on the allowed list and is still never a predictive feature — its only use is deterministic tie-breaking.

**Three frozen persistence profiles exist**, each specifying how many consecutive available rows are needed to confirm a transition:

| Profile | watch_clear | event_confirm | event_release | re_event_confirm | recovery_clear | cold_event_confirm |
|---|---:|---:|---:|---:|---:|---:|
| CONSERVATIVE | 6 | 6 | 6 | 3 | 12 | 12 |
| BALANCED | 3 | 3 | 3 | 2 | 6 | 6 |
| **FAST (promoted)** | 2 | **2** | 2 | 1 | 3 | 4 |

Combined with the quantile grid `Q_WATCH = (0.90, 0.95)` and `Q_EVENT = (0.99, 0.995)`, there are `2 × 2 × 3 = 12` candidate policies in total (`T1_CANDIDATE_POLICY_COUNT`); the promoted policy is named `qw0.9_qe0.99_FAST`.

Source: `src/cardiosentinel/neural/t1_protocol.py` (lines 155–265, read directly in this session).

---

## 11. W1 — the memoryless comparator

**Purpose, in one sentence**: *what happens if the identical upstream evidence T1 consumes is interpreted memorylessly, at the exact same promoted operating point, with everything else held fixed?*

| | Arm T1 (stateful) | Arm W1 (memoryless) |
|---|---|---|
| Subject-macro episode F1 | **0.2524** | 0.0603 |
| Difference | | **+0.1921** |
| 95% paired subject-bootstrap interval | | **[0.0505, 0.3455] — excludes zero** |
| Upstream evidence | identical frozen trace, both arms | identical frozen trace, both arms |
| Operating point | `qw0.9_qe0.99_FAST` — **jointly tuned with the state machine in the loop** | same operating point, applied without state |

**Mandatory qualifier, never dropped**: *at the promoted operating point.* A separately, independently tuned memoryless detector was **never tested** — sweeping a new threshold for W1 would itself be new threshold generation, which the analysis plan explicitly excludes. **What the mechanism actually is**: T1's hysteresis produces fewer, longer runs once EVENT state is entered; W1 produces many short runs. Both hold "run dominance" (W1 produces at least as many predicted runs, in every fold) but not "alert-row dominance" — the pre-registered plan's reasoning about this was wrong and is reported as wrong, not silently corrected.

Source: `docs/experiments/w1/W1_WINDOW_COMPARATOR_REPORT_V1.md`.

---

## 12. E1–E13a — the representation-investigation branch

**These are investigations into *why* the selected B4-B representation fails to generalize on held-out subjects. None of them is a runtime module, and none of them revisits the B4 architecture-selection decision (§4) or the sealed TEST result.** Grouped thematically below; every row is a distinct, separately-documented investigation, not a restatement of "representation investigation."

### 12.1 Representation geometry and mechanism (E1, E9, E10)

| ID | Purpose | Evidence stage | Headline result | Decision |
|---|---|---|---|---|
| **E1** | Representation Gap Probe — is missing information the cause of held-out failure? | Development, confirmatory | **Negative/inconclusive.** All five registered contrasts include zero; the 12-subject cohort cannot separate "information absent" from "information present but unused" | No conclusion; the question remains open |
| **E9** | Lead / Polarity / Label-Semantics Audit | Development, read-only | Two headlines: (1) the binary target is **polarity-agnostic** by construction (elevation and depression both get the positive label); (2) the TRAIN partition contains **no stream-quality failures** to characterize, invalidating part of a planned design | Mechanism evidence only |
| **E10** | Representation-Geometry Audit | Development, read-only | **The geometry separates the failures completely; the frozen head is "innocent."** The three E9 failure streams are exactly the three lowest-alignment, smallest-magnitude, lowest-centroid-separation streams in validation, with no overlap against the other sixteen | Head is faithful; failure is representational, not a head defect |

### 12.2 Score-scale and cross-stream mechanism (E7a, E7b) — both closed negative

| ID | Purpose | Headline result | Decision |
|---|---|---|---|
| **E7a** | Does static per-subject score normalization fix pooling? | **Refuted in direction.** Static normalization does not narrow the pooling gap — it **widens** it; between-subject score scale carries real information, not just nuisance | Closed |
| **E7b** | Is a cross-stream location/scale offset the mechanism? | **Not supported.** Cross-stream discrimination is not consistently worse than within-stream; a stream oracle does not repair it; variation is discriminative quality, not offset | Closed — "close score-normalization personalization" |

### 12.3 Memory-mechanism and information probes (E7, E8a, E8b)

| ID | Purpose | Headline result | Decision |
|---|---|---|---|
| **E7** | Can existing personalization machinery reduce score-scale heterogeneity? | **The premise is false as stated** — at the time of this audit, `personalization/` was an empty package; no such machinery existed to test | Redirects the question rather than answering it |
| **E8a** | Do memory quantities identify unreliable windows/streams? | **Split verdict.** Identifies unreliable *windows* broadly (8/9 subjects, coherent mechanism); does **not** identify unreliable *streams* (correlation between upper-tail `d_long` and stream AUROC: **−0.028**) | Mechanism evidence only |
| **E8b** | Does M1 memory information survive conditioning on the B4 score? | **Largely survives.** Pooled `d_long` concordance falls from **0.8362** (unconditional) to **0.7119** (score-stratified) — a real drop, far from 0.5; broad across 7/9 evaluable subjects | Recommends (but does not itself execute) a further incremental probe |

### 12.4 Instrument feasibility (E6, E6a) — both negative for their own purpose

| ID | Purpose | Headline result | Decision |
|---|---|---|---|
| **E6** | Feasibility/design audit for a cross-fitted transfer instrument | **E6 proper should NOT be the next action** — costs ~30h compute, needs fresh authorization, and cannot narrow the confidence interval on B4-B at all as scoped | Gated by E6a instead of proceeding |
| **E6a** | One-hour precision analysis meant to gate E6 | **Negative for its own gating purpose** — cannot determine whether more subjects would resolve E1/E2's ambiguities | Closed; E6 never proceeded |

### 12.5 The morphology-intervention branch and its instrumented follow-ups (E11, E12a, E12d, E13a) — the largest, most recent, and most consequential sub-branch

| ID | Purpose | Evidence stage | Headline result | Decision |
|---|---|---|---|---|
| **E11 (ATTEMPT 1)** | Test whether a morphology auxiliary objective improves unseen-stream direction stability | Prospective, confirmatory | **Apparatus failure** (`NaN * 0 == NaN` in the auxiliary loss mask) — classified by the authorizing human as **no scientific attempt consumed** | Quarantined; not a scientific result |
| **E11 (ATTEMPT 2)** | Same question, re-run after the fix | Prospective, confirmatory, 44-subject/79-stream held-out population | **Category C — performance changes without established geometry improvement.** All three primary geometry contrasts include zero; a fragile secondary AUPRC gain (+0.0258, 95% CI lower bound +0.0002) is explicitly not the headline | **Category C**; does not establish the mechanism |
| **E12a** | Read-only audit: was checkpoint selection stable in E11? | Read-only audit of already-persisted training histories | 4/6 selected epochs are epoch 1; training-loss and AUPRC epoch ordering disagree in all six fits — **cannot distinguish a weak objective from a weak selection instrument** | **Decision C — no further conclusion**; does not revise E11 |
| **E12d** | Instrumented replication: had the auxiliary loss plateaued at the selected checkpoint? | Prospective replication, ATTEMPT 2 (ATTEMPT 1 quarantined as a harness/RNG failure) | **Replication gate PASSED bit-identically.** The auxiliary loss continues decreasing after selection in all three folds; no coherent B1-specific geometry continuation established | **Decision D — no further conclusion**; does not revise E11 |
| **E13a** | Post-hoc: is held-out geometry failure a reproducible mechanism? | **Exploratory/post-hoc**, on the now-**consumed** 44-subject/79-stream population | Within-stream class direction highly stable (median cosine +0.9935, 56/57 sign agreement); only 1 of 2 assessable reversal streams reproduced | **Decision D — no coherent mechanism established**; does not revise E11 or E12d |

**Branch closure, stated as the project itself states it**: the representation-improvement branch was closed on this corpus **because no sufficiently coherent corrective mechanism was established across E11, E12a, E12d and E13a** — not because representation learning was proven not to work in general, and not because the frozen head was found at fault (E10 shows the opposite). The 44-subject/79-stream population is now **consumed** and cannot support a future confirmatory geometry claim.

### 12.6 Identifiers checked and not found as executed work

**E2 (Selection-Variance Audit) and E3 (Prior-Mismatch Correction) exist only as a pre-registered plan** (`docs/experiments/b4/B4_E2_E3_ANALYSIS_PLAN_V1.md`), itself derived from `B4_IMPROVEMENT_INVESTIGATION_BRIEF_V1.md` §6–§7. **No corresponding report document was found in this repository.** Per this document's own instruction not to invent status: **E2 and E3 should be treated as planned/designed but of unconfirmed execution status from primary evidence available in this pass** — not as completed investigations, and not asserted here to have produced any result. **E4 and E5 were searched for explicitly and no reference to either identifier was found anywhere in `docs/experiments/b4/` or the control-plane documents** — they do not appear to exist as named investigations in this repository.

**None of E1–E13a is a runtime module.** All are read-only or training-and-discard investigations against development or now-consumed populations; none of them executes as part of the live inference pipeline described in §16.

---

## 13. Agentic / explanation layer

| Component | Type | Role |
|---|---|---|
| **Evidence Agent** (`agents/evidence.py`) | **RUNTIME COMPONENT** | Deterministic — no language model. Constructs why an alert fired from the frozen artifact chain. The substrate every generative behavior is grounded on. |
| **Evidence Graph** (`agents/graph.py`) | **RUNTIME COMPONENT** | 35 nodes / 39 edges per alert; closed node/edge vocabularies; distinguishes a cryptographically **verified** provenance record from one that is absent/unverifiable (`frozen_by` vs. `provenance_unavailable` — code-verified). |
| **Explanation Agent / `PatientExplanationAgent`** (`agents/explain.py`, `context.py`, `providers.py`) | **RUNTIME COMPONENT** | Runs the guard sequence (below) and returns either a generative or deterministic explanation. |
| **Local Qwen provider** (`LocalQwenProvider`) | **RUNTIME COMPONENT** (optional, explicit opt-in) | Loads a pinned, locally-cached open-weight model; no hosted fallback. |
| **Qwen3-1.7B** | **EVALUATION COMPONENT** — one evaluated model, n=1 context | Fidelity 1.000, completeness 1.000, 0 registered claim-boundary violations — **yet asserted G1–G6 passed while G4 and G5 were blocked.** Categorical guard refused it; deterministic fallback served; the inversion reproduced on a second run. |
| **Qwen3-4B-Instruct-2507** | **EVALUATION COMPONENT** — one evaluated model, same context | Correctly stated "G1, G2, G3, G6 passed; G4, G5 blocked." No guard fired; the generative response was served. |
| **Lexical claim guard** (`agents/claims.py`, `claims.audit()`) | **RUNTIME COMPONENT** | 18 forbidden-claim regex patterns, applied first in the guard sequence. |
| **Numeric claim guard** (`explain.py::_unsupported_numeric_claims`) | **RUNTIME COMPONENT** | Applied second — flags any generated number the evidence does not license. Did **not** catch the G1–G6 inversion, because "G1" is not a numeric claim (the digit follows a letter). |
| **Categorical state-alignment guard** (`agents/alignment.py::categorical_violations`) | **RUNTIME COMPONENT** | Applied third — the only one of the three that compares a categorical assertion against the field that records the truth. Built specifically because the first two passed the G1–G6 inversion cleanly. |
| **Deterministic fallback** (`TemplateRenderer`) | **RUNTIME COMPONENT** | The no-call default; also what is served whenever any guard fires. |
| **Research Assistant** (`agents/research.py`) | **RESEARCH TOOL / SUPPORTING AGENT** | Six curated evidence objects, no document access. Not part of the alert-to-explanation pipeline. |
| **Architecture Selection Agent** (`agents/architecture.py`) | **SUPPORTING AGENT** | Traces candidate lifecycle from protocol lock to decision ("lifecycle, not recommendation"); formalizes the *process* by which §4/§6/§10 decisions were made, but is not itself part of any retained model chain. |
| **Explanation evaluation framework** (`agents/evaluation/`) | **EVALUATION COMPONENT** | Produced the fidelity/completeness/violation numbers reported for both Qwen models. |

**Data flow, verified against `explain.py` directly**:

```
AlertEvent (contiguous EVENT run, from T1)
  → EvidenceRecord (deterministic, Evidence Agent)
  → EvidenceGraph (closed provenance, verified-or-unavailable per artifact)
  → ExplanationContext (four closed sections)
  → provider.generate() [deterministic template, OR local Qwen, OR hosted — explicit selection only]
  → claims.audit()               [lexical guard — 1st]
  → _unsupported_numeric_claims()[numeric guard — 2nd]
  → categorical_violations()     [categorical guard — 3rd]
  → served generative explanation   (all three guards pass)
     OR
     deterministic fallback served  (any guard fires; mode and reason recorded)
```

**The Qwen result, stated without a rate or a scaling law**: this is **one evaluated context, two models** — a demonstrated failure mode (a fluent, numerically faithful, zero-violation generation can still be categorically wrong) and a demonstrated success mode (the identical governed path can serve a correct generation from a different model on the same evidence) in the same controlled comparison. It is not a claim about Qwen models generally, and it is not a claim that larger models are safer in general.

---

## 14. Experiment identifier vs. runtime component — the classification that resolves most confusion

| Identifier | Type |
|---|---|
| B0–B3 | Experimental arms only — sealed, consumed, not runtime |
| B4-A | Experimental arm only — not selected, not in the runtime chain |
| **B4-B** | Experimental arm **AND** retained runtime encoder |
| B4-C | Experimental arm only — not selected, not in the runtime chain |
| P1-A | Experimental arm (matched control) only |
| **P1-B** | Experimental arm **AND** retained runtime fusion mechanism |
| M1S | Experimental arm only — not retained |
| **M1L** | Experimental arm **AND** retained runtime memory architecture |
| M1D | Experimental arm only — "Pareto-relevant," explicitly not retained |
| M2-0 | Experimental arm (naive control) only — preserved as frozen evidence, never runs live |
| **M2-G** | Experimental arm **AND** retained runtime update policy |
| **G1–G6** | **Not experimental arms at all** — six runtime gate conditions evaluated continuously inside the one retained M2-G policy |
| U1 Platt | Experimental arm **AND** retained runtime calibration stage |
| U1 router | Experimental arm only — rejected, does not exist in the shipped system |
| T2-GRU | Experimental arm (comparator) only |
| **T2-S4D** | Experimental arm **AND** retained runtime temporal component |
| **T1** | **Not an experimental "arm" in the comparator sense — the runtime state machine itself**, measured against the W1 comparator |
| W1 | Comparator only — a derived analysis, no run directory, not runtime |
| E1–E13a | **Investigation only, in every case** — none is a runtime module, none is a deployable arm |
| Qwen3-1.7B | Explanation-provider evaluation; also an optional runtime provider if explicitly selected |
| Qwen3-4B-Instruct-2507 | Same — evaluation subject and optional runtime provider |
| Evidence Agent, Evidence Graph, the three guards | Runtime components, not experimental arms |
| Research Assistant, Architecture Selection Agent | Supporting/research tools, not part of the retained inference chain |

**Not every code in this project is a deployable module, and the table above is the fastest way to check.**

---

## 15. Current retained pipeline

Every stage below is the one that actually executes in `src/cardiosentinel/edge/` today; every arrow states exactly what crosses it, verified against the code paths cited in prior sections.

```
Ambulatory ECG (stored LTSTDB waveform, replayed causally)
  │  raw signal, causally filtered
  ▼
Causal 10 s windows / 5 s stride
  │  a [1, 2500] waveform tensor per window
  ▼
B4-B CNN-Transformer embedding                                  (§4)
  │  a 128-d pooled representation
  ▼
P1-B physiology late fusion                                     (§5)
  │  128-d embedding CONCATENATED with 18-d physiology vector → 146-d
  ▼
M1L patient-relative memory                                     (§6)
  │  d_long: causal distance between this window and the evolving
  │  long-timescale patient prototype
  ▼
M2-G gated continual adaptation                                 (§7, §8)
  │  the M1L score and prototype-update decision, gated by G1-G6;
  │  the prototype itself only updates when all applicable gates pass
  ▼
U1 Platt calibration                                            (§9)
  │  a calibrated probability derived from the (unchanged) classification
  │  decision — the decision itself does not move
  ▼
T2 S4D longitudinal temporal evidence                            (§10.1)
  │  s4d_temporal_evidence_s_t: a continuous learned score carried across
  │  windows for this subject's stream
  ▼
T1 NORMAL/WATCH/EVENT/RECOVERY episode state                    (§10.3)
  │  a discrete episode state, computed from exactly 9 allowed inputs
  │  (including s4d_temporal_evidence_s_t, never a binarized T2 decision)
  ▼
AlertEvent (contiguous EVENT run)
  │  component lineage attached
  ▼
EvidenceRecord / EvidenceGraph                                  (§13)
  │  a closed, provenance-verified evidence object
  ▼
Guarded explanation
  │  lexical → numeric → categorical guards, in that order
  ▼
Generative output (if all guards pass) OR deterministic fallback (otherwise)
```

---

## 16. Master retained / rejected / comparator table

| Stage | Question | Candidates | Retained | Rejected / comparator | Selection evidence | Key caveat |
|---|---|---|---|---|---|---|
| Classical baseline | Does a classical model beat chance? | B0, B1, B2, B3 | — (all sealed, none is a "retained runtime" in the neural sense) | B0 is the floor; B3 is the standing comparator | Sealed TEST | B3 remains the strongest comparator the neural chain has never beaten |
| Representation | Which encoder architecture? | B4-A (CNN), B4-B (CNN+Transformer), B4-C (CNN+SSM) | **B4-B** | B4-A (reference), B4-C (negative/alternative result) | Development validation, pre-registered rule | Sealed TEST of B4-B alone: 0.0935 < B3's 0.1683 |
| Physiology | Does explicit physiology help the embedding? | P1-A (neural-only), P1-B (fusion) | **P1-B** | P1-A | Development validation | Rate-related challenge FPR worsened |
| Memory architecture | Which patient-memory timescale? | M1S, M1D, M1L | **M1L** | M1S (dominated), M1D (Pareto-relevant, not retained) | Development validation | M1D scores higher on sensitivity/AUROC/MCC |
| Adaptation policy | When may memory update? | M2-0 (naive), M2-G (gated) | **M2-G** | M2-0 | Development validation | FP rates worsened under M2-G |
| Calibration | Improve probability quality? | Uncalibrated, Platt | **Platt** | uncalibrated reference | Development, out-of-fold | ECE dominated by the near-zero bin |
| Routing | Reduce cloud dependence safely? | Router (c*=0.90) | none | **Router — rejected** | Development, prespecified gate | Asymmetry ratio 6.45 > guard 3.0 |
| Temporal | Which longitudinal sequence model? | GRU, S4D | **S4D**, by predefined rule | GRU | Development outer-validation | Paired CI includes zero; S4D is more fragmented |
| Episode reasoning | Stateful or memoryless? | W1 (memoryless), T1 (stateful) | **T1** | W1 (comparator) | Held-out, paired bootstrap | Bounded to the promoted operating point |
| Explanation | Deterministic or guarded generative? | Template, local Qwen | **Both, conditionally** | — (Qwen3-1.7B's specific generation on this context was refused; the model itself is not "rejected" as a component) | Executed, n=1 | Not a rate or scaling law |

---

## 17. Evidence-stage matrix

| Component | TRAIN-derived? | Development/validation? | Held-out (subject-disjoint)? | Sealed TEST? | Engineering/runtime measurement? | Post-hoc? |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| B4 architecture selection (B4-A/B/C) | (front end shares TRAIN-fit norms) | **Yes — the decision itself** | — | — | — | No |
| **B4-B sealed encoder benchmark** | — | — | — | **Yes — the only sealed TEST access in this entire mapping** | — | No |
| P1-A/P1-B | (encoder frozen from TRAIN) | **Yes** | — | — | — | No |
| M1S/M1D/M1L | (standardizer TRAIN-fit only) | **Yes** | — | — | — | No |
| M2-0/M2-G | — | **Yes** | — | — | — | No |
| U1 Platt / router | — | **Yes (out-of-fold)** | — | — | — | No |
| T2 GRU/S4D headline AUPRC | — | **Yes (outer-validation, IS the selection criterion)** | — | — | — | No |
| T2 fragmentation statistics | — | **Yes — explicitly free of selection conditioning** | — | — | — | No |
| T1/W1 comparison | — | — | **Yes — 12 held-out subjects** | — | — | No |
| E11 (ATTEMPT 2) primary geometry | — | — | **Yes — 44-subject/79-stream, now consumed** | — | — | No |
| E13a | — | — | (re-uses the now-consumed E11 population) | — | — | **Yes — explicitly exploratory/post-hoc** |
| Qwen runtime observation | — | — | — | — | **Yes — n=1 context, executed** | No |
| Runtime throughput (~61×) | — | — | — | — | **Yes — measured, laptop host** | No |
| Reproducibility bundle | — | — | — | — | **Yes — manifest-verified, demo tier** | No |

**This table exists to prevent exactly one mistake**: reading the B4-B sealed benchmark (row 2, the *only* sealed-TEST row in this whole document) as if it shared an evidence level with P1/M1/M2/T2's development-selection numbers, or with T1/W1's held-out comparison, or with the Qwen runtime observation. It does not. It is the single most consumed, least repeatable number in the project (`repeat_attempt_permitted: false`), and every other number in this matrix remains open to (authorized) re-analysis in a way that row does not.

---

## 18. Dependency graph

```
                         B4-B (retained encoder)
                              │
                              ▼
                         P1-B (physiology fusion)
                              │
                              ▼
                         M1L (patient memory)
                              │
                              ▼
                         M2-G (gated adaptation) ──── side: M2-0 (frozen control, never runs live)
                              │
                              ▼
                         U1 Platt (calibration) ──── side: U1 router (rejected, does not exist at runtime)
                              │
                              ▼
                         T2-S4D (temporal evidence) ──── side: T2-GRU (comparator, not retained)
                              │
                              ▼
                         T1 (episode state) ──── side: W1 (comparator, derived analysis only)
                              │
                              ▼
                    Evidence / explanation layer

Side branches, not in the inheritance chain above:
  B3 classical comparator ─── the standing target B4-B has never beaten on sealed TEST
  B4-A, B4-C ─── stop at the architecture-selection decision; never receive
                 downstream data (no physiology fusion, no memory, no gate)
  E1–E13a ─── an entirely separate investigation branch INTO B4-B's own
              representation; consumes no downstream stage's output and
              feeds no downstream stage; terminates at "branch closed" (§12.5)
```

**Where frozen upstream state is inherited without re-derivation**: every arrow above carries a "frozen" artifact — a checkpoint, a fitted standardizer, or a lock — forward unchanged; §4.1, §7 and §9 each state explicitly that the component below them does not retrain or re-fit the component above. **Where a new comparison occurs**: at each node with a labeled "side" branch (M2-0, U1 router, T2-GRU, W1) — these are the four places a live comparator was evaluated against the retained choice. **Where rejected branches stop**: B4-A and B4-C stop immediately after architecture selection; M1S and M1D stop immediately after the M1 decision; the U1 router stops immediately after U1; T2-GRU stops immediately after T2 — none of these ever receives or produces data for anything downstream.

---

## 19. Common confusions — FAQ

**Is B4 the whole CardioSentinel model?** No. B4 is one stage — the raw-waveform representation — of an eight-stage retained pipeline (§15). The B4-B sealed benchmark (§4.1) evaluates the encoder alone, with none of P1/M1/M2/U1/T2/T1 present.

**Is B4-B the same as P1-B?** No. B4-B is architecture candidate B in the B4 family (the CNN+Transformer encoder). P1-B is experiment arm B in the P1 family (the physiology-fusion arm, which is *built on top of* B4-B's embedding). They share the letter "B" by two independent, unrelated naming choices (§2.C).

**Does "-B" always mean the winning arm?** No, and this is a coincidence worth naming directly: in `B4-B` and `P1-B`, "B" happens to be the retained/selected arm; in `M2-B`... there is no `M2-B` — M2's arms are `M2-0` and `M2-G`. The letter position in an alphabetic sequence carries no meaning about retention status; check the specific family's own retention decision.

**Does "G" in M2-G mean G1–G6?** No (§2.C). `M2-G` names the retained *policy as a whole* ("Gated"). `G1`–`G6` are the six conditions *evaluated inside* that policy on every row.

**Is G4 a model?** No. G4 is a threshold comparison (`score <= NORMAL_EVIDENCE_THRESHOLD`) against the already-computed M1L score. It trains nothing and is not a classifier in its own right.

**Is G5 the T1 RECOVERY state?** No — explicitly, by the code's own constant: `REFRACTORY_SEMANTICS` states G5 is "NOT NORMAL/WATCH/EVENT/RECOVERY, not episode reasoning, not clinical persistence logic." G5 is a 60-second memory-update safety window; T1's RECOVERY is a distinct episode-state concept with its own, separately-tuned `recovery_clear_windows` duration (§10.3).

**Is S4D used in B4-C and T2 for the same purpose?** No (§10.2). Same block family and math, reused verbatim, but B4-C's use discards state per window (a representation-level candidate) and T2's use carries state across a subject's whole stream (the retained longitudinal temporal arm).

**Why is T2 upstream of T1?** Because T2 is Phase 8 and T1 is Phase 9 in actual execution order (§2.B) — the "1" and "2" in the family names do not encode this; the `phaseN-*` run-directory numbering does.

**Is T1 a neural network?** No. Zero trainable parameters; a deterministic finite-state machine (§10.3).

**Is W1 another trained model?** No. W1 is a derived analysis with no run directory of its own — it re-scores the same frozen upstream trace T1 uses, memorylessly, for comparison only.

**Was U1 rejected?** Only half of it. Platt calibration (retained) and the selective router (rejected) are two separate decisions inside one experiment stage (§9).

**Is M1D worse than M1L on every metric?** No (§6). M1D scores higher on sensitivity, AUROC and MCC. M1L was preferred for its tighter subject-level false-alarm distribution, which better matched M1's prespecified objective.

**Does the B4 sealed TEST evaluate M2/T1/Qwen?** No. It evaluates the B4-B encoder/head path alone — no memory, no gate, no calibration, no temporal evidence, no episode state, no explanation layer (§4.1).

**Are E1–E13a part of runtime?** No, none of them (§12, §14). All are investigation artifacts against development or now-consumed populations.

**Does Qwen make alert decisions?** No. Alerts are produced entirely by the deterministic T1 state machine before any language model is ever invoked; Qwen (when explicitly selected) only narrates an alert that has already been decided (§13).

**What does "retained" mean?** The specific arm carried forward into the pipeline (or, for a decision-only stage like calibration, kept as the standing choice) after a documented comparison against at least one alternative.

**What does "frozen" mean?** A value, weight, threshold or protocol that is fixed before the measurement it governs and is not permitted to change after — enforced by digest binding in most cases, not merely convention.

**What does "sealed" mean?** A partition (TEST) whose access is a one-shot, digest-verified, non-repeatable event — used exactly once across the entire project, for B4-B alone.

**What does "consumed" mean?** An access or a population that has been used in a way that permanently forecloses using it again for a fresh confirmatory claim — applies to every one-shot budget (all fifteen are spent) and, separately, to the E11 44-subject/79-stream geometry population (§12.5).

---

## 20. Terminology glossary

| Term | Meaning in this project |
|---|---|
| **retained** | The arm/mechanism carried forward after a documented comparison; does not imply universal superiority |
| **rejected** | An arm/mechanism evaluated against a prespecified gate or comparator and not carried forward; preserved as evidence, not deleted |
| **comparator** | An arm run specifically to give a retained arm something to be measured against; not itself a candidate for retention |
| **ablation** | An experiment removing one component to measure its contribution (e.g., M1S/M1D/M1L as ablations of memory timescale) |
| **frozen** | Fixed before measurement and digest-bound against later change |
| **sealed** | A partition whose one-shot access has been consumed or is being protected pending consumption (TEST) |
| **consumed** | An access or population that can no longer support a fresh confirmatory claim |
| **development evidence** | Evidence from the TRAIN/VALIDATION partitions, prior to any sealed-TEST access |
| **held-out** | Subject-disjoint from the fitting population, though not necessarily the sealed TEST partition (T1/W1's "held-out" 12 subjects are the VALIDATION partition, not TEST) |
| **subject-macro** | A metric averaged per-subject, then across subjects — sensitive to how many subjects "contribute" (have a defined value) |
| **pooled** | A metric computed over all rows/windows at once, regardless of subject |
| **prototype** | The evolving per-stream representation summary (`DualTimescaleMemory`'s EMA state) that a patient's incoming windows are compared against |
| **patient memory** | The general mechanism (M1 family) by which patient-relative context accumulates over a stream |
| **contamination proxy** | A measurable stand-in (prototype drift) for an unmeasurable target (whether an abnormal state corrupted the learned "normal" baseline) |
| **refractory** | A time window during which a specific action (here, a memory update) is blocked following a triggering event (here, a G4 failure) |
| **calibration** | Post-hoc transformation of a model's raw score into a better-behaved probability estimate, without changing classification decisions |
| **selective routing** | Deferring low-confidence cases to a different (e.g., cloud/human) decision path rather than the local model |
| **SSM** | Structured state-space model — a sequence-modeling family using a (here, diagonal) linear recurrence in a latent state |
| **S4D** | The specific diagonal-parameterization variant of an SSM used in both B4-C and T2 |
| **GRU** | Gated Recurrent Unit — the conventional recurrent-network comparator to T2's S4D arm |
| **episode state** | T1's four discrete states (NORMAL/WATCH/EVENT/RECOVERY) |
| **evidence graph** | The closed-vocabulary provenance graph every generated explanation is grounded on |
| **claim guard** | The lexical forbidden-pattern check applied to any generated text before exposure |
| **deterministic fallback** | The template-rendered explanation served whenever a guard fires or no generative provider is configured |

---

## 21. Presentation cheat sheet

**A. One-line project journey**

`B (representation) → P (physiology) → M1 (memory architecture) → M2 (memory policy) → U (calibration) → T2 (temporal score) → T1 (episode state) → explanation`

**B. 30-second explanation**

"CardioSentinel is an ambulatory-ECG monitoring pipeline where every stage — which representation, whether to fuse physiology, which memory timescale, when memory may update, whether to calibrate or route, which temporal architecture, and whether to serve a generated explanation — was decided by a documented comparison against at least one alternative, not assumed. The system that runs today is the specific chain of winners; the alternatives are preserved as evidence, not deleted."

**C. 2-minute explanation**

"The pipeline has three headline, independently-measured behaviors. First, patient memory only updates when a six-condition gate (G1–G6) says the current window looks safe to learn from — this cut a measured contamination proxy by 96–99.8% while still admitting a fifth of all windows, so it isn't a trivial freeze. Second, a deterministic four-state episode machine (T1) interprets a learned temporal score (T2, a structured state-space model) statefully rather than window-by-window, which measurably changed episode-level agreement versus a memoryless reading of the identical evidence. Third, a locally-hosted open-weight model can narrate an alert, but only after passing three governance checks — lexical, numeric, and categorical — and in our one evaluated case, a fluent, numerically perfect explanation was still caught and refused for silently inverting a true/false gate outcome, while a larger model on the same evidence was correctly served. Underneath all three, the representation itself went through a genuine three-way architecture search — CNN, CNN+Transformer, CNN+state-space — before any of this was built on top of it, and that search's winner still did not beat the classical baseline on the one sealed test the project ever ran."

**D. What does each letter mean? (quick table)**

| Letter | Family | Quick meaning |
|---|---|---|
| B | B0–B4 | Representation / baseline programme |
| P | P1 | Physiology fusion |
| M1 | M1S/L/D | Which memory architecture |
| M2 | M2-0/G | When memory may update |
| G (in G1–G6) | — | Six gate *conditions*, not a family letter |
| U | U1 | Calibration + routing |
| T2 | GRU/S4D | Learned temporal score |
| T1 | — | Explicit episode state |
| W | W1 | Memoryless comparator |
| E | E1–E13a | Representation-mechanism investigations |

**E. Top 10 codes to memorize**

1. `B4-B` — the retained encoder (CNN+Transformer)
2. `M2-G` — the gated adaptation policy (96–99.8% drift reduction)
3. `G1`–`G6` — the six conditions inside M2-G, not experiments
4. `M1L` — the retained patient-memory architecture
5. `T2-S4D` — the retained longitudinal temporal arm
6. `T1` — the deterministic episode state machine
7. `W1` — the memoryless comparator to T1 (+0.1921 difference)
8. `P1-B` — the retained physiology-fusion arm
9. `B4-C` — the rejected-as-encoder SSM candidate, same family as T2-S4D
10. `E11` — the closed morphology-intervention branch (Category C)

**F. Codes most likely to be asked about by a reviewer**

`B4-C` (why build an SSM candidate and reject it — because it is evidence, not a mistake); `G4` vs. the classification threshold (why two different thresholds exist); `T2` vs. `T1` (why a learned score needs a separate deterministic state layer on top of it); the Qwen pair (why refusing a "perfect-scoring" generation is the point, not a failure); `M1D` (why the higher-sensitivity arm was not retained).

---

## 22. Visual-map recommendations (not generated here)

1. **Full experiment lineage** — nodes: every identifier in §16's master table plus every E-series entry in §12; edges: "compared against," "feeds," "gated by," colored by retained (solid) vs. rejected/comparator (dashed) vs. investigation-only (dotted, terminating, no downstream edge).
2. **Retained runtime pipeline** — exactly the nine boxes in §15's ASCII diagram, one arrow each, annotated with the exact information crossing it (embedding dimension, score name, state type) as already written in §15.
3. **M2-G gate detail** — one central "row arrives" node branching to six gate boxes (G1…G6) in `CONDITION_ORDER`, each annotated with its pass/fail/not-applicable semantics from §8's table, converging on a single "admitted?" decision diamond, with a visibly separate loop-back arrow from "G4 fails" to "refractory re-armed" (and explicitly no such arrow from G6, since `G6_ARMS_REFRACTORY = False`).

---

## 23. Source index

| Section | Primary source(s) | Type |
|---|---|---|
| §3.1 (B0–B3) | `docs/control-plane/CURRENT_STATE.md` §4 | control-plane summary of sealed-test artifacts |
| §3.2–§4 (B4-A/B/C) | `docs/experiments/b4/B4_GLOBAL_ENCODER_SELECTION_V1.md`; `src/cardiosentinel/neural/model.py`; `src/cardiosentinel/neural/candidates.py` | retention decision + code |
| §5 (P1) | `docs/experiments/p1/P1_PHYSIOLOGY_RETENTION_DECISION_V1.md`; `src/cardiosentinel/neural/physiology_fusion.py` | retention decision + code |
| §6 (M1) | `docs/experiments/m1/M1_MEMORY_RETENTION_DECISION_V1.md`; `src/cardiosentinel/neural/patient_memory.py` | retention decision + code |
| §7 (M2) | `docs/experiments/m2/M2_UPDATE_POLICY_RETENTION_DECISION_V1.md` | retention decision |
| §8 (G1–G6) | `src/cardiosentinel/neural/m2_gate.py`; `src/cardiosentinel/neural/m2_policy.py` | code (read directly, not summarized) |
| §9 (U1) | `docs/experiments/u1/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md`; `U1_CALIBRATION_SELECTIVE_ROUTING_PROTOCOL_V1.md`; `U1_CALIBRATION_RELIABILITY_REPORT_V1.md` | retention decision + protocol + report |
| §10.1–10.2 (T2) | `docs/experiments/t2/T2_ARM_COMPARISON_REPORT_V1.md`; `src/cardiosentinel/neural/t2_models.py`; `B4_GLOBAL_ENCODER_SELECTION_V1.md` §8 | report + code + cross-reference |
| §10.3 (T1) | `src/cardiosentinel/neural/t1_protocol.py` (lines 155–265) | code (read directly) |
| §11 (W1) | `docs/experiments/w1/W1_WINDOW_COMPARATOR_REPORT_V1.md` | report |
| §12 (E1–E13a) | `docs/experiments/b4/B4_E1_REPRESENTATION_PROBE_REPORT_V1.md` through `B4_E13A_HELD_OUT_GEOMETRY_RELIABILITY_PLAN_V1.md` (each cited by exact filename in-row); `docs/control-plane/CURRENT_STATE.md` §3.1–3.4 | individual reports/plans + control-plane summary |
| §13 (agentic layer) | `src/cardiosentinel/agents/{evidence,graph,explain,context,providers,claims,alignment,research,architecture}.py`; `docs/explanation/EXPLANATION_EVALUATION_REPORT_V1.md` | code (read directly) + report |
| §14–§18 (classification, pipeline, tables, matrix, dependency graph) | Synthesized from all sources above; no new fact introduced beyond §3–§13 | synthesis |

**Manuscript-level documents (the paper drafts, its various audits) were deliberately not cited as primary sources anywhere above** — every number and mechanism in this document traces to a protocol, retention decision, experiment report, or the source code itself, per this task's own instruction to prefer primary evidence over the manuscript.

---

**Living document, not a frozen `_V1` record.** Like `ARCHITECTURE.md` and `EXPERIMENT_CATALOGUE.md` in this same directory, this document carries no digest and no freeze ritual — it explains naming and lineage, and complements rather than restates `EXPERIMENT_CATALOGUE.md` (which tracks the consumed/available ledger) and `EVIDENCE_MAP.md` (which separates method from findings). It should be refreshed by a read-only pass against source code and the retention decisions it cites, the same way `CURRENT_STATE.md` is, if a future retention decision changes any mapping recorded above.

---

CANONICAL MAPPING STATUS:
COMPLETE

UNRESOLVED IDENTIFIER MEANINGS:
1. E2 (Selection-Variance Audit) and E3 (Prior-Mismatch Correction) exist only as a pre-registered plan (`B4_E2_E3_ANALYSIS_PLAN_V1.md`); no execution report was found in this repository, so their completed status and any result are unconfirmed from primary evidence.
2. E4 and E5 were searched for explicitly and do not appear to exist as named investigations anywhere in this repository.
3. No formal, explicit "letter = word" acronym definition was found for B, P, M, U, T, W, or E anywhere in the source documentation — every expansion offered in this document (§2.A) is labeled a practical mnemonic, not an official project fact, because none could be verified as such.

TOP 10 CODES THE AUTHOR SHOULD MEMORIZE:
1. B4-B — the retained CNN+Transformer encoder
2. M2-G — the gated adaptation policy (96–99.8% drift reduction, 21.84% admission)
3. G1–G6 — the six conditions inside M2-G, never confuse with experiment IDs
4. M1L — the retained patient-memory architecture
5. T2-S4D — the retained longitudinal temporal arm (same SSM family as B4-C, different scope)
6. T1 — the deterministic NORMAL/WATCH/EVENT/RECOVERY episode state machine
7. W1 — the memoryless comparator to T1 (+0.1921, CI excludes zero)
8. P1-B — the retained physiology late-fusion arm
9. B4-C — the rejected-as-encoder state-space candidate, evidence not a mistake
10. E11 — the closed morphology-intervention branch (Category C, population now consumed)

ONE-SENTENCE CARDIOSENTINEL EXPERIMENT JOURNEY:
Every stage of CardioSentinel's retained pipeline — which representation, whether to fuse physiology, which memory timescale, when memory may update, whether to calibrate or route, which temporal architecture, and whether to serve a generated explanation — was decided by a documented, pre-registered comparison against at least one rejected or comparator alternative, all of which remain preserved as evidence rather than deleted.
