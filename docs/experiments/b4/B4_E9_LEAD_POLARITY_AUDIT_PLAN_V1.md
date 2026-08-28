# B4 · E9 Lead / Polarity / Label-Semantics Audit — Preregistered Plan, V1

**Read-only. No retraining, no corrective model, no sealed-test artifact and no
test header opened. Development data only.** §1 is the audit, completed
**before** any mechanism outcome was computed. §3 onward is the
pre-registration.

---

## 1. Audit

### 1.1 LABEL SEMANTICS — labels are **channel-specific**, and **polarity-agnostic**

Traced from source to cache:

```
LTSTDB .stb annotation      e.g.  (st1-  …  ast1-140  …  st1-)
        │                          ^^^ lead index 0-2, and a SIGNED deviation
        ├─ ltstdb.parse_annotations  → STEvent(lead:int, direction, peak_deviation_uv, …)
        │      `_direction(v)` = "elevation" if v > 0 else "depression"
        ├─ targets.assign_window_target  → filters events by `_same_lead(window, event.lead)`
        └─ window cache `target_families` → {ischemic_positive, background_negative}
```

**`STEvent.lead` is `int`, never optional**, and every `.stb` regex captures
`(?P<lead>[0-2])`. Window targets are filtered by `_same_lead`, so **episodes
annotated on one lead do not label the other.** Labels are **not broadcast**.

**But the binary target collapses ST direction.** `direction` and
`peak_deviation_uv` exist on `STEvent` and are **discarded** when the target is
reduced to `ischemic_positive`. **Elevation episodes and depression episodes
receive the identical positive label.**

**Answer to the explicit question:** two channels with reciprocal ST morphology
**can** both be labelled positive — not because a label is broadcast, but
because each lead is annotated on its own and the binary target is
polarity-agnostic. **Confirmed in the motivating record:**

| `s20311` | lead 0 (MLIII) | lead 1 (V3) |
|---|---|---|
| ischemic **elevation** | **8** | 2 |
| ischemic **depression** | **0** | **8** |
| heart-rate-related elevation | 3 | 26 |

**A detector must therefore be polarity-invariant to score both channels
correctly.** This is a **target-definition property**, not a model defect, and
§5 keeps it as a separate candidate mechanism.

### 1.2 TRUE LEAD IDENTITY — recovered, with a residual gap

Read from WFDB headers for **all 73 development records**; **the 13 test records
were enumerated only to exclude them and were never opened.**
**162 `(record_id, channel_index)` entries** mapped, zero read failures.

| lead | channels | | lead | channels |
|---|---|---|---|---|
| **ECG** *(generic)* | **42** | | V5 | 4 |
| MLIII | 22 | | V3 | 2 |
| V4 | 20 | | V2 | 2 |
| ML2 | 13 | | II | 2 |
| MV2 | 13 | | V6 | 2 |
| E-S / A-S / A-I *(EASI)* | 13 each | | aVF | 1 |

**The degeneracy is not only in the feature corpus: 42 of 162 development
channels carry the generic name `ECG` in the WFDB header itself.** Those
channels have **no recoverable lead identity**, and any lead-identity analysis
must report them as a separate `UNKNOWN` stratum rather than pooling them.

### 1.3 SIGNED MORPHOLOGY — semantics and comparability

Eight signed features, all **baseline-relative in mV** against the median
waveform 200–80 ms before the detected R:

`post_r_{80,120,160,200}ms_delta_mv`, `post_r_80_160_slope_mv_per_s`,
`post_r_80_200_area_mv_s`, `pre_r_baseline_median_mv`,
`qrs_proxy_peak_to_peak_mv`.

- **Sign is preserved and physiologically meaningful**: positive = ST elevation
  relative to baseline, negative = depression.
- **Magnitude is NOT comparable across lead types.** These are raw-profile mV on
  differently placed electrodes with differing gain; `processing_profile: raw`,
  no amplitude normalisation. **E9 therefore compares sign and within-stream
  contrasts, never raw magnitude across leads.**
- Provenance: schema `morphology_v1` sha256 `13f60be400b5b957c1eb592b…`,
  annotation definition `ltstdb.stb`.

### 1.4 TRAIN→VALIDATION structure

TRAIN B4 scores are **not persisted**. They are **exactly reproducible**: E8b
verified `representation.npy`'s 128-d prefix equals the frozen embedding cache,
and `forward = classifier.head(encode(x))`.

**Registered reproduction procedure, in this order:**
1. Reproduce **validation** scores by `classifier.head(embedding)` and assert
   agreement with `validation_predictions.npz` to float32 tolerance — the E1 A0
   gate, re-run.
2. **Only if that passes**, apply the identical path to TRAIN.

**This is a head-only forward pass over frozen cached embeddings. No encoder is
invoked, nothing is trained, no label is used.** If step 1 fails, E9's TRAIN
arm stops and only the validation description is reported.

Labels for TRAIN come from `target_families == "ischemic_positive"`; **the
identity of that mapping is asserted against validation's `label` column
first.**

---

## 2. Discipline

**No correction rule is derived from VALIDATION and evaluated on VALIDATION.**
Mechanism characterisation is performed on **TRAIN (56 subjects)**; VALIDATION
(12 subjects) is used **only** to check reproduction. Any relationship reported
as reproducing must have been stated from TRAIN first.

---

## 3. Primary analysis A — per-stream description

For every development stream with defined discrimination: true lead (or
`UNKNOWN`), window count, prevalence, B4 AUROC, positive−negative score
separation, signed ST-direction summaries (median `post_r_120ms_delta_mv` and
`post_r_80_200_area_mv_s` for positives and negatives **separately**), SQI
summaries (the six G3 columns), and M2 admission fraction where available.

**Episode-level direction mix** is added from `.stb`: the fraction of that
lead's **ischemic** episodes annotated as depression.

## 4. Analysis B — association with failure

Whether low or inverted B4 discrimination associates with (i) reversed ST
direction, (ii) weak ST magnitude, (iii) poor SQI, (iv) lead identity, (v)
channel-level label/direction mismatch. **Spearman only, no fitting**, with n
stated. **Stated from TRAIN, checked on VALIDATION.**

## 5. Analysis E — four mechanisms kept separate

Registered as **four distinct hypotheses that are not collapsed**:

| # | Mechanism | Operational signature |
|---|---|---|
| **M-pol** | polarity / sign reversal | ischemic-episode depression fraction, and sign of positive-minus-negative ST delta |
| **M-inf** | weak lead informativeness | small \|ST delta\| contrast between classes, with acceptable SQI |
| **M-sqi** | signal-quality degradation | G3 column excursions, low admission fraction |
| **M-sem** | label / lead semantic mismatch | a lead labelled positive while its own signed morphology shows the opposite direction from the co-recorded lead |

**A stream may exhibit more than one. No composite "bad stream" score is
formed**, and no mechanism is declared dominant on the basis of a single case.

## 6. Analysis C — within-subject paired

For multi-stream subjects, contrasts are computed **within subject**, so
subject-level nuisance (prevalence, burden, recording device) is differenced
out. **9 of 12 validation subjects own ≥ 2 streams; all TRAIN subjects likewise
have ≥ 2 channels.**

## 7. Analysis D — `s2031` as motivating case only

Reported explicitly and **excluded from every pooled estimate** so it cannot
drive the result it motivated.

---

## 8. Registered predictions

1. **The ischemic depression fraction will differ between co-recorded leads** in
   a substantial minority of multi-channel records.
2. **Streams whose ischemic episodes are predominantly depression will show
   lower B4 AUROC** than their co-recorded sibling. *This is M-pol and the core
   claim.*
3. **SQI will not explain the extreme failures.** E8a found `s20311:1`'s
   distances unremarkable; if its G3 columns are also unremarkable, M-sqi is not
   the mechanism there.
4. **`UNKNOWN`-lead channels (42 of 162) will not differ systematically** —
   generic naming is a documentation artifact, not a physiological one.
5. **The relationship will be weaker on VALIDATION than TRAIN**, because n = 30
   streams and E6a applies.

## 9. Interpretation rules

| Outcome | Recommendation |
|---|---|
| Polarity / lead semantics track failures **and reproduce TRAIN→VALIDATION** | Recommend a preregistered **E9b lead-aware or polarity-aware representation experiment** |
| **SQI** explains failures instead | Recommend **quality-aware modelling**, not representation polarity changes |
| **Label semantics inconsistent across channels** | Treat first as a **target-definition problem**, not model capacity |
| **Nothing reproduces beyond isolated subjects** | **Close this mechanism**; return to M1 incremental value or broader representation learning |

**Bounds.** Mechanism evidence only. Development only. No sealed generalization
claim is available, permanently.
