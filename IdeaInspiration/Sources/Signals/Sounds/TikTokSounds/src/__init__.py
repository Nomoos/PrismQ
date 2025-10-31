"""Main module exports for TikTokSoundsSource."""

from .core import Config, Database, UniversalMetrics, SignalProcessor
from .plugins.tik_tok_sounds_plugin import TikTokSoundsPlugin

__all__ = [
    "Config",
    "Database",
    "UniversalMetrics",
    "SignalProcessor",
    "TikTokSoundsPlugin",
]

__version__ = "1.0.0"
