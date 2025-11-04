"""Main module exports for TikTokHashtagSource."""

from .core import Config
from .plugins.tik_tok_hashtag_plugin import TikTokHashtagPlugin

__all__ = [
    "Config",
    "TikTokHashtagPlugin",
]

__version__ = "1.0.0"
