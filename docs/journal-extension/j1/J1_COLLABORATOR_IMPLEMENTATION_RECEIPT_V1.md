# J1 — Collaborator Implementation Receipt, V1

# `QUALIFICATION CANDIDATE — NOT AUTHORIZED`

**Date:** 2026-09-01
**Protocol:** [`J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1.md`](J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1.md), FROZEN
**Instrument:** [`J1_EXECUTION_INSTRUMENT_SPEC_V1.md`](J1_EXECUTION_INSTRUMENT_SPEC_V1.md), V1

---

## What this records

The execution instrument named seven collaborators in its pre-claim capability
gate and shipped all of them as qualification fixtures. **All seven now satisfy
the gate**, implemented against the frozen protocol. **No environment is authorized, no
authorization document exists, no attempt is claimed, and nothing here can
run** — the preflight gate refuses before any of this is reached.

| Collaborator | Gate methods | State |
|---|---|---|
| **`fold_allocator`** | `allocate` | **real — `folds.py`, §5.1; gate adapter added** |
| `calibration_fitter` | `fit_inner`, `fit_outer` | real — `calibration.py`, §5.3.1, §5.9, §5.10, §5.11 |
| `threshold_deriver` | `derive` | real — `thresholds.py`, §5.4 |
| `selection_ranker` | `rank` | real — `selection.py`, §6.5 |
| **`candidate_evaluator`** | `evaluate_inner`, `evaluate_outer` | **real — `evaluation.py`, §2.1, §2.2, §5.5, §5.6, §5.9** |
| **`bootstrap`** | `resample` | **real — `statistics.py`, §7.1.0; gate adapter added** |
| `provenance_sink` | `open_attempt`, `promote` | interface; its value comes from the authorization |

**Two collaborators were listed as real and were not gate-shaped.** `folds.py`
and `statistics.py` held the frozen algorithms as module functions, so no object
exposed `allocate` or `resample` with an attestation and the gate could never
have passed. Thin adapters now do, over the same functions — not second
implementations.

## 1. Calibration fitter — the population boundary is the whole point

**The U1 Platt procedure is inherited, not reimplemented.** `calibration.py`
calls `neural/u1_calibration.fit_calibrator`. Refitting the calibration
mathematics inside J1 would change a nuisance quantity the question depends on,
and two implementations of one frozen procedure eventually disagree.

What J1 adds is the boundary. §5.11 requires a structural proof that
`fit_subjects ∩ heldout_subjects == ∅` and states that **no runtime flag may
bypass it**. The two populations are therefore separate arguments at every entry
point, and there is no `force`, `allow_overlap`, `strict` or `skip_disjointness`
parameter — asserted by test, not by intention.

**`fit_inner` and `fit_outer` are separate methods, not one method with a level
argument**, because §5.10's entire purpose is that the two levels produce
quantities that must not be interchangeable. A level *argument* is a value a
caller can pass wrongly.

**Fit-side and held-out application are separate methods too.**
`fit_side_probabilities` and `oof_probabilities` return distinct types and each
refuses the other population *by subject identity*, so the §5.10 rule is
enforced at run time and not only by static typing. A fit subject cannot be
handed a value named held-out, because for that subject the name would be false.

Every fit carries a `CalibrationProvenance` with all eight §5.11 bindings.

## 2. Threshold deriver — and why a frozen rule is re-stated

§5.4 says to preserve the inherited empirical-order-statistic method.
`t1_protocol.empirical_order_statistic` **is** that method, and it is one of
`t1_protocol`'s forbidden entry points for J1, because T1/W1 were developed on
the 12 VALIDATION subjects J1 may not reopen.

**Read together, the two frozen constraints admit exactly one implementation:**
the same arithmetic, computed inside J1, over J1's own fit population. So
`k = ceil(q · N)`, one-based, no interpolation, ties broken by `stable_id`, is
re-stated rather than imported — and a qualification test asserts it agrees with
the inherited implementation on shared inputs, which is what keeps the
re-statement honest rather than a second opinion.

**A held-out row in the threshold population is a hard failure, not a silent
drop.** Its presence means the caller assembled the wrong population, and
discarding it quietly would hide that at exactly the point §5.4's guarantee is
established.

## 3. Selection ranker — one trap worth recording

§6.5 preserves V1's `policy_sort_key`, which is also a forbidden entry point, so
the same doctrine applies: the arithmetic is re-stated and the frozen *data* is
imported rather than copied.

**The profile tie-break reverses if it is taken from the wrong tuple.** J1's
registry enumerates persistence profiles `("FAST", "MED", "SLOW")`. V1's frozen
tie-break preference is `T1_PERSISTENCE_PROFILES`, ordered *most cautious
first* — `CONSERVATIVE, BALANCED, FAST`. **The two are exact opposites**, both
are three-element tuples of profile labels, and both accept `.index()` without
complaint. §6.5 names V1's.

Taking it from the enumeration tuple would invert the preference among tied
candidates and nothing downstream would look wrong. `selection.py` imports
`T1_PERSISTENCE_PROFILES` and matches on profile name — J1 calls the middle
profile `MED`, V1 calls it `BALANCED`, and they are the same profile — and a
test asserts the two orders are opposites so the trap cannot quietly reappear.

## 4. The evaluator, and the line between inherited and re-stated

`evaluation.py` closes the last fixture. The line it draws is the one this
programme keeps having to draw, so it is worth stating exactly.

**Inherited, because they are not operating-point functions.**
`group_reference_episodes` and `match_runs_to_episodes` live in `t1_protocol`
but are **not** among J1's forbidden entry points, and they are not that kind of
function: they are measurement conventions over reference truth, they resolve no
operating point, and §7.1.1 says V1's convention is *preserved unchanged*. They
are imported. Re-stating them where re-statement is not required would be a
second opinion about a frozen measurement.

**Re-stated, because `next_state` is forbidden.** The §2.1 state machine —
`NORMAL → WATCH → EVENT → RECOVERY`, the three evidence predicates, the streak
counters, escalation priority, and state held across an unavailable row — is
implemented inside J1 and **pinned to the inherited implementation across every
state, profile, streak shape and row in a sweep of over 3,000 comparisons**.

### The reading of §2.1 that would have changed the policy under test

§2.1 gives EVENT evidence as `d_t AND p_t ≥ p_event AND s_t ≥ s_event`. The
retained implementation **relaxes the S4D term before `T1_COLD_START_SECONDS`**,
because T2 recorded zero thresholded sensitivity in the first five minutes and
demanding it there makes early EVENT unreachable by construction. §2.1 also says
the retained state semantics are **not modified**.

Read together, §2.1's line is the *mature-stream* form and the cold-start
relaxation is part of what is retained. **Implementing §2.1's prose literally
would silently change the policy J1 exists to test** — a fair comparator built
against a subtly different stateful arm answers a different question. A test
pins both the cold and mature branches to the inherited predicate.

### Boundaries the evaluator holds

- a subject outside the held-out population is refused — a candidate is never
  applied to the population its thresholds came from;
- exactly one evaluation per stream, per §5.5's postcondition;
- **state never crosses a stream**: the evaluator resets per stream rather than
  trusting a caller to hand them over one at a time;
- an unavailable row is decided positive by **neither** arm — J1-S holds state
  and resets streaks, J1-W emits `False`, and neither manufactures evidence;
- a population with no primary-F1-eligible subject **refuses rather than
  imputes**; §7.1.1 proves an undefined F1 unreachable inside the primary
  cohort, so encountering one is an apparatus fault, not a result.

## 5. The graph can finish. J1 still may not start.

`require_execution_capability` now passes over all seven collaborators with a
synthetic provenance sink — the first time the canonical graph has been provable
end to end.

**This proves capability, never permission.** The gate reads no data and
consults no authorization, and a capability attestation never implies one. The
same test file asserts that preflight still refuses with
`authorization absent`.

## Verification

| | |
|---|---|
| Evaluator tests | `test_j1_candidate_evaluator.py` — **23 passed** |
| Earlier collaborator tests | `test_j1_calibration_and_thresholds.py` **38**, `test_j1_selection_order.py` **17** |
| Instrument tests | `tests/journal_extension/` — **306 passed** |
| Governance tests | `tests/reproducibility/` — **52 passed** |
| Sealed-test identity | `tests/neural/test_b4b_sealed_test_identity.py` — **23 passed** |
| Shared-interpreter condition | all three together — **381 passed** |
| Lint | `ruff check .` — clean |

Every threshold derivation is exercised against **all 12 J1-S and all 206 J1-W
frozen candidates**: a candidate the deriver cannot serve would be an unrunnable
fold.

## Status

| | |
|---|---|
| Collaborators | **7 of 7 satisfy the capability gate; no fixture remains** |
| Environment | **NONE SUBMITTED** |
| Authorization | **ABSENT** |
| J1 | **`PRE-REGISTERED — NOT AUTHORIZED`** |

`real_data_authority = NONE` · `attempt_budget = NOT ESTABLISHED` ·
`execution_authorized = FALSE`

No physiological data, annotation, reference-episode count, fold, calibrator,
threshold, candidate selection or result was accessed or generated by the work
this receipt records. Every fixture in the qualification tests is fabricated.
The frozen protocol, pre-registration and freeze receipt are byte-unchanged.
