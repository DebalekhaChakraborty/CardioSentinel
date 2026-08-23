# CardioSentinel

**An evidence-grounded intelligent physical system for adaptive ECG
monitoring.** CardioSentinel senses a physiological stream, reasons over it with
patient-adaptive temporal models, explains its own alerts from frozen
provenance, and refuses to state claims its evidence does not support.

It is **not a medical device** and does not provide diagnosis, treatment, or
medical recommendations.

## What the system does

| | |
|---|---|
| **Causal temporal modelling** | a diagonal state-space model carrying state across windows, plus a frozen four-state episode machine |
| **Patient-aware adaptation** | dual-timescale memory that scores each window *before* updating from it |
| **Contamination-safe learning** | a six-condition admission gate; abnormal windows never move the patient baseline |
| **Evidence-backed alerts** | every alert carries the checkpoint, calibrator, threshold policy and experiment lock behind it |
| **Research traceability** | 16 experiment locks; provenance reachable from any alert by graph traversal |
| **AI-assisted explanation** | agents that translate evidence into language, with a publication claim boundary enforced in code |

**Run the simulation** — replays a stored LTSTDB recording as a live stream:

```bash
cardiosentinel edge simulate s20201 --seconds 2400   # ECG -> alerts, ~61x real time
cardiosentinel agent why s20201                      # why did it alert?
cardiosentinel agent research "Why was S4D selected instead of GRU?"
```

## What the system does NOT do

This list is load-bearing and is enforced in code by
`agents/claims.py`, which encodes 18 of the handbook's forbidden claims:

- **No diagnosis.** Detection only, and no clinical utility is claimed.
- **No deployment.** There is no serving path, no ONNX, no TorchScript.
- **No edge-hardware result.** The runtime is a **laptop simulation replaying a
  stored recording**. There is no sensor and no acquisition path. RQ5 is open.
- **No generalisation beyond LTSTDB.** One dataset, twelve validation subjects,
  and no independent cohort exists in the public record.
- **No test-set performance.** The neural sealed test is **unopened**.

**State:** `ips-agentic-runtime-v1.0` at `origin/master` `9f38f47`. The
authoritative record is
[`docs/CardioSentinel_Research_Execution_Handbook_v1.4.md`](docs/CardioSentinel_Research_Execution_Handbook_v1.4.md);
architecture is [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Project evolution

This repository previously hosted a 2020 B.Tech prototype based on fixed ECG
thresholds. That work is retained unchanged in
[`legacy/college-v1/`](legacy/college-v1/README.md) for historical traceability.
It is not part of the CardioSentinel pipeline and its outputs are not clinical
evidence.

The current research objective is a reproducible system that can eventually
support the physical-system loop:

`ECG acquisition or replay -> edge processing -> patient-adaptive inference -> uncertainty -> local decision or escalation -> temporal episode reasoning -> evidence-grounded alert`.

No clinical effectiveness claim is made. Physiological data and experiment
outputs remain external to this repository.

## Repository structure

- `src/cardiosentinel/`: package and future research domains.
- `configs/`: versioned, validated configuration profiles.
- `docs/`: scope, integrity contract, audit, and implementation roadmap.
- `tests/`: offline unit, contract, and integration tests.
- `data/` and `artifacts/`: documented local locations; their contents are not
  committed.
- `legacy/college-v1/`: preserved academic prototype.

## Setup

Python 3.11 is the initial supported version.

```bash
python -m pip install -e ".[dev]"
python -m cardiosentinel --help
python -m cardiosentinel info
```

Raw or processed physiological data is not included. Read
[`docs/RESEARCH_SCOPE.md`](docs/RESEARCH_SCOPE.md) and
[`docs/EXPERIMENT_CONTRACT.md`](docs/EXPERIMENT_CONTRACT.md) before conducting
research changes.

## Development status

Phase 1 implementation and annotation-semantic validation are complete for
header and annotation metadata from EDB and LTSTDB. Phase 2 implements a bounded
physical-waveform reader, canonical mV representation, raw identity profile,
optional stateful causal filters, causal windows, descriptive signal-quality
metrics, and filter audits. Bounded physical-waveform integration validation is
complete for the first 60 seconds of EDB `e0113`, EDB `e0161`, and LTSTDB
`s20011`. Phase 3A freezes the LTSTDB `.stb` benchmark protocol, 56/12/12
subject split, causal 10-second/5-second window targets, leakage controls,
training-sampling policy, and metrics protocol. Phase 3B-1 is complete: each
frozen B0--B3 global classical baseline received one sealed-test evaluation,
with no test-guided tuning. The compact evidence and limitations are recorded in
[`docs/PHASE3B1_CLASSICAL_BASELINE_RESULTS.md`](docs/PHASE3B1_CLASSICAL_BASELINE_RESULTS.md).
The B4 neural-architecture selection, frozen in
[`docs/B4_PROTOCOL_V1.md`](docs/B4_PROTOCOL_V1.md), is complete: three
candidates (compact CNN, CNN-Transformer, CNN-SSM) were trained and compared
on validation, and B4-B (CNN-Transformer) is the selected official model
(see [`docs/B4_GLOBAL_ENCODER_SELECTION_V1.md`](docs/B4_GLOBAL_ENCODER_SELECTION_V1.md)).
Physiology fusion, patient-adaptive memory, and contamination-safe memory
updates are each complete and frozen. Calibration is a **split** retention:
Platt calibration is retained, and the window-level selective router at
`c_star = 0.90` is explicitly **not** retained, so no routing policy is frozen
or in force
(see [`docs/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md`](docs/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md)).
Longitudinal temporal modeling is trained, one-shot outer-validated, and
analysed: the S4D and GRU arms are compared in
[`docs/T2_ARM_COMPARISON_REPORT_V1.md`](docs/T2_ARM_COMPARISON_REPORT_V1.md).
The predefined rule selected the causal S4D arm on the observed validation
contrast; that contrast **is** the selection criterion, and its paired
subject-bootstrap interval includes zero, so no claim of superior performance
follows from it.

The causal episode-state layer has been executed and measured; its result is
reported in [`docs/T1_DESCRIPTIVE_REPORT_V1.md`](docs/T1_DESCRIPTIVE_REPORT_V1.md)
and no further execution is authorized. A window-only comparator was then
pre-registered and run against it
([`docs/W1_WINDOW_COMPARATOR_REPORT_V1.md`](docs/W1_WINDOW_COMPARATOR_REPORT_V1.md)):
at the frozen operating point the episode state machine agrees with reference
episodes substantially better than a memoryless rule does at that same point.
That is the first research question this programme answers affirmatively, and
the operating point is part of the claim — both arms ran at thresholds selected
with the state machine in the loop, so it does not show that episode reasoning
beats window-level alerting in general.

External validation has been scoped but not performed. No independent
ST-episode cohort exists in the public record; the audit and its consequences
are in
[`docs/EXTERNAL_VALIDATION_STRATEGY_V1.md`](docs/EXTERNAL_VALIDATION_STRATEGY_V1.md).
The B4 neural sealed test remains unopened. See
[`docs/CURRENT_STATE.md`](docs/CURRENT_STATE.md) for the current experiment
ladder, open work, and known risks.

Data commands require the optional `data` dependency group and never download
data during import or tests:

```bash
python -m pip install -e ".[dev,data]"
python -m cardiosentinel data --help
```

Signal commands require the optional `signal` dependency group. High-pass,
low-pass, and notch filtering are disabled by default:

```bash
python -m pip install -e ".[dev,data,signal]"
python -m cardiosentinel signal --help
```

See [`docs/SIGNAL_PROCESSING_CONTRACT.md`](docs/SIGNAL_PROCESSING_CONTRACT.md)
for the causality, physical-unit, filtering, quality, and ground-truth boundary.

Benchmark commands inspect metadata and annotations without training or full
waveform downloads:

```bash
python -m cardiosentinel benchmark --help
python -m cardiosentinel benchmark split-info \
  --split protocols/splits/ltstdb_v1.json
```

The frozen rules are in [`docs/BENCHMARK_PROTOCOL_V1.md`](docs/BENCHMARK_PROTOCOL_V1.md),
with metrics in [`docs/METRICS_PROTOCOL.md`](docs/METRICS_PROTOCOL.md) and known
EDB/LTSTDB overlap in
[`docs/CROSS_DATASET_PROVENANCE.md`](docs/CROSS_DATASET_PROVENANCE.md).

Classical baseline commands require the `ml` extras. Raw and derived
physiological data and experiment outputs are never committed to Git. They may
use explicit roots outside the repository filesystem or the approved Git-ignored
local roots `cardiosentinel-data/`, `cardiosentinel-features/`, and
`cardiosentinel-runs/`:

```bash
python -m pip install -e ".[dev,data,signal,ml]"
python -m cardiosentinel baseline --help
python -m cardiosentinel baseline acquire \
  --destination /external/data/ltstdb/1.0.0
```

The acquisition command is plan-only unless `--execute` is supplied. The frozen
feature, model, preprocessing, sampling, test-access, and artifact rules are in
[`docs/BASELINE_PROTOCOL_V1.md`](docs/BASELINE_PROTOCOL_V1.md).

### Monitoring Phase 3B materialization

The read-only Phase 3B monitor reports progress from an existing external
feature root. It does not access waveform source data, run models, or change
feature caches or manifests:

```bash
python scripts/monitor_phase3b.py
watch -n 30 python scripts/monitor_phase3b.py
```

To inspect a different external feature root:

```bash
python scripts/monitor_phase3b.py --feature-root /path/to/features
```

### Auditing a completed Phase 3B corpus

The read-only corpus audit validates every cache and the persisted corpus hash
before reporting frozen primary counts, descriptive challenge/exclusion families,
and algorithmic morphology-feature validity:

```bash
python scripts/audit_phase3b_corpus.py \
  --feature-root /path/to/ltstdb-baseline-v1
```

## License and attribution

The repository code is licensed under the MIT License. See `NOTICE.md` before
adding third-party data, annotations, models, or documentation.
