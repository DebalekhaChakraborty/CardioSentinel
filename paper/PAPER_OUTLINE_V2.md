# CardioSentinel — Paper Outline, V2

**This supersedes `PAPER_OUTLINE_V1.md`, which is retained unedited.** V1 was
written at #81, when the repository held a frozen research pipeline and nothing
else. Between #82 and #94 the project stopped being an ECG model and became an
intelligent physical system that senses, decides, explains, and refuses claims
its evidence does not support. **No experiment was run, no budget was opened, no
artifact was touched, and no scientific finding changed** — §56 of the handbook
states that explicitly, and §7 of this outline depends on it being true.

V1's §2 and §9 arguments were sound and are carried forward rather than
rewritten. What V1 could not know is the subject of §§3.5, 4.6, 5.6 and 9.6
below.

**It is an outline, not a draft, and it contains no citations.** Where a
citation is required it says so. Inventing one would be the same class of error
the programme's entire apparatus exists to prevent.

**Pinned to `origin/master` `a8f1b47`** (merge of #94), tags
`research-freeze-v1.0` and `ips-agentic-runtime-v1.0`, 3,302 tests collected.

---

## 0. The argument, in one paragraph

Machine-learning research on clinical time series routinely reports results that
cannot be audited: thresholds selected on the evaluation set, held-out data
consulted more than once, and comparative claims made against arms that were
never run. **CardioSentinel is an ambulatory ECG ischemia-detection pipeline
built so that each of those failures is structurally impossible rather than
merely discouraged**, and the paper's contribution is that machinery together
with an honest account of what it permitted us to conclude — which is less than
we expected, in ways the machinery itself surfaced.

**V2 adds a second half to that sentence.** The same apparatus was then carried
past the research boundary into a running system, and the claim boundary that
had governed a manuscript was compiled into code that governs a live output. The
paper can now show a boundary being enforced on prose a machine wrote thirty
seconds ago, not only asserted about prose a human will write later.

**The paper is a methodology paper with a worked application. It is not a
performance paper.** Section 9 has to defend that choice rather than apologise
for it.

---

## 1. Introduction

- Ambulatory ST-episode detection: the task, the horizon, why continuous
  monitoring differs from resting diagnosis.
- **Detection, not diagnosis.** Fixed at first use and never relaxed.
- The auditability gap, stated as the problem the paper addresses.
- Contributions, in the order the paper delivers them: the evidence framework;
  a real post-claim failure and its authorized recovery; **a claim boundary
  enforced as executable code, with five instances of it catching this
  repository's own authors**; a measured pipeline with every boundary reported;
  and one methodological finding that generalises past ECG (§9.2).
- **"Causal" means temporal non-anticipation**, defined here and never used in
  the inferential sense.

## 2. Related work — **searched 2026-08-25; drafted; gap statement refuted**

> **Amendment, 2026-08-25.** The search this section waited four sessions for
> has been run and recorded: `LITERATURE_SEARCH_V1.md` and its JSON, 65 queries
> across Crossref, arXiv and PubMed, 393 hits. **The gap statement at the foot
> of this section did not survive it** — `arxiv:2605.08586` (May 2026) names the
> same problem, makes the same negative argument about checklists and code
> sharing, and ships a reference implementation. **Do not write the gap
> statement as this section specifies it.** The drafted section is
> `PAPER_S2_RELATED_WORK_DRAFT.md` and its §2.6 is the narrower claim that
> survives. The rest of this section's positioning is unaffected and was used
> as written.

Unchanged from V1 in substance. Four bodies of work, each with the positioning
claim the paper needs to make against it. **Citations to be gathered; none are
asserted here.**

**2.1 ST-episode detection on LTSTDB and EDB.** The immediate technical
neighbours. *Positioning:* we are not claiming a better detector. We are
claiming a detector whose reported number can be traced to the access that
produced it. The comparison to make is on **what is reported**, not on the
metric value — and the paper should say plainly that our headline figure is
modest.

**2.2 Deep learning for ambulatory ECG.** Architecture lineage for the encoder,
the physiology fusion, the memory, and the longitudinal arm. *Positioning:*
every architectural choice here was made by a rule frozen before the deciding
evidence existed, and one of them (S4D over GRU) is reported with an interval
that includes zero.

**2.3 Reproducibility, pre-registration and result-blind analysis in ML.**
*Positioning, and this is the paper's sharpest claim:* checklists record intent
at submission time. **This work enforces the same properties at execution time,
from code, and produces artifacts that prove what did not happen.** A checklist
cannot demonstrate that no model was loaded; a zero-capability counter written
by the run can.

**2.4 Selective prediction, calibration, and deferral to a human or cloud.**
*Positioning:* we implemented it, evaluated it against a prespecified exit gate,
and **rejected** it. The paper reports the rejection as a result.

**2.5 — new in V2. Grounded generation, provenance-constrained NLG, and
guardrails.** Required because the paper now contains §4.6 and §5.6. The
neighbours are retrieval-grounded generation, structured-evidence NLG, and the
guardrail/output-filter literature. *Positioning:* the usual arrangement grounds
a model in retrieved **documents**. This system grounds it in a **closed
evidence graph with closed vocabularies**, gives it four sealed context sections
and no free-text channel, and places a lexical claim guard between generator and
user with a deterministic fallback behind it. **The distinguishing property is
not that the model is constrained — it is that the constraint is the same
publication claim boundary the manuscript is bound by, so an overclaim in
generated prose and an overclaim in the paper fail against one artifact.**
Whether that framing is novel is a question for the search, not for this
outline.

**Gap statement to close the section.** Each of these literatures reports
outcomes. None of them, as far as we are aware, ships the machinery that makes
the outcome checkable by a third party who does not trust the authors. **That is
the gap.** Whether *"as far as we are aware"* survives the literature search is
itself a finding, and the section must be written after the search, not before.

**This remains the single largest unstarted item in the manuscript.** V1 said
so; it is still true, and it is now the *only* section with no source material
in the repository at all.

## 3. Methods

**3.1 Problem and data.** LTSTDB, subject-disjoint 70/15/15, seed 2026,
annotation semantics, cross-dataset provenance. **EDB's contamination is
established here, not deferred to limitations** — it is a design constraint that
shaped the split policy.

**3.2 Signal pipeline.** Complete; sources named in the handbook.

**3.3 Architecture.** Encoder, physiology fusion, dual-timescale memory,
contamination-safe update policy, calibration, longitudinal arm, episode state
machine. Each with the rule that selected it and the date that rule was frozen.

**3.4 Episode layer.** The frozen four-state protocol, no trainable parameters.

### 3.5 ★ The intelligent physical system — **new in V2**

Source: handbook §52 and §55, and `src/cardiosentinel/edge/`. **Write from code.**

Four layers, each grounded on the one below:

```
Layer 4  AGENTIC          Evidence · Explanation · Research · Architecture agents
Layer 3  EVIDENCE         AlertEvent -> EvidenceRecord -> EvidenceGraph
Layer 2  EDGE RUNTIME     StreamingInferenceSession, five pieces of causal state
Layer 1  SIGNAL           StreamingPreprocessor -> CausalWindowGenerator -> 146-d
```

- **3.5.1 The representation bridge, and why it was the only real unknown.**
  For the whole research phase no module imported both halves: the signal path
  ended at `CausalWindow`, the model chain began at a precomputed 16 GB corpus.
  `edge/representation.py` joins them. **The composition was proven, not
  asserted** — physiology half **bit-exact** (`0.000e+00` on 64 of 64 audited
  rows), embedding half within **6 ULP** of float32 (max `7.15e-07`, median 2.5
  ULP). **The asymmetry is the evidence**: the physiology half goes through no
  reduction, so its exactness shows the inputs are identical and the residual is
  kernel jitter rather than a data-path divergence.
- **3.5.2 One implementation of each decision rule.** The M2 causal order was
  *extracted* from `m2_policy.replay_stream` into `m2_policy.step` rather than
  reimplemented, with byte-identical evidence over 300 real corpus rows
  (`sha256 8830a2e1…`) and 555 M2 tests. **A runtime that reimplements the
  research path is a second system, and its agreement is a coincidence rather
  than a guarantee.**
- **3.5.3 What the simulation is.** `~61×` real time on a laptop CPU (1079
  windows of `s20201` in 89 s wall); encoder benchmark on the fixed host, median
  `4.161` ms/window, p95 `4.337` ms, peak RSS `~305` MB. **The permitted phrase
  is *"laptop-based edge simulation using streaming physiological replay"* and
  nothing more.** A laptop is not edge hardware; Appendix A claim 5 stands and
  RQ5 remains open.
- **3.5.4 Two refusals that shape what may be claimed.** Only the twelve
  validation subjects are replayable, because T1 thresholds are
  leave-one-subject-out and every other record has no validated operating point
  — the runtime **refuses** rather than borrowing the nearest. And the stream
  must use the raw identity profile, because the frozen corpus is
  `processing_profile: raw` and a band-pass would shift every embedding
  silently; `require_raw_profile` makes that fail loudly.
- **3.5.5 Patient identity, again.** `subject_id` selects a state namespace and a
  calibrator. **It is never a model input**, and `t1_protocol.next_state` still
  never reads `row.stable_id`.

## 4. ★ Evidence framework — **the contribution**

The section the paper exists for. Written **from code**, with file and symbol
references, not from prose about the code.

- **4.1 Leakage controls as executable constraints.** The 15-entry deny list,
  the 9-entry allow list, and the design decision that makes them interesting:
  `stable_id` is *in* the allow list and the transition never reads it. Both
  halves stated together.
- **4.2 One-shot access semantics.** What a consumed budget is, why a spent flag
  is not a live permission, and why the re-run guard is the persistence claim
  rather than the flag. **All fifteen budgets are spent.** The fifteenth — the
  neural sealed test — was consumed on 2026-08-25, and the way it was consumed
  is the section's best material: an authorization signed against a **named
  architecture**, an evaluator that was bound to the architecture selection had
  **rejected**, and the mismatch caught by reading the entry point rather than
  by any test. Handbook §43.2.
- **4.3 Pre-registration at execution time.** Plan merged, then generator run,
  then report opened as a separate change — enforced by ordering, not by
  intention.
- **4.4 Negative capability.** Zero-capability counters, and the argument that
  proving what a run *did not do* is a different and stronger claim than
  testing what it does.
- **4.5 Digest-bound provenance.** Artifact digests, environment lock, tracked
  generators, immutable run directories.

### 4.6 ★ The claim boundary as executable code — **new in V2**

Source: handbook §53, `src/cardiosentinel/agents/claims.py`. **The strongest new
material in the paper.**

Appendix A lists **twenty-five** forbidden claims. Through v1.3 it was a
document a human was expected to remember. **Eighteen of them are now
word-anchored patterns** and `enforce()` raises rather than returning prose that
breaks one.

```
Evidence -> Context (four closed sections) -> Generator -> Claim guard -> Output
                                                              |
                                                 fails -> deterministic fallback
```

Three properties the section must state together, because any two without the
third would be misleading:

1. **It is lexical, not semantic.** It catches *outperforms · deployment-ready ·
   early detection · generalizes to · statistically significant · externally
   validated · false alarms per hour · conformal prediction*, and it **cannot**
   catch a novel sentence that means the same thing. It reduces the failure
   rate; it does not make overclaiming impossible, and **no sentence in the
   paper may imply otherwise**.
2. **Word anchoring is not optional.** A substring check for *"proved"* matches
   *"improved"* and *"Provenance"*, which has bitten this repository roughly ten
   times.
3. **It cannot be run as a gate on human-authored prose, and that is not a
   defect.** Running it over handbook §52–§56 reports **twelve violations, every
   one of them a quotation** — the document that defines a boundary must state
   the boundary. This is why the exemption is a caller-declared `quoting=`
   argument rather than a global suppression list: a document-wide exemption
   would silence the guard exactly where prose is most likely to overclaim.

**4.6.1 The evidence graph is the substrate, and the boundary is structural.**
35 nodes / 39 edges per alert. **Node kinds and edge relations are closed
vocabularies** — adding `"probably_caused"` raises. Each *"does not establish"*
is a `constraint` node joined by `bounded_by`, so a model reading the graph sees
the boundary **as evidence** rather than as trailing prose it may summarise away,
and `s_t` carries `is_calibrated_probability: false` in its own node so Appendix
A claim 9 cannot be inferred from the substrate.

**4.6.2 Grounding by curation, not by retrieval.** The research assistant
answers from six curated evidence objects, verified in CI against the merged
reports. It never reads a `_V1` document at runtime, never embeds one, never
searches, and **refuses** an uncovered or ambiguous question. The section should
use the router rejection as the case: a plausible summary would say *"utility
gain insufficient."* The frozen record says the **calibration-agreement guard
passed** at `0.006683691656635168` against a frozen tolerance of `0.02`, and
what failed was the **asymmetric-abstention guard** — an escalation ratio of
`6.453604523726777` against a limit of `3.0` fixed in advance. **Raw document
access lets a model paraphrase that badly; invented placeholders get it wrong.**

**4.6.3 What the guard does not establish.** That the explanations are
*correct*. They are **grounded** — every value traces to a frozen artifact —
which is a different and weaker property than being clinically meaningful.

**What sections 4 and 4.6 must resist.** They are the most flattering material
in the paper and they are about machinery, not results. Every claim in them is a
claim about process. **They license nothing in section 7.**

## 5. ★ Failure and recovery — **exceptional material**

- **5.1 The stage-24 failure.** The canonical T1 attempt failed **post-claim**.
  Zero locks, which is correct — a lock would mean it completed.
- **5.2 Why the attempt was consumed anyway.** The semantics that make this a
  cost rather than a do-over.
- **5.3 The authorized recovery.** A single-use continuation under a recorded
  authorization, completing in ten seconds and running no model.
- **5.4 The near-miss inside the recovery.** The continuation's first launch
  raised a `TypeError` *before* the claim point, so the attempt was not consumed
  and the authorization survived. **Do not present this as a system working
  well.** It is the same defect class that consumed the canonical attempt:
  stages tested, junctions not.
- **5.5 Refuted predictions.** Two registered W1 predictions were wrong — one
  mechanism claim, one aggregate expectation — and both were reported as
  written.

### 5.6 ★ Nine boundaries the guards caught in our own code — **new in V2**

> **Amendment, 2026-08-25.** This section was written at five and is now
> **nine**: the explanation layer added four, each found by a failure the gates
> already in place had passed. They are a different finding from the five below
> and the draft keeps them in a separate part. Drafted as
> `PAPER_S5_6_CLAIM_BOUNDARY_DRAFT.md`; sources are handbook §53.2 **and
> §53.2.1**.

Source: handbook §53.2. **Short, and the best evidence in the paper that the
guard is load-bearing rather than decorative** — better evidence than any test
written for it, because none of the five was written to demonstrate it.

| # | Component | What tripped it |
|---|---|---|
| 1 | Evidence Agent (#84) | its own disclaimer *"does not establish a diagnosis"* |
| 2 | Explanation template (#86) | its closing sentence, same claim |
| 3 | Research Assistant (#87) | `claims_forbidden`, which states forbidden claims **in order to prohibit them** |
| 4 | Demonstration console (#93) | `textwrap` split the canonical disclaimer across two lines, so the literal exemption stopped matching and a **correct** output was flagged |
| 5 | Evaluation report (#94) | its **reporting rules**, which prohibit a claim by naming it |

**The fourth is the one to lead with.** The first three are one limitation seen
three times: a lexical guard cannot tell an assertion from a disclaimer. The
fourth is a different and worse defect — **the guard accepted unwrapped prose
and rejected the *identical* wrapped prose, so its exemption was defeated by
presentation.** Any rendered output would have hit it.

**Every fix was structural, and the section must say why.** A registered
disclaimer, a caller-declared `quoting=`, whitespace normalisation, a
test-scoped exemption. **Rewording around the guard would have taught authors to
avoid stating boundaries plainly, which is the exact opposite of the intent** —
and that, not the catch rate, is the finding.

## 6. Experimental setup

Retention decisions, metric hierarchy, and the two metrics that v1.1 specified
and that were **never computed** — false alarms per hour and temporal IoU. That
gap is reported, not glossed, and the corresponding claims are forbidden
(Appendix A claim 21).

## 7. Results — **one row added since V1, and where it came from is the point**

Reported in the order the evidence was produced, each with its boundary inline
rather than deferred to section 8. **Nothing in #82–#94 altered a single figure
in this table**; a reader should be told so explicitly, because a paper that
adds a runtime and reports new numbers in the same revision has not shown that
the runtime changed nothing.

**V1 said this section was unchanged, and that was the claim. It is now one row
longer.** The B4-B sealed test was authorized and executed once on 2026-08-25,
and the row below is its result. What has *not* changed is §9: the discussion
was drafted before the test opened and no thesis in it moved afterwards. That
ordering is checkable in the history, which is why it was done that way.

| | Reported | Boundary that travels with it |
|---|---|---|
| T1 | subject-macro `episode_f1` 0.2524, 95% [0.0826, 0.4415] | seven of twelve zero, for two incomparable reasons that push the operating point in opposite directions |
| T2 | difference 0.093215, 95% paired **[-0.015229, 0.148951]** | **includes zero**; the difference **is** the selection rule; scores uncalibrated; subject-macro is a mean over **9 of 12** subjects |
| U1 | router **rejected**; Platt retained | split retention; edge/cloud routing does not exist |
| W1 | difference 0.1921, 95% paired **[0.0505, 0.3455]** | **excludes zero**; bounded at one operating point selected with the state machine in the loop |
| **B4-B sealed test** | pooled AUPRC **0.0935334** at prevalence **0.0460529**; subject-macro AUPRC **0.354901**, 95% **[0.033058, 0.239284]** | **one attempt, twelve subjects, one dataset, and nothing to corroborate it against.** Subject-macro discrimination is a mean over **8 of 12** — four test subjects are single-class and are excluded rather than scored 0 or 1. The MCC interval **[-0.033876, 0.221346]** includes zero. Threshold **0.8329097628593445** came from validation, `test_informed: false`. Scores are **uncalibrated sigmoid outputs, not probabilities** |
| External validation | **no independent cohort exists** | a finding about the public record, not a gap awaiting effort. The one candidate route, EDB `overlap_clean`, was **declined in writing** on 2026-08-24 — so this is now permanent for this paper rather than pending |

**Two research questions are answered — one negatively, one affirmatively and
bounded. Four remain open and every one needs a run.** RQ4 is *"Supported
(bounded)"*, never bare *"Supported"*. **The sealed-test row answers none of
them**: it characterises the selected encoder on held-out subjects and is not an
arm of any comparison.

### 7.5 Reporting the sealed test — the pre-registered form — **new**

§6.4 of `B4_TEST_AUTHORIZATION_V1.md` fixed how this number would be reported
**before** it existed. The commitment, not paraphrased:

- **Registered primary is pooled-window AUPRC.** It leads. Everything else is
  secondary.
- **Every subject-macro figure carries its denominator.** AUPRC, AUROC, balanced
  accuracy, MCC and sensitivity are over **8 of 12**; F1, NPV, PPV and
  specificity are over 12 of 12. **Never quote one without saying which.** This
  is the §9.2 denominator finding recurring in the final evaluation, and it was
  pre-registered precisely because it had already happened in T2.
- **Intervals are 1,000 subject-bootstrap replicates at seed 2026**, 1000/1000
  successful, 0 undefined.
- **Challenge strata are secondary and bounded**: rate-related FP fraction
  0.2292818 (4 subjects), axis-shift 0.0389143 (8 subjects). Conduction-change
  — 8 of 10 windows in **one** subject — is **exploratory and descriptive, never
  bootstrapped and never headlined.**
- **Score semantics stated every time:** uncalibrated sigmoid model score.

**The reason to print the commitment beside the number** is that a reader cannot
otherwise distinguish a boundary chosen before the result from one chosen after
it, and those are different claims.

### 7.6 System behaviour — measurements, not findings — **new in V2**

**These belong in the paper and they are not results in the sense of §7 above.**
The section must be titled so a reader cannot mistake one for the other.

- **The end-to-end demonstration is contracted before it is run.**
  `DEMO_SCENARIO.md` fixes the expected outcome; `s20201` at 2400 s yields
  **exactly 1** alert opening at `00:17:05`, held **640 s** across **129**
  windows, peak calibrated probability **0.545613**, gates `G1 PASS G2 PASS G3
  PASS G4 BLOCK G5 BLOCK G6 PASS`, **0** memory updates admitted, explanation
  mode `DETERMINISTIC`.
- **`0` admitted is the control working, not a fault.** The contamination gate
  admits only windows that look normal and outside a 60 s refractory; G5
  dominates, since any above-threshold window arms 60 s while windows arrive
  every 5 s. **A reviewer will ask, so it belongs here rather than in a
  discovery.**
- **A reproduced null is the strongest single piece of composition evidence.**
  Replaying `s20591` for an hour produces **zero alerts**, reproducing the
  published result that s2059 is one of the four missed subjects — 47 reference
  episodes, **0** predicted runs. **The live runtime firing zero times is
  evidence the composition is faithful.**
- **The explanation evaluation (#94) reports an unexercised arm in the table.**
  Deterministic arm: fidelity **1.000**, claim violations **0**, completeness
  **1.000**. Generative arm: **`NOT EXERCISED` — no provider configured**,
  printed in the provider row rather than hidden in a footnote. The harness is
  validated against deliberately bad stub providers. **No winner is declared and
  neither arm is described as better**; the protocol forbids it.

## 8. Limitations

Quotable near-verbatim from existing documents. **The publication claim boundary
is the authoritative list and should be cited rather than paraphrased** — and
the paper should note that it is now also executable, which makes §8 the one
limitations section in the literature that a reader can run.

## 9. Discussion — **drafted**

> **Amendment, 2026-08-25.** §9 is drafted in `PAPER_S9_DISCUSSION_DRAFT.md`.
> §9.3, stubbed here pending the literature search, is written. **§9.5.5 is new
> and is not in the plan below** — the checks-that-pass-for-the-wrong-reason
> pattern, now at ten instances.

**9.1 Why this is a methodology paper.** The honest version: the results are
modest, the one architectural contrast spans zero, and the affirmative answer is
bounded by an operating point chosen with the thing under test already in the
loop. **A performance framing would require experiments that are not merely
unfunded but, for external validation, not currently possible** — no cohort
exists. The methodology framing is not a consolation prize; it is the accurate
description of where the effort went.

**9.2 The finding that generalises: denominators.** Three headline numbers, from
three experiments, using three different metrics, each concealed a denominator
that was not what it looked like — and in every case the arithmetic was correct
and the metric signalled nothing. **The recommendation the paper should make:
report the contributing-unit count beside every population-level scalar, as a
matter of course.** This is the one section a reader outside cardiology can use
directly, and it should be written for them.

**9.3 What a rejection is worth.** The selective router was built, evaluated
against a prespecified gate, and rejected. Literature in that area
overwhelmingly reports adoption. **Discuss the publication incentive that
produces that asymmetry**, and what it costs the field — carefully, without
implying bad faith by other authors.

**9.4 When pre-registration is wrong.** W1's registered reasoning was half false
and its aggregate prediction was refuted. **Pre-registration does not make
predictions correct, it makes them checkable**, and a programme that only ever
reports confirmed predictions has not demonstrated the difference.

### 9.5 ★ What a machine-checked claim boundary actually taught us — **new in V2**

**The required new subsection, and the one a reader is most likely to take
away.** It is about §5.6's five findings, and it must argue from them rather
than restate them.

- **9.5.1 The authors were the offenders, every time.** Five components, built
  weeks apart under different reasoning, each tried to **state a boundary** and
  each tripped the guard. Not one was a case of a model overclaiming. **The
  people who wrote the boundary were the ones who kept breaking it**, which is
  the argument for machine checking that no amount of care substitutes for.
- **9.5.2 A guard defeated by presentation is a distinct failure class.** #93's
  finding is the one to develop at length. Wrapping is not a semantic operation
  and no author would think to test it, yet it inverted the guard's verdict on
  identical content. **The general form: any exemption matched against a surface
  form is a bug waiting for a renderer.** This generalises well past claim
  guards — to secret scanners, licence detectors, and content filters — and the
  paper should say so plainly.
- **9.5.3 Fixing a guard by rewording is a governance failure, not a fix.** All
  five were resolved structurally. **The tempting fix — reword until the guard
  is quiet — trains authors to stop stating boundaries plainly**, so the guard
  gets quieter as the prose gets worse. The section should name this incentive
  explicitly, because it is the mechanism by which well-intentioned automated
  checks corrode the writing they are meant to protect.
- **9.5.4 The guard caught itself, and the boundary applies to this paper.**
  Running it over the handbook's own governance sections reports twelve
  violations, **every one a quotation**. The honest statement is that the tool
  cannot police the document that defines it, and the exemption is therefore
  declared per caller rather than globally. **A paper claiming otherwise would
  be making exactly the kind of claim its Appendix A forbids.**

**9.6 The cost, stated plainly.** **A reader deciding whether to adopt this
apparatus deserves the bill, not just the benefits.**

**The volume, re-measured.** As of `origin/master` `a8f1b47`, `docs/` holds
**20,529 lines against 68,100 lines of source** — **one line of governance prose
for every 3.32 lines of code** — across **45 versioned protocol, decision, plan,
amendment and report documents** out of 67 in the directory.

**The direction of travel is the finding, not the ratio.** V1 measured 16,517
against 63,330 at `d5a86ce`, a ratio of **3.83**. Removing V1's own 298 lines
from the current count, so that neither figure includes a paper outline, gives
**3.37**. Between those two commits **the documentation grew 22.5% while the
source grew 7.5%** — the governance prose grew three times faster than the code
it governs.
**That is uncomfortable and it is the honest figure**; understating it would
read as defensive. *(Both figures are pinned deliberately: this outline lives in
`docs/` and would otherwise count itself.)*

**The largest single line item is still the stage-24 recovery, and it is still
the most instructive.** A canonical attempt was consumed and **not retried**.
Re-measuring work the machine had already computed once cost a **625-line
amendment**, **nine new modules totalling 3,165 lines**, **five test files**, and
a **separate human authorization**. Under a conventional regime it would have
been an afternoon's re-run. **This is where the discipline hurt most, and it was
still right** — but the paper has to show the size of the bill before that
sentence means anything.

**A case where the discipline withheld a better number.** U1's pre-registration
fixed four degeneracy statistics. Once the values were visible it was obvious
that the one that told the story — share of mass in the heaviest bin — was not
among them. **It was recorded as a limitation and not added**, because choosing a
statistic after seeing the values is what the pre-registration existed to
prevent. The report is worse than it could have been, deliberately.

**A case where over-restriction actively produced a worse report.** The first T2
execution resolved a conflict between two plan sections by **silently dropping
both arms' absolute AUPRC**, and the same instinct dropped 17 metric keys across
3 strata and 2 arms. That omission removed the scale a reader needs to interpret
a difference of 0.093215 — and it **concealed that the subject-macro figure was a
mean over 9 of 12 subjects.** An amendment reversed it. **The failure mode was
not slowness; it was a silent, unregistered reporting decision taken at execution
time — precisely what pre-registration exists to prevent, produced by the
discipline's own over-caution.**

**New in V2 — the cost of composing rather than rewriting.** The IPS layer is
**4,731 lines across 22 modules** in `edge/` and `agents/`. **The expensive part
was not writing it**; it was proving that it changed nothing — a 64-row ULP
audit against the frozen corpus, byte-identical M2 evidence over 300 rows, and a
reproduced null result on a missed subject. **A cheaper composition would have
been a second system whose agreement with the first was a hope.**

**This section must not end by arguing the cost was worth it.** Its power is
that it declines to. If the line items do their work the reader reaches that
conclusion unaided; the moment the section reaches for it, it becomes advocacy
and loses the credibility it exists to buy.

**9.7 What we would do differently.** The stage-24 lesson — junctions, not just
stages. The U1 lesson — a pre-registration must name the statistic that carries
the story, not merely a plausible family of statistics. **And new in V2: an
exemption should be defined over normalised content, never over a surface form,
because the renderer is not part of the contract.**

**9.8 Future work, honestly scoped.** RQ1 and the S4D contribution both need
**re-scoring**, not derived analysis. External validation needs a cohort that
does not exist, or a reframing onto a different question. RQ5 needs real edge
hardware, and until it exists an edge-benchmark capability could only report
measurements and would have to **refuse** the readiness verdict. **The
generative explanation arm has never run against a real model, and the paper
must say that in the table rather than in a footnote.** **The sealed neural test was consumed on
2026-08-25, and no cohort exists to corroborate it.** That is now a permanent
property of this paper rather than a scheduling problem: the EDB `overlap_clean`
route was declined in writing on 2026-08-24, so the single one-shot result on
twelve subjects is the only test-set evidence there will be. §7 reports it with
its boundary inline; **§9 was written before it opened and does not move because
of it.**

## 10. Reproducibility — **the V1 blocker is closed**

**V1 recorded that the reproducibility package did not exist and called its
absence disqualifying for a paper whose contribution is auditability. It exists
now.** A **committed 1.63 MiB demo bundle** (#90) plus one PhysioNet record
reproduces the contracted scenario in three commands, and usability tests (#91)
assert that it *runs*, not merely that it hashes correctly.

Environment lock, artifact manifest, restore procedure, tracked generators.
**The restore procedure must replay mtimes**, because immutability here is
asserted in terms of file times and object storage assigns its own.

**Reproducibility is not free at execution time either.** A tracked generator has
to reproduce its tracked document byte-for-byte, so every correction means a full
regeneration rather than an edit. The T2 report needed **five regenerations at
roughly nine minutes each**, two of them caused by defects in the generator
itself. **That cost is inherent to the guarantee, not a defect in it.**

**Two failure modes to record here rather than discover later:**

- **Integrity is not usability.** `.gitignore` silently dropped three
  demo-bundle checkpoints because `*.pt` matched them, and the integrity tests
  passed — **the manifest and the missing files agreed with each other.** Only
  executing the bundle caught it. **A manifest check cannot detect a file that
  was never staged.**
- **A preservation guarantee degrades silently.** An expired credential turns a
  verified backup into an unverified claim without anything failing, so the
  package needs a re-verification procedure with a date attached. The honest
  state when it cannot be run is *"not verified as of &lt;date&gt;"* — never
  verified, and never lost. The S3 evidence mirror is in exactly that state as
  of 2026-08-23, correctly scoped out of `CHECKSUM_MANIFEST.md`, and nothing
  depends on it.

---

## Writing order, and what now blocks it

1. **§4, §4.6 and §5, §5.6 first.** They are the contribution, the sources
   exist, and drafting them fixes the vocabulary the rest of the paper uses.
   **§5.6 is the paragraph to write first of all** — it is short, it is the best
   evidence the guard is load-bearing, and it sets up §9.5.
2. **§3.5 next**, while the code is fresh. It is assembly from §52/§55 and
   `edge/`, and it is the section most likely to drift into deployment language
   if written late.
3. **§9 third**, while §§4–5 are fresh — the section most likely to overclaim if
   written last against a deadline.
4. ~~**§2 last**, and only after an actual literature search.~~ **Done.** Its gap statement is
   the paper's sharpest claim and it must survive contact with the literature
   rather than be written to fit the contribution. **§2.5 is new and has no
   source material in the repository at all.**
5. §§1, 3.1–3.4, 6, 7, 8, 10 are assembly from existing documents.

**V1's blocker is closed.** The reproducibility package exists, is committed, and
is tested for usability rather than only for integrity.

~~**The remaining blocker is the literature search**, and it is not a resource
problem — it is that the gap statement in §2 cannot honestly be written until it
has been attempted.~~ **Closed 2026-08-25.** The search ran, §2 is drafted, and
§9.3 — which was stubbed pending it — is written. **Everything else in this
outline is writing, and none of it is building.**

---

## What this outline must not become

A paper that reads section 4's confidence into section 7's numbers. **The
machinery is complete, demonstrated, and now running; the findings are small,
bounded, or negative.** Both halves are true, they are separate claims, and the
manuscript has to keep them separate on every page.

**V2 adds a second failure mode to guard against.** The system is now visibly
impressive — it streams, it explains, it refuses. **None of that is a scientific
result, and §7 is identical to what it was before any of it existed.** A draft
that lets the runtime's competence colour the reading of a confidence interval
that includes zero has made exactly the error this apparatus was built to
prevent, and it will be a more persuasive error than the one V1 warned about.
