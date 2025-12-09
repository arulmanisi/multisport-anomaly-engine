from plaix.config import settings


def test_config_defaults() -> None:
    assert settings.service_name == "plaix"
    assert settings.anomaly_run_threshold == 6.0
    assert settings.anomaly_wicket_threshold == 1.0
