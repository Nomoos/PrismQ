"""Base YouTube worker with YouTube-specific enhancements.

This module provides progressive enrichment over BaseVideoSourceWorker by adding
YouTube-specific functionality like API client management, quota tracking, and
YouTube-specific error handling.

Design Pattern: Template Method Pattern (Progressive Enrichment)
Reference: https://refactoring.guru/design-patterns/template-method

Hierarchy Level 4:
    BaseWorker (general task processing)
      ↓
    BaseSourceWorker (configuration and storage)
      ↓
    BaseVideoSourceWorker (video-specific operations)
      ↓
    BaseYouTubeWorker (this class - YouTube-specific operations)
      ↓
    YouTubeVideoWorker, YouTubeChannelWorker, YouTubeSearchWorker

Progressive Enrichment:
- BaseWorker provides: Task claiming, processing loop, result reporting
- BaseSourceWorker adds: Configuration management, database operations
- BaseVideoSourceWorker adds: Video validation, duration parsing, video metadata
- BaseYouTubeWorker adds: YouTube API client, quota management, YouTube errors
- Endpoint workers add: Specific scraping logic (video, channel, search)

Follows SOLID principles:
- Single Responsibility: Manages YouTube-specific operations
- Open/Closed: Open for extension via inheritance
- Liskov Substitution: Can substitute BaseVideoSourceWorker
- Dependency Inversion: Depends on YouTube API abstraction
"""

import logging

# Import parent class
import sys
from abc import ABC
from pathlib import Path
from typing import Any, Dict, Optional

# Add paths for imports
source_path = Path(__file__).resolve().parents[4]
if str(source_path) not in sys.path:
    sys.path.insert(0, str(source_path))

# Import from 001_YouTube shared utilities (using relative path within platform)
# Note: Cannot use absolute import like "from Source.001_YouTube..." because
# Python doesn't allow module names starting with digits
try:
    # Try relative import from platform's src directory
    from ...src.core.base_video_source_worker import BaseVideoSourceWorker
except ImportError:
    # Fallback for old Video path during transition
    try:
        from Video.src.core.base_video_source_worker import BaseVideoSourceWorker
    except ImportError:
        from Source.Video.src.core.base_video_source_worker import BaseVideoSourceWorker

from src.core.base_worker import Task, TaskResult

# Import YouTube-specific modules
try:
    from ..core.youtube_api_client import YouTubeAPIClient
    from ..core.youtube_quota_manager import QuotaExceededException, QuotaManager
except ImportError:
    # Fallback for when imports are different
    YouTubeAPIClient = None
    QuotaExceededException = None
    QuotaManager = None

from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class BaseYouTubeWorker(BaseVideoSourceWorker, ABC):
    """Base worker for YouTube operations with API and quota management.

    This class extends BaseVideoSourceWorker with YouTube-specific functionality:
    - YouTube API client initialization
    - YouTube authentication
    - Quota management and tracking
    - YouTube-specific error handling
    - YouTube data format conversion

    This follows progressive enrichment where each level adds
    more specific functionality without modifying the parent.

    Attributes:
        youtube_client: YouTube API client instance
        quota_manager: Quota tracking and management
        api_key: YouTube Data API key

    Example:
        >>> class MyYouTubeWorker(BaseYouTubeWorker):
        ...     def process_task(self, task: Task) -> TaskResult:
        ...         if not self.check_quota_available():
        ...             return TaskResult(success=False, error='Quota exceeded')
        ...
        ...         try:
        ...             video_data = self.fetch_youtube_video(video_id)
        ...             return self.process_video_data(video_data)
        ...         except HttpError as e:
        ...             return self.handle_youtube_error(e)
    """

    def __init__(
        self,
        worker_id: str,
        task_type_ids: list,
        config,
        results_db,
        quota_storage_path: Optional[str] = None,
        daily_quota_limit: int = 10000,
        **kwargs,
    ):
        """Initialize YouTube worker with API client and quota management.

        Args:
            worker_id: Unique worker identifier
            task_type_ids: List of task type IDs to handle
            config: Configuration object (must have youtube_api_key)
            results_db: Database for storing results
            quota_storage_path: Path to quota tracking file (optional)
            daily_quota_limit: Daily quota limit (default: 10,000 units)
            **kwargs: Additional arguments passed to BaseVideoSourceWorker
        """
        # Initialize parent BaseVideoSourceWorker
        super().__init__(
            worker_id=worker_id,
            task_type_ids=task_type_ids,
            config=config,
            results_db=results_db,
            **kwargs,
        )

        # Validate YouTube API key
        if not hasattr(config, "youtube_api_key") or not config.youtube_api_key:
            raise ValueError("YouTube API key not configured in config.youtube_api_key")

        self.api_key = config.youtube_api_key

        # Initialize YouTube API client
        if YouTubeAPIClient:
            self.quota_storage_path = quota_storage_path or "data/youtube_quota.json"
            self.daily_quota_limit = daily_quota_limit

            self.youtube_client = YouTubeAPIClient(
                api_key=self.api_key,
                quota_storage_path=self.quota_storage_path,
                daily_quota_limit=self.daily_quota_limit,
            )

            # Initialize quota manager
            if QuotaManager:
                self.quota_manager = self.youtube_client.quota_manager
            else:
                self.quota_manager = None
        else:
            logger.warning("YouTubeAPIClient not available, some functionality may be limited")
            self.youtube_client = None
            self.quota_manager = None

        # YouTube-specific statistics
        self.youtube_api_calls = 0
        self.quota_exceeded_count = 0

        logger.info(
            f"YouTubeWorker {worker_id} initialized with YouTube API "
            f"(quota_storage: {self.quota_storage_path}, daily_limit: {self.daily_quota_limit})"
        )

    def check_quota_available(self, required_units: int = 1) -> bool:
        """Check if sufficient quota is available for operation.

        Args:
            required_units: Number of quota units required (default: 1)

        Returns:
            True if sufficient quota available, False otherwise
        """
        if not self.youtube_client or not self.quota_manager:
            logger.warning("Quota manager not available, assuming quota available")
            return True

        remaining = self.quota_manager.get_remaining_quota()
        return remaining >= required_units

    def get_quota_status(self) -> Dict[str, Any]:
        """Get current quota status.

        Returns:
            Dictionary with quota information:
            - total_used: Total units used today
            - remaining: Remaining units
            - daily_limit: Daily quota limit
            - percentage_used: Percentage of quota used
        """
        if not self.quota_manager:
            return {
                "total_used": 0,
                "remaining": self.daily_quota_limit,
                "daily_limit": self.daily_quota_limit,
                "percentage_used": 0.0,
            }

        usage = self.quota_manager.get_quota_usage()
        return {
            "total_used": usage["total_used"],
            "remaining": usage["remaining"],
            "daily_limit": usage["daily_limit"],
            "percentage_used": (
                (usage["total_used"] / usage["daily_limit"]) * 100
                if usage["daily_limit"] > 0
                else 0.0
            ),
        }

    def fetch_youtube_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Fetch video data from YouTube API.

        This is a helper method that handles quota checking and tracking
        automatically. Subclasses should use this instead of calling
        the API client directly.

        Args:
            video_id: YouTube video ID

        Returns:
            Video data dictionary or None if failed

        Raises:
            QuotaExceededException: If quota exceeded
            HttpError: If YouTube API error
        """
        # Check quota (videos.list costs 1 unit)
        if not self.check_quota_available(required_units=1):
            self.quota_exceeded_count += 1
            raise QuotaExceededException("Insufficient quota for videos.list")

        try:
            # Call YouTube API
            video = self.youtube_client.get_video_details(video_id)
            self.youtube_api_calls += 1

            return video

        except HttpError as e:
            logger.error(f"YouTube API error fetching video {video_id}: {e}")
            raise

    def fetch_youtube_videos_batch(self, video_ids: list) -> list:
        """Fetch multiple videos in a batch.

        Args:
            video_ids: List of YouTube video IDs

        Returns:
            List of video data dictionaries

        Raises:
            QuotaExceededException: If quota exceeded
        """
        # Check quota (videos.list costs 1 unit regardless of count)
        if not self.check_quota_available(required_units=1):
            self.quota_exceeded_count += 1
            raise QuotaExceededException("Insufficient quota for batch videos.list")

        try:
            videos = self.youtube_client.get_videos_batch(video_ids)
            self.youtube_api_calls += 1

            return videos

        except HttpError as e:
            logger.error(f"YouTube API error fetching videos batch: {e}")
            raise

    def search_youtube_videos(self, query: str, max_results: int = 10, **kwargs) -> list:
        """Search YouTube videos.

        Args:
            query: Search query string
            max_results: Maximum number of results (default: 10)
            **kwargs: Additional search parameters

        Returns:
            List of video data dictionaries

        Raises:
            QuotaExceededException: If quota exceeded
        """
        # Check quota (search.list costs 100 units)
        if not self.check_quota_available(required_units=100):
            self.quota_exceeded_count += 1
            raise QuotaExceededException("Insufficient quota for search.list (100 units)")

        try:
            results = self.youtube_client.search_videos(
                query=query, max_results=max_results, **kwargs
            )
            self.youtube_api_calls += 1

            return results

        except HttpError as e:
            logger.error(f"YouTube API error searching videos: {e}")
            raise

    def handle_youtube_error(self, error: HttpError) -> TaskResult:
        """Handle YouTube-specific API errors.

        This method converts YouTube HttpError exceptions into appropriate
        TaskResult responses with descriptive error messages.

        Args:
            error: HttpError from YouTube API

        Returns:
            TaskResult with error information
        """
        error_str = str(error)

        # Quota exceeded
        if "quotaExceeded" in error_str:
            self.quota_exceeded_count += 1
            logger.error(f"YouTube API quota exceeded for worker {self.worker_id}")
            return TaskResult(
                success=False, error="YouTube API quota exceeded. Try again tomorrow."
            )

        # Video not found
        if "videoNotFound" in error_str or error.resp.status == 404:
            logger.warning(f"YouTube video not found")
            return TaskResult(success=False, error="Video not found or deleted")

        # Video unavailable (private, deleted, etc.)
        if "forbidden" in error_str.lower() or error.resp.status == 403:
            logger.warning(f"YouTube video unavailable (private or restricted)")
            return TaskResult(success=False, error="Video is private or restricted")

        # Invalid API key
        if "invalid" in error_str.lower() and "key" in error_str.lower():
            logger.error(f"Invalid YouTube API key")
            return TaskResult(success=False, error="Invalid YouTube API key")

        # Rate limit (rare, but possible)
        if "rateLimitExceeded" in error_str or error.resp.status == 429:
            logger.warning(f"YouTube API rate limit exceeded")
            return TaskResult(success=False, error="Rate limit exceeded. Slow down requests.")

        # Generic error
        logger.error(f"YouTube API error: {error}")
        return TaskResult(success=False, error=f"YouTube API error: {error_str[:200]}")

    def convert_youtube_to_video_data(self, youtube_item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert YouTube API response format to standard video data format.

        YouTube API returns data in specific structure (snippet, contentDetails, statistics).
        This method converts it to our standardized video data format used by
        BaseVideoSourceWorker.

        Args:
            youtube_item: Raw YouTube API response item

        Returns:
            Standardized video data dictionary
        """
        snippet = youtube_item.get("snippet", {})
        statistics = youtube_item.get("statistics", {})
        content_details = youtube_item.get("contentDetails", {})

        return {
            "id": youtube_item.get("id", ""),
            "title": snippet.get("title", "Untitled"),
            "description": snippet.get("description", ""),
            "url": f"https://www.youtube.com/watch?v={youtube_item.get('id', '')}",
            "duration": content_details.get("duration", "PT0S"),
            "published_at": snippet.get("publishedAt", ""),
            "channel_id": snippet.get("channelId", ""),
            "channel_title": snippet.get("channelTitle", ""),
            "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "view_count": int(statistics.get("viewCount", 0)),
            "like_count": int(statistics.get("likeCount", 0)),
            "comment_count": int(statistics.get("commentCount", 0)),
            "category_id": snippet.get("categoryId", ""),
            "tags": snippet.get("tags", []),
            "has_subtitles": content_details.get("caption", "false") == "true",
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get YouTube worker statistics.

        Extends parent statistics with YouTube-specific metrics.

        Returns:
            Dictionary containing worker statistics including YouTube metrics
        """
        # Get parent statistics
        stats = super().get_statistics()

        # Add YouTube-specific statistics
        stats.update(
            {
                "youtube_api_calls": self.youtube_api_calls,
                "quota_exceeded_count": self.quota_exceeded_count,
                "quota_status": self.get_quota_status(),
            }
        )

        return stats


__all__ = ["BaseYouTubeWorker"]
