You are my coding agent.

Feature 3 UI: "Analyst Report Export" button.

Goal (UI):
Add a "Download Analyst Report (PDF)" button in:
- Single Innings tab (after results)
- Featured Anomaly Story box (leaderboard)
- Optional: Anomaly Feed detail view

The button should call backend POST /report/anomaly/pdf and allow the user
to download the PDF directly from Streamlit.

Constraints:
- Use Streamlit st.download_button.
- Use requests to fetch PDF bytes from backend.
- Keep it demo-friendly.

Tasks:

1) Add an API helper:
- call_report_pdf(payload) -> bytes
  POST to http://localhost:8000/report/anomaly/pdf
  return response.content

Use env override base URL PLAIX_REPORT_URL default "http://localhost:8000".

2) In Single Innings tab:
- After result is computed, build payload including:
   player_id, match_format, current_runs, baseline_mean_runs, baseline_std_runs,
   ups_score, ups_bucket, model_anomaly_probability, model_anomaly_label,
   headline (if you have), key_drivers (if you have), tone
- Call call_report_pdf(payload) when button clicked.
- Use st.download_button with filename:
   f"anomaly_report_{player_id}_{match_format}.pdf"

3) In Featured Anomaly Story section:
- Reuse the featured anomaly fields and allow PDF download.

4) Degrade gracefully if report endpoint errors:
- show st.error with a helpful message.

After implementing, show me the updated sections where the download button appears.
