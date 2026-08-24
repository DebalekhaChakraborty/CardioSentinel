# §5.6 — Five boundaries the guard caught in our own code

> **Draft prose for the manuscript.** Not a frozen record: no `_V1`, no digest.
> Source: handbook §53.2. Written first per `PAPER_OUTLINE_V2.md`'s ordering,
> because §9.5 argues from it and cannot be drafted until it exists.
>
> Target length: short. The outline is explicit that its force comes from
> brevity and from the fact that **none of the five was written to demonstrate
> the guard.**

---

## Draft

The system enforces a claim boundary in code. `enforce()` scans generated prose
for a fixed list of forbidden clinical claims — that the system establishes a
diagnosis, detects ischemia in a patient, or is fit for clinical use — and
refuses text that asserts one. The list is Appendix A. The guard is lexical: it
matches surface forms, not meaning.

We did not learn what it was worth from the tests written for it. We learned it
from five components that tripped it by accident, built weeks apart, under
different reasoning, by authors who had all read the same claim boundary.

| # | Component | What tripped it |
|---|---|---|
| 1 | Evidence Agent (#84) | its own disclaimer, *"does not establish a diagnosis"* |
| 2 | Explanation template (#86) | its closing sentence, the same claim |
| 3 | Research Assistant (#87) | `claims_forbidden`, which states the forbidden claims **in order to prohibit them** |
| 4 | Demonstration console (#93) | `textwrap` split the canonical disclaimer across two lines; the literal exemption stopped matching and a **correct** output was flagged |
| 5 | Evaluation report (#94) | its **reporting rules**, which prohibit a claim by naming it — *"no winner is declared"*, *"neither arm is better"* |

**In every case the offending text was a boundary statement.** Not one was a
model overclaiming; not one was careless prose. Each component was trying to say
what the system does not do, and saying so is what the guard caught. A lexical
guard cannot distinguish an assertion from its denial, and the five instances
are that limitation meeting five authors who each assumed their own phrasing was
obviously exempt.

**The fourth is the instructive one, and it is a different defect.** The first
three are one limitation seen three times. The fourth is worse: the guard
accepted a passage and rejected the *identical* passage after `textwrap` had
broken it across two lines. Content was unchanged; only presentation differed;
the verdict inverted. The exemption was matched against a surface form, and a
renderer changed the surface. Any rendered output would have hit it, and no
author writing an exemption would think to test line wrapping.

The general form is worth stating beyond this system: **an exemption matched
against a surface form is a bug waiting for a renderer.** The same failure is
available to secret scanners, licence detectors, and content filters — anything
that decides on text after something else has decided how to lay it out.

**The fifth is scoped differently, deliberately.** #94's reporting rules are
curated constants, reviewed once by a human rather than generated per alert, so
its exemption lives in the evaluation test rather than in the guard. Only the
report body can overclaim, and that is where `audit` is pointed. Registering the
rules globally would have widened a permanent exemption to buy nothing.

**Every fix was structural, and that is the finding.** `enforce()` guards
*generated* prose; text that quotes a forbidden claim in order to deny it is
**declared** — registered once in `APPROVED_DISCLAIMERS`, or passed by the
caller as `quoting=`. `strip_approved_disclaimers` is now whitespace-insensitive.
One canonical closing sentence, `claims.SYSTEM_BEHAVIOUR_ONLY`, is used verbatim
by every writer; each writer inventing its own variant is what produced findings
1 and 2.

The alternative was available and cheaper each time: reword until the guard goes
quiet. We did not take it, and the reason belongs in the paper rather than in a
commit message. **Rewording trains authors to stop stating boundaries plainly.**
A guard fixed that way grows quieter as the prose it governs grows worse, and
the quiet is indistinguishable from safety. Regex negation detection was also
considered and rejected: it would have replaced a visible failure mode with a
worse invisible one.

**The guard cannot police the document that defines it.** Run over this
programme's own governance prose it reports twelve violations, every one a
quotation. The exemption is therefore declared per caller rather than globally,
and we state the limit rather than claiming coverage we do not have.

---

## Notes for the writer — not part of the section

**A footnote candidate, for §9.5 rather than here.** The count in the source
document drifted twice in consecutive changes: #93 added the fourth as a table
row and updated the lead-in from *three* to *four* but left the heading at
three; #94 recorded the fifth as a parenthetical rather than a row. For a period
the table said four, the heading said three, and the prose said both. No finding
changed — all five were recorded somewhere throughout — but **the section whose
subject is a guard against unstated inconsistency was itself inconsistent about
its own count.** It is a small point and it is honest; §9.5 can afford one
sentence of it, and §5.6 cannot afford any.

**Must not say.** That the guard prevents overclaiming. It catches a lexical
class of it, in code the authors wrote, and the twelve-violation result on the
governance prose is the proof of its limit. §9.5.4 develops this.

**Must not say.** That five catches demonstrate effectiveness. Five is the count
of boundary statements the authors happened to write, not a detection rate. The
claim is that the guard is load-bearing, not that it is sufficient.

**Pins.** #84, #86, #87, #93, #94 are pull request numbers and are unaffected by
the 2026-08-24 identifier migration. Any *commit* SHA cited when this section is
finalised must be checked against `COMMIT_PIN_TRANSLATION_V1.md`.
