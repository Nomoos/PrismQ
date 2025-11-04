"""Main module exports for TikTokSoundsSource."""

from .core import Config
from .plugins.tik_tok_sounds_plugin import TikTokSoundsPlugin

__all__ = [
    "Config",
    "TikTokSoundsPlugin",
]

__version__ = "1.0.0"
