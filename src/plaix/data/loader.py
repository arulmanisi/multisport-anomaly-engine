"""CSV loader for PLAIX events."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {"match_id", "over", "ball", "runs", "wickets", "phase"}


def load_events_csv(path: str | Path) -> pd.DataFrame:
    """Load events CSV, validate schema, and enforce basic dtypes."""
    df = pd.read_csv(path)
    df.columns = [col.strip() for col in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    df = df.copy()
    df["match_id"] = df["match_id"].astype(str).str.strip()
    df["phase"] = df["phase"].astype(str).str.strip().str.upper()
    df["over"] = df["over"].astype(int)
    df["ball"] = df["ball"].astype(int)
    df["runs"] = df["runs"].astype(float)
    df["wickets"] = df["wickets"].astype(float)
    return df
