"""YouTube video data models using dataclasses.

This module defines YouTube-specific data structures for videos, channels,
and search results. These models represent raw YouTube API data before
mapping to the standardized VideoMetadata schema.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class YouTubeVideo:
    """YouTube video data model.
    
    Represents a YouTube video with all its metadata from the API.
    This is the YouTube-specific representation before mapping to
    the standardized VideoMetadata schema.
    
    Attributes:
        video_id: YouTube video ID (e.g., 'dQw4w9WgXcQ')
        title: Video title
        description: Video description
        channel_id: Channel ID that published the video
        channel_title: Channel name
        published_at: Publication timestamp
        duration: Video duration in seconds
        view_count: Number of views
        like_count: Number of likes
        comment_count: Number of comments
        tags: List of video tags
        category_id: YouTube category ID
        thumbnails: Dictionary of thumbnail URLs by quality
        is_short: Whether this is a YouTube Short
        is_live: Whether this is a live stream
        is_upcoming: Whether this is an upcoming premiere
        language: Video language code
        caption_available: Whether captions are available
        made_for_kids: Whether video is made for kids
        metadata: Additional platform-specific metadata
        
    Example:
        >>> video = YouTubeVideo(
        ...     video_id="abc123",
        ...     title="Python Tutorial",
        ...     description="Learn Python",
        ...     channel_id="UC...",
        ...     channel_title="Coding Channel",
        ...     published_at=datetime.now(),
        ...     duration=600
        ... )
    """
    
    # Core identifiers
    video_id: str
    title: str
    description: str = ""
    
    # Channel information
    channel_id: str = ""
    channel_title: str = ""
    
    # Timestamps
    published_at: Optional[datetime] = None
    
    # Video details
    duration: int = 0  # seconds
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    
    # Content classification
    tags: List[str] = field(default_factory=list)
    category_id: str = ""
    
    # Media assets
    thumbnails: Dict[str, str] = field(default_factory=dict)
    
    # Video type flags
    is_short: bool = False
    is_live: bool = False
    is_upcoming: bool = False
    
    # Additional metadata
    language: str = ""
    caption_available: bool = False
    made_for_kids: bool = False
    
    # Platform-specific metadata (JSON-serializable)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary with all video data
        """
        return {
            'video_id': self.video_id,
            'title': self.title,
            'description': self.description,
            'channel_id': self.channel_id,
            'channel_title': self.channel_title,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'duration': self.duration,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'tags': self.tags,
            'category_id': self.category_id,
            'thumbnails': self.thumbnails,
            'is_short': self.is_short,
            'is_live': self.is_live,
            'is_upcoming': self.is_upcoming,
            'language': self.language,
            'caption_available': self.caption_available,
            'made_for_kids': self.made_for_kids,
            'metadata': self.metadata,
        }


@dataclass
class YouTubeChannel:
    """YouTube channel data model.
    
    Represents a YouTube channel with metadata from the API.
    
    Attributes:
        channel_id: YouTube channel ID
        title: Channel name
        description: Channel description
        custom_url: Custom channel URL (e.g., @channelname)
        published_at: Channel creation date
        subscriber_count: Number of subscribers
        video_count: Total number of videos
        view_count: Total channel views
        thumbnails: Channel thumbnail URLs
        uploads_playlist_id: ID of uploads playlist
        country: Channel country
        metadata: Additional platform-specific metadata
        
    Example:
        >>> channel = YouTubeChannel(
        ...     channel_id="UC...",
        ...     title="Coding Channel",
        ...     description="Learn to code",
        ...     subscriber_count=100000
        ... )
    """
    
    # Core identifiers
    channel_id: str
    title: str
    description: str = ""
    custom_url: str = ""
    
    # Timestamps
    published_at: Optional[datetime] = None
    
    # Statistics
    subscriber_count: int = 0
    video_count: int = 0
    view_count: int = 0
    
    # Media
    thumbnails: Dict[str, str] = field(default_factory=dict)
    
    # Channel details
    uploads_playlist_id: str = ""
    country: str = ""
    
    # Platform-specific metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary with all channel data
        """
        return {
            'channel_id': self.channel_id,
            'title': self.title,
            'description': self.description,
            'custom_url': self.custom_url,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'subscriber_count': self.subscriber_count,
            'video_count': self.video_count,
            'view_count': self.view_count,
            'thumbnails': self.thumbnails,
            'uploads_playlist_id': self.uploads_playlist_id,
            'country': self.country,
            'metadata': self.metadata,
        }


@dataclass
class YouTubeSearchResult:
    """YouTube search result data model.
    
    Represents a video from YouTube search results.
    Contains limited information compared to full video details.
    
    Attributes:
        video_id: YouTube video ID
        title: Video title
        description: Video description (snippet)
        channel_id: Channel ID
        channel_title: Channel name
        published_at: Publication timestamp
        thumbnails: Thumbnail URLs
        
    Example:
        >>> result = YouTubeSearchResult(
        ...     video_id="abc123",
        ...     title="Python Tutorial",
        ...     description="Learn Python basics",
        ...     channel_id="UC...",
        ...     channel_title="Coding Channel"
        ... )
    """
    
    video_id: str
    title: str
    description: str = ""
    channel_id: str = ""
    channel_title: str = ""
    published_at: Optional[datetime] = None
    thumbnails: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary with all search result data
        """
        return {
            'video_id': self.video_id,
            'title': self.title,
            'description': self.description,
            'channel_id': self.channel_id,
            'channel_title': self.channel_title,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'thumbnails': self.thumbnails,
        }
