"""Tests for configuration manager."""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from config_manager import ConfigManager, get_working_directory_from_env, setup_working_directory


class TestConfigManager:
    """Test ConfigManager class."""

    def test_create_config_manager_with_directory(self):
        """Test creating ConfigManager with a specific directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ConfigManager(tmpdir)
            assert config.working_dir == Path(tmpdir).resolve()
            assert config.env_file == Path(tmpdir).resolve() / ".env"
            assert config.config == {}

    def test_create_config_manager_without_directory(self):
        """Test creating ConfigManager without directory uses current directory."""
        config = ConfigManager()
        assert config.working_dir == Path.cwd().resolve()

    def test_ensure_exists_creates_env_file(self):
        """Test ensure_exists creates .env file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ConfigManager(tmpdir)
            env_file = Path(tmpdir) / ".env"
            
            assert not env_file.exists()
            config.ensure_exists()
            assert env_file.exists()

    def test_set_and_get_config_value(self):
        """Test setting and getting configuration values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ConfigManager(tmpdir)
            
            config.set('TEST_KEY', 'test_value')
            assert config.get('TEST_KEY') == 'test_value'
            
            # Verify persisted to file
            with open(config.env_file, 'r') as f:
                content = f.read()
                assert 'TEST_KEY=test_value' in content

    def test_get_with_default(self):
        """Test get with default value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ConfigManager(tmpdir)
            
            assert config.get('NONEXISTENT', 'default_value') == 'default_value'
            assert config.get('NONEXISTENT') is None

    def test_has_config_key(self):
        """Test checking if configuration key exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ConfigManager(tmpdir)
            
            assert not config.has('TEST_KEY')
            config.set('TEST_KEY', 'value')
            assert config.has('TEST_KEY')

    def test_update_multiple_values(self):
        """Test updating multiple configuration values at once."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ConfigManager(tmpdir)
            
            config.update({
                'KEY1': 'value1',
                'KEY2': 'value2',
                'KEY3': 'value3'
            })
            
            assert config.get('KEY1') == 'value1'
            assert config.get('KEY2') == 'value2'
            assert config.get('KEY3') == 'value3'
            
            # Verify persisted to file
            with open(config.env_file, 'r') as f:
                content = f.read()
                assert 'KEY1=value1' in content
                assert 'KEY2=value2' in content
                assert 'KEY3=value3' in content

    def test_load_existing_env_file(self):
        """Test loading configuration from existing .env file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            
            # Create .env file with some values
            with open(env_file, 'w') as f:
                f.write("# Comment line\n")
                f.write("KEY1=value1\n")
                f.write("KEY2=value2\n")
                f.write("\n")  # Empty line
                f.write("KEY3=value3\n")
            
            # Load config
            config = ConfigManager(tmpdir)
            
            assert config.get('KEY1') == 'value1'
            assert config.get('KEY2') == 'value2'
            assert config.get('KEY3') == 'value3'

    def test_preserve_values_with_equals_sign(self):
        """Test that values containing = are handled correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ConfigManager(tmpdir)
            
            config.set('CONNECTION_STRING', 'user=admin;password=secret')
            assert config.get('CONNECTION_STRING') == 'user=admin;password=secret'
            
            # Reload and verify
            config2 = ConfigManager(tmpdir)
            assert config2.get('CONNECTION_STRING') == 'user=admin;password=secret'

    def test_config_file_format(self):
        """Test that .env file is formatted correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ConfigManager(tmpdir)
            
            config.update({
                'BETA_KEY': 'beta_value',
                'ALPHA_KEY': 'alpha_value',
                'GAMMA_KEY': 'gamma_value'
            })
            
            with open(config.env_file, 'r') as f:
                lines = f.readlines()
            
            # Check header comments exist
            assert any('PrismQ Module Configuration' in line for line in lines)
            
            # Check keys are sorted
            key_lines = [line for line in lines if '=' in line and not line.strip().startswith('#')]
            keys = [line.split('=')[0] for line in key_lines]
            assert keys == sorted(keys)


class TestGetWorkingDirectory:
    """Test get_working_directory_from_env function."""

    def test_get_from_environment_variable(self):
        """Test getting working directory from environment variable."""
        test_dir = '/test/working/directory'
        os.environ['PRISMQ_WORKING_DIR'] = test_dir
        
        try:
            result = get_working_directory_from_env()
            assert result == test_dir
        finally:
            del os.environ['PRISMQ_WORKING_DIR']

    def test_get_from_env_file(self):
        """Test getting working directory from .env file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                
                # Create .env file with WORKING_DIR
                config = ConfigManager(tmpdir)
                config.set('WORKING_DIR', tmpdir)
                
                result = get_working_directory_from_env()
                assert result == tmpdir
            finally:
                os.chdir(original_cwd)

    def test_returns_none_when_not_found(self):
        """Test returns None when working directory not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                
                # Make sure no environment variable is set
                if 'PRISMQ_WORKING_DIR' in os.environ:
                    del os.environ['PRISMQ_WORKING_DIR']
                
                result = get_working_directory_from_env()
                assert result is None
            finally:
                os.chdir(original_cwd)


class TestSetupWorkingDirectory:
    """Test setup_working_directory function."""

    def test_creates_config_in_current_directory(self):
        """Test setup creates configuration in current directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                
                # In non-interactive mode, should use current directory
                config = setup_working_directory("TestPackage")
                
                assert config.working_dir == Path(tmpdir).resolve()
                assert config.env_file.exists()
                assert config.get('APP_NAME') == 'TestPackage'
                assert config.get('WORKING_DIR') == str(Path(tmpdir).resolve())
            finally:
                os.chdir(original_cwd)

    def test_uses_existing_working_directory(self):
        """Test setup uses existing working directory from environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ['PRISMQ_WORKING_DIR'] = tmpdir
            
            try:
                config = setup_working_directory("TestPackage")
                
                assert config.working_dir == Path(tmpdir).resolve()
                assert config.env_file.exists()
            finally:
                del os.environ['PRISMQ_WORKING_DIR']

    def test_preserves_existing_config_values(self):
        """Test setup preserves existing configuration values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create initial config
            config1 = ConfigManager(tmpdir)
            config1.set('APP_NAME', 'ExistingApp')
            config1.set('CUSTOM_KEY', 'custom_value')
            
            os.environ['PRISMQ_WORKING_DIR'] = tmpdir
            
            try:
                # Setup should preserve existing values
                config2 = setup_working_directory("NewPackage")
                
                # APP_NAME should be preserved
                assert config2.get('APP_NAME') == 'ExistingApp'
                # Custom key should be preserved
                assert config2.get('CUSTOM_KEY') == 'custom_value'
            finally:
                del os.environ['PRISMQ_WORKING_DIR']


class TestConfigManagerEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_env_file(self):
        """Test handling empty .env file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.touch()  # Create empty file
            
            config = ConfigManager(tmpdir)
            assert config.config == {}

    def test_env_file_with_only_comments(self):
        """Test handling .env file with only comments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            
            with open(env_file, 'w') as f:
                f.write("# Comment 1\n")
                f.write("# Comment 2\n")
                f.write("# Comment 3\n")
            
            config = ConfigManager(tmpdir)
            assert config.config == {}

    def test_env_file_with_malformed_lines(self):
        """Test handling .env file with malformed lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            
            with open(env_file, 'w') as f:
                f.write("VALID_KEY=valid_value\n")
                f.write("malformed line without equals\n")
                f.write("ANOTHER_KEY=another_value\n")
            
            config = ConfigManager(tmpdir)
            # Should load valid keys, skip malformed ones
            assert config.get('VALID_KEY') == 'valid_value'
            assert config.get('ANOTHER_KEY') == 'another_value'

    def test_working_directory_with_spaces(self):
        """Test handling working directory path with spaces."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "dir with spaces"
            test_dir.mkdir()
            
            config = ConfigManager(str(test_dir))
            config.set('TEST_KEY', 'test_value')
            
            assert config.env_file.exists()
            assert config.get('TEST_KEY') == 'test_value'

    def test_unicode_values(self):
        """Test handling unicode characters in values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ConfigManager(tmpdir)
            
            unicode_value = "Hello 世界 🌍"
            config.set('UNICODE_KEY', unicode_value)
            
            # Reload and verify
            config2 = ConfigManager(tmpdir)
            assert config2.get('UNICODE_KEY') == unicode_value


class TestFindPrismQDirectory:
    """Test find_prismq_directory function."""

    def test_finds_current_directory_with_prismq(self):
        """Test finding PrismQ in current directory name."""
        from config_manager import find_prismq_directory
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a directory with PrismQ in the name
            prismq_dir = Path(tmpdir) / "PrismQ.Test.Package"
            prismq_dir.mkdir()
            
            original_cwd = os.getcwd()
            try:
                os.chdir(str(prismq_dir))
                result = find_prismq_directory()
                assert result == prismq_dir
            finally:
                os.chdir(original_cwd)

    def test_finds_parent_directory_with_prismq(self):
        """Test finding PrismQ in parent directory name."""
        from config_manager import find_prismq_directory
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a directory structure with PrismQ in parent
            prismq_dir = Path(tmpdir) / "PrismQ.Module"
            prismq_dir.mkdir()
            sub_dir = prismq_dir / "subdir" / "nested"
            sub_dir.mkdir(parents=True)
            
            original_cwd = os.getcwd()
            try:
                os.chdir(str(sub_dir))
                result = find_prismq_directory()
                assert result == prismq_dir
            finally:
                os.chdir(original_cwd)

    def test_case_insensitive_search(self):
        """Test that search is case-insensitive."""
        from config_manager import find_prismq_directory
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory with lowercase prismq
            prismq_dir = Path(tmpdir) / "prismq.test"
            prismq_dir.mkdir()
            
            original_cwd = os.getcwd()
            try:
                os.chdir(str(prismq_dir))
                result = find_prismq_directory()
                assert result == prismq_dir
            finally:
                os.chdir(original_cwd)

    def test_returns_none_when_not_found(self):
        """Test returns None when no PrismQ directory found."""
        from config_manager import find_prismq_directory
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "regular" / "directory"
            test_dir.mkdir(parents=True)
            
            original_cwd = os.getcwd()
            try:
                os.chdir(str(test_dir))
                result = find_prismq_directory()
                # Should return None since no PrismQ directory in path
                assert result is None
            finally:
                os.chdir(original_cwd)

    def test_finds_nearest_prismq_directory(self):
        """Test finds the nearest (not the farthest) PrismQ directory."""
        from config_manager import find_prismq_directory
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested PrismQ directories
            outer_prismq = Path(tmpdir) / "PrismQ.Outer"
            outer_prismq.mkdir()
            inner_prismq = outer_prismq / "nested" / "PrismQ.Inner"
            inner_prismq.mkdir(parents=True)
            sub_dir = inner_prismq / "subdirectory"
            sub_dir.mkdir()
            
            original_cwd = os.getcwd()
            try:
                os.chdir(str(sub_dir))
                result = find_prismq_directory()
                # Should find the nearest one (inner)
                assert result == inner_prismq
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
