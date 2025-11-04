"""Main module exports for InstagramHashtagSource."""

from .core import Config
from .plugins.instagram_hashtag_plugin import InstagramHashtagPlugin

__all__ = [
    "Config",
    "InstagramHashtagPlugin",
]

__version__ = "1.0.0"
