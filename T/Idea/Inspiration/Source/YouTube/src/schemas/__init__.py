"""YouTube data schemas.

This module provides data models for YouTube-specific data structures.
"""

from .youtube_video import YouTubeVideo, YouTubeChannel, YouTubeSearchResult

__all__ = [
    'YouTubeVideo',
    'YouTubeChannel',
    'YouTubeSearchResult',
]
