# B4 · E1 Representation Gap Probe — Preregistered Analysis Plan, V1

**Pre-registration. Nothing has been fitted and no probe result exists.**
Everything below is derived from artifact *structure* — array names, shapes,
dtypes, manifest fields, SHA-256 digests, subject identifiers and row counts —
and from values already published in
`docs/B4_IMPROVEMENT_INVESTIGATION_BRIEF_V1.md`,
`docs/B4_GLOBAL_ENCODER_SELECTION_V1.md` and `VALIDATION_METRICS.json`.

**This plan authorizes nothing and requires nothing.** No model is trained, no
encoder forward pass is run, no budget is opened, no lock is modified, and **no
sealed-test artifact is opened.** The brief records E1 as *"No new budget;
derived analysis on existing development artifacts."*

| | |
|---|---|
| Experiment | **E1** — representation gap probe |
| Question | If the downstream classifier failed, is the information **absent from the representation**, or **present but unused**? |
| Partition | development **train** (fit) and **validation** (evaluate). No test |
| Evidence class | `development_validation_result` |
| Authorization | **none required, none requested, none granted** |
| Predecessors | E2 / E2b / E3, `B4_E2_E3_ANALYSIS_PLAN_V1.md` |

> **Amendment 1, 2026-08-25, after human review and before execution.** Two
> changes were required and both are made below: **an A0 frozen-head
> reproduction arm** was added, and **the morphology interpretation language was
> weakened.** A third change was made on our own initiative and is flagged for
> the reviewer in §3.1: the reviewer's proposed matrix listed *"capacity matched
> MLP"* and *"head-equivalent MLP"* as two separate arms. **They are the same
> arm**, and running it twice under two names would report one result as two.
> It appears once.
>
> **E1 is a diagnosis, not a tuning step.** It decides which of two directions
> is justified; it does not attempt to improve anything. §12 records the fork.

---

## 0. What E2 and E3 already settled, and why E1 follows

- **E3.** The analytic prior correction moved Brier `0.06557 → 0.04205` and NLL
  `0.22741 → 0.16545`, and moved pooled AUPRC and AUROC by **exactly 0.0**, with
  the selected window set bit-identical. **Threshold and calibration are not the
  source of the shortfall**, and cannot be.
- **E2b.** All three paired subject-bootstrap intervals include zero
  (B4-B−B4-A `[-0.03197, 0.13060]`, B4-B−B4-C `[-0.03402, 0.10765]`,
  B4-A−B4-C `[-0.08808, 0.06066]`). **The evidence does not separate the three
  architectures at n=12**, so "try a different architecture" is not a supported
  next step.

Both eliminate a downstream explanation. What remains is the representation
itself, and that is E1.

---

## 1. Embedding extraction path — no forward pass is required

The cache already exists and is **digest-bound to the frozen checkpoint**:

| | |
|---|---|
| Artifact | `cardiosentinel-features/p1-b4b-embeddings-v1/{train,validation}/p1_embeddings.npz` |
| Tap | `B4BTransformerCNN.encode:pooled_post_final_norm` |
| Shape · dtype | `(N, 128)` · `float32` |
| `encoder_fine_tuned` | **False** |
| `encoder_checkpoint_sha256` | `b1301723909c641a0014c31f6daa9549d47ab231f0b07483e0de729aff5591c9` |

**That digest is verified equal to `sha256(model_selected.pt)` of
`B4B_cnn_transformer_v1`.** The constraint *"use the frozen B4-B encoder
checkpoint"* is therefore satisfied **by verified provenance rather than by
re-running the encoder**, which is stronger: no forward pass can drift, no
`processing_profile` can be mis-set, and no checkpoint can be silently
substituted.

**E1 re-verifies that digest at run time and refuses to proceed if it differs.**
The tap is the same `[B, 128]` representation P1 fusion and M1 memory consume —
the layer *before* the head's first dropout — so the probe sees exactly what the
head sees, and nothing else.

---

## 2. Available data, labels, and subject separation

| | train | validation |
|---|---|---|
| Rows | **374,452** | **473,897** |
| Subjects | **56** | **12** |
| Positives | 93,613 | 21,628 |
| Prevalence | **0.250000** (sampled) | **0.045639** |

**Labels** are the `label` array carried in the embedding cache itself, from
annotation definition `ltstdb.stb`, 10 s windows at 5 s stride,
`processing_profile: raw`. Validation labels are verified **element-wise
identical and in identical order** to `validation_predictions.npz` — so the
probe and the deployed head are scored on the same rows, in the same order,
against the same labels, with **no join and no alignment step that could go
wrong**. E1 asserts that equality before computing anything.

**Subject separation** is by the frozen split policy: 56 train subjects, 12
validation subjects, disjoint. The 12 validation subjects are
`s2004 s2005 s2019 s2020 s2023 s2031 s2057 s2058 s2059 s3068 s3072 s3073`.
**E1 asserts the train/validation subject intersection is empty before fitting.**

**Morphology reference features** come from
`cardiosentinel-features/ltstdb-baseline-v1`, schema `combined_v1` — **40
features = `morphology_v1` (18) + `signal_v1` (22)**, the corpus B0–B3 were
built from. Structural check already performed: **every embedding row has a
morphology row, in both partitions — coverage 1.000000, zero embedding rows
unmatched.** The morphology corpus is a strict superset (2,208,431 train /
492,904 validation rows), so the join is an inner join that **loses nothing on
the embedding side**, and the comparison is on identical windows as the brief
requires. The 19,007 validation rows and 1,833,979 train rows present only in
the morphology corpus are **outside B4's evaluated set and are dropped**; the
dropped counts are reported beside every result rather than left implicit.

---

## 3. Arms

All arms are scored on the **same 473,897 validation rows**.

| Arm | Input | Model | Fitted on | Purpose |
|---|---|---|---|---|
| **A0 · head reproduction** | cached embedding | **frozen B4-B head weights** | *nothing — frozen* | prove the bridge before using it |
| **A1 · head as published** | — | — | *nothing — on disk* | the existing-system reference |
| **A2 · linear probe** | cached embedding | L2 logistic regression | train | **linear** separability |
| **A3 · capacity-matched probe** | cached embedding | `128→64 SiLU →1` MLP | train | **non-linear** separability at the head's own capacity |
| **A4 · morphology probe** | 40 `combined_v1` features | L2 logistic regression | train | independent morphology signal |
| **A5 · joint probe** | embedding ⊕ morphology (168-d) | L2 logistic regression | train | complementary information |

### 3.1 A0 — the reproduction arm, and why it is not redundant with A1

**A1 reads scores off disk. A0 recomputes them.** Without A0 the whole
experiment assumes, rather than demonstrates, that the cached embedding is the
tensor the deployed head actually consumes.

The reproduction path is **exact, not approximate**, and the source says so:

```python
def forward(self, waveforms: Tensor) -> Tensor:
    return self.classifier.head(self.encode(waveforms)).squeeze(-1)
```

`encode()` returns the pooled `[B, 128]` after the final LayerNorm and pooling,
which is precisely what the cache stores. So `classifier.head(embedding)` is the
deployed computation with the encoder half replaced by its own recorded output.

**Note the pooling trap that A0 must avoid.** `SharedClassifierHead.forward`
pools *first* (`self.pool(values)`), because in deployment it receives
`[B, C, T]`. The cached embedding is **already pooled**. A0 therefore applies
`classifier.head` — the `nn.Sequential` — and **not** `classifier.forward`,
which would pool a `[N, 128]` matrix a second time and silently produce a
plausible, wrong result. This is registered because it is the kind of error that
returns a number rather than an exception.

Weights are loaded through `neural.p1_experiment.load_official_b4b_encoder`,
which **refuses unless** the experiment-lock SHA-256 and checkpoint SHA-256 are
the selected ones and the lock records `test: null`, then sets `eval()` and
`requires_grad_(False)`. Dropout is inert in `eval()`, so A0 is deterministic.

**A0's registered acceptance criterion, and it is a gate, not a metric.**

> A0's per-row scores must agree with `validation_predictions.npz` to within
> **float32 tolerance (`atol = 1e-6`)**, and A0's pooled validation AUPRC must
> agree with the published **0.38053499010488423** to within **`1e-5`**.
>
> **If A0 fails, E1 stops and reports the failure.** No probe result is
> interpretable if the bridge cannot be reproduced, and a mismatch would mean
> the cached embedding is not the head's true input — which would invalidate
> P1 fusion and M1 memory as well, and is a larger finding than E1.

#### Amendment 2 — the gate as first registered was unsatisfiable

**The first execution of A0 returned `GATE: FAIL`, and the gate was wrong, not
the bridge.** As originally registered the gate demanded *both* that per-row
scores agree to float32 tolerance *and* that pooled AUPRC "equal" the published
value, which was implemented as exact equality. **Those two clauses cannot both
hold.** AUPRC is a rank statistic over exactly those scores, so a float32-level
score difference necessarily admits an AUPRC difference of the same order. The
gate demanded bit-exactness from a float32 pipeline.

**Measured, not assumed.** Perturbing the published scores by ±8.772e-08 — the
magnitude A0 actually differed by — and recomputing pooled AUPRC over 20 draws
(seed 2026) gives AUPRC differences of:

```
min 1.095e-08    median 8.491e-07    max 2.417e-06
```

**A0's observed AUPRC difference was 1.101e-06 — inside that range, near its
median.** The difference is round-off in the rank statistic and nothing else.

**What actually passed, unchanged, on the first run:** per-row agreement at
`max |Δscore| = 8.772e-08`, `np.allclose(atol=1e-6) → True`. That was the
substantive criterion and it was met before any amendment.

**Why this is a correction and not a widened metric.** The gate's discriminating
power is untouched. A cached embedding that was *not* the head's input would
differ by O(0.1); applying `classifier.forward` instead of `classifier.head` —
the double-pooling trap above — changes the scores grossly, not in the seventh
decimal. **Every failure mode the gate was built to catch is still caught at
`1e-5`.** Nothing was relaxed to accommodate a result: the result was already
correct, and the specification was internally inconsistent.

**Recorded rather than silently fixed**, because a gate that fails for a reason
unrelated to what it claims to verify is the pattern
`PAPER_S9_DISCUSSION_DRAFT.md` §9.5.5 catalogues, and this one is the subtler
form — not a check that wrongly passed, but a check that wrongly failed, whose
two clauses contradicted each other.

**A3 exists because A2 is deliberately weaker than the head.** The deployed head
is `Linear(128→64) → SiLU → Dropout → Linear(64→1)`, **8,321 parameters — a
one-hidden-layer MLP, not a linear map.** A 129-parameter linear probe is a
strictly smaller hypothesis class. Without A3, "A2 below A1" would be
uninterpretable: it could mean the information is absent, or merely that it is
not *linearly* decodable. A3 separates those.

---

## 4. Probe classifier choice, and why

**Primary probe: L2-regularised logistic regression**, `lbfgs`,
`max_iter = 2000`, `class_weight = None`, on standardised features.

- **Linear is the point.** The question is whether the information is *present*,
  and a linear decoder is the strictest evidence of presence: if a linear map
  over the frozen embedding matches or beats a trained non-linear head, the
  information is there and the head did not use it. A strong probe would prove
  less, because a sufficiently flexible probe can manufacture separability that
  the head could never have exploited.
- **`class_weight = None`** matches the head's frozen recipe
  (`BCEWithLogitsLoss`, `class_weighting: null`). The probe inherits the same
  25% → 4.56% prior mismatch as the head. **No prior correction is applied**, and
  E3 established it could not change AUPRC or AUROC anyway.
- **Standardisation** (`StandardScaler`) is fitted on **train only** and applied
  unchanged to validation.

**Amendment 3 — non-finite morphology cells, registered before execution.** A
structural scan found **148 non-finite cells in the validation morphology
corpus**, 0.0016% of cells, concentrated in ~8 rows where beat detection
produced no usable beats and ~7 where the spectral ratios are undefined. The
registered policy:

- **Median imputation, with the median fitted on train only**, applied unchanged
  to validation — the same train-only discipline as the scaler.
- **No row is dropped.** Dropping would change the row set for the morphology
  arms and destroy the identical-windows property the paired bootstrap depends
  on. Every arm must score the same 473,897 rows.
- **`morphology_valid` is itself one of the 18 morphology features**, so the
  probe can see that a row's morphology was not extractable; imputation does not
  hide the failure from the model.
- The affected cell and row counts are **reported beside the morphology arms'
  results**, not left implicit.

The embedding arms are unaffected: the cached embeddings contain no non-finite
values, and this is asserted at load.

**Hyperparameter selection.** `C ∈ {0.01, 0.1, 1.0, 10.0}`, chosen by
`GroupKFold(n_splits=5)` **grouped by subject, within the 56 training subjects
only**, maximising pooled AUPRC on held-out training folds. **Validation is
never consulted for selection**, and the chosen `C` is reported.

**A3's MLP** uses the head's own hidden width and activation so its capacity
matches by construction; its only registered hyperparameter is the epoch count,
fixed by the same subject-grouped CV within train. **A3 fits a head, not an
encoder — the encoder stays frozen, and no B4 retraining occurs anywhere in
E1.**

---

## 5. Leakage prevention — enumerated, and asserted in code

1. **No sealed-test artifact is opened.** `TEST_PREDICTIONS.npz`,
   `TEST_METRICS.json`, `TEST_ATTEMPT.json`, `TEST_AUDIT.json` are not read, not
   stat-ed for schema, and not counted.
2. **No probe is fitted on validation.** Every `fit` call sees train rows only.
3. **The scaler is fitted on train only.**
4. **Hyperparameters are selected within train**, by subject-grouped CV. The
   registered grid is fixed above and is not widened after seeing anything.
5. **Subject disjointness is asserted**, not assumed: the train/validation
   subject-id intersection must be empty or E1 aborts.
6. **Row alignment is asserted**, not assumed: validation `stable_id` order must
   be element-wise equal across the embedding cache and
   `validation_predictions.npz`.
7. **No threshold is selected on validation.** All primary metrics are
   threshold-free.
8. **One fit, one evaluation, per arm.** No re-fit after seeing a validation
   number, no arm dropped, no arm added. Whatever the arms report is reported.
9. **Frozen locks are not modified.** E1 writes nothing into any run directory;
   all outputs go to a scratch path outside the repository.

### 5.1 The asymmetry that favours the head, stated before it is exploited

**A1 has had validation exposure and A2–A5 have not.** The head's checkpoint was
chosen as the maximum validation AUPRC over epochs — epoch 2 of 6 — and E2
measured that argmax-over-epochs bias at **+0.03211** for B4-B. The probes are
fitted on train and evaluated once on validation, with no epoch selected and no
threshold tuned there.

**This makes the comparison conservative in one direction only:**

- **A probe beating A1 is a strong result**, because the probe wins despite the
  handicap.
- **A1 beating a probe is a weak result**, because up to ~0.032 of A1's
  validation AUPRC is selection bias that the probes do not enjoy.

Any margin below that bias is reported as **not interpretable in the head's
favour**. This sentence is registered here so it cannot be omitted later.

---

## 6. Metrics

Reported for **every** arm, always together:

| Metric | Role |
|---|---|
| **Pooled window AUPRC** | **primary** — the frozen checkpoint objective, and the metric the registered B0–B3 comparison uses |
| **Subject-macro AUPRC** | mandatory review dimension under `B4_ARCHITECTURE_SELECTION_PROTOCOL_V1`; reported with its **contributing-subject count** beside it |
| AUROC | secondary, for shape only |

**The contributing-unit count is reported beside every population-level scalar**
— `PAPER_S9_DISCUSSION_DRAFT.md` §9.2 is the reason, and subject-macro AUPRC is
exactly the statistic that concealed a 9-of-12 denominator in T2.

**No metric is added after seeing results, and no post-hoc scalar score is
formed** across dimensions — the selection protocol forbids folding review
dimensions into a composite, and E1 inherits that.

---

## 7. Bootstrap method

**Paired subject bootstrap, 1,000 replicates, seed 2026** — the programme's
`BOOTSTRAP_REPLICATES` / `BOOTSTRAP_SEED`, identical to T1, T2, U1, W1 and E2b.

Implemented by reusing
`neural.t2_paired_bootstrap.paired_subject_bootstrap_difference` and
`evaluation.metrics.subject_bootstrap_plan`, so E1's intervals are comparable to
T2's published interval **by construction rather than by resemblance**. Where a
faster equivalent loop is used, it is asserted equal to the repo function's
`lower_95`/`upper_95` on a reduced replicate count before the full run — the
check E2b already applies.

**Paired**, because every arm is scored on the same rows: one subject resample
per replicate, applied to all arms, one difference per replicate.

Registered contrasts:

```
A2 - A1      linear probe            vs deployed head   ← the decisive contrast
A3 - A1      capacity-matched probe  vs deployed head
A4 - A2      morphology              vs embedding
A5 - A2      joint                   vs embedding
A5 - A4      joint                   vs morphology
```

**A0 carries no bootstrap.** It is a reproduction gate with a pass/fail
criterion, not an arm to be compared.

**The n=12 bound is restated with every interval.** Twelve subjects can be drawn
at most twelve ways per replicate; these are subject-resampling intervals over a
fixed development cohort and **are not confidence intervals for a new cohort**.

---

## 8. Decision rules — registered before any number exists

The question is *absent* versus *present but unused*. The rules:

| Outcome | Reading |
|---|---|
| **A2 − A1 excludes zero, positive** | **Present and unused.** A linear map over the frozen embedding beats the trained head despite the head's validation-selection advantage. The indicated direction is downstream — head, loss, prior handling. |
| **A2 − A1 includes zero, and A3 − A1 includes zero** | **The head is extracting what a probe of its own capacity can extract.** No evidence of unused information at this capacity. |
| **A2 − A1 negative, A3 − A1 includes zero** | Information present but **not linearly** decodable. The head's non-linearity is load-bearing and a linear read-out understates the representation. |
| **A4 − A2 excludes zero, positive** | Under the evaluated probe, the morphology features carry predictive signal **the probe could not extract from the embedding**. This is *evidence toward* the representational branch — see §8.1 before reading it as more. |
| **A5 − A2 and A5 − A4 both exclude zero** | The two feature sets are **complementary under this probe** — each supplies something the other did not. |
| **All intervals include zero** | **The instrument cannot separate the arms at n=12**, exactly as E2b found for the architectures. An instrument result, **not** evidence of equivalence. |

### 8.1 What a morphology comparison can and cannot license

**Amended after review.** An earlier draft of this plan read: *"if the
morphology arm does not beat the embedding arm, then the embedding does contain
what morphology carries, and the entire 'improve the representation' branch of
the brief loses its motivation."* **That is too strong and is withdrawn.**
(It was written under the pre-amendment numbering, in which the morphology arm
was A3; it is A4 here. The claim is quoted by role rather than by ID so the
withdrawal is not itself misquoted.)

The defensible form:

> **If the morphology features do not improve over the embedding representation,
> this indicates that the extracted morphology signal provides limited
> additional predictive information *under the evaluated probe, on this cohort*.**

The weaker reading is required because a null morphology result has at least
four explanations besides "the embedding already contains it":

1. **The extracted morphology features may be noisy.** `morphology_valid` is
   itself one of the 18 fields, which means the extractor already reports that
   it sometimes fails.
2. **The extraction may be weak** — these are proxy measurements, not clinical
   ST measurements.
3. **The probe's capacity may be insufficient** for the morphology feature space
   even where it suffices for the embedding. B3 is a histogram gradient-boosted
   model; a linear probe on the same features is not B3.
4. **Fusion strategy matters.** Concatenation is one way to combine feature sets
   and not obviously the best one; A5's null would be a null *for concatenation*.

**Symmetrically**, a positive morphology result does not prove the embedding
lacks the information in principle — only that this probe did not recover it.
Both directions are statements about decodability under a fixed probe, and the
report must say so in those words.

**The last row is the most likely outcome and the plan says so in advance.** E2b
could not separate three architectures whose validation AUPRCs differ by 0.043 at
this cohort size. E1's contrasts should be read expecting the same limitation,
and a wide interval is a fact about twelve subjects rather than about the
representation.

---

## 9. Registered predictions

Stated now so they can be wrong, and reported as written if they are.

0. **A0 will reproduce the published pooled AUPRC exactly**, and per-row scores
   will agree to float32 tolerance. **This is a gate: if it fails, E1 stops.**
1. **A2 will not beat A1 outright**; `A2 − A1` will be negative in point estimate
   with an interval including zero. The head has both non-linearity and
   validation selection on its side.
2. **A3 − A1 will include zero.** A capacity-matched probe on the frozen
   embedding should approximately reproduce the head, because it *is* the head's
   architecture fitted to the same frozen features — differing only in training
   regime and in having no validation-selected checkpoint.
3. **A4 will be the strongest single-feature-set arm on subject-macro AUPRC**,
   consistent with B3 beating B4-B on the registered comparison
   (0.436410 against 0.354901 subject-macro on test; 0.6801 against 0.3805 on
   validation pooled).
4. **A5 will not beat A4 by an interval excluding zero.**
5. **At least three of the five contrasts will include zero.**

**Prediction 3 is the one to watch**, and §8.1 governs how its outcome may be
read. A null there is evidence that the morphology signal adds little *under
this probe*; it is not proof that the embedding contains everything morphology
carries.

---

## 10. What E1 cannot establish

- **Nothing about test performance.** Every number is development evidence, on a
  12-subject validation cohort. Report as *"mechanism understood"*, never
  *"performance improved"* — brief §8.
- **No held-out estimate is obtainable within LTSTDB, permanently.**
- **Not that a probe result predicts a retrained model's result.** A probe over
  frozen features answers what is *decodable now*, not what a different training
  run would achieve. E4/E5 are separate experiments with separate
  authorizations.
- **Not a ranking of architectures.** E2b already showed the cohort cannot do
  that.
- **Not causal.** "Present but unused" describes decodability, not why the
  optimiser failed to use it.

---

## 11. The fork this experiment exists to decide

E1 does not attempt to improve anything. It chooses which of two directions is
justified, so that the remaining days are not spent tuning blind:

```
                        E1
                         |
          ---------------------------------
          |                               |
  embedding carries signal         embedding lacks signal
          |                               |
  improve what consumes it         improve the representation
  (temporal reasoning, fusion,     (B4 training: prior/loss,
   personalisation, gating)         regularisation, augmentation)
```

**If the embedding carries the signal, retraining B4 is the wrong direction**,
and the effort belongs downstream. **If it does not, B4 retraining becomes
justified** — and only then, with a fresh authorization, because fifteen of
fifteen one-shot budgets are spent.

### 11.1 Explicitly excluded from E1

Registered so they are not re-proposed inside this experiment, and not smuggled
in as "while we were there":

- ❌ a new or modified encoder architecture
- ❌ any transformer modification
- ❌ augmentation experiments
- ❌ contrastive or self-supervised pretraining
- ❌ **any retraining of B4**

None of these is refused permanently. Each is a separate experiment with its own
pre-registration and, where it retrains, its own human authorization. **E1's job
is to say which of them is worth proposing at all.**

---

## 12. Outputs

One JSON of arm metrics and bootstrap intervals, and one report document, both
derived. Scratch and intermediate fits live **outside the repository**. No run
directory is written to, no lock is touched, no cached artifact is regenerated.
