# B4 · E10 Representation-Geometry Audit — Report, V1

Executed under `B4_E10_REPRESENTATION_GEOMETRY_PLAN_V1.md`. **Read-only,
development only. No retraining, no sealed-test artifact, no new model
selection, no weight modified.** **Mechanism evidence only.**

**Headline: the geometry separates the failures completely, and the head is
innocent.** The three E9 failure streams are the **three lowest-alignment,
three smallest-magnitude and three lowest centroid-separation streams in
validation, with no overlap against the other sixteen.** The frozen head maps
whatever direction the representation supplies, faithfully, in every case.

**And registered prediction 5 is refuted in a way that changes the
prescription:** the representation is **not** subject-dominated. Class
separation exceeds between-subject centroid dispersion by **26×** on TRAIN and
**12×** on VALIDATION.

---

## 1. A · Class-direction geometry

The consensus `c` was defined on **TRAIN only** — 79 evaluable streams,
unit-normalised per stream, equal weight per stream, so window count is not
treated as replication.

| | TRAIN (79 streams, 44 subjects) | VALIDATION (19 streams, 9 subjects) |
|---|---|---|
| `cos(delta, c)` **leave-one-subject-out** | min **+0.971**, med +0.993, max +0.999 | — |
| `cos(delta, c)` in-sample / frozen `c` | min +0.971, med +0.993 | min **−0.935**, med +0.987, max +0.998 |
| **streams with cos < 0** | **0 / 79** | **2 / 19** |
| `‖delta‖` | min **4.264**, med **8.656**, max 16.194 | min **0.972**, med **4.685**, max 12.917 |

**TRAIN's class direction is extraordinarily coherent.** The leave-one-subject-out
figures are indistinguishable from the in-sample ones (both min +0.971), so `c`
is not an artifact of any single subject — that is the registered subject-level
robustness check, and it passes.

**On unseen subjects the direction is both weaker and occasionally reversed.**
Median `‖delta‖` roughly halves (8.656 → 4.685) and two streams invert.

**Within-subject cross-stream agreement** — 59 TRAIN pairs, min **+0.951**; 14
VALIDATION pairs, min **−0.922**. **The only two negative pairs in the entire
study are `s2031` (−0.922) and `s2019` (−0.416)** — precisely the two subjects
that own the E9 failures. Every other validation pair is ≥ +0.911.

## 2. B · Frozen-head compatibility — the head is not the failure

Centroid logit separation `logit(mu_pos) − logit(mu_neg)`:

| | min | median | max | negative |
|---|---|---|---|---|
| TRAIN | **+3.321** | +7.553 | +14.427 | **0 / 79** |
| VALIDATION | **−2.126** | +4.485 | +11.099 | **2 / 19** |

**Centroid separation tracks alignment almost deterministically:**
cos −0.935 → sep −2.126; cos −0.132 → sep −0.177; cos +0.394 → sep +0.372; and
**every stream with cos ≥ +0.933 has sep ≥ +2.684.**

**Local head sensitivity along `delta`** (frozen grid `t = 0, .25, .5, .75, 1, 1.5`;
forward evaluation only, no weight touched, no gradient taken):

| stream | t=0 | 0.25 | 0.50 | 0.75 | 1.00 | 1.50 |
|---|---|---|---|---|---|---|
| **s20311:1** | +0.45 | −0.06 | −0.59 | −1.12 | −1.67 | **−2.82** |
| **s20191:0** | −5.18 | −5.22 | −5.27 | −5.31 | −5.36 | **−5.45** |
| **s20191:1** | −3.27 | −3.18 | −3.09 | −2.99 | −2.90 | −2.72 |
| s20311:0 | −8.05 | −6.35 | −4.66 | −3.00 | −1.39 | **+1.55** |

`s20311:1` decreases **monotonically** from its negative centroid toward its
positive centroid — the head is behaving consistently with a reversed direction.
`s20191:*` is essentially **flat**: the direction carries almost nothing to map.
The healthy `s20311:0` rises monotonically across the full span.

**Registered attribution: reading (1) — the representation fails, and the head
maps it faithfully.** Reading (2) — a valid direction mapped incorrectly —
**does not occur anywhere**, on TRAIN or VALIDATION.

## 3. C · Subject dominance — prediction 5 refuted

| | between-subject centroid trace | within-subject trace | mean `‖delta‖²` | **between / class** |
|---|---|---|---|---|
| TRAIN | 3.1625 | 13.8395 | **82.4198** | **0.038** |
| VALIDATION | 3.0024 | 9.7997 | **35.0621** | **0.086** |

**Class separation dominates subject identity by 26× on TRAIN and 12× on
VALIDATION.** I predicted the opposite. **The representation is not
subject-dominated**, so "subject nuisance swamps the class signal" is **not**
the mechanism, and §5 qualifies the prescription accordingly.

Note that between-subject dispersion is near-identical across partitions
(3.16 vs 3.00) while mean class separation **more than halves** (82.4 → 35.1).
**What degrades on unseen subjects is the class signal, not the subject
nuisance.**

## 4. D · Failure localization — complete separation

The four streams were located **after** every definition above was frozen, and
**none of them contributed to `c`**, which is TRAIN-only.

| stream | cos | `‖delta‖` | logit(mu_neg) | logit(mu_pos) | centroid sep | AUROC |
|---|---|---|---|---|---|---|
| **s20311:1** | **−0.935** | **3.109** | +0.453 | −1.673 | **−2.126** | **0.2235** |
| **s20191:0** | **−0.132** | **0.972** | −5.180 | −5.357 | **−0.177** | **0.4821** |
| **s20191:1** | **+0.394** | **1.004** | −3.273 | −2.901 | **+0.372** | **0.5241** |
| *next worst (s20581:1)* | +0.933 | 6.264 | −6.361 | −0.449 | +5.912 | — |
| **s20311:0** | **+0.995** | 6.721 | −8.053 | −1.394 | **+6.659** | **0.9379** |

**The three failures are simultaneously the three lowest cosines, the three
smallest `‖delta‖`, and the three lowest centroid separations — and there is a
clean gap to the sixteen others** (next cosine +0.933, next `‖delta‖` 3.148,
next separation +2.684).

**Two distinct geometric failures, not one:**

- **`s20311:1` — direction reversal.** `cos = −0.935` with substantial magnitude
  (3.109). The class direction exists and points the wrong way.
- **`s20191:0/1` — direction collapse.** `‖delta‖` of **0.972** and **1.004**,
  the two smallest in the study against a TRAIN minimum of 4.264. There is
  barely a direction to point. This matches E9's M-inf attribution and
  **confirms registered prediction 4.**

**`s20311:0`, the healthy sibling, sits at cos +0.995** — so within one subject
and one record, one channel is textbook and the other is inverted.

## 5. Registered predictions

| # | Prediction | Outcome |
|---|---|---|
| 1 | TRAIN LOSO alignment high and tight | **Confirmed** — min +0.971, 0/79 negative |
| 2 | VALIDATION alignment lower than TRAIN LOSO | **Confirmed** |
| 3 | `s20311:1` negative or near-zero alignment | **Confirmed** — −0.935 |
| 4 | `s20191:*` small `‖delta‖` rather than reversed | **Confirmed** — 0.972 / 1.004, the two smallest |
| 5 | Between-subject dispersion exceeds class separation | **REFUTED** — 0.038 / 0.086, class dominates |

---

## 6. Recommendation

**Rule 1's antecedent holds: unseen-subject failures are associated with
class-direction instability relative to TRAIN**, and the association is
complete rather than statistical — three of three failures, sixteen of sixteen
non-failures, with a clean gap.

**Rules 2 and 3 do not fire.** The head never mis-maps a valid direction; there
is no stream in the study with high alignment and non-positive separation. A
head-side or memory-aware decision experiment cannot repair a reversed or
collapsed direction, so E8b's C0/C1 probe should **not** be promoted on the
strength of E10.

### 6.1 One qualification, forced by §3

**"Subject-invariant representation learning" is the standard prescription for
rule 1 and it is not quite what this evidence indicates.** Subject-invariance
objectives suppress subject nuisance — and §3 shows subject nuisance is already
small (between/class 0.038). What degrades is the **class signal itself**
(mean `‖delta‖²` 82.4 → 35.1) with subject dispersion essentially unchanged.

**The indicated objective is class-direction stability across unseen streams —
sign consistency and magnitude retention — not nuisance removal.** Connecting
E9: the target is **polarity-agnostic**, collapsing elevation and depression
episodes into one class, so a representation organised around a single dominant
class direction has no way to represent both consistently. **That is a
plausible generator of exactly the two failure modes observed**, and E9 already
showed polarity alone does not predict failure, so it is a hypothesis for the
next experiment rather than a conclusion of this one.

### 6.2 The binding constraint on anything that follows

**The 12 VALIDATION subjects are spent for confirmatory purposes.** They have
been used for hypothesis generation across E1, E2b, E3, E6a, E7a, E7b, E8a,
E8b, E9 and E10. **No intervention derived from E10 may be presented as
independently validated on them.**

Any future model experiment must:

1. define a **fresh subject-disjoint split inside the 56 TRAIN subjects**,
   recorded before any outcome is read;
2. treat the 12 validation subjects as **hypothesis-generating only**;
3. carry E6a's instrument limit — 44 TRAIN evaluable subjects is the largest
   honest unit count now available, and it still cannot resolve small contrasts;
4. state in advance that **no sealed generalization evidence is obtainable**,
   permanently.

---

## 7. Bounds

- **Mechanism evidence only.** Not development performance, not generalization.
- **19 evaluable validation streams in 9 subjects; 79 TRAIN streams in 44.**
  Three failures in two subjects — a small denominator behind a clean split.
- Subject-level robustness is provided by the **leave-one-subject-out
  consensus**; no additional bootstrap was run, and no contrast here is
  interval-estimated.
- Centroids are means of a high-dimensional embedding; `‖delta‖` is **not**
  comparable to a metric on the score scale.
- **No weight was modified, no gradient taken, no sealed artifact opened.**
