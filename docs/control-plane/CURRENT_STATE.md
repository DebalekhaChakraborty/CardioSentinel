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
`docs/handbook/CardioSentinel_Research_Execution_Handbook_v1.5.md` for the programme's
governing account of itself, `docs/control-plane/ARCHITECTURE.md` for where the code actually
lives, and `docs/control-plane/EXPERIMENT_CATALOGUE.md` for what has been spent.

For the sealed test specifically:
`docs/experiments/b4/B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md` for **what the number is made
of** — written after the values were read, and explicitly not a revision of
anything pre-registered — and `docs/control-plane/IMPROVEMENT_ROADMAP_V1.md` for what follows
from it. **Neither authorizes an experiment.**

---

**As of target post-merge state:** working branch
`docs/legacy-content-only-reconciliation`
based on GitHub `master` at
`92ed049163e454bfd0a6f81230c6c91e595560b3` (demo-UI consolidation and
documentation cleanup), with
**no other open pull request**, 2026-08-30 · tags
`research-freeze-v1.0` · `ips-agentic-runtime-v1.0`
**Refresh status:** living repository, pull-request, reporting, documentation,
runtime, demo and legacy-archive state reconciled on 2026-08-30. Scientific
values below were not recomputed or re-scored; their frozen records remain
authoritative.
**Working tree:** **clean at refresh**. The runtime trust-boundary work,
document-hierarchy V2 migration, identifier mapping, research-artifact
presentation and read-only replay dashboard are merged; `master` carries them.
**Open PRs:** none after this reconciliation merges; #128 through #134 are
merged. This reconciliation PR is the sole review-time exception.
*(Snapshot only — `gh pr list` is authoritative.)*
**Canonical T1 attempt:** **CONSUMED** — failed post-claim at stage 24
**T1 measurement continuation:** **COMPLETED** — the single authorization is spent
**T2 outer validation:** **CONSUMED and ANALYSED** — values published
**Sealed B4/neural TEST:** **CONSUMED 2026-08-25 — attempt 1 of 1, and the last
budget in the programme**
**B4 E11 morphology-aware representation:** **COMPLETED — ATTEMPT 2, 2026-08-27.
Primary mechanism NOT ESTABLISHED (Category C). Not pending.**
**B4 E12a training-dynamics / selection audit:** **COMPLETE — read-only,
2026-08-27. Decision C, no further conclusion. Not pending.**
**B4 E12d instrumented phase-1 replication:** **COMPLETE — ATTEMPT 2,
2026-08-27. Historical replication PASSED. Decision D. Not pending.**
**B4 E13a held-out geometry reliability:** **COMPLETE 2026-08-28. Decision D.
The 44-subject / 79-stream E11 B0 held-out geometry population is CONSUMED for
future confirmatory geometry claims.**

---

## Live flag — every one-shot budget is spent

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

**A content-frozen long-form write-up of the programme exists in the tree** at
`docs/paper/`, 14,415 words, SHA-256
`78863bcc659f9ee54b1c6566c12fe815098f2d2852598a3bd0a708fe60029fe2`. It is a
historical record of how the evidence was narrated, not a live research
artifact, and **nothing in this repository depends on it.**

**Venue-specific preparation is out of scope for this repository** and belongs
in an external publication workspace — see `CONTRIBUTING.md`. No formatting
rule, layout constraint or author metadata is inferred or tracked here.

---

## 1. Repository identity

| | |
|---|---|
| `master` | `92ed049163e454bfd0a6f81230c6c91e595560b3` — demo-UI consolidation and documentation cleanup |
| Working branch | `docs/legacy-content-only-reconciliation`, rebased onto `master` at `92ed049`; archive-layout documentation only |
| Tags | `research-freeze-v1.0` · `ips-agentic-runtime-v1.0` · `legacy/v0` · four `archive/*` tags, including `archive/legacy-v0-tree` |
| Releases | none |
| Working tree | **clean at refresh** — the archive receipt, removal and state reconciliation are committed |
| Open PRs | **none after this reconciliation merges** — #128 through #134 are merged; this reconciliation PR is the sole review-time exception |
| Tracked Python | 318 files · 137,221 LOC |
| Tests | 127 `test_*.py` files · 3,579 collected tests |
| Documents | 174 tracked files in `docs/` (151 `.md`), including `docs/paper/` 31, `docs/handbook/` 10 and `docs/handoffs/` 24; ignored owner DOCX drafts also remain under `docs/paper/drafts/` |
| Root documentation | `audits/` 10 Markdown audits, including the recovery and formal hierarchy-migration audits; `reproducibility/` remains separate |
| Handbook | **v1.5**, with v1.2–v1.4 retained, superseded and unedited |
| `neural/` | 96 Python files · 57,980 LOC — still where most research code lives |
| `edge/` · `agents/` | 2,276 · 4,023 Python lines |
| `reproducibility/` | 36 tracked files totalling 1.72 MiB, including the read-only replay dashboard |
| Evidence on disk | `cardiosentinel-runs` 3.4 GB · `cardiosentinel-data` 5.6 GB · `cardiosentinel-features` 16 GB (all gitignored) |

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
`docs/provenance/COMMIT_PIN_TRANSLATION_V1.md` rather than following any pin written before
2026-08-24 — see defect 0.

---

## 2. Where this stands vs. the plan docs

`docs/control-plane/IMPLEMENTATION_PLAN.md` was refreshed in #68 and #77.
`docs/control-plane/REPO_AUDIT.md` was refreshed in #77. `docs/README.md` exists
and indexes the categorized `docs/` tree.
`docs/control-plane/RESEARCH_SCOPE.md` retains its original objective and now states the
post-B4 execution boundary explicitly: attempt 1 completed, repeat is
prohibited, and the bounded result is available through the post-hoc analysis.

**The handbook is v1.5.** Earlier v1.2–v1.4 editions are superseded but tracked
and unedited on purpose; they remain evidence of what the programme asserted at
those moments rather than living descriptions of the repository.

**The long-form write-up and its outlines are retained under `docs/paper/` as
historical records** of how this evidence was narrated. They are preserved
unedited under the `_V1` convention, are not authoritative for any scientific
value, and no code, test or artifact depends on their content.

**`docs/experiments/b4/B4_TEST_DEFERRAL_DECISION_V1.md` is superseded and frozen.** It argued
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
| **IPS runtime** | `src/cardiosentinel/edge/`, 2,276 lines | complete · replay simulation on a laptop; **not edge hardware** |
| **Evidence graph** | `src/cardiosentinel/agents/graph.py` | complete · verified or explicitly unavailable artifact lineage, closed node/edge vocabularies |
| **Explanation agents** | `src/cardiosentinel/agents/context.py`, `explain.py`, `providers.py` | complete · deterministic is the no-call default; local and hosted providers require explicit selection; local has no hosted fallback; **generative arm exercised once (n=1 context)** — `EXPLANATION_EVALUATION_REPORT_V1.md` |
| **Architecture Selection Agent** | `src/cardiosentinel/agents/architecture.py` | complete · lifecycle, not recommendation |
| **Explanation evaluation framework** | `src/cardiosentinel/agents/evaluation/` | complete · **both arms exercised on n=1 context** (Qwen3-1.7B, Qwen3-4B-Instruct-2507): fidelity 1.000, 0 claim violations, and the runtime **refused** the generation for a categorical gate inversion. The separate manual contract `QWEN_EVALUATION_RUN.md` is **NOT EXECUTED** |

**Not started:** E1 edge hardware. RQ5 is open and a laptop is not an edge
device.

**Declined rather than not-yet-done:** EDB `overlap_clean` as a secondary
evaluation, refused in writing on 2026-08-24
(`EXTERNAL_VALIDATION_ROUTE_A_DECISION_V1.md`). No EDB data was accessed. Its
§2.4 records the price: **no second cohort will corroborate any result in this
paper, permanently.**

Full ledger with the consumed/available column: `docs/control-plane/EXPERIMENT_CATALOGUE.md`
and handbook §51.

---

### 3.1 B4 representation investigation — E1 through E11

**E11 is COMPLETE. Any document or session describing E11 as pending, planned,
authorized-but-unrun, or in progress is out of date.**

| | |
|---|---|
| **E11** | **COMPLETED — ATTEMPT 2** |
| Executed | 2026-08-26T19:54:43Z → 2026-08-27T00:57:30Z, 5.04 h, `failure_state: null` |
| **Primary mechanism** | **NOT ESTABLISHED** |
| **Registered interpretation** | **Category C** — performance changes without established geometry improvement |
| Report | `docs/experiments/b4/B4_E11_MORPHOLOGY_AWARE_REPRESENTATION_REPORT_V1.md` |
| Plan | `docs/experiments/b4/B4_E11_MORPHOLOGY_AWARE_REPRESENTATION_PLAN_V1.md` (+ amendments A1–A8) |
| Run root | `cardiosentinel-runs/b4-e11-morphology-aware-v1/E11_ATTEMPT_2/` |
| Manifest digest | `5d357209005bf1571e3a740219dd89f6cd770ea62ee00b17c6c9806985f49359` |

**Primary geometry paired contrasts** (B1 − B0; subject bootstrap, 44 evaluable
subjects, 1,000 replicates, seed 2026):

| endpoint | point | 95% CI |
|---|---|---|
| median cosine | **+0.0030** | [−0.0178, +0.0073] |
| median `‖delta‖` | **+0.1217** | [−0.5993, +0.5617] |
| negative-cosine fraction | **−0.0127** | [−0.0406, 0.0000] |

**All three include zero.** All three point estimates moved in the predicted
pooled direction; per-fold effects are heterogeneous in sign.

**Secondary subject-macro AUPRC: +0.0258, 95% CI [+0.0002, +0.0562].**
Secondary, nominally separated, **fragile** — the lower bound is +0.0002 — and
**unsupported by the primary mechanism**. It is not E11's headline result.

**Boundaries.** **Sealed TEST untouched** (`test_partition_opened: false`,
`test_authority_constructed: false`). **Historical 12-subject VALIDATION
untouched by E11.** **44 evaluable held-out subjects — prospective development
evidence**, the largest honest unit count the programme has had, against the 9
that E1–E10 were confined to.

**ATTEMPT 1 was an experimental-apparatus failure** (`NaN * 0 == NaN` in the
auxiliary loss mask), classified by the authorizing human as **no scientific
attempt consumed**; its fold-0 B0 values are **quarantined** and were used only
as ATTEMPT 2's bit-for-bit reproduction gate.
`docs/experiments/b4/B4_E11_ATTEMPT_1_FAILURE_RECEIPT_V1.md`.

**One protocol deviation:** the registered operating-point sensitivity /
specificity endpoint **could not be computed** — the runner persisted neither
the inner-validation F1-optimal threshold nor the inner-validation predictions
needed to reconstruct it. A runner implementation gap. No threshold was derived
from held-out scores and no substitute operating point was used. See report §9.1.

**E1–E10 conclusions are unchanged by E11.**

### 3.2 E12a — read-only training-dynamics and checkpoint-selection audit

**E12a is COMPLETE. Any document or session describing E12a as pending,
planned, or in progress is out of date.** Read-only audit of E11's six
persisted phase-1 training histories. **No model was trained, no checkpoint
regenerated, no outer-held-out subject scored at any alternative epoch.**

| | |
|---|---|
| **E12a** | **COMPLETE — READ-ONLY TRAINING-DYNAMICS / SELECTION AUDIT** |
| **E11** | **remains CATEGORY C, unchanged** |
| **E12a decision** | **C — NO FURTHER CONCLUSION** |
| Report | `docs/experiments/b4/B4_E12A_TRAINING_DYNAMICS_SELECTION_AUDIT_V1.md` |

**Established:**

- **checkpoint selection is not demonstrably stable;**
- **four of six selected epochs are epoch 1;**
- **four of six best-vs-second-best AUPRC margins are below the previously
  documented +0.032 argmax-selection bias;**
- **fold 1 B1's best-vs-second-best margin is only +0.00029213;**
- **training-loss and AUPRC epoch ordering disagree in all six fits;**
- **inner-validation prevalence is 8.4×–12.1× below inner-training prevalence.**

**Unobservable from persisted evidence:**

- separate BCE trajectory;
- auxiliary-loss trajectory;
- morphology prediction trajectory;
- inner-validation AUROC trajectory;
- per-epoch representation geometry;
- whether the auxiliary task was mature at checkpoint selection;
- when the fold-2 B1 negative TRAIN stream emerged.

**Interpretation.** E11 tested the registered morphology auxiliary objective
through a **noisy early-selection regime**, but **persisted evidence cannot
distinguish a weak objective from a weak delivery/selection instrument.**

**E12a does not invalidate E11**, and **nothing in E12a states or implies that
a later epoch would have improved E11.** E11's Category C classification is
unmodified. The decision is C precisely because the auxiliary-maturity half of
the question was never persisted — an instrumentation gap, not a scientific
ambiguity.

### 3.3 E12d — instrumented E11 phase-1 replication

**E12d is COMPLETE. Any document or session describing E12d as pending,
planned, or in progress is out of date.**

| | |
|---|---|
| **E12d** | **COMPLETE — ATTEMPT 2** |
| **Historical replication** | **PASSED** |
| **Decision** | **D — NO FURTHER CONCLUSION** |
| Report | `docs/experiments/b4/B4_E12D_INSTRUMENTED_PHASE1_REPLICATION_REPORT_V1.md` |
| Plan | `docs/experiments/b4/B4_E12D_INSTRUMENTED_PHASE1_REPLICATION_PLAN_V1.md` (amended §7.0) |
| Run root | `cardiosentinel-runs/b4-e11-morphology-aware-v1/E12D_PHASE1_REPLICATION_ATTEMPT_2/` |
| Executed | 2026-08-27T15:31:38Z → 20:02:26Z · 3.60 h training + 0.91 h geometry |

**Historical replication gate: PASSED.** All six fits reproduced E11
inner-validation AUPRC **bit-identically**; selected epochs **1, 1, 1, 2, 4, 1**
and epoch counts **5, 5, 5, 6, 8, 5** exact; all three B0 `train_loss`
trajectories bit-identical; B1 total-loss differences only the preregistered
accumulation effect (≈1.3–1.8 × 10⁻⁹ relative).

**Established:**

- **B1 auxiliary loss continues decreasing after AUPRC selection in all three
  folds;**
- **`F_aux` = +0.6208 / +0.2556 / +0.5378;**
- **post-selection loss trajectories are monotone, `V == F`;**
- **5/6 selected epochs precede the largest observed geometry movement;**
- **no coherent B1-specific geometry continuation is established** — B1 exceeds
  B0 on cosine travel in 1/3 folds and on delta-norm travel in 1/3 folds, and
  they are *different* folds.

**Decision D** because A fails (no consistent B1-greater geometry), B fails
(there *is* a coherent auxiliary continuation), and C fails (that continuation
is B1-specific, so it is not a purely common training-dynamics result).

**E12d ATTEMPT 1 is quarantined: HARNESS / RNG-REPLICATION FAILURE,
SCIENTIFIC RESULT INTERPRETABLE: NO.** Its B1 trajectories must never enter
E12d results. ATTEMPT 2 is the only scientific E12d execution.

**E12d does NOT revise E11. E11 remains Category C.**

### 3.4 E13a — held-out geometry reliability and failure taxonomy

**E13a is COMPLETE (2026-08-28). Decision D — NO COHERENT MECHANISM
ESTABLISHED.** Post-hoc mechanism analysis of subjects prospectively
outer-held-out during E11; **read-only, no training**.
Report: `docs/experiments/b4/B4_E13A_HELD_OUT_GEOMETRY_RELIABILITY_PLAN_V1.md` (plan + frozen
decision table); results
`cardiosentinel-runs/b4-e11-morphology-aware-v1/E13A_HELD_OUT_GEOMETRY/`.

> ## POPULATION CONSUMPTION — RECORDED ON SUCCESSFUL EXECUTION
>
> **The E11 B0 outer-held-out 44-subject / 79-stream geometry population is
> CONSUMED for future confirmatory geometry claims.**
>
> It may still be described. It may **not** be quoted as a fresh held-out
> confirmation of any geometry hypothesis. Any future confirmatory geometry
> claim requires a partition this programme does not have.

**Established:** within-stream class direction is highly stable across
independent non-overlapping temporal halves — median `cos_within` **+0.9935**,
block-to-block sign agreement **56/57 (98%)**. **One stream (`s20171:0`) shows
temporally reproducible reversal** (`cos_A_train` −0.4984, `cos_B_train`
−0.3302). **`s20021:1` does not reproduce** (+0.4514 then −0.9537). **`s20101:1`
is not assessable** — all 390 positives fall in one temporal half.

**Decision D** because the frozen criterion required **both** eligible
negative-orientation streams to reproduce, and one of two did.

**E13a does not revise E11 (Category C) or E12d (Decision D).**

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
`docs/control-plane/ARCHITECTURE.md` §0.2 for the flow.

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
`src/cardiosentinel/edge/` and `src/cardiosentinel/agents/` now hold real code
(see `ARCHITECTURE.md` §0.1 and §0.2);
`episodes/`, `personalization/` and `uncertainty/` remain two-line docstring
stubs, while most work lives in `neural/` — 96 Python files, 57,980 LOC.
Two of those three stubs describe research that is complete elsewhere.

---

## 8. Data preservation — **three snapshots, re-verified 2026-08-31**

```
s3://cardiosentinel-evidence-341181499761/
  snapshot-2026-08-22-1bbbd47/        786 objects ·  24,779,296,980 bytes
  snapshot-2026-08-25-sealed-test/      5 objects ·           5,015,638 bytes
  snapshot-2026-08-28-4c59ff1/        196 objects ·   1,193,258,795 bytes
Versioning · Object Lock GOVERNANCE (365 d default) · SSE-S3 AES256 · SSE-C
blocked · all four public-access blocks true
```

### 8.0 The 2026-08-29 verification — all three prefixes, all read-only

Account `341181499761`, `us-east-1`. Nothing was written, deleted or retained.

| Check | Result |
|---|---|
| Object count · bytes, per prefix | **786 / 24,779,296,980**, **5 / 5,015,638**, **196 / 1,193,258,795** — exact match to creation, all three |
| Prefixes in bucket | exactly the three above; nothing else |
| Delete markers | **0** in every prefix. Nothing has ever been deleted |
| Non-latest versions | **0** in every prefix. Nothing has ever been overwritten |
| Retention, sampled per prefix | `GOVERNANCE` on the object, `RetainUntilDate` 2027-08-22 / 2027-08-25 / 2027-08-28 |
| Manifest digest, `snapshot-2026-08-22-1bbbd47` | **`dd42385631ded57320116f82d14124c99d3ffb25ea4c6ec046c69b0d13d377f6`** — matches handbook §47 |
| Manifest digest, `snapshot-2026-08-28-4c59ff1` | **`07fd04bec1d0323724f18c2c99844dbbade3f86663ef490726818f9eecad3713`** — matches the value recorded at creation |
| Manifest digest, `snapshot-2026-08-25-sealed-test` | `3d91b3b3fd87835a85935ea919a68e476488c2f0683b5a1367a044e81f6994ea` — **recorded here for the first time**; §8.2 round-tripped the five objects but never published the manifest's own digest |
| Manifest rows resolving locally | 785/785 · 4/4 · 195/195 — **0 missing** |
| Sizes matching locally | 784/785 · 4/4 · 195/195 — **one drift, explained in §8.0.1** |
| **Content re-hash, downloaded from S3** | **24/24 matched**, 93,583,879 bytes, seed 2026 — including **12 objects from `snapshot-2026-08-28-4c59ff1`, which had never been checked by anything but its own creation** |

**The 2026-08-28 snapshot is no longer the unverified one.** It was previously
attested only at upload; it has now been independently round-tripped.

**This is a verification of contents, not of existence.** A headcount would have
passed even if every file had been replaced.

#### 8.0.1 The one size mismatch, and why it is not a mirror defect

`artifacts/README.md` is **254 bytes in the manifest and 264 bytes on disk**.

The mirror is not wrong. `docs/` was reorganised on 2026-08-28 and that file's
one stale pointer was repointed — `docs/EXPERIMENT_CONTRACT.md` →
`docs/contracts/EXPERIMENT_CONTRACT.md`, exactly the ten characters — in commit
`d6dab5f`. The manifest correctly records the bytes as they were on 2026-08-22.

**It is in the manifest at all for the reason §8.3 gives:** the 2026-08-22
manifest reaches outside the three evidence trees to cover this one repository
README. It is documentation, not evidence, and no scientific artifact drifted.

**Do not "repair" this by editing the manifest or re-uploading the file.** A
snapshot is a point in time; a manifest row that no longer matches a working
tree is that property working. §8.1's *"785/785 sizes match"* was true on
2026-08-25 and is now 784/785, for this reason and only this reason.

**Read the date, not the sentence.** The guarantee is exactly as current as its
last check, and it degrades silently — the session expired between 2026-08-24
and the 2026-08-25 check, and again before 2026-08-29, each time with nothing
failing to announce it. **It will happen again.** Re-authenticate, re-run this
section, and attach the new date rather than inheriting this one.

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

### 8.4 The 2026-08-31 coverage check — what is outside Git, and where it is

Not a re-run of §8.0. That asked whether the mirror still holds what it claimed;
this asks the different question of **whether everything the repository declines
to track is held anywhere at all.**

Every file on disk outside Git was diffed, by path, against the union of keys in
all three prefixes — not compared by count, which agreeing totals can hide.

| | |
|---|---|
| Local files outside Git | **994** |
| Held in the evidence mirror | **983** |
| Held nowhere | **11** — every file in `docs/paper/drafts/` |

The three `cardiosentinel-*` trees are complete: 261 data, 158 features, 564
runs, every path resolving to an object. The three prefixes still report
**786 / 24,779,296,980**, **5 / 5,015,638** and **196 / 1,193,258,795** — exact
match to §8.0, so defect 1 has not reopened as of 2026-08-31.

#### 8.4.1 The eleven, and why they are not in the evidence bucket

`docs/paper/drafts/` holds the manuscript, `v0.1` through `v0_11`, 4,033,945
bytes. It is gitignored on purpose: `CONTRIBUTING.md` places DOCX manuscripts
outside this repository, and that has not changed.

**They are not in the evidence bucket, and should not be.** That bucket carries
Object Lock GOVERNANCE with a 365-day default, which is right for sealed
evidence and wrong for a document still being revised — `v0_11` was written on
2026-08-29, every later version would lock for a year, and the store whose
purpose is scientific evidence would fill with publication material.

They are mirrored instead to a bucket that matches what they are:

```
s3://cardiosentinel-drafts-341181499761/docs/paper/drafts/
  11 objects · 4,033,945 bytes · repo-relative keys
Versioning enabled · NO Object Lock · SSE-S3 AES256 · all four public-access
blocks true
```

Versioned so revisions accumulate, unlocked so a draft stays a draft. Verified
on 2026-08-31 the way §8.0 verifies: **11/11 re-hashed after download from S3**,
4,033,945 bytes, `sha256(sorted per-file digests)` =
`b1c6bd8ad758418b7700b16421dc9f0e2591835fc2d46eec259d071196d598e8`.

**This is a mirror, not an archive.** No Object Lock means these objects can be
overwritten or deleted; versioning preserves prior versions but not against a
deliberate purge. Item 4 of the ECG 25 open list — *"single-copy, one disk
failure loses it"* — is closed. A second copy now exists. It is not immutable
and is not claimed to be.

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

   **Now translated rather than repaired.** `docs/provenance/COMMIT_PIN_TRANSLATION_V1.md`
   (#102) carries **326 exact mappings**, both directions, with the derivation
   stated so a third party can re-derive it, and
   `docs/provenance/PROVENANCE_INCIDENT_V1.md` carries the dated chronology. The pins in
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

1. ~~**AWS session expired; the S3 mirror is unverified.**~~ **Reopened and
   closed again on 2026-08-29.** The session had expired for the third time in
   one week; it was renewed and **all three prefixes were verified by content**
   — exact object counts and byte totals, 0 delete markers, 0 overwrites,
   GOVERNANCE retention on the objects, both recorded manifest digests matching,
   984/984 manifest rows resolving, and **24/24 sampled objects downloaded from
   S3 and re-hashed** (§8.0). `snapshot-2026-08-28-4c59ff1` is no longer
   attested only by its own upload.

   **The pattern is the defect, not the outage.** Three open-and-close cycles in
   one week, each discovered by someone happening to look. The guarantee is only
   as current as its last check, so re-verify with a date attached rather than
   inheriting this one.
2. ~~The generative explanation path has never run against a real model~~ —
   **closed 2026-08-25.** Arm B is exercised: `Qwen/Qwen3-1.7B` at revision
   `70d244cc`, greedy on CPU, reported in
   `docs/explanation/EXPLANATION_EVALUATION_REPORT_V1.md`. Fidelity 1.000, **0 claim
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
2b. **The frozen environment is bound to the repository's old directory name.**
   `/home/AI_POC/venvs/tactics/lib/python3.12/site-packages/__editable__.cardiosentinel-0.1.0.pth`
   contains one line —
   `/home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal/src`
   — and the working directory was renamed to `.../tactics/CardioSentinel`.
   `import cardiosentinel` then fails outright, and **nine governance tests fail
   for a reason that has nothing to do with the code they guard**: the
   source-order and capability-gate proofs resolve their own source through
   `inspect.getsource`, which follows the stale path.

   ```
   tests/neural/test_b4b_e2e.py::test_preflight_runs_before_the_claim_in_source_order
   tests/neural/test_b4b_sealed_test_identity.py  (2)
   tests/neural/test_candidate_experiment.py::test_simultaneous_candidate_claims_yield_exactly_one_winner
   tests/neural/test_sealed_test.py  (2)
   tests/neural/test_t1_capability_gate.py  (3)
   ```

   **They report `DID NOT RAISE`, which reads as a guard that stopped working.**
   It is not: with the path restored, all nine pass. A failure mode that makes
   safety guards look disabled is worth more alarm than a normal red test, not
   less.

   **Do not repair this with `pip install -e .`.** The `tactics` interpreter is
   the frozen scientific environment — 335 packages,
   `installed_packages_sha256 = b0fd6ea…`, asserted by the code that consumes it
   — and reinstalling would put that digest at risk to fix a filename. The
   repair is a symlink at the old path, which changes nothing inside the venv:

   ```bash
   ln -s /home/AI_POC/tactics/CardioSentinel \
         /home/AI_POC/tactics/Myocardial-Ischemia-Detection-by-Analysing-ECG-Signal
   ```

   That symlink is in place as of 2026-08-29. **It is untracked infrastructure,
   not repository state** — a fresh clone or a different machine will not have
   it, and will see the same nine failures until either the directory is named
   as the `.pth` expects or the symlink is recreated.

3. **Three empty packages** advertise an architecture the code does not use.
   Repair named in `docs/control-plane/ARCHITECTURE.md` §5, deliberately not done during the
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

- **Runtime trust boundaries were reconciled on 2026-08-29.** Waveform-reader
  failures no longer masquerade as EOF; runtime artifacts are digest-verified;
  evidence-graph lineage distinguishes verified from unavailable locks; and
  provider selection is explicit, with no API-key-driven hosted fallback. The
  authoritative verification record is
  `audits/CARDIOSENTIN_RUNTIME_TRUST_BOUNDARY_HARDENING_V1.md`.
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
analysis of existing evidence, and reporting. No new experiment, no
architecture change, no threshold generation. The sealed-test clause is now moot
rather than lifted — there is nothing left to open.

1. Keep venue-specific preparation outside this repository, in the publication
   workspace described in `CONTRIBUTING.md`. Formatting rules and author
   metadata are not repository state and are not inferred here.
2. Land the runtime trust-boundary and documentation/demo reconciliation branch
   (`fix/runtime-hardening-doc-reconciliation`, 2 commits) — PR #129 is merged
   and this work is not yet on `master`. Do not introduce a second directory
   reorganization.
3. Re-verify the evidence mirror when credentials are next available or the
   existing dated verification becomes too old for the intended claim (§8.1).
4. Keep E1 edge hardware and external validation explicitly open. Neither is
   authorized under the current freeze.

Leaving the freeze requires a named experiment with a pre-registered protocol,
as T1, T2, U1 and W1 each had. The two candidates are the **T2-score ablation**
(what did S4D contribute?) and the **RQ1 no-memory arm** — both require a
re-scoring run, neither can reuse the W1 trick, and **neither has a budget**:
every one-shot access in the programme is spent, so each would need a fresh
human authorization.

---

_Post-`92ed049` content-only archive reconciliation: 2026-08-30, on
`docs/legacy-content-only-reconciliation`, based on GitHub `master`
`92ed049163e4`, with no other open pull request. The historical prototype is
preserved on the locked content-only `legacy` branch, while
`archive/legacy-v0-tree` pins the former full pre-removal snapshot; the
prototype is absent from `master`.
Scientific values were not recomputed; their frozen source records remain
authoritative. Evidence-mirror statements in §8 carry their own verification
dates._
