"""Placeholder anomaly scorer for PLAIX MVP."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


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
    """Trivial rule-based scorer for MVP placeholder."""
    is_anomaly = event.runs >= 6 or event.wickets >= 1
    score = 1.0 if is_anomaly else 0.0
    reason = "boundary or wicket" if is_anomaly else "within expected range"
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
