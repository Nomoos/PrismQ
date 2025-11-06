"""Configuration management for PrismQ Web Client Backend."""

import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "PrismQ Web Client"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # Execution
    MAX_CONCURRENT_RUNS: int = 10
    
    # Directories
    LOG_DIR: str = "./logs"
    CONFIG_DIR: str = "./configs"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    def get_log_dir(self) -> Path:
        """Get log directory as Path object."""
        return Path(self.LOG_DIR)
    
    def get_config_dir(self) -> Path:
        """Get config directory as Path object."""
        return Path(self.CONFIG_DIR)


# Global settings instance
settings = Settings()
