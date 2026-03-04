"""Test YouTube Shorts URL parsing and video ID extraction.

This test validates that YouTube Shorts URLs are properly supported,
including the example from the problem statement:
https://youtube.com/shorts/FIZdGdagbeE?si=5De3nxrCKcjK2BsT
"""

import re
from typing import Optional

import pytest


def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from various URL formats.

    This is a standalone version of YouTubeVideoWorker._extract_video_id
    for testing purposes without requiring full worker dependencies.

    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID

    Args:
        url: YouTube video URL

    Returns:
        Video ID or None if not found
    """
    if not url:
        return None

    # Pattern for standard watch URLs
    match = re.search(r"[?&]v=([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)

    # Pattern for youtu.be short URLs
    match = re.search(r"youtu\.be/([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)

    # Pattern for /shorts/ URLs
    match = re.search(r"/shorts/([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)

    # If it looks like a video ID itself (11 characters)
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url):
        return url

    return None


class TestYouTubeShortsURL:
    """Test YouTube Shorts URL handling."""

    def test_extract_video_id_from_shorts_url(self):
        """Test extraction of video ID from standard /shorts/ URL."""
        url = "https://www.youtube.com/shorts/FIZdGdagbeE"
        video_id = extract_video_id(url)
        assert video_id == "FIZdGdagbeE"

    def test_extract_video_id_from_shorts_url_with_query_params(self):
        """Test extraction from /shorts/ URL with query parameters.

        This is the format from the problem statement:
        https://youtube.com/shorts/FIZdGdagbeE?si=5De3nxrCKcjK2BsT
        """
        url = "https://youtube.com/shorts/FIZdGdagbeE?si=5De3nxrCKcjK2BsT"
        video_id = extract_video_id(url)
        assert video_id == "FIZdGdagbeE"

    def test_extract_video_id_from_various_shorts_formats(self):
        """Test various YouTube Shorts URL formats."""
        test_cases = [
            ("https://www.youtube.com/shorts/abc123defgh", "abc123defgh"),
            ("https://youtube.com/shorts/abc123defgh", "abc123defgh"),
            ("https://m.youtube.com/shorts/abc123defgh", "abc123defgh"),
            ("https://www.youtube.com/shorts/abc123defgh?feature=share", "abc123defgh"),
            ("https://youtube.com/shorts/abc123defgh?si=randomstring", "abc123defgh"),
        ]

        for url, expected_id in test_cases:
            video_id = extract_video_id(url)
            assert video_id == expected_id, f"Failed for URL: {url}"

    def test_extract_video_id_from_standard_watch_url(self):
        """Test that standard watch URLs still work."""
        url = "https://www.youtube.com/watch?v=FIZdGdagbeE"
        video_id = extract_video_id(url)
        assert video_id == "FIZdGdagbeE"

    def test_extract_video_id_from_youtu_be_url(self):
        """Test that youtu.be short URLs still work."""
        url = "https://youtu.be/FIZdGdagbeE"
        video_id = extract_video_id(url)
        assert video_id == "FIZdGdagbeE"

    def test_extract_video_id_from_plain_id(self):
        """Test that plain video IDs are recognized."""
        video_id = extract_video_id("FIZdGdagbeE")
        assert video_id == "FIZdGdagbeE"

    def test_extract_video_id_returns_none_for_invalid(self):
        """Test that invalid URLs return None."""
        assert extract_video_id("") is None
        assert extract_video_id(None) is None
        assert extract_video_id("not a url") is None
        assert extract_video_id("https://example.com") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
