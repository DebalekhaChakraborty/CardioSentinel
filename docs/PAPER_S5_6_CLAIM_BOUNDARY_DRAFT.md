# §5.6 — Nine boundaries the guards caught in our own code

> **Draft prose for the manuscript.** Not a frozen record: no `_V1`, no digest.
> Source: handbook §53.2 for findings 1–5; `LOCAL_LLM_EXPLANATION_PROTOCOL_V1.md`
> and `EXPLANATION_EVALUATION_REPORT_V1.md` for findings 6–9. Written first per
> `PAPER_OUTLINE_V2.md`'s ordering, because §9.5 argues from it and cannot be
> drafted until it exists.
>
> **The outline calls this section "Five boundaries" and that count is now
> wrong.** The explanation layer added four, each of them found by a failure the
> gates already in place had passed. `PAPER_OUTLINE_V2.md` §5.6 is superseded on
> the count and on nothing else.
>
> Target length: short, and **it is now under pressure**. The section's force
> comes from brevity and from the fact that **none of the nine was written to
> demonstrate a guard.** Part B is four short paragraphs and a table for that
> reason; if the section has to lose weight, it loses Part B's prose and keeps
> Part B's table.
>
> **The two parts are different findings and the draft must not merge them.**
> Part A is one guard catching the authors nobody expected it to catch. Part B
> is four guards in a chain, each of which exists because the ones before it
> passed a real failure. §9.5.1 argues from A; §9.5.5 argues from B.

---

## Draft

### Part A — the claim guard, and the five boundary statements it caught

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

### Part B — four gates, each built because the ones before it passed a failure

When the system acquired an open-weight generator (§4.6), the claim guard became
the first of four checks rather than the only one. **That sequence was not
designed. Each gate exists because a real generation got past everything already
in place**, and the order in which they were added is the order in which the
failures were found.

| # | What got through | What it got past | What was added |
|---|---|---|---|
| 6 | a **truncated reasoning trace**, returned as if it were the explanation | fidelity **1.000**, **0** claim violations, completeness **1.000** — a deliberation fragment scored as a valid explanation on every metric in force | `enable_thinking=False`, and `_strip_reasoning` returns **empty** on an unclosed `<think>`, so truncation falls back rather than ships |
| 7 | *"an estimated peak probability of **54.6%**"*, from `peak_probability = 0.545613` | the lexical claim guard, which sees no forbidden pattern, **and the registered fidelity metric, which extracts `\d+\.\d{2,}` and cannot see one decimal place** | the **numeric claim guard** — number plus optional unit, integers included, checked against all four context sections |
| 8 | *"passed several safety checks, including **G1 through G6**"*, when **G4 and G5 were blocked** | the claim guard, the numeric guard (`G1` is not a number — the digit follows a letter), fidelity **1.000**, and completeness | **categorical state alignment** — gate status and lifecycle states compared against the structured fields |
| 9 | the categorical validator flagging the English word *normal* and **rejecting the deterministic fallback** | **its own regression test**, whose fixture set the lifecycle state to `NORMAL` and so licensed the bug | case-**sensitive** matching, since evidence and brief names are upper case |

**Finding 7 is the one that constrains the paper's own reporting.** The guard
that refuses `54.6%` is strictly stricter than the fidelity metric registered in
`EXPLANATION_EVALUATION_PROTOCOL.md` §3.1, and the two were deliberately left
different. **Widening the registered metric so that the gate and the statistic
agreed would have redefined a registered statistic to make a gate work** — the
failure the entire apparatus exists to prevent, arriving as a tidying-up task.
The metric is unchanged and §7.6 reports it unchanged.

**Finding 8 is the argument for having a categorical gate at all.** The
generation was fluent, correctly rounded, invented no number, and closed with
the canonical disclaimer. It inverted the single most safety-relevant fact in
the explanation — the one the contamination control exists to communicate — and
**every gate then in force passed it.** Lexical and numeric properties were
being checked; the assertion was categorical; nothing compared it to the fields
that record the truth.

**Finding 9 is the worst of the nine and it belongs in the paper for that
reason.** The gate added in response to finding 8 rejected the *deterministic
renderer's own output*, because the gate reason it quotes verbatim —
*"the window did not look normal enough to learn from"* — contains an ordinary
English adjective that is also a lifecycle state. A gate that rejects its own
fallback converts every generative failure into a second failure and leaves the
user with nothing. **And the regression test written for exactly this property
passed**, because its fixture licensed the state the code was wrongly matching:
the fixture agreed with the code, and only the real data disagreed. This was
first reported in the evaluation as a *model* failure, against both models, and
is corrected in the record rather than quietly dropped.

**What Part B shows that Part A does not.** Part A is a guard catching authors.
Part B is four guards in sequence, where **the evidence that each was necessary
is a specific output the previous ones passed** — and where the check most
likely to certify a defect as correct was the test written to prevent it.

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

**Must not say, for Part B.** That four gates make generated explanations safe.
Four is the number of failures that happened to be found by running two models
on a small number of contexts, and finding 8's inversion was **model-dependent**:
`Qwen3-1.7B` produced it reproducibly and `Qwen3-4B-Instruct-2507` stated the
same fact correctly. **Two models on one context is not a scaling law** and the
section must not imply the sequence is complete. The honest claim is the one
Part B's last paragraph makes: each gate is load-bearing because a real output
got past its predecessors.

**Must not say, for Part B.** That the evaluation table in §7.6 describes what a
user receives. `evaluate_arms` calls `provider.generate()` directly and **runs no
gate**, which is correct for an evaluation — gating first would only ever measure
the template — but it means the table measures raw model output. §7.6 already
carries this and §5.6 must not contradict it.

**Pin for Part B.** The lifecycle correction in finding 9 was published as a
correction to `EXPLANATION_EVALUATION_REPORT_V1.md` §4.3, not as a silent edit.
If §5.6 is ever trimmed, the correction stays: a report that was wrong and says
so is worth more here than one that was never wrong.

**Pins.** #84, #86, #87, #93, #94 are pull request numbers and are unaffected by
the 2026-08-24 identifier migration. Any *commit* SHA cited when this section is
finalised must be checked against `COMMIT_PIN_TRANSLATION_V1.md`.
