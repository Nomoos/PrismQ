"""YouTube data schemas.

This module provides data models for YouTube-specific data structures.
"""

from .youtube_video import YouTubeChannel, YouTubeSearchResult, YouTubeVideo

__all__ = [
    "YouTubeVideo",
    "YouTubeChannel",
    "YouTubeSearchResult",
]
