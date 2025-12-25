"""Tests for YouTube plugin."""

import pytest

from src import YouTubePlugin


class TestYouTubePluginShortDuration:
    """Test YouTube Shorts duration validation (simplified - no strict limits)."""

    def test_is_short_with_various_durations(self):
        """Test that videos with valid ISO 8601 format are accepted."""
        # Short videos
        assert YouTubePlugin._is_short("PT15S") == True
        assert YouTubePlugin._is_short("PT30S") == True
        assert YouTubePlugin._is_short("PT45S") == True

        # 1 minute
        assert YouTubePlugin._is_short("PT1M") == True
        assert YouTubePlugin._is_short("PT60S") == True

        # Longer videos (also accepted - YouTube decides what's a Short)
        assert YouTubePlugin._is_short("PT1M30S") == True
        assert YouTubePlugin._is_short("PT2M") == True
        assert YouTubePlugin._is_short("PT3M") == True

    def test_is_short_with_edge_cases(self):
        """Test edge cases for Shorts duration parsing."""
        # 0 seconds
        assert YouTubePlugin._is_short("PT0S") == True

        # Various valid formats
        assert YouTubePlugin._is_short("PT5M30S") == True
        assert YouTubePlugin._is_short("PT10M") == True

        # Invalid format should return False
        assert YouTubePlugin._is_short("INVALID") == False
        assert YouTubePlugin._is_short("") == False

    def test_is_short_format_validation(self):
        """Test ISO 8601 format validation."""
        # Valid formats are accepted
        assert YouTubePlugin._is_short("PT2M59S") == True
        assert YouTubePlugin._is_short("PT3M0S") == True
        assert YouTubePlugin._is_short("PT3M1S") == True

        # Invalid or missing formats return False
        assert YouTubePlugin._is_short("PT1H") == False  # Hours not in our regex
        assert YouTubePlugin._is_short("1M30S") == False  # Missing PT prefix
        assert YouTubePlugin._is_short("invalid") == False
