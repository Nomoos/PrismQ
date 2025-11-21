"""YouTube-specific exception classes.

This module defines custom exceptions for YouTube API interactions,
rate limiting, quota management, and other YouTube-specific errors.
"""

from .youtube_exceptions import (
    YouTubeError,
    YouTubeAPIError,
    YouTubeQuotaExceededError,
    YouTubeRateLimitError,
    YouTubeInvalidVideoError,
    YouTubeConfigError,
)

__all__ = [
    'YouTubeError',
    'YouTubeAPIError',
    'YouTubeQuotaExceededError',
    'YouTubeRateLimitError',
    'YouTubeInvalidVideoError',
    'YouTubeConfigError',
]
