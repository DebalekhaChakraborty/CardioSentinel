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

**Estimand:** the paired, subject-level difference in subject-macro episode F1
between a stateful episode-decision policy and an independently tuned memoryless
episode-decision policy, both consuming identical cross-fitted upstream evidence
rows, over the V1-TRAIN development population.

**The only intended experimental contrast in J1 is the episode-decision policy.**
Every other component is either common to both arms by construction or excluded.

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
row minus its state-derived fields (§3.2). It is required to be implementable as
a pure function `row → bool` with no carried state of any kind. Any candidate
rule that cannot be written that way is out of the J1-W search space by
definition, not by review.

Post-hoc smoothing, merging or morphological closing of J1-W's output is
**prohibited**: it would reintroduce persistence and make J1-W a second state
machine wearing a different name.

## 3. The common-upstream invariant

**J1-S and J1-W consume identical evidence rows.** The rows are produced once per
outer fold and handed to both arms unchanged.

### 3.1 The boundary is repository-derived, not assumed

The boundary is `T1_ALLOWED_ROW_INPUTS`, the nine-entry allow list enforced at
[`src/cardiosentinel/neural/t1_protocol.py`](../../../src/cardiosentinel/neural/t1_protocol.py),
paired with the fifteen-entry `T1_FORBIDDEN_TRANSITION_INPUTS` deny list. That
allow list is already the authoritative statement of what an episode decision may
see, and J1 adopts it rather than inventing a boundary.

| Field | J1-S | J1-W | Note |
|---|---|---|---|
| `stable_id` | ✓ | ✓ | identity only |
| `m2g_detector_score` | ✓ | ✓ | |
| `detector_decision_d_t` | ✓ | ✓ | |
| `oof_calibrated_probability_p_t` | ✓ | ✓ | out-of-fold by contract |
| `decision_error_uncertainty_u_t` | ✓ | ✓ | |
| `s4d_temporal_evidence_s_t` | ✓ | ✓ | a bounded score, not a probability |
| `score_present` | ✓ | ✓ | |
| `elapsed_stream_seconds` | ✓ | ✓ | time since stream start; not state-derived |
| `elapsed_state_seconds` | ✓ | **✗** | **state-derived — see §3.2** |

### 3.2 One allowed field is state-derived, and J1-W must not receive it

`elapsed_state_seconds` is time since entry to the current episode state. It
exists *because* there is a state machine. Handing it to J1-W would give the
memoryless arm a summary of the very memory it is defined not to have, and the
comparison would no longer isolate statefulness.

**J1-W's input row is the common row minus `elapsed_state_seconds`.** This is the
single asymmetry in input access, it is in the memoryless arm's disfavour, and it
is required for the arm to mean what it is called. It is disclosed as a design
decision, not buried as an implementation detail.

`s4d_temporal_evidence_s_t` is *not* treated as state-derived. It is a frozen
upstream quantity that V1 supplied identically to both arms, and W1's report
records that holding it fixed is what makes the ablation an episode-policy
ablation. Both arms receive it.

### 3.3 If the invariant cannot hold

If any scientifically unavoidable upstream difference between the arms is
discovered during implementation, **execution stops and the protocol returns for
human review.** J1 would no longer isolate stateful episode reasoning, and a
result produced anyway would not answer the registered question.

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

## 5. Prospective cross-fitting geometry

A **nested, subject-disjoint** structure over the 56 TRAIN subjects.

```
OUTER fold k:
  outer-train subjects  ─┬─> fit fold-specific upstream nuisance artifacts
                         │     (U1 calibration; T2 if cross-fit required)
                         └─> INNER split of the same subjects
                               ├─ arm-specific operating-point selection, J1-S
                               └─ arm-specific operating-point selection, J1-W
  outer-held-out subjects ──> apply the frozen fold artifacts
                               produce ONE set of (d_t, p_t, s_t) rows
                               evaluate frozen J1-S   ─┐  identical rows
                               evaluate frozen J1-W   ─┘
```

**The firewall.** No information from an outer-held-out subject may influence the
calibration fitted for that subject, the policy tuning, the stateful parameter
selection, or the memoryless threshold selection. Nesting is what makes the
operating point out-of-sample for the subject it is applied to — the property V1's
LOSO geometry provided and that J1 must reproduce prospectively.

**Why nested rather than flat K-fold.** J1's whole purpose is independent
operating-point selection. A flat K-fold would select the operating point on the
same subjects that assess it, which is the defect J1 exists to remove, transposed.
Nesting is not a preference here; it is entailed by the question.

### 5.1 What is not decided here

The following are **not** established by existing authority and are **not**
invented by this protocol. They are listed in §12 as human decisions:

- outer K, and inner structure;
- fold-assignment seed;
- whether folds are balanced on episode burden, and by what statistic;
- any subject-exclusion rule;
- whether subjects with zero reference episodes are eligible for the *tuning*
  portion.

V1's split generator used deterministic greedy subject-level burden balancing at
seed 2026 with SHA-256 tie-breaking; that is a precedent worth considering but it
governs a 70/15/15 partition, not a J1 fold geometry, and it is not adopted by
default.

## 6. Independent operating-point selection

This is the core of J1.

### 6.1 J1-S selection space

The retained policy's selection space, as V1 defines it:

- quantile levels `Q_WATCH ∈ {0.90, 0.95}` × `Q_EVENT ∈ {0.99, 0.995}`;
- one of three frozen persistence profiles, each fixing `watch_clear_windows`,
  `event_confirm_windows`, `event_release_windows`, `re_event_confirm_windows`,
  `recovery_clear_windows`, `cold_event_confirm_windows`.

**Candidate count: 4 × 3 = 12.** Whether J1 should widen this space beyond V1's
frozen profiles is a human decision (§12); widening it changes the retained
policy's identity.

### 6.2 J1-W selection space

J1-W must be a **credible** memoryless comparator, not a weakened one.

Its space is a per-row decision rule over the common row minus
`elapsed_state_seconds`. At minimum it must be permitted:

- a threshold on `p_t` over a grid at least as fine as J1-S's quantile levels;
- a threshold on `s_t`;
- a threshold on `m2g_detector_score`;
- use of `detector_decision_d_t`;
- conjunctions and disjunctions of the above.

**J1-W is not restricted to reproducing V1's W1 rule.** V1's W1 was a fixed rule
at an inherited operating point; that is the thing J1 exists to stop doing.

**Candidate count: not fixed here.** The grid resolution is a human decision
(§12). Both arms' final candidate counts must be **recorded and disclosed** in the
report so the eventual paper states the dimensionality asymmetry rather than
hiding it.

### 6.3 Fairness constraints — binding

- the **same inner subjects** for both arms;
- the **same cross-fitting structure**;
- the **same optimization endpoint** (§7 primary metric);
- the **same selection discipline** — argmax over the space on inner data, ties
  broken by a prospectively fixed deterministic rule;
- **identical information access**, except the `elapsed_state_seconds` exclusion
  of §3.2, which is disclosed and in J1-W's disfavour;
- **no manual tuning after viewing any outer-held-out outcome**;
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
| Subject denominator | every eligible outer-held-out subject, all folds | this protocol |
| Aggregation | `(1/N) · Σ_i (F1_S,i − F1_W,i)` — the mean of paired per-subject differences | follows V1's subject-macro form |
| Bootstrap unit | subject | V1 T1 analysis plan |
| Replicates | 1000 | V1 T1 analysis plan |
| Seed | 2026 | V1 T1 analysis plan |
| Reselection inside replicates | none | V1 T1 analysis plan |
| Interval level | **HUMAN DECISION** (§12) | not established |
| Undefined per-subject F1 | **HUMAN DECISION** (§12) | not established for the paired form |

V1's convention — subject-macro mean `episode_f1` with a 1000-replicate subject
bootstrap at seed 2026, no reselection — is adopted because it is already
governed, not because it is convenient. Its warning that a data-dependent subset
"is not a subject-macro average, whatever it is labelled" applies here too.

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

## 9. Gate A

| Outcome | Condition |
|---|---|
| **PASS** | Stateful policy retains a practically meaningful advantage under independently tuned operating points, and the uncertainty interval supports the direction. |
| **MIXED** | Point estimate favours stateful reasoning but uncertainty is wide or highly subject-dependent. |
| **FAIL / NEGATIVE** | The fair memoryless policy matches or beats it. |

### 9.1 `HUMAN_DECISION_REQUIRED: J1 practical-effect criterion`

**"Practically meaningful advantage" has no existing authority in this
repository.** The audit searched the V1 statistical and governance documents; the
only effect-size mention is descriptive, in a B4 memory-mechanism plan. No
superiority margin, minimum detectable effect or clinical threshold is defined
anywhere.

**No numerical margin is invented here.** Inventing one would be choosing the
answer's bar without justification, and adding one after results is the failure
this pre-registration exists to prevent.

**Proposed alternative, for human review.** Gate A PASS could require only:

> a positive paired subject-level contrast whose pre-registered uncertainty
> interval supports the direction, with the **magnitude reported separately** and
> no threshold imposed on it.

This is honest about what the programme can currently justify: it has no
alerting-cost model, and W1's report already declines to rank the arms in
monitoring terms for exactly that reason. It moves the practical-significance
judgement to the reader, with the number in front of them.

**This is a proposal. The blueprint's Gate A wording is not modified by this
protocol.** The human decides.

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

## 12. Human decisions required before freeze

| # | Decision | Why it is not made here |
|---|---|---|
| 1 | **J1 practical-effect criterion** (§9.1) | No existing authority. Proposal offered. |
| 2 | Outer K and inner structure | Not established; convenience is not a justification |
| 3 | Fold-assignment seed | Not established for J1 |
| 4 | Episode-burden balancing across folds, and its statistic | Not established; V1's split precedent governs a different object |
| 5 | Subject-exclusion rules | Not established |
| 6 | Handling of subjects with no reference episodes — in tuning, and in the paired difference | V1 handled undefined F1 for a single-arm mean; the paired form is a new case |
| 7 | Bootstrap interval level | V1 fixed replicates and seed but the level is not established for this contrast |
| 8 | J1-W grid resolution and final candidate count | Must be credible; the number is a disclosure obligation |
| 9 | Whether J1-S's space may widen beyond V1's three frozen profiles | Widening changes the retained policy's identity |
| 10 | B4 encoder fitting partition (README verification 1) | Changes what in-sampleness must be disclosed |
| 11 | T2 S4D reusability (README verification 2) | Changes what must be cross-fitted |

**Items 1–9 are scientific. Items 10–11 are read-only code-tracing tasks that
require no data access and could be closed before the others.**

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
