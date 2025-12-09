"""Placeholder football scorer that marks all events as non-anomalous."""

from __future__ import annotations

from typing import List


def score_events_from_dicts(events: List[dict]) -> List[dict]:
    """Return non-anomalous results for football placeholder."""
    results = []
    for event in events:
        results.append(
            {
                "sport": "football",
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "reason": "placeholder scorer",
                **event,
            }
        )
    return results
