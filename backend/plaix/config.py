"""Configuration placeholders for PLAIX."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime settings for PLAIX service."""

    service_name: str = "plaix"
    log_level: str = "INFO"
    anomaly_run_threshold: float = 6.0
    anomaly_wicket_threshold: float = 1.0


settings = Settings()
