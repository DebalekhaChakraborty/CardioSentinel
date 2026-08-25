# Evidence-Constrained Explanation Evaluation — report, V1

**Arm B is exercised.** This is the first report of a real generative model in
this programme.

Executed under `docs/EXPLANATION_EVALUATION_PROTOCOL.md` and
`docs/LOCAL_LLM_EXPLANATION_PROTOCOL_V1.md`. **Its §5 reporting rules govern
every sentence below: no winner is declared, neither arm is described as better
than the other, no generative result appears without its violation count, and
latency is not comparable across hosts.**

**No experiment was run on patient data, no budget was opened, no artifact was
touched.** This consumes an `EvidenceRecord` that already exists and needs no
authorization.

---

## 1. What was executed

| | |
|---|---|
| Record | `s20201`, 2400 simulated seconds, the contracted demo scenario |
| Contexts evaluated | **1** — the scenario produces exactly one alert |
| Arm A | `TemplateRenderer` |
| Arm B | `LocalQwenProvider` |
| Model | `Qwen/Qwen3-1.7B` |
| Revision | `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` |
| Quantization | none |
| Runtime · host | `transformers` · CPU, 32 cores, no GPU |
| Decoding | greedy, `do_sample=False`, `max_new_tokens=400` |
| Repository | `origin/master` `2fc39af` |

**No package was installed.** The scientific environment is unchanged at 335
packages, `b0fd6eaa…`.

---

## 2. The trade-off table

| Metric | deterministic | generative |
|---|---|---|
| exercised | yes | **yes** |
| provider | `template` | `local_qwen` |
| evidence fidelity | 1.000 | **1.000** |
| **claim violations** | **0** | **0** |
| completeness | 1.000 | 1.000 |
| latency | 0.0000 s | 63.4014 s |

**This table reports the trade-off. It does not rank the arms.**

**Latency is not comparable across hosts** and is not comparable between these
two arms in kind: one is a string format, the other is 1.7 billion parameters on
a CPU. It is reported for shape.

---

## 3. What the table measures, and what it does not

**The harness calls `provider.generate()` directly.** It does not route through
`PatientExplanationAgent`, so **no runtime gate runs during evaluation**.

That is correct for an evaluation — gating first would mean only ever measuring
the template — but it makes the scope explicit: **the table above describes raw
model output, not what a user would receive.** Reading it as the latter would be
wrong.

---

## 4. What the runtime did with the same generation

**Refused it.**

```
mode = DETERMINISTIC
  gate_range_passed : the range asserts G4, G5 as passed,
                      which the evidence does not record
  lifecycle_state   : NORMAL is named, but the event records
                      only EVENT, RECOVERY, WATCH
```

The user received the deterministic explanation, with the mode and both
contradictions recorded.

### 4.1 The generation was fluent, faithful, and wrong

It scored **fidelity 1.000**, **0 claim violations**, **completeness 1.000**. It
rounded correctly, ended with the canonical disclaimer, and invented no number.

It also asserted that a `G1`–`G6` range passed when **G4 and G5 were blocked** —
inverting the fact the contamination control exists to communicate — and named a
lifecycle state the event never carried.

**The first three gates passed it. The fourth did not.**

### 4.2 The failure reproduces

The categorical inversion appeared on **two independent runs**, before and after
the reasoning-mode fix, on the same context. That makes it a repeatable failure
mode of this model on this evidence, not an anecdote.

### 4.3 A failure that was not anticipated

The lifecycle check was implemented because it was specified, not because there
was evidence it was needed. **It fired.** No prior run had produced a fabricated
state, and none of the three earlier gates detects one.

---

## 5. The registered prediction

`LOCAL_LLM_EXPLANATION_PROTOCOL_V1.md` §7 recorded, before any model ran:

> The local arm will produce more fluent prose than the template and will fail
> the fidelity gate at least occasionally … **If the local arm never fails either
> gate across the demo contexts, that is evidence the gates are too weak, not
> that the model is safe.**

**Both halves are informative, and the prediction is partly refuted.**

- The fidelity failure it predicted **did not occur**. Fidelity was 1.000.
- The clause about weak gates was **borne out in a stronger form than written**:
  the arm passed every metric the protocol measures *and* misstated the evidence
  twice. The weakness was not that a gate scored generously; it was that no
  metric in the protocol asks whether a categorical assertion is true.

**A prediction that was wrong about the mechanism and right about the risk is
reported as written**, in the same way W1's two refuted predictions were.

---

## 6. What this does not establish

- **Not that either arm is better.** Different arms, different costs.
- **Not a rate.** One context, one model, one host, one revision. This is a
  reproduced failure mode, not a frequency.
- **Not that the gates are sufficient.** All four are lexical or numeric.
  Handbook §53.1's limit applies: they reduce a failure rate; they do not make
  misstatement impossible.
- **Not that larger models behave the same.** `Qwen3-4B-Instruct-2507`, the
  configuration §1 names as the reported one, has not been run.
- **Nothing about the ECG pipeline.** This layer explains results; it does not
  produce them. No figure in §49 or Appendix A is affected.

---

## 7. What it does establish

**A locally deployable, Apache-2.0, ungated foundation model can be driven from a
closed evidence object under executable governance constraints, on commodity CPU,
with no addition to a frozen scientific environment** — and its output can be
refused, with the reason recorded, when it contradicts the evidence.

**The governance layer earned its place by catching a real failure**, twice, that
three prior gates and four registered metrics passed.

---

_Executed 2026-08-25 against `origin/master` `2fc39af`. Arm B: `Qwen/Qwen3-1.7B`
at revision `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`, greedy decoding, CPU._
