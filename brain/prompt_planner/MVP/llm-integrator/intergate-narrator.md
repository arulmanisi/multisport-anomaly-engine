You are my coding agent.

Goal:
Integrate the AnomalyNarrator into both the REST API and CLI prediction flow,
so each prediction includes a human-readable message.

Assumptions:
- AnomalyNarrator and AnomalyEvent are implemented in backend/llm/anomaly_narrator.py.
- DummyLLMClient exists as a simple, rule-based implementation.
- The prediction flow currently has access to:
    - player_id, match_format, team, opposition, venue,
    - baseline_mean_runs, baseline_std_runs,
    - current_runs,
    - ups_score, ups_bucket, ups_anomaly_flag_baseline,
    - model_anomaly_probability, model_anomaly_label.

Tasks:

1) REST API integration (FastAPI)
- Open the FastAPI module that defines POST /predict/single (e.g. backend/app/main.py or similar).
- After computing UPS and model outputs, build an AnomalyEvent instance.
- Instantiate a DummyLLMClient and an AnomalyNarrator (for now; leave TODO to inject this later).
- Call narrator.generate_description(event) to obtain:
    - narrative_title
    - narrative_summary
- Add these fields to the JSON response of /predict/single, e.g.:

    {
      "ups_score": ...,
      "ups_bucket": ...,
      "ups_anomaly_flag_baseline": ...,
      "model_anomaly_probability": ...,
      "model_anomaly_label": ...,
      "narrative_title": "...",
      "narrative_summary": "..."
    }

2) CLI integration
- Open the CLI module (e.g. backend/cli.py).
- In the predict-single flow, after computing UPS and model outputs, build the same AnomalyEvent instance.
- Instantiate DummyLLMClient + AnomalyNarrator.
- Call generate_description() and print the narrative fields, e.g.:

    Narrative:
      Title: <narrative_title>
      Summary: <narrative_summary>

3) Keep the narrator optional
- Wrap the narrator usage in a small helper function or flag so that:
    - If instantiation fails or event-building fails, the core scores are still returned.
    - Add a config flag or ENV check (TODO) to enable/disable LLM narration in the future.

4) Update pydantic response model (if used)
- If the FastAPI endpoint uses a response model (Pydantic), extend it with:
    - narrative_title: Optional[str]
    - narrative_summary: Optional[str]

After implementing, show me:
- The updated /predict/single handler code.
- The updated CLI predict-single output snippet.
