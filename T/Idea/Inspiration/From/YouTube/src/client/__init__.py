"""YouTube API client module.

This module provides client classes for interacting with YouTube Data API v3,
including rate limiting and quota management.
"""

from .rate_limiter import RateLimiter
from .youtube_api_client import YouTubeAPIClient

__all__ = [
    "YouTubeAPIClient",
    "RateLimiter",
]
