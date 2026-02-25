"""Tests for T/Idea/Creation module."""

import pytest
from pathlib import Path

CREATION_ROOT = Path(__file__).parent.parent.parent


def test_creation_module_has_src():
    """Verify the Creation module has a src/ directory."""
    assert (CREATION_ROOT / "src").is_dir()


def test_interactive_module_exists():
    """Verify idea_creation_interactive.py exists in src/."""
    assert (CREATION_ROOT / "src" / "idea_creation_interactive.py").is_file()
