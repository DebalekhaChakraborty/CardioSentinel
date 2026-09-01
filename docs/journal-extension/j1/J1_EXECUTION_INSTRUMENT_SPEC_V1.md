# J1 — Execution Instrument Specification, V1

# `QUALIFICATION CANDIDATE — NOT AUTHORIZED`

**This is an implementation specification, not a scientific protocol.** It says
how the frozen protocol is realized. It may not change what the protocol
requires, and where the two disagree the frozen protocol wins and the code is
wrong.

Bound documents, unmodified by this work:

| Document | SHA-256 |
|---|---|
| `J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1.md` | `cedb152eef187fd573212daaad7492242d6963d9b9de897ed1312cde0a976cf0` |
| `J1_PRE_REGISTRATION_V1.md` | `1b6eb6645bf2449e4b76fb40b5ee7e44250474bd08c4a1c42ba79c00dc45fcd1` |

**Building this apparatus authorizes nothing.** J1 remains `PRE-REGISTERED`. No
authorization document exists, no attempt budget is set, and the production
entry point refuses before claiming anything.

---

## 1. Two principles that had to survive the port

From `neural/t1_capability_gate` and `neural/t1_continuation_gate`:

> **Capability to finish is different from permission to execute.**

> **Forbidden scientific actions must be mechanically impossible or mechanically
> detectable, not merely prohibited in prose.**

## 2. V1 precedent audit

| V1 pattern | J1 | Why |
|---|---|---|
| `t1_capability_gate` — three checks: signature `bind`, positive attestation allowlist, AST reachable-return proof | **ADAPTED** | Same invariant: *an attempt must never be consumed by an execution path that cannot complete.* Collaborator names and second-phase methods differ. |
| Capability gate never reads the authorization flag | **REUSED** | The separation is the point. |
| `t1_continuation_gate` — three independent layers | **REUSED** | Structural, runtime, evidence. |
| *"Never by scanning source text"* | **REUSED** | This module names every function it forbids; a text scan matches the guard itself. V1 recorded that false positive five times. |
| Runtime instrumentation rebinding attributes in-process, restored in `finally` | **REUSED** | The frozen module's file is never modified. |
| `t1_persistence` state semantics | **NOT APPLICABLE** | J1 does not modify the retained state machine; it selects its operating point. |
| `t1_execution_spec` stage numbering | **ADAPTED** | J1's stage order differs — it has a nested inner/outer barrier V1's single-level run did not. |
| V1 edge runtime's VALIDATION-only resolver | **NOT APPLICABLE, AND NOT RELAXED** | J1 is implemented in its own namespace. No V1 guard was touched. |

## 3. Stage order — structurally enforced

```text
freeze binding
→ authorization verification
→ git / environment verification
→ negative-capability proof
→ execution-capability proof
→ provenance sink validation
→ attempt-budget validation
→ atomic attempt claim
→ ONLY THEN scientific data access
```

**No physiological datum, annotation-derived quantity, score artifact or fold
metadata may be opened before the attempt is claimed.** The run directory *is*
the claim; claiming is atomic and refuses reuse.

In the repository's current state `run_preflight` stops at stage 2 with
**`J1 authorization absent`**.

## 4. Modules

| Module | Responsibility |
|---|---|
| `freeze_binding` | Frozen digests as compiled-in constants. Mismatch is `INVALID_EXECUTION`, never a new baseline. |
| `partition_authority` | `V1_TRAIN_ONLY`. No enum, no `partition:` argument, no other constructor. |
| `authorization` | The schema. Every field required, no defaults. Instantiates nothing. |
| `capability_gate` | Can the graph finish? Never consults permission. |
| `negative_capability` | Layers 1 and 2, plus the counters Layer 3 persists. |
| `visibility` | The monotonic latch of protocol §11. |
| `rows` | The eight-field arm-neutral row; four distinct calibration types. |
| `folds` | The frozen deterministic allocator. |
| `candidates` | J1-S 12, J1-W 206, stable IDs, pure `row → bool` rules. |
| `choreography` | Nested inner-OOF assembly with disjointness asserted. |
| `statistics` | Endpoint, percentile bootstrap, Gate A. |
| `provenance` | Attempt-claim contract and artifact schema. |
| `preflight` | The unarmed production entry point. |

## 5. Negative capability

**Layer 1 — structural.** AST and resolved import graph over every J1 module.
Forbidden entry points are named individually rather than banning whole modules,
because J1 legitimately imports `t1_protocol` for frozen primitives:

- `b4b_sealed_test.{verify_selection_identity, load_selected_model, resolve_selected_run_dir, read_selection_record}`
- `edge/artifacts.{resolve_t1_policy, load_frozen_artifacts}` — the validation-identity resolvers
- `t1_protocol.{candidate_policies, empirical_order_statistic, policy_sort_key, next_state}`

**Layer 2 — runtime.** `b4b_sealed_test` need never load, so its absence from
`sys.modules` is proven directly. Entry points in modules that must load are
instrumented with record-then-refuse wrappers, restored in a `finally`.

Counters, each of which must remain zero — a non-zero counter is a stop, not a
warning: `validation_subject_accesses`, `test_subject_accesses`,
`sealed_test_calls`, `v1_validation_operating_point_resolutions`,
`forbidden_partition_resolutions`, `protocol_digest_bypasses`,
`authorization_bypasses`.

**Layer 3 — evidence.** Every attempt receipt persists these attestations and
their zero counters, so the record proves what did *not* happen.

## 6. Calibration boundary

Four distinct types, not a string flag, so a fit-side probability cannot satisfy
an interface expecting assessment evidence:

`InnerFitCalibratedProbability` · `InnerOofCalibratedProbability` ·
`OuterFitCalibratedProbability` · `OuterOofCalibratedProbability`

`assessment_row` accepts only `outer_oof_p_t`, named so that a caller holding a
fit-side value must rename it deliberately rather than pass it along.

## 7. What this task did not do

No authorization document. No attempt budget. No attempt claimed. No fold
manifest for real subjects. No calibrator, threshold, candidate selection,
bootstrap artifact or run directory. No physiological data, annotation or
reference-episode count was read. No V1 guard was relaxed and no V1 TEST or
VALIDATION artifact was touched.

## 8. Remaining blockers before authorization

1. **No environment authority exists.** The preflight requires an
   `environment_sha256` match, but the V2/J1 programme has not yet defined what
   authoritative environment identity is. A mutable developer environment must
   not be silently promoted to scientific authority.
2. **The provenance sink is an interface, not a choice.** Its value comes from
   the authorization.
3. **The real TRAIN subject manifest is supplied by the authorization**, not
   discovered by the instrument — reading the split here would be
   physiological-adjacent access before the claim.
4. **Collaborator implementations are qualification fixtures.** The real fold
   evaluator, calibration fitter and threshold deriver are not written.
