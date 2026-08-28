# B4 · E12d Instrumented E11 Phase-1 Replication — Design and Preregistration, V1

**DESIGN AND PREREGISTRATION ONLY. NOT AUTHORIZED. NOT EXECUTED.**

E12d is a **diagnostic replication of E11 phase 1** under the E12c
instrumentation. It is **not** a performance experiment, not a checkpoint
search, not a λ experiment, not a new-target experiment, and not a new
outer-held-out evaluation. **No scientific parameter changes.**

**E11 remains Category C and is not revised by anything proposed here.**

---

## 1. The question, and why it is currently unanswerable

E12a established that E11's checkpoint-selection instrument is noisy — four of
six margins below the documented +0.032 argmax bias, one margin of +0.00029213,
AUPRC/loss epoch ordering disagreeing in six of six fits. It could **not**
establish whether the morphology auxiliary objective was still evolving at the
selected epoch, because E11 persisted none of the quantities that would show it.

**E12d asks exactly one question:**

> Did the preregistered morphology auxiliary objective still have meaningful
> learning/geometry dynamics **after** the epoch selected by inner-validation
> AUPRC?

The answer distinguishes two readings of E11's null that E12a explicitly could
not separate: **a weak objective** versus **a weak delivery mechanism**.

---

## 2. Feasibility

**Feasible, with one component still to build.** E12c made every required
quantity observable and proved instrumentation does not perturb training. What
does not yet exist is the **orchestrator** — the driver that binds data, mints
authorities, and runs all three folds × two arms in the historical construction
order. That is implementation work inside the existing, tested seams, and it is
a prerequisite of execution, not of this preregistration.

| requirement | status |
|---|---|
| separate BCE / auxiliary loss per epoch | **available** (`EpochLossRecord`) |
| inner-validation AUROC | **available** (`InnerValidationRecord`) |
| F1-optimal threshold + source partition | **available**, fails closed off-partition |
| per-epoch model checkpoints | **available** (1.20 MB, identity-bound, hashed) |
| per-epoch geometry from checkpoints | **available** (`run_inner_geometry_driver`) |
| outer-held-out structurally unreachable | **available** (`E11FoldAuthority`) |
| three-fold × two-arm orchestrator | **TO BUILD** |

---

## 3. Exact evidence E12d would produce

Per fold ∈ {0,1,2}, per arm ∈ {B0,B1}, per phase-1 epoch:

**Training** — BCE loss; raw auxiliary SmoothL1 loss (**B1 only; B0 records
`null`, never `0.0`**); λ-weighted auxiliary contribution; total loss; learning
rate; runtime.

**Inner validation** — AUPRC; AUROC; F1-optimal threshold; prevalence;
positive/negative counts; immutable score evidence (`.npz` of labels + scores,
SHA-256 recorded).

**Checkpoint** — model-state-only checkpoint, SHA-256, bound to
fold/arm/epoch/git-commit/split-digest.

**Post-hoc geometry** — from each persisted checkpoint: consensus from
**inner-train only**, then inner-validation per-stream ‖delta‖, cosine to that
epoch's consensus, negative-cosine indicator. Single-class streams preserved
with undefined fields. Emitted under `e11-geometry-trajectory-v1` with
`diagnostic_only: true` and `influences_selection: false`.

**Outer-held-out is untouched.** No phase 2, no outer scoring, no outer
geometry, no operating-point evaluation on held-out data. The authority the
driver hands to the diagnostic path exposes only inner-train and
inner-validation.

---

## 4. Historical-replication contract

This is the part that must be verified **before** any trajectory is interpreted.

### 4.1 Required bit-identical

| quantity | expectation |
|---|---|
| inner AUPRC, every epoch, all six fits | **bit-identical** |
| selected epoch, all six fits | **bit-identical** (1, 1, 1, 2, 4, 1) |
| B0 recorded `train_loss`, every epoch | **bit-identical** |
| phase-1 epoch counts | **identical** (5, 5, 5, 6, 8, 5) |

### 4.2 Expected NOT bit-identical, and why — declared in advance

**B1's recorded `train_loss` scalar will differ by roughly 3 × 10⁻⁹ relative.**
E11 accumulated one running total over the *combined* loss tensor; E12d
accumulates BCE and auxiliary separately and recombines them. The two agree
mathematically by linearity but round differently. Measured on a 200-batch
synthetic trace: **absolute 1.35 × 10⁻⁹, relative 3.12 × 10⁻⁹, bit-identical:
False.**

**This does not touch training.** `backward()` receives the identical tensor —
`bce + λ·aux`, built by the same operations in the same order — so weights,
AUPRC and the selected epoch are unaffected. The difference exists only in a
recorded diagnostic scalar.

**Timing is not comparable** and no timing agreement is claimed.

### 4.3 New quantities with no historical counterpart

Inner AUROC, F1 threshold, per-epoch checkpoints, per-epoch geometry. These
cannot be replication-checked because E11 never recorded them; that absence is
the reason E12d exists.

### 4.4 Mismatch policy

**Any deviation in §4.1 halts E12d before interpretation.** The failure state is
written, the run stops, and the mismatch is reported for human review.
**The protocol is never adjusted to force historical agreement.**

---

## 5. Scientific freeze

Unchanged from E11, and not re-derived here: outer split digest
`ce037309cc2d67944acbee76e82700e5a54c9d2ff69bf54a121ab1b8940206c3`; the
registered inner subject splits (lowest third of outer-training subjects by the
frozen serpentine order); seed 2026; `AUX_SEED` 20260826; AdamW `lr=1e-3`,
`weight_decay=1e-4`, no scheduler; `BATCH_SIZE=256`; `MAX_EPOCHS=15`;
`EARLY_STOPPING_PATIENCE=4`; `EARLY_STOPPING_DELTA=1e-6`; augmentation `null`;
`B4BTransformerCNN`; `Linear(128→1)` auxiliary head on the `encode()` tap;
target `post_r_80ms_delta_mv`; **λ = 0.1**; fold-training median/IQR scaling;
**the AUPRC selection rule exactly as registered**.

**Driver construction-order contract.** Because the architecture contains
dropout, the global RNG stream is load-bearing during training. The driver
**must** reproduce E11's order: `initialize_determinism()` → construct model →
build optimizer → build loss → construct loaders. E12c's equivalence tests prove
the instrumentation itself consumes no RNG; that proof is what licenses the
bit-identity claim in §4.1, and it must be re-asserted at run time.

---

## 6. Scope

**Six phase-1 fits only:** fold 0 {B0,B1}, fold 1 {B0,B1}, fold 2 {B0,B1}.

The run ends after phase-1 training, checkpoint selection, and post-hoc
inner-train/inner-validation geometry generation. **No phase 2. No outer
scoring. No outer geometry. No operating point on held-out data.**

---

## 7. Preregistered diagnostic estimands

**Amended at review, before any E12d execution outcome existed.** See §7.0 for
the withdrawal record.

### 7.0 · D1 WITHDRAWN — structurally degenerate at s = 1

The V1 draft preregistered a remaining-descent fraction:

```
D1 (WITHDRAWN)   R(x) = ( x(s) - x(E) ) / ( x(1) - x(E) )
```

**Withdrawn in place, with the reason recorded rather than the definition
quietly edited.** When the selected epoch is the first epoch, `x(s) = x(1)` and
`R` collapses to **exactly 1 by construction**, independent of the trajectory.
It measures the selected epoch's index, not the trajectory's behaviour.

**This is not a hypothetical failure mode: four of the six historical E11 fits
selected epoch 1.** Evaluated on the only real trajectories E11 persisted (total
training loss), `R` is identically `1.0000` in every one of those four fits,
while the replacement `F` separates them:

| fold | arm | s | E | R (withdrawn) | F (replacement) |
|---|---|---|---|---|---|
| 0 | B0 | 1 | 5 | **1.0000** | 0.5344 |
| 0 | B1 | 1 | 5 | **1.0000** | 0.5491 |
| 1 | B0 | 1 | 5 | **1.0000** | 0.4603 |
| 1 | B1 | 2 | 6 | 0.3488 | 0.2716 |
| 2 | B0 | 4 | 8 | 0.1957 | 0.1868 |
| 2 | B1 | 1 | 5 | **1.0000** | 0.4719 |

`R` would have carried **zero information for two-thirds of the experiment**.
It is withdrawn and is not reported by E12d.

### 7.1 · D1′ — post-selection endpoint change (replacement)

```
F(x) = ( x(s) - x(E) ) / ( |x(s)| + EPSILON )
```

with **`EPSILON = 1e-12`**, a fixed numerical guard declared here, before
execution, solely to keep the denominator defined when `x(s)` is zero.

`F` is normalised by the **selected-epoch value**, not by the full-trajectory
descent, so it is well defined and informative when `s = 1`.

| sign | reading |
|---|---|
| `F > 0` | endpoint loss is **lower** after the selected epoch |
| `F = 0` | no endpoint change |
| `F < 0` | endpoint loss is **higher** after the selected epoch |

**Reported continuously.** **No universal effect-size threshold is established
from E12d**, and none is introduced anywhere in this plan.

### 7.2 · D2 — post-selection slope (retained unchanged)

```
S(x) = ( x(s) - x(E) ) / ( (E - s) * ( max_e x - min_e x ) )
```

Reported continuously. `NA` when `E = s` (nothing after selection) or when the
range is zero; both exclusions are declared here, not after seeing data.

### 7.3 · D5 — post-selection volatility (new, descriptive only)

```
V(x) = ( max_{e >= s} x(e) - min_{e >= s} x(e) ) / ( |x(s)| + EPSILON )
```

**`V` is descriptive and may never independently trigger a decision.** It exists
because `F` compares two endpoints and is blind to what happens between them: a
trajectory that falls and rebounds can return a small `F` while having moved a
great deal. `V` makes that visible.

**Note, recorded in advance:** for a monotonically descending post-selection
trajectory `V` equals `F` exactly. Divergence between them is therefore itself
the signal of non-monotone behaviour, and on the historical total-loss
trajectories the two coincide in all six fits — those trajectories are monotone.

### 7.4 · D3 — post-selection geometry travel (retained)

```
G_cos  = | cos_med(E)  - cos_med(s)  | / range_e( cos_med )
G_norm = | norm_med(E) - norm_med(s) | / range_e( norm_med )
```

plus the raw negative-cosine stream count at `s` and at `E`.

### 7.5 · D4 — selection position (retained)

`s / E`, and whether `s` falls before, at, or after the epoch of maximum
consecutive-epoch geometry change.

### 7.6 · Reporting discipline

Every estimand is reported **per fold, per arm, individually**. **No pooling
across folds and no bootstrap interval** — three folds is not a unit count this
programme may make inferential claims from, and E2 already demonstrated what
bootstrapping an argmax-selected quantity does.

---

## 8. Two separate questions, not one normalised comparison

**Amended at review.** The V1 draft compared normalised B1 auxiliary loss
against B0 BCE loss as if they were interchangeable. **They are not** — a
SmoothL1 regression loss on a morphology target and a BCE classification loss
are different quantities on different scales measuring different things, and
normalising them does not make them commensurable.

E12d therefore reports **three trajectories separately for every fold**:

| trajectory | what it answers |
|---|---|
| **B0 BCE** | the control's optimisation behaviour |
| **B1 BCE** | B1's *classification* optimisation behaviour |
| **B1 auxiliary (raw SmoothL1)** | the auxiliary objective's own behaviour |

### 8.1 Auxiliary-maturity question — within B1 only

> Does B1's auxiliary loss continue decreasing after the selected epoch?

Answered from `F_aux`, the post-selection auxiliary slope `S_aux`, and the **raw
per-epoch auxiliary trajectory printed in full**. This question is **not**
answered by any comparison to B0, which has no auxiliary term at all.

### 8.2 Arm-comparison question — geometry only

> Does B1's representation geometry continue evolving after selection more than
> the paired B0 geometry?

Answered from the registered geometry trajectories (`G_cos`, `G_norm`,
negative-cosine counts), which **are** commensurable: both arms produce
embeddings in the same 128-dimensional space and both are measured against a
consensus built the same way.

**The two questions are reported separately and are never combined into a single
score.**

---

## 9. Preregistered decision rule (amended)

**The `R > 0.5` convention from V1 is removed.** It was structurally biased by
`s = 1`: with `R ≡ 1` in four of six fits, that rule would have fired on the
selected epoch's index rather than on any trajectory behaviour.

| decision | preregistered condition |
|---|---|
| **A · SELECTION-PROTOCOL EXPERIMENT JUSTIFIED** | **all three** B1 folds show continued post-selection auxiliary decrease **in the same direction** (§8.1), **AND** B1 shows consistently greater post-selection geometry evolution than paired B0 across **all three** folds (§8.2) |
| **B · DIRECT REPRESENTATION-OBJECTIVE EXPERIMENT JUSTIFIED** | B1 auxiliary trajectories show **no coherent continued-learning pattern** after selection, **AND** B1 geometry does not continue more strongly than B0 |
| **C · GENERAL B4 TRAINING-DYNAMICS INVESTIGATION JUSTIFIED** | B0 and B1 both show **coherent, comparable** post-selection geometry evolution, without a B1-specific auxiliary-delivery pattern |
| **D · NO FURTHER CONCLUSION** | folds disagree; or trajectories are non-monotone in a way that prevents a coherent reading (`V` >> `F`); or any required estimand is `NA`; or the A/B/C conditions are not cleanly met |

**Continuous magnitudes are reported for every branch. No post-hoc magnitude
threshold may be introduced to reach a decision.**

**The escape hatch is explicit and binding:** if "little or no change" cannot be
classified **without inventing a numerical threshold**, the decision is **D**,
not B. Branch B requires a positive finding of incoherence, not the absence of a
finding.

**Explicitly excluded from every branch:** a λ sweep, a second morphology
target, any historical VALIDATION use, any sealed TEST access, and any
outer-held-out alternative-epoch scoring. **No later epoch may be called
"better"** — E12d cannot observe outer outcomes and will not infer them.
**Causality is not claimed from one fold**; every condition requires agreement
across all three.

---

## 10. Compute and storage

**Training wall time: 3.52 h** (the historical phase-1 total, 34 epochs), plus
**0.6 s** of checkpoint writes — **+0.004%**.

**Post-hoc diagnostic wall time: 1.38 h**, run after training, re-runnable, and
**not counted as training time**. Synchronous per-epoch geometry would instead
have added that 1.38 h *inside* training (+40%); E12c's checkpoint-then-post-hoc
design is what avoids it.

| artifact | size |
|---|---|
| phase-1 checkpoints (34 × 1.20 MB) | 40.8 MB |
| inner score evidence | 4.5 MB |
| geometry summaries + manifests | 0.5 MB |
| receipts / binding receipt | 0.3 MB |
| **total** | **46.1 MB** |

Epoch counts could exceed the historical 34 only if replication has already
failed, which halts the run under §4.4.

---

## 11. Risks

1. **Bit-identity may fail for environmental reasons.** E11 used
   `num_workers=4` with `persistent_workers=True` over a memory-mapped array. A
   mismatch may reflect the environment rather than a defect. **Either way the
   run halts and reports** — it is not silently accepted and the protocol is not
   adjusted.
2. **Dropout makes the RNG stream load-bearing.** Any inserted RNG consumption
   would break replication. E12c proved the instrumentation consumes none; this
   must be re-asserted at run time rather than assumed.
3. **Fold 2 B0 is the fragile fit** — 8 epochs and a selected epoch of 4, the
   only non-epoch-1 B0 selection. If its trajectory diverges, the selected epoch
   changes and §4.4 halts the run.
4. **Three folds is not an inferential unit count.** E12d can describe and
   compare; it cannot estimate. No interval is claimed.
5. **The diagnostic consensus is inner-train, E11's was outer-train.** These are
   different estimands under different schemas and **must never be compared or
   pooled**. E12d numbers are not E11 numbers.
6. **A clean E12d result still does not license E12.** Every §9 branch is a
   recommendation about what to investigate, not an authorization.

---

## 12. Explicit non-claims

E12d will not claim any medical or diagnostic performance; will not revise E11's
Category C; will not assert that any epoch other than the selected one would
have performed better on any outer fold; will not generalise beyond
`post_r_80ms_delta_mv` at λ = 0.1; will not treat three folds as an inferential
sample; and will not produce any new outer-held-out scientific outcome.

---

## 13. Authorization boundary

**E12d must not launch until all three hold:**

1. the full `tests/neural` regression sweep for E12c has completed cleanly;
2. this plan has been reviewed;
3. a separate, explicit human authorization is issued.

Under the standing §A8 policy, any re-execution after a failure is a **new
attempt requiring new authorization**. **NO AUTOMATIC RETRY.**
