"""Core request/response models for multi-sport scoring."""

from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    """Top-level score request including sport identifier."""

    sport: str = Field(..., description="Sport identifier, e.g., cricket, football.")
    events: List[Any]


class ScoreResponse(BaseModel):
    """Generic score response wrapper."""

    results: List[Any]
