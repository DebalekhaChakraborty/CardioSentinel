# J1 — Pre-Registration V1

# **NOT READY TO FREEZE**

**Eleven decisions are unresolved (§13).** Until they are closed by a human, this
document is a draft and J1 remains `PLANNED / NOT AUTHORIZED`. Freezing it in this
state would leave choices open that could later be made after seeing outcomes —
the exact failure a pre-registration exists to prevent.

Protocol: [`J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1.md`](J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1.md).

---

## 1. Hypothesis

**H1.** Under prospectively and independently selected development operating
points, the stateful episode-decision policy achieves a higher subject-macro
episode F1 than an independently tuned memoryless episode-decision policy, on the
V1-TRAIN development population, with both arms consuming identical cross-fitted
upstream evidence rows.

**H0.** It does not.

**Direction is not assumed.** V1's W1 report states that a memoryless rule given
its own operating point "would very likely score better than Arm W does here" —
J1 is run because the answer is genuinely unknown, and a negative result is a
result.

## 2. Frozen on freeze

| # | Item | Status |
|---|---|---|
| 1 | Hypothesis | **FROZEN** (§1) |
| 2 | Arms | **FROZEN** — protocol §2 |
| 3 | Common upstream boundary | **FROZEN** — `T1_ALLOWED_ROW_INPUTS`; J1-W excludes `elapsed_state_seconds` |
| 4 | Development population | **FROZEN** — the 56 V1 TRAIN subjects |
| 5 | Fold-generation procedure | **OPEN** — decisions 2, 3, 4, 5 |
| 6 | Tuning spaces | **PARTIAL** — J1-S space frozen at 12 candidates; J1-W resolution open (8, 9) |
| 7 | Selection objective | **FROZEN** — subject-macro episode F1 on inner data, both arms |
| 8 | Primary metric | **FROZEN** — paired subject-level difference `J1-S − J1-W` |
| 9 | Inferential unit | **FROZEN** — the subject |
| 10 | Bootstrap procedure | **PARTIAL** — 1000 replicates, seed 2026, no reselection; interval level open (7) |
| 11 | Undefined-subject handling | **OPEN** — decision 6 |
| 12 | Secondary metrics | **FROZEN** — protocol §7.2, all descriptive |
| 13 | Gate A interpretation | **OPEN** — decision 1 |
| 14 | Exclusion rules | **OPEN** — decision 5 |
| 15 | Failure handling | **FROZEN** — protocol §11 |
| 16 | Claim language | **FROZEN** — protocol §10 |

## 3. Prohibited after freeze

Once frozen, none of the following may change in response to any observed
outcome: the hypothesis; either arm's definition; the common upstream boundary;
the population; the fold procedure or seed; either tuning space; the selection
objective; the primary metric; the inferential unit; the bootstrap procedure;
undefined-subject handling; the secondary metric list; Gate A's interpretation;
exclusion rules; failure classification; or the claim forms.

**Specifically prohibited**, because each is a way this study could be quietly
rescued:

- adding a persistence profile to J1-S after seeing a negative result;
- coarsening or refining J1-W's grid after seeing its performance;
- switching the primary metric to a secondary one;
- switching from subject-macro to pooled aggregation;
- introducing an effect-size margin after the effect is known;
- excluding subjects discovered to be unfavourable;
- reporting a subgroup as though it were the primary contrast;
- smoothing or merging J1-W's output.

## 4. Analysis, stated in advance

1. Generate nested subject-disjoint folds over the 56 TRAIN subjects, by the
   frozen procedure and seed.
2. Per outer fold: fit fold-specific upstream nuisance artifacts on outer-train
   subjects only; select J1-S's and J1-W's operating points independently on inner
   data, same subjects, same endpoint, same discipline.
3. Per outer fold: produce **one** set of evidence rows for the held-out subjects
   and hand the identical rows to both frozen arms.
4. Compute per-subject episode F1 for each arm.
5. Compute the paired per-subject difference and its subject-macro mean.
6. Compute the subject bootstrap: 1000 replicates, seed 2026, no reselection.
7. Report secondary and per-subject descriptives.
8. Read Gate A against the frozen criterion.

**Outcomes are inspected only at step 4, and only after steps 1–3 are complete for
every fold.** No operating point is revised after any held-out outcome is seen.

## 5. What would falsify H1

A paired subject-level contrast at or below zero, or an uncertainty interval that
does not support the direction, with a J1-W that met its credibility requirements.

**If that is the outcome, it is the finding.** J1-W beating J1-S would mean the V1
T1/W1 result was an artifact of the shared operating point — which is precisely
what W1's own limitation section says is possible, and what J1 was built to test.

## 6. Reviewer-attack audit

Every attack is closed prospectively or recorded as a limitation. None is
deferred to the report.

| Attack | Response |
|---|---|
| **Is J1-W genuinely competitive?** | Its space includes thresholds on `p_t`, `s_t` and the detector score, plus conjunctions — not V1's fixed rule. Grid resolution is decision 8; **the requirement is credibility, not resemblance to W1.** |
| **Are tuning budgets symmetrical?** | Not in parameter count, deliberately — J1-S is stateful and J1-W is not. *Opportunity* is equalised: same inner subjects, endpoint, discipline, access. Both candidate counts are disclosed. |
| **Is the comparison isolated to statefulness?** | Both arms take identical rows from one common scaffold. The single input difference, `elapsed_state_seconds`, is state-derived, excluded from J1-W, and disclosed — in J1-W's disfavour. |
| **Is a subject used in both tuning and evaluation?** | No. Nesting exists for this; outer-held-out subjects contribute to no fitting, calibration or selection of their own rows. |
| **Is cross-fitting truly subject-disjoint?** | Required at both levels. **Limitation:** the B4 encoder may have been fit on all 56 TRAIN subjects (README verification 1). If so, every row is partly in-sample at the representation layer. It affects both arms identically and cancels in the paired contrast, but it bounds the absolute values and must be stated in the report. |
| **Are subjects without episodes handled transparently?** | Decision 6 — open, and it must be closed before freeze precisely because it is choosable after the fact. |
| **Could pooled prevalence drive the result?** | Inference is subject-macro on a paired difference. Pooled metrics are reported separately and cannot substitute. |
| **Could threshold search overfit folds?** | Selection is on inner data only, evaluation on outer-held-out subjects. Residual inner-fold overfitting affects both arms and is bounded by the identical discipline. |
| **Does the stateful arm have more degrees of freedom?** | Yes — 12 candidates against J1-W's grid. Disclosed as a number in the report, not argued away. Forcing equality would cripple one arm or smuggle memory into the other. |
| **Is the bootstrap unit correct?** | Subject, following V1's governed convention. Window count is explicitly not the sample size. |
| **Are metrics chosen because V1 looked favourable?** | Episode F1 is V1's pre-registered primary and is inherited, not selected now. Choosing a new primary at this point would be the suspicious act. |
| **Could consumed V1 evidence leak in?** | VALIDATION and TEST are prohibited. **Open risk:** the V1 runtime resolves operating points by validation-subject identity; a J1 path reusing it carelessly could bind to a VALIDATION artifact. A structural guard making forbidden partitions unrepresentable is **required before execution** (protocol §13.6). |
| **What would falsify the thesis?** | §5. Stated before any data is seen. |

## 7. Status

`PLANNED / NOT AUTHORIZED`. No data authority. No attempt budget. No
authorization document. **NOT READY TO FREEZE.**
