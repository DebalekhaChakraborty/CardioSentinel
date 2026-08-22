# CardioSentinel Research Execution Handbook, V1.2

**Status:** revision of v1.1 · **Date:** 2026-08-22 · **Against:** `origin/master` `1bbbd47`

---

## §0 Revision notice

**This is a revision, not a reconstruction.** Handbook v1.0 (7 Aug 2026) and v1.1
(8 Aug 2026) were located in `docs/` on 2026-08-22 as Microsoft Word documents
and were read in full before this version was written.

| File | SHA-256 | Size |
|---|---|---|
| `CardioSentinel_Research_Execution_Handbook_v1.0.docx` | `669aecc2533e1604bdf0ed8809ec72c6e7129a93e2edb313292745d480674864` | 72,977 B |
| `CardioSentinel_Research_Execution_Handbook_v1.1.docx` | `9a35813abc2a4e31266c5586bf65405a38681e68eb9bfa9722b39dbdee8b9c43` | 79,725 B |

**Authenticity.** v1.1 §10.2 "Architecture selection rule" exists exactly where
`docs/B4_GLOBAL_ENCODER_SELECTION_V1.md:18` cites it, and v1.1 §10.1 predeclares
the B4-A/B/C/D architecture families, which is precisely what
`docs/B4_ARCHITECTURE_SELECTION_PROTOCOL_V1.md:779` asserts. Both citations
resolve. The documents are what they claim to be.

### 0.1 Numbering is preserved

v1.1 has 38 numbered sections in a phase-organized structure. **This revision
keeps §1–§38 at their original numbers** so every existing citation continues to
resolve. Statuses are corrected in place; new governance material is added as
**§39–§47**, which did not exist in v1.1.

Nothing in v1.1 is deleted. Where v1.1 recorded a plan that reality diverged
from, the divergence is recorded — not the plan rewritten.

### 0.2 Correction to the pre-v1.2 audit record

An audit conducted on 2026-08-22, before these files were located, concluded
that v1.1 was unrecoverable and that its §10.2 survived verbatim as a
three-item evidence hierarchy. **Both conclusions were wrong.**

v1.1 §10.2 is a **Pareto rule**, quoted in full at §7 of this document. The
three-item ranked list appearing in `B4_GLOBAL_ENCODER_SELECTION_V1.md:18` is
**that document's operationalization of §10.2**, not v1.1 text. The citation is
legitimate; the wording is the selection document's own. Any claim that the
ranked hierarchy is verbatim handbook text should be withdrawn.

### 0.3 Revision log

| Version | Date | Change |
|---|---|---|
| 1.0 | 7 Aug 2026 | Initial handbook: phases, architecture candidates, experiment tiers, paper strategy, frozen benchmark state, B0–B3 execution status |
| 1.1 | 8 Aug 2026 | B0–B3 closed; B4-A train/validation locked; B4-B/B4-C validation-only selection gate restored; live execution pointers and step reference cards (§35–§38) added |
| **1.2** | **22 Aug 2026** | **Execution truth through Phase 9.** B4-B selected; P1/M1/M2/U1/T2 retained with U1 split; T1 executed, failed post-claim, recovered under single-use authorization, measured and published. Adds §39–§47: document governance, experiment contract, negative capability, attempt semantics, recovery protocol, pre-registration, reporting discipline, preservation, amendment process. Corrects the §10.2 citation record (§0.2) |

---

## §1–§4 Contract, architecture, benchmark state, roadmap — unchanged in substance

v1.1 §1's thirteen non-negotiable rules stand **without amendment**. Three have
since been tested by events and are worth restating:

- *"Softmax is not calibration"* / *"Raw sigmoid is not calibrated probability"*
  (§1, §37.7). **Vindicated.** T2 scores are `sigmoid(current_window_t2_logit)`
  with `score_is_calibrated_probability: false`. §45 makes this binding.
- *"EDB is not automatically independent."* **Vindicated.**
  `CROSS_DATASET_PROVENANCE.md` documents ten LTSTDB recordings from the same
  Pisa collection, with record-level correspondences.
- *"All runs are traceable."* Honoured across all fourteen experiment locks.

§1.1 remains the operative fallback: **simplify by removing optional technology,
never by weakening experimental integrity.**

§33.2's core rule is the sentence this entire revision serves:

> *"We are allowed to try advanced techniques. We are only allowed to claim the
> techniques that survive controlled experiments."*

---

## §5–§9 Phases 0 through 3B-1 — COMPLETE, unchanged

Repository governance, dataset integrity, causal pipeline, frozen benchmark and
split, classical baselines. All complete as v1.1 recorded.

**One status hardening.** §9's B0–B3 sealed-test access is now **CONSUMED**. That
chain is spent, cannot be reopened, and **cannot be extended to neural claims.**

---

## §10 Phase 3B-2 — Architecture selection: **COMPLETE** (was ACTIVE)

### 10.1 Neural architecture candidates — outcome

v1.1's predeclaration stands as written. Outcomes appended:

| Candidate | v1.1 selection logic | Implementation | Outcome |
|---|---|---|---|
| **B4-A** CNN/TCN | *"Required reference."* | `neural/model.py:66` `B4CompactCNN`, 87,089 params | Trained, 8 epochs, `COMPLETE` @ `21a38ec`. **Rejected**; retained as historical comparator |
| **B4-B** CNN+Transformer | *"Keep only if gain justifies parameters/latency."* | `neural/candidates.py:159` `B4BTransformerCNN`, 309,809 params | Trained, 6 epochs, `COMPLETE` @ `b27d528`. **SELECTED global encoder** (PR #15, 10 Aug 2026) |
| **B4-C** CNN+SSM | *"High-value candidate."* | `neural/candidates.py:296` `B4CSSMCNN`, 155,313 params | Trained, 6 epochs, `COMPLETE` @ `b27d528`. **Rejected** |
| **B4-D** Hybrid | *"Preferred advanced experiment if schedule permits."* | **none** | **Withdrawn unless reauthorized** — see below |

**B4-D status change.** v1.1 called it a preferred advanced experiment.
`B4_ARCHITECTURE_SELECTION_PROTOCOL_V1.md:26` subsequently narrowed it to
*"Conditional; **not authorized**"*, and §795 defers it to the temporal phase. It
has no code, no experiment ID, and is absent from
`CANDIDATE_SELECTORS = {"b4b", "b4c"}`. **It is not a pending work item.**
Reactivating it requires a new authorization, not merely schedule room.

**B4-C does not satisfy T2.** Load-bearing and easily lost. B4-C applies a
state-space recurrence **inside one completed 10-second window**, over the 79
tokens from the convolutional front end; its state is created at window start and
discarded at window end. T2 carries state **across successive windows**. B4-C's
rejection says nothing about T2, and T2's retention says nothing about B4-C.

### 10.2 Architecture selection rule — unchanged, quoted in full at §7

---

## §11–§14 Phases 4, 4B, 5, 5B — outcomes

| v1.1 phase | Status | Outcome |
|---|---|---|
| **§11 Phase 4** Physiology-guided | **COMPLETE** | P1-A control vs P1-B fusion; **P1-B retained** with a recorded rate-related challenge FPR degradation of +0.00603 that must travel with any P1 claim |
| **§12 Phase 4B** Foundation-model distillation | **NOT STARTED** | Conditional in v1.1; never begun. No code, no run |
| **§13 Phase 5** Patient dual-timescale memory | **COMPLETE** | M1S/M1D/M1L; **M1L retained** on development evidence only. M1-v1 failed twice; both failures documented rather than silently retried. M1-v2 is the sole canonical evidence |
| **§14 Phase 5B** Contamination-safe adaptation | **COMPLETE** | M2-0 vs M2-G; **M2-G retained**. Canonical evidence is **recovery2**; attempt-1 and recovery-1 failure receipts are retained and are part of the record |

---

## §15 Phase 6 — Calibration and routing: **SPLIT RETENTION**

**This is the single most misreported result in the programme.**

| Component | Outcome |
|---|---|
| Platt calibration `g(s) = sigmoid(a·z(s) + b)` | ✅ **RETAINED** as the prospective calibration mapping for genuinely unseen data. Produces `oof_calibrated_probability_p_t`, a frozen T1 row input |
| Symmetric window-level selective router at `c_star = 0.90` | ❌ **`Retained: false`** — at that operating point the router disproportionately escalates positive-label cases |

The rejected router is **preserved, not deleted**. Preservation is provenance,
not retention. v1.1 §37.7's exit gate — *"risk decreases sensibly as coverage
falls"* — was **not met**, and the handbook's own instruction in that case was to
report the limitation. That is what happened.

**Consequence for §18 and for the paper:** edge/cloud routing does not exist. Any
document claiming it is complete is wrong.

### 15.1 Conformal prediction (U2) — **DECLARED OPTIONAL, NEVER BEGUN**

v1.1 called U2 *"strongly recommended"*.
`U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` §12 subsequently ruled:

> *"U2 conformal prediction does NOT automatically begin. U2 remains optional."*

Zero code, zero runs, zero evidence. **Its non-execution is a recorded decision,
not an omission**, and it must not appear in any capability list.

---

## §16 Phase 6B — Confounder-aware multi-task: **NOT STARTED**

Tier 2 in v1.1. Never begun. RQ7 is unanswered.

---

## §17 Phase 7 — Longitudinal temporal and episode reasoning: **EXECUTED**

v1.1 treated T2 and T1 as one phase. In execution they became two, with
separate run roots.

### 17.1 T2 — longitudinal modelling: **COMPLETE**

`CausalS4DLongitudinal` vs `CausalGRULongitudinal`, both trained
(`neural/t2_models.py`), both scored in a **single causal pass** over 492,904
identical rows. **S4D retained** as the continuous score under a rule frozen in
advance (`selection_basis: pooled_primary_validation_auprc`).

The outer validation is a **consumed one-shot artifact** (`validation_accessed:
true`). No rerun is authorized.

### 17.2 T1 — episode state machine: **EXECUTED, MEASURED, FROZEN**

Frozen protocol, **no trainable parameters**. NORMAL → WATCH → EVENT → RECOVERY
with persistence and hysteresis, exactly as v1.1 §37.8 specified.

Two executions:

```
t1-v1-development              @ c538181   CONSUMED — failed post-claim at stage 24
t1-v1-measurement-continuation @ 61704aa   COMPLETED under authorization b40b4ac
```

Both directories immutable. **No further T1 attempt is authorized.**

### 17.3 Where execution diverged from v1.1 — recorded, not rewritten

**v1.1 §25.3 specified episode-level metrics** — episode sensitivity, episode
PPV, false alarms per hour, onset detection delay, temporal IoU. **The T1
measurement reports** pooled and per-subject `episode_f1`, window MCC, and signed
onset offsets. **False alarms per hour and temporal IoU were never computed.**
This is a gap between plan and evidence, not a substitution to be glossed.

**v1.1 §37.8's exit gate** — *"Temporal reasoning must reduce isolated false
alarms / improve episode behavior while preserving prompt event detection"* — is
**a two-armed criterion that was never evaluated.** No window-only comparator arm
was run on the held-out subjects. RQ4 therefore remains **unanswered**, and no
improvement claim may be made (§46, forbidden claim 6).

---

## §18 Phase 8 — Edge / hardware-in-the-loop: **NOT STARTED**

v1.1 §37.9 targets a Raspberry Pi 4B with ≥30 latency runs, peak RAM, CPU, model
size, bytes transmitted, and outage behaviour. **None exists.**
`src/cardiosentinel/edge/__init__.py` is a one-line docstring. There is no
inference or serving path anywhere — no `predict()`, no ONNX, no TorchScript.

`B4_RESOURCE_BENCHMARK_V1.md` measured latency and parameter counts on a **fixed
benchmark host**. Per v1.1's own *"Do not invent"* rule, **those are not edge
measurements** and must never be presented as such.

---

## §19–§22 Phases 9–12 — Ablation, consolidation, paper, reproducibility freeze

All **NOT STARTED**. §19.1's ablation ladder is unbuilt; every ablation requires
new authorized runs. §22's reproducibility freeze has two known defects recorded
at §46.

---

## §23 Experiment tiers — status

Tier 1 core is complete except E1. Tier 2 (§16 multi-task, §12 distillation) and
Tier 3 (§17.1 HMM/CRF comparator) were never begun. Under §1.1 this is the
**correct** outcome: optional technology was dropped, integrity was not.

---

## §24 Research questions — evidence status

| RQ | Question | Status |
|---|---|---|
| **RQ1** | Does patient-specific memory reduce false alarms without sacrificing sensitivity? | ❌ **Unanswered.** No no-memory arm at episode level |
| **RQ2** | Can continual personalization be made contamination-safe? | ⚠️ **Partial.** M2-G retained on development evidence; no contamination-stress comparison at episode level |
| **RQ3** | Can uncertainty reduce cloud dependence without unsafe local decisions? | ❌ **Answered negatively.** The router was evaluated and rejected |
| **RQ4** | Does longitudinal/episode reasoning improve monitoring quality? | ❌ **Unanswered.** One-armed measurement; no window-only comparator |
| **RQ5** | Can the selected model operate efficiently on edge hardware? | ❌ **Unanswered.** E1 not started |
| **RQ6** | Does foundation-model knowledge improve the compact student? | ❌ **Not started** |
| **RQ7** | Can confounder-aware supervision reduce false ST alarms? | ❌ **Not started** |

**Not one of the seven research questions is affirmatively answered.** RQ3 is
answered negatively, which is a real result and should be reported as one. This
table is the honest basis for §46 and for any paper framing.

---

## §25 Metric hierarchy — unchanged, with one binding addition

§25.1–§25.5 stand. §47 adds reporting rules that constrain **how** these metrics
may be stated, learned from the T1 measurement.

---

## §26–§33 Paper strategy, decision matrix, snapshots, core rule — unchanged

§29's execution snapshot (8 Aug 2026) is superseded by §39. §33.3's next
checkpoint is **achieved**: the encoder family was frozen on validation only, and
the claim-bearing ladder ran through to episode reasoning.

---

## §34 Revision log — see §0.3

---

## §35–§38 Execution reference, control board, step cards, go/no-go

§35.1's seven-point preflight and §35.2's prompt anchor remain in force.

**§35.3 test-access choreography — extended by execution.** v1.1's rule was:
architecture family selected on validation only, then one-shot test access *may*
be authorized, and *"no test result may be used to return to architecture
selection."* In practice `B4_TEST_DEFERRAL_DECISION_V1.md` went further: B4-B
sealed-test access is **eligible but intentionally NOT authorized.** §43 records
the current chain state.

§37's step cards remain the best per-phase operational reference. §37.7's
non-negotiable — *"Raw sigmoid is not calibrated probability"* — is now binding
policy at §45.

---

# New sections added in v1.2

## §39 Current execution snapshot — 22 August 2026

**`origin/master` `1bbbd47` · working tree clean**

**Completed:** B0–B3 classical (test consumed) · B4-A/B/C with **B4-B selected** ·
P1-B retained · M1L retained · M2-G retained · U1 **calibration retained, router
rejected** · T2 S4D retained · **T1 executed, failed, recovered, measured,
published**.

**Active:** T2 arm-comparison analysis. Pre-registered in
`docs/T2_ARM_COMPARISON_ANALYSIS_PLAN_V1.md`. **No T2 measured value has been
read.** The first read requires explicit human authorization and has not been
given.

**Future:** external validation strategy · calibration reliability analysis
(closes RQ3's weakest evidence with no new run) · ablation strategy design ·
inference pathway.

**Published T1 result**, with the labelling §47 requires:

| | |
|---|---|
| Registered primary — subject-macro mean `episode_f1` | **0.2524** |
| 95% subject-bootstrap interval | **[0.0826, 0.4415]** |
| `pooled_episode_f1` — episode-weighted, **descriptive, not what the interval brackets** | 0.3423 |

Twelve held-out LTSTDB subjects, cross-fitted, subject-disjoint. **Seven of
twelve score zero**, for two incomparable reasons: three subjects have **no
reference episodes at all** (false-alarm burden), four missed real episodes.

## §40 Document governance model

Three classes, one rule each.

**FROZEN** — `_V1` suffix, carries a digest. **Never edited.** Correct by
superseding document or dated addendum appended below the frozen body, the
pattern `recovery/T1_CONTINUATION_PREAUTHORIZATION.md` §10 establishes. **34
documents.** A frozen document may become historically stale without becoming
wrong: `B4_ARCHITECTURE_SELECTION_PROTOCOL_V1.md:21–33` calls B4-B and B4-C *"not
implemented"* — true at freeze, false now. Quote such tables **with their date**.

**CONTRACT** — freeze language or digests, no `_V1` suffix. **Append-only**; a
semantic change requires a new version file.

**LIVING** — a cache of repository truth. **Regenerated wholesale**, never
hand-patched.

### 40.1 Classification of previously ambiguous documents

| Document | Class |
|---|---|
| `DATASET_CONTRACT.md` · `SIGNAL_PROCESSING_CONTRACT.md` · `METRICS_PROTOCOL.md` · `ANNOTATION_SEMANTICS.md` · `CROSS_DATASET_PROVENANCE.md` | **CONTRACT** — bind identity, meaning or digests relied on by frozen locks |
| `M1_DUAL_MEMORY_PROTOCOL_V2.md` | **CONTRACT** — already a versioned amendment |
| `M1_STAGE1_ATTEMPT1_FAILURE.md` · `M1_STAGE1_ATTEMPT2_FAILURE.md` · `M1_ATTEMPT2_VALIDATION_ADMISSIBILITY_CENSUS.md` | **CONTRACT** — failure records, append-only, never revised |
| `PHASE3B1_CLASSICAL_BASELINE_RESULTS.md` | **CONTRACT** — reports consumed sealed-test evidence |
| `T1_CONTINUATION_PREAUTHORIZATION.md` | **CONTRACT** — already demonstrates append-only via §10 |
| `t1_episode_reasoning.md` | **CONTRACT** — design note under the frozen T1 protocol |
| `README.md` | **LIVING** |
| **This handbook** | **LIVING** |

**LIVING:** `CURRENT_STATE.md`, `IMPLEMENTATION_PLAN.md`, `RESEARCH_SCOPE.md`,
`REPO_AUDIT.md`, `DATA_SPLIT_POLICY.md`, `EXPERIMENT_CONTRACT.md`, `README.md`,
this handbook.

## §41 Experiment contract

Every experiment is a **code constant** bound to a run directory outside version
control. There is no YAML experiment registry; configuration is frozen in code so
it cannot drift.

| `experiment_id` | Code constant | Run directory | Lock file |
|---|---|---|---|
| `B0…B3_*_v1` | `models/baselines.py` | `phase3b-classical-v3/` | `experiment_lock.json` |
| `B4_raw_compact_cnn_v1` | `neural/experiment.py:82` | `phase3b2-b4-v1/` | `EXPERIMENT_LOCK.json` |
| `B4B_cnn_transformer_v1` | `neural/candidates.py:33` | `phase3b2-architecture-v1/` | `EXPERIMENT_LOCK.json` |
| `B4C_cnn_ssm_v1` | `neural/candidates.py:34` | `phase3b2-architecture-v1/` | `EXPERIMENT_LOCK.json` |
| `P1A_neural_head_v1`, `P1B_phys_fusion_v1` | `neural/physiology_fusion.py` | `phase4-p1-physiology-v1/` | `EXPERIMENT_LOCK.json` |
| `M1S/M1L/M1D_*_v2` | `neural/patient_memory.py` | `phase5-m1-dual-memory-v2/` | `EXPERIMENT_LOCK.json` |
| `m2-v1-development-two-arm`, `…-recovery1`, `…-recovery2` | `neural/m2_development_run.py` | `phase6-m2-development-v1/` | `M2_EXPERIMENT_LOCK.json` |
| `u1-v1-development` | `neural/u1_development_run.py` | `phase7-u1-development-v1/` | `U1_EXPERIMENT_LOCK.json` |
| `t2-v1-training` | `neural/t2_persistence.py` | `phase8-t2-development-v1/` | `T2_TRAINING_EXPERIMENT_LOCK.json` |
| `t2-v1-outer-validation` | `neural/t2_persistence.py` | `phase8-t2-development-v1/` | `T2_OUTER_VALIDATION_EXPERIMENT_LOCK.json` |
| `t1-v1-development` | `neural/t1_continuation_spec.py:154` | `phase9-t1-development-v1/` | **none — see 41.2** |
| `t1-v1-measurement-continuation` | `neural/t1_recovery_amendment.py:53` | `phase9-t1-continuation-v1/` | `T1_EXPERIMENT_LOCK.json` |

### 41.1 Four lock naming conventions

| Pattern | Used by |
|---|---|
| `EXPERIMENT_LOCK.json` | B4, P1, M1 |
| Prefixed `<PHASE>_EXPERIMENT_LOCK.json` | M2, U1, T1 |
| T2 role-qualified `T2_<ROLE>_EXPERIMENT_LOCK.json` | T2 |
| **lowercase** `experiment_lock.json` | B0–B3 classical |

`find -name "*EXPERIMENT_LOCK*.json"` returns **14** and silently misses all four
classical runs. **Any lock audit must be case-insensitive.**

### 41.2 Absence of a lock is evidence

`t1-v1-development` has no lock: it failed post-claim and never reached
promotion. Its truth lives in `recovery/T1_FAILURE_RECEIPT_RECONSTRUCTED.json`.
**A missing lock records a failed run, not a missing run.**

### 41.3 Result artifact naming

Classical runs emit `RESULTS_SUMMARY.json`; **neural runs do not.** Their
equivalent is `VALIDATION_METRICS.json` plus `EPOCH_HISTORY.json`. There is no
tensorboard or wandb logging anywhere — zero event files, zero code references.
Evidence is JSON artifacts and digests only.

### 41.4 Phase numbering caution

**Handbook phase numbers and run-directory phase numbers do not correspond.**
v1.1 Phase 5B is `phase6-m2-*`; Phase 6 is `phase7-u1-*`; Phase 7 spans
`phase8-t2-*` and `phase9-t1-*`. Cite run directories by path, never by inferred
phase number.

## §42 Data governance

**LTSTDB 1.0.0** — 86 records / 80 subjects, materialized, the primary evidence
source. **EDB 1.0.0** — parser exists at `data/edb.py`; **no EDB data is on disk
and no neural phase uses it.**

Split `protocols/splits/ltstdb_v1.json`, `split_sha256 66e25d77…`, **seed 2026**,
subject-level, deterministic greedy burden balancing: train 56 subjects / 60
records · validation 12 / 13 · test 12 / 13. Windows **10 s, 5 s stride**, causal.

**EDB provenance restriction.** Ten LTSTDB recordings come from the same Pisa
collection as EDB, with verified record-level correspondences. **EDB is not a
clean external cohort for any LTSTDB-trained model.** Any future external
validation requires a contamination audit completed **before** data reaches disk.

## §43 Sealed-test choreography — current chain state

**One-shot semantics.** Single use per chain. Once opened it is consumed: no
second evaluation, no re-tuning, no partial access.

| Chain | State |
|---|---|
| **B0–B3 classical** | **CONSUMED** in Phase 3B-1 |
| **B4 / neural** | **UNOPENED** — eligible, deliberately deferred |

*"TEST is sealed"* is therefore **half true** and must never be stated
unqualified. Every downstream lock records `test_evidence_used: false` or
`sealed_test_state: unopened`.

**Do not** execute evaluate-locked-test; create `TEST_ATTEMPT.json`; read, open
or hash a B4 test cache or waveform; inspect B4 test labels; calculate B4 test
metrics; or inspect test predictions.

**Opening the neural test before external validation spends the final firewall on
a result no cohort can corroborate.** It should be last, not next.

## §44 Negative capability and safety gates

Conventional testing shows what code *does*. Negative capability proves what code
**cannot do**. `T1ContinuationNegativeCapabilityGate` enforces three layers.

**Layer 1 — structural.** The proven import graph may not *name* a forbidden
module:

```
FORBIDDEN_MODULES = (t1_fold_evaluator, t1_development_run, t1_canonical_driver,
                     t1_composition, t1_engine, t1_stream)
```

**Layer 2a — runtime.** Named modules must be absent from `sys.modules`:

```
NEVER_LOADED_MODULES = (t1_fold_evaluator, t1_canonical_driver,
                        t1_composition, t1_engine, t1_stream)
```

**The two sets answer different questions and differ by exactly one member.**
`t1_development_run` is forbidden to *name* but not required to be *absent*,
because the §16 label authority legitimately drags it into the process; its three
entry points carry real call counters instead. A test asserts the two sets
partition the forbidden set exactly. **Never assume they are the same list.**

**Layer 3 — evidence.** Promoted artifacts carry zero-capability counters. The
completed continuation attests `fold_evaluations 0`, `policy_selection_calls 0`,
`state_machine_invocations 0`, `threshold_generation_calls 0`,
`state_transitions_regenerated false`, `test_accessed false`,
`sealed_test_state unopened`.

**Continuation architecture.** `t1_assembly` is deliberately unused: it binds no
forbidden name but imports `t1_development_run`, which would grant transitive
reach the Layer 1 proof does not inspect. Four helpers are re-implemented with
equivalence tests. **Not duplication to be cleaned up.**

**The leakage guarantee is inherited, not re-enforced.** The continuation invokes
no transition function, so `T1_FORBIDDEN_TRANSITION_INPUTS` does not run in its
process. The guarantee comes from the predecessor run via the digest-verified
state trace `cf74f00a…`. Any paper must say it that way.

**"Unprovable by construction" is usually false.** ECG 12 asserted the assembled
path could not be exercised without arming. It could: sandbox the run root,
synthesize labels, run a subprocess. If you write *"irreducible residue"*, check
whether a sandbox reduces it.

## §45 Attempt semantics and recovery protocol

**One attempt.** A canonical experiment is authorized for exactly one execution.

**The claim boundary.** An attempt is consumed when it crosses `_claim()`. Before
that line a refusal leaves the authorization intact; after it, failure consumes
the attempt permanently. The T1 continuation's first invocation raised at
`runner.py:282`, **six lines before `_claim()` at `runner.py:288`**. Read that as
a narrow escape, not a system working as designed: the stages were tested and the
junctions were not — the same defect class that consumed the canonical attempt at
stage 24.

**NO AUTOMATIC RETRY UNDER ANY CIRCUMSTANCE.** No `--force`, `--retry`,
`--reset`, `--overwrite` or `--fresh-seed` may be added to any canonical runner.

**Failure consumption.** A failed post-claim attempt is consumed, its directory
immutable, its `RUN_STATUS` preserved exactly as the failure left it.
`t1-v1-development` still reads `STARTED` with every flag false; the truth is
reconstructed into a receipt rather than overwritten.

**Recovery is not retry.** A continuation may be authorized subject to all of:
a frozen amendment defining what may be recovered; a pre-authorization record
written **before** arming, separating technical readiness from execution
authorization; **explicit human authorization recorded as a commit** — the only
edit that arms the path; **single use** — failure after claim consumes it, and no
successor identity is authorized; **consumption of persisted evidence only**,
with predecessor digests verified and no model run; and **the consumed attempt
directory is never modified.**

**A record cannot contain its own hash.** Authorization needed two commits — flip,
then record the flip's SHA. The experiment lock records six artifact digests, not
seven, for the same reason.

**Arming a flag can arm the test suite.** With the flag `True` on disk, refusal
tests stop refusing and a routine `pytest` could consume the attempt.
`tests/neural/conftest.py` forces it `False` for the session. **Any future arming
must re-verify that guard.** Once spent, a flag left `True` is a **spent token,
not a live permission.**

**Standing constraints:** no M2 rerun · no U1 rerun · no T2 rerun · no T1 fold
retry · no second continuation · never install, upgrade or downgrade anything in
the frozen `tactics` interpreter (Python 3.12.6, 335 packages,
`installed_packages_sha256 = b0fd6ea…`, verified via
`provenance.dependency_environment()`, not a pip-freeze hash).

## §46 Pre-registration and reporting discipline

**The plan precedes the read.** An analysis plan is written and approved before
any measured value is opened. Only structure — key names, shapes, digests,
definedness counts — may be inspected while writing it.

**Human authorization gate.** The first read of measured values is an explicit,
recorded human decision, never a side effect of a status check.

**Post-hoc labelling.** Anything decided after values are visible is labelled
**post-hoc** where it appears and changes no pre-registered number.

**Tightening is permitted, loosening is not.** A pre-read amendment removing a
reportable number is conservative and allowed; any relaxation must be named,
justified and confined.

**The ordering is the claim** — plan, report, post-hoc, in git history, in that
order.

### 46.1 Reporting rules

**Undefined stays undefined** — never omitted, never zero-filled. `window_mcc` is
undefined on an empty confusion margin; a subject with no matched episodes has no
latency. Zero would read as a real measurement. Per-subject tables are always
complete.

**No mean over a data-determined subset.** If a metric is defined for only some
subjects, no subject-macro mean of it is reported, with or without an attached
`n`.

**Estimand labelling.** Pooled and subject-macro statistics are different
estimands and are never printed adjacently as interchangeable. An interval is
printed only beside the quantity it brackets, with its `claim_scope` attached.

**Defined is not meaningful.** A subject with zero reference episodes yields an
F1 of exactly 0.0 — a false-alarm penalty, not a detection failure. Availability
analysis must check both.

**No significance language.** No p-value, no hypothesis test. Bootstrap intervals
describe between-subject variation conditional on a fitted procedure.

## §47 Preservation, reproducibility, and amendment

**Immutable evidence philosophy.** A promoted run directory is never modified,
regenerated or cleaned up. Digests bind artifacts to the run that produced them;
a lock omits its own digest because a file cannot contain its own hash.

**Manifests** record `sha256  size  mtime_epoch  relative_path` per file.

**Backup.** 23.08 GiB across 785 files, gitignored, on one disk, mirrored to
`s3://cardiosentinel-evidence-341181499761/snapshot-2026-08-22-1bbbd47/` — 786
objects, 24,779,296,980 bytes, manifest
`dd42385631ded57320116f82d14124c99d3ffb25ea4c6ec046c69b0d13d377f6`, verified by
object count, byte total, manifest round-trip and a 16/16 sample re-hash.
Versioning · Object Lock GOVERNANCE 365 days · SSE-S3 · public access blocked.

**mtime preservation is mandatory.** Immutability is asserted in timestamps —
*"20 files at `2026-08-21T19:57:57`"*. Object storage assigns its own
`LastModified`, so **restoring bytes is not restoring evidence state**:

```bash
while read -r sha size mtime path; do touch -d "@$mtime" "$path"; done < MANIFEST_SHA256.txt
```

**Known reproducibility defects.** The T1 report generator is untracked and lives
only in a scratch directory; regenerating from a stale copy would silently revert
merged corrections. Thirteen tests assert the continuation run root is absent and
fail on any machine holding the evidence while passing in CI, where the directory
is gitignored — **the local suite cannot currently signal a regression.** Both
are open, recorded here rather than resolved.

### 47.1 Amendment process

**Revision** produces the next version from a predecessor that can be read: read,
diff, supersede, and state what changed. **This document is a revision.**

**Reconstruction** produces a version from a predecessor that cannot be read. It
must open with a notice naming the missing version, listing every surviving
source with its fidelity, and stating each section's authority level.

Rules: the handbook never overrides a frozen document · it grants no scientific
permission and authorizes no execution · superseded versions are retained, never
deleted · original numbering is preserved so citations resolve · **derived content
is never presented as recovered content.**

---

## Appendix A — Publication claim boundary

Forbidden in any manuscript, abstract, figure caption or presentation.

| # | Forbidden claim | Why |
|---|---|---|
| 1 | **Causal inference** | *"Causal"* here means **temporal non-anticipation** — `next_state` reads "nothing ahead of it". Use *"causally ordered streaming"* or *"non-anticipative"*, defined at first use |
| 2 | **Deployment readiness** | No `predict()`, no ONNX, no TorchScript, no serving path (§18) |
| 3 | **Generalization** beyond LTSTDB | One dataset, 12 validation subjects; EDB is not independent (§42) |
| 4 | **Clinical utility** | Detection, not diagnosis (§1) |
| 5 | **Edge performance** | Benchmark-host numbers are not edge measurements (§18) |
| 6 | **Improvement** — improved, helped, outperformed, better | Every comparative verb needs a second arm. T1 is one-armed; RQ4 is unanswered (§17.3, §24) |
| 7 | **Memory contribution** | RQ1 unanswered; no no-memory arm |
| 8 | **S4D superiority without selection context** | The pooled AUPRC contrast **is** the selection rule. The paired difference is unbiased; the winner's absolute figure is not. Say *"the predefined selection rule selected S4D based on the observed validation contrast"* |
| 9 | **Calibrated probability for T2 scores** | `score_is_calibrated_probability: false`. v1.1 §1 already forbade this |
| 10 | Encoder or calibration **contribution** | No ablations (§19) |
| 11 | **Subgroup** performance | `join_performed: false` |
| 12 | **Test** performance | Neural chain unopened; classical chain spent and not extensible (§43) |
| 13 | **Statistical significance** | The bootstrap is not a hypothesis test |
| 14 | *"Selective routing implemented / deployed"* | `Retained: false` (§15) |
| 15 | *"Edge/cloud routing complete"* | The router it refers to was rejected |
| 16 | *"Conformal prediction"* / U2 in any capability list | Declared optional, never begun (§15.1) |
| 17 | *"Early detection"*, *"warning time"*, *"predictive lead time"* | Matching is overlap-only with no tolerance window and no run durations are stored; a negative onset offset does not establish anticipation |
| 18 | *"Median patient onset latency"* | The statistic is a median over **episodes**, not subjects |
| 19 | *"Mean MCC across subjects"* | Defined for 5 of 12; forbidden by §46.1 |
| 20 | *"B4-C provides longitudinal modelling"* | Window-internal recurrence is not T2 (§10.1) |
| 21 | *"False alarms per hour"* or *"temporal IoU"* for T1 | **Specified in v1.1 §25.3 but never computed** (§17.3) |

**Claim 21 is new in v1.2** and replaces the pre-v1.2 audit's provisional claim
about unprovable pre-declaration. That concern is **resolved**: v1.1 §10.1 does
predeclare the B4-A/B/C/D families, and the handbook is now in the repository, so
the prospectivity of the B4-B selection is substantiable on request.

---

_Research Execution Handbook v1.2 — a revision of v1.1 (8 Aug 2026). Section
numbering §1–§38 preserved from v1.1; §39–§47 new. Revised against
`origin/master` `1bbbd47` on 2026-08-22. This handbook grants no scientific
permission and authorizes no execution._
