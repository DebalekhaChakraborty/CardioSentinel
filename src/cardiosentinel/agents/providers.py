"""Generator adapters. Optional, replaceable, and never required.

Each adapter is a thin translation from `ExplanationProvider` onto a vendor SDK.
They are constructed lazily and import their SDK inside the constructor, so a
machine without the package -- or without credentials -- degrades to the
deterministic renderer instead of failing at import time.

**No SDK is added to the project's dependencies.** The scientific environment is
frozen at 335 packages with a recorded digest and must not be modified, so an
adapter uses what happens to be present and is skipped when it is not.
"""

from __future__ import annotations

import os
import pathlib


class ProviderUnavailable(RuntimeError):
    """The provider cannot be constructed here. Callers fall back."""


class GeminiProvider:
    """`google.generativeai`, configured from the environment."""

    name = "gemini"

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        *,
        api_key_env: str = "GOOGLE_API_KEY",
    ) -> None:
        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise ProviderUnavailable(
                f"{api_key_env} is not set; no generative provider is configured."
            )
        try:
            import google.generativeai as genai
        except ImportError as error:  # pragma: no cover - depends on the host
            raise ProviderUnavailable(f"google.generativeai unavailable: {error}")
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)
        self.name = f"gemini:{model}"

    def generate(self, brief: str, payload: str) -> str:
        response = self._model.generate_content(f"{brief}\n\nJSON:\n{payload}")
        return getattr(response, "text", "") or ""


#: Apache-2.0 and ungated, both deliberately. A reviewer must be able to
#: reproduce a reported result without accepting a licence or holding a token.
#: `Qwen2.5-3B-Instruct` is excluded for `license:other`, Llama 3.1 for being
#: gated, Mistral 7B v0.3 for vLLM-only packaging, Phi-4-mini for requiring
#: `trust_remote_code`. See `docs/LOCAL_LLM_EXPLANATION_PROTOCOL_V1.md` §1.
DEFAULT_LOCAL_MODEL = "Qwen/Qwen3-1.7B"
REPORTED_LOCAL_MODEL = "Qwen/Qwen3-4B-Instruct-2507"


class LocalQwenProvider:
    """Open-weight generation on the frozen environment, weights loaded lazily.

    **Adds no dependency.** `torch` and `transformers` are already present; this
    imports them inside the constructor so a host without them degrades to the
    deterministic renderer instead of failing at import time.

    **Constructing this does not download anything.** The constructor probes for
    locally cached weights and raises `ProviderUnavailable` if there are none, so
    `default_provider()` can never trigger a multi-gigabyte fetch as a side
    effect of rendering an explanation. Weights load on the first `generate`.

    **Decoding is greedy.** Greedy decoding, fixed weights and a pinned revision
    make generation reproducible, which is the property that justifies open
    weights over a hosted API in a programme built on reproducibility.
    """

    name = "local-qwen"

    def __init__(
        self,
        model: str | None = None,
        *,
        revision: str | None = None,
        max_new_tokens: int | None = None,
    ) -> None:
        self.model_id = model or os.environ.get(
            "CARDIOSENTINEL_LLM_MODEL", DEFAULT_LOCAL_MODEL
        )
        self.revision = revision or os.environ.get("CARDIOSENTINEL_LLM_REVISION")
        self.max_new_tokens = int(
            max_new_tokens or os.environ.get("CARDIOSENTINEL_LLM_MAX_TOKENS", 256)
        )
        try:
            import torch  # noqa: F401
            import transformers  # noqa: F401
        except ImportError as error:  # pragma: no cover - depends on the host
            raise ProviderUnavailable(f"torch/transformers unavailable: {error}")

        # Probe the cache without touching the network. No weights, no provider.
        try:
            from transformers import AutoConfig

            AutoConfig.from_pretrained(
                self.model_id, revision=self.revision, local_files_only=True
            )
        except Exception as error:  # noqa: BLE001 - any miss means "not cached"
            raise ProviderUnavailable(
                f"{self.model_id!r} is not cached locally "
                f"({type(error).__name__}); no local generator is configured."
            )

        self._resolved = self._resolve_revision()
        #: Recorded with the model name, because a bare tag is a moving pointer
        #: and provenance here is expected to survive the tag moving.
        self.model_name = (
            f"{self.model_id}@{self._resolved}" if self._resolved else self.model_id
        )
        self._tokenizer = None
        self._model = None

    def _resolve_revision(self) -> str | None:
        """The commit actually on disk, so the record names weights not a tag."""
        if self.revision and len(self.revision) >= 7:
            return self.revision
        try:
            from huggingface_hub import snapshot_download

            path = snapshot_download(
                self.model_id, revision=self.revision, local_files_only=True
            )
            marker = pathlib.Path(path).name
            return marker if len(marker) >= 7 else None
        except Exception:  # noqa: BLE001 - provenance is best-effort, not a gate
            return None

    def _load(self) -> None:
        if self._model is not None:
            return
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        torch.set_num_threads(os.cpu_count() or 1)
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.model_id, revision=self.revision, local_files_only=True
        )
        # float32 rather than bfloat16: measured faster on this CPU host, and
        # there is no GPU for bf16 kernels to help on.
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            revision=self.revision,
            dtype=torch.float32,
            local_files_only=True,
        ).eval()

    def generate(self, brief: str, payload: str) -> str:
        import torch

        self._load()
        assert self._tokenizer is not None and self._model is not None
        # transformers 5.x returns a BatchEncoding from apply_chat_template, not
        # a tensor, so the template is rendered to text and tokenized after.
        text = self._tokenizer.apply_chat_template(
            [{"role": "user", "content": f"{brief}\n\nJSON:\n{payload}"}],
            add_generation_prompt=True,
            tokenize=False,
        )
        encoded = self._tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            output = self._model.generate(
                **encoded,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                pad_token_id=self._tokenizer.eos_token_id,
            )
        generated = output[0][encoded["input_ids"].shape[-1] :]
        return self._tokenizer.decode(generated, skip_special_tokens=True)


def default_provider() -> object | None:
    """The best available provider, or `None` so the caller degrades.

    Returning `None` rather than raising is deliberate: "no generator" is a
    normal operating state for this system, not an error.

    The local provider is opt-in via `CARDIOSENTINEL_LLM_PROVIDER=local`. It is
    never selected implicitly: a demonstration that silently became four minutes
    slower because weights appeared in a cache would be a worse surprise than
    having no generator at all.
    """
    if os.environ.get("CARDIOSENTINEL_LLM_PROVIDER", "").lower() == "local":
        try:
            return LocalQwenProvider()
        except ProviderUnavailable:
            return None
    try:
        return GeminiProvider()
    except ProviderUnavailable:
        return None
