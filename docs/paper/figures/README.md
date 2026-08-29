# Evidence visualizations — provenance and reproduction

**Assembly and plotting only. No figure computes a new scientific quantity.**
Every value plotted traces to a frozen report or a promoted run artifact.

Regenerate with:

```
venvs/tactics/bin/python docs/paper/figures/make_f3_f4.py      # data figures
venvs/tactics/bin/python docs/paper/figures/make_f1_f2_f5.py   # diagrams
```

Outputs vector `.pdf` and `.png` at 200 dpi.

## Palette

`#2a78d6` (blue) / `#eb6834` (orange), validated colourblind-safe on the light
surface `#fcfcfb`:

```
Lightness band      PASS   both inside L 0.43–0.77
Chroma floor        PASS   both >= 0.1
CVD separation      PASS   dE 24.7 (protan) · 32.7 (tritan)
Normal-vision floor PASS   dE 33.6
Contrast vs surface PASS   both >= 3:1
```

**Identity is never carried by colour alone** — each series also has its own
marker shape (circle vs square in F3, circle vs diamond in F4), so the figures
survive greyscale printing and colour-vision deficiency.

## F3 · Episode reasoning vs the memoryless comparator

**Source:** `docs/experiments/w1/W1_WINDOW_COMPARATOR_REPORT_V1.md` §3 per-subject table, read
verbatim; subject-macro values and the paired interval from the same report and
`docs/T1_DESCRIPTIVE_REPORT_V1.md`.

- **(a)** paired per-subject episode `F_1`, 12 held-out subjects, sorted by T1.
  Reference-episode counts are printed beside each subject id.
- **(b)** subject-macro difference **0.1921**, 95% paired subject bootstrap
  **[0.0505, 0.3455]**.

**Two things the figure is built to show rather than hide.** The **seven
subjects scoring zero** are plotted at zero, not dropped — three have no
reference episodes and four are genuine misses, and the two groups push the
operating point in opposite directions. Where both arms score zero the orange
square is drawn larger with the blue circle nested inside it, so a coincident
pair reads as *both arms here*, not as a missing marker. And **`s2059` is the
one subject where the memoryless rule scores higher** (0.0417 vs 0.0000); it is
visible in panel (a) and is the reason the per-subject panel exists at all.

## F4 · Representation geometry and its failure minority

**Source:** E11 ATTEMPT 2 B0 held-out artifacts
(`cardiosentinel-runs/b4-e11-morphology-aware-v1/E11_ATTEMPT_2/artifacts/`) and
each fold's frozen B0 outer-train consensus, rebuilt with the registered E10
aggregation (`class_direction_consensus`). This is the **same estimand** E11's
outer geometry already reported in summary form, plotted at per-stream
granularity.

- **(a)** cosine to the fold consensus, outer-train (**158** streams across the
  three folds, **0 negative**) against outer-held-out (**79** streams,
  **3 negative**).
- **(b)** `‖delta‖` against cosine for the 79 held-out streams, with the three
  negative-direction streams marked by shape and labelled.

**The asymmetry is the finding.** Direction is essentially never reversed on
training streams and reverses on a small minority of unseen ones.

## F1 · CardioSentinel as an intelligent physical system

**Source:** handbook §52 (the four layers verbatim) and §52.1 (the train/runtime
equivalence audit). Layer bands carry the component names; the grey line under
each carries the evidence that constrains it — **18 of 25** Appendix A claims
machine-checked, **35 nodes / 39 edges** per alert, **~61×** real time,
**4.161 ms/window** median.

The orange band is the part a careful reader will press on: the bridge between the
trained pipeline and the running one. **Physiology half bit-exact at
`0.000e+00` on 64 of 64 audited rows; embedding half max `7.15e-07` = 6 ULP of
float32.**

## F2 · Partition authority and the one-way spend of evidence

**Source:** handbook v1.5 §3–§4, `DATA_SPLIT_POLICY.md`, and the E13a
consumption record.

Three partitions, each with its authority and its consumption state, and a
one-way arrow that never reverses. **TRAIN** is the only partition a future
experiment may use; inside it the E11 prospective split is marked with the
geometry population **consumed 2026-08-28**. **VALIDATION** is spent for
confirmatory purposes. **TEST** was consumed once on 2026-08-25 and cannot be
reopened.

**This is the figure that carries the governance contribution**, and the reason
it is a figure rather than a sentence is the nesting: a population *inside* a
still-usable partition can itself be spent, and that is hard to say in prose.

## F5 · A fluent generation that three gates passed and the fourth refused

**Source:** `EXPLANATION_EVALUATION_REPORT_V1.md` §2, §4, §4.1, §4.2.

Left to right: the generation, three gates it passed — **evidence fidelity
1.000**, **claim violations 0**, **completeness 1.000** — and the runtime gate
that **refused** it, switching the delivered output to `DETERMINISTIC`.

The panel beneath is the actual contradiction: the generation asserted *"the
G1–G6 range passed"* where the evidence records **G4 and G5 BLOCKED**. Two
qualifiers are drawn into the figure rather than left to the caption, because
the figure is misleading without them: the harness calls `provider.generate()`
directly so **no runtime gate runs during evaluation** — the three PASS scores
describe raw output, not what a user receives — and the inversion **reproduced
on two independent runs**.

Status colours are reserved (green pass / red refusal) and each ships with a
text label, never colour alone.

## Not drawn

**F6** streaming throughput and gate admission. It rests on two measured values
(**~61×** real time; **0 of 1079** windows admitted on `s20201`, G5 refractory
dominating) and a figure may not earn the space over a sentence. **Recommend
deciding this against the final §9 draft rather than drawing it speculatively.**

## Layout discipline

`make_f1_f2_f5.py` never hand-positions text. `panel()` stacks wrapped lines
from the top of a box using the font metrics, so a string that grows cannot
silently escape its frame. **All three diagrams failed exactly that way on the
first two passes** — text over box edges, labels over data points, a clipped
title — which is why the layout is computed rather than tuned by eye.
