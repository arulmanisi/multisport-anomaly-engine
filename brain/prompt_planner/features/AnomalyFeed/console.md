You are my coding agent.

Feature 1 UI: "Anomaly Feed" SOC-style console.

Goal (UI):
Add a new tab "Anomaly Feed" in ui/demo_streamlit/demo_ui.py that:
- Pulls anomalies from GET /feed/anomalies
- Shows filter controls
- Renders a feed of cards
- Clicking/selecting an item shows a detail drawer with narrative, drivers, and a small chart

Constraints:
- Keep existing tabs working.
- No secrets in UI. It just calls backend.
- Must be demo-friendly and fast.

Tasks:

1) Add a new tab:
   ["Single Innings", "Recent Innings Trend", "Top Anomalies", "Anomaly Feed"]

2) Add API helpers:
- call_feed_list(format, min_ups, min_prob, limit, sort) -> dict
  calls GET http://localhost:8000/feed/anomalies with query params.
- call_feed_detail(event_id, tone) -> dict
  calls GET http://localhost:8000/feed/anomaly/{event_id}?tone=...

Use env overrides:
- PLAIX_FEED_URL base default "http://localhost:8000"
  so list URL is f"{base}/feed/anomalies"

3) UI layout (Anomaly Feed tab):
- Left side filters:
  - format selectbox (ALL/T20/ODI/TEST)
  - min_ups slider (0–5)
  - min_prob slider (0–1)
  - limit slider (10–50)
  - sort selectbox ("combined","ups")
  - tone selectbox ("analyst","commentator","casual") for detail narrative

- Right side feed results:
  - For each item, render a card-like block showing:
      headline (bold)
      player_id, format, date
      UPS score, probability, bucket, combined score
      key drivers bullets (3 items)
  - Add a “View details” button per item which sets st.session_state["selected_event_id"]

4) Detail panel:
- If selected_event_id present:
  - Call call_feed_detail(selected_event_id, tone)
  - Render:
      - narrative title + summary
      - key drivers bullets
      - metric row
      - small chart baseline vs current runs (bar chart)
  - Add “Clear selection” button

5) Keep it professional:
- Use clear headings and spacing, st.divider() where needed.
- Degrade gracefully if backend unreachable (show st.error).

After implementing, show me the updated Anomaly Feed tab code.
