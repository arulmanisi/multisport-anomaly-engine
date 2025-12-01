from cae.data.schemas import EventInput
from cae.models.pipeline import score_and_persist
from cae.utils.storage import ResultStore


def test_score_and_persist_round_trip(tmp_path) -> None:
    store = ResultStore(tmp_path / "cae.db")
    events = [
        EventInput(
            match_id="M1",
            over=1,
            ball=1,
            runs=8,
            wickets=0,
            phase="POWERPLAY",
            expected_runs=3.0,
            expected_wickets=0.05,
        )
    ]

    results = score_and_persist(events, store=store)

    assert len(results) == 1
    assert results[0].is_anomaly is True

    recent = store.fetch_recent(limit=5)
    assert len(recent) == 1
    assert recent[0].match_id == "M1"
