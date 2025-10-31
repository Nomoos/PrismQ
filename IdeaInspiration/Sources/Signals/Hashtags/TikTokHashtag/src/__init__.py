"""Main module exports for TikTokHashtagSource."""

from .core import Config, Database, UniversalMetrics, SignalProcessor
from .plugins.tik_tok_hashtag_plugin import TikTokHashtagPlugin

__all__ = [
    "Config",
    "Database",
    "UniversalMetrics",
    "SignalProcessor",
    "TikTokHashtagPlugin",
]

__version__ = "1.0.0"
