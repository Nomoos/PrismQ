"""YouTube Video Worker - Refactored to use Template Method hierarchy.

This worker now inherits from BaseYouTubeWorker and focuses only on
video-specific endpoint logic. All common YouTube functionality (API client,
quota management, error handling) is inherited from BaseYouTubeWorker.

Hierarchy:
    BaseWorker → BaseSourceWorker → BaseVideoSourceWorker → BaseYouTubeWorker → YouTubeVideoWorker

Following SOLID principles:
- Single Responsibility: Only handles video endpoint scraping
- Dependency Inversion: Inherits dependencies from hierarchy
- Liskov Substitution: Can substitute BaseYouTubeWorker
"""

import logging
from typing import Optional
from pathlib import Path
import sys

# Import IdeaInspiration model
model_path = Path(__file__).resolve().parents[5] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration import IdeaInspiration
from idea_inspiration_db import IdeaInspirationDatabase

# Import parent class
from .base_youtube_worker import BaseYouTubeWorker
from src.core.base_worker import Task, TaskResult

logger = logging.getLogger(__name__)


class YouTubeVideoWorker(BaseYouTubeWorker):
    """Worker for scraping individual YouTube videos.
    
    This worker extends BaseYouTubeWorker and focuses ONLY on video endpoint
    logic. All YouTube API, quota management, and video operations are
    inherited from parent classes.
    
    **Progressive Enrichment Levels**:
    - Level 1 (BaseWorker): Task claiming, processing loop
    - Level 2 (BaseSourceWorker): Configuration, database
    - Level 3 (BaseVideoSourceWorker): Video validation, duration parsing
    - Level 4 (BaseYouTubeWorker): YouTube API, quota management
    - Level 5 (THIS CLASS): Video endpoint scraping
    
    **Task Types Handled**:
    - youtube_video_single: Scrape single video by ID/URL
    - youtube_video_search: Search and scrape multiple videos
    - youtube_video_scrape: General scraping (auto-routes)
    
    **Example Usage**:
    ```python
    worker = YouTubeVideoWorker(
        worker_id="youtube-video-01",
        task_type_ids=["youtube_video_single", "youtube_video_search"],
        config=config,
        results_db=database
    )
    worker.run()
    ```
    """
    
    def __init__(
        self,
        worker_id: str,
        task_type_ids: list,
        config,
        results_db,
        idea_db_path: Optional[str] = None,
        **kwargs
    ):
        """Initialize YouTube Video Worker.
        
        Args:
            worker_id: Unique worker identifier
            task_type_ids: List of task type IDs (e.g., ["youtube_video_single"])
            config: Configuration object (must have youtube_api_key)
            results_db: Results database
            idea_db_path: Path to IdeaInspiration database (optional)
            **kwargs: Additional arguments passed to BaseYouTubeWorker
        """
        # Initialize parent BaseYouTubeWorker
        # This handles YouTube API client, quota manager, etc.
        super().__init__(
            worker_id=worker_id,
            task_type_ids=task_type_ids,
            config=config,
            results_db=results_db,
            **kwargs
        )
        
        # Initialize IdeaInspiration database (video endpoint specific)
        self.idea_db_path = idea_db_path or getattr(config, 'idea_db_path', 'ideas.db')
        self.idea_db = IdeaInspirationDatabase(self.idea_db_path, interactive=False)
        
        logger.info(
            f"YouTubeVideoWorker {worker_id} initialized "
            f"(idea_db: {self.idea_db_path})"
        )
    
    def process_task(self, task: Task) -> TaskResult:
        """Process a YouTube video scraping task.
        
        This is the main entry point called by BaseWorker.run().
        Routes to appropriate handler based on task type.
        
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
                # General scraping - route based on parameters
                return self._process_scrape(task)
            else:
                return TaskResult(
                    success=False,
                    error=f"Unknown task type: {task.task_type}"
                )
                
        except Exception as e:
            # Use parent's error handling for YouTube-specific errors
            if hasattr(e, 'resp'):  # HttpError
                return self.handle_youtube_error(e)
            
            # Generic error
            error_msg = f"Error processing YouTube task: {e}"
            logger.error(error_msg, exc_info=True)
            return TaskResult(success=False, error=error_msg)
    
    def _process_scrape(self, task: Task) -> TaskResult:
        """Process general scraping task - route based on parameters.
        
        Args:
            task: Task with video_id, video_url, or search_query
            
        Returns:
            TaskResult with scraped data
        """
        params = task.parameters
        
        # Route to search if search_query provided
        if 'search_query' in params:
            return self._process_search(task)
        
        # Route to single video if video_id or video_url provided
        if 'video_id' in params or 'video_url' in params:
            return self._process_single_video(task)
        
        # No valid parameters
        return TaskResult(
            success=False,
            error="No valid parameters. Expected 'video_id', 'video_url', or 'search_query'"
        )
    
    def _process_single_video(self, task: Task) -> TaskResult:
        """Process single YouTube video by ID or URL.
        
        Uses inherited methods from parent classes:
        - fetch_youtube_video() from BaseYouTubeWorker (Level 4)
        - validate_video_metadata() from BaseVideoSourceWorker (Level 3)
        - create_video_inspiration() from BaseVideoSourceWorker (Level 3)
        
        Args:
            task: Task with video_id or video_url parameter
            
        Returns:
            TaskResult with scraped video data
        """
        params = task.parameters
        
        # Extract video ID
        video_id = params.get('video_id')
        if not video_id:
            video_url = params.get('video_url', '')
            video_id = self._extract_video_id(video_url)
        
        if not video_id:
            return TaskResult(
                success=False,
                error="No video_id or valid video_url provided"
            )
        
        try:
            # Fetch video from YouTube API (from BaseYouTubeWorker)
            youtube_item = self.fetch_youtube_video(video_id)
            
            if not youtube_item:
                return TaskResult(
                    success=False,
                    error=f"Video not found: {video_id}"
                )
            
            # Convert YouTube format to standard format (from BaseYouTubeWorker)
            video_data = self.convert_youtube_to_video_data(youtube_item)
            
            # Validate video metadata (from BaseVideoSourceWorker)
            if not self.validate_video_metadata(video_data):
                return TaskResult(
                    success=False,
                    error=f"Invalid video metadata for {video_id}"
                )
            
            # Create IdeaInspiration (from BaseVideoSourceWorker)
            idea = self.create_video_inspiration(
                video_data=video_data,
                platform='youtube',
                source_url=f"https://www.youtube.com/watch?v={video_id}"
            )
            
            if not idea:
                return TaskResult(
                    success=False,
                    error=f"Failed to create IdeaInspiration for {video_id}"
                )
            
            # Save to IdeaInspiration database
            idea_id = self.idea_db.insert(idea)
            
            # Get quota status
            quota_status = self.get_quota_status()
            
            logger.info(
                f"Successfully scraped YouTube video {video_id}, "
                f"saved as IdeaInspiration ID {idea_id}. "
                f"Quota: {quota_status['remaining']}/{quota_status['daily_limit']} remaining"
            )
            
            return TaskResult(
                success=True,
                data={
                    'video_id': video_id,
                    'idea_id': idea_id,
                    'title': idea.title,
                    'view_count': video_data.get('view_count', 0),
                    'quota_remaining': quota_status['remaining']
                },
                items_processed=1,
                metrics={
                    'api_calls': 1,
                    'videos_scraped': 1,
                    'quota_used': quota_status['total_used'],
                    'quota_remaining': quota_status['remaining']
                }
            )
            
        except Exception as e:
            # Use parent's YouTube error handling
            if hasattr(e, 'resp'):  # HttpError
                return self.handle_youtube_error(e)
            
            logger.error(f"Error processing video {video_id}: {e}", exc_info=True)
            return TaskResult(
                success=False,
                error=f"Error processing video {video_id}: {str(e)}"
            )
    
    def _process_search(self, task: Task) -> TaskResult:
        """Process YouTube search query to find and scrape videos.
        
        Uses inherited methods from parent classes:
        - search_youtube_videos() from BaseYouTubeWorker (Level 4)
        - fetch_youtube_videos_batch() from BaseYouTubeWorker (Level 4)
        - create_video_inspiration() from BaseVideoSourceWorker (Level 3)
        
        Args:
            task: Task with search_query parameter
            
        Returns:
            TaskResult with scraped videos data
        """
        params = task.parameters
        search_query = params.get('search_query')
        max_results = params.get('max_results', 5)
        
        if not search_query:
            return TaskResult(
                success=False,
                error="No search_query provided"
            )
        
        try:
            # Search for videos (from BaseYouTubeWorker)
            search_results = self.search_youtube_videos(
                query=search_query,
                max_results=max_results,
                video_duration='short',  # Prefer YouTube Shorts
                order='viewCount'
            )
            
            if not search_results:
                quota_status = self.get_quota_status()
                return TaskResult(
                    success=True,
                    data={
                        'message': 'No videos found',
                        'quota_remaining': quota_status['remaining']
                    },
                    items_processed=0
                )
            
            # Extract video IDs from search results
            video_ids = [
                item['id']['videoId']
                for item in search_results
                if item['id'].get('kind') == 'youtube#video'
            ]
            
            # Get detailed information (from BaseYouTubeWorker)
            videos = self.fetch_youtube_videos_batch(video_ids)
            
            # Process each video
            ideas_saved = []
            for youtube_item in videos:
                try:
                    # Convert format (from BaseYouTubeWorker)
                    video_data = self.convert_youtube_to_video_data(youtube_item)
                    
                    # Create IdeaInspiration (from BaseVideoSourceWorker)
                    idea = self.create_video_inspiration(
                        video_data=video_data,
                        platform='youtube',
                        source_url=f"https://www.youtube.com/watch?v={video_data['id']}"
                    )
                    
                    if idea:
                        idea_id = self.idea_db.insert(idea)
                        ideas_saved.append({
                            'video_id': video_data['id'],
                            'idea_id': idea_id,
                            'title': idea.title
                        })
                except Exception as e:
                    logger.warning(f"Failed to process video {youtube_item.get('id')}: {e}")
                    continue
            
            # Get quota status
            quota_status = self.get_quota_status()
            
            logger.info(
                f"Search query '{search_query}' returned {len(ideas_saved)} videos. "
                f"Quota: {quota_status['remaining']}/{quota_status['daily_limit']} remaining"
            )
            
            return TaskResult(
                success=True,
                data={
                    'search_query': search_query,
                    'videos': ideas_saved,
                    'quota_remaining': quota_status['remaining']
                },
                items_processed=len(ideas_saved),
                metrics={
                    'api_calls': 2,  # search + videos.list
                    'videos_scraped': len(ideas_saved),
                    'quota_used': quota_status['total_used'],
                    'quota_remaining': quota_status['remaining']
                }
            )
            
        except Exception as e:
            # Use parent's YouTube error handling
            if hasattr(e, 'resp'):  # HttpError
                return self.handle_youtube_error(e)
            
            logger.error(f"Error processing search '{search_query}': {e}", exc_info=True)
            return TaskResult(
                success=False,
                error=f"Error processing search: {str(e)}"
            )
    
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
        import re
        
        if not url:
            return None
        
        # Pattern for standard watch URLs
        match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)
        
        # Pattern for youtu.be short URLs
        match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)
        
        # Pattern for /shorts/ URLs
        match = re.search(r'/shorts/([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)
        
        # If it looks like a video ID itself (11 characters)
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
        
        return None


__all__ = ['YouTubeVideoWorker']
