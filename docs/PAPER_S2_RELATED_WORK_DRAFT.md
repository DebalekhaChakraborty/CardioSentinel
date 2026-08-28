# §2 — Related work

> **Draft prose for the manuscript.** Not a frozen record: no `_V1`, no digest.
> Written **after** the search it depends on, which is
> `LITERATURE_SEARCH_V1.md` and `LITERATURE_SEARCH_V1.json`, executed
> 2026-08-25.
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
> **Every citation key here resolves to a record the recorded search returned.**
> `python scripts/literature_search.py verify docs/PAPER_S2_RELATED_WORK_DRAFT.md`
> fails on any key that does not. That check proves provenance, not
> comprehension: it cannot tell whether a work says what this section says it
> says. `LITERATURE_SEARCH_V1.md` §6 states the rest of the limits, and a
> reader should apply them here.

---

## Draft

Four literatures neighbour this work, and a fifth became a neighbour only when
the system acquired a generated-language surface. This section positions the
contribution against each. **In no case is the claim that we detect ischemia
better**, and §2.1 says so first because it is the comparison a reader of an ECG
paper will reach for.

### 2.1 ST-episode detection in ambulatory ECG

The immediate technical neighbours are small in number and unusually coherent.
Transient ischemic ST episodes in long ambulatory recordings have been studied
against two annotated resources: the European ST-T Database
[pmid:1396824], and the Long-Term ST Database [pmid:12691437], which is this
system's training cohort and which was built expressly as a reference for
developing and evaluating automated ischemia detectors. Both are distributed
through PhysioNet [doi:10.1161/01.cir.101.23.e215].

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
systematically in [arxiv:2001.01550] and, for the personalised setting, in
[arxiv:2409.07975]. **Its centre of mass is not our task.** The dominant setting
is 12-lead resting or short-strip diagnosis — recent examples include occlusion
myocardial infarction identification [pmid:42129209], large-scale acute coronary
syndrome corpora [pmid:42082497], and transfer learning from ECG imagery
[pmid:41358268] — rather than continuous multi-hour ambulatory streams with
episode-level endpoints. Work directly on ambulatory signal quality and noise
[arxiv:2201.10061] is closer to our operating conditions than most of the
diagnostic literature is.

Self-supervised and contrastive representation learning for ECG is well
populated: lead-agnostic local and global representations [arxiv:2203.06889],
physiologically-inspired augmentations for 12-lead records [arxiv:2106.04452],
subject-aware contrastive learning for biosignals [arxiv:2007.04871], and masked
transformer pretraining [arxiv:2309.07136]. Our encoder's architectural lineage
is the structured state-space family — [arxiv:2111.00396], its diagonal
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
programme [arxiv:2003.12206] and the first large analysis of the NLP
Reproducibility Checklist [arxiv:2306.09562] measure what checklists changed;
the latter, over 10,405 responses, finds increases in reported information and
that fewer than half of submissions claim to open-source code. Leakage has been
shown to be widespread and consequential across 17 fields
[doi:10.1016/j.patter.2023.100804, arxiv:2207.07048], with concrete instances in
applied domains [arxiv:1909.06539] and sustained attention in the scientific
press [doi:10.1038/d41586-022-02035-w]. Reproducibility in ML for health
specifically has been characterised as structurally worse than in neighbouring
fields [arxiv:1907.01463], and domain-specific assessment frameworks have
followed [arxiv:2401.08847]. Pre-registration itself has been adapted to
predictive modelling as a lightweight template with a qualitative evaluation
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
artifacts that testify to what did not happen** — a checklist cannot demonstrate
that no model was loaded, and a zero-capability counter written by the run can.
**That positioning is real but it is no longer sufficient on its own**, because
§2.6's neighbours enforce at execution time too.

### 2.4 Selective prediction, calibration, and deferral

The reject option is old and the theory is settled: the error–reject tradeoff
was characterised in [doi:10.1109/tit.1970.1054406], and the modern selective
classification line — pointwise-competitive selective classification
[doi:10.1613/jair.4439], selective classification for deep networks
[arxiv:1705.08500], and an integrated reject option trained end to end
[arxiv:1901.09192] — extends it to the setting we work in. Recent work sharpens
the objective [arxiv:2206.09034], couples it to calibration
[arxiv:2208.12084], derives it from training dynamics [arxiv:2205.13532], and
examines its behaviour under distribution shift [arxiv:2405.05160]. Calibration
itself has an equally clear line [arxiv:1706.04599, arxiv:2106.07998], and
learning-to-defer treats the human as a second decision-maker rather than a
fallback [arxiv:2006.01862, arxiv:2202.03673, arxiv:2310.14774].

**Positioning, and it is a negative result.** We implemented selective routing,
evaluated it against a prespecified exit gate fixed before the evaluation, and
**rejected it**. The paper reports the rejection as a result, with the gate that
produced it.

**One observation about this literature, stated with its bound.** Across the 77
records this subsection's queries returned, the abstracts describe methods that
improve a risk–coverage curve or a deferral rule; **none reports a selective
mechanism that was built, evaluated against a prespecified gate, and abandoned.**
That is a statement about what a recorded search returned, not a claim about the
field, and §9.3 develops the publication-incentive argument on exactly that
footing and no further.

### 2.5 Grounded generation, provenance-constrained NLG, and guardrails

This literature became a neighbour when the system acquired a generated-language
surface (§4.6), and it has three parts.

**Grounding output in retrieved evidence.** Retrieval-augmented generation
[arxiv:2005.11401] established the arrangement — a parametric generator over a
non-parametric retrieved memory — and subsequent work makes retrieval active
[arxiv:2305.06983] or corrective [arxiv:2401.15884].

**Measuring whether output is actually supported.** Faithfulness and factuality
in abstractive summarisation [arxiv:2005.00661] and the Attributable to
Identified Sources framework [arxiv:2112.12870] give the vocabulary; the
hallucination survey [arxiv:2202.03629] gives the taxonomy. Evaluation has since
moved to maintained leaderboards with private splits [arxiv:2501.03200] and to
runtime monitoring of faithfulness during generation [arxiv:2406.13692].

**Guardrails.** Programmable output rails, independent of the underlying model
and interpretable by the developer, are the industrial pattern
[arxiv:2310.10501]. Their limits are documented: a comparative evaluation across
industrial guardrails finds an unavoidable security/usability tradeoff
[arxiv:2504.00441], and guardrail robustness degrades under RAG-style contexts
[arxiv:2510.05310]. In clinical deployment the pattern appears both as a safety
classifier [pmid:41933065] and as an error-prevention layer over generated
instructions [pmid:38664535].

**Positioning.** The usual arrangement grounds a model in retrieved
**documents**. This system grounds it in a **closed evidence graph with closed
vocabularies**, gives it four sealed context sections and no free-text channel,
and places a lexical claim guard, a numeric claim guard and a categorical
alignment check between generator and user, with a deterministic renderer behind
them as the fallback. The distinguishing property is not that the model is
constrained — [arxiv:2310.10501] constrains a model. **It is that the constraint
is the same publication claim boundary the manuscript is bound by, so an
overclaim in generated prose and an overclaim in this paper fail against one
artifact.** We take [arxiv:2504.00441]'s finding as the honest frame for what
that costs: our fallback rate is the usability side of exactly that tradeoff,
and §7.6 reports it rather than defending it.

### 2.6 Where this work sits

**The problem this paper addresses has been independently named, and we do not
claim to have noticed it first.** [arxiv:2605.08586] calls it *experiment
nonrepudiation*: binding the numbers in a paper to an actually executed
computation in a way the author cannot later alter or deny. It argues — with the
threat model spelled out — that self-reported checklists, optional code sharing
and author-controlled logging do not answer the question a reviewer cannot
check, and it ships a reference implementation to show the problem is solvable.
Nearby, sample-level pipeline traceability anchored to tamper-evident
cryptographic commitments [arxiv:2601.14971] and machine-verifiable provenance
for model lineage and environment [arxiv:2605.19755] attack the same class of
problem from the supply-chain side. The re-executable-publication tradition is
older than all of it [doi:10.1016/j.procs.2011.04.061,
doi:10.1016/j.procs.2012.04.047] and now has platforms
[doi:10.3233/apc200107, doi:10.1186/s13059-021-02299-x], and code review has
been proposed as the human complement [doi:10.1038/s41562-021-01190-w].

**What that machinery binds is the computation. What it does not bind is the
claim.** A signed attestation establishes that a number came from a run. A
provenance chain establishes which data and which environment produced it. A
private leaderboard split establishes that a score was not tuned against its own
test set. **None of them reads the sentence a human will actually take away and
refuses it because the evidence does not support that sentence.** That object —
the natural-language claim, checked against a closed evidence graph and refused
when the check fails — is where this work sits, and it is the honest form of the
gap.

Three properties follow, and they are the section's exit:

1. **The claim, not the computation, is the enforced object.** The guards in
   §4.6 operate on generated prose and on the manuscript's own text.
2. **One artifact governs two surfaces.** The claim boundary that binds this
   paper is the code that binds the runtime's explanation. The neighbouring
   systems have one surface, so the question does not arise for them.
3. **The apparatus produces evidence of absence.** Attestation records what
   happened; a zero-capability counter written by a run records what did not,
   and §5 turns on artifacts of that kind.

**These are complements, not competitors.** [arxiv:2605.08586] proposes a
protocol for conferences and calls for a standard; this is one project's
machinery, applied at authoring time, reported in §9.6 with the cost it imposed.
A field that adopted both would have numbers bound to runs and claims bound to
evidence. **It currently has neither as a default, and this paper is an
existence proof for the second half at the scale of a single research
programme.**
