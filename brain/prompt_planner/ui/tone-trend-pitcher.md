You are my coding agent.

Goal:
Improve the Streamlit UI with three features:
1) Tone selector (analyst/commentator/casual) used for LLM narration
2) A "Recent Innings Trend" view that shows last N innings story and chart
3) A "How to pitch this" helper section for demo guidance

Constraints:
- Keep existing /predict/single flow working.
- If backend does not yet expose last N innings data, add a minimal demo endpoint.
- Keep all changes MVP-friendly (no large refactors).

-------------------------------------------------------------------
PART A — Tone selector and pass tone to backend
-------------------------------------------------------------------

1) Update Streamlit UI (ui/demo_streamlit/demo_ui.py):
- Add a selector near inputs:

    tone = st.selectbox(
        "Narrative Tone",
        options=["analyst", "commentator", "casual"],
        index=0,
        help="Controls how the AI narrative is written."
    )

- When calling the backend for single prediction, include "tone" in the request payload.
  Example JSON payload addition:
      "tone": tone

- Make sure the UI reads narrative_title and narrative_summary from API response as before.

2) Update backend /predict/single endpoint:
- Accept an optional "tone" field in request body (default "analyst").
- Use this tone when calling narrator.generate_description(event, tone=tone).
- Return narrative_title and narrative_summary as before.

Note:
- Keep backward compatibility: if tone is not provided, behave like "analyst".

-------------------------------------------------------------------
PART B — Add "Recent Innings Trend" view using multi-event summary
-------------------------------------------------------------------

3) UI navigation:
- Convert the UI to include two tabs:

    tab1, tab2 = st.tabs(["Single Innings", "Recent Innings Trend"])

- Move the existing single-innings UI into tab1 with minimal changes.
- Implement tab2 as a player-focused view.

4) Recent Innings Trend (tab2) UI requirements:
- Inputs:
    - player_id (text input)
    - match_format (selectbox)
    - last_n (slider 3–10, default 5)
    - tone (reuse same tone selector or add separate tone selector)

- Behavior:
    - Calls a backend endpoint to fetch last N innings for that player+format
      along with computed UPS and model scores for each innings.
    - Calls a backend endpoint to generate a multi-event summary:
         summary_title, summary_body
      (or a combined endpoint that returns both events + summary)

- Display:
    1) Summary area:
       - headline: summary_title
       - paragraph: summary_body

    2) Trend chart:
       - plot a simple line chart of UPS score across the last N innings
         (x-axis index or date, y-axis ups_score)
       - if model probability is available, optionally plot as another line (but keep it simple).

    3) Table:
       - A compact table listing each innings row:
           date, runs_scored, baseline_mean_runs, ups_score, ups_bucket, model_probability

5) Backend support for last N events (minimal demo-ready endpoint):
- Add a new endpoint in FastAPI:

    GET /player/{player_id}/recent?format=T20&n=5

  It should return a JSON list of the last N events (most recent last or first—be consistent),
  each event including:
      - date (string)
      - current_runs
      - baseline_mean_runs
      - baseline_std_runs
      - ups_score
      - ups_bucket
      - ups_anomaly_flag_baseline
      - model_anomaly_probability
      - model_anomaly_label

Implementation approach for MVP:
- If you already have a local dataset (e.g., per_innings_with_ups.csv or synthetic),
  load it once at startup or lazily, then filter by player_id + format and take last N by date.
- If no real dataset is available, create a small in-memory demo dataset for P_DEMO
  (5–10 fake innings) so the UI is demoable.
- Add TODOs for wiring real Cricsheet ingestion later.

6) Add an endpoint to get the multi-event summary:
Option A (preferred): One endpoint does both:
    POST /player/recent/summary
    body:
      { "player_id": "...", "match_format": "...", "n": 5, "tone": "analyst" }

Return:
    {
      "events": [...],
      "summary_title": "...",
      "summary_body": "..."
    }

Option B:
- UI calls GET /player/{id}/recent then calls narrator.generate_sequence_summary locally.
But better to keep LLM calls server-side.

Implement Option A.

In the backend handler:
- Build AnomalyEvent objects from the recent events.
- Call narrator.generate_sequence_summary(events, tone=tone).
- Return summary + events.

-------------------------------------------------------------------
PART C — Add "How to pitch this" helper section
-------------------------------------------------------------------

7) In Streamlit UI, add a collapsible expander near the top or in the right panel:

    with st.expander("How to pitch this demo"):
        st.markdown("""
        **Suggested 60–90 second talk track:**
        1. "This is an AI anomaly engine, not a win predictor."
        2. "We build a baseline of expected performance per player and format."
        3. "UPS quantifies how unexpected an innings is vs historical behavior."
        4. "The ML model adds context and outputs anomaly probability."
        5. "The LLM narrates results so users get an immediate explanation."
        6. "The trend view shows behavior across recent innings—volatility, breakouts, stabilization."
        """)

- Keep it short and professional.

-------------------------------------------------------------------
DELIVERABLES / SHOW ME
-------------------------------------------------------------------

After implementing, show me:

1) Updated ui/demo_streamlit/demo_ui.py with:
   - tone selector
   - two tabs
   - trend view with chart + table + summary
   - pitch helper expander

2) Backend changes:
   - updated /predict/single to accept tone
   - new endpoint for recent trend summary (Option A)
   - any minimal demo dataset logic if real data is not present

Ensure everything still runs locally with:
- backend: uvicorn ...
- UI: streamlit run ...
