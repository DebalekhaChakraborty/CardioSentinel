# CardioSentinel V2 — Research Charter, V1

**Status:** Frozen charter. Grants no experimental authorization.
**Planning authority:** [`CARDIOSENTINEL_TOP_JOURNAL_RESEARCH_MASTER_BLUEPRINT_V2_1.md`](CARDIOSENTINEL_TOP_JOURNAL_RESEARCH_MASTER_BLUEPRINT_V2_1.md)
**Date:** 2026-09-01

---

## A. Programme identity

**CardioSentinel V1** is a completed evidence programme. Its measurements are
final, its one-shot budgets are spent, and its record is immutable.

**CardioSentinel V2** is a prospective journal-extension programme. Nothing in it
has been measured.

**V2 exists to resolve limitations V1 revealed, not to overwrite them.** Where V1
returned a negative result, V2 does not get to re-run it until it turns positive.
Where V1 stated a limitation, that limitation stands until new evidence
addresses it prospectively.

"V1" and "V2" name **research evidence programmes**, not product generations.

## B. Central scientific thesis

> An adaptive physiological monitoring system should be judged not only by what it
> predicts, but also by **what observations it may learn from**, **how evidence
> persists into an event**, **how it behaves under distribution shift and physical
> constraints**, and **what claims its human-facing AI layer may assert**.

Prediction quality is one axis among five. A system that scores well and learns
from contaminated observations, or that explains itself in terms its evidence
does not record, has not been shown to be good — it has been shown to be
unmeasured on the axes that matter.

## C. Core journal-extension research questions

Six, frozen. None is authorized by appearing here.

| ID | Question |
|---|---|
| **J-RQ1** | **Patient-relative memory / cold start.** What does a patient-relative memory contribute over a patient-agnostic baseline, and how does that contribution behave before the memory has anything to learn from? |
| **J-RQ2** | **Contamination-gated adaptation.** What does the admission gate buy, what does it cost, and how does the system behave under adaptation stress and recovery? |
| **J-RQ3** | **Fair stateful vs memoryless episode reasoning.** Does stateful episode reasoning beat a memoryless comparator that has been **independently tuned** rather than inherited, on the same partition? |
| **J-RQ4** | **Genuinely fresh external transfer.** How does a frozen V2 system behave on a cohort qualified as external, contamination-reviewed, and never used to develop it? |
| **J-RQ5** | **Explanation-state consistency.** Can a model-independent guard keep a generated explanation consistent with the state the evidence records, and at what scale does that hold? |
| **J-RQ6** | **Real ECG-capable physical / edge execution.** What does the system do on hardware that actually acquires or replays ECG under physical constraint? |

**R2 — Representation 2.0 is conditional, not a seventh core question.** It is
approached only if mechanism evidence from the core workstreams warrants it. It
does not carry the standing of J-RQ1–J-RQ6.

## D. Scientific boundaries

V2 does not claim, and no V2 document may assert:

- **diagnosis** of any condition;
- **treatment recommendation** of any kind;
- **clinical utility** — detection is not care;
- **medical-device** status or readiness;
- **generalization beyond the cohorts actually evaluated**;
- **wearable readiness** without device-specific evidence;
- **neural superiority** unless it is actually established — V1's B4-B result
  (0.0935 against B3's 0.1683 on the same held-out partition) is a negative
  finding and remains one;
- **S4D superiority** unless it is actually established.

These are boundaries on claims, not on questions. V2 may investigate any of them;
it may not assert them ahead of evidence.

## E. Programme success definition

**V2 does not require every experiment to be positive.** A programme that can only
succeed by producing positive results is not measuring anything.

Success means:

1. **Fair questions** — comparators tuned independently, not inherited from the
   system under test.
2. **Prospective comparators** — designed before the outcome is known.
3. **Fresh evidence where confirmation is claimed** — never a re-reading of spent
   evidence.
4. **Preserved negative results** — reported as results, not tuned away.
5. **Traceable artifacts** — every number reaches a frozen report or promoted run.
6. **Claims bounded by observed evidence** — the boundary in §D compiled into the
   claim guard, not merely written down.

A V2 that answers all six questions negatively, fairly, and traceably has
succeeded as a research programme.

## F. Journal ambition

The intended evidence ladder, in order:

1. rigorous internal prospective comparisons;
2. external frozen evaluation;
3. scaled explanation-governance benchmark;
4. physical edge / acquisition evidence;
5. integrated flagship journal package.

**No journal is warranted yet, and this charter does not claim one is.** Each rung
is earned by evidence produced under its own authorization. The ladder records
the order in which the programme intends to climb, not a prediction that it will.
