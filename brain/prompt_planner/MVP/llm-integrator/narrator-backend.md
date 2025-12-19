You are my coding agent.

We are adding an LLM-based narration layer to the Cricket Anomaly Engine MVP.

Goal:
Introduce a small, well-structured component that takes a detected anomaly
(UPS + model output) and produces a human-readable description.

Tasks:

1) Create a module: backend/llm/anomaly_narrator.py

2) Define a data structure for the anomaly event:
   - Use a @dataclass or TypedDict named AnomalyEvent with at least:
       player_id: str
       match_format: str               # "T20", "ODI", "TEST"
       team: str | None
       opposition: str | None
       venue: str | None
       baseline_mean_runs: float
       baseline_std_runs: float
       current_runs: float
       ups_score: float
       ups_bucket: str                 # "normal", "mild_spike", "strong_spike", "extreme_spike"
       ups_anomaly_flag_baseline: int  # 0/1
       model_anomaly_probability: float
       model_anomaly_label: int        # 0/1
       match_context: dict | None      # optional extra fields, can default to {}

3) Define an AnomalyNarrator class with:
   - __init__(self, llm_client: "LLMClient"):
       * llm_client is an abstraction, not a concrete provider.

   - generate_description(self, event: AnomalyEvent) -> dict:
       * Returns a dict with:
           {
             "narrative_title": str,
             "narrative_summary": str,
           }

4) Define a simple LLMClient protocol/interface:
   - In the same module or a separate one (e.g., backend/llm/base_client.py), define:

       class LLMClient(Protocol):
           def generate(self, prompt: str) -> str:
               ...

   - Provide a DummyLLMClient implementation for now that:
       * Does NOT call any external APIs.
       * Generates a basic, rule-based message using f-strings and event fields.
       * This keeps the code runnable without secrets.
       * Add TODO comments where a real OpenAI / other provider integration would go.

5) Prompt construction inside AnomalyNarrator:
   - Implement a private method _build_prompt(event: AnomalyEvent) -> str that:
       * Builds a concise, system + user prompt string, for example:

           "You are an assistant that explains cricket batting anomalies.\n"
           "Given the following JSON of an innings and its anomaly scores, "
           "write a short title and 2–3 sentence summary for a human user.\n"
           f"JSON: {json.dumps(event_dict, ...)}\n"
           "Respond in JSON with keys: narrative_title, narrative_summary."

     (Even though DummyLLMClient will ignore the prompt format, design it
      so it can be used with a real provider later.)

   - In generate_description():
       * Call _build_prompt(event) to get a prompt string.
       * Call self.llm_client.generate(prompt).
       * For DummyLLMClient, simply construct the output dict directly,
         without parsing LLM output.
       * For now, return a dict:
           {
             "narrative_title": ...,
             "narrative_summary": ...
           }

6) Rule-based fallback (Dummy implementation):
   - For DummyLLMClient, generate something like:
       narrative_title:
         - "Huge spike in batting performance" if ups_bucket in {"strong_spike", "extreme_spike"}
         - "Unusual dip in batting performance" if ups_bucket is "normal" but model_anomaly_label == 1 and current_runs << baseline
         - Otherwise a neutral title.
       narrative_summary:
         - One or two sentences referencing:
             player_id, match_format, current_runs, baseline_mean_runs, ups_score, model_anomaly_probability.

7) Add clear docstrings explaining:
   - This layer is optional and augmentative.
   - A real LLM backend (OpenAI, etc.) can be plugged in by providing a concrete LLMClient.

After implementing, show me anomaly_narrator.py (and any new base_client module if created).
