# CardioSentinel: Evidence-Governed Intelligent Physical Monitoring with Bounded Adaptation and Agentic Reasoning

*Working title — provisional.*

[ABSTRACT — WRITE AFTER BODY FREEZE]

---

## 1. Introduction

Continuous physiological monitoring is not a classification problem with a
sensor attached to it. A monitor sits inside a physical loop: a signal arrives
from a body under conditions nobody controls, a computation must run causally
because the future has not happened yet, state accumulates about a particular
patient over hours, a decision is committed at a moment that cannot be revisited,
and something is then said to a person who will act on it. Each of those stages
imposes a constraint that a window-level classifier evaluated on a fixed split
never encounters.

The constraints compound once the system is allowed to change. A monitor that
adapts to a patient can adapt to the wrong thing. A monitor that accumulates
state can accumulate it from windows it should not have learned from. A monitor
that reasons over time commits to an episode boundary before it can know whether
the episode continues. And a monitor that explains itself in generated language
can produce a fluent, well-grounded sentence that inverts the one fact a
clinician most needs to be true.

Those capabilities raise two governance questions that are usually asked
separately, if at all:

1. **What evidence was the system legally allowed to produce?** Which partition
   could it read, how many times could it read it, which artifacts survive, and
   what happens to the results that did not work.
2. **What may the deployed system state from that evidence?** Which sentences
   are licensed by the artifacts that exist, and what happens to a sentence that
   is not.

The first question is asked by the reproducibility literature and answered with
checklists, provenance chains and, more recently, with call-time enforcement.
The second is asked by the grounded-generation literature and answered with
guardrails, attribution metrics and renderer-side claim verification. They are
answered by different communities, with different tooling, about different
objects.

**CardioSentinel couples them.** The same provenance and authority model that
constrains partition access, attempt consumption and retained scientific
evidence also constrains what the operational and agentic surfaces may assert.
An overclaim in a generated explanation and an overclaim in this manuscript fail
against the same code. That coupling is the contribution, and §2 is explicit
that neither half is new on its own.

The worked setting is transient ST-segment ischemia in long-term ambulatory ECG,
using the Long-Term ST Database. **The clinical task is the substrate, not the
claim.** This paper reports no diagnostic capability, no deployment, and no
external corroboration; its headline predictive numbers are weak and are
reported as such. What the setting provides is a domain in which every one of
the constraints above is real: the signal is physical, the reasoning is
temporal, the adaptation is patient-specific, and the output is something a
person might act on.

### 1.1 Contributions

**C1 — An implemented intelligent physical system.** A causal physical–digital
monitoring pipeline running as a streaming runtime, integrating window
representation learning, physiology fusion, patient-relative memory, a
contamination-safe update gate, calibration, a longitudinal temporal arm, an
episode state machine, an evidence graph and a governed agentic surface. Every
component carries an individual, documented retention decision (Table T1), and
two of those decisions were to reject.

**C2 — An experimentally evaluated temporal and episode-reasoning result.**
Episode reasoning improves episode-level agreement relative to a memoryless
window rule, on identical rows, at the promoted operating point: subject-macro
`episode_f1` difference **0.1921**, 95% paired subject-bootstrap
**[0.0505, 0.3455]** over 12 held-out subjects. The temporal-arm selection that precedes it is reported as selection
under a preregistered rule, not as superiority: its paired interval
**[−0.015229, 0.148951]** includes zero.

**C3 — An executable evidence authority.** Partition access, experiment attempt
consumption, artifact provenance, retention decisions and negative-result
handling are enforced by code rather than by convention. All fifteen one-shot
budgets in the programme are spent, the sealed test was consumed once, and the
framework's own most instructive failure — an evaluator bound to an architecture
the selection protocol had rejected, caught by a person reading the entry point
rather than by any guard — is reported rather than omitted.

**C4 — Two-surface evidence coupling.** The same governed evidence model
constrains runtime explanations. In the single evaluated context, a generation
scoring evidence fidelity **1.000** with **0** claim violations and completeness
**1.000** was refused at runtime for asserting a categorical gate state the
evidence contradicted, and the runtime served a deterministic fallback. The
inversion reproduced on two independent runs.

**Not claimed as contributions:** representation improvement, which the E11,
E12d and E13a results closed on this corpus; foundation-model distillation
(RQ6), never begun; and confounder-aware supervision (RQ7), never begun. **No
claim is made that every implemented component improved predictive accuracy**,
and several did not.

---
## 2. Related work

Four literatures neighbour this work, and a fifth became a neighbour only when
the system acquired a generated-language surface. A sixth places the paper in
its theme. This section positions the contribution against each. **In no case is
the claim that we detect ischemia better**, and §2.1 says so first because it is
the comparison a reader of an ECG paper will reach for.

### 2.1 ST-episode detection in ambulatory ECG

The immediate technical neighbours are small in number and unusually coherent.
Transient ischemic ST episodes in long ambulatory recordings have been studied
against two annotated resources: the European ST-T Database [pmid:1396824], and
the Long-Term ST Database [pmid:12691437], which is this system's training
cohort and which was built expressly as a reference for developing and
evaluating automated ischemia detectors. Both are distributed through PhysioNet
[doi:10.1161/01.cir.101.23.e215].

The detector lineage runs from early episode-detection systems
[doi:10.1109/cic.1995.482762] and the characterisation of episode temporal
patterns [doi:10.1109/cic.1996.542628], through reference-level tracking
[doi:10.1109/cic.2002.1166774] and its journal treatment [pmid:15191074], to
record-level classification of ischemic heart disease type
[doi:10.1186/1475-925x-10-107]. A second thread addresses the discrimination
this task actually turns on — separating ischemic ST change from heart-rate
related ST change [doi:10.1109/cic.2008.4749058, pmid:20130344], including via
ST/HR diagrams [pmid:22874369]. Adjacent work covers real-time detection
[pmid:19696464], morphology delineation [pmid:26863140], and the annotation
tooling the reference databases themselves required [pmid:15265622].

**Positioning.** We are not claiming a better detector, and our headline figure
is modest. The comparison we invite is on **what is reported and how it can be
checked**, not on the metric value: every number in §7 is traceable to the
access that produced it, and the boundaries around it are machine-enforced
rather than described. We also note, because §9.1 depends on it, that this
literature's small size is not an artifact of our reading — a search across
Crossref and PubMed returned essentially one ambulatory ST-episode resource
beyond our own training cohort, which is independent corroboration of the
negative finding in our external-validation audit.

### 2.2 Deep learning for ambulatory ECG

Deep learning on ECG is a large and fast-moving literature, surveyed
systematically in [arxiv:2001.01550] and reviewed, for the personalised
setting, in [arxiv:2409.07975]. **Its centre of mass is not our task.** The
dominant setting is 12-lead resting or short-strip diagnosis — recent examples
include occlusion myocardial infarction identification [pmid:42129209],
large-scale acute coronary syndrome corpora [pmid:42082497], and transfer
learning from ECG imagery [pmid:41358268] — rather than continuous multi-hour
ambulatory streams with episode-level endpoints. Work directly on ambulatory
signal quality and noise [arxiv:2201.10061] is closer to our operating
conditions than most of the diagnostic literature is.

Self-supervised and contrastive representation learning for ECG is well
populated: lead-agnostic local and global representations [arxiv:2203.06889],
physiologically-inspired augmentations for 12-lead records [arxiv:2106.04452],
subject-aware contrastive learning for biosignals [arxiv:2007.04871], and
masked transformer pretraining [arxiv:2309.07136]. Our encoder's architectural
lineage is the structured state-space family — [arxiv:2111.00396], its diagonal
simplification [arxiv:2203.14343], and the parameterisation and initialisation
that make diagonal variants work [arxiv:2206.11893].

**Positioning.** Every architectural choice reported here was made by a rule
frozen before the deciding evidence existed, and the record of that freezing is
an artifact rather than a claim in a methods section. The consequence is
reported rather than smoothed: our one architectural contrast is stated with a
paired subject-bootstrap interval that **includes zero**, and it stays that way
in §7. **The contribution is not the encoder.** Any architecture in the
paragraph above could be substituted without touching the evidence framework,
and the framework is what §4 is about.

### 2.3 Reproducibility, pre-registration, and result-blind analysis

Three traditions live here and the paper's positioning depends on keeping them
apart.

**Documentation.** Model cards [arxiv:1810.03993] and datasheets
[arxiv:1803.09010] standardise what is disclosed about a model and a dataset.
In the clinical prediction setting, TRIPOD+AI [doi:10.1136/bmj.q824] does the
same for reporting. These are authored artifacts describing a process that has
already happened, and their value does not depend on the description being
verifiable.

**Empirical study of whether documentation works.** The NeurIPS reproducibility
programme report [arxiv:2003.12206] describes what was deployed and what its
organisers learned; the first large analysis of the NLP Reproducibility
Checklist [arxiv:2306.09562] measures what changed, finding across 10,405
responses an increase in reported information and that only 46% of submissions
claim to open-source their code. Leakage has been shown to be widespread and
consequential across 17 fields [doi:10.1016/j.patter.2023.100804,
arxiv:2207.07048], with concrete instances in applied domains
[arxiv:1909.06539] and sustained attention in the scientific press
[doi:10.1038/d41586-022-02035-w]. Reproducibility in ML for health specifically
was found, in a review of over 100 ML4H papers, to compare poorly with more
established machine-learning fields on data and code accessibility
[arxiv:1907.01463], and domain-specific assessment frameworks have followed
[arxiv:2401.08847]. Pre-registration itself has been adapted to predictive
modelling as a lightweight template with a qualitative evaluation
[arxiv:2311.18807], and registered reports are an established response to
publication bias in other fields [doi:10.1038/s41593-024-01762-9].

**Result-blind analysis** is mature outside machine learning. Nuclear and
particle physics has practised deliberate blinding of the analyst to the result
for decades [doi:10.1146/annurev.nucl.55.090704.151521,
doi:10.1088/0954-3899/28/10/312, doi:10.2172/826602], and the argument there is
the one this paper makes: the discipline must be structural, because the
individual analyst's care is not the failure mode.

**Positioning.** A checklist records intent at submission time; the
`arxiv:2306.09562` analysis is evidence of how far that gets you. This work
enforces the same properties **at execution time, from code, and produces
artifacts that testify to what did not happen** — a checklist cannot
demonstrate that no model was loaded, and a zero-capability counter written by
the run can. **That positioning is real but it is no longer sufficient on its
own**, because §2.6's neighbours enforce at execution time too.

### 2.4 Selective prediction, calibration, and deferral

The reject option is old and the theory is settled: the error–reject tradeoff
was characterised in [doi:10.1109/tit.1970.1054406], and the modern selective
classification line — pointwise-competitive selective classification
[doi:10.1613/jair.4439], selective classification for deep networks
[arxiv:1705.08500], and an integrated reject option trained end to end
[arxiv:1901.09192] — extends it to the setting we work in. Recent work sharpens
the objective [arxiv:2206.09034], couples it to calibration [arxiv:2208.12084],
derives it from training dynamics [arxiv:2205.13532], and examines its
behaviour under distribution shift [arxiv:2405.05160]. Calibration itself has
an equally clear line [arxiv:1706.04599, arxiv:2106.07998], and
learning-to-defer treats the human as a second decision-maker rather than a
fallback [arxiv:2006.01862, arxiv:2202.03673, arxiv:2310.14774].

**Positioning, and it is a negative result.** We implemented selective routing,
evaluated it against a prespecified exit gate fixed before the evaluation, and
**rejected it**. The paper reports the rejection as a result, with the gate
that produced it.

**One observation about this literature, stated with its bound.** Across the 77
records this subsection's queries returned, the abstracts describe methods that
improve a risk–coverage curve or a deferral rule; **none reports a selective
mechanism that was built, evaluated against a prespecified gate, and
abandoned.** That is a statement about what a recorded search returned, not a
claim about the field, and §9.3 develops the publication-incentive argument on
exactly that footing and no further.

### 2.5 Grounded generation, provenance-constrained NLG, and guardrails

This literature became a neighbour when the system acquired a
generated-language surface (§4.6), and it has three parts.

**Grounding output in retrieved evidence.** Retrieval-augmented generation
[arxiv:2005.11401] established the arrangement — a parametric generator over a
non-parametric retrieved memory — and subsequent work makes retrieval active
[arxiv:2305.06983] or corrective [arxiv:2401.15884].

**Measuring whether output is actually supported.** Faithfulness and factuality
in abstractive summarisation [arxiv:2005.00661] and the Attributable to
Identified Sources framework [arxiv:2112.12870] give the vocabulary; the
hallucination survey [arxiv:2202.03629] gives the taxonomy. Evaluation has
since moved to maintained leaderboards with private splits [arxiv:2501.03200]
and to runtime monitoring of faithfulness during generation [arxiv:2406.13692].

**Guardrails.** Programmable output rails, independent of the underlying model
and interpretable by the developer, are the industrial pattern
[arxiv:2310.10501]. Their limits are documented: a comparative evaluation
across industrial guardrails finds a recurring security/usability tradeoff
[arxiv:2504.00441], and guardrail robustness degrades under RAG-style contexts
[arxiv:2510.05310]. In clinical deployment the pattern appears both as a safety
classifier [pmid:41933065] and as an error-prevention layer over generated
instructions [pmid:38664535].

**Positioning.** The usual arrangement grounds a model in retrieved
**documents**. This system grounds it in a **closed evidence graph with closed
vocabularies**, gives it four sealed context sections and no free-text channel,
and places a lexical claim guard, a numeric claim guard and a categorical
alignment check between generator and user, with a deterministic renderer
behind them as the fallback. The distinguishing property is not that the model
is constrained — [arxiv:2310.10501] constrains a model. **It is that the
constraint is the same publication claim boundary the manuscript is bound by,
so an overclaim in generated prose and an overclaim in this paper fail against
one artifact.** We take [arxiv:2504.00441]'s finding as the honest frame for
what that costs: our fallback rate is the usability side of exactly that
tradeoff, and §7.6 reports it rather than defending it.

### 2.6 Where this work sits

**The problem this paper addresses has been independently named, and we do not
claim to have noticed it first.** [arxiv:2605.08586] calls it *experiment
nonrepudiation*: binding the numbers in a paper to an actually executed
computation in a way the author cannot later alter or deny. It argues — with
the threat model spelled out — that self-reported checklists, optional code
sharing and author-controlled logging do not answer the question a reviewer
cannot check, and it ships a reference implementation to show the problem is
solvable. Nearby, sample-level pipeline traceability anchored to tamper-evident
cryptographic commitments [arxiv:2601.14971] and machine-verifiable provenance
for model lineage and environment [doi:10.3389/fcomp.2026.1735919] attack the
same class of problem from the supply-chain side. Two further lines bear
directly on what this system enforces, and the first of them is closer than any
of the above. **A typed workflow grammar enforces a terminal assess-once
constraint at call time** [arxiv:2603.10742]: the test partition is locked
until `assess` is called, `assess` is valid only while the model's `assessed`
flag is false, a second call raises, and the result is described by its author
as terminal evidence the grammar does not allow to be revisited. That is
partition authority, a runtime gate and consumed-attempt semantics in one
mechanism. Separately, the question of how often a held-out set may be
consulted has an established statistical treatment: the Ladder
[arxiv:1502.04585] and the reusable holdout [arxiv:1506.02629] make *repeated*
consultation safe rather than forbidding it — the Ladder explicitly places no
limit on the number of submissions. The re-executable-publication tradition is
older than all of it [doi:10.1016/j.procs.2011.04.061,
doi:10.1016/j.procs.2012.04.047] and now has platforms [doi:10.3233/apc200107,
doi:10.1186/s13059-021-02299-x], and code review has been proposed as the human
complement [doi:10.1038/s41562-021-01190-w].

**Each of these binds a different object, and none of them binds two.** A
signed attestation establishes that a number came from a run
[arxiv:2605.08586]. A provenance chain establishes which data and which
environment produced it [arxiv:2601.14971, doi:10.3389/fcomp.2026.1735919]. A
workflow grammar establishes that the analysis path was legal
[arxiv:2603.10742]. An adaptive-holdout bound establishes how often a test set
may be consulted [arxiv:1502.04585, arxiv:1506.02629]. On the other side,
claim-level enforcement is not new either: Proof-Carrying Numbers
[arxiv:2509.06902] emits numeric spans as claim-bound tokens, verifies them in
the renderer rather than the model and defaults to unverified when the check
fails, and runtime governance systems mediate what an agent may *do* under a
policy that fails closed [arxiv:2608.16891].

**To the best of our targeted review, we found no prior system in which one
authority spans both halves.** The artifact that governs partition use, attempt
consumption and retained evidence in this system is the artifact that
constrains what its runtime surface — and this manuscript — may state, so an
overclaim in generated prose and an overclaim in §7 fail against the same code.
That coupling is the claim. It is not a claim about either half separately, and
it does not rest on the priority that either 2026 preprint above asserts for
itself: if `arxiv:2603.10742` is not the first call-time evaluation gate, or
`arxiv:2509.06902` not the first renderer-side claim verifier, the coupling is
exactly as unattested as it is now.

Three properties follow, and they are the section's exit:

1. **The claim, not the computation, is the enforced object.** The guards in
   §4.6 operate on generated prose and on the manuscript's own text. The
   principle is shared with [arxiv:2509.06902]; what differs is scope — lexical
   and categorical guards over a closed evidence graph, not numeric spans
   alone.
2. **One artifact governs two surfaces.** The claim boundary that binds this
   paper is the code that binds the runtime's explanation. The neighbouring
   systems have one surface, so the question does not arise for them.
3. **The apparatus produces evidence of absence.** Attestation records what
   happened; a zero-capability counter written by a run records what did not,
   and §5 turns on artifacts of that kind. Runtime governance systems report
   governed-zero counts in the same spirit [arxiv:2608.16891]; here the counters
   are retained as experimental evidence rather than as operational telemetry.

**These are complements, not competitors.** [arxiv:2605.08586] proposes a
protocol for conferences and calls for a standard; this is one project's
machinery, applied at authoring time, reported in §9.6 with the cost it
imposed. Our one-shot budgets sit between the two traditions above.
[arxiv:1502.04585] and [arxiv:1506.02629] make repeated holdout use
statistically safe; [arxiv:2603.10742] makes a second assessment raise inside
one process. **This system's budgets are neither statistical nor
process-scoped**: an attempt is consumed across the whole research programme,
its consumption is an artifact that outlives the process that wrote it, and a
further attempt requires a human authorisation recorded before the access. That
is a difference in scope and durability, not in principle, and §9.6 reports
what it cost. A field that adopted both would have numbers bound to runs and
claims bound to evidence. **It currently has neither as a default, and this
paper is an existence proof for the second half at the scale of a single
research programme.**

### 2.7 Intelligent physical systems

This system is not only an ECG classifier, and the theme it belongs to has its
own literature. Continuous physiological monitoring is now a physical-digital
loop rather than an offline analysis: textile ECG sensors streaming to a 5G
edge device for continuous end-to-end classification are already demonstrated
[arxiv:2107.13767], and the wearable-physiology modelling landscape has been
surveyed for photoplethysmography [arxiv:2401.12783]. Language models have been
applied directly over wearable sensor streams for health inference
[arxiv:2401.06866], and agentic systems now perform both reactive question
answering and proactive monitoring over ECG and PPG signals [arxiv:2605.29483].
The trust question this raises for cyber-physical decision making has been
reviewed in its own right [arxiv:2405.06347].

**Positioning.** The distinction that matters is not ECG-classifier versus
something else; it is that the object under study is a chain rather than a
mapping. A classifier is *signal → label*. This system is *physical
physiological signal → causal streaming computation → adaptive temporal state →
bounded decision state → machine-generated evidence → governed agentic
interaction*, and every stage after the first is load-bearing somewhere else in
the paper. The signal arrives under real ambulatory conditions, so the
operating envelope is set by the sensor and the patient rather than by a
dataset split (§3). The computation is causal and streaming, and its behaviour
is measured rather than claimed (§7.6). Temporal state is carried across hours
rather than recomputed per strip — the property [arxiv:2605.29483] names as
longitudinal physiological memory and identifies as missing from task-specific
pipelines. The decision state is bounded by a prespecified exit gate, which is
why §2.4's routing result is reported as a rejection rather than omitted. The
evidence is machine-generated and retained, including the evidence of absence
§5 turns on. And the agentic surface is governed by the claim boundary of §4.6.

**What the literature above does and does not supply.** It establishes that
each stage of that chain is an active research setting: edge-streamed ECG
[arxiv:2107.13767], wearable-physiology modelling [arxiv:2401.12783], language
models over sensor streams [arxiv:2401.06866], agentic monitoring with
persistent temporal context [arxiv:2605.29483], and the trust problem this
raises for cyber-physical decision making [arxiv:2405.06347]. **None of these
systems implements the governance mechanism this paper contributes, and none is
cited here as though it did** — they build capability into the loop, and the
contribution here is the enforcement that constrains what the loop may assert.

---

## 3. CardioSentinel as an intelligent physical system

This section describes what runs. It separates **model components**, which carry
learned parameters and whose scientific benefit is adjudicated in §5–§7, from
**governance components**, which carry no parameters and whose job is to
constrain what the model components may do and what may be said about them.
Figure **F1** shows the four layers and the evidence that constrains each.

The path a sample takes is:

```
LTSTDB waveform
  -> causal windows                      (Layer 1, signal)
  -> B4-B representation                 (model)
  -> physiology features, P1-B fusion    (model)
  -> patient-relative memory M1L         (model, patient state)
  -> M2-G contamination-safe update gate (GOVERNANCE)
  -> U1 calibration                      (model)
  -> causal S4D temporal score s_t       (model)
  -> T1 episode state machine            (GOVERNANCE-CONSTRAINED, no parameters)
  -> alert
  -> evidence graph                      (GOVERNANCE)
  -> guarded explanation / agentic surface (GOVERNANCE + generator)
```

### 3.1 Physical signal and causal streaming path

The corpus is the Long-Term ST Database [pmid:12691437], 24-hour ambulatory
records annotated for transient ischaemic and non-ischaemic ST change, split
subject-disjoint into 56 TRAIN / 12 VALIDATION / sealed TEST subjects. Layer 1 is
a `StreamingPreprocessor` feeding a `CausalWindowGenerator`; each window yields a
146-dimension representation. **The path is causal by construction**: no
transform reads a sample later than the window it is producing, because in
deployment those samples do not exist.

Two refusals in the runtime bound what may be replayed. Only the twelve
validation subjects are replayable, because the episode thresholds are
leave-one-subject-out and no other record has a validated operating point — the
runtime refuses rather than borrowing the nearest. And a stream must use the raw
identity processing profile, because the frozen corpus is `processing_profile:
raw` and a band-pass would shift every embedding silently; `require_raw_profile`
makes that fail loudly rather than quietly.

### 3.2 Predictive representation

**B4-B** is a CNN + Transformer encoder over the raw waveform, **309,809
parameters**, input `[B,1,2500]`, selected over the B4-A and B4-C candidates
under a rule frozen before the deciding evidence existed. **P1-B** fuses a
frozen 18-dimension `morphology_v1` physiology vector with the encoder output
and was retained on development evidence. **The two P1-B quantities have
different denominators and the frozen decision reports them that way**: pooled
AUPRC **+0.03802798** over **473,897 validation windows across 12 subjects**,
and subject-macro AUPRC **+0.01550711** over **9 contributing subjects**.
`P1_PHYSIOLOGY_RETENTION_DECISION_V1.md` states the 9-subject denominator and
**does not state why three subjects do not contribute**; we report the
denominator it gives rather than supplying a reason it does not. The retention
also carries a recorded caveat: rate-related challenge FPR degraded by
**+0.00603**, kept explicit rather than netted against the gains. §5 reports the
sealed evaluation of the B4-B encoder/head path and the four investigations that
closed the representation-improvement branch.

### 3.3 Physiology and patient-relative memory

**M1L** maintains long-timescale patient-relative context across a stream. §5.4
reports what it demonstrably carries — incremental patient-relative information
— and states plainly that its predictive contribution is unresolved.

### 3.4 Temporal reasoning and episode state

**T2** is a causal S4D longitudinal arm emitting a continuous temporal evidence
value `s_t`. **T1** is a four-state episode state machine with **no trainable
parameters**, reading exactly nine permitted row inputs. Its transitions are a
frozen protocol rather than a learned policy, which is why §4.1 can make a
structural leakage claim about it that no training-time argument could support.

### 3.5 Evidence graph and agentic interaction

Each alert is materialised as a graph of **35 nodes and 39 edges** with closed
node kinds and edge relations. Four agents — Evidence, Explanation, Research and
Architecture — read that graph and nothing else. There is no autonomous agent
and no free-text channel into the generator. §4.6 and §8 describe the boundary
this places on what any of them may say.

### 3.6 Runtime and the physical–digital loop

`src/cardiosentinel/edge/` (1,692 lines) hosts a `StreamingInferenceSession`
carrying five pieces of causal state. **The composition of the research path and
the runtime path was proven rather than asserted.** For the whole research phase
no module imported both halves: the signal path ended at `CausalWindow` and the
model chain began at a precomputed corpus. `edge/representation.py` joins them,
and the join was audited: the physiology half is **bit-exact** (`0.000e+00` on
**64 of 64** audited rows) and the embedding half agrees to a maximum of
`7.15e-07`, **6 ULP** of float32, median 2.5 ULP. **The asymmetry is the
evidence.** The physiology half passes through no reduction, so its exactness
shows the inputs are identical and the residual on the embedding half is kernel
jitter rather than a data-path divergence.

Where a decision rule exists in both the research and runtime paths, there is
**one implementation**. The M2 causal order was *extracted* from
`m2_policy.replay_stream` into `m2_policy.step` rather than reimplemented, with
byte-identical evidence over 300 real corpus rows and 555 M2 tests. A runtime
that reimplements a research path is a second system, and its agreement with the
first is a coincidence rather than a guarantee.

**Patient identity selects a namespace, never a feature.** `subject_id` chooses a
state namespace and a calibrator; it is never a model input, and
`t1_protocol.next_state` never reads `row.stable_id` even though the identifier
is present in the row (§4.1).

**Table T1** lists every component with its role, its retention decision, its
evidence artifact and its decision document. Two rows say **no**.

---

## 4. Evidence framework


A monitoring system that learns from patients is easy to evaluate badly. The
usual failure is not a wrong number; it is a number whose provenance nobody can
reconstruct, produced by a pipeline that could have seen what it should not
have, reported after the fact by an author who already knew what the result was.

We built CardioSentinel so that each of those failures is prevented by
something that runs, rather than by something a reader is asked to trust. This
section describes that machinery. It is the paper's contribution, and it is
placed before the results it governs because every negative result in §5–§7 was
produced under it rather than explained by it afterwards. Figure **F2** shows
partition authority and the one-way spend of evidence; **Table T3** lists the
component gates, including the two that returned no.

**What this section must resist, stated first because it is the risk.** §4 is
the most flattering material in the paper and it is about machinery, not
results. **Every claim here is a claim about process. None of it licenses a
number in §5–§9.**

### 4.1 Leakage controls as executable constraints

The episode state machine may read exactly **nine** row inputs. The list is a
frozen tuple, `T1_ALLOWED_ROW_INPUTS` in `neural/t1_protocol.py`, and a
companion tuple `T1_FORBIDDEN_TRANSITION_INPUTS` names **fifteen** inputs a
transition may never touch. A name outside the allow list raises before any
value is read.

The interesting half is not the deny list. It is that **`stable_id` is *in* the
allow list, and the transition never reads it.**

Both halves have to be stated together or the design is misread. `stable_id` is
admitted because the row must be identifiable — evidence has to be traceable to
a window, and an artifact that cannot name its rows cannot be audited. It is
never consulted in a transition because identity must not influence a decision.
A deny list alone would have forced identity out of the record entirely and
made the provenance claim unverifiable; an allow list alone would have said
nothing about use. **The constraint is that the identifier is present and
unused, and only code can carry that distinction** — no prose convention
survives a refactor.

### 4.2 One-shot access semantics

Several evaluations in this programme could be performed exactly once. A
held-out partition scored twice is no longer held out, and no amount of
reporting discipline repairs it afterwards.

We treat such an access as a **budget**. **All fifteen budgets in this programme
are spent.** The fifteenth — the neural sealed test — was consumed on
2026-08-25.

A spent budget leaves an `*_AUTHORIZED` flag sitting `True` on disk, and the
temptation is to read that flag as a live permission. It is not: **it is a
receipt for an access already taken.** The persistence claim is therefore not
carried by the flag but by the **re-run guard** — the code path that refuses a
second execution against a consumed record, and that would refuse it even if
every flag were flipped by hand.

**How the fifteenth budget was consumed is this section's best material, and it
is not a success story.** The authorization was signed against a *named
architecture*. The evaluator that ran was bound to an architecture the selection
protocol had **rejected**. The mismatch was caught by **reading the entry
point** — not by a test, not by a guard, and not by the authorization document,
which was correct and which the evaluator did not contradict in any way a
machine could see. Handbook §43.2 records it.

We report this because the honest reading of our own framework is that it is
**partial**. It catches what it was built to catch. The thing it did not catch
was found by a person reading code before pressing the button, and a framework
that cannot admit that is advertising rather than describing.

### 4.3 Pre-registration at execution time

Pre-registration in this programme is enforced by **ordering in version
control**, not by intention.

The plan is merged first, as its own change. The generator runs second. The
report is opened third, as a separate change. Because each step is a commit, the
sequence is checkable after the fact by anyone with the repository: a report
whose plan postdates it is visible, and no assertion by an author is required.

This is weaker than a public registry and stronger than a claim of good faith.
It cannot stop a plan from being written to fit a result the author already
suspects. It does stop a plan from being *edited* once the result is in — which
is the failure we could actually prevent.

Two amendments in this programme postdate the reads they concern. Both say so in
their own first paragraph.

### 4.4 Negative capability

Most testing establishes what a system does. Some of the claims a monitoring
programme needs are about what a run **did not do**: it did not open the sealed
partition, did not read a label, did not train a model.

Promoted artifacts therefore carry **zero-capability counters** — recorded
counts of operations the run was structurally incapable of performing, asserted
to be zero at promotion time. The measurement that produced our primary episode
result consumed a persisted trace and **ran no model**, and four such counters
attest to it, with the sealed test still unopened at the time it ran.

**Proving absence is a different and stronger claim than testing presence**, and
it is the one an evaluation of a learning system on patient data most needs.
The pattern generalises past this system: the strongest form of the guarantee is
that the capability does not exist on the path, so the counter is zero because
nothing could have incremented it.

### 4.5 Digest-bound provenance

Every promoted artifact is bound by SHA-256 to the run that produced it, the
environment lock it ran under, the generator that wrote it, and the immutable
run directory it lives in. Split assignments carry their own digest — the
prospective three-fold split used in §5 is
`ce037309cc…206c3` — and a run refuses to start if the digest it recomputes
does not match the one it was authorized against.

The value is compositional rather than cryptographic. Any single digest proves
little; the chain proves that a reported number, the artifact behind it, the
code that produced it and the environment it ran in are the same objects a
reader can fetch. When one link was broken in this programme, the break was
visible as a mismatch rather than as a wrong result.

---

## 4.6 The claim boundary as executable code

Appendix A lists **twenty-five** forbidden claims. Through an earlier revision
it was a document a human was expected to remember. **Eighteen of them are now
word-anchored regular expressions** in `agents/claims.py`, and `enforce()`
raises rather than returning prose that breaks one.

```
Evidence -> Context (four closed sections) -> Generator -> Claim guard -> Output
                                                              |
                                                 fails -> deterministic fallback
```

Three properties must be stated together. Any two without the third would
mislead.

**First, it is lexical, not semantic.** It catches *outperforms*,
*deployment-ready*, *early detection*, *generalizes to*, *statistically
significant*, *externally validated*, *false alarms per hour*, *conformal
prediction*. It **cannot** catch a novel sentence that means the same thing in
words it does not hold. **It reduces the rate at which overclaims reach output;
it does not make overclaiming impossible, and no sentence in this paper may
imply otherwise.**

**Second, word anchoring is not optional.** A substring test for *"proved"*
matches *"improved"* and *"Provenance"*. That specific bug has bitten this
repository roughly ten times, which is why every one of the eighteen patterns is
anchored at word boundaries rather than written as a substring.

**Third, it cannot be run as a gate over human-authored prose, and that is not a
defect.** Running `find_violations` across the handbook sections that describe
this architecture reports **twelve violations, every one of them a quotation** —
the document that defines a boundary must state the boundary. The exemption is
therefore a caller-declared `quoting=` argument rather than a global suppression
list, because a document-wide exemption would silence the guard exactly where
prose is most likely to overclaim.

### 4.6.1 The evidence graph is the substrate, and the boundary is structural

Each alert is represented as a graph of **35 nodes and 39 edges**. Node kinds
and edge relations are **closed vocabularies**: adding a relation such as
`"probably_caused"` raises rather than being accepted as a new edge type.

The boundary lives in the graph rather than after it. Each *"does not
establish"* is a `constraint` node joined by a `bounded_by` edge, so a model
reading the graph encounters the limitation **as evidence**, structurally
indistinguishable in kind from the measurement it bounds — not as trailing prose
it may summarise away. The temporal evidence value `s_t` carries
`is_calibrated_probability: false` in its own node, so the corresponding
Appendix A claim cannot be inferred from the substrate even by a generator that
never reads a disclaimer.

### 4.6.2 Grounding by curation, not by retrieval

The research assistant answers from **six curated evidence objects**, verified in
continuous integration against the merged reports. It never reads a `_V1`
document at runtime, never embeds one, never searches, and **refuses** a question
that is uncovered or ambiguous.

The uncertainty-router rejection is the case that shows why. A plausible
free-text summary would say *"utility gain insufficient"*. The frozen record says
something different and more specific: the **calibration-agreement guard
passed**, at `0.006683691656635168` against a frozen tolerance of `0.02`, and
what failed was the **asymmetric-abstention guard** — an escalation ratio of
`6.453604523726777` against a limit of `3.0` fixed in advance.

**Raw document access lets a model paraphrase that badly. Invented placeholders
get it wrong outright.** Curation is the only one of the three that fails
closed: an object that does not exist produces a refusal, not a plausible
sentence.

### 4.6.3 What the guard does not establish

It does not establish that the explanations are **correct**.

They are **grounded**: every value in an explanation traces to a frozen
artifact, and a value with no such trace does not appear. Grounded is a
different and weaker property than clinically meaningful, and the distance
between them is not something this machinery measures. §8 reports a generation
that was fluent, scored **1.000** evidence fidelity with **zero** claim
violations, and was nonetheless **refused at runtime** for asserting a gate
state the evidence contradicted. That case is the clearest available statement
of the limit: the guard bounds what may be *said*, not what is *true*.

---

---

## 5. Predictive representation and personalization

**The machinery of §4 now has to pay for itself, and the rest of the paper is
the bill.** Everything from here is a measured quantity produced under that
apparatus, including three results that a programme without it could have
quietly declined to report.

This section reports two different kinds of evidence and **keeps them apart
throughout**: one sealed, confirmatory, single-use evaluation, and a set of
development-partition investigations conducted afterwards to understand it.
Conflating them is the error the whole apparatus in §4 exists to prevent.

### 5.1 The sealed encoder evaluation

The sealed TEST partition was opened once, on 2026-08-25, under an authorization
signed in advance. **It scored the B4-B encoder/head path alone.** That path
contains no memory, no physiology fusion and no episode state machine; it is not
the integrated system described in §3.

| Estimand | Value |
|---|---|
| Pooled-window AUPRC | **0.0935334** at prevalence **0.0460529** |
| AUROC | **0.7332374** |
| Subject-macro AUPRC | **0.354901**, over **8 of 12** subjects |
| 95% subject-bootstrap | **[0.033058, 0.239284]** |
| Decision threshold | **0.8329097628593445**, validation-selected, `test_informed: false` |

Four facts must accompany every use of these numbers. The test was **used
once** and `repeat_attempt_permitted` is `false`, so it cannot be reopened. The
threshold was **frozen from development** before the partition was opened. The
score is an **uncalibrated model score, not a calibrated probability**. And the
evaluation is of the **encoder/head path, not the integrated system**.

The result is weak in absolute terms and is reported as such. Its value to this
paper is not the number but its provenance: it is what the programme measured
when it could measure only once, at a threshold it could no longer change.

### 5.2 What the development investigation established, and what it did not

Four subsequent investigations, all on the development partition, asked whether
the representation could be improved. **All four returned null, inconclusive or refuted results, and all four are
reported because the manuscript's representation claims are bounded by them.**
The branch is closed on this corpus; that is a programme decision taken on the
evidence below, not a result the evidence produced. Figure **F4** carries the geometry.

**E10 — the head is faithful; the failure is representational.** Class direction
is highly coherent on training streams: LOSO cosine minimum **+0.971**, **0 of
79** negative. On held-out streams a small minority reverses. The registered
hypothesis that the frozen head was responsible was **refuted**: separation
exceeds between-subject dispersion by **26×** on TRAIN and **12×** on
VALIDATION. The head maps the direction the representation supplies.

**E11 — the registered mechanism was not established.** A morphology-aware
auxiliary objective was evaluated prospectively over **44 subjects / 79
streams**. Median cosine difference **+0.0030** [−0.0178, +0.0073]; `‖delta‖`
**+0.1217** [−0.5993, +0.5617]; negative fraction **−0.0127** [−0.0406, 0.0000].
**All three intervals include zero.** The outcome is Category C: the registered
mechanism was **not established**. A secondary subject-macro AUPRC movement was
observed and is treated as fragile — one seed per arm per fold means an arm
difference cannot be separated from single-seed training variance.

**E12d — the auxiliary loss had not plateaued at selection.** A replication gate
was passed first: **6 of 6** AUPRC values bit-identical to the prior run.
Instrumented replication then showed `F_aux` still moving (**+0.6208 / +0.2556 /
+0.5378**) and **5 of 6** checkpoint selections preceding the largest geometry
movement. The finding is that **the auxiliary loss had not plateaued at the
selected epoch**. No outer outcome was observed, so this says nothing about
whether a later checkpoint would have scored better. Decision D.

**E13a — one of two assessable failure streams reproduced.** Of 79 streams,
**57 were eligible**. Within-stream direction is highly stable: median
`cos_within` **+0.9935**, sign agreement **56 of 57**. Of the failure streams,
`s20171:0` reproduced (−0.4984, −0.3302) and `s20021:1` did not (+0.4514,
−0.9537); a third was unassessable because of positive concentration. The frozen
criterion required both, and **it was not relaxed when the result landed
one-of-two**. Decision D. **The 44-subject / 79-stream geometry population is
now consumed for confirmatory purposes.**

**Interpretation, bounded.** Minority unseen-stream representation failures are
real but heterogeneous, and the present corpus does not justify another
confirmatory representation intervention. The branch is closed **on this
corpus**, which is a statement about available evidence rather than about
representation learning.

### 5.3 Patient-relative memory: information, not prediction

**M1 carries incremental patient-relative information.** Stratified `d_long`
concordance moves **0.836 → 0.712**, broadly across **7 of 9** subjects; errors
sit further from the patient prototype (concordance **0.691**), and false
negatives sit *closer* than true positives (**0.126**). The natural reading is
that memory measures **atypicality**.

**Its predictive contribution is unresolved.** M1L moved pooled AUPRC
**0.375248 → 0.384796** (**+0.009548**) and subject-macro **0.409540 →
0.415833**, with sensitivity **−0.005318** and FPR **0.041489 → 0.039395**.
**There is no interval on any of these**, and the component was retained on
development evidence. The status is INCONCLUSIVE and the manuscript does not
upgrade it. The planned C0/C1 incremental probe was never executed, and RQ1
accordingly remains open (§11).

---

## 6. Temporal and episode-level reasoning

This is the paper's strongest affirmative quantitative section. It contains one
selection that must not be read as a win, and one bounded improvement that must
not be read as unbounded.

### 6.1 Temporal arm selection is selection, not superiority

S4D was selected over a GRU under a rule registered before the read, with tie
tolerance **0.002000**. The signed pooled difference is **0.093215**, 95% paired
subject-bootstrap **[−0.015229, 0.148951]**; the subject-macro difference is
**0.018415**. **The interval includes zero.** The correct statement is that S4D
was selected under a preregistered rule. The programme has **bounded selection
evidence** and nothing stronger, and Table T2 row 7 carries it that way.

### 6.2 Episode reasoning against a memoryless comparator

The episode state machine was compared with W1, a memoryless window-only
comparator, over 12 held-out subjects. Figure **F3** shows the paired
per-subject values and the difference.

| Estimand | Value |
|---|---|
| Subject-macro `episode_f1` (primary) | **0.2524**, 95% **[0.0826, 0.4415]**, defined **12/12** |
| `pooled_episode_f1` (descriptive, not primary) | **0.3423** |
| **T1 − W1 subject-macro difference** | **0.1921**, 95% paired subject-bootstrap **[0.0505, 0.3455]** |
| Reference episodes / predicted runs | **163 / 59** |
| Matched / unmatched predicted runs | **38 / 21** |
| Primary windows | **473,897** |

**The mandatory qualifier is "at the selected operating point"**, and it may
never be dropped. The comparator's operating point was not independently tuned,
so the difference bounds a comparison at one point rather than establishing a
general ordering. The pooled value in the table is the higher of the two and is
included rather than omitted, marked descriptive, because a reader will
otherwise find it and wonder why it was missing.

### 6.3 The failure distribution, which the mean hides

**Seven of twelve subjects score zero**, in two classes that push the operating
point in opposite directions:

- **Three subjects have no reference episodes at all** (`s2005`, `s2020`,
  `s2023`) and produced **7, 8 and 1** false runs respectively. Their score
  improves with *fewer* predicted runs.
- **Four subjects have reference episodes and produced no matched detection**
  (`s2019`, `s2058`, `s3072`, `s2059`). Their score improves with *more*.

There is one subject, `s2059`, where the memoryless comparator scores higher
than the episode machine (0.0417 vs 0.0000). It is visible in Figure F3(a), and
it is the reason the per-subject panel exists. **A subject-macro mean alone does
not characterise this system's episode performance**, and this manuscript does
not present one without its distribution.

### 6.4 Latency is a signed offset

**6 of 38** matched latencies are negative, and a median is defined for only
**5 of 12** subjects. Matching is overlap-only and run durations were not
stored. A negative signed offset under overlap matching **does not establish
anticipation**, and no anticipation claim is made anywhere in this paper.

---

## 7. Calibration, uncertainty and safe adaptation

Three components, adjudicated separately, of which **one was rejected**. Table
**T3** lists the gates, each written before the outcome it judged.

### 7.1 Calibration is retained

Platt calibration was selected on **NLL**, the criterion fixed before the read.
ECE was *not* the selection criterion and is reported as a descriptive check.

| | NLL | Brier | ECE (equal-width / equal-mass) |
|---|---|---|---|
| **Platt (retained)** | **0.143708** | **0.040344** | **0.016991 / 0.018604** |
| Temperature only | 0.191692 | 0.058647 | 0.074040 / 0.074040 |
| Uncalibrated | 0.231705 | 0.063567 | 0.063844 / 0.062464 |

Over **473,897** out-of-fold rows. Calibration improves the properties it was
selected for. It does not turn the sealed evaluation's score into a probability:
that score was produced by the uncalibrated path (§5.1).

### 7.2 The selective uncertainty router was rejected

A selective router at `c_star = 0.90` would abstain and escalate under
uncertainty. It was evaluated against **two guards frozen in advance**:

- **calibration-agreement guard — PASSED**, at `0.006683691656635168` against a
  frozen tolerance of `0.02`;
- **asymmetric-abstention guard — FAILED**, at an escalation ratio of
  `6.453604523726777` against a limit of `3.0` fixed in advance.

**`Retained: false`.** RQ3 is therefore answered, and the answer is negative.

The rejection is reported as a result rather than as a gap, and the specificity
matters. A plausible summary would say the utility gain was insufficient. The
frozen record says something different: the calibration half passed and the
abstention asymmetry failed. **The distinction is only available because the
gate was written before the outcome existed**, and it is what makes the
retentions elsewhere in this section credible. A programme in which every gate
passed would be indistinguishable from one that never wrote gates.

### 7.3 The contamination-safe update gate

**M2-G governs whether patient memory may update. It is a gate, not a
classifier**, and it is not offered as an accuracy improvement. Under gating,
AUPRC moves **−0.000268** (0.3847956 → 0.3845275) and AUROC **+0.000878**
(0.9075699 → 0.9084481); the decision threshold **0.7554003** was inherited
frozen rather than re-selected here. It was **RETAINED** on the basis of
contamination safety at essentially unchanged discrimination.

The right way to read M2-G is as a constraint on what the adaptive state is
allowed to learn from. RQ2 is **partial**: the gate is contamination-safe by
construction and by its gate evidence, and no episode-level contamination-stress
comparison was run.

---

## 8. Agentic explanation and runtime claim governance

§7 ended with a gate deciding what the system may *learn* from. This section is
the same authority deciding what the system may *say*, and that is the coupling
§1 names as the contribution: not two governance mechanisms that resemble each
other, but one evidence model applied to a second surface.

### 8.1 The generative arm has been exercised

An open-weight generative arm was evaluated on the contracted scenario with two
real models, **Qwen3-1.7B** and **Qwen3-4B-Instruct-2507**, greedy decoding on
CPU. The evaluation is **n = 1 context**.

| Metric | deterministic arm | generative arm |
|---|---|---|
| exercised | yes | **yes** |
| evidence fidelity | 1.000 | **1.000** |
| **claim violations** | **0** | **0** |
| completeness | 1.000 | 1.000 |
| latency | 0.0000 s | **63.4014 s** |

**One property of this table must be stated wherever it is used.** The
evaluation harness calls `provider.generate()` directly, so **no runtime gate
runs during evaluation**. The table therefore describes raw model output, not
what a user receives. Gating first would only ever have measured the template,
which is why the harness is built this way — but it means these three scores
answer a different question from the one a deployed system has to answer.

### 8.2 What the runtime did with the same generation: refused it

The generation that scored fidelity **1.000**, **0** claim violations and
completeness **1.000** asserted that the **`G1`–`G6`** range of safety checks had
passed. **`G4` and `G5` were blocked.** The assertion inverted the single most
safety-relevant fact in the explanation — the fact the contamination control
exists to communicate.

**Three gates passed it. The fourth did not.** The lexical claim guard saw no
forbidden pattern. The numeric claim guard saw no number (`G1` is not a numeral;
the digit follows a letter). The registered fidelity metric extracted no
unsupported value. The **categorical state-alignment gate** compared the asserted
gate range against the structured fields that record gate status, found the
contradiction, and refused. The runtime switched the delivered output to
`DETERMINISTIC` and served the deterministic renderer's text instead.

**The inversion reproduced on two independent runs.** It was also
**model-dependent**: `Qwen3-1.7B` produced it reproducibly and
`Qwen3-4B-Instruct-2507` stated the same fact correctly.

**This is a demonstrated failure mode in one context. It is not a failure rate**,
and no rate is claimed anywhere in this paper. One context, two models, one host
configuration. **What is not n = 1 is the sequence in §8.4**: four gates, each
added because a different real generation defeated everything already in place.
The single refusal reported here is the fourth of those, and the argument for
the architecture rests on the sequence rather than on the one case. Figure **F5** shows the generation, the three scores it passed and
the gate that refused it, with both qualifiers drawn into the figure rather than
left to the caption.

### 8.3 Why fluency metrics answer a different question

Evidence fidelity, claim-violation count and completeness are all properties of
the *relation between the text and the evidence it cites*. Every value in the
refused generation traced to a frozen artifact; nothing was invented; the
rounding was correct; it closed with the canonical disclaimer. **The defect was
categorical**: a statement about which gates were in which state, checkable only
against the structured fields that hold those states, and none of the three
metrics looks there.

This is the general form of the finding, and it is what the two-surface coupling
buys. A grounded-generation stack can be simultaneously faithful by every
registered metric and wrong about the fact that matters most. **Consistency with
structured state is a separate check from consistency with cited evidence**, and
the second does not imply the first.

### 8.4 Four gates, each added because the previous ones passed a real failure

The sequence in §8.2 was not designed. Each gate exists because a real
generation got past everything already in place, and the order in which they
were added is the order in which the failures were found.

| # | What got through | What it got past | What was added |
|---|---|---|---|
| 1 | a **truncated reasoning trace**, returned as if it were the explanation | fidelity **1.000**, **0** claim violations, completeness **1.000** — a deliberation fragment scored valid on every metric then in force | `enable_thinking=False`, and `_strip_reasoning` returns **empty** on an unclosed `<think>`, so truncation falls back rather than ships |
| 2 | *"an estimated peak probability of 54.6%"*, from `peak_probability = 0.545613` | the lexical guard, which sees no forbidden pattern, **and the registered fidelity metric, which extracts `\d+\.\d{2,}` and cannot see one decimal place** | the **numeric claim guard** — number plus optional unit, integers included, checked against all four context sections |
| 3 | *"passed several safety checks, including G1 through G6"*, when **G4 and G5 were blocked** | the lexical guard, the numeric guard, fidelity **1.000**, completeness | **categorical state alignment** against the structured fields |
| 4 | the categorical validator flagging the English word *normal* and **rejecting the deterministic fallback** | **its own regression test**, whose fixture set the lifecycle state to `NORMAL` and so licensed the bug | case-**sensitive** matching, since evidence and brief names are upper case |

**Gate 2 constrains this paper's own reporting.** The numeric guard that refuses
`54.6%` is strictly stricter than the registered fidelity metric, and the two
were deliberately left different. Widening the registered metric so that gate and
statistic agreed would have redefined a registered statistic to make a gate work
— the failure the entire apparatus exists to prevent, arriving disguised as
tidying-up. The metric is unchanged and §8.1 reports it unchanged.

**Gate 4 is the worst of the four and belongs here for that reason.** The gate
added in response to gate 3 rejected the deterministic renderer's *own* output,
because the gate reason it quotes verbatim contains an ordinary English adjective
that is also a lifecycle state name. **A gate that rejects its own fallback
converts every generative failure into a second failure and leaves the user with
nothing.** The regression test written for exactly this property passed, because
its fixture agreed with the code and only the real data disagreed. This was
first reported as a model failure against both models and is corrected in the
record rather than quietly dropped.

**Four gates do not make generated explanations safe.** Four is the number of
failures found by running two models on a small number of contexts. The
defensible claim is narrower: each gate is load-bearing, because a real output
got past its predecessors.

### 8.5 The claim guard, and who it actually catches

The publication claim boundary is Appendix A's **twenty-five** forbidden claims,
of which **eighteen are word-anchored regular expressions** in
`agents/claims.py`. The remaining seven are human-enforced, and that gap is real.

We did not learn the guard's worth from its tests. We learned it from **five
components that tripped it by accident**, built weeks apart by authors who had
all read the same boundary: an Evidence Agent's own disclaimer; an explanation
template's closing sentence; a Research Assistant's `claims_forbidden` list,
which states the forbidden claims *in order to prohibit them*; a demonstration
console where `textwrap` split the canonical disclaimer across two lines so a
**correct** output was flagged; and an evaluation report's reporting rules, which
prohibit a claim by naming it.

**In every case the offending text was a boundary statement.** Not one was a
model overclaiming. A lexical guard cannot distinguish an assertion from its
denial, and these five are that limitation meeting five authors who each assumed
their own phrasing was obviously exempt.

The fourth is a distinct and worse failure class: the guard accepted a passage
and rejected the *identical* passage after a renderer had broken it across two
lines. Content unchanged, presentation changed, verdict inverted. Stated beyond
this system: **an exemption matched against a surface form is a bug waiting for a
renderer**, and the same failure is available to secret scanners, licence
detectors and content filters.

Every fix was structural. Text that quotes a forbidden claim in order to deny it
is **declared** — registered once in `APPROVED_DISCLAIMERS`, or passed by the
caller as `quoting=`. The alternative was available and cheaper each time:
reword until the guard goes quiet. **Rewording trains authors to stop stating
boundaries plainly**, and a guard fixed that way grows quieter as the prose it
governs grows worse — a quiet indistinguishable from safety.

**What the guard does not establish.** It is lexical. It reduces the rate at
which a known class of overclaim reaches output; it does not make overclaiming
impossible, and no sentence in this paper implies otherwise. Run over this
programme's own governance prose it reports **twelve violations, every one a
quotation**; run over the §4 draft, **eight, every one a quotation**. That is why
the exemption is caller-declared rather than global: a document-wide exemption
would silence the guard exactly where prose is most likely to overclaim. **Five
catches are a count of boundary statements the authors happened to write, not a
detection rate.**

---

## 9. Integrated streaming operation

The runtime replays a record causally through the full path of §3 and emits
alerts with their evidence.

**Measured scope, stated exactly.** **1,079 windows of `s20201` in 89 s wall
clock**, giving approximately **61× real time** on a laptop CPU. On a separately
fixed host the encoder benchmark is median **4.161 ms/window**, p95 **4.337 ms**,
peak RSS approximately **305 MB**.

**Gate admission behaviour is restrictive by design.** On `s20201`, **0 of 1,079
windows were admitted** for memory update. `G5` dominates: an above-threshold
window arms a 60-second refractory while windows arrive every 5 seconds. This is
the contamination control of §7.3 doing what it was built to do, and it is
reported because a reader who assumed the gate was permissive would misread every
adaptation claim in §7.

**Evidence and alert provenance.** Every alert carries its evidence graph (§3.5),
and every agent output is grounded on that graph and nothing else. The
interaction boundary is the graph's closed vocabulary: a relation the vocabulary
does not contain raises rather than being accepted.

**What this measurement is not.** It is a **laptop-based edge simulation using
streaming physiological replay**. It is **not** edge-device validation, **not** a
clinical deployment, and **not** a production latency benchmark. No edge-hardware
measurement exists in this programme, and RQ5 remains open (§11).

**F6 decision.** The runtime evidence rests on two measured quantities — a
throughput ratio and a gate-admission count — each stated once above with its
denominator and its scope. Neither is a distribution, a trade-off curve, or a
relationship between variables; both are single numbers that a sentence carries
as well as a panel would, and the mechanism behind the admission count (a
60-second refractory against a 5-second window cadence) is one clause of prose.
A figure would restate the numbers at greater cost in space than the space it
would save the reader. **F6 NOT REQUIRED.**

---

## 10. Discussion

§3 through §9 have followed one path: a physical signal, a causal computation
over it, evidence produced under an enforced authority, a temporal decision, an
evidence graph, and a generated claim refused against that graph. What follows
asks what the combined evidence means, and what it cost.

### 10.1 An intelligent physical system must govern adaptation, not only optimise a predictor

The components in §3 that carry the most governance machinery are not the ones
that carry the most predictive weight. M2-G changes discrimination by
**−0.000268** AUPRC and exists entirely to constrain what the adaptive state may
learn from. The episode state machine has **no trainable parameters** and its
contribution is a decision procedure, not a fit. The claim guard changes no
number at all.

That distribution is the argument. In a system that adapts to a patient over
hours and then says something to a clinician, the questions that determine
whether the output is trustworthy are mostly not questions about the predictor.
They are questions about which windows were allowed to influence the state, which
partition produced which number, and whether the sentence delivered is consistent
with the state that produced it. **Optimising the predictor answers none of
them**, and a monitoring system evaluated only as a classifier leaves all of them
unasked.

### 10.2 Negative findings are operational, not decorative

Three components in this paper were built, evaluated against gates written
first, and **not** retained or **not** established: the selective uncertainty
router (§7.2), the morphology-aware representation objective (§5.2), and the
head-failure hypothesis (§5.2, refuted). Two prior normalization strategies were
closed the same way — static subject-score normalization was refuted *in
direction*, and stream-score normalization was closed on the finding that stream
variation is discriminative quality rather than removable offset.

Their value is not modesty. **It is that they make the retentions credible.** A
programme in which every component was retained is indistinguishable from one
that never wrote a gate, and a reader has no way to tell those apart from the
outside. The rejections are the only evidence available that the gates could
return no. That is why §7.2 reports the router's two guard values rather than a
summary: the specificity is what shows the gate was real.

### 10.3 Sealed evaluation and consumed evidence change what may be claimed

**All fifteen one-shot budgets in this programme are spent.** The sealed test was
consumed once; the historical VALIDATION partition is spent for confirmatory
purposes; the 44-subject / 79-stream geometry population was consumed by E13a.

The practical consequence is visible in §5.2. When E13a returned one of two
assessable failure streams reproduced, against a criterion frozen before
execution that required both, there was no version of the programme in which the
criterion could be relaxed and the population re-read. The branch closed. **A
budget that can be spent is what makes a preregistered criterion mean
something**, and the cost is that a genuinely promising direction can be closed
by an ambiguous result. We regard that as the correct trade and report both
halves of it.

This also bounds what §5.1's number can support. An encoder-only evaluation, used
once, at a threshold frozen beforehand, on an uncalibrated score, is a narrow
instrument. It is reported as one.

### 10.4 Agentic fluency is not evidence-state consistency

§8 is the paper's clearest single result and it is a negative one about a
positive-looking artifact. A generation that scored **1.000** on evidence
fidelity with **zero** claim violations and **1.000** completeness was refused,
because it asserted a gate range had passed when two of its gates were blocked.

The general lesson is about what the registered metrics measure. Fidelity checks
the text against the evidence it cites. Completeness checks that required
elements are present. Neither compares the text against the **structured state**
that records what actually happened. In a monitoring system, the categorical
facts — which gate blocked, which lifecycle state applies, whether an update was
admitted — are exactly the facts a clinician would act on, and they are the ones
a fluency metric cannot see.

**This is where the two-surface coupling pays.** The state the runtime checks the
generation against is the same governed evidence the experimental framework
produced and retained. There is no second, softer copy of the truth for the
generator to be scored against.

### 10.5 The cost, stated plainly

A reader deciding whether to adopt this apparatus deserves the bill, not only
the benefits.

**Volume.** At the measurement commit, `docs/` held **20,529 lines against
68,100 lines of source** — one line of governance prose for every **3.32** lines
of code, across **45** versioned protocol, decision, plan, amendment and report
documents. **The direction of travel is the finding, not the ratio**: between
two measurement points the documentation grew **22.5%** while the source grew
**7.5%**. The governance prose grew roughly three times faster than the code it
governs. That is uncomfortable, and understating it would read as defensive.

**The largest single line item.** A canonical experiment attempt failed after
its claim point and was **consumed rather than retried**. Re-measuring work the
machine had already computed once cost a 625-line amendment, nine new modules
totalling 3,165 lines, five test files and a separate human authorization. Under
a conventional regime it would have been an afternoon's re-run.

**Two cases where the discipline produced a worse report, on purpose and by
accident.** U1 pre-registered four degeneracy statistics; once the values were
visible it was clear the statistic that told the story was not among them, and
it was recorded as a limitation and **not added**, because choosing a statistic
after seeing the values is what pre-registration exists to prevent. Separately,
the first T2 execution silently dropped both arms' absolute AUPRC and seventeen
metric keys, removing the scale a reader needs to interpret a difference of
0.093215 — an unregistered reporting decision taken at execution time, produced
by the discipline's own over-caution and reversed by amendment.

**We do not claim the cost is worth paying in general.** We claim it was worth
paying here, and the numbers above are what a reader needs in order to disagree.

### 10.6 Why the representation branch was closed rather than tuned

E11, E12d and E13a could each have been followed by another intervention on the
same development subjects. We closed the branch instead.

The reason is in §4.2 and §10.3. The subjects available for that work are the
subjects the previous three investigations already read. Another intervention
tuned against them would produce a number whose optimism could not be measured,
because the population that would have measured it had been consumed producing
the hypothesis. **Closing the branch on this corpus is a statement about
available evidence, not about representation learning**, and the honest form of
it names the corpus.

---

## 11. Limitations

The limitations below are load-bearing. Several restrict claims made earlier in
this paper, and the required wording for each is carried in **Table T4**.

**External validity is the largest.** Route A external validation was **declined
in writing on 2026-08-24**. **No second cohort will corroborate any result in
this paper, permanently.** Every result is specific to LTSTDB, a single primary
corpus.

**The sealed evaluation is narrow.** It scored the **B4-B encoder/head path, not
the integrated system**; it was **used once** and cannot be reopened; and its
score is an **uncalibrated model score, not a calibrated probability**. Absolute
pooled predictive performance is weak — AUPRC **0.0935334** at prevalence
**0.0460529**.

**Episode performance is heterogeneous and partly absent.** **7 of 12** subjects
score zero, in two opposing classes; **4** subjects with reference episodes
produced **0** matched detections. A subject-macro mean alone does not
characterise this system.

**Latency is ambiguous in sign.** **6 of 38** matched latencies are negative
under overlap-only matching with no stored run durations. Nothing about
anticipation follows.

**Several analyses are post-hoc, and several populations are consumed.** E13a is
an exploratory post-hoc analysis of a prospectively held-out population. The
44-subject / 79-stream geometry population is consumed for confirmatory claims;
the historical VALIDATION partition is spent for confirmatory purposes. **E11
used a single seed per arm per fold**, so an arm difference cannot be separated
from single-seed training variance.

**Two component questions are unresolved rather than answered.** M1's predictive
contribution is unresolved (no interval), and RQ1 has no no-memory arm at
episode level. The selective uncertainty router was **rejected**; RQ3 is answered
negatively and no autonomy claim follows.

**There is no edge hardware.** §9 is a replay simulation on a laptop CPU. **No
edge-hardware measurement exists**, and RQ5 remains open.

**The agentic evidence is n = 1.** One context, two models, one host
configuration, reproduced across two runs. It is a demonstrated failure mode, not
a failure rate.

**The categorical validator is vocabulary-bound.** It compares asserted
categorical statements against structured fields by matching names drawn from a
closed vocabulary. **It is not a general semantic truth checker**, and gate 4 in
§8.4 is the demonstration: an ordinary English adjective that collided with a
lifecycle state name produced a false rejection of a correct output. The lexical
claim guard shares the limitation — it cannot distinguish an assertion from a
disclaimer, and **4 of 5** of its catches in our own code were quotations.
**Eighteen of Appendix A's twenty-five** forbidden claims are machine-checked;
seven remain human-enforced.

**Two research questions were never begun.** **RQ6** (foundation-model knowledge
for the compact student, Phase 4B) and **RQ7** (confounder-aware supervision for
false ST alarms, Phase 6B) were not started, and neither appears as a
contribution.

---

## 12. Conclusion

CardioSentinel is a monitoring system whose intelligence is deliberately
bounded, and the boundaries are executable rather than described.

The work demonstrates that connected physiological intelligence can be
implemented with enforced boundaries around four things: **what evidence a
system may learn from**, through partition authority and a contamination-safe
update gate; **how temporal decisions are formed**, through a parameterless
episode protocol reading a frozen list of permitted inputs; **what experimental
evidence remains valid**, through one-shot budgets that are spent, retention
decisions written before outcomes, and negative results retained rather than
discarded; and **what an agentic layer may claim**, through a claim boundary and
a categorical state-alignment gate that refused a fluent, fully faithful
generation in the single evaluated context.

The predictive results are modest and several are negative. Episode reasoning
improves episode-level agreement relative to a memoryless window rule, on
identical rows, at the promoted operating point, by **0.1921 [0.0505,
0.3455]**; the sealed encoder evaluation returned pooled AUPRC
**0.0935334** at prevalence **0.0460529**; a preregistered uncertainty router was
rejected by its own gate; and a representation-improvement branch was closed on
this corpus. **None of that is a diagnostic capability, and none of it is
offered as one.**

What the programme offers instead is a worked demonstration that the two
governance questions of §1 — what a system was allowed to learn, and what it is
allowed to say — can be answered by the same artifact, inside one physiological
physical–digital system. **To the best of our targeted review, we found no prior
system in which one authority spans both.** Bounded intelligence, not autonomous
diagnosis, is what this architecture is for.

---

## Tables

## Table T1 · System components and their individual retention decisions

**Purpose.** Show that the system is assembled from *individually adjudicated*
parts, each with its own decision document — not a pipeline described after the
fact. This is the table that makes the governance claim concrete before any
result is quoted.

| Component | Role in the IPS | Retained? | Evidence artifact | Decision document |
|---|---|---|---|---|
| **B4-B** CNN+Transformer encoder | window-level representation over raw waveform, 309,809 params, input `[B,1,2500]` | **SELECTED** over B4-A / B4-C | `phase3b2-architecture-v1` | `B4_GLOBAL_ENCODER_SELECTION_V1.md`, `B4_PROTOCOL_V1.md` |
| **P1-B** physiology fusion | fuses the frozen 18-dimension `morphology_v1` vector with the encoder | **RETAINED** | `phase4-p1-physiology-v1` | `P1_PHYSIOLOGY_RETENTION_DECISION_V1.md` |
| **M1L** long-timescale patient memory | patient-relative context across a stream | **RETAINED** | `phase5-m1-dual-memory-v2` | `M1_MEMORY_RETENTION_DECISION_V1.md` |
| **M2-G** contamination-safe update gate | governs *whether* memory may update; **a gate, not a classifier** | **RETAINED** | `phase6-m2-development-v1` | `M2_UPDATE_POLICY_RETENTION_DECISION_V1.md` |
| **U1** calibration | Platt calibration of the detector score | **RETAINED** | `phase7-u1-development-v1` | `U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` |
| **U1** selective uncertainty router | would abstain and escalate under uncertainty | **REJECTED** — `Retained: false` | `phase7-u1-development-v1` | `U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` |
| **T2** longitudinal temporal arm | continuous temporal evidence `s_t`; S4D selected over GRU | **RETAINED** (S4D) | `phase8-t2-development-v1` | `T2_LONGITUDINAL_TEMPORAL_RETENTION_DECISION_V1.md` |
| **T1** episode state machine | causal episode-level reasoning over 9 permitted row inputs | **EXECUTED, MEASURED, FROZEN** | `phase9-t1-*` | `T1_CAUSAL_EPISODE_STATE_PROTOCOL_V1.md` |
| **W1** window-only comparator | memoryless reference for T1 | **derived comparator** — no run directory | `W1_WINDOW_COMPARATOR_REPORT_V1.md` |
| **Evidence graph** | closed-vocabulary substrate; 35 nodes / 39 edges per alert | **structural** | `agents/graph.py` | handbook §53 |
| **Claim guard** | 18 machine-checked patterns of Appendix A's 25 | **structural** | `agents/claims.py` | handbook §53 |
| **IPS runtime** | streaming replay, gating, evidence emission | **implemented** | `edge/`, 1,692 lines | handbook §55 |

**Note the two rows that say no.** The selective router was built, evaluated
against a gate written before the outcome, and rejected. **A table in which
every component was retained would be evidence of a weaker process, not a
stronger system.**

---

## Table T2 · Primary quantitative results

**Purpose.** One place a reviewer can check every headline number, its
denominator, its partition and its epistemic status. This table is the paper's
factual spine.

| # | Result | Estimand | Value | Interval / denominator | Partition | Status |
|---|---|---|---|---|---|---|
| 1 | **Episode reasoning vs memoryless rule** | subject-macro `episode_f1` difference | **0.1921** | 95% paired subject-bootstrap **[0.0505, 0.3455]**; 12 subjects | development, held-out subjects | **SUPPORTED — BOUNDED** (one operating point) |
| 2 | **Episode state machine** | subject-macro mean `episode_f1` | **0.2524** | 95% **[0.0826, 0.4415]**; defined **12/12** subjects | development, held-out subjects | **SUPPORTED — BOUNDED** |
| 3 | Episode state machine, pooled | `pooled_episode_f1` | **0.3423** | 163 reference episodes, 59 predicted runs, 38 matched, 21 unmatched; 473,897 windows | development | descriptive — **not the primary estimand** |
| 4 | **Sealed encoder evaluation** | pooled-window AUPRC | **0.0935334** | prevalence **0.0460529** | **sealed TEST — consumed, single use** | **SUPPORTED** (negative in direction) |
| 5 | Sealed encoder evaluation | AUROC | **0.7332374** | same rows | sealed TEST | descriptive |
| 6 | Sealed encoder evaluation | subject-macro AUPRC | **0.354901** | over **8 of 12** subjects; 95% subject-bootstrap **[0.033058, 0.239284]** | sealed TEST | descriptive |
| 7 | **Temporal arm selection** | `pooled_auprc_difference`, signed S4D − GRU | **0.093215** | 95% paired subject-bootstrap **[−0.015229, 0.148951]** — **includes zero**; tie tolerance 0.002000 | development outer validation | **INCONCLUSIVE** |
| 8 | Temporal arm, subject-macro | `subject_macro_auprc_difference` | **0.018415** | — | development | descriptive |
| 9 | **Physiology fusion** | pooled AUPRC gain | **+0.03802798** | pooled over **473,897 windows / 12 subjects**; subject-macro **+0.01550711** over **9 contributing subjects** — the frozen decision gives this denominator without stating why three do not contribute; rate-related challenge FPR **+0.00603** (worse), carried explicitly | development | retained |
| 10 | **Patient memory (M1L)** | pooled AUPRC | **0.375248 → 0.384796** (**+0.009548**) | subject-macro **0.409540 → 0.415833**; sensitivity **−0.005318**; FPR **0.041489 → 0.039395** | development | **INCONCLUSIVE** — no interval |
| 11 | **Contamination gate (M2-G)** | AUPRC / AUROC under gating | **−0.000268** / **+0.000878** | threshold **0.7554003** inherited frozen, not selected here | development | **SUPPORTED** (safety, not accuracy) |
| 12 | **Calibration (U1 Platt)** | NLL / Brier / ECE | **0.143708** / **0.040344** / **0.016991** (equal-width), **0.018604** (equal-mass) | **473,897** out-of-fold rows; uncalibrated baseline **0.231705** / **0.063567** / **0.063844** | development | **SUPPORTED** |
| 13 | **Uncertainty router** | prespecified retention gate | **`Retained: false`** | calibration-agreement guard **passed** at 0.006683691656635168 vs tolerance 0.02; **asymmetric-abstention guard failed** at ratio **6.453604523726777** vs limit **3.0** | development | **NEGATIVE FINDING** |
| 14 | **Representation geometry, prospective** | held-out streams with negative class direction | **3 / 79** | 44 evaluable subjects; TRAIN LOSO reference min **+0.971**, **0/79** negative | development, prospective 3-fold | **SUPPORTED** (mechanism) |
| 15 | **Morphology intervention (E11)** | median cosine / ‖delta‖ / negative fraction, B1 − B0 | **+0.0030** / **+0.1217** / **−0.0127** | 95% paired subject bootstrap **[−0.0178, +0.0073]** / **[−0.5993, +0.5617]** / **[−0.0406, 0.0000]**; 44 subjects | development, prospective | **NOT SUPPORTED** — Category C |
| 16 | **Streaming runtime** | replay throughput | **~61× real time** | 1079 windows of `s20201` in 89 s wall, laptop CPU | n/a — system measurement | **SUPPORTED — BOUNDED** (not edge hardware) |
| 17 | Encoder inference cost | per-window latency | median **4.161 ms**, p95 **4.337 ms** | peak RSS **~305 MB**, fixed host | n/a | descriptive |
| 18 | **Guarded explanation** | evidence fidelity / claim violations / completeness | **1.000** / **0** / **1.000** | **n = 1 context**, Qwen3-1.7B and Qwen3-4B-Instruct-2507; generative latency 63.4014 s | n/a — system evaluation | **SUPPORTED** as a demonstrated failure mode |

**Rows 4–6 are the encoder/head path alone**, not the integrated system, and the
score is an **uncalibrated model score, not a calibrated probability**. Rows 1–3
concern the episode layer; **rows 4–6 and rows 1–3 must never be presented as
comparable.**

---

## Table T3 · Personalization, uncertainty and governance gates

**Purpose.** Show that each adaptive or agentic component was tested against a
gate **written before the outcome existed** — including the two gates that
returned no. This is the table that makes T1's retentions credible.

| Component | What was tested | Prespecified gate | Outcome | Retained? |
|---|---|---|---|---|
| **M1L memory** | whether patient-relative memory is retained into the pipeline | retention criteria fixed in `M1_DUAL_MEMORY_PROTOCOL_V2.md` before the read | pooled AUPRC **+0.009548**, FPR **−0.002094** abs, sensitivity **−0.005318** | **yes** |
| **M2-G update gate** | whether memory may update without contamination | gate derivation frozen on TRAIN; threshold **0.7554003** inherited, not re-selected | AUPRC **−0.000268**, AUROC **+0.000878** — discrimination essentially unchanged | **yes** |
| **U1 calibration family** | which calibration family, selected on **NLL** | family selection rule fixed before the read; **ECE was not the criterion** | Platt NLL **0.143708** vs uncalibrated **0.231705** | **yes** (Platt) |
| **U1 selective router** | whether abstention improves safe autonomy at `c_star = 0.90` | two guards, both frozen in advance | calibration-agreement **PASSED** (0.006683691656635168 vs 0.02); **asymmetric-abstention FAILED** (6.453604523726777 vs 3.0) | **NO** |
| **T2 temporal arm** | S4D vs GRU under a preregistered selection rule | selection rule and tie tolerance **0.002000** fixed before the read | difference **0.093215**, 95% **[−0.015229, 0.148951]** — **interval includes zero** | **yes** (selected, not proven superior) |
| **E11 morphology objective** | whether a training-only auxiliary objective improves held-out direction stability | primary geometry endpoints and paired bootstrap registered before execution | all three intervals include zero | **NO** — Category C |
| **Claim guard** | whether the publication boundary binds generated prose | 18 word-anchored patterns of Appendix A's 25, `enforce()` raises | caught **5** violations in the repository's own code | **structural** |
| **Runtime explanation gate** | whether a fluent generation reaches the user | four sequential gates on the evidence graph | fidelity **1.000**, **0** claim violations — and **refused**: asserted `G1`–`G6` passed while **G4, G5 blocked**; reproduced on **2** runs | **refused → deterministic fallback** |

**Two gates returned no, and one refused an output that had already passed three
checks.** The first three gates passed that generation; the fourth did not.

---

## Table T4 · Negative findings, limitations, and required wording

**Purpose.** The paper's credibility rests on this table being present and
unflinching. Every row states what the finding restricts and the wording the
manuscript must use.

| Finding / limitation | Evidence | Restricts | Required wording |
|---|---|---|---|
| **Uncertainty router rejected** | `Retained: false`; asymmetric-abstention ratio 6.4536 vs limit 3.0 | any autonomy claim | "built, evaluated against a prespecified gate, and rejected" |
| **Morphology intervention not established** | E11 Category C; all three intervals include zero | representation-improvement claims | "the registered mechanism was not established" |
| **E12d Decision D** | replication gate PASSED; `F_aux` +0.6208 / +0.2556 / +0.5378 | checkpoint claims | "the auxiliary loss had not plateaued"; **never** "a later checkpoint is better" |
| **E13a Decision D** | 1 of 2 assessable failure streams reproduced; 57/79 eligible | mechanism claims | "one of two assessable failure streams reproduced"; **never** "a reversal mechanism was established" |
| **Static subject-score normalization closed** | E7a: perfect ECDF normalization is the **worst** arm | personalization-by-normalization | "refuted in direction" |
| **Stream-score normalization closed** | E7b: one stream anti-correlated, AUROC **0.2119** | same | "stream variation is discriminative quality, not offset" |
| **Head-failure hypothesis refuted** | E10: separation exceeds between-subject dispersion **26×** TRAIN / **12×** VALIDATION | attribution of failure | "the head is faithful; the failure is representational" |
| **S4D superiority not established** | **[−0.015229, 0.148951]** includes zero | temporal-architecture claims | "selected under a preregistered rule", **never** "superior" |
| **M1 predictive gain unresolved** | +0.009548 pooled AUPRC, **no interval** | memory claims | "retained on development evidence; the predictive contribution is unresolved" |
| **Sealed test is encoder-only** | `TEST_ATTEMPT.json` input contract, 309,809 params, no memory / fusion / state machine | any system-level performance claim | "the B4-B encoder/head path, **not** the integrated system" |
| **Sealed test consumed** | `repeat_attempt_permitted: false` | any re-evaluation | "used once; cannot be reopened" |
| **Score is uncalibrated** | `score_semantics` in `TEST_ATTEMPT.json` | probability language | "an uncalibrated model score, not a clinical probability" |
| **Heterogeneous subject performance** | **7 of 12** subjects score zero: 3 episode-free (7, 8, 1 false runs), 4 missed | episode-detection claims | report the subject distribution, **never the mean alone** |
| **Signed latency** | **6 of 38** matched latencies negative; overlap-only matching, no run durations stored | timing claims | "a signed offset; does **not** establish anticipation" |
| **Consumed geometry population** | E13a, 2026-08-28 | future geometry claims | "the 44-subject / 79-stream population is **consumed** for confirmatory claims" |
| **Historical VALIDATION spent** | used for hypothesis generation across E1–E10 | fresh confirmation | "spent for confirmatory purposes" |
| **Single seed per arm per fold** | E11 amendment A3 | E11 arm contrasts | "an arm difference cannot be separated from single-seed training variance" |
| **No external cohort** | Route A declined 2026-08-24, §2.4 | all external validity | "**no second cohort will corroborate any result, permanently**" |
| **Laptop, not edge** | 61× on laptop CPU; no edge measurement exists | RQ5, deployment | "replay simulation on a laptop CPU" |
| **Qwen n = 1** | 1 context, 2 models | agentic-safety generalization | "a demonstrated failure mode in one context — **not a failure rate**" |
| **Lexical claim validator** | 4 of 5 catches were quotations; 8 of 8 on the §4 draft were quotations | guard strength | "lexical; cannot distinguish assertion from disclaimer" |
| **Appendix A partially machine-checked** | **18 of 25** patterns encoded | governance completeness | "eighteen of twenty-five are machine-checked" |
| **RQ6 / RQ7 never begun** | Phase 4B, Phase 6B | contribution scope | must not appear as contributions |

---

---

## Figures

All five figures are supplied as vector PDF, with 200 dpi PNG previews.
**No figure computes a new scientific quantity**; every plotted value traces to
a frozen report or promoted run artifact. Regeneration commands and full
provenance accompany the figure sources. Series identity is never carried by
colour alone —
each series also carries its own marker shape, so the figures survive greyscale
printing and colour-vision deficiency.

| Figure | Title | Carries | Cited in |
|---|---|---|---|
| **F1** | CardioSentinel as an intelligent physical system | four layers; the evidence constraining each; the train/runtime equivalence audit (physiology half bit-exact `0.000e+00` on 64/64 rows, embedding half max `7.15e-07` = 6 ULP) | §3, §3.6 |
| **F2** | Partition authority and the one-way spend of evidence | 56 TRAIN / 12 VALIDATION / sealed TEST; nested consumption of the E11 geometry population inside a still-usable partition; TEST consumed 2026-08-25 | §4 |
| **F3** | Episode reasoning vs the memoryless comparator | (a) paired per-subject `episode_f1`, 12 subjects, the 7 zeros plotted at zero and `s2059` visible; (b) difference **0.1921** [0.0505, 0.3455] | §6.2, §6.3 |
| **F4** | Representation geometry and its failure minority | (a) outer-train (158 streams, 0 negative) vs outer-held-out (79 streams, 3 negative) cosine; (b) `‖delta‖` against cosine with the three negatives labelled | §5.2 |
| **F5** | A fluent generation that three gates passed and the fourth refused | fidelity 1.000 / violations 0 / completeness 1.000, the `G1`–`G6` assertion against **G4, G5 BLOCKED**, mode → `DETERMINISTIC`; both qualifiers drawn into the figure | §8.2 |

**F6 — not drawn.** See §9 for the decision and its reasoning.

---

## Assembly provenance — not manuscript prose

This body was assembled 2026-08-28 from repository sources under the authority
order *frozen report → `CURRENT_STATE.md` → handbook → audit → existing draft*.

| Manuscript section | Source |
|---|---|
| §1, §1.1 | `CARDIOSENTINEL_PAPER_READINESS_AUDIT_V1.md` §1, §10 |
| §2 | `PAPER_S2_RELATED_WORK_DRAFT.md`, integrated verbatim below the heading |
| §3 | `PAPER_OUTLINE_V2.md` §3.5, handbook §52/§55, `src/cardiosentinel/edge/` |
| §4, §4.6 | `PAPER_S4_EVIDENCE_FRAMEWORK_DRAFT.md`, integrated verbatim |
| §5–§7 | audit §4.1–§4.5, §2 claim matrix |
| §8.1–§8.3 | audit §4.6, `EXPLANATION_EVALUATION_REPORT_V1.md` |
| §8.4–§8.5 | `PAPER_S5_6_CLAIM_BOUNDARY_DRAFT.md` Parts A and B |
| §9 | audit §4.7, outline §3.5.3 |
| §10 | `PAPER_S9_DISCUSSION_DRAFT.md` §9.1–§9.3, §9.5 |
| §11 | audit §11 limitations matrix |
| T1–T4 | `PAPER_TABLES_T1_T4_DRAFT.md`, integrated verbatim |

**Renumbering.** `PAPER_S5_6_CLAIM_BOUNDARY_DRAFT.md` is titled §5.6 under the
outline's numbering, where §5 was the failure-and-recovery section. Under the
assembled structure §5 is representation and personalization, so that material
is placed at **§8.4–§8.5**, with the claim-guard half after the four-gate half
because §8.2's refusal is the case both explain. No content was dropped in the
move.
