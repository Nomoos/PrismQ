"""Main module exports for NewsApiSource."""

from .core import Config, Database, UniversalMetrics, SignalProcessor
from .plugins.news_api_plugin import NewsApiPlugin

__all__ = [
    "Config",
    "Database",
    "UniversalMetrics",
    "SignalProcessor",
    "NewsApiPlugin",
]

__version__ = "1.0.0"
