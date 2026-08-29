# §9 Discussion — draft prose

> **Draft for the manuscript.** Not a frozen record: no `_V1`, no digest.
> Written from `PAPER_S9_DISCUSSION_SKELETON.md` against `origin/master`
> `1018001`. **§9.3 was stubbed pending the §2 literature search. That search
> ran on 2026-08-25** — `LITERATURE_SEARCH_V1.md`, 65 queries, 393 hits — **and
> §9.3 is now written**, on the footing that record supports and no wider.
> §9.5.5 is new and argues from `PAPER_S5_6_CLAIM_BOUNDARY_DRAFT.md` Part B.
>
> **Written with no sealed-test result in existence.** §9.8 of the skeleton
> bound what could change here if B4 were ever opened: the number goes in §7, a
> single sentence goes in §9.1, and nothing else moves. **B4 was opened on
> 2026-08-25**, one day after this draft merged in #105, and that is exactly
> what happened — the sentence below marked *[added under §9.8 clause 2]* is the
> only change this document has taken because of it. Diff it across that date;
> the ordering is the claim.

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

A sealed-test characterisation of the selected encoder exists: it was authorized
in writing, executed once on 2026-08-25 after this section was drafted, and is
reported in §7 with the boundary that was fixed before it was produced; it
corroborates nothing and is corroborated by nothing, because the cohort that
would have done so does not exist. *[added under §9.8 clause 2 — this sentence
records that the number exists and does nothing else with it]*

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

## 9.3 What a rejection is worth

We built a selective router, fixed its exit gate before the evaluation, ran the
evaluation, and **rejected it**. The gate, the result and the retention decision
are recorded in `U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md`, and the
rejection is reported in §7 as a result rather than omitted as a dead end.

**The literature we compared it against does not appear to contain that move,
and the sentence needs its bound stated before its content.** A recorded search
(`LITERATURE_SEARCH_V1.md`, 2026-08-25) returned 77 records across the selective
prediction, calibration and deferral queries. Read at the level of title and
abstract, they describe methods that improve a risk–coverage curve, sharpen a
deferral rule, or extend the setting. **None of the 77 reports a selective
mechanism that was built, evaluated against a prespecified bar, and abandoned.**

That is a statement about what a search of three indices returned, at eight hits
per query, from metadata rather than full text. **It is not a claim about the
field**, and there are at least three ways it could be an artifact of the
instrument rather than of the literature:

- **Abstracts do not advertise abandonment even when papers contain it.** A
  negative ablation lives in §5 of a paper whose abstract describes what worked,
  and title/abstract matching cannot see it.
- **Relevance ranking rewards the affirmative.** The queries name techniques, and
  the eight best-ranked hits for a technique's name are papers that advance it.
- **A rejection is most likely to be reported inside an applied paper**, as one
  component that did not earn its place, rather than as the subject of a method
  paper. The search was aimed at method literatures.

**With that bound in place, the argument is still worth making, and it is
strongest when it is not about other authors.** The asymmetry is not evidence
that anyone concealed anything. It is a property of what gets written up: a
component that clears its bar becomes a contribution and a section; a component
that does not becomes a deleted branch, and no venue exists that would have
published it alone.

**We are not outside that incentive; we were merely constrained against it.**
Had the exit gate not been fixed in writing before the evaluation, and had the
decision not been required to land as a retention document, this project's most
likely account of the selective router is silence — not a false claim, just an
absent one, in a paper about something else. **The apparatus did not make us
more honest than other authors. It removed the option of quietly not
mentioning it**, which is the only difference we are entitled to claim.

**What the asymmetry costs the field is a denominator, and §9.2 is about
denominators.** A reader deciding whether to add selective routing to a clinical
pipeline can find many reports of routers that helped. They cannot find how many
were built and dropped, because that number is not written down anywhere — so
the published record answers *"can this work?"* while the question being asked is
*"how often does this work?"*. **Reporting a rejection is cheap, and it
contributes the one quantity the literature structurally cannot accumulate on
its own.**

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

### 9.5.5 The most repeatable finding: checks that pass for the wrong reason

*Argues from `PAPER_S5_6_CLAIM_BOUNDARY_DRAFT.md` Part B and from the incident
record. This is the subsection we expect to generalise furthest and it should be
written for a reader with no interest in ECG.*

Across this programme the same defect has now appeared **ten times, in ten
unrelated components, over the full life of the project**: a check that passed or
failed **for a reason unrelated to what it claimed to verify**, while reporting
exactly the result it was designed to report.

| # | The check | What it claimed | What it actually measured |
|---|---|---|---|
| 1 | a recorded digest beside an archived generator | that the generator is the one that produced the document | nothing — **no test asserted it**, and it was stale on `master` from the moment it first appeared |
| 2 | `git cat-file -t` on a commit pin | that the pin resolves | that a *local* `refs/original` backup keeps the object alive. **The count was wrong by two orders of magnitude** |
| 3 | a provenance pin scan | that ~50 files were affected | that ~50 **markdown** files were affected; a full scan of all tracked files found **71**, including the load-bearing source, test and lock files |
| 4 | `assert package_count == 335` | that the new provider adds no dependency | **which host the test ran on.** CI builds its own environment — 71 packages — so it could only ever hold on the development machine |
| 5 | the provider's contract tests | that the provider works against `transformers` | that it works against a fake shadowing `transformers` in `sys.modules`. Real API drift — `apply_chat_template` in 5.x — would pass unnoticed |
| 6 | the lifecycle validator's regression test | that no fabricated state is asserted | that the *fixture's* state matched the code's bug. **It certified the defect as correct** |
| 7 | a literature harvest reporting `22 queries, 161 hits, 0 failed` | coverage of a literature | reachability of an HTTP endpoint. The re-run with corrected query syntax shares **zero records** with it |
| 8 | the citation checker built for that search | that no citation was invented | that no citation carried an arXiv version suffix. It reported **38 of 61 unresolved**, and all 38 were correct |
| 9 | `test_real_model_execution_is_a_separate_unexecuted_manual_record` | that real-model execution stays separate from CI | that the string `"Status: NOT EXECUTED"` appeared in a file. **It passed for a day after the run happened**, while the document it guarded was false |
| 10 | `grep` for one registered disclaimer's literal text | whether that disclaimer was dead code | whether the *string* appeared in a second file. **An alias carried the value where the literal did not**, and the entry was in fact printed on every alert and stored as a graph node |

**The shape is always the same, and naming it is the contribution.** A check has
a *claimed* predicate — the sentence in the test name, the commit message, the
docstring — and an *operative* predicate, which is whatever the code actually
evaluates. The two are written at different moments by the same person, and
**nothing in any tooling we know of compares them.** Tests are asserted against
the operative predicate by construction, so a test cannot detect the gap; that is
what #6 demonstrates, where the test was the thing certifying the bug.

**Green is the dangerous state, not red.** Every instance above reported success
or an unremarkable number. #2 and #3 reported *smaller* problems than existed,
which is worse than reporting none: a plausible figure ends an investigation.
#7 reported `0 failed`, which is true of the network and says nothing about the
corpus. **A failing check invites inspection; a passing one closes the question**,
and these were all passing.

**Three of the ten were found by a human reading the output and finding it
absurd** — eight nonsense search hits, a package count that was obviously the
wrong machine's, a fifty-file estimate that felt low. **None was found by
another check**, and #9 is the sharpest case: it surfaced only because someone
corrected the *document*, at which point the test failed for the first time —
**the test detected the fix, not the defect.**

**#10 deserves its own sentence, because it nearly produced a worse outcome than
the defect it was investigating.** The grep was run to decide whether a stale
registered disclaimer was dead code and could simply be deleted. It reported one
occurrence, in the file that defines it. The entry was in fact aliased by
another module, printed to the user on every alert, and emitted as a constraint
node in the evidence graph — so *deleting* it would have removed a stated
boundary from user-facing output, which is the §9.5.3 failure exactly. **A check
that answers a narrower question than the one you asked is most dangerous when
its answer licenses an action**, and "is this dead?" is that kind of question. We take that seriously as a limit on the position this paper
argues: the apparatus makes claims checkable, and it does not make its own
checks correct.

**What we would recommend, stated as narrowly as we can defend it.** Where a
check exists to establish a property that matters, it should be **negatively
controlled at the moment it is written** — broken deliberately, and observed to
fail. Finding #4's replacement was: adding `accelerate` to the extra makes the
new assertion fail, and it was restored afterwards. That costs one minute and
would have caught #1, #4, #5 and #6 outright. It would not have caught #2, #3 or
#7, where the check worked exactly as written and the *concept* was wrong, and we
do not claim otherwise.

**The honest summary is uncomfortable and belongs in the paper.** This is a
project whose entire subject is making claims checkable, staffed by people
thinking about that problem full-time, and it produced ten of these — the last
four while writing the section you are reading, in the tooling built to keep
this section honest, and one of them found only by fixing something else.

**One counterweight is owed, because the section would otherwise read as though
no check ever works.** The reworded disclaimer that replaced #10's stale entry
was itself wrong on the first attempt: it spelled out the sealed test's
denominators and its interval, and those words are research prose, which must
never enter the closed context handed to the generator.
`test_the_context_carries_no_research_prose` failed, three files away from the
edit, for exactly the right reason. **That check's claimed and operative
predicates were the same, and it caught an author who had just spent a day
writing about authors who are caught.** **We do not think that is a statement about this project's
competence. We think it is the base rate**, and that most such checks in most
codebases have never been examined closely enough for anyone to notice.

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
with the physiology half **bit-exact at `0.000e+00` on 64 of 64 rows** and the
embedding half within **6 ULP of float32** (max `7.15e-07`, median 2.5 ULP).

> **Correction, 2026-08-28.** This paragraph previously reported the composition
> audit as *"passing at 0.006683691656635168 against a tolerance of 0.02"*. **That
> pair of numbers belongs to the U1 calibration-agreement guard**
> (`U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md`), not to the ULP comparison,
> and reached this draft by copy-paste from the router material above. The ULP
> figures are in `docs/paper/figures/README.md` §F1 and `PAPER_OUTLINE_V2.md`
> §3.5.1. **No frozen report was changed** — the error was local to this draft,
> and the manuscript never carried it: §3.6 of the submission candidate was
> written from the figures README and states the ULP values correctly.

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
