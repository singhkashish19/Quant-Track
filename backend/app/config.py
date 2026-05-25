"""
Application Configuration Management

This module handles environment-based configuration using Pydantic Settings.
Supports development, testing, and production environments.
"""

from functools import lru_cache
from typing import List, Optional

try:
    from pydantic import BaseSettings, Field, field_validator
except ImportError:
    from pydantic_settings import BaseSettings
    from pydantic import Field, field_validator

ConfigDict = dict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = ConfigDict(
        extra="allow",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "QuantTrack"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"

    # Database
    database_url: str = Field("sqlite:///./quanttrack.db", env="DATABASE_URL")
    db_echo: bool = False

    # Redis (optional, not required for core API)
    redis_url: str = "redis://localhost:6379/0"

    # JWT & Security
    secret_key: str = Field("your_super_secret_key_change_in_production", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/quanttrack.log"

    # Model paths
    ml_model_path: str = "./backend/app/ml/model_storage/"
    retrain_interval_days: int = 7

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "development", "dev"}:
                return True
            if normalized in {"0", "false", "no", "off", "production", "prod", "release"}:
                return False
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Optional[str]):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache()
def get_settings() -> Settings:
    """Return the shared settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
