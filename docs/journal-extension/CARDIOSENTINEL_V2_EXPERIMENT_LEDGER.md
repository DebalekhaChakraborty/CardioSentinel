# CardioSentinel V2 — Experiment Ledger

**Status:** Initialized. **No experiment is authorized.**
**Date:** 2026-09-01
**Governing authority:** [`CARDIOSENTINEL_V2_EVIDENCE_AUTHORITY_V1.md`](CARDIOSENTINEL_V2_EVIDENCE_AUTHORITY_V1.md)

A row in this table is a **plan**, not a licence. Appearing here authorizes
nothing. Every workstream must still pass
`QUESTION -> PROTOCOL -> PRE-REGISTRATION -> AUTHORIZATION -> EXECUTION -> REPORT / DECISION`.

This ledger contains **no results, no metrics and no attempt budgets.** An attempt
budget is set by an authorization, and none exists.

## Workstreams

| ID | Workstream | Parent RQ | Current state | Real-data authority | Primary dependency |
|---|---|---|---|---|---|
| **J1** | Fair episode comparator | J-RQ3 | PLANNED / NOT AUTHORIZED | NONE | [protocol](j1/J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1.md) and [pre-registration](j1/J1_PRE_REGISTRATION_V1.md) drafted; **not ready to freeze** — 11 open human decisions |
| **J2** | Patient-memory contribution | J-RQ1 | PLANNED / NOT AUTHORIZED | NONE | P0 + cross-fit design |
| **J3** | Adaptation stress / recovery | J-RQ2 | PLANNED / NOT AUTHORIZED | NONE | J2 / stress registry |
| **J4** | Explanation-state consistency | J-RQ5 | PLANNED / NOT AUTHORIZED | synthetic / structured context protocol required | context freeze |
| **J5** | External validation | J-RQ4 | BLOCKED / NOT AUTHORIZED | NONE | cohort qualification + V2 system freeze |
| **J6** | Physical edge execution | J-RQ6 | PLANNED / NOT AUTHORIZED | physical protocol required | platform qualification |
| **R2** | Representation 2.0 | conditional | CONDITIONAL / NOT AUTHORIZED | NONE | mechanism evidence |

**J5 is BLOCKED, not merely unauthorized.** External confirmation cannot begin
before a cohort is qualified and contamination-reviewed *and* the V2 system is
frozen. Evaluating an unfrozen system on an external cohort produces
V2_DEVELOPMENT evidence wearing a confirmatory label.

**R2 is conditional.** It is not a seventh core research question and is
approached only if mechanism evidence from the core workstreams warrants it.

## Per-workstream record

Empty for every workstream. These fields are filled by execution under
authorization, never in advance.

| Field | J1 | J2 | J3 | J4 | J5 | J6 | R2 |
|---|---|---|---|---|---|---|---|
| Protocol path | draft | — | — | — | — | — | — |
| Protocol digest | — | — | — | — | — | — | — |
| Pre-registration path | — | — | — | — | — | — | — |
| Authorization path | — | — | — | — | — | — | — |
| Attempt budget | — | — | — | — | — | — | — |
| Attempts used | — | — | — | — | — | — | — |
| Execution commit | — | — | — | — | — | — | — |
| Artifact root | — | — | — | — | — | — | — |
| Report | — | — | — | — | — | — | — |
| Decision | — | — | — | — | — | — | — |
| Evidence class | — | — | — | — | — | — | — |
| Claim enabled | — | — | — | — | — | — | — |
| Claim prohibited | — | — | — | — | — | — | — |

A dash means **not yet established**. It does not mean zero, none, or unlimited —
particularly for *Attempt budget*, where an absent value is not permission to run
once.

## State vocabulary

| State | Meaning |
|---|---|
| `PLANNED / NOT AUTHORIZED` | Intended; no protocol frozen, no authorization exists |
| `BLOCKED / NOT AUTHORIZED` | A named precondition is unmet; cannot proceed even if authorized |
| `CONDITIONAL / NOT AUTHORIZED` | Approached only if prior evidence warrants it |
| `PROTOCOL FROZEN` | A protocol exists and is digest-pinned; still not authorized |
| `PRE-REGISTERED` | Pre-registration recorded; still not authorized |
| `AUTHORIZED` | Explicit human authorization naming protocol, data authority and attempt budget |
| `EXECUTED` | Ran under authorization; artifacts promoted |
| `REPORTED` | Report and decision recorded, including negative outcomes |

Nothing in this ledger is beyond `PLANNED / NOT AUTHORIZED`, except J5 which is
`BLOCKED` and R2 which is `CONDITIONAL`.
