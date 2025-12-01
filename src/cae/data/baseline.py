"""Baseline computation helpers."""

from __future__ import annotations

from typing import Literal

import pandas as pd


def compute_phase_baselines(
    df: pd.DataFrame,
    *,
    phase_col: str = "phase",
    runs_col: str = "runs",
    wickets_col: str = "wickets",
    aggregation: Literal["mean", "median"] = "mean",
) -> pd.DataFrame:
    """Compute simple per-phase baselines for runs and wickets.

    Returns a DataFrame with columns [phase_col, expected_runs, expected_wickets].
    """
    if aggregation not in {"mean", "median"}:
        raise ValueError(f"Unsupported aggregation: {aggregation}")

    agg_fn = aggregation
    grouped = df.groupby(phase_col).agg(
        expected_runs=(runs_col, agg_fn),
        expected_wickets=(wickets_col, agg_fn),
    )
    grouped = grouped.reset_index()
    return grouped
