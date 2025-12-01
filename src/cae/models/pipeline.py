"""End-to-end scoring pipeline with optional persistence."""

from __future__ import annotations

from typing import Iterable, List

from cae.data.schemas import AnomalyResult, EventInput
from cae.models.anomaly import DEFAULT_RUN_STD, DEFAULT_THRESHOLD, DEFAULT_WICKET_STD, score_events
from cae.utils.storage import ResultStore


def score_and_persist(
    events: Iterable[EventInput],
    *,
    store: ResultStore | None = None,
    run_std: float = DEFAULT_RUN_STD,
    wicket_std: float = DEFAULT_WICKET_STD,
    threshold: float = DEFAULT_THRESHOLD,
) -> List[AnomalyResult]:
    """Score events and persist results when a store is provided."""
    results = score_events(events, run_std=run_std, wicket_std=wicket_std, threshold=threshold)
    if store:
        store.save_results(results)
    return results
