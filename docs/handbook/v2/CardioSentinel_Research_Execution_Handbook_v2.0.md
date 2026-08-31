# CardioSentinel — Top-Journal Research Master Blueprint

**Version 2.1 — Master Journal-Extension Research Control Plane**  
**Status:** Governing planning blueprint; grants no experimental authorization  
**Repository basis checked:** `DebalekhaChakraborty/CardioSentinel`, `master` at `3ae0a36956f1ec9ea9ee8dee4d6e26cdf2f88fdc` (checked 2026-08-31)  
**Relationship to V1:** This document does **not** supersede `CardioSentinel_Research_Execution_Handbook_v1.5.md` for the completed V1 programme. V1 remains an immutable evidence foundation. This blueprint governs a separately authorized journal-extension programme that builds on V1 without reopening, rewriting or discarding it.

**Naming note:** “V1” and “V2” in this document refer to **research evidence programmes**, not to separate commercial/product generations of CardioSentinel.

> **Control-plane rule.** This blueprint is a plan, not a licence. No experiment, dataset access, model training, re-scoring, external evaluation, LLM benchmark run, hardware measurement or manuscript claim is authorized merely because it appears here. Every scientific execution still requires its own protocol, pre-registration, data-authority check, attempt budget and explicit human authorization.
>
> **Preservation rule.** V1 is never thrown away. Its code, decisions, failures, artifacts and frozen results remain part of the scientific lineage. V2 may inherit mechanisms and motivate new hypotheses from V1, but spent V1 evidence can never be made “fresh” again.

---

## Contents

- Executive intent
- How to use this blueprint
- Part I — Repository-grounded baseline
- Part II — V2 programme charter
- Part III — Governance boundary between V1 and V2
- Part IV — Data and evidence authority
- Part V — Core workstreams
- Part VI — Conditional representation track
- Part VII — Metrics and statistical discipline
- Part VIII — Reproducibility and evidence governance
- Part IX — Programme phases and execution order
- Part X — Journal strategy
- Part XI — Risk register
- Part XII — Immediate action plan
- Part XIII — Top-journal evidence bar and publication decision framework
- Appendix A — Proposed V2 experiment ledger
- Appendix B — Pre-registration template
- Appendix C — Authorization and attempt receipt template
- Appendix D — J4 EvidenceContext schema
- Appendix E — Journal-readiness checklist
- Appendix F — Proposed V2 claim language
- Appendix G — Recommended repository layout
- Appendix H — Reviewer attack checklist
- Appendix I — Living-blueprint change control
- Appendix J — External reporting standards and venue references

---

## How to use this blueprint

This is the **master navigation document** for the journal-extension journey. It should answer four questions at any point in time:

1. **What question are we trying to close?** — map the activity to J-RQ1–J-RQ6 or the conditional R2 mechanism track.
2. **What evidence are we legally allowed to use?** — resolve data authority before implementation becomes scientific execution.
3. **What result would change the system?** — use the predefined gate and stop condition rather than adding experiments until a preferred answer appears.
4. **What claim would the result actually license?** — write the claim boundary before the run, not after seeing the metric.

### Operational cycle

Every workstream follows the same cycle:

```text
QUESTION -> PROTOCOL -> PRE-REGISTRATION -> AUTHORIZATION -> EXECUTION
        -> FAILURE/RESULT RECEIPT -> ANALYSIS -> DECISION -> CLAIM MAP
```

The blueprint is updated only when programme-level plans change. Individual experimental results belong in their own immutable reports and are referenced from the experiment ledger; they are not rewritten into this document as if the plan had predicted them.

### The programme's non-negotiable success criterion

CardioSentinel does **not** become top-journal-grade because every component wins. It becomes top-journal-grade if the programme produces **independent, fair, reproducible and clinically/physically meaningful evidence**, including negative evidence, with claims that remain narrower than the measurements.

---

## Executive intent

CardioSentinel V1 established a rigorous computational research artifact for continuous monitoring of transient ischemic ST episodes in ambulatory ECG. Its strongest contribution is not a single classifier score; it is the disciplined coupling of representation, physiology, patient-relative memory, contamination-aware adaptation, calibration, longitudinal reasoning, episode-state logic, provenance and guarded explanation under explicit claim boundaries.

The V1 record is also deliberately incomplete. Patient memory has no clean no-memory episode comparator; contamination-safe adaptation has not been evaluated as a full episode-level stress study; the T1 state machine beats W1 only at the operating point promoted with T1 in the loop; the explanation guard has only a two-model, one-context generative demonstration; there is no independent external cohort; and the runtime is a laptop replay rather than a measured edge/wearable system. The sealed neural representation also underperformed the classical morphology baseline on its consumed held-out benchmark.

**V2 exists to turn those limitations into a coherent journal-grade research programme without rewriting V1.** The central thesis is:

> **An adaptive physiological monitoring system should be judged not only by what it predicts, but also by what observations it may learn from, how evidence persists into an event, how the system behaves under distribution shift and resource constraints, and what claims its human-facing AI layer is permitted to assert.**

The intended end state is not “a better ischemia classifier.” It is a reproducible, evidence-governed adaptive physical-intelligence system evaluated across predictive validity, personalization, temporal reasoning, distribution shift, explanation consistency and real physical execution.

---

## V1 is the foundation, not waste

The journal extension is **not a restart**. The correct model is:

```text
                    CARDIOSENTINEL SCIENTIFIC LINEAGE

  V1 — completed / sealed evidence programme
       |
       |  inherits architecture, code, lessons, negative findings,
       |  reproducibility machinery and hypothesis motivation
       v
  V2 — journal-extension programme
       |
       |  asks new preregistered questions on fair development geometry
       |  and genuinely fresh confirmation
       v
  Journal evidence package
```

### What is retained from V1

- the entire repository history and frozen artifacts;
- B0–B4 development and sealed outcomes, including weak/negative results;
- P1-B physiology, M1L memory, M2-G gate, Platt calibration, S4D selection and T1 episode logic as **candidate inherited mechanisms**;
- the evidence graph, claim boundary, replay runtime and agentic guard architecture;
- the reproducibility, attempt-budget, provenance and failure-receipt machinery;
- V1 limitations as explicit generators of V2 research questions.

### What is not reused as fresh evidence

- the consumed V1 sealed TEST;
- V1 validation/test outcomes as confirmation of hypotheses invented after those outcomes were seen;
- any V1 threshold or model choice whose “success” depends on post-hoc re-selection;
- quarantined failed-attempt outputs.

### Why preserving V1 makes the journal paper stronger

A top reviewer can see the complete scientific trajectory: what was tried, what failed, what was selected under frozen rules, what remained unresolved, and which new experiments were designed specifically to resolve those gaps. The journal extension therefore becomes a **prospective extension of an auditable research programme**, rather than a polished retrospective benchmark exercise.

---

# Part I — Repository-grounded baseline

## 1. What V1 already established

The following statements are repository-grounded facts from the current V1 programme. They are inputs to V2 planning, not claims newly created by this handbook.

| Area | V1 state carried into V2 planning |
|---|---|
| Scope | Ambulatory ECG monitoring of transient ischemic ST episodes; research alerting, not diagnosis or medical-device validation |
| Primary corpus | LTSTDB |
| Representation | B4-B CNN-Transformer selected over B4-A and B4-C on development criteria |
| Sealed representation benchmark | B4-B pooled AUPRC 0.0935; B3 classical morphology baseline 0.1683 on the same consumed held-out partition |
| Physiology fusion | P1-B retained, with false-positive-rate caveat |
| Patient memory | M1L retained among memory variants; no clean no-memory episode comparator |
| Adaptation | M2-G retained over naive updating; strong drift reduction but mixed false-alarm trade-offs |
| Calibration/routing | Platt calibration retained; selective uncertainty router rejected |
| Longitudinal arm | S4D selected by the frozen rule; comparison interval includes zero, so no universal superiority claim |
| Episode reasoning | T1 state machine retained; W1 comparison supports RQ4 only at the promoted operating point |
| Generative explanation | Qwen3-1.7B produced an evidence-state inversion and was refused; Qwen3-4B-Instruct-2507 aligned and was served; one contracted context only |
| Runtime | Stored-record replay on a laptop; no sensor acquisition, edge-hardware power or thermal measurement |
| V1 budget state | All fifteen one-shot budgets spent; old sealed TEST must never be reopened |

The current V1 handbook describes the programme as one where the rigour lies in the boundaries. V2 preserves that posture. A V2 result may revise the future system design, but it must never rewrite what V1 measured or retroactively improve a V1 claim.

## 2. Source hierarchy for this handbook

This V2 plan was built after checking the following current repository authorities:

1. `README.md` — public research-artifact framing and current system architecture.
2. `docs/handbook/CardioSentinel_Research_Execution_Handbook_v1.5.md` — governing account of the completed V1 programme.
3. `docs/control-plane/CURRENT_STATE.md` — living repository-state cache.
4. `docs/control-plane/EXPERIMENT_CATALOGUE.md` — experiment locations, status and consumption rules.
5. `docs/control-plane/IMPROVEMENT_ROADMAP_V1.md` — post-hoc forward plan after the consumed B4 sealed evaluation.
6. `docs/control-plane/RESEARCH_SCOPE.md` — non-diagnostic scope and original physical-system research boundary.

**Authority rule:** if this handbook paraphrases a V1 result differently from a frozen V1 report, the frozen report wins. If a V1 living document conflicts with the current V1.5 handbook, V1.5 is the higher programme authority. This handbook is not permitted to “fix” historical evidence by wording.

## 3. What V2 must not inherit as if it were fresh evidence

The following are permanently non-fresh for confirmatory V2 claims:

- the consumed V1 sealed TEST;
- historical V1 VALIDATION as a new confirmatory set;
- any V1 result used to choose the V2 hypothesis it is then asked to confirm;
- quarantined failed attempts;
- any external route that is silently re-labelled without a new V2 authority decision.

V2 may use V1 findings to motivate hypotheses. It may use V1 TRAIN data for development if a new V2 protocol permits it. It may describe historical validation/test results. It may not turn those results back into an unspent test set.

---

# Part II — V2 programme charter

## 4. Programme objective

**Primary objective:** establish whether evidence-governed adaptive intelligence improves the trustworthiness and usefulness of continuous physiological monitoring when evaluated under fair comparators, fresh external evidence and real physical execution constraints.

V2 has six core research questions.

| ID | Research question | V1 gap closed |
|---|---|---|
| **J-RQ1** | Does patient-relative memory improve episode-level monitoring over an otherwise matched no-memory system, and when does that benefit emerge after cold start? | V1 RQ1 open |
| **J-RQ2** | Does contamination-gated adaptation preserve patient state better than naive or non-adaptive policies under normal variation, abnormal episodes and signal-quality shift without unacceptable detection trade-offs? | V1 RQ2 partial |
| **J-RQ3** | Does stateful episode reasoning outperform a separately tuned memoryless comparator under a fair, independently selected operating point? | Removes the V1 RQ4 operating-point bound |
| **J-RQ4** | How does a frozen V2 system transfer to genuinely new subjects and acquisition conditions, and which component fails first under cross-dataset distribution shift? | No external corroboration in V1 |
| **J-RQ5** | Can model-independent guards reliably detect and suppress generative explanations that contradict structured physical-system state across many contexts and model families? | V1 generative evidence is n=1 context |
| **J-RQ6** | Can the retained control pattern execute continuously on an ECG-capable physical/edge platform within defined latency, memory, energy and signal-quality limits? | V1 RQ5 open |

**Scope discipline:** the old V1 RQ6 foundation-model distillation and V1 RQ7 confounder-aware multi-task learning are not automatically promoted into the V2 core. They remain optional mechanism tracks and require their own justification if evidence from J-RQ1–J-RQ6 makes them necessary.

## 5. V2 thesis hierarchy

The journal programme should distinguish four levels of evidence rather than collapsing everything into “performance.”

### Level A — predictive evidence
Can the scoring path discriminate and rank useful physiological evidence on new subjects?

### Level B — adaptive-state evidence
Can the system personalize without allowing abnormal or unreliable observations to corrupt the patient state it learns from?

### Level C — event-semantics evidence
Can the system convert window evidence into stable episodes more credibly than a fair memoryless alternative?

### Level D — operational truthfulness
Can a human-facing explanation remain consistent with structured machine state, provenance and uncertainty boundaries?

A journal paper may succeed even if one level is negative. The programme fails only if negative results are hidden, controls are changed after seeing the answer, or evidence boundaries become ambiguous.

## 6. Non-diagnostic and non-device boundary

V2 remains research monitoring unless and until a separate clinical/regulatory programme exists. The following remain prohibited claims:

- diagnosis of myocardial ischemia in a patient;
- treatment or triage recommendation;
- clinical safety or clinical utility;
- medical-device validation;
- generalization beyond the evaluated cohorts;
- deployment validation merely because code runs on a small computer;
- smartwatch/smart-ring readiness without device-specific acquisition and validation;
- “early detection” inferred only from negative overlap latency.

A future wearable experiment may establish **engineering feasibility**. It does not create clinical evidence.

---

# Part III — Governance boundary between V1 and V2

## 7. Immutable V1 record

V1 should be treated as a sealed historical programme.

**Never:**

- reopen or re-score the old sealed TEST;
- replace B4-B inside the V1 runtime and inherit downstream V1 evidence as if nothing changed;
- retune V1 thresholds against consumed held-out subjects;
- change old experiment outcomes because V2 finds a better mechanism;
- delete rejected arms or failed attempts;
- rewrite a negative result into an “initial baseline.”

V2 is allowed to say: “V1 found X; V2 therefore preregistered Y.” It is not allowed to say: “V2 found Y, therefore V1 should be interpreted as if Y had always been known.”

### 7.1 V1-to-V2 inheritance matrix

| Asset | Keep? | V2 use | Restriction |
|---|---|---|---|
| V1 source code and architecture | **Yes** | starting implementation / comparator | changes must be versioned under V2 |
| V1 TRAIN-authorized data | **Yes, conditionally** | V2 development/cross-fitting | only under new V2 data-authority protocol |
| V1 VALIDATION | **Historical only** | describe prior evidence | never fresh confirmation |
| V1 sealed TEST | **Historical only** | preserve/report | never reopen or re-score as a new claim |
| V1 frozen checkpoints | **Yes** | baseline/ablation/reproduction | do not relabel as newly trained models |
| V1 thresholds | **Yes as historical baselines** | comparator/reference | fair V2 comparators get their own tuning where required |
| V1 negative/rejected results | **Yes** | hypothesis generation and claim boundaries | never delete or rewrite |
| V1 evidence graph / guard code | **Yes** | foundation for J4 | benchmark evidence must be newly frozen |
| V1 laptop replay runtime | **Yes** | H0 engineering baseline | not an edge-device result |
| V1 manuscript narrative | **Historical only** | lineage/reference | not scientific authority |

## 8. New programme identity

Recommended conceptual namespace:

```text
CardioSentinel V1    completed evidence programme
CardioSentinel V2    journal-extension programme

V2 workstreams:
  J1  fair episode comparator
  J2  memory contribution / cold start
  J3  adaptation stress and recovery
  J4  explanation-state consistency benchmark
  J5  external validation
  J6  edge / wearable physical execution
  R2  representation 2.0, conditional mechanism track
```

The `J` prefix prevents collision with V1 experiment names and makes it obvious that a result came from the new programme.

## 9. Authorization model

Every V2 scientific execution should pass through five states:

```text
QUESTION
  -> PROTOCOL
  -> PRE-REGISTRATION
  -> AUTHORIZATION
  -> EXECUTION
  -> REPORT / DECISION
```

A code implementation may exist before authorization if it is tested only on synthetic fixtures or clearly non-scientific toy data. The first access to real scientific rows under the new hypothesis is the execution boundary.

**No automatic retry.** A failed real-data execution must be classified before any re-run:

- launch failure;
- harness/apparatus failure;
- data-bound failure;
- scientific negative result.

Only the first three can even be candidates for a replacement attempt, and only after a written failure receipt and new authorization.

---

# Part IV — Data and evidence authority

## 10. Development data policy

For the cleanest V2 separation, use the original LTSTDB **TRAIN** subjects as the default legacy development pool. Historical V1 VALIDATION and TEST remain spent for fresh confirmation.

Within TRAIN, V2 may establish a new prospective subject-disjoint cross-fitting geometry. The split must be frozen before model comparison and reused across all arms that claim paired comparability.

Recommended minimum reporting for every development fold:

- number of subjects and evaluable subjects;
- number of windows and reference episodes;
- positive prevalence;
- pooled and subject-macro metrics;
- denominator of every macro metric;
- threshold-transfer behaviour across folds;
- per-subject distribution, not only pooled mean.

## 11. Fresh external cohort policy

J-RQ4 requires genuinely new evidence. V2 should therefore begin a fresh external-corpus qualification programme rather than treating “find another ECG dataset” as an implementation detail.

### 11.1 Qualification criteria before data access

For each candidate cohort, record:

- license and redistribution constraints;
- subject overlap risk with LTSTDB or other PhysioNet-derived cohorts;
- lead configuration and lead semantics;
- sampling frequency and resolution;
- annotation source and event definition;
- ischemic vs non-ischemic ST-event semantics;
- record duration;
- prevalence and class structure;
- availability of raw waveform rather than only derived features;
- whether event timing supports episode-level evaluation;
- whether acquisition conditions are materially different enough to test transfer.

### 11.2 Contamination audit

Before external data reaches the analysis path, produce a V2 contamination audit that answers:

1. Have any subjects or records appeared in V1 development, exploratory notebooks or figures?
2. Has anyone inspected outcome labels during dataset selection?
3. Was the cohort chosen because a pilot result looked favourable?
4. Are annotation semantics compatible enough to support the registered endpoint?
5. Does the cohort require a mapping that itself uses labels?

If any answer weakens independence, downgrade the evidence level before execution rather than after.

### 11.3 External one-shot rule

Once the V2 model/system and primary endpoint are frozen, the first confirmatory evaluation on the designated external cohort should be treated as one-shot. No model or threshold changes in response to that result are allowed to remain in the same confirmatory claim.

A second cohort, if available, is preferred to repeated tuning on the first.

---

# Part V — Core workstreams

## 12. J1 — Fair stateful vs memoryless episode comparator

### 12.1 Question

Does T1-like stateful episode reasoning retain an advantage when the memoryless comparator receives its **own** development-tuned operating point?

### 12.2 Why this is first

The V1 T1-W1 result is encouraging but explicitly bounded because both arms inherit thresholds promoted with the state machine in the loop. A fair comparator is the highest-value way to either strengthen or falsify the current event-semantics claim.

### 12.3 Design

Use identical upstream score/evidence rows and create two decision policies:

- **J1-S:** stateful NORMAL/WATCH/EVENT/RECOVERY policy;
- **J1-W:** memoryless window policy with independently tuned threshold/rule.

Tune each arm using the same prospective TRAIN-only cross-fitting design. Freeze both independently before any external evaluation.

### 12.4 Primary endpoints

- subject-macro episode F1;
- paired subject-level difference J1-S minus J1-W;
- bootstrap interval with subject as the resampling unit.

### 12.5 Secondary endpoints

- episode sensitivity and precision;
- false alarms per hour;
- number of predicted runs;
- median predicted run duration;
- fragmentation: predicted runs per reference episode;
- overlap latency as descriptive only;
- subject-stratified failure modes.

### 12.6 Decision gate

**Gate A — comparator credibility**

- **PASS:** stateful policy retains practically meaningful advantage under independently tuned operating points and the uncertainty interval supports the direction.
- **MIXED:** point estimate favours stateful reasoning but uncertainty is wide or highly subject-dependent.
- **FAIL/NEGATIVE:** the fair memoryless policy matches or beats it.

All three are publishable outcomes if preregistered.

---

## 13. J2 — Does patient memory actually help?

### 13.1 Question

Does patient-relative memory improve episode-level monitoring over a matched no-memory system, and what is the cost of cold start?

### 13.2 Arms

At minimum:

- **J2-NM:** no patient-relative memory;
- **J2-M:** retained long-timescale memory concept, under the V2 frozen implementation.

Everything else should be matched as closely as possible. A change to memory must not silently change calibration, temporal logic or threshold selection unless the protocol explicitly defines a full-system retuning comparison.

### 13.3 Cold-start analysis

Pre-register elapsed-monitoring strata, for example:

- 0–5 min;
- 5–15 min;
- 15–30 min;
- 30–60 min;
- greater than 60 min.

Primary cold-start questions:

- when does memory become populated enough to affect decisions?
- does sensitivity initially fall because memory has not stabilized?
- how many admitted updates are required before patient-relative information becomes useful?
- is wall-clock acquisition time or admitted-update count the better maturity variable?

### 13.4 Primary endpoints

- episode F1 difference no-memory vs memory;
- false alarms/hour difference;
- sensitivity difference;
- per-subject heterogeneity.

### 13.5 Mechanism endpoints

- memory update admission rate;
- distribution of long-memory deviation;
- number of updates to stable baseline;
- performance as a function of admitted-update count.

### 13.6 Decision gate

**Gate B — personalization value**

Memory is retained in V2 only if it changes an endpoint or mechanism in a way that justifies its statefulness and complexity. “It produces an interesting feature” is not enough.

---

## 14. J3 — Contamination-safe adaptation under stress

### 14.1 Question

Can the system continue to adapt to benign subject variation while resisting contamination from abnormal or unreliable observations?

### 14.2 Comparator policies

Recommended core arms:

1. **STATIC:** no online baseline update after initialization;
2. **ALWAYS:** naive/always update;
3. **GATED:** contamination-aware update policy.

A fourth confidence-weighted policy may be added only if motivated and preregistered before results.

### 14.3 Stress families

Use a frozen perturbation registry rather than ad hoc “interesting examples.” Candidate families:

- ischemic/event-labelled intervals;
- heart-rate-related morphology change;
- unreadable/low-SQI intervals;
- baseline wander;
- amplitude scaling;
- additive noise at preregistered SNR levels;
- missing/dropout windows;
- transient acquisition interruption;
- lead or axis perturbation only where physiologically and technically defensible.

Synthetic perturbations must be identified as synthetic. They test engineering robustness, not clinical prevalence.

### 14.4 Primary adaptation endpoints

- prototype/state drift during stress;
- state recovery time after stress ends;
- update admission fraction;
- detection degradation during and after stress;
- false-alarm effect;
- percentage of benign windows that remain learnable.

### 14.5 Key principle

The winning policy is **not** the one that blocks the most updates. A never-update system trivially avoids contamination but also ceases to adapt. The central trade-off is:

> preserve a useful adaptation channel while refusing observations that would corrupt the patient state.

### 14.6 Decision gate

**Gate C — adaptation integrity**

The gated policy must demonstrate both contamination resistance **and** non-trivial adaptation. Drift reduction without useful update admission is not sufficient.

---

## 15. J4 — Explanation-state consistency benchmark

### 15.1 Question

Can a model-independent guard detect operationally wrong generative explanations even when the prose is fluent, numerically plausible and lexically compliant?

### 15.2 Why this should become a real benchmark

V1 revealed a highly specific failure: a local model could cite the correct evidence and still invert categorical gate state. The V2 objective is to determine whether that is an isolated anecdote or a repeatable class of failure, and whether deterministic guards reduce it without rejecting too many correct explanations.

### 15.3 Benchmark unit

The unit is a **structured EvidenceContext**, not a free-form clinical vignette. Each context should be generated or authored before model evaluation and should contain only fields the runtime is legitimately allowed to expose.

Recommended benchmark size: **120–240 frozen contexts**, subject to a separate protocol. The exact number should be justified by coverage and cost, not chosen after observing model error rates.

### 15.4 Context dimensions

Stratify across:

- system state: NORMAL / WATCH / EVENT / RECOVERY;
- gate patterns including PASS/BLOCK combinations;
- memory update admitted/refused;
- low/high calibrated probability;
- low/high temporal evidence;
- complete vs missing provenance;
- open vs closed event;
- ambiguous evidence where abstention is correct.

Do not enumerate all 64 gate combinations mechanically unless they are semantically reachable. Include reachable states and a smaller set of deliberately invalid contexts for guard testing, clearly labelled as synthetic adversarial cases.

### 15.5 Error taxonomy

At minimum:

| Code | Error class | Example |
|---|---|---|
| **E-NUM** | numeric contradiction | reported probability differs from structured value beyond tolerance |
| **E-CAT** | categorical inversion | G4 BLOCK becomes “G4 passed” |
| **E-STATE** | episode-state inversion | EVENT described as NORMAL |
| **E-UNSUP** | unsupported causal/clinical claim | explanation asserts diagnosis or mechanism absent from evidence |
| **E-MISS** | invented missing evidence | unavailable artifact described as verified |
| **E-OMIT** | omission of required safety boundary | materially incomplete explanation |
| **E-ABST** | failure to abstain | model asserts certainty where the evidence contract requires uncertainty/fallback |

### 15.6 Model panel

Use a small, justified model panel rather than a model zoo. Recommended scope: **3–5 models** spanning at least two sizes or families that can run under the intended local/controlled environment.

Default decoding for the primary benchmark should be deterministic where possible. If stochastic robustness is studied, it should be a separately preregistered repeated-generation analysis.

### 15.7 Primary metrics

- pre-guard operational contradiction rate;
- guard recall for true contradictions;
- guard false-refusal rate on correct outputs;
- post-guard served-output contradiction rate;
- deterministic-fallback coverage;
- end-to-end explanation latency.

### 15.8 Secondary metrics

- evidence fidelity;
- completeness;
- lexical claim violations;
- error rate by context type and model;
- agreement between automated and human/independent adjudication on an audit subset.

### 15.9 Decision gate

**Gate D — explanation safety utility**

The guard is useful only if it materially lowers served operational contradictions while keeping false refusal within a pre-specified acceptable bound.

A larger model being “better” is not the research claim. The research claim is about **guarded exposure of generated explanations under structured evidence authority**.

---

## 16. J5 — External validation and transfer diagnosis

### 16.1 Question

What survives when the frozen V2 system meets new subjects, acquisition conditions and annotation practice?

### 16.2 Two-stage design

**Stage 1 — dataset qualification**  
No model result. Establish compatibility, independence and endpoint mapping.

**Stage 2 — frozen evaluation**  
One-shot execution of the registered V2 system and comparators.

### 16.3 What to freeze before external execution

- representation/scoring path;
- patient-memory policy;
- update gate;
- calibration method;
- temporal evidence model;
- episode policy;
- thresholds/operating-point selection procedure;
- primary and secondary metrics;
- missing-data handling;
- cohort inclusion/exclusion rules;
- bootstrap unit and random seed(s) where applicable.

### 16.4 External evaluation should diagnose, not merely score

Report:

- overall and subject-macro performance;
- per-subject score distribution;
- prevalence shift;
- calibration shift;
- threshold-transfer penalty;
- event-duration distribution shift;
- memory-update admission shift;
- gate-block reason distribution;
- which component first deviates from V2 development behaviour.

A weaker external result is still valuable if the programme can say **why** it failed without tuning to the answer.

### 16.5 Decision gate

**Gate E — external robustness**

Do not define PASS as “metric exceeds V1.” Define it as a preregistered combination of usable discrimination, bounded calibration/threshold transfer and interpretable failure behaviour appropriate to the target journal claim.

---

## 17. J6 — Physical edge/wearable execution

### 17.1 Question

Can the V2 control pattern operate continuously on a real ECG-capable physical platform under resource and acquisition constraints?

### 17.2 Hardware progression

Use a staged path:

1. **H0 — existing stored-record laptop replay.** Baseline only; not an edge result.
2. **H1 — real ECG acquisition device or development board.** Establish acquisition correctness and timing.
3. **H2 — constrained edge compute or mobile gateway.** Run the monitoring path under CPU/RAM limits.
4. **H3 — ECG-capable wearable/patch integration.** Measure sustained execution with realistic sensing interruptions/noise.
5. **H4 — smartwatch-class ECG feasibility.** Only after lead geometry, sampling and acquisition regime are explicitly revalidated.

A smart ring is **not** a drop-in endpoint for the present ST-morphology pipeline because most rings are PPG-centric. Ring deployment belongs to a separate multimodal sensing programme unless an ECG-capable device with suitable signal geometry is available.

### 17.3 Engineering endpoints

- end-to-end sample-to-decision latency;
- per-window inference latency distribution, not only mean;
- peak and steady-state RAM;
- CPU utilization;
- model/artifact footprint;
- energy per window or per minute;
- sustained power and thermal behaviour;
- dropped-window rate;
- 1-hour and extended continuous-run stability;
- acquisition jitter and data-loss rate;
- signal-quality distribution under real acquisition.

### 17.4 Behavioural endpoints under real acquisition

- update-gate reason distribution;
- number of memory updates admitted;
- whether degraded physical signal is blocked from adaptation;
- effect of interruptions on episode state;
- recovery after acquisition resumes;
- consistency between replayed and physically acquired test signals where a controlled signal source permits it.

### 17.5 Decision gate

**Gate F — edge feasibility**

A successful result means the system can execute the registered monitoring/control loop within a realistic resource envelope for the selected device class. It does **not** mean clinical deployment readiness.

---

# Part VI — Conditional representation track

## 18. R2 — Representation 2.0: mechanism before architecture search

The V1 sealed result cannot be ignored: the learned encoder retained signal but did not match the classical ST-morphology baseline. V2 should not respond with blind architecture search.

### 18.1 First question

**What information does B3 morphology carry that the learned representation fails to preserve or use across subjects?**

Candidate analyses, development-only:

- probe whether B3 feature components are predictable from the frozen embedding;
- within-subject vs between-subject separability;
- baseline-referenced morphology contrast;
- score transfer across subjects;
- representation stability under rate, amplitude and axis perturbations;
- paired error analysis where B3 is correct and B4 is not.

### 18.2 Candidate V2 representations only after mechanism evidence

If the mechanism supports intervention, candidate families may include:

- baseline-referenced encoding;
- physiology-informed learned representation;
- hybrid classical morphology + neural embedding;
- subject-balanced or within-subject contrastive objectives;
- explicit invariance to subject identity where justified.

### 18.3 What is deliberately low priority

- large architecture sweep;
- focal loss merely because the task is imbalanced;
- arbitrary context-length search;
- replacing Transformer with another fashionable sequence model without a mechanism hypothesis.

### 18.4 Representation promotion rule

A new representation may enter the scored V2 system only after:

1. mechanism hypothesis preregistered;
2. development comparison completed under the frozen V2 cross-fitting instrument;
3. endpoint alignment checked at episode level where the full system claim depends on it;
4. representation decision frozen **before** external evaluation.

If no representation clearly earns promotion, V2 may legitimately use a classical or hybrid representation. The programme is not obligated to keep a neural encoder for aesthetic reasons.

---

# Part VII — Metrics and statistical discipline

## 19. Endpoint hierarchy

Every V2 experiment must declare one primary endpoint family and separate secondary/descriptive analyses.

Recommended hierarchy:

### Representation/scoring
- pooled AUPRC;
- subject-macro AUPRC with denominator;
- AUROC as secondary where class structure permits;
- calibration only for calibrated outputs.

### Episode reasoning
- subject-macro episode F1;
- sensitivity/precision;
- false alarms/hour;
- fragmentation.

### Adaptation
- state/prototype drift;
- recovery time;
- update admission fraction;
- downstream detection trade-offs.

### Explanation
- served-output contradiction rate;
- guard recall;
- false-refusal rate.

### Edge
- latency percentile(s);
- RAM;
- energy/power;
- sustained runtime stability.

## 20. Statistical unit

For generalization claims, the subject should normally be the resampling/inference unit rather than the window. Windows within a subject are strongly dependent and must not be treated as independent evidence merely to create a large `n`.

Where episodes are nested in subjects, report both episode counts and subject counts. Bootstrap at the subject level unless a preregistered hierarchical procedure is justified.

## 21. Paired comparisons

When two arms use the same subjects, prefer paired subject-level contrasts. Report:

- point estimate;
- interval;
- subject count;
- subjects favouring each arm;
- zero/undefined subjects and why;
- pooled result separately from macro result.

## 22. Multiple comparisons

Do not create dozens of nominal p-values from exploratory subgroups. For preregistered multiple primary endpoints, define either:

- a hierarchical testing order;
- multiplicity adjustment;
- or a decision rule based on confidence intervals and practical thresholds rather than significance fishing.

## 23. Negative results

Negative results are first-class outputs. The handbook specifically expects possible negatives:

- independently tuned W1 may remove T1's apparent advantage;
- patient memory may not improve episode outcomes;
- gating may protect memory but worsen false alarms;
- external transfer may be poor;
- larger LLMs may still produce state contradictions;
- the edge runtime may miss power or thermal targets.

A negative result should trigger a decision record, not a silent new hyperparameter sweep.

---

# Part VIII — Reproducibility and evidence governance

## 24. Experiment artifact minimum

Every scientific V2 run should emit, at minimum:

- protocol identifier and digest;
- code commit SHA;
- data-manifest digest;
- environment digest/container identifier;
- split digest;
- random seed(s);
- authorization receipt;
- attempt sequence;
- start/end timestamps;
- failure-state field;
- primary metrics artifact;
- per-subject outputs needed for the registered analysis;
- immutable decision/report pointer after interpretation.

## 25. Environment policy

V1's scientific environment should remain untouched as an archival reproducibility target. V2 should create a **new isolated environment** rather than upgrading the V1 environment in place.

Recommended policy:

```text
V1 environment   archival, immutable, reproduce-only
V2 environment   new lockfile/container, explicit versioned digest
UI environment   separate from scientific execution when possible
hardware image   separately versioned for J6
```

This prevents a journal extension from invalidating the ability to reproduce V1.

## 26. Synthetic fixtures vs scientific data

Unlimited iteration is acceptable on synthetic/unit-test fixtures provided those fixtures cannot answer the scientific question. Real-data execution begins only when the code can emit a scientifically interpretable result.

A synthetic smoke test that verifies file shapes is not an attempt. A “smoke test” that happens to compute the primary metric on real V2 subjects is an attempt regardless of what it is called.

## 27. Failure receipts

Every failed scientific attempt must record:

- stage reached;
- data touched;
- whether primary outputs became visible;
- whether the failure could bias a replacement attempt;
- root cause;
- files quarantined;
- explicit decision on whether a new attempt may be requested.

Do not delete a failed attempt to make the ledger cleaner.

---

# Part IX — Programme phases and execution order

## 28. Phase roadmap

The following is a **planning sequence**, not a fixed calendar. Several tracks can overlap only after their dependencies are frozen.

| Phase | Approx. effort | Purpose | Exit gate |
|---|---:|---|---|
| **P0 — V2 charter** | 1–2 weeks | finalize RQs, authority, naming, split policy, attempt budgets | handbook + V2 research charter approved |
| **P1 — fair comparators** | 3–5 weeks | J1 fair W1/T1 + J2 memory/no-memory | Gate A and Gate B decisions recorded |
| **P2 — adaptation robustness** | 3–5 weeks | J3 stress registry and adaptation study | Gate C decision recorded |
| **P3 — explanation benchmark** | 3–5 weeks | freeze contexts, evaluate 3–5 models, guard study | Gate D decision recorded |
| **P4 — external qualification/evaluation** | 4–10 weeks | identify cohort, contamination audit, one-shot evaluation | Gate E decision recorded |
| **P5 — physical edge system** | 4–10 weeks | acquisition + constrained runtime + power/latency measurement | Gate F decision recorded |
| **P6 — journal synthesis** | 3–6 weeks | integrated analysis, figures, manuscript | target venue selected from evidence, not aspiration |

P3, P4 and hardware procurement for P5 may proceed partly in parallel, but **external scoring must wait until the V2 system to be evaluated is frozen**.

## 29. Recommended dependency graph

```text
P0 V2 CHARTER
   |
   +--> J1 FAIR EPISODE COMPARATOR ----+
   |                                    |
   +--> J2 MEMORY ABLATION -------------+--> V2 SYSTEM FREEZE --> J5 EXTERNAL
   |                                    |
   +--> J3 ADAPTATION STRESS -----------+
   |                                    |
   +--> R2 REPRESENTATION (conditional)-+
   |
   +--> J4 EXPLANATION BENCHMARK (can proceed independently after context freeze)
   |
   +--> J6 HARDWARE ACQUISITION WORK (interface work can start early; scored run waits for freeze)
```

## 30. Stop conditions

The programme should stop or narrow rather than expand indefinitely when:

- J1 shows no stateful advantage and no mechanistic benefit worth retaining;
- J2 shows patient memory contributes no practical value;
- no defensible external cohort can be qualified;
- hardware acquisition signal is incompatible with the ST-morphology assumptions;
- the explanation guard adds no benefit over deterministic explanation;
- R2 mechanism study does not identify a coherent representation defect.

Stopping a track is a successful governance outcome when the evidence says it should stop.

---

# Part X — Journal strategy

## 31. Minimum journal-grade package

A credible full journal extension should contain at least:

1. **fair independently tuned stateful vs memoryless episode comparison;**
2. **clean no-memory vs patient-memory ablation;**
3. **proper multi-context explanation-consistency benchmark;**
4. **fresh external evaluation or a clearly different independent acquisition cohort.**

Without #4, the work may still be publishable as a systems/methodology paper, but its biomedical generalization claim must remain narrow.

## 32. Strong systems package

Add:

- J3 adaptation stress/recovery analysis;
- J6 real ECG acquisition and constrained edge measurements;
- evidence of gate behaviour under real signal degradation.

This version supports a stronger Intelligent Physical Systems / IoT / biomedical engineering positioning.

## 33. Ambitious package

The highest-tier version would combine:

- fair episode comparator;
- validated personalization contribution;
- contamination-safe adaptation under stress;
- mechanism-driven representation improvement or justified classical/hybrid retention;
- external frozen cohort;
- large explanation-state benchmark;
- real edge/wearable acquisition;
- open reproducibility bundle with hardware and software manifests.

The ambition is not “all metrics must improve.” The ambition is that **every layer has a fair question, a frozen comparator and a clear boundary on what the answer means**.

## 34. Venue selection principle

Do not choose the final journal first and then manufacture the story. Choose the venue after P4/P5 based on what the evidence actually supports.

Possible direction examples:

- strong ECG/personalization/external-validation evidence -> biomedical signal-processing journal;
- broader computational biomedical system + robust evaluation -> biomedical computing journal;
- real sensor/edge acquisition + system/control novelty -> IoT/connected-health systems journal;
- very strong external evidence + informatics contribution -> higher-tier biomedical informatics venue.

Conference-to-journal extension rules must be checked against the eventual venue. If the TACTiCS paper becomes formally published, the journal version must be a substantial extension and should disclose/cite the prior conference version as required.

---

# Part XI — Risk register

## 35. Scientific risks

| Risk | Consequence | Mitigation |
|---|---|---|
| Fair W1 tuning removes T1 advantage | headline weakens | report honestly; investigate event semantics rather than re-tuning until positive |
| Memory has no episode value | personalization narrative weakens | simplify system; retain only if it provides a different justified function |
| Gating blocks too much | “safe adaptation” becomes near-static | make update admission and recovery co-primary mechanism endpoints |
| External cohort incompatible | no valid transfer claim | perform qualification before data access; seek another cohort rather than force mapping |
| External performance collapses | generalization weak | component-level transfer diagnosis; no post-hoc tuning within same confirmatory claim |
| LLM guard false-refuses too often | poor usability | preregister false-refusal bound; compare deterministic-only strategy |
| Edge target cannot sustain runtime | no deployment feasibility | optimize only after baseline measurement; document resource bottleneck |
| Representation 2.0 becomes endless search | programme drifts into benchmark chasing | require mechanism hypothesis before every representation experiment |

## 36. Governance risks

| Risk | Mitigation |
|---|---|
| V1/V2 evidence mixed | use `J*` namespace, new environment, new reports, explicit V1 archival status |
| Old TEST accidentally reopened | structural code authority should make old TEST inexpressible in V2 runners |
| External data inspected too early | dataset qualification and contamination audit before waveform/labels enter analysis path |
| “Smoke test” leaks scientific result | synthetic fixtures only before authorization |
| UI or LLM dependency changes science environment | separate presentation/agent environment from scientific runtime where possible |
| Negative result triggers uncontrolled retries | written decision before any replacement attempt |

---

# Part XII — Immediate action plan

## 37. What to do next

### Master execution rule

The first journal-extension milestone is **not another model**. It is a frozen programme authority capable of making future results interpretable.

Do **not** begin J1 training or buy hardware first. The next deliverable should be a V2 research charter that ratifies this handbook and converts the proposed structure into executable authority.

Recommended immediate sequence:

1. **Create the V2 namespace and document hierarchy** without changing any V1 evidence.
2. **Freeze J-RQ1–J-RQ6 wording** and define which RQs are core vs optional.
3. **Define the TRAIN-only V2 cross-fitting instrument** and threshold-transfer reporting.
4. **Write J1 protocol/pre-registration** for independently tuned stateful vs memoryless comparison.
5. **Write J2 protocol/pre-registration** for no-memory vs patient-memory and cold-start strata.
6. In parallel, begin **external cohort qualification research** and **edge hardware requirements**, but do not score external data or perform scientific hardware claims yet.
7. Build the **J4 context schema and generation rules** before running any model over the benchmark.

## 38. First three documents to create in the repository

Recommended, but not yet created by this handbook:

```text
docs/journal-extension/
  CARDIOSENTINEL_V2_RESEARCH_CHARTER_V1.md
  CARDIOSENTINEL_V2_EVIDENCE_AUTHORITY_V1.md
  CARDIOSENTINEL_V2_EXPERIMENT_LEDGER.md
```

Then each workstream gets its own protocol/report directory only when it becomes active.

## 39. Definition of “journal-ready”

CardioSentinel V2 is ready for manuscript drafting only when:

- all core workstreams have explicit recorded decisions, including negative ones;
- no primary result exists only as a notebook or terminal output;
- the external-evidence status is unambiguous;
- the fair comparator question is closed;
- patient-memory value is closed;
- the explanation benchmark is frozen and evaluated;
- any hardware claim is backed by actual physical measurements;
- all figures can be regenerated from committed scripts/artifacts;
- the manuscript claim map is derivable from the evidence ledger.

The paper should be the **last summary of the programme**, not the place where the programme decides what it did.

---

# Part XIII — Top-journal evidence bar and publication decision framework

## 40. What “top-journal level” means for CardioSentinel

The programme should be engineered against the questions an expert reviewer will ask, not against an impact-factor target. A submission is considered **top-journal-ready** only when the central claim is supported by evidence that is:

1. **independent** — a primary conclusion is not merely recycled from the cohort used to invent it;
2. **fairly compared** — major components have matched or independently tuned comparators;
3. **subject-level** — uncertainty respects within-subject dependence;
4. **mechanistically interpretable** — the programme can identify why a component helps or fails;
5. **externally challenged** — transfer is tested on a genuinely independent cohort or acquisition condition;
6. **calibrated and operationally meaningful** — not AUROC/AUPRC alone;
7. **physically demonstrated** where an edge/wearable claim is made;
8. **claim-governed** — explanation and manuscript claims can be traced to evidence;
9. **reproducible** — code, protocol, environment, splits, artifacts and failure history are inspectable;
10. **negative-result tolerant** — the system may simplify when evidence says a component is unnecessary.

## 41. Evidence-tier ladder

| Tier | Evidence package | What it supports | Typical publication posture |
|---|---|---|---|
| **T0 — V1 foundation** | completed internal/sealed programme | rigorous historical baseline and hypothesis generation | already achieved; not a new journal claim |
| **T1 — Fair internal extension** | J1 + J2 + J3, prospective TRAIN-only cross-fit | mechanistic/personalization/episode claims within the legacy corpus | strong methods/systems paper, limited generalization |
| **T2 — External validation** | T1 + frozen J5 on independent cohort | bounded cross-cohort transfer and failure diagnosis | minimum ambition for high-quality biomedical AI journal |
| **T3 — Physical-system validation** | T2 + J6 real acquisition/edge measurements | engineering feasibility and causal physical execution | strong biomedical engineering / connected-health positioning |
| **T4 — Governed AI benchmark** | T2/T3 + large J4 benchmark | generalizable claim about evidence-state guarding of generated explanations | trustworthy-AI / digital-health systems contribution |
| **T5 — Live clinical evaluation** | new ethically approved prospective study, workflow/human factors | early clinical utility/safety/human-factors evidence | required before clinical-effectiveness ambitions |

The full “best possible” CardioSentinel programme aims for **T3 + T4** before the flagship journal manuscript. T5 is a later clinical programme, not something this blueprint silently assumes.

## 42. Reporting-standard alignment

For every V2 experiment and manuscript table, maintain a reporting map:

- **TRIPOD+AI** for development/evaluation reporting of prediction models; the 2024 statement contains 27 main items and 52 subitems and supersedes the 2015 TRIPOD checklist for prediction-model studies.
- **DECIDE-AI** only if/when CardioSentinel enters early live clinical evaluation; it addresses early-stage clinical evaluation, safety, human factors and implementation reporting.
- Appropriate study-specific guidelines (for example STROBE/CONSORT-family guidance) if future study design warrants them.

Compliance with a reporting checklist is **not** treated as proof of methodological quality; the protocol must still establish valid design, data authority and inference.

## 43. Reviewer attack matrix

Before any flagship submission, conduct an internal red-team review against these attacks:

| Reviewer attack | Evidence needed to survive it |
|---|---|
| “You tuned the comparator unfairly.” | J1 independent operating-point selection and paired results |
| “Personalization is decorative.” | J2 no-memory ablation, cold-start curve, mechanism endpoints |
| “The gate just stops adaptation.” | J3 admission + contamination + recovery trade-off |
| “The model only works on LTSTDB.” | J5 independent frozen external evaluation |
| “Window metrics exaggerate n.” | subject-level bootstrap/macro reporting |
| “Neural architecture is arbitrary.” | R2 mechanism-first promotion rule; classical/hybrid allowed |
| “The LLM guard is an anecdote.” | frozen multi-context J4 benchmark across model families |
| “The edge claim is laptop theatre.” | J6 real acquisition, latency, RAM, energy, thermal and stability measurements |
| “A good metric is not clinical utility.” | strict non-diagnostic boundary; no utility claim without live clinical study |
| “Negative results disappeared.” | immutable ledger, rejected arms, failure receipts and decision records |
| “The story was written after the answer.” | preregistrations, digests, authorizations, one-shot external receipt |

## 44. Publication decision matrix

Final venue selection is evidence-driven. The following is a **directional strategy**, not a promise of acceptance.

| Evidence state after P4/P5 | Primary journal direction | Why |
|---|---|---|
| strong external biomedical validation, clinically meaningful monitoring contribution, mature governance | **npj Digital Medicine** | scope explicitly includes monitors, sensors, wearables, AI and governance; small preliminary studies are generally not the target |
| strong engineering novelty + real edge/acquisition validation | **IEEE Transactions on Biomedical Engineering** | biomedical engineering merit and physical-system validation become central |
| strong biomedical informatics/AI system with external validation and broad methods contribution | **IEEE Journal of Biomedical and Health Informatics** | natural fit for health informatics + AI system evidence |
| broad conceptual advance spanning evidence governance + physical monitoring + external validation, with exceptionally strong support | **Nature Communications** stretch | editorial evaluation emphasizes novelty, impact, conceptual/methodological advance and strong support for conclusions |
| strongest novelty is executable evidence authority / governed generative AI, with broad benchmark evidence | **Patterns / trustworthy-AI systems direction** | stronger methodological framing than a detector-performance paper |

**Do not target the journal by name first.** At Gate E/Gate F closure, select the venue whose scope matches what the evidence actually established.

## 45. Flagship manuscript go/no-go gate

A flagship top-journal manuscript is **GO** only when all mandatory conditions below are closed:

- [ ] J1 fair stateful-vs-memoryless question closed.
- [ ] J2 patient-memory contribution closed.
- [ ] J3 adaptation integrity closed or explicitly removed from the flagship system.
- [ ] J4 benchmark frozen and evaluated at meaningful scale.
- [ ] J5 independent external evidence completed, or the manuscript is explicitly repositioned away from biomedical generalization.
- [ ] J6 physical measurements completed for any edge/wearable claim.
- [ ] R2 resolved: promoted representation, justified hybrid/classical path, or explicit no-change decision.
- [ ] Primary/secondary endpoint hierarchy and multiplicity policy respected.
- [ ] TRIPOD+AI reporting map complete for applicable prediction-model content.
- [ ] Every main figure/table regenerates from governed artifacts.
- [ ] Claim map passes internal evidence-authority audit.
- [ ] No unresolved contradiction exists between manuscript wording and frozen evidence.

If one mandatory scientific question fails, the correct response may be to **simplify the system and manuscript**, not to manufacture another experiment.

---

# Appendix A — Proposed V2 experiment ledger

| ID | Workstream | Scientific question | Data authority | Status at handbook creation |
|---|---|---|---|---|
| J1 | Fair episode comparator | State machine vs independently tuned memoryless rule | V2 TRAIN cross-fit; external after freeze | PLANNED / NOT AUTHORIZED |
| J2 | Memory contribution | No-memory vs patient memory; cold start | V2 TRAIN cross-fit; external after freeze | PLANNED / NOT AUTHORIZED |
| J3 | Adaptation stress | Static vs always-update vs gated under stress | V2 TRAIN + frozen perturbation registry | PLANNED / NOT AUTHORIZED |
| J4 | Explanation consistency | Can guards suppress evidence-state contradictions? | frozen synthetic/structured EvidenceContexts | PLANNED / NOT AUTHORIZED |
| J5 | External validation | What transfers to independent cohort? | new qualified cohort, one-shot | BLOCKED ON COHORT / NOT AUTHORIZED |
| J6 | Edge execution | Can the control pattern run on real ECG/edge hardware? | physical acquisition/hardware | PLANNED / NOT AUTHORIZED |
| R2 | Representation 2.0 | Why does classical morphology transfer better, and what mechanism fixes it? | V2 TRAIN development only until promotion | CONDITIONAL / NOT AUTHORIZED |

---

# Appendix B — Pre-registration template

Every V2 scientific protocol should answer these fields before execution.

## B1. Identity

- Experiment ID:
- Version:
- Parent RQ:
- Code branch/commit:
- Protocol author:
- Date frozen:

## B2. Question and hypothesis

- Exact research question:
- Null/negative outcome that would be accepted:
- Mechanism hypothesis:
- What result would **not** be sufficient to support the mechanism?

## B3. Data authority

- Allowed subjects/records:
- Forbidden partitions:
- Split digest:
- Label-access rules:
- External contamination audit reference, if applicable:

## B4. Arms

- Arm A:
- Arm B:
- What is held fixed:
- What is allowed to differ:

## B5. Endpoints

- Primary endpoint:
- Primary comparison:
- Resampling/statistical unit:
- Confidence interval method:
- Practical decision threshold:
- Secondary endpoints:
- Descriptive-only analyses:

## B6. Attempts

- Authorized real-data attempts:
- Retry policy:
- Failure classification rules:
- Quarantine location:

## B7. Claim boundary

Complete this sentence before running:

> If the registered primary result is positive, this experiment will permit us to say: ________.

And:

> Even if the result is positive, it will **not** permit us to say: ________.

---

# Appendix C — Authorization and attempt receipt template

## C1. Authorization

- Experiment ID:
- Protocol digest verified: YES / NO
- Data authority verified: YES / NO
- Attempt sequence authorized:
- Human authorizer:
- Timestamp:
- Expected command/entrypoint:
- Expected artifact root:

## C2. Post-attempt receipt

- Attempt sequence:
- Start/end time:
- Exit status:
- Data touched:
- Primary outputs visible: YES / NO
- Classification: COMPLETE / LAUNCH FAILURE / APPARATUS FAILURE / DATA FAILURE / OTHER
- Scientific interpretation permitted: YES / NO
- Quarantined artifacts:
- Replacement attempt permitted automatically: **NO**
- New authorization required: YES

---

# Appendix D — J4 EvidenceContext schema

A benchmark context should have a machine-readable schema approximately like:

```text
context_id
scenario_class
state                 NORMAL | WATCH | EVENT | RECOVERY
opened_at / closed_at
calibrated_probability
longitudinal_evidence
memory_deviation
memory_update_admitted
G1..G6                 PASS | BLOCK | UNAVAILABLE
provenance_status
missing_evidence_fields[]
required_boundary_statements[]
allowed_claim_categories[]
forbidden_claim_categories[]
expected_abstention     true | false
synthetic_adversarial   true | false
```

The generated text is **not** part of the source context. It is the object being evaluated against the context.

---

# Appendix E — Journal-readiness checklist

Before drafting the full journal manuscript, verify all applicable items.

### Scientific comparison

- [ ] W1/memoryless arm had its own operating-point selection.
- [ ] Memory vs no-memory comparison completed.
- [ ] Cold-start behaviour quantified.
- [ ] Adaptation admission rate quantified over full recordings.
- [ ] Adaptation stress/recovery evaluated under a frozen registry.

### External evidence

- [ ] External cohort independence/compatibility audited before scoring.
- [ ] V2 system frozen before external evaluation.
- [ ] No tuning performed in response to confirmatory external result.
- [ ] Subject counts and denominators visible for every macro metric.

### Explanation benchmark

- [ ] Context set frozen before model execution.
- [ ] At least three justified models evaluated or a rationale given for fewer.
- [ ] Pre-guard contradiction rate reported.
- [ ] Guard recall reported.
- [ ] False-refusal rate reported.
- [ ] Post-guard served-output contradiction rate reported.

### Physical system

- [ ] Real acquisition path exists if hardware claims are made.
- [ ] Latency distribution measured.
- [ ] Peak RAM measured.
- [ ] Power/energy measured where feasible.
- [ ] Sustained execution measured.
- [ ] Signal degradation behaviour measured.

### Governance

- [ ] V1 sealed TEST never reopened.
- [ ] Every real-data run has authorization and attempt receipt.
- [ ] Failed attempts preserved/quarantined.
- [ ] Negative results retained.
- [ ] V2 environment reproducibly locked.
- [ ] Figures/tables regenerate from artifacts.

### Claims

- [ ] No diagnosis claim.
- [ ] No medical-device claim.
- [ ] No edge/wearable claim beyond measured device class.
- [ ] No universal neural/Transformer/S4D superiority claim.
- [ ] No generalization claim beyond evaluated external cohorts.
- [ ] No “early detection” claim from overlap-only negative latency.

---

# Appendix F — Proposed V2 claim language

Preferred phrases:

- “evidence-governed adaptive monitoring”
- “patient-relative memory”
- “contamination-aware update admission”
- “stateful episode reasoning”
- “structured evidence-state consistency”
- “guarded generative explanation”
- “engineering feasibility on the evaluated edge platform”
- “external transfer on the evaluated cohort”
- “the predefined rule selected…” rather than “architecture X is superior”

Avoid unless directly supported by new evidence:

- “diagnoses ischemia”
- “clinically safe”
- “deployable medical device”
- “generalizes to wearable ECG”
- “smartwatch ready”
- “neural model outperforms classical methods”
- “S4D is superior to GRU”
- “AI explanation is trustworthy” without the guard/error-rate qualifier

---

# Appendix G — Recommended repository layout

This handbook does not create these paths; it proposes them.

```text
docs/
  journal-extension/
    README.md
    CARDIOSENTINEL_V2_RESEARCH_CHARTER_V1.md
    CARDIOSENTINEL_V2_EVIDENCE_AUTHORITY_V1.md
    CARDIOSENTINEL_V2_EXPERIMENT_LEDGER.md

    j1-fair-episode-comparator/
    j2-memory-ablation/
    j3-adaptation-stress/
    j4-explanation-consistency/
    j5-external-validation/
    j6-edge-platform/
    r2-representation/
```

V1 `docs/handbook/`, frozen `_V1` reports, attempt receipts and consumed-test artifacts remain where they are. Do not reorganize historical provenance merely to make V2 look cleaner.

---

# Appendix H — Reviewer attack checklist

Use this checklist twice: once before external evaluation is opened, and once before manuscript submission.

### H1. Study design
- [ ] Was each primary question stated before scientific execution?
- [ ] Are comparator tuning opportunities symmetric?
- [ ] Are TRAIN/VALIDATION/TEST/external roles unambiguous?
- [ ] Is subject overlap impossible or explicitly audited?
- [ ] Are all adaptive decisions frozen before confirmatory evaluation?

### H2. Statistics
- [ ] Is subject the inferential/resampling unit for generalization claims?
- [ ] Are pooled and macro results both visible?
- [ ] Are confidence intervals reported for primary contrasts?
- [ ] Is multiplicity controlled or hierarchically declared?
- [ ] Are denominators visible when subjects/episodes are unevaluable?

### H3. Clinical/physiological interpretation
- [ ] Are ischemic vs non-ischemic ST-change semantics explicit?
- [ ] Are confounders and signal-quality failures analysed rather than hidden?
- [ ] Are episode-level metrics reported where the claim is episode-level?
- [ ] Are calibration and false-alarm burden visible?
- [ ] Are diagnosis/utility/device claims absent unless separately supported?

### H4. AI/LLM claims
- [ ] Is generated language evaluated against structured ground truth rather than style preference?
- [ ] Are false refusals reported alongside caught contradictions?
- [ ] Is deterministic fallback included as a real comparator?
- [ ] Are model-family conclusions avoided unless the benchmark supports them?

### H5. Physical system
- [ ] Does the claimed device class match the hardware actually tested?
- [ ] Are latency distributions, power/energy and sustained operation measured?
- [ ] Is acquisition geometry compatible with ST-morphology assumptions?
- [ ] Are signal interruptions and degraded-quality behaviour exercised?

### H6. Reproducibility and integrity
- [ ] Can every headline number be traced to a protocol, run and artifact?
- [ ] Can failed attempts be inspected?
- [ ] Can figures/tables be regenerated?
- [ ] Is the current environment/version frozen?
- [ ] Is V1 still reproducible independently of V2?

---

# Appendix I — Living-blueprint change control

This blueprint is **living at the planning layer** and must remain stable at the evidence layer.

### I1. Version rules
- Minor version (`2.1 -> 2.2`): planning clarification, venue strategy, dependency changes, new risk, or non-scientific sequencing change.
- Major version (`2.x -> 3.0`): change to the programme thesis, core RQs, evidence authority, or experimental governance model.
- Frozen experiment protocols/reports are **never edited to follow the blueprint**; they remain historical records.

### I2. Required change log entry
Every blueprint revision should state:
- date;
- repository commit used as basis;
- sections changed;
- reason;
- whether any already-authorized experiment is affected;
- explicit statement that no frozen result was rewritten.

### I3. Status dashboard
Maintain one compact live table in `docs/journal-extension/README.md` rather than stuffing results into this handbook:

```text
Workstream | Protocol | Authorized | Attempt | Decision | External status | Claim status
J1         | ...      | ...        | ...     | ...      | ...             | ...
...
```

---

# Appendix J — External reporting standards and venue references

These references guide **reporting and publication strategy**; they do not authorize experiments. Verify venue instructions again at submission time because journal policies can change.

1. Collins GS, Moons KGM, Dhiman P, et al. **TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods.** *BMJ*. 2024;385:e078378. doi:10.1136/bmj-2023-078378.
2. Vasey B, Nagendran M, Campbell B, et al. **Reporting guideline for the early-stage clinical evaluation of decision support systems driven by artificial intelligence: DECIDE-AI.** *Nature Medicine*. 2022;28:924–933. doi:10.1038/s41591-022-01772-9.
3. **npj Digital Medicine — Aims and scope.** Current scope includes clinical applications of monitors, sensors, wearables, validated AI/ML and digital-medicine governance; the journal notes that small-scale preliminary studies are typically outside scope. Accessed 2026-08-31.
4. **Nature Communications — Editorial process / reviewer criteria.** Current editorial criteria emphasize novelty, potential impact, conceptual or methodological advance, quality of data, appropriate controls and strength of evidence for conclusions. Accessed 2026-08-31.
5. **PhysioNet — European ST-T Database v1.0.0.** 90 annotated ambulatory ECG excerpts from 79 subjects, designed for evaluation of ST/T-change analysis methods. This is a candidate external cohort subject to the V2 qualification and contamination protocol; mention here does not authorize access or scoring.

---

# Closing principle

CardioSentinel V2 should not be judged by whether every planned experiment “wins.” Its standard should be whether each question was asked fairly, each access was governed, each negative result remained visible, and each operational claim could be traced back to evidence with a boundary that survived contact with the result.

> **Learn selectively. Reason persistently. Explain conditionally. Validate independently. Execute physically.**

That is the journal-extension programme — and this blueprint is the control plane we use to keep it scientifically honest, strategically ambitious and on track.
