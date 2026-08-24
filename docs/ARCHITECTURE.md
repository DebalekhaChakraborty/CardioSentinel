# CardioSentinel — Architecture Map

Part of **Research Baseline v1.0**. Describes the repository as of
`origin/master` `a8f1b47` (merge of #94).

**Read this before navigating the package tree.** The top-level layout of
`src/cardiosentinel/` does not describe where the work is. Three packages that
look like major subsystems are empty, and two of those three describe research
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
concern. `neural/` is 86 files and 54,097 lines — **43% of the codebase**.

**`edge/` was on that list until `ips-agentic-runtime-v1.0`, and is not any
more.** It now holds the IPS runtime (§0.1), and `agents/` — which did not exist
at all when this document was first written — holds the agentic layer (§0.2).

---

## 0.1 The edge runtime — a replay-based edge execution environment

```
src/cardiosentinel/
  edge/     8 files  1,666 lines   the IPS runtime
  agents/  14 files  3,065 lines   the agentic layer
```

**This is not future edge execution and it is not a deployment.** It is a
**replay-based edge execution environment**: a stored recording is streamed
through the retained model chain in causal order, on a laptop CPU, producing
alerts that carry the provenance of every frozen component that produced them.

| `edge/` | |
|---|---|
| `representation.py` | the bridge: `CausalWindow` → the 146-d representation the retained models consume |
| `artifacts.py` | the single controlled loader; nothing else in `edge/` opens a checkpoint |
| `session.py` | `StreamingInferenceSession`, holding five pieces of causal state |
| `alerts.py` | contiguous `EVENT` runs → `AlertEvent` |
| `replay.py` · `cli.py` | laptop replay driver and `cardiosentinel edge simulate` |
| `console.py` | the IPS demonstration console (#93), `cardiosentinel edge console` |

**Demonstrated:**

- **laptop replay** — 1,079 windows of `s20201` in 89 s wall, ~61× real time
- **streaming runtime** — causal window generation and five pieces of carried
  state, one implementation shared with the batch research path
- **provenance** — every reported value traces to a frozen artifact, and the
  representation is verified against the frozen corpus to 6 ULP
- **alert generation** — contiguous `EVENT` runs promoted to `AlertEvent`

**Not demonstrated:**

- **embedded hardware** — a laptop is not an edge device. Appendix A claim 5
  stands and **RQ5 remains open**
- **power consumption** — never measured, on any device
- **thermal constraints** — never measured, on any device
- **memory-pressure behaviour** — never measured, on any device
- **acquisition hardware** — there is no sensor and no acquisition path; this
  replays a stored recording

**Deployment readiness is separately excluded.** No serving path, no ONNX, no
TorchScript. Appendix A claim 2 stands.

The permitted description is *"laptop-based edge simulation using streaming
physiological replay"* — no more than that.

---

## 0.2 The agentic layer

**Every agent is grounded on the evidence graph, and none is autonomous.** The
graph is the substrate; the claim boundary is enforced on every output that
leaves the layer.

```
                        Evidence Agent
                              |
                              v
                        Evidence Graph
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
        Explanation      Research      Architecture
           Agent         Assistant    Selection Agent
              |               |               |
              +---------------+---------------+
                              |
                              v
                     Evaluation Framework
```

| `agents/` | |
|---|---|
| `claims.py` | the publication claim boundary as code — 18 Appendix A patterns |
| `evidence.py` | Evidence Agent: why an alert fired, deterministic, **no language model** |
| `graph.py` | evidence graph, closed node kinds and edge relations |
| `context.py` · `explain.py` · `providers.py` | Patient Explanation Agent and its deterministic fallback |
| `research.py` | Evidence-Grounded Research Assistant, curated objects only |
| `architecture.py` | Architecture Selection Agent (#92) — lifecycle, not recommendation |
| `evaluation/` | Evidence-Constrained Explanation Evaluation framework (#94), 4 modules |
| `cli.py` | `cardiosentinel agent …` |

**The Evidence Agent is deterministic on purpose.** It is the layer a generative
agent is grounded *on*, so it must be the part that cannot hallucinate.

**Naming collision worth knowing about.** There are now **two** packages called
`evaluation/`: `cardiosentinel/evaluation/` (splits, targets, contamination
registry — §2 below) and `cardiosentinel/agents/evaluation/` (#94's explanation
evaluation harness). They are unrelated.

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
| **IPS runtime** | `edge/` | **1,666** | **Implemented — replay simulation only (§0.1)** |
| **Agentic layer** | `agents/` | **3,065** | **Implemented (§0.2)** |
| Edge hardware / E1 | — | 0 | **Not started.** RQ5 open |
| §16 confounder-aware multi-task (RQ7) · RQ6 distillation · HMM/CRF | — | **0** | **Never begun** |

**Totals at `a8f1b47`:** 287 tracked `.py` files · 124,672 LOC · 116 test files
· 3,302 tests collected · 74 documents in `docs/` (67 of them `.md`).

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
  Neither is an edge measurement. Power and thermal behaviour have never been
  measured on any device (§0.1).
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
