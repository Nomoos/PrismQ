"""YouTube video downloader for user-provided links.

This module handles downloading video metadata and text content from
user-provided YouTube URLs.
"""

import re
import subprocess
import json
from typing import Optional, Dict, Any
from datetime import datetime


class YouTubeVideoDownloader:
    """Download YouTube video metadata and text content from user-provided URL."""
    
    def __init__(self):
        """Initialize the downloader."""
        self._check_ytdlp()
    
    def _check_ytdlp(self) -> bool:
        """Check if yt-dlp is installed.
        
        Returns:
            True if yt-dlp is available
            
        Raises:
            RuntimeError: If yt-dlp is not installed
        """
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("yt-dlp is not working properly")
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            raise RuntimeError(
                "yt-dlp is not installed. Install with: pip install yt-dlp"
            ) from e
    
    def validate_url(self, url: str) -> bool:
        """Validate if the URL is a valid YouTube URL.
        
        Args:
            url: YouTube video URL
            
        Returns:
            True if valid YouTube URL
        """
        youtube_patterns = [
            r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(https?://)?(www\.)?youtu\.be/[\w-]+',
            r'(https?://)?(www\.)?youtube\.com/shorts/[\w-]+',
        ]
        
        return any(re.match(pattern, url) for pattern in youtube_patterns)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video ID or None if not found
        """
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([\w-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def download_metadata(self, url: str) -> Dict[str, Any]:
        """Download video metadata from YouTube.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary with video metadata
            
        Raises:
            ValueError: If URL is invalid
            RuntimeError: If download fails
        """
        if not self.validate_url(url):
            raise ValueError(f"Invalid YouTube URL: {url}")
        
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError(f"Could not extract video ID from URL: {url}")
        
        try:
            # Use yt-dlp to extract metadata
            cmd = [
                "yt-dlp",
                "--dump-json",
                "--no-download",
                "--write-auto-sub",
                "--sub-lang", "en",
                f"https://www.youtube.com/watch?v={video_id}"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"yt-dlp failed: {result.stderr}")
            
            metadata = json.loads(result.stdout)
            
            # Extract subtitles if available
            subtitles_text = self._extract_subtitles(video_id)
            
            return {
                "video_id": video_id,
                "title": metadata.get("title", ""),
                "description": metadata.get("description", ""),
                "channel": metadata.get("channel", ""),
                "channel_id": metadata.get("channel_id", ""),
                "duration": metadata.get("duration", 0),
                "view_count": metadata.get("view_count", 0),
                "like_count": metadata.get("like_count", 0),
                "upload_date": metadata.get("upload_date", ""),
                "tags": metadata.get("tags", []),
                "categories": metadata.get("categories", []),
                "subtitles": subtitles_text,
                "source_url": url,
                "downloaded_at": datetime.utcnow().isoformat(),
            }
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Timeout while downloading video: {video_id}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse video metadata: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to download video metadata: {e}")
    
    def _extract_subtitles(self, video_id: str) -> Optional[str]:
        """Extract subtitles from video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Subtitle text or None if not available
        """
        try:
            cmd = [
                "yt-dlp",
                "--write-auto-sub",
                "--sub-lang", "en",
                "--skip-download",
                "--print", "%(subtitles)s",
                f"https://www.youtube.com/watch?v={video_id}"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            
            return None
            
        except Exception:
            # Subtitles are optional, don't fail if not available
            return None
    
    def download_video_inspiration(self, url: str) -> Dict[str, Any]:
        """Download video and prepare it as inspiration data.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary ready to be converted to IdeaInspiration
        """
        metadata = self.download_metadata(url)
        
        # Prepare inspiration data
        inspiration_data = {
            "source": "User.YouTube.Video",
            "source_url": metadata["source_url"],
            "title": metadata["title"],
            "content": metadata.get("subtitles") or metadata.get("description", ""),
            "metadata": {
                "video_id": metadata["video_id"],
                "channel": metadata["channel"],
                "channel_id": metadata["channel_id"],
                "duration": metadata["duration"],
                "view_count": metadata["view_count"],
                "like_count": metadata["like_count"],
                "upload_date": metadata["upload_date"],
                "tags": metadata["tags"],
                "categories": metadata["categories"],
                "downloaded_at": metadata["downloaded_at"],
            }
        }
        
        return inspiration_data


def download_video_inspiration(url: str) -> Dict[str, Any]:
    """Convenience function to download video inspiration.
    
    Args:
        url: YouTube video URL
        
    Returns:
        Inspiration data dictionary
    """
    downloader = YouTubeVideoDownloader()
    return downloader.download_video_inspiration(url)
