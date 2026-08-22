# CardioSentinel — Experiment Catalogue

Part of **Research Baseline v1.0**. Complete inventory as of `origin/master`
`d5a86ce`.

**This document exists for one reason: to put the consumed/available column
somewhere a human can read it.** Until now that information lived only inside
gitignored run directories, and it is the single most decision-relevant fact in
the repository.

> **Exactly one irreversible budget remains unspent: the B4 neural sealed test.**

---

## 1. The ledger

| Experiment | Code | Evidence | Locks | Executed | **Consumed** | Result | Class |
|---|---|---|:--:|:--:|---|---|:--:|
| **B0–B3** classical | `models/baselines.py`, `baseline/` | `phase3b-classical-v3` 39 MB | 4 | ✅ | **sealed test SPENT** | comparators | 🟢 |
| **B4-A** compact CNN | `neural/model.py:66` | `phase3b2-b4-v1` 6.4 MB | 1 | ✅ | dev budget spent | rejected | 🟢 |
| **B4-B** CNN-Transformer | `neural/candidates.py:159` | `phase3b2-architecture-v1` 18 MB | 2 | ✅ | dev budget spent | **selected encoder** | 🟢 |
| **B4-C** CNN-SSM | `neural/candidates.py:296` | same | — | ✅ | dev budget spent | rejected | 🟢 |
| **P1-A / P1-B** | `neural/physiology_fusion.py:305` | `phase4-p1-physiology-v1` 9.8 MB | 2 | ✅ | dev budget spent | **P1-B retained** | 🟡 |
| **M1S / M1D / M1L** | `neural/patient_memory.py:501` | `phase5-m1-dual-memory-v2` 440 KB | 3 | ✅ | **v2 is canonical; v1 failed twice** | **M1L retained** | 🟡 |
| **M2-0 / M2-G** | 14 `neural/m2_*` | `phase6-m2-development-v1` 1.3 GB | 2 | ✅ | **recovery2 canonical** | **M2-G retained** | 🟡 |
| **U1** | 6 `neural/u1_*` | `phase7-u1-development-v1` 134 MB | 1 | ✅ | one-shot spent | **SPLIT** — Platt kept, router rejected | 🟢 |
| **T2** training | 10 `neural/t2_*` | `phase8-t2-development-v1` 407 MB | 2 | ✅ | one-shot spent | S4D + GRU trained | 🟡 |
| **T2** outer validation | `neural/t2_evaluation.py` | same | (incl.) | ✅ | **one-shot SPENT** | S4D selected; **interval spans zero** | 🟡 |
| **T1** canonical attempt | 28 `neural/t1_*` | `phase9-t1-development-v1` 349 MB | **0** | ✅ **FAILED** stage 24 | **attempt SPENT** | consumed, immutable | 🟢 |
| **T1** continuation | 9 `neural/t1_continuation_*` | `phase9-t1-continuation-v1` 184 KB | 1 | ✅ | **single authorization SPENT** | measured, reported | 🟢 |
| **W1** comparator | `neural/w1_window_comparator.py` | derived — no run directory | — | ✅ | **label re-read SPENT** | **RQ4 supported (bounded)** | 🟢 |
| **U1** reliability | `scripts/provenance/gen_u1_reliability_report.py` | derived | — | ✅ | free analysis — none left | per-bin read published | 🟢 |
| **B4 sealed test** | `neural/sealed_test.py` | — | — | ❌ | **AVAILABLE** | — | 🔵 |

**Zero locks on `phase9-t1-development-v1` is correct**: the attempt failed at
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
B4 neural sealed test.

---

## 3. Published results

| Experiment | Headline | Interval | Document |
|---|---|---|---|
| T1 | subject-macro `episode_f1` **0.2524** | [0.0826, 0.4415] | `T1_DESCRIPTIVE_REPORT_V1.md` |
| T2 | `pooled_auprc_difference` **0.093215** | **[-0.015229, 0.148951]** — includes zero | `T2_ARM_COMPARISON_REPORT_V1.md` |
| W1 | T1 − W **0.1921** | **[0.0505, 0.3455]** — excludes zero | `W1_WINDOW_COMPARATOR_REPORT_V1.md` |
| U1 | Platt NLL **0.143708** / Brier **0.040344** | vs baseline 0.231705 / 0.063567 | `U1_CALIBRATION_RELIABILITY_REPORT_V1.md` |

### 3.1 Three denominator caveats — read together

Each headline has a footnote about what its denominator actually is. Taken
together they are arguably a finding about the measurement layer, not three
separate footnotes:

- **T1** — `episode_f1` is *defined* for 12/12 subjects, but three have **zero
  reference episodes**, so their `0.0` is a false-alarm penalty, not a detection
  failure.
- **T2** — the subject-macro AUPRC is a mean over **9 of 12** subjects;
  `non_contributing_subject_count` is 3 for both arms.
- **U1** — the low ECE is carried by the near-zero region. Equal-width bin 0
  holds **398,513 of 473,897 rows (84.1%)**, and the signed gap turns negative
  from bin 3 upward.

**Defined is not meaningful.** The phrase recurs because the failure recurs.

---

## 4. Consumption rules still in force

- **No M2 rerun. No U1 rerun. No T2 rerun. No T1 fold retry. No second
  continuation.**
- `T1_CONTINUATION_AUTHORIZED` and `T2_OUTER_VALIDATION_EXECUTION_AUTHORIZED`
  are both `True` on disk. **Both are spent tokens, not live permissions.** The
  re-run guard is the persistence claim, not the flag.
- The consumed T1 attempt directory and the continuation directory are
  **immutable**.
- **No automatic retry under any circumstance.** Never add `--force`,
  `--retry`, `--reset`, `--overwrite` or `--fresh-seed`.

---

## 5. What could still be run, and what it costs

| Candidate | Needs | Cost |
|---|---|---|
| **T2-score ablation** (does S4D contribute?) | protocol → pre-registration → authorization | **a re-scoring run.** `s4d_temporal_evidence_s_t` is baked into persisted rows, so this cannot reuse the W1 trick |
| **RQ1 no-memory arm** | protocol → pre-registration → authorization | **a re-scoring run** — a memory ablation changes `m2g_detector_score` itself |
| **EDB `overlap_clean`** | pre-registration, cold-start stratified | data acquisition; secondary cohort only, never "external" |
| **B4 sealed test** | human decision | **irreversible; the last firewall** |

**There is no remaining cheap move.** Every derived analysis that needed no new
authorization has been run. Anything further requires a new authorization, a
re-scoring run, or data the project does not have.

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

# the one that matters
find . -name "TEST_ATTEMPT.json" -not -path "./.git/*"                # expect empty

# frozen T1 sources — bare filenames, from src/cardiosentinel/neural/
sha256sum t1_protocol.py t1_execution_spec.py t1_evidence_store.py \
          t1_development_run.py t1_persistence.py | md5sum
# expect 4107286307d147d542ff15e916225315
```
