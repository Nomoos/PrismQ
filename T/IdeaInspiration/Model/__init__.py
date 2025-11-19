"""Model - Core IdeaInspiration data model for PrismQ.

This module provides the central data model used across all PrismQ modules.
"""

import sys

# Re-export from src to maintain backward compatibility
from .src.idea_inspiration import (
    IdeaInspiration,
    ContentType,
)

from .src.idea_inspiration_db import (
    IdeaInspirationDatabase,
)

# Import submodules to make old import paths work
from . import src

# Register the src submodules as Model submodules for backward compatibility
# This allows: from Model.idea_inspiration import IdeaInspiration
sys.modules['Model.idea_inspiration'] = src.idea_inspiration
sys.modules['Model.idea_inspiration_db'] = src.idea_inspiration_db
sys.modules['Model.config_manager'] = src.config_manager

__all__ = [
    "IdeaInspiration",
    "ContentType",
    "IdeaInspirationDatabase",
]

__version__ = "0.1.0"
