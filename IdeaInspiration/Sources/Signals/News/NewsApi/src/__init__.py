"""Main module exports for NewsApiSource."""

from .core import Config
from .plugins.news_api_plugin import NewsApiPlugin

__all__ = [
    "Config",
    "NewsApiPlugin",
]

__version__ = "1.0.0"
