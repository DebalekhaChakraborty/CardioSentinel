# J1 — Fair stateful vs memoryless episode comparator

**State: `PRE-REGISTERED — NOT AUTHORIZED`.** Nothing here authorizes execution.

J1 exists to remove the one limitation that bounds the V1 W1 result. W1's own
report names it: both arms ran at `qw0.9_qe0.99_FAST`, an operating point whose
quantile levels were selected **jointly with** `event_confirm_windows = 2`, a
state-machine parameter. The memoryless arm was therefore evaluated at a point
tuned for a rule it does not implement, and the report concludes that *"a
memoryless rule given its own operating point would very likely score better than
Arm W does here."*

J1 asks the question that leaves open:

> Does T1-like stateful episode reasoning retain an advantage when the memoryless
> comparator receives its own independently selected development operating point?

## Documents

| File | Status |
|---|---|
| [`J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1.md`](J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1.md) | **FROZEN — NOT AUTHORIZED** |
| [`J1_PRE_REGISTRATION_V1.md`](J1_PRE_REGISTRATION_V1.md) | **PRE-REGISTERED — NOT AUTHORIZED** |
| [`J1_FREEZE_RECEIPT_V1.md`](J1_FREEZE_RECEIPT_V1.md) | **ACTIVE GOVERNANCE BINDING** |
| [`J1_EXECUTION_INSTRUMENT_SPEC_V1.md`](J1_EXECUTION_INSTRUMENT_SPEC_V1.md) | **QUALIFICATION CANDIDATE — NOT AUTHORIZED** |
| [`J1_ENVIRONMENT_AUTHORITY_SPEC_V1.md`](J1_ENVIRONMENT_AUTHORITY_SPEC_V1.md) | **QUALIFICATION CANDIDATE — NOT AUTHORIZED** |
| [`J1_ENVIRONMENT_QUALIFICATION_RECEIPT_V1.md`](J1_ENVIRONMENT_QUALIFICATION_RECEIPT_V1.md) | **MECHANISM QUALIFIED — NO ENVIRONMENT SUBMITTED** |
| [`J1_COLLABORATOR_IMPLEMENTATION_RECEIPT_V1.md`](J1_COLLABORATOR_IMPLEMENTATION_RECEIPT_V1.md) | **QUALIFICATION CANDIDATE — NOT AUTHORIZED**; 7 of 7 collaborators real |
| [`J1_AUTHORIZATION_CONTRACT_V1.md`](J1_AUTHORIZATION_CONTRACT_V1.md) | **ABSENT — NO AUTHORIZATION EXISTS**; the boundary a human act will populate |
| [`J1_RUNTIME_AND_DEPENDENCY_LOCK_V1.md`](J1_RUNTIME_AND_DEPENDENCY_LOCK_V1.md) | **ESTABLISHED FROM FROZEN EVIDENCE**; 4 of 12 record fields determined, no artifact |

> ## Pre-registration is not authorization.

> **No real-data access may occur until a separate authorization names the frozen
> digests, data authority and attempt budget.**

**Human freeze review is complete.** Both scientific documents are frozen and
digest-bound by [`J1_FREEZE_RECEIPT_V1.md`](J1_FREEZE_RECEIPT_V1.md).

**J1 is `PRE-REGISTERED`, not `AUTHORIZED`.** No authorization document exists, no
attempt budget is set, no data authority is granted, no fold manifest has been
generated and no result exists.

## The population finding that shaped this design

The audit that preceded this protocol found that **J1 cannot be run on the
population V1 developed T1 and W1 on.**

```
V1 split (protocols/splits/ltstdb_v1.json):  56 train / 12 validation / 12 test
T1 and W1 development pool:                  the 12 VALIDATION subjects
Population the V2 Evidence Authority permits: V1 TRAIN
overlap:                                      0 subjects
```

The V1 edge runtime refuses any subject outside those twelve, in code, at
[`src/cardiosentinel/edge/artifacts.py`](../../../src/cardiosentinel/edge/artifacts.py):

> `'…' is not one of the twelve T1 validation subjects, so no leave-one-subject-out
> operating point exists for it. The edge runtime refuses to borrow another
> subject's thresholds.`

**That refusal is correct and is not modified by J1.** It is a property of the V1
deployment runtime. J1 will eventually need a separately governed research
evaluation path that takes explicitly supplied V2 cross-fitted artifacts. That
path is not implemented in this task.

## Route decisions, recorded

| Route | Decision | Reason |
|---|---|---|
| J1 on the 12 historical VALIDATION subjects | **Rejected** | Historical-only evidence under the V2 Evidence Authority. Consumed evidence cannot be made fresh, and convenience of existing artifacts is not an argument. |
| Lower the common boundary from `(d_t, p_t, s_t)` to `d_t` alone | **Rejected as primary** | Changes the estimand relative to the V1 T1/W1 limitation and would no longer test the retained episode-policy contrast. May return later as a separately labelled ablation. |
| **V1-TRAIN-only prospective cross-fitting with a common regenerated upstream scaffold** | **Selected** | The only route that produces fresh `V2_DEVELOPMENT` evidence for the question actually asked. |

## Component audit — what is re-fit, and what is not

Classified against the retained V1 chain. The principle is minimal regeneration:
a component is re-fit only where the historical artifact is unavailable for TRAIN
subjects, not merely because J1 has moved partition.

| Component | Class | Why |
|---|---|---|
| **B4 encoder / detector** — produces `m2g_detector_score`, `detector_decision_d_t` | `FROZEN_REUSED` *(closed, §1)* | Trained on the 56 TRAIN subjects. Inherited as a fixed V1 mechanism; re-fitting it would make J1 a representation experiment. |
| **P1 physiology fusion** | `FROZEN_REUSED` | Deterministic given the row; no subject-specific fitted state identified. |
| **M1 patient-relative memory** | `FROZEN_REUSED` | Patient-relative by construction — it adapts *within* a subject's stream rather than being fitted across a development pool. |
| **M2 contamination gate** | `FROZEN_REUSED` | Frozen thresholds and a frozen refractory. `m2_gate_outcome` and `m2_update_admitted` are on the forbidden-input list, so the gate cannot leak into the episode decision. |
| **U1 Platt calibration** — produces `oof_calibrated_probability_p_t` | **`TRAIN_CROSSFIT_REQUIRED`** | The field name says `oof`: out-of-fold by contract. U1's folds are LOSO over the twelve VALIDATION subjects, and the all-VALIDATION deployment calibrator is explicitly *forbidden* for development. No calibrator exists for any TRAIN subject. |
| **T2 S4D temporal** — produces `s4d_temporal_evidence_s_t` | **`FROZEN_REUSED`** *(closed, §2)* | Fitted on TRAIN through a frozen internal split. Cross-fitting it inside J1 would make J1 a temporal-model **and** policy experiment, changing the estimand. |
| **T1 quantile levels + persistence profile** | `ARM_SPECIFIC_TUNING` | The J1-S selection space — what J1 exists to select independently. |
| **W1 threshold / rule** | `ARM_SPECIFIC_TUNING` | The J1-W selection space, which must be credible. |
| **U1 selective router** | `NOT_USED_IN_J1` | Rejected in V1 as a negative finding. |
| **B4-B sealed test evidence** | `NOT_USED_IN_J1` | Consumed. Permanently unavailable. |

### Decision 10 — CLOSED: B4-B was trained on the 56 TRAIN subjects

Verified from the canonical experiment lock, not from prose.

| | |
|---|---|
| Lock | `cardiosentinel-runs/phase3b2-architecture-v1/B4B_cnn_transformer_v1/EXPERIMENT_LOCK.json` |
| `experiment_lock_sha256` | `58e44a09ce3ebffecfcd49d957acfa368fc03b534fdcd990aedb9b6b0e9bda7b` — matches `B4B_BINDING` in `neural/b4b_sealed_test.py` |
| `training_rows.partition` | **`train`** |
| `training_rows.subjects` | **56** |
| `validation_rows` | `validation`, 12 subjects |
| `split_sha256` | `66e25d77b6aaa25502974b4b60667b4c4b24d649bf9493666827c747a385ced7` — identical to `protocols/splits/ltstdb_v1.json` |
| Checkpoint | `model_selected.pt`, `b1301723909c641a0014c31f6daa9549d47ab231f0b07483e0de729aff5591c9` |

**What this means, stated precisely.** B4 is inherited as a fixed V1 mechanism. It
was trained using the **same 56 subjects** on which J1 development evidence will
be measured. Therefore:

- **J1 is not a fully out-of-sample evaluation of the whole CardioSentinel system.**
- J1 estimates a **conditional episode-policy contrast given the inherited
  upstream scaffold**.
- Using the same fixed upstream for both arms removes upstream model identity as
  an intentional arm difference. **It does not prove that upstream in-sampleness
  has zero interaction with policy behaviour.**
- **Absolute J1 performance numbers are development evidence only** and must never
  be presented as generalization performance.

### Decision 11 — CLOSED: T2 S4D is `FROZEN_REUSED`

| | |
|---|---|
| Fitting population | the 56 TRAIN subjects, via a frozen internal split |
| Internal split | **48 FIT** / **8 INTERNAL-DEV** (early stopping, checkpoint selection) |
| Algorithm | `sha256_identity_ranked_subject_partition_v1`, seed string `cardiosentinel-t2-internal-split-v1` |
| Split inputs | subject identity and seed only — *"No label, prevalence, episode count or model outcome participates."* |
| VALIDATION / TEST in fitting | none. *"The 12-subject outer VALIDATION partition is not repeatedly tuned against."* |
| Arm selection | consumed **outer-VALIDATION pooled AUPRC**, once, after training |

**Classified `FROZEN_REUSED`, not `TRAIN_CROSSFIT_REQUIRED`.** J1 is a policy-layer
ablation conditional on the inherited retained upstream. Retraining or
cross-fitting T2 inside J1 would turn J1 into a temporal-model **and** policy
experiment and alter the estimand.

**Limitation, recorded.** The frozen T2 mechanism was itself developed using the
TRAIN population, and its arm identity was selected on outer VALIDATION. So a
**J1 outer assessment fold is not held out from all historical upstream model
development.** It is held out prospectively from exactly three things:

1. J1's U1 calibration fitting for those subjects' rows;
2. J1-S operating-point selection;
3. J1-W operating-point selection.

The term **"J1 outer assessment fold"** is used throughout in preference to any
wording implying a fully unseen system-test population.

## What this task did not do

No physiological data was opened. No fold was generated. No model was fitted, no
calibration fitted, no threshold derived, no ECG inference run, no result
computed. No authorization exists and no attempt budget is set.
