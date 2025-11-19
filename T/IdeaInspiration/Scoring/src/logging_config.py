"""DEPRECATED: Use ConfigLoad module instead.

This file is kept for backward compatibility but is deprecated.
New code should import from ConfigLoad module:

    from ConfigLoad import get_module_logger, setup_basic_logging

For migration guide, see: /ConfigLoad/README.md
"""

import warnings
warnings.warn(
    "Scoring/src/logging_config is deprecated. Use ConfigLoad module instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from ConfigLoad for backward compatibility
import sys
from pathlib import Path

# Add ConfigLoad to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ConfigLoad.logging_config import (
    ModuleLogger,
    get_module_logger,
    setup_basic_logging
)

__all__ = ["ModuleLogger", "get_module_logger", "setup_basic_logging"]

