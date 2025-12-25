"""User-provided YouTube video inspiration downloader.

This module allows users to provide YouTube video URLs interactively
and downloads the video metadata and text content for inspiration gathering.
"""

from .downloader import download_video_inspiration, YouTubeVideoDownloader

__all__ = [
    'download_video_inspiration',
    'YouTubeVideoDownloader',
]
