# CardioSentinel Research Execution Handbook, V1.3

**Status:** revision of v1.2 · **Date:** 2026-08-23 · **Against:** `origin/master` `d5a86ce`

---

## Executive summary

**One research question is now affirmatively answered, and the answer is
bounded.** v1.2 stated that not one of the seven was — that sentence was true
when written and is false now. It is the single most important correction in
this revision, and §50's publication argument is re-made from the new premise
rather than left standing on the old one.

| RQ | One-line status |
|---|---|
| **RQ4** — does longitudinal / episode reasoning improve monitoring quality? | **Supported (bounded).** W1 ran the two-armed comparison v1.1 §37.8 always required. Never write "Supported" unqualified — see §17.4 |
| **RQ3** — can uncertainty reduce cloud dependence without unsafe local decisions? | **Answered negatively.** The router was evaluated and rejected. A real result, and the only *clean* answer the programme owns |
| **RQ2** — can continual personalization be made contamination-safe? | **Partial.** M2-G retained on development evidence; no contamination-stress comparison at episode level |
| **RQ1, RQ5, RQ6, RQ7** | **Open.** RQ1 needs re-scoring, not a derived analysis (§24) |

**Three things a reader should not take away from that table.**

1. **RQ4's bound is load-bearing.** Both W1 arms ran at thresholds selected with
   the state machine in the loop. A well-tuned memoryless rule was never tested,
   so the finding is that episode reasoning helps *at one operating point*, not
   that it helps.
2. **The T2 contrast's interval includes zero.** S4D was selected over GRU by
   the predefined rule on a pooled AUPRC difference of 0.093215, and the 95%
   paired subject-bootstrap interval on that difference is
   **[-0.015229, 0.148951]**. The selection is valid; a superiority claim is
   not.
3. **Exactly one one-shot budget remains unspent** — the B4 / neural sealed
   test. Everything else is consumed. §51 is the ledger, and it is the most
   decision-relevant page in this document.

**One finding generalises past ECG.** Three headline numbers — T1's
subject-macro `episode_f1`, T2's subject-macro AUPRC, U1's ECE — each concealed
a denominator that was not what it looked like, in three different experiments,
found by three different checks, and never by the metric itself. §49.8.

**What the programme actually owns** is an evidence apparatus: pre-registration
that recorded refuted predictions as refuted, one-shot gates that were honoured
under pressure, a real post-claim failure and its authorized recovery, and
digest-bound provenance throughout. §50 still recommends the methodology paper,
now for a better reason than "there is no headline".

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

**v1.3 keeps the same discipline.** §1–§50 hold their numbers; §51 is new;
§17.4–§17.6 and §43.1 are new subsections under existing numbers, added rather
than renumbering anything. §24's table is the one thing replaced outright, and
§24 says so in its own first line.

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
| 1.2 | 22 Aug 2026 | **Execution truth through Phase 9.** B4-B selected; P1/M1/M2/U1/T2 retained with U1 split; T1 executed, failed post-claim, recovered under single-use authorization, measured and published. Adds §39–§47: document governance, experiment contract, negative capability, attempt semantics, recovery protocol, pre-registration, reporting discipline, preservation, amendment process. Corrects the §10.2 citation record (§0.2) |
| **1.3** | **23 Aug 2026** | **The evidence layer closes and RQ4 is answered.** T2 arm comparison read and published; W1 window-only comparator executed, answering RQ4 **Supported (bounded)** and refuting two registered predictions; U1 per-bin reliability read; external validation audited to a negative finding. Replaces §24 outright, re-argues §50 from the changed premise, corrects Appendix A claim 6, and adds **§51**, the experiment ledger with a consumed column |

### 0.4 What v1.3 changes, and what it leaves alone

**Changed, because merged evidence contradicted it:** the executive summary is
new · §17.3's RQ4 verdict · §24 replaced outright · §39 re-snapshotted · §43
gains the evidence that now backs its argument · §49 gains four findings ·
§50 re-argued · Appendix A claim 6 rewritten, claims 22–25 added · §51 new.

**Unchanged, deliberately:** §1–§16, §18–§23, §25–§38, §40–§42, §44–§48. v1.2's
statuses there survived contact with four new documents. Where a v1.2 sentence
is now wrong it is corrected in place and the correction is visible; nothing is
quietly deleted, per §0.1.

**This handbook is not a frozen document.** §40 classes it as LIVING. The
frozen protocols, retention decisions, pre-registrations, amendments and reports
it cites are the record; this document is a map of them and is revised when
they move.

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

**The measured values have since been read**, under explicit authorization, at
merged commit `4018435`. `docs/T2_ARM_COMPARISON_REPORT_V1.md` is the published
read; the numbers and their boundary are at §49.4. That first read is itself a
consumed budget (§51).

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
a two-armed criterion. **v1.2 recorded that it had never been evaluated. It has
now been evaluated.**

### 17.4 W1 — the window-only comparator: **EXECUTED, RQ4 ANSWERED (BOUNDED)**

Pre-registered in `docs/W1_WINDOW_COMPARATOR_PREREGISTRATION_V1.md`, executed at
merged commit `f998bf5` under a §6 authorization to re-open the held-out labels
once. `docs/W1_WINDOW_COMPARATOR_REPORT_V1.md` is the published read.

| | |
|---|---|
| Arm T1 — state machine, subject-macro `episode_f1` | **0.2524** — reproduces the published T1 value exactly |
| Arm W — memoryless window rule, subject-macro `episode_f1` | **0.0603** |
| **Difference, Arm T1 − Arm W** | **0.1921** |
| **95% paired subject-bootstrap** | **[0.0505, 0.3455]** — **excludes zero** |

**The bound, which is not optional.** Both arms ran at thresholds selected
*with the state machine in the loop*. The promoted policy `qw0.9_qe0.99_FAST`
binds the quantile levels together with the `FAST` persistence profile, whose
`event_confirm_windows = 2` is a **state-machine parameter** that a memoryless
rule does not implement. **A well-tuned memoryless rule was never tested.**

So RQ4 reads **"Supported (bounded)"** and never "Supported". The supported
claim is that episode reasoning improves episode-level agreement relative to a
memoryless window rule **on identical rows, at this operating point**. It is not
a claim about episode reasoning in general.

### 17.5 Two registered predictions were refuted, and reported as refuted

This is the part of W1 worth a paper section.

1. **The alert-row dominance limb was false.** The pre-registration reasoned
   that Arm T1 would produce fewer alert rows. T1's `EVENT` hysteresis marks
   rows where the event condition does not hold, so T1 produces **more alert
   rows in fewer, longer runs**. The run-dominance limb held; the row limb did
   not.
2. **The "near-zero difference expected" aggregate prediction was wrong.** It
   reasoned only about the seven zero-scoring subjects and ignored the five that
   actually score, where Arm W's flood of runs collapses the score.

**A pre-registration's reasoning can be wrong while its discipline is right.**
Both were reported as written, which is the only thing that makes registering a
prediction worth anything. §46 is amended by nothing here — it already required
this — but §50 should cite it, because it is the clearest available evidence
that the machinery does what it claims.

### 17.6 What W1 does **not** answer

`s4d_temporal_evidence_s_t` feeds **both** W1 arms. W1 therefore says nothing
about what the S4D architecture contributed — the question a reviewer will
actually ask. That needs **re-scoring**, not a derived analysis, and so does
RQ1's memory ablation: removing memory changes `m2g_detector_score` itself, so
the W1 trick of re-reading a persisted trace does not transfer. Both require a
run, and neither is authorized.

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

**This table replaces v1.2's outright.** v1.2's closing sentence — *"Not one of
the seven research questions is affirmatively answered"* — was true when written
and is **false as of W1**.

| RQ | Question | Status | What would change it |
|---|---|---|---|
| **RQ1** | Does patient-specific memory reduce false alarms without sacrificing sensitivity? | ❌ **Open.** No no-memory arm at episode level | **A run.** Removing memory changes `m2g_detector_score` itself, so this needs re-scoring — the W1 re-read trick does not transfer (§17.6) |
| **RQ2** | Can continual personalization be made contamination-safe? | ⚠️ **Partial.** M2-G retained on development evidence; no contamination-stress comparison at episode level | An episode-level contamination-stress comparison. A run |
| **RQ3** | Can uncertainty reduce cloud dependence without unsafe local decisions? | ✅ **Answered — negatively.** The router at `c_star = 0.90` was evaluated and rejected; `Retained: false` | Nothing. It is answered. The per-bin reliability read (§49.6) describes the retained calibrator and does **not** reopen the router |
| **RQ4** | Does longitudinal/episode reasoning improve monitoring quality? | ✅ **Supported (bounded).** W1: difference 0.1921, 95% paired interval [0.0505, 0.3455], excludes zero | The bound comes off only if a **well-tuned memoryless rule** is given its own operating point and still loses. A run (§17.4) |
| **RQ5** | Can the selected model operate efficiently on edge hardware? | ❌ **Open.** E1 not started; no inference path exists at all | An edge benchmark. Benchmark-host numbers are not edge measurements (§18) |
| **RQ6** | Does foundation-model knowledge improve the compact student? | ❌ **Not started** | Phase 4B, never begun |
| **RQ7** | Can confounder-aware supervision reduce false ST alarms? | ❌ **Not started** | Phase 6B, never begun |

**Two answered, one partial, four open.** Both answers are worth reporting and
neither is a performance headline: RQ3 is a rejection, and RQ4 is bounded by an
operating point chosen with the thing under test already in the loop.

**The fourth column is the point of this table.** Five of the seven rows say
*"a run"*, and every run needs its own authorization. What separates the two
answered rows from the rest is that both were answerable from evidence already
on disk. That well is now dry — §51.

This table is the honest basis for §46, for Appendix A, and for any paper
framing.

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

## §39 Current execution snapshot — 23 August 2026

**`origin/master` `d5a86ce` · working tree clean**

**Completed:** B0–B3 classical (test consumed) · B4-A/B/C with **B4-B selected** ·
P1-B retained · M1L retained · M2-G retained · U1 **calibration retained, router
rejected** · T2 S4D retained · **T1 executed, failed, recovered, measured,
published** · **T2 arm comparison read and published** · **W1 comparator
executed — RQ4 answered, bounded** · **U1 per-bin reliability read** ·
**external validation audited**.

**Active: nothing is executing.** Every derived analysis that needed no new
authorization is done. What remains is documentation and design.

**The change since v1.2 that matters most.** v1.2's §39 read *"No T2 measured
value has been read. The first read requires explicit human authorization and
has not been given."* **The authorization was given, and it is spent.** The
same is true of the one-shot re-read of T1's held-out labels, which was spent on
W1. Both flags now sit `True` on disk and **neither is a live permission** —
they are spent tokens. The re-run guard is the persistence claim, not the flag.

**Future, none of it authorized here:** RQ1 memory-ablation protocol (needs
re-scoring, so a run) · S4D contribution ablation (same) · EDB `overlap_clean`
as a pre-registered, **cold-start-stratified** secondary evaluation · inference
pathway · E1 edge benchmarking · the neural sealed test, **last** (§43).

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

### 43.1 That argument is no longer a caution — it is a finding

v1.2 made this case on principle. Two merged documents now make it on evidence.

- **No cohort exists to corroborate a test number.** `docs/EXTERNAL_VALIDATION_STRATEGY_V1.md`
  audited the public record and found **no drop-in independent cohort**. EDB is
  the only other ST-episode resource and is partly contaminated; STAFF III fails
  on five axes. §49.7.
- **The headline contrast a test would be reported beside spans zero.** T2's
  95% paired interval on the S4D − GRU difference is
  **[-0.015229, 0.148951]**. §49.4.

**Exactly one one-shot budget remains unspent, and this is it.** §51.

`TEST_ATTEMPT.json` does not exist anywhere in the tree; the classical chain's
four `test_evaluation_attempt.json` receipts under
`cardiosentinel-runs/phase3b-classical-v3/` are what a consumed chain looks
like, and are the reason *"TEST is sealed"* is only half true.

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

## §48 System and model inventory

The pipeline, in execution order. Every retained component is named with its
class and file so a claim can be traced to code.

```
LTSTDB waveform   10 s windows, 5 s stride, subject-disjoint 70/15/15, seed 2026
  -> B4-B encoder            CNN + tiny Transformer
  -> P1-B physiology fusion  ST-T morphology fusion
  -> M1L long memory         dual-timescale patient baseline
  -> M2-G gated update       contamination-safe update policy
  -> U1 Platt calibration    g(s) = sigmoid(a*z(s) + b)  ->  p_t
  -> T2 causal S4D           non-anticipative longitudinal score s_t
  -> T1 episode state machine  NORMAL / WATCH / EVENT / RECOVERY
```

### 48.1 Component table

| Component | Class | File | Params | Checkpoint | Status |
|---|---|---|---|---|---|
| B0–B3 classical | — | `models/baselines.py` | — | `model.joblib` 108 B – 789 KB | comparators |
| B4-A | `B4CompactCNN` | `neural/model.py:66` | 87,089 | `model_selected.pt` 360 K | rejected |
| **B4-B** | `B4BTransformerCNN` | `neural/candidates.py:159` | **309,809** | 1.3 M | **SELECTED** |
| B4-C | `B4CSSMCNN` | `neural/candidates.py:296` | 155,313 | 632 K | rejected |
| — shared stem | `SharedLocalFrontEnd` | `neural/candidates.py:70` | — | — | shared by B4-B/C |
| — attention block | `PreNormTransformerBlock` | `neural/candidates.py:115` | — | — | `nn.MultiheadAttention` |
| — SSM block | `DiagonalGatedSSMBlock` | `neural/candidates.py:204` | — | — | **not Mamba**; diagonal, time-invariant |
| P1-A | `P1FusionHead` (control config) | `neural/physiology_fusion.py:305` | — | 36 K | control |
| **P1-B** | `P1FusionHead` + `PhysiologyTransform` | `neural/physiology_fusion.py:305`, `:180` | — | 40 K | **retained**, FPR caveat |
| M1S / M1D | `DualTimescaleMemory` | `neural/patient_memory.py:501` | — | 40 K / 44 K | rejected |
| **M1L** | `DualTimescaleMemory`, `M1StreamMemory` | `neural/patient_memory.py:501`, `:599` | — | 40 K | **retained** |
| M2-0 | `FrozenM1LScorer` | `neural/m2_scorer.py:169` | — | run artifacts | control |
| **M2-G** | gate derivation | `neural/m2_gate_derivation.py` | — | run artifacts | **retained** |
| **U1 calibration** | `U1Calibrator` | `neural/u1_calibration.py:211` | 2 (`a`, `b`) | run artifacts | **retained** |
| U1 router | selective-routing policy | `neural/u1_selection.py` | — | preserved | **rejected** (§15) |
| **T2 S4D** | `CausalS4DLongitudinal` | `neural/t2_models.py:261` | — | `T2_S4D_BEST_CHECKPOINT.pt` 188 K | **retained** |
| T2 GRU | `CausalGRULongitudinal` | `neural/t2_models.py:108` | — | 240 K | comparator |
| **T1** | frozen protocol, `next_state` | `neural/t1_protocol.py` + 20 `t1_*` modules | **none** | no checkpoint | **retained** |

Trainable-parameter counts are frozen constants only for B4-B and B4-C
(`candidates.py:51,53`). Other components' counts were never bound as constants
and are **not asserted here**; checkpoint sizes are measured.

### 48.2 Leakage guarantees, in code

| Guarantee | Enforcement |
|---|---|
| Labels never reach the transition | `T1_FORBIDDEN_TRANSITION_INPUTS` blocks `label`, `target_family`, `subject_outcome`, `episode_identity`, `future_row`, `future_score`, `gru_score` and others |
| Only frozen row inputs are readable | `T1_ALLOWED_ROW_INPUTS` — `stable_id`, `m2g_detector_score`, `detector_decision_d_t`, `oof_calibrated_probability_p_t`, `decision_error_uncertainty_u_t`, `s4d_temporal_evidence_s_t`, `score_present`, `elapsed_stream_seconds`, `elapsed_state_seconds` |
| **Patient identity is never a predictive feature** | `t1_protocol.next_state` **never reads `row.stable_id`**. Its only other use is `T1_THRESHOLD_TIE_ORDER`, deterministic tie-breaking so quantiles are input-order-independent |
| No future information | `next_state` is *"one causal step. Pure: it reads the current row and nothing ahead of it"* |
| Folds are subject-disjoint | 12 folds, 12 distinct subjects, indices exactly `range(12)` |
| Thresholds frozen upstream | `thresholds_generated_here: false`, `selection_performed_here: false`, `thresholds_source: promoted_fold_selection_artifacts` |

**`stable_id` appears in the allow-list and is still not a feature.** It is
present on the row; the transition never reads it. Both halves must be stated
together or the allow-list reads as a contradiction.

## §49 Scientific findings to date

### 49.1 SUPPORTED

- Episode-level detection on 12 held-out LTSTDB subjects, cross-fitted and
  subject-disjoint: **subject-macro mean `episode_f1` = 0.2524**, 95%
  subject-bootstrap **[0.0826, 0.4415]**
- Between-subject variability, scoped exactly as the bootstrap's `claim_scope`
- Pooled description: 163 reference episodes, 59 predicted runs, 38 matched, 21
  unmatched predicted; 473,897 primary windows
- Prospective architecture, physiology, memory and temporal-arm selections under
  rules frozen before the deciding evidence existed
- The measurement **consumed a persisted trace and ran no model** — four
  zero-capability counters, sealed test unopened
- **Episode reasoning over a memoryless window rule, at one operating point**:
  subject-macro `episode_f1` difference **0.1921**, 95% paired subject-bootstrap
  **[0.0505, 0.3455]** (§49.5). The operating-point bound travels with this
  claim everywhere it appears
- End-to-end auditability of the evidence chain itself

### 49.2 Two failure modes behind the seven zeros

`_episode_f1 = 2 * matched / (predicted_event_runs + reference_episodes)` returns
undefined **only** when that denominator is zero. A subject with no reference
episodes but a firing prediction therefore scores a **defined** `0.0`.

| Kind | Subjects | Ref ep. | Predicted runs | Meaning |
|---|---|---|---|---|
| **A — episode-free** | `s2005`, `s2020`, `s2023` | 0 | 7, 8, 1 | False-alarm burden on subjects with **nothing to detect** |
| **B — missed** | `s2019`, `s2058`, `s2059`, `s3072` | 6, 3, 47, 1 | 0, 0, 0, 1 | Genuine detection failure |

**They push the operating point in opposite directions.** Group A improves with
*fewer* predicted runs, Group B with *more*. A single averaged score conceals
that tension. `s3072` is a *matching* failure rather than a silence — one run
that did not overlap its single episode.

**Defined is not meaningful.** Availability analysis that asks only *"is this
metric defined?"* misses this class entirely; the T1 pre-registration did, and
§46.1 now requires both checks.

### 49.3 Latency is a signed offset, not a delay

`_onset_latency = (start_samples[run_begin] - start_samples[episode_begin]) / 250.0`.
**6 of 38** matched-episode latencies are negative. Because
`match_runs_to_episodes` pairs on **overlap alone** — `run_begin < end and begin <
run_end`, no tolerance window, no bound on how early a run may start — and the
artifacts store no run durations, a negative offset is equally consistent with a
persistent `EVENT` state or a long-duration run. **It does not establish
anticipation.**

### 49.4 The T2 contrast — measured, and its interval includes zero

Published in `docs/T2_ARM_COMPARISON_REPORT_V1.md` at merged commit `4018435`.
v1.2 recorded the structure of this contrast before any value was readable;
the values are now in.

| | |
|---|---|
| `selection_basis` | `pooled_primary_validation_auprc` |
| `selected_arm` | `causal_s4d_longitudinal_v1` |
| **`pooled_auprc_difference`** | **0.093215**, against a tie tolerance of 0.002000 |
| **95% paired subject-bootstrap on the difference** | **[-0.015229, 0.148951]** — **includes zero** |
| Pooled primary AUPRC, descriptive and unranked | S4D 0.388085 · GRU 0.294870 |
| Subject-macro AUPRC, descriptive and unranked | S4D 0.428152 · GRU 0.409737 |

**The paired contrast is unbiased** — same held-out rows, rule fixed in advance.
The **winner's absolute figure is not**: S4D was chosen for having the higher
value on this very set. The bias attaches to the maximum, not the contrast.

**This difference IS the selection criterion.** Never write *"S4D achieved
superior AUPRC"*. Write *"the predefined selection rule selected S4D based on
the observed validation contrast"* (Appendix A claim 8).

**The subject-macro figures are means over 9 of 12 subjects**, both arms — the
artifact's own `non_contributing_subject_count` is 3. That is a denominator, not
a derivation, and a subject-macro mean quoted without it is the T1 *"defined is
not meaningful"* lesson repeating on a second experiment. T1 and T2 now both
carry a denominator caveat; §46.1 requires both checks and both experiments
needed them.

The selection-independent comparisons — temporal descriptors, challenge,
cold-start, all `is_selection_input: false` — remain the only ones free of this
conditioning. **T2 scores are uncalibrated**:
`score_is_calibrated_probability: false`, and a bounded sigmoid is not a
probability (Appendix A claim 9).

### 49.5 RQ4 — the programme's first affirmative answer

W1, at merged commit `f998bf5`. Subject-macro `episode_f1` **0.2524** for the
state-machine arm against **0.0603** for the memoryless window arm, a difference
of **0.1921** with a 95% paired subject-bootstrap of **[0.0505, 0.3455]**, which
**excludes zero**. Arm T1 reproduces the published T1 value exactly, which is
what makes the comparison a comparison and not a re-measurement.

**Bounded at one operating point** — §17.4. And **two registered predictions
were refuted and reported as refuted** — §17.5, which is the finding a
methodology paper should lead with, not bury.

**T2's interval includes zero; W1's excludes it.** Different experiments,
different estimands. Neither licenses a claim about the other.

### 49.6 U1 per-bin reliability — the ECE is carried by the near-zero region

Published in `docs/U1_CALIBRATION_RELIABILITY_REPORT_V1.md`; pre-registered in
the plan merged as PR #71. First read of evidence that had sat on disk unread
since August. **It changes nothing** — the retention decision was already taken
on evidence that included these bins' summary.

| | |
|---|---|
| Retained Platt — NLL · Brier · ECE equal-width | 0.143708 · 0.040344 · 0.016991 |
| Uncalibrated baseline — NLL · Brier · ECE equal-width | 0.231705 · 0.063567 · 0.063844 |
| Protocol §16 condition 2 (Brier **and** NLL both lower) | holds, on both scalars |

**Where the low ECE comes from.** Equal-width bin 0 holds **398,513 of the
family's 473,897 rows** at a gap of +0.003638. From bin 3 upward the signed gap
`empirical − mean` is negative and widens monotonically through bin 11: the
calibrator predicts **above** the observed positive rate wherever the probability
is high. Bin 13 reads −0.770848 on 128 rows; bin 14 reads −0.941428 on 16 rows
and is sparse by the plan's own threshold, so it is **not an estimate**.

**The baseline is not a matched comparison.** `U1_OOF_CALIBRATION.json` records
`uncalibrated_baseline` as `out_of_fold: false`, `development_evidence: false`,
with a `baseline_semantics` string calling it *"a reference, not an out-of-fold
artifact"*. Every comparison above inherits that asymmetry.

The retention stays **split**: calibration retained, the selective router at
`c_star = 0.90` not retained (§15). **Improved ECE alone is not a success
criterion** — U1 protocol §16 says so, and the family selection used NLL, not
ECE.

### 49.7 External validation — the finding is negative, and it is a finding

`docs/EXTERNAL_VALIDATION_STRATEGY_V1.md`. **No drop-in independent cohort
exists in the public record.** PhysioNet's `st-segment` index returns
essentially only LTSTDB. EDB is the only other ST-episode resource and is
partly contaminated. STAFF III has gold-standard occlusion timing and fails on
five axes: 1000 Hz, 12-lead, ~5-minute segments, inflation *instants* rather
than episodes, and *induced* rather than spontaneous ischemia.

**The contamination work is already done and enforced in code.**
`evaluation/provenance.py` carries 15 exclusions, `overlap_clean` is 75 records,
and `validate_edb_secondary_evaluation_policy` rejects the full cohort for
LTSTDB-trained models. EDB is a **secondary** cohort and **may never be called
external** (§42, Appendix A claim 3).

**The cold-start trap, and it is the reason this matters.** T2's strata show
**95.5% of validation rows sit past the first hour**, and the `0_5_minutes`
stratum scores AUPRC **0.0015**. EDB records are ~2-hour excerpts against
LTSTDB's ~24 hours, so roughly half of every EDB record would fall in the
warm-up regime. **Any EDB evaluation must be cold-start stratified and
pre-registered, or the number is uninterpretable** — and an unstratified EDB run
would produce a bad number for a reason that has nothing to do with
generalization.

### 49.8 Three headline numbers whose denominator is not what it looks like

**This is a finding, not a limitations list**, and it is the one a methodology
paper can generalise from. Three of the programme's headline figures came from
three different experiments, three different teams of assumptions, and three
different metrics — and all three concealed the same defect until someone looked
underneath.

| Experiment | The headline | What the denominator actually is |
|---|---|---|
| **T1** | subject-macro `episode_f1` **0.2524** over 12 subjects | **Defined for 12, meaningful for 9.** Three subjects have *no reference episodes at all*, so their zero is a false-alarm penalty, not a detection failure — and it pushes the operating point in the *opposite* direction from the four genuine misses (§49.2) |
| **T2** | subject-macro AUPRC **0.428152** | A mean over **9 of 12** subjects, both arms. `non_contributing_subject_count: 3` is in the artifact (§49.4) |
| **U1** | ECE equal-width **0.016991** | Carried by one bin: equal-width bin 0 holds **398,513 of 473,897 rows**. The calibrator is well-behaved where almost all the mass is and over-predicts badly where a clinician would act (§49.6) |

**Three for three.** Each was found by a different check, none by the metric
itself, and in each case the summary statistic was *correctly computed* — the
arithmetic was never wrong. **Availability analysis that asks only "is this
metric defined?" catches none of them.** §46.1 requires both checks because T1
taught the lesson; T2 and U1 are the evidence that the lesson generalises past
the experiment that produced it.

**The methodological claim this supports** — and it is a claim about method, not
about ECG — is that a scalar summary over a heterogeneous population needs its
contributing-unit count reported beside it as a matter of course, not as a
caveat added when someone happens to check. Appendix A claim 23 makes that
binding for this programme.

### 49.9 NOT SUPPORTED

Memory, encoder, SSM or calibration **contribution** · episode-level
S4D-vs-GRU · **external generalization** · subgroup performance · test
performance · clinical utility · deployment behaviour · causal inference · **any
unqualified improvement claim**. See §24 and Appendix A.

**One item left this list in v1.3 and it left partially.** *"Improvement over
any comparator"* was unqualified in v1.2. W1 supplies exactly one comparator, at
exactly one operating point, for exactly one arm — so the improvement claim is
now permitted **only** in the form Appendix A claim 6 fixes, and remains
forbidden everywhere else.

## §50 Roadmap and publication strategy

### 50.1 Positioning — recommended: methodology paper

| | **Option A — architecture performance paper** | **Option B — auditable ML methodology, ECG case study** |
|---|---|---|
| Contribution | The pipeline and its selections | The evidence machinery: negative capability, digest-bound provenance, consumed-attempt semantics, pre-registration, **a real post-claim failure and its authorized recovery** |
| Results burden | Must carry the paper | The modest, un-rescued result is *evidence the method works* |
| Reviewer risk | *"n = 12"*, *"external validation?"*, *"which components matter?"* — **still fatal**. *"Compared to what?"* is now answerable for the episode layer alone, at one operating point | *"Is this just engineering?"* — answered by the stage-24 failure **and by two registered predictions reported as refuted** (§17.5) |
| Required experiments | Memory ablation, encoder ablation, episode-level S4D-vs-GRU, an external cohort. **6–12 months** | **None.** Every analysis it needs is merged |

### 50.1.1 The recommendation is unchanged; the argument for it is not

**v1.2 argued Option B from a premise that no longer holds.** Its reasoning was
*"not one of the seven research questions is affirmatively answered, so Option A
has no headline to carry."* RQ4 is now answered. That sentence cannot be
recycled, and a recommendation resting on a false premise has to be re-made or
withdrawn.

**Re-made, and it survives — for three better reasons.**

1. **RQ4's answer is not a performance headline.** It is bounded at an operating
   point selected with the state machine in the loop (§17.4). Option A would
   have to lead with it, and the first competent reviewer question — *"what does
   a well-tuned memoryless rule score?"* — has no answer on disk.
2. **The T2 contrast, which is the architecture result Option A actually needs,
   spans zero** (§49.4). A performance paper cannot lead with a selection rule.
3. **There is no cohort to generalize to.** §49.7 is not a gap awaiting effort;
   it is an audited negative finding about the public record. Option A's
   *"external validation?"* is not answerable in 6–12 months either.

**Option B, meanwhile, got stronger.** W1's two refuted predictions are the
best evidence the programme has that the machinery is load-bearing rather than
decorative: a pre-registration whose *reasoning* was half wrong, whose
*discipline* held, and which reported itself as refuted. That is a paper
section, and it did not exist in v1.2.

**Framed as methodology, submission is weeks away. Framed as performance, it is
not reachable** without runs that are currently unauthorized — and, for external
validation, without a cohort that does not exist.

### 50.2 Priority waves

**Wave 1 and Wave 2 of v1.2 are complete.** T2 arm comparison, calibration
reliability, external validation strategy, documentation drift and the 13 stale
tests all landed, and W1 — which v1.2 did not anticipate at all — landed with
them. The reproducibility package remains the one Wave 1 item outstanding.

**Wave 1 — before submission, and this is the whole list**

1. **Reproducibility package** — environment lock, manifest, restore procedure.
   The report generators are now tracked. Its absence is disqualifying for a
   methodology paper, and it is the only remaining blocker of that class
2. **Paper sections 2 and 9** — Related Work and Discussion do not exist in any
   form (§50.3). Nothing else in the skeleton is missing outright
3. **Evidence map** — one page separating methodology from findings, so a
   reviewer can see which is which without reading fifty documents

**Wave 2 — written and frozen, executed later, each needing its own authorization**

4. **RQ1 memory-ablation protocol.** Pre-register *before* touching anything. It
   cannot reuse the W1 trick: a memory ablation changes `m2g_detector_score`
   itself, so it needs **re-scoring** — a run, not a derived analysis
5. **S4D contribution protocol** — same shape, same constraint (§17.6)
6. **EDB `overlap_clean` as a pre-registered, cold-start-stratified secondary
   evaluation.** Never to be called external (§49.7)

**Wave 3 — future**

7. Ablation execution · 8. Inference pathway / deployment prototype ·
9. E1 on-device benchmarking · 10. **The sealed neural test, last** (§43) —
   and §43.1 now argues that on evidence rather than on caution

### 50.3 Manuscript skeleton

| Section | Source documents | Readiness |
|---|---|---|
| 1. Introduction | `RESEARCH_SCOPE.md`, §1 | needs writing |
| 2. Related work | — | **missing entirely** |
| 3.1 Problem and data | `DATASET_CONTRACT`, `DATA_SPLIT_POLICY`, `ANNOTATION_SEMANTICS`, `CROSS_DATASET_PROVENANCE`, §42 | near-complete |
| 3.2 Signal pipeline | `SIGNAL_PROCESSING_CONTRACT` | complete |
| 3.3 Architecture | `B4_*`, `P1_*`, `M1_*`, `M2_*`, `U1_*`, `T2_*`, §48 | complete |
| 3.4 Episode layer | `T1_CAUSAL_EPISODE_STATE_PROTOCOL_V1`, `t1_episode_reasoning` | complete |
| **4. Evidence framework** ★ | `EXPERIMENT_CONTRACT`, `RUNTIME_INTEGRITY_SENTINEL_V1`, §§40–47 | **the contribution — write from code** |
| **5. Failure and recovery** ★ | `T1_EXECUTION_RECOVERY_AMENDMENT_V1_1`, `T1_FAILURE_RECEIPT_RECONSTRUCTED.json`, `T1_CONTINUATION_PREAUTHORIZATION` §10, §45 | **exceptional material, needs assembly** |
| 6. Experimental setup | retention decisions, `METRICS_PROTOCOL`, §25 | complete |
| 7. Results | `T1_DESCRIPTIVE_REPORT_V1`, `T2_ARM_COMPARISON_REPORT_V1`, `W1_WINDOW_COMPARATOR_REPORT_V1`, `U1_CALIBRATION_RELIABILITY_REPORT_V1`, §49 | **complete** — the gate is spent and all four reports are merged |
| 8. Limitations | `T1_POST_HOC_ANALYSIS_V1` §3, `EXTERNAL_VALIDATION_STRATEGY_V1`, §24, §51, Appendix A | quotable verbatim; §49.7 makes the external-validation limitation a *finding* rather than an apology |
| 9. Discussion | — | **missing entirely** |
| 10. Reproducibility | §47 | needs the package |

★ marks the novel contribution. Sections 4 and 5 are where the writing effort
belongs — and section 5 should now carry **W1's two refuted predictions**
alongside the stage-24 failure. A failure that was recovered under authorization
and a prediction that was reported as refuted are the same argument told twice,
which is exactly what a methodology paper needs.

**Sections 2 and 9 are the only ones missing outright.** Everything else is
either complete or has its sources named.

**Title candidates.** *Auditable Machine Learning Research: Provenance,
Pre-registration, and Consumed-Attempt Semantics in Ambulatory ECG Ischemia
Detection* · *When the Run Fails: Authorized Recovery of a Consumed Measurement
Under a Frozen Protocol* · *Negative Capability: Proving What a Model Pipeline
Cannot Do*.

---

## §51 Experiment ledger — what has been spent

**New in v1.3.** This is the most decision-relevant page in the handbook and
until now it existed only as flags scattered across run directories.

A **one-shot budget** is an access that can be taken once. It is not a policy
that can be relaxed and not a flag that can be re-read: once consumed, the
evidence it produced is the only evidence there will ever be. Several of these
flags sit `True` on disk **and are spent tokens, not live permissions**. The
re-run guard is the persistence claim, not the flag.

### 51.1 The ledger

| # | Budget / gate | Consumed | Where, and what it bought |
|---|---|:---:|---|
| 1 | B0–B3 classical sealed test | **YES** | Phase 3B-1. Four `test_evaluation_attempt.json` receipts under `cardiosentinel-runs/phase3b-classical-v3/`. The chain is spent and **not extensible** |
| 2 | **B4 / neural sealed test** | **NO** | **The last one.** No `TEST_ATTEMPT.json` exists anywhere in the tree; 80 artifacts read `sealed_test_state: unopened`. §43 |
| 3 | M1-v1 attempt 1 | **YES** | Failed. `M1_STAGE1_ATTEMPT1_FAILURE.md` — documented, not silently retried |
| 4 | M1-v1 attempt 2 | **YES** | Failed. `M1_STAGE1_ATTEMPT2_FAILURE.md` |
| 5 | M1-v2 | **YES** | `phase5-m1-dual-memory-v2`. The **sole** canonical M1 evidence; M1L retained |
| 6 | M2 attempt 1 · M2 recovery 1 | **YES** | Both failed; both receipts retained and part of the record |
| 7 | M2 recovery 2 | **YES** | `phase6-m2-development-v1`. Canonical; M2-G retained |
| 8 | U1 development run | **YES** | `phase7-u1-development-v1`. Split retention: calibration retained, router rejected. **No U1 rerun** |
| 9 | U1 per-bin first read | **YES** | Spent on `U1_CALIBRATION_RELIABILITY_REPORT_V1.md` (§49.6) |
| 10 | T2 training | **YES** | `phase8-t2-development-v1`. S4D and GRU both trained |
| 11 | T2 outer validation | **YES** | `validation_accessed: true`. `T2_OUTER_VALIDATION_EXECUTION_AUTHORIZED` is `True` on disk **and its run is consumed** |
| 12 | T2 first read of measured values | **YES** | Spent at merged commit `4018435` on `T2_ARM_COMPARISON_REPORT_V1.md` (§49.4) |
| 13 | T1 canonical development attempt | **YES** | `phase9-t1-development-v1` @ `c538181`. Failed post-claim at stage 24, **no lock**. Directory immutable |
| 14 | T1 measurement continuation | **YES** | `phase9-t1-continuation-v1` @ `61704aa`, under authorization `b40b4ac`. Completed and locked. Directory immutable. **No second continuation** |
| 15 | T1 held-out label re-read | **YES** | Spent at merged commit `f998bf5` on W1 (§49.5). This is what made RQ4 answerable without a run |

### 51.2 What the ledger says

**Fourteen of fifteen are spent.** Every derived analysis that could be done
without new authorization has been done. There is no remaining question that can
be answered by reading something already on disk — which is why §24's fourth
column says *"a run"* five times.

**Row 2 is the whole of what remains, and it should stay unspent.** §43.1 makes
that case on evidence: the headline T2 contrast spans zero, and no cohort exists
to corroborate a test number.

**Rows 3, 4, 6, 13 — four recorded failures — are assets, not embarrassments.**
They are what §50's Option B is made of. A programme with no failure receipts
either got lucky or is not showing you everything.

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
| 6 | **Improvement, stated unqualified** — improved, helped, outperformed, better | **Rewritten in v1.3.** T1 is no longer one-armed: W1 supplies a memoryless comparator and RQ4 is **Supported (bounded)**. Exactly one improvement claim is now permitted, in exactly one form: *"episode reasoning improves episode-level agreement relative to a memoryless window rule, on identical rows, at the promoted operating point."* The operating-point clause is **not optional** — both arms ran at thresholds selected with the state machine in the loop (§17.4). Every other comparative verb still needs a second arm it does not have |
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

| 22 | *"S4D outperforms GRU"* in any form | **New in v1.3.** The 95% paired subject-bootstrap on the difference is **[-0.015229, 0.148951]** and **includes zero** (§49.4). Claim 8 governs how the selection may be described; this claim forbids the superiority reading that survives it |
| 23 | A **subject-macro** figure quoted without its contributing-subject count | **New in v1.3.** T2's subject-macro AUPRC is a mean over **9 of 12** subjects; `non_contributing_subject_count` is 3. T1 has the same defect for a different reason (§49.2). Both are the *defined is not meaningful* failure and §46.1 requires the check |
| 24 | *"Externally validated"*, or **EDB described as an external cohort** | **New in v1.3.** No drop-in independent cohort exists in the public record (§49.7). EDB is **secondary** and partly contaminated; `validate_edb_secondary_evaluation_policy` rejects the full cohort for LTSTDB-trained models in code |
| 25 | Any **EDB number reported without cold-start stratification** | **New in v1.3.** 95.5% of T2 validation rows sit past the first hour and the `0_5_minutes` stratum scores AUPRC **0.0015**. EDB records are ~2-hour excerpts, so roughly half of every record falls in the warm-up regime. An unstratified figure is uninterpretable (§49.7) |

**Claims 22–25 are new in v1.3.** They exist because four analyses were
published between v1.2 and v1.3, and every one of them created a new way to
overstate the result. Claim 6 was **rewritten** rather than added to: it is the
only claim in this table that a merged document made *less* restrictive, and the
narrowness of what it now permits is the point.

**Claim 21 is new in v1.2** and replaces the pre-v1.2 audit's provisional claim
about unprovable pre-declaration. That concern is **resolved**: v1.1 §10.1 does
predeclare the B4-A/B/C/D families, and the handbook is now in the repository, so
the prospectivity of the B4-B selection is substantiable on request.

---

_Research Execution Handbook v1.3 — a revision of v1.2 (22 Aug 2026), which was
a revision of v1.1 (8 Aug 2026). Section numbering §1–§38 preserved from v1.1;
§39–§47 new in v1.2; §48–§50 added in v1.2; **§51 new in v1.3**. Revised against
`origin/master` `d5a86ce` on 2026-08-23._

_**This handbook grants no scientific permission and authorizes no execution.**
It describes budgets that are already spent and one that is not. Nothing in it
authorizes spending the one that is not._
