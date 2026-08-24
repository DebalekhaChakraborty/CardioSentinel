# External Validation Route A — Decision V1

**THIS IS A HUMAN GOVERNANCE DECISION, NOT A NEW SCIENTIFIC EXPERIMENT.**

It records a choice about which evaluations this programme will and will not
run. It computes nothing, reads no data, and changes no result.

| | |
|---|---|
| Decision | **Route A DECLINED** |
| Class | human governance decision |
| Data accessed | **none** — no EDB record was downloaded, opened, or evaluated |
| Artifacts modified | **none** |
| Authorizes B4 access | **no** — see §5 |
| Decided | 2026-08-24 |

## Documents this decision acts on

| Artifact | SHA-256 |
|---|---|
| `EXTERNAL_VALIDATION_STRATEGY_V1.md` | `d40c8dff391d8fcf4c0de674b7633768f8327f1370580a341c66c341d12fe1b7` |
| `B4_TEST_DEFERRAL_DECISION_V1.md` | `d34eeb0aa855d01f494011fa9d6843d4a517526565c47d5689f8ab1bc9d289c4` |
| `CROSS_DATASET_PROVENANCE.md` | `8e45b7dd4d51c4fc8c5f171dd3e8427f0cb56e6e39e73d02720498af646e7278` |

---

## 1. Decision

`EXTERNAL_VALIDATION_STRATEGY_V1.md` §5.1 identified four routes and §5.2
recommended **"Do A and D."** §5.4 recorded that the decision had not been made.

**Route A — the EDB `overlap_clean` secondary evaluation, 75 records, stratified
by cold-start bin — is DECLINED.**

This is a decline, not a deferral. No milestone reopens it automatically. It may
be revisited only by a new, explicitly argued governance decision, in the same
way this one was made.

**Route D — reporting the absence of an independent cohort as a finding about the
field — is retained and is now the whole of the programme's external-validation
position.**

---

## 2. Rationale

### 2.1 EDB `overlap_clean` cannot be claimed as an independent external cohort

`CROSS_DATASET_PROVENANCE.md` states the limit in its own words:

> *Neither cohort may be called fully independent external validation because
> independence of every remaining subject has not been proven.*

The contamination audit was done properly and is not in question. Our recordings
are Pisa-collection originals that EDB excerpts; ten record pairs were verified
individually; fifteen EDB records are conservatively excluded. **That exclusion
addresses *known* overlap. It does not establish that the remaining 75 records
are independent — only that no documented correspondence links them.** Absence of
a recorded correspondence is not evidence of independence.

A second consideration compounds it. EDB records are roughly two-hour excerpts
against our roughly twenty-four-hour recordings. For a system that carries state
across windows, that is not a cosmetic difference; T2 has already quantified how
much cold-start exposure matters. An evaluation on EDB would score a partly
different task.

### 2.2 Running it would not resolve the independence question

This is the operative reason. A Route A result would be a number on a cohort
whose independence remains unproven, and **running it would not make it any more
independent.** The question Route A was proposed to help with is not answerable
with the public record as it stands, and executing the evaluation does not move
it.

The cost was correctly assessed as low. Declining is not a resource decision.

### 2.3 The programme will not use it to strengthen generalization claims

Given §2.1 and §2.2, a Route A result could support no generalization claim this
programme is willing to make. **An evaluation whose result cannot be used is not
a cheap experiment; it is an invitation to use it anyway.** A secondary number,
once published, tends to be read as weak external validation regardless of the
caveats attached to it, and the caveat that matters here — unproven independence
— is precisely the kind that does not survive citation.

### 2.4 What this decline costs, stated plainly

§5.2 recommended A **and** D. Taking only D is a departure from that
recommendation and it costs something real:

- the programme forgoes its only available second-cohort measurement;
- **Route D becomes load-bearing.** The absence-of-cohort finding is now the
  entire external-validation content of the paper and must be written properly,
  as an audit of the field, not as an apology for the project;
- no future result of this programme, including any sealed-test result, will be
  corroborated on any second cohort. **This decision makes that permanent for
  this paper** rather than pending.

That last point is the honest cost and it is not small.

---

## 3. Impact on paper claims

| Claim | Status after this decision |
|---|---|
| External validation performed | **Forbidden.** None was performed, primary or secondary. |
| "Validated on a second cohort" | **Forbidden**, in any wording, including *secondary*, *supporting* or *preliminary*. |
| Generalization to other cohorts, sites or populations | **Forbidden.** Unchanged from Appendix A; this decision removes the only route that could have been read as softening it. |
| The absence of an independent ST-episode cohort | **Reportable as a finding**, sourced to `EXTERNAL_VALIDATION_STRATEGY_V1.md` §§2–4. |
| Any sealed-test result, should one ever exist | Remains **uncorroborated by any second cohort**, permanently for this paper. |

**§9.1 of the manuscript is strengthened and its wording must change.** It
currently argues that external validation *is not possible on the public record*.
That remains true, and it is now also true that the programme **considered the
one available secondary route and declined it on stated grounds.** The section
should say so: an audited decision is stronger evidence of discipline than an
unexamined absence, and a reader who discovers Route A existed will ask why it
was not taken. This document is the answer, and §9.1 should cite it.

**§9.3 is unaffected.** It remains blocked on the §2 literature search.

---

## 4. Future work

Recommended, none of it authorized here:

1. **Route B — STAFF III as a mechanism check, on its own terms.** 104 patients
   with gold-standard ischemia timing. It fails our benchmark contract on five
   axes and must not be folded into an external-validation milestone to make that
   milestone look complete. It is a good experiment wearing the wrong label:
   proposed separately, in its own protocol, answering *does the detector respond
   to known ischemia onset?* — a different and defensible question.
2. **Route C — new acquisition or clinical partnership.** The only route to
   genuine independence, and the only one that would let this system's
   generalization be tested rather than argued about.
3. **Revisiting Route A** is permitted only if the independence question changes
   — for example if record-level provenance for the EDB collection is published.
   A change in schedule, appetite or reviewer pressure is not such a change.

Any of these must satisfy `CROSS_DATASET_PROVENANCE.md` §5.3 before a waveform is
downloaded: provenance audit from release documentation and headers first; new
correspondences entered through the typed registry by reviewed update; confidence
levels never promoted by demographic similarity; and the evaluation pre-registered
before any value is read.

---

## 5. Scope limits — this does **not** authorize B4

`B4_TEST_DEFERRAL_DECISION_V1.md` remains in force. This document removes one
precondition and grants nothing.

Handbook §43.1 raised two objections to opening the sealed test. This decision
addresses only the first:

- **"A cheap reversible option is unspent."** Addressed. Route A is now decided.
- **"No cohort can corroborate a test number."** **Not addressed — and now
  permanent.** Declining Route A does not make the corroboration problem go away;
  it settles that it will not be solved for this paper.

A reader of this document should draw no inference about whether B4 should be
opened. That requires its own decision, separately argued and recorded before any
access, per `B4_TEST_DEFERRAL_DECISION_V1.md` §3.

| | |
|---|---|
| Route A | **DECLINED** |
| Route D | retained, and now load-bearing |
| EDB data accessed | **none** |
| B4 sealed test | **UNOPENED** |
| `TEST_ATTEMPT` | absent |
| Authorizes test access | **no** |
