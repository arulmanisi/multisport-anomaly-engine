import pandas as pd
import pytest

from plaix.data.baselines import attach_baselines, compute_phase_baselines


def sample_df():
    return pd.DataFrame(
        {
            "match_id": ["M1", "M1", "M1"],
            "over": [1, 2, 18],
            "ball": [1, 1, 1],
            "runs": [4, 2, 10],
            "wickets": [0, 1, 0],
            "phase": ["POWERPLAY", "MIDDLE", "DEATH"],
        }
    )


def test_compute_phase_baselines() -> None:
    df = sample_df()

    baselines = compute_phase_baselines(df)

    assert set(baselines.columns) == {"phase", "expected_runs", "expected_wickets"}
    assert len(baselines) == 3


def test_attach_baselines_success() -> None:
    df = sample_df()
    baselines = compute_phase_baselines(df)

    with_baselines = attach_baselines(df, baselines)

    assert "expected_runs" in with_baselines.columns
    assert "expected_wickets" in with_baselines.columns
    assert not with_baselines["expected_runs"].isna().any()


def test_attach_baselines_missing_phase() -> None:
    df = sample_df()
    baselines = compute_phase_baselines(df[df["phase"] != "DEATH"])

    with pytest.raises(ValueError):
        attach_baselines(df, baselines)
