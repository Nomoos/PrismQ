"""TikTok Trending source plugin for scraping trending videos.

This plugin uses yt-dlp to scrape TikTok trending videos with comprehensive
metadata extraction.
"""

import json
import subprocess
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from . import SourcePlugin, IdeaInspiration


class TikTokTrendingPlugin(SourcePlugin):
    """Plugin for scraping ideas from TikTok trending page using yt-dlp."""
    
    def __init__(self, config):
        """Initialize TikTok trending plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        
        # Check if yt-dlp is available
        if not self._check_ytdlp():
            raise ValueError("yt-dlp is not installed. Install with: pip install yt-dlp")
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "tiktok_trending"
    
    def _check_ytdlp(self) -> bool:
        """Check if yt-dlp is installed.
        
        Returns:
            True if yt-dlp is available
        """
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def scrape(self, max_videos: Optional[int] = None) -> List[IdeaInspiration]:
        """Scrape trending TikTok videos.
        
        Args:
            max_videos: Number of videos to scrape (optional, uses config if not provided)
        
        Returns:
            List of IdeaInspiration objects
        """
        ideas = []
        
        if max_videos is None:
            max_videos = getattr(self.config, 'tiktok_trending_max', 10)
        
        print(f"Scraping trending TikTok videos (max: {max_videos})...")
        
        # Note: TikTok trending scraping is challenging without official API
        # This is a placeholder implementation showing the architecture
        # Real implementation would require a working TikTok scraping library
        
        print("⚠️  TikTok trending scraping requires additional setup:")
        print("   - Consider using TikTokApi (unofficial)")
        print("   - Or playwright-based scraping")
        print("   - Respect TikTok's ToS and rate limits")
        
        # Placeholder: Would normally call TikTok API or scraping library here
        # Example structure for when implemented:
        # videos = self._fetch_trending_videos(max_videos)
        # for video in videos:
        #     idea = self._video_to_idea(video)
        #     ideas.append(idea)
        
        return ideas
    
    def _fetch_trending_videos(self, max_videos: int) -> List[Dict[str, Any]]:
        """Fetch trending videos from TikTok.
        
        This is a placeholder for the actual implementation.
        Real implementation would use TikTokApi or similar library.
        
        Args:
            max_videos: Maximum number of videos to fetch
            
        Returns:
            List of video data dictionaries
        """
        # Placeholder for actual TikTok API integration
        # Example using TikTokApi (unofficial):
        # from TikTokApi import TikTokApi
        # api = TikTokApi()
        # trending = api.trending.videos(count=max_videos)
        # return [video.as_dict for video in trending]
        
        return []
    
    def _video_to_idea(self, video_data: Dict[str, Any]) -> IdeaInspiration:
        """Convert TikTok video data to IdeaInspiration object.
        
        Args:
            video_data: TikTok video data
            
        Returns:
            IdeaInspiration object
        """
        return self.transform_video_to_idea(video_data)
    
    def transform_video_to_idea(self, video_data: Dict[str, Any]) -> Optional[IdeaInspiration]:
        """Transform TikTok video data to IdeaInspiration object.
        
        Args:
            video_data: TikTok video data
            
        Returns:
            IdeaInspiration object or None
        """
        try:
            # Extract basic info
            video_id = video_data.get('id', '')
            title = video_data.get('desc', '') or video_data.get('title', 'Untitled')
            description = video_data.get('desc', '')
            
            # Extract hashtags
            hashtags = []
            if 'challenges' in video_data:
                hashtags = [challenge.get('title', '') for challenge in video_data.get('challenges', [])]
            elif 'hashtags' in video_data:
                hashtags = video_data.get('hashtags', [])
            
            # Extract creator info
            creator = video_data.get('author', {})
            creator_username = creator.get('uniqueId', '') or creator.get('username', '')
            creator_followers = creator.get('followerCount', 0)
            creator_verified = creator.get('verified', False)
            
            # Extract engagement metrics
            stats = video_data.get('stats', {})
            view_count = stats.get('playCount', 0)
            like_count = stats.get('diggCount', 0)
            comment_count = stats.get('commentCount', 0)
            share_count = stats.get('shareCount', 0)
            save_count = stats.get('collectCount', 0)
            
            # Extract video info
            video_info = video_data.get('video', {})
            duration = video_info.get('duration', 0)
            
            # Extract music info
            music = video_data.get('music', {})
            music_title = music.get('title', '')
            
            # Calculate engagement rate
            engagement_rate = self._calculate_engagement_rate(view_count, like_count, comment_count, share_count)
            
            # Build metadata dict with all metrics
            metadata = {
                'view_count': str(view_count),
                'like_count': str(like_count),
                'comment_count': str(comment_count),
                'share_count': str(share_count),
                'save_count': str(save_count),
                'engagement_rate': str(engagement_rate),
                'creator_username': creator_username,
                'creator_followers': str(creator_followers),
                'creator_verified': str(creator_verified),
                'duration_seconds': str(duration),
                'music': music_title,
                'created_time': str(video_data.get('createTime', 0)),
            }
            
            # Create IdeaInspiration using from_video factory method
            return IdeaInspiration.from_video(
                title=title,
                description=description,
                subtitle_text='',  # TikTok doesn't provide subtitles via basic API
                keywords=self.format_tags(hashtags),
                metadata=metadata,
                source_id=video_id,
                source_url=f"https://www.tiktok.com/@{creator_username}/video/{video_id}" if creator_username and video_id else None,
                source_platform='tiktok',
                source_created_by=creator_username,
                source_created_at=None,  # Would need to convert createTime timestamp
            )
        except Exception as e:
            print(f"Error transforming video to IdeaInspiration: {e}")
            return None
    
    def _calculate_engagement_rate(self, views: int, likes: int, comments: int, shares: int) -> float:
        """Calculate engagement rate.
        
        Args:
            views: View count
            likes: Like count
            comments: Comment count
            shares: Share count
            
        Returns:
            Engagement rate as percentage
        """
        if views == 0:
            return 0.0
        
        total_engagement = likes + comments + shares
        return (total_engagement / views) * 100
