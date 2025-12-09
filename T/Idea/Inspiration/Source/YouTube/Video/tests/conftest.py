"""Pytest configuration for Video module tests.

Handles setup for test environment including:
- Model module path configuration
- Common fixtures
- Test utilities
"""

import sys
from pathlib import Path

# CRITICAL: Add Model module to path BEFORE any other imports
# This must be done first to allow workers to import IdeaInspiration
model_path = Path(__file__).resolve().parents[4] / "Model" / "src"
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

import pytest


@pytest.fixture
def mock_youtube_api():
    """Fixture to mock YouTube API responses."""
    from unittest.mock import Mock

    mock_api = Mock()
    return mock_api


@pytest.fixture
def temp_database_path(tmp_path):
    """Fixture providing a temporary database path."""
    return str(tmp_path / "test.db")
