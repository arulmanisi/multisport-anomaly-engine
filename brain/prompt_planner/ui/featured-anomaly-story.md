You are my coding agent.

Goal:
Add a “Featured Anomaly Story” box on the Top Anomalies leaderboard tab.
It should pick the #1 anomaly (most extreme) and auto-generate a commentator-style narrative.

Constraints:
- Keep OpenAI keys server-side only (no keys in UI).
- UI should call backend for narrative generation.
- If backend LLM is disabled (dummy), still show a rule-based narrative.

Assumptions:
- Streamlit UI: ui/demo_streamlit/demo_ui.py
- Backend has /predict/single which returns narrative_title/narrative_summary
  and supports `tone` in the request body.
- UI already has a Top Anomalies tab with a leaderboard DataFrame based on local dataset.
- Dataset rows contain enough fields for the backend request:
    player_id, match_format, baseline_mean_runs, baseline_std_runs, current_runs
  If any are missing, compute or approximate for MVP with reasonable defaults and TODOs.

-------------------------------------------------------------------
PART A — Add a backend endpoint dedicated to narration (recommended)
-------------------------------------------------------------------

1) Add a new endpoint to the FastAPI backend:
   POST /narrate/anomaly

Request body (Pydantic model recommended):
{
  "player_id": str,
  "match_format": str,
  "team": optional str,
  "opposition": optional str,
  "venue": optional str,
  "baseline_mean_runs": float,
  "baseline_std_runs": float,
  "current_runs": float,
  "ups_score": optional float,
  "ups_bucket": optional str,
  "ups_anomaly_flag_baseline": optional int,
  "model_anomaly_probability": optional float,
  "model_anomaly_label": optional int,
  "tone": optional str (default "commentator")
}

Behavior:
- Build an AnomalyEvent using provided fields.
- Instantiate narrator using get_llm_client_from_env().
- Call narrator.generate_description(event, tone=tone).
- Return:
{
  "narrative_title": str,
  "narrative_summary": str
}

Notes:
- This endpoint should not re-run UPS scoring or model inference; it only narrates.
- It allows the UI to request narration for any precomputed anomaly row without needing
  to reconstruct the whole scoring pipeline.
- Keep it resilient: if some optional fields are missing, set safe defaults.

-------------------------------------------------------------------
PART B — Update Streamlit UI to show “Featured Anomaly Story”
-------------------------------------------------------------------

2) In ui/demo_streamlit/demo_ui.py, in the “Top Anomalies” tab:

- After applying filters and creating the leaderboard top_df,
  pick the top row (rank #1). Example:
    featured = top_df.iloc[0].to_dict()

- Add a prominent box above the leaderboard:

    st.subheader("Featured Anomaly Story")
    st.caption("Auto-generated in commentator tone from the most extreme anomaly in the current view.")

- Build a payload for the narration endpoint using the featured row fields.

Payload requirements:
- tone must be "commentator"
- Include:
    player_id
    match_format
    current_runs
    baseline_mean_runs (if missing, fallback to something like current_runs * 0.4 or 20.0)
    baseline_std_runs (if missing, fallback to 10.0)
    ups_score, ups_bucket if present
    model_anomaly_probability, model_anomaly_label if present
- Add TODO comments explaining these fallbacks.

- Implement a small helper function in UI:

    def call_narrate_api(payload: dict) -> dict:
        url = os.getenv("PLAIX_NARRATE_URL", "http://localhost:8000/narrate/anomaly")
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()

- Use the response to render a “story card”:

    story = call_narrate_api(payload)
    st.markdown(f"### {story.get('narrative_title','')}")
    st.write(story.get('narrative_summary',''))

- Next to the story (or below), show quick stats:

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Player", player_id)
    c2.metric("Runs", current_runs)
    c3.metric("UPS", f"{ups_score:.2f}" if available else "—")
    c4.metric("Model Prob", f"{prob:.2%}" if available else "—")

3) Add a button to refresh narration:
- Since LLM output can vary, add:
    if st.button("Regenerate Story"):
        call again and re-render

Use st.session_state to cache the story per featured anomaly to avoid repeated calls on every rerun.
Example:
- Store story in st.session_state["featured_story"]
- Key it with player_id + format + current_runs + ups_score

4) Graceful degradation:
- If the narration endpoint fails:
    - show st.warning("Could not generate narrative. Showing fallback message.")
    - show a simple rule-based summary in the UI:
        "Top anomaly: player scored X vs baseline Y (UPS Z)."

-------------------------------------------------------------------
PART C — Update README or inline docs (optional)
-------------------------------------------------------------------

5) Add a short comment or docstring in UI noting:
- PLAIX_NARRATE_URL can override the narration endpoint URL.
- Defaults to localhost.

-------------------------------------------------------------------
DELIVERABLES
-------------------------------------------------------------------

After implementing, show me:
1) The new backend endpoint code for POST /narrate/anomaly (including request/response models).
2) The updated portion of ui/demo_streamlit/demo_ui.py that renders:
   - Featured Anomaly Story box
   - API call helper
   - Regenerate button with session_state caching
3) Any new env vars introduced:
   - PLAIX_NARRATE_URL (optional)
