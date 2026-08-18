"""LLM provider wiring for BPL live runs (Azure OpenAI or public OpenAI).

Credentials come only from the environment (or the caller's shell). This module
never reads a repo-local ``.env`` file and never prints key material.
"""

from __future__ import annotations

import os
import time
from typing import Any


class LLMUnavailable(RuntimeError):
    """Azure/OpenAI did not answer after retries. Not a scored episode."""


def _timeout() -> float:
    # gpt-5-mini tool turns routinely exceed 60s. A short read timeout shows up
    # as APIConnectionError and used to be scored as V=0 / P=0.
    return float(os.environ.get("BPL_LLM_TIMEOUT", "180"))


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
    timeout = _timeout()
    # We retry in llm_create; SDK retries stacked on a 60s cap caused both hangs
    # and connection flaps.
    max_retries = int(os.environ.get("BPL_LLM_SDK_RETRIES", "0"))

    if use_azure:
        from openai import AzureOpenAI

        api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

        def _factory(*_a, **_k):
            client = AzureOpenAI(
                azure_endpoint=az_ep,
                api_key=az_key,
                api_version=api_version,
                timeout=timeout,
                max_retries=max_retries,
            )
            _orig = client.chat.completions.create

            def _create(*a, **k):
                if k.get("temperature") == 0:
                    k.pop("temperature")
                return _orig(*a, **k)

            client.chat.completions.create = _create
            client._bpl_sdk = True  # type: ignore[attr-defined]
            return client

        openai.OpenAI = _factory  # type: ignore[misc,assignment]
        return f"azure:{az_ep} ({model})"

    Real = configure_provider._real_openai  # type: ignore[attr-defined]

    def _openai_factory(*_a, **_k):
        client = Real(timeout=timeout, max_retries=max_retries)
        client._bpl_sdk = True  # type: ignore[attr-defined]
        return client

    openai.OpenAI = _openai_factory  # type: ignore[misc,assignment]
    return f"openai ({model})"


def new_client():
    import openai

    return openai.OpenAI()


def llm_create(client: Any, **kw: Any):
    """One chat.completions.create with backoff. Fresh client after transport errors."""
    from openai import (
        APIConnectionError,
        APIStatusError,
        APITimeoutError,
        RateLimitError,
    )

    if not getattr(client, "_bpl_sdk", False):
        return client.chat.completions.create(**kw)

    attempts = int(os.environ.get("BPL_LLM_ATTEMPTS", "6"))
    delay = float(os.environ.get("BPL_LLM_BACKOFF", "2"))
    last: BaseException | None = None
    current = client
    for attempt in range(1, attempts + 1):
        try:
            return current.chat.completions.create(**kw)
        except RateLimitError as exc:
            last = exc
            wait = max(delay, float(getattr(exc, "retry_after", None) or delay))
            print(
                f"    [llm] RateLimitError attempt {attempt}/{attempts}, sleep {wait:.0f}s",
                flush=True,
            )
            time.sleep(wait)
        except (APITimeoutError, APIConnectionError) as exc:
            last = exc
            print(
                f"    [llm] {type(exc).__name__} attempt {attempt}/{attempts}, "
                f"sleep {delay:.0f}s (new client)",
                flush=True,
            )
            time.sleep(delay)
            current = new_client()
        except APIStatusError as exc:
            last = exc
            if exc.status_code < 500:
                raise
            print(
                f"    [llm] HTTP {exc.status_code} attempt {attempt}/{attempts}, "
                f"sleep {delay:.0f}s",
                flush=True,
            )
            time.sleep(delay)
            current = new_client()
        delay = min(delay * 2, 45.0)
    raise LLMUnavailable(str(last) if last else "llm unavailable") from last
