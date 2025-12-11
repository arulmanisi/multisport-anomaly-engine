"""OpenAI LLM client implementation (MVP)."""

from __future__ import annotations

import os
from typing import Optional

import openai
+
+
+MODEL_NAME = "gpt-4.1-mini"
+
+
+class OpenAILLMClient:
+    """LLM client using OpenAI's Chat Completions API.
+
+    Notes:
+        - Expects OPENAI_API_KEY to be set in the environment.
+        - Keep prompts concise; avoid PII; sanitize inputs before sending.
+        - Swap MODEL_NAME or provider as needed; extend for Anthropic/etc.
+    """
+
+    def __init__(self) -> None:
+        api_key = os.getenv("OPENAI_API_KEY")
+        if not api_key:
+            raise RuntimeError("OPENAI_API_KEY not set; cannot initialize OpenAILLMClient")
+        openai.api_key = api_key
+
+    def generate(self, prompt: str, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
+        params = {
+            "model": MODEL_NAME,
+            "messages": [{"role": "user", "content": prompt}],
+        }
+        if temperature is not None:
+            params["temperature"] = temperature
+        if max_tokens is not None:
+            params["max_tokens"] = max_tokens
+
+        response = openai.chat.completions.create(**params)
+        return response.choices[0].message.content
+EOF