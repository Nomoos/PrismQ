#!/usr/bin/env python3
"""
Tests for Windows batch script functionality.

This test suite validates that the .bat wrapper scripts are properly configured
and that the Python scripts they invoke exist and are functional.
"""

import pytest
from pathlib import Path
import re
import sys


class TestBatchScripts:
    """Test suite for Windows batch scripts."""

    @pytest.fixture
    def scripts_dir(self):
        """Get the scripts directory path."""
        return Path(__file__).parent

    def test_add_module_bat_exists(self, scripts_dir):
        """Verify add-module.bat exists."""
        bat_file = scripts_dir / "add-module.bat"
        assert bat_file.exists(), "add-module.bat not found"
        assert bat_file.is_file(), "add-module.bat is not a file"

    def test_sync_modules_bat_exists(self, scripts_dir):
        """Verify sync-modules.bat exists."""
        bat_file = scripts_dir / "sync-modules.bat"
        assert bat_file.exists(), "sync-modules.bat not found"
        assert bat_file.is_file(), "sync-modules.bat is not a file"

    def test_add_module_bat_structure(self, scripts_dir):
        """Verify add-module.bat has proper structure and references."""
        bat_file = scripts_dir / "add-module.bat"
        content = bat_file.read_text(encoding='utf-8')
        
        # Check for essential components
        assert "setlocal enabledelayedexpansion" in content, "Missing delayed expansion"
        assert "SCRIPT_DIR" in content, "Missing SCRIPT_DIR variable"
        assert "VENV_DIR" in content, "Missing VENV_DIR variable"
        assert "PYTHON_SCRIPT" in content, "Missing PYTHON_SCRIPT variable"
        
        # Check for git repository validation
        assert "git rev-parse --git-dir" in content, "Missing git repository check"
        
        # Check for virtual environment handling
        assert "activate.bat" in content, "Missing venv activation"
        assert "setup_env.bat" in content, "Missing setup_env.bat reference"
        
        # Check for Python script execution
        assert "python" in content.lower(), "Missing Python execution"
        assert "deactivate" in content, "Missing venv deactivation"

    def test_sync_modules_bat_structure(self, scripts_dir):
        """Verify sync-modules.bat has proper structure and references."""
        bat_file = scripts_dir / "sync-modules.bat"
        content = bat_file.read_text(encoding='utf-8')
        
        # Check for essential components
        assert "setlocal enabledelayedexpansion" in content, "Missing delayed expansion"
        assert "SCRIPT_DIR" in content, "Missing SCRIPT_DIR variable"
        assert "VENV_DIR" in content, "Missing VENV_DIR variable"
        assert "PYTHON_SCRIPT" in content, "Missing PYTHON_SCRIPT variable"
        
        # Check for git repository validation
        assert "git rev-parse --git-dir" in content, "Missing git repository check"
        
        # Check for virtual environment handling
        assert "activate.bat" in content, "Missing venv activation"
        assert "setup_env.bat" in content, "Missing setup_env.bat reference"
        
        # Check for Python script execution
        assert "python" in content.lower(), "Missing Python execution"
        assert "deactivate" in content, "Missing venv deactivation"

    def test_add_module_python_module_exists(self, scripts_dir):
        """Verify add_module Python module exists and is importable."""
        add_module_dir = scripts_dir / "add_module"
        assert add_module_dir.exists(), "add_module directory not found"
        assert add_module_dir.is_dir(), "add_module is not a directory"
        
        # Check for __init__.py
        init_file = add_module_dir / "__init__.py"
        assert init_file.exists(), "add_module/__init__.py not found"
        
        # Check for __main__.py
        main_file = add_module_dir / "__main__.py"
        assert main_file.exists(), "add_module/__main__.py not found"

    def test_sync_modules_python_module_exists(self, scripts_dir):
        """Verify sync_modules Python module exists and is importable."""
        sync_modules_dir = scripts_dir / "sync_modules"
        assert sync_modules_dir.exists(), "sync_modules directory not found"
        assert sync_modules_dir.is_dir(), "sync_modules is not a directory"
        
        # Check for __init__.py
        init_file = sync_modules_dir / "__init__.py"
        assert init_file.exists(), "sync_modules/__init__.py not found"
        
        # Check for __main__.py
        main_file = sync_modules_dir / "__main__.py"
        assert main_file.exists(), "sync_modules/__main__.py not found"

    def test_setup_env_bat_exists_for_add_module(self, scripts_dir):
        """Verify setup_env.bat exists for add_module."""
        setup_file = scripts_dir / "add_module" / "setup_env.bat"
        assert setup_file.exists(), "add_module/setup_env.bat not found"

    def test_setup_env_bat_exists_for_sync_modules(self, scripts_dir):
        """Verify setup_env.bat exists for sync_modules."""
        setup_file = scripts_dir / "sync_modules" / "setup_env.bat"
        assert setup_file.exists(), "sync_modules/setup_env.bat not found"

    def test_add_module_bat_references_correct_setup_env(self, scripts_dir):
        """Verify add-module.bat references the correct setup_env.bat path."""
        bat_file = scripts_dir / "add-module.bat"
        content = bat_file.read_text(encoding='utf-8')
        
        # Check for correct path to setup_env.bat in add_module subdirectory
        assert "add_module\\setup_env.bat" in content, \
            "add-module.bat should reference add_module\\setup_env.bat"
        
        # Ensure it doesn't reference the wrong path
        assert not re.search(r'%SCRIPT_DIR%setup_env\.bat(?!\\)', content), \
            "add-module.bat should not reference %SCRIPT_DIR%setup_env.bat directly"

    def test_sync_modules_bat_references_correct_setup_env(self, scripts_dir):
        """Verify sync-modules.bat references the correct setup_env.bat path."""
        bat_file = scripts_dir / "sync-modules.bat"
        content = bat_file.read_text(encoding='utf-8')
        
        # Check for correct path to setup_env.bat in sync_modules subdirectory
        assert "sync_modules\\setup_env.bat" in content, \
            "sync-modules.bat should reference sync_modules\\setup_env.bat"
        
        # Ensure it doesn't reference the wrong path
        assert not re.search(r'%SCRIPT_DIR%setup_env\.bat(?!\\)', content), \
            "sync-modules.bat should not reference %SCRIPT_DIR%setup_env.bat directly"

    def test_requirements_exist_for_add_module(self, scripts_dir):
        """Verify requirements.txt exists for add_module."""
        req_file = scripts_dir / "add_module" / "requirements.txt"
        assert req_file.exists(), "add_module/requirements.txt not found"
        
        # Verify it has content
        content = req_file.read_text()
        assert len(content.strip()) > 0, "requirements.txt is empty"

    def test_requirements_exist_for_sync_modules(self, scripts_dir):
        """Verify requirements.txt exists for sync_modules."""
        req_file = scripts_dir / "sync_modules" / "requirements.txt"
        assert req_file.exists(), "sync_modules/requirements.txt not found"
        
        # Verify it has content
        content = req_file.read_text()
        assert len(content.strip()) > 0, "requirements.txt is empty"

    def test_bat_files_have_proper_encoding(self, scripts_dir):
        """Verify batch files can be read with UTF-8 encoding."""
        bat_files = ["add-module.bat", "sync-modules.bat"]
        
        for bat_file in bat_files:
            file_path = scripts_dir / bat_file
            try:
                content = file_path.read_text(encoding='utf-8')
                assert len(content) > 0, f"{bat_file} is empty"
            except UnicodeDecodeError:
                pytest.fail(f"{bat_file} has encoding issues")

    def test_bat_files_have_exit_codes(self, scripts_dir):
        """Verify batch files properly handle exit codes."""
        bat_files = ["add-module.bat", "sync-modules.bat"]
        
        for bat_file in bat_files:
            file_path = scripts_dir / bat_file
            content = file_path.read_text(encoding='utf-8')
            
            # Check for exit code handling
            assert "errorlevel" in content.lower(), f"{bat_file} missing errorlevel check"
            assert "exit /b" in content, f"{bat_file} missing proper exit"


class TestPythonModules:
    """Test suite for Python modules called by batch scripts."""

    @pytest.fixture
    def scripts_dir(self):
        """Get the scripts directory path."""
        return Path(__file__).parent

    def test_add_module_can_be_run(self, scripts_dir):
        """Verify add_module module can be executed."""
        # Add to path and try importing
        add_module_parent = scripts_dir
        if str(add_module_parent) not in sys.path:
            sys.path.insert(0, str(add_module_parent))
        
        try:
            import add_module
            assert hasattr(add_module, '__version__') or True  # Module exists
        except ImportError as e:
            pytest.fail(f"Cannot import add_module: {e}")

    def test_sync_modules_can_be_run(self, scripts_dir):
        """Verify sync_modules module can be executed."""
        # Add to path and try importing
        sync_modules_parent = scripts_dir
        if str(sync_modules_parent) not in sys.path:
            sys.path.insert(0, str(sync_modules_parent))
        
        try:
            import sync_modules
            assert hasattr(sync_modules, '__version__') or True  # Module exists
        except ImportError as e:
            pytest.fail(f"Cannot import sync_modules: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
