# CardioSentinel

**An evidence-grounded adaptive intelligent physical system for ambulatory ECG
monitoring** — and the machinery that makes every number it reports traceable to
the access that produced it.

It is **not a medical device** and does not provide diagnosis, treatment, or
medical recommendations.

---

## What this repository is

A complete computational research artifact: the implementation, the
pre-registered protocols, the measured results with their boundaries, the
decisions that retained or rejected each component, and the provenance machinery
that binds all four together.

**Two things are on offer here, and mixing them is the easiest way to misread
the project.**

- **A method** — one-shot experiment budgets, negative-capability proofs,
  digest-bound artifacts and a claim boundary compiled into executable code.
  It would still be a contribution if every number below were different.
- **Findings** — what the numbers actually say, each carrying the boundary that
  travels with it. Every one is small, bounded, or negative.

The temptation this repository is built to resist is letting the first one's
confidence bleed into the second one's numbers. **The rigour is in the
boundaries, not behind them.**
[`docs/control-plane/EVIDENCE_MAP.md`](docs/control-plane/EVIDENCE_MAP.md)
separates the halves line by line.

---

## Scope and the non-diagnostic boundary

CardioSentinel investigates **continuous detection of transient ischemic ST
episodes in long-term ambulatory ECG** — the Long-Term ST Database (LTSTDB),
whose records run about **21–24 hours** each. The system emits an alert carrying
the provenance of every frozen component behind it.

**Detection research is not clinical diagnosis.** The alert is a research
output. This repository must not recommend treatment, declare a patient
condition, or claim clinical performance
([scope](docs/control-plane/RESEARCH_SCOPE.md)).

This list is load-bearing and **enforced in code** by
[`agents/claims.py`](src/cardiosentinel/agents/claims.py), which encodes 18
forbidden claims as word-anchored patterns:

- **No diagnosis.** Detection only. No clinical utility is claimed.
- **No deployment.** No serving path, no ONNX, no TorchScript.
- **No edge-hardware result.** The runtime is a **laptop simulation replaying a
  stored recording**. There is no sensor and no acquisition path. Power, thermal
  and memory-pressure behaviour have never been measured on any device.
- **No generalisation beyond LTSTDB.** One dataset, twelve validation subjects,
  and no independent ST-episode cohort exists in the public record — a finding,
  not a gap awaiting effort
  ([audit](docs/external-validation/EXTERNAL_VALIDATION_STRATEGY_V1.md)).
- **No generalisable held-out performance, and no neural superiority.** The
  neural sealed test was consumed on 2026-08-25 and a number exists — pooled
  AUPRC **0.0935** at a prevalence of **0.0461**, subject-macro AUPRC **0.3549**
  over **8 of 12** subjects, 95% subject-bootstrap **[0.0331, 0.2393]**, scores
  uncalibrated.

  **On that same held-out partition the B3 classical morphology baseline scored
  pooled AUPRC 0.1683 — higher than the neural encoder's 0.0935.** The sealed
  analysis states it plainly: *"the raw-waveform representation did not match
  handcrafted ST features."* Nothing here should be read as the neural encoder
  outperforming the classical baselines.

  It is also **encoder-only**, not full-system performance: the sealed test
  characterises the selected representation on held-out subjects, and did not
  move any research question from open to answered. **One uncorroborated
  one-shot on twelve subjects from one dataset**, reported because it was
  pre-registered to be. The MCC interval includes zero.
  ([analysis](docs/experiments/b4/B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md) ·
  [baselines](docs/baselines/PHASE3B1_CLASSICAL_BASELINE_RESULTS.md))

Run the boundary against your own sentence:

```bash
cardiosentinel agent check-claims "S4D outperforms GRU"
#   2 violation(s): claim 6, claim 22                         -> exits 1

cardiosentinel agent check-claims \
  "the predefined selection rule selected S4D based on the observed validation contrast"
#   no violations                                             -> exits 0
```

**The guard is lexical, not semantic.** It reduces the failure rate; it does not
make overclaiming impossible. It has caught this repository's own authors five
times — including once when `textwrap` split a disclaimer across two lines and a
**correct** output was flagged.

---

## The physical-monitoring problem

A transient ischemic ST episode is a *minutes-to-hours* deviation in the ST
segment, appearing and resolving inside a recording that runs most of a day.
Long-term ambulatory ECG is therefore a continuous physical stream from one
body, and three properties make it hard in ways a window classifier does not
address.

1. **A physiological event persists through time.** Reference episodes are
   minutes long; a window-level decision is seconds long. Fragmented window
   alarms are not events.
2. **Baselines are entity-specific.** What is normal for one subject is not
   normal for another, so a useful system adapts to the individual — and
   adapting *during* an abnormal state corrupts the very baseline it learns
   from.
3. **The operating point is not transferable.** Thresholds validated on one
   subject do not license another. The runtime **refuses** rather than borrowing
   the nearest.

CardioSentinel is the attempt to build a causal, adaptive, stateful monitor
under those three constraints, and to measure honestly what each part
contributed.

---

## System architecture — the retained path

```
physical ECG stream (LTSTDB, 250 Hz, 10 s windows, 5 s stride)
    ↓  causal preprocessing              signal/     label-free windowing
    ↓  CNN-Transformer representation    B4-B        selected over B4-A, B4-C
    ↓  physiology fusion                 P1-B        retained over P1-A
    ↓  patient-relative memory           M1L         retained over M1S, M1D
    ↓  contamination-gated adaptation    M2-G        retained over M2-0
    ↓  calibrated probability            U1 Platt    router evaluated, rejected
    ↓  longitudinal temporal evidence    T2-S4D      selected over T2-GRU
    ↓  episode-state reasoning           T1          NORMAL/WATCH/EVENT/RECOVERY
    ↓  evidence graph                    agents/     closed node and edge kinds
    ↓  guarded explanation               agents/     deterministic or local model
                                                      ALERT
```

**The package layout does not describe where the work is**, and
[`docs/control-plane/ARCHITECTURE.md`](docs/control-plane/ARCHITECTURE.md)
exists to correct that before you go looking:

```
src/cardiosentinel/
  neural/     96 files, 57,980 lines -- ~43% of the codebase, organised by
              experiment ID. Episode reasoning, memory, calibration and the
              longitudinal arm all live here, not in the packages named for them
  edge/        8 files, 2,276 lines -- the replay-based execution environment
  agents/     15 files, 4,023 lines -- evidence, graph, explanation, research,
              architecture selection, evaluation, and the claim guard
  evaluation/ splits, annotation-after-window targets, contamination registry
              (unrelated to agents/evaluation/, the explanation harness)
  episodes/ · personalization/ · uncertainty/   two-line stubs. Empty on purpose,
              and ARCHITECTURE.md §5 names the repair that was not done
```

The identifier scheme — why `T2` feeds `T1`, why `G1`–`G6` are gate conditions
and not experiments — is decoded in
[`EXPERIMENT_AND_COMPONENT_MAPPING.md`](docs/control-plane/EXPERIMENT_AND_COMPONENT_MAPPING.md).

---

## Controlled AI design lineage

**No component is in the pipeline because it seemed reasonable.** Each was run
as a named arm against a sibling, under a protocol merged before any value was
visible, and retained or rejected by a recorded decision.

| Stage | Alternatives evaluated | Outcome | Decision record |
|---|---|---|---|
| Classical baselines | B0 · B1 · B2 · B3 | test consumed | [`PHASE3B1_CLASSICAL_BASELINE_RESULTS`](docs/baselines/PHASE3B1_CLASSICAL_BASELINE_RESULTS.md) |
| Representation | CompactCNN (B4-A) · **CNN-Transformer (B4-B)** · CNN-SSM (B4-C) | **B4-B selected** | [`B4_GLOBAL_ENCODER_SELECTION_V1`](docs/experiments/b4/B4_GLOBAL_ENCODER_SELECTION_V1.md) |
| Physiology fusion | P1-A · **P1-B** | **P1-B retained** | [`P1_PHYSIOLOGY_RETENTION_DECISION_V1`](docs/experiments/p1/P1_PHYSIOLOGY_RETENTION_DECISION_V1.md) |
| Patient memory | M1S · M1D · **M1L** | **M1L retained** | [`M1_MEMORY_RETENTION_DECISION_V1`](docs/experiments/m1/M1_MEMORY_RETENTION_DECISION_V1.md) |
| Adaptation policy | M2-0 naive · **M2-G gated** | **M2-G retained** | [`M2_UPDATE_POLICY_RETENTION_DECISION_V1`](docs/experiments/m2/M2_UPDATE_POLICY_RETENTION_DECISION_V1.md) |
| Calibration / routing | **Platt** · selective router `c*=0.90` | **split: Platt retained, router rejected** | [`U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1`](docs/experiments/u1/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md) |
| Temporal arm | GRU · **S4D** | **S4D selected** | [`T2_LONGITUDINAL_TEMPORAL_RETENTION_DECISION_V1`](docs/experiments/t2/T2_LONGITUDINAL_TEMPORAL_RETENTION_DECISION_V1.md) |
| Episode reasoning | memoryless window rule (W1) · **state machine (T1)** | **T1 retained** | [`W1_WINDOW_COMPARATOR_REPORT_V1`](docs/experiments/w1/W1_WINDOW_COMPARATOR_REPORT_V1.md) |
| Explanation | **deterministic** · local open-weight generative | both exercised; runtime gates the generative path | [`EXPLANATION_EVALUATION_REPORT_V1`](docs/explanation/EXPLANATION_EVALUATION_REPORT_V1.md) |

**Rejected arms are preserved, never deleted.** M2-0 remains the frozen control
that makes M2-G's effect measurable, and the rejected router's entire
risk-coverage curve is intact. Preservation is provenance, not retention.

---

## Research questions

| RQ | Question | Status |
|---|---|---|
| **RQ1** | does patient memory help at the episode level? | **Open** — needs a re-scoring run |
| **RQ2** | contamination-safe personalization | **Partial** |
| **RQ3** | does uncertainty routing improve monitoring? | **Negative finding** — router built, evaluated against a prespecified gate, rejected |
| **RQ4** | does episode reasoning improve monitoring quality? | **Supported (bounded)** |
| **RQ5** | edge-hardware feasibility | **Open** — never begun |
| **RQ6** | foundation-model distillation | **Not started** |
| **RQ7** | confounder-aware multi-task | **Not started** |

**RQ4 is the only affirmative answer, and *"(bounded)"* may not be dropped when
quoting it.** RQ3's negative finding is a result, not a gap — literature in that
area overwhelmingly reports adoption.

**Still unanswered and not an RQ:** what the S4D architecture itself
contributed. T2's interval spans zero, and the S4D temporal evidence feeds
*both* arms of the W1 comparison, so that ablation holds it fixed.

---

## Key measured findings

Organised by the system behaviour each one characterises. **Nothing in the
runtime or the agentic layer changed any of them.**

### Adaptation can be made contamination-safe at negligible discrimination cost

The gated policy **M2-G** reduced peak patient-prototype drift during ischemic
stress intervals by **99.82%** (1.3088 → 0.0023) and during heart-rate-related
intervals by **96.04%**, while AUPRC moved by **−0.000268** and sensitivity rose
by **+0.0148**.

It is **not** a trivial never-update policy: it admitted **107,671 updates**,
**21.84%** of 492,904 timeline rows.

**Boundary.** False-alarm behaviour got *worse*, and this is recorded rather
than minimised — background FPR **+0.0031**, PPV **−0.0099**, and the
subject-level FPR upper tail is less favourable throughout. No statistical
significance is claimed. Cold start is unsolved: 0–5 minute sensitivity is
**0.000000** in both arms.
→ [`M2_UPDATE_POLICY_RETENTION_DECISION_V1`](docs/experiments/m2/M2_UPDATE_POLICY_RETENTION_DECISION_V1.md)

### Episode-state reasoning beats a memoryless rule at the frozen operating point

Subject-macro `episode_f1` **0.2524** (state machine) against **0.0603**
(memoryless window rule) on identical rows — difference **0.1921**, 95% paired
subject-bootstrap **[0.0505, 0.3455]**, **excludes zero**.

**Boundary, and it is load-bearing.** Both arms ran at thresholds selected
*with the state machine in the loop*. **A separately tuned memoryless rule was
never tested.** RQ4 reads "Supported (bounded)", never bare "Supported".
→ [`W1_WINDOW_COMPARATOR_REPORT_V1`](docs/experiments/w1/W1_WINDOW_COMPARATOR_REPORT_V1.md)

### Episode detection, measured and bounded

Subject-macro `episode_f1` **0.2524**, 95% subject-bootstrap
**[0.0826, 0.4415]**, 12 held-out subjects, cross-fitted and subject-disjoint.

**Boundary.** Seven of twelve subjects score zero for **two incomparable
reasons** — three have no reference episodes at all, four missed real ones — and
they push the operating point in *opposite* directions. A single averaged score
conceals that tension.
→ [`T1_DESCRIPTIVE_REPORT_V1`](docs/T1_DESCRIPTIVE_REPORT_V1.md)

### Calibration can be added without perturbing a frozen detector

Platt calibration improved NLL **0.2317 → 0.1437** and Brier
**0.0636 → 0.0403**, with **zero classification disagreements** across all
473,897 rows — a pure probability transformation that changes no detection
decision.

**Boundary.** Low pooled ECE is carried by the near-zero region: one bin holds
**398,513 of 473,897** rows, and above bin 3 the calibrator over-predicts.
→ [`U1_CALIBRATION_RELIABILITY_REPORT_V1`](docs/experiments/u1/U1_CALIBRATION_RELIABILITY_REPORT_V1.md)

### A prespecified gate rejected a component that looked attractive

The selective router at `c* = 0.90` was built, evaluated and **rejected**:
escalation ratio **6.4536** against a limit of **3.0** fixed in advance. **No
routing policy exists in this system.**
→ [`U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1`](docs/experiments/u1/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md)

### A selection rule is not a superiority result

`pooled_auprc_difference` **0.093215** favouring S4D, 95% paired subject
bootstrap **[-0.015229, 0.148951]** — **includes zero**.

**Boundary.** That difference **is** the selection criterion. Say *"the
predefined selection rule selected S4D based on the observed validation
contrast"*; never *"S4D achieved superior AUPRC"*. T2 scores are **not**
calibrated probabilities, and the subject-macro figure is a mean over **9 of
12** subjects.
→ [`T2_ARM_COMPARISON_REPORT_V1`](docs/experiments/t2/T2_ARM_COMPARISON_REPORT_V1.md)

### A model-independent guard refused a fluent, faithful, wrong explanation

A locally-cached open-weight model — `Qwen/Qwen3-1.7B`, greedy decoding on CPU
— produced output scoring **fidelity 1.000, 0 claim violations, completeness
1.000**, and asserted that a `G1`–`G6` range passed when **G4 and G5 were
blocked**. Three prior gates and four registered
metrics passed it; the categorical-alignment guard refused it, the deterministic
explanation was served, and the contradiction was recorded. The failure
reproduced across independent runs.

`Qwen/Qwen3-4B-Instruct-2507` on the same context stated the fact correctly —
no gate fired, and its generation **was served**.

**Boundary.** Two models, one context. **That is not a scaling law**, and no
failure rate is claimed.
→ [`EXPLANATION_EVALUATION_REPORT_V1`](docs/explanation/EXPLANATION_EVALUATION_REPORT_V1.md)

### The runtime replays faster than real time on a laptop CPU

1,079 windows of `s20201` in **89 s wall**, **~61× real time**, with the 146-d
representation bridge verified against the frozen corpus to **6 ULP**.

**Boundary.** A laptop is not an edge device. This is replay of a stored
recording — no sensor, no acquisition path, no power or thermal measurement.

### Three denominators that were not what they looked like

T1's `episode_f1` is defined for 12 subjects and **meaningful for 9**. T2's
subject-macro AUPRC is a mean over **9 of 12**. U1's ECE is carried by one bin
holding **84%** of rows. Three experiments, three metrics, three different
checks that found them — **and in every case the arithmetic was correct.**

This is the finding that generalises past ECG: **a scalar summary over a
heterogeneous population needs its contributing-unit count reported beside it as
a matter of course.**

---

## Run the demonstrator

**This works from a clean clone.** The demo bundle — checkpoints, calibrators,
thresholds, experiment locks, 1.63 MiB — is committed to this repository. You
supply one ECG record from PhysioNet
([`reproducibility/DATA_ACCESS.md`](reproducibility/DATA_ACCESS.md)).

```bash
pip install -e ".[dev,data,signal,ml,neural]"

# 1. ECG stream -> alert, with the provenance of every component behind it
cardiosentinel edge console s20201 --seconds 2400 \
  --run-root reproducibility/demo_bundle/runs \
  --feature-root reproducibility/demo_bundle/features

# 2. why a component was rejected -- read from the frozen record, not summarised
cardiosentinel agent research "Why was the selective router rejected?"

# 3. why an architecture was selected -- lifecycle, not recommendation
cardiosentinel agent architecture "Why was S4D selected?"
```

**The first command's output is contracted in advance** by
[`docs/explanation/DEMO_SCENARIO.md`](docs/explanation/DEMO_SCENARIO.md), and a
test asserts it. You should see exactly one alert:

| | |
|---|---|
| Alert | `00:17:05` → `00:27:45`, held **640 s** across **129** windows |
| Peak calibrated probability | **`0.545613`** |
| Safety gates | `G1 PASS  G2 PASS  G3 PASS  G4 BLOCK  G5 BLOCK  G6 PASS` |
| Memory updates admitted | **0** |
| Explanation mode | `DETERMINISTIC`, `no provider configured` |

**`0` admitted is the control working, not a fault.** The contamination gate
admits only windows that look normal and sit outside a 60-second refractory, so
it blocks during an event by design.

**Only the twelve validation subjects are replayable** (`cardiosentinel edge
subjects`). T1 thresholds are leave-one-subject-out; every other record has no
validated operating point, and the runtime **refuses** rather than borrowing the
nearest.

Explanation generation is an explicit boundary. The default is `deterministic`:
no model call, no data egress. `--provider local` uses only the pinned, locally
cached model and never falls back to a hosted service. `--provider gemini` is an
explicit hosted choice: the structured evidence context leaves the local
machine. A generic `GOOGLE_API_KEY` authenticates that explicit choice but never
selects Gemini by itself.

---

## Reproduce the evidence

All read-only. **These three need nothing but the clone:**

```bash
# the demo bundle is intact
python reproducibility/verify_reproducibility.py
#   -> demo bundle verified: 27 files, 1.63 MiB, all digests match.

# verify exactly one consumed sealed-test attempt and no repeat attempt
find . -name "TEST_ATTEMPT.json" -not -path "./.git/*"
#   -> one receipt, since 2026-08-25:
#      cardiosentinel-runs/phase3b2-architecture-v1/B4B_cnn_transformer_v1/
#      attempt_sequence 1, attempt_status COMPLETE,
#      repeat_attempt_permitted false.
#   Before that date this command printed nothing, and that was the whole
#   claim. Now the claim is the receipt: one attempt, and no second one is
#   possible.

# the frozen episode-reasoning sources, from src/cardiosentinel/neural/
sha256sum t1_protocol.py t1_execution_spec.py t1_evidence_store.py \
          t1_development_run.py t1_persistence.py | md5sum
#   -> 4107286307d147d542ff15e916225315
```

**This one also needs the PhysioNet record** from
[`DATA_ACCESS.md`](reproducibility/DATA_ACCESS.md), since it replays a waveform:

```bash
# trace any reported measurement back to its experiment lock
cardiosentinel agent graph s20201 --format lineage --of measurement:p_t \
  --seconds 2400 --run-root reproducibility/demo_bundle/runs \
  --feature-root reproducibility/demo_bundle/features
#   -> measurement:p_t <- component:U1 Platt calibration
#                      <- artifact:U1_DEPLOYMENT_CALIBRATOR.json
#                         [digest verified via runtime bundle manifest]
#                      <- experiment lock: unavailable in the demo bundle
```

**`sealed_test_state: unopened` in the full U1 experiment lock is correct and
will not change.** That lock is not in the demo bundle, as the graph states. In
the full evidence tree it is U1's attestation about U1 — the calibrator was
fitted with the B4 test unopened, and the lock says so about itself. It is not a
status board. Sixty-seven `.json` artifacts carry that field, thirteen of them
`EXPERIMENT_LOCK.json` files pinned by a self-referential digest, and **editing
one to reflect 2026-08-25 would be falsifying a record, not updating it.**

**And this one needs the full evidence tree**, which is git-ignored and not
distributed — it is what *we* run, listed so you can see what we check:

```bash
find cardiosentinel-runs -iname "*experiment_lock*.json" | wc -l   # -> 20
```

`zero locks on phase9-t1-development-v1 is correct` — that attempt failed at
stage 24, before promotion. A lock would mean it completed. The failure and the
single-use authorized recovery that followed it are recorded in
[`T1_EXECUTION_RECOVERY_AMENDMENT_V1_1`](docs/T1_EXECUTION_RECOVERY_AMENDMENT_V1_1.md)
and [`recovery/`](recovery/README.md).

---

## Experiment catalogue

The run-by-run inventory, the consumed-budget ledger and what each access cost
are in
[`docs/control-plane/EXPERIMENT_CATALOGUE.md`](docs/control-plane/EXPERIMENT_CATALOGUE.md).

**All fifteen one-shot budgets are spent.** The B4 neural sealed test, the last
of them, was consumed on **2026-08-25** under a signed authorization, after the
one route to a corroborating cohort had been declined. Nothing further can be
measured here without a new human authorization, a re-scoring run, or data this
project does not have.

Six failure records are kept, not hidden: the T1 canonical attempt failed
post-claim at stage 24 and carries **zero locks**, M1-v1 failed twice, M2 failed
twice. **No automatic retry, under any circumstance.**

---

## Evidence and provenance model

| Mechanism | What it establishes |
|---|---|
| Digest-bound artifacts | Every published number traces to a SHA-256'd file and the commit its analysis ran at |
| Frozen dependency environment | 335 packages, `installed_packages_sha256 = b0fd6ea…`, asserted by the code that consumes it |
| Tracked report generators | [`scripts/provenance/`](scripts/provenance/README.md) holds the byte-identical script that produced each merged report, so derivations are re-runnable rather than described |
| Immutable run directories | Consumed attempt and continuation directories are frozen |
| **Negative-capability counters** | The T1 measurement **consumed a persisted trace and ran no model**: `fold_evaluations: 0`, `policy_selection_calls: 0`, `state_machine_invocations: 0`, `threshold_generation_calls: 0`, alongside `test_accessed: false` |
| Path and pin translation | [`docs/provenance/`](docs/provenance/) — commit-pin and document-path translations, so a stale pointer in frozen evidence resolves instead of being edited |

**Negative capability is the unusual part.** Conventional testing shows what code
*does*. These artifacts prove what the code *did not do* — did not load a model,
did not regenerate a threshold, did not touch the sealed test — from counters
written by the run itself rather than from an author's assurance.

Leakage controls are enforced in code, not asserted in prose: a 15-entry deny
list on state-transition inputs, a 9-entry allow list, subject-disjoint folds,
labels applied *after* windowing, and thresholds frozen upstream of measurement.
[`EVIDENCE_MAP.md`](docs/control-plane/EVIDENCE_MAP.md) §1.1 locates each one.

---

## Repository structure

```
src/           implementation, organised by experiment ID (see ARCHITECTURE.md)
tests/         3,579 collected; integrity and usability asserted separately
configs/       experiment and runtime configuration
protocols/     frozen split manifests
scripts/       provenance generators, literature search, corpus audits
reproducibility/  committed demo bundle, checksum manifest, environment lock
recovery/      the single-use authorized T1 recovery record
legacy/v0/     the 2020 origin, retained unchanged
docs/
  control-plane/    current state, architecture, evidence map, catalogue, mapping
  contracts/        frozen dataset, experiment, signal and metrics contracts
  experiments/      b4 · m1 · m2 · p1 · t2 · u1 · w1 protocols, reports, decisions
  T1_*.md           episode-reasoning protocol, spec and reports (flat, see below)
  explanation/      evaluation protocol and report, local-model protocol, demo
  provenance/       translations, incident record, runtime integrity sentinel
  external-validation/  the declined route and the strategy behind it
  literature/       the two frozen literature-search harvests
  baselines/        classical baseline results
  paper/figures/    evidence visualizations F1–F5 and their generators
  handbook/         research execution handbook, v1.5 authoritative
  handoffs/         session-by-session working record (historical)
```

**The seven `docs/T1_*.md` files are deliberately flat.** The T1 driver's
sources are frozen by SHA-256 and construct those paths, so moving the documents
would break a governance guard that is working as designed. The reason is
recorded in [`docs/README.md`](docs/README.md) and the path translation table.

---

## Known limitations

Beyond the boundaries stated with each finding above:

- **Cold start is unsolved.** 0–5 minute sensitivity is `0.000000`. 95.5% of
  validation rows sit past the first hour, and the first-five-minutes stratum
  scores AUPRC **0.0015**.
- **No calibrated temporal score.** `score_is_calibrated_probability: false`.
- **No episode-level memory ablation.** M1/M2 were selected on window-level
  development evidence; RQ1 is unanswered.
- **No routing policy in force.** The only one built was evaluated and rejected.
- **Three empty packages** — `episodes/`, `personalization/`, `uncertainty/` —
  advertise an architecture the code does not use. The repair is named and was
  not done during the freeze.

---

## Setup and data access

Python **3.11+**. Raw and derived physiological data and experiment outputs are
never committed; they live in the git-ignored roots `cardiosentinel-data/`,
`cardiosentinel-features/` and `cardiosentinel-runs/`, or outside the repository
entirely.

```bash
pip install -e ".[dev]"                       # core + tests
pip install -e ".[dev,data,signal,ml,neural]" # everything the demo needs
cardiosentinel --help
```

Filtering is **disabled by default**: the frozen corpus was built under
`processing_profile: raw`, and a band-pass inserted before the representation
would shift every embedding silently
([contract](docs/contracts/SIGNAL_PROCESSING_CONTRACT.md)). Data acquisition is
plan-only unless `--execute` is supplied.

Source data is LTSTDB from PhysioNet — obtain it yourself per
[`reproducibility/DATA_ACCESS.md`](reproducibility/DATA_ACCESS.md). EDB is
contracted, audited and **deliberately never downloaded**; it is a *secondary*
cohort, enforced in code, and may never be called external.

Before making research changes, read
[`docs/control-plane/RESEARCH_SCOPE.md`](docs/control-plane/RESEARCH_SCOPE.md)
and [`docs/contracts/EXPERIMENT_CONTRACT.md`](docs/contracts/EXPERIMENT_CONTRACT.md).
The repository is under **Research Baseline v1.0**: frozen for documentation and
analysis of existing evidence. Leaving that freeze requires a named experiment
with a pre-registered protocol.

---

## Current state

Tagged **`ips-agentic-runtime-v1.0`**; the science is frozen at
**`research-freeze-v1.0`**. The pinned checkpoint — commit, counts, open work
and known defects — is
[`docs/control-plane/CURRENT_STATE.md`](docs/control-plane/CURRENT_STATE.md),
which is regenerated wholesale rather than amended.

*(No commit SHA is pinned here on purpose. The previous one went stale in the
commit that updated it.)*

---

## Project evolution

**This began as my final-year B.Tech project in 2020.** One file, 110 lines:
moving-average R-peak detection, heart rate from the mean R-R interval, then the
ST segment located by fixed fractions of the cycle and its slope compared
against a single hardcoded number.

```python
if (avg_slope > 0.35):
    print(" Heart Condition : MYOCARDIAL ISCHEMIA ")
```

It read its input from a hardcoded path on my desktop.

**CardioSentinel asks the same question.** Most of the work since has gone into
establishing what may *not* be said in answer to it — where the 2020 version
printed a diagnosis from one threshold, this one carries twenty-five forbidden
claims enforced in code, fifteen spent one-shot budgets, and a headline
architectural result whose confidence interval includes zero and says so in
every document that quotes it.

That original code is retained **unchanged** in
[`legacy/v0/`](legacy/v0/README.md), tagged `legacy/v0`. It is not part of the
pipeline, was never validated, and its fixed-threshold outputs are not clinical
evidence — its sample CSVs carry a single `hart` column with no recorded source,
patient, lead, unit or sampling metadata. It is kept because the honest version
of this project's history includes where it started.

---

## License and attribution

Code is licensed under the MIT License. See [`NOTICE.md`](NOTICE.md) before
adding third-party data, annotations, models, or documentation.
