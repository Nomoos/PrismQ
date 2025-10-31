"""Tests for Etsy Trending configuration."""

import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.config import Config


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup
    import shutil
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


def test_config_defaults(temp_dir):
    """Test configuration with default values."""
    env_backup = {}
    env_vars = ['DATABASE_URL', 'ETSY_CATEGORIES', 'ETSY_MAX_LISTINGS', 'WORKING_DIRECTORY']
    for var in env_vars:
        if var in os.environ:
            env_backup[var] = os.environ[var]
            del os.environ[var]
    
    try:
        env_path = Path(temp_dir) / ".env"
        config = Config(str(env_path), interactive=False)
        
        assert config.database_path.endswith("db.s3db")
        assert Path(config.database_path).is_absolute()
        assert len(config.etsy_categories) > 0
        assert config.etsy_max_listings == 50
    finally:
        for var, value in env_backup.items():
            os.environ[var] = value


def test_config_working_directory(temp_dir):
    """Test that working directory is set correctly."""
    env_path = Path(temp_dir) / ".env"
    config = Config(str(env_path), interactive=False)
    
    assert config.working_directory is not None
    assert Path(config.working_directory).exists()


def test_config_category_parsing(temp_dir):
    """Test parsing of comma-separated categories."""
    env_path = Path(temp_dir) / ".env"
    with open(env_path, 'w') as f:
        f.write("ETSY_CATEGORIES=jewelry, home-living , art,craft-supplies\n")
    
    config = Config(str(env_path), interactive=False)
    assert config.etsy_categories == ["jewelry", "home-living", "art", "craft-supplies"]
