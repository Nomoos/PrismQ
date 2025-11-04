"""Kick Trending clips plugin for scraping idea inspirations.

This plugin scrapes trending clips from Kick.com using the unofficial API.
"""

import time
import cloudscraper
from typing import List, Dict, Any, Optional
from datetime import datetime
from . import SourcePlugin, IdeaInspiration


class KickTrendingPlugin(SourcePlugin):
    """Plugin for scraping trending clips from Kick.com."""
    
    # Kick API endpoints
    KICK_API_BASE = "https://kick.com/api/v2"
    KICK_CLIPS_ENDPOINT = f"{KICK_API_BASE}/clips"
    
    def __init__(self, config):
        """Initialize Kick trending plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        # Use cloudscraper to bypass Cloudflare protection
        self.scraper = cloudscraper.create_scraper()
        self.request_delay = getattr(config, 'request_delay', 1.0)
        self.max_retries = getattr(config, 'max_retries', 3)
        self.request_timeout = getattr(config, 'request_timeout', 30)
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "kick_trending"
    
    def scrape(self, max_clips: Optional[int] = None) -> List[IdeaInspiration]:
        """Scrape trending clips from Kick.
        
        Args:
            max_clips: Maximum number of clips to scrape (uses config if not provided)
            
        Returns:
            List of IdeaInspiration objects
        """
        if max_clips is None:
            max_clips = getattr(self.config, 'kick_trending_max_clips', 50)
        
        print(f"Scraping trending Kick clips (max: {max_clips})...")
        
        ideas = []
        page = 1
        per_page = 20  # Fetch 20 clips per page
        
        while len(ideas) < max_clips:
            # Fetch clips from API
            clips = self._fetch_trending_clips(page, per_page)
            
            if not clips:
                print(f"No more clips found on page {page}")
                break
            
            print(f"  Page {page}: Found {len(clips)} clips")
            
            # Process each clip
            for clip in clips:
                if len(ideas) >= max_clips:
                    break
                
                idea = self.transform_clip_to_idea(clip)
                if idea:
                    ideas.append(idea)
            
            # Check if we have more pages
            if len(clips) < per_page:
                break
            
            page += 1
            time.sleep(self.request_delay)
        
        print(f"Successfully scraped {len(ideas)} trending clips")
        return ideas
    
    def _fetch_trending_clips(self, page: int = 1, per_page: int = 20) -> List[Dict[str, Any]]:
        """Fetch trending clips from Kick API.
        
        Args:
            page: Page number
            per_page: Number of clips per page
            
        Returns:
            List of clip data dictionaries
        """
        url = f"{self.KICK_CLIPS_ENDPOINT}/trending"
        params = {
            'page': page,
            'limit': per_page,
        }
        
        for attempt in range(self.max_retries):
            try:
                response = self.scraper.get(
                    url,
                    params=params,
                    timeout=self.request_timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # API may return clips directly or in a 'data' field
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'data' in data:
                        return data['data']
                    return []
                elif response.status_code == 404:
                    # No more clips
                    return []
                else:
                    print(f"  Warning: API returned status {response.status_code}")
                    
            except Exception as e:
                print(f"  Error fetching clips (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.request_delay * 2)
        
        return []
    
    def _clip_to_idea(self, clip: Dict[str, Any]) -> Optional[IdeaInspiration]:
        """Convert Kick clip data to IdeaInspiration object.
        
        Args:
            clip: Clip data from API
            
        Returns:
            IdeaInspiration object or None if invalid
        """
        return self.transform_clip_to_idea(clip)
    
    def transform_clip_to_idea(self, clip: Dict[str, Any]) -> Optional[IdeaInspiration]:
        """Transform Kick clip data to IdeaInspiration object.
        
        Args:
            clip: Clip data from API
            
        Returns:
            IdeaInspiration object or None
        """
        try:
            # Extract clip ID
            clip_id = clip.get('id') or clip.get('clip_id')
            if not clip_id:
                return None
            
            # Extract basic info
            title = clip.get('title', 'Untitled Clip')
            
            # Build description from available data
            description_parts = []
            if clip.get('category'):
                category_name = clip['category'].get('name') if isinstance(clip['category'], dict) else clip['category']
                description_parts.append(f"Category: {category_name}")
            
            if clip.get('channel'):
                channel_name = clip['channel'].get('username') if isinstance(clip['channel'], dict) else clip['channel']
                description_parts.append(f"Streamer: {channel_name}")
            
            description = " | ".join(description_parts) if description_parts else ""
            
            # Extract tags
            tags = []
            if clip.get('category'):
                category_name = clip['category'].get('name') if isinstance(clip['category'], dict) else clip['category']
                if category_name:
                    tags.append(category_name)
            
            if clip.get('channel'):
                channel_name = clip['channel'].get('username') if isinstance(clip['channel'], dict) else clip['channel']
                if channel_name:
                    tags.append(channel_name)
            
            # Extract streamer info
            streamer_followers = 0
            streamer_verified = False
            channel_name = ''
            if clip.get('channel'):
                channel = clip['channel']
                if isinstance(channel, dict):
                    streamer_followers = channel.get('followers_count', 0)
                    streamer_verified = channel.get('verified', False)
                    channel_name = channel.get('username', '')
            
            # Build metadata dict with all metrics
            metadata = {
                'views': str(clip.get('views', 0)),
                'likes': str(clip.get('likes', 0)),
                'comments': '0',
                'shares': '0',
                'reactions': str(clip.get('likes', 0)),
                'duration': str(clip.get('duration', 0)),
                'created_at': clip.get('created_at', ''),
                'streamer_followers': str(streamer_followers),
                'streamer_verified': str(streamer_verified),
                'language': clip.get('language', 'en'),
            }
            
            # Create IdeaInspiration using from_video factory method
            return IdeaInspiration.from_video(
                title=title,
                description=description,
                subtitle_text='',  # Kick doesn't provide subtitles via basic API
                keywords=self.format_tags(tags),
                metadata=metadata,
                source_id=str(clip_id),
                source_url=clip.get('url') or clip.get('clip_url'),
                source_platform='kick',
                source_created_by=channel_name,
                source_created_at=clip.get('created_at'),
            )
        except Exception as e:
            print(f"Error transforming clip to IdeaInspiration: {e}")
            return None
