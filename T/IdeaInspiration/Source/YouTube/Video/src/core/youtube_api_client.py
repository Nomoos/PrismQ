"""YouTube Data API v3 Client with Quota Management.

This module provides a wrapper around google-api-python-client with integrated
quota management, rate limiting, and error handling.

Following SOLID principles:
- Single Responsibility: API client with quota awareness
- Dependency Inversion: Depends on YouTubeQuotaManager abstraction
- Open/Closed: Extensible via configuration

Note: Uses JSON-based quota storage to comply with architectural requirement
that SQLite databases are reserved for IdeaInspiration model only.
"""

import logging
import time
from typing import Optional, Dict, Any, List
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from .youtube_quota_manager import YouTubeQuotaManager, QuotaExceededException


logger = logging.getLogger(__name__)


class YouTubeAPIClient:
    """YouTube Data API v3 client with quota management and rate limiting.
    
    This class wraps the YouTube API client with intelligent quota tracking,
    exponential backoff, and error handling. Uses JSON file storage for quota
    data to avoid creating additional database schemas.
    
    Features:
    - Automatic quota tracking for all operations
    - Exponential backoff for rate limit errors
    - Quota-aware request validation
    - Detailed error handling and logging
    - Retry logic for transient failures
    
    Example:
        >>> client = YouTubeAPIClient(api_key='YOUR_KEY', quota_storage_path='quota.json')
        >>> 
        >>> # Search for videos (automatically tracks quota)
        >>> results = client.search_videos(query='python tutorial', max_results=5)
        >>> 
        >>> # Get video details
        >>> video = client.get_video_details('dQw4w9WgXcQ')
    """
    
    def __init__(
        self,
        api_key: str,
        quota_storage_path: str,
        daily_quota_limit: int = 10000,
        max_retries: int = 3,
        base_delay: float = 1.0
    ):
        """Initialize YouTube API Client.
        
        Args:
            api_key: YouTube Data API key
            quota_storage_path: Path to JSON file for quota storage
            daily_quota_limit: Daily quota limit in units (default: 10000)
            max_retries: Maximum number of retry attempts (default: 3)
            base_delay: Base delay for exponential backoff in seconds (default: 1.0)
        """
        if not api_key:
            raise ValueError("YouTube API key is required")
        
        self.api_key = api_key
        self.max_retries = max_retries
        self.base_delay = base_delay
        
        # Initialize YouTube API client
        self.youtube: Resource = build('youtube', 'v3', developerKey=api_key)
        
        # Initialize quota manager with JSON storage
        self.quota_manager = YouTubeQuotaManager(
            storage_path=quota_storage_path,
            daily_limit=daily_quota_limit
        )
        
        logger.info("YouTubeAPIClient initialized with quota management (JSON storage)")
    
    def _execute_with_quota(
        self,
        operation: str,
        request_callable
    ) -> Optional[Dict[str, Any]]:
        """Execute a YouTube API request with quota tracking.
        
        This method handles quota checking, request execution, retries,
        and quota consumption tracking.
        
        Args:
            operation: Operation name (e.g., 'search.list')
            request_callable: Callable that returns a YouTube API request object
            
        Returns:
            API response dictionary or None if quota exceeded
            
        Raises:
            HttpError: For non-recoverable API errors
            QuotaExceededException: If quota is exceeded
        """
        # Check quota before making request
        if not self.quota_manager.can_execute(operation):
            remaining = self.quota_manager.get_remaining_quota()
            cost = self.quota_manager.get_operation_cost(operation)
            raise QuotaExceededException(operation, cost, remaining)
        
        # Execute request with retry logic
        last_error = None
        for attempt in range(self.max_retries):
            try:
                # Get the request object and execute it
                request = request_callable()
                response = request.execute()
                
                # Consume quota on success
                self.quota_manager.consume(operation)
                
                return response
                
            except HttpError as e:
                last_error = e
                
                # Handle quota exceeded errors (403)
                if e.resp.status == 403:
                    error_details = e.error_details if hasattr(e, 'error_details') else []
                    for detail in error_details:
                        reason = detail.get('reason', '')
                        if reason in ['quotaExceeded', 'dailyLimitExceeded']:
                            logger.error(f"YouTube API quota exceeded: {e}")
                            raise QuotaExceededException(operation, 0, 0)
                    
                    # Other 403 errors (not quota-related)
                    logger.error(f"YouTube API permission error: {e}")
                    raise
                
                # Handle rate limiting (429)
                elif e.resp.status == 429:
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(
                        f"Rate limited on attempt {attempt + 1}/{self.max_retries}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    continue
                
                # Handle server errors (5xx) - retry with backoff
                elif 500 <= e.resp.status < 600:
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(
                        f"Server error {e.resp.status} on attempt {attempt + 1}/{self.max_retries}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    continue
                
                # Other errors - don't retry
                else:
                    logger.error(f"YouTube API error: {e}")
                    raise
            
            except Exception as e:
                logger.error(f"Unexpected error executing YouTube API request: {e}")
                raise
        
        # All retries exhausted
        if last_error:
            logger.error(f"All {self.max_retries} retry attempts failed")
            raise last_error
        
        return None
    
    def search_videos(
        self,
        query: str,
        max_results: int = 5,
        video_duration: str = 'any',
        order: str = 'relevance',
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search for YouTube videos.
        
        Args:
            query: Search query
            max_results: Maximum number of results (default: 5)
            video_duration: Video duration filter ('any', 'short', 'medium', 'long')
            order: Sort order ('relevance', 'date', 'viewCount', 'rating')
            **kwargs: Additional search parameters
            
        Returns:
            List of video items from search results
        """
        def make_request():
            return self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                videoDuration=video_duration,
                order=order,
                **kwargs
            )
        
        response = self._execute_with_quota('search.list', make_request)
        
        if response:
            return response.get('items', [])
        return []
    
    def get_video_details(
        self,
        video_id: str,
        parts: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get details for a specific video.
        
        Args:
            video_id: YouTube video ID
            parts: List of parts to retrieve (default: ['snippet', 'statistics', 'contentDetails'])
            
        Returns:
            Video details dictionary or None if not found
        """
        if parts is None:
            parts = ['snippet', 'statistics', 'contentDetails']
        
        parts_str = ','.join(parts)
        
        def make_request():
            return self.youtube.videos().list(
                part=parts_str,
                id=video_id
            )
        
        response = self._execute_with_quota('videos.list', make_request)
        
        if response and response.get('items'):
            return response['items'][0]
        return None
    
    def get_videos_batch(
        self,
        video_ids: List[str],
        parts: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get details for multiple videos in a single request.
        
        Args:
            video_ids: List of YouTube video IDs (max 50)
            parts: List of parts to retrieve (default: ['snippet', 'statistics', 'contentDetails'])
            
        Returns:
            List of video details dictionaries
        """
        if not video_ids:
            return []
        
        # YouTube API limits to 50 IDs per request
        if len(video_ids) > 50:
            logger.warning(f"Too many video IDs ({len(video_ids)}), limiting to 50")
            video_ids = video_ids[:50]
        
        if parts is None:
            parts = ['snippet', 'statistics', 'contentDetails']
        
        parts_str = ','.join(parts)
        ids_str = ','.join(video_ids)
        
        def make_request():
            return self.youtube.videos().list(
                part=parts_str,
                id=ids_str
            )
        
        response = self._execute_with_quota('videos.list', make_request)
        
        if response:
            return response.get('items', [])
        return []
    
    def get_channel_details(
        self,
        channel_id: str,
        parts: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get details for a specific channel.
        
        Args:
            channel_id: YouTube channel ID
            parts: List of parts to retrieve (default: ['snippet', 'statistics', 'contentDetails'])
            
        Returns:
            Channel details dictionary or None if not found
        """
        if parts is None:
            parts = ['snippet', 'statistics', 'contentDetails']
        
        parts_str = ','.join(parts)
        
        def make_request():
            return self.youtube.channels().list(
                part=parts_str,
                id=channel_id
            )
        
        response = self._execute_with_quota('channels.list', make_request)
        
        if response and response.get('items'):
            return response['items'][0]
        return None
    
    def get_playlist_items(
        self,
        playlist_id: str,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """Get items from a playlist.
        
        Args:
            playlist_id: YouTube playlist ID
            max_results: Maximum number of results (default: 50, max: 50)
            
        Returns:
            List of playlist items
        """
        if max_results > 50:
            logger.warning(f"Max results limited to 50 (requested: {max_results})")
            max_results = 50
        
        def make_request():
            return self.youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=playlist_id,
                maxResults=max_results
            )
        
        response = self._execute_with_quota('playlistItems.list', make_request)
        
        if response:
            return response.get('items', [])
        return []
    
    def get_comment_threads(
        self,
        video_id: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Get comment threads for a video.
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum number of results (default: 20)
            
        Returns:
            List of comment thread items
        """
        def make_request():
            return self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=max_results,
                textFormat='plainText'
            )
        
        response = self._execute_with_quota('commentThreads.list', make_request)
        
        if response:
            return response.get('items', [])
        return []
    
    def get_quota_usage(self) -> Dict[str, Any]:
        """Get current quota usage statistics.
        
        Returns:
            Dictionary with quota usage information
        """
        usage = self.quota_manager.get_usage()
        return {
            'date': usage.date,
            'total_used': usage.total_used,
            'remaining': usage.remaining,
            'percentage_used': self.quota_manager.get_usage_percentage(),
            'daily_limit': self.quota_manager.daily_limit,
            'operations': usage.operations
        }
    
    def can_execute_operation(self, operation: str, count: int = 1) -> bool:
        """Check if an operation can be executed without exceeding quota.
        
        Args:
            operation: Operation name (e.g., 'search.list')
            count: Number of times to execute (default: 1)
            
        Returns:
            True if operation can be executed
        """
        return self.quota_manager.can_execute(operation, count)
    
    def get_remaining_quota(self) -> int:
        """Get remaining quota units.
        
        Returns:
            Remaining quota units
        """
        return self.quota_manager.get_remaining_quota()


__all__ = ['YouTubeAPIClient']
