# J1 — Pre-Registration V1

# **NOT READY TO FREEZE**

**Ten of eleven decisions are now closed. One remains open, and it is enough.**

Decision 6 — how a zero-reference subject enters the **paired** difference — is a
`STOP` recorded at protocol §7.1.1, not an oversight. V1's convention exists and
is internally consistent, but it does not determine the paired case, and every
resolution has a **known directional consequence** for the primary estimand.

Because that choice would change which subjects enter the primary contrast, this
document cannot become a freeze candidate. J1 remains `PLANNED / NOT AUTHORIZED`.

Protocol: [`J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1.md`](J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1.md).

---

## 1. Hypothesis

**H1.** Under prospectively and independently selected development operating
points, the stateful episode-decision policy achieves a higher subject-macro
episode F1 than an independently tuned memoryless episode-decision policy, on the
V1-TRAIN development population, with both arms consuming the identical arm-neutral upstream evidence row,
conditional on the inherited fixed B4 / P1 / M1 / M2 / T2 scaffold.

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
| 3 | Arm-neutral upstream row | **FROZEN** — 8 fields, protocol §3.1. `elapsed_state_seconds` is endogenous to J1-S and is not in the row |
| 4 | Development population | **FROZEN** — all 56 V1 TRAIN subjects |
| 5 | Fold-generation procedure | **FROZEN** — outer 7 × 8, inner 6 × 8 over 48; seed 2026; burden balancing; sha256 identity tie-break |
| 6 | Tuning spaces | **FROZEN** — J1-S 12 (`NO EXPANSION`); J1-W 206 enumerated with stable IDs |
| 7 | Selection objective | **FROZEN** — subject-macro episode F1 on inner data, both arms |
| 8 | Primary metric | **FROZEN** — paired subject-level difference `Δ = J1-S − J1-W` |
| 9 | Inferential unit | **FROZEN** — the subject |
| 10 | Bootstrap procedure | **FROZEN** — paired, subject unit, 1000 replicates, seed 2026, no reselection, **95%** |
| 11 | **Undefined-subject handling in the paired form** | **OPEN — `STOP`, protocol §7.1.1** |
| 12 | Secondary metrics | **FROZEN** — protocol §7.2, all descriptive |
| 13 | Gate A interpretation | **FROZEN** — `Δ > 0` and 95% lower bound `> 0`; no margin invented |
| 14 | Exclusion rules | **FROZEN** — none post-hoc; pre-existing integrity rules only |
| 15 | Failure handling | **FROZEN** — protocol §11 |
| 16 | Claim language | **FROZEN** — protocol §10 |

**One open item. Fifteen frozen.**

## 3. Prohibited after freeze

Once frozen, none of the following may change in response to any observed
outcome: the hypothesis; either arm's definition; the arm-neutral row;
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
2. Per outer fold: fit fold-specific U1 calibration on the 48 outer-development
   subjects only; select J1-S's and J1-W's operating points independently on inner
   data, same subjects, same endpoint, same discipline.
3. Per outer fold: produce **one** arm-neutral row set for the 8 outer-assessment subjects
   and hand the identical rows to both frozen arms.
4. Compute per-subject episode F1 for each arm.
5. Compute the paired per-subject difference and its subject-macro mean.
6. Compute the subject bootstrap: 1000 replicates, seed 2026, no reselection.
7. Report secondary and per-subject descriptives.
8. Read Gate A against the frozen criterion.

**Outcomes are inspected only at step 4, and only after steps 1–3 are complete for
every fold.** No operating point is revised after any outer-assessment outcome is seen.

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
| **Is J1-W genuinely competitive?** | **206 enumerated rules** over `p_t`, `s_t`, `m2g_detector_score` and `d_t` at five threshold levels, including pairwise conjunctions and disjunctions at independent levels. Far stronger than V1's single fixed rule at an inherited operating point. |
| **Are tuning budgets symmetrical?** | Not in parameter count, deliberately — J1-S is stateful and J1-W is not. *Opportunity* is equalised: same inner subjects, endpoint, discipline, access. Both candidate counts are disclosed. |
| **Is the comparison isolated to statefulness?** | Both arms take the identical 8-field arm-neutral row. `elapsed_state_seconds` is not in that row at all: it is endogenous to J1-S and derived from J1-S's own state. Its absence from J1-W is **constitutive of the memoryless definition**, not an imposed handicap. |
| **Is a subject used in both tuning and evaluation?** | No. Nesting exists for this; outer-assessment subjects contribute to no fitting, calibration or selection of their own rows. |
| **Is cross-fitting truly subject-disjoint?** | At the J1 levels, yes — outer-assessment subjects contribute to no calibration, tuning or selection of their own rows. **Verified limitation:** the B4 encoder **was** trained on all 56 TRAIN subjects, and T2 was developed on them too. A J1 outer assessment fold is therefore **not held out from all historical upstream model development**. J1 estimates a conditional episode-policy contrast given the inherited scaffold. Using one fixed upstream for both arms removes upstream identity as an intentional arm difference; it does **not** prove upstream in-sampleness has zero interaction with policy behaviour. Absolute values are development evidence only. |
| **Are subjects without episodes handled transparently?** | **Not yet — this is the open item.** In the paired form, definedness depends on each arm's own predictions, so the subject set entering the primary contrast would be arm- and outcome-dependent, and dropping such subjects systematically favours the arm predicting fewer runs on zero-episode subjects. Reported at protocol §7.1.1 rather than resolved. They remain included in false alarms/hour, predicted-event count and duration, and the descriptives regardless. |
| **Could pooled prevalence drive the result?** | Inference is subject-macro on a paired difference. Pooled metrics are reported separately and cannot substitute. |
| **Could threshold search overfit folds?** | Selection is on the 6 inner folds only; evaluation is on the 8 outer-assessment subjects. **J1-W searches 206 candidates against J1-S's 12, so residual inner-fold selection variance is larger for J1-W.** This is disclosed rather than corrected, because shrinking J1-W's space to match would make it a weaker comparator — the defect J1 exists to remove. |
| **Does the stateful arm have more degrees of freedom?** | **No — the reverse.** J1-S has 12 candidates; J1-W has **206**. The larger space makes J1-W credible rather than constrained to resemble V1's W1, but it also gives J1-W more opportunity to overfit the inner folds. Both counts are disclosed in the report. The asymmetry is a deliberate design choice recorded here, in J1-W's favour on capability and against it on selection variance. |
| **Is the bootstrap unit correct?** | Subject, following V1's governed convention. Window count is explicitly not the sample size. |
| **Are metrics chosen because V1 looked favourable?** | Episode F1 is V1's pre-registered primary and is inherited, not selected now. Choosing a new primary at this point would be the suspicious act. |
| **Could consumed V1 evidence leak in?** | VALIDATION and TEST are prohibited. **Open risk:** the V1 runtime resolves operating points by validation-subject identity; a J1 path reusing it carelessly could bind to a VALIDATION artifact. A structural guard making forbidden partitions unrepresentable is **required before execution** (protocol §13.6). |
| **What would falsify the thesis?** | §5. Stated before any data is seen. |

## 7. Status

`PLANNED / NOT AUTHORIZED`. No data authority. No attempt budget. No
authorization document. **NOT READY TO FREEZE** — one open decision, protocol §7.1.1.
