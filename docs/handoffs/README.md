# CardioSentinel — session handoffs

One file per session. Each is written at the **end** of a session and read at
the **start** of the next. **Read the highest-numbered one first, and read it
before touching anything.**

```
handoffs/CARDIOSENTINEL_HANDOFF_ECG<N>.md
```

**These are tracked in the repository as of 2026-08-24.** Until then they lived
at `/home/AI_POC/handoffs/` and before that at `/home/AI_POC/` directly, under
the standing constraint that scratch and operational files stay out of the repo.

**That constraint was deliberately reversed for these files**, because they
existed in exactly one place: not in git, not in the S3 evidence mirror, only on
one machine's disk. The handoff is where the programme records which one-shot
budgets are spent and what is currently authorized — losing it loses the
authorization state, which no amount of git history reconstructs.

**They are still operational notes, not publishable record.** They contain
session-specific paths, tool quirks and working detail. Nothing in `docs/`
should cite them as a source, and a reader of the manuscript has no reason to
open one.

## Current

| | |
|---|---|
| **Latest** | **ECG 30** — the one to read |
| Covers | #157 merged, **the first controlled build that ever passed its gate**, and its failure. Run `33902875021` recorded the canonical qualification claim — **spending `J1-ENV-BUILDER-AUTH-002`** — then failed in both builds on `--require-hashes option does not take a value`, a syntax defect in the authorized Containerfile. Classified `POST_CLAIM_PRE_ARTIFACT`, reproducibility `NONE` (no manifest ever existed, so not `DIVERGED`). #158 preserved the claim and retired 002; this session repaired the one line and added the executable pip-parser boundary nothing had ever crossed. **No authorization 003 exists.** Artifact, environment authority and J1 authorization all remain absent |

## Index, newest first

| Session | Date | The danger it named for the session after it |
|---|---|---|
| **ECG 30** | 2026-09-04 | proving everything about an apparatus except that it runs |
| **ECG 29** | 2026-09-03 | reading a green CI run as evidence that the test you just wrote had run |
| **ECG 28** | 2026-09-03 | a test that passes tells you about the environment it ran in |
| **ECG 27** | 2026-09-01 | writing the guarantee in prose and the weaker check in code, then building the fixture to the prose |
| **ECG 26** | 2026-09-01 | verifying a scoped test run and calling it verified — twice |
| **ECG 25** | 2026-08-30 | a presentation layer quietly acquiring authority the runtime never gave it |
| **ECG 24** | 2026-08-29 | breaking a working repository to tidy a directory |
| **ECG 23** | 2026-08-27 | four kinds of defensible work — experiment, audit, hardening, documentation — none of them the manuscript |
| **ECG 22** | 2026-08-26 | relaunching a failed experiment on its own judgement |
| ECG 21 | 2026-08-26 | *(no handoff written — session ran E11 ATTEMPT 1, which failed on the NaN-mask defect; ECG 22 was written in its place)* |
| **ECG 20** | 2026-08-25 | the governance layer generating its own work, all of it defensible |
| ECG 19 | 2026-08-25 | making true documents truer, instead of writing §2 |
| ECG 18 | 2026-08-25 | *(named by ECG 19)* |
| **ECG 17** | 2026-08-24 | planning and tidying in place of writing — the next defensible task |
| ECG 16 | 2026-08-24 | stopping short of the manuscript |
| ECG 15 | 2026-08-23 | the codebase outrunning its documentation |
| ECG 14 | 2026-08-22 | merge-race and stale state |
| ECG 13 | 2026-08-22 | premature interpretation |
| ECG 12 | 2026-08-21 | haste |
| ECG 11 | 2026-08-21 | over-engineering |
| ECG 10 | 2026-08-21 | *(convention not yet started)* |
| ECG 9 | 2026-08-20 | *(convention not yet started)* |
| ECG 8 | 2026-08-19 | *(convention not yet started)* |
| ECG 7 | 2026-08-19 | *(convention not yet started)* |
| ECG 6 | 2026-08-17 | *(convention not yet started)* |
| ECG 5 | 2026-08-16 | *(convention not yet started)* |
| ECG 4 | 2026-08-14 | *(convention not yet started)* |
| ECG 3 | 2026-08-12 | *(convention not yet started)* |

**From ECG 11 onward, each handoff closes by naming the characteristic failure
of the session that wrote it.** ECG 3–10 predate that convention; the blank
cells above are accurate, not missing data.

That chain is the most useful thing in these files — it is the only place the
programme records how it goes wrong, as opposed to what it produced.

## Why they are worth keeping

The handoff records what is *currently authorized*, which one-shot attempts are
*consumed*, and which frozen digests must match. **Git history shows what
changed; it does not show which budgets are spent or what a session is permitted
to do next.** That state lives here and nowhere else.

## Paths inside the older files are stale, on purpose

**Handoffs ECG 3 through ECG 16 were written when these files lived at
`/home/AI_POC/` directly**, and their internal text still cites that path. They
moved twice on 2026-08-24 — first to `/home/AI_POC/handoffs/`, then into the
repository — and were **deliberately not rewritten**. They are records of what a
session knew at the time, and editing fourteen historical documents to correct a
path is worse than a note saying so.

Only the **live** handoff's self-reference is kept current, because it is the
one the next session pastes verbatim. That is now **ECG 18**; ECG 17 joins the
historical set and is not rewritten.

**ECG 18 records the one event the chain was built around: the B4 sealed test
was consumed on 2026-08-25.** Every handoff before it describes a programme
with one unspent budget. None remain.
