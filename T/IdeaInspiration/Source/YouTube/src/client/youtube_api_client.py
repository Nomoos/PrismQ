"""YouTube Data API v3 client with rate limiting and quota management.

This module provides a client for interacting with the YouTube Data API v3,
including automatic rate limiting, quota tracking, retry logic, and error handling.
"""

import time
from typing import Dict, Any, Optional, List
import requests

from .rate_limiter import RateLimiter
from ..exceptions import YouTubeAPIError, YouTubeQuotaExceededError


class YouTubeAPIClient:
    """YouTube Data API v3 client with rate limiting.
    
    Handles API authentication, rate limiting, quota management, request retries,
    and error handling for YouTube Data API v3 interactions.
    
    API Quota Costs:
    - search: 100 units
    - videos.list: 1 unit per video (up to 50 videos)
    - channels.list: 1 unit per channel
    - playlistItems.list: 1 unit
    
    Attributes:
        api_key: YouTube Data API key
        rate_limiter: RateLimiter instance for quota management
        session: Requests session for connection pooling
        
    Example:
        >>> client = YouTubeAPIClient(api_key="YOUR_API_KEY")
        >>> results = client.search(query="python tutorial", max_results=10)
        >>> video_ids = [item['id']['videoId'] for item in results['items']]
        >>> details = client.get_video_details(video_ids)
    """
    
    BASE_URL = 'https://www.googleapis.com/youtube/v3'
    
    # API quota costs for different operations
    QUOTA_COSTS = {
        'search': 100,
        'videos': 1,
        'channels': 1,
        'playlistItems': 1,
    }
    
    def __init__(
        self,
        api_key: str,
        rate_limit: int = 100,
        quota_per_day: int = 10000,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize YouTube API client.
        
        Args:
            api_key: YouTube Data API key
            rate_limit: Requests per minute (default: 100)
            quota_per_day: Daily quota limit in units (default: 10000)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
            
        Raises:
            ValueError: If api_key is empty
        """
        if not api_key:
            raise ValueError("YouTube API key is required")
        
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            requests_per_minute=rate_limit,
            quota_per_day=quota_per_day
        )
        
        # Create session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'PrismQ-IdeaInspiration/1.0'
        })
    
    def search(
        self,
        query: Optional[str] = None,
        channel_id: Optional[str] = None,
        max_results: int = 10,
        order: str = 'relevance',
        published_after: Optional[str] = None,
        published_before: Optional[str] = None,
        video_duration: Optional[str] = None,
        video_type: Optional[str] = None,
        page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for videos on YouTube.
        
        Args:
            query: Search query string
            channel_id: Filter by channel ID
            max_results: Maximum results to return (1-50, default: 10)
            order: Sort order (date, rating, relevance, title, viewCount)
            published_after: RFC 3339 timestamp (e.g., '2024-01-01T00:00:00Z')
            published_before: RFC 3339 timestamp
            video_duration: any, short (<4min), medium (4-20min), long (>20min)
            video_type: any, episode, movie
            page_token: Token for pagination
            
        Returns:
            YouTube API search response with items and pagination info
            
        Raises:
            YouTubeAPIError: If API request fails
            YouTubeQuotaExceededError: If quota would be exceeded
        """
        params = {
            'part': 'snippet',
            'type': 'video',
            'maxResults': min(max_results, 50),
            'order': order,
            'key': self.api_key
        }
        
        if query:
            params['q'] = query
        if channel_id:
            params['channelId'] = channel_id
        if published_after:
            params['publishedAfter'] = published_after
        if published_before:
            params['publishedBefore'] = published_before
        if video_duration:
            params['videoDuration'] = video_duration
        if video_type:
            params['videoType'] = video_type
        if page_token:
            params['pageToken'] = page_token
        
        return self._make_request('search', params, quota_cost=self.QUOTA_COSTS['search'])
    
    def get_video_details(self, video_ids: List[str]) -> Dict[str, Any]:
        """Get detailed information for videos.
        
        Args:
            video_ids: List of video IDs (max 50 per request)
            
        Returns:
            YouTube API videos response with detailed video information
            
        Raises:
            YouTubeAPIError: If API request fails
            YouTubeQuotaExceededError: If quota would be exceeded
            ValueError: If video_ids is empty or too long
        """
        if not video_ids:
            raise ValueError("video_ids cannot be empty")
        
        if len(video_ids) > 50:
            raise ValueError("Maximum 50 video IDs per request")
        
        params = {
            'part': 'snippet,contentDetails,statistics,status',
            'id': ','.join(video_ids),
            'key': self.api_key
        }
        
        return self._make_request('videos', params, quota_cost=self.QUOTA_COSTS['videos'])
    
    def get_channel_details(self, channel_ids: List[str]) -> Dict[str, Any]:
        """Get information about YouTube channels.
        
        Args:
            channel_ids: List of channel IDs
            
        Returns:
            YouTube API channels response with channel information
            
        Raises:
            YouTubeAPIError: If API request fails
            YouTubeQuotaExceededError: If quota would be exceeded
            ValueError: If channel_ids is empty
        """
        if not channel_ids:
            raise ValueError("channel_ids cannot be empty")
        
        params = {
            'part': 'snippet,statistics,contentDetails',
            'id': ','.join(channel_ids),
            'key': self.api_key
        }
        
        return self._make_request('channels', params, quota_cost=self.QUOTA_COSTS['channels'])
    
    def get_playlist_items(
        self,
        playlist_id: str,
        max_results: int = 50,
        page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get items from a YouTube playlist.
        
        Useful for getting all videos from a channel's uploads playlist.
        
        Args:
            playlist_id: YouTube playlist ID
            max_results: Maximum results to return (1-50, default: 50)
            page_token: Token for pagination
            
        Returns:
            YouTube API playlistItems response
            
        Raises:
            YouTubeAPIError: If API request fails
            YouTubeQuotaExceededError: If quota would be exceeded
        """
        params = {
            'part': 'snippet,contentDetails',
            'playlistId': playlist_id,
            'maxResults': min(max_results, 50),
            'key': self.api_key
        }
        
        if page_token:
            params['pageToken'] = page_token
        
        return self._make_request(
            'playlistItems',
            params,
            quota_cost=self.QUOTA_COSTS['playlistItems']
        )
    
    def get_quota_usage(self) -> int:
        """Get current quota usage for the day.
        
        Returns:
            Current quota usage in units
        """
        return self.rate_limiter.current_quota_usage
    
    def get_remaining_quota(self) -> int:
        """Get remaining quota for the day.
        
        Returns:
            Remaining quota in units
        """
        return self.rate_limiter.get_remaining_quota()
    
    def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        quota_cost: int = 1
    ) -> Dict[str, Any]:
        """Make API request with rate limiting and retries.
        
        Args:
            endpoint: API endpoint (search, videos, channels, etc.)
            params: Query parameters
            quota_cost: Quota cost of this request
            
        Returns:
            API response JSON
            
        Raises:
            YouTubeAPIError: On API errors
            YouTubeQuotaExceededError: If quota would be exceeded
        """
        url = f'{self.BASE_URL}/{endpoint}'
        
        # Check quota before making request
        if not self.rate_limiter.can_make_request(quota_cost):
            raise YouTubeQuotaExceededError(
                f"Insufficient quota for request (cost: {quota_cost}, "
                f"remaining: {self.rate_limiter.get_remaining_quota()})",
                current_usage=self.rate_limiter.current_quota_usage,
                daily_limit=self.rate_limiter.quota_per_day
            )
        
        for attempt in range(self.max_retries):
            try:
                # Wait for rate limit
                self.rate_limiter.wait_if_needed()
                
                # Make request
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout
                )
                
                # Check for HTTP errors
                if response.status_code == 403:
                    error_data = response.json().get('error', {})
                    error_reason = error_data.get('errors', [{}])[0].get('reason', '')
                    
                    if error_reason == 'quotaExceeded':
                        raise YouTubeQuotaExceededError(
                            "YouTube API quota exceeded",
                            current_usage=self.rate_limiter.current_quota_usage,
                            daily_limit=self.rate_limiter.quota_per_day
                        )
                
                response.raise_for_status()
                
                # Track quota usage
                self.rate_limiter.track_request(quota_cost)
                
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                if attempt == self.max_retries - 1:
                    raise YouTubeAPIError(
                        f"HTTP error: {str(e)}",
                        status_code=response.status_code if 'response' in locals() else None,
                        response=response.json() if 'response' in locals() else None
                    )
                
                # Exponential backoff
                time.sleep(2 ** attempt)
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise YouTubeAPIError(f"Request failed: {str(e)}")
                
                # Exponential backoff
                time.sleep(2 ** attempt)
        
        raise YouTubeAPIError("Max retries exceeded")
    
    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
