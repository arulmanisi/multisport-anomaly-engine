"""Factory to obtain LLM client from environment."""

from __future__ import annotations

import os
from typing import Literal

from llm.anomaly_narrator import LLMClient, DummyLLMClient

ProviderName = Literal["dummy", "openai"]


def get_llm_client_from_env() -> LLMClient:
    """Return an LLM client based on env var LLM_PROVIDER."""
    provider = os.getenv("LLM_PROVIDER", "dummy").lower()
    if provider == "openai":
        from llm.openai_client import OpenAILLMClient

        return OpenAILLMClient()
    return DummyLLMClient()
