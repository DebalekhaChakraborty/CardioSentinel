# CardioSentinel — Experiment Catalogue

Part of **Research Baseline v1.0**. Complete inventory as of `origin/master`
`0480b34`.

**The consumed/available ledger is canonical in
`CardioSentinel_Research_Execution_Handbook_v1.4.md` §51.** This document does
not restate it. Two ledgers drifting apart is the exact failure v1.2 just
demonstrated, and the handbook's is the better one: it tracks fifteen budgets at
the level of *access* — including M1's and M2's failed attempts as budgets in
their own right — where an experiment-level table would have hidden them.

> **§51: all fifteen budgets are spent.** The B4 neural sealed test — the last
> of them — was consumed on 2026-08-25 under `B4_TEST_AUTHORIZATION_V1`.
> **There is no unspent one-shot access anywhere in this programme.**

What follows is the operational companion to that ledger: where each experiment
lives on disk, how far each result can be trusted without further work, what in
`cardiosentinel-runs/` is *not* evidence, and how to re-verify any of it.

---

## 1. Where the experiments live

| Experiment | Code | Evidence directory | Locks |
|---|---|---|:--:|
| B0–B3 classical | `models/baselines.py`, `baseline/` | `phase3b-classical-v3` · 39 MB | 4 |
| B4-A | `neural/model.py:66` | `phase3b2-b4-v1` · 6.4 MB | 1 |
| B4-B / B4-C | `neural/candidates.py:159`, `:296` | `phase3b2-architecture-v1` · 18 MB | 2 |
| P1-A / P1-B | `neural/physiology_fusion.py:305` | `phase4-p1-physiology-v1` · 9.8 MB | 2 |
| M1S / M1D / M1L | `neural/patient_memory.py:501` | `phase5-m1-dual-memory-v2` · 440 KB | 3 |
| M2-0 / M2-G | 14 `neural/m2_*` | `phase6-m2-development-v1` · 1.3 GB | 2 |
| U1 | 6 `neural/u1_*` | `phase7-u1-development-v1` · 134 MB | 1 |
| T2 train + outer | 10 `neural/t2_*` | `phase8-t2-development-v1` · 407 MB | 2 |
| T1 canonical | 28 `neural/t1_*` | `phase9-t1-development-v1` · 349 MB | **0** |
| T1 continuation | 9 `neural/t1_continuation_*` | `phase9-t1-continuation-v1` · 184 KB | 1 |
| W1 | `neural/w1_window_comparator.py` | derived — no run directory | — |
| U1 reliability | `scripts/provenance/gen_u1_reliability_report.py` | derived | — |

**Zero locks on `phase9-t1-development-v1` is correct** — the attempt failed at
stage 24, before promotion. A lock would mean it completed.

---

## 2. Classification

**🟢 GREEN — complete and scientifically usable**
B0–B3 · B4-A/B/C · U1 · T1 canonical · T1 continuation · W1 · U1 reliability

**🟡 YELLOW — complete but needs interpretation before it is quoted**

| Experiment | Why |
|---|---|
| P1-B | carries an unresolved false-positive-rate caveat |
| M1L, M2-G | selected on **window-level** development evidence; never evaluated at the episode endpoint the project reports. RQ1 is unanswered as a direct consequence |
| T2 | the headline contrast **is** the selection criterion; its paired interval includes zero; the subject-macro figure is a mean over **9 of 12** subjects |

**🔴 RED — incomplete or risky**
None. Every started experiment reached a recorded conclusion, including the one
that failed.

**🔵 RESERVED**
None. The category is empty as of 2026-08-25 — the B4 neural sealed test was its
only member and it has been consumed. **Nothing is held in reserve any more**,
which is a different statement from *"nothing is left to do"*: the remaining work
in §5 needs authorizations that do not exist yet, not budgets that do.

---

## 3. Published results

| Experiment | Headline | Interval | Document |
|---|---|---|---|
| T1 | subject-macro `episode_f1` **0.2524** | [0.0826, 0.4415] | `T1_DESCRIPTIVE_REPORT_V1.md` |
| T2 | `pooled_auprc_difference` **0.093215** | **[-0.015229, 0.148951]** — includes zero | `T2_ARM_COMPARISON_REPORT_V1.md` |
| W1 | T1 − W **0.1921** | **[0.0505, 0.3455]** — excludes zero | `W1_WINDOW_COMPARATOR_REPORT_V1.md` |
| U1 | Platt NLL **0.143708** / Brier **0.040344** | vs baseline 0.231705 / 0.063567 | `U1_CALIBRATION_RELIABILITY_REPORT_V1.md` |
| **B4-B sealed test** | pooled AUPRC **0.0935334** at prevalence 0.0460529 | subject-macro AUPRC 0.354901 over **8 of 12**, 95% **[0.033058, 0.239284]** | artifacts only — `phase3b2-architecture-v1/B4B_cnn_transformer_v1/TEST_*`; no `_V1` report exists |

### 3.1 Denominator caveats

Each of these headlines carries a caveat about what its denominator actually is.
The pattern is recorded as a **finding** in handbook §49.8 and is not restated
here. **The sealed test is its fourth instance** — subject-macro discrimination
over 8 of 12, because four test subjects are single-class and `METRICS_PROTOCOL`
excludes them rather than scoring them 0 or 1. It was pre-registered as a
reporting requirement precisely because the same thing had already happened in
T2.

**The sealed-test row is the only one in the table above with no `_V1` report
behind it.** The number is registered in `TEST_METRICS.json` and its provenance
in `TEST_AUDIT.json`; §7 of `PAPER_OUTLINE_V2.md` carries it with its boundary.
Cite the artifacts, and quote no subject-macro figure without its denominator.

---

## 4. Consumption rules

In force and canonical in handbook §51 and §45. In summary: no M2, U1 or T2
rerun; no T1 fold retry; no second continuation; no automatic retry under any
circumstance; never add `--force`, `--retry`, `--reset`, `--overwrite` or
`--fresh-seed`. Both `T1_CONTINUATION_AUTHORIZED` and
`T2_OUTER_VALIDATION_EXECUTION_AUTHORIZED` are `True` on disk and **both are
spent tokens** — the re-run guard is the persistence claim, not the flag.

---

## 5. What could still be run, and what it costs

| Candidate | Needs | Cost |
|---|---|---|
| **T2-score ablation** (does S4D contribute?) | protocol → pre-registration → authorization | **a re-scoring run.** `s4d_temporal_evidence_s_t` is baked into persisted rows, so this cannot reuse the W1 trick |
| **RQ1 no-memory arm** | protocol → pre-registration → authorization | **a re-scoring run** — a memory ablation changes `m2g_detector_score` itself |
| ~~**EDB `overlap_clean`**~~ | — | **DECLINED 2026-08-24**, in writing, with reasons (`EXTERNAL_VALIDATION_ROUTE_A_DECISION_V1.md`). No EDB data was accessed. Not a candidate; retained struck through because a route that was considered and refused is evidence and a deleted one is not |
| ~~**B4 sealed test**~~ | — | **CONSUMED 2026-08-25.** Attempt 1 of 1, `repeat_attempt_permitted: false`. Not a candidate; retained struck through because a spent budget is part of the ledger |

**Two rows above have left this table rather than been done.** EDB
`overlap_clean` was **declined in writing** on 2026-08-24
(`EXTERNAL_VALIDATION_ROUTE_A_DECISION_V1.md`) — no EDB data was accessed, and
its §2.4 records that no second cohort will corroborate any result in this
paper, permanently. The B4 sealed test was **consumed** on 2026-08-25.

**There is no remaining cheap move, and now no remaining budget either.** Every
derived analysis that needed no new authorization has been run. Anything further
requires a new authorization, a re-scoring run, or data the project does not
have.

---

## 5.1 IPS runtime phase — built, not experimented

**New after `research-freeze-v1.0`.** These consumed **no** one-shot budget,
ran no model training and produced no new metric, so they are not experiments
and do not appear in the §1 ledger. They are recorded here because a reader
looking for "what happened after the science froze" should find it.

| Work | Merged | What it produced | Budget consumed |
|---|---|---|---|
| Edge representation bridge | #82 | live `CausalWindow` → 146-d representation; verified against the frozen corpus to 6 ULP | **none** |
| Streaming runtime | #83 | `StreamingInferenceSession`; ECG chunk → alert at ~61× real time | **none** |
| Evidence Agent + claim guard | #84 | alert explanation; 18 Appendix A patterns executable | **none** |
| Evidence graph | #85 | 35-node provenance graph reaching the experiment locks | **none** |
| Patient Explanation Agent | #86 | guarded generation with deterministic fallback | **none** |
| Research Assistant | #87 | six curated evidence objects, no document access | **none** |
| Architecture Selection Agent | #92 | candidate lifecycle traced from protocol lock to decision; refuses on keyword ties | **none** |
| Demonstration console | #93 | end-to-end terminal view, contracted by `DEMO_SCENARIO.md` before it was built | **none** |
| Explanation evaluation framework | #94 | fidelity, claim violations, completeness, latency; generative arm **unexercised** | **none** |

**Validation performed, all against already-published evidence:**

- **Representation equality** — 64 rows, 13 records, 3 channels: physiology half
  bit-exact, embedding half within 6 ULP of float32.
- **M2 order preservation** — `replay_stream` byte-identical before and after
  the `step()` extraction, `sha256 8830a2e1…`, plus 555 M2 tests.
- **Null-result reproduction** — replaying `s20591` produces zero alerts, which
  reproduces the published finding that s2059 has 47 reference episodes and
  **0 predicted runs**.

**E1 remains not started.** The runtime is a laptop replay simulation; no edge
hardware measurement exists and RQ5 is open.

**None of #82-#94 consumed a budget**, opened an artifact or computed a new
metric, which is why §1's lock counts are unchanged. Handbook §56 states this
explicitly, and the §7 audit commands below still return the values they did
before the IPS layer existed.

---

## 6. Not experiments

Present in `cardiosentinel-runs/` and easily mistaken for evidence:

- `T1/T1_state_machine_v1` — `run_class: harness_verification`,
  `protocol_evidence: false`. **Not evidence**, despite reading
  `status: COMPLETE`.
- `phase-3b-smoke-*` (three directories) — CI fixtures.
- `phase3b-classical-v1`, `-v2` — superseded by `-v3`.
- `*-logs` directories — logs only.

---

## 7. Audit commands

```bash
# locks are case-inconsistent: 4 classical runs use lowercase experiment_lock.json
find cardiosentinel-runs -iname "*experiment_lock*.json" | wc -l      # expect 20

# the one that matters: exactly one consumed B4-B attempt, never zero or two
find . -name "TEST_ATTEMPT.json" -not -path "./.git/*"                # expect 1
# receipt must say: attempt_sequence 1, attempt_status COMPLETE,
#                   repeat_attempt_permitted false

# frozen T1 sources — bare filenames, from src/cardiosentinel/neural/
sha256sum t1_protocol.py t1_execution_spec.py t1_evidence_store.py \
          t1_development_run.py t1_persistence.py | md5sum
# expect 4107286307d147d542ff15e916225315
```
