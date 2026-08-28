# CardioSentinel Paper-Readiness Audit, V1

**Audit only. No experiment was run, no model trained, no hypothesis created, no
sealed TEST reopened, no historical VALIDATION used for a fresh claim, no
external literature consulted.**

Every quantity below was **read from a frozen report, receipt or manifest in
this repository**, not recalled. Where a handbook summary and a frozen
experiment report disagreed, **the frozen report won** — §0.1 records the one
case where that rule changed a stated fact.

---

## 0. Authoritative sources, and one state correction

**Primary control-plane:** `CardioSentinel_Research_Execution_Handbook_v1.5.md`,
`CURRENT_STATE.md`, `EXPERIMENT_CATALOGUE.md`.

**Frozen scientific record consulted:** `B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1`,
`B4_TEST_AUTHORIZATION_V1`, `B4_E1…E10` plans/reports,
`B4_E11_MORPHOLOGY_AWARE_REPRESENTATION_REPORT_V1`,
`B4_E12A_TRAINING_DYNAMICS_SELECTION_AUDIT_V1`,
`B4_E12D_INSTRUMENTED_PHASE1_REPLICATION_REPORT_V1`,
`B4_E13A_HELD_OUT_GEOMETRY_RELIABILITY_PLAN_V1` + `E13A_RESULTS.json`,
`T1_DESCRIPTIVE_REPORT_V1`, `T1_POST_HOC_ANALYSIS_V1`,
`T2_ARM_COMPARISON_REPORT_V1`, `W1_WINDOW_COMPARATOR_REPORT_V1`,
`M1_MEMORY_RETENTION_DECISION_V1`, `M2_UPDATE_POLICY_RETENTION_DECISION_V1`,
`U1_CALIBRATION_RELIABILITY_REPORT_V1`,
`U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1`,
`EXPLANATION_EVALUATION_REPORT_V1`, `QWEN_EVALUATION_RUN`,
`EXTERNAL_VALIDATION_ROUTE_A_DECISION_V1`, handbook v1.4 §49/§53/§55.

### 0.1 STATE CORRECTION — the generative arm HAS been exercised

`CURRENT_STATE.md` (lines 173, 175) and handbook v1.5 §12 state that the
**"real-model arm remains unexercised"** and that the generative arm has
**"never been measured"**.

**`EXPLANATION_EVALUATION_REPORT_V1.md` opens: *"Arm B is exercised. This is the
first report of a real generative model in this programme."*** It reports two
real Qwen models on the contracted demo scenario, with a full trade-off table.

**The frozen report wins. The control-plane statement is wrong and is corrected
by this audit.** The accurate statement is:

> The generative arm **has been exercised once**, on **n = 1 context**, under
> `EXPLANATION_EVALUATION_PROTOCOL.md`. The **separate** manual run contract
> `QWEN_EVALUATION_RUN.md` is **NOT EXECUTED** and remains a template.

This matters for the paper: the programme's single most striking governance
result lives in that report, and a control-plane document was telling future
sessions it did not exist.

---

## 1. Paper positioning

**Proposed thesis, evaluated:**

> *"CardioSentinel is an intelligent physical monitoring system in which
> learning, personalization, temporal reasoning and agentic explanation remain
> bounded by executable evidence, provenance and fail-closed governance."*

**VERDICT: the accumulated evidence supports this positioning, and supports
almost nothing else.**

It is supported because every clause is backed by an artifact: *learning* (B4-B
selected under rules frozen before the deciding evidence existed), *temporal
reasoning* (T1/W1, RQ4 supported-bounded), *personalization* (M1L/M2-G retained
under contamination-safe gates), *agentic explanation bounded by executable
evidence* (a fluent, fidelity-1.000, zero-violation generation **refused at
runtime** for a categorical inversion), and *fail-closed governance* (a claim
guard that caught **five violations in this repository's own code**; a
replication gate that halted E12d ATTEMPT 1; a state machine whose chain
terminating at `SELECTION_FROZEN` proves phase 2 never ran).

**It must not be positioned as** a new ECG diagnostic model, a medical-device
claim, a SOTA ischemia classifier, or a framework illustrated by screenshots.
**The predictive numbers cannot carry a paper**: the sealed test returned pooled
AUPRC **0.0935** at prevalence **0.0461**, and the B4 improvement branch is now
**closed on this corpus** after E11 (Category C), E12d (Decision D) and E13a
(Decision D).

**The honest framing is that the governance is the contribution and the
modelling is the substrate** — including the negative results, which are
evidence that the governance binds.

---

## 2. Master claim matrix

Abbreviations: **EL** = allowed wording, **FB** = forbidden wording.
Status set: SUPPORTED · SUPPORTED–BOUNDED · NEGATIVE FINDING · INCONCLUSIVE ·
EXPLORATORY/POST-HOC · NOT SUPPORTED · CLOSED.

| ID | Candidate claim | Component | Evidence type | Exact evidence | Status | Strength | Key limitation | Allowed wording | Forbidden wording | Location | Abs? | Concl? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **C1** | Episode reasoning beats a memoryless window rule | T1 vs W1 | confirmatory, development | subject-macro `episode_f1` difference **0.1921**, 95% paired subject-bootstrap **[0.0505, 0.3455]** | **SUPPORTED — BOUNDED** | strongest positive | one operating point, chosen with the thing under test in the loop | "improves episode-level monitoring quality at one operating point (bounded)" | "episode reasoning is superior" | §6 | **Y** | **Y** |
| **C2** | A fluent, faithful, zero-violation generation was refused at runtime | Qwen / guard | executed, n=1 | fidelity **1.000**, claim violations **0**, completeness **1.000**, latency **63.4014 s**; runtime → `DETERMINISTIC`; asserted G1–G6 passed when **G4, G5 blocked**; reproduced on **2** runs | **SUPPORTED** (n=1) | strongest governance | **n = 1 context, 2 models**; not a failure rate | "in the single evaluated context, the runtime refused a fluent, fidelity-1.000 generation that inverted a categorical gate state" | "Qwen fails X% of the time" | §8 | **Y** | **Y** |
| **C3** | The publication claim boundary is executable and load-bearing | `claims.py` | implementation + audit | **25** forbidden claims; **5** violations caught in the repository's own code | **SUPPORTED** | strong | lexical; cannot distinguish assertion from disclaimer | "an executable claim guard that caught five violations in our own code" | "guarantees no overclaim" | §8 | N | **Y** |
| **C4** | The B4-B encoder generalizes weakly to unseen subjects | B4 sealed test | **confirmatory, consumed** | pooled AUPRC **0.0935334** at prevalence **0.0460529**; AUROC **0.7332374**; subject-macro AUPRC **0.354901** over **8 of 12**; 95% subject-bootstrap **[0.033058, 0.239284]** | **SUPPORTED** (negative in direction) | strong | **encoder/head path only**, not the IPS stack; used once; uncalibrated score | "the sealed encoder-only evaluation returned pooled AUPRC 0.0935 at prevalence 0.0461" | "CardioSentinel achieves…" | §5 | **Y** | **Y** |
| **C5** | Class direction is coherent on train and occasionally reverses on unseen streams | E10 + E11 | mechanism, prospective | E10 TRAIN LOSO cosine min **+0.971**, **0/79** negative; E11 B0 prospective median **+0.9777**, **3/79** negative over **44 subjects / 79 streams** | **SUPPORTED** | strong mechanism | development only; population now consumed | "the class direction is highly coherent across training streams and reverses on a small minority of unseen streams" | "we characterize the cause of failure" | §5 | N | **Y** |
| **C6** | The frozen head is faithful; failure is representational | E10 | mechanism | separation exceeds between-subject dispersion **26×** (TRAIN), **12×** (VALIDATION); registered prediction 5 refuted | **SUPPORTED** | strong | development only | "the head maps the direction the representation supplies; the failure is representational" | "we fixed the representation" | §5 | N | N |
| **C7** | A morphology auxiliary objective improves unseen-stream direction stability | E11 | confirmatory, prospective | cosine **+0.0030** [−0.0178, +0.0073]; ‖delta‖ **+0.1217** [−0.5993, +0.5617]; negative-fraction **−0.0127** [−0.0406, 0.0000] | **NOT SUPPORTED** (Category C) | — | single seed per arm per fold | "the registered mechanism was not established" | "morphology supervision fixes representation failure" | §5 | N | **Y** |
| **C8** | The auxiliary objective had plateaued at checkpoint selection | E12d | replication + diagnostic | replication gate **PASSED** (6/6 AUPRC bit-identical; epochs 1,1,1,2,4,1); `F_aux` **+0.6208 / +0.2556 / +0.5378**; **5/6** selections precede the largest geometry movement | **NEGATIVE FINDING** (Decision D) | moderate | no outer outcome observed | "the auxiliary loss had not plateaued at the selected epoch" | "a later checkpoint would be better" | §5 | N | N |
| **C9** | Held-out geometry failure is a reproducible mechanism | E13a | **EXPLORATORY / POST-HOC** | **57/79** eligible; median `cos_within` **+0.9935**; sign agreement **56/57**; `s20171:0` (−0.4984, −0.3302) reproduces, `s20021:1` (+0.4514, −0.9537) does not | **INCONCLUSIVE** (Decision D) | weak | post-hoc; population **consumed** | "within-stream direction is highly stable; one of two assessable failure streams reproduced" | "we established a reversal mechanism" | §5 / §11 | N | N |
| **C10** | Patient memory adds incremental patient-relative information | M1 / E8a / E8b | mechanism | `d_long` concordance **0.836 → 0.712** stratified, broad across **7/9** subjects | **SUPPORTED** (information, not prediction) | moderate | C0/C1 probe never executed | "memory carries information beyond the score, and measures atypicality" | "memory improves prediction" | §5 | N | N |
| **C11** | M1L improves predictive performance | M1 | development | pooled AUPRC **0.375248 → 0.384796** (**+0.009548**); subject-macro **0.409540 → 0.415833**; sensitivity **−0.005318**; FPR **0.041489 → 0.039395** | **INCONCLUSIVE** | weak | no interval; retained on development evidence | "retained on development evidence, with a small FPR reduction and a small sensitivity cost" | "memory definitively improves prediction" | §5 | N | N |
| **C12** | M2-G is a contamination-safe update policy | M2 | development | AUPRC **0.3847956 → 0.3845275** (**−0.000268**); AUROC **0.9075699 → 0.9084481** (**+0.000878**); threshold **0.7554003** inherited frozen; **RETAINED** | **SUPPORTED** (safety, not accuracy) | moderate | **M2-G is a gate, not a classifier** | "a contamination-safe update policy retained at essentially unchanged discrimination" | "M2 improves classification accuracy" | §7 | N | N |
| **C13** | Post-hoc calibration is retained and improves calibration | U1 | development | Platt NLL **0.143708**, Brier **0.040344**, ECE **0.016991** / **0.018604** vs uncalibrated NLL **0.231705**, Brier **0.063567**, ECE **0.063844** / **0.062464**; **473,897** rows | **SUPPORTED** | strong | ECE was not the selection criterion; NLL was | "Platt calibration retained; NLL and Brier both lower" | "the model outputs clinical probabilities" | §7 | N | N |
| **C14** | Selective uncertainty routing improves safe autonomy | U1 router | confirmatory | router at `c_star = 0.90` evaluated against a prespecified gate; **`Retained: false`** | **NEGATIVE FINDING** | strong | — | "the router was built, evaluated against a prespecified gate, and rejected" | "uncertainty routing improves safety" | §7 | N | **Y** |
| **C15** | S4D outperforms GRU | T2 | confirmatory | `pooled_auprc_difference` **0.093215**, 95% paired subject-bootstrap **[−0.015229, 0.148951]**; subject-macro difference **0.018415**; tie tolerance **0.002** | **INCONCLUSIVE** | moderate | **interval includes zero** | "S4D was selected under a preregistered rule; the paired interval includes zero" | "S4D is superior to GRU" | §6 | N | N |
| **C16** | The episode state machine detects episodes on held-out subjects | T1 | confirmatory | subject-macro `episode_f1` **0.2524**, 95% **[0.0826, 0.4415]**, defined **12/12**; pooled **0.3423**; **163** reference episodes, **59** predicted runs, **38** matched, **21** unmatched; **473,897** windows | **SUPPORTED — BOUNDED** | moderate | heterogeneous; **7 subject zeros** (3 episode-free, 4 missed) | "subject-macro episode F1 0.2524 [0.0826, 0.4415] over 12 subjects" | "reliable episode detection" | §6 | **Y** | N |
| **C17** | Onset latency demonstrates anticipation | T1 | descriptive | **6 of 38** matched latencies negative; overlap-only matching, no run durations stored | **NOT SUPPORTED** | — | signed offset, not a delay | "latency is a signed offset; negative values do not establish anticipation" | "the system predicts episodes early" | §6 / §11 | N | N |
| **C18** | The system runs in real time on commodity hardware | IPS runtime | measured | **1079** windows of `s20201` in **89 s** wall → **~61× real time**; encoder median **4.161 ms/window**, p95 **4.337 ms**, peak RSS **~305 MB** | **SUPPORTED — BOUNDED** | moderate | **laptop replay simulation, not edge hardware** | "replays a record at ~61× real time on a laptop CPU" | "validated on edge hardware" | §9 | **Y** | N |
| **C19** | The evidence graph bounds every agent output | evidence graph | implementation | **35** nodes / **39** edges per alert; closed node kinds and edge relations; no autonomous agent | **SUPPORTED** | strong | descriptive of design | "every agent output is grounded on a closed evidence graph" | "the agents reason autonomously" | §8 | N | N |
| **C20** | External validation corroborates the results | Route A | decision | declined in writing 2026-08-24; §2.4: **no second cohort, permanently** | **CLOSED** | — | — | "external corroboration was declined and is recorded as a limitation" | "externally validated" | §11 | N | **Y** |
| **C21** | The B4 improvement branch is closed on this corpus | E11+E12d+E13a | programme decision | Category C, Decision D, Decision D; geometry population **consumed** | **CLOSED** | strong | corpus-specific | "closed on this corpus without genuinely fresh subject-disjoint data" | "representation learning does not work" | §10 | N | **Y** |

---

## 3. RQ1–RQ7 paper status

| RQ | Question | Final status | Strongest evidence | Unresolved | Main paper? | Claim boundary |
|---|---|---|---|---|---|---|
| **RQ1** | Does patient-specific memory reduce false alarms without sacrificing sensitivity? | **Open** | M1L FPR **0.041489 → 0.039395**, sensitivity **−0.005318**; E8b information result | no no-memory arm **at episode level**; C0/C1 probe never run | **Limitations / future work** | may not be stated as answered |
| **RQ2** | Can continual personalization be made contamination-safe? | **Partial** | M2-G retained; AUPRC **−0.000268**, AUROC **+0.000878**; threshold inherited frozen | no episode-level contamination-stress comparison | **Main §7**, as partial | "contamination-safe by construction and gate evidence", not "proven safe" |
| **RQ3** | Can uncertainty reduce cloud dependence without unsafe local decisions? | **Answered — negatively** | router at `c_star = 0.90`, `Retained: false` | — | **Main §7** | must be reported as a rejection |
| **RQ4** | Does longitudinal/episode reasoning improve monitoring quality? | **Supported (bounded)** | **0.1921**, 95% **[0.0505, 0.3455]** | bound removable only by a well-tuned memoryless rule with its own operating point | **Main §6 — headline** | **"(bounded)" may never be dropped** |
| **RQ5** | Can the model operate efficiently on edge hardware? | **Open** | ~**61×** real time on a laptop; encoder **4.161 ms/window** | **no edge-hardware measurement exists** | **Main §9 + Limitations** | "simulation", never "edge validation" |
| **RQ6** | Does foundation-model knowledge improve the compact student? | **Not started** | — | Phase 4B never begun | **Limitations only** | must not appear as a contribution |
| **RQ7** | Can confounder-aware supervision reduce false ST alarms? | **Not started** | — | Phase 6B never begun | **Limitations only** | must not appear as a contribution |

**Two answered, one partial, four open. The paper must not present seven
successes.** RQ3's answer is a rejection and RQ4's is bounded — and both are
more useful to the governance thesis than a vague positive would be.

---

## 4. Results inventory

### 4.1 B4 sealed evaluation — **B4-B encoder/head path only, NOT the IPS stack**

```
Pooled-window AUPRC          0.0935334      prevalence 0.0460529
AUROC                        0.7332374
Subject-macro AUPRC          0.354901       over 8 of 12 subjects
95% subject-bootstrap AUPRC  [0.033058, 0.239284]
Threshold                    0.8329097628593445   validation-selected, test_informed: false
Model                        B4BTransformerCNN, 309,809 params, input [B,1,2500]
Score semantics              uncalibrated sigmoid model score — NOT a calibrated probability
```

**Must be stated explicitly every time:** the test was **used once**; the
threshold was **frozen from development**; the test **cannot be reopened**
(`repeat_attempt_permitted: false`); the score is **uncalibrated**; and this
path contains **no memory, no physiology fusion, no state machine** — it is the
encoder alone.

### 4.2 T2 temporal model

`pooled_auprc_difference` **0.093215** (signed S4D − GRU); **95% paired
subject-bootstrap [−0.015229, 0.148951]**; `subject_macro_auprc_difference`
**0.018415**; tie tolerance **0.002000**. **The interval includes zero.** S4D was
selected under a preregistered rule; selection is not superiority.

### 4.3 T1 episode reasoning — pooled and macro kept separate

| Estimand | Value |
|---|---|
| **Subject-macro mean `episode_f1`** (primary) | **0.2524**, 95% **[0.0826, 0.4415]**, defined **12/12** |
| `pooled_episode_f1` (descriptive) | **0.3423** |
| Reference episodes / predicted runs | **163 / 59** |
| Matched / unmatched predicted | **38 / 21** |
| Primary windows | **473,897** |
| Onset latency | **6 of 38** matched latencies **negative**; median defined for only **5/12** subjects |
| Subject failure burden | **7 zeros**: **3 episode-free** (`s2005`, `s2020`, `s2023`, 7/8/1 false runs) + **4 missed** (`s2019`, `s2058`, `s2059`, `s3072`) |

**The two zero-classes push the operating point in opposite directions** —
Group A improves with fewer predicted runs, Group B with more. **No subject-macro
mean of MCC or latency is reported anywhere in the programme**, and the paper
must not invent one.

**W1 comparator:** subject-macro `episode_f1` difference **0.1921**, 95% paired
subject-bootstrap **[0.0505, 0.3455]**.

### 4.4 M1 / M2 — three different things, never merged

| Kind | Evidence |
|---|---|
| **Incremental patient-relative information** (M1, E8a/E8b) | `d_long` concordance **0.836 → 0.712** stratified, broad across **7/9** subjects; errors sit further from the patient prototype (concordance **0.691**); **FN sit closer than TP (0.126)** — memory measures **atypicality** |
| **Predictive performance** (M1L) | pooled AUPRC **+0.009548**, subject-macro **+0.006293**, sensitivity **−0.005318**, FPR **−0.002094** abs — **no interval; INCONCLUSIVE** |
| **Contamination safety** (M2-G) | AUPRC **−0.000268**, AUROC **+0.000878**, threshold **0.7554003** inherited frozen, **RETAINED** |

**M2-G is a gate, not a classifier.** Its retention rests on contamination
safety at essentially unchanged discrimination.

### 4.5 U1 / selective routing — two separable results

| | NLL | Brier | ECE (equal-width / equal-mass) |
|---|---|---|---|
| **Platt (retained)** | **0.143708** | **0.040344** | **0.016991 / 0.018604** |
| Temperature only | 0.191692 | 0.058647 | 0.074040 / 0.074040 |
| Uncalibrated | 0.231705 | 0.063567 | 0.063844 / 0.062464 |

**473,897** out-of-fold rows. Family selection used **NLL, not ECE**.
**The selective router at `c_star = 0.90` was evaluated against a prespecified
gate and NOT retained.**

### 4.6 Qwen / agentic safety — **n = 1 context**

| Metric | deterministic | generative |
|---|---|---|
| exercised | yes | **yes** |
| evidence fidelity | 1.000 | **1.000** |
| **claim violations** | **0** | **0** |
| completeness | 1.000 | 1.000 |
| latency | 0.0000 s | **63.4014 s** |

Models: **Qwen3-1.7B** and **Qwen3-4B-Instruct-2507**, greedy, CPU.
**The harness calls `provider.generate()` directly — no runtime gate runs during
evaluation**, so the table describes **raw model output, not what a user
receives**.

**What the runtime did with the same generation: refused it.**
Mode → `DETERMINISTIC`; the generation asserted a `G1`–`G6` range passed when
**G4 and G5 were blocked**, inverting the fact the contamination control exists
to communicate. **The first three gates passed it; the fourth did not.** The
inversion **reproduced on two independent runs**.

**This is n = 1 context and 2 models. It is a demonstrated failure mode, not a
failure rate.**

### 4.7 IPS runtime

**1079 windows of `s20201` in 89 s wall → ~61× real time**, laptop CPU.
Encoder benchmark on a fixed host: median **4.161 ms/window**, p95 **4.337 ms**,
peak RSS **~305 MB**. Gate behaviour: **0 of 1079 windows admitted on `s20201`**;
G5 dominates — an above-threshold window arms a 60-second refractory while
windows arrive every 5 seconds.

**This is a replay simulation on a laptop. It is not edge-hardware validation.**

---

## 5. Negative and inconclusive findings — and whether they strengthen the paper

| Finding | Exact evidence | Strengthens governance story? | How (without reframing failure as success) |
|---|---|---|---|
| **Uncertainty router rejected** | `c_star = 0.90`, `Retained: false` | **Yes** | A prespecified gate was written first and the component failed it. The paper can show a retention decision that said **no** — which is what makes the other retentions credible |
| **Static subject-score normalization closed** | E7a: perfect ECDF normalization is the **worst** arm | **Yes** | A plausible fix was tested and **refuted in direction**, not quietly dropped |
| **Stream-score normalization closed** | E7b: stream variation is discriminative quality; one stream anti-correlated (AUROC **0.2119**) | **Yes** | Shows the programme distinguishes offset from signal |
| **Head-failure hypothesis not supported** | E10: **26×** / **12×** separation ratio; prediction 5 refuted | **Yes** | A registered prediction was **refuted and reported as refuted** |
| **Morphology intervention not established** | E11 Category C; all three intervals include zero | **Yes** | A preregistered intervention returned a clean null under a protocol that could have shown an effect |
| **E12d Decision D** | replication gate PASSED; `F_aux` **+0.6208/+0.2556/+0.5378**; no coherent B1-specific geometry continuation | **Yes** | The programme **reproduced its own prior computation bit-identically** before interpreting anything — and still declined to conclude |
| **E13a Decision D** | 1 of 2 assessable failure streams reproduced; frozen criterion required both | **Yes** | The decision rule was frozen **before** execution and was not relaxed when the result landed one-of-two |
| **No external validation** | Route A declined, §2.4: no second cohort, permanently | **No — it is a limitation** | Must appear in Limitations, not as a strength |
| **S4D superiority not universal** | **[−0.015229, 0.148951]** includes zero | **Yes** | Selection under a preregistered rule is reported as selection, not as a win |
| **M1 predictive contribution unresolved** | **+0.009548** pooled AUPRC, no interval | **Partly** | Honest separation of *information* from *prediction*; the unresolved half stays unresolved |

**Rule for the manuscript:** every one of these is reported as what it is. **None
is reframed as a success.** Their collective value is that they make the
retention decisions credible — a programme that only ever retained things would
be indistinguishable from one that never tested them.

---

## 6. Figure inventory — 6 figures

| # | Purpose | Source | Panels | Quantities | Why it earns space | Data exists? | New computation? |
|---|---|---|---|---|---|---|---|
| **F1** | The IPS architecture and where evidence crosses layers | handbook §52, `ARCHITECTURE.md` | single schematic | four layers; evidence graph **35 nodes / 39 edges**; claim guard placement | The paper's thesis is architectural; without this the rest is a list of experiments | yes | **no** (drawing only) |
| **F2** | Partition authority and the one-way spend of evidence | handbook v1.5 §3–§4, `DATA_SPLIT_POLICY.md` | single diagram | 56 TRAIN / 12 VALIDATION / sealed TEST; **15/15 budgets spent**; consumed markers incl. the E11 geometry population | This is the governance contribution made visible; no competing paper shows partition *consumption* | yes | **no** |
| **F3** | Episode reasoning vs the memoryless comparator | `T1_DESCRIPTIVE_REPORT_V1`, `W1_WINDOW_COMPARATOR_REPORT_V1` | (a) per-subject `episode_f1` T1 vs W1, 12 subjects; (b) paired difference with interval | **0.2524 [0.0826, 0.4415]**; difference **0.1921 [0.0505, 0.3455]**; the **7 zeros** split 3 episode-free / 4 missed | RQ4 is the only affirmative answer; panel (a) shows the heterogeneity the mean hides | yes | **no** |
| **F4** | Representation geometry and its failure minority | E10, E11, E13a receipts | (a) TRAIN vs held-out cosine distributions; (b) `‖delta‖` vs cosine scatter, 79 streams, 3 negatives marked | TRAIN min **+0.971**, **0/79**; B0 held-out **3/79**; `cos`–`norm` ρ **+0.658** | Carries C5, C6 and the closure of the B4 branch in one figure | yes | **no** |
| **F5** | The generation that passed three gates and failed the fourth | `EXPLANATION_EVALUATION_REPORT_V1` | side-by-side raw generation vs delivered output, with gate states | fidelity **1.000**, violations **0**, completeness **1.000**; **G4, G5 blocked**; mode → `DETERMINISTIC` | **The single most publishable artifact in the programme** — fluent, faithful, zero-violation, and refused | yes | **no** |
| **F6** | Streaming runtime and gate behaviour | handbook §55 | (a) throughput; (b) gate admission over the replay | **1079 windows / 89 s ≈ 61×**; **4.161 ms/window**; **0 of 1079** admitted; G5 refractory | Makes the "physical" half of IPS concrete and shows the gate is restrictive by design | yes | **no** |

**No figure requires new computation.** A candidate "T2 selection" figure was
**rejected**: its interval includes zero and Table T2 carries it adequately.
**No screenshots.**

---

## 7. Table inventory — 4 tables

| Table | Columns | Source | Why needed | Duplicates a figure? |
|---|---|---|---|---|
| **T1 · System components** | component · role · retained? · evidence artifact · decision document | handbook v1.5 §13 | Shows the system is assembled from *individually adjudicated* parts, each with a retention decision | No — F1 is topology, T1 is adjudication |
| **T2 · Primary quantitative results** | result · estimand · value · interval/denominator · partition · status | §4.1–4.5 of this audit | One place a reviewer can check every headline number and its denominator | No |
| **T3 · Personalization, uncertainty and governance** | component · what was tested · prespecified gate · outcome · retained? | M1/M2/U1 decisions + claim guard | Shows gates written **before** outcomes, including the one that rejected | Partly overlaps F2; F2 is partitions, T3 is component gates |
| **T4 · Negative findings and limitations** | finding · evidence · what it restricts · required wording | §5 + §11 of this audit | The paper's credibility rests on this table being present and unflinching | No |

**Deliberately omitted:** a per-subject numeric table (F3a shows it better) and a
T2 arm table (one row in T2 suffices).

---

## 8. Section-by-section evidence map

| § | Title | Purpose | Claims allowed | Evidence | Figures/Tables | Limitations that must appear |
|---|---|---|---|---|---|---|
| 1 | Introduction | Frame IPS: bounded intelligence in a physical monitoring loop | C1, C2, C18 | — | F1 | none yet — no numbers here |
| 2 | Related Work | Position among monitoring, personalization, agentic-safety work | none quantitative | — | — | **§2 must not be shaped by the sealed-test result** (`B4_TEST_AUTHORIZATION_V1` §6.3) |
| 3 | CardioSentinel IPS | Describe the four layers and the evidence graph | C19 | architecture, graph | F1, T1 | none autonomous |
| 4 | Experimental governance | The contribution that makes the rest credible | C3, C20, C21 | budgets, gates, consumption | F2, T3 | 15/15 spent; no external cohort |
| 5 | Representation and personalization | Encoder, its failure, memory | C4, C5, C6, C7, C8, C9, C10, C11 | sealed test, E10–E13a, M1 | F4, T2 | encoder-only; single seed; consumed population |
| 6 | Temporal and episode reasoning | RQ4, the affirmative answer | C1, C15, C16, C17 | T1, W1, T2 | F3, T2 | **bounded**; 7 zeros; signed latency |
| 7 | Uncertainty and safe adaptation | Calibration retained, router rejected | C12, C13, C14 | U1, M2 | T3 | uncalibrated sealed score; M2 is a gate |
| 8 | Agentic explanation and evidence governance | The strongest governance result | C2, C3, C19 | Qwen report, claims.py | F5, T3 | **n = 1**; lexical guard |
| 9 | Integrated runtime | Physical–digital operation | C18 | §55 | F6 | **laptop, not edge** |
| 10 | Discussion | What bounded intelligence bought | — | — | — | closure of the B4 branch |
| 11 | Limitations | Unflinching | — | — | T4 | the full §11 matrix |
| 12 | Conclusion | 3–5 contributions only | C1, C2, C3, C4, C14 | — | — | — |

**Structural recommendation:** keep the 12-section shape but **move §4
(governance) before §5**, as shown. The governance protocol is the paper's
contribution; presenting it before the results makes every subsequent negative
result read as designed rather than as an excuse.

---

## 9. Abstract claim budget — 5 claims, ranked

| Rank | Exact wording | Number | Why abstract-worthy | Qualification required |
|---|---|---|---|---|
| **1** | "episode-level reasoning improved monitoring quality over a memoryless window rule at one operating point" | **0.1921**, 95% **[0.0505, 0.3455]** | The only affirmative RQ answer, with a paired interval excluding zero | **"(at one operating point)" is mandatory** |
| **2** | "a fluent generation scoring 1.000 evidence fidelity with zero claim violations was refused at runtime for inverting a categorical gate state" | fidelity **1.000**, violations **0** | The governance thesis in one sentence; unusually concrete | **must say "in the single evaluated context"** |
| **3** | "a sealed, single-use encoder evaluation on held-out subjects" | pooled AUPRC **0.0935** at prevalence **0.0461** | Establishes the programme measured itself honestly rather than reporting development numbers | **must say "encoder-only"** and give prevalence |
| **4** | "the system replays a record at ~61× real time on a laptop CPU" | **~61×** | Makes the physical half concrete | **"laptop simulation, not edge hardware"** |
| **5** | "a preregistered uncertainty router was evaluated against a prespecified gate and rejected" | `Retained: false` | Demonstrates the gates can return no — the credibility anchor | none |

**Not in the abstract:** E11/E12d/E13a (too conditional), M1 predictive gain
(inconclusive), T2 (interval includes zero), subject-macro episode F1 (its
heterogeneity needs a figure).

---

## 10. Main contributions — exactly 4

1. **An implemented four-layer intelligent physical monitoring system** in which every component carries an individual, documented retention decision — B4-B encoder, P1-B fusion, M1L memory, M2-G contamination gate, U1 calibration, T2 temporal arm, T1 episode state machine — running as a streaming runtime at **~61× real time** on a laptop CPU. *(C18, C19, T1)*
2. **An experimentally evaluated episode-level temporal reasoning result**: subject-macro `episode_f1` **0.2524 [0.0826, 0.4415]** over 12 held-out subjects, improving on a memoryless window comparator by **0.1921 [0.0505, 0.3455]** at one operating point. *(C1, C16)*
3. **A bounded personalization and adaptation contribution**: patient memory carrying incremental patient-relative information (concordance **0.836 → 0.712** stratified) delivered through a contamination-safe update gate retained at essentially unchanged discrimination (**−0.000268** AUPRC), with a selective uncertainty router **evaluated and rejected**. *(C10, C12, C14)*
4. **An executable governance and agentic-safety contribution**: a claim boundary encoded as **25** machine-checked forbidden claims that caught **5** violations in the repository's own code, and a runtime that **refused** a fluent, fidelity-**1.000**, zero-violation generation which inverted a categorical gate state — reproduced across two independent runs. *(C2, C3)*

**Deliberately not claimed as a contribution:** representation improvement
(E11/E12d/E13a closed it), foundation-model distillation (RQ6 never begun),
confounder-aware supervision (RQ7 never begun).

---

## 11. Limitations matrix

| Limitation | Severity | Restricts | Required wording |
|---|---|---|---|
| Single primary dataset (LTSTDB) | **High** | all generalization | "results are specific to LTSTDB" |
| No independent external cohort | **High** | all external validity | "external corroboration was declined; **no second cohort will corroborate any result, permanently**" |
| Sealed test is **encoder-only** | **High** | C4 | "the sealed evaluation scored the B4-B encoder/head path, **not** the integrated system" |
| Sealed test **consumed, single use** | **High** | any re-evaluation | "used once; `repeat_attempt_permitted: false`" |
| Uncalibrated sealed score | Medium | probability language | "an uncalibrated model score, not a clinical probability" |
| Heterogeneous subject performance | **High** | C16 | "**7 of 12** subjects score zero; report the subject distribution, never the mean alone" |
| Episode misses | **High** | C16 | "**4** subjects with reference episodes produced **0** matched runs" |
| Signed latency | Medium | C17 | "a signed offset; **6 of 38** negative; does **not** establish anticipation" |
| Post-hoc mechanism work (E13a) | Medium | C9 | "exploratory post-hoc analysis of a prospectively held-out population" |
| Consumed development populations | **High** | future geometry claims | "the 44-subject / 79-stream geometry population is **consumed** for confirmatory claims" |
| Single seed per arm per fold (E11) | Medium | C7 | "an arm difference cannot be separated from single-seed training variance" |
| Unresolved M1 predictive gain | Medium | C11 | "retained on development evidence; the predictive contribution is unresolved" |
| Rejected uncertainty routing | Low | C14 | report as a rejection, not a gap |
| Laptop, not edge hardware | **High** | C18, RQ5 | "replay simulation on a laptop CPU; **no edge-hardware measurement exists**" |
| Qwen **n = 1** context, 2 models | **High** | C2 | "a demonstrated failure mode in one context — **not a failure rate**" |
| Lexical claim validator | Medium | C3 | "a lexical guard cannot distinguish an assertion from a disclaimer; **4 of 5** catches were quotations" |
| **RQ6 / RQ7 never begun** | Medium | contribution scope | "Phase 4B and Phase 6B were never begun" |

---

## 12. Manuscript evidence gaps

| Gap | Class | Detail | Mandatory? |
|---|---|---|---|
| §4 and §4.6 have **no draft** | **A — documentation** | Every source is on disk; this is writing, not research | **Mandatory** (it is the contribution) |
| §2 literature search not started | **A — documentation** | Explicitly out of scope for this task; carries the §6.3 no-contamination condition | **Mandatory**, and must precede submission |
| Control-plane says generative arm unexercised | **A — documentation** | **Corrected by this audit (§0.1)** | **Closed by this audit** |
| F1–F6 do not exist as figures | **B — figure/table** | All underlying data exists; drawing only | **Mandatory** |
| T1–T4 not assembled | **B — figure/table** | Numbers verified in §4; assembly only | **Mandatory** |
| Per-subject T1 vs W1 pairing for F3a | **C — analysis** | Both reports store per-subject `episode_f1`; a join, no new metric | Desirable, low cost |
| E13a stream-level table for F4b | **C — analysis** | `E13A_RESULTS.json` already holds all 79 rows | Desirable, low cost |
| RQ1 no-memory arm at episode level | **D — experiment** | Would need re-scoring; memory changes `m2g_detector_score` itself | **Not mandatory** — RQ1 stays open in Limitations |
| RQ5 edge-hardware measurement | **D — experiment** | Needs physical hardware the programme does not have | **Not mandatory** — RQ5 stays open; C18 is already correctly bounded |
| E8b C0/C1 incremental probe | **D — experiment** | Proposed, never executed | **Not mandatory** — C10 is already scoped to information, not prediction |
| Qwen evaluation at n > 1 | **D — experiment** | `QWEN_EVALUATION_RUN.md` template exists, NOT EXECUTED | **Not mandatory** — C2 is scoped to a demonstrated failure mode |

> ## NO FURTHER SCIENTIFIC EXPERIMENT IS REQUIRED FOR THE CURRENT PAPER.
>
> Every **D-gap** is desirable, none is mandatory, and each corresponds to a
> claim the paper is already required to scope correctly. The mandatory gaps are
> **all class A and B** — writing and drawing.

---

## 13. Red-line claims — must not appear

1. CardioSentinel **diagnoses** myocardial ischemia. *(prohibited outright)*
2. The B4 sealed test represents **full IPS performance**. *(encoder-only)*
3. **S4D is universally superior to GRU.** *(interval includes zero)*
4. **M1 definitively improves prediction.** *(no interval; inconclusive)*
5. **M2 improves classification accuracy.** *(it is a gate; AUPRC −0.000268)*
6. **Selective uncertainty routing improves safety.** *(rejected)*
7. **Morphology supervision fixes representation failures.** *(E11 Category C)*
8. **E12d proves a later checkpoint is better.** *(no outer outcome observed)*
9. **E13a confirms a general reversal mechanism.** *(1 of 2 reproduced; Decision D)*
10. A **Qwen failure rate** is established. *(n = 1 context)*
11. **External validation was completed.** *(declined, permanently)*
12. **Laptop replay is edge-device validation.** *(no edge measurement exists)*
13. *(added)* The **historical VALIDATION partition** supports a fresh confirmatory claim. *(spent across E1–E10)*
14. *(added)* The **E11 held-out geometry population** can confirm a future geometry hypothesis. *(consumed 2026-08-28)*
15. *(added)* The **claim guard guarantees** no overclaim. *(lexical; 4 of 5 catches were quotations)*
16. *(added)* **Negative latency establishes anticipation.** *(signed offset; 6 of 38)*
17. *(added)* **Subject-macro episode F1 alone** characterizes T1 performance. *(7 of 12 are zeros in two opposing classes)*

---

## 14. Paper-readiness scorecard

| Dimension | Rating | Explanation |
|---|---|---|
| Scientific evidence | **GREEN** | Every headline number traces to a frozen artifact with a denominator |
| System implementation | **GREEN** | Four layers, streaming runtime, 3,075 passing tests, individual retention decisions |
| Quantitative evaluation | **AMBER** | Predictive results are weak in absolute terms (sealed AUPRC **0.0935**) and several intervals include zero. Defensible **only** under the governance framing; a modelling paper would be RED here |
| Negative-result transparency | **GREEN** | Exceptional — rejections, refutations and withdrawals are all recorded, including two pre-execution withdrawals |
| Reproducibility | **GREEN** | Frozen digests, manifests, hash-chained receipts, bit-identical replication demonstrated in E12d |
| IPS theme alignment | **GREEN** | Physical sensing → learning → memory → reasoning → agentic explanation → streaming runtime, with evidence crossing every boundary |
| Agentic-AI relevance | **GREEN** | An executed generative arm, an executable claim boundary, and a runtime refusal with a concrete failure mode |
| External validity | **RED** | One corpus, no second cohort ever, and the strongest agentic result is **n = 1**. Cannot be fixed by writing; must be stated plainly in the abstract's framing and §11 |
| Clinical claim safety | **GREEN** | 25 machine-checked forbidden claims; no diagnostic language survives the guard |
| Narrative coherence | **AMBER** | The evidence supports the governance thesis, but the manuscript does not yet exist in the shape §8 proposes; §4/§4.6 undrafted and the ordering change is unimplemented |

**Not averaged.** The two AMBERs are closable by writing. **The RED is a
permanent property of the corpus and must be disclosed, not repaired.**

---

## 15. Final decision

> # B. READY TO DRAFT MANUSCRIPT — WITH NON-EXPERIMENTAL GAPS TO CLOSE
>
> **No new experiment is required.** All mandatory gaps are class **A**
> (documentation) and class **B** (figures/tables).

**Exact next task:** draft **§4 Experimental Governance and Evaluation
Protocol** and **§4.6**, using handbook v1.5 §3–§5, T3 and F2 as sources — the
only undrafted sections, the paper's actual contribution, and the section that
makes every subsequent negative result legible as design rather than
disappointment. **Then** assemble T1–T4 from §4 of this audit, **then** draw
F1–F6.

---

## 16. Audit non-claims

This audit created no scientific conclusion, computed no new metric, ran no
experiment, and consumed no partition. It made **one** state correction (§0.1),
grounded in a frozen report. **E11 remains Category C; E12d remains Decision D;
E13a remains Decision D; the B4 improvement branch remains CLOSED on this
corpus.**
