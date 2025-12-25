"""Tests for YouTubeVideoWorker MVP implementation.

This test suite verifies the YouTubeVideoWorker implementation
following the worker pattern with task queue integration.
"""

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.core.config import Config
from src.core.database import Database
from src.workers import Task, TaskResult, TaskStatus, YouTubeVideoWorker


@pytest.fixture
def temp_queue_db():
    """Create temporary queue database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    # Initialize queue database schema
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE task_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_type TEXT NOT NULL,
            parameters TEXT,
            priority INTEGER DEFAULT 5,
            status TEXT DEFAULT 'queued',
            retry_count INTEGER DEFAULT 0,
            max_retries INTEGER DEFAULT 3,
            created_at TEXT NOT NULL,
            claimed_at TEXT,
            claimed_by TEXT,
            completed_at TEXT,
            updated_at TEXT,
            run_after_utc TEXT,
            result_data TEXT,
            error_message TEXT
        )
    """
    )
    conn.execute(
        """
        CREATE TABLE worker_heartbeats (
            worker_id TEXT PRIMARY KEY,
            last_heartbeat TEXT NOT NULL,
            tasks_processed INTEGER DEFAULT 0,
            tasks_failed INTEGER DEFAULT 0
        )
    """
    )
    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def temp_results_db():
    """Create temporary results database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db = Database(db_path)
    yield db

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def temp_idea_db():
    """Create temporary IdeaInspiration database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    yield db_path

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def mock_config():
    """Create mock configuration."""
    config = Mock(spec=Config)
    config.youtube_api_key = "test_api_key_123"
    config.database_path = ":memory:"
    config.idea_db_path = ":memory:"
    return config


class TestYouTubeVideoWorkerInitialization:
    """Test worker initialization and configuration."""

    def test_worker_initializes_correctly(
        self, temp_queue_db, temp_results_db, temp_idea_db, mock_config
    ):
        """Test that worker initializes with correct configuration."""
        mock_config.idea_db_path = temp_idea_db

        with patch("src.workers.youtube_video_worker.build") as mock_build, patch(
            "src.workers.youtube_video_worker.IdeaInspirationDatabase"
        ):
            worker = YouTubeVideoWorker(
                worker_id="test-worker-1",
                queue_db_path=temp_queue_db,
                config=mock_config,
                results_db=temp_results_db,
                idea_db_path=temp_idea_db,
            )

            assert worker.worker_id == "test-worker-1"
            assert worker.queue_db_path == temp_queue_db
            assert worker.idea_db_path == temp_idea_db
            mock_build.assert_called_once()

    def test_worker_requires_api_key(self, temp_queue_db, temp_results_db, temp_idea_db):
        """Test that worker raises error without API key."""
        config = Mock(spec=Config)
        config.youtube_api_key = None

        with pytest.raises(ValueError, match="YouTube API key not configured"):
            YouTubeVideoWorker(
                worker_id="test-worker",
                queue_db_path=temp_queue_db,
                config=config,
                results_db=temp_results_db,
                idea_db_path=temp_idea_db,
            )


class TestYouTubeVideoWorkerTaskProcessing:
    """Test task processing functionality."""

    def test_process_single_video_task(
        self, temp_queue_db, temp_results_db, temp_idea_db, mock_config
    ):
        """Test processing a single video task."""
        mock_config.idea_db_path = temp_idea_db

        mock_youtube = MagicMock()
        mock_response = {
            "items": [
                {
                    "id": "dQw4w9WgXcQ",
                    "snippet": {
                        "title": "Test Video",
                        "description": "Test description",
                        "channelId": "UC123",
                        "channelTitle": "Test Channel",
                        "publishedAt": "2024-01-01T00:00:00Z",
                        "tags": ["test", "video"],
                    },
                    "statistics": {"viewCount": "1000", "likeCount": "100", "commentCount": "10"},
                    "contentDetails": {"duration": "PT1M30S"},
                }
            ]
        }
        mock_youtube.videos().list().execute.return_value = mock_response

        with patch("src.workers.youtube_video_worker.build", return_value=mock_youtube), patch(
            "src.workers.youtube_video_worker.IdeaInspirationDatabase"
        ) as mock_db_class:

            mock_db = MagicMock()
            mock_db.insert.return_value = 123
            mock_db_class.return_value = mock_db

            worker = YouTubeVideoWorker(
                worker_id="test-worker",
                queue_db_path=temp_queue_db,
                config=mock_config,
                results_db=temp_results_db,
                idea_db_path=temp_idea_db,
            )

            task = Task(
                id=1,
                task_type="youtube_video_single",
                parameters={"video_id": "dQw4w9WgXcQ"},
                priority=5,
                status=TaskStatus.CLAIMED,
                retry_count=0,
                max_retries=3,
                created_at="2024-01-01 00:00:00",
            )

            result = worker.process_task(task)

            assert result.success is True
            assert result.data["video_id"] == "dQw4w9WgXcQ"
            assert result.data["idea_id"] == 123
            assert result.items_processed == 1
            mock_db.insert.assert_called_once()

    def test_process_search_task(self, temp_queue_db, temp_results_db, temp_idea_db, mock_config):
        """Test processing a search task."""
        mock_config.idea_db_path = temp_idea_db

        mock_youtube = MagicMock()

        # Mock search response
        search_response = {
            "items": [
                {"id": {"kind": "youtube#video", "videoId": "video1"}},
                {"id": {"kind": "youtube#video", "videoId": "video2"}},
            ]
        }

        # Mock videos response
        videos_response = {
            "items": [
                {
                    "id": "video1",
                    "snippet": {
                        "title": "Video 1",
                        "description": "Description 1",
                        "channelId": "UC1",
                        "channelTitle": "Channel 1",
                        "publishedAt": "2024-01-01T00:00:00Z",
                    },
                    "statistics": {"viewCount": "1000"},
                    "contentDetails": {"duration": "PT1M"},
                },
                {
                    "id": "video2",
                    "snippet": {
                        "title": "Video 2",
                        "description": "Description 2",
                        "channelId": "UC2",
                        "channelTitle": "Channel 2",
                        "publishedAt": "2024-01-02T00:00:00Z",
                    },
                    "statistics": {"viewCount": "2000"},
                    "contentDetails": {"duration": "PT2M"},
                },
            ]
        }

        mock_youtube.search().list().execute.return_value = search_response
        mock_youtube.videos().list().execute.return_value = videos_response

        with patch("src.workers.youtube_video_worker.build", return_value=mock_youtube), patch(
            "src.workers.youtube_video_worker.IdeaInspirationDatabase"
        ) as mock_db_class:

            mock_db = MagicMock()
            mock_db.insert.side_effect = [1, 2]  # Return different IDs
            mock_db_class.return_value = mock_db

            worker = YouTubeVideoWorker(
                worker_id="test-worker",
                queue_db_path=temp_queue_db,
                config=mock_config,
                results_db=temp_results_db,
                idea_db_path=temp_idea_db,
            )

            task = Task(
                id=1,
                task_type="youtube_video_search",
                parameters={"search_query": "test query", "max_results": 5},
                priority=5,
                status=TaskStatus.CLAIMED,
                retry_count=0,
                max_retries=3,
                created_at="2024-01-01 00:00:00",
            )

            result = worker.process_task(task)

            assert result.success is True
            assert result.items_processed == 2
            assert len(result.data["videos"]) == 2
            assert mock_db.insert.call_count == 2

    def test_unknown_task_type(self, temp_queue_db, temp_results_db, temp_idea_db, mock_config):
        """Test handling of unknown task type."""
        mock_config.idea_db_path = temp_idea_db

        with patch("src.workers.youtube_video_worker.build"), patch(
            "src.workers.youtube_video_worker.IdeaInspirationDatabase"
        ):

            worker = YouTubeVideoWorker(
                worker_id="test-worker",
                queue_db_path=temp_queue_db,
                config=mock_config,
                results_db=temp_results_db,
                idea_db_path=temp_idea_db,
            )

            task = Task(
                id=1,
                task_type="unknown_task_type",
                parameters={},
                priority=5,
                status=TaskStatus.CLAIMED,
                retry_count=0,
                max_retries=3,
                created_at="2024-01-01 00:00:00",
            )

            result = worker.process_task(task)

            assert result.success is False
            assert "Unknown task type" in result.error


class TestVideoIdExtraction:
    """Test video ID extraction from various URL formats."""

    def test_extract_standard_url(self):
        """Test extraction from standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = YouTubeVideoWorker._extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_short_url(self):
        """Test extraction from youtu.be short URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = YouTubeVideoWorker._extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_shorts_url(self):
        """Test extraction from /shorts/ URL."""
        url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        video_id = YouTubeVideoWorker._extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_direct_id(self):
        """Test that direct video ID is accepted."""
        video_id = YouTubeVideoWorker._extract_video_id("dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_invalid_url(self):
        """Test handling of invalid URL."""
        video_id = YouTubeVideoWorker._extract_video_id("not-a-valid-url")
        assert video_id is None

    def test_extract_empty_string(self):
        """Test handling of empty string."""
        video_id = YouTubeVideoWorker._extract_video_id("")
        assert video_id is None


class TestWorkerFactoryIntegration:
    """Test integration with worker factory."""

    def test_worker_registered_in_factory(self):
        """Test that YouTubeVideoWorker is registered in the factory."""
        from src.workers.factory import worker_factory

        supported_types = worker_factory.get_supported_types()
        assert "youtube_video_single" in supported_types
        assert "youtube_video_search" in supported_types

    def test_factory_creates_worker(
        self, temp_queue_db, temp_results_db, temp_idea_db, mock_config
    ):
        """Test that factory can create YouTubeVideoWorker instances."""
        from src.workers.factory import worker_factory

        mock_config.idea_db_path = temp_idea_db

        with patch("src.workers.youtube_video_worker.build"), patch(
            "src.workers.youtube_video_worker.IdeaInspirationDatabase"
        ):

            worker = worker_factory.create(
                task_type="youtube_video_single",
                worker_id="test-worker",
                queue_db_path=temp_queue_db,
                config=mock_config,
                results_db=temp_results_db,
                idea_db_path=temp_idea_db,
            )

            assert isinstance(worker, YouTubeVideoWorker)
            assert worker.worker_id == "test-worker"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
