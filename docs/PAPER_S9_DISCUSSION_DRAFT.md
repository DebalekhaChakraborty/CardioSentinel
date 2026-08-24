# §9 Discussion — draft prose

> **Draft for the manuscript.** Not a frozen record: no `_V1`, no digest.
> Written from `PAPER_S9_DISCUSSION_SKELETON.md` against `origin/master`
> `1018001`. **§9.3 is stubbed and not written** — it is gated on the §2
> literature search, which has not started.
>
> **Contains no sealed-test result and assumes none.** §9.8 of the skeleton
> binds what may change here if B4 is ever opened: the number goes in §7, a
> single sentence goes in §9.1, and nothing else moves.

---

## 9.1 Why this is a methodology paper

The results are modest. The one architectural contrast we drew spans zero: the
paired subject-bootstrap interval on the S4D−GRU difference is
[-0.015229, 0.148951] around a point estimate of 0.093215. The one research
question we answered affirmatively, RQ4, reads *Supported (bounded)* and never
*Supported*, because both arms of the comparison ran at operating points selected
with the component under test already in the loop. Those are the headline
findings and we report them in that form throughout.

It would be conventional at this point to promise that a performance framing
awaits more compute, more data, or more time. That promise is not available here.
We audited the public record for a cohort on which this system could be
externally validated and found none. The European ST-T Database is the only other
ST-episode resource of comparable annotation depth, and it is not independent of
our training cohort: our recordings are Pisa-collection originals that EDB
excerpts, with ten record pairs individually verified and fifteen records
conservatively excluded. It is also structurally different — roughly two-hour
excerpts against our roughly twenty-four-hour recordings — so an evaluation on it
would be scored on a different task. STAFF III, the obvious alternative, fails on
five separate axes of our benchmark contract. **External validation of this
system is not merely unfunded; on the public record as it stands, it is not
possible.**

The methodology framing is therefore not a fallback chosen after the numbers
disappointed. It is the accurate description of where the effort went. What this
programme built, and what it can defend, is an apparatus for producing claims
that survive audit: pre-registered analyses, one-shot budgets that are spent
once, decisions recorded before values are read, and a claim boundary enforced in
code. The sections that follow report what that apparatus cost and what it
caught, including the several occasions on which it caught us.

> *Note for the writer: do not write that the modest results are why this is a
> methodology paper. The causality runs the other way — the methodology was the
> object of the work from the outset — and a reader will catch the inversion.*

---

## 9.2 The finding that generalises: denominators

If a reader takes one recommendation from this paper into a field other than
cardiology, we would like it to be this one: **report the count of contributing
units beside every population-level scalar, as a matter of course.**

We arrived at it the hard way. Three headline numbers, produced by three
different experiments using three different metrics, each concealed a
denominator that was not what it appeared to be. In every case the arithmetic
was correct, every intermediate value was recorded, and no metric signalled
anything wrong.

**A subject-macro mean that was not over the cohort.** T2's subject-macro AUPRC
is a mean over nine of twelve subjects. The evaluation artifact records three
non-contributing subjects for both arms — its own count, not a later derivation —
because the metric is undefined for them. A subject-macro figure quoted without
that denominator reads as an average over the cohort when it is an average over
the subset of the cohort for which the metric exists.

**An F1 denominator inflated by the arm under test.** W1's `episode_f1` has
denominator `predicted + reference`. Arm W's flood of predicted runs inflated it
without matching proportionally more episodes, and its score collapsed for
exactly the five subjects that actually score. Seven subjects scored zero on both
arms; the aggregate was driven by them, which is to say it was driven by the
subjects on which the comparison was uninformative.

**A binning diagnostic that looked healthy.** U1 pre-registered four degeneracy
statistics for its reliability curve: empty bins, bins under thirty rows,
smallest and largest. On the retained calibrator they read zero empty and one
sparse, which on its own describes a healthy curve. The concentration was visible
only by comparing the smallest and largest columns directly: **sixteen rows
against 398,513.** The four registered statistics were individually correct and
collectively silent.

The common structure is that a population-level scalar is a summary over a set,
and the identity of that set is not carried by the number. Reporting the count
alongside the value costs one column and makes the omission impossible. We have
no evidence this is novel — it is a discipline recommendation rather than a
discovery — but we found it three times in one programme while looking for other
things, which suggests the failure is cheap to make and hard to see.

> *Note for the writer: this section should be written for a reader who skips
> §§4–7 entirely. Do not require any cardiology to follow it, and do not claim
> novelty for it.*

---

## 9.3 What a rejection is worth — **NOT WRITTEN**

**Blocked on the §2 literature search, which has not started.**

The argument is available in outline: the selective router was built, evaluated
against a gate fixed in advance, and rejected; `U1_CALIBRATION_ROUTING_
RETENTION_DECISION_V1.md` records the split retention. The section's claim is
that literature in this area overwhelmingly reports adoption, and that the
asymmetry reflects a publication incentive rather than a fact about routers.

**That claim is quantitative in shape and cannot honestly be asserted before the
literature search is done.** It is the one subsection of §9 that is not writable
today. Writing it from impression would be the precise failure this paper spends
§9.4 and §9.5 describing.

When it is written, it must not imply bad faith by other authors. The claim is
about what gets published, not about who is honest.

---

## 9.4 When pre-registration is wrong

W1's registered reasoning was half false, and its aggregate prediction was
refuted.

The prediction reasoned about the seven subjects that score zero on both arms,
whose two failure modes push in opposite directions, and among those subjects it
held: Group A unchanged at zero, one Group B subject improved. It never
considered the five subjects that actually score, and those are the subjects that
determined the aggregate. The reasoning was sound about the part of the cohort it
examined and silent about the part that mattered.

We report this as refuted rather than reinterpreted, and the record says so. That
is the entire value of having registered it. **Pre-registration does not make
predictions correct; it makes them checkable.** A prediction that is only checked
when it succeeds is not a prediction, and a programme that reports only confirmed
predictions has not demonstrated that its predictions were registered at all.

The defect was in the pre-registered reasoning, not in the measurement. We think
that distinction is worth preserving in the literature: a registered analysis can
be wrong in its argument and still produce a correct and interpretable number,
and the two failures deserve different responses.

> *Note for the writer: do not write that refutation validates the method. It
> demonstrates the method is capable of refutation, which is weaker and
> defensible.*

---

## 9.5 What a machine-checked claim boundary actually taught us

*Depends on §5.6. Written against `PAPER_S5_6_CLAIM_BOUNDARY_DRAFT.md`, which
must be finalised first.*

### 9.5.1 The authors were the offenders, every time

Five components tripped the claim guard. They were built weeks apart, under
different reasoning, by authors who had all read the same claim boundary. **Not
one was a case of a model overclaiming.** In every instance the offending text
was an attempt to *state a boundary* — a disclaimer, a list of prohibited claims,
a set of reporting rules that named a claim in order to forbid it.

This is the argument for machine checking that no amount of care substitutes
for. The people who wrote the boundary were the ones who kept breaking it, and
each of them believed their own phrasing was self-evidently exempt. A guard that
only caught careless authors would have caught nobody here.

### 9.5.2 A guard defeated by presentation is a distinct failure class

The fourth finding is different in kind from the other three, and we develop it
because it generalises furthest.

The demonstration console passed the canonical disclaimer through `textwrap`,
which split it across two lines. The literal exemption stopped matching, and a
**correct** output was flagged as a claim-boundary violation. The content was
unchanged. Only the presentation differed, and the verdict inverted.

The general form: **any exemption matched against a surface form is a bug
waiting for a renderer.** The exemption was written by someone thinking about
meaning; it was evaluated against bytes; and something downstream was entitled to
change the bytes without changing the meaning. No author writing an exemption
would think to test line wrapping, and any rendered output would have hit it.

This is not specific to claim guards. Secret scanners, licence detectors and
content filters all decide about text that something else has already decided how
to lay out. We would expect the same defect to be latent in most of them.

### 9.5.3 Fixing a guard by rewording is a governance failure, not a fix

Each of the five had a cheaper resolution available: reword until the guard goes
quiet. We took the structural fix in all five cases — a registered disclaimer, a
caller-declared quoting flag, whitespace normalisation, a test-scoped exemption —
and the reason belongs in the paper rather than in a commit message.

**Rewording trains authors to stop stating boundaries plainly.** The guard exists
to keep the system from overclaiming; a fix that discourages writing disclaimers
makes the prose worse in exactly the dimension the guard was protecting. Worse,
it does so invisibly: the guard grows quieter as the writing degrades, and the
quiet is indistinguishable from safety.

We also considered and rejected regex negation detection — teaching the guard to
recognise *"does not"*. It would have replaced a visible, noisy failure mode with
an invisible one, and a guard that silently approves a real claim because it
resembles a denial is worse than a guard that noisily rejects a denial.

### 9.5.4 The guard caught itself, and the boundary applies to this paper

Run over this programme's own governance prose, the claim guard reports twelve
violations. **Every one is a quotation.** The tool cannot police the document
that defines it, and the exemption is therefore declared per caller rather than
granted globally.

We state this as a limit rather than working around it. A paper claiming that its
claim boundary is comprehensively enforced would be making precisely the kind of
unbounded claim its own Appendix A forbids.

> *Note for the writer: do not write that the guard prevents overclaiming. It
> catches a lexical class of it, in code the authors wrote, and §9.5.4 is the
> proof of the limit. Five catches is the number of boundary statements the
> authors happened to write, not a detection rate.*

---

## 9.6 The cost, stated plainly

A reader deciding whether to adopt this apparatus deserves the bill, not only the
benefits.

**The volume.** At the measurement commit, `docs/` held **20,529 lines against
68,100 lines of source** — one line of governance prose for every **3.32** lines
of code — across **45 versioned protocol, decision, plan, amendment and report
documents**.

**The direction of travel is the finding, not the ratio.** An earlier measurement
gave 16,517 against 63,330, a ratio of 3.83; excluding that outline's own lines
so neither figure counts a paper outline gives 3.37. Between those two points
**the documentation grew 22.5% while the source grew 7.5%**. The governance prose
grew roughly three times faster than the code it governs. That is uncomfortable
and it is the honest figure; understating it would read as defensive.

**The largest single line item.** A canonical experiment attempt failed after its
claim point and was **consumed rather than retried**. Re-measuring work the
machine had already computed once cost a 625-line amendment, nine new modules
totalling 3,165 lines, five test files, and a separate human authorization. Under
a conventional regime it would have been an afternoon's re-run. This is where the
discipline hurt most, and we still think it was right — but that sentence is
worth nothing until the size of the bill is on the page.

**A case where the discipline withheld a better number.** U1 pre-registered four
degeneracy statistics. Once the values were visible it was obvious that the
statistic which told the story — share of mass in the heaviest bin — was not among
them. It was recorded as a limitation and **not added**, because choosing a
statistic after seeing the values is exactly what the pre-registration existed to
prevent. The published report is worse than it could have been, deliberately.

**A case where over-restriction produced a worse report.** The first T2 execution
resolved a conflict between two plan sections by silently dropping both arms'
absolute AUPRC, and the same instinct dropped seventeen metric keys across three
strata and two arms. That removed the scale a reader needs to interpret a
difference of 0.093215, and it concealed the nine-of-twelve denominator discussed
in §9.2. An amendment reversed it. The failure mode was not slowness — it was a
silent, unregistered reporting decision taken at execution time, which is
precisely what pre-registration exists to prevent, produced here by the
discipline's own over-caution.

**The cost of composing rather than rewriting.** The intelligent-physical-system
layer is 4,731 lines across 22 modules. The expensive part was not writing it; it
was proving that it changed nothing — a 64-row unit-in-last-place comparison,
passing at 0.006683691656635168 against a tolerance of 0.02 frozen in advance.

> *Note for the writer: the two volume measurements are pinned to commits that
> the 2026-08-24 identifier migration invalidated. Per
> `COMMIT_PIN_TRANSLATION_V1.md`, `a8f1b47` → `ff382d5` and `d5a86ce` →
> `ce984c9`. Cite the new SHAs and the translation table. **Do not re-measure**
> — the figures are correct; only the identifiers moved.*
>
> *Do not write that the cost was worth it in general. The paper can say it was
> worth it here, and give the reader the numbers to disagree.*

---

## 9.7 When the provenance layer itself failed

An auditable system must be able to detect provenance uncertainty **before** an
irreversible decision, not after. This one did, on itself, and the sequence is
the evidence rather than the assurance.

On 2026-08-24 the repository history was rewritten to remove authorship trailers
from commit messages. The rewrite was authorized, executed once, and its cost was
stated in advance as identifier churn across 268 commits. File contents did not
change: every tree object is byte-identical before and after, and no result,
threshold, checkpoint or digest moved.

What was not anticipated is that the identifiers were load-bearing. This
repository records provenance by citing commit SHAs — in frozen records, in
protocol documents, in constants in the source tree, and inside experiment locks.
**Sixty-nine commits cited across seventy-one tracked files stopped resolving.**

The rewrite's own verification passed, and every check it ran was sound: content
identity confirmed, commit counts matched, the stated objective achieved. **None
of them asked what referred to the identifiers being replaced.** That is the
finding. A verification suite can be individually correct at every step and
collectively blind to the property that actually mattered — which is the same
shape as the denominator failures in §9.2 and the registered-reasoning failure in
§9.4, arriving in a third form.

The repair was append-only. Correcting the pins in place was not merely
inadvisable but arithmetically impossible: experiment locks are sealed by a
self-referential digest, so amending a recorded commit SHA inside a lock changes
the lock's own digest, and that digest is registered in twenty-eight places
including three downstream protocol documents and five other experiments' locks.
A translation table was published instead, carrying 326 exact mappings derived by
matching unchanged tree hashes, timestamps and subjects — a derivation any reader
can repeat without trusting the party that produced it. No frozen record was
edited. The sealed evaluation budget remained closed throughout.

Two measurement errors were made during the review that found this, and both are
recorded because they share one structure with everything else in this section:
**a check that passes for a reason unrelated to what it claims to verify.** The
first tested whether commits existed rather than whether they were reachable from
the published branch, and so counted objects that a local backup was keeping
alive. The second scanned documentation only, missing the source constants and
locks that turned out to be the load-bearing cases. A third finding — that a lock
digest was corrupt — was raised and then withdrawn: the digest was correct and the
hashing input was wrong, because the self-referential convention was undocumented
and had no executable check. It now has both.

> *Note for the writer: do not write that the system detected this
> automatically. It did not. Every automated check passed; a human-directed
> review found it. **That is the finding**, and presenting it as automated
> detection would be the exact failure §9.5 spends its length describing.*
