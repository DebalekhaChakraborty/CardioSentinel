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

For the sealed test specifically:
`docs/B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md` for **what the number is made
of** — written after the values were read, and explicitly not a revision of
anything pre-registered — and `docs/IMPROVEMENT_ROADMAP_V1.md` for what follows
from it. **Neither authorizes an experiment.**

---

**As of:** `master` `652da3d` (handoff ECG 20), 2026-08-25 ·
tags `research-freeze-v1.0` · `ips-agentic-runtime-v1.0`
**Refresh status:** **this is a targeted correction, not a wholesale
regeneration.** The §2 / §9.3 / literature-search claims below were false after
2026-08-25 and are fixed; the run, artifact and ledger sections were not
re-derived and carry whatever date their last full refresh gave them.
**Working tree:** shared by three workers; run `git status` before assuming
anything about it
**Open PRs:** none at the time of writing. *(Snapshot only — `gh pr list`
is authoritative; this line is stale the moment a PR opens or merges.)*
**Canonical T1 attempt:** **CONSUMED** — failed post-claim at stage 24
**T1 measurement continuation:** **COMPLETED** — the single authorization is spent
**T2 outer validation:** **CONSUMED and ANALYSED** — values published
**Sealed B4/neural TEST:** **CONSUMED 2026-08-25 — attempt 1 of 1, and the last
budget in the programme**

---

## Live flag — every budget is spent, and the paper is still not written

**The B4 / neural sealed test was consumed on 2026-08-25, 00:17:57Z to
00:43:22Z.** It was the fifteenth of fifteen one-shot budgets and the last
unspent one. **There is now no budget left to protect and none left to spend.**

This changes what the governance machinery is *for*. Until 2026-08-25 it
protected an unspent access; from now on it protects the **record** of accesses
already taken. Consumed attempt directories are immutable, the four sealed-test
artifacts are immutable, and every `*_AUTHORIZED` flag sitting `True` on disk is
a spent token rather than a live permission.

**Nothing further can be measured without one of three things:** a new human
authorization, a re-scoring run, or data the project does not have. That was
true before the sealed test opened; the one remaining exception has now been
taken.

**The remaining gap is the manuscript, not model capability.** ~~§2 Related Work
still does not exist and its literature search has not been started~~ — **§2 was
searched and drafted on 2026-08-25** (`LITERATURE_SEARCH_V1.md`,
`PAPER_S2_RELATED_WORK_DRAFT.md`), honouring the §6.3 condition of
`B4_TEST_AUTHORIZATION_V1.md`: **no sealed-test value appears in the section.**
The search **refuted the gap statement** the outline specified. §9 Discussion
exists as a merged skeleton and draft (#105), both written *before* the test
opened, which is the point: a discussion revised in light of the result would be
post-hoc reasoning whatever it concluded. **§9.3 and §9.5.5 were added after the
search and neither touches a sealed-test number.**

**What is still missing is §4 and §4.6 — the contribution — and §3.5.** They have
no draft, every source is on disk, and they are the sections the outline's own
writing order puts first.

---

## 1. Repository identity

| | |
|---|---|
| `master` | `652da3d72dbedd5c5994803ba9c9a41c1b111fd2` — handoff ECG 20. **Ahead of the last full refresh of this file, which was pinned to `84991e147d94c74481a1458645e8796781ebe14e` (merge of PR #121)** |
| Tags | `research-freeze-v1.0` · `ips-agentic-runtime-v1.0` · `legacy/v0` · three `archive/*` tags |
| Releases | none |
| Working tree | **shared.** Two Claude sessions and the user work in this checkout; `HEAD` moves under you |
| Open PRs | none |
| Tracked Python | 292 files · 126,844 LOC |
| Tests | 120 files |
| Documents | 85 in `docs/` (78 `.md`) |
| Handbook | **v1.4**, amended 2026-08-25 (v1.2 and v1.3 retained, superseded, unedited) |
| `neural/` | 87 files · 54,964 LOC — still where the work lives |
| `edge/` · `agents/` | 1,692 · 3,289 lines |
| `reproducibility/` | 35 tracked files including the 1.63 MiB demo bundle |
| Evidence on disk | `cardiosentinel-runs` 2.3 GB · `cardiosentinel-data` 5.6 GB · `cardiosentinel-features` 16 GB (all gitignored) |

### Merged since the previous refresh (`544581e`, PR #97)

```
#98  documentation state sync
#99  README written for paper readers
#100 session handoffs tracked in-repo
#101 legacy archive tag corrected, remote rename recorded  (squash-merged)
#102 COMMIT_PIN_TRANSLATION_V1 — the provenance repair
#103 B4 test authorization + Route A decline
#104 experiment-lock digest verifier
#105 paper sections 5.6 and 9, drafted before the test opened
#106 sealed evaluator bound to the SELECTED architecture
#107 B4-B sealed evaluation orchestrator
#108 end-to-end orchestrator coverage on synthetic data
#109 audit-schema pre-flight, non-masking failure recording
#110 rejected-candidate path disarmed at its source
#111 ECG 18 handoff
#112 CI repair after the sealed attempt changed a world-state assumption
#113 living sealed-test state reconciled after consumption
#114 sealed-test row added to paper §7 outline
#115 experiment catalogue updated with the consumed result
#116 local evidence-tree suite findings recorded
#117 evidence mirror verified; sealed-test artifacts mirrored separately
#118 B4-B post-hoc analysis and improvement roadmap
#119 runtime sealed-test provenance assertions corrected
#120 post-hoc diagnosis corrected against the classical comparators
#121 opt-in local Qwen explanation provider; real-model arm still unexercised
```

**The previous refresh pinned `0480b34`, which no longer resolves on the
remote.** It is the pre-rewrite identifier for `544581e`. Translate through
`docs/COMMIT_PIN_TRANSLATION_V1.md` rather than following any pin written before
2026-08-24 — see defect 0.

---

## 2. Where this stands vs. the plan docs

`docs/IMPLEMENTATION_PLAN.md` was refreshed in #68 and #77.
`docs/REPO_AUDIT.md` was refreshed in #77. *(#77 also refreshed a
`docs/README.md`; no such file exists on master today, and this line has carried
the claim forward unchecked ever since.)*
`docs/RESEARCH_SCOPE.md` retains its original objective and now states the
post-B4 execution boundary explicitly: attempt 1 completed, repeat is
prohibited, and the bounded result is available through the post-hoc analysis.

**The handbook is v1.4, amended 2026-08-25** to record the consumed sealed test
(§35.3, §43, new §43.2, §44, §49.1, §50.2, §50.3, §51, §56, Appendix A claim 12).
The amendment changed no number, interval or finding. v1.2 and v1.3 are
superseded but tracked and unedited, on purpose — v1.2 is the document that
recorded "not one of the seven research questions is affirmatively answered",
and that statement is now evidence of a moment rather than a fact.

**`docs/PAPER_OUTLINE_V2.md` is the current outline** (merged in #95, amended
2026-08-25). It supersedes `PAPER_OUTLINE_V1.md`, which predates the runtime and
the agentic layer and is retained unedited under the `_V1` convention.

**`docs/B4_TEST_DEFERRAL_DECISION_V1.md` is superseded and frozen.** It argued
for not opening the sealed test; it was overridden in writing by
`B4_TEST_AUTHORIZATION_V1.md`. It is not edited, because a decision that was
reconsidered is evidence and a deleted one is not.

---

## 3. Research state — what is complete

| Component | Evidence | Outcome |
|---|---|---|
| **B0–B3** classical baselines | `phase3b-classical-v3` | complete · sealed test **CONSUMED**, chain not extensible |
| **B4-B** neural encoder | `phase3b2-architecture-v1` | complete · **selected** over B4-A and B4-C · **sealed test CONSUMED 2026-08-25** |
| **P1-B** physiology fusion | `phase4-p1-physiology-v1` | complete · **retained**, FPR caveat recorded |
| **M1L** long-timescale memory | `phase5-m1-dual-memory-v2` | complete · **retained** |
| **M2-G** contamination-safe gate | `phase6-m2-development-v1` | complete · **retained** |
| **U1 calibration** | `phase7-u1-development-v1` | complete · Platt **retained**, router **rejected** |
| **T1 episode reasoning** | `phase9-t1-*` | complete · measured and reported |
| **T2 longitudinal comparison** | `phase8-t2-development-v1` | complete · S4D selected; contrast interval spans zero |
| **W1 window comparator** | derived — no run directory | complete · **RQ4 supported (bounded)** |
| **IPS runtime** | `edge/`, 1,692 lines | complete · replay simulation on a laptop; **not edge hardware** |
| **Evidence graph** | `agents/graph.py` | complete · 35 nodes / 39 edges per alert, closed vocabularies |
| **Explanation agents** | `agents/context.py`, `explain.py`, `providers.py` | complete · guarded generation, opt-in local provider, deterministic fallback; real-model arm unexercised |
| **Architecture Selection Agent** | `agents/architecture.py` | complete · lifecycle, not recommendation |
| **Explanation evaluation framework** | `agents/evaluation/` | complete · deterministic arm measured, generative arm **unexercised** |

**Not started:** E1 edge hardware. RQ5 is open and a laptop is not an edge
device.

**Declined rather than not-yet-done:** EDB `overlap_clean` as a secondary
evaluation, refused in writing on 2026-08-24
(`EXTERNAL_VALIDATION_ROUTE_A_DECISION_V1.md`). No EDB data was accessed. Its
§2.4 records the price: **no second cohort will corroborate any result in this
paper, permanently.**

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
| **B4-B sealed test** | pooled AUPRC **0.0935334** at prevalence **0.0460529** | subject-macro AUPRC 0.354901 over **8 of 12**, 95% **[0.033058, 0.239284]** |

**T2's difference IS the selection criterion**, not an independent discovery.
**W1's answer is bounded** by an operating point selected with the state machine
in the loop. **U1's baseline is not an out-of-fold artifact** — the artifact says
so.

Each headline carries a caveat about what its denominator actually is; the
pattern is recorded as a finding in handbook §49.4, and the sealed test is its
fourth instance.

### 4.1 The sealed-test row, with the boundary that is not optional

Registered primary: **pooled-window AUPRC 0.0935334**, over 453,804 primary
windows from 12 subjects — 20,899 positive, 432,905 negative.

| Pooled secondary | | | Subject-macro | value | contributing |
|---|---|---|---|---|---|
| AUROC | 0.7332374 | | AUPRC | 0.354901 | **8 / 12** |
| F1 | 0.0687550 | | AUROC | 0.780837 | **8 / 12** |
| Sensitivity | 0.0705775 | | Balanced accuracy | 0.563647 | **8 / 12** |
| Specificity | 0.9525716 | | MCC | 0.231071 | **8 / 12** |
| PPV | 0.0670241 | | Sensitivity | 0.169043 | **8 / 12** |
| NPV | 0.9550159 | | F1 | 0.142821 | 12 / 12 |
| Balanced accuracy | 0.5115746 | | NPV | 0.972640 | 12 / 12 |
| MCC | 0.0225878 | | PPV | 0.332849 | 12 / 12 |
| | | | Specificity | 0.947705 | 12 / 12 |

**Never quote a subject-macro figure without its denominator.** Four of the
twelve test subjects are single-class, and `METRICS_PROTOCOL.md` excludes them
from discrimination metrics rather than assigning them 0.0 or 1.0.

95% subject-bootstrap, 1,000 replicates at seed 2026, 1000/1000 successful and
0 undefined for every metric:

| | 95% interval | | | 95% interval |
|---|---|---|---|---|
| AUPRC | [0.033058, 0.239284] | | NPV | [0.912590, 0.993000] |
| AUROC | [0.653182, 0.836523] | | PPV | [0.019556, 0.415725] |
| Balanced accuracy | [0.481415, 0.650244] | | Sensitivity | [0.029482, 0.334282] |
| F1 | [0.027598, 0.222080] | | Specificity | [0.896129, 0.994691] |
| **MCC** | **[-0.033876, 0.221346]** — **includes zero** | | | |

Threshold **0.8329097628593445**, `threshold_selected_on_test: false`, taken
from the immutable development lock and never recomputed. Confusion at it:
TP 1,475 · FP 20,532 · FN 19,424 · TN 412,373. Scores are **uncalibrated sigmoid
model scores, not calibrated probabilities.**

Challenge strata at the frozen threshold — registered quantitative secondary:
rate-related FP fraction **0.2292818** (1,162/5,068, 4 subjects, 95%
[0.073911, 0.493590]); axis-shift FP fraction **0.0389143** (119/3,058, 8
subjects, 95% [0.003330, 0.229638]). **Exploratory and descriptive, never
bootstrapped and never headlined:** conduction-change, 8 of 10 windows in a
single subject.

**Provenance.** `attempt_sequence 1`, `attempt_status COMPLETE`,
`repeat_attempt_permitted false`, `evaluator_git_sha 61d9009` with
`evaluator_git_dirty false`, duration 1,524.2 s, 463,035 scored rows. Model
state digest identical before and after inference; no optimizer constructed and
`backward` never called.

**Two digests are both named `test_audit_sha256` and they are not the same
number.** `TEST_AUDIT.json`'s own field, `79447d4d…`, is self-referential — the
SHA-256 of the audit payload with that field removed, `sort_keys=True`,
`separators=(",", ":")`, the same rule the experiment locks use.
`TEST_ATTEMPT.json`'s field of the same name, `2f6af19c…`, is the SHA-256 of the
`TEST_AUDIT.json` **file bytes**. Both were recomputed and both match. Quote the
one you mean and say which it is.

**The registered comparison, which is what the budget was spent to buy.**
`B4_PROTOCOL_V1` asks whether the neural representation improves subject-disjoint
discrimination **relative to the frozen B0–B3 classical baselines**. Those were
scored on the identical partition — 453,804 windows, prevalence matching to
sixteen places, the same 8-of-12 macro denominators:

| Model | Pooled AUPRC | AUROC | Subject-macro AUPRC |
|---|---|---|---|
| B0 constant prior | 0.0460529 | 0.5000 | 0.042561 |
| B1 signal logreg | 0.1172989 | 0.7900 | 0.334247 |
| B2 morphology logreg | 0.1640117 | 0.8227 | 0.405035 |
| **B3 morphology HGB** | **0.1682901** | **0.8360** | **0.436410** |
| B4-B neural | 0.0935334 | 0.7332 | 0.354901 |

**The answer is no.** B4-B is below B1, B2 and B3, and above only the constant
prior. **It was below B3 on validation too** (0.3805 against 0.6801), so the
sealed test confirmed the development ordering rather than reversing it. That is
a clean pre-registered negative finding, of the same class as RQ3's rejected
router.

**What this row does not establish.** One dataset, twelve subjects, one attempt,
and no cohort exists to corroborate it. It supports no claim of generalisation,
superiority or clinical utility. Handbook Appendix A claim 12 states the
reporting requirement; §6.4 of `B4_TEST_AUTHORIZATION_V1.md` fixed it before
access.

**The IPS layer changed none of these.** #82–#94 ran no experiment, opened no
budget, touched no artifact and computed no new metric. Handbook §56 states this
explicitly, and the sealed test was run separately from and after that work.

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

**The sealed test answered no research question.** It characterises the selected
encoder on held-out subjects; it is not an arm of any comparison and it moved no
RQ from open to answered. RQ1 and RQ5 are open for exactly the reasons they were
open on 2026-08-24.

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

The research assistant's current-state topic is `sealed_test_consumed`: it
reports attempt 1 `COMPLETE`, repeat prohibited, and routes stale-premise
questions about an "unopened" test to the consumed record. `research.py` also
repeats U1 and T2 `source_lock` values that say `unopened`; those remain correct
historical attestations about those runs, not claims about today's repository.

---

## 7. Code maturity

Strongest: governance. One-shot claims, negative-capability proofs (AST plus
`sys.modules`), frozen dependency digests, immutable attempt directories,
pre-registration workflow, tracked provenance generators, the publication
claim boundary compiled into code, and — new since 2026-08-25 — a
selected-architecture binding that makes "the model the authorization names" and
"the model the evaluator loads" one comparable object, verified before any
sealed access is attempted (`neural/b4b_sealed_test.py`, handbook §43.2).

Weakest: the top-level package tree still partly misrepresents the codebase.
`edge/` and `agents/` now hold real code (see `ARCHITECTURE.md` §0.1 and §0.2);
`episodes/`, `personalization/` and `uncertainty/` remain two-line docstring
stubs, while the work lives in `neural/` — 87 files, 54,897 LOC, 44% of the code.
Two of those three stubs describe research that is complete elsewhere.

---

## 8. Data preservation — **verified 2026-08-25, and the sealed test is now in it**

Two snapshots, both Object-Locked, both verified by content on **2026-08-25**:

```
s3://cardiosentinel-evidence-341181499761/
  snapshot-2026-08-22-1bbbd47/        786 objects ·  24,779,296,980 bytes
  snapshot-2026-08-25-sealed-test/      5 objects ·           5,015,638 bytes
Versioning · Object Lock GOVERNANCE · SSE-S3 · public access blocked
```

**Read the date, not the sentence.** The guarantee is exactly as current as its
last check, and it degrades silently: between 2026-08-24 and this check the AWS
session expired and the mirror was unverifiable, with nothing failing to
announce it. It will happen again.

### 8.1 What was checked on 2026-08-25, all read-only

| | `snapshot-2026-08-22-1bbbd47` |
|---|---|
| Object count · bytes | **786** / **24,779,296,980** — exact match to creation |
| Delete markers | **none.** Nothing has ever been deleted |
| Object versions | **786** — one per object, no overwrites |
| Retention, sampled object | `GOVERNANCE`, `RetainUntilDate 2027-08-22T19:07:47Z` — on the object, not merely a bucket default |
| Public access · encryption | all four blocks `true` · `AES256` |
| Manifest integrity | `MANIFEST_SHA256.txt` digest **`dd42385631ded573…`**, matching handbook §47 exactly |
| Against the local tree | **785/785** manifest rows resolve, **785/785** sizes match, **0** missing |
| Content re-hash | **15/15** sampled `sha256` recomputed and matched, seed 2026, 191,976,558 bytes |

**This is a verification of contents, not of existence.** A headcount would have
passed even if every file had been replaced.

### 8.2 The sealed-test artifacts are mirrored

Uploaded 2026-08-25 to a **separate prefix**, deliberately. Appending to
`snapshot-2026-08-22-1bbbd47` would have made its 785-row manifest wrong and
destroyed the property that a snapshot is a point in time.

```
snapshot-2026-08-25-sealed-test/
  MANIFEST_SHA256.txt                                    686 B
  …/B4B_cnn_transformer_v1/TEST_ATTEMPT.json          34,513 B
  …/B4B_cnn_transformer_v1/TEST_AUDIT.json            34,129 B
  …/B4B_cnn_transformer_v1/TEST_METRICS.json           6,521 B
  …/B4B_cnn_transformer_v1/TEST_PREDICTIONS.npz    4,939,789 B
```

All five carry `GOVERNANCE` until **2027-08-25T07:59Z**, confirmed per object.
**All four artifacts and the manifest were round-tripped from S3 and compared by
digest, not by size** — five of five matched. The three digests the manifest
records for `TEST_AUDIT`, `TEST_METRICS` and `TEST_PREDICTIONS` were also
cross-checked against the values `TEST_ATTEMPT.json` itself records for them,
so the mirrored bytes are provably the ones the attempt receipt describes.

**An `AccessDenied` on `put-object-retention` here is the lock working, not a
failure.** The bucket's 365-day default applies GOVERNANCE at PUT time; an
explicit call asking for an earlier date is refused because *shortening*
GOVERNANCE needs `s3:BypassGovernanceRetention`. Read the retention back rather
than concluding it was not applied.

### 8.3 The 788 / 789 arithmetic, resolved

An earlier draft of this file flagged a one-file discrepancy: the manifest
covers 785 files and the three evidence trees now hold 788, and 785 + 4 ≠ 788.
**There was no loss.** The manifest also covers `artifacts/README.md`, which is
outside those three trees. In-tree at snapshot time: 784. Plus the four
sealed-test artifacts: **788.** Every manifest row resolves locally.

Recorded because the reasoning matters more than the number: a count that is off
by one and shrugged at is how a mirror check passes while being wrong.

**`MANIFEST_SHA256.txt` has four fields — `sha256 size mtime path`** — the same
shape the restore procedure below reads. A two-field parse silently resolves
zero rows and reports success, which is worse than failing.

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

**The package does not reproduce the sealed test and is not meant to.** It
carries development artifacts only, the scenario replays a validation record,
and no path in it touches the test partition.

---

## 10. Open defects and next steps

### Defects

0. **Every commit SHA pinned before 2026-08-24 is dangling on the remote.**
   Master's history was rewritten to strip `Co-Authored-By` trailers and
   force-pushed; **no content changed** — every tree object is identical — but
   268 commit identifiers moved and **69 commits cited across 71 tracked files
   stopped resolving**.

   **Now translated rather than repaired.** `docs/COMMIT_PIN_TRANSLATION_V1.md`
   (#102) carries **326 exact mappings**, both directions, with the derivation
   stated so a third party can re-derive it, and
   `docs/PROVENANCE_INCIDENT_V1.md` carries the dated chronology. The pins in
   frozen `_V1` records are **not** edited: rewriting them would mean editing
   records whose immutability is itself a claim.

   **Experiment locks cannot be corrected in place even in principle.**
   `experiment_lock_sha256` is self-referential — the SHA-256 of the lock with
   that field removed, `sort_keys=True`, `separators=(",", ":")` — so editing
   any field changes the lock's own digest, and B4-B's appears in **32 files**
   — measured 2026-08-25, excluding caches — across the docs, the source, the
   tests, the demo bundle and the evidence tree, **9 of them other experiments'
   `EXPERIMENT_LOCK.json`**, 13 of them tracked in git.
   `neural.integrity.verify_experiment_lock()` (#104) implements the check.
   **Translate; never edit.** *(The ECG 18 handoff says 28 files. That figure
   was inherited; re-counting gives 32. It changes no conclusion, but quote the
   measured one.)*

   Pre-rewrite history is preserved in `refs/original/*`,
   `refs/local-backup/pre-coauthor-rewrite` and
   `~/cardiosentinel-recovery/pre-coauthor-rewrite.bundle`. **Do not run
   `git gc --prune=now`.** Note the trap this creates: `git cat-file -t` on an
   old SHA succeeds *on this machine* and fails on a fresh clone, so it is not a
   test of whether a pin resolves.

1. ~~**AWS session expired; the S3 mirror is unverified.**~~ **Closed
   2026-08-25.** The session was renewed and both snapshots verified by content
   — 786 objects exact, 0 delete markers, manifest digest matching handbook §47,
   785/785 rows resolving, 15/15 sampled digests recomputed (§8.1). **It will
   degrade again**, silently and with nothing failing: this defect has now been
   opened and closed twice in three days. The guarantee is only as current as
   its last check, so re-verify with a date attached rather than inheriting
   this one.
2. ~~The generative explanation path has never run against a real model~~ —
   **closed 2026-08-25.** Arm B is exercised: `Qwen/Qwen3-1.7B` at revision
   `70d244cc`, greedy on CPU, reported in
   `docs/EXPLANATION_EVALUATION_REPORT_V1.md`. Fidelity 1.000, **0 claim
   violations**, completeness 1.000, 63.4 s.

   **The result worth carrying forward is not the table.** `Qwen3-1.7B`
   asserted that a `G1`–`G6` range passed while G4 and G5 were blocked. Three
   gates and four registered metrics passed it; the categorical alignment
   validator refused it and the user received the deterministic explanation. The
   failure reproduced across independent runs. **`Qwen3-4B-Instruct-2507` did not
   make it** and was served — two models, one context, which is not a scaling
   law.

   **The harness measures raw model output** — it calls `provider.generate()`
   directly and no runtime gate runs during evaluation. That table is not what a
   user receives, and reading it as such would be wrong.
3. **Three empty packages** advertise an architecture the code does not use.
   Repair named in `docs/ARCHITECTURE.md` §5, deliberately not done during the
   freeze.
4. **`scripts/provenance/` is ruff-excluded**, so lint errors there are
   invisible to CI. Passing explicit paths still reports **116 errors, 9
   auto-fixable**, unchanged. **Reformatting a generator changes its digest**,
   so any such pass must update `scripts/provenance/README.md` in the same
   commit.
5. **Nothing asserts the four tracked-generator digests.** All four match as of
   this pin — recomputed 2026-08-25 — but one was false on master from #72 until
   #96 and no automated reader would have noticed. The assertion test is
   recommended and still unwritten.
6. ~~**The sealed-test artifacts are unbacked and unrepeatable.**~~ **Closed
   2026-08-25.** Mirrored to `snapshot-2026-08-25-sealed-test`, five objects
   under `GOVERNANCE` until 2027-08-25, **round-tripped and compared by digest
   rather than by size** (§8.2). They remain unrepeatable —
   `repeat_attempt_permitted` is `false` and no authorization can make it true —
   so the second copy is the whole of the protection they will ever have.
   **Anything that changes them must be treated as a finding, not a file to
   regenerate.**
7. ~~**Runtime assertions that the sealed test is unopened.**~~ **Closed.**

   **Fixed:** `agents/claims.py:107` (the Appendix A claim-12 rationale, which
   told authors *"The neural chain is unopened"* while refusing their §7 text),
   `edge/console.py:39` and its `DEMO_SCENARIO.md` §5 counterpart, and
   `edge/artifacts.py` — whose module docstring asserted the test *"remains
   unopened"* and whose `provenance()` **hardcoded** `test_accessed` and
   `sealed_test_state`. Those two are now **read from the P1-B experiment
   lock**, which is the artifact that actually attests them; the loader refuses
   rather than defaulting if the lock omits either. The value is unchanged. What
   changed is that it is sourced from the record instead of asserted about the
   world.

   **An earlier count of "seven false assertions" was wrong, and the correction
   matters.** `agents/research.py:95` and `:167` restate the `source_lock` of
   the **U1** and **T2** experiments. Those locks do say
   `sealed_test_state: unopened`, permanently and correctly, so those two lines
   are accurate — hardcoded rather than read, which is a lesser fault, but not
   false. The former `sealed_test_unopened` current-state topic is now
   `sealed_test_consumed`, backed by the one immutable attempt receipt and the
   post-hoc analysis. The coupled test checks the receipt's sequence, status and
   repeat prohibition rather than asserting absence.

8. **`stash@{0}` is a stale `CURRENT_STATE` refresh** pinned to `1018001`,
   predating the sealed test. Regenerate; do not pop.
9. ~~**M1 and P1 preflight are permanently pinned to one status.**~~ **Closed.**
   `m1_experiment.unexpected_test_artifacts()` now asks the question the gates
   actually need — *"has anything appeared the authorization does not account
   for?"* — against `AUTHORIZED_TEST_ARTIFACTS`, the four artifacts of the
   consumed B4-B attempt **pinned by content digest**. `scan_test_artifacts` is
   unchanged and still answers the honest primitive question, because that
   function was never wrong. `p1_preflight`'s inline glob was rewired to the
   same check.

   **Pinned by digest, not by path**: a file at an expected path whose bytes
   differ is **reported**, because a changed immutable record is a finding
   rather than an exemption. The gate was not relaxed — its information content
   was restored, and it can now say something other than one status again.

10. ~~**The full local suite fails where CI cannot see it.**~~ **Closed by the
    post-sealed-test reconciliation.** The last failure was the research
    assistant's zero-attempt claim. Its replacement asserts exactly one receipt
    and verifies `attempt_sequence`, `attempt_status` and
    `repeat_attempt_permitted` against the immutable file. The structural CI
    asymmetry remains: `cardiosentinel-runs/` is gitignored, so CI is
    authoritative for "did I break tracked code" and the local evidence-tree
    suite is authoritative for "does runtime curation match the evidence on
    disk."

### Closed since the previous refresh

- **Eleven stale scratch worktrees** — gone. `git worktree list` shows one entry.
- **CI was red on master** for two independent reasons, neither a defect in the
  code under test: fifteen ruff errors from #107–#110, and
  `test_b4b_sealed_test_identity.py`, whose autouse fixture asserted that no
  `TEST_ATTEMPT` existed anywhere. That assertion conflated *"this suite created
  no attempt"* with *"no attempt has ever been taken"*, and the second stopped
  being true when the budget was legitimately spent. Repaired in #112: the guard
  now compares an inventory of attempt paths and digests across each test, and
  the tests that need the gitignored evidence tree skip without it.
- **Research Assistant claimed the B4 evaluation was unopened.** Reconciled to
  the consumed attempt: one receipt, attempt 1 `COMPLETE`, repeat prohibited,
  with the result bounded through `B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md`.

### Next steps

The **Research Baseline v1.0** freeze (handbook §51) still governs: documentation,
analysis of existing evidence, and paper drafting. No new experiment, no
architecture change, no threshold generation. The sealed-test clause is now moot
rather than lifted — there is nothing left to open.

1. **The manuscript's §7 must carry the fifth row already registered in the
   outline**, with its boundary inline, and §9.1 gets one sentence. Per
   `PAPER_S9_DISCUSSION_SKELETON.md` §9.8: the number goes in §7, the sentence
   goes in §9.1, and **no thesis in §9 moves.**
2. ~~**The literature search for §2.**~~ **Done 2026-08-25** — 65 queries across
   Crossref, arXiv and PubMed, 393 hits, recorded in `LITERATURE_SEARCH_V1.json`
   with the request URL and timestamp per record. §2 is drafted with 61
   citations, 0 unresolved. **The gap statement did not survive the search**;
   the draft's §2.6 is the narrower claim. **The replacement next step is §4 and
   §4.6**, which are the contribution and have no draft.
3. **Review the drafts already merged** — `PAPER_S2_RELATED_WORK_DRAFT.md`,
   `PAPER_S5_6_CLAIM_BOUNDARY_DRAFT.md`, `PAPER_S9_DISCUSSION_SKELETON.md`,
   `PAPER_S9_DISCUSSION_DRAFT.md` (#105). ~~§9.3 is deliberately stubbed~~ —
   **§9.3 is written**, and §5.6 is now nine findings rather than five. §9.7, the
   provenance-incident subsection, is accepted and unwritten.
4. ~~**Remove or re-word one dead entry in `APPROVED_DISCLAIMERS`.**~~
   **Done 2026-08-25, and it was not dead.** `agents/claims.py` registered *"any
   claim about the sealed test, which is unopened"* from before the B4-B test was
   authorized until after it was consumed. It was first assessed as dead code on
   a `grep` for its literal text, which found one occurrence — **but
   `evidence.py` aliases the whole tuple as `CANNOT_SUPPORT`, attaches it to
   every `EvidenceRecord`, prints it under "This alert does not establish:", and
   `graph.py` emits each entry as a `constraint` node.** It was a false boundary
   shown to users on every alert, not an unused constant. **Reworded rather than
   deleted**, because deleting removes a stated boundary from user output. Two
   tests were added: one binding the disclaimer to claim 12's `reason`, one
   asserting no registered disclaimer carries research prose — the first
   rewording spelled out the denominators and the interval and was caught by
   `test_the_context_carries_no_research_prose`.
5. **Decide what phrasing the claim guard approves for reporting the sealed
   test.** Appendix A claim 12 in the handbook now reads *"test
   performance, stated unqualified"* with a reporting requirement, while
   `agents/claims.py` still encodes the absolute form and **blocks the §7 text
   the manuscript must contain** — `"on the sealed test set"` and `"test
   result"` are both refused. Those two documents now disagree. **This blocks
   next-step 1.**
6. **Report the registered comparison in §7, and name the scored artifact.**
   The sealed test evaluated the **B4-B encoder alone**, which is exactly what
   `B4_PROTOCOL_V1` §Scope pre-registered — *"a global, single-channel comparator
   to the frozen B0–B3 classical baselines… not the CardioSentinel
   contribution"*. §7 must not imply the number characterises the assembled IPS,
   **and it must report the B0–B3 comparison**, because that comparison is the
   registered research question and its answer is **no**.
   `B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md` §1.1.
7. **Re-verify the mirror when the session next expires** (defect 1, closed
   twice now). §8.1 lists what a real check is: contents, not a headcount.

Leaving the freeze requires a named experiment with a pre-registered protocol,
as T1, T2, U1 and W1 each had. The two candidates are the **T2-score ablation**
(what did S4D contribute?) and the **RQ1 no-memory arm** — both require a
re-scoring run, neither can reuse the W1 trick, and **neither has a budget**:
every one-shot access in the programme is spent, so each would need a fresh
human authorization.

---

_Last fully refreshed: 2026-08-25, against `origin/master` `84991e1` (merge of
PR #121), after reconciling the research assistant and living state documents to
the single consumed B4-B attempt._

_Targeted correction: 2026-08-25, against `master` `652da3d`, after the §2
literature search. Only the §2 / §9.3 / literature-search claims, the repository
pin, and the next-step list were touched; **the run, artifact and ledger
sections were not re-derived and are as of the full refresh above.**_
