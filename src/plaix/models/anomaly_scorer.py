"""Placeholder anomaly scorer for PLAIX MVP."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from plaix.config import settings


class AnomalyRequest(BaseModel):
    """Minimal event input for anomaly scoring."""

    match_id: str
    over: int = Field(..., ge=1)
    ball: int = Field(..., ge=1)
    runs: float
    wickets: float


class AnomalyResponse(BaseModel):
    """Anomaly scoring result."""

    match_id: str
    over: int
    ball: int
    anomaly_score: float
    is_anomaly: bool
    reason: str


def score_event(event: AnomalyRequest) -> AnomalyResponse:
    """Rule-based scorer using configurable thresholds."""
    run_thresh = getattr(settings, "anomaly_run_threshold", 6)
    wicket_thresh = getattr(settings, "anomaly_wicket_threshold", 1)

    is_run_spike = event.runs >= run_thresh
    is_wicket_event = event.wickets >= wicket_thresh

    is_anomaly = is_run_spike or is_wicket_event
    score = float(event.runs) + (5.0 if is_wicket_event else 0.0)
    reason_parts = []
    if is_run_spike:
        reason_parts.append(f"runs >= {run_thresh}")
    if is_wicket_event:
        reason_parts.append(f"wickets >= {wicket_thresh}")
    reason = "; ".join(reason_parts) if reason_parts else "within expected range"

    return AnomalyResponse(
        match_id=event.match_id,
        over=event.over,
        ball=event.ball,
        anomaly_score=score,
        is_anomaly=is_anomaly,
        reason=reason,
    )


def score_events(events: List[AnomalyRequest]) -> List[AnomalyResponse]:
    """Score a list of events."""
    return [score_event(event) for event in events]
