You are my coding agent.

Feature 2 UI: "Live Match Mode" (simulated streaming innings timeline).

Goal (UI):
Add a new tab "Live Match Mode" in ui/demo_streamlit/demo_ui.py that:
- Starts a live simulation session
- Plays through steps automatically (play/pause) or manually (next)
- Shows real-time updates: risk level, UPS, probability, narrative
- Shows a line chart of UPS over time and cumulative runs

Constraints:
- Use backend endpoints /live/start and /live/step/{session_id}.
- Keep it demo-friendly; no complex async required.

Tasks:

1) Add new tab:
   ["Single Innings", "Recent Innings Trend", "Top Anomalies", "Anomaly Feed", "Live Match Mode"]

2) Add API helpers:
- call_live_start(payload) -> dict  (POST /live/start)
- call_live_step(session_id, i, include_narrative, tone) -> dict (GET /live/step/...)

Use env override base URL PLAIX_LIVE_URL default "http://localhost:8000"

3) UI layout:
- Left controls:
  - player selector (reuse dropdown)
  - match_format selector
  - scenario selector (normal/breakout/collapse)
  - baseline sliders
  - overs (10–20)
  - tone selector
  - include narrative checkbox (default true)
  - Start Session button

- Playback controls:
  - Play / Pause toggle using st.session_state
  - Next Step button
  - Step speed slider (0.2–2.0 seconds)
  - Reset button (stop session and clear state)

4) Rendering:
- At each step, show:
  - risk label (green/orange/red)
  - metrics row (runs, UPS, prob, bucket)
  - headline + narrative summary
  - key drivers bullets

- Maintain a session_state list of steps to plot:
  - cumulative_runs vs step index
  - ups_score vs step index

Use st.line_chart with DataFrame.

5) Auto-play:
- Implement a simple loop using time.sleep when "Play" is enabled:
  - Each rerun advances one step until end.
  - Keep it stable; do not create infinite loops.
  - Use st.experimental_rerun to continue playback.

If complexity is high, implement manual step first and add play after.

After implementing, show the new Live Match Mode tab code.
