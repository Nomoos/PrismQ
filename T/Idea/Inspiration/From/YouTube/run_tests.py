#!/usr/bin/env python
"""Simple test runner for YouTube Foundation tests.

This script sets up the Python path correctly to allow testing
the YouTube Foundation components in isolation from the rest
of the YouTube module.
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Now run pytest
import pytest

if __name__ == "__main__":
    # Run pytest with arguments
    exit_code = pytest.main(
        ["_meta/tests/unit/", "-v", "--tb=short", "-W", "ignore::DeprecationWarning"]
    )
    sys.exit(exit_code)
