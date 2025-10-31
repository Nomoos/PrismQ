"""Main module exports for GoogleTrendsSource."""

from .core import Config, Database, UniversalMetrics, SignalProcessor
from .plugins.google_trends_plugin import GoogleTrendsPlugin

__all__ = [
    "Config",
    "Database",
    "UniversalMetrics",
    "SignalProcessor",
    "GoogleTrendsPlugin",
]

__version__ = "1.0.0"
