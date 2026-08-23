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


def default_provider() -> object | None:
    """The best available provider, or `None` so the caller degrades.

    Returning `None` rather than raising is deliberate: "no generator" is a
    normal operating state for this system, not an error.
    """
    try:
        return GeminiProvider()
    except ProviderUnavailable:
        return None
