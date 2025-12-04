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
    # Patch model load and run_inference behavior to avoid NotImplemented
    monkeypatch.setattr(cli, "load_model", lambda model_path: None)
    monkeypatch.setattr(cli, "build_feature_extractor", lambda: None)

    payload = {"features": {"runs": 10}}
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(payload))

    out = run_cli(["predict-single", "--input", str(payload_file), "--model", "model.pkl"], capsys)

    assert "ups_score" in out
    assert "is_anomalous" in out


def test_cli_predict_batch(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(cli, "load_model", lambda model_path: None)
    monkeypatch.setattr(cli, "build_feature_extractor", lambda: None)

    batch_file = tmp_path / "batch.json"
    batch_file.write_text(json.dumps([{"features": {"runs": 1}}]))

    out = run_cli(["predict-batch", "--input", str(batch_file), "--model", "model.pkl"], capsys)

    assert "ups_score" in out
    assert "is_anomalous" in out
