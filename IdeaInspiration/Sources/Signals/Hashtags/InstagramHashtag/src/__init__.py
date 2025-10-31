"""Main module exports for InstagramHashtagSource."""

from .core import Config, Database, UniversalMetrics, SignalProcessor
from .plugins.instagram_hashtag_plugin import InstagramHashtagPlugin

__all__ = [
    "Config",
    "Database",
    "UniversalMetrics",
    "SignalProcessor",
    "InstagramHashtagPlugin",
]

__version__ = "1.0.0"
