# B4 · E8a Representation-Space Memory Mechanism Analysis — Report, V1

Executed under `B4_E8A_MEMORY_MECHANISM_PLAN_V1.md`. **Development validation
only, read-only. No retraining, no model loaded, no sealed artifact, no
threshold optimized, no classifier fitted, no score transformed.**
**Mechanism evidence only.**

**Headline, and it is a split verdict.** Memory quantities **do** identify
unreliable **windows** — broadly, across 8 of 9 subjects, with a coherent and
label-conditioned mechanism. They **do not** identify unreliable **streams**:
the correlation between upper-tail `d_long` and stream AUROC is **−0.028**, and
the polarity-reversed stream E7b found is **not** flagged by any distance. The
one quantity that does track stream quality is **M2-G's admission fraction**
(ρ = +0.682), which is a gate statistic, not a memory distance — and which is
confounded with signal quality.

**Recommendation: (2) — separate the M1 and M2 questions.** §7.

---

## 1. Provenance gate — PASSED

`ordered_chronology_sha256` recomputed from the persisted arrays equals the
manifest value `89f0b08bcd518fe0017c50bac0e198a1d9b61bc69fc1e3c6e06c148bbcb6960f`,
and **30 of 30 streams are strictly chronological in the persisted array order**
— unlike the B4 arrays, where E7b found 0 of 30. Causality is proven from an
order-sensitive digest, **not inferred from file order**, as required.

M1 and M2-G row evidence are element-wise identical in `stable_id` order; B4 is
a strict subset (473,897 of 492,904). **Zero non-finite memory rows** in the
scored subset. All analyses below use the 473,897-row intersection; **9 of 12
subjects are evaluable.**

---

## 2. A · Window-level error association

At the frozen threshold `0.7554003000259399` — never re-derived.

| group | n | `d_long` median [IQR] | `d_short` median | disagreement median | admitted rate |
|---|---|---|---|---|---|
| **TN** | 432,887 | 0.377 [0.288, 0.499] | 0.308 | 0.172 | 0.2462 |
| **FP** | 19,382 | 0.506 [0.367, 0.733] | 0.367 | 0.227 | **0.0000** |
| **FN** | 11,664 | 0.564 [0.409, 0.773] | 0.479 | 0.328 | 0.0007 |
| **TP** | 9,964 | **1.215** [0.898, 1.510] | 0.529 | 0.771 | **0.0000** |

**Rank concordance** (0.5 = no association):

| contrast | `d_long` | `d_short` | disagreement |
|---|---|---|---|
| incorrect vs correct | **0.6908** | 0.6636 | 0.6576 |
| FP vs TN | 0.6808 | 0.6106 | 0.6212 |
| **FN vs TP** | **0.1264** | 0.4362 | 0.1996 |

**Errors sit further from the patient's own prototype than correct windows.**
But the FN/TP contrast is the informative one and it runs the other way:
**false negatives sit far *closer* to baseline than true positives** — median
`d_long` 0.564 against 1.215.

**The mechanism is coherent: memory distance measures atypicality, and B4
detects the atypical positives while missing the typical-looking ones.**

**The effect is broad, not concentrated.** Per-subject `incorrect vs correct`
concordance on `d_long`:

```
s2058 0.985  s3072 0.971  s2019 0.915  s2059 0.889  s2057 0.841
s3073 0.743  s3068 0.668  s2004 0.606  s2031 0.519
```

**Eight of nine subjects exceed 0.60.** The concentration test does **not**
fire. The single near-chance subject is **s2031** — the subject that owns E7b's
polarity-reversed stream.

---

## 3. B · Label-conditioned behaviour

| label | n | ρ(B4 score, `d_long`) | ρ(score, `d_short`) | ρ(score, disagreement) | admitted |
|---|---|---|---|---|---|
| **positive** | 21,628 | **+0.727** | +0.169 | +0.542 | 0.0004 |
| **negative** | 452,269 | +0.102 | +0.160 | +0.112 | 0.2357 |

**Within positives, B4's score tracks memory distance strongly (ρ = 0.727);
within negatives it barely does (ρ = 0.102).** Conditioning on the label
separately is what makes this interpretable — a pooled correlation would be
prevalence-confounded.

**This is the same finding as §2 from the other direction.** B4 scores an
ischemic window highly *to the extent that the window is unlike that patient's
own recent baseline*. A genuine ischemic window that resembles the patient's
baseline receives a low score.

---

## 4. C · Stream-quality analysis — the mechanism fails here

Spearman across the **19 streams carrying both classes** (nested within 9
subjects, so n = 19 overstates independence):

| quantity | vs stream AUROC | vs separation |
|---|---|---|
| median `d_short` | −0.398 | −0.282 |
| p90 `d_short` | −0.209 | +0.018 |
| median `d_long` | −0.140 | −0.021 |
| **p90 `d_long`** | **−0.028** | +0.195 |
| median disagreement | +0.107 | +0.226 |
| **M2 admission fraction** | **+0.682** | +0.459 |

**Registered prediction 3 — that stream AUROC would correlate negatively with
upper-tail `d_long` — is refuted at −0.028.** Registered prediction 4 — that
admission fraction would *not* track quality — is **also refuted**, in the
opposite direction: it is the strongest correlate in the table.

### 4.1 The E7b failure stream, inspected as a case and not as the estimand

`s2031` owns two streams:

| stream | prevalence | AUROC | separation | admission | med `d_long` | p90 `d_long` |
|---|---|---|---|---|---|---|
| `s20311:0` | 0.0288 | **0.9413** | +0.4101 | **0.6425** | 0.4863 | 0.8412 |
| `s20311:1` | 0.0255 | **0.2119** | **−0.3163** | **0.0000** | 0.4176 | 0.6804 |

**The failing stream has *lower* memory distances than its healthy sibling.**
Memory distance does not merely fail to flag the polarity reversal — it points
the wrong way. **M2-G's admission fraction separates the two perfectly**
(0.0000 against 0.6425).

**A confound that must be stated before that is read as memory doing work.**
Admission embeds **G3**, a waveform signal-quality gate. A noisy lead can
produce both a low admission fraction and poor B4 discrimination through a
common cause, with no memory mechanism involved. **E8a cannot separate those**,
and the +0.682 must not be reported as evidence that memory identifies quality
failures.

---

## 5. D · M2 contamination mechanism

| | admitted | refused |
|---|---|---|
| windows | 106,586 | 367,311 |
| **B4 error rate** | **0.000075** | **0.084501** |
| prevalence | 0.000075 | 0.058860 |
| median B4 score | 0.000209 | 0.009104 |
| median `d_long` | 0.3597 | 0.3974 |

Full-stream admission rate **0.21844**.

**M2-G admits windows that are low-scoring, close to baseline, and almost never
positive.** It admits **zero** FP and **zero** TP (§2), i.e. essentially nothing
above the decision threshold — which is precisely what G4's normal-evidence
margin is for.

**Interpreted only as contamination control, as registered.** The near-zero
error rate among admitted windows is **not** a classification result: it is the
arithmetic consequence of refusing everything abnormal. **Nothing here says M2-G
improves detection, and this report makes no such claim.**

---

## 6. Registered predictions

| # | Prediction | Outcome |
|---|---|---|
| 1 | Errors at larger memory distances | **Confirmed** — 0.6908 on `d_long` |
| 2 | FP more distinctive than FN | **Confirmed** — FP vs TN 0.681; FN sit *below* TP at 0.126 |
| 3 | Stream AUROC ↔ upper-tail `d_long` negative | **REFUTED** — −0.028 |
| 4 | Admission fraction will not track stream quality | **REFUTED** — +0.682, the strongest correlate |
| 5 | Effects heterogeneous across subjects | **Partly refuted** — the window-level effect is broad (8/9), not concentrated |

---

## 7. Recommendation — **(2) separate the M1 and M2 questions**

Rule (1) required credible, non-concentrated evidence on **windows *and*
streams**. Windows pass; **streams fail**. Rule (3) required that neither
identifies anything; that is false. **Rule (2) is the one that fits**, and the
split runs along the M1/M2 seam:

- **M1 (`d_long`) — window-level mechanism evidence, no stream-level evidence.**
  It measures atypicality relative to a patient's own baseline, and B4's
  positive-class score is strongly coupled to it (ρ = 0.727). **The open M1
  question is about false negatives**: ischemic windows that resemble the
  patient's baseline.
- **M2-G — contamination-control evidence, plus a stream-quality correlate that
  is confounded.** The open M2 question is whether admission fraction tracks
  discrimination **beyond** what G3's signal-quality gate already explains.

**A joint M1L/M2-G ON-versus-OFF ablation should not be run first**, because the
two components have evidence about different objects and a joint ON/OFF would
confound them.

---

## 8. Read-only dependency audit for the future RQ1 ablation

### 8.1 Where memory features actually enter

| Consumer | What it consumes | Memory features? |
|---|---|---|
| **M1L** | 146-d representation **⊕ `d_long`** (a single scalar) | **yes — `d_long` only** |
| M1S / M1D | ⊕ `d_short` / ⊕ both | yes |
| **T2 / S4D** | `T2_INPUT_DIM = 146` = 128 embedding + 18 physiology | **NO** |
| T1 | `m2g_detector_score`, calibrated probability, S4D evidence | indirectly, via M2-G |

**T2 uses the M1 cache only as a chronologically ordered representation store
(`T2_INPUT_STORE_KIND = "m1_full_stream_memory_cache"`), not as a memory-feature
provider.** An "M1L OFF" arm is therefore **meaningless for T2** — T2 never had
memory features to remove.

### 8.2 Is a valid no-memory comparator available without retraining?

**Yes at window level, and it already exists.** `m1_selection.py` fixes
`GLOBAL_CONTROL_EXPERIMENT_ID = P1B_EXPERIMENT_ID` — **P1B is the registered
no-memory control**, and all four arms are on disk with the same 9/12
denominator:

| arm | pooled AUPRC | pooled AUROC | subject-macro AUPRC (9/12) |
|---|---|---|---|
| **P1B — no memory** | 0.375248 | 0.904506 | 0.409540 |
| **M1L — `d_long`** | 0.384796 | 0.907570 | 0.415833 |
| M1S — `d_short` | 0.365077 | 0.911717 | 0.415404 |
| M1D — both | 0.381417 | 0.912372 | 0.415817 |

**M1L − P1B = +0.009548 pooled AUPRC, +0.006293 subject-macro.** E6a measured
interval widths of ~0.11–0.16 for contrasts of this kind at n = 12. **This
difference is far inside the noise floor of the instrument**, and no ON/OFF
ablation on this cohort can resolve it.

### 8.3 What is *not* available without new work

| Need | Status |
|---|---|
| Aggregate M1 ON/OFF | ✅ on disk, read-only |
| **Per-row / paired-bootstrap M1 ON/OFF** | ❌ **P1B persists `VALIDATION_PREDICTIONS.npz`; no M1 arm does.** Requires loading `M1L…/model_selected.pt` and re-scoring — a forward pass, not retraining |
| Per-row M2-G ON/OFF | ❌ the M2-G store holds the **gated** score; the ungated per-row M1L score is not persisted. Same re-scoring requirement |
| **Episode-level (T1) ON/OFF** | ❌ **A scan of every `.npz` under `phase9-t1-*` finds no `label`, `target`, `episode` or `reference` column.** T1 opened held-out labels one fold at a time at run time and did not persist them. **Episode scoring requires re-opening held-out labels — a fresh human authorization** |

**So the RQ1 *episode* ablation the plan contemplates is not obtainable without
a new authorization**, and the window-level version that *is* obtainable is
measuring a difference the cohort cannot resolve.

---

## 9. Bounds

- **Mechanism evidence only.** Not development performance, not generalization.
- **9 of 12 subjects evaluable**; `s2005`, `s2020`, `s2023` carry no positives.
- **§4's stream statistics rest on 19 streams nested in 9 subjects** — not 19
  independent units. No stream contrast is bootstrapped.
- **§4.1's admission/quality relationship is confounded with G3 signal quality**
  and E8a cannot separate them.
- **Nothing here is a claim that memory improves detection.** M2-G's low
  admitted-error rate is a consequence of refusing abnormal windows, by design.
- The sealed test is consumed; no held-out estimate is obtainable within LTSTDB,
  permanently.
