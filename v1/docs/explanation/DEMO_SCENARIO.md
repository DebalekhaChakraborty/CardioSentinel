# Demonstration scenario — the contract the console must satisfy

**The demo can drift, so it gets the same governance as everything else.** This
repository has already lost a disclaimer (#84), a handbook section (#88), a
reproducibility test to a merge race (#90/#91) and a keyword to a collision
(#87/#92). A demonstration that quietly stops matching its description is the
same failure with an audience.

Every expectation below is **machine-checked** by
`tests/edge/test_demo_scenario.py`. If the console stops satisfying this
document, CI fails.

---

## 1. Scenario

| | |
|---|---|
| Subject | `ltstdb:s2020` |
| Record | `s20201`, channel 0 |
| Duration | **2400 simulated seconds** (40 minutes of ECG) |
| Mode | **replay simulation** — a stored recording, no sensor |
| Artifacts | the committed demo bundle, `reproducibility/demo_bundle/` |
| Command | `cardiosentinel edge console s20201 --seconds 2400` |

## 2. Expected outcome

| | |
|---|---|
| Windows | **≥ 400** |
| Alerts | **exactly 1** EVENT run |
| First alert opens | `00:17:05` |
| First alert duration | **640 s** across **129** windows |
| Peak calibrated probability | **0.545613** |
| Memory updates admitted | **0** |
| Explanation mode | **`DETERMINISTIC`**, `fallback_reason: no provider configured` |

**`0` memory updates is correct.** The contamination gate admits only windows
that look normal and sit outside a 60-second refractory. G4 and G5 both block
during an event, which is the control working.

## 3. Expected gate state at the opening window

```
G1 PASS   G2 PASS   G3 PASS   G4 BLOCK   G5 BLOCK   G6 PASS
```

## 4. Expected provenance

| | |
|---|---|
| encoder | `B4BTransformerCNN` |
| memory arm | `M2-G` |
| calibrator | `platt_logistic_on_recovered_logit` |
| temporal arm | `CausalS4DLongitudinal` |
| T1 policy | `qw0.9_qe0.99_FAST` for `ltstdb:s2020` |
| `sealed_test_state` | `unopened` |

## 5. Limitations the console MUST state

Non-negotiable. A demo that omits these overclaims by omission.

- Simulation only: a stored recording is replayed. No sensor, no acquisition.
- Not a diagnosis. Detection only; no clinical utility is claimed.
- Not deployment validation. No serving path, and a laptop is not edge hardware.
- Not generalisation. One dataset, twelve validation subjects.
- The sealed neural test was consumed once, on twelve subjects, and no cohort exists to corroborate it.

**These are quoted verbatim from `edge.console.LIMITATIONS`**, which is the
single source. Each writer inventing its own wording is what produced the
disclaimer drift in #84 and #86; the test compares these strings exactly, so a
reworded console fails rather than silently diverging from its contract.

## 6. What is acceptable to vary

- Wall-clock time and the real-time factor — hardware dependent.
- `DETERMINISTIC` **or** `GENERATIVE` explanation mode. Both are valid; the mode
  must be declared either way.
- Terminal width.

## 7. What must never vary

- The alert count, timing, and measured values in §2.
- The gate pattern in §3.
- The provenance in §4.
- Every limitation in §5.
- **Only the twelve validation subjects are replayable.** Any other record is
  refused, not served another subject's thresholds.
