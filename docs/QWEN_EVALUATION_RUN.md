# Local Qwen Evaluation Run

**Status: EXECUTED 2026-08-25.** Arm B was exercised and is reported in
`EXPLANATION_EVALUATION_REPORT_V1.md`. This document remains the manual run
contract; §5 below is its run record, populated after the fact.

**It said `NOT EXECUTED` for one day after the run, and that is a defect worth
naming rather than overwriting.** The template's own closing instruction is
*"populate this table from the emitted machine record"*, and the run happened
without that step. **Three of its fourteen fields could not be recovered** — §5
marks them, and they are marked rather than reconstructed, because a run record
filled in from a report is a report, not a record.

CI must never download or execute the real model; that separation is unchanged.

This document supersedes the operational identity and latency fields in
`LOCAL_LLM_EXPLANATION_PROTOCOL_V1.md` §§1, 5 for every real-model run. The V1
document remains unchanged as the historical pre-implementation protocol.

## 1. Separation of responsibilities

| Path | Purpose | Real weights |
|---|---|---|
| CI provider-contract test | fake cached config, tokenizer and weights → `LocalQwenProvider` → output audit | prohibited |
| Manual evaluation | identical registered contexts through the locally cached model | required |

Passing CI establishes adapter and audit behavior. It is not evidence about
Qwen output quality, fidelity, latency or failure rate.

## 2. Immutable identity gate

A real run is invalid unless provider construction resolves and records all of:

```json
{
  "provider": "local_qwen",
  "model_id": "Qwen/Qwen3-4B-Instruct-2507",
  "revision": "<full 40-character Hugging Face commit SHA>",
  "quantization": "<value proved by cached config; Q4 only when config proves 4-bit>",
  "runtime": "transformers",
  "device": "cpu"
}
```

The model ID is not an identity by itself. `revision: unknown`, a tag, an
abbreviated hash, or a cache path that does not end in a full commit SHA causes
`ProviderUnavailable`. Provider construction also fails unless the resolved
snapshot contains:

1. `config.json`, loadable by `AutoConfig`;
2. tokenizer assets, loadable by `AutoTokenizer`;
3. a single Transformers checkpoint or every shard named by its weight index.

Every Transformers load uses the resolved snapshot path with
`local_files_only=True`. Construction and generation must not contact the
network or repair an incomplete cache.

The selected reported model remains `Qwen/Qwen3-4B-Instruct-2507`. Do not record
`Q4` merely because it was requested: the current float32 checkpoint must say
`quantization: none`; a genuinely quantized cache must expose four-bit metadata
that resolves to `Q4`.

## 3. Manual preflight

The weights must already exist in the local Hugging Face cache. Set the exact
model revision before constructing the provider:

```bash
export CARDIOSENTINEL_LLM_PROVIDER=local
export CARDIOSENTINEL_LLM_MODEL=Qwen/Qwen3-4B-Instruct-2507
export CARDIOSENTINEL_LLM_REVISION=<full-40-character-commit-sha>
export CARDIOSENTINEL_LLM_MAX_TOKENS=256
```

From the repository root, using the frozen `tactics` interpreter, print and
inspect the resolved identity without generating text:

```bash
PYTHONPATH=src /home/AI_POC/venvs/tactics/bin/python -c \
  'import json; from cardiosentinel.agents.providers import LocalQwenProvider; print(json.dumps(LocalQwenProvider().identity.as_dict(), indent=2))'
```

Stop if any field differs from the authorized configuration. Do not download a
replacement during the run, relabel quantization, or substitute a moving tag.

## 4. Manual real-model execution

Run outside CI, on the declared CPU host, against the same evidence contexts as
the deterministic arm:

```bash
PYTHONPATH=src /home/AI_POC/venvs/tactics/bin/python -m cardiosentinel \
  agent evaluate-explanations s20041 --seconds 2400 --json
```

The JSON report must carry, for the generative arm:

- `provider`, `model`, `revision`, `quantization`, `runtime`, and `host`;
- `latency_scope: total generation latency`;
- every per-context score and `mean_latency_seconds`;
- fidelity, fabricated numbers, claim violations and completeness;
- all registered reporting rules, including that no winner is declared.

For the patient-explanation path, `latency_seconds` means **total response
latency**. If generation takes 35.40 seconds and then fails, and deterministic
rendering takes 0.02 seconds, the fallback explanation records approximately
35.42 seconds—not 0.02 seconds. It also retains the attempted provider identity
and records `renderer: template`.

## 5. Run record — populate only after execution

**Every value below is transcribed from `EXPLANATION_EVALUATION_REPORT_V1.md`,
which is the published record of the run.** Fields marked **not recorded** were
never captured and are not reconstructed here.

| Field | Value |
|---|---|
| Execution status | **EXECUTED — 2026-08-25** |
| Repository commit | `origin/master` `2fc39af` |
| Provider | `local_qwen` |
| Model ID | `Qwen/Qwen3-1.7B` · `Qwen/Qwen3-4B-Instruct-2507` |
| Revision | `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` · `cdbee75f17c01a7cc42f958dc650907174af0554` |
| Quantization | none |
| Runtime | `transformers` |
| Host/device | CPU, 32 cores, no GPU |
| Frozen dependency digest | unchanged — 335 packages, `b0fd6eaa…`; **no package was installed** |
| Context count and identity | **1** — record `s20201`, 2400 simulated seconds, the contracted demo scenario |
| Command | **not recorded** |
| Start/end UTC | **not recorded** — the date is published; the times are not |
| Output artifact and SHA-256 | **not recorded** |
| Failure/fallback counts | `Qwen3-1.7B` → **DETERMINISTIC** fallback, reason `gate_range_passed`, reproduced on two runs · `Qwen3-4B-Instruct-2507` → **GENERATIVE**, no gate fired. Claim violations **0** on both arms; fidelity 1.000; completeness 1.000; generative latency 63.4014 s |

**Decoding** was greedy, `do_sample=False`, `max_new_tokens=400`.

Populate this table from the emitted machine record. Do not copy measurements
from terminal prose, edit generated values manually, or mark the arm exercised
because the CI contract test passed.

**And populate it at execution time.** The three unrecoverable fields above are
the cost of not doing so. `EXPLANATION_EVALUATION_REPORT_V1.md` is a good report
and it was never meant to be the only record of how its own run was invoked.
