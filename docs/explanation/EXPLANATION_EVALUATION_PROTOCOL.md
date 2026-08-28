# Evidence-Constrained Explanation Evaluation — protocol, V1

**Written before the implementation**, as every capability in this programme
now is: contract, then implementation, then verification.

---

## 0. What this measures, and what it does not

**The question is not "is the language model better".** It is:

> Given **identical** evidence, can a generative layer produce useful
> explanations without violating evidence boundaries — and what does that cost?

This is a **governance experiment**, not a model benchmark. The output is a
trade-off table, and the protocol forbids declaring a winner (§5).

**It is not a scientific experiment on patient data.** It consumes an
`EvidenceRecord` that already exists, touches no waveform, no run directory and
no sealed artifact, and needs no authorization.

---

## 1. Frozen input contract

Both arms receive **exactly** the `ExplanationContext` built from one evidence
graph — four closed sections — and nothing else.

Explicitly withheld from both arms: the handbook · reports · protocols · any
research prose · the internet · any patient data outside the evidence object ·
the raw waveform.

**Both arms receive byte-identical input.** A test asserts it. If the arms saw
different inputs, every metric below would be uninterpretable.

---

## 2. The two arms

| | |
|---|---|
| **Arm A — deterministic** | `TemplateRenderer`. Already exists, already tested. |
| **Arm B — generative** | Any `ExplanationProvider`. Adapter only. |

**No SDK becomes a project dependency.** The frozen environment knows the
*interface*; providers are constructed lazily and skipped when absent.
`StubProvider` makes the harness fully exercisable with no credentials.

---

## 3. Metrics

### 3.1 Evidence fidelity

> Did the explanation state only quantities present in the evidence object?

```
fidelity = supported_numeric_claims / total_numeric_claims
```

Every number in the output is extracted and matched against the context.
**A number that appears in prose and not in the evidence is a fabrication**, and
that is the failure this whole architecture exists to prevent.

`undefined` when the output contains no numbers — never silently 1.0.

### 3.2 Claim-boundary violations

`claims.audit(text, quoting=…)`, counted per explanation. **Arm A is expected to
score 0**; a non-zero Arm A is a defect in this repository, not in a model.

### 3.3 Completeness

Four elements the contract requires an explanation to carry:

`state_transition` · `gate_behaviour` · `baseline_update_decision` · `limitation`

```
completeness = elements_present / 4
```

### 3.4 Latency

Wall-clock per explanation. **Not comparable across hosts**, and reported for
shape rather than as a benchmark.

---

## 4. Procedure

1. Build one `EvidenceGraph` per alert from the demo scenario.
2. Reduce to `ExplanationContext`. **This object is shared by both arms.**
3. Run each arm on each context.
4. Score all four metrics per explanation.
5. Emit the trade-off table.

Deterministic and repeatable for Arm A. Arm B is repeatable only to the extent
its provider is; **non-determinism is recorded, not smoothed over.**

---

## 5. Reporting rules

1. **No winner is declared.** The report is a trade-off table.
2. **No claim that either arm is "better".** Different arms, different costs.
3. A generative result **may not** be reported without its violation count.
4. Fidelity below 1.0 is reported as **fabrication**, not as "hallucination
   tendency" — the softer word obscures what happened.
5. **Latency is not comparable across hosts** and carries that caveat.
6. If Arm B is not exercised, the report says so **in the table**, not in a
   footnote.

---

## 6. Expected result, registered in advance

Recorded before running so it can be **refuted**, in the same spirit as W1:

> Arm A will score 0 violations and 1.0 fidelity by construction, and will be
> less linguistically flexible. Arm B, if exercised, will show higher
> completeness variance and non-zero violations at least occasionally, which is
> the reason the claim guard sits between the generator and the user.

**If Arm A ever scores a violation or fidelity below 1.0, that is a defect
here** — the template can only emit values it was handed — and it must be
reported as one rather than treated as a finding about generation.

---

## 7. Status

**Arm B is unexercised in this environment.** No API credentials are configured,
so the framework ships with the deterministic arm measured and the generative
arm validated against `StubProvider` only.

**That is stated plainly rather than presented as a completed comparison.** The
harness runs Arm B in one command wherever credentials exist.
