"""Anomaly feed utilities (MVP) for FastAPI endpoints."""

from __future__ import annotations

import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

import pandas as pd
from fastapi import HTTPException

from llm.anomaly_narrator import AnomalyEvent, AnomalyNarrator
from llm.factory import get_llm_client_from_env


DATA_CANDIDATES = [
    Path("data/processed/per_innings_with_ups.csv"),
    Path("data/synthetic_ups_dataset.csv"),
]

_NARRATOR = AnomalyNarrator(get_llm_client_from_env())


def _build_demo_dataset() -> pd.DataFrame:
    """Create a small synthetic dataset for demo purposes."""
    records = []
    start_date = datetime(2024, 1, 1)
    players = [f"P_DEMO_{i}" for i in range(1, 11)]
    formats = ["T20", "ODI", "TEST"]
    runs_pattern = [18, 24, 32, 15, 55, 42, 28, 65, 33, 48, 72, 14]
    for idx in range(30):
        player = players[idx % len(players)]
        match_format = formats[idx % len(formats)]
        current_runs = runs_pattern[idx % len(runs_pattern)] + (idx % 7)
        baseline_mean = 25 + (idx % 5)
        baseline_std = 8 + (idx % 3)
        ups_score = (current_runs - baseline_mean) / max(baseline_std, 1)
        bucket = "normal"
        if ups_score >= 3:
            bucket = "extreme_spike"
        elif ups_score >= 2:
            bucket = "strong_spike"
        elif ups_score >= 1:
            bucket = "mild_spike"
        flag = 1 if ups_score >= 2 else 0
        records.append(
            {
                "player_id": player,
                "match_format": match_format,
                "date": (start_date + timedelta(days=idx)).strftime("%Y-%m-%d"),
                "current_runs": current_runs,
                "baseline_mean_runs": baseline_mean,
                "baseline_std_runs": baseline_std,
                "ups_score": ups_score,
                "ups_bucket": bucket,
                "ups_anomaly_flag_baseline": flag,
                "model_anomaly_probability": min(max(0.2 + 0.05 * ups_score, 0.01), 0.99),
                "model_anomaly_label": 1 if flag else 0,
                "venue_flatness": 0.4 + 0.05 * (idx % 4),
                "opposition_strength": 0.3 + 0.07 * (idx % 4),
                "batting_position": 3 + (idx % 4),
            }
        )
    return pd.DataFrame.from_records(records)


def load_feed_dataset() -> pd.DataFrame:
    """Load feed dataset, with demo fallback."""
    for path in DATA_CANDIDATES:
        if path.exists():
            try:
                df = pd.read_csv(path)
            except Exception:
                continue
            if "player_id" not in df.columns and "player_name" in df.columns:
                df = df.rename(columns={"player_name": "player_id"})
            if "current_runs" not in df.columns and "runs_scored" in df.columns:
                df = df.rename(columns={"runs_scored": "current_runs"})
            if "date" in df.columns:
                df["date"] = df["date"].astype(str)
            else:
                df["date"] = ""
            return df
    return _build_demo_dataset()


def _combined_score(row: pd.Series) -> float:
    """Compute combined severity using UPS and model probability when available."""
    ups = row.get("ups_score", 0.0) or 0.0
    prob = row.get("model_anomaly_probability", math.nan)
    if pd.notna(prob):
        return 0.7 * ups + 0.3 * (prob * 5.0)
    return ups


def _build_headline(row: pd.Series) -> str:
    """Rule-based sports headline."""
    player = row.get("player_id", "Player")
    fmt = row.get("match_format", "T20")
    runs = row.get("current_runs", "a breakout innings")
    baseline = row.get("baseline_mean_runs")
    baseline_text = f"usual {baseline:.0f}" if pd.notna(baseline) else "typical baseline"
    bucket = str(row.get("ups_bucket", "normal"))
    if bucket in {"extreme_spike", "strong_spike"}:
        return f"{player} lights up {fmt} with a breakout {runs} — way above the {baseline_text}"
    if bucket == "mild_spike":
        return f"{player} finds extra gears in {fmt}, posting {runs} beyond the {baseline_text}"
    return f"Featured anomaly: {player} posts {runs} in {fmt}"


def _build_key_drivers(row: pd.Series) -> List[str]:
    """Rule-based bullets describing drivers."""
    drivers: List[str] = []
    ups = row.get("ups_score", None)
    if ups is not None and pd.notna(ups):
        if ups >= 3:
            drivers.append(f"Extreme spike (≈ {ups:.1f}σ above baseline)")
        elif ups >= 2:
            drivers.append(f"Strong spike (≈ {ups:.1f}σ above baseline)")
        elif ups >= 1:
            drivers.append(f"Moderate spike (≈ {ups:.1f}σ above baseline)")
        else:
            drivers.append(f"Near baseline (≈ {ups:.1f}σ)")
    else:
        drivers.append("Spike magnitude not available")

    opp = row.get("opposition_strength", None)
    if opp is not None and pd.notna(opp):
        if opp > 0.7:
            drivers.append("Strong opposition increases anomaly confidence.")
        elif opp < 0.3:
            drivers.append("Weaker opposition may soften anomaly significance.")
    venue = row.get("venue_flatness", None)
    if venue is not None and pd.notna(venue):
        if venue > 0.7:
            drivers.append("Batting-friendly venue may partially explain the spike.")
        elif venue < 0.3:
            drivers.append("Bowler-friendly venue makes the spike more impressive.")
    if not drivers or len(drivers) < 2:
        drivers.append("Context: baseline vs current runs drives this anomaly.")
    return drivers[:3]


def list_feed_items(df: pd.DataFrame, match_format: str = "ALL", min_ups: float = 0.0, min_prob: float = 0.0, limit: int = 25, sort: str = "combined") -> List[dict]:
    """Filter and rank feed items."""
    data = df.copy()
    if match_format and match_format != "ALL":
        data = data[data["match_format"] == match_format]
    if "ups_score" in data.columns:
        data = data[data["ups_score"] >= min_ups]
    if "model_anomaly_probability" in data.columns and not data["model_anomaly_probability"].isna().all():
        data = data[data["model_anomaly_probability"].fillna(0) >= min_prob]

    if data.empty:
        return []

    data["combined_score"] = data.apply(_combined_score, axis=1)
    sort_col = "combined_score" if sort == "combined" and "combined_score" in data.columns else "ups_score"
    data = data.sort_values(sort_col, ascending=False).head(min(limit, 100))

    items = []
    for _, row in data.iterrows():
        event_id = f"{row.get('player_id', 'player')}-{row.get('date', '')}-{row.get('match_format', 'T20')}"
        item = row.to_dict()
        item["event_id"] = event_id
        item["headline"] = _build_headline(row)
        item["key_drivers"] = _build_key_drivers(row)
        items.append(item)
    return items


def get_event_detail(df: pd.DataFrame, event_id: str) -> pd.Series:
    """Retrieve event by id."""
    matches = df.apply(
        lambda r: f"{r.get('player_id', '')}-{r.get('date', '')}-{r.get('match_format', '')}" == event_id, axis=1
    )
    if not matches.any():
        raise HTTPException(status_code=404, detail="Event not found")
    return df[matches].iloc[0]


def narrate_event(row: pd.Series, tone: str = "commentator") -> dict:
    """Generate narrative for an event row."""
    event = AnomalyEvent(
        player_id=row.get("player_id", "unknown"),
        match_format=row.get("match_format", "T20"),
        team=None,
        opposition=None,
        venue=None,
        baseline_mean_runs=row.get("baseline_mean_runs", 20.0),
        baseline_std_runs=row.get("baseline_std_runs", 10.0),
        current_runs=row.get("current_runs", 0.0),
        ups_score=row.get("ups_score", 0.0),
        ups_bucket=row.get("ups_bucket", "normal"),
        ups_anomaly_flag_baseline=row.get("ups_anomaly_flag_baseline", 0),
        model_anomaly_probability=row.get("model_anomaly_probability", 0.0),
        model_anomaly_label=row.get("model_anomaly_label", 0),
        match_context={},
    )
    return _NARRATOR.generate_description(event, tone=tone or "commentator")
