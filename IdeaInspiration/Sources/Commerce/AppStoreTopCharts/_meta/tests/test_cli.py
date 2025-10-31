"""Tests for App Store Top Charts CLI."""

import pytest
import tempfile
import os
from pathlib import Path
from click.testing import CliRunner

from src import cli


@pytest.fixture
def temp_env():
    """Create temporary .env file."""
    temp_dir = tempfile.mkdtemp()
    env_path = Path(temp_dir) / ".env"
    with open(env_path, 'w') as f:
        f.write(f"DATABASE_URL=sqlite:///{temp_dir}/test.db\n")
        f.write("APP_STORE_CATEGORIES=games\n")
        f.write("APP_STORE_MAX_APPS=5\n")
        f.write("APP_STORE_DELAY_SECONDS=0.1\n")
    
    yield str(env_path)
    
    # Cleanup
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['--help'])
    assert result.exit_code == 0
    assert 'App Store' in result.output or 'app' in result.output.lower()


def test_cli_has_scrape_command(temp_env):
    """Test CLI has scrape command."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['scrape', '--help'])
    assert result.exit_code == 0


def test_cli_has_list_command(temp_env):
    """Test CLI has list command."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['list', '--help'])
    assert result.exit_code == 0


def test_cli_has_stats_command(temp_env):
    """Test CLI has stats command."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['stats', '--help'])
    assert result.exit_code == 0
