"""Main module exports for CommentMiningSource."""

from .core import Config
from .plugins.multiplatform_plugin import MultiPlatformCommentPlugin

__all__ = [
    "Config",
    "MultiPlatformCommentPlugin",
]

__version__ = "1.0.0"
