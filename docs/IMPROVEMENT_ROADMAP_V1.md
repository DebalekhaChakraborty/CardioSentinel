# Improvement Roadmap, V1

**This document grants no scientific permission and authorizes no execution.**
Every experiment named here requires its own pre-registration and its own human
authorization before anything runs, exactly as T1, T2, U1 and W1 each did. It
is a plan, not a licence.

**It is downstream of a post-hoc analysis and inherits that status.** The
diagnosis it acts on is `docs/B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md`, written
after the sealed-test values were read. Nothing here may be used to revise a
pre-registered claim, a reported number, or any thesis in §9.

| | |
|---|---|
| Class | forward plan, post-hoc derived |
| Authorizes | **nothing** |
| Supersedes | nothing |
| Depends on | `B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md` |

---

## 0. The constraint that shapes every option

**Within LTSTDB there is no held-out partition left, permanently.**

- Both sealed chains are consumed: B0–B3 in Phase 3B-1, B4/neural on 2026-08-25.
  Handbook §51 — fifteen of fifteen budgets spent.
- Test subjects are consumed. Train and validation subjects have all been used
  for selection.
- **Re-splitting LTSTDB produces a contaminated partition, not a fresh one.**
- The one route to a corroborating cohort, EDB `overlap_clean`, was **declined
  in writing** on 2026-08-24. Its §2.4 records that no second cohort will
  corroborate any result in this paper, permanently.

| Ambition | Available |
|---|---|
| Understand and fix the mechanism | **Yes** |
| Demonstrate a fix, as development evidence | **Yes** |
| Claim improved held-out performance | **No — not on this dataset, at any effort level** |

**Plan against that honestly.** The failure mode of this roadmap is building
something genuinely better and being unable to say so, then saying so anyway.

---

## 1. Phase 0 — build the instrument before touching the model

**Entry gate:** none. **Exit gate:** the transfer instrument exists and has been
run once on the current B4-B.

**Do not start modelling.** The sealed-test failure was invisible beforehand
because the development instrument could not see it, and every fix below is
equally unmeasurable until that changes.

### 1.1 Why the current instrument cannot work

A single 12-subject validation draw estimates **performance**, not **transfer
variance**. The pooling penalty was 5.0% on one draw of twelve subjects and
73.6% on another. **One draw cannot reveal that the spread exists.**

### 1.2 The replacement — leave-subjects-out cross-fitting

Over the **68-subject development pool** (56 train + 12 validation; handbook
§42). For every future candidate, report:

| Metric | Why |
|---|---|
| Per-fold pooled **and** subject-macro AUPRC | Both, always, with denominators |
| **Pooling divergence** (macro − pooled) | Promote to a first-class reported metric. It *is* the failure, made visible |
| Distribution of per-subject score medians | Direct measurement of scale non-comparability |
| **Threshold-transfer penalty** — fit the F1-optimal cut on fold *k*, apply to fold *j*, tabulate the loss | The number this programme does not have |

**The threshold-transfer penalty would have predicted the sealed-test outcome
before the budget was spent.** Establishing that, and saying so in §9.7, is
worth more to the manuscript than any accuracy gain this roadmap could produce.

### 1.3 Phase 0's cheapest and most urgent measurement

**Measure M2-G's admission rate over full development recordings.**

`DEMO_SCENARIO.md` §2 records **0 memory updates admitted** over a 2,400 s
replay, with G4 and G5 blocking during the event. That is correct *during* an
event and the document says so. But **nobody has measured the admission rate
over a full recording**, and if it is near zero in general then the per-subject
state never populates and every personalization fix in Phase 2 is inert before
it starts.

One read-only pass over development data answers it. **Do this first**, because
it gates item 3 in §3.

---

## 2. The fix, in three tiers

The diagnosed defect: **the model learned a subject-relative decision function
and was evaluated with a subject-absolute threshold.**

### Tier 1 — inference-time, no retraining

Replace the subject-absolute cut.

- Maintain a per-subject running estimate of the score distribution over
  **M2-G-admitted** windows — label-free by construction, so no contamination.
- Decide on a per-subject quantile, or on `z = (s − μ_subject) / σ_subject`.
- **A cold-start policy is mandatory and must be explicit.** Until *N* admitted
  windows accumulate, fall back to the global boundary and stamp the decision
  `COLD_START` in provenance. **A silent fallback is the exact failure class
  this programme exists to prevent.**

**Sanctioned by the project's own standing constraints**, and this should be
quoted in the pre-registration because it will otherwise look like a violation:

> *Patient identity selects a state namespace and a calibrator; **never** a
> predictive feature.*

A per-subject baseline is calibrator selection, not a feature. And *"labels
never determine memory-stream membership, ordering or update eligibility"* is
satisfied because M2-G gates on appearance, not on labels.

**Highest value per unit of effort in this document, and it requires no
retraining.**

### Tier 2 — training-time, same architecture

Stop rewarding the shortcut that broke.

- **Subject-balanced batch construction**, so the loss cannot exploit
  cross-subject separability.
- **Within-subject contrastive or pairwise ranking objective** — anchor ischemic
  windows against *that subject's own* normals. This trains the contrast that
  survived (82–89% retained) instead of the one that did not.
- **Gradient reversal on subject identity**, to strip subject-identifying signal
  from the embedding. **State explicitly in the pre-registration that this is
  the inverse of identity-as-feature** — it removes identity rather than using
  it — or a reviewer skimming the constraint list will read it as a violation.

### Tier 3 — representation change

**Baseline-referenced encoding.** ST-segment ischemia is *clinically defined* as
deviation from the patient's own isoelectric baseline. The current model
receives absolute morphology and must learn that invariance from 56 subjects.
Give it architecturally instead: encode the window's deviation from a subject
reference beat.

The deepest fix, physiologically motivated rather than an ML trick, and it makes
the representation subject-relative **by construction** rather than by hope.

### Cross-cutting — endpoint alignment

The encoder was selected on **window-level** evidence; the paper reports
**episode-level**. M1L and M2-G were also selected at window level and never
evaluated at the episode endpoint — which is why **RQ1 is unanswered by
construction**, not by omission. **Select on the endpoint you report.**

---

## 3. Ranked interventions

| # | Intervention | Sci. value | Impact on the diagnosed defect | Effort | Paper value |
|---|---|:--:|:--:|:--:|:--:|
| 1 | Cross-fitted transfer instrument (§1.2) | ★★★★★ | enables everything | Low–Med | ★★★★★ |
| 2 | M2-G admission-rate measurement (§1.3) | ★★★★☆ | gates #3 | **Very low** | ★★★☆☆ |
| 3 | **Per-subject calibrator + subject-relative threshold** (Tier 1) | ★★★★★ | ★★★★★ | Medium | ★★★★★ |
| 4 | Within-subject contrastive / ranking objective (Tier 2) | ★★★★★ | ★★★★☆ | High | ★★★★☆ |
| 5 | Episode-endpoint selection for M1L / M2-G | ★★★★☆ | ★★★☆☆ | Medium | ★★★★☆ |
| 6 | Baseline-referenced encoding (Tier 3) | ★★★★★ | ★★★★★ | Very high | ★★★★☆ |
| 7 | Characterise the diffuse false positives, then mine them | ★★★☆☆ | ★★★☆☆ | Medium | ★★★☆☆ |
| 8 | Multi-cohort acquisition | ★★★★★ | ★★★★★ | **Blocked** | ★★★★☆ |
| 9 | Focal loss / class weighting | ★★☆☆☆ | ★☆☆☆☆ | Low | ★★☆☆☆ |
| 10 | Temporal context length | ★★☆☆☆ | ★☆☆☆☆ | Medium | ★★☆☆☆ |
| 11 | Alternative encoder / SSM improvements | ★☆☆☆☆ | ★☆☆☆☆ | High | ★☆☆☆☆ |

**Why 9–11 rank low against intuition, stated so nobody re-proposes them.**

- **Focal loss and class weighting attack imbalance.** Validation AUPRC showed
  **8.34× lift** over prevalence (0.380535 against 0.045639, post-hoc
  descriptive), so imbalance is not the binding constraint — transfer is.
- **Encoder and SSM work attacks within-subject ranking**, which is the part
  that mostly survived. It optimises the wrong term.
- **There is no established temporal gain to improve on.** T2's selection
  contrast interval **[−0.015229, 0.148951]** spans zero.

**Item 7 requires characterisation before mining.** The false positives moved
*out* of the confounder strata, so what they are is currently unknown. Mining an
uncharacterised population is guesswork.

**Item 8 is the highest-impact intervention and the one already established as
unavailable.** That asymmetry is the manuscript's strongest limitation argument
and should be written as one.

---

## 4. Phases and gates

### Phase 1 — manuscript completion. *Nothing is measured.*

1. **§2 Related Work.** Unstarted, blocks §9.3, bound by §6.3 of
   `B4_TEST_AUTHORIZATION_V1.md`: **it must not be shaped by the sealed-test
   result.**
2. Correct §7 to name what was scored — *B4-B window-level encoder,
   uncalibrated, frozen validation threshold* — not the architecture list.
3. Land `B4B_SEALED_TEST_POST_HOC_ANALYSIS_V1.md` as clearly-labelled post-hoc
   material.
4. Report the confounder-stratum result as a **positive finding**: robustness
   held on held-out subjects while the overall FP rate rose 44%.
5. Close `CURRENT_STATE.md` defects 7 and 9.

> **Exit gate: manuscript submitted.** Do not begin Phase 2 first. §2 carries a
> non-contamination condition whose integrity degrades the longer anyone sits
> with the failure analysis.

### Phase 2 — mechanism, not performance. *New authorizations required.*

Order: **§1.2 instrument → #2 → #3 → #5 → #4.** Each pre-registered separately.
Each reported as *"mechanism understood"*.

> **Exit gate: the pooling divergence is reduced under cross-fitting and you can
> say why.** Not *"AUPRC improved"* — no partition licenses that sentence.

### Phase 3 — a defensible performance claim becomes possible again

- Multi-cohort acquisition with a contamination audit completed **before data
  reaches disk** (handbook §42).
- A fresh sealed test on the new cohort, under a new one-shot budget.
- RQ5 on real edge hardware. A laptop replay is not an edge measurement.
- **The calibration and personalization layers promoted into the scored path**
  as first-class evaluated components, rather than downstream consumers of an
  artifact nobody tested them against. This is the direct lesson of §1 of the
  post-hoc analysis.

> **Entry gate: a cohort exists.** Until then Phase 3 is a plan, not a project.

---

## 5. What each phase may legitimately claim

| Phase | Permitted claim |
|---|---|
| 1 | *"We report what we measured, with the boundary fixed before we measured it."* |
| 2 | *"We identified the mechanism and demonstrated a fix under cross-fitted development evidence."* |
| 3 | *"On an independent cohort, the system achieves X."* — **the only phase that can say this** |

---

## 6. Prohibited, and why

| Action | Why it is prohibited |
|---|---|
| Re-score or re-threshold against test | The budget is consumed; `repeat_attempt_permitted: false` |
| Open `TEST_PREDICTIONS.npz` for unregistered per-subject analysis | Post-hoc analysis on test data that was never pre-registered |
| Choose among §3's items by their fit to the test outcome | Test-informed selection. The result is final evidence, not a tuning signal |
| Revise any §9 thesis, hedge or emphasis | §9.8 clause 1. §9 was merged 2026-08-24; the test ran 2026-08-25, and the ordering is the claim |
| Claim the assembled stack would have scored higher | Never measured; now unmeasurable. §1 of the post-hoc analysis |
| Let §2 be shaped by the failure analysis | §6.3 of the authorization |
| Relax the M1/P1 preflight gate to make the suite green | `CURRENT_STATE.md` defect 9. It fails closed by design; what it should say instead is a governance decision |
| Weaken `test_the_sealed_test_claim_matches_the_tree` | It is failing correctly. Make the claim true instead |

---

## 7. Next action

**Write §2 Related Work.**

It is the only unstarted item in the paper plan, it blocks §9.3, and it carries
a condition that gets harder to honour the longer anyone holds this analysis in
mind. Everything in Phase 2 can wait; §2 is the single task whose integrity
degrades with delay.

**After submission**, Phase 2 opens with the two cheapest items in this
document: build the cross-fitted transfer instrument, and measure M2-G's
admission rate. Neither trains anything, both are read-only over development
data, and together they determine whether the per-subject calibrator — the
highest-leverage build here — is viable at all.
