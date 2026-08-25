# Local Qwen Evaluation Run

**Status: NOT EXECUTED.** This is the manual run contract and record template,
not a result. CI must never download or execute the real model.

This document supersedes the operational identity and latency fields in
`LOCAL_LLM_EXPLANATION_PROTOCOL_V1.md` §§1, 5 for every future real-model run.
The V1 document remains unchanged as the historical pre-implementation
protocol; no generative arm has yet been exercised or reported.

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

| Field | Value |
|---|---|
| Execution status | **NOT EXECUTED** |
| Repository commit | — |
| Provider | — |
| Model ID | — |
| Revision | — |
| Quantization | — |
| Runtime | — |
| Host/device | — |
| Frozen dependency digest | — |
| Context count and identity | — |
| Command | — |
| Start/end UTC | — |
| Output artifact and SHA-256 | — |
| Failure/fallback counts | — |

Populate this table from the emitted machine record. Do not copy measurements
from terminal prose, edit generated values manually, or mark the arm exercised
because the CI contract test passed.
