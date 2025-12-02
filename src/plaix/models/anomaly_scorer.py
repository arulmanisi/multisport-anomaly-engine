"""Placeholder anomaly scorer for PLAIX MVP."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

import pandas as pd

from plaix.config import settings


class AnomalyRequest(BaseModel):
    """Minimal event input for anomaly scoring."""

    match_id: str
    over: int = Field(..., ge=1)
    ball: int = Field(..., ge=1)
    runs: float
    wickets: float
    expected_runs: float | None = None
    expected_wickets: float | None = None


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
    if event.expected_runs is None or event.expected_wickets is None:
        raise ValueError("Run baseline attachment first: expected_runs/expected_wickets missing.")

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


def prepare_requests_from_df(df: pd.DataFrame) -> List[AnomalyRequest]:
    """Convert a DataFrame to AnomalyRequest list with validation."""
    required = {"match_id", "over", "ball", "runs", "wickets", "expected_runs", "expected_wickets"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns for requests: {', '.join(sorted(missing))}")

    if df[["expected_runs", "expected_wickets"]].isna().any().any():
        raise ValueError("Expected values contain NaNs; compute baselines first.")

    events: List[AnomalyRequest] = [
        AnomalyRequest(
            match_id=str(row["match_id"]),
            over=int(row["over"]),
            ball=int(row["ball"]),
            runs=float(row["runs"]),
            wickets=float(row["wickets"]),
            expected_runs=float(row["expected_runs"]),
            expected_wickets=float(row["expected_wickets"]),
        )
        for _, row in df.iterrows()
    ]
    return events
