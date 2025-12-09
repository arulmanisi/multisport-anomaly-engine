import json
from pathlib import Path
from typing import List

import pytest

from plaix import cli


def run_cli(args: List[str], capsys) -> str:
    cli.main(args)
    captured = capsys.readouterr()
    return captured.out


def test_cli_predict_single(monkeypatch, tmp_path: Path, capsys) -> None:
    # Patch model load and run_inference behavior to avoid heavy dependencies
    class DummyModel:
        def predict_proba(self, X):
            return [[0.1, 0.9]]

        def predict(self, X):
            return [1]

    monkeypatch.setattr(cli, "load_model", lambda model_path: DummyModel())
    monkeypatch.setattr(cli, "build_feature_extractor", lambda: None)

    payload = {
        "player_id": "P1",
        "match_format": "T20",
        "baseline_mean_runs": 22,
        "baseline_std_runs": 10,
        "current_runs": 40,
    }
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(payload))

    out = run_cli(["predict-single", "--input", str(payload_file), "--model", "model.pkl"], capsys)

    assert "ups_score" in out
    assert "ups_bucket" in out
    assert "model_anomaly_probability" in out


def test_cli_predict_batch(monkeypatch, tmp_path: Path, capsys) -> None:
    class DummyModel:
        def predict_proba(self, X):
            return [[0.2, 0.8] for _ in X]

        def predict(self, X):
            return [1 for _ in X]

    monkeypatch.setattr(cli, "load_model", lambda model_path: DummyModel())
    monkeypatch.setattr(cli, "build_feature_extractor", lambda: None)

    batch_file = tmp_path / "batch.json"
    batch_file.write_text(
        json.dumps(
            [
                {
                    "player_id": "P1",
                    "match_format": "T20",
                    "baseline_mean_runs": 22,
                    "baseline_std_runs": 10,
                    "current_runs": 30,
                }
            ]
        )
    )

    out = run_cli(["predict-batch", "--input", str(batch_file), "--model", "model.pkl"], capsys)

    assert "ups_score" in out
    assert "ups_bucket" in out
    assert "model_anomaly_probability" in out
