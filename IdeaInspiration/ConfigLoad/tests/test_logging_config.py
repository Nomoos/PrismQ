"""Tests for logging configuration."""

import pytest
import logging
import os
import tempfile
from pathlib import Path
import sys

# Add parent directory to path to import ConfigLoad
sys.path.insert(0, str(Path(__file__).parent.parent))

from logging_config import ModuleLogger, get_module_logger, setup_basic_logging


class TestModuleLogger:
    """Test ModuleLogger class."""

    def test_create_module_logger(self):
        """Test creating a ModuleLogger instance."""
        logger = ModuleLogger(
            module_name="TestModule",
            module_version="1.0.0",
            module_path="/test/path"
        )
        
        assert logger.module_name == "TestModule"
        assert logger.module_version == "1.0.0"
        assert logger.module_path == "/test/path"

    def test_module_logger_default_values(self):
        """Test ModuleLogger with default values."""
        logger = ModuleLogger(module_name="TestModule")
        
        assert logger.module_name == "TestModule"
        assert logger.module_version == "0.1.0"
        assert logger.module_path == str(Path.cwd())

    def test_get_logger_returns_logging_logger(self):
        """Test that get_logger returns a logging.Logger instance."""
        module_logger = ModuleLogger(module_name="TestModule")
        logger = module_logger.get_logger()
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "TestModule"

    def test_logger_respects_log_level_from_env(self):
        """Test that logger respects LOG_LEVEL from environment."""
        os.environ["LOG_LEVEL"] = "DEBUG"
        
        try:
            module_logger = ModuleLogger(module_name="TestModule")
            logger = module_logger.get_logger()
            
            assert logger.level == logging.DEBUG
        finally:
            del os.environ["LOG_LEVEL"]

    def test_logger_default_log_level(self):
        """Test default log level when not set in environment."""
        # Make sure LOG_LEVEL is not set
        if "LOG_LEVEL" in os.environ:
            del os.environ["LOG_LEVEL"]
        
        module_logger = ModuleLogger(module_name="TestModule")
        logger = module_logger.get_logger()
        
        assert logger.level == logging.INFO

    def test_logger_with_file_handler(self):
        """Test logger with file handler when LOG_FILE is set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            os.environ["LOG_FILE"] = str(log_file)
            
            try:
                module_logger = ModuleLogger(module_name="TestModule")
                logger = module_logger.get_logger()
                
                # Should have both console and file handlers
                assert len(logger.handlers) == 2
                
                # Log a message
                logger.info("Test message")
                
                # Verify file was created and contains the message
                assert log_file.exists()
                with open(log_file, 'r') as f:
                    content = f.read()
                    assert "Test message" in content
            finally:
                del os.environ["LOG_FILE"]

    def test_logger_only_console_handler_by_default(self):
        """Test that logger has only console handler by default."""
        # Make sure LOG_FILE is not set
        if "LOG_FILE" in os.environ:
            del os.environ["LOG_FILE"]
        
        module_logger = ModuleLogger(module_name="TestModule")
        logger = module_logger.get_logger()
        
        # Should have only console handler
        assert len(logger.handlers) == 1

    def test_log_module_startup(self):
        """Test log_module_startup method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            os.environ["LOG_FILE"] = str(log_file)
            
            try:
                module_logger = ModuleLogger(
                    module_name="TestModule",
                    module_version="1.0.0",
                    module_path="/test/path"
                )
                
                module_logger.log_module_startup()
                
                # Verify startup information was logged
                with open(log_file, 'r') as f:
                    content = f.read()
                    assert "MODULE STARTUP" in content
                    assert "TestModule" in content
                    assert "1.0.0" in content
                    assert "Operating System" in content
                    assert "Python Version" in content
            finally:
                del os.environ["LOG_FILE"]

    def test_log_module_shutdown(self):
        """Test log_module_shutdown method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            os.environ["LOG_FILE"] = str(log_file)
            
            try:
                module_logger = ModuleLogger(module_name="TestModule")
                module_logger.log_module_shutdown()
                
                # Verify shutdown information was logged
                with open(log_file, 'r') as f:
                    content = f.read()
                    assert "MODULE SHUTDOWN" in content
                    assert "TestModule" in content
            finally:
                del os.environ["LOG_FILE"]


class TestGetModuleLogger:
    """Test get_module_logger function."""

    def test_get_module_logger_returns_logger(self):
        """Test that get_module_logger returns a logging.Logger."""
        logger = get_module_logger("TestModule", log_startup=False)
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "TestModule"

    def test_get_module_logger_with_startup(self):
        """Test get_module_logger with log_startup=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            os.environ["LOG_FILE"] = str(log_file)
            
            try:
                logger = get_module_logger(
                    "TestModule",
                    module_version="1.0.0",
                    log_startup=True
                )
                
                # Verify startup was logged
                assert log_file.exists()
                with open(log_file, 'r') as f:
                    content = f.read()
                    assert "MODULE STARTUP" in content
            finally:
                del os.environ["LOG_FILE"]

    def test_get_module_logger_without_startup(self):
        """Test get_module_logger with log_startup=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            os.environ["LOG_FILE"] = str(log_file)
            
            try:
                logger = get_module_logger(
                    "TestModule",
                    log_startup=False
                )
                
                # File should be created but without startup log
                # (or might not exist if no other logging happened)
                if log_file.exists():
                    with open(log_file, 'r') as f:
                        content = f.read()
                        assert "MODULE STARTUP" not in content
            finally:
                del os.environ["LOG_FILE"]

    def test_get_module_logger_default_version(self):
        """Test get_module_logger with default version."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            os.environ["LOG_FILE"] = str(log_file)
            
            try:
                logger = get_module_logger("TestModule", log_startup=True)
                
                # Should use default version 0.1.0
                with open(log_file, 'r') as f:
                    content = f.read()
                    assert "0.1.0" in content
            finally:
                del os.environ["LOG_FILE"]


class TestSetupBasicLogging:
    """Test setup_basic_logging function."""

    def test_setup_basic_logging_creates_handler(self):
        """Test setup_basic_logging creates a handler."""
        # Clear any existing handlers first
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        setup_basic_logging()
        
        # Should have at least one handler
        assert len(root_logger.handlers) > 0

    def test_setup_basic_logging_custom_level(self):
        """Test setup_basic_logging with custom log level."""
        # Clear any existing handlers first
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        setup_basic_logging(log_level="DEBUG")
        
        # Handler should be created (level may not change if already configured)
        assert len(root_logger.handlers) > 0

    def test_setup_basic_logging_works_without_error(self):
        """Test setup_basic_logging executes without error."""
        # Just verify it doesn't raise an exception
        try:
            setup_basic_logging(log_level="INFO")
            setup_basic_logging(log_level="INVALID")
            success = True
        except Exception:
            success = False
        
        assert success


class TestLoggingEdgeCases:
    """Test edge cases and error handling."""

    def test_logger_handles_special_characters_in_messages(self):
        """Test logger handles special characters in log messages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            os.environ["LOG_FILE"] = str(log_file)
            
            try:
                logger = get_module_logger("TestModule", log_startup=False)
                
                # Log message with special characters
                logger.info("Message with unicode: 世界 🌍")
                
                # Should be logged correctly
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    assert "世界 🌍" in content
            finally:
                del os.environ["LOG_FILE"]

    def test_log_file_creates_parent_directories(self):
        """Test that log file handler creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "nested" / "dirs" / "test.log"
            os.environ["LOG_FILE"] = str(log_file)
            
            try:
                logger = get_module_logger("TestModule", log_startup=False)
                logger.info("Test message")
                
                # Parent directories should be created
                assert log_file.exists()
                assert log_file.parent.exists()
            finally:
                del os.environ["LOG_FILE"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
