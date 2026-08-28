# B4 · E10 Representation-Geometry Audit — Preregistered Plan, V1

**Read-only, development only. No retraining, no sealed-test artifact, no new
model selection, no weight modified.** Uses the frozen 128-d B4 embedding and
the frozen B4 head only.

**Every definition below is fixed before any validation outcome is examined.**
The TRAIN consensus is computed from TRAIN alone; VALIDATION receives frozen
quantities and contributes nothing to their definition.

---

## 1. Audit — verified before pre-registration

| | TRAIN | VALIDATION |
|---|---|---|
| Embedding tap | `B4BTransformerCNN.encode:pooled_post_final_norm` | same |
| `encoder_checkpoint_sha256` == `sha256(model_selected.pt)` | **True** | **True** |
| Rows | 2,208,431 | 492,904 |
| Chronology digest | `99dff218…` (recomputed, matched) | `89f0b08b…` (recomputed, matched) |
| Streams | 132 | 30 |
| **Evaluable streams (both classes)** | **79** | **19** |
| Subjects / evaluable subjects | 56 / **44** | 12 / **9** |

The M1 cache manifest does not itself carry `encoder_fine_tuned`; the P1
embedding cache records it as `False`, and E8b verified the M1
`representation.npy` 128-d prefix equals that cache. Provenance chains through.

Labels come from `target_families == "ischemic_positive"`, whose identity with
the published `label` column was asserted in E9. The frozen head is reached via
`load_official_b4b_encoder`, which refuses unless the lock and checkpoint SHAs
match and `test` is null.

---

## 2. Frozen definitions

For each **evaluable stream** `s` (both classes present):

```
mu_pos(s) = mean embedding over positive windows      [128]
mu_neg(s) = mean embedding over negative windows      [128]
delta(s)  = mu_pos(s) - mu_neg(s)
||delta(s)||  = Euclidean norm
```

**TRAIN consensus direction — the aggregation, fixed now:**

```
c = normalize( mean over the 79 TRAIN evaluable streams of  delta(s)/||delta(s)|| )
```

**Unit-normalised per stream before averaging, and every stream weighted
equally.** Window count is therefore **not** treated as independent replication,
as required. Streams nest in subjects, so uncertainty is assessed by resampling
**subjects**, never windows or streams.

**Reported per stream:** `cos(delta(s), c)`, `||delta(s)||`, and — for subjects
owning ≥2 evaluable streams — the pairwise `cos(delta(s_i), delta(s_j))`
**within** that subject.

**TRAIN self-consistency, registered:** a **leave-one-subject-out** consensus
`c_{-u}` recomputed excluding subject `u`'s streams, and each TRAIN stream
scored against the consensus that did not see it. **This is the only honest
TRAIN-side alignment figure**, since a stream contributes to `c`.

---

## 3. B · Frozen-head compatibility

**The head is not approximated by a linear weight.** It is
`Linear(128→64) → SiLU → Dropout → Linear(64→1)`, evaluated in `eval()` mode so
dropout is inert, applied through `classifier.head` — never `classifier.forward`,
which would pool a `[N,128]` matrix a second time.

Per stream: `logit(mu_neg)`, `logit(mu_pos)`, and
**centroid logit separation** `= logit(mu_pos) − logit(mu_neg)`.

**Local head sensitivity along `delta`, registered grid:**

```
t ∈ {0.00, 0.25, 0.50, 0.75, 1.00, 1.50}      logit( mu_neg + t · delta )
```

`t=0` is `mu_neg`, `t=1` is `mu_pos`; `t=1.5` extrapolates beyond the positive
centroid to expose saturation. **No weight is modified and no gradient is
taken** — this is forward evaluation at frozen points on a fixed segment.

**The three-way attribution is registered as:**

| Reading | Signature |
|---|---|
| **(1) representation fails** | `cos(delta, c)` low or negative, and/or `‖delta‖` small |
| **(2) head fails** | `cos(delta, c)` high and `‖delta‖` normal, but centroid logit separation ≈ 0 or negative |
| **(3) both** | low alignment **and** non-positive centroid separation |

## 4. C · Subject-dominance

Computed on TRAIN first, then VALIDATION, label-conditioned:

- **within-subject dispersion** — mean over subjects of the mean squared
  distance of windows from their own subject centroid (trace of within-subject
  covariance);
- **between-subject centroid dispersion** — trace of the covariance of the
  subject centroids;
- **class separation** — `‖mu_pos − mu_neg‖` computed globally and per subject.

Reported as a ratio `between-subject / class-separation²` so the question
*"does subject identity dominate ischemia in this representation?"* has a
number rather than an impression.

## 5. D · Validation failure localization

**After §2–§4 are frozen.** The E9 failure streams — `s20311:1` (AUROC 0.2235),
`s20191:0` (0.4821), `s20191:1` (0.5241) — and the contrasting `s20311:0`
(0.9379) are located in the geometry.

**They define nothing.** They are not used to set a threshold, choose an
aggregation, or contribute to `c` — `c` is TRAIN-only and all four are
VALIDATION streams.

Reported for each: consensus alignment, `‖delta‖`, centroid logit separation,
and which of §3's three readings applies, or **none of the above**.

---

## 6. Registered predictions

1. **TRAIN leave-one-subject-out alignment will be high and tightly
   distributed** — a coherent class direction exists across seen subjects.
2. **VALIDATION alignment will be lower on average** than TRAIN LOSO.
3. **`s20311:1` will show negative or near-zero consensus alignment.** Its
   separation is −0.3057, so either its `delta` is reversed or the head inverts
   it. *This is the core E10 claim and the one most likely to fail.*
4. **`s20191:*` will show small `‖delta‖`** rather than reversed alignment —
   E9 attributed those to weak lead informativeness (separations −0.011,
   +0.035), not inversion.
5. **Between-subject centroid dispersion will exceed class separation** — the
   representation will be subject-dominated. *Falsifiable and important: if
   false, subject-invariance is not the problem.*

## 7. Interpretation rules

| Outcome | Recommendation |
|---|---|
| Failures associated with class-direction instability vs TRAIN | **(1)** new subject-invariant representation-learning experiment |
| Directions coherent, head maps them incorrectly | **(2)** head/memory-aware decision experiment, potentially E8b |
| Both fail | **(3)** representation retraining rather than calibration/personalization |
| No geometry mechanism reproduces | **(4)** close this branch |

## 8. Binding constraint on anything E10 recommends

**The 12 VALIDATION subjects have now been used for hypothesis generation
across E1, E2b, E3, E6a, E7a, E7b, E8a, E8b, E9 and E10.** Any intervention
derived from E10 **must not be presented as independently validated on that
partition.** A future model experiment must specify a **fresh subject-disjoint
development protocol inside the 56 TRAIN subjects** — split before any
outcome is read, with the split recorded — and treat the 12 validation subjects
as spent for confirmatory purposes.

**Bounds.** Mechanism evidence only. Development only. Uncertainty by subject
resampling, 1,000 replicates, seed 2026; **E6a applies — 44 and 9 evaluable
subjects.** No sealed generalization claim is available, permanently.
