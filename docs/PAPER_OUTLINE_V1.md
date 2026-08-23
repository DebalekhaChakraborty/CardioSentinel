# CardioSentinel — Paper Outline, V1

**Scope of this document.** The manuscript skeleton in the Research Execution
Handbook lists ten sections and marks two as *"missing entirely"*: **§2 Related
Work** and **§9 Discussion**. Everything else has named sources and is either
complete or assemblable. This outline exists to close those two, and to fix the
argument the paper is making before anyone writes prose.

**It is an outline, not a draft, and it contains no citations.** Where a
citation is required it says so. Inventing one would be the same class of error
the programme's entire apparatus exists to prevent.

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
  a real post-claim failure and its authorized recovery; a measured pipeline
  with every boundary reported; and one methodological finding that generalises
  past ECG (§9.2).
- **"Causal" means temporal non-anticipation**, defined here and never used in
  the inferential sense.

## 2. Related work — **to be written**

Four bodies of work, each with the positioning claim the paper needs to make
against it. **Citations to be gathered; none are asserted here.**

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
that includes zero. **Section 3.3 describes the architectures; section 7
reports that the selection is a selection.**

**2.3 Reproducibility, pre-registration and result-blind analysis in ML.**
The closest methodological neighbours, including pre-registration practice
imported from clinical trials and psychology, and existing reproducibility
checklists. *Positioning, and this is the paper's sharpest claim:* checklists
record intent at submission time. **This work enforces the same properties at
execution time, from code, and produces artifacts that prove what did not
happen.** A checklist cannot demonstrate that no model was loaded; a
zero-capability counter written by the run can.

**2.4 Selective prediction, calibration, and deferral to a human or cloud.**
Background for the U1 component. *Positioning:* we implemented it, evaluated it
against a prespecified exit gate, and **rejected** it. The paper reports the
rejection as a result. Related work in this area overwhelmingly reports
adoption; a rejection is the contribution.

**Gap statement to close the section.** Each of these literatures reports
outcomes. None of them, as far as we are aware, ships the machinery that makes
the outcome checkable by a third party who does not trust the authors. **That is
the gap.** Whether "as far as we are aware" survives the literature search is
itself a finding, and the section must be written after the search, not before.

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

## 4. ★ Evidence framework — **the contribution**

The section the paper exists for. Written **from code**, with file and symbol
references, not from prose about the code.

- **4.1 Leakage controls as executable constraints.** The 15-entry deny list,
  the 9-entry allow list, and the design decision that makes them interesting:
  `stable_id` is *in* the allow list and the transition never reads it. Both
  halves stated together.
- **4.2 One-shot access semantics.** What a consumed budget is, why a spent flag
  is not a live permission, and why the re-run guard is the persistence claim
  rather than the flag. **Fourteen of fifteen budgets spent.**
- **4.3 Pre-registration at execution time.** Plan merged, then generator run,
  then report opened as a separate change — enforced by ordering, not by
  intention.
- **4.4 Negative capability.** Zero-capability counters, and the argument that
  proving what a run *did not do* is a different and stronger claim than
  testing what it does.
- **4.5 Digest-bound provenance.** Artifact digests, environment lock, tracked
  generators, immutable run directories.

**What this section must resist.** It is the most flattering section in the
paper and it is about machinery, not results. Every claim in it is a claim about
process. **It licenses nothing in section 7.**

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
  written. Paired with 5.4 this is the section's real argument: **the machinery
  is only demonstrated by the cases where it cost us something.**

## 6. Experimental setup

Retention decisions, metric hierarchy, and the two metrics that v1.1 specified
and that were **never computed** — false alarms per hour and temporal IoU. That
gap is reported, not glossed, and the corresponding claims are forbidden.

## 7. Results

Reported in the order the evidence was produced, each with its boundary inline
rather than deferred to section 8.

| | Reported | Boundary that travels with it |
|---|---|---|
| T1 | subject-macro `episode_f1` 0.2524, 95% [0.0826, 0.4415] | seven of twelve zero, for two incomparable reasons that push the operating point in opposite directions |
| T2 | difference 0.093215, 95% paired **[-0.015229, 0.148951]** | **includes zero**; the difference **is** the selection rule; scores uncalibrated |
| U1 | router **rejected**; Platt retained | split retention; edge/cloud routing does not exist |
| W1 | difference 0.1921, 95% paired **[0.0505, 0.3455]** | **excludes zero**; bounded at one operating point selected with the state machine in the loop |
| External validation | **no independent cohort exists** | a finding about the public record, not a gap awaiting effort |

**Two research questions are answered — one negatively, one affirmatively and
bounded. Four remain open and every one needs a run.**

## 8. Limitations

Quotable near-verbatim from existing documents. The publication claim boundary
is the authoritative list and should be cited rather than paraphrased.

## 9. Discussion — **to be written**

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

**9.4 When pre-registration is wrong.** W1's registered reasoning was half
false and its aggregate prediction was refuted. The discussion should make the
distinction explicit: **pre-registration does not make predictions correct, it
makes them checkable**, and a programme that only ever reports confirmed
predictions has not demonstrated the difference.

**9.5 The cost, stated plainly.** This apparatus is expensive. Six failure
records, fourteen consumed budgets, and roughly one merged governance document
per experiment. **A reader deciding whether to adopt it deserves the bill, not
just the benefits** — including the cases where the discipline blocked an
analysis that would probably have been fine.

**9.6 What we would do differently.** The stage-24 lesson — junctions, not just
stages — and the U1 lesson that a pre-registration must name the statistic that
carries the story, not merely a plausible family of statistics.

**9.7 Future work, honestly scoped.** RQ1 and the S4D contribution both need
**re-scoring**, not derived analysis. External validation needs a cohort that
does not exist, or a reframing onto a different question. **The sealed neural
test remains unopened and should stay that way until there is something to
corroborate it against.**

## 10. Reproducibility

Environment lock, artifact manifest, restore procedure, and the tracked
generators. **The restore procedure must replay mtimes**, because immutability
here is asserted in terms of file times and object storage assigns its own.

---

## Writing order, and the one blocker

1. **§4 and §5 first.** They are the contribution, the sources exist, and
   drafting them fixes the vocabulary the rest of the paper uses.
2. **§9 second**, while §4 and §5 are fresh — it is the section most likely to
   drift into overclaiming if written last against a deadline.
3. **§2 last**, and only after an actual literature search. Its gap statement is
   the paper's sharpest claim and it must survive contact with the literature
   rather than be written to fit the contribution.
4. §§1, 3, 6, 7, 8, 10 are assembly from existing documents.

**Blocker:** the reproducibility package (§10) does not exist yet, and its
absence is disqualifying for a paper whose contribution is auditability. It
should be built before submission, not before drafting.

---

## What this outline must not become

A paper that reads section 4's confidence into section 7's numbers. **The
machinery is complete and demonstrated; the findings are small, bounded, or
negative.** Both halves are true, they are separate claims, and the manuscript
has to keep them separate on every page.
