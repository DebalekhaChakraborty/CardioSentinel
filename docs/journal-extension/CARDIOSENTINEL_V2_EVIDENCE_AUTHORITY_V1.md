# CardioSentinel V2 — Evidence Authority, V1

**Status:** Frozen governance document. Grants no experimental authorization.
**Date:** 2026-09-01

This is the document that decides what a V2 result is allowed to mean. If it
conflicts with a plan, a roadmap, an issue or a convenience, this wins.

---

## A. Evidence classes

| Class | What it is | Can support | Cannot support |
|---|---|---|---|
| **V1_HISTORICAL** | Measurements completed under the V1 programme, budgets spent | Statements about **what V1 measured**; motivation for a V2 question; a comparator's *design* rationale | Any V2 confirmatory claim. It is not fresh and cannot be made fresh. |
| **V2_DEVELOPMENT** | Prospective V2 work on TRAIN-authorized data under a workstream protocol | Design decisions, mechanism evidence, hypothesis generation, tuning of V2 components | Confirmatory performance claims. Development data cannot confirm the system developed on it. |
| **V2_EXTERNAL_CONFIRMATORY** | Evaluation of a **frozen** V2 system on a qualified, contamination-reviewed cohort never used in development | Transfer and generalization claims, bounded to the evaluated cohort | Claims beyond that cohort; any claim if the system was not frozen first. |
| **V2_SYNTHETIC_ENGINEERING** | Synthetic or structured contexts built to exercise a mechanism | Engineering and guard behaviour — that a control fires when it should | Physiological, clinical or population claims of any kind. |
| **V2_PHYSICAL_MEASUREMENT** | Measurement on hardware that acquires or replays ECG under physical constraint | Latency, throughput, power, thermal and feasibility claims **for the measured platform** | Clinical utility, wearable readiness, or claims about platforms not measured. |

**A claim inherits the weakest class it depends on.** A performance number
computed on development data is V2_DEVELOPMENT even if a confirmatory protocol
quotes it.

## B. V1 inheritance policy

> **Reuse of an implementation is not reuse of its evidence.**
>
> Running V1's code in a V2 experiment produces **new** evidence, governed by the
> V2 protocol that ran it. It does not import V1's old results, and it does not
> re-open what those results consumed. The converse also holds: inheriting a
> mechanism does not inherit permission to claim what that mechanism once showed.

| V1 object | May V2 use it? | In what role? | Forbidden interpretation |
|---|---|---|---|
| **V1 source code** | Yes | Implementation to build on or run under a V2 protocol | That V1's results transfer with the code |
| **Retained model architecture** | Yes | Starting architecture; a comparator to beat | That the architecture is already validated for V2's question |
| **Retained checkpoints** | Yes, under a protocol that permits it | Initialization; a frozen comparator | That checkpoint metrics are fresh V2 evidence |
| **V1 TRAIN subjects** | Yes, with a workstream-specific protocol | V2 development data | That TRAIN performance is confirmatory |
| **V1 VALIDATION** | **No** as confirmation | Historical record only | That it can serve as a fresh V2 validation set |
| **V1 TEST (sealed, B4)** | **No.** Consumed 2026-08-25, attempt 1 of 1 | Historical record only | That any re-reading, re-scoring or re-partitioning yields new evidence |
| **V1 thresholds** | Yes as a recorded starting point | A value a V2 protocol may adopt or supersede | That an inherited threshold is tuned for V2's question — J-RQ3 exists because it is not |
| **V1 experimental results** | Yes | Motivation, comparator design, related work | Confirmation of any V2 claim |
| **V1 negative findings** | Yes | Motivation, and a standing constraint on claims | That they may be revisited until they turn positive |
| **V1 runtime** | Yes | The system under test, or its baseline | That runtime behaviour observed in V1 is observed in V2 |
| **V1 evidence graph** | Yes | Provenance machinery and lineage | That lineage of a V1 artifact confers V2 standing |
| **V1 explanation guard** | Yes | The guard under study in J-RQ5 | That V1's guard evaluation is J-RQ5's result |
| **Failed / quarantined attempts** | Yes, as record | What was tried, what failed, why | That a failed attempt may be silently retried as if new |

## C. Data authority

- **Future V2 TRAIN access requires a workstream-specific protocol.** Not the
  blueprint, not this document, not the ledger.
- **Historical VALIDATION and TEST are not available as fresh confirmatory sets.**
  There is no procedure — re-partitioning, re-scoring, cross-fitting or otherwise
  — that converts spent evidence into fresh evidence.
- **External data must pass qualification and contamination review before any
  confirmatory evaluation.** A cohort that overlaps development data is not
  external, whatever it is called. V1 recorded this for EDB, which is a
  *secondary* cohort partly contaminated with LTSTDB and may never be described
  as external.

## D. Execution states

```text
QUESTION
  -> PROTOCOL
    -> PRE-REGISTRATION
      -> AUTHORIZATION
        -> EXECUTION
          -> REPORT / DECISION
```

**No experiment becomes authorized because it appears somewhere.** Not in the
blueprint, not in the charter, not in the ledger, not in source code, not in an
issue, not in a roadmap, not in a handoff, and not in this document. Authorization
is an explicit human act naming the protocol, the data authority and the attempt
budget.

## E. Attempt policy

Every authorization names an **attempt budget** before execution. Failures are
classified, and the classification decides what may follow:

| Classification | Meaning | May it be retried? |
|---|---|---|
| **INFRASTRUCTURE** | Crash, environment, I/O — no scientific quantity produced | Yes, same authorization, recorded |
| **PROTOCOL_DEFECT** | The protocol was wrong or under-specified | Only under a **new** protocol and a new authorization |
| **SCIENTIFIC_NEGATIVE** | Ran correctly, result is not what was hoped | **No.** This is a result, not a failure |

**Automatic scientific retry is prohibited.** A run that completes and disappoints
has spent its budget. Re-running until an outcome improves is the mechanism this
policy exists to prevent.

## F. Negative-result policy

**Negative results are first-class evidence.** They are reported as results, in
the same detail and with the same standing as positive ones.

A negative result must not trigger uncontrolled tuning, quiet re-specification,
comparator substitution, or metric replacement. If a negative result motivates a
new question, that question enters at `QUESTION` and earns its own protocol,
pre-registration and authorization — it does not inherit the failed one's budget.

V1's RQ3 is a negative finding reported as a result. That precedent binds V2.

## G. Structural V1 protection — requirement, not implementation

V2 tooling **should eventually make accidental access to consumed V1 TEST
scientifically inexpressible** — refused at the level of what the code can
represent, not merely forbidden by policy that a future contributor may not read.
V1 established the pattern with negative-capability proofs over AST and
`sys.modules`, and with a selection-identity check that must pass before any
sealed access is attempted.

**This task defines the requirement and implements none of it.** No new tooling,
no new guard, no change to existing guards. Building it is a separate,
explicitly authorized piece of work.
