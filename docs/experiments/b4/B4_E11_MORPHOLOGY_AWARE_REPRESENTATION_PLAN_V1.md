# B4 · E11 Morphology-Aware Representation Generalization — Design Audit and Preregistration, V1

**This document designs and registers. It authorizes nothing and trains
nothing.** §1–§3 are the read-only audit; §4 onward is the pre-registration.

**E11 requires a fresh human authorization before any training begins.**
Fifteen of fifteen one-shot budgets are spent; §10 estimates the cost.

**E11 is a new development experiment. It does not change, reopen or
re-interpret the historical sealed B4 result, which remains consumed with
`repeat_attempt_permitted: false`.** No sealed artifact is read at any point.

---

## 1. Auxiliary target audit

### 1.1 The eight signed features, and their provenance

All eight come from `combined_v1` (schema `13f60be400b5b957c1eb592b…`),
`processing_profile: raw`, 10 s windows at 5 s stride, annotation definition
`ltstdb.stb`. All are **baseline-relative in mV** against the median waveform
200–80 ms before the detected R peak.

Measured over the **2,208,431 TRAIN windows** (93,613 positive, 4.2389%):

| feature | non-finite | neg median | neg IQR | pos median | \|Δmedian\| | \|Δ\|/IQR |
|---|---|---|---|---|---|---|
| **`post_r_80ms_delta_mv`** | **53** | −0.0600 | 0.1050 | −0.2125 | **0.1525** | **1.45** |
| `post_r_120ms_delta_mv` | 53 | −0.0462 | 0.1147 | −0.1950 | 0.1487 | 1.30 |
| `post_r_160ms_delta_mv` | 53 | −0.0275 | 0.1363 | −0.1525 | 0.1250 | 0.92 |
| `post_r_80_200_area_mv_s` | 53 | −0.0040 | 0.0152 | −0.0193 | 0.0153 | 1.01 |
| `pre_r_baseline_median_mv` | 53 | −0.0175 | 0.0850 | +0.0275 | 0.0450 | 0.53 |
| `qrs_proxy_peak_to_peak_mv` | 53 | 1.5200 | 1.0325 | 1.9550 | 0.4350 | 0.42 |
| `post_r_80_160_slope_mv_per_s` | 53 | 0.3750 | 0.9375 | 0.6562 | 0.2812 | 0.30 |
| `post_r_200ms_delta_mv` | 53 | +0.0225 | 0.1850 | −0.0256 | 0.0481 | 0.26 |

**Definedness is uniform**: the same **53 windows** (0.0024%) are non-finite in
every feature, and `morphology_valid == 0` in exactly 53 windows. **The
auxiliary target is defined for 99.9976% of windows, positive and negative
alike** — it is a per-window physiological measurement, not an event property,
so it exists for negatives as well.

### 1.2 The registered auxiliary target — one signed scalar

> **`post_r_80ms_delta_mv`** — the R+80 ms sample relative to the pre-R
> baseline.

**Chosen on physiological grounds**: R+80 ms is the closest available proxy to
the conventional ST measurement point (J+60/80 ms), and being **signed and in
mV it carries direction and magnitude in a single scalar**. This is the
*minimal* target that satisfies the hypothesis — one output, not a
reconstruction of eight handcrafted features.

**Disclosure, because blindness cannot be claimed.** The definedness audit
above also displayed class-conditional medians, so I saw that this feature has
the largest standardised class separation before registering it. **The choice
is justified physiologically and would have been the same without those
columns**, but the fact that they were visible is recorded rather than
concealed. **No alternative auxiliary target may be tried later** — that would
be the post-hoc variant selection §9 forbids.

### 1.3 Scaling, masking, and what is forbidden

- **Scaling:** standardised by **median and IQR computed on outer-training
  windows only**, per fold. IQR > 0, so **sign is preserved**.
- **Forbidden:** per-lead or per-stream normalisation of the target. It would
  inject stream identity into the objective and is precisely what E7a/E7b
  closed.
- **Masking:** windows with `morphology_valid == 0` or a non-finite target
  (53 in TRAIN) are **excluded from the auxiliary loss only**. They still carry
  the primary ischemia loss. The masked count is reported per fold.
- **No future information**: the target is computed from the same 10 s window
  the encoder sees. **No test access at any point.**

---

## 2. Model intervention

**Encoder and primary head are unchanged**, exactly as built:
`SharedLocalFrontEnd → positional embedding → 2 × PreNormTransformerBlock →
final_norm → SharedClassifierHead`, 309,809 parameters, frozen recipe §2.1.

| Arm | Definition |
|---|---|
| **B0** | the original B4-B training recipe, unmodified |
| **B1** | **identical** to B0, plus one auxiliary head and loss term |

**Auxiliary head: `Linear(128 → 1)`** on the same pooled `encode()` tap the
primary head consumes — **129 parameters**, no non-linearity, no added capacity
on the primary path. **Training-only: discarded before any evaluation**, so B0
and B1 are architecturally identical at inference.

**Loss:** `L = BCEWithLogits(primary) + λ · Huber(aux, standardised target)`,
with **λ = 0.1, fixed now and never varied.** λ was not tuned and will not be:
re-running with a different λ would be variant selection.

**E11 does not add** — registered as exclusions — subject-adversarial learning,
score normalisation, memory features, calibration changes, a larger classifier
head, or direct class-direction regularisation. **The intervention is the
auxiliary morphology objective and nothing else.**

---

## 3. Prospective subject-disjoint protocol

**The historical 12-subject VALIDATION partition is not used at all in E11.**
It has been used for hypothesis generation across ten experiments and cannot
serve as fresh confirmation.

**All E11 evaluation happens inside the original 56 TRAIN subjects.**

### 3.1 The frozen assignment

Deterministic and independent of any model outcome: subjects sorted by
TRAIN-side ischemic window prevalence (ties by subject id), then
**serpentine-assigned** to 3 folds.

```
assignment digest (SHA-256): ce037309cc2d67944acbee76e82700e5a54c9d2ff69bf54a121ab1b8940206c3
```

| fold | subjects | evaluable | windows | positives | prevalence | streams |
|---|---|---|---|---|---|---|
| 0 | 19 | 15 | 768,363 | 43,741 | 0.05693 | 46 |
| 1 | 19 | 15 | 727,927 | 30,859 | 0.04239 | 42 |
| 2 | 18 | 14 | 712,141 | 19,013 | 0.02670 | 44 |

**56 subjects, 12 of them zero-positive, 132 streams, 44 evaluable subjects.**

**Residual prevalence imbalance is 2.1× and is registered, not hidden.**
Prevalence is highly skewed (0 to 0.193) and no subject-level assignment can
equalise it. **AUPRC is bounded below by prevalence, so per-fold AUPRC is
reported with its prevalence beside it and is never pooled across folds
without it.**

### 3.2 The outer rule

For each fold `k`: train **B0 and B1** on the other two folds; evaluate each
**exactly once** on fold `k`. **No outer-held-out subject may influence
gradients, checkpoint selection, auxiliary weighting, thresholds,
hyperparameters or architecture.** Outer-fold outcomes are not inspected until
every choice above is frozen — and this document freezes them.

### 3.3 Fixed duration is NOT safe — nested selection is required

**Audited, and the answer is no.**

1. **The historical epoch counts are contaminated for this purpose.** B4-A/B/C
   selected epochs 4/2/2 by **maximum AUPRC on the 12 validation subjects**.
   Importing "train for 2–4 epochs" would import a decision made on the
   partition E11 exists to avoid.
2. **The choice matters materially.** E2 measured argmax-over-epochs bias at
   **+0.032** and epoch-to-epoch validation spread up to **0.117**; all three
   candidates overfit within 2–4 epochs of a 15-epoch budget.

**Therefore: nested inner subject-disjoint selection.** Within each fold's
outer-training subjects, a further subject-disjoint inner split (registered:
**the lowest-numbered third of outer-training subjects by the same frozen
serpentine order**) is held out for checkpoint selection only. The selection
rule is the **frozen B4 rule** — maximum inner pooled AUPRC, earliest epoch
wins an exact tie — applied **identically to B0 and B1**.

**Registered consequence:** inner selection reintroduces argmax bias, but it is
**common-mode across the paired arms**, so the B1−B0 contrast is far less
affected than either absolute value. **Absolute per-fold AUPRC must not be
compared to any historical B4 figure.**

---

## 4. Primary mechanism endpoint

**Per fold**, the ischemia class-direction consensus is built from **that
fold's training subjects only**, by E10's frozen aggregation: unit-normalise
each evaluable training stream's `delta`, average with **equal weight per
stream**, renormalise.

For every evaluable **outer-held-out** stream, for **B0 and B1**:

```
delta_s = mu_positive(s) - mu_negative(s)      on that arm's encoder embedding
```

- `cos(delta_s, fold-train consensus)`
- `‖delta_s‖`
- **negative-direction count and fraction** (`cos < 0`)
- **collapse behaviour**: count of streams with `‖delta_s‖` below the
  fold-training minimum
- **within-subject cross-stream direction agreement** for subjects with ≥2
  evaluable held-out streams

**The primary question is whether B1 improves unseen-stream class-direction
stability**, measured as: fewer negative-cosine streams, higher median cosine,
and larger median `‖delta‖`, relative to B0 on the identical folds.

**E10's reference values, for context and not as a target:** TRAIN LOSO cosine
min +0.971 / median +0.993 with 0/79 negative; historical validation min
−0.935 with 2/19 negative.

## 5. Secondary performance endpoints

Pooled AUPRC and AUROC; subject-macro AUPRC and AUROC **with contributing-subject
denominators**; the stream-level AUROC distribution; and sensitivity and
specificity **only at a training-derived frozen operating point** — the inner
split's F1-optimal threshold, fixed before the outer fold is scored and never
re-derived. **Prevalence accompanies every AUPRC.**

## 6. Paired comparison

B0 and B1 share **identical outer folds, identical inner splits, identical
seed (2026), identical sampling, identical batch order and identical epoch
budget**. The only difference is the auxiliary head and its loss term.

**Uncertainty is subject-level and paired**: bootstrap over the **44 evaluable
TRAIN subjects**, 1,000 replicates, seed 2026, each subject appearing in exactly
one held-out fold. **Windows are never treated as independent replicates**, and
neither are streams.

**44 evaluable subjects is the largest honest unit count this programme has
had** — against the 9 that E1–E10 were confined to. It is still small, and
E6a's finding applies: intervals will be wide.

## 7. Registered interpretation

| Outcome | Reading |
|---|---|
| **A** geometry **and** performance improve | supports morphology-aware representation generalization |
| **B** geometry improves, performance does not resolve | **mechanism support without established predictive gain** |
| **C** performance changes without geometry improvement | **does not** support the registered mechanism |
| **D** neither improves | mechanism unsupported; do not escalate |
| **E** harm | **report directly and stop the branch** |

**Outcome B is the most likely and is registered as such**, because E6a showed
this programme's instrument cannot resolve small performance contrasts even at
larger unit counts.

## 8. Registered predictions

1. **B0 will reproduce E10's qualitative geometry**: high fold-train coherence,
   with a minority of held-out streams showing reversal or collapse.
2. **B1 will show fewer negative-cosine held-out streams than B0.** *The core
   claim, and the one that must be allowed to fail.*
3. **B1's median `‖delta‖` on held-out streams will exceed B0's.**
4. **Pooled AUPRC will not separate** — the paired subject interval will include
   zero.
5. **Collapse streams will respond less than reversal streams**, since a
   morphology objective supplies direction, not signal where there is none.

## 9. Epistemic boundaries

- **Development evidence only. Not new sealed-test evidence.**
- **The original sealed B4 result remains consumed and unchanged.** E11 neither
  reopens nor re-scores it.
- **The 12-subject historical validation set is not fresh confirmation** and is
  untouched by E11.
- **No medical or diagnostic performance claim** is made or implied.
- **No winning configuration may be selected from multiple post-hoc variants.**
  One auxiliary target, one λ, one architecture, one split. If E11 is null, it
  is reported null.

## 10. Compute estimate and risks

**Cost basis: 5,458 s/epoch for 374,452 windows** = 0.01458 s/window (frozen
recipe §2.1). Outer-training sampled sets at the recipe's 25% prevalence:

| held-out fold | outer-train positives | sampled windows | s/epoch |
|---|---|---|---|
| 0 | 49,872 | ~199,000 | ~2,900 |
| 1 | 62,754 | ~251,000 | ~3,660 |
| 2 | 74,600 | ~298,000 | ~4,350 |

**Expected ≈ 42 h wall clock** for both arms across three folds (≈7 epochs per
model-fold under patience-4 early stopping). **Worst case ≈ 91 h** if every run
uses the full 15-epoch budget. The auxiliary head adds negligible compute.
Geometry and scoring add minutes.

**Risks, registered:**

| # | Risk | Severity | Handling |
|---|---|---|---|
| 1 | **λ = 0.1 is untuned and may be wrong.** A null could reflect the weight, not the mechanism | **High** | Registered in advance; **λ is not re-tried**. A null is reported as "null at λ = 0.1", not as "mechanism refuted" |
| 2 | Nested selection reintroduces argmax bias | Medium | Common-mode across paired arms; absolute figures not compared to history |
| 3 | 2.1× prevalence imbalance across folds | Medium | Prevalence reported beside every AUPRC; no cross-fold pooling without it |
| 4 | 44 evaluable subjects still cannot resolve small contrasts | **High** | Outcome B pre-registered as most likely; geometry is primary, performance secondary |
| 5 | Compute overrun beyond authorization | Medium | Per-fold checkpointing; **no re-run on failure without a new authorization** |
| 6 | Auxiliary head leaks into inference | Low | Discarded before scoring; arms architecturally identical at evaluation, asserted in code |

## 11. Feasibility verdict

**Feasible, and blocked only on authorization.** All inputs exist: the frozen
recipe, the 56-subject corpus, the signed target at 99.9976% coverage, and a
deterministic split with a recorded digest. **Nothing in E11 requires sealed
data, and nothing reopens the sealed result.**

**Not authorized. Not started. Awaiting explicit review.**

---
---

# AMENDMENTS — pre-execution preflight, 2026-08-26

**Made before any training. No model was trained, no checkpoint created, no
historical VALIDATION outcome re-read, no sealed artifact opened.**

## A1 · Auxiliary-target provenance — HARD GATE PASSED

**Computation path, traced end to end:**

```
CausalWindow(values, sampling_frequency_hz, …)     ← window samples only
   └─ features/morphology.py :: extract_morphology_features(window)
        ├─ _detect_r_peaks(values, fs)             ← WFDB XQRS on THIS window
        ├─ usable = peaks[(peaks+template_start >= 0) &
        │                 (peaks+template_end  <  values.size)]
        ├─ baseline_i = median(values[peak-200ms : peak-80ms])
        ├─ post_i     = _local_median(values, peak+80ms, ±10ms) - baseline_i
        └─ post_r_80ms_delta_mv = median_i(post_i)
```

| Requirement | Verdict | Evidence |
|---|---|---|
| Derived from the window signal | **YES** | sole argument is `CausalWindow`; docstring *"Waveform-only R-aligned morphology proxies for completed causal windows"* |
| Does not use the ischemic label | **YES** | no label parameter exists in the signature or the module |
| Does not use ST-event annotations | **YES** | `STEvent` is defined in `data/models.py` and never imported by `features/morphology.py` |
| Does not use episode boundaries | **YES** | no onset/end/peak sample is referenced |
| No future samples beyond the causal window | **YES** | `usable` **explicitly bounds every index inside `values`**; `CausalWindow` is *"emitted only after its final sample"* |
| Not a transform of `direction` / `peak_deviation_uv` | **YES** | those are `STEvent` fields; the function's only numeric inputs are `values` and `fs` |

**Source hashes (first 32 hex) recorded for the receipt:**

```
features/morphology.py   1cdfe3ed1bc23893d250c7b38da3a934
features/schema.py       6dcf3e8adec970426e80b25f17385036
signal/models.py         ff9a24b36d590f0727e3d4e044aabebe
neural/training.py       57af2c6869c8feeb3fa131d054488128
neural/candidates.py     334618458cc1f8596c18720b9c2a815d
```

**Verdict: PASS. The auxiliary target is label-free, annotation-free and
causal.** No substitute target is considered, per instruction.

## A2 · Nested selection — corrected language and data boundaries

**The "common-mode bias" claim in §3.3 is withdrawn.** It is replaced by:

> **Both B0 and B1 undergo the identical preregistered inner selection
> procedure. Selection bias remains confined to the inner development process;
> the outer held-out comparison remains prospective. The magnitude of selection
> bias need not be identical between arms because their learning curves may
> differ.**

**Registered data-flow, per outer fold:**

```
OUTER-TRAIN  (2 folds)
  ├── INNER-TRAIN   (2/3 of outer-train subjects, frozen serpentine order)
  │       fit model weights
  │       fit morphology median/IQR scaler          ← inner-train ONLY
  └── INNER-VALIDATION (1/3)
          checkpoint/epoch selection ONLY

then, with the selected epoch count fixed:

ALL OUTER-TRAIN
  refit morphology scaler on ALL OUTER-TRAIN
  retrain B0/B1 for exactly the selected epoch count
        │
OUTER-HELD-OUT (1 fold)
  evaluate exactly once
```

**Hard assertions, to be enforced in code and recorded in the receipt:**

1. inner-validation subject ids ∉ the scaler-fitting set during phase 1;
2. outer-held-out subject ids ∉ {gradients, scaler, epoch selection, threshold,
   architecture, λ, any training decision};
3. the historical 12-subject VALIDATION set ∉ every E11 partition — asserted by
   set intersection against the recorded manifest, not by prose.

**Adapting the historical max-validation-AUPRC logic.** `training.py`'s
`CheckpointSelector.update(epoch, validation_auprc)` is partition-agnostic: it
consumes a scalar. **The adaptation is therefore not to modify the selector but
to control what is fed to it** — the loader supplying `validation_auprc` is
constructed from **inner-validation subject ids only**, and an assertion
immediately before the training call verifies that the loader's subject set is
disjoint from the outer-held-out fold. **The selector cannot see an outer fold
because no outer-fold row is ever placed in its loader.**

## A3 · Stochastic pairing contract — audited, achievable

| Source | Paired? | Basis |
|---|---|---|
| Encoder initialization | **YES** | `initialize_determinism()` resets all seeds immediately before `factory()`; comment: *"Nothing may consume RNG between this call and the constructor"* |
| Primary-head initialization | **YES** | same construction, identical draw order, base model built **before** any auxiliary module |
| Batch order | **YES** | `build_training_loader` passes a **dedicated** `data_order_generator()` (`torch.Generator`, seeded `SEED`), so ordering is **independent of the global RNG and of model construction** |
| Augmentation draws | **N/A** | the frozen recipe sets `augmentation: null` — no draws exist |
| Optimizer / scheduler | **YES** | AdamW, identical hyperparameters; scheduler `none` |
| Primary-loss implementation | **YES** | unchanged `BCEWithLogitsLoss` |
| Max budget, inner rule | **YES** | identical by registration |
| Subject split | **YES** | identical digest |

**Auxiliary-head isolation, registered:** B1 constructs the **base model first**
with byte-identical calls to B0, then initializes `Linear(128→1)` from an
**isolated `torch.Generator` seeded with a dedicated `AUX_SEED`**, consuming
**zero** global RNG. The global stream is therefore untouched by B1's extra
module.

**What cannot be paired, stated rather than approximated:**

- **Weight trajectories diverge from the first optimizer step**, because B1's
  gradient includes the auxiliary term. **That is the intervention, not a
  pairing defect.**
- **E11 V1 uses one seed per arm per fold and no repeats** (per instruction).
  **A difference between arms therefore cannot be separated from single-seed
  training variance.** Registered as a limitation of V1, not resolved in it.

## A4 · Geometry endpoint lock — no collapse category

Primary continuous endpoints, per arm, per evaluable held-out stream:
`cos(delta_s, arm-specific outer-train consensus)`, `‖delta_s‖`, and
within-subject cross-stream `cos` where defined. Plus the **count and fraction
of held-out streams with `cos < 0`**.

**"Class-direction collapse" is NOT used as a categorical endpoint, and the
category is deleted from §4.** No defensible TRAIN-only threshold exists: a
single order statistic over ~50 fold-training streams is unstable, and E10
showed held-out `‖delta‖` medians are systematically about half of TRAIN's for
distributional reasons unrelated to collapse, so any TRAIN-derived cut would
flag streams for the wrong reason. **`‖delta‖` is retained as a continuous
endpoint.**

**Each arm's consensus is built from that arm's own representations on that
fold's outer-train subjects only, and frozen before any held-out row is
embedded.**

## A5 · Intervention freeze — confirmed

E11 V1 is exactly **B0** (original recipe under the new nested protocol) and
**B1** (= B0 + `Linear(128→1)` auxiliary head + fixed **λ = 0.1** + fold-training
median/IQR target scaling; head discarded before held-out evaluation).

**Not authorized, and not to be added:** alternative morphology target, λ sweep,
second λ, direct cosine/class-direction loss, subject-adversarial objective,
lead embedding, polarity normalization, M1/M2 features, calibration changes,
larger head, architecture search, or any augmentation chosen from E11 outcomes.

**A null result means:** *"no established benefit for this preregistered
morphology-aware formulation at λ = 0.1."* **It must not be generalized to
"morphology-aware representation learning does not work."**

## A6 · Split and label-authority preflight

| check | result |
|---|---|
| Digest recomputed from the assignment | `ce037309cc2d67944acbee76e82700e5a54c9d2ff69bf54a121ab1b8940206c3` — **MATCH** |
| Exactly the 56 original TRAIN subjects | **True** (set equality) |
| Historical VALIDATION subjects present | **0** |
| TEST subjects present | **0** |
| Outer folds pairwise disjoint | **True** — 19 / 19 / 18 |
| Union equals the assigned set | **True** |
| Evaluable subjects per fold | **15 / 15 / 14 — total 44**, as registered |

**Structural TEST unreachability — required before authorization.** Modelled on
`t1_fold_authority.py`, whose docstring records the pattern: *"VALIDATION is the
only partition a T1 development authority can be built for, and it is
**hard-coded rather than passed**. TEST cannot be requested because there is no
parameter that could carry it."*

**Registered requirement:** an `E11FoldAuthority` that (a) binds an outer fold
id and an explicit subject-id set at construction, (b) exposes **no** partition
parameter, (c) hard-codes the development corpus root, (d) refuses any subject
id not in the recorded assignment, and (e) has **no method returning a whole
partition, index, iterator or mapping**. Tests must assert each absence rather
than trust it. **TEST is then unreachable by construction, not by prose.**

## A7 · Execution receipt schema

No scientific outcome may be written without its matching receipt:

```
git_commit, git_dirty, environment_dependency_digest,
split_digest, outer_fold_id, inner_split_subject_ids, inner_split_digest,
arm ∈ {B0, B1}, shared_initialization_seed, aux_head_seed  (B1 only),
scaler_median, scaler_iqr, scaler_fitting_partition,
checkpoint_selection_partition, selected_epoch, epoch_history,
lambda, auxiliary_target_name, auxiliary_target_source_sha256,
morphology_module_sha256, encoder_checkpoint_sha256,
input_corpus_sha256, masked_auxiliary_window_count,
test_partition_opened: false, test_authority_constructed: false,
started_utc, finished_utc, failure_state
```

`failure_state` is written on interruption **before** any partial metric.

## A8 · Compute re-estimate and failure policy

**Two-phase cost, at 0.01458 s/window.** Inner-train is 2/3 of outer-train;
phase 2 retrains on all outer-train for the selected epoch count.

| | phase 1 (select) | phase 2 (final) | per arm |
|---|---|---|---|
| windows/epoch, summed over 3 folds | ~499,000 | ~748,000 | — |
| expected epochs | ~7 (patience-4) | ~3 | — |
| **expected** | ~14.2 h | ~9.1 h | **~23.2 h** |
| **worst case (15 + 15)** | ~30.3 h | ~45.4 h | **~75.8 h** |

**Both arms: expected ≈ 46 h; worst case ≈ 152 h.**

**Failure policy, fixed now:**

- **Interruption:** the run writes `failure_state` and stops. **No automatic
  retry, restart or fresh seed** — the standing prohibition applies unchanged.
- **One failed fold:** the remaining folds are **not** re-planned. The
  experiment reports **completed folds only, with the failed fold named**, and
  the paired comparison is computed **only over folds where both arms
  completed**.
- **Restart from an existing checkpoint:** **not permitted** in E11 V1.
- **Same attempt vs new attempt:** an authorized attempt is one execution of the
  registered protocol at the recorded split digest. **Any re-execution after a
  failure is a NEW attempt requiring a NEW human authorization.**
- **Broken pair:** if B0 completes and B1 does not on the same fold, that fold
  contributes **nothing** to the paired contrast and is reported as incomplete.
- **Hard cap:** if wall clock exceeds **the worst-case estimate**, the run stops
  and reports incompletion rather than continuing.
