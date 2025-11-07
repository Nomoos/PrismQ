"""Tests for ConfigLoad module."""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path to import ConfigLoad
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import Config, find_prismq_directory


class TestConfig:
    """Test Config class."""

    def test_create_config_with_custom_env_file(self):
        """Test creating Config with a custom .env file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            config = Config(env_file=str(env_file), interactive=False)
            
            assert config.env_file == str(env_file)
            assert config.working_directory == tmpdir
            assert env_file.exists()

    def test_create_config_creates_env_file(self):
        """Test that Config creates .env file if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / "test_env" / ".env"
            
            assert not env_file.exists()
            config = Config(env_file=str(env_file), interactive=False)
            assert env_file.exists()

    def test_get_configuration_value(self):
        """Test getting configuration values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            
            # Create .env file with a value
            with open(env_file, 'w') as f:
                f.write("TEST_KEY=test_value\n")
            
            config = Config(env_file=str(env_file), interactive=False)
            
            # Should be loaded into environment
            assert config.get("TEST_KEY") == "test_value"

    def test_get_with_default(self):
        """Test get with default value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            config = Config(env_file=str(env_file), interactive=False)
            
            assert config.get("NONEXISTENT", "default_value") == "default_value"
            assert config.get("NONEXISTENT") is None

    def test_set_configuration_value(self):
        """Test setting configuration values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            config = Config(env_file=str(env_file), interactive=False)
            
            config.set("NEW_KEY", "new_value")
            
            # Verify it's in the environment
            assert config.get("NEW_KEY") == "new_value"
            
            # Verify it's persisted to file (python-dotenv may add quotes)
            with open(env_file, 'r') as f:
                content = f.read()
                assert "NEW_KEY" in content
                assert "new_value" in content

    def test_working_directory_is_stored(self):
        """Test that working directory is automatically stored in .env."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            config = Config(env_file=str(env_file), interactive=False)
            
            # WORKING_DIRECTORY should be set
            assert config.get("WORKING_DIRECTORY") == tmpdir

    def test_get_or_prompt_non_interactive_with_default(self):
        """Test get_or_prompt in non-interactive mode returns default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            config = Config(env_file=str(env_file), interactive=False)
            
            value = config.get_or_prompt(
                "MISSING_KEY",
                "Enter value",
                default="default_value",
                required=False
            )
            
            assert value == "default_value"

    def test_get_or_prompt_returns_existing_value(self):
        """Test get_or_prompt returns existing value without prompting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            
            # Pre-populate .env
            with open(env_file, 'w') as f:
                f.write("EXISTING_KEY=existing_value\n")
            
            config = Config(env_file=str(env_file), interactive=True)
            
            value = config.get_or_prompt(
                "EXISTING_KEY",
                "Enter value",
                default="default_value",
                required=True
            )
            
            assert value == "existing_value"

    def test_find_prismq_directory_current(self):
        """Test finding PrismQ directory when current directory is PrismQ."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prismq_dir = Path(tmpdir) / "PrismQ"
            prismq_dir.mkdir()
            
            original_cwd = os.getcwd()
            try:
                os.chdir(str(prismq_dir))
                
                result = find_prismq_directory()
                assert result == prismq_dir
            finally:
                os.chdir(original_cwd)

    def test_find_prismq_directory_parent(self):
        """Test finding PrismQ directory in parent path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prismq_dir = Path(tmpdir) / "PrismQ"
            prismq_dir.mkdir()
            sub_dir = prismq_dir / "Module1" / "SubModule"
            sub_dir.mkdir(parents=True)
            
            original_cwd = os.getcwd()
            try:
                os.chdir(str(sub_dir))
                
                result = find_prismq_directory()
                assert result == prismq_dir
            finally:
                os.chdir(original_cwd)

    def test_find_prismq_directory_topmost(self):
        """Test finding the topmost PrismQ directory when multiple exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested PrismQ directories
            outer_prismq = Path(tmpdir) / "PrismQ"
            outer_prismq.mkdir()
            inner_prismq = outer_prismq / "nested" / "PrismQ"
            inner_prismq.mkdir(parents=True)
            sub_dir = inner_prismq / "subdirectory"
            sub_dir.mkdir()
            
            original_cwd = os.getcwd()
            try:
                os.chdir(str(sub_dir))
                
                result = find_prismq_directory()
                # Should find the topmost (outer) PrismQ
                assert result == outer_prismq
            finally:
                os.chdir(original_cwd)

    def test_find_prismq_directory_none_found(self):
        """Test finding PrismQ directory when none exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            regular_dir = Path(tmpdir) / "regular" / "directory"
            regular_dir.mkdir(parents=True)
            
            original_cwd = os.getcwd()
            try:
                os.chdir(str(regular_dir))
                
                result = find_prismq_directory()
                # Should return None when no PrismQ directory found
                assert result is None
            finally:
                os.chdir(original_cwd)

    def test_config_creates_prismq_wd_directory(self):
        """Test that Config creates PrismQ_WD directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prismq_dir = Path(tmpdir) / "PrismQ"
            prismq_dir.mkdir()
            
            original_cwd = os.getcwd()
            try:
                os.chdir(str(prismq_dir))
                
                config = Config(interactive=False)
                
                # Should create PrismQ_WD at the same level as PrismQ
                expected_wd = Path(tmpdir) / "PrismQ_WD"
                assert expected_wd.exists()
                assert config.working_directory == str(expected_wd)
                
                # .env should be in PrismQ_WD
                expected_env = expected_wd / ".env"
                assert expected_env.exists()
                assert config.env_file == str(expected_env)
            finally:
                os.chdir(original_cwd)

    def test_config_without_prismq_uses_current_directory(self):
        """Test that Config uses current directory when no PrismQ found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            regular_dir = Path(tmpdir) / "regular"
            regular_dir.mkdir()
            
            original_cwd = os.getcwd()
            try:
                os.chdir(str(regular_dir))
                
                config = Config(interactive=False)
                
                # Should use current directory as working directory
                assert config.working_directory == str(regular_dir)
                assert Path(config.env_file) == regular_dir / ".env"
            finally:
                os.chdir(original_cwd)

    def test_environment_variable_persistence(self):
        """Test that environment variables persist across Config instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            
            # First instance sets a value
            config1 = Config(env_file=str(env_file), interactive=False)
            config1.set("PERSIST_KEY", "persist_value")
            
            # Second instance should load it
            config2 = Config(env_file=str(env_file), interactive=False)
            assert config2.get("PERSIST_KEY") == "persist_value"

    def test_config_handles_special_characters(self):
        """Test that Config handles special characters in values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            config = Config(env_file=str(env_file), interactive=False)
            
            # Test with special characters
            special_value = "user=admin;password=secret@123"
            config.set("CONNECTION_STRING", special_value)
            
            # Should retrieve the same value
            assert config.get("CONNECTION_STRING") == special_value


class TestConfigEdgeCases:
    """Test edge cases and error handling."""

    def test_config_with_empty_env_file(self):
        """Test Config with an empty .env file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.touch()
            
            config = Config(env_file=str(env_file), interactive=False)
            
            # Should still work, just no variables loaded
            assert config.env_file == str(env_file)

    def test_config_with_unicode_values(self):
        """Test Config handles unicode characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            config = Config(env_file=str(env_file), interactive=False)
            
            unicode_value = "Hello 世界 🌍"
            config.set("UNICODE_KEY", unicode_value)
            
            # Should handle unicode correctly
            assert config.get("UNICODE_KEY") == unicode_value

    def test_config_directory_with_spaces(self):
        """Test Config handles directory paths with spaces."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "dir with spaces"
            test_dir.mkdir()
            env_file = test_dir / ".env"
            
            config = Config(env_file=str(env_file), interactive=False)
            
            assert config.env_file == str(env_file)
            assert env_file.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
