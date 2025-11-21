"""YouTube data mapper for transforming YouTube API responses.

This module provides mapping functionality to convert YouTube API responses
to standardized VideoMetadata format and YouTubeVideo/Channel/SearchResult models.
"""

import re
from datetime import datetime
from typing import Dict, Any, Optional
from dateutil import parser as date_parser

from ..schemas import YouTubeVideo, YouTubeChannel, YouTubeSearchResult


class YouTubeMapper:
    """Mapper for YouTube API data to internal data models.
    
    Transforms raw YouTube API responses into structured data models
    (YouTubeVideo, YouTubeChannel, YouTubeSearchResult) and provides
    mapping to the standardized VideoMetadata format.
    
    Example:
        >>> mapper = YouTubeMapper()
        >>> api_response = {...}  # YouTube API response
        >>> video = mapper.parse_video(api_response)
        >>> metadata = mapper.to_video_metadata(video)
    """
    
    def parse_video(self, api_response: Dict[str, Any]) -> YouTubeVideo:
        """Parse YouTube API video response to YouTubeVideo model.
        
        Args:
            api_response: Raw YouTube API videos.list response item
            
        Returns:
            YouTubeVideo instance with parsed data
            
        Example:
            >>> response = {
            ...     'id': 'abc123',
            ...     'snippet': {'title': 'My Video', ...},
            ...     'contentDetails': {'duration': 'PT5M30S'},
            ...     'statistics': {'viewCount': '1000', ...}
            ... }
            >>> video = mapper.parse_video(response)
        """
        snippet = api_response.get('snippet', {})
        content_details = api_response.get('contentDetails', {})
        statistics = api_response.get('statistics', {})
        status = api_response.get('status', {})
        
        # Parse video ID
        video_id = api_response.get('id', '')
        if isinstance(video_id, dict):
            video_id = video_id.get('videoId', '')
        
        # Parse timestamps
        published_at = self._parse_datetime(snippet.get('publishedAt'))
        
        # Parse duration
        duration_str = content_details.get('duration', 'PT0S')
        duration = self._parse_duration(duration_str)
        
        # Parse statistics (all returned as strings)
        view_count = int(statistics.get('viewCount', 0) or 0)
        like_count = int(statistics.get('likeCount', 0) or 0)
        comment_count = int(statistics.get('commentCount', 0) or 0)
        
        # Extract thumbnails
        thumbnails = self._extract_thumbnails(snippet.get('thumbnails', {}))
        
        # Detect if video is a Short (duration < 61 seconds and vertical aspect ratio)
        is_short = self._detect_short(duration, content_details)
        
        # Detect live stream
        is_live = snippet.get('liveBroadcastContent') == 'live'
        is_upcoming = snippet.get('liveBroadcastContent') == 'upcoming'
        
        # Caption availability
        caption_available = content_details.get('caption', 'false') == 'true'
        
        # Made for kids
        made_for_kids = status.get('madeForKids', False)
        
        return YouTubeVideo(
            video_id=video_id,
            title=snippet.get('title', ''),
            description=snippet.get('description', ''),
            channel_id=snippet.get('channelId', ''),
            channel_title=snippet.get('channelTitle', ''),
            published_at=published_at,
            duration=duration,
            view_count=view_count,
            like_count=like_count,
            comment_count=comment_count,
            tags=snippet.get('tags', []),
            category_id=snippet.get('categoryId', ''),
            thumbnails=thumbnails,
            is_short=is_short,
            is_live=is_live,
            is_upcoming=is_upcoming,
            language=snippet.get('defaultLanguage', '') or snippet.get('defaultAudioLanguage', ''),
            caption_available=caption_available,
            made_for_kids=made_for_kids,
            metadata={
                'definition': content_details.get('definition', ''),
                'dimension': content_details.get('dimension', ''),
                'projection': content_details.get('projection', ''),
                'licensed_content': content_details.get('licensedContent', False),
            }
        )
    
    def parse_channel(self, api_response: Dict[str, Any]) -> YouTubeChannel:
        """Parse YouTube API channel response to YouTubeChannel model.
        
        Args:
            api_response: Raw YouTube API channels.list response item
            
        Returns:
            YouTubeChannel instance with parsed data
        """
        snippet = api_response.get('snippet', {})
        statistics = api_response.get('statistics', {})
        content_details = api_response.get('contentDetails', {})
        
        # Parse timestamps
        published_at = self._parse_datetime(snippet.get('publishedAt'))
        
        # Parse statistics
        subscriber_count = int(statistics.get('subscriberCount', 0) or 0)
        video_count = int(statistics.get('videoCount', 0) or 0)
        view_count = int(statistics.get('viewCount', 0) or 0)
        
        # Extract thumbnails
        thumbnails = self._extract_thumbnails(snippet.get('thumbnails', {}))
        
        # Get uploads playlist
        related_playlists = content_details.get('relatedPlaylists', {})
        uploads_playlist_id = related_playlists.get('uploads', '')
        
        return YouTubeChannel(
            channel_id=api_response.get('id', ''),
            title=snippet.get('title', ''),
            description=snippet.get('description', ''),
            custom_url=snippet.get('customUrl', ''),
            published_at=published_at,
            subscriber_count=subscriber_count,
            video_count=video_count,
            view_count=view_count,
            thumbnails=thumbnails,
            uploads_playlist_id=uploads_playlist_id,
            country=snippet.get('country', ''),
            metadata={
                'hidden_subscriber_count': statistics.get('hiddenSubscriberCount', False),
            }
        )
    
    def parse_search_result(self, api_response: Dict[str, Any]) -> YouTubeSearchResult:
        """Parse YouTube API search result to YouTubeSearchResult model.
        
        Args:
            api_response: Raw YouTube API search.list response item
            
        Returns:
            YouTubeSearchResult instance with parsed data
        """
        snippet = api_response.get('snippet', {})
        video_id = api_response.get('id', {}).get('videoId', '')
        
        # Parse timestamp
        published_at = self._parse_datetime(snippet.get('publishedAt'))
        
        # Extract thumbnails
        thumbnails = self._extract_thumbnails(snippet.get('thumbnails', {}))
        
        return YouTubeSearchResult(
            video_id=video_id,
            title=snippet.get('title', ''),
            description=snippet.get('description', ''),
            channel_id=snippet.get('channelId', ''),
            channel_title=snippet.get('channelTitle', ''),
            published_at=published_at,
            thumbnails=thumbnails,
        )
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse YouTube ISO 8601 duration to seconds.
        
        YouTube uses ISO 8601 duration format (e.g., PT1H2M3S for 1:02:03).
        
        Args:
            duration_str: ISO 8601 duration string (e.g., 'PT5M30S')
            
        Returns:
            Duration in seconds
            
        Example:
            >>> mapper._parse_duration('PT1H2M3S')
            3723
            >>> mapper._parse_duration('PT5M30S')
            330
            >>> mapper._parse_duration('PT45S')
            45
        """
        if not duration_str:
            return 0
        
        # Parse ISO 8601 duration: PT1H2M3S
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def _detect_short(self, duration: int, content_details: Dict[str, Any]) -> bool:
        """Detect if video is a YouTube Short.
        
        YouTube Shorts are vertical videos under 61 seconds.
        
        Args:
            duration: Video duration in seconds
            content_details: Content details from API response
            
        Returns:
            True if video is likely a Short, False otherwise
        """
        # Shorts are typically under 61 seconds
        if duration > 61:
            return False
        
        # Check dimension (2d = standard, 3d = 3D video)
        # Shorts are always 2d
        dimension = content_details.get('dimension', '2d')
        if dimension != '2d':
            return False
        
        # Additional heuristic: very short duration is likely a Short
        return duration <= 60
    
    def _extract_thumbnails(self, thumbnails_dict: Dict[str, Any]) -> Dict[str, str]:
        """Extract thumbnail URLs from YouTube thumbnails object.
        
        Args:
            thumbnails_dict: YouTube thumbnails object with different qualities
            
        Returns:
            Dictionary mapping quality names to thumbnail URLs
        """
        result = {}
        
        for quality in ['default', 'medium', 'high', 'standard', 'maxres']:
            if quality in thumbnails_dict:
                result[quality] = thumbnails_dict[quality].get('url', '')
        
        return result
    
    def _parse_datetime(self, datetime_str: Optional[str]) -> Optional[datetime]:
        """Parse YouTube datetime string to datetime object.
        
        Args:
            datetime_str: ISO 8601 datetime string
            
        Returns:
            Parsed datetime object or None if parsing fails
        """
        if not datetime_str:
            return None
        
        try:
            return date_parser.parse(datetime_str)
        except (ValueError, TypeError):
            return None
    
    def to_video_metadata_dict(self, youtube_video: YouTubeVideo) -> Dict[str, Any]:
        """Convert YouTubeVideo to VideoMetadata dictionary.
        
        This creates a dictionary that can be used to initialize
        the standardized VideoMetadata Pydantic model.
        
        Args:
            youtube_video: YouTubeVideo instance
            
        Returns:
            Dictionary compatible with VideoMetadata schema
        """
        # Get best thumbnail
        thumbnail_url = (
            youtube_video.thumbnails.get('maxres') or
            youtube_video.thumbnails.get('high') or
            youtube_video.thumbnails.get('medium') or
            youtube_video.thumbnails.get('default') or
            ''
        )
        
        return {
            'platform': 'youtube',
            'video_id': youtube_video.video_id,
            'url': f'https://www.youtube.com/watch?v={youtube_video.video_id}',
            'title': youtube_video.title,
            'description': youtube_video.description,
            'duration_seconds': youtube_video.duration,
            'published_at': youtube_video.published_at,
            'channel_id': youtube_video.channel_id,
            'channel_name': youtube_video.channel_title,
            'channel_url': f'https://www.youtube.com/channel/{youtube_video.channel_id}' if youtube_video.channel_id else None,
            'view_count': youtube_video.view_count,
            'like_count': youtube_video.like_count,
            'comment_count': youtube_video.comment_count,
            'share_count': None,  # Not provided by YouTube API
            'category': youtube_video.category_id,
            'tags': youtube_video.tags,
            'is_live': youtube_video.is_live,
            'is_short': youtube_video.is_short,
            'thumbnail_url': thumbnail_url,
            'preview_url': None,
            'quality': youtube_video.metadata.get('definition', '').upper(),
            'fps': None,
            'resolution': None,
            # Additional YouTube-specific metadata
            'metadata': {
                'youtube': {
                    'language': youtube_video.language,
                    'caption_available': youtube_video.caption_available,
                    'made_for_kids': youtube_video.made_for_kids,
                    'is_upcoming': youtube_video.is_upcoming,
                    **youtube_video.metadata
                }
            }
        }
