"""Simple anomaly detection logic based on z-scores."""

from __future__ import annotations

from math import sqrt
from typing import Iterable, List

from cae.data.schemas import AnomalyResult, EventInput

# Defaults chosen as simple, interpretable baselines. Calibrate with data later.
DEFAULT_RUN_STD = 1.5
DEFAULT_WICKET_STD = 0.25
DEFAULT_THRESHOLD = 2.0
_EPSILON = 1e-6


def _safe_std(value: float) -> float:
    """Prevent division by zero when caller supplies an extremely small std."""
    if value <= 0:
        return _EPSILON
    return value


def _build_reason(z_run: float, z_wicket: float, is_anomaly: bool) -> str:
    """Generate a simple human-readable reason for the score."""
    if not is_anomaly:
        return "within expected range"

    messages: List[str] = []
    if abs(z_run) >= 1.0:
        messages.append("runs higher than expected" if z_run > 0 else "runs lower than expected")
    if abs(z_wicket) >= 1.0:
        messages.append("more wickets than expected" if z_wicket > 0 else "fewer wickets than expected")

    if not messages:
        return "overall deviation from baseline"
    return "; ".join(messages)


def score_event(
    event: EventInput,
    *,
    run_std: float = DEFAULT_RUN_STD,
    wicket_std: float = DEFAULT_WICKET_STD,
    threshold: float = DEFAULT_THRESHOLD,
) -> AnomalyResult:
    """Compute anomaly score and label for a single event."""
    run_std = _safe_std(run_std)
    wicket_std = _safe_std(wicket_std)

    run_diff = event.runs - event.expected_runs
    wicket_diff = event.wickets - event.expected_wickets

    z_run = run_diff / run_std
    z_wicket = wicket_diff / wicket_std
    score = sqrt(z_run**2 + z_wicket**2)
    is_anomaly = score >= threshold
    reason = _build_reason(z_run, z_wicket, is_anomaly)

    return AnomalyResult(
        match_id=event.match_id,
        over=event.over,
        ball=event.ball,
        anomaly_score=score,
        is_anomaly=is_anomaly,
        reason=reason,
    )


def score_events(
    events: Iterable[EventInput],
    *,
    run_std: float = DEFAULT_RUN_STD,
    wicket_std: float = DEFAULT_WICKET_STD,
    threshold: float = DEFAULT_THRESHOLD,
) -> List[AnomalyResult]:
    """Vectorized scoring over a collection of events."""
    return [
        score_event(event, run_std=run_std, wicket_std=wicket_std, threshold=threshold)
        for event in events
    ]
