"""Main module exports for InstagramAudioTrendsSource."""

from .core import Config, Database, UniversalMetrics, SignalProcessor
from .plugins.instagram_audio_trends_plugin import InstagramAudioTrendsPlugin

__all__ = [
    "Config",
    "Database",
    "UniversalMetrics",
    "SignalProcessor",
    "InstagramAudioTrendsPlugin",
]

__version__ = "1.0.0"
