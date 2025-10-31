"""Main module exports for KnowYourMemeSource."""

from .core import Config, Database, UniversalMetrics, SignalProcessor
from .plugins.know_your_meme_plugin import KnowYourMemePlugin

__all__ = [
    "Config",
    "Database",
    "UniversalMetrics",
    "SignalProcessor",
    "KnowYourMemePlugin",
]

__version__ = "1.0.0"
