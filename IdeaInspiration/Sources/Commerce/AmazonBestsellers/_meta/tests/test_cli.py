"""Tests for Amazon Bestsellers CLI."""

import pytest
import tempfile
import os
from pathlib import Path
from click.testing import CliRunner

# Import using src package
from src import cli


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # Cleanup
    import shutil
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


@pytest.fixture
def temp_env(temp_dir):
    """Create temporary .env file."""
    env_path = Path(temp_dir) / ".env"
    with open(env_path, 'w') as f:
        f.write(f"DATABASE_URL=sqlite:///{temp_dir}/test.db\n")
        f.write("AMAZON_CATEGORIES=Electronics,Books\n")
        f.write("AMAZON_MAX_PRODUCTS=5\n")
        f.write("AMAZON_DELAY_SECONDS=0.1\n")
    return str(env_path)


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['--help'])
    assert result.exit_code == 0
    assert 'PrismQ Amazon Bestsellers Source' in result.output


def test_cli_version():
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['--version'])
    assert result.exit_code == 0
    assert '1.0.0' in result.output


def test_scrape_command(temp_env):
    """Test scrape command."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['scrape', '--env-file', temp_env, '--no-interactive'])
    
    assert result.exit_code == 0
    assert 'Scraping Amazon bestsellers' in result.output
    assert 'Scraping complete!' in result.output


def test_list_command_empty(temp_env):
    """Test list command with empty database."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['list', '--env-file', temp_env, '--no-interactive'])
    
    # Will show no products initially
    assert result.exit_code == 0


def test_list_command_after_scrape(temp_env):
    """Test list command after scraping."""
    runner = CliRunner()
    
    # First scrape
    runner.invoke(cli.main, ['scrape', '--env-file', temp_env, '--no-interactive'])
    
    # Then list
    result = runner.invoke(cli.main, ['list', '--env-file', temp_env, '--no-interactive', '--limit', '5'])
    
    assert result.exit_code == 0
    assert 'Collected Products' in result.output or 'Bestseller' in result.output


def test_stats_command(temp_env):
    """Test stats command."""
    runner = CliRunner()
    
    # First scrape
    runner.invoke(cli.main, ['scrape', '--env-file', temp_env, '--no-interactive'])
    
    # Then get stats
    result = runner.invoke(cli.main, ['stats', '--env-file', temp_env, '--no-interactive'])
    
    assert result.exit_code == 0
    assert 'Statistics' in result.output or 'Total Products' in result.output


def test_clear_command(temp_env, temp_dir):
    """Test clear command."""
    runner = CliRunner()
    
    # First scrape to create database
    runner.invoke(cli.main, ['scrape', '--env-file', temp_env, '--no-interactive'])
    
    # Check database exists
    db_path = Path(temp_dir) / "test.db"
    assert db_path.exists()
    
    # Clear with confirmation
    result = runner.invoke(cli.main, ['clear', '--env-file', temp_env, '--no-interactive'], input='y\n')
    
    assert result.exit_code == 0


def test_list_with_category_filter(temp_env):
    """Test list command with category filter."""
    runner = CliRunner()
    
    # First scrape
    runner.invoke(cli.main, ['scrape', '--env-file', temp_env, '--no-interactive'])
    
    # List with category filter
    result = runner.invoke(cli.main, ['list', '--env-file', temp_env, '--no-interactive', 
                                  '--category', 'Electronics', '--limit', '5'])
    
    assert result.exit_code == 0


def test_scrape_displays_progress(temp_env):
    """Test that scrape command displays progress."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ['scrape', '--env-file', temp_env, '--no-interactive'])
    
    assert result.exit_code == 0
    assert 'Categories:' in result.output
    assert 'Max products per category:' in result.output
    assert 'Total products found:' in result.output


def test_list_with_limit(temp_env):
    """Test list command with custom limit."""
    runner = CliRunner()
    
    # First scrape
    runner.invoke(cli.main, ['scrape', '--env-file', temp_env, '--no-interactive'])
    
    # List with limit
    result = runner.invoke(cli.main, ['list', '--env-file', temp_env, '--no-interactive', '--limit', '3'])
    
    assert result.exit_code == 0
