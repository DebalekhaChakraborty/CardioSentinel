# B4 · E12d Instrumented E11 Phase-1 Replication — Report, V1

Executed under `B4_E12D_INSTRUMENTED_PHASE1_REPLICATION_PLAN_V1.md` and its
review amendment (§7.0 withdrawal of D1). **Phase 1 only. Development evidence
only. No phase 2, no outer-train retraining, no outer-held-out scoring, no
outer geometry, no outer operating point.** **Mechanism/instrument evidence
only — no medical or diagnostic claim follows.**

**E12d does NOT revise E11. E11 remains Category C.**

> ## HISTORICAL REPLICATION GATE: **PASSED**
>
> All six fits reproduced historical E11 inner-validation AUPRC
> **bit-identically**. Selected epochs reproduced exactly — **1, 1, 1, 2, 4, 1**.
> Epoch counts reproduced exactly — **5, 5, 5, 6, 8, 5**. All three B0
> `train_loss` trajectories reproduced **bit-identically**. B1 diagnostic
> total-loss differences were **only** the preregistered floating-point
> accumulation effect, **≈1.3 × 10⁻⁹ to 1.8 × 10⁻⁹ relative**.

**Headline: the morphology auxiliary loss had not plateaued at the
AUPRC-selected epoch under the observed E12d training horizon** — it continued
to decrease in all three folds. **But no coherent B1-specific geometry
continuation is established.** **Registered decision: D — NO FURTHER
CONCLUSION.**

---

## 1. Research question

E12a established that E11's checkpoint-selection instrument is noisy, and could
**not** determine whether the morphology auxiliary objective was still evolving
at the selected epoch, because E11 persisted neither a separate auxiliary loss,
nor inner-validation AUROC, nor per-epoch geometry, nor phase-1 checkpoints.

E12d asks exactly one question:

> Did the preregistered morphology auxiliary objective still have meaningful
> learning/geometry dynamics **after** the epoch selected by inner-validation
> AUPRC?

It is a **diagnostic replication of E11 phase 1** — not a performance
experiment, not a checkpoint search, not a λ or target experiment, and not a
new outer evaluation.

---

## 2. Authorization and execution provenance

| | |
|---|---|
| Attempt | **E12d ATTEMPT 2** (the only scientific E12d execution) |
| Authorization | `human-explicit-2026-08-27-E12d` |
| Started / finished | 2026-08-27T15:31:38Z → **2026-08-27T20:02:26Z** |
| Phase-1 training | **3.60 h** |
| Post-hoc geometry | **0.91 h** (separate; not training time) |
| `failure_state` | **None** |
| Terminal run state | **`SELECTION_FROZEN`** |
| Checkpoints retained | **34** (all phase-1 epochs, model state only), 45 MB |

**Run-state chain** — sealed, each stage over its predecessor:

```
DATA_BOUND        2026-08-27T15:31:38Z   seal 5e7dda233669739a
PHASE1_COMPLETE   2026-08-27T19:07:51Z   seal 5f86818fbc5995b6
SELECTION_FROZEN  2026-08-27T19:07:51Z   seal 5bf573fc693cdb93
```

**The chain stopping at `SELECTION_FROZEN` is itself the proof that phase 2 was
never executed.** The state machine refuses to skip `PHASE2_COMPLETE` and
`OUTER_SCORED`, so a later state is unreachable — not merely unused.
`E12D_COMPLETION.json` records `phase2_executed: false`,
`outer_held_out_scored: false`, `outer_geometry_computed: false`,
`outer_operating_point_computed: false`.

**Frozen inputs.** Split digest
`ce037309cc2d67944acbee76e82700e5a54c9d2ff69bf54a121ab1b8940206c3`;
374,452 rows; 56 subjects; auxiliary defined 374,448 / undefined 4; binding
digest `b5eba39843631530…f461c3d6`; execution plan digest
**`109c42a14daaf202e604994b40e4f349285783ff846d72a512088a4fe290c924`**, verified
by the driver before training with an abort on mismatch.

| fit | fold | arm | inner-train | inner-val | inner-val prevalence | scaler (median, IQR) |
|---|---|---|---|---|---|---|
| 0 | 0 | B0 | 195,043 | 30,367 | 0.0300 | — |
| 1 | 0 | B1 | 195,043 | 30,367 | 0.0300 | (−0.075, 0.14625) |
| 2 | 1 | B0 | 225,626 | 30,198 | 0.0246 | — |
| 3 | 1 | B1 | 225,626 | 30,198 | 0.0246 | (−0.105, 0.14) |
| 4 | 2 | B0 | 243,449 | 24,221 | 0.0251 | — |
| 5 | 2 | B1 | 243,449 | 24,221 | 0.0251 | (−0.1025, 0.14) |

**Loader audit** — the ATTEMPT 1 defect, closed: `fits 6`, `loaders_built 12`,
`train_loaders 6`, `validation_loaders 6`, `distinct_objects 12`,
`any_object_shared_between_fits false`.

---

## 3. Historical replication gate

Verified **before** any newly observable quantity was interpreted.

| fit | epochs | selected | AUPRC bit-identical | max abs ΔAUPRC | B0 `train_loss` bit-identical | B1 loss max rel. Δ |
|---|---|---|---|---|---|---|
| 0 / B0 | 5/5 | 1/1 | **True** | **0.0** | **True** | — |
| 0 / B1 | 5/5 | 1/1 | **True** | **0.0** | — | 1.78 × 10⁻⁹ |
| 1 / B0 | 5/5 | 1/1 | **True** | **0.0** | **True** | — |
| 1 / B1 | 6/6 | 2/2 | **True** | **0.0** | — | 1.29 × 10⁻⁹ |
| 2 / B0 | 8/8 | 4/4 | **True** | **0.0** | **True** | — |
| 2 / B1 | 5/5 | 1/1 | **True** | **0.0** | — | 1.46 × 10⁻⁹ |

`passed: true`, `mismatches: []`.

**This establishes that E12d ATTEMPT 2 reproduces the registered E11 phase-1
computation before interpreting the newly observable quantities.** The B1
deviations are the accumulation effect declared in plan §4.2 — E11 accumulated
one running total over the combined loss tensor while E12d accumulates BCE and
auxiliary separately and recombines. `backward()` received the identical tensor,
which is why AUPRC and the selected epochs are unaffected.

---

## 4. Phase-1 learning trajectories

`*` marks the AUPRC-selected epoch.

**Inner-validation AUPRC** (the registered selection statistic):

```
fold 0 B0  *0.41281   0.39119   0.35697   0.35101   0.39412
fold 0 B1  *0.46056   0.38349   0.34431   0.27151   0.38101
fold 1 B0  *0.30911   0.28473   0.23686   0.29836   0.19201
fold 1 B1   0.29571  *0.32747   0.32718   0.31453   0.24418   0.26649
fold 2 B0   0.18419   0.17007   0.16380  *0.25190   0.12639   0.17500   0.20790   0.17916
fold 2 B1  *0.26118   0.23994   0.20212   0.20834   0.20146
```

**Inner-validation AUROC** — newly observable; E11 recorded none:

```
fold 0 B0  *0.89509   0.90014   0.88006   0.87827   0.89043
fold 0 B1  *0.90996   0.91131   0.90704   0.88949   0.92114
fold 1 B0  *0.88128   0.88484   0.89285   0.88025   0.85061
fold 1 B1   0.87977  *0.89904   0.89381   0.89830   0.87413   0.89020
fold 2 B0   0.85551   0.86429   0.86474  *0.85238   0.85322   0.86564   0.87714   0.86191
fold 2 B1  *0.89148   0.89797   0.89080   0.87018   0.87342
```

**AUROC and AUPRC do not peak at the same epoch in any fit.** Fold 0 B1 is the
clearest: AUPRC peaks at epoch 1 while AUROC peaks at epoch 5. This is recorded
as observed; **no alternative selection metric is proposed or applied, and the
registered AUPRC rule is unchanged.**

**BCE loss** (both arms, separately recorded for the first time):

```
fold 0 B0  *0.19608   0.12775   0.10819   0.09782   0.09129
fold 0 B1  *0.19519   0.12438   0.10615   0.09496   0.08867
fold 1 B0  *0.22072   0.14955   0.13323   0.12454   0.11912
fold 1 B1   0.22135  *0.14774   0.13007   0.12077   0.11371   0.10755
fold 2 B0   0.21955   0.15204   0.13510  *0.12419   0.11826   0.11149   0.10589   0.10099
fold 2 B1  *0.22223   0.15301   0.13426   0.12391   0.11785
```

---

## 5. B1 auxiliary-loss trajectory

Raw SmoothL1 on `post_r_80ms_delta_mv`, λ-unweighted. **This quantity did not
exist for E11 and is the reason E12d was run.**

```
fold 0 B1  *0.09297   0.05024   0.04204   0.03785   0.03526
fold 1 B1   0.07597  *0.04156   0.03627   0.03405   0.03260   0.03094
fold 2 B1  *0.07502   0.04564   0.04094   0.03632   0.03467
```

**All three folds show continued post-selection decrease.**

> **The morphology auxiliary loss had not plateaued at the AUPRC-selected epoch
> under the observed E12d training horizon.**

**What this does not say, stated explicitly.** It does **not** say a later epoch
would have performed better; it does **not** say checkpoint selection truncated
a beneficial representation; and it does **not** say the auxiliary objective
would improve outer performance if trained longer. **Outer-held-out performance
was not evaluated in E12d at all**, so no such statement is available from this
evidence.

---

## 6. F / slope / V diagnostics

Amended estimands (plan §7.1–7.3), `EPSILON = 1e-12`:

```
F(x) = ( x(s) - x(E) ) / ( |x(s)| + EPSILON )
S(x) = ( x(s) - x(E) ) / ( (E - s) * ( max x - min x ) )
V(x) = ( max_{e>=s} x - min_{e>=s} x ) / ( |x(s)| + EPSILON )
```

| trajectory | fold | s | E | **F** | slope | V |
|---|---|---|---|---|---|---|
| B0 BCE | 0 | 1 | 5 | 0.5344 | 0.2500 | 0.5344 |
| B1 BCE | 0 | 1 | 5 | 0.5457 | 0.2500 | 0.5457 |
| **B1 auxiliary** | 0 | 1 | 5 | **+0.6208** | 0.2500 | 0.6208 |
| B0 BCE | 1 | 1 | 5 | 0.4603 | 0.2500 | 0.4603 |
| B1 BCE | 1 | 2 | 6 | 0.2721 | 0.0883 | 0.2721 |
| **B1 auxiliary** | 1 | 2 | 6 | **+0.2556** | 0.0590 | 0.2556 |
| B0 BCE | 2 | 4 | 8 | 0.1868 | 0.0489 | 0.1868 |
| B1 BCE | 2 | 1 | 5 | 0.4697 | 0.2500 | 0.4697 |
| **B1 auxiliary** | 2 | 1 | 5 | **+0.5378** | 0.2500 | 0.5378 |

**Registered F values for the auxiliary trajectory: fold 0 +0.6208, fold 1
+0.2556, fold 2 +0.5378.** All positive — endpoint loss lower after selection in
every fold.

**`V == F` in all nine cases.** Because `V` equals `F` exactly for a monotone
post-selection trajectory (plan §7.3), every trajectory here is monotone after
selection. **The non-monotonicity route into decision D therefore does not
apply**, and `V` triggered nothing, as registered.

**The withdrawn D1 quantity `R(x)` is not used anywhere in this report.**

---

## 7. Per-epoch representation geometry

Consensus built from **inner-train only**, per epoch, from the persisted
checkpoint; scored on **inner-validation only**. `diagnostic_only: true`,
`influences_selection: false`. Outer-held-out was not reachable by this path.

```
fold 0 B0  (8 evaluable inner-val streams)
   cos_med  *+0.9928   +0.9939   +0.9897   +0.9885   +0.9882
   |delta|  * 8.004     8.138     7.744     7.456     6.641
   neg      *     0         0         0         0         0
fold 0 B1  (8)
   cos_med  *+0.9900   +0.9814   +0.9805   +0.9855   +0.9797
   |delta|  * 8.097     8.323     7.512     6.841     7.553
   neg      *     0         0         0         0         0
fold 1 B0  (6)
   cos_med  *+0.9880   +0.9807   +0.9777   +0.9821   +0.9764
   |delta|  * 5.865     7.150     7.020     7.230     6.530
   neg      *     0         1         1         1         0
fold 1 B1  (6)
   cos_med   +0.9849  *+0.9788   +0.9897   +0.9838   +0.9524   +0.9779
   |delta|    6.320   * 6.736     7.634     7.860     6.384     6.397
   neg            1   *     0         1         0         0         1
fold 2 B0  (6)
   cos_med   +0.9792   +0.9784   +0.9727  *+0.9484   +0.9563   +0.9523   +0.9495   +0.9386
   |delta|    4.086     5.044     4.388   * 2.744     3.360     3.075     3.654     2.557
   neg            1         1         1   *     1         1         1         1         1
fold 2 B1  (6)
   cos_med  *+0.9547   +0.9666   +0.9624   +0.9147   +0.9429
   |delta|  * 4.696     4.549     4.362     3.391     3.199
   neg      *     1         1         1         1         1
```

---

## 8. B0-vs-B1 post-selection comparison

Post-selection geometry travel, `|value(E) − value(s)| / range`:

| fold | G_cos B0 → B1 | B1 greater? | G_norm B0 → B1 | B1 greater? |
|---|---|---|---|---|
| **0** | **0.7986 → 1.0000** | **yes** | **0.9098 → 0.3669** | no |
| **1** | **1.0000 → 0.0248** | no | **0.4876 → 0.2195** | no |
| **2** | **0.2400 → 0.2253** | no | **0.0751 → 1.0000** | **yes** |

Stated explicitly, as registered:

- **B1 exceeds B0 on cosine travel in only 1 of 3 folds.**
- **B1 exceeds B0 on delta-norm travel in only 1 of 3 folds.**
- **Those are different folds** — cosine in fold 0, delta-norm in fold 2.
- **Therefore there is no coherent B1-specific geometry continuation pattern.**

The two geometry endpoints also disagree *within* folds: fold 0 has B1 greater
on cosine and B0 greater on delta-norm; fold 2 is the reverse.

**Selection position.** In **5 of 6 fits the selected epoch precedes the largest
consecutive-epoch geometry movement** (fold 2 B0 is the exception).

**Interpretation, bounded as registered:** this is evidence that **representation
geometry continues to evolve after AUPRC checkpoint selection in most fits.**
**It is not evidence that later geometry is better.** E12d observed no outer
outcome and can make no such comparison.

---

## 9. Registered A/B/C/D decision

### **E12d DECISION = D — NO FURTHER CONCLUSION**

| branch | verdict | reason |
|---|---|---|
| **A** selection-protocol experiment justified | **fails** | B1 auxiliary loss continues after selection in all three folds, **but** B1 does not show consistently greater geometry evolution than B0 |
| **B** direct representation-objective experiment justified | **fails** | there **is** a coherent continued-learning pattern in B1 auxiliary loss |
| **C** general B4 training-dynamics investigation justified | **fails** | there **is** a B1-specific auxiliary-loss continuation pattern, so this cannot be reduced to a purely common B0/B1 training-dynamics result |
| **D** no further conclusion | **applies** | the arm-specific geometry comparison disagrees **across folds** and **across geometry endpoints** |

**D is frozen. It is not weakened or upgraded by narrative interpretation.**
No post-hoc magnitude threshold was introduced to reach any branch.

---

## 10. Protocol deviations

**1. Epoch runtime was not captured.** The phase-1 driver used the default no-op
clock, so every epoch record carries `seconds = 0.0`. **Classified as an
observability/logging omission, not a scientific replication defect** — it
touches no loss, no metric, no selection and no geometry. **Wall-clock execution
duration is available from the execution log** (phase-1 training 3.60 h,
post-hoc geometry 0.91 h).

**2. Inner-validation geometry denominators are small** — **8, 8, 6, 6, 6, 6**
evaluable streams. **Median geometry and normalized geometry-travel quantities
are therefore coarse descriptive instruments**: a median over six streams moves
in large steps, and `G_cos`/`G_norm` divide by a range that can itself be small.
**These values are reported exactly as observed and were not retrospectively
altered or smoothed.**

**No other deviation.** Sealed TEST untouched; historical 12-subject VALIDATION
untouched; no phase 2; no outer-held-out scoring; no outer geometry; no outer
operating point; the registered checkpoint-selection rule unchanged.

---

## 11. ATTEMPT 1 quarantine

**E12d ATTEMPT 1: HARNESS / RNG-REPLICATION FAILURE. SCIENTIFIC RESULT
INTERPRETABLE: NO.**

ATTEMPT 1's historical replication gate failed. All three B0 fits reproduced E11
bit-identically; all three B1 fits matched at epoch 1 and diverged thereafter.
Root cause: the driver cached the inner-validation DataLoader on row identity
and arm, and because the orchestrator requests it with `arm="B0"` for both arms,
each fold's B1 fit reused the B0 fit's object. With `persistent_workers=True` a
loader draws its worker `base_seed` from the **global** RNG exactly once, at
first iteration, so reuse skipped one global draw per fold and shifted every
subsequent dropout mask. Its receipt never advanced past `DATA_BOUND`; no
trajectory was interpreted and no geometry was executed.

**ATTEMPT 1's B1 trajectories must never enter E12d scientific results.**
ATTEMPT 1 evidence is preserved separately under
`E12D_PHASE1_REPLICATION/` with `E12D_ATTEMPT_1_CLASSIFICATION.md`.
**ATTEMPT 2 is the only scientific E12d execution**, and nothing from ATTEMPT 1
entered any calculation in this report.

---

## 12. Scientific interpretation

**E12d reproduced the registered E11 phase-1 computation exactly and then
observed what E11 could not.**

The one coherent finding is about the auxiliary objective itself: **it had not
plateaued at the AUPRC-selected epoch in any of the three folds**, with between
roughly a quarter and five-eighths of its selected-epoch value still to come
(F = +0.6208 / +0.2556 / +0.5378), and every post-selection trajectory monotone.
**Selection is landing early relative to the auxiliary objective's own
optimisation**, and in five of six fits it also lands before the largest
observed geometry movement.

**What E12d could not establish is that any of this is specific to B1.** The
arm-comparison endpoint — the only commensurable comparison available, since a
SmoothL1 morphology regression and a BCE classification loss are not
interchangeable quantities — disagrees across folds and across the two geometry
measures. B1 exceeds B0 on one endpoint in one fold and on the other endpoint in
a different fold. **That is the definition of an incoherent reading, and the
preregistration says to prefer D over narrative rescue.**

**The E11 null is therefore neither explained nor overturned.** E12a asked
whether a weak objective or a weak delivery mechanism produced Category C.
E12d shows the objective was still learning when delivery stopped — but cannot
show that this distinguishes B1 from B0. **The question E12a posed remains
open.**

**E12d does not revise E11. E11 remains Category C.**

---

## 13. Explicit non-claims

E12d does not claim, and must not be cited as claiming:

1. **Any medical or diagnostic performance.** Development evidence on a research
   corpus.
2. **That a later epoch would have performed better.** Outer-held-out
   performance was not evaluated in E12d at all.
3. **That checkpoint selection truncated a beneficial representation.** That
   the auxiliary loss was still falling says nothing about held-out benefit.
4. **That the auxiliary objective would improve outer performance if trained
   longer.**
5. **That later geometry is better.** Continued evolution is not improvement.
6. **Any revision of E11.** E11 remains Category C, unmodified.
7. **Any B1-specific geometry effect.** 1/3 folds on each endpoint, different
   folds, is not a pattern.
8. **Any inferential claim from three folds.** Every quantity here is
   descriptive; no interval is computed and none could be.
9. **Anything about the sealed TEST or historical VALIDATION partitions.**
   Neither was touched.
10. **Anything derived from E12d ATTEMPT 1.** Its B1 evidence is quarantined.

**Nothing in E1–E11 is revised by this report.**
