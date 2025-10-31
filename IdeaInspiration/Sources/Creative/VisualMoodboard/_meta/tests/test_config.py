"""Tests for configuration module."""

import pytest
import tempfile
import os
from pathlib import Path
from src.core.config import Config


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
        f.write("DATABASE_URL=sqlite:///test_lyrics.s3db\n")
        f.write("GENIUS_API_KEY=test_key\n")
        f.write("GENIUS_MAX_RESULTS=25\n")
        env_path = f.name
    
    yield env_path
    
    if os.path.exists(env_path):
        os.unlink(env_path)


def test_config_from_env_file(temp_env_file):
    """Test loading configuration from .env file."""
    config = Config(temp_env_file, interactive=False)
    
    assert config.database_path.endswith("test_lyrics.s3db")
    assert Path(config.database_path).is_absolute()
    assert config.genius_api_key == "test_key"
    assert config.genius_max_results == 25


def test_config_defaults():
    """Test configuration with default values."""
    with tempfile.TemporaryDirectory() as temp_dir:
        env_file = Path(temp_dir) / ".env"
        env_file.touch()
        
        config = Config(str(env_file), interactive=False)
        
        # Should use default or test_lyrics.s3db from environment
        assert config.database_path.endswith(".s3db")
        # Note: genius_max_results may vary if picked up from environment
        assert config.genius_max_results > 0


def test_config_database_url():
    """Test DATABASE_URL configuration."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
        f.write("DATABASE_URL=sqlite:///custom_lyrics.s3db\n")
        env_path = f.name
    
    try:
        config = Config(env_path, interactive=False)
        assert "custom_lyrics.s3db" in config.database_url
        assert config.database_path.endswith("custom_lyrics.s3db")
    finally:
        if os.path.exists(env_path):
            os.unlink(env_path)
