"""Main module exports for MemeTrackerSource."""

from .core import Config, Database, UniversalMetrics, SignalProcessor
from .plugins.meme_tracker_plugin import MemeTrackerPlugin

__all__ = [
    "Config",
    "Database",
    "UniversalMetrics",
    "SignalProcessor",
    "MemeTrackerPlugin",
]

__version__ = "1.0.0"
