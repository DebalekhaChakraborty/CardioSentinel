# Local Open-Weight Explanation Provider — protocol, V1

**Written before the implementation**, as every capability in this programme is:
contract, then implementation, then verification.

---

## 0. What this adds, and what it does not

It adds **one adapter**. The governed explanation path — closed context, claim
guard, deterministic fallback, declared mode — already exists and is unchanged.
This populates the arm that `EXPLANATION_EVALUATION_PROTOCOL.md` §7 records as
**unexercised**.

**It is not a chatbot.** There is no conversation, no history, no user-supplied
text reaching the model. The model receives one `ExplanationContext` and returns
one paragraph.

**It runs no experiment and touches no artifact.** No budget, no sealed test, no
run directory.

---

## 1. Model

| | |
|---|---|
| Reported configuration | `Qwen/Qwen3-4B-Instruct-2507` · Apache-2.0 |
| Development default | `Qwen/Qwen3-1.7B` · Apache-2.0 |
| Selected by | `CARDIOSENTINEL_LLM_MODEL`, else the development default |
| Revision | `CARDIOSENTINEL_LLM_REVISION`, recorded with the model name |

**Apache-2.0 and ungated are requirements, not preferences.** A reviewer must be
able to reproduce a reported result without accepting a licence or holding a
token. `Qwen2.5-3B-Instruct` is excluded (`license:other`, non-commercial);
Llama 3.1 is excluded (gated); Mistral 7B v0.3 is excluded (packaged for vLLM,
which cannot be installed here); Phi-4-mini is excluded (`custom_code` requires
`trust_remote_code`, which this repository will not do).

---

## 2. Runtime

`transformers` + `torch` on CPU. **No package is added to the scientific
environment**, which is frozen at 335 packages,
`b0fd6eaa592537b7e4d5574ca68b675e85e923ae3c4a5ba411028ba6fcd7297a`. vLLM,
llama.cpp, Ollama, ONNX Runtime, `accelerate` and `bitsandbytes` are all absent
and installing any of them would void that digest.

| | |
|---|---|
| dtype | `float32` — measured faster than `bfloat16` on this host |
| decoding | **greedy**, `do_sample=False` |
| threads | `torch.set_num_threads(cpu_count())` |
| weights | `HF_HOME`, outside every repository |

**Greedy decoding plus fixed weights plus a pinned revision makes generation
reproducible.** That is a stronger claim than a hosted API can make, and it is
the reason to prefer open weights here.

Measured on the development host, 32 cores, no GPU: **6.68 tok/s at 0.5B**,
extrapolating to ~111 s (1.7B) and ~219 s (4B) for a 180-token explanation.
**This path is for the evaluation harness, not the live console.**

---

## 3. What the model receives

`ExplanationContext` — four closed sections — serialized as JSON, plus
`SYSTEM_BRIEF`. **Nothing else.** No handbook, no reports, no research prose, no
free-text field, no raw waveform, no training artifact.

The brief is the one already registered in `explain.py`, ending in the canonical
disclaimer `claims.SYSTEM_BEHAVIOUR_ONLY`. **It is not restated here.** Handbook
§53.3 records that each writer inventing its own variant is what produced
claim-boundary findings 1 and 2.

---

## 4. What must hold on the way out

Generated text passes **two** gates, in order. Failing either falls back.

### 4.1 Claim boundary — `claims.audit()`

Existing behaviour, unchanged. `audit`, not `find_violations`, because the brief
*requires* the canonical disclaimer and raw matching would reject a model for
complying.

### 4.2 Numeric claim guard — **a guard, not the metric**

`claims.audit()` is lexical. It cannot catch a fabricated *number*.

Observed while selecting the model: asked to describe
`peak_probability = 0.545613`, a small Qwen wrote *"an estimated peak
probability of **54.6%**"*. **The claim guard passes that text cleanly**, because
a percentage breaks no forbidden-claim pattern.

**The metric and the guard are different concepts and are kept apart.**

| | Registered metric | Governance guard |
|---|---|---|
| Question | *what fraction of extractable values are supported* | *does the text assert a number the evidence never gave it* |
| Extracts | `\d+\.\d{2,}` — two or more decimals | number **+ optional unit**, integers included |
| Purpose | reporting, in the trade-off table | refusing output at runtime |
| Registered in §3.1 | **yes — unchanged** | no |

The two-decimal threshold is deliberate *in the metric*: window counts and clock
parts are formatting noise for that statistic. **It is not changed here.**
Redefining a registered statistic so a gate works is the failure this
programme's apparatus exists to prevent.

**A unit changes the claim.** `0.545613` is in the evidence; `54.6%` is not, and
neither is `54%`. Any number carrying a percent sign is refused, because no field
of `ExplanationContext` is a percentage.

Measured behaviour of the guard:

| Generated text | Verdict |
|---|---|
| `The peak score was 0.545613` | allowed — verbatim |
| `reached 0.546` | allowed — rounding is not fabrication |
| `for 640 seconds`, `across 129 windows`, `at 00:17:05` | allowed — all in the context |
| `The system achieved 54% improvement` | **refused** — no such field |
| `peak probability of 54.6%` | **refused** — a unit the evidence never had |
| `reached 0.812345` | **refused** — invented |
| `fired 999 times` | **refused** — invented, and **invisible to the metric** |

**The guard must never reject the deterministic renderer**, which states a
timestamp, a duration and a window count. A gate that rejected its own fallback
would turn every generative failure into a second failure. A test asserts it.

The supported set is built from **all four context sections**, and digit runs
inside strings count — so `"00:17:05"` licenses `00`, `17` and `05`.

### 4.4 Categorical state alignment — **registered after Arm B**

**Numeric and lexical guards are insufficient for categorical assertions, and
this was discovered by running the experiment, not by anticipating it.**

The first exercised Arm B run — `Qwen3-1.7B @ 70d244cc`, one context — produced a
fluent, correctly-rounded explanation containing this sentence:

> *"The system passed several safety checks, including G1 through G6."*

The evidence said:

```
conditions_passed  G1, G2, G3, G6
blocked_by         G4, G5
```

**G4 and G5 were blocked.** The sentence asserts all six passed — inverting the
single most safety-relevant fact in the explanation, the one the contamination
control exists to communicate.

Measured against every gate then in force:

| Gate | Result |
|---|---|
| `claims.audit()` | **0 violations** — it breaks no forbidden-claim pattern |
| numeric claim guard | **0 unsupported** — `G1`/`G6` are not numeric claims; the digit follows a letter |
| evidence fidelity | **1.000** |
| completeness | **passes** — a gate-behaviour cue is present |

**Every gate passed a false statement about safety state.** The gates enforce
*numeric* and *lexical* properties. Nothing compared a categorical assertion
against the structured fields that record the truth.

#### What is now required

A generated explanation must not assert a categorical state the evidence
contradicts. Three families are checked, all against `ExplanationContext` fields
and nothing else:

| Family | Evidence field |
|---|---|
| gate status, passed conditions | `safety.conditions_passed` |
| blocked conditions | `safety.blocked_by` |
| lifecycle states | `event.type`, `event.entered_from`, `event.closed_into` |

#### Evaluation criteria

1. A gate named as **passed** must appear in `conditions_passed`.
2. A gate named as **blocked** must appear in `blocked_by`.
3. A **universal claim** — *all*, *every*, *each*, *G1 through G6* — asserting
   that gates passed fails whenever `blocked_by` is non-empty.
4. A **lifecycle state** named must be one the event actually carries.
5. Text asserting no categorical claim is **not** penalised. Silence is a
   completeness question, not an alignment failure.

#### What this deliberately is not

**No second model judges the first.** A generative judge would move the
governance boundary from something checkable into something that must itself be
trusted, and this programme's contribution is that its constraints are
executable.

**No semantic inference.** The validator works from a fixed vocabulary and the
structured fields. It resolves ranges (`G1 through G6`) and attributes polarity
by proximity to a fixed marker list. It does not attempt to parse meaning, and
it fails **closed**: an assertion it cannot align is a violation, not a pass.

**It is lexical too, and therefore also insufficient on its own.** It is a third
necessary condition, not a sufficient one. Handbook §53.1's limit applies here as
it does to the claim guard: this reduces a failure rate; it does not make
misstatement impossible, and no claim in this document should be read as saying
otherwise.

---

---

## 5. What is recorded, always

Every `Explanation` carries:

| Field | Meaning |
|---|---|
| `explanation_mode` | `GENERATIVE` or `DETERMINISTIC` |
| `provider` | adapter name |
| `model` | model id **with revision**, e.g. `Qwen/Qwen3-1.7B@<sha>` |
| `latency_seconds` | wall clock, **both** paths |
| `claim_violations` | what tripped the guard, when it did |
| `fallback_reason` | why the deterministic path was taken |

**Five fallback reasons, each recorded verbatim:** no provider configured ·
provider raised · provider returned nothing · generated text broke the claim
boundary · **generated text stated a number not present in the evidence**.

`latency_seconds` is not comparable across hosts and carries that caveat
wherever it is reported.

---

## 6. What does not change

- **The deterministic path is the default.** With no provider configured the
  agent behaves exactly as before, and a test asserts it.
- **The demonstration console is untouched.** `DEMO_SCENARIO.md` contracts its
  output and `tests/edge/test_demo_scenario.py` pins it. The generative path is
  opt-in and never enabled by default.
- **`ExplanationContext` is unchanged.** It is already the schema; a parallel one
  would diverge from it.
- **No scientific finding is affected.** This layer explains results; it does not
  produce them.

---

## 7. Expected result, registered in advance

Recorded before running so it can be **refuted**, in the same spirit as W1 and
as §6 of the evaluation protocol:

> The local arm will produce more fluent prose than the template and will fail
> the fidelity gate at least occasionally, most likely by converting a
> probability to a percentage or by rounding a duration. Claim-boundary
> violations will be rarer than fidelity failures, because the forbidden claims
> are lexically distinctive and fabricated numbers are not.

**If the local arm never fails either gate across the demo contexts, that is
evidence the gates are too weak, not that the model is safe.**

---

## 8. Status

Arm B is exercisable but **not exercised in CI**: the runner has no weights and
no network. Tests use stubs. Any reported comparison must name the model, the
revision, and the host, and must follow the reporting rules of
`EXPLANATION_EVALUATION_PROTOCOL.md` §5 — no winner is declared.
