# J1 — Fair Stateful vs Memoryless Episode Comparator, Protocol V1

**Status: `PROPOSED / NOT AUTHORIZED`.**
**Evidence class: `V2_DEVELOPMENT`.**
**Attempt budget: `NOT YET AUTHORIZED`.**

Governing authority:
[`../CARDIOSENTINEL_V2_EVIDENCE_AUTHORITY_V1.md`](../CARDIOSENTINEL_V2_EVIDENCE_AUTHORITY_V1.md).
Planning authority:
[`../CARDIOSENTINEL_TOP_JOURNAL_RESEARCH_MASTER_BLUEPRINT_V2_1.md`](../CARDIOSENTINEL_TOP_JOURNAL_RESEARCH_MASTER_BLUEPRINT_V2_1.md).

---

## 1. Question and estimand

> Does T1-like stateful episode reasoning retain an advantage when the memoryless
> comparator receives its own independently selected development operating point?

**Estimand.** The paired subject-level difference in episode F1 between
independently tuned stateful and memoryless episode-decision policies,
**conditional on the same inherited fixed B4 / P1 / M1 / M2 / T2 upstream
mechanisms** and prospectively cross-fitted J1 calibration and operating-point
machinery, over the V1-TRAIN development population.

**This is not fully cross-fitted upstream system performance, and must never be
described as such.**

- **B4 is historically fitted on the TRAIN population** — the same 56 subjects J1
  measures on (README §1, verified from the experiment lock).
- **T2 is historically developed on the TRAIN population**, and its arm identity
  was selected on outer VALIDATION (README §2).
- J1 is therefore **`V2_DEVELOPMENT`** evidence.
- **J1 cannot support external or generalization claims.** J5 remains the future
  fresh external test.
- Using one fixed upstream for both arms removes upstream model identity as an
  intentional arm difference. It does **not** prove that upstream in-sampleness
  has zero interaction with policy behaviour.

**The only intended experimental contrast in J1 is the episode-decision policy.**

V1's T1/W1 result motivates this question. It is `V1_HISTORICAL` and cannot serve
as J1 confirmation.

## 2. Arms

### 2.1 J1-S — stateful

The retained T1 episode-state policy: `NORMAL → WATCH → EVENT → RECOVERY`, four
states, state never crossing a record, channel or subject boundary, every stream
starting in `NORMAL`. Its evidence predicates are the retained ones:

- **WATCH evidence** — `d_t == True` **OR** `p_t >= p_watch` **OR** `s_t >= s_watch`
- **EVENT evidence** — `d_t == True` **AND** `p_t >= p_event` **AND** `s_t >= s_event`
- **NORMAL evidence** — `d_t == False` **AND** `p_t < p_watch` **AND** `s_t < s_watch`

**The retained state semantics are not modified.** J1 selects the policy's
operating point prospectively; it does not redesign the state machine.

### 2.2 J1-W — memoryless

A per-row decision function of the common evidence row alone. It emits a binary
event indication for row `t` computed **only** from quantities carried by that
row.

J1-W has, and must be constructed so that it *cannot* have:

- no prior episode state;
- no event-persistence state;
- no WATCH or RECOVERY memory;
- no counter, timer, run-length, hysteresis or confirmation window;
- no dependence on any earlier or later row's decision.

**The structural guarantee.** J1-W's inputs are drawn from the common evidence
arm-neutral row of §3.1, which does not contain `elapsed_state_seconds`. It is required to be implementable as
a pure function `row → bool` with no carried state of any kind. Any candidate
rule that cannot be written that way is out of the J1-W search space by
definition, not by review.

Post-hoc smoothing, merging or morphological closing of J1-W's output is
**prohibited**: it would reintroduce persistence and make J1-W a second state
machine wearing a different name.

## 3. The arm-neutral upstream evidence row

### 3.1 Definition

The **arm-neutral upstream evidence row** is generated once per outer fold and
provided **identically** to J1-S and J1-W:

| Field |
|---|
| `stable_id` |
| `m2g_detector_score` |
| `detector_decision_d_t` |
| `oof_calibrated_probability_p_t` |
| `decision_error_uncertainty_u_t` |
| `s4d_temporal_evidence_s_t` |
| `score_present` |
| `elapsed_stream_seconds` |

Eight fields. Both arms receive all eight, unchanged. The treatment contrast is:

> identical arm-neutral evidence **+ stateful policy machinery**
> versus
> identical arm-neutral evidence **+ memoryless decision rule**.

### 3.2 `elapsed_state_seconds` is not an upstream feature

The retained implementation's `T1_ALLOWED_ROW_INPUTS`
([`neural/t1_protocol.py`](../../../src/cardiosentinel/neural/t1_protocol.py))
carries nine entries; the ninth is `elapsed_state_seconds`, time since entry to
the current episode state.

**For the J1 estimand it is not upstream evidence at all.** It is an endogenous
internal quantity of the state machine — it exists only because J1-S has states,
and it is a function of J1-S's own prior decisions. It belongs to J1-S, not to the
shared scaffold.

**This is constitutive of the memoryless comparator's definition, not a
disadvantage imposed on it.** A rule that consumed a summary of episode-state
history would not be memoryless; excluding it is what makes J1-W the thing its
name says. Describing the exclusion as a handicap would misstate the design.

**Implementation note, separate from the science.** Because the retained T1 row
schema technically carries the field, the J1 adapter must **derive and supply
`elapsed_state_seconds` from J1-S's own state**, never read it from the
arm-neutral row. The arm-neutral row does not contain it. J1-W is never offered
it, and cannot be, because it is not in the row.

`s4d_temporal_evidence_s_t` is **not** treated as endogenous. It is a frozen
upstream quantity that V1 supplied identically to both arms, and W1's report
records that holding it fixed is what makes the ablation an episode-policy
ablation. Both arms receive it.

### 3.3 If the invariant cannot hold

If any scientifically unavoidable upstream difference between the arms is
discovered during implementation, **execution stops and the protocol returns for
human review.**

## 4. Development population and data authority

| | |
|---|---|
| Eligible subjects | the **56 V1 TRAIN** subjects of `protocols/splits/ltstdb_v1.json` |
| V1 VALIDATION | **prohibited** — historical only |
| V1 TEST | **prohibited** — consumed 2026-08-25, permanently |
| External datasets | **prohibited** for J1 development |
| Evidence class produced | `V2_DEVELOPMENT` |
| Labels | usable only as the frozen protocol specifies, never as a transition input |
| Provenance | every access emits a record |

**No data authority is granted by this protocol.** It is granted, if at all, by a
later authorization.

The V1 edge runtime's refusal to score non-VALIDATION subjects is **not relaxed**.
J1 will require a separately governed research evaluation path that accepts
explicitly supplied V2 cross-fitted artifacts. That path is not implemented and
not designed here beyond the requirement that it exist.

## 5. Prospective cross-fitting geometry — FROZEN

Nested and subject-disjoint over the 56 TRAIN subjects.

| Level | Folds | Subjects per fold | Pool |
|---|---|---|---|
| **Outer** | **7** | **8 assessment** / 48 development | all 56 |
| **Inner** | **6** | **8** | the 48 outer-development subjects |

```
OUTER fold k (7 of them):
  48 outer-development subjects ─┬─> fit fold-specific U1 calibration
                                 └─> INNER 6 x 8 split
                                       ├─ J1-S operating-point selection
                                       └─ J1-W operating-point selection
   8 outer-assessment subjects  ───> apply the frozen fold artifacts
                                     produce ONE arm-neutral row set
                                     evaluate frozen J1-S  ─┐ identical rows
                                     evaluate frozen J1-W  ─┘
```

**Rationale, fixed before any J1 outcome is observed.** 56 = 7 × 8 exactly, so
every subject receives exactly one outer assessment and all folds hold equal
subject counts; each outer analysis retains 48 development subjects; and 48 = 6 × 8
gives six equal inner folds for operating-point selection. The geometry follows
from the frozen population size and the subject-level inferential unit, not from
observed performance.

**Why nested rather than flat.** A flat K-fold would select the operating point on
the same subjects that assess it — the defect J1 exists to remove, transposed.

**The firewall.** No information from an outer-assessment subject may influence the
calibration fitted for its rows, the policy tuning, the stateful parameter
selection, or the memoryless threshold selection.

### 5.1 Fold assignment — FROZEN

**Seed: `2026`.** One deterministic procedure, applied identically to outer and
inner levels, producing the same assignments for both arms.

Balancing uses **reference-episode burden only**. No model-performance quantity of
any kind participates.

1. Stratify on **whether a subject has at least one reference episode**.
2. Within stratum, order by **reference-episode count**.
3. Deterministically allocate across folds to equalise both, in fold-index order.
4. Break every remaining tie by `sha256(f"2026:{subject}")` ascending, then by
   subject identity — following the identity-hash precedent already used by V1's
   split generator and T2's internal split.

**No fold may be regenerated because its eventual performance looks unusual.**
Fold assignment is frozen at generation and recorded with its seed.

*This protocol specifies the algorithm. It does not generate the folds.*

### 5.2 Subject exclusions — FROZEN

**Primary population: all 56 subjects of the frozen V1 TRAIN partition. No
post-hoc exclusion is permitted.**

A subject may be technically unevaluable only where an **already-existing, pre-J1
dataset-integrity rule** makes evaluation impossible. Such a case must be
identified **by that rule, never by observed J1 performance**, must be recorded,
must remain visible in the denominator accounting, and must never be silently
dropped. **No new exclusion criterion may be invented during execution.**

## 6. Independent operating-point selection

This is the core of J1.

### 6.1 J1-S selection space — FROZEN, NO EXPANSION

Exactly the **12** registered candidates of the retained policy:

- quantile levels `Q_WATCH ∈ {0.90, 0.95}` × `Q_EVENT ∈ {0.99, 0.995}` — 4 combinations;
- one of the **3 frozen persistence profiles**, each fixing `watch_clear_windows`,
  `event_confirm_windows`, `event_release_windows`, `re_event_confirm_windows`,
  `recovery_clear_windows`, `cold_event_confirm_windows`.

**Candidate count: 4 × 3 = 12.**

**J1-S is not widened.** J1 asks whether *the retained T1-like policy* survives a
fair comparator. Widening the stateful space would change the object under test
and create a rescue path for a negative result. Human decision 9 is closed as
**`NO EXPANSION`**.

### 6.2 J1-W candidate registry — FROZEN

J1-W is a pure memoryless `row → bool` mapping over the arm-neutral row of §3.1.
It uses **no** state, history, run length, persistence, hysteresis, confirmation
window, smoothing or cross-row post-processing.

**Threshold levels**, quantiles derived from **inner-development subjects only**:
`{0.90, 0.95, 0.975, 0.99, 0.995}` — 5 levels.

**Candidate signals:** `p_t` (calibrated), `s_t` (S4D evidence), `m2g_detector_score`
(3 continuous), and the binary `d_t`.

| Family | Construction | Count |
|---|---|---|
| W-A | single continuous signal ≥ threshold | 3 × 5 = **15** |
| W-B | `d_t` alone | **1** |
| W-C | pairwise conjunction, independent levels | 3 pairs × 5 × 5 = **75** |
| W-D | pairwise disjunction, independent levels | 3 pairs × 5 × 5 = **75** |
| W-E | continuous ∧ `d_t` | 3 × 5 = **15** |
| W-F | continuous ∨ `d_t` | 3 × 5 = **15** |
| W-G | triple conjunction, matched level | **5** |
| W-H | triple disjunction, matched level | **5** |
| | **Total** | **206** |

**Rule IDs** are stable and assigned at enumeration: `W-<family>-<signals>-<levels>`,
e.g. `W-C-pt.st-0.99.0.95`. **Ties in the selection argmax are broken by ascending
rule ID**, deterministically and before any data is seen.

**Semantic reduction, applied before data access and never by performance.** The
triple families are restricted to a matched threshold level; admitting independent
levels there would add 240 further rules that are near-duplicates of the pairwise
families under any realistic score distribution. No rule was removed by looking at
an outcome, because no outcome exists.

**206 against J1-S's 12.** The asymmetry is deliberate: J1-W must be a *credible*
memoryless comparator, not one constrained to resemble V1's W1 or to match a
parameter count. **Both counts are a disclosure obligation in the report**, and the
larger search space is itself a reviewer-visible risk — recorded in the
pre-registration's attack audit rather than argued away.

### 6.3 Fairness constraints — binding

- the **same inner subjects** for both arms;
- the **same cross-fitting structure**;
- the **same optimization endpoint** (§7 primary metric);
- the **same selection discipline** — argmax over the space on inner data, ties
  broken by a prospectively fixed deterministic rule;
- **identical information access**, except the `elapsed_state_seconds` exclusion
  of §3.2, which is disclosed and in J1-W's disfavour;
- **no manual tuning after viewing any outer-assessment outcome**;
- **no borrowing J1-S's promoted threshold for J1-W** — the V1 defect, prohibited
  by name;
- **no arm selected on more information than the other.**

**Parameter counts are not forced to be equal.** J1-S has persistence parameters
because it is stateful; J1-W has none because it is not. Equalising counts for
symmetry would either cripple J1-S or smuggle memory into J1-W. What is equalised
is *opportunity*: same subjects, same endpoint, same discipline, same access.

### 6.4 What must change from V1's mechanism

V1 promoted `qw0.9_qe0.99_FAST` — quantile levels bound **jointly** with
`event_confirm_windows = 2`. One selection served both arms. J1 replaces that with
two selections, run independently on the same inner data against the same
endpoint, neither able to see the other's outcome.

## 7. Endpoints

### 7.1 Primary

1. subject-macro episode F1 for J1-S;
2. subject-macro episode F1 for J1-W;
3. **the paired subject-level difference `J1-S − J1-W`** — the single primary
   contrast;
4. a subject-resampled bootstrap interval for that paired contrast.

**Inferential unit: the subject.** Window count is not the sample size, and no
inference is computed on pooled rows.

| Specification | Value | Authority |
|---|---|---|
| Subject denominator | every eligible outer-assessment subject, all 7 folds | this protocol |
| Aggregation | `(1/N) · Σ_i (F1_S,i − F1_W,i)` | follows V1's subject-macro form |
| Bootstrap unit | subject | V1 T1 analysis plan |
| Resampling | **paired** — `(F1_S,i, F1_W,i)` resampled together | this protocol |
| Replicates | 1000 | V1 T1 analysis plan |
| Seed | 2026 | V1 T1 analysis plan |
| Reselection of candidates inside replicates | **none** | V1 T1 analysis plan |
| Interval level | **95%** | frozen here |
| Undefined per-subject F1 in the paired form | **OPEN — see §7.1.1** | conflict, not chosen |

Interval construction reuses V1's method where it is explicitly defined and valid
for a paired contrast. **The method is not changed after results are seen.**

#### 7.1.1 `STOP` — the zero-reference convention does not extend to the paired form

V1's convention was traced in code, not assumed. Both implementations agree:

```
episode_f1 = 2·matched / (predicted + reference)     # None when denominator == 0
```

- [`neural/t1_development_run.py`](../../../src/cardiosentinel/neural/t1_development_run.py) — `2TP/(2TP+FP+FN)`, "Undefined when the denominator is zero"
- [`neural/t1_continuation_results.py`](../../../src/cardiosentinel/neural/t1_continuation_results.py) — returns `None` when `predicted + reference == 0`

So for a single arm: zero reference **and** zero predicted → **undefined**; zero
reference with ≥1 predicted → **0.0**; reference with zero predicted → **0.0**.
V1's prose agrees and records that `episode_f1` was *"defined for all twelve"* —
**the undefined case never arose**, and V1 computed a single-arm mean, not a
paired difference.

**Why this does not settle J1.** Definedness depends on `predicted`, which is
**arm output**. A subject with zero reference episodes can therefore be defined for
one arm and undefined for the other:

| Subject | reference | J1-S predicted | J1-W predicted | `F1_S` | `F1_W` | paired difference |
|---|---|---|---|---|---|---|
| example | 0 | 0 | 0 | undefined | undefined | undefined |
| example | 0 | 0 | ≥1 | **undefined** | **0.0** | **ambiguous** |
| example | 0 | ≥1 | 0 | **0.0** | **undefined** | **ambiguous** |

The set of subjects entering the paired mean would then be **arm-dependent and
outcome-dependent** — precisely what V1's own analysis plan warns is *"a statistic
over a data-dependent subset — not a subject-macro average, whatever it is
labelled."*

Worse, it is **directionally biased**: dropping such a subject removes a `0.0`
from whichever arm predicted runs while the quieter arm contributes nothing, so
the convention would systematically favour the arm that predicts fewer runs on
zero-episode subjects. That is a thumb on the scale in the primary estimand.

**Per the task's instruction, this is reported rather than chosen.** No convention
is invented here. Resolving it requires a human decision with a known directional
consequence, and it is the reason this protocol is not a freeze candidate.

**Independent of the resolution**, zero-reference subjects remain included in false
alarms per hour, predicted-event count, predicted-event duration, and the
subject-level descriptives.

### 7.2 Secondary — descriptive, never confirmatory

Episode sensitivity; episode precision; false alarms per hour; predicted-event run
count; predicted-event duration; fragmentation; overlap and onset latency
(**descriptive only**); per-subject results; subject-level failure modes.

**Pooled metrics are reported separately from subject-macro inference and never
substituted for it.** A favourable pooled result does not displace an unfavourable
subject-level one; V1's Evidence Map already names three denominators that were
not what they looked like.

## 8. Multiplicity and claim hierarchy

- **Exactly one primary contrast**: the paired subject-level difference of §7.1.3.
- Everything in §7.2 is **descriptive**. No secondary endpoint may be promoted to
  primary after results are seen.
- Subgroup and per-subject analyses are **exploratory** and generate hypotheses
  only.
- No multiplicity adjustment is required, because there is one confirmatory
  contrast. Were more added, adjustment would become mandatory — which is a reason
  not to add them.

## 9. Gate A — FROZEN

Primary contrast:

```
Δ = subject-macro episode F1(J1-S) − subject-macro episode F1(J1-W)
```

with the paired subject bootstrap of §7.1.

| Outcome | Condition |
|---|---|
| **PASS** | `Δ > 0` **and** the lower bound of the pre-registered **95%** bootstrap interval is **> 0** |
| **MIXED** | `Δ > 0` **but** the 95% interval includes `0` |
| **FAIL / NEGATIVE** | `Δ <= 0` |

**No minimum practically or clinically meaningful margin is imposed.** The
programme has no justified utility function, alert-cost model or minimum important
difference from which one could be derived. W1's report already declines to rank
the arms in monitoring terms for exactly that reason. Inventing a margin would be
choosing the bar without justification; adding one after results is the failure
pre-registration exists to prevent.

**Magnitude is always reported alongside** false alarms per hour, episode
sensitivity, episode precision, fragmentation, and subject-level heterogeneity.

**The phrase "practically meaningful improvement" must not be used merely because
Gate A passes.** Gate A establishes direction and interval support, nothing about
practical importance.

**Blueprint reconciliation.** The blueprint's Gate A wording contains the phrase
"practically meaningful advantage". This protocol does **not** silently rewrite it.
If its formal wording must be reconciled, that happens under the blueprint's own
change-control procedure, as a separate reviewed act.

## 10. Claim map — written before results

**No result is pre-written.** These are the permitted *forms*.

**If PASS.** *"Under prospectively and independently selected development
operating points, the stateful episode policy showed [observed bounded result]
relative to a matched, independently tuned memoryless comparator, in the V2
development study on the V1-TRAIN population."* Bounded to that population, that
upstream scaffold, and development evidence. Not a generalisation claim, not a
clinical claim, not a claim about episode reasoning in general.

**If MIXED.** The claim must carry the uncertainty and the heterogeneity: which
subjects drive it, how wide the interval is, and that the direction is not
established.

**If FAIL / NEGATIVE.** The report must state plainly that **a fairly tuned
memoryless comparator matched or exceeded the stateful policy under the registered
design.** This is a publishable result and is reported with the same standing as a
positive one.

**A negative J1 does not license expanding the J1-S search space, adding
persistence profiles, changing the endpoint, or running a stronger second
attempt.** Under the Evidence Authority a completed run that disappoints is
`SCIENTIFIC_NEGATIVE` and has spent its budget. A new question enters at
`QUESTION` with its own protocol and authorization.

## 11. Failure classification and attempts

| Classification | Definition | Consequence |
|---|---|---|
| `INFRASTRUCTURE` | Crash, environment or I/O failure **before any scientific quantity is visible** | Retry permitted under the same authorization, recorded |
| `APPARATUS_AFTER_VISIBILITY` | Failure after partial scientific visibility | **Not a free retry.** The run is recorded, what was seen is recorded, and continuation requires human review — because the analyst now knows something |
| `COMPLETED_ATTEMPT` | Ran to completion under the protocol | A result, whatever its direction. Budget spent |
| `PROTOCOL_VIOLATION` | Executed outside the frozen protocol | Invalid. Recorded, not reported as evidence |
| `INVALID_EXECUTION` | Frozen artifact or digest mismatch | Invalid. Recorded, not reported as evidence |

**`attempt_budget = NOT YET AUTHORIZED`.** Set by explicit authorization, never by
this protocol. **No automatic retry of any kind.**

The later authorization must resolve: the attempt budget; the data authority for
the 56 TRAIN subjects; who may declare `APPARATUS_AFTER_VISIBILITY`; and the
provenance sink for J1 artifacts.

## 12. Decision register

| # | Decision | Status |
|---|---|---|
| 1 | Gate A criterion | **CLOSED** — §9. Direction + 95% lower bound > 0. No margin invented. |
| 2 | Outer K and inner structure | **CLOSED** — §5. Outer 7 × 8, inner 6 × 8 over 48. |
| 3 | Fold-assignment seed | **CLOSED** — §5.1. `2026`. |
| 4 | Fold balancing and statistic | **CLOSED** — §5.1. Reference-episode presence, then count, sha256 identity tie-break. Burden only. |
| 5 | Subject exclusions | **CLOSED** — §5.2. None post-hoc; pre-existing integrity rules only, always visible in the denominator. |
| 6 | **Zero-reference-subject handling in the paired form** | **OPEN — `STOP` recorded at §7.1.1.** V1's convention exists and is internally consistent, but does not determine the paired case, and every resolution has a known directional consequence. Reported, not chosen. |
| 7 | Bootstrap interval level | **CLOSED** — §7.1. 95%, paired, 1000 replicates, seed 2026. |
| 8 | J1-W registry and count | **CLOSED** — §6.2. 206 enumerated candidates, stable IDs, deterministic tie-break. |
| 9 | J1-S expansion | **CLOSED** — §6.1. `NO EXPANSION`; 12 candidates. |
| 10 | B4 fitting population | **CLOSED** — README §1. TRAIN, 56 subjects, lock `58e44a09…`. |
| 11 | T2 S4D classification | **CLOSED** — README §2. `FROZEN_REUSED`. |

**Ten of eleven closed. One remains open, and it is a `STOP` reported for human
resolution rather than a gap left unnoticed.**

Decision 6 alone prevents this protocol from being a freeze candidate. It is not a
formatting detail: it determines which subjects enter the primary estimand, and
the choice is directionally consequential.

## 13. Implementation audit — read-only

1. **Can the T1 implementation be reused without scientific modification?**
   Its state machine, predicates and profiles are frozen and parameterised by the
   operating point, so selecting a different point is a use of the implementation
   rather than a change to it. Its allow/deny input lists are enforced in code.
2. **Can W1's implementation support independent selection?** V1's W1 was
   evaluated at an inherited point and its plan *excluded* threshold sweeps by
   design. J1-W therefore needs a **new selection harness**; the W1 rule
   evaluation itself may be reusable.
3. **What new code is later required?** A research evaluation path accepting
   supplied V2 cross-fitted artifacts; a nested fold generator; a TRAIN-side
   calibration fitter; two arm-specific selection harnesses; a paired subject
   bootstrap. **None is written in this task.**
4. **Can both arms consume one canonical row schema?** Yes —
   `T1_ALLOWED_ROW_INPUTS`, with J1-W's `elapsed_state_seconds` exclusion applied
   at the arm boundary, not upstream.
5. **What risks exposing V1 VALIDATION or TEST?** The V1 runtime resolves
   operating points by validation-subject identity. A J1 path that reused it
   without care could bind a J1 subject to a VALIDATION artifact. The runtime's
   refusal currently prevents this and **must not be relaxed**.
6. **What structural guard is later required?** J1 artifact loading should make a
   forbidden partition **unrepresentable** — a J1 fold that cannot name a
   VALIDATION or TEST subject — following V1's negative-capability precedent.
   Required; not built here.
7. **Which synthetic fixtures are needed first?** Synthetic evidence rows with
   known episode structure, to exercise both arms, the nested splitter and the
   paired bootstrap before any real subject is touched.

**No execution path is implemented in this task, and no interface sketch was
written.**
