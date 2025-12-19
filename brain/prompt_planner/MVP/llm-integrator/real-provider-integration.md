You are my coding agent.

Goal:
Extend the existing LLMClient abstraction to support a real LLM provider (e.g., OpenAI),
while keeping DummyLLMClient as a safe default.

Assumptions:
- There is already a module backend/llm/anomaly_narrator.py with:
    - LLMClient Protocol
    - DummyLLMClient
    - AnomalyNarrator

Tasks:

1) Refine LLMClient interface
- In backend/llm/anomaly_narrator.py (or a small dedicated module backend/llm/base_client.py),
  update the LLMClient Protocol to support optional generation params:

    from typing import Protocol, Optional

    class LLMClient(Protocol):
        def generate(
            self,
            prompt: str,
            temperature: Optional[float] = None,
            max_tokens: Optional[int] = None,
        ) -> str:
            """
            Generate a completion for the given prompt.
            """

2) Keep DummyLLMClient working
- Update DummyLLMClient to accept the new parameters but ignore them:

    class DummyLLMClient:
        def generate(
            self,
            prompt: str,
            temperature: Optional[float] = None,
            max_tokens: Optional[int] = None,
        ) -> str:
            return "DUMMY_RESPONSE"

3) Implement OpenAILLMClient (MVP version)
- Create backend/llm/openai_client.py
- Implement a class OpenAILLMClient(LLMClient) that:
    - Reads an environment variable OPENAI_API_KEY.
    - If the key is not set, raises a clear RuntimeError when instantiated
      (with a helpful message).
    - Uses the official OpenAI Python SDK (or a simple HTTPS call) to
      send the prompt to a chat/completions model (e.g., gpt-4.1).
    - For now, keep configuration simple:
        - Model name hardcoded in a constant (e.g., MODEL_NAME = "gpt-4.1-mini").
        - temperature and max_tokens passed through when not None.
    - Returns the raw text content from the model as a string.

  Add clear TODOs/docstrings about:
    - Keeping prompts small, no PII, etc.
    - Allowing swapping in other providers (Anthropic, etc.) in the same pattern.

  NOTE: Do not actually require the key at import time—only when constructing
  or calling OpenAILLMClient.

4) Provider selection helper
- Create a small factory function in backend/llm/anomaly_narrator.py (or a new module,
  e.g. backend/llm/factory.py):

    import os
    from typing import Literal

    ProviderName = Literal["dummy", "openai"]

    def get_llm_client_from_env() -> LLMClient:
        provider = os.getenv("LLM_PROVIDER", "dummy").lower()
        if provider == "openai":
            from backend.llm.openai_client import OpenAILLMClient
            return OpenAILLMClient()
        return DummyLLMClient()

- This allows the rest of the code to just call get_llm_client_from_env().

5) Wire into AnomalyNarrator
- In the places where AnomalyNarrator is instantiated (REST API, CLI),
  replace direct DummyLLMClient() usage with:

    from backend.llm.anomaly_narrator import AnomalyNarrator
    from backend.llm.factory import get_llm_client_from_env

    llm_client = get_llm_client_from_env()
    narrator = AnomalyNarrator(llm_client=llm_client)

- This makes the actual provider configurable via env:
    - LLM_PROVIDER=dummy  → fully offline, safe
    - LLM_PROVIDER=openai → use real OpenAI backend

6) Ensure tests still pass
- Keep DummyLLMClient as default in tests by ensuring LLM_PROVIDER is not set
  or explicitly mocked to "dummy" in test setup.

After implementing, show me:
- OpenAILLMClient implementation,
- get_llm_client_from_env(),
- and one example of AnomalyNarrator being instantiated with this factory.
