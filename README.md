# CardioSentinel

**An evidence-grounded intelligent physical system for adaptive ECG monitoring**
— and the machinery that makes every number it reports traceable to the access
that produced it.

It is **not a medical device** and does not provide diagnosis, treatment, or
medical recommendations.

> **If you arrived here from the manuscript**, start with
> [Run it in three commands](#run-it-in-three-commands), then use
> [From the manuscript to the evidence](#from-the-manuscript-to-the-evidence) to
> go from any section to the artifact behind it.
>
> **The manuscript is in preparation.** Its current structure is
> [`docs/PAPER_OUTLINE_V2.md`](docs/PAPER_OUTLINE_V2.md), and the section
> numbers used below refer to that outline. The governing record of the
> programme is the
> [Research Execution Handbook v1.4](docs/CardioSentinel_Research_Execution_Handbook_v1.4.md).

---

## Run it in three commands

**This works from a clean clone.** The demo bundle — checkpoints, calibrators,
thresholds, experiment locks, 1.63 MiB — is committed to this repository. You
supply one ECG record from PhysioNet
([`reproducibility/DATA_ACCESS.md`](reproducibility/DATA_ACCESS.md)).

```bash
pip install -e ".[dev,data,signal,ml]"

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
[`docs/DEMO_SCENARIO.md`](docs/DEMO_SCENARIO.md), and a test asserts it. You
should see exactly one alert:

| | |
|---|---|
| Alert opens | `00:17:05`, held **640 s** across **129** windows |
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

---

## From the manuscript to the evidence

Section numbers refer to [`docs/PAPER_OUTLINE_V2.md`](docs/PAPER_OUTLINE_V2.md).

| Section | What it claims | Where the evidence is |
|---|---|---|
| §3.1 Data | subject-disjoint 56/12/12, seed 2026, EDB contamination | [`DATASET_CONTRACT`](docs/DATASET_CONTRACT.md) · [`DATA_SPLIT_POLICY`](docs/DATA_SPLIT_POLICY.md) · [`ANNOTATION_SEMANTICS`](docs/ANNOTATION_SEMANTICS.md) · [`CROSS_DATASET_PROVENANCE`](docs/CROSS_DATASET_PROVENANCE.md) |
| §3.2–3.4 Pipeline | causal signal path, encoder, memory, calibration, episode layer | [`SIGNAL_PROCESSING_CONTRACT`](docs/SIGNAL_PROCESSING_CONTRACT.md) · `B4_*` · `P1_*` · `M1_*` · `M2_*` · `U1_*` · `T2_*` · [`T1_CAUSAL_EPISODE_STATE_PROTOCOL_V1`](docs/T1_CAUSAL_EPISODE_STATE_PROTOCOL_V1.md) |
| §3.5 The runtime | 146-d bridge verified to **6 ULP**; ~61× real time | `src/cardiosentinel/edge/` · Handbook §52, §55 |
| §4 Evidence framework | one-shot budgets, negative capability, digest-bound provenance | [`EXPERIMENT_CONTRACT`](docs/EXPERIMENT_CONTRACT.md) · [`RUNTIME_INTEGRITY_SENTINEL_V1`](docs/RUNTIME_INTEGRITY_SENTINEL_V1.md) · Handbook §40–§47 |
| §2 Related work | the gap this work sits in, after a recorded search | [`LITERATURE_SEARCH_V1`](docs/LITERATURE_SEARCH_V1.md) · [`PAPER_S2_RELATED_WORK_DRAFT`](docs/PAPER_S2_RELATED_WORK_DRAFT.md) · [`scripts/literature_search.py`](scripts/literature_search.py) |
| §4.6 Claim governance | the publication boundary as executable code | [`src/cardiosentinel/agents/claims.py`](src/cardiosentinel/agents/claims.py) · Handbook §53 |
| §5 Failure and recovery | a consumed attempt, and an authorized single-use recovery | [`T1_EXECUTION_RECOVERY_AMENDMENT_V1_1`](docs/T1_EXECUTION_RECOVERY_AMENDMENT_V1_1.md) · `recovery/` |
| §5.6 Nine boundaries | the guard catching this repository's own authors, and four gates each added because the previous ones passed a real failure | Handbook §53.2, §53.2.1 · [`PAPER_S5_6_CLAIM_BOUNDARY_DRAFT`](docs/PAPER_S5_6_CLAIM_BOUNDARY_DRAFT.md) |
| §7 Results | the four reported numbers | the four `_V1` reports in the table below |
| §8 Limitations | 25 forbidden claims | Handbook **Appendix A** |
| §10 Reproducibility | committed bundle, restore procedure | [`reproducibility/`](reproducibility/) |

The full experiment-to-artifact inventory is
[`docs/EXPERIMENT_CATALOGUE.md`](docs/EXPERIMENT_CATALOGUE.md); the spent-budget
ledger is Handbook **§51**.

---

## Every reported number, with the boundary that travels with it

**These four are the results. Nothing in the runtime or the agentic layer
changed any of them** — Handbook §56 states that explicitly.

| | Reported | The boundary, which is not optional |
|---|---|---|
| **T1** episode reasoning | subject-macro `episode_f1` **0.2524**, 95% [0.0826, 0.4415] | seven of twelve subjects score zero, for two incomparable reasons that push the operating point in opposite directions ([report](docs/T1_DESCRIPTIVE_REPORT_V1.md)) |
| **T2** S4D vs GRU | difference **0.093215**, 95% paired **[-0.015229, 0.148951]** | **includes zero.** The difference **is** the selection rule; scores are not calibrated probabilities; the subject-macro figure is a mean over **9 of 12** ([report](docs/T2_ARM_COMPARISON_REPORT_V1.md)) |
| **U1** calibration | Platt retained, NLL **0.143708** / Brier **0.040344** | the selective router was **rejected** — escalation ratio **6.4536** against a limit of **3.0** fixed in advance. No routing policy exists ([decision](docs/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md)) |
| **W1** vs memoryless | difference **0.1921**, 95% paired **[0.0505, 0.3455]** | **excludes zero**, but bounded: both arms ran at thresholds selected with the state machine in the loop ([report](docs/W1_WINDOW_COMPARATOR_REPORT_V1.md)) |

**Research questions:** RQ4 is **Supported (bounded)** — the parenthesis is part
of the claim. RQ3 is a **negative finding**, reported as a result. RQ1, RQ2
(partial), RQ5, RQ6 and RQ7 are open, and every one needs a run that has not
been authorized.

**All fifteen one-shot budgets are spent.** The B4 neural sealed test, the last
of them, was consumed on **2026-08-25** under a signed authorization, after the
one route to a corroborating cohort had been declined. Nothing further can be
measured here without a new human authorization, a re-scoring run, or data this
project does not have.

---

## What this repository does not establish

This list is load-bearing and **enforced in code** by
[`agents/claims.py`](src/cardiosentinel/agents/claims.py), which encodes 18 of
the handbook's 25 forbidden claims as word-anchored patterns:

- **No diagnosis.** Detection only. No clinical utility is claimed.
- **No deployment.** No serving path, no ONNX, no TorchScript.
- **No edge-hardware result.** The runtime is a **laptop simulation replaying a
  stored recording**. There is no sensor and no acquisition path. RQ5 is open,
  and power, thermal and memory-pressure behaviour have never been measured on
  any device.
- **No generalisation beyond LTSTDB.** One dataset, twelve validation subjects,
  and no independent ST-episode cohort exists in the public record — a finding,
  not a gap awaiting effort
  ([audit](docs/EXTERNAL_VALIDATION_STRATEGY_V1.md)).
- **No generalisable test-set performance.** The neural sealed test was
  consumed on 2026-08-25 and a number exists — pooled AUPRC **0.0935** at a
  prevalence of **0.0461**, subject-macro AUPRC **0.3549** over **8 of 12**
  subjects, 95% subject-bootstrap **[0.0331, 0.2393]**, scores uncalibrated.
  **One uncorroborated one-shot on twelve subjects from one dataset**, reported
  because it was pre-registered to be, and it establishes no generalisation, no
  superiority and no clinical utility. The MCC interval includes zero.

You can run the boundary against your own sentence:

```bash
cardiosentinel agent check-claims "S4D outperforms GRU"
#   2 violation(s): Appendix A claim 6, Appendix A claim 22   -> exits 1

cardiosentinel agent check-claims \
  "the predefined selection rule selected S4D based on the observed validation contrast"
#   no violations                                             -> exits 0
```

**The guard is lexical, not semantic.** It reduces the failure rate; it does not
make overclaiming impossible, and nothing here should be read as saying
otherwise. Handbook §53.1 states its limits, and §53.2 records the five times it
caught this repository's own authors — including once when `textwrap` split a
disclaimer across two lines and a **correct** output was flagged.

---

## Verify it yourself

All read-only. **These three need nothing but the clone:**

```bash
# the demo bundle is intact
python reproducibility/verify_reproducibility.py
#   -> demo bundle verified: 27 files, 1.63 MiB, all digests match.

# the sealed test has never been opened
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
#                      <- artifact:platt_logistic_on_recovered_logit
#                      <- lock: experiment_id u1-v1-development,
#                               test_accessed false, sealed_test_state unopened
```

**`sealed_test_state: unopened` in that lock is correct and will not change.** It
is U1's attestation about U1 — the calibrator was fitted with the B4 test
unopened, and the lock says so about itself. It is not a status board. Sixty-seven
`.json` artifacts carry that field, thirteen of them `EXPERIMENT_LOCK.json` files
pinned by a self-referential digest, and **editing one to reflect 2026-08-25
would be falsifying a record, not updating it.** Handbook §43 says how to read
the field, and carries those counts with the date they were measured.

**And this one needs the full evidence tree**, which is git-ignored and not
distributed — it is what *we* run, listed so you can see what we check:

```bash
find cardiosentinel-runs -iname "*experiment_lock*.json" | wc -l   # -> 20
```

`zero locks on phase9-t1-development-v1 is correct` — that attempt failed at
stage 24, before promotion. A lock would mean it completed. The failure, and the
single-use authorized recovery that followed it, are §5 of the manuscript.

---

## Where the code actually is

**The package layout does not describe where the work is**, and
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) exists to correct that before you
go looking. In short:

```
src/cardiosentinel/
  neural/     86 files, 54,097 lines -- 43% of the codebase, organised by
              experiment ID. Episode reasoning, memory, calibration and the
              longitudinal arm all live here, not in the packages named for them
  edge/        8 files -- the replay-based edge execution environment
  agents/     14 files -- evidence, graph, explanation, research, architecture
              selection, evaluation, and the claim guard
  evaluation/ splits, annotation-after-window targets, contamination registry
              (unrelated to agents/evaluation/, which is the explanation harness)
  episodes/ · personalization/ · uncertainty/   two-line stubs. Empty on purpose,
              and ARCHITECTURE.md §5 names the repair that was not done
```

---

## Reproducibility

[`reproducibility/`](reproducibility/) holds the committed demo bundle, the
checksum manifest, the environment lock, the restore procedure and the
experiment map. Two properties are tested **separately**, and the distinction
was learned the hard way: `tests/reproducibility/` asserts **integrity**,
`tests/edge/test_demo_scenario.py` asserts **usability**. A manifest check
cannot detect a file that was never staged — which is exactly how three
checkpoints were briefly lost to a `.gitignore` rule while the integrity tests
passed.

**The restore procedure must replay mtimes.** Immutability here is asserted in
file times, and object storage assigns its own.

---

## Setup

Python **3.11+**. Raw and derived physiological data and experiment outputs are
never committed; they live in the git-ignored roots `cardiosentinel-data/`,
`cardiosentinel-features/` and `cardiosentinel-runs/`, or outside the repository
entirely.

```bash
pip install -e ".[dev]"                      # core + tests
pip install -e ".[dev,data,signal,ml]"       # everything the demo needs
cardiosentinel --help
```

Filtering is **disabled by default**: the frozen corpus was built under
`processing_profile: raw`, and a band-pass inserted before the representation
would shift every embedding silently
([contract](docs/SIGNAL_PROCESSING_CONTRACT.md)). Data acquisition is plan-only
unless `--execute` is supplied.

Before making research changes, read
[`docs/RESEARCH_SCOPE.md`](docs/RESEARCH_SCOPE.md) and
[`docs/EXPERIMENT_CONTRACT.md`](docs/EXPERIMENT_CONTRACT.md). The repository is
under **Research Baseline v1.0**: frozen for documentation, analysis of existing
evidence, and manuscript drafting. Leaving that freeze requires a named
experiment with a pre-registered protocol.

---

## Current state

Tagged **`ips-agentic-runtime-v1.0`**; the science is frozen at
**`research-freeze-v1.0`**. The pinned checkpoint — commit, counts, open work
and known defects — is [`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md), which
is regenerated wholesale rather than amended.

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

## License and attribution

Code is licensed under the MIT License. See `NOTICE.md` before adding
third-party data, annotations, models, or documentation.
