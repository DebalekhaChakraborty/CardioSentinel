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

**As of:** `origin/master` `c5595b3` (merge of PR #116), 2026-08-25 ·
tags `research-freeze-v1.0` · `ips-agentic-runtime-v1.0`
**Working tree:** shared by three workers; run `git status` before assuming
anything about it
**Open PRs:** #111 at the time of writing. *(Snapshot only — `gh pr list`
is authoritative and free; this line is stale the moment a PR opens or merges.)*
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

**The remaining gap is the manuscript, not model capability.** §2 Related Work
still does not exist and its literature search has not been started — and it now
carries the §6.3 condition of `B4_TEST_AUTHORIZATION_V1.md`: **§2 must not be
shaped by the sealed-test result.** §9 Discussion exists as a merged skeleton and
draft (#105), both written *before* the test opened, which is the point: a
discussion revised in light of the result would be post-hoc reasoning whatever
it concluded.

---

## 1. Repository identity

| | |
|---|---|
| `origin/master` | `61d9009b17293304ec3f4590a9ace1f3b8421acd` — merge of PR #110 |
| Tags | `research-freeze-v1.0` · `ips-agentic-runtime-v1.0` · `legacy/v0` · three `archive/*` tags |
| Releases | none |
| Working tree | **shared.** Two Claude sessions and the user work in this checkout; `HEAD` moves under you |
| Open PRs | #111 (ECG 18 handoff), #112 (CI repair) |
| Tracked Python | 291 files · 126,060 LOC |
| Tests | 119 files |
| Documents | 82 in `docs/` (75 `.md`) |
| Handbook | **v1.4**, amended 2026-08-25 (v1.2 and v1.3 retained, superseded, unedited) |
| `neural/` | 87 files · 54,897 LOC — still where the work lives |
| `edge/` · `agents/` | 1,666 · 3,065 lines |
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
```

**The previous refresh pinned `0480b34`, which no longer resolves on the
remote.** It is the pre-rewrite identifier for `544581e`. Translate through
`docs/COMMIT_PIN_TRANSLATION_V1.md` rather than following any pin written before
2026-08-24 — see defect 0.

---

## 2. Where this stands vs. the plan docs

`docs/IMPLEMENTATION_PLAN.md` was refreshed in #68 and #77.
`docs/README.md` and `docs/REPO_AUDIT.md` were refreshed in #77.
`docs/RESEARCH_SCOPE.md` has not been revised since 2026-08-07 and does not
need to be: the objective it states is unchanged.

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
| **IPS runtime** | `edge/`, 1,666 lines | complete · replay simulation on a laptop; **not edge hardware** |
| **Evidence graph** | `agents/graph.py` | complete · 35 nodes / 39 edges per alert, closed vocabularies |
| **Explanation agents** | `agents/context.py`, `explain.py`, `providers.py` | complete · guarded generation, deterministic fallback |
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

**Four of its provenance constants are now factually false** — `research.py:95,
167, 258` and the claim-guard strings. See defect 7. These are hardcoded, not
read from a lock, so nothing protects them and nothing excuses them.

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
2. **The generative explanation path has never run against a real model.** No
   credentials exist here and no generative SDK is a project dependency. #94
   reports this in the table rather than in a footnote, which is the correct
   handling, not a fix.
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
7. **Seven runtime assertions that the sealed test is unopened are now false.**
   Found by running the full local suite, which CI cannot reproduce — see
   defect 9.

   *User-visible text:* `edge/console.py:39` emits *"The sealed neural test is
   unopened."* as a demo limitation; `agents/claims.py:216` registers *"any
   claim about the sealed test, which is unopened"* as an approved disclaimer;
   `agents/claims.py:107` carries the Appendix A claim 12 rationale *"The neural
   chain is unopened."* `docs/DEMO_SCENARIO.md` §4 and §5 mirror the console
   strings and `tests/edge/test_demo_scenario.py` pins them, so console,
   contract and test have to move together.

   *Hardcoded provenance:* `edge/artifacts.py:101` and `agents/research.py:95,
   167, 258` write `"sealed_test_state": "unopened"` into the provenance the
   runtime reports. **These are constants, not values read from a lock.** They
   are not attestations about a past run and carry none of the protection §8 and
   handbook §43 extend to the frozen artifacts — they are the live system
   answering a question wrongly.

   `tests/agents/test_research_assistant.py::test_the_sealed_test_claim_matches_the_tree`
   **is failing on this**, correctly, and its docstring reads *"The one fact a
   reviewer will check first."* Do not weaken it; make the claim true.

   **Deliberately not fixed in the documentation pass**, because it changes
   emitted behaviour and belongs in its own reviewed change.
8. **`stash@{0}` is a stale `CURRENT_STATE` refresh** pinned to `1018001`,
   predating the sealed test. Regenerate; do not pop.
9. **M1 and P1 preflight are permanently pinned to one status.**
   `m1_experiment.scan_test_artifacts()` walks
   `REPOSITORY_ROOT/cardiosentinel-runs/**/TEST_*` **by design** — a hardcoded
   `False` there "would make the firewall decorative", as its docstring says.
   Its result feeds `m1_preflight`, where
   `test_artifact_present_human_review_required` is the **highest-precedence**
   status, and `p1_preflight`, where it sits above
   `embedding_cache_materialization_required`.

   So on any machine holding the evidence tree, **both preflights now return
   that status for every run, forever**, masking cache readiness, encoder
   verification and challenge validation underneath it.

   **This is not a bug and it is not unsafe.** It fails closed, which is the
   design. It is a gate whose trigger condition became permanently true because
   four legitimate, authorized, recorded artifacts now exist, and it has no way
   to say *"these four are known and expected"*. **What it should say instead is
   a governance decision, not a coding one**, which is why it is recorded rather
   than patched. Do not simply relax the gate.
10. **The full local suite fails seven tests and CI cannot see any of them.**
   On `01f035e`: **7 failed, 3343 passed, 1 skipped**. Six are defect 9's gate
   and one is defect 7's claim. All seven are invisible to CI because
   `cardiosentinel-runs/` is gitignored and the runner has no evidence tree.
   **CI is authoritative for "did I break something" and blind to "is the system
   still telling the truth about the evidence on disk."** Run the local suite
   before believing the second, and read the failures rather than counting them.

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

### Next steps

The **Research Baseline v1.0** freeze (handbook §51) still governs: documentation,
analysis of existing evidence, and paper drafting. No new experiment, no
architecture change, no threshold generation. The sealed-test clause is now moot
rather than lifted — there is nothing left to open.

1. **Paper §7 gains a fifth row**, with its boundary inline, and **one sentence
   in §9.1**. Per `PAPER_S9_DISCUSSION_SKELETON.md` §9.8: the number goes in §7,
   the sentence goes in §9.1, and **no thesis in §9 moves.**
2. **The literature search for §2.** Still the only unstarted item in the paper
   plan, still blocking §9.3, and now bound by §6.3 of the authorization: it must
   not be shaped by the sealed-test result. The gap statement must be written
   *after* the search rather than to fit the contribution.
3. **Review the drafts already merged** — `PAPER_S5_6_CLAIM_BOUNDARY_DRAFT.md`,
   `PAPER_S9_DISCUSSION_SKELETON.md`, `PAPER_S9_DISCUSSION_DRAFT.md` (#105). §9.3
   is deliberately stubbed; §9.7, the provenance-incident subsection, is accepted
   and unwritten.
4. **Correct the stale runtime strings** (defect 7), console and contract and
   test together, and **decide what the M1/P1 preflight gate should say now**
   (defect 9). The second is the more consequential and is a governance call,
   not a patch.
5. **Re-verify the mirror when the session next expires** (defect 1, closed
   twice now). §8.1 lists what a real check is: contents, not a headcount.

Leaving the freeze requires a named experiment with a pre-registered protocol,
as T1, T2, U1 and W1 each had. The two candidates are the **T2-score ablation**
(what did S4D contribute?) and the **RQ1 no-memory arm** — both require a
re-scoring run, neither can reuse the W1 trick, and **neither has a budget**:
every one-shot access in the programme is spent, so each would need a fresh
human authorization.

---

_Last refreshed: 2026-08-25, against `origin/master` `61d9009`, after the B4/
neural sealed test was consumed and the four sealed-test artifacts were written._
