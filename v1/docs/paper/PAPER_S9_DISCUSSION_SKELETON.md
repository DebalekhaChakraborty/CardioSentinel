# §9 Discussion — writing skeleton

> **Draft scaffold, not prose and not a frozen record.** No `_V1` suffix, no
> digest, no freeze ritual. It converts `PAPER_OUTLINE_V2.md` §9 from directives
> into checkable claims, each with its evidence and its prohibition, so that the
> prose can be written against a structure rather than improvised.
>
> **It was written with no sealed-test result in existence, and it assumes
> none.** §9.8 stated what must happen if B4 were ever opened. **B4 was opened
> on 2026-08-25**, and §9.8 has now been executed to the letter: the number went
> into §7, one sentence went into §9.1, and nothing else moved. The value of
> this document is that the ordering is checkable in the history rather than
> promised in a sentence.

| | |
|---|---|
| Source | `PAPER_OUTLINE_V2.md` §9 |
| Written against | `origin/master` `1018001` |
| Hard dependency | **§5.6 must be written first** — §9.5 argues from it |
| Status | scaffold; every subsection is UNWRITTEN |

---

## 0. Order, and one warning

`PAPER_OUTLINE_V2.md` sets the order: **§5.6 first**, §3.5 second, **§9 third**,
§2 last. This skeleton is being prepared third-in-line by that rule, and §9.5
cannot be finished until §5.6 exists — it must *argue from* the five findings,
not restate them.

**The warning the outline gives about this section:** §9 is *"the section most
likely to overclaim if written last against a deadline."* Writing it now, before
the last number exists, is the point. A discussion drafted after seeing a test
result is a different document, and everyone involved will be able to tell.

---

## 9.1 Why this is a methodology paper

**THESIS.** The performance framing is unavailable — not unfunded, unavailable —
and the methodology framing is the accurate description of where the effort
went, not a consolation prize.

**EVIDENCE.**
- The one architectural contrast spans zero: T2 paired subject-bootstrap
  interval **[-0.015229, 0.148951]** on a point difference of **0.093215**.
- The affirmative answer is bounded: RQ4 reads **"Supported (bounded)"**, never
  unqualified, because both W1 arms ran at thresholds selected with the thing
  under test already in the loop.
- External validation is not merely undone but **not currently possible** —
  `EXTERNAL_VALIDATION_STRATEGY_V1.md` audited the field and found no drop-in
  independent cohort.

**THE ONE PERMITTED ADDITION, under §9.8 clause 2.** One sentence recording that
a sealed-test characterisation of the selected encoder now exists — executed
once on 2026-08-25, after this section was drafted, reported in §7 with its
boundary, and corroborated by nothing because no cohort exists to corroborate
it. **That is the whole of what may be added here.**

**MUST NOT SAY.** That the modest results are *why* the paper is methodological.
The causality runs the other way and a reader will catch the inversion. **Nor
anything at all about whether the sealed-test number is good or bad**, or what
it implies — §9.8 clause 1 forbids revising a thesis, hedge or emphasis in
light of it, and clause 3 says the argument does not change either way.

**STATUS.** Unwritten. Ready to write — all three evidence items are published,
and the §9.8 addition is now determined rather than contingent.

---

## 9.2 The finding that generalises: denominators

**THESIS.** Report the contributing-unit count beside every population-level
scalar, as a matter of course.

**EVIDENCE.** Three headline numbers, three experiments, three different
metrics, each concealing a denominator that was not what it looked like — and in
every case **the arithmetic was correct and the metric signalled nothing.** The
subject-macro AUPRC that was a mean over **9 of 12 subjects** is the clearest
instance.

**AUDIENCE NOTE.** The outline is explicit that this is *"the one section a
reader outside cardiology can use directly, and it should be written for them."*
Write it so it survives being read by someone who skips §§4–7 entirely.

**MUST NOT SAY.** That this is novel. It is a discipline recommendation, and
claiming novelty for it invites a reviewer to find prior art that exists.

**STATUS.** Unwritten. Needs the three instances enumerated with their pins.

---

## 9.3 What a rejection is worth

**THESIS.** The selective router was built, evaluated against a **prespecified**
gate, and rejected; the literature in that area overwhelmingly reports adoption,
and the asymmetry is a publication incentive rather than a fact about routers.

**EVIDENCE.** `U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` — split
retention, router rejected, gate fixed in advance.

**MUST NOT SAY.** Anything implying bad faith by other authors. The outline flags
this explicitly. The claim is about what gets published, not about who is honest.

**BLOCKED ON.** §2 literature search. The asymmetry claim is quantitative in
shape and cannot be asserted without having looked.

**STATUS.** Unwritten, and **not yet writable** — this is the one §9 subsection
gated on §2.

---

## 9.4 When pre-registration is wrong

**THESIS.** Pre-registration does not make predictions correct; it makes them
**checkable**. A programme that only ever reports confirmed predictions has not
demonstrated the difference.

**EVIDENCE.** W1's registered reasoning was half false and its aggregate
prediction was **refuted** — recorded as refuted in
`W1_WINDOW_COMPARATOR_REPORT_V1.md` rather than reinterpreted.

**MUST NOT SAY.** That refutation validates the method. It demonstrates the
method is capable of refutation, which is a weaker and defensible claim.

**STATUS.** Unwritten. Ready to write.

---

## 9.5 ★ What a machine-checked claim boundary actually taught us

**HARD DEPENDENCY: §5.6.** Do not draft this before §5.6 exists.

**9.5.1 — THESIS.** The authors were the offenders, every time. Five components,
built weeks apart under different reasoning, each tried to **state a boundary**
and each tripped the guard. **Not one was a model overclaiming.** That is the
argument for machine checking that no amount of care substitutes for.

**9.5.2 — THESIS.** A guard defeated by presentation is a distinct failure
class. `textwrap` split the canonical disclaimer across two lines; the literal
exemption stopped matching; identical content received an inverted verdict.
**General form: any exemption matched against a surface form is a bug waiting
for a renderer.** Develop at length, and generalise explicitly to secret
scanners, licence detectors and content filters.

**9.5.3 — THESIS.** Fixing a guard by rewording is a governance failure, not a
fix. All five were resolved **structurally**. The tempting fix trains authors to
stop stating boundaries plainly, so the guard gets quieter as the prose gets
worse. **Name the incentive explicitly** — it is the mechanism by which
well-intentioned automated checks corrode the writing they protect.

**9.5.4 — THESIS.** The guard caught itself. Run over the handbook's own
governance sections it reports twelve violations, **every one a quotation**. The
tool cannot police the document that defines it; the exemption is declared per
caller rather than globally. **A paper claiming otherwise would be making
exactly the kind of claim its Appendix A forbids.**

**MUST NOT SAY.** That the guard prevents overclaiming. It catches a lexical
class of it, in code the authors wrote, and §9.5.4 is the proof of its limit.

**STATUS.** Unwritten, blocked on §5.6.

---

## 9.6 The cost, stated plainly

**THESIS.** A reader deciding whether to adopt this apparatus deserves the bill,
not just the benefits.

**EVIDENCE — the volume.** `docs/` at **20,529 lines against 68,100 of source**,
one line of governance prose per **3.32** lines of code, across **45 versioned
documents** of 67.

**EVIDENCE — the direction of travel, which is the finding.** V1 measured
**16,517 / 63,330**, ratio **3.83**; excluding V1's own 298 lines gives **3.37**.
Between those commits **documentation grew 22.5% while source grew 7.5%** — the
governance prose grew **three times faster** than the code it governs.
*Uncomfortable, and the honest figure. Understating it would read as defensive.*

> **PIN TRANSLATION REQUIRED.** Both measurements are pinned to commits that the
> 2026-08-24 identifier migration invalidated. Per
> `COMMIT_PIN_TRANSLATION_V1.md`: **`a8f1b47` → `ff382d5`**, **`d5a86ce` →
> `ce984c9`**. Use the new SHAs in the manuscript and cite the translation table.
> Do not re-measure — the figures are correct; only the identifiers moved.

**EVIDENCE — the largest line item.** The stage-24 recovery: a canonical attempt
consumed and **not retried**, at a cost of a **625-line amendment**, **nine
modules totalling 3,165 lines**, **five test files**, and a **separate human
authorization**. Under a conventional regime, an afternoon's re-run. *This is
where the discipline hurt most, and it was still right* — but show the bill
before that sentence means anything.

**EVIDENCE — the discipline withholding a better number.** U1 pre-registered four
degeneracy statistics. Once values were visible, the one that told the story —
share of mass in the heaviest bin — was not among them. **Recorded as a
limitation, not added.** The report is worse than it could have been,
deliberately.

**EVIDENCE — over-restriction producing a worse report.** The first T2 execution
silently dropped both arms' absolute AUPRC and **17 metric keys across 3 strata
and 2 arms**, removing the scale needed to interpret a 0.093215 difference and
concealing the 9-of-12 denominator. An amendment reversed it. **The failure was
not slowness; it was a silent, unregistered reporting decision at execution
time** — precisely what pre-registration exists to prevent, produced by the
discipline's own over-caution.

**EVIDENCE — composing rather than rewriting.** The IPS layer is **4,731 lines
across 22 modules**. The expensive part was not writing it; it was **proving it
changed nothing** — a 64-row ULP table, tolerance `0.006683691656635168` against
a frozen `0.02`.

**MUST NOT SAY.** That the cost was worth it *in general*. The paper can say it
was worth it here, and give the reader the numbers to disagree.

**STATUS.** Unwritten. All figures published; two pins need translating.

---

## 9.7 ✚ NEW SUBSECTION — when the provenance layer itself failed

**Not in `PAPER_OUTLINE_V2.md`.** The events postdate it. **Accepted 2026-08-24.**
Included because §9.6
is the honest-cost section and this is a cost, and because §9.4's thesis —
checkable, not correct — generalises to the apparatus itself.

**THESIS.** An auditable system must be able to detect provenance uncertainty
**before** an irreversible decision, not after. On 2026-08-24 this one did, on
itself, and the sequence is the evidence.

**EVIDENCE.** `PROVENANCE_INCIDENT_V1.md` and `COMMIT_PIN_TRANSLATION_V1.md`
(merged as PR #102). A history rewrite changed 268 commit identifiers; **69
commits cited across 71 tracked files stopped resolving**; no file content, no
result, no digest and no behaviour changed. Repaired append-only, because
experiment locks are sealed by a self-referential digest and **cannot** be
corrected in place — B4-B's digest is registered in 28 files, including three
downstream protocol documents and five downstream experiment locks.

**THE CHRONOLOGY IS THE ARGUMENT — state it with dates.**
1. Rewrite authorized and executed, cost stated as SHA churn.
2. Pins dangle. The rewrite's own checks — content identity, commit counts,
   contributors — **all passed and were all sound**. None asked what *referred
   to* the identifiers being replaced.
3. Detected in review, before any further irreversible action.
4. Two measurement errors made and corrected during that review, both of the
   same class: **a check that passed for a reason unrelated to what it claimed
   to verify.** One counted objects a local backup was keeping alive; one scanned
   markdown only and missed the load-bearing cases. A third finding — that a lock
   digest was corrupt — was raised and **withdrawn**: the digest was correct and
   the hashing input was wrong.
5. Repaired append-only. No frozen record edited. **B4 still sealed.**

**MUST NOT SAY.** That the system detected this automatically. It did not — a
human-directed review did, and the automated checks all passed. **That is the
finding**, and dressing it up as automated detection would be the precise
failure the paper spends §9.5 warning about.

**STATUS.** Accepted, unwritten. `PAPER_OUTLINE_V3` should carry it forward.

---

## 9.8 B4 contingency — **EXECUTED 2026-08-25**

> **This was a contingency and is now a record.** It was written while no
> sealed-test result existed. B4 was authorized under
> `B4_TEST_AUTHORIZATION_V1.md` and executed once on 2026-08-25, and the four
> clauses below were applied as written. What was added: the number, in §7, with
> its boundary inline (§7 and the new §7.5 of `PAPER_OUTLINE_V2.md`); and one
> sentence in §9.1. What moved: **nothing else.** The clauses stay in the
> present tense below, unedited, because a rule rewritten after the event it
> governs is no longer evidence that it bound anyone.

This document is drafted with **no sealed-test result in existence**. If B4 is
ever authorized and executed, the following are binding:

1. **Nothing above may be revised in light of the result.** Not a thesis, not a
   hedge, not an emphasis. A discussion rewritten after seeing the number is
   post-hoc reasoning, whatever it says.
2. **What may be added:** the number, in §7, with its boundary inline; and a
   sentence in §9.1 recording that a sealed-test characterisation exists.
3. **§9.1's argument does not change if the number is good.** A favourable
   result on 12 subjects with no corroborating cohort does not convert a
   methodology paper into a performance paper, and §5.2's limitations continue
   to apply verbatim.
4. **If the number is poor**, §9.1 gets stronger and no other section moves.

The purpose of writing §9 first is to make this checkable rather than promised.

**It is now checkable.** `PAPER_S9_DISCUSSION_DRAFT.md` and this skeleton were
merged in #105 on 2026-08-24. The sealed test was executed on 2026-08-25. Both
dates are in the history, and a reviewer can diff §9 across that boundary and
see for themselves that only the recording sentence in §9.1 was added.
