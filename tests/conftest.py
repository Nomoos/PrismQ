"""Root conftest.py for PrismQ test framework.

This file provides shared fixtures and configuration for all tests across the project.
It sets up common paths and imports to ensure tests can find project modules.
"""

import sys
from pathlib import Path

# Add project root to sys.path
_test_dir = Path(__file__).parent
_project_root = _test_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
