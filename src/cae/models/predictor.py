"""Prediction helpers that bridge data frames and anomaly scoring."""

from __future__ import annotations

from typing import Iterable, List

import pandas as pd

from cae.data.schemas import AnomalyResult, EventInput
from cae.models.anomaly import DEFAULT_RUN_STD, DEFAULT_THRESHOLD, DEFAULT_WICKET_STD, score_events

REQUIRED_COLUMNS = {
    "match_id",
    "over",
    "ball",
    "runs",
    "wickets",
    "phase",
    "expected_runs",
    "expected_wickets",
}


def _validate_columns(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")


def score_dataframe(
    df: pd.DataFrame,
    *,
    run_std: float = DEFAULT_RUN_STD,
    wicket_std: float = DEFAULT_WICKET_STD,
    threshold: float = DEFAULT_THRESHOLD,
) -> List[AnomalyResult]:
    """Convert a DataFrame to EventInput objects and score them."""
    _validate_columns(df)
    events: List[EventInput] = [
        EventInput(
            match_id=row["match_id"],
            over=int(row["over"]),
            ball=int(row["ball"]),
            runs=float(row["runs"]),
            wickets=float(row["wickets"]),
            phase=str(row["phase"]),
            expected_runs=float(row["expected_runs"]),
            expected_wickets=float(row["expected_wickets"]),
        )
        for _, row in df.iterrows()
    ]
    return score_events(events, run_std=run_std, wicket_std=wicket_std, threshold=threshold)


def score_events_to_dataframe(
    events: Iterable[EventInput],
    *,
    run_std: float = DEFAULT_RUN_STD,
    wicket_std: float = DEFAULT_WICKET_STD,
    threshold: float = DEFAULT_THRESHOLD,
) -> pd.DataFrame:
    """Score EventInput objects and return a DataFrame of results."""
    results = score_events(events, run_std=run_std, wicket_std=wicket_std, threshold=threshold)
    return pd.DataFrame([result.model_dump() for result in results])
