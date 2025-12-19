You are my coding agent.

Feature 3: "Analyst Report Export" (one-click PDF report for an anomaly/event).

Goal (Backend):
Add an endpoint that generates a PDF report for an anomaly event including:
- Headline
- Narrative title and summary (tone selectable)
- Key drivers bullets
- Key stats table
- Baseline vs current runs chart (simple)
Return PDF bytes as a downloadable response.

Constraints:
- Use reportlab for PDF generation (already available).
- Do not require external services.
- Keep it MVP: one page report.

Tasks:

1) Create module:
   backend/app/report_export.py

2) Add endpoint:
   POST /report/anomaly/pdf

Request body:
{
  "player_id": str,
  "match_format": str,
  "date": optional str,
  "current_runs": float,
  "baseline_mean_runs": float,
  "baseline_std_runs": float,
  "ups_score": float,
  "ups_bucket": str,
  "model_anomaly_probability": float,
  "model_anomaly_label": int,
  "headline": optional str,
  "key_drivers": optional list[str],
  "tone": optional str default "analyst"
}

Behavior:
- Build AnomalyEvent and generate narrative using narrator.generate_description(tone=tone).
- Generate a PDF (reportlab):
  - Title: "Cricket Anomaly Report"
  - Headline line (bold)
  - Narrative section
  - Key Drivers bullets
  - Key stats table (runs, baseline, UPS, probability)
  - Simple bar chart style graphic: baseline vs current (can be drawn rectangles or small table)
- Return as FastAPI Response with:
  - media_type="application/pdf"
  - Content-Disposition attachment; filename like:
      anomaly_report_{player_id}_{match_format}.pdf

3) Wire router to FastAPI main.

After implementing, show:
- report_export.py
- Example curl command to download PDF.
