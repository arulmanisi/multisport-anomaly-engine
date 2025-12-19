"""OpenAI LLM client implementation (MVP)."""

from __future__ import annotations

import os
from typing import Optional

from openai import OpenAI

MODEL_NAME = "gpt-4.1-mini"


class OpenAILLMClient:
    """LLM client using OpenAI's Chat Completions API."""

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is missing")
        self._model_name = model_name
        self._client = OpenAI(api_key=api_key)

    def generate(self, prompt: str, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
        params = {
            "model": self._model_name,
            "messages": [{"role": "user", "content": prompt}],
        }
        if temperature is not None:
            params["temperature"] = temperature
        if max_tokens is not None:
            params["max_tokens"] = max_tokens

        response = self._client.chat.completions.create(**params)
        return response.choices[0].message.content
