"""Tests for Etsy Trending CLI."""

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
        f.write("ETSY_CATEGORIES=jewelry,home-living\n")
        f.write("ETSY_MAX_LISTINGS=5\n")
        f.write("ETSY_DELAY_SECONDS=0.1\n")
    
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
    assert 'Etsy' in result.output


def test_scrape_command(temp_env):
    """Test scrape command."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['scrape', '--env-file', temp_env, '--no-interactive'])
    
    assert result.exit_code == 0
    assert 'Scraping' in result.output


def test_list_command(temp_env):
    """Test list command."""
    runner = CliRunner()
    
    # First scrape
    runner.invoke(cli.main, ['scrape', '--env-file', temp_env, '--no-interactive'])
    
    # Then list
    result = runner.invoke(cli.main, ['list', '--env-file', temp_env, '--no-interactive'])
    
    assert result.exit_code == 0


def test_stats_command(temp_env):
    """Test stats command."""
    runner = CliRunner()
    
    # First scrape
    runner.invoke(cli.main, ['scrape', '--env-file', temp_env, '--no-interactive'])
    
    # Then get stats
    result = runner.invoke(cli.main, ['stats', '--env-file', temp_env, '--no-interactive'])
    
    assert result.exit_code == 0
