# J1 — Pre-Registration V1

# **PRE-REGISTERED — NOT AUTHORIZED**

| | |
|---|---|
| Protocol | **frozen** |
| Pre-registration | **frozen** |
| TRAIN data authority | **none** |
| Attempt budget | **none** |
| Execution authorization | **none** |
| Fold manifest | **not generated** |
| Scientific result | **none exists** |

**This is `PRE-REGISTERED`. It is not `EXECUTABLE`.** Pre-registration is not
authorization: no real-data access may occur until a separate authorization names
the frozen digests, the data authority and the attempt budget.

**Every result-affecting design choice is closed.** None was made by inspecting an
outcome, a fold, or an annotation count.

The decision that blocked the previous revision — how a zero-reference subject
enters the paired difference — was **dissolved rather than adjudicated**. Primary
episode-F1 eligibility is `reference_episode_count > 0`, defined from reference
truth alone, so the denominator `predicted + reference` is strictly positive for
both arms on every subject in the primary cohort and the undefined branch is
unreachable. The arm-dependence that made every earlier option directionally
biased cannot arise.

**This is not `PRE-REGISTERED`, not `AUTHORIZED`, and not `EXECUTABLE`.** Those
require explicit human action. No authorization document exists, no attempt budget
is set, and no real-data authority is granted. J1 remains
`PLANNED / NOT AUTHORIZED`.

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
| 4 | Study population | **FROZEN** — all 56 V1 TRAIN subjects |
| 4a | Primary-F1 cohort | **FROZEN** — `reference_episode_count > 0`, from reference truth alone, identical for both arms |
| 5 | Fold-generation procedure | **FROZEN** — outer 7 × 8, inner 6 × 8 over 48; seed 2026; deterministic lexicographic allocator (protocol §5.1) |
| 5a | Inner OOF choreography | **FROZEN** — protocol §5.3–5.9. 40-subject inner fit, 8-subject inner OOF, complete 48-subject assembly, ID promotion, then outer nuisance refit |
| 5b | Fit vs OOF terminology | **FROZEN** — protocol §5.10. Fit-side values are never persisted as `oof_calibrated_probability_p_t` |
| 6 | Tuning spaces | **FROZEN** — J1-S 12 (`NO EXPANSION`); J1-W 206 enumerated with stable IDs |
| 7 | Selection objective | **FROZEN** — subject-macro episode F1 on inner data, both arms |
| 8 | Primary metric | **FROZEN** — paired subject-level difference `Δ = J1-S − J1-W` |
| 9 | Inferential unit | **FROZEN** — the subject |
| 10 | Bootstrap procedure | **FROZEN** — paired, subject unit, with replacement, mean paired difference per replicate, 1000 replicates, seed 2026, no reselection, **percentile** interval at 2.5/97.5 via `numpy.percentile` default `linear` |
| 11 | Undefined-subject handling in the paired form | **FROZEN** — unreachable in the primary cohort; V1's `episode_f1` unmodified; no imputation |
| 12 | Secondary metrics | **FROZEN** — protocol §7.2, all descriptive |
| 13 | Gate A interpretation | **FROZEN** — `Δ > 0` and 95% lower bound `> 0`; no margin invented |
| 14 | Exclusion rules | **FROZEN** — none post-hoc; pre-existing integrity rules only |
| 15 | Failure handling | **FROZEN** — protocol §11 |
| 16 | Claim language | **FROZEN** — protocol §10 |
| 17 | Selection order and tie-break | **FROZEN** — V1's `policy_sort_key` preserved, protocol §6.5 |
| 18 | Zero-reference operational reporting | **FROZEN** — mandatory, protocol §7.3 |

**All twenty frozen. None open.** Two were made *algorithmically unique* in this reconciliation: the bootstrap quantile convention and the fold allocator.

## 3. Prohibited after freeze

Once frozen, none of the following may change in response to any observed
outcome: the hypothesis; either arm's definition; the arm-neutral row;
the population; the fold procedure or seed; either tuning space; the selection
objective; the primary metric; the inferential unit; the bootstrap procedure;
the primary-F1 eligibility rule; the secondary metric list; Gate A's interpretation;
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
   frozen allocator and seed (protocol §5.1).
2. **Per outer fold, per inner fold `j`:** fit the U1 calibrator on the 40
   `INNER_FIT_j` subjects only; derive every candidate's numeric thresholds from
   that fit population; apply the calibrator to the 8 `INNER_HELDOUT_j` subjects
   to obtain **inner OOF** `p_t`; evaluate **every** candidate ID of both arms on
   those 8 subjects.
3. **Combine the six inner-held-out evaluations** into a complete 48-subject
   inner-OOF assembly — exactly one held-out evaluation per subject per candidate,
   asserted. Score candidates **only** from this assembly, never from fit-side
   predictions (protocol §5.5–5.6).
4. **Select and freeze one J1-S ID and one J1-W ID** for the outer fold, from that
   assembly alone, **before any outer-assessment result is visible** (§5.7).
5. **Refit nuisance only:** fit the final outer U1 calibrator on all 48
   outer-development subjects and derive the two frozen IDs' numeric thresholds
   from that population. **The identities do not change** (§5.8).
6. Apply those artifacts to the 8 outer-assessment subjects, producing **one**
   eight-field arm-neutral row set with **outer OOF** `p_t`, handed identically to
   both frozen arms (§5.9).
7. Compute per-subject episode F1 for each arm, over the **primary-F1-eligible**
   subjects (`reference_episode_count > 0`) — the same set for both arms.
8. Compute the paired per-subject difference and its subject-macro mean.
9. Compute the percentile paired subject bootstrap: 1000 replicates, seed 2026,
   2.5/97.5, no reselection.
10. Report the zero-reference and all-56 operational analyses of protocol §7.3,
    with the full cohort accounting.
11. Report secondary and per-subject descriptives.
12. Read Gate A against the frozen criterion, scoped as protocol §9.1 requires.

**The six inner-fold predictions are selection evidence. The seven
outer-assessment folds produce the primary J1 evidence.**

**No outer-assessment outcome is inspected before step 7, and no candidate identity
is revised after any outer-assessment outcome is seen.**

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
| **Is the comparison isolated to statefulness?** | Both arms take the identical 8-field arm-neutral row. `elapsed_state_seconds` is not in that row at all: it is endogenous to J1-S and derived from J1-S's own state. Its absence from J1-W is **constitutive of the definition of a memoryless policy** — J1-S's own internal state, not upstream evidence J1-W is denied. |
| **Is a subject used in both tuning and evaluation?** | No. Nesting exists for this; outer-assessment subjects contribute to no fitting, calibration or selection of their own rows. |
| **Is cross-fitting truly subject-disjoint?** | At the J1 levels, yes — outer-assessment subjects contribute to no calibration, tuning or selection of their own rows. **Verified limitation:** the B4 encoder **was** trained on all 56 TRAIN subjects, and T2 was developed on them too. A J1 outer assessment fold is therefore **not held out from all historical upstream model development**. J1 estimates a conditional episode-policy contrast given the inherited scaffold. Using one fixed upstream for both arms removes upstream identity as an intentional arm difference; it does **not** prove upstream in-sampleness has zero interaction with policy behaviour. Absolute values are development evidence only. |
| **Are subjects without episodes handled transparently?** | Yes. They stay in the 56-subject study population and carry the false-alerting evidence (protocol §7.3). They are outside the *primary episode-F1 endpoint* because that endpoint is undefined without a reference episode — endpoint-specific evaluability, not exclusion. |
| **Did zero-event subjects disappear from the comparison in a way that favoured one arm?** | **No.** Primary-F1 eligibility is determined **only** by `reference_episode_count > 0`; the criterion is **identical for both arms**; **no prediction-dependent dropping occurs**; zero-reference subjects remain in **all** false-alarm analyses; and total plus per-stratum subject counts are reported. |
| **Could pooled prevalence drive the result?** | Inference is subject-macro on a paired difference. Pooled metrics are reported separately and cannot substitute. |
| **Could threshold search overfit folds?** | Selection is on the 6 inner folds only; evaluation is on the 8 outer-assessment subjects. **J1-W searches 206 candidates against J1-S's 12, so residual inner-fold selection variance is larger for J1-W.** This is disclosed rather than corrected, because shrinking J1-W's space to match would make it a weaker comparator — the defect J1 exists to remove. |
| **Does the stateful arm have more degrees of freedom?** | **No — the reverse.** J1-S has 12 candidates; J1-W has **206**. The larger space makes J1-W credible rather than constrained to resemble V1's W1, but it also gives J1-W more opportunity to overfit the inner folds. Both counts are disclosed in the report. The asymmetry is a deliberate design choice recorded here, in J1-W's favour on capability and against it on selection variance. |
| **Is the bootstrap unit correct?** | Subject, following V1's governed convention. Window count is explicitly not the sample size. |
| **Are metrics chosen because V1 looked favourable?** | Episode F1 is V1's pre-registered primary and is inherited, not selected now. Choosing a new primary at this point would be the suspicious act. |
| **Could consumed V1 evidence leak in?** | VALIDATION and TEST are prohibited. **Open risk:** the V1 runtime resolves operating points by validation-subject identity; a J1 path reusing it carelessly could bind to a VALIDATION artifact. A structural guard making forbidden partitions unrepresentable is **required before execution** (protocol §13.6). |
| **What would falsify the thesis?** | §5. Stated before any data is seen. |

## 6a. Recorded limitation

> The primary F1 estimand characterizes **episode detection among subjects
> containing at least one reference episode.** Event-free monitoring behaviour is
> characterized separately, by false-alarm and predicted-event metrics over the
> zero-reference cohort and over all 56 subjects.

This is stated in the report, not omitted. A Gate A PASS is a statement about the
reference-positive estimand and **does not by itself support "better overall
monitoring"** — that requires the operational evidence alongside it.

## 7. Status

`PLANNED / NOT AUTHORIZED`. No data authority. No attempt budget. No
authorization document.

**FREEZE CANDIDATE — NOT AUTHORIZED.** Human review required to freeze; a further
explicit act to authorize.
