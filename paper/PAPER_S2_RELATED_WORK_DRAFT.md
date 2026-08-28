# §2 — Related work

> **Draft prose for the manuscript.** Not a frozen record: no `_V1`, no digest.
> Written **after** the search it depends on, which is
> `LITERATURE_SEARCH_V1.md` and `LITERATURE_SEARCH_V1.json`, executed
> 2026-08-25.
>
> **The §6.3 ordering condition, recorded here because it binds this file.**
> `B4_TEST_AUTHORIZATION_V1.md` §6.3 waived §2's completion until manuscript
> drafting, and attached one condition to the waiver: **§2, when written, must
> not be shaped by the sealed-test result.** This section honours it by
> construction — it was drafted from the recorded literature search and revised
> from `CARDIOSENTIN_RELATED_WORK_VERIFICATION_V1.md`, and neither input reads
> the sealed evaluation. The §2.6 gap statement was narrowed by prior art
> (`arxiv:2509.06902`, `arxiv:2603.10742`), not by any number this programme
> produced. **Checked mechanically, 2026-08-28:** no numeric surface form
> derived from the sealed TEST metrics appears anywhere in this file. The
> condition stays binding on every future revision.
>
> **This draft supersedes `PAPER_OUTLINE_V2.md` §2 on one point and the point
> matters.** The outline instructs the author to close the section with the gap
> statement *"none of them, as far as we are aware, ships the machinery that
> makes the outcome checkable by a third party who does not trust the
> authors."* **The search refutes it.** `arxiv:2605.08586` names the same
> problem, argues the same negative about checklists and code sharing, and
> ships a reference implementation. §2.6 below is what remains true, and it is
> narrower.
>
> **Citation status is recorded in
> `CARDIOSENTIN_RELATED_WORK_VERIFICATION_V1.md`**, which audits all 77 keys
> against Crossref, PubMed and arXiv: 48 `VERIFIED — PRIMARY`, 29
> `PREPRINT — VERIFIED`, none unresolved. That document also records four
> narrowed overstatements, the prior art that refutes part of §2.6's earlier
> gap statement, and the EDB/LTSTDB comparison that must not be reintroduced.
>
> **Every citation key here resolves to a record the recorded search returned.**
> `python scripts/literature_search.py verify paper/PAPER_S2_RELATED_WORK_DRAFT.md`
> fails on any key that does not. That check proves provenance, not
> comprehension: it cannot tell whether a work says what this section says it
> says. `LITERATURE_SEARCH_V1.md` §6 states the rest of the limits, and a
> reader should apply them here.

---

## Draft

Four literatures neighbour this work, and a fifth became a neighbour only when
the system acquired a generated-language surface. This section positions the
contribution against each. **In no case is the claim that we detect ischemia
better**, and §2.1 says so first because it is the comparison a reader of an
ECG paper will reach for.

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
