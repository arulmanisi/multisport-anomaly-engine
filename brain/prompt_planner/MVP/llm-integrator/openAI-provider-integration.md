You are my coding agent.

Goal:
Implement a real OpenAI-backed LLM client under the existing LLMClient abstraction,
so the system can switch between DummyLLMClient and OpenAILLMClient using an env variable.

Tasks:

1) Create a new file:
   backend/llm/openai_client.py

2) Implement a class OpenAILLMClient(LLMClient) with:
   - __init__(self, model_name="gpt-4.1-mini"):
       * Reads OPENAI_API_KEY from environment.
       * If missing, raise RuntimeError("OPENAI_API_KEY is missing").
       * Creates an OpenAI client using the official SDK: from openai import OpenAI.

   - generate(self, prompt: str, temperature=None, max_tokens=None) -> str:
       * Call client.chat.completions.create(...)
         using model self._model_name.
       * Pass temperature and max_tokens if provided.
       * Extract and return the string response: response.choices[0].message.content.

3) Extend the LLMClient Protocol (in backend/llm/anomaly_narrator.py or base_client.py) to:
       def generate(self, prompt: str,
                    temperature: Optional[float] = None,
                    max_tokens: Optional[int] = None) -> str: ...

4) Update DummyLLMClient to accept the new arguments but ignore them.

5) Add a new file: backend/llm/factory.py
   Implement:

       def get_llm_client_from_env() -> LLMClient:
           provider = os.getenv("LLM_PROVIDER", "dummy").lower()
           if provider == "openai":
               from backend.llm.openai_client import OpenAILLMClient
               return OpenAILLMClient()
           return DummyLLMClient()

6) Update the REST API and CLI to use:

       from backend.llm.factory import get_llm_client_from_env
       llm = get_llm_client_from_env()
       narrator = AnomalyNarrator(llm)

7) Ensure that:
   - Default is DummyLLMClient when LLM_PROVIDER is not set.
   - No API key is committed.
   - Ask me to review the diff when done.

Implement now.
