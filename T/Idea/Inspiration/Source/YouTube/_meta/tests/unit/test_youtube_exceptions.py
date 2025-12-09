"""Unit tests for YouTube exception classes."""

import sys
from pathlib import Path

import pytest

# Add src directory to path for direct imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from exceptions.youtube_exceptions import (
    YouTubeAPIError,
    YouTubeConfigError,
    YouTubeError,
    YouTubeInvalidVideoError,
    YouTubeQuotaExceededError,
    YouTubeRateLimitError,
)


class TestYouTubeError:
    """Tests for YouTubeError base exception."""

    def test_youtube_error_creation(self):
        """Test creating a YouTube error."""
        error = YouTubeError("Test error")
        assert str(error) == "Test error"

    def test_youtube_error_inheritance(self):
        """Test that YouTubeError inherits from Exception."""
        error = YouTubeError("Test")
        assert isinstance(error, Exception)


class TestYouTubeAPIError:
    """Tests for YouTubeAPIError."""

    def test_api_error_basic(self):
        """Test basic API error creation."""
        error = YouTubeAPIError("API failed")
        assert str(error) == "API failed"
        assert error.status_code is None
        assert error.response is None

    def test_api_error_with_status_code(self):
        """Test API error with status code."""
        error = YouTubeAPIError("Not found", status_code=404)
        assert str(error) == "Not found"
        assert error.status_code == 404

    def test_api_error_with_response(self):
        """Test API error with response data."""
        response_data = {"error": {"message": "Invalid"}}
        error = YouTubeAPIError("Failed", response=response_data)
        assert error.response == response_data

    def test_api_error_inheritance(self):
        """Test that YouTubeAPIError inherits from YouTubeError."""
        error = YouTubeAPIError("Test")
        assert isinstance(error, YouTubeError)


class TestYouTubeQuotaExceededError:
    """Tests for YouTubeQuotaExceededError."""

    def test_quota_error_basic(self):
        """Test basic quota error."""
        error = YouTubeQuotaExceededError("Quota exceeded")
        assert str(error) == "Quota exceeded"
        assert error.current_usage is None
        assert error.daily_limit is None

    def test_quota_error_with_usage(self):
        """Test quota error with usage info."""
        error = YouTubeQuotaExceededError("Quota exceeded", current_usage=10000, daily_limit=10000)
        assert error.current_usage == 10000
        assert error.daily_limit == 10000

    def test_quota_error_inheritance(self):
        """Test that quota error inherits from YouTubeError."""
        error = YouTubeQuotaExceededError("Test")
        assert isinstance(error, YouTubeError)


class TestYouTubeRateLimitError:
    """Tests for YouTubeRateLimitError."""

    def test_rate_limit_error_basic(self):
        """Test basic rate limit error."""
        error = YouTubeRateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert error.retry_after is None

    def test_rate_limit_error_with_retry(self):
        """Test rate limit error with retry time."""
        error = YouTubeRateLimitError("Rate limit", retry_after=60)
        assert error.retry_after == 60

    def test_rate_limit_error_inheritance(self):
        """Test that rate limit error inherits from YouTubeError."""
        error = YouTubeRateLimitError("Test")
        assert isinstance(error, YouTubeError)


class TestYouTubeInvalidVideoError:
    """Tests for YouTubeInvalidVideoError."""

    def test_invalid_video_error_basic(self):
        """Test basic invalid video error."""
        error = YouTubeInvalidVideoError("Video not found")
        assert str(error) == "Video not found"
        assert error.video_id is None

    def test_invalid_video_error_with_id(self):
        """Test invalid video error with video ID."""
        error = YouTubeInvalidVideoError("Not found", video_id="abc123")
        assert error.video_id == "abc123"

    def test_invalid_video_error_inheritance(self):
        """Test that invalid video error inherits from YouTubeError."""
        error = YouTubeInvalidVideoError("Test")
        assert isinstance(error, YouTubeError)


class TestYouTubeConfigError:
    """Tests for YouTubeConfigError."""

    def test_config_error_basic(self):
        """Test basic config error."""
        error = YouTubeConfigError("Invalid config")
        assert str(error) == "Invalid config"
        assert error.config_key is None

    def test_config_error_with_key(self):
        """Test config error with config key."""
        error = YouTubeConfigError("Missing key", config_key="api_key")
        assert error.config_key == "api_key"

    def test_config_error_inheritance(self):
        """Test that config error inherits from YouTubeError."""
        error = YouTubeConfigError("Test")
        assert isinstance(error, YouTubeError)
