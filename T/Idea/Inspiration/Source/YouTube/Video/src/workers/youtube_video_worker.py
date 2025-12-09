"""YouTube Video Worker for scraping video metadata and content.

This worker processes YouTube video URLs/IDs from the task queue,
extracts metadata, and saves results to the IdeaInspiration database.

Following SOLID principles:
- Single Responsibility: Only handles YouTube video scraping
- Dependency Inversion: Depends on abstractions (BaseWorker, Config, Database)
- Liskov Substitution: Can substitute BaseWorker in any context
"""

import json
import logging
import re

# Import IdeaInspiration model
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from googleapiclient.errors import HttpError

from ..core.config import Config
from ..core.database import Database
from ..core.subtitle_extractor import SubtitleExtractor
from ..core.youtube_api_client import YouTubeAPIClient
from ..core.youtube_quota_manager import QuotaExceededException
from . import Task, TaskResult, TaskStatus
from .base_worker import BaseWorker

model_path = Path(__file__).resolve().parents[5] / "Model"
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration import ContentType, IdeaInspiration
from idea_inspiration_db import IdeaInspirationDatabase

logger = logging.getLogger(__name__)


class YouTubeVideoWorker(BaseWorker):
    """Worker for scraping YouTube video metadata and content.

    This worker extends BaseWorker and implements the process_task method
    to handle YouTube video scraping tasks.

    Task Parameters:
        video_id: YouTube video ID (required if video_url not provided)
        video_url: Full YouTube video URL (required if video_id not provided)
        search_query: Search query to find videos (alternative mode)
        max_results: Number of videos to fetch for search (default: 5)

    Task Types:
        - youtube_video_single: Scrape a single video by ID/URL
        - youtube_video_search: Search and scrape multiple videos
        - youtube_video_scrape: General scraping (auto-routes based on parameters)

    Example Tasks:
        Single video:
        {
            "task_type": "youtube_video_single",
            "parameters": {
                "video_id": "dQw4w9WgXcQ"
            }
        }

        Search:
        {
            "task_type": "youtube_video_search",
            "parameters": {
                "search_query": "startup ideas",
                "max_results": 5
            }
        }

        General scrape (auto-routes):
        {
            "task_type": "youtube_video_scrape",
            "parameters": {
                "video_id": "dQw4w9WgXcQ"  // or video_url or search_query
            }
        }
    """

    def __init__(
        self,
        worker_id: str,
        queue_db_path: str,
        config: Config,
        results_db: Database,
        idea_db_path: Optional[str] = None,
        quota_storage_path: Optional[str] = None,
        **kwargs,
    ):
        """Initialize YouTube Video Worker.

        Args:
            worker_id: Unique worker identifier
            queue_db_path: Path to queue database
            config: Configuration object
            results_db: Results database
            idea_db_path: Path to IdeaInspiration database (optional)
            quota_storage_path: Path to quota JSON storage file (optional)
            **kwargs: Additional arguments passed to BaseWorker
        """
        super().__init__(
            worker_id=worker_id,
            queue_db_path=queue_db_path,
            config=config,
            results_db=results_db,
            **kwargs,
        )

        # Validate YouTube API key
        if not hasattr(config, "youtube_api_key") or not config.youtube_api_key:
            raise ValueError("YouTube API key not configured")

        # Initialize YouTube API client with quota management (JSON storage)
        self.quota_storage_path = quota_storage_path or getattr(
            config, "quota_storage_path", "data/youtube_quota.json"
        )
        self.youtube_client = YouTubeAPIClient(
            api_key=config.youtube_api_key,
            quota_storage_path=self.quota_storage_path,
            daily_quota_limit=getattr(config, "youtube_daily_quota_limit", 10000),
        )

        # Initialize IdeaInspiration database
        self.idea_db_path = idea_db_path or getattr(config, "idea_db_path", "ideas.db")
        self.idea_db = IdeaInspirationDatabase(self.idea_db_path, interactive=False)

        # Initialize subtitle extractor
        try:
            self.subtitle_extractor = SubtitleExtractor()
            logger.info(f"SubtitleExtractor initialized successfully")
        except ValueError as e:
            logger.warning(
                f"SubtitleExtractor initialization failed: {e}. Subtitles will not be available."
            )
            self.subtitle_extractor = None

        logger.info(
            f"YouTubeVideoWorker {worker_id} initialized with quota management "
            f"(quota_storage: {self.quota_storage_path}, idea_db: {self.idea_db_path})"
        )

    def process_task(self, task: Task) -> TaskResult:
        """Process a YouTube video scraping task.

        Args:
            task: Task object with type and parameters

        Returns:
            TaskResult with success status and scraped data
        """
        try:
            logger.info(f"Processing YouTube video task {task.id} (type: {task.task_type})")

            # Route to appropriate handler based on task type
            if task.task_type == "youtube_video_single":
                return self._process_single_video(task)
            elif task.task_type == "youtube_video_search":
                return self._process_search(task)
            elif task.task_type == "youtube_video_scrape":
                # General scraping task - route based on parameters
                return self._process_scrape(task)
            else:
                return TaskResult(success=False, error=f"Unknown task type: {task.task_type}")

        except HttpError as e:
            error_msg = f"YouTube API error: {e}"
            logger.error(error_msg)
            return TaskResult(success=False, error=error_msg)

        except Exception as e:
            error_msg = f"Error processing YouTube task: {e}"
            logger.error(error_msg, exc_info=True)
            return TaskResult(success=False, error=error_msg)

    def _process_scrape(self, task: Task) -> TaskResult:
        """Process a general YouTube video scraping task.

        This method intelligently routes to the appropriate handler based on
        the parameters provided in the task.

        Args:
            task: Task with video_id, video_url, or search_query parameter

        Returns:
            TaskResult with scraped video data
        """
        params = task.parameters

        # Check if this is a search task
        if "search_query" in params:
            return self._process_search(task)

        # Check if this is a single video task
        if "video_id" in params or "video_url" in params:
            return self._process_single_video(task)

        # No valid parameters provided
        return TaskResult(
            success=False,
            error="No valid parameters provided. "
            "Expected 'video_id', 'video_url', or 'search_query'",
        )

    def _process_single_video(self, task: Task) -> TaskResult:
        """Process a single YouTube video by ID or URL.

        Args:
            task: Task with video_id or video_url parameter

        Returns:
            TaskResult with scraped video data
        """
        params = task.parameters

        # Extract video ID from parameters
        video_id = params.get("video_id")
        if not video_id:
            video_url = params.get("video_url", "")
            video_id = self._extract_video_id(video_url)

        if not video_id:
            return TaskResult(success=False, error="No video_id or valid video_url provided")

        # Check quota before making API call
        if not self.youtube_client.can_execute_operation("videos.list"):
            remaining = self.youtube_client.get_remaining_quota()
            return TaskResult(
                success=False, error=f"YouTube API quota exceeded. Remaining: {remaining} units"
            )

        # Fetch video details from YouTube API with quota tracking
        try:
            video = self.youtube_client.get_video_details(video_id)

            if not video:
                return TaskResult(success=False, error=f"Video not found: {video_id}")

            # Convert to IdeaInspiration
            idea = self._video_to_idea(video)

            # Save to IdeaInspiration database
            idea_id = self.idea_db.insert(idea)

            # Get quota usage
            quota_usage = self.youtube_client.get_quota_usage()

            logger.info(
                f"Successfully scraped YouTube video {video_id}, "
                f"saved as IdeaInspiration ID {idea_id}. "
                f"Quota: {quota_usage['remaining']}/{quota_usage['daily_limit']} remaining"
            )

            return TaskResult(
                success=True,
                data={
                    "video_id": video_id,
                    "idea_id": idea_id,
                    "title": idea.title,
                    "view_count": idea.metadata.get("view_count", "0"),
                    "quota_remaining": quota_usage["remaining"],
                },
                items_processed=1,
                metrics={
                    "api_calls": 1,
                    "videos_scraped": 1,
                    "quota_used": quota_usage["total_used"],
                    "quota_remaining": quota_usage["remaining"],
                },
            )

        except QuotaExceededException as e:
            error_msg = f"YouTube API quota exceeded: {e}"
            logger.error(error_msg)
            return TaskResult(success=False, error=error_msg)

        except HttpError as e:
            return TaskResult(success=False, error=f"YouTube API error for video {video_id}: {e}")

    def _process_search(self, task: Task) -> TaskResult:
        """Process a YouTube search query to find and scrape videos.

        Args:
            task: Task with search_query parameter

        Returns:
            TaskResult with scraped videos data
        """
        params = task.parameters
        search_query = params.get("search_query")
        max_results = params.get("max_results", 5)

        if not search_query:
            return TaskResult(success=False, error="No search_query provided")

        # Check quota before making API calls
        # search.list costs 100 units, videos.list costs 1 unit
        if not self.youtube_client.can_execute_operation("search.list"):
            remaining = self.youtube_client.get_remaining_quota()
            return TaskResult(
                success=False,
                error=f"YouTube API quota exceeded for search. Remaining: {remaining} units",
            )

        try:
            # Search for videos using the API client
            search_results = self.youtube_client.search_videos(
                query=search_query,
                max_results=max_results,
                video_duration="short",  # Prefer YouTube Shorts
                order="viewCount",
            )

            if not search_results:
                quota_usage = self.youtube_client.get_quota_usage()
                return TaskResult(
                    success=True,
                    data={
                        "message": "No videos found",
                        "quota_remaining": quota_usage["remaining"],
                    },
                    items_processed=0,
                    metrics={
                        "api_calls": 1,
                        "videos_scraped": 0,
                        "quota_used": quota_usage["total_used"],
                        "quota_remaining": quota_usage["remaining"],
                    },
                )

            # Extract video IDs
            video_ids = [
                item["id"]["videoId"]
                for item in search_results
                if item["id"].get("kind") == "youtube#video"
            ]

            # Get detailed information for found videos
            videos = self.youtube_client.get_videos_batch(video_ids)

            # Process each video
            ideas_saved = []
            for video in videos:
                idea = self._video_to_idea(video)
                idea_id = self.idea_db.insert(idea)
                ideas_saved.append(
                    {"video_id": video["id"], "idea_id": idea_id, "title": idea.title}
                )

            # Get final quota usage
            quota_usage = self.youtube_client.get_quota_usage()

            logger.info(
                f"Search query '{search_query}' returned {len(ideas_saved)} videos. "
                f"Quota: {quota_usage['remaining']}/{quota_usage['daily_limit']} remaining"
            )

            return TaskResult(
                success=True,
                data={
                    "search_query": search_query,
                    "videos": ideas_saved,
                    "quota_remaining": quota_usage["remaining"],
                },
                items_processed=len(ideas_saved),
                metrics={
                    "api_calls": 2,  # search + videos.list
                    "videos_scraped": len(ideas_saved),
                    "quota_used": quota_usage["total_used"],
                    "quota_remaining": quota_usage["remaining"],
                },
            )

        except QuotaExceededException as e:
            error_msg = f"YouTube API quota exceeded during search: {e}"
            logger.error(error_msg)
            return TaskResult(success=False, error=error_msg)

        except HttpError as e:
            return TaskResult(success=False, error=f"YouTube API error during search: {e}")

    def _video_to_idea(self, video: Dict[str, Any]) -> IdeaInspiration:
        """Convert YouTube API video response to IdeaInspiration object.

        Args:
            video: Video data from YouTube API

        Returns:
            IdeaInspiration object
        """
        snippet = video["snippet"]
        statistics = video.get("statistics", {})
        content_details = video.get("contentDetails", {})

        # Extract tags
        tags = self._extract_tags(snippet)

        # Build metadata dictionary (all string values for SQLite)
        metadata = {
            "video_id": video["id"],
            "channel_id": snippet.get("channelId", ""),
            "channel_title": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "duration": content_details.get("duration", ""),
            "view_count": str(statistics.get("viewCount", 0)),
            "like_count": str(statistics.get("likeCount", 0)),
            "comment_count": str(statistics.get("commentCount", 0)),
            "category_id": snippet.get("categoryId", ""),
        }

        # Extract subtitles if available
        subtitle_text = ""
        if self.subtitle_extractor:
            try:
                logger.info(f"Attempting to extract subtitles for video {video['id']}")
                subtitle_text = self.subtitle_extractor.extract_subtitles(video["id"]) or ""
                if subtitle_text:
                    logger.info(
                        f"Successfully extracted {len(subtitle_text)} characters of subtitles"
                    )
                    metadata["subtitles_available"] = "true"
                else:
                    logger.info(f"No subtitles available for video {video['id']}")
                    metadata["subtitles_available"] = "false"
            except Exception as e:
                logger.warning(f"Error extracting subtitles for video {video['id']}: {e}")
                metadata["subtitles_available"] = "false"
        else:
            logger.debug("Subtitle extractor not available")
            metadata["subtitles_available"] = "false"

        # Create IdeaInspiration using from_video factory method
        idea = IdeaInspiration.from_video(
            title=snippet.get("title", "Untitled Video"),
            description=snippet.get("description", ""),
            subtitle_text=subtitle_text,  # Now includes downloaded subtitles
            keywords=tags,
            metadata=metadata,
            source_id=video["id"],
            source_url=f"https://www.youtube.com/watch?v={video['id']}",
            source_platform="youtube",
            source_created_by=snippet.get("channelTitle", ""),
            source_created_at=snippet.get("publishedAt", ""),
        )

        return idea

    def _extract_tags(self, snippet: Dict[str, Any]) -> List[str]:
        """Extract and format tags from YouTube video snippet.

        Args:
            snippet: Video snippet from YouTube API

        Returns:
            List of tag strings
        """
        tags = ["youtube_video"]

        # Check if it's a Short based on URL format or duration
        # Note: This is a heuristic, actual Shorts detection requires /shorts/ URL
        tags.append("youtube_shorts")

        # Add channel name
        if "channelTitle" in snippet:
            tags.append(snippet["channelTitle"])

        # Add category
        if "categoryId" in snippet:
            tags.append(f"category_{snippet['categoryId']}")

        # Add video tags (limit to first 5)
        if "tags" in snippet:
            video_tags = snippet["tags"][:5]
            tags.extend(video_tags)

        # Clean and format tags
        return [tag.strip() for tag in tags if tag and tag.strip()]

    @staticmethod
    def _extract_video_id(url: str) -> Optional[str]:
        """Extract YouTube video ID from various URL formats.

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

    def _save_results(self, task: Task, result: TaskResult) -> None:
        """Save results to database.

        Note: IdeaInspiration records are already saved in _video_to_idea.
        This method is for any additional result storage if needed.

        Args:
            task: The completed task
            result: The task execution result
        """
        # Results already saved to IdeaInspiration database
        # This override prevents duplicate saves
        pass


__all__ = ["YouTubeVideoWorker"]
