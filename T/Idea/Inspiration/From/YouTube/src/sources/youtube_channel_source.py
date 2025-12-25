"""YouTube Channel source implementation.

This module provides YouTubeChannelSource for fetching videos from specific
YouTube channels using channel ID, custom URL (@username), or uploads playlist ID.
"""

import logging
import re
import subprocess
from typing import Any, Dict, List, Optional

try:
    from ..base import YouTubeBaseSource
    from ..exceptions import YouTubeError, YouTubeInvalidVideoError
except ImportError:
    from base.youtube_base_source import YouTubeBaseSource
    from exceptions.youtube_exceptions import YouTubeError, YouTubeInvalidVideoError

logger = logging.getLogger(__name__)


class YouTubeChannelSource(YouTubeBaseSource):
    """
    YouTube Channel source implementation.

    Fetches videos from specific YouTube channels using an efficient two-stage approach:
    1. Extract video IDs quickly using yt-dlp (no API quota)
    2. Batch fetch video details via YouTube API (minimal quota)

    This approach provides 99% API quota savings compared to traditional methods.

    Attributes:
        Inherits from YouTubeBaseSource:
        - api_client: YouTubeAPIClient for API interactions
        - mapper: YouTubeMapper for data transformation
        - config: YouTubeConfig with settings

    Example:
        >>> config = {'api_key': 'YOUR_KEY'}
        >>> source = YouTubeChannelSource(config)
        >>>
        >>> # Fetch videos from channel
        >>> videos = source.fetch_videos(
        ...     query='@mkbhd',  # Can use @username, channel ID, or URL
        ...     limit=50
        ... )
        >>>
        >>> # With filters
        >>> videos = source.fetch_videos(
        ...     query='UC...',
        ...     limit=100,
        ...     filters={'published_after': '2024-01-01T00:00:00Z'}
        ... )
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize YouTube Channel source.

        Args:
            config: Configuration dictionary with YouTube settings
        """
        super().__init__(config)
        logger.info("YouTubeChannelSource initialized")

    def fetch_videos(
        self, query: Optional[str] = None, limit: int = 50, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch videos from a YouTube channel.

        Uses efficient two-stage approach:
        1. Extract video IDs via yt-dlp (fast, no quota)
        2. Batch fetch details via API (minimal quota)

        Args:
            query: Channel ID (UC...), username (@user), or URL
            limit: Maximum number of videos to fetch (default: 50)
            filters: Additional filters:
                - published_after: RFC 3339 timestamp
                - published_before: RFC 3339 timestamp
                - order: 'date' or 'viewCount'

        Returns:
            List of video metadata dictionaries compatible with VideoMetadata schema

        Raises:
            YouTubeError: If channel fetching fails
            ValueError: If query is empty

        Example:
            >>> source = YouTubeChannelSource(config)
            >>> videos = source.fetch_videos('@mkbhd', limit=20)
            >>> print(f"Found {len(videos)} videos")
        """
        if not query:
            raise ValueError("Channel query (ID, username, or URL) is required")

        logger.info(f"Fetching videos from channel: {query} (limit: {limit})")

        try:
            # Stage 1: Get video IDs efficiently via yt-dlp
            video_ids = self.fetch_channel_videos_efficient(query, limit)

            if not video_ids:
                logger.warning(f"No videos found for channel: {query}")
                return []

            logger.info(f"Found {len(video_ids)} video IDs from channel")

            # Stage 2: Batch fetch video details via API
            videos = self._fetch_videos_batch(video_ids)

            # Apply filters if provided
            if filters:
                videos = self._apply_filters(videos, filters)

            # Limit results
            videos = videos[:limit]

            logger.info(f"Returning {len(videos)} videos from channel")
            return videos

        except Exception as e:
            logger.error(f"Error fetching videos from channel {query}: {e}")
            raise YouTubeError(f"Failed to fetch channel videos: {e}")

    def fetch_channel_videos_efficient(self, channel_identifier: str, limit: int = 50) -> List[str]:
        """
        Efficiently fetch video IDs from channel using yt-dlp.

        Uses --flat-playlist to get video IDs without downloading metadata.
        This is much faster than API and uses no API quota.

        Args:
            channel_identifier: Channel ID, @username, or URL
            limit: Maximum number of video IDs to fetch

        Returns:
            List of video IDs

        Raises:
            YouTubeError: If yt-dlp fails

        Example:
            >>> ids = source.fetch_channel_videos_efficient('@mkbhd', 100)
            >>> print(f"Got {len(ids)} video IDs")
        """
        try:
            # Convert to channel URL if not already
            channel_url = self._normalize_channel_url(channel_identifier)

            # Build yt-dlp command
            cmd = [
                "yt-dlp",
                "--flat-playlist",
                "--get-id",
                "--playlist-end",
                str(limit),
                "--no-warnings",
                channel_url,
            ]

            logger.debug(f"Running yt-dlp command: {' '.join(cmd)}")

            # Execute yt-dlp
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"yt-dlp failed: {error_msg}")
                raise YouTubeError(f"yt-dlp failed: {error_msg}")

            # Parse video IDs from output
            video_ids = [
                line.strip()
                for line in result.stdout.strip().split("\n")
                if line.strip() and len(line.strip()) == 11  # YouTube IDs are 11 chars
            ]

            logger.info(f"yt-dlp extracted {len(video_ids)} video IDs")
            return video_ids

        except subprocess.TimeoutExpired:
            raise YouTubeError("yt-dlp command timed out after 60 seconds")
        except FileNotFoundError:
            raise YouTubeError("yt-dlp not found. Please install: pip install yt-dlp")
        except Exception as e:
            raise YouTubeError(f"Failed to fetch channel videos: {e}")

    def get_channel_uploads_playlist(self, channel_id: str) -> str:
        """
        Get the uploads playlist ID for a channel.

        YouTube channels have an uploads playlist (starts with 'UU' instead of 'UC')
        that contains all uploaded videos.

        Args:
            channel_id: YouTube channel ID (starts with UC)

        Returns:
            Uploads playlist ID (starts with UU)

        Example:
            >>> playlist_id = source.get_channel_uploads_playlist('UC...')
            >>> print(playlist_id)  # 'UU...'
        """
        # Simple transformation: UC -> UU
        if channel_id.startswith("UC"):
            return "UU" + channel_id[2:]

        # If already a playlist ID, return as-is
        if channel_id.startswith("UU") or channel_id.startswith("PL"):
            return channel_id

        # Otherwise, fetch from API
        try:
            response = self.api_client.get_channel_details([channel_id])
            if response.get("items"):
                channel_data = response["items"][0]
                content_details = channel_data.get("contentDetails", {})
                related_playlists = content_details.get("relatedPlaylists", {})
                return related_playlists.get("uploads", "")
        except Exception as e:
            logger.error(f"Failed to get uploads playlist: {e}")

        return ""

    def create_tasks_for_new_videos(self, channel_id: str, task_manager_client: Any) -> int:
        """
        Create tasks for new videos from channel.

        **CRITICAL**: Uses TaskManager API as single source of truth for
        distributed workers. Never checks local database.

        Process:
        1. Fetch video IDs from channel (via yt-dlp)
        2. Query TaskManager API for existing tasks (ANY status)
        3. Filter out videos that already have tasks
        4. Create tasks ONLY for new videos

        Args:
            channel_id: YouTube channel ID
            task_manager_client: TaskManager API client with methods:
                - list_tasks(task_type, status)
                - create_task(task_type, params, priority)

        Returns:
            Number of new tasks created

        Example:
            >>> from TaskManager import TaskManagerClient
            >>> tm_client = TaskManagerClient(api_url="http://taskmanager:8000")
            >>> new_tasks = source.create_tasks_for_new_videos('UC...', tm_client)
            >>> print(f"Created {new_tasks} new tasks")
        """
        try:
            # Step 1: Get all video IDs from channel
            logger.info(f"Fetching video IDs for channel: {channel_id}")
            video_ids = self.fetch_channel_videos_efficient(channel_id, limit=1000)

            if not video_ids:
                logger.warning(f"No videos found for channel: {channel_id}")
                return 0

            logger.info(f"Found {len(video_ids)} videos in channel")

            # Step 2: Check TaskManager API for existing tasks
            logger.info("Checking TaskManager for existing tasks...")
            existing_tasks = task_manager_client.list_tasks(
                task_type="youtube_video_single", status="pending,claimed,completed"
            )

            # Extract video IDs from existing tasks
            existing_video_ids = set()
            for task in existing_tasks:
                params = task.get("params", {})
                if "video_id" in params:
                    existing_video_ids.add(params["video_id"])

            logger.info(f"Found {len(existing_video_ids)} existing tasks in TaskManager")

            # Step 3: Filter out videos that already have tasks
            new_video_ids = [vid for vid in video_ids if vid not in existing_video_ids]

            logger.info(f"Identified {len(new_video_ids)} new videos (not in TaskManager)")

            # Step 4: Create tasks for new videos
            tasks_created = 0
            for video_id in new_video_ids:
                try:
                    task_manager_client.create_task(
                        task_type="youtube_video_single", params={"video_id": video_id}, priority=5
                    )
                    tasks_created += 1
                except Exception as e:
                    logger.error(f"Failed to create task for video {video_id}: {e}")

            logger.info(f"Successfully created {tasks_created} new tasks")
            return tasks_created

        except Exception as e:
            logger.error(f"Error creating tasks for channel {channel_id}: {e}")
            raise YouTubeError(f"Failed to create tasks for channel: {e}")

    def _normalize_channel_url(self, identifier: str) -> str:
        """
        Normalize channel identifier to full URL.

        Args:
            identifier: Channel ID (UC...), @username, or URL

        Returns:
            Full YouTube channel URL
        """
        # Already a full URL
        if identifier.startswith("http"):
            return identifier

        # Username format (@user)
        if identifier.startswith("@"):
            return f"https://www.youtube.com/{identifier}/videos"

        # Channel ID format (UC...)
        if identifier.startswith("UC"):
            return f"https://www.youtube.com/channel/{identifier}/videos"

        # Assume it's a username without @
        return f"https://www.youtube.com/@{identifier}/videos"

    def _apply_filters(
        self, videos: List[Dict[str, Any]], filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply filters to video list.

        Args:
            videos: List of video metadata dictionaries
            filters: Filter criteria (published_after, published_before, order)

        Returns:
            Filtered video list
        """
        filtered = videos

        # Filter by publish date
        if "published_after" in filters:
            published_after = filters["published_after"]
            filtered = [
                v
                for v in filtered
                if v.get("published_at") and v["published_at"] >= published_after
            ]

        if "published_before" in filters:
            published_before = filters["published_before"]
            filtered = [
                v
                for v in filtered
                if v.get("published_at") and v["published_at"] <= published_before
            ]

        # Sort by order
        if filters.get("order") == "viewCount":
            filtered = sorted(filtered, key=lambda v: v.get("view_count", 0), reverse=True)
        elif filters.get("order") == "date":
            filtered = sorted(filtered, key=lambda v: v.get("published_at", ""), reverse=True)

        return filtered
