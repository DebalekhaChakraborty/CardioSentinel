# B4 Sealed-Test Authorization V1 — **DRAFT, UNSIGNED, NOT IN FORCE**

> **This document does not authorize anything.** It is a drafted argument
> prepared for human review under the requirement set by
> `B4_TEST_DEFERRAL_DECISION_V1.md` §3, that any change to the deferral
> choreography "must be argued and recorded before any access, never assumed."
> It carries no digest and has not been through the freeze ritual. Until §6 is
> filled in by a human and this file is committed with a `_V1` freeze record,
> the operative decision remains **deferral**, and the B4 sealed test remains
> **unopened**.

| | |
|---|---|
| Prepared against | `master` `1ef7cf6`, working tree clean, 0 open PRs |
| Supersedes | nothing — `B4_TEST_DEFERRAL_DECISION_V1.md` remains in force |
| Sealed-test state at drafting | **UNOPENED**, `TEST_ATTEMPT.json` absent from the tree |
| Status | **DRAFT — authorization NOT granted** |

---

## 1. Background

### 1.1 What was deferred, and when

Phase 3B-2 architecture selection completed on validation evidence alone and
froze the global short-window encoder as **B4-B**
(`B4B_cnn_transformer_v1` / `B4BTransformerCNN`), recorded in
`docs/B4_GLOBAL_ENCODER_SELECTION_V1.md`
(SHA-256 `1300e7ad641df9137e1722771e5d3932cae0fc4d244047b7c8a5070f151f74bb`).

Under the Handbook choreography in force at that moment, one-shot sealed-test
access for the selected encoder became **eligible**. It was not taken.
`B4_TEST_DEFERRAL_DECISION_V1.md` recorded the refusal:

> B4-B sealed-test access is eligible but is intentionally **NOT authorized now**.

### 1.2 Why the deferral was scientifically correct

The stated reason was not caution for its own sake. It was a specific,
falsifiable claim about information flow:

> The remaining claim-bearing architecture still contains prospective
> development choices that are not yet frozen — physiology fusion (P1), patient
> memory (M1), contamination-safe adaptation (M2), calibration and selective
> routing, longitudinal temporal reasoning (T1/T2), episode logic.
>
> The sealed test draws on a fixed, small set of held-out subjects. Observing
> their outcomes now — even once, even only for B4-B — would put that
> information inside the design loop for every component listed above.

That reasoning was sound and remains sound. The test partition is **12 subjects,
13 records, 164 annotated ischemic episodes**. Against a design surface of six
unfrozen components, a single observation of those 12 subjects would have
contaminated every downstream choice, and no subsequent honesty about it could
have undone the contamination. **Deferring cost nothing; spending could not be
undone.** The decision was right when it was made, and this document does not
reinterpret it as excessive.

---

## 2. Changed research state

Every component named in §1.2 as "not yet frozen" now carries a recorded
retention decision, and none of them used test information.

| Component | Decision record | Outcome |
|---|---|---|
| P1 physiology fusion | `P1_PHYSIOLOGY_RETENTION_DECISION_V1.md` | RETAIN the frozen 18-dimension `morphology_v1` vector, with the rate-related FPR cost (+0.00603) recorded as a retained caveat |
| M1 patient memory | `M1_MEMORY_RETENTION_DECISION_V1.md` | RETAIN `M1L_long_memory_v2` |
| M2 contamination-safe update | `M2_UPDATE_POLICY_RETENTION_DECISION_V1.md` | RETAIN `M2-G` |
| U1 calibration / routing | `U1_CALIBRATION_ROUTING_RETENTION_DECISION_V1.md` | **Split** retention, with calibration's scope made explicit |
| T2 longitudinal temporal | `T2_LONGITUDINAL_TEMPORAL_RETENTION_DECISION_V1.md` | RETAIN the **continuous** score arm |
| T1 episode logic | `T1_DESCRIPTIVE_REPORT_V1.md`, `T1_POST_HOC_ANALYSIS_V1.md` | Canonical attempt CONSUMED — failed post-claim at stage 24, recovered under single-use authorization, measured and published |

Beyond the frozen science, the following were completed after the deferral:

- **IPS agentic runtime** — complete, tagged `ips-agentic-runtime-v1.0`. It
  senses, decides, explains, and refuses claims its evidence does not support.
- **Evidence graph** — `docs/EVIDENCE_MAP.md`.
- **Explanation layer** — `docs/EXPLANATION_EVALUATION_PROTOCOL.md`, with an
  evidence-constrained evaluation framework.
- **Architecture reasoning** — `B4_ARCHITECTURE_SELECTION_PROTOCOL_V1.md`,
  `B4_RESOURCE_BENCHMARK_V1.md`, `B4_VALIDATION_CHALLENGE_PROTOCOL_V1.md`,
  all resolved on validation evidence.
- **Reproducibility package** — `reproducibility/`, 27-file demo bundle with a
  per-file SHA-256 manifest, plus an offsite S3 mirror re-verified 2026-08-24
  (786 objects, Object Lock GOVERNANCE until 2027-08-22).
- **Manuscript preparation initiated** — `PAPER_OUTLINE_V2.md`. §2 Related Work
  and §9 Discussion do not yet exist as prose.

**The design surface the deferral was protecting no longer exists.** There is no
remaining component whose design a test observation could contaminate, because
there is no remaining component that is still being designed.

---

## 3. Scientific justification

### 3.1 The argument

The justification for opening B4 is **not** that the manuscript needs a number.
A paper that needs a specific result is a paper that will find one, and this
project has spent eleven months building machinery specifically to prevent that.
`PHASE3B1_CLASSICAL_BASELINE_RESULTS.md`, the T1 post-claim failure record, and
the T2 zero-spanning interval are all evidence that the programme reports what
it finds rather than what it wants.

The justification is a change in what the test measurement *is*:

> **The selected architecture has already been frozen. B4 is a final
> characterization of a locked system, not a model-selection activity.**

When the deferral was written, a test observation would have been an *input* —
one more signal feeding six open design decisions. That is what made it
dangerous. Today the same observation is an *output*: every architecture,
threshold, transform, preprocessing and routing choice is already fixed in
immutable locks, and no path exists by which a test number could flow backwards
into any of them.

### 3.2 Why the structure guarantees this rather than promising it

This is enforced by construction, not by discipline:

- `B4WindowReference` rejects the test partition **in its own validator**; test
  rows require the distinct `SealedTestWindowReference` type.
- No test-resolving function runs without a `SealedTestAccess` token, and the
  only issuer is `open_sealed_test_attempt`, which returns one **exclusively
  after `TEST_ATTEMPT.json` has been written and fsynced to durable storage**.
  Receipt-before-access is structural, not merely ordered.
- The checkpoint and decision threshold come only from the immutable development
  lock. `sealed_test.py` never selects, tunes or recomputes a threshold, never
  constructs an optimizer, and never calls backward.
- The threshold's provenance is validation-only and self-declaring:
  `VALIDATION_THRESHOLD.json` records `selected_from: "validation"` and
  `test_informed: false`.

### 3.3 Identity of what would be characterized

| Field | Value |
|---|---|
| Experiment | `B4B_cnn_transformer_v1` |
| Architecture | `B4BTransformerCNN` |
| Checkpoint | `model_selected.pt`, SHA-256 `b1301723909c641a0014c31f6daa9549d47ab231f0b07483e0de729aff5591c9` |
| Experiment lock | SHA-256 `58e44a09ce3ebffecfcd49d957acfa368fc03b534fdcd990aedb9b6b0e9bda7b` |
| Decision threshold | `0.8329097628593445`, from `locked_experiment_lock.validation_threshold` |
| Score semantics | uncalibrated sigmoid model score — **not** a calibrated probability |
| Split | `split_sha256` `66e25d77b6aaa25502974b4b60667b4c4b24d649bf9493666827c747a385ced7` |

All of the above were verified against their registered values during the
pre-execution audit that preceded this draft.

---

## 4. Explicit non-goals

If authorized, B4 execution **will not**:

1. modify the architecture, or select among architectures;
2. retrain, fine-tune, or alter any weight;
3. tune, recompute, or re-select the decision threshold;
4. change preprocessing, transforms, or feature construction;
5. compare multiple checkpoints, or substitute a different checkpoint after
   seeing a result;
6. re-open, revisit, or re-argue any prior retention decision (P1, M1, M2, U1,
   T1, T2) in light of the result;
7. alter, soften, or strengthen any existing claim after observing the outcome;
8. be re-run, retried, reset, or forced. **There is exactly one attempt.**

Additionally, per `B4_TEST_DEFERRAL_DECISION_V1.md` §4.2, the consumed B0–B3
classical test evidence remains closed and must not be used to motivate,
contextualize, or benchmark the B4 result.

**A result that is disappointing is a result.** The value of this evaluation is
that its outcome was not negotiable before it was observed, and it must not
become negotiable afterwards.

---

## 5. Remaining limitations

These must appear beside any reported B4 number, in the manuscript and anywhere
else the value is quoted.

### 5.1 No independent external cohort exists

`EXTERNAL_VALIDATION_STRATEGY_V1.md` audited the public record and found **no
drop-in independent cohort**:

- **EDB `overlap_clean`** (75 records) is available and audited, but is **not
  independent** — LTSTDB recordings are Pisa-collection originals that EDB
  excerpts, with ten pairs individually verified and fifteen records
  conservatively excluded. It is also structurally shifted: EDB records are
  ~2-hour excerpts against LTSTDB's ~24-hour recordings.
- **STAFF III** (104 patients) fails on five separate axes.

A B4 test number therefore **cannot be corroborated on any second cohort**, and
must never be described as externally validated.

### 5.2 Test and validation live on the same small cohort

| Partition | Subjects | Records | Ischemic episodes |
|---|---|---|---|
| Train | 56 | 60 | 791 |
| Validation | 12 | 13 | 163 |
| **Test** | **12** | **13** | **164** |

Every result this programme has produced — T1, T2, W1 — rests on 12 validation
subjects. A sealed-test number would rest on 12 more. Twelve subjects is a
sample from which no population claim survives.

### 5.3 The headline contrast already spans zero

T2's 95% paired subject-bootstrap interval on the S4D − GRU difference is
**[-0.015229, 0.148951]**, which includes zero. A B4 test number would be
reported beside a headline architectural comparison that does not exclude the
null.

### 5.4 What the result cannot establish

A B4 test number **cannot** establish clinical deployment readiness, diagnostic
performance on patients, generalization to any hospital or population, or
clinical superiority over any existing practice. It answers exactly one
question:

> How does the frozen B4-B encoder perform on the sealed evaluation set, under
> the registered protocol?

Nothing broader may be claimed from it, in the manuscript or anywhere else.

---

## 6. Objections, and where each now stands

*This section previously argued against authorization on the ground that a cheap
reversible option was unspent. **That ground no longer holds**, and the section
is rewritten rather than deleted so the change is visible.*

`EXTERNAL_VALIDATION_STRATEGY_V1.md` §5.2 carried a standing recommendation:

> **Do A and D. Do not do B yet. Do not open the sealed test.**

Route **A** was the EDB `overlap_clean` secondary evaluation — 75 records,
stratified by cold-start bin, costed as low because the adapter existed and the
audit was done. Route **D** was reporting the absence of an independent cohort as
a finding about the field.

### 6.1 Route A was declined in writing on 2026-08-24

`EXTERNAL_VALIDATION_ROUTE_A_DECISION_V1.md` records the decline, with reasons:
EDB `overlap_clean` cannot be claimed as an independent cohort — the fifteen-record
exclusion addresses *known* overlap and does not establish that the remaining 75
are independent; running it would not resolve the independence question; and the
programme will not use it to strengthen generalization claims. No EDB data was
accessed in reaching that decision.

**What the decline closes.** The reversible-option objection is resolved. It is
no longer true that a cheap, repeatable evaluation sits unexecuted while an
irreversible budget is spent. Route A is decided, on the record, before access —
which is the ordering this programme has followed without exception.

**What the decline does not close, and cannot.** Route A **does not provide
external corroboration**, and declining it does not create any. Handbook §43.1's
second objection stands:

> Opening the neural test before external validation spends the final firewall on
> a result no cohort can corroborate.

The decline changes that objection's character rather than its force: it is no
longer a *pending task* but a *settled fact*. No cohort will corroborate a B4
result, and none will become available to this paper.

**This limitation is accepted.** Not overcome, not mitigated, not deferred —
accepted, knowingly, as the price of completing the pre-registered evaluation
loop. §5 states it in the terms that must accompany any reported number, and
§6.4 forbids any wording that softens it.

### 6.2 Preconditions — current status

| # | Precondition | Status |
|---|---|---|
| 1 | Route A executed, or declined in writing with reasons | ✅ **SATISFIED** — declined 2026-08-24 |
| 2 | Route D drafted as a manuscript limitation | ✅ **SATISFIED** — `PAPER_S9_DISCUSSION_DRAFT.md` §9.1 |
| 3 | §2 and §9 of the manuscript exist as prose | ⚠️ **WAIVED** — see §6.3. §9 drafted; §9.3 and §2 unwritten |
| 4 | A pre-registered reporting commitment | ✅ **SATISFIED** — §6.4 |

### 6.3 §2 Related Work — completion waived until manuscript drafting

**Waived.** §2 Related Work need not exist before the sealed test is opened.

**Reason, as decided.** The sealed evaluation answers the registered performance
question — *how does the frozen B4-B encoder perform on the sealed evaluation set
under the registered protocol?* — and that question does not depend on manuscript
positioning. §2 situates the contribution against the literature; it does not
alter what the evaluation measures, how it is executed, or what may be claimed
from it. Deferring it to manuscript drafting changes nothing about the result.

**What the waiver costs, recorded so it is not discovered later.** §2 is where
the gap statement lives, and a result published without one has nothing external
to be measured against. The waiver therefore carries a condition: **§2, when
written, must not be shaped by the sealed-test result.** If the gap statement
comes to depend on the number, the ordering this waiver relies on has been
inverted, and the waiver's reason will have become false in retrospect.

### 6.4 Pre-registered reporting commitment

**Frozen before access. Binding on whatever the result turns out to be.**

**Metrics.** Exactly those registered in `B4_PROTOCOL_V1.md` "Evaluation
metrics" — pooled-window AUPRC as primary; AUROC, F1, sensitivity, specificity,
PPV, NPV, balanced accuracy and MCC as secondary; the same subject-macro metrics
as B0–B3; and rate-related and axis-shift false-positive fractions at the
validation-frozen threshold. **No metric may be added, substituted or dropped
after access.** A metric that looks informative once the values are visible is
precisely the metric this commitment exists to exclude.

**Uncertainty.** 1,000 subject-bootstrap replicates, seed `2026`, as registered.
Not re-derived, not re-seeded, not re-run.

**Subject accounting.** For every subject-macro metric, report:
- the **eligible** subject count;
- the **contributing** subject count — the denominator actually used;
- the **reason** for each exclusion.

`METRICS_PROTOCOL.md` excludes subjects lacking both classes from subject-macro
means, and counts single-class bootstrap replicates as undefined. **The
contributing count will therefore very likely be fewer than twelve.** This
commitment is written knowing that, because the identical omission has already
occurred once in this programme — T2's subject-macro was a mean over nine of
twelve subjects — and is discussed as a general finding at §9.2 of the
manuscript. Reporting a subject-macro figure here without its denominator would
reproduce, in the final evaluation, the exact defect the paper reports.

**Class distribution.** AUPRC is reported with observed prevalence and class
counts, per `METRICS_PROTOCOL.md`. AUPRC without prevalence is not interpretable
and will not be quoted alone.

**Exploratory evidence.** Conduction-change evidence remains **exploratory and
descriptive only**. It is never bootstrapped and never headlined.

**Interpretation.** The result supports **no clinical claim** — not effectiveness,
not diagnosis, not fitness for use. It supports **no external generalization
claim** — not to other cohorts, sites, populations or devices. **No selective
reporting**: every registered metric is published whatever its value, and a poor
result is published unchanged, with no revision to any thesis in §9 of the
manuscript.

**The single question this evaluation answers:**

> How does the frozen B4-B encoder perform on the sealed evaluation set, under
> the registered protocol?

---

## 7. Authorization

*To be completed by a human researcher. Claude must not fill in any part of this
section, and has not.*

```
Researcher decision:

[ ] Authorize B4 sealed-test execution
[ ] Continue deferral

I have read B4_TEST_DEFERRAL_DECISION_V1.md and, by this decision, supersede
its deferral -- argued and recorded before any access, per its section 3.

Preconditions (section 6.2):
  1. Route A declined 2026-08-24 ................. satisfied  [ ]
  2. Route D drafted at section 9.1 .............. satisfied  [ ]
  3. Section 2 / section 9 prose ................. waived, per section 6.3  [ ]
  4. Pre-registered reporting commitment ......... satisfied, section 6.4  [ ]

I accept, knowingly and permanently:
  - no second cohort will corroborate this result, and Route A's decline
    makes that final for this paper;
  - it rests on 12 subjects, 13 records, 164 annotated ischemic episodes;
  - it will be reported beside a headline contrast whose 95% interval
    includes zero;
  - it establishes no clinical, diagnostic or generalization claim.

Reasons / conditions:



Date:

Signature:
```

---

## 8. Scope limits of this document

This document does not modify the frozen test subjects, the test labels, the
benchmark definition, any protocol, any existing scientific artifact, or any
retention decision. Like the deferral it would supersede, it records a
governance choice about *when* the sealed test may be opened, and nothing else.

Until §7 is completed and this file is frozen with a recorded digest:

| | |
|---|---|
| B4 sealed test | **UNOPENED** |
| `TEST_ATTEMPT` | absent |
| Operative decision | `B4_TEST_DEFERRAL_DECISION_V1.md` — deferral |
| Route A | declined 2026-08-24 |
| Authorizes test access | **no** |
