"""Configuration placeholders for PLAIX."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime settings for PLAIX service."""

    service_name: str = "plaix"
    log_level: str = "INFO"


settings = Settings()
