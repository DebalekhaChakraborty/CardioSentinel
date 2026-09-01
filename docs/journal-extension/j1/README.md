# J1 — Fair stateful vs memoryless episode comparator

**State: `PLANNED / NOT AUTHORIZED`.** Nothing here authorizes execution.

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
| [`J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1.md`](J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1.md) | PROPOSED / NOT AUTHORIZED |
| [`J1_PRE_REGISTRATION_V1.md`](J1_PRE_REGISTRATION_V1.md) | **NOT READY TO FREEZE** — unresolved human decisions |

No authorization document exists. No report, result or decision document exists.

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
| **B4 encoder / detector** — produces `m2g_detector_score`, `detector_decision_d_t` | `FROZEN_REUSED` *(pending verification, see below)* | A learned representation whose frozen implementation can generate causal evidence for any subject. Re-fitting it would make J1 a representation experiment. |
| **P1 physiology fusion** | `FROZEN_REUSED` | Deterministic given the row; no subject-specific fitted state identified. |
| **M1 patient-relative memory** | `FROZEN_REUSED` | Patient-relative by construction — it adapts *within* a subject's stream rather than being fitted across a development pool. |
| **M2 contamination gate** | `FROZEN_REUSED` | Frozen thresholds and a frozen refractory. `m2_gate_outcome` and `m2_update_admitted` are on the forbidden-input list, so the gate cannot leak into the episode decision. |
| **U1 Platt calibration** — produces `oof_calibrated_probability_p_t` | **`TRAIN_CROSSFIT_REQUIRED`** | The field name says `oof`: it is out-of-fold by contract. U1's folds are LOSO over the twelve VALIDATION subjects, and the all-VALIDATION deployment calibrator is explicitly *forbidden* for development. No calibrator exists for any TRAIN subject. |
| **T2 S4D temporal** — produces `s4d_temporal_evidence_s_t` | **`TRAIN_CROSSFIT_REQUIRED`** *(pending verification)* | T2's development used an 8-subject internal partition inside the twelve. Whether the S4D model itself is subject-agnostic and reusable, or requires TRAIN cross-fitting, is listed under verification below. |
| **T1 quantile levels + persistence profile** | `ARM_SPECIFIC_TUNING` | This is the J1-S selection space. It is the thing J1 exists to select independently. |
| **W1 threshold / rule** | `ARM_SPECIFIC_TUNING` | This is the J1-W selection space, and it must be a credible one. |
| **U1 selective router** | `NOT_USED_IN_J1` | Rejected in V1 as a negative finding; not part of the retained chain. |
| **B4-B sealed test evidence** | `NOT_USED_IN_J1` | Consumed. Permanently unavailable. |

### Verification required before freeze — not assumed here

Two classifications above are marked *pending verification* because the audit
established them from documentation rather than by tracing the fitting code, and
the difference changes what J1 must regenerate:

1. **Was the B4 encoder fit on the 56 TRAIN subjects?** If it was, then scoring a
   TRAIN subject with it is **in-sample**, and every J1 evidence row is partly a
   function of its own subject's contribution to the encoder. See the protocol's
   treatment of this — it does not invalidate the paired contrast, but it bounds
   what the absolute values mean and must be stated.
2. **Is the T2 S4D model subject-agnostic?** If it is, it is `FROZEN_REUSED`. If
   its fitting consumed the twelve, it is `TRAIN_CROSSFIT_REQUIRED`.

Both are read-only code-tracing tasks. Neither requires data access.

## What this task did not do

No physiological data was opened. No fold was generated. No model was fitted, no
calibration fitted, no threshold derived, no ECG inference run, no result
computed. No authorization exists and no attempt budget is set.
