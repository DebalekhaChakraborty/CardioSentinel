# B4 · E13a Held-Out Geometry Reliability and Failure Taxonomy — Design and Preregistration, V1

**DESIGN AND PREREGISTRATION ONLY. NOT AUTHORIZED. NOT EXECUTED.**

**AMENDED AT REVIEW, 2026-08-28, before any E13a outcome existed.** The
amendment record is §0.1; every change is recorded in place rather than
silently applied.

**Read-only analysis of evidence already on disk. No retraining, no threshold
optimization, no historical VALIDATION, no sealed TEST, no new model.**

E13a asks whether the held-out geometry failures E10 and E11 observed are
**reliable properties of streams** or **artifacts of limited positive support**,
and whether *reversal*, *collapse* and *weak discrimination* are empirically
distinct. **It creates no new scientific conclusion about E11**, which remains
Category C.

---

## 0. Epistemic classification — what authority this evidence carries

**E13a is a POST-HOC MECHANISM ANALYSIS of subjects that were prospectively
outer-held-out during E11. It is NOT a fresh confirmatory cohort.**

The distinction is exact and matters. Those 44 subjects were held out
prospectively *for E11*, and E11 scored them once under a registered protocol.
E13a returns to the same scores and embeddings to ask a different, exploratory
question. **That is legitimate mechanism work and its value is not diminished by
saying so — but it is exploratory authority, not confirmatory authority, and it
must never be quoted as though a second held-out evaluation had occurred.**

> **After E13a, the 44-subject / 79-stream E11 B0 held-out geometry population
> is CONSUMED for future confirmatory geometry claims.**

This mirrors what already happened to the historical 12-subject VALIDATION
partition across E1–E10: repeated exploratory use spends a partition's ability
to confirm anything, whether or not any single use was improper. Recording the
consumption **now, in advance**, is what prevents a future session from
discovering it retrospectively.

**Any future confirmatory geometry claim requires a partition this programme
does not currently have.** No held-out estimate is obtainable within LTSTDB,
permanently; the sealed TEST is consumed; external corroboration was declined.

### 0.1 Amendment record

| # | Amendment |
|---|---|
| A1 | **§0 added** — post-hoc classification, and the population declared consumed for future confirmatory geometry claims |
| A2 | **§3.3 replaced** — the K=2 instrument is now literally non-overlapping in raw signal, with a boundary guard; measured outcome frozen in §3.3.1 |
| A3 | **§4 expanded** — the stability tuple now carries orientation to the TRAIN consensus per block, not only block-to-block agreement |
| A4 | **§3.6 demoted** — the cross-stream quantity is a **descriptive comparator**, never a null/chance/significance reference, and cannot trigger a decision |
| A5 | **§4.1 added** — coverage/exclusion is a primary estimand in its own right |
| A6 | **§8 decision C replaced** — no categorical collapse class; C is now stated on continuous evidence |
| A7 | **§8 decisions A, B, D replaced** — A's residual "collapse" reference removed and A restated as an exact, pre-named criterion; B's undefined categorical terms removed; D clarified. **Frozen 2026-08-28 before execution.** |

---

## 1. Population

**Primary analysis population: the E11 **B0** outer-held-out development
evidence** — the original B4-B recipe under the prospective 3-fold
subject-disjoint split.

```
44 evaluable subjects · 79 evaluable streams · split digest ce037309cc…206c3
B0 held-out artifacts: E11_ATTEMPT_2/artifacts/e11_fold{0,1,2}_B0.npz
```

**B0 only.** B1 is not the subject of E13a; the question is about the
representation the programme actually selected. B1 evidence exists and is not
used here.

**Measured support in the population (feasibility, not a result):**

| quantity | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|
| positive windows / stream | 12 | 330 | 814 | 1,508 | 5,062 |
| windows / stream | 2,000 | — | 3,526 | — | 7,613 |
| stream span (minutes) | 1,012 | — | 1,407 | — | 2,869 |

**1 of 79 streams has fewer than 30 positives; 5 have fewer than 100.**

---

## 2. Research questions

1. **Are negative/weak class-direction estimates temporally stable within
   streams, or partly caused by limited positive support?**
2. **How do positive-window count, episode count, prevalence and stream duration
   relate to cosine-to-TRAIN-consensus, `‖delta‖`, and stream AUROC?**
3. **Are representation reversal and representation collapse empirically
   distinct and reproducible failure modes?**
4. **What characterizes the three prospective B0 negative-direction streams,
   without using them to define the analysis retrospectively?**

---

## 3. The stability instrument — defined before anything is computed

### 3.1 Why windows must not be bootstrapped

**Windows are not independent samples and must never be resampled as if they
were.** ST episodes persist for minutes to hours; adjacent windows share
physiological state, and in LTSTDB a stream spans a median of **1,407 minutes**.
Bootstrapping windows would treat thousands of correlated observations as
thousands of replicates and manufacture precision that does not exist. **This is
the same class of error E2 already made once**, where bootstrapping an
argmax-selected quantity pinned the interval to the maximum and the instrument
was withdrawn.

**No window-level bootstrap, no window-level permutation, and no per-window
interval appears anywhere in E13a.**

### 3.2 Chronological order must be reconstructed, not assumed

**0 of 132 streams are in chronological order in the B4 arrays** — they are
sorted lexicographically. `start_sample` is recoverable from the cache's own
stable id (`ltstdb:record:channel:start:end`) and **every temporal operation in
E13a sorts by it first**. A block analysis performed on array order would be
meaningless, and would look identical to a correct one.

### 3.3 Primary instrument — contiguous, non-overlapping temporal halves

**The registered B4 windows overlap.** The cache manifest records
`window_seconds = 10.0` against `stride_seconds = 5.0` at 250 Hz — **adjacent
windows share 5 seconds of raw signal**. A naive index split would therefore put
the *same waveform samples* in both blocks and the two "independent" halves
would share data at their boundary.

**Procedure, in order:**

1. **sort every stream numerically by `start_sample`** (mandatory — §3.2);
2. **define the split by the preregistered within-stream midpoint rule**:
   `A = positions [0, n//2)`, `B = positions [n//2, n)`;
3. **apply the overlap guard** — remove the minimal trailing window(s) from
   block A until **no raw waveform interval assigned to A overlaps any interval
   assigned to B**, i.e. until `max(end_A) <= min(start_B)`;
4. **record pre-guard and post-guard window counts and class counts** for every
   stream.

**The blocks are not otherwise altered.** No window is moved, added or dropped
to improve class balance. Eligibility is unchanged: **both classes must be
represented in both post-guard blocks.**

For each block independently:

```
delta_H = mu_positive(H) - mu_negative(H)          H in {A, B}
```

#### 3.3.1 Measured guard effect — frozen before execution

| | |
|---|---|
| window / stride | 10.0 s / 5.0 s → **50% overlap between adjacent windows** |
| boundary windows dropped | **min 0, median 0, max 1** |
| K=2 eligible **before** guard | **57 / 79** |
| **K=2 eligible AFTER guard** | **57 / 79 — FROZEN** |
| streams whose eligibility the guard changed | **0** |

**The guard costs almost nothing here**, because the B4 cache is a *selected*
subset rather than a contiguous stride: consecutive retained windows are usually
far enough apart that no boundary overlap exists. **The denominator therefore
remains 57 / 79 and is frozen at that value.** The guard is retained regardless,
because its cheapness is a property of this cache and not a guarantee.

**Post-guard positive support across the 57 eligible streams:** block A min 11,
median 560, max 2,805; block B min 37, median 518, max 2,541.

#### 3.3.2 One eligibility fact about the named subset, frozen now

Of the **three** prospective B0 negative-direction streams, **two are eligible
and one is not**:

| stream | fold | block A | block B | guard | eligible |
|---|---|---|---|---|---|
| `s20171:0` | 0 | 1,660 windows, **295** positive | 1,661 windows, **148** positive | 1 dropped | **yes** |
| `s20101:1` | 1 | 1,654 windows, **0** positive | 1,654 windows, **390** positive | 0 | **NO** |
| `s20021:1` | 2 | 1,610 windows, **72** positive | 1,611 windows, **297** positive | 0 | **yes** |

**`s20101:1` carries every one of its 390 positive windows in the second
temporal half and none in the first.** It is therefore ineligible for the
stability instrument — not by choice, but because a direction cannot be
estimated in a block with no positives.

**This is recorded here, before execution, so that it can never be presented as
a post-hoc exclusion.** It is also directly relevant to RQ1: complete temporal
concentration of the positive class is exactly the kind of support limitation
RQ1 asks about, and it is reported as evidence under §4.1 rather than treated as
missing data.

### 3.4 Secondary instrument and its cost, stated in advance

| blocks K | streams with both classes in every block | share |
|---|---|---|
| **2 (primary)** | **57 / 79** | **72%** |
| 3 (secondary) | 38 / 79 | 48% |
| 4 | 31 / 79 | 39% |
| 6 | 24 / 79 | 30% |

**K = 3 is reported as a sensitivity analysis only, with its reduced
denominator printed beside every value.** K ≥ 4 is not used: it discards more
than 60% of the cohort, and the streams it discards are exactly the
sparse-positive ones the analysis is about.

**The 22 streams excluded at K = 2 are themselves a finding and are reported as
a named group**, not silently dropped. Their exclusion means positives are
concentrated in one temporal half — which is directly relevant to RQ1.

### 3.5 Episode-aware variant — conditional

If `STEvent` episode boundaries can be aligned to held-out rows under the
existing development authority (`onset_sample` / `end_sample` / `lead` are
present in the data model), a variant splitting at **episode boundaries rather
than the median sample** is reported alongside. **Alignment must be
demonstrated, not assumed.** If it cannot be demonstrated legally and exactly,
the variant is reported **NA** and the halves instrument stands alone.

### 3.6 Cross-stream quantity — a DESCRIPTIVE COMPARATOR only

`cos_within` invites the question "compared to what?", and the honest answer is
that **this analysis has no null distribution available.**

**B4 may contain a genuinely shared class direction across streams** — E10
measured TRAIN leave-one-subject-out cosine at min **+0.971** with **0/79
negative**, which is precisely a shared direction. **A high cross-stream cosine
is therefore scientifically expected, not evidence of chance agreement.**

The cross-stream quantity is defined as

```
cos( delta_A(i) , delta_B(j) )      subject to
    stream_i != stream_j            (different streams)
    subject_i != subject_j          (subject-disjoint)
    outer_fold_i == outer_fold_j    (same fold, same frozen consensus)
```

**Subject-disjointness is required**: two streams from the same patient share
physiology and electrode placement, and pairing them would measure within-patient
similarity while appearing to measure across-patient similarity.

> **It is a descriptive comparator. It is NOT a null distribution, NOT a chance
> distribution, and NOT a significance reference. It may not independently
> trigger an A/B/C/D decision**, and no test statistic, p-value or interval is
> computed from it.

Shuffling labels within a stream is also excluded — it would destroy the very
temporal structure the instrument exists to respect.

---

## 4. Preregistered estimands

All are **continuous** and **descriptive**. **No categorical threshold is
introduced anywhere in E13a**, consistent with E11 amendment A4, which deleted
the collapse category precisely because no defensible TRAIN-only cut exists.

**Per stream (n = 79 unless stated):**

| # | Estimand |
|---|---|
| G1 | `cos(delta_s, fold B0 outer-train consensus)` — whole stream |
| G2 | `‖delta_s‖` — whole stream |
| G3 | stream AUROC |
| G4 | positive-window count, prevalence, window count, span in minutes |
| G5 | episode count and total episode duration *(conditional, §3.5)* |

**Per stream eligible under §3.3 (n = 57) — the primary stability tuple:**

| # | Estimand | Why it is required |
|---|---|---|
| **S1** | `cos_within = cos(delta_A, delta_B)` | within-stream **directional reproducibility** |
| **S2a** | `cos_A_train = cos(delta_A, train_consensus)` | orientation of block A against the fold's frozen B0 **outer-train** consensus |
| **S2b** | `cos_B_train = cos(delta_B, train_consensus)` | orientation of block B against the same consensus |
| **S2c** | whether `sign(cos_A_train) == sign(cos_B_train)` | **temporally reproducible orientation** |
| **S3a** | `norm_A = ‖delta_A‖` | magnitude in block A |
| **S3b** | `norm_B = ‖delta_B‖` | magnitude in block B |
| **S3c** | `norm_A / norm_B` | magnitude stability |
| **S4** | half-A and half-B stream AUROC | discrimination, per block |
| **S5** | the §3.6 cross-stream **descriptive comparator** | context only — cannot trigger a decision |

**S2 is not optional, and S1 alone would be misleading.** A high
`cos(delta_A, delta_B)` says the two halves agree with *each other* — it does
**not** say what they agree *on*. Two halves can agree perfectly while both
pointing **against** the TRAIN consensus, which is stable reversal, and they can
agree perfectly while both pointing with it, which is ordinary stability. **S1
cannot distinguish those two cases; only S2 can.**

> **Stable reversal therefore requires the temporal blocks themselves to
> preserve the negative orientation relative to the legally corresponding TRAIN
> consensus** — that is, `cos_A_train < 0` **and** `cos_B_train < 0`, evaluated
> against the frozen consensus of that stream's own fold.

**The consensus is the one E11 already froze** for that fold's B0 arm, built
from that arm's outer-train representation before any held-out row was embedded.
E13a does not rebuild or re-choose it.

**No magnitude threshold is introduced.** `norm_A`, `norm_B` and their ratio are
reported as continuous quantities.

**Association (RQ2).** **Spearman rank** correlation only — the covariates are
heavily skewed (positives span 12 to 5,062) and no linear form is registered.
Reported as a matrix of coefficients with n printed in every cell. **No p-value
threshold governs any decision**, and no regression is fitted.

### 4.1 Coverage and exclusion — a primary estimand, not bookkeeping

**The 79 streams are the full descriptive population. The K=2 stability analysis
is a support-qualified estimand over a subset of them.** These are different
denominators and are never merged.

Reported explicitly, always together:

| quantity | value |
|---|---|
| total evaluable held-out streams | **79** |
| K=2 eligible after overlap guard | **57** |
| K=2 ineligible | **22** |
| reason for ineligibility | a post-guard block contains only one class |
| positive support per block | reported per stream, both blocks |
| prevalence per block | reported per stream, both blocks |

> **K=2 stability findings are never generalized to the 22 excluded streams.**
> Any statement about stability carries the denominator 57, and any statement
> about the population carries 79.

**The excluded streams are themselves evidence.** A stream is excluded precisely
because its positive class is concentrated in one temporal half — which is a
direct observation about the temporal structure of ischemia in that stream, and
is exactly what RQ1 asks about. **They are reported as a named group with their
support profiles, not as missing data.**

**No imputation.** No excluded stream receives an estimated `cos_within`,
orientation or magnitude by any means.

---

## 5. Reversal, collapse and weak discrimination — kept distinct

These are **three phenomena, not one**, and E13a never collapses them into a
single score:

| phenomenon | continuous quantity | what it would mean |
|---|---|---|
| **reversal** | `cos(delta_s, consensus)` **< 0** — sign, not magnitude | the direction points the wrong way |
| **collapse** | small `‖delta_s‖` relative to the cohort | the direction is barely present |
| **weak discrimination** | low stream AUROC | scores separate poorly, whatever the geometry |

**Sign is not a threshold.** `cos < 0` is a property of the estimate, not a cut
chosen by the analyst, and is the only categorical distinction E13a uses.

**RQ3 is answered by the joint distribution, not by classification.** E13a
reports the rank correlation between `cos` and `‖delta‖`, the rank correlation
of each with AUROC, and whether the streams occupying the low tail of one are
the streams occupying the low tail of the other. **Reproducibility is answered
by S1/S2**: a failure mode is *reproducible* if it appears in **both independent
temporal halves of the same stream**, and this is reported as a count out of the
57-stream denominator.

---

## 6. The three negative-direction streams (RQ4)

The prospective B0 held-out population contains **three** negative-cosine
streams:

```
s20171:0  subject s2017  fold 0   cos -0.3626  ||delta|| 1.076
s20101:1  subject s2010  fold 1   cos -0.7449  ||delta|| 2.589
s20021:1  subject s2002  fold 2   cos -0.9033  ||delta|| 2.246
```

**They do not define the analysis.** Every estimand in §4 is computed over the
full 79-stream (or 57-stream) population, and the three are then located within
those already-computed marginal distributions as a **pre-specified named
subset**. Nothing is fitted to them, no covariate is selected because it
separates them, and no threshold is tuned to isolate them.

**One feasibility observation, recorded now so it cannot later be presented as a
discovery:** their positive-window counts are **444, 390 and 369** against a
cohort median of **814** and Q1 of **330**. **All three sit above the first
quartile of positive support.** Whatever explains them, "almost no positives"
does not obviously. This is stated as a property of the population as it exists
today, and **it is not a result** — RQ1 is still answered by the stability
instrument, not by this observation.

---

## 7. Metadata audit

| covariate | source | status |
|---|---|---|
| positive burden, prevalence, window count | `e11_train_y.npy` + stream ids | **available** |
| stream duration / temporal order | `start_sample` parsed from stable ids | **available** — and mandatory (§3.2) |
| signed morphology | `extract_morphology_features` (`morphology_v1`, incl. `post_r_80ms_delta_mv`) | **available**, label-free and causal (E11 gate A1) |
| **true lead** | `wfdb` header `sig_name` via `ltstdb.py`; channel index in the stable id | **conditional** — the channel index is certain, the lead *name* requires header alignment that must be demonstrated |
| **SQI** | `m2_feature_join` / `m2_evidence` | **conditional on exact row alignment.** E9 already found SQI does **not** predict held-out failure; E13a uses it as a covariate, **not as a revived hypothesis** |
| **episode count / duration** | `STEvent` (`onset_sample`, `end_sample`, `lead`) | **conditional** — alignment to held-out rows must be demonstrated |
| M1 representation-memory quantities | `m1-stream-memory-v2` (**chronological**, digest-verified) | **conditional on legal alignment.** E8a/E8b evidence, reused as covariates only |

**Any covariate whose alignment cannot be demonstrated exactly is reported
`NA`.** None is approximated, imputed or reconstructed. **Every table prints its
own denominator.**

---

## 8. Preregistered decision rule

| decision | condition |
|---|---|
| **A · STABLE ORIENTATION FAILURE SUPPORTED** | **Both** K=2-eligible, previously identified full-stream negative-orientation streams — **`s20171:0` and `s20021:1`** — show `cos_A_train < 0` **AND** `cos_B_train < 0` against their **own fold-specific frozen E11 B0 outer-train consensus**. **This criterion is fixed before execution and may not be relaxed to one-of-two after observing results.** `s20101:1` is **not** counted as a failed stability observation — its first temporal block contains zero positive windows, so no direction is estimable there; it remains part of the registered coverage / temporal-concentration result (§4.1) |
| **B · GEOMETRY INSTRUMENT / SUPPORT INVESTIGATION JUSTIFIED** | Temporal replication does **not** support stable negative orientation in the eligible failure streams, **AND** the observed evidence supports class-support / temporal-concentration instability as the appropriate next methodological problem **without introducing any new numerical cutoff**. **If reaching B would require inventing a threshold for sparse support, low `cos_within`, unstable norm, or any other post-hoc category, return D instead** |
| **C · MULTIPLE REPRESENTATION-FAILURE SIGNATURES SUPPORTED** | **all three** must hold on continuous evidence: (i) **temporally reproducible negative orientation** in one signature — `cos_A_train < 0` **and** `cos_B_train < 0` for the same stream; **and** (ii) a **distinguishable weak-magnitude / weak-discrimination signature** that does **not** share that negative-orientation pattern; **and** (iii) the distinction is **not adequately explained by positive-support instability** (§4.1). **No categorical collapse threshold and no post-hoc classifier may be introduced.** **One generic geometry loss would then be the wrong instrument and must not be proposed** |
| **D · NO COHERENT MECHANISM ESTABLISHED** | A/B/C are not cleanly satisfied. In particular: **one of the two eligible negative streams reproducing while the other does not is NOT sufficient for A**; ambiguous support effects are **not** sufficient for B; an apparent second signature requiring a newly invented cutoff is **not** sufficient for C |

**C requires no categorical "collapse" class**, and none is defined anywhere in
E13a. Its second clause is satisfied by the continuous joint distribution of
orientation, magnitude and discrimination — by streams occupying the weak tail of
magnitude/AUROC *without* carrying reproducible negative orientation — not by a
class membership.

> **If C cannot be determined without inventing a new threshold or a post-hoc
> classification rule, the decision is D.** No numerical cutoff may be
> introduced after seeing outcomes in order to manufacture the distinction.

**A and C are not mutually exclusive in evidence but are in recommendation:** if
both stability (A) and separability (C) hold, **C governs**, because
recommending a single objective for two mechanisms would be the more expensive
error.

**Prefer D over post-hoc reinterpretation.** No magnitude threshold may be
introduced after seeing results in order to reach A, B or C.

### 8.1 Boundaries preserved, in full

**Excluded from E13a entirely — not merely from its decision branches:**

model training · checkpoint selection · threshold optimization · λ changes ·
morphology-target changes · **any new morphology hypothesis** · **any revived
SQI hypothesis** · historical VALIDATION · sealed TEST · outer-held-out
alternative-epoch scoring · **window-level bootstrap** · **any naive
independence assumption over windows**.

**SQI remains a covariate only if exact row alignment is demonstrated.** E9
already refuted SQI as a predictor of held-out failure; E13a does not reopen
that question and uses SQI, if alignable, only as a descriptor.

**Lead, episode and M1 quantities remain `NA` unless exact row alignment is
proven.** None is approximated, imputed or reconstructed, and no result may
depend on one that could not be aligned.

---

## 9. Feasibility

**Feasible and cheap.** Every input exists on disk: E11 B0 held-out embeddings
and scores, the frozen split, labels, subjects, streams and stable ids.
**No training, no GPU, no new data access.** Expected cost is minutes of CPU and
negligible storage — the analysis is arithmetic over 79 streams of
128-dimensional deltas.

**Authority.** E13a reads only `outer_held_out` and `outer_train` rows through
`E11FoldAuthority`, which has no accessor capable of naming TEST or the
historical VALIDATION partition.

---

## 10. Risks and limitations, registered in advance

1. **K = 2 yields one `cos_within` per stream** — a single agreement measurement, not a variance estimate. The instrument can show *whether* halves agree, not how much that agreement varies within a stream.
2. **The 22 streams excluded at K = 2 are not missing at random.** They are excluded precisely because their positives cluster in time, which is plausibly related to the phenomenon under study. Their exclusion is reported as a result, not a footnote.
3. **Three negative streams is a very small named subset.** Nothing inferential can rest on three streams, and §6 forbids fitting to them.
4. **79 streams over 44 subjects are not independent** — streams within a subject share physiology and hardware. Any cross-stream summary reports its subject denominator alongside its stream denominator.
5. **A clean E13a result authorizes nothing.** Every branch is a recommendation about what to investigate, and any subsequent experiment needs its own human authorization.
6. **E13a cannot revise E11 or E12d.** It observes no new outcome and re-scores no model.

---

## 11. Explicit non-claims

E13a will not claim any medical or diagnostic performance; will not revise E11's
Category C or E12d's Decision D; will not assert that any model, epoch,
threshold or objective would perform better; will not treat 79 streams or 44
subjects as an inferential sample; will not use the historical VALIDATION or
sealed TEST partitions; and will not reintroduce the collapse category as a
categorical endpoint.

---

## 12. Authorization boundary

**E13a must not be executed until a separate, explicit human authorization is
issued.** This document is design and preregistration only. Under the standing
§A8 policy, re-execution after any failure is a **new attempt requiring new
authorization**. **NO AUTOMATIC RETRY.**
