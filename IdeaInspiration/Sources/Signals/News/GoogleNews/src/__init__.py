"""Main module exports for GoogleNewsSource."""

from .core import Config, Database, UniversalMetrics, SignalProcessor
from .plugins.google_news_plugin import GoogleNewsPlugin

__all__ = [
    "Config",
    "Database",
    "UniversalMetrics",
    "SignalProcessor",
    "GoogleNewsPlugin",
]

__version__ = "1.0.0"
