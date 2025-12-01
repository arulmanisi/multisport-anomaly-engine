"""Synthetic data generation for Cricket Anomaly Engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import numpy as np

from cae.data.schemas import EventInput


@dataclass(frozen=True)
class PhaseConfig:
    """Baseline expectations per phase."""

    expected_runs: float
    expected_wickets: float


DEFAULT_PHASE_BASELINES = {
    "POWERPLAY": PhaseConfig(expected_runs=1.0, expected_wickets=0.05),
    "MIDDLE": PhaseConfig(expected_runs=0.8, expected_wickets=0.04),
    "DEATH": PhaseConfig(expected_runs=1.2, expected_wickets=0.06),
}


def _phase_for_over(over: int) -> str:
    """Assign phase based on over number (T20 defaults)."""
    if over <= 6:
        return "POWERPLAY"
    if over <= 16:
        return "MIDDLE"
    return "DEATH"


def simulate_match_events(
    *,
    match_id: str = "SIM-1",
    overs: int = 20,
    balls_per_over: int = 6,
    anomaly_rate: float = 0.1,
    run_noise: float = 0.5,
    wicket_noise: float = 0.01,
    seed: int | None = None,
    phase_baselines: dict[str, PhaseConfig] = DEFAULT_PHASE_BASELINES,
) -> List[EventInput]:
    """Generate a list of synthetic EventInput objects."""
    rng = np.random.default_rng(seed)
    events: List[EventInput] = []

    for over in range(1, overs + 1):
        phase = _phase_for_over(over)
        baseline = phase_baselines[phase]

        for ball in range(1, balls_per_over + 1):
            expected_runs = max(0.0, baseline.expected_runs + rng.normal(0, 0.1))
            expected_wickets = max(0.0, baseline.expected_wickets + rng.normal(0, 0.005))

            runs = max(0.0, rng.normal(expected_runs, run_noise))
            wickets = 1.0 if rng.random() < expected_wickets + wicket_noise else 0.0

            if rng.random() < anomaly_rate:
                # Inject simple anomalies: spike runs or unexpected wicket cluster.
                if rng.random() < 0.6:
                    runs = expected_runs + abs(rng.normal(4.0, 1.0))
                else:
                    wickets = 1.0
                    runs = max(0.0, runs - abs(rng.normal(1.0, 0.5)))

            events.append(
                EventInput(
                    match_id=match_id,
                    over=over,
                    ball=ball,
                    runs=runs,
                    wickets=wickets,
                    phase=phase,
                    expected_runs=expected_runs,
                    expected_wickets=expected_wickets,
                )
            )

    return events


def events_to_dataframe(events: Iterable[EventInput]):
    """Convert events to a pandas DataFrame without importing pandas globally."""
    import pandas as pd  # Local import to keep optional dependency surface lean.

    return pd.DataFrame([event.model_dump() for event in events])
