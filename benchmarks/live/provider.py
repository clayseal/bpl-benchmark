"""LLM provider wiring for BPL live runs (Azure OpenAI or public OpenAI).

Credentials come only from the environment (or the caller's shell). This module
never reads a repo-local ``.env`` file and never prints key material.
"""

from __future__ import annotations

import os


def configure_provider(model: str) -> str:
    """Patch ``openai.OpenAI`` toward Azure when endpoint+key are set."""
    import openai
    from openai import OpenAI as _RealOpenAI

    # Keep a handle so we can restore public OpenAI between runs.
    if not hasattr(configure_provider, "_real_openai"):
        configure_provider._real_openai = _RealOpenAI  # type: ignore[attr-defined]

    az_ep = os.environ.get("AZURE_OPENAI_ENDPOINT")
    az_key = os.environ.get("AZURE_OPENAI_KEY") or os.environ.get(
        "AZURE_OPENAI_API_KEY"
    )
    az_models = {
        m
        for m in os.environ.get(
            "AZURE_OPENAI_DEPLOYMENTS", "gpt-4o-mini-2024-07-18"
        ).split(",")
        if m
    }
    has_openai = bool(os.environ.get("OPENAI_API_KEY"))
    use_azure = bool(az_ep and az_key) and (model in az_models or not has_openai)

    if use_azure:
        from openai import AzureOpenAI

        api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

        def _factory(*_a, **_k):
            client = AzureOpenAI(
                azure_endpoint=az_ep, api_key=az_key, api_version=api_version
            )
            _orig = client.chat.completions.create

            def _create(*a, **k):
                if k.get("temperature") == 0:
                    k.pop("temperature")
                return _orig(*a, **k)

            client.chat.completions.create = _create
            return client

        openai.OpenAI = _factory  # type: ignore[misc,assignment]
        return f"azure:{az_ep} ({model})"

    openai.OpenAI = configure_provider._real_openai  # type: ignore[attr-defined,misc]
    return f"openai ({model})"
