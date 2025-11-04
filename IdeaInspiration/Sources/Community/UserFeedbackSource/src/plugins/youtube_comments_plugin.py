"""YouTube comments plugin for scraping own channel feedback."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from . import CommunitySourcePlugin, IdeaInspiration


class YouTubeCommentsPlugin(CommunitySourcePlugin):
    """Plugin for scraping comments from own YouTube channel.
    
    Uses YouTube Data API v3 to fetch comments from own channel videos.
    """
    
    def __init__(self, config):
        """Initialize YouTube comments plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        # Validate API key
        if not config.youtube_api_key:
            raise ValueError("YouTube API key is required. Set YOUTUBE_API_KEY in .env file.")
        
        # Initialize YouTube API client
        self._init_youtube_client()
    
    def _init_youtube_client(self):
        """Initialize YouTube API client."""
        try:
            from googleapiclient.discovery import build
            self.youtube = build('youtube', 'v3', developerKey=self.config.youtube_api_key)
        except ImportError:
            raise ValueError("google-api-python-client is not installed. "
                           "Install with: pip install google-api-python-client")
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "user_feedback"
    
    def scrape(
        self,
        channel_id: Optional[str] = None,
        max_videos: int = 10,
        max_comments_per_video: Optional[int] = None
    ) -> List[IdeaInspiration]:
        """Scrape comments from YouTube channel.
        
        Args:
            channel_id: YouTube channel ID (uses config if not provided)
            max_videos: Maximum number of videos to fetch comments from
            max_comments_per_video: Maximum comments per video (uses config if not provided)
            
        Returns:
            List of IdeaInspiration objects
        """
        # Use config values if not provided
        if channel_id is None:
            channel_id = self.config.youtube_channel_id
            if not channel_id:
                print("Error: No channel ID provided and none configured")
                return []
        
        if max_comments_per_video is None:
            max_comments_per_video = self.config.max_comments
        
        signals = []
        
        # Get recent videos from channel
        video_ids = self._get_channel_videos(channel_id, max_videos)
        
        if not video_ids:
            print(f"No videos found for channel: {channel_id}")
            return signals
        
        print(f"Found {len(video_ids)} videos from channel")
        
        # Fetch comments for each video
        for i, video_id in enumerate(video_ids, 1):
            print(f"  [{i}/{len(video_ids)}] Fetching comments for video: {video_id}")
            
            comments_data = self._get_video_comments(video_id, max_comments_per_video)
            
            for comment_data in comments_data:
                # Transform to IdeaInspiration
                idea = self._transform_comment_to_idea(comment_data)
                signals.append(idea)
            
            print(f"    Found {len(comments_data)} comments")
        
        return signals
    
    def _get_channel_videos(self, channel_id: str, max_results: int) -> List[str]:
        """Get recent videos from a channel.
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to fetch
            
        Returns:
            List of video IDs
        """
        try:
            # Search for videos from the channel, ordered by date
            request = self.youtube.search().list(
                part='id',
                channelId=channel_id,
                maxResults=max_results,
                order='date',
                type='video'
            )
            response = request.execute()
            
            video_ids = []
            for item in response.get('items', []):
                if item['id']['kind'] == 'youtube#video':
                    video_ids.append(item['id']['videoId'])
            
            return video_ids
            
        except Exception as e:
            print(f"Error fetching channel videos: {e}")
            return []
    
    def _get_video_comments(
        self,
        video_id: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Get comments for a video.
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum number of comments to fetch
            
        Returns:
            List of community signal dictionaries
        """
        comments = []
        
        try:
            # Fetch comment threads
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=max_results,
                order='relevance',  # Get most relevant comments first
                textFormat='plainText'
            )
            response = request.execute()
            
            for item in response.get('items', []):
                snippet = item['snippet']['topLevelComment']['snippet']
                
                # Parse timestamp
                published_at = snippet.get('publishedAt', '')
                try:
                    timestamp = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    timestamp = datetime.utcnow()
                
                # Create community signal (minimal format, will be processed by CommunityProcessor)
                comment_data = {
                    'source': 'user_feedback',
                    'source_id': item['id'],
                    'text': snippet.get('textDisplay', ''),
                    'author': snippet.get('authorDisplayName', 'Unknown'),
                    'platform': 'youtube',
                    'parent_content': video_id,
                    'upvotes': snippet.get('likeCount', 0),
                    'replies': item['snippet'].get('totalReplyCount', 0),
                    'timestamp': timestamp,
                    'category': None  # Could be determined from video metadata
                }
                
                comments.append(comment_data)
            
        except Exception as e:
            print(f"Error fetching comments for video {video_id}: {e}")
        
        return comments
    
    def _transform_comment_to_idea(self, comment_data: Dict[str, Any]) -> IdeaInspiration:
        """Transform YouTube comment data to IdeaInspiration object.
        
        Args:
            comment_data: Comment data dictionary
            
        Returns:
            IdeaInspiration object
        """
        author = comment_data.get('author', 'Unknown')
        text = comment_data.get('text', '')
        video_id = comment_data.get('parent_content', '')
        tags = self.format_tags(['youtube', 'comment', 'feedback', 'user_feedback'])
        
        # Build metadata with string values
        metadata = {
            'comment_id': comment_data.get('source_id', ''),
            'author': author,
            'platform': 'youtube',
            'video_id': video_id,
            'upvotes': str(comment_data.get('upvotes', 0)),
            'replies': str(comment_data.get('replies', 0)),
            'timestamp': comment_data.get('timestamp', ''),
            'comment_type': 'user_feedback',
        }
        
        # Build description
        description = f"YouTube comment by {author} on video {video_id}"
        
        # Create IdeaInspiration using from_text factory method
        idea = IdeaInspiration.from_text(
            title=f"Comment by {author}",
            description=description,
            text_content=text,
            keywords=tags,
            metadata=metadata,
            source_id=comment_data.get('source_id', ''),
            source_url=f"https://www.youtube.com/watch?v={video_id}",
            source_platform="user_feedback",
            source_created_by=author,
            source_created_at=comment_data.get('timestamp', '')
        )
        
        return idea
