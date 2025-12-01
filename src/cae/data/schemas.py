"""Pydantic schemas for Cricket Anomaly Engine data models."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field, field_validator


class EventInput(BaseModel):
    """Single ball/phase event with expected baselines."""

    match_id: str = Field(..., description="Unique match identifier.")
    over: int = Field(..., ge=1, description="Over number (1-based).")
    ball: int = Field(..., ge=1, le=12, description="Ball number within the over.")
    runs: float = Field(..., description="Runs scored on this delivery.")
    wickets: float = Field(..., description="Wickets fallen on this delivery.")
    phase: str = Field(..., description="Match phase such as POWERPLAY, MIDDLE, DEATH.")
    expected_runs: float = Field(..., description="Baseline expected runs for this delivery.")
    expected_wickets: float = Field(..., description="Baseline expected wickets for this delivery.")

    @field_validator("match_id", "phase")
    @classmethod
    def non_empty_str(cls, value: str) -> str:
        """Ensure string fields are non-empty after stripping whitespace."""
        if not value or not value.strip():
            raise ValueError("value must be a non-empty string")
        return value.strip()

    @field_validator("runs", "wickets", "expected_runs", "expected_wickets", mode="before")
    @classmethod
    def numeric_not_none(cls, value: float) -> float:
        """Basic guard against None values sneaking in."""
        if value is None:
            raise ValueError("value cannot be None")
        return value


class BatchScoreRequest(BaseModel):
    """Request payload for anomaly scoring."""

    events: List[EventInput]


class AnomalyResult(BaseModel):
    """Anomaly detection output for a single event."""

    match_id: str
    over: int
    ball: int
    anomaly_score: float
    is_anomaly: bool
    reason: str


class BatchScoreResponse(BaseModel):
    """Response payload containing scored events."""

    results: List[AnomalyResult]
