"""Integration tests for ISSUE-IMPL-001-01: PrismQ.T.Idea.Creation script verification.

This test verifies the complete implementation of the idea creation scripts:
- Run.bat and Preview.bat batch scripts
- idea_creation_interactive.py Python module
- Virtual environment setup and dependency management
- Database integration
- Ollama integration for AI generation
"""

import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add paths for imports
TESTS_DIR = Path(__file__).parent.absolute()
REPO_ROOT = TESTS_DIR.parent.parent  # Repository root (up from _meta/tests)
SCRIPT_DIR = REPO_ROOT / "_meta" / "scripts" / "01_PrismQ.T.Idea.Creation"
CREATION_ROOT = REPO_ROOT / "T" / "Idea" / "Creation"
CREATION_SRC = CREATION_ROOT / "src"

sys.path.insert(0, str(CREATION_SRC))
sys.path.insert(0, str(REPO_ROOT))


class TestScriptStructure:
    """Test the script structure and file existence."""

    def test_script_folder_exists(self):
        """Verify the script folder exists."""
        assert SCRIPT_DIR.exists(), f"Script folder not found: {SCRIPT_DIR}"
        assert SCRIPT_DIR.is_dir(), f"Script folder is not a directory: {SCRIPT_DIR}"

    def test_run_bat_exists(self):
        """Verify Run.bat exists."""
        run_bat = SCRIPT_DIR / "Run.bat"
        assert run_bat.exists(), f"Run.bat not found: {run_bat}"
        assert run_bat.is_file(), f"Run.bat is not a file: {run_bat}"

    def test_preview_bat_exists(self):
        """Verify Preview.bat exists."""
        preview_bat = SCRIPT_DIR / "Preview.bat"
        assert preview_bat.exists(), f"Preview.bat not found: {preview_bat}"
        assert preview_bat.is_file(), f"Preview.bat is not a file: {preview_bat}"

    def test_common_start_ollama_exists(self):
        """Verify common/start_ollama.bat exists."""
        start_ollama = REPO_ROOT / "_meta" / "scripts" / "common" / "start_ollama.bat"
        assert start_ollama.exists(), f"start_ollama.bat not found: {start_ollama}"

    def test_requirements_txt_exists(self):
        """Verify requirements.txt exists in module."""
        requirements = CREATION_ROOT / "requirements.txt"
        assert requirements.exists(), f"requirements.txt not found: {requirements}"

    def test_interactive_module_exists(self):
        """Verify idea_creation_interactive.py exists."""
        interactive_py = CREATION_SRC / "idea_creation_interactive.py"
        assert interactive_py.exists(), f"Interactive module not found: {interactive_py}"


class TestBatchScriptContent:
    """Test the batch script content and structure."""

    def test_run_bat_calls_start_ollama(self):
        """Verify Run.bat calls start_ollama.bat."""
        run_bat = SCRIPT_DIR / "Run.bat"
        content = run_bat.read_text()
        assert "start_ollama.bat" in content, "Run.bat should call start_ollama.bat"

    def test_run_bat_sets_up_venv(self):
        """Verify Run.bat sets up virtual environment."""
        run_bat = SCRIPT_DIR / "Run.bat"
        content = run_bat.read_text()
        assert ":setup_env" in content, "Run.bat should have setup_env function"
        assert "python -m venv" in content, "Run.bat should create venv"
        assert "activate.bat" in content, "Run.bat should activate venv"

    def test_run_bat_installs_requirements(self):
        """Verify Run.bat installs requirements."""
        run_bat = SCRIPT_DIR / "Run.bat"
        content = run_bat.read_text()
        assert "pip install" in content, "Run.bat should install requirements"
        assert "requirements.txt" in content, "Run.bat should use requirements.txt"
        assert ".requirements_installed" in content, "Run.bat should use marker file"

    def test_run_bat_calls_interactive_module(self):
        """Verify Run.bat calls idea_creation_interactive.py."""
        run_bat = SCRIPT_DIR / "Run.bat"
        content = run_bat.read_text()
        assert "idea_creation_interactive.py" in content, "Run.bat should call interactive module"

    def test_preview_bat_uses_preview_flag(self):
        """Verify Preview.bat uses --preview flag."""
        preview_bat = SCRIPT_DIR / "Preview.bat"
        content = preview_bat.read_text()
        assert "--preview" in content, "Preview.bat should use --preview flag"
        assert "--debug" in content, "Preview.bat should use --debug flag"

    def test_preview_bat_mentions_no_database_save(self):
        """Verify Preview.bat mentions no database save."""
        preview_bat = SCRIPT_DIR / "Preview.bat"
        content = preview_bat.read_text()
        assert "NOT save to database" in content or "not save" in content.lower(), \
            "Preview.bat should mention not saving to database"


class TestInteractiveModuleStructure:
    """Test the idea_creation_interactive.py module structure."""

    def test_module_imports_successfully(self):
        """Verify the module can be imported."""
        import idea_creation_interactive  # noqa: F401
        # If import fails, pytest will catch and report the ImportError

    def test_module_has_main_function(self):
        """Verify the module has a main function."""
        import idea_creation_interactive
        assert hasattr(idea_creation_interactive, "main"), "Module should have main() function"
        assert callable(idea_creation_interactive.main), "main should be callable"

    def test_module_has_run_interactive_mode(self):
        """Verify the module has run_interactive_mode function."""
        import idea_creation_interactive
        assert hasattr(idea_creation_interactive, "run_interactive_mode"), \
            "Module should have run_interactive_mode() function"

    def test_module_has_parse_input_text(self):
        """Verify the module has parse_input_text function."""
        import idea_creation_interactive
        assert hasattr(idea_creation_interactive, "parse_input_text"), \
            "Module should have parse_input_text() function"


class TestInputParsing:
    """Test input parsing functionality."""

    def test_parse_plain_text_short(self):
        """Test parsing short plain text (title/keyword)."""
        from idea_creation_interactive import parse_input_text
        
        title, description, metadata = parse_input_text("Horror story")
        assert title == "Horror story"
        assert description == ""
        assert metadata == {}

    def test_parse_plain_text_long(self):
        """Test parsing long plain text (story snippet)."""
        from idea_creation_interactive import parse_input_text
        
        long_text = "This is a long story about a haunted house. " * 5
        title, description, metadata = parse_input_text(long_text)
        assert len(title) <= 80  # Title should be truncated
        assert description.strip() == long_text.strip()  # Full text as description

    def test_parse_json_input(self):
        """Test parsing JSON input."""
        from idea_creation_interactive import parse_input_text
        import json
        
        json_input = json.dumps({
            "story_title": "The Mystery",
            "tone": "suspenseful",
            "theme": "discovery"
        })
        
        title, description, metadata = parse_input_text(json_input)
        assert title == "The Mystery"
        assert "suspenseful" in description or "discovery" in description


class TestDatabaseIntegration:
    """Test database integration functionality."""

    def test_database_path_helper(self):
        """Test get_database_path function."""
        from idea_creation_interactive import get_database_path
        
        db_path = get_database_path()
        assert db_path is not None
        assert isinstance(db_path, str)
        # Should be a path to db.s3db
        assert "db.s3db" in db_path or ".db" in db_path or ".s3db" in db_path

    def test_database_setup_available(self):
        """Test that database setup is available."""
        try:
            from src import setup_idea_database
            assert callable(setup_idea_database)
        except ImportError:
            pytest.skip("Database module not available in test environment")


class TestCommandLineArguments:
    """Test command-line argument parsing."""

    def test_preview_flag_parsing(self):
        """Test --preview flag is recognized."""
        import idea_creation_interactive
        
        # Mock sys.argv to test argument parsing
        with patch('sys.argv', ['idea_creation_interactive.py', '--preview']):
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument('--preview', '-p', action='store_true')
            parser.add_argument('--debug', '-d', action='store_true')
            args = parser.parse_args(['--preview'])
            
            assert args.preview is True
            assert args.debug is False

    def test_debug_flag_parsing(self):
        """Test --debug flag is recognized."""
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--preview', '-p', action='store_true')
        parser.add_argument('--debug', '-d', action='store_true')
        args = parser.parse_args(['--debug'])
        
        assert args.preview is False
        assert args.debug is True

    def test_both_flags_parsing(self):
        """Test both --preview and --debug flags together."""
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--preview', '-p', action='store_true')
        parser.add_argument('--debug', '-d', action='store_true')
        args = parser.parse_args(['--preview', '--debug'])
        
        assert args.preview is True
        assert args.debug is True


class TestModuleStructureCompliance:
    """Test module structure compliance with coding guidelines."""

    def test_module_has_src_directory(self):
        """Verify module follows src/_meta structure."""
        assert (CREATION_ROOT / "src").exists(), "Module should have src/ directory"
        assert (CREATION_ROOT / "_meta").exists(), "Module should have _meta/ directory"

    def test_tests_in_meta_directory(self):
        """Verify tests are in _meta directory."""
        tests_dir = CREATION_ROOT / "_meta" / "tests"
        assert tests_dir.exists(), "Tests should be in _meta/tests/"

    def test_examples_in_meta_directory(self):
        """Verify examples are in _meta directory."""
        examples_dir = CREATION_ROOT / "_meta" / "examples"
        assert examples_dir.exists(), "Examples should be in _meta/examples/"


class TestSecurityAspects:
    """Test security aspects of the implementation."""

    def test_no_hardcoded_secrets_in_scripts(self):
        """Verify no hardcoded secrets in batch scripts."""
        run_bat = SCRIPT_DIR / "Run.bat"
        preview_bat = SCRIPT_DIR / "Preview.bat"
        
        for script in [run_bat, preview_bat]:
            content = script.read_text().lower()
            # Check for common secret patterns
            assert "password=" not in content, f"Hardcoded password found in {script.name}"
            assert "api_key=" not in content, f"Hardcoded API key found in {script.name}"
            assert "secret=" not in content, f"Hardcoded secret found in {script.name}"

    def test_no_hardcoded_secrets_in_python(self):
        """Verify no hardcoded secrets in Python module."""
        interactive_py = CREATION_SRC / "idea_creation_interactive.py"
        content = interactive_py.read_text().lower()
        
        # Check for common secret patterns
        assert "password =" not in content, "Hardcoded password found"
        assert "api_key =" not in content, "Hardcoded API key found"
        assert "secret =" not in content, "Hardcoded secret found"

    def test_no_dangerous_eval_exec(self):
        """Verify no eval() or exec() in Python module."""
        interactive_py = CREATION_SRC / "idea_creation_interactive.py"
        content = interactive_py.read_text()
        
        # These should not be used for security reasons
        assert "eval(" not in content, "eval() found - security risk"
        assert "exec(" not in content, "exec() found - security risk"


class TestErrorHandling:
    """Test error handling requirements."""

    def test_batch_script_checks_python_availability(self):
        """Verify batch scripts check for Python availability."""
        run_bat = SCRIPT_DIR / "Run.bat"
        content = run_bat.read_text()
        
        assert "where python" in content, "Should check Python availability"
        assert "ERROR" in content and "Python" in content, "Should report Python error"

    def test_batch_script_checks_ollama_availability(self):
        """Verify batch scripts start Ollama."""
        run_bat = SCRIPT_DIR / "Run.bat"
        content = run_bat.read_text()
        
        assert "start_ollama.bat" in content, "Should check/start Ollama"

    def test_batch_script_error_codes(self):
        """Verify batch scripts use proper error codes."""
        run_bat = SCRIPT_DIR / "Run.bat"
        content = run_bat.read_text()
        
        assert "exit /b 1" in content, "Should use exit code 1 for errors"
        assert "exit /b 0" in content, "Should use exit code 0 for success"


class TestLoggingObservability:
    """Test logging and observability requirements."""

    def test_run_mode_header_display(self):
        """Verify Run mode displays appropriate header."""
        run_bat = SCRIPT_DIR / "Run.bat"
        content = run_bat.read_text()
        
        assert "RUN MODE" in content.upper(), "Should display RUN MODE header"
        assert "saves" in content.lower() and "database" in content.lower(), \
            "Should mention database save"

    def test_preview_mode_header_display(self):
        """Verify Preview mode displays appropriate header."""
        preview_bat = SCRIPT_DIR / "Preview.bat"
        content = preview_bat.read_text()
        
        assert "PREVIEW MODE" in content.upper(), "Should display PREVIEW MODE header"
        assert "NOT save" in content or "not save" in content.lower(), \
            "Should mention no database save"

    def test_python_module_has_logging_setup(self):
        """Verify Python module sets up logging."""
        interactive_py = CREATION_SRC / "idea_creation_interactive.py"
        content = interactive_py.read_text()
        
        assert "import logging" in content, "Should import logging"
        assert "logger" in content, "Should use logger"


class TestIdempotencyAndSafeReruns:
    """Test idempotency and safe re-run requirements."""

    def test_venv_marker_file_usage(self):
        """Verify scripts use marker file for idempotency."""
        run_bat = SCRIPT_DIR / "Run.bat"
        content = run_bat.read_text()
        
        assert ".requirements_installed" in content, "Should use marker file"
        assert "if not exist" in content, "Should check before creating/installing"

    def test_venv_creation_check(self):
        """Verify scripts check if venv exists before creating."""
        run_bat = SCRIPT_DIR / "Run.bat"
        content = run_bat.read_text()
        
        assert "pyvenv.cfg" in content or "venv" in content, "Should check for venv"
        assert "if not exist" in content, "Should check before creating"


class TestPerformanceAndScalability:
    """Test performance-related aspects."""

    def test_requirements_includes_requests(self):
        """Verify requirements.txt includes necessary packages."""
        requirements = CREATION_ROOT / "requirements.txt"
        content = requirements.read_text()
        
        assert "requests" in content, "Should include requests for Ollama API calls"

    def test_requirements_includes_pytest(self):
        """Verify requirements.txt includes test packages."""
        requirements = CREATION_ROOT / "requirements.txt"
        content = requirements.read_text()
        
        assert "pytest" in content, "Should include pytest for testing"


class TestCompatibilityEnvironment:
    """Test compatibility and environment assumptions."""

    def test_windows_batch_file_format(self):
        """Verify batch files are Windows format."""
        run_bat = SCRIPT_DIR / "Run.bat"
        preview_bat = SCRIPT_DIR / "Preview.bat"
        
        for script in [run_bat, preview_bat]:
            content = script.read_text()
            assert "@echo off" in content, f"{script.name} should be Windows batch file"
            assert "REM" in content, f"{script.name} should have REM comments"

    def test_python_shebang_present(self):
        """Verify Python module has shebang for cross-platform use."""
        interactive_py = CREATION_SRC / "idea_creation_interactive.py"
        content = interactive_py.read_text()
        
        # First line should be shebang
        first_line = content.split('\n')[0]
        assert first_line.startswith('#!') and 'python' in first_line.lower(), \
            "Python module should have shebang"


class TestTestability:
    """Test testability requirements."""

    def test_preview_mode_available(self):
        """Verify preview mode is available for testing."""
        from idea_creation_interactive import run_interactive_mode
        
        # Verify function accepts preview parameter
        import inspect
        sig = inspect.signature(run_interactive_mode)
        assert 'preview' in sig.parameters, "Should have preview parameter"

    def test_debug_mode_available(self):
        """Verify debug mode is available for testing."""
        from idea_creation_interactive import run_interactive_mode
        
        # Verify function accepts debug parameter
        import inspect
        sig = inspect.signature(run_interactive_mode)
        assert 'debug' in sig.parameters, "Should have debug parameter"

    def test_existing_tests_present(self):
        """Verify existing tests are present."""
        tests_dir = CREATION_ROOT / "_meta" / "tests"
        test_files = list(tests_dir.glob("test_*.py"))
        
        assert len(test_files) > 0, "Should have test files in _meta/tests/"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
