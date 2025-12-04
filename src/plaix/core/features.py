"""Core feature extraction abstractions for PLAIX."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import BaseModel


class FeatureExtractionInput(BaseModel):
    """Generic input schema for feature extraction."""

    sport: str
    payload: dict


class FeatureExtractionOutput(BaseModel):
    """Generic output schema for extracted features."""

    sport: str
    match_id: str
    features: Dict[str, Any]


class FeatureExtractor(ABC):
    """Base class for sport-specific feature extractors."""

    sport: str

    @abstractmethod
    def extract(self, data: FeatureExtractionInput) -> FeatureExtractionOutput:
        """Extract model-ready features from raw sport-specific payload."""
