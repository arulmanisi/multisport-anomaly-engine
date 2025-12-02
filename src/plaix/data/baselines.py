"""Baseline computation utilities for PLAIX."""

from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = {"match_id", "over", "ball", "runs", "wickets", "phase"}


def compute_phase_baselines(df: pd.DataFrame) -> pd.DataFrame:
    """Compute mean runs/wickets per phase."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if df.empty:
        raise ValueError("Cannot compute baselines on empty DataFrame")
    grouped = (
        df.groupby("phase")
        .agg(expected_runs=("runs", "mean"), expected_wickets=("wickets", "mean"))
        .reset_index()
    )
    return grouped


def attach_baselines(df: pd.DataFrame, baselines: pd.DataFrame) -> pd.DataFrame:
    """Attach expected runs/wickets per phase to events."""
    merged = df.merge(baselines, on="phase", how="left")
    if merged["expected_runs"].isna().any() or merged["expected_wickets"].isna().any():
        missing_phases = merged.loc[
            merged["expected_runs"].isna() | merged["expected_wickets"].isna(), "phase"
        ].unique()
        raise ValueError(f"Missing baselines for phases: {', '.join(missing_phases)}")
    return merged
