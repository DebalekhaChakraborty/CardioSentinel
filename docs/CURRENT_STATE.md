# Current State

This is a living document, not a frozen protocol record. Unlike the `_V1`
documents elsewhere in this folder, it carries no digest and no freeze ritual —
it is meant to be regenerated wholesale, not amended. Do not hand-edit the
data sections; ask Claude to refresh this file (a fresh read-only pass against
`git`, `gh`, and `cardiosentinel-runs/`) and it will be rewritten in place.
Commentary can go in a `Notes` subsection if needed, but treat everything else
here as disposable output, not source of truth — **the repository is the
source of truth; this file is a cache of it.**

Read this file for *"where are we"*. Read the `_V1` documents for *"what did we
decide and why"*. Read
`docs/CardioSentinel_Research_Execution_Handbook_v1.4.md` for the programme's
governing account of itself, `docs/ARCHITECTURE.md` for where the code actually
lives, and `docs/EXPERIMENT_CATALOGUE.md` for what has been spent.

---

**As of:** `origin/master` `9f38f47` (merge of PR #88), 2026-08-23 ·
tag `ips-agentic-runtime-v1.0`
**Working tree:** clean
**Open PRs:** 1 — #80, Research Baseline v1.0
**Canonical T1 attempt:** **CONSUMED** — failed post-claim at stage 24
**T1 measurement continuation:** **COMPLETED** — the single authorization is spent
**T2 outer validation:** **CONSUMED and ANALYSED** — values published
**Sealed B4/neural TEST:** **unopened — the last irreversible budget**

---

## Live flag — every free move has been spent

Since the previous refresh the programme has run out of cheap options. Every
derived analysis that required no new authorization has now been executed:
the T2 arm comparison, the T2 paired bootstrap, the W1 window comparator, and
the U1 per-bin reliability read.

**Nothing further can be run without one of three things:** a new human
authorization, a re-scoring run, or data the project does not have.

The flags `T1_CONTINUATION_AUTHORIZED` and
`T2_OUTER_VALIDATION_EXECUTION_AUTHORIZED` are both `True` on disk. **Both are
spent tokens, not live permissions.** The re-run guard is the persistence claim
— an attempt directory that already exists is refused — not the flag.

---

## 1. Repository identity

| | |
|---|---|
| `origin/master` | `9f38f478cde93ed9264ea121b58f2d1f51292c91` — merge of PR #88 |
| Tags | `research-freeze-v1.0` (science frozen) · `ips-agentic-runtime-v1.0` (agentic layer complete) |
| Working tree | clean, no untracked non-ignored files |
| Open PRs | #80 (Research Baseline v1.0) |
| Tracked Python | 250 files · 117,104 LOC |
| Tests | 102 files · 2,689 definitions |
| Documents | 64 |
| Evidence on disk | `cardiosentinel-runs` 2.3 GB · `cardiosentinel-data` 5.6 GB · `cardiosentinel-features` 16 GB (all gitignored) |

### Merged since the previous refresh (`1bbbd47`)

```
#66 handbook rename + .docx          #73 W1 pre-registration + arm
#67 track document generators        #74 W1 report — RQ4 answered
#68 IMPLEMENTATION_PLAN/README drift #75 external validation strategy
#69 13 stale tests + firewall docs   #76 W1 section renumber
#70 T2 paired bootstrap (no values)  #77 README/PLAN/REPO_AUDIT refresh
#71 U1 reliability plan + generator  #78 U1 per-bin reliability report
#72 T2 arm-comparison report
```

---

## 2. Where this stands vs. the plan docs

`docs/IMPLEMENTATION_PLAN.md` was refreshed in #68 and #77 and is **current**.
`docs/README.md` and `docs/REPO_AUDIT.md` were refreshed in #77.
`docs/RESEARCH_SCOPE.md` has not been revised since 2026-08-07 and does not
need to be: the objective it states is unchanged.

**The handbook is now v1.3.** v1.2 is superseded but tracked and unedited, on
purpose — it is the document that recorded "not one of the seven research
questions is affirmatively answered", and that statement is now evidence of a
moment rather than a fact.

---

## 3. Experiment ladder

| ID | Status | Evidence | Outcome |
|---|---|---|---|
| B0–B3 | complete | `phase3b-classical-v3` | sealed test **CONSUMED** |
| B4-A / B4-B / B4-C | complete | `phase3b2-*` | **B4-B selected** |
| P1 | complete | `phase4-p1-physiology-v1` | **P1-B retained**, FPR caveat |
| M1 | complete | `phase5-m1-dual-memory-v2` | **M1L retained** |
| M2 | complete | `phase6-m2-development-v1` | **M2-G retained** |
| U1 | **split retention** | `phase7-u1-development-v1` | Platt retained, **router rejected** |
| T2 | complete and **analysed** | `phase8-t2-development-v1` | S4D selected; contrast interval spans zero |
| T1 | complete and **analysed** | `phase9-t1-*` | measured, reported |
| W1 | complete | derived — no run directory | **RQ4 supported (bounded)** |
| **IPS runtime** | **implemented** | `edge/`, 1,428 lines | replay simulation on a laptop; **not edge hardware** |
| **Agentic layer** | **implemented** | `agents/`, 2,049 lines | evidence, graph, explanation, research assistant |
| E1 edge hardware | not started | — | RQ5 open; a laptop is not an edge device |

Full ledger with the consumed/available column: `docs/EXPERIMENT_CATALOGUE.md`.

---

## 4. Published results

| Experiment | Headline | Interval |
|---|---|---|
| **T1** | subject-macro `episode_f1` **0.2524** | [0.0826, 0.4415] |
| **T2** | `pooled_auprc_difference` **0.093215** | **[-0.015229, 0.148951]** — includes zero |
| **W1** | T1 − W **0.1921** | **[0.0505, 0.3455]** — excludes zero |
| **U1** | Platt NLL **0.143708** / Brier **0.040344** | vs baseline 0.231705 / 0.063567 |

**T2's difference IS the selection criterion**, not an independent discovery.
**W1's answer is bounded** by an operating point selected with the state machine
in the loop. **U1's baseline is not an out-of-fold artifact** — the artifact says
so.

Each headline carries a caveat about what its denominator actually is; the
pattern is recorded as a finding in handbook §49.4.

---

## 5. Research questions

| RQ | Status |
|---|---|
| RQ1 memory reduces false alarms | **Open** |
| RQ2 personalization contamination-safe | **Partial** |
| RQ3 uncertainty routing | **Negative** — router rejected |
| **RQ4 episode reasoning** | **Supported (bounded)** |
| RQ5 edge efficiency · RQ6 distillation · RQ7 confounder-aware | **Open** |

**RQ4 is the programme's first affirmative answer.** *"(bounded)"* may not be
dropped when quoting it.

**Still unanswered and not an RQ:** what the S4D architecture contributed. T2's
interval spans zero and `s4d_temporal_evidence_s_t` feeds both W1 arms.

---

## 6. Code maturity

Strongest: governance. One-shot claims, negative-capability proofs (AST plus
`sys.modules`), frozen dependency digests, immutable attempt directories,
pre-registration workflow, tracked provenance generators.

Weakest: the top-level package tree still partly misrepresents the codebase.
`edge/` and `agents/` now hold real code (see `ARCHITECTURE.md` §0.1);
`episodes/`, `personalization/` and `uncertainty/` are two-line docstring stubs,
while the work lives in `neural/` — 86 files, 54,073 LOC, 46% of the code. Two of
those four stubs describe research that is complete elsewhere. See
`docs/ARCHITECTURE.md`.

---

## 7. Data preservation — **snapshot exists, mirror NOT re-verified today**

A full evidence mirror was created and verified on 2026-08-22:

```
s3://cardiosentinel-evidence-341181499761/snapshot-2026-08-22-1bbbd47/
786 objects · 24,779,296,980 bytes
Versioning · Object Lock GOVERNANCE 365 days · SSE-S3 · public access blocked
```

**As of 2026-08-23 the AWS session has expired and the mirror could not be
re-verified.** That is a statement about this moment, not about the snapshot:
Object Lock GOVERNANCE with a 365-day retention was confirmed at creation, and
nothing has been deleted. **Re-authenticate before relying on it, and do not
record it as verified until you have.**

The local evidence tree is **unchanged since the snapshot**. The T2 analysis and
W1 both wrote only to `docs/`; `find -newermt` over the run directories after
each returned nothing.

**Restoring bytes is not restoring evidence state.** S3 assigns its own
`LastModified`, and immutability here is asserted in timestamps. A restore must
replay the manifest:

```bash
while read -r sha size mtime path; do touch -d "@$mtime" "$path"; done < MANIFEST_SHA256.txt
```

---

## 8. Open defects and next steps

### Defects

1. **AWS session expired** — S3 mirror unverified as of 2026-08-23 (§7).
2. **Four empty packages** advertise an architecture the code does not use.
   Repair named in `docs/ARCHITECTURE.md` §5, deliberately not done during the
   freeze.
3. **Seven scratch worktrees** remain registered from the ECG 14 session, all on
   merged branches with no uncommitted work.
4. The ECG 3 outer-repo index reconstruction still merits a human glance.

### Next steps

Under **Research Baseline v1.0** (handbook §51) the repository is frozen for
documentation, analysis of existing evidence, and paper drafting. No new
experiment, no architecture change, no threshold generation, no sealed-test
access.

1. Merge #80 — completes the baseline.
2. **Related Work and Discussion** — do not exist in any form; the long pole.
3. Evidence map and paper outline.
4. **Do not open the B4 sealed test.** Handbook §43 now argues this on evidence:
   the headline contrast spans zero, and no cohort exists to corroborate a test
   number.

Leaving the freeze requires a named experiment with a pre-registered protocol,
as T1, T2, U1 and W1 each had. The two candidates are the **T2-score ablation**
(what did S4D contribute?) and the **RQ1 no-memory arm** — both require a
re-scoring run, neither can reuse the W1 trick.

---

_Last refreshed: 2026-08-23, against `origin/master` `9f38f47`, after the IPS
runtime and agentic layer merged (#82-#88)._
