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

**As of:** `origin/master` `a8f1b47` (merge of PR #94), 2026-08-24 ·
tags `research-freeze-v1.0` · `ips-agentic-runtime-v1.0`
**Working tree:** clean
**Open PRs:** 2 — #95 (paper outline V2 + §53.2 correction), #96 (generator
digest correction). Both docs-only, both CI green.
**Canonical T1 attempt:** **CONSUMED** — failed post-claim at stage 24
**T1 measurement continuation:** **COMPLETED** — the single authorization is spent
**T2 outer validation:** **CONSUMED and ANALYSED** — values published
**Sealed B4/neural TEST:** **unopened — the last irreversible budget**

---

## Live flag — the system is complete and the paper is not

Every derived analysis that required no new authorization has been executed, and
the intelligent physical system built on top of that frozen evidence is now
complete: it senses, decides, explains, and refuses claims its evidence does not
support.

**Nothing further can be run without one of three things:** a new human
authorization, a re-scoring run, or data the project does not have.

**The remaining gap is the manuscript, not model capability.** §2 Related Work
and §9 Discussion still do not exist as prose, and the literature search that
§2 depends on has not been started.

The flags `T1_CONTINUATION_AUTHORIZED` and
`T2_OUTER_VALIDATION_EXECUTION_AUTHORIZED` are both `True` on disk. **Both are
spent tokens, not live permissions.** The re-run guard is the persistence claim
— an attempt directory that already exists is refused — not the flag.

---

## 1. Repository identity

| | |
|---|---|
| `origin/master` | `a8f1b472a18fed6f7347522293471fc65479a625` — merge of PR #94 |
| Tags | `research-freeze-v1.0` (science frozen) · `ips-agentic-runtime-v1.0` (agentic layer complete) |
| Releases | none |
| Working tree | clean, no untracked non-ignored files |
| Open PRs | #95, #96 |
| Tracked Python | 287 files · 124,672 LOC |
| Tests | 116 files · **3,302 collected** — 3,301 passed, 1 skipped |
| Documents | 74 in `docs/` (67 `.md`) |
| Handbook | **v1.4** (v1.2 and v1.3 retained, superseded, unedited) |
| Evidence on disk | `cardiosentinel-runs` 2.3 GB · `cardiosentinel-data` 5.6 GB · `cardiosentinel-features` 16 GB (all gitignored) |

### Merged since the previous refresh (`9f38f47`, PR #88)

```
#89 documentation alignment + RQ5 contradiction fix
#90 reproducibility package — committed 1.63 MiB demo bundle
#91 recovered usability tests that lost #90's merge race
#92 Architecture Selection Intelligence Agent
#93 IPS demonstration console
#94 Evidence-Constrained Explanation Evaluation framework
```

---

## 2. Where this stands vs. the plan docs

`docs/IMPLEMENTATION_PLAN.md` was refreshed in #68 and #77.
`docs/README.md` and `docs/REPO_AUDIT.md` were refreshed in #77.
`docs/RESEARCH_SCOPE.md` has not been revised since 2026-08-07 and does not
need to be: the objective it states is unchanged.

**The handbook is v1.4.** v1.2 and v1.3 are superseded but tracked and unedited,
on purpose — v1.2 is the document that recorded "not one of the seven research
questions is affirmatively answered", and that statement is now evidence of a
moment rather than a fact.

**`docs/PAPER_OUTLINE_V1.md` predates the runtime and the agentic layer.** Its
successor, `PAPER_OUTLINE_V2.md`, is in PR #95 and is not on master yet.

---

## 3. Research state — what is complete

| Component | Evidence | Outcome |
|---|---|---|
| **B0–B3** classical baselines | `phase3b-classical-v3` | complete · sealed test **CONSUMED**, chain not extensible |
| **B4-B** neural encoder | `phase3b2-architecture-v1` | complete · **selected** over B4-A and B4-C |
| **P1-B** physiology fusion | `phase4-p1-physiology-v1` | complete · **retained**, FPR caveat recorded |
| **M1L** long-timescale memory | `phase5-m1-dual-memory-v2` | complete · **retained** |
| **M2-G** contamination-safe gate | `phase6-m2-development-v1` | complete · **retained** |
| **U1 calibration** | `phase7-u1-development-v1` | complete · Platt **retained**, router **rejected** |
| **T1 episode reasoning** | `phase9-t1-*` | complete · measured and reported |
| **T2 longitudinal comparison** | `phase8-t2-development-v1` | complete · S4D selected; contrast interval spans zero |
| **W1 window comparator** | derived — no run directory | complete · **RQ4 supported (bounded)** |
| **IPS runtime** | `edge/`, 1,666 lines | complete · replay simulation on a laptop; **not edge hardware** |
| **Evidence graph** | `agents/graph.py` | complete · 35 nodes / 39 edges per alert, closed vocabularies |
| **Explanation agents** | `agents/context.py`, `explain.py`, `providers.py` | complete · guarded generation, deterministic fallback |
| **Architecture Selection Agent** | `agents/architecture.py` | complete · lifecycle, not recommendation |
| **Explanation evaluation framework** | `agents/evaluation/` | complete · deterministic arm measured, generative arm **unexercised** |

**Not started:** E1 edge hardware. RQ5 is open and a laptop is not an edge
device.

Full ledger with the consumed/available column: `docs/EXPERIMENT_CATALOGUE.md`
and handbook §51.

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

**The IPS layer changed none of these.** #82–#94 ran no experiment, opened no
budget, touched no artifact and computed no new metric. Handbook §56 states this
explicitly.

---

## 5. Research questions

| RQ | Status |
|---|---|
| **RQ1** memory | **Open** |
| **RQ2** contamination-safe personalization | **Partial** |
| **RQ3** uncertainty routing | **Negative finding** — router built, evaluated against a prespecified gate, rejected |
| **RQ4** episode reasoning | **Supported (bounded)** |
| **RQ5** edge | **Open** |
| **RQ6** foundation-model distillation | **Not started** — Phase 4B, never begun |
| **RQ7** confounder-aware multi-task | **Not started** — Phase 6B, never begun |

*RQ labels follow handbook §50 and §16: **RQ6 is foundation-model distillation**
(Phase 4B), and **"multi-task" belongs to RQ7** — §16 is titled "Confounder-aware
multi-task" and answers RQ7. The two are separate never-begun phases.*

**RQ4 is the programme's only affirmative answer.** *"(bounded)"* may not be
dropped when quoting it.

**RQ3's negative finding is a result, not a gap.** Literature in that area
overwhelmingly reports adoption.

**Still unanswered and not an RQ:** what the S4D architecture contributed. T2's
interval spans zero and `s4d_temporal_evidence_s_t` feeds both W1 arms.

---

## 6. Agent layer

```
agents/
 ├ evidence       Evidence Agent — deterministic, no language model
 ├ graph          evidence graph — closed node kinds and edge relations
 ├ context        ExplanationContext — four closed sections
 ├ research       Evidence-Grounded Research Assistant — curated objects only
 ├ architecture   Architecture Selection Agent — lifecycle, not recommendation
 └ evaluation     Evidence-Constrained Explanation Evaluation framework
```

Alongside these: `claims.py` (the publication claim boundary as executable code,
18 Appendix A patterns), `explain.py` and `providers.py` (the Patient
Explanation Agent and its deterministic fallback), and `cli.py`.

**Every agent is grounded on the evidence graph and none is autonomous.** The
claim guard sits between every generator and its output; a violation falls back
to deterministic prose rather than publishing the claim. See
`docs/ARCHITECTURE.md` §0.2 for the flow.

---

## 7. Code maturity

Strongest: governance. One-shot claims, negative-capability proofs (AST plus
`sys.modules`), frozen dependency digests, immutable attempt directories,
pre-registration workflow, tracked provenance generators, and the publication
claim boundary compiled into code.

Weakest: the top-level package tree still partly misrepresents the codebase.
`edge/` and `agents/` now hold real code (see `ARCHITECTURE.md` §0.1 and §0.2);
`episodes/`, `personalization/` and `uncertainty/` remain two-line docstring
stubs, while the work lives in `neural/` — 86 files, 54,097 LOC, 43% of the code.
Two of those three stubs describe research that is complete elsewhere.

---

## 8. Data preservation — **snapshot exists, mirror NOT re-verified**

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

**Restoring bytes is not restoring evidence state.** S3 assigns its own
`LastModified`, and immutability here is asserted in timestamps. A restore must
replay the manifest:

```bash
while read -r sha size mtime path; do touch -d "@$mtime" "$path"; done < MANIFEST_SHA256.txt
```

---

## 9. Reproducibility package — **exists and is executable**

`reproducibility/` holds 35 tracked files including a **committed 1.63 MiB demo
bundle** (1,706,219 bytes) with all three `.pt` checkpoints tracked. A clone plus
one PhysioNet record reproduces the contracted scenario in three commands.

Both properties are tested, and the distinction matters: `tests/reproducibility/
test_demo_bundle.py` asserts **integrity**, `tests/edge/test_demo_scenario.py`
asserts **usability**. A manifest check cannot detect a file that was never
staged — which is exactly how three checkpoints were briefly lost to a
`.gitignore` rule while the integrity tests passed.

---

## 10. Open defects and next steps

### Defects

1. **AWS session expired** — S3 mirror unverified as of 2026-08-23 (§8).
   Neither verified nor lost.
2. **The generative explanation path has never run against a real model.** No
   credentials exist here and no generative SDK is a project dependency. #94
   reports this in the table rather than in a footnote, which is the correct
   handling, not a fix.
3. **Three empty packages** advertise an architecture the code does not use.
   Repair named in `docs/ARCHITECTURE.md` §5, deliberately not done during the
   freeze.
4. **`scripts/provenance/` is ruff-excluded**, so lint errors there are
   invisible to CI. Passing explicit paths reports 116 errors, 9 auto-fixable.
   **Reformatting a generator changes its digest**, so any such pass must update
   `scripts/provenance/README.md` in the same commit.
5. **Nothing asserts the four tracked-generator digests.** One was false on
   master from #72 until PR #96 corrected it, and no automated reader would have
   noticed.
6. **Eleven stale scratch worktrees** remain registered from two dead sessions,
   all on merged or pushed branches with no uncommitted work.

### Next steps

Under **Research Baseline v1.0** (handbook §51) the repository is frozen for
documentation, analysis of existing evidence, and paper drafting. No new
experiment, no architecture change, no threshold generation, no sealed-test
access.

1. Merge #95 and #96. **Verify heads with `git ls-remote` first** — a green
   check proves *a* SHA passed, not that it is still the branch head.
2. **The literature search for §2.** It is the only unstarted item in the paper
   plan, and the gap statement must be written *after* the search rather than to
   fit the contribution.
3. **Draft prose**, beginning with the five claim-boundary findings. The outline
   is finished; the manuscript is not.
4. **Do not open the B4 sealed test.** Handbook §43 argues this on evidence: the
   headline contrast spans zero, and no cohort exists to corroborate a test
   number.

Leaving the freeze requires a named experiment with a pre-registered protocol,
as T1, T2, U1 and W1 each had. The two candidates are the **T2-score ablation**
(what did S4D contribute?) and the **RQ1 no-memory arm** — both require a
re-scoring run, neither can reuse the W1 trick.

---

_Last refreshed: 2026-08-24, against `origin/master` `a8f1b47`, after the
explanation evaluation framework merged (#94)._
