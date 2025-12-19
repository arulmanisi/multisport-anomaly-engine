"""PDF report export for anomaly events (MVP, single-page)."""

from __future__ import annotations

import io
from typing import List

from fastapi import HTTPException
from fastapi.responses import Response
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from llm.anomaly_narrator import AnomalyEvent, AnomalyNarrator
from llm.factory import get_llm_client_from_env

narrator = AnomalyNarrator(get_llm_client_from_env())


def _draw_bar(c: canvas.Canvas, x: float, y: float, width: float, height: float, label: str, value: float):
    """Draw simple bar with label."""
    c.setFillColor(colors.darkblue)
    c.rect(x, y, width, height, fill=True, stroke=False)
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 8)
    c.drawString(x, y - 10, f"{label}: {value:.1f}")


def generate_pdf(request: dict) -> bytes:
    """Generate a one-page PDF report."""
    required_fields = [
        "player_id",
        "match_format",
        "current_runs",
        "baseline_mean_runs",
        "baseline_std_runs",
        "ups_score",
        "ups_bucket",
        "model_anomaly_probability",
        "model_anomaly_label",
    ]
    for field in required_fields:
        if field not in request:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")

    tone = request.get("tone", "analyst")
    event = AnomalyEvent(
        player_id=request["player_id"],
        match_format=request["match_format"],
        team=None,
        opposition=None,
        venue=None,
        baseline_mean_runs=request["baseline_mean_runs"],
        baseline_std_runs=request["baseline_std_runs"],
        current_runs=request["current_runs"],
        ups_score=request["ups_score"],
        ups_bucket=request["ups_bucket"],
        ups_anomaly_flag_baseline=request.get("ups_anomaly_flag_baseline", 0),
        model_anomaly_probability=request["model_anomaly_probability"],
        model_anomaly_label=request["model_anomaly_label"],
        match_context={},
    )
    narrative = narrator.generate_description(event, tone=tone or "analyst")

    headline = request.get("headline") or narrative.get("narrative_title") or "Anomaly highlight"
    key_drivers: List[str] = request.get("key_drivers") or []
    if not key_drivers:
        key_drivers = [
            f"UPS: {request['ups_score']:.2f} ({request['ups_bucket']})",
            f"Baseline vs current: {request['baseline_mean_runs']:.1f} → {request['current_runs']}",
            f"Model probability: {request['model_anomaly_probability']:.2%}",
        ]

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    styles = getSampleStyleSheet()

    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, height - 72, "Cricket Anomaly Report")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, height - 96, headline)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(72, height - 120, narrative.get("narrative_title", "Narrative"))
    text = Paragraph(narrative.get("narrative_summary", ""), styles["BodyText"])
    text.wrapOn(c, width - 144, 80)
    text.drawOn(c, 72, height - 210)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(72, height - 230, "Key drivers")
    y = height - 245
    c.setFont("Helvetica", 10)
    for driver in key_drivers[:3]:
        c.drawString(80, y, f"• {driver}")
        y -= 14

    y -= 10
    c.setFont("Helvetica-Bold", 11)
    c.drawString(72, y, "Key stats")
    y -= 16
    stats = [
        f"Player: {request['player_id']} ({request['match_format']})",
        f"Runs: {request['current_runs']}",
        f"Baseline: {request['baseline_mean_runs']:.1f} ± {request['baseline_std_runs']:.1f}",
        f"UPS: {request['ups_score']:.2f} ({request['ups_bucket']})",
        f"Model probability: {request['model_anomaly_probability']:.2%}",
    ]
    c.setFont("Helvetica", 10)
    for stat in stats:
        c.drawString(80, y, stat)
        y -= 14

    y -= 10
    c.setFont("Helvetica-Bold", 11)
    c.drawString(72, y, "Baseline vs Current")
    y -= 20
    bar_height = 20
    max_runs = max(request["baseline_mean_runs"], request["current_runs"], 1)
    scale = 200 / max_runs
    _draw_bar(c, 80, y, request["baseline_mean_runs"] * scale, bar_height, "Baseline", request["baseline_mean_runs"])
    _draw_bar(c, 80, y - 35, request["current_runs"] * scale, bar_height, "Current", request["current_runs"])

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def build_pdf_response(request: dict) -> Response:
    """Create a PDF Response."""
    pdf_bytes = generate_pdf(request)
    filename = f"anomaly_report_{request.get('player_id','player')}_{request.get('match_format','T20')}.pdf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
