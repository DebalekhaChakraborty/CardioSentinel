# T1 Post-hoc Failure Mode Analysis and Interpretation, V1

**POST-HOC ANALYSIS. This document was written after the measured values were
read.** It is not part of the pre-registration in
`docs/T1_EVIDENCE_ANALYSIS_PLAN_V1.md` and it carries none of that document's
authority. Every quantity here that is not already published in
`docs/T1_DESCRIPTIVE_REPORT_V1.md` is labelled **post-hoc descriptive
analysis** at the point it appears.

## What this document does not do

| | |
|---|---|
| Changes the primary endpoint | **No.** The registered primary remains the subject-macro mean `episode_f1` |
| Changes the primary value | **No.** `episode_f1 = 0.2524` is unchanged and is not recomputed anywhere in this document |
| Removes any subject | **No.** All twelve subjects remain in the registered estimate, including the three with no reference episodes |
| Presents a new headline number | **No.** No alternative performance figure is computed, reported, or implied |
| Recomputes any metric | **No.** Only counts already published in the descriptive report are quoted |
| Alters any promoted artifact | **No.** All seven artifact digests re-verify unchanged |

The registered result stands exactly as reported:

```
Subject-macro mean episode_f1 = 0.2524
95% subject-bootstrap interval = [0.0826, 0.4415]
```

This analysis explains **what the zeros inside that mean are made of**. It does
not adjust the mean, and a reader who wants a single number should continue to
use the registered one.

---

## 1. The seven zero-`episode_f1` subjects are two different failure modes

Seven of twelve subjects score `episode_f1 = 0.0000`. The descriptive report
§9.1 records that these zeros arise for two incomparable reasons. This section
separates them.

`_episode_f1` returns `2 · matched / (predicted_event_runs + reference_episodes)`
and returns undefined **only** when that denominator is zero. A subject with no
reference episodes but at least one predicted run therefore has a non-zero
denominator, zero matches, and a defined score of exactly `0.0`.

### 1.1 Group A — episode-free subjects carrying a false-alarm burden

These subjects have **no annotated ischemic episodes at all**. Their zero is a
false-alarm penalty, not a failure to detect: there was nothing available to
detect.

| Subject | Fold | Reference episodes | Predicted runs | Unmatched predicted runs | FP windows | TP | FN | `episode_f1` |
|---|---|---|---|---|---|---|---|---|
| `ltstdb:s2005` | 1 | **0** | 7 | 7 | 6,947 | 0 | 0 | 0.0000 |
| `ltstdb:s2020` | 3 | **0** | 8 | 8 | 4,764 | 0 | 0 | 0.0000 |
| `ltstdb:s2023` | 4 | **0** | 1 | 1 | 2 | 0 | 0 | 0.0000 |

> **Post-hoc descriptive analysis.** Summing the published counts: these three
> subjects contribute **16 predicted event runs** and **11,713 false-positive
> windows** against **0 reference episodes**. No rate, ratio or normalised
> quantity is derived from these sums.

**Interpretation.** For Group A the measurement is one of *false-alarm burden on
subjects without annotated episodes*. `primary_window_mcc` is undefined for all
three because the reference-positive margin is empty, and
`onset_latency_seconds_median` is undefined because no episode existed to match.
Both undefined values are reported as undefined in the descriptive report and
are not filled here.

### 1.2 Group B — reference episodes present, no matched detection

These subjects **do** have annotated episodes. Their zero is a genuine detection
failure.

| Subject | Fold | Reference episodes | Predicted runs | Matched | FN windows | TP | `episode_f1` |
|---|---|---|---|---|---|---|---|
| `ltstdb:s2019` | 2 | **6** | 0 | 0 | 138 | 0 | 0.0000 |
| `ltstdb:s2058` | 7 | **3** | 0 | 0 | 99 | 0 | 0.0000 |
| `ltstdb:s2059` | 8 | **47** | 0 | 0 | 1,241 | 0 | 0.0000 |
| `ltstdb:s3072` | 10 | **1** | 1 | 0 | 47 | 0 | 0.0000 |

> **Post-hoc descriptive analysis.** Summing the published counts: these four
> subjects carry **57 reference episodes**, of which **0 were matched**, and
> **1,525 false-negative windows**. No rate, ratio or normalised quantity is
> derived from these sums.

**Interpretation.** For Group B the measurement is one of *complete detection
failure on subjects that had annotated episodes*. Three of the four produced no
predicted event run at all; `ltstdb:s3072` produced one run that did not overlap
its single reference episode, so it is a matching failure rather than a silence.
That distinction is visible in the published counts and is recorded here without
further inference about cause.

### 1.3 Why the two groups must not be pooled in interpretation

Both groups contribute `0.0000` to the registered mean, and the mean cannot
distinguish them. They answer different questions:

| | Group A | Group B |
|---|---|---|
| What the zero measures | False alarms where nothing was annotated | Failure to detect what was annotated |
| Clinical failure mode | Alarm fatigue | Missed ischemia |
| Would improve by | Fewer predicted runs | More predicted runs |

The last row is the point: the two failure modes push the operating point in
**opposite directions**, so any change that improves one is liable to worsen the
other. A single averaged score conceals that tension. This is an interpretive
observation about the reported evidence and is not a proposal to change the
estimator, the thresholds, or the registered result.

**No subject is excluded, and no adjusted mean is offered.** Excluding Group A
would remove the false-alarm penalty and raise the headline, which is precisely
the appearance a post-hoc analysis must avoid.

---

## 2. Latency interpretation

The descriptive report §6 and §9.2 report onset latency. This section fixes how
it may be described.

**Definition.** `_onset_latency` computes

```
(start_samples[run_begin] - start_samples[episode_begin]) / 250.0
```

seconds from a matched episode's annotated onset to its matched run's onset. It
is a **signed offset**, not a delay. Negative values indicate the matched
predicted run started **before** the annotated episode onset.

**Why a negative offset does not establish anticipation.**
`match_runs_to_episodes` pairs a run to an episode on **overlap alone** —
`run_begin < end and begin < run_end` — with **no tolerance window** and no
bound on how early a run may begin. A negative offset is therefore equally
consistent with:

- a **persistent `EVENT` state** that was already active and merely overlaps the
  annotated episode, and
- a **long-duration detected run** that spans the annotated onset.

The artifacts record `onset_latency_seconds` but **not run durations**, so this
evidence cannot separate those from genuine anticipation.

**Prohibited terminology.** The following must not be used of any T1 latency
figure, in this repository or in any manuscript drawn from it:

| ❌ Prohibited | Why |
|---|---|
| "early detection" | Asserts anticipation the overlap matcher cannot establish |
| "warning time" | Implies a clinically actionable interval before onset |
| "predictive lead time" | Implies a validated prediction horizon |

**Acceptable phrasing:** *"signed onset offset"*, *"median latency across
detected episodes"*, or *"episode-level onset latency distribution among
detected episodes"*, each stating the sign convention.

---

## 3. Limitations

**This study does not evaluate:**

- **Improvement over a T1-disabled baseline.** No T1-disabled arm was run on
  these held-out subjects. The study measures one configuration; it compares
  nothing.
- **Memory contribution.** No no-memory arm exists at the episode level.
- **S4D contribution at the episode level.** The continuation measured the
  retained arm only; no file in the run references the declared comparator arm
  `causal_gru_longitudinal_v1`.
- **External generalization.** One dataset, 12 validation subjects. EDB shares
  source recordings with LTSTDB per `docs/CROSS_DATASET_PROVENANCE.md` and is
  not a clean external cohort.
- **Deployment performance.** No inference or serving path exists — no
  `predict()`, no ONNX, no TorchScript. No latency or throughput claim about a
  deployed system is available.
- **Clinical utility.** Research software validated on a public dataset only.
- **Causal inference.** "Causal" throughout this programme means temporal
  non-anticipation — `t1_protocol.next_state` reads "nothing ahead of it" — and
  never a treatment effect, intervention or counterfactual.
- **Subgroup performance.** `join_performed: false`, `strata_reported: []`,
  recorded before execution.

Each is a boundary fixed by what was run, not a gap discovered in the numbers.

---

## 4. Calibration positioning

U1 was a **split** retention decision, and describing it as a single retained
system misstates the record.

**Correct statement:**

> U1 Platt calibration was retained to calibrate continuous scores. The
> selective routing mechanism was evaluated but not retained.

Per `docs/U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md`, the frozen symmetric
window-level selective-routing policy at `c_star = 0.90` carries
`retained: false` as the downstream or final operational router. The rejected
router was preserved rather than deleted, which is a provenance decision and not
a retention one.

**Prohibited statements:**

| ❌ Do not say | Why |
|---|---|
| "adaptive routing implemented" | The router exists in code but was explicitly not retained |
| "uncertainty routing deployed" | Nothing is deployed; there is no serving path at all |
| "selective prediction system" | Implies an operational abstention mechanism that was rejected |

Any document claiming that edge/cloud routing is complete is wrong and should be
corrected against the retention decision.

---

## 5. Scientific boundary verification

Performed before this document was opened as a pull request.

| Boundary | Result |
|---|---|
| New metrics generated | **None.** Only counts already published in the descriptive report are quoted; group sums are labelled post-hoc descriptive |
| New experiments executed | **None.** No run was started; none is authorized |
| Test partition access | **None.** `sealed_test_state: unopened`, `test_accessed: false` in every artifact |
| Threshold changes | **None.** Thresholds remain frozen per fold in the promoted fold-selection artifacts |
| Model retraining | **None.** No checkpoint was read or written |
| Artifact modification | **None.** All seven digests re-verify |

### 5.1 Artifact digests at the time of writing

| Artifact | SHA-256 | Unchanged |
|---|---|---|
| `T1_OOF_RESULT.json` | `9309b00b55173e00ee793d2468b6aaf796105928c0e5241537ef3fe80ccec6ae` | ✅ |
| `T1_SUBJECT_EVIDENCE.json` | `6695dd36d890dfdc5e6e6fa16514f2cee8676b7402ba93f0c0f9c10b27223120` | ✅ |
| `T1_BOOTSTRAP.json` | `57ba66553e712a63b0f670cbb01bc9d680c824a90a2c9b723baa1aaa1adc0f48` | ✅ |
| `T1_CHALLENGE_EVIDENCE.json` | `0eb8e684944da6768511d57264b20b8d201ab935bdb73125a0f41f9b3fed2d25` | ✅ |
| `T1_FINAL_CONFIGURATION.json` | `374114293160c1f778a4803ff3a2d893d0eda2b81d6277ae326e201084495a34` | ✅ |
| `T1_EXPERIMENT_LOCK.json` | `bcbdfdb08293b9c2ba7a9abef38d185e3128177c555b01dea0b81ec62f726a76` | ✅ |
| `T1_V1_CONTINUATION_EXECUTION_ATTESTATION.json` | `b5a557dd40927999e00516e982c2f1619fdbeb3e5ebdd3ad108037b474eca588` | ✅ |

The consumed development attempt remains 20 files at `2026-08-21T19:57:57`; the
continuation run remains 19 files at `2026-08-22T16:18`. Neither directory was
written to.
