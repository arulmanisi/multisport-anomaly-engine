"""CSV loader for PLAIX events."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {"match_id", "over", "ball", "runs", "wickets", "phase"}


def load_events_csv(path: str | Path) -> pd.DataFrame:
    """Load events CSV and validate required columns."""
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    return df
