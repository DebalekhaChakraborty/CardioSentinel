# CardioSentinel — Evidence Map

**One page. Two halves. The halves are the point.**

This programme produced two kinds of thing, and mixing them is the single
easiest way to misrepresent it. **Part 1 is method** — machinery that constrains
what a claim is allowed to say, and which would still be a contribution if every
number below were different. **Part 2 is findings** — what the numbers actually
say, each with the boundary that travels with it.

A reader deciding what CardioSentinel established should be able to answer *"is
this a method claim or a result claim?"* about any sentence in the reported
record. That is what this page is for.

Companion documents, both fuller and neither a substitute: the **Research
Execution Handbook** for governance and rationale, the **Experiment Catalogue**
for the run-by-run inventory and the consumed ledger.

---

## Part 1 — Methodology

### 1.1 Leakage controls — enforced in code, not asserted in prose

| Control | How it is enforced | Where |
|---|---|---|
| **Labels never reach the state transition** | A 15-entry deny list, checked at input binding: `label`, `target_family`, `subject_outcome`, `episode_identity`, `future_row`, `future_score`, `gru_score`, `s4d_binary_decision`, `t2_frozen_reporting_threshold`, `u_star_dev`, `u_star_deploy`, `challenge_family_identity`, `m2_gate_outcome`, `m2_update_admitted`, `test_derived_quantity` | `T1_FORBIDDEN_TRANSITION_INPUTS`, `neural/t1_protocol.py:170` |
| **Only frozen row inputs are readable** | A 9-entry allow list; anything outside it raises | `T1_ALLOWED_ROW_INPUTS`, `neural/t1_protocol.py:158` |
| **Patient identity is never a predictive feature** | `stable_id` is *on* the row and `next_state` never reads it. Its only other use is deterministic tie-breaking, so quantiles are input-order-independent | `T1_THRESHOLD_TIE_ORDER`, `t1_protocol.py:202` |
| **No future information** | `next_state` is one pure causal step: current row, nothing ahead of it | `t1_protocol.next_state` |
| **Subject-disjoint folds** | 12 folds, 12 distinct subjects | fold manifests |
| **Thresholds frozen upstream of measurement** | `thresholds_generated_here: false`, `selection_performed_here: false` | promoted fold-selection artifacts |

**`stable_id` is in the allow list and is still not a feature.** Both halves of
that sentence have to be stated together or the allow list reads as a
contradiction.

### 1.2 Pre-registration — including when it was wrong

Every measured read in this programme was preceded by a merged plan that fixed
the reporting shape before any value was visible.

| Analysis | Plan merged first | What the discipline cost or caught |
|---|---|---|
| T1 evidence | `T1_EVIDENCE_ANALYSIS_PLAN_V1.md` | Fixed the primary estimand before the values existed. The pooled figure is **not** what the interval brackets, and the report says so |
| T2 arm comparison | `T2_ARM_COMPARISON_ANALYSIS_PLAN_V1.md` + amendment V1.1 | The plan stays unedited; the amendment carries the change, so the pre-read document survives as evidence of what was pre-read |
| W1 comparator | `W1_WINDOW_COMPARATOR_PREREGISTRATION_V1.md` | **Two registered predictions were refuted and reported as refuted** |
| U1 reliability | `U1_CALIBRATION_RELIABILITY_ANALYSIS_PLAN_V1.md` | Fixed the sign convention and the degeneracy statistics in advance. The report records that one of those statistics was the **wrong** choice, and declines to substitute a better one |

**The strongest evidence that this machinery is load-bearing rather than
decorative is W1.** Its §5 mechanism claim was half false — T1's `EVENT`
hysteresis produces *more* alert rows in *fewer, longer* runs, the opposite of
what was registered — and its aggregate prediction of a near-zero difference was
refuted outright. Both were reported as written. **A pre-registration's
reasoning can be wrong while its discipline is right**, and a programme that
only ever reports confirmed predictions has not demonstrated the difference.

The U1 case is the quieter version: having seen the values, the right degeneracy
statistic was obvious and the plan had not named it. It was recorded as a
limitation rather than added, because choosing a statistic after seeing the
values is precisely what the pre-registration existed to prevent.

### 1.3 One-shot gates — consumed, never reset

**A one-shot budget is an access that can be taken once.** Not a policy that can
be relaxed, and not a flag that can be re-read.

- **All fifteen budgets are spent.** The last of them, the B4 / neural sealed
  test, was consumed on 2026-08-25, and the single `TEST_ATTEMPT.json` in the
  tree is its receipt: `attempt_sequence 1`, `attempt_status COMPLETE`,
  `repeat_attempt_permitted false`. **There is now no budget left to protect and
  none left to spend** — from here the machinery protects the *record* of
  accesses already taken rather than an unspent one.
- ***"TEST is sealed" is half true.*** B0–B3 spent theirs in Phase 3B-1 — four
  `test_evaluation_attempt.json` receipts are what a consumed chain looks like.
- **Spent flags are not live permissions.** `T1_CONTINUATION_AUTHORIZED` and
  `T2_OUTER_VALIDATION_EXECUTION_AUTHORIZED` both read `True` on disk **and both
  runs are consumed.** The re-run guard is the persistence claim, not the flag.
- **Failures are consumed too, and are kept.** The T1 canonical attempt failed
  post-claim at stage 24 and carries **zero locks**, which is correct: a lock
  would mean it completed. M1-v1 failed twice, M2 failed twice. Six failure
  records, none silently retried.
- **No automatic retry, under any circumstance.**

### 1.4 Provenance — and negative capability

| Mechanism | What it proves |
|---|---|
| Digest-bound artifacts | Every published number traces to a SHA-256'd file and the commit the analysis ran at |
| Frozen dependency environment | 335 packages, `installed_packages_sha256 = b0fd6ea…`, Python 3.12.6, asserted by the code that consumes it |
| Tracked report generators | `scripts/provenance/` holds the byte-identical script that produced each merged document, so derivations are re-runnable rather than described |
| Immutable run directories | Consumed attempt and continuation directories are both frozen |
| **Zero-capability counters** | The T1 measurement **consumed a persisted trace and ran no model**: `fold_evaluations: 0`, `policy_selection_calls: 0`, `state_machine_invocations: 0`, `threshold_generation_calls: 0`, alongside `test_accessed: false` and `sealed_test_state: unopened` |

**Negative capability is the part that is unusual.** Conventional testing shows
what code *does*. These artifacts prove what the code *did not do* — did not
load a model, did not regenerate a threshold, did not touch the sealed test —
and they prove it from counters written by the run itself rather than from an
author's assurance.

---

## Part 2 — Scientific findings

Each row carries its boundary. **The boundary is not a caveat appended to the
finding; it is part of the finding.**

### 2.1 T1 — episode detection, measured and bounded

**Subject-macro mean `episode_f1` = 0.2524**, 95% subject-bootstrap
**[0.0826, 0.4415]**, on 12 held-out LTSTDB subjects, cross-fitted and
subject-disjoint.

**Boundary.** Seven of twelve subjects score zero for **two incomparable
reasons**: three have no reference episodes at all, so their zero is a
false-alarm penalty; four missed real episodes. **They push the operating point
in opposite directions** — the first group improves with *fewer* predicted runs,
the second with *more* — and a single averaged score conceals that tension.
Latency is a **signed offset**, not a delay, and a negative offset does **not**
establish anticipation: matching is overlap-only with no tolerance window and no
run durations are stored.

### 2.2 T2 — the contrast is the selection rule, and its interval spans zero

**`pooled_auprc_difference` = 0.093215** in favour of the S4D arm, tie tolerance
0.002000. **95% paired subject-bootstrap: [-0.015229, 0.148951] — includes
zero.**

**Boundary.** This difference **is** the selection criterion
(`selection_basis: pooled_primary_validation_auprc`). The paired contrast is
unbiased — same held-out rows, rule fixed in advance — but the winner's absolute
figure is not, because S4D was chosen for having the higher value on this very
set. Say *"the predefined selection rule selected S4D based on the observed
validation contrast."* Never *"S4D achieved superior AUPRC."* T2 scores are
**uncalibrated**: `score_is_calibrated_probability: false`, and a bounded
sigmoid is not a probability.

### 2.3 U1 — RQ3 answered negatively, and the retention is split

**The selective router at `c_star = 0.90` was evaluated and rejected**
(`Retained: false`): at that operating point it disproportionately escalates
positive-label cases, and the exit gate *"risk decreases sensibly as coverage
falls"* was not met. **Platt calibration is retained.**

**This is a real result and should be reported as one.** It is also the
programme's only *clean* answer — no operating-point bound, no selection
conditioning.

**Boundary.** The rejected router is **preserved, not deleted**; preservation is
provenance, not retention. Edge/cloud routing **does not exist**, and any
document claiming it is complete is wrong. Separately, the retained calibrator's
low pooled ECE (0.016991 against the reference's 0.063844) is carried by the
near-zero region: equal-width bin 0 holds **398,513 of 473,897 rows**, and above
bin 3 the calibrator predicts *above* the observed positive rate.

### 2.4 W1 — RQ4 supported, bounded at one operating point

**Subject-macro `episode_f1` 0.2524 (state machine) against 0.0603 (memoryless
window rule)**, difference **0.1921**, 95% paired subject-bootstrap
**[0.0505, 0.3455] — excludes zero.** The state-machine arm reproduces the
published T1 value exactly, which is what makes this a comparison rather than a
re-measurement.

**Boundary, and it is load-bearing.** Both arms ran at thresholds selected
**with the state machine in the loop**: the promoted policy `qw0.9_qe0.99_FAST`
binds the quantile levels together with the `FAST` persistence profile, whose
`event_confirm_windows = 2` is a state-machine parameter a memoryless rule does
not implement. **A well-tuned memoryless rule was never tested.** RQ4 reads
**"Supported (bounded)"**, never bare "Supported".

**What W1 does not answer.** `s4d_temporal_evidence_s_t` feeds **both** arms, so
W1 says nothing about what the S4D architecture contributed — the question a
careful reader will actually ask.

### 2.5 External validation — a negative finding, not a gap awaiting effort

**No drop-in independent cohort exists in the public record.** EDB is the only
other ST-episode resource and is partly contaminated; STAFF III has gold-standard
occlusion timing and fails on five axes. EDB is a **secondary** cohort, enforced
in code, and **may never be called external**.

**The cold-start trap.** 95.5% of T2 validation rows sit past the first hour and
the first-five-minutes stratum scores AUPRC **0.0015**. EDB records are ~2-hour
excerpts against LTSTDB's ~24 hours, so roughly half of every EDB record falls in
the warm-up regime. **An unstratified EDB number would be bad for a reason that
has nothing to do with generalization.**

### 2.6 Three denominators that were not what they looked like

| Experiment | Headline | The denominator |
|---|---|---|
| T1 | subject-macro `episode_f1` 0.2524 over 12 subjects | defined for 12, **meaningful for 9** |
| T2 | subject-macro AUPRC 0.428152 | a mean over **9 of 12**; `non_contributing_subject_count: 3` |
| U1 | ECE equal-width 0.016991 | carried by one bin — **398,513 of 473,897 rows** |

**Three experiments, three metrics, three different checks that found them, and
in every case the arithmetic was correct.** The metric itself signalled nothing.
This is the finding that generalises past ECG: **a scalar summary over a
heterogeneous population needs its contributing-unit count reported beside it as
a matter of course**, not as a caveat added when someone happens to look.

---

## Part 3 — Reading the two halves together

**What is answered:** RQ3, negatively and cleanly. RQ4, affirmatively and
bounded. RQ2 partially. **Four of seven remain open, and every one of them needs
a run, not an analysis.**

**Why that is not a weakness of the method.** The programme spent all fifteen
one-shot budgets and produced two answers, one rejection, six failure records,
and four refuted-or-corrected predictions. The fifteenth — the sealed test —
**answered no research question at all**: it characterises the selected encoder
on held-out subjects and moved nothing from open to answered. **That ratio is
what honest measurement looks like** when the machinery is built to prevent the
alternative.

**The trap this page exists to prevent.** Every Part 2 finding is small, bounded
or negative. Every Part 1 mechanism is complete and demonstrated. The temptation
is to let Part 1's confidence bleed into Part 2's numbers — to write *"a
rigorously validated detector"* when what exists is a rigorously *bounded* one.
**The rigour is in the boundaries, not behind them.**
