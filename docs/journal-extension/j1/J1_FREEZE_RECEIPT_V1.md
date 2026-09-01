# J1 — Freeze Receipt V1

**Date:** 2026-09-01

## Human decision

# `J1 FREEZE APPROVED`

The scientific design passed human scientific review. **This receipt performs the
governance freeze only. It does not authorize execution.**

## Scientific candidate reviewed

| | |
|---|---|
| Pull request | **#140** — *P0-B / J1: preregister the fair stateful-vs-memoryless comparator design* |
| Reviewed head | `9870254b39e16c237f698795991a641836f6361f` |
| Merge commit | `82315ad67de9497274e286daae670f2587e27781` |

The merged content is **byte-identical** to the reviewed head for every J1
document. The merge introduced no reconciliation drift, so there is no difference
between what was reviewed and what is bound here.

## Frozen protocol

| | |
|---|---|
| Path | `docs/journal-extension/j1/J1_FAIR_EPISODE_COMPARATOR_PROTOCOL_V1.md` |
| **SHA-256** | `cedb152eef187fd573212daaad7492242d6963d9b9de897ed1312cde0a976cf0` |
| Byte count | 42,863 |
| Line count | 891 |
| Git blob | `c32f7e236112…` |
| Commit containing the frozen bytes | `52066be2fdf8c5c8b3fded315dd738ff03a559ce` |
| State | `FROZEN PROSPECTIVE PROTOCOL — NOT AUTHORIZED` |

## Frozen pre-registration

| | |
|---|---|
| Path | `docs/journal-extension/j1/J1_PRE_REGISTRATION_V1.md` |
| **SHA-256** | `1b6eb6645bf2449e4b76fb40b5ee7e44250474bd08c4a1c42ba79c00dc45fcd1` |
| Byte count | 13,658 |
| Line count | 188 |
| Git blob | `ce347da84f08…` |
| Commit containing the frozen bytes | `d75ac9b075233ffa1404378a719e4d0e477d5d3e` |
| State | `PRE-REGISTERED — NOT AUTHORIZED` |

**Digest method.** `SHA-256` over the **raw committed bytes**. No canonicalisation,
no whitespace normalisation, no newline rewriting, no Markdown rendering before
hashing. Each digest was computed and then independently recomputed, and the two
agreed.

**Neither document contains its own digest.** A self-referential digest cannot be
satisfied; the binding lives here instead.

### Amendment 1 — 2026-09-01, governance metadata only

The pre-registration's status table read `Attempt budget | none`, which asserts an
established budget of zero. No budget has been set at all; setting one belongs to
the later authorization. Corrected to **`NOT ESTABLISHED`**, matching this
receipt's own non-authority table and the ledger's dash.

**One table cell changed. No scientific content was touched**, and the frozen
protocol is byte-unchanged at `cedb152e…`. The pre-registration was re-hashed
because it is digest-bound:

| | Before | After |
|---|---|---|
| SHA-256 | `88dadd88e0593641…` | `1b6eb6645bf2449e…` |
| Bytes | 13,570 | 13,658 |
| Lines | 188 | 188 |
| Commit | `52066be…` | `d75ac9b…` |

This amendment is recorded rather than applied silently: the superseded digest
stays visible so the binding history is auditable. **The immutability rule below
governs *scientific* byte changes, which this is not** — it changed a governance
state label that was stronger than the governing documents allowed.

## Evidence class

`V2_DEVELOPMENT`

## State

`PRE-REGISTERED`

```text
QUESTION              complete
PROTOCOL              FROZEN
PRE-REGISTRATION      complete / digest-bound
AUTHORIZATION         ABSENT
EXECUTION             NOT PERMITTED
REPORT / DECISION     nonexistent
```

## Explicit non-authority

| | |
|---|---|
| `real_data_authority` | **NONE** |
| `attempt_budget` | **NOT ESTABLISHED** |
| `execution_authorized` | **FALSE** |
| `scientific_attempts_used` | **0** |
| `fold_manifest` | **NOT GENERATED** |
| `results` | **NONE** |

**Pre-registration is not authorization.** No real-data access may occur until a
separate authorization names the frozen digests above, the permitted data
authority, the provenance sink and the attempt budget.

Nothing was executed to produce this receipt. No physiological data, annotation,
reference-episode count, fold assignment, calibrator, threshold, model output or
scientific metric was accessed or generated.

## Immutability rule

> **Any subsequent scientific byte change to either bound document invalidates this
> binding for execution purposes.** A scientific amendment requires a new versioned
> protocol and pre-registration, an explicit change rationale, new digests, and a
> new human freeze review.

**V1 is not silently updated.** If the science must change, it changes as V2 of
these documents, with this receipt left standing as the record of what was frozen
on 2026-09-01 and what it bound.

## What was frozen, in one table

| Element | Frozen value |
|---|---|
| Question | does stateful episode reasoning retain an advantage against an independently tuned memoryless comparator |
| Population | 56 V1 TRAIN subjects |
| Primary F1 cohort | `reference_episode_count > 0` — reference-defined, identical for both arms |
| Arm-neutral row | 8 fields |
| Inherited scaffold | B4 / P1 / M1 / M2 / T2, frozen |
| Cross-fit upstream | U1 calibration only |
| Geometry | outer 7 × 8, inner 6 × 8 over 48 |
| J1-S | 12 candidates, `NO EXPANSION` |
| J1-W | 206 candidates |
| Primary contrast | `Δ = mean(F1_S,i − F1_W,i)` |
| Interval | percentile paired subject bootstrap, 1000 replicates, seed 2026, 2.5 / 97.5 |
| Gate A | PASS = `Δ > 0` **and** 95% lower bound `> 0` |

The bound documents are authoritative for all of it. This table is a reader's
summary and settles nothing on its own.
