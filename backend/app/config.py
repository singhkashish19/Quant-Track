"""
Application Configuration Management

This module handles environment-based configuration using Pydantic Settings.
Supports development, testing, and production environments.
"""

from functools import lru_cache
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application Settings
    
    Configuration is loaded from environment variables or .env file.
    Use model_config to specify env_file location.
    """
    
    # Application
    app_name: str = "QuantTrack"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"
    
    # Database
    database_url: str = "postgresql://quanttrack_user:password@localhost:5432/quanttrack_db"
    db_echo: bool = False
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT & Security
    secret_key: str = "your_super_secret_key_change_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # ML & NLP
    ml_model_path: str = "./app/ml/model_storage/"
    retrain_interval_days: int = 7
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/quanttrack.log"

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
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached).
    
    Returns:
        Settings: Application configuration object
    """
    return Settings()


# Global settings instance
settings = get_settings()
