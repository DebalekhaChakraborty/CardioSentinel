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

import json
import os
import pathlib
import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any


class ProviderUnavailable(RuntimeError):
    """The provider cannot be constructed here. Callers fall back."""


@dataclass(frozen=True)
class ProviderIdentity:
    """Immutable execution identity carried by every local-model record."""

    provider: str
    model_id: str
    revision: str
    quantization: str
    runtime: str
    device: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


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

    name = "local_qwen"

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
        requested_revision = revision or os.environ.get(
            "CARDIOSENTINEL_LLM_REVISION"
        )
        self.max_new_tokens = int(
            max_new_tokens or os.environ.get("CARDIOSENTINEL_LLM_MAX_TOKENS", 256)
        )
        try:
            import torch  # noqa: F401
            import transformers  # noqa: F401
        except ImportError as error:  # pragma: no cover - depends on the host
            raise ProviderUnavailable(f"torch/transformers unavailable: {error}")

        self._snapshot_path, self.revision = self._resolve_cached_snapshot(
            requested_revision
        )
        self._require_config()
        self._require_tokenizer_assets()
        self._require_complete_weights()

        # Parse both through Transformers before declaring the provider
        # available. Paths, not moving model identifiers, keep these calls
        # immutable and prevent a network fallback.
        try:
            from transformers import AutoConfig, AutoTokenizer

            self._config = AutoConfig.from_pretrained(
                str(self._snapshot_path), local_files_only=True
            )
            self._tokenizer = AutoTokenizer.from_pretrained(
                str(self._snapshot_path), local_files_only=True
            )
        except Exception as error:  # noqa: BLE001 - an incomplete cache is unusable
            raise ProviderUnavailable(
                f"{self.model_id!r} cached configuration/tokenizer cannot be "
                f"loaded ({type(error).__name__}); provider unavailable."
            ) from error

        self.identity = ProviderIdentity(
            provider=self.name,
            model_id=self.model_id,
            revision=self.revision,
            quantization=self._quantization(self._config),
            runtime="transformers",
            device="cpu",
        )
        self._model = None

    def _resolve_cached_snapshot(
        self, requested_revision: str | None
    ) -> tuple[pathlib.Path, str]:
        """Resolve a local snapshot to its full immutable Hugging Face SHA."""
        if not requested_revision or not re.fullmatch(
            r"[0-9a-fA-F]{40}", requested_revision
        ):
            raise ProviderUnavailable(
                "model revision cannot be resolved: configure an immutable full "
                f"40-character commit hash for {self.model_id!r}."
            )
        requested_revision = requested_revision.lower()
        try:
            from huggingface_hub import snapshot_download

            snapshot = pathlib.Path(
                snapshot_download(
                    self.model_id,
                    revision=requested_revision,
                    local_files_only=True,
                )
            )
        except Exception as error:  # noqa: BLE001 - any cache miss is unavailable
            raise ProviderUnavailable(
                f"{self.model_id!r} is not completely cached locally "
                f"({type(error).__name__}); provider unavailable."
            ) from error

        revision = snapshot.name.lower()
        if not re.fullmatch(r"[0-9a-f]{40}", revision):
            raise ProviderUnavailable(
                "model revision cannot be resolved to an immutable full "
                f"commit hash for {self.model_id!r}."
            )
        if revision != requested_revision:
            raise ProviderUnavailable(
                f"model revision {requested_revision} resolved to unexpected "
                f"cached snapshot {revision} for {self.model_id!r}."
            )
        return snapshot, revision

    def _require_config(self) -> None:
        if not (self._snapshot_path / "config.json").is_file():
            raise ProviderUnavailable(
                f"{self.model_id!r} cached config.json is unavailable."
            )

    def _require_tokenizer_assets(self) -> None:
        candidates = (
            "tokenizer.json",
            "tokenizer.model",
            "spiece.model",
            "vocab.json",
            "vocab.txt",
        )
        if not any((self._snapshot_path / name).is_file() for name in candidates):
            raise ProviderUnavailable(
                f"{self.model_id!r} cached tokenizer assets are unavailable."
            )

    def _require_complete_weights(self) -> None:
        """Require one complete Transformers checkpoint without loading it."""
        for index_name in (
            "model.safetensors.index.json",
            "pytorch_model.bin.index.json",
        ):
            index_path = self._snapshot_path / index_name
            if not index_path.is_file():
                continue
            try:
                payload = json.loads(index_path.read_text(encoding="utf-8"))
                shards = set(payload["weight_map"].values())
            except (
                AttributeError,
                KeyError,
                OSError,
                TypeError,
                json.JSONDecodeError,
            ) as error:
                raise ProviderUnavailable(
                    f"{self.model_id!r} cached weight index is invalid."
                ) from error
            if not all(isinstance(name, str) and name for name in shards):
                raise ProviderUnavailable(
                    f"{self.model_id!r} cached weight index is invalid."
                )
            missing = sorted(
                name for name in shards if not (self._snapshot_path / name).is_file()
            )
            if not shards or missing:
                detail = ", ".join(missing) if missing else "empty weight map"
                raise ProviderUnavailable(
                    f"{self.model_id!r} cached model weights are incomplete: {detail}."
                )
            return

        if any(
            (self._snapshot_path / name).is_file()
            for name in ("model.safetensors", "pytorch_model.bin")
        ):
            return
        raise ProviderUnavailable(
            f"{self.model_id!r} cached model weights are unavailable."
        )

    @staticmethod
    def _quantization(config: Any) -> str:  # noqa: ANN401 - external config object
        """Describe what the cached config proves; never infer Q4 from intent."""
        quantization = getattr(config, "quantization_config", None)
        if quantization is None:
            return "none"
        if hasattr(quantization, "to_dict"):
            quantization = quantization.to_dict()
        if not isinstance(quantization, Mapping):
            raise ProviderUnavailable(
                f"model quantization cannot be resolved for {config!r}."
            )
        bits = quantization.get("bits") or quantization.get("nbits")
        if quantization.get("load_in_4bit") is True:
            bits = 4
        if isinstance(bits, (int, str)) and str(bits).isdigit() and int(bits) > 0:
            return f"Q{int(bits)}"
        method = quantization.get("quant_method") or quantization.get("method")
        if method:
            return str(method).upper()
        raise ProviderUnavailable(
            f"model quantization cannot be resolved from {dict(quantization)!r}."
        )

    def _load(self) -> None:
        if self._model is not None:
            return
        import torch
        from transformers import AutoModelForCausalLM

        torch.set_num_threads(os.cpu_count() or 1)
        load_options: dict[str, Any] = {"local_files_only": True}
        if self.identity.quantization == "none":
            # float32 rather than bfloat16: measured faster on this CPU host,
            # and there is no GPU for bf16 kernels to help on.
            load_options["dtype"] = torch.float32
        self._model = AutoModelForCausalLM.from_pretrained(
            str(self._snapshot_path),
            **load_options,
        ).eval()

    def generate(self, brief: str, payload: str) -> str:
        import torch

        self._load()
        assert self._model is not None
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


def default_provider(*, strict_local: bool = False) -> object | None:
    """The best available provider, or `None` so the caller degrades.

    Returning `None` rather than raising is deliberate: "no generator" is a
    normal operating state for this system, not an error.

    The local provider is opt-in via `CARDIOSENTINEL_LLM_PROVIDER=local`. It is
    never selected implicitly: a demonstration that silently became four minutes
    slower because weights appeared in a cache would be a worse surprise than
    having no generator at all. Research evaluation passes `strict_local=True`:
    an explicitly requested but irreproducible local provider is then a refusal,
    not an arm quietly relabelled "not exercised".
    """
    if os.environ.get("CARDIOSENTINEL_LLM_PROVIDER", "").lower() == "local":
        try:
            return LocalQwenProvider()
        except ProviderUnavailable:
            if strict_local:
                raise
            return None
    try:
        return GeminiProvider()
    except ProviderUnavailable:
        return None
