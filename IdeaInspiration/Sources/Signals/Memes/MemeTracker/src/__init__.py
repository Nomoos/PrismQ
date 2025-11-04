"""Main module exports for MemeTrackerSource."""

from .core import Config
from .plugins.meme_tracker_plugin import MemeTrackerPlugin

__all__ = [
    "Config",
    "MemeTrackerPlugin",
]

__version__ = "1.0.0"
