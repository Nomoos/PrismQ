"""Tests for src configuration module."""

import pytest
import tempfile
import os
from pathlib import Path
from src import Config


@pytest.fixture
def temp_env_file():
    """Create a temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env') as f:
        f.write("DATABASE_URL=sqlite:///test.db\n")
        f.write("YOUTUBE_API_KEY=test_key\n")
        env_path = f.name
    
    yield env_path
    
    if os.path.exists(env_path):
        os.unlink(env_path)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    import tempfile
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup
    import shutil
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


@pytest.fixture
def clean_env():
    """Clean environment variables before and after test."""
    env_backup = {}
    env_vars = ['DATABASE_URL', 'WORKING_DIRECTORY', 'PRISMQ_WORKING_DIRECTORY', 
                'YOUTUBE_API_KEY', 'YOUTUBE_CHANNEL_URL']
    for var in env_vars:
        if var in os.environ:
            env_backup[var] = os.environ[var]
            del os.environ[var]
    
    yield
    
    # Restore environment variables
    for var, value in env_backup.items():
        os.environ[var] = value


def test_config_from_env_file(temp_env_file):
    """Test loading configuration from .env file."""
    config = Config(temp_env_file, interactive=False)
    
    # Database path should be absolute (relative to working directory)
    assert config.database_path.endswith("test.db")
    assert Path(config.database_path).is_absolute()
    assert config.youtube_api_key == "test_key"
    # youtube_max_results is a runtime parameter, not from env
    assert config.youtube_max_results == 50  # Default value from Config.DEFAULT_YOUTUBE_MAX_RESULTS


def test_config_defaults(temp_dir, clean_env):
    """Test configuration with default values."""
    # Create config without .env file (non-interactive)
    env_path = Path(temp_dir) / ".env"
    config = Config(str(env_path), interactive=False)
    
    # Database path should be absolute (relative to working directory)
    assert config.database_path.endswith("db.s3db")
    assert Path(config.database_path).is_absolute()
    # Runtime parameter defaults are class constants, not from env
    assert config.youtube_max_results == 50
    assert config.youtube_channel_max_shorts == 10
    assert config.youtube_trending_max_shorts == 10
    assert config.youtube_keyword_max_shorts == 10


def test_working_directory_stored(temp_dir, clean_env):
    """Test that working directory is stored in .env file."""
    env_path = Path(temp_dir) / ".env"
    
    # Create config
    config = Config(str(env_path), interactive=False)
    
    # Check that working directory is set
    assert config.working_directory == temp_dir
    
    # Check that it's stored in .env file
    assert env_path.exists()
    with open(env_path, 'r') as f:
        content = f.read()
        # The value might be quoted by set_key, so check for the value itself
        assert "WORKING_DIRECTORY=" in content
        assert temp_dir in content


def test_env_file_created_if_missing(temp_dir, clean_env):
    """Test that .env file is created if it doesn't exist."""
    env_path = Path(temp_dir) / ".env"
    
    # Ensure file doesn't exist
    assert not env_path.exists()
    
    # Create config
    config = Config(str(env_path), interactive=False)
    
    # Check that file was created
    assert env_path.exists()
    assert config.env_file == str(env_path)


def test_working_directory_from_env_file_path(temp_dir, clean_env):
    """Test that working directory is derived from env_file path."""
    env_path = Path(temp_dir) / "subdir" / ".env"
    env_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create config
    config = Config(str(env_path), interactive=False)
    
    # Check that working directory is the parent of .env file
    assert config.working_directory == str(env_path.parent.absolute())


def test_config_non_interactive_mode(temp_dir, clean_env):
    """Test that non-interactive mode doesn't prompt."""
    env_path = Path(temp_dir) / ".env"
    
    # Create config in non-interactive mode
    config = Config(str(env_path), interactive=False)
    
    # Should use defaults without prompting
    # Database path should be absolute (relative to working directory)
    assert config.database_path.endswith("db.s3db")
    assert Path(config.database_path).is_absolute()
    # Runtime parameters use class defaults, not from env
    assert config.youtube_max_results == 50


def test_existing_env_values_preserved(temp_dir, clean_env):
    """Test that existing .env values are preserved."""
    env_path = Path(temp_dir) / ".env"
    
    # Create .env with some values
    with open(env_path, 'w') as f:
        f.write("DATABASE_URL=sqlite:///custom.db\n")
        f.write("YOUTUBE_API_KEY=custom_key\n")
    
    # Create config
    config = Config(str(env_path), interactive=False)
    
    # Check that values are preserved
    # Database path should be absolute (relative to working directory)
    assert config.database_path.endswith("custom.db")
    assert Path(config.database_path).is_absolute()
    assert config.youtube_api_key == "custom_key"
    # Runtime parameters always use class defaults, not from env
    assert config.youtube_max_results == 50
    
    # Check that working directory was added
    with open(env_path, 'r') as f:
        content = f.read()
        assert "WORKING_DIRECTORY=" in content
        assert "DATABASE_URL=sqlite:///custom.db" in content


def test_standard_working_directory_with_explicit_env_path(temp_dir, clean_env):
    """Test that working directory is derived from env_file path when provided."""
    env_path = Path(temp_dir) / ".env"
    config = Config(str(env_path), interactive=False)
    
    # Working directory should be derived from env_file path, not the standard location
    # when env_file is explicitly provided
    assert config.working_directory == temp_dir


def test_standard_working_directory_fallback(temp_dir, clean_env):
    """Test that PRISMQ_WORKING_DIRECTORY env var overrides the default C:/PrismQ fallback."""
    # Override the working directory to use temp_dir for testing
    # Note: We use the override because C:/PrismQ may not exist in the test environment
    os.environ["PRISMQ_WORKING_DIRECTORY"] = temp_dir
    
    config = Config(interactive=False)
    
    # Working directory should use the override
    assert config.working_directory == temp_dir


def test_working_directory_override(temp_dir, clean_env):
    """Test that PRISMQ_WORKING_DIRECTORY environment variable overrides default."""
    custom_wd = temp_dir
    os.environ["PRISMQ_WORKING_DIRECTORY"] = custom_wd
    
    # Create config without specifying env_file
    config = Config(interactive=False)
    
    # Working directory should use the override
    assert config.working_directory == custom_wd


def test_get_module_directory(temp_dir, clean_env):
    """Test getting module directory paths."""
    env_path = Path(temp_dir) / ".env"
    config = Config(str(env_path), interactive=False)
    
    # Test without content_id
    t_dir = config.get_module_directory("T")
    assert t_dir == Path(temp_dir) / "T"
    
    # Test with content_id
    t_content_dir = config.get_module_directory("T", content_id="12345")
    assert t_content_dir == Path(temp_dir) / "T" / "12345"


def test_ensure_module_structure(temp_dir, clean_env):
    """Test ensuring module directory structure."""
    env_path = Path(temp_dir) / ".env"
    config = Config(str(env_path), interactive=False)
    
    # Module directory should not exist yet
    t_dir = Path(temp_dir) / "T"
    assert not t_dir.exists()
    
    # Ensure structure
    config.ensure_module_structure("T")
    
    # Module directory should now exist
    assert t_dir.exists()
    assert t_dir.is_dir()


def test_database_url_absolute_path(temp_dir, clean_env):
    """Test that absolute database paths are preserved."""
    env_path = Path(temp_dir) / ".env"
    abs_db_path = Path(temp_dir) / "custom" / "db.s3db"
    
    with open(env_path, 'w') as f:
        f.write(f"DATABASE_URL=sqlite:///{abs_db_path}\n")
    
    config = Config(str(env_path), interactive=False)
    
    # Absolute path should be preserved
    assert config.database_path == str(abs_db_path)


def test_database_url_relative_path(temp_dir, clean_env):
    """Test that relative database paths are resolved to working directory."""
    env_path = Path(temp_dir) / ".env"
    
    with open(env_path, 'w') as f:
        f.write("DATABASE_URL=sqlite:///relative.db\n")
    
    config = Config(str(env_path), interactive=False)
    
    # Relative path should be resolved to working directory
    assert config.database_path == str(Path(temp_dir) / "relative.db")


def test_non_sqlite_database_url(temp_dir, clean_env):
    """Test handling of non-SQLite database URLs."""
    env_path = Path(temp_dir) / ".env"
    
    with open(env_path, 'w') as f:
        f.write("DATABASE_URL=postgresql://user:pass@localhost/db\n")
    
    config = Config(str(env_path), interactive=False)
    
    # For non-SQLite, database_path should fallback to default SQLite path
    assert config.database_path == str(Path(temp_dir) / "db.s3db")
    # But database_url should be preserved
    assert config.database_url == "postgresql://user:pass@localhost/db"


def test_runtime_parameters_are_constants(temp_dir, clean_env):
    """Test that runtime parameters come from class constants, not environment."""
    env_path = Path(temp_dir) / ".env"
    
    # Try to set runtime parameters in environment (should be ignored)
    os.environ["YOUTUBE_MAX_RESULTS"] = "999"
    
    config = Config(str(env_path), interactive=False)
    
    # Runtime parameters should use class defaults, not env
    assert config.youtube_max_results == Config.DEFAULT_YOUTUBE_MAX_RESULTS
    assert config.youtube_max_results == 50  # Not 999
