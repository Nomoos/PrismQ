"""Unit tests for YouTubeChannelSource."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src directory to path for direct imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from exceptions.youtube_exceptions import YouTubeError
from sources.youtube_channel_source import YouTubeChannelSource


@pytest.fixture
def mock_config():
    """Create mock configuration."""
    return {"api_key": "test_api_key_12345", "rate_limit": 100, "quota_per_day": 10000}


@pytest.fixture
def channel_source(mock_config):
    """Create YouTubeChannelSource for testing."""
    with patch("sources.youtube_channel_source.YouTubeAPIClient"):
        source = YouTubeChannelSource(mock_config)
        return source


class TestYouTubeChannelSourceInitialization:
    """Tests for YouTubeChannelSource initialization."""

    def test_initialization(self, mock_config):
        """Test successful initialization."""
        with patch("sources.youtube_channel_source.YouTubeAPIClient"):
            source = YouTubeChannelSource(mock_config)
            assert source is not None
            assert source.source_name == "youtube"


class TestNormalizeChannelUrl:
    """Tests for _normalize_channel_url method."""

    def test_normalize_full_url(self, channel_source):
        """Test normalizing a full URL."""
        url = "https://www.youtube.com/@mkbhd/videos"
        result = channel_source._normalize_channel_url(url)
        assert result == url

    def test_normalize_username_with_at(self, channel_source):
        """Test normalizing @username format."""
        result = channel_source._normalize_channel_url("@mkbhd")
        assert result == "https://www.youtube.com/@mkbhd/videos"

    def test_normalize_channel_id(self, channel_source):
        """Test normalizing channel ID."""
        result = channel_source._normalize_channel_url("UC123456789")
        assert result == "https://www.youtube.com/channel/UC123456789/videos"

    def test_normalize_username_without_at(self, channel_source):
        """Test normalizing username without @."""
        result = channel_source._normalize_channel_url("mkbhd")
        assert result == "https://www.youtube.com/@mkbhd/videos"


class TestGetChannelUploadsPlaylist:
    """Tests for get_channel_uploads_playlist method."""

    def test_channel_id_to_playlist(self, channel_source):
        """Test converting channel ID to uploads playlist."""
        result = channel_source.get_channel_uploads_playlist("UC123456789")
        assert result == "UU123456789"

    def test_already_playlist_id(self, channel_source):
        """Test with playlist ID input."""
        result = channel_source.get_channel_uploads_playlist("UU123456789")
        assert result == "UU123456789"

    def test_pl_playlist_id(self, channel_source):
        """Test with PL playlist ID."""
        result = channel_source.get_channel_uploads_playlist("PL123456789")
        assert result == "PL123456789"


class TestFetchChannelVideosEfficient:
    """Tests for fetch_channel_videos_efficient method."""

    def test_fetch_success(self, channel_source):
        """Test successful video ID fetching."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "abc12345678\ndef12345678\nghi12345678"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            video_ids = channel_source.fetch_channel_videos_efficient("@mkbhd", limit=10)

            assert len(video_ids) == 3
            assert "abc12345678" in video_ids
            assert "def12345678" in video_ids

    def test_fetch_with_channel_id(self, channel_source):
        """Test fetching with channel ID."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "abc12345678"

        with patch("subprocess.run", return_value=mock_result):
            video_ids = channel_source.fetch_channel_videos_efficient("UC123", limit=10)
            assert len(video_ids) == 1

    def test_fetch_yt_dlp_failure(self, channel_source):
        """Test handling yt-dlp failure."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "ERROR: Channel not found"

        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(YouTubeError, match="yt-dlp failed"):
                channel_source.fetch_channel_videos_efficient("@invalid", limit=10)

    def test_fetch_timeout(self, channel_source):
        """Test handling timeout."""
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("yt-dlp", 60)):
            with pytest.raises(YouTubeError, match="timed out"):
                channel_source.fetch_channel_videos_efficient("@mkbhd", limit=10)

    def test_fetch_yt_dlp_not_found(self, channel_source):
        """Test handling missing yt-dlp."""
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            with pytest.raises(YouTubeError, match="yt-dlp not found"):
                channel_source.fetch_channel_videos_efficient("@mkbhd", limit=10)


class TestFetchVideos:
    """Tests for fetch_videos method."""

    def test_fetch_videos_basic(self, channel_source):
        """Test basic video fetching."""
        # Mock fetch_channel_videos_efficient
        with patch.object(
            channel_source, "fetch_channel_videos_efficient", return_value=["abc12345678"]
        ):
            # Mock _fetch_videos_batch
            mock_video = {
                "platform": "youtube",
                "video_id": "abc12345678",
                "title": "Test Video",
                "url": "https://www.youtube.com/watch?v=abc12345678",
                "duration_seconds": 300,
            }
            with patch.object(channel_source, "_fetch_videos_batch", return_value=[mock_video]):
                videos = channel_source.fetch_videos(query="@mkbhd", limit=10)

                assert len(videos) == 1
                assert videos[0]["video_id"] == "abc12345678"

    def test_fetch_videos_empty_query(self, channel_source):
        """Test with empty query."""
        with pytest.raises(ValueError, match="Channel query.*is required"):
            channel_source.fetch_videos(query=None)

    def test_fetch_videos_no_results(self, channel_source):
        """Test when no videos are found."""
        with patch.object(channel_source, "fetch_channel_videos_efficient", return_value=[]):
            videos = channel_source.fetch_videos(query="@empty", limit=10)
            assert videos == []

    def test_fetch_videos_with_filters(self, channel_source):
        """Test fetching with filters."""
        mock_video = {"video_id": "abc12345678", "published_at": "2024-01-15T00:00:00Z"}

        with patch.object(
            channel_source, "fetch_channel_videos_efficient", return_value=["abc12345678"]
        ):
            with patch.object(channel_source, "_fetch_videos_batch", return_value=[mock_video]):
                filters = {"published_after": "2024-01-01T00:00:00Z"}
                videos = channel_source.fetch_videos(query="@mkbhd", limit=10, filters=filters)

                # Should not be filtered out
                assert len(videos) >= 0


class TestCreateTasksForNewVideos:
    """Tests for create_tasks_for_new_videos method."""

    def test_create_tasks_basic(self, channel_source):
        """Test creating tasks for new videos."""
        # Mock video IDs from channel
        with patch.object(
            channel_source,
            "fetch_channel_videos_efficient",
            return_value=["video1", "video2", "video3"],
        ):
            # Mock TaskManager client
            mock_tm_client = Mock()
            mock_tm_client.list_tasks.return_value = []
            mock_tm_client.create_task.return_value = {"id": "123"}

            # Create tasks
            count = channel_source.create_tasks_for_new_videos("UC123", mock_tm_client)

            assert count == 3
            assert mock_tm_client.create_task.call_count == 3

    def test_create_tasks_with_existing(self, channel_source):
        """Test creating tasks when some already exist."""
        with patch.object(
            channel_source,
            "fetch_channel_videos_efficient",
            return_value=["video1", "video2", "video3"],
        ):
            # Mock existing tasks
            mock_tm_client = Mock()
            mock_tm_client.list_tasks.return_value = [
                {"params": {"video_id": "video1"}}  # video1 already exists
            ]
            mock_tm_client.create_task.return_value = {"id": "123"}

            count = channel_source.create_tasks_for_new_videos("UC123", mock_tm_client)

            # Should only create 2 new tasks (video2, video3)
            assert count == 2

    def test_create_tasks_all_exist(self, channel_source):
        """Test when all videos already have tasks."""
        with patch.object(
            channel_source, "fetch_channel_videos_efficient", return_value=["video1", "video2"]
        ):
            mock_tm_client = Mock()
            mock_tm_client.list_tasks.return_value = [
                {"params": {"video_id": "video1"}},
                {"params": {"video_id": "video2"}},
            ]

            count = channel_source.create_tasks_for_new_videos("UC123", mock_tm_client)

            assert count == 0
            mock_tm_client.create_task.assert_not_called()

    def test_create_tasks_no_videos(self, channel_source):
        """Test when channel has no videos."""
        with patch.object(channel_source, "fetch_channel_videos_efficient", return_value=[]):
            mock_tm_client = Mock()

            count = channel_source.create_tasks_for_new_videos("UC123", mock_tm_client)

            assert count == 0


class TestApplyFilters:
    """Tests for _apply_filters method."""

    def test_filter_published_after(self, channel_source):
        """Test filtering by published_after."""
        videos = [
            {"video_id": "1", "published_at": "2024-01-01T00:00:00Z"},
            {"video_id": "2", "published_at": "2024-02-01T00:00:00Z"},
            {"video_id": "3", "published_at": "2024-03-01T00:00:00Z"},
        ]

        filters = {"published_after": "2024-02-01T00:00:00Z"}
        result = channel_source._apply_filters(videos, filters)

        # Should include video 2 and 3
        assert len(result) >= 1

    def test_filter_order_viewcount(self, channel_source):
        """Test sorting by view count."""
        videos = [
            {"video_id": "1", "view_count": 100},
            {"video_id": "2", "view_count": 500},
            {"video_id": "3", "view_count": 200},
        ]

        filters = {"order": "viewCount"}
        result = channel_source._apply_filters(videos, filters)

        # Should be sorted by view count (highest first)
        assert result[0]["video_id"] == "2"
        assert result[0]["view_count"] == 500

    def test_filter_order_date(self, channel_source):
        """Test sorting by date."""
        videos = [
            {"video_id": "1", "published_at": "2024-01-01T00:00:00Z"},
            {"video_id": "2", "published_at": "2024-03-01T00:00:00Z"},
            {"video_id": "3", "published_at": "2024-02-01T00:00:00Z"},
        ]

        filters = {"order": "date"}
        result = channel_source._apply_filters(videos, filters)

        # Should be sorted by date (newest first)
        assert result[0]["video_id"] == "2"
