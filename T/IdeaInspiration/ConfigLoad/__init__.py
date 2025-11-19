"""ConfigLoad - Centralized configuration loading for PrismQ modules.

This module provides centralized .env file management and loading functionality
for all PrismQ modules, based on the pattern from YouTubeShortsSource.
"""

from .src.config import Config
from .src.logging_config import ModuleLogger, get_module_logger, setup_basic_logging

__all__ = [
    "Config",
    "ModuleLogger",
    "get_module_logger",
    "setup_basic_logging",
]

__version__ = "0.1.0"
