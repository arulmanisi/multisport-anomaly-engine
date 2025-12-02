"""Helpers to go from CSV → baselines → requests ready for scoring."""

from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from plaix.data.baselines import attach_baselines, compute_phase_baselines
from plaix.data.loader import load_events_csv
from plaix.models.anomaly_scorer import AnomalyRequest, prepare_requests_from_df


def prepare_events_for_scoring(csv_path: str | Path) -> List[AnomalyRequest]:
    """Load events, compute baselines, attach expected values, and return requests."""
    df = load_events_csv(csv_path)
    baselines = compute_phase_baselines(df)
    df_with_expected = attach_baselines(df, baselines)
    return prepare_requests_from_df(df_with_expected)


def dataframe_to_requests(df: pd.DataFrame) -> List[AnomalyRequest]:
    """Convert a dataframe (with expected values attached) to requests."""
    return prepare_requests_from_df(df)
