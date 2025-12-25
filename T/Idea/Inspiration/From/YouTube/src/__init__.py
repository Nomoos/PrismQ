"""YouTube Shorts Source - Scraping and processing YouTube Shorts content.

This module provides tools for collecting idea inspirations from YouTube Shorts
with comprehensive metadata extraction and universal metrics collection.
"""

__version__ = "1.0.0"

# YouTube Foundation (Issue #005)
from .base import YouTubeBaseSource
from .client import RateLimiter, YouTubeAPIClient
from .config import YouTubeConfig

# Core modules
from .core.config import Config
from .core.database import Database
from .core.idea_processor import IdeaProcessor
from .core.metrics import UniversalMetrics
from .exceptions import (
    YouTubeAPIError,
    YouTubeConfigError,
    YouTubeError,
    YouTubeInvalidVideoError,
    YouTubeQuotaExceededError,
    YouTubeRateLimitError,
)
from .mappers import YouTubeMapper
from .plugins.youtube_channel_plugin import YouTubeChannelPlugin

# Plugins
from .plugins.youtube_plugin import YouTubePlugin
from .plugins.youtube_trending_plugin import YouTubeTrendingPlugin
from .schemas import YouTubeChannel, YouTubeSearchResult, YouTubeVideo

# YouTube Sources (Issue #006)
from .sources import YouTubeChannelSource

__all__ = [
    "Config",
    "Database",
    "UniversalMetrics",
    "IdeaProcessor",
    "YouTubePlugin",
    "YouTubeChannelPlugin",
    "YouTubeTrendingPlugin",
    # YouTube Foundation
    "YouTubeBaseSource",
    "YouTubeAPIClient",
    "RateLimiter",
    "YouTubeVideo",
    "YouTubeChannel",
    "YouTubeSearchResult",
    "YouTubeMapper",
    "YouTubeConfig",
    "YouTubeError",
    "YouTubeAPIError",
    "YouTubeQuotaExceededError",
    "YouTubeRateLimitError",
    "YouTubeInvalidVideoError",
    "YouTubeConfigError",
    # YouTube Sources
    "YouTubeChannelSource",
]
