"""Tests for configuration module."""

import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv, set_key

from src.config import Config


def test_config_defaults():
    """Test that configuration has sensible defaults."""
    config = Config(interactive=False)
    assert config.app_name == os.getenv("APP_NAME", "PrismQ.ModuleName")
    assert config.app_env in ["development", "production", "testing"]
    assert isinstance(config.debug, bool)


def test_config_directories():
    """Test that configuration creates necessary directories."""
    config = Config(interactive=False)
    assert config.input_dir.exists()
    assert config.output_dir.exists()
    assert config.cache_dir.exists()


def test_config_api_key():
    """Test API key retrieval."""
    config = Config(interactive=False)
    # Should return None for non-existent keys
    assert config.get_api_key("nonexistent") is None


def test_config_python_executable():
    """Test Python executable configuration."""
    config = Config(interactive=False)
    # Should have a default value
    assert config.python_executable is not None
    assert isinstance(config.python_executable, str)
    # Default should be "python"
    assert config.python_executable == os.getenv("PYTHON_EXECUTABLE", "python")


def test_working_directory_stored():
    """Test that working directory is stored in .env file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".env"

        # Create config
        config = Config(str(env_path), interactive=False)

        # Check that working directory is set
        assert config.working_directory == tmpdir

        # Check that it's stored in .env file
        assert env_path.exists()
        with open(env_path, 'r') as f:
            content = f.read()
            assert "WORKING_DIRECTORY=" in content


def test_env_file_created_if_missing():
    """Test that .env file is created if it doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".env"

        # Ensure file doesn't exist
        assert not env_path.exists()

        # Create config
        config = Config(str(env_path), interactive=False)

        # Check that file was created
        assert env_path.exists()
        assert config.env_file == str(env_path)


def test_working_directory_from_cwd():
    """Test that working directory defaults to current directory when no PrismQ dir found."""
    # Save original cwd
    original_cwd = os.getcwd()

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to temp directory (no PrismQ in path)
            os.chdir(tmpdir)

            # Create config without specifying env_file
            config = Config(interactive=False)

            # Check that working directory is the temp directory (fallback)
            assert config.working_directory == tmpdir
            assert config.env_file == str(Path(tmpdir) / ".env")
    finally:
        # Restore original cwd
        os.chdir(original_cwd)


def test_working_directory_finds_prismq_parent():
    """Test that working directory finds topmost parent with exact name PrismQ."""
    # Save original cwd
    original_cwd = os.getcwd()

    try:
        with tempfile.TemporaryDirectory() as base_temp:
            # Create a temporary directory structure with exact name "PrismQ"
            prismq_dir = Path(base_temp) / "PrismQ"
            subdir = prismq_dir / "subdirectory" / "nested"
            subdir.mkdir(parents=True, exist_ok=True)

            # Change to nested subdirectory
            os.chdir(subdir)

            # Create config without specifying env_file
            config = Config(interactive=False)

            # Check that working directory is PrismQ_WD (sibling to PrismQ)
            expected_wd = Path(base_temp) / "PrismQ_WD"
            assert config.working_directory == str(expected_wd)
            assert config.env_file == str(expected_wd / ".env")
            assert (expected_wd / ".env").exists()
    finally:
        # Restore original cwd
        os.chdir(original_cwd)


def test_working_directory_from_env_file_path():
    """Test that working directory is derived from env_file path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / "subdir" / ".env"
        env_path.parent.mkdir(parents=True, exist_ok=True)

        # Create config
        config = Config(str(env_path), interactive=False)

        # Check that working directory is the parent of .env file
        assert config.working_directory == str(env_path.parent.absolute())


def test_config_non_interactive_mode():
    """Test that non-interactive mode doesn't prompt."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".env"

        # Create config in non-interactive mode
        config = Config(str(env_path), interactive=False)

        # Should use defaults without prompting
        assert config.app_name == "PrismQ.ModuleName"
        assert config.python_executable == "python"


def test_existing_env_values_preserved():
    """Test that existing .env values are preserved."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".env"

        # Create .env with some values
        with open(env_path, 'w') as f:
            f.write("APP_NAME=CustomApp\n")
            f.write("DEBUG=false\n")

        # Create config
        config = Config(str(env_path), interactive=False)

        # Check that values are preserved
        assert config.app_name == "CustomApp"
        assert not config.debug

        # Check that working directory was added
        with open(env_path, 'r') as f:
            content = f.read()
            assert "WORKING_DIRECTORY=" in content


def test_topmost_prismq_directory():
    """Test that the topmost PrismQ directory is found, not just the first one."""
    # Save original cwd
    original_cwd = os.getcwd()

    try:
        with tempfile.TemporaryDirectory() as base_temp:
            # Create nested PrismQ directories
            outer_prismq = Path(base_temp) / "PrismQ"
            inner_prismq = outer_prismq / "modules" / "PrismQ" / "submodule"
            inner_prismq.mkdir(parents=True, exist_ok=True)

            # Change to innermost directory
            os.chdir(inner_prismq)

            # Create config without specifying env_file
            config = Config(interactive=False)

            # Check that working directory is from the topmost (outer) PrismQ
            expected_wd = Path(base_temp) / "PrismQ_WD"
            assert config.working_directory == str(expected_wd)
    finally:
        # Restore original cwd
        os.chdir(original_cwd)


def test_get_or_prompt_non_interactive():
    """Test _get_or_prompt in non-interactive mode."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".env"

        # Create config in non-interactive mode
        config = Config(str(env_path), interactive=False)

        # Test getting a value that doesn't exist
        value = config._get_or_prompt("NONEXISTENT_KEY", "Some description", "default_value")
        assert value == "default_value"

        # Test getting a value that exists
        os.environ["TEST_KEY"] = "test_value"
        value = config._get_or_prompt("TEST_KEY", "Some description", "default_value")
        assert value == "test_value"

        # Cleanup
        del os.environ["TEST_KEY"]


def test_env_write_test_value():
    """Test writing a test value to .env file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = Path(tmpdir) / ".env"
        
        # Create config (this creates the .env file)
        config = Config(str(env_path), interactive=False)
        
        # Write a test value to .env
        test_key = "TEST_VALUE"
        test_value = "test_data_12345"
        set_key(env_path, test_key, test_value)
        
        # Verify the value was written to the file
        with open(env_path, 'r') as f:
            content = f.read()
            # set_key adds quotes around values, so check for the key in the content
            assert test_key in content
            assert test_value in content
        
        # Verify we can read it back using os.getenv after reloading
        load_dotenv(env_path, override=True)
        assert os.getenv(test_key) == test_value
        
        # Cleanup
        if test_key in os.environ:
            del os.environ[test_key]


def test_working_directory_creation():
    """Test that working directory is physically created."""
    with tempfile.TemporaryDirectory() as base_tmpdir:
        # Create a path for working directory that doesn't exist yet
        working_dir = Path(base_tmpdir) / "test_working_dir"
        env_path = working_dir / ".env"
        
        # Ensure the working directory doesn't exist before creating config
        assert not working_dir.exists()
        
        # Create config - this should create the working directory
        config = Config(str(env_path), interactive=False)
        
        # Verify the working directory was created
        assert working_dir.exists()
        assert working_dir.is_dir()
        
        # Verify the .env file is in the working directory
        assert env_path.exists()
        assert env_path.is_file()
        
        # Verify config.working_directory points to the created directory
        assert config.working_directory == str(working_dir.absolute())

