# B4 · E12a Training-Dynamics and Checkpoint-Selection Audit — Report, V1

**Read-only instrument audit of the six completed E11 phase-1 training
histories.** No model was trained, no checkpoint was regenerated, no
outer-held-out subject was scored at any alternative epoch, and **nothing in
E11 is modified**. E11 remains formally frozen at **Category C**.

**This audit produces no new scientific outcome.** It characterises the
*instrument* that selected E11's checkpoints. It must not be used to
retrospectively choose a better E11 checkpoint, and no selected epoch has been
changed.

**Research question.** Did E11's nested checkpoint-selection process provide a
stable opportunity for the morphology auxiliary objective to influence
representation learning, or were B0/B1 selected under an early/noisy selection
regime that limits interpretation of the E11 null?

**Headline: the selection instrument is demonstrably weak, and the auxiliary
objective's maturity is UNOBSERVABLE.** The persisted evidence refutes the
"stable selection" explanation and cannot confirm the "still-evolving
auxiliary" explanation, because the auxiliary loss was never separately logged.
**Recommendation: C — no further conclusion**, for a reason that is a one-line
persistence gap rather than a scientific ambiguity.

---

## 1. Evidence availability

Enumerated from the execution receipt, the preserved artifacts, and the runner
source. **A definitive filesystem search for `*.pt`, `*.pth`, `*.ckpt` and any
per-epoch artifact returned nothing**, and the runner contains exactly one
`savez_compressed` call, which writes the post-phase-2 representation only.

| Quantity | Status | Detail |
|---|---|---|
| Per-epoch inner-validation **AUPRC** | **OBSERVED** | all six fits, `phase1_history[].inner_auprc` |
| Per-epoch inner-validation **AUROC** | **UNOBSERVABLE** | never computed or recorded |
| **Total** training loss per epoch | **OBSERVED** | `phase1_history[].train_loss` |
| **Primary (BCE) loss** separately | **UNOBSERVABLE** | for B1, only the summed total was accumulated |
| **Auxiliary loss** for B1 | **UNOBSERVABLE** | never recorded as a separate term |
| Morphology prediction metric | **UNOBSERVABLE** | never computed |
| **Learning rate** | **OBSERVED by registration, not per-epoch** | AdamW, `lr = 1e-3` constant; **no scheduler exists in the frozen recipe** |
| **Selected epoch** | **OBSERVED** | all six fits |
| Phase-1 **checkpoints** | **UNOBSERVABLE** | none saved; phase-1 models discarded by construction |
| Per-epoch **embeddings / predictions** | **UNOBSERVABLE** | none saved |
| Epoch wall time | OBSERVED | `phase1_history[].seconds` |

Persisted per-arm keys, exhaustively: `held_out_auprc`, `held_out_auroc`,
`inner_auprc`, `phase1_history`, `phase2_history`, `scaler_inner`,
`scaler_outer`, `selected_epoch`, `wall_seconds`. Phase-1 epoch records contain
exactly `epoch`, `inner_auprc`, `seconds`, `train_loss`.

**No missing history was recreated by retraining.**

---

## 2. Six epoch-selection trajectories

**No preregistered descriptive rule for selection separation exists** in the
E11 plan or its amendments. Per the audit constraint, **continuous margins are
reported and no categorical threshold is introduced.** The words
"strongly/weakly/tied" are therefore not applied as defined categories below;
the margins are given and the reader may judge them.

| fold | arm | epochs | selected | best | best epoch | second-best | **margin** | full range |
|---|---|---|---|---|---|---|---|---|
| 0 | B0 | 5 | 1 | 0.4128 | 1 | 0.3941 | **+0.0187** | 0.0618 |
| 0 | B1 | 5 | 1 | 0.4606 | 1 | 0.3835 | **+0.0771** | 0.1890 |
| 1 | B0 | 5 | 1 | 0.3091 | 1 | 0.2984 | **+0.0108** | 0.1171 |
| 1 | B1 | 6 | 2 | 0.3275 | 2 | 0.3272 | **+0.0003** | 0.0833 |
| 2 | B0 | 8 | **4** | 0.2519 | 4 | 0.2079 | **+0.0440** | 0.1255 |
| 2 | B1 | 5 | 1 | 0.2612 | 1 | 0.2399 | **+0.0212** | 0.0597 |

Full AUPRC-by-epoch trajectories:

```
fold 0 B0   ep1 .4128  ep2 .3912  ep3 .3570  ep4 .3510  ep5 .3941
fold 0 B1   ep1 .4606  ep2 .3835  ep3 .3443  ep4 .2715  ep5 .3810
fold 1 B0   ep1 .3091  ep2 .2847  ep3 .2369  ep4 .2984  ep5 .1920
fold 1 B1   ep1 .2957  ep2 .3275  ep3 .3272  ep4 .3145  ep5 .2442  ep6 .2665
fold 2 B0   ep1 .1842  ep2 .1701  ep3 .1638  ep4 .2519  ep5 .1264  ep6 .1750  ep7 .2079  ep8 .1792
fold 2 B1   ep1 .2612  ep2 .2399  ep3 .2021  ep4 .2083  ep5 .2015
```

**Fold 1 B1's margin is +0.00029213** — epoch 2 at 0.327467519 against epoch 3
at 0.327175392. That is 292× the `EARLY_STOPPING_DELTA` of 1e-6, so the rule
fired correctly and lawfully, but the two epochs are separated by three
ten-thousandths of AUPRC. **The selected epoch in that fit is not meaningfully
distinguished from its runner-up by the selection statistic.**

**Trajectories are non-monotone and non-unimodal.** Fold 2 B0 falls for three
epochs, peaks at epoch 4, collapses to its global minimum at epoch 5, then
rises again to its second-best at epoch 7. Fold 0 B0 and fold 1 B0 both reach
their second-best value at their *final* epoch after a monotone decline.

**No selected epoch was changed.**

---

## 3. B0/B1 training dynamics

Within-fold, descriptive:

| fold | B0 selected | B1 selected | B0 epochs run | B1 epochs run | direction of divergence |
|---|---|---|---|---|---|
| 0 | 1 | 1 | 5 | 5 | none — identical selection |
| 1 | 1 | **2** | 5 | 6 | B1 selected **later** |
| 2 | **4** | 1 | 8 | 5 | B1 selected **earlier** |

**The arms diverge in opposite directions on different folds.** In fold 1, B1
ran one epoch longer and selected later; in fold 2, B0 ran three epochs longer
and selected epoch 4 while B1 selected epoch 1. **There is no consistent
"B1 trains differently" signal** in the persisted histories — the pattern is
consistent with fold-level variation in a noisy selection statistic rather than
with a systematic effect of the auxiliary term.

**Four of six fits selected epoch 1**, reproducing the
overfit-within-2-4-epochs signature E2 documented for this recipe. **Most of
the E11 contrast is therefore between one-epoch encoders.** This is a property
of the frozen B4-B recipe, not of E11 and not of the auxiliary objective.

**Total training loss falls monotonically in all six fits, without exception**,
while inner AUPRC does not. The two quantities are moving in unrelated
directions from epoch 2 onward in every fit.

---

## 4. Auxiliary-loss maturity

### **UNOBSERVABLE.**

The registered question — at the epoch selected by inner AUPRC, was the
auxiliary task already approximately stable, still materially changing, or
unobservable? — **resolves to UNOBSERVABLE, and no inference is drawn.**

The runner accumulated `tot += float(loss.detach()) * lb.numel()` on the
**combined** objective. For B1 that scalar is `BCE + λ·smoothL1`, summed. The
auxiliary term was never separated, never logged, and no morphology metric was
computed. **There is no auxiliary-loss trajectory, no relative-change series,
and no morphology metric series to report.**

**The one adjacent observable, reported with its confound stated.** Under A3
pairing, B0 and B1 begin each fit from byte-identical weights. Their epoch-1
total losses therefore differ initially only by the auxiliary term:

| fold | B0 epoch-1 total loss | B1 epoch-1 total loss | difference |
|---|---|---|---|
| 0 | 0.19608 | 0.20448 | **+0.00840** |
| 1 | 0.22072 | 0.22895 | **+0.00823** |
| 2 | 0.21955 | 0.22973 | **+0.01018** |

**This does not measure auxiliary maturity and is not used as if it did.** The
difference is accumulated across a full epoch during which the two arms' weights
diverge from the first optimizer step (A3), so the BCE components are no longer
comparable by the end of epoch 1. The quantity is recorded only to state that
the auxiliary term's contribution to the total objective is **small and of
consistent sign across folds** at λ = 0.1, and for no other purpose.

**No inference is made that a later epoch would have performed better on any
outer fold.**

---

## 5. Inner-distribution and metric-ordering disagreement

### 5.1 Registered inner-split prevalences

Recomputed read-only from the frozen split under the registered inner rule:

| fold | inner-train prevalence | inner-train n | inner-val prevalence | inner-val n | inner-val positives | ratio |
|---|---|---|---|---|---|---|
| 0 | 0.2510 | 195,043 | **0.0300** | 30,367 | 911 | **8.4×** |
| 1 | 0.2748 | 225,626 | **0.0246** | 30,198 | 742 | **11.2×** |
| 2 | 0.3039 | 243,449 | **0.0251** | 24,221 | 607 | **12.1×** |

**Inner-validation prevalence is 8.4× to 12.1× lower than inner-train**, and
the selection statistic rests on **607 to 911 positive windows**. This was
preregistered and retained deliberately, and was explicitly **not** asserted to
be harmless.

**No prevalence-adjusted AUPRC was computed and no replacement metric was
introduced.**

### 5.2 Epoch-to-epoch movement against the preregistered E2 reference

E11 §3.3 records, *before any E11 outcome existed*, that E2 measured
argmax-over-epochs bias at **+0.032** and epoch-to-epoch validation spread up to
**0.117**. Those are the only pre-existing reference values, and they are used
here as documented reference points rather than as thresholds.

| fold | arm | margin | margin < E2 bias (0.032) | full range | range vs E2 spread (0.117) |
|---|---|---|---|---|---|
| 0 | B0 | 0.0187 | **yes** | 0.0618 | within |
| 0 | B1 | 0.0771 | no | 0.1890 | **exceeds** |
| 1 | B0 | 0.0108 | **yes** | 0.1171 | **exceeds** |
| 1 | B1 | 0.0003 | **yes** | 0.0833 | within |
| 2 | B0 | 0.0440 | no | 0.1255 | **exceeds** |
| 2 | B1 | 0.0212 | **yes** | 0.0597 | within |

**In four of six fits the winning margin is smaller than the documented bias of
the selection procedure itself. In three of six the epoch-to-epoch range
exceeds the documented E2 spread.**

### 5.3 Metric-ordering disagreement

| fold | arm | AUPRC-selected epoch | loss-optimal epoch | loss monotone falling | verdict |
|---|---|---|---|---|---|
| 0 | B0 | 1 | 5 | yes | **DISAGREE** |
| 0 | B1 | 1 | 5 | yes | **DISAGREE** |
| 1 | B0 | 1 | 5 | yes | **DISAGREE** |
| 1 | B1 | 2 | 6 | yes | **DISAGREE** |
| 2 | B0 | 4 | 8 | yes | **DISAGREE** |
| 2 | B1 | 1 | 5 | yes | **DISAGREE** |

**Six of six disagree.** Because training loss falls monotonically in every
fit, the loss-optimal epoch is always the final epoch, which is never the
AUPRC-selected epoch. **AUROC ordering is UNOBSERVABLE** — inner AUROC was
never computed.

**This is diagnostic only. No AUROC-optimal or loss-optimal epoch was
retrospectively selected, and the registered AUPRC rule stands unaltered.**

---

## 6. Representation-geometry trajectory

### **UNAVAILABLE.**

Geometry-by-epoch **cannot be characterised from persisted artifacts.** No
phase-1 checkpoint, per-epoch embedding, or per-epoch prediction exists. A
filesystem search across both the preserved run root and the original scratch
directory for `*.pt`, `*.pth`, `*.ckpt` and any per-epoch artifact returned
nothing, and the runner contains a single `savez_compressed` call which writes
the **post-phase-2** representation only.

The six preserved `.npz` files each contain `emb_ho`, `score_ho`, `emb_ot`,
`idx_ho`, `idx_ot` for the **final** model of that fold and arm. **They
represent one point in training, not a trajectory.**

Accordingly: no outer-held-out subject was scored at any alternative epoch, no
different checkpoint was selected, and no discarded checkpoint was regenerated
through training.

---

## 7. Fold-2 B1 diagnostic

The registered observation is that B1's fold-2 consensus contains one
negative-cosine **TRAIN-side** stream: `s20471:1`, subject s2047,
`cos = −0.4625`, `‖delta‖ = 2.582`, 2,917 windows of which **12 are positive**.

**Whether this appears throughout training is UNOBSERVABLE.** It is observable
**only at the selected/final representation**, because that is the only
representation that was persisted. There is no phase-1 embedding from which the
stream's direction at any earlier epoch could be recovered, and regenerating one
would require retraining, which this audit does not do.

**This stream is not promoted into a primary estimand.** It remains an observed
secondary diagnostic, as recorded in the E11 report §5.3, and E11's result
category is unaffected.

---

## 8. Interpretation

**Established by this audit:**

1. **The checkpoint-selection instrument is demonstrably weak.** Four of six
   winning margins fall below the documented argmax bias of the selection
   procedure itself; one margin is +0.0003; trajectories are non-monotone and
   non-unimodal; the selection statistic rests on 607–911 positives at a
   prevalence 8–12× below inner-train; and AUPRC ordering disagrees with loss
   ordering in six of six fits.
2. **Four of six fits selected epoch 1**, so most of the E11 contrast is between
   one-epoch encoders — a property of the frozen recipe.
3. **B0 and B1 diverge in opposite directions across folds**, with no consistent
   arm-level training-dynamics signal.

**Not established, and not inferable from persisted evidence:**

4. **Whether the morphology auxiliary objective was mature, still evolving, or
   inert at the selected epochs.** The auxiliary loss was never separately
   logged. This is the decisive unknown.
5. **Whether representation geometry was still changing across epochs.** No
   per-epoch representation exists.

**What this means for the E11 null.** The audit **refutes** the reading that
E11's Category C arose under a stable, mature selection regime — the regime was
not stable. It **cannot confirm** the competing reading that the auxiliary
objective was still materially evolving when selection cut training short,
because the quantity that would show this was never persisted.

**The E11 null is therefore neither strengthened nor overturned by this audit.**
It is bounded: E11 tested a morphology-aware auxiliary objective **as delivered
through a demonstrably noisy early-selection regime**, and the persisted
evidence cannot separate a weak objective from a weak delivery mechanism.
**E11's Category C classification stands unmodified.**

---

## 9. Next-question recommendation

### **DECISION: C — NO FURTHER CONCLUSION.**

The decision rule requires both clauses of A or both clauses of B.

- **B is affirmatively REFUTED** on its first clause: checkpoint selection is
  demonstrably **not** stable.
- **A cannot be CONFIRMED**: its first clause is established, but its second
  clause — the auxiliary objective still materially evolving at selected
  epochs — is **UNOBSERVABLE**.

With A unconfirmable and B refuted, the persisted evidence **cannot distinguish
the two explanations**, which is precisely the condition for **C**.

**The asymmetry matters and should be recorded.** C is returned here **not
because the evidence is scientifically ambiguous, but because one scalar per
epoch was never written to disk.** The selection-instrument finding is strong
and stands on its own; only the auxiliary-maturity half is dark.

**The implied next step is a persistence fix, not an experiment.** Any future
E11-class runner should log, per epoch and per arm: the **primary loss and the
auxiliary loss as separate terms**, an inner-validation **AUROC** alongside
AUPRC, and — if geometry trajectory is ever to be answerable — a per-epoch
inner-validation embedding or a phase-1 checkpoint. **This is the same class of
defect as the E11 report §9.1 operating-point gap: the experiment was run
correctly and under-instrumented.** Neither gap requires a new authorization to
fix; both require the fix to precede the next authorization.

**Explicitly not recommended**, per the audit constraints and A5: a **λ sweep**;
a **second morphology target**; any use of the **historical VALIDATION**
partition; any **sealed TEST** access; and any **retrospective outer-fold
checkpoint selection**. None of these follows from anything in this audit, and
the λ = 0.1 null is not a reason to try another λ.

**No training was performed. No new scientific outcome was derived from any
outer-held-out fold. E11 is unmodified.**
