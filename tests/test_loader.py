import pandas as pd
import pytest

from plaix.data.loader import load_events_csv


def test_load_events_csv_valid(tmp_path) -> None:
    csv_path = tmp_path / "events.csv"
    df = pd.DataFrame(
        {
            "match_id": ["M1"],
            "over": [1],
            "ball": [1],
            "runs": [4],
            "wickets": [0],
            "phase": ["POWERPLAY"],
        }
    )
    df.to_csv(csv_path, index=False)

    loaded = load_events_csv(csv_path)

    assert not loaded.empty
    assert set(loaded.columns) == {"match_id", "over", "ball", "runs", "wickets", "phase"}


def test_load_events_csv_missing_columns(tmp_path) -> None:
    csv_path = tmp_path / "events.csv"
    df = pd.DataFrame({"match_id": ["M1"], "runs": [4]})
    df.to_csv(csv_path, index=False)

    with pytest.raises(ValueError):
        load_events_csv(csv_path)
