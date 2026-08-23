# CardioSentinel — Architecture Map

Part of **Research Baseline v1.0**. Describes the repository as of
`origin/master` `d5a86ce`.

**Read this before navigating the package tree.** The top-level layout of
`src/cardiosentinel/` does not describe where the work is. Four packages that
look like major subsystems are empty, and two of those four describe research
that is complete — somewhere else.

---

## 0. The thing that misleads

```
src/cardiosentinel/
  episodes/         2 lines   "Future temporal reasoning for ST-event and episode construction."
  personalization/  2 lines   "Future contamination-safe patient baseline and adaptation components."
  uncertainty/      2 lines   "Future calibrated uncertainty estimation and confidence controls."
```

Each is a single `__init__.py` holding one docstring. **No code.**

But episode reasoning **is** implemented (28 `t1_*` modules, executed, measured,
reported). Uncertainty **is** implemented (6 `u1_*` modules, executed, split
retention). Personalization **is** implemented (`patient_memory.py` plus 17
`m1_*`/`m2_*` modules, two retained components).

All of it lives in `neural/`, organised by **experiment ID** rather than by
concern. `neural/` is 86 files and 54,073 lines — **46% of the codebase**.

**`edge/` was on that list until `ips-agentic-runtime-v1.0`, and is not any
more.** It now holds the IPS runtime, and `agents/` — which did not exist at
all when this document was first written — holds the agentic layer. Both are
described in §0.1.

---

## 0.1 The two packages that stopped being stubs

```
src/cardiosentinel/
  edge/     7 files  1,428 lines   the IPS runtime
  agents/   9 files  2,049 lines   the agentic layer
```

| `edge/` | |
|---|---|
| `representation.py` | the bridge: `CausalWindow` → the 146-d representation the retained models consume |
| `artifacts.py` | the single controlled loader; nothing else in `edge/` opens a checkpoint |
| `session.py` | `StreamingInferenceSession`, holding five pieces of causal state |
| `alerts.py` | contiguous `EVENT` runs → `AlertEvent` |
| `replay.py` · `cli.py` | laptop replay driver and `cardiosentinel edge simulate` |

| `agents/` | |
|---|---|
| `claims.py` | the publication claim boundary as code — 18 Appendix A patterns |
| `evidence.py` | Evidence Agent: why an alert fired, deterministic |
| `graph.py` | evidence graph, closed node kinds and edge relations |
| `context.py` · `explain.py` · `providers.py` | Patient Explanation Agent and its deterministic fallback |
| `research.py` | Evidence-Grounded Research Assistant, curated objects only |

**What is established:** a replay-based ECG stream running on a laptop CPU at
roughly 61× real time, producing alerts that carry the provenance of every
frozen component that produced them.

**What is NOT established, and the claim boundary is unchanged:**

- **Embedded hardware deployment.** A laptop is not edge hardware. Appendix A
  claim 5 stands and **RQ5 remains open**.
- **Real acquisition.** This replays a stored recording. There is no sensor and
  no acquisition path.
- **Power, thermal or memory-pressure behaviour.** Never measured on any device.
- **Deployment readiness.** No serving path, no ONNX, no TorchScript. Appendix A
  claim 2 stands.

The permitted description is *"laptop-based edge simulation using streaming
physiological replay"* — no more than that.

---

## 1. The pipeline, in execution order

```
                        LTSTDB v1.0.0  (5.6 GB on disk)
                        10 s windows · 5 s stride · 250 Hz
                        subject-disjoint 70/15/15 · seed 2026
                                     |
        ┌────────────────────────────┴────────────────────────────┐
        │  DATA LAYER              data/            1,806 loc     │
        │  WFDB ingestion · EDB + LTSTDB adapters · manifests      │
        │  annotations are NOT reduced to binary labels here       │
        └────────────────────────────┬────────────────────────────┘
                                     |
        ┌────────────────────────────┴────────────────────────────┐
        │  SIGNAL PROCESSING       signal/          1,236 loc      │
        │  causal SOS filters · label-free windows · quality       │
        └────────────────────────────┬────────────────────────────┘
                                     |
        ┌────────────────────────────┴────────────────────────────┐
        │  FEATURES                features/          389 loc      │
        │  frozen schemas with SHA-256 identities                  │
        └────────────────────────────┬────────────────────────────┘
                                     |
             ┌───────────────────────┴───────────────────────┐
             |                                               |
    ┌────────┴─────────┐                        ┌────────────┴──────────────┐
    │ CLASSICAL        │                        │ NEURAL ENCODER            │
    │ models/,baseline/│                        │ neural/candidates.py      │
    │ B0–B3            │                        │ B4-A · B4-B · B4-C        │
    │ TEST CONSUMED    │                        │ B4-B SELECTED             │
    └──────────────────┘                        └────────────┬──────────────┘
                                                             |
                        ┌────────────────────────────────────┴───────────┐
                        │ PHYSIOLOGY FUSION   neural/physiology_fusion.py │
                        │ P1-A vs P1-B → P1-B retained (FPR caveat)       │
                        └────────────────────────────────────┬───────────┘
                                                             |
                        ┌────────────────────────────────────┴───────────┐
                        │ PERSONALIZATION   neural/patient_memory.py     │
                        │                   + 3 m1_* + 14 m2_*           │
                        │ M1S/M1D/M1L → M1L retained                     │
                        │ M2-0 vs M2-G → M2-G retained                   │
                        │ patient identity selects a namespace,          │
                        │ NEVER a predictive feature                     │
                        └────────────────────────────────────┬───────────┘
                                                             |
                        ┌────────────────────────────────────┴───────────┐
                        │ CALIBRATION       neural/u1_* (6 modules)      │
                        │ SPLIT retention:                               │
                        │   Platt calibration        RETAINED            │
                        │   selective router c*=0.90 REJECTED  (RQ3 −ve) │
                        └────────────────────────────────────┬───────────┘
                                                             |
                        ┌────────────────────────────────────┴───────────┐
                        │ TEMPORAL REASONING  neural/t2_* (10 modules)   │
                        │ causal S4D vs GRU · state carried across       │
                        │ windows · one-shot outer validation CONSUMED   │
                        │ S4D selected; contrast interval spans zero     │
                        │ scores are NOT calibrated probabilities        │
                        └────────────────────────────────────┬───────────┘
                                                             |
                        ┌────────────────────────────────────┴───────────┐
                        │ EPISODE REASONING   neural/t1_* (28 modules)   │
                        │ NORMAL / WATCH / EVENT / RECOVERY              │
                        │ no parameters, no checkpoint                   │
                        │ vs W1 memoryless comparator → RQ4 supported    │
                        └────────────────────────────────────┬───────────┘
                                                             |
                                                          ALERT
                                          (a research output, never a diagnosis)
```

**Cross-cutting, not a pipeline stage:**

```
EVALUATION FRAMEWORK   evaluation/  1,965 loc
  splits · annotation-after-window targets · benchmark protocol
  cross-dataset contamination registry

SAFETY / GOVERNANCE    neural/sealed_test.py, *_gate.py, runtime_sentinel.py,
                       determinism.py, integrity.py        ~2,600 loc
  one-shot claims · negative-capability proofs · frozen digests
```

---

## 2. Module status table

| Layer | Location | LOC | Status |
|---|---|---:|---|
| Data | `data/` | 1,806 | Implemented · Tested · Executed |
| Signal | `signal/` | 1,236 | Implemented · Tested · Executed |
| Features | `features/` | 389 | Implemented · Tested · Executed |
| Classical baselines | `models/`, `baseline/` | 3,038 | Executed · **test consumed** |
| B4-A | `neural/model.py:66` | — | Executed · **rejected** |
| **B4-B** | `neural/candidates.py:159` | — | Executed · **RETAINED** |
| B4-C | `neural/candidates.py:296` | — | Executed · **rejected** |
| **P1-B** | `neural/physiology_fusion.py:305` | — | Executed · **RETAINED** |
| **M1L** | `neural/patient_memory.py:501` | ~11,000 | Executed · **RETAINED** |
| **M2-G** | `neural/m2_gate_derivation.py` | (incl. above) | Executed · **RETAINED** |
| **U1 Platt** | `neural/u1_calibration.py:211` | 4,380 | Executed · **RETAINED** |
| U1 router | `neural/u1_selection.py` | (incl. above) | Executed · **REJECTED** |
| **T2 S4D** | `neural/t2_models.py:261` | ~8,900 | Executed · **selected** |
| T2 GRU | `neural/t2_models.py:108` | (incl. above) | Executed · comparator |
| **T1** | `neural/t1_protocol.py` + 27 | ~16,000 | Executed · **RETAINED** |
| **W1** | `neural/w1_window_comparator.py` | 268 | Executed · ablation arm |
| Evaluation | `evaluation/` | 1,965 | Implemented · Tested |
| Governance | `sealed_test`, gates, sentinel | ~2,600 | **Active** |
| **IPS runtime** | `edge/` | **1,428** | **Implemented — replay simulation only (§0.1)** |
| **Agentic layer** | `agents/` | **2,049** | **Implemented** |
| Edge hardware / E1 | — | 0 | **Not started.** RQ5 open |
| §16 multi-task · RQ6 · HMM/CRF | — | **0** | **Never begun** |

**Totals at `d5a86ce`:** 250 tracked `.py` files · 117,104 LOC · 102 test files
· 2,689 test definitions · 64 documents (this baseline adds two more).

---

## 3. Leakage controls, by location

| Guarantee | Where |
|---|---|
| Labels cannot reach the transition | `t1_protocol.py:170` — 15 forbidden inputs, enforced `:691` |
| Only frozen row inputs readable | `t1_protocol.py:158` — 9 allowed inputs, enforced `:697` |
| Patient identity never predictive | `next_state` never reads `stable_id`; its only other use is tie-breaking at `:202` |
| Subject-disjoint folds | `evaluation/splits.py`, manifest `protocols/splits/ltstdb_v1.json` |
| Labels never shape windows | `evaluation/targets.py` — annotation **after** window |
| Thresholds frozen upstream | recorded per run: `derived_before_outer_validation: true` |
| Cross-dataset contamination | `evaluation/provenance.py` — 15 EDB exclusions, policy validator |
| Attempt immutability | `tests/neural/_attempt_guard.py` + package-wide autouse fixture |
| One-shot test access | `neural/sealed_test.py` — exclusive claim, `ATTEMPT_SEQUENCE = 1` |
| Negative capability | `neural/t1_continuation_gate.py` — AST + `sys.modules` proof |

---

## 4. What this architecture does not contain

Stated so nobody looks for it:

- **No serving path.** No inference endpoint, no deployment, no on-device code.
- **No edge *hardware* implementation.** `B4_RESOURCE_BENCHMARK_V1` numbers are
  from a fixed benchmark host, and the runtime in `edge/` runs on a laptop.
  Neither is an edge measurement.
- **No routing policy in force.** The only one built was evaluated and rejected.
- **No external cohort.** Only LTSTDB is on disk; EDB is contracted, audited and
  deliberately never downloaded.
- **No episode-level memory ablation.** M1/M2 were selected on window-level
  development evidence; RQ1 is unanswered.
- **No calibrated T2 score.** `score_is_calibrated_probability: false`.

---

## 5. Suggested repair, not done here

The four empty packages should either be removed or made to re-export their real
implementations from `neural/`. Leaving them advertises an architecture the code
does not have, and it costs every newcomer the same wrong assumption.

This map does not make that change: it is a baseline document, and moving code
during a freeze is exactly what the freeze exists to prevent.
