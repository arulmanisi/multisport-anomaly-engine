"""Generate a synthetic UPS training dataset."""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pandas as pd

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "synthetic_ups_dataset.csv"
N_ROWS = 200


def sample_baseline() -> tuple[float, float]:
    """Sample baseline mean/std for runs, clipped to reasonable cricket ranges."""
    mean = float(np.clip(np.random.normal(22, 8), 5, 60))
    std = float(np.clip(np.random.uniform(5, 20), 5, 20))
    return mean, std


def sample_context() -> tuple[float, float, int]:
    """Sample simple context features."""
    venue_flatness = float(np.clip(np.random.beta(2, 5), 0, 1))
    opposition_strength = float(np.clip(np.random.beta(5, 2), 0, 1))
    batting_position = int(np.random.randint(1, 8))
    return venue_flatness, opposition_strength, batting_position


def derive_bucket_and_flag(ups: float) -> tuple[str, int]:
    """Bucket and flag based on UPS thresholds."""
    if ups < 1.0:
        return "normal", 0
    if ups < 2.0:
        return "mild_spike", 0
    if ups < 3.0:
        return "strong_spike", 1
    return "extreme_spike", 1


def generate_row(player_id: str, match_format: str) -> dict:
    """Generate one synthetic innings row."""
    mean_runs, std_runs = sample_baseline()

    # Draw epsilon: mostly modest noise, occasional big spike.
    if random.random() < 0.15:
        epsilon = np.random.normal(std_runs * 2.5, std_runs)  # spike
    else:
        epsilon = np.random.normal(0, std_runs)  # normal variation

    current_runs = float(max(0, mean_runs + epsilon))
    ups_raw = (current_runs - mean_runs) / max(std_runs, 5.0)
    ups_score = float(np.clip(max(ups_raw, 0.0), 0, 5))
    bucket, flag = derive_bucket_and_flag(ups_score)

    venue_flatness, opposition_strength, batting_position = sample_context()

    return {
        "player_id": player_id,
        "match_format": match_format,
        "baseline_mean_runs": mean_runs,
        "baseline_std_runs": std_runs,
        "current_runs": current_runs,
        "ups_score": ups_score,
        "ups_anomaly_flag": flag,
        "ups_bucket": bucket,
        "venue_flatness": venue_flatness,
        "opposition_strength": opposition_strength,
        "batting_position": batting_position,
    }


def main() -> None:
    players = [f"P{i}" for i in range(1, 11)]
    match_format = "T20"

    rows = []
    for _ in range(N_ROWS):
        player_id = random.choice(players)
        rows.append(generate_row(player_id, match_format))

    df = pd.DataFrame(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(df.head())
    print(f"\nSaved {len(df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
