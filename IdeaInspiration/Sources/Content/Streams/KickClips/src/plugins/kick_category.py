"""Kick Category clips plugin for scraping idea inspirations by category.

This plugin scrapes clips from specific Kick.com categories using the unofficial API.
"""

import time
import cloudscraper
from typing import List, Dict, Any, Optional
from . import SourcePlugin, IdeaInspiration


class KickCategoryPlugin(SourcePlugin):
    """Plugin for scraping clips from Kick categories."""
    
    # Kick API endpoints
    KICK_API_BASE = "https://kick.com/api/v2"
    KICK_CATEGORIES_ENDPOINT = f"{KICK_API_BASE}/categories"
    
    def __init__(self, config, category_slug: Optional[str] = None):
        """Initialize Kick category plugin.
        
        Args:
            config: Configuration object
            category_slug: Category slug to scrape (e.g., 'gaming', 'just-chatting')
        """
        super().__init__(config)
        self.category_slug = category_slug
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
        return "kick_category"
    
    def scrape(self, max_clips: Optional[int] = None, category_slug: Optional[str] = None) -> List[IdeaInspiration]:
        """Scrape clips from a specific category.
        
        Args:
            max_clips: Maximum number of clips to scrape (uses config if not provided)
            category_slug: Category slug to scrape (uses instance value if not provided)
            
        Returns:
            List of IdeaInspiration objects
        """
        if max_clips is None:
            max_clips = getattr(self.config, 'kick_category_max_clips', 50)
        
        if category_slug is None:
            category_slug = self.category_slug
        
        if not category_slug:
            print("Error: No category specified")
            return []
        
        print(f"Scraping Kick clips from category '{category_slug}' (max: {max_clips})...")
        
        ideas = []
        page = 1
        per_page = 20
        
        while len(ideas) < max_clips:
            # Fetch clips from API
            clips = self._fetch_category_clips(category_slug, page, per_page)
            
            if not clips:
                print(f"No more clips found on page {page}")
                break
            
            print(f"  Page {page}: Found {len(clips)} clips")
            
            # Process each clip
            for clip in clips:
                if len(ideas) >= max_clips:
                    break
                
                idea = self.transform_clip_to_idea(clip, category_slug)
                if idea:
                    ideas.append(idea)
            
            # Check if we have more pages
            if len(clips) < per_page:
                break
            
            page += 1
            time.sleep(self.request_delay)
        
        print(f"Successfully scraped {len(ideas)} clips from category '{category_slug}'")
        return ideas
    
    def _fetch_category_clips(self, category_slug: str, page: int = 1, per_page: int = 20) -> List[Dict[str, Any]]:
        """Fetch clips from a specific category.
        
        Args:
            category_slug: Category slug
            page: Page number
            per_page: Number of clips per page
            
        Returns:
            List of clip data dictionaries
        """
        url = f"{self.KICK_CATEGORIES_ENDPOINT}/{category_slug}/clips"
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
                    # Category not found or no clips
                    print(f"  Category '{category_slug}' not found or has no clips")
                    return []
                else:
                    print(f"  Warning: API returned status {response.status_code}")
                    
            except Exception as e:
                print(f"  Error fetching clips (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.request_delay * 2)
        
        return []
    
    def _clip_to_idea(self, clip: Dict[str, Any], category_slug: str) -> Optional[IdeaInspiration]:
        """Convert Kick clip data to IdeaInspiration object.
        
        Args:
            clip: Clip data from API
            category_slug: Category slug
            
        Returns:
            IdeaInspiration object or None if invalid
        """
        return self.transform_clip_to_idea(clip, category_slug)
    
    def transform_clip_to_idea(self, clip: Dict[str, Any], category_slug: str) -> Optional[IdeaInspiration]:
        """Transform Kick clip data to IdeaInspiration object.
        
        Args:
            clip: Clip data from API
            category_slug: Category slug
            
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
            
            # Build description
            description_parts = [f"Category: {category_slug}"]
            channel_name = ''
            if clip.get('channel'):
                channel_name = clip['channel'].get('username') if isinstance(clip['channel'], dict) else clip['channel']
                description_parts.append(f"Streamer: {channel_name}")
            
            description = " | ".join(description_parts)
            
            # Extract tags
            tags = [category_slug]
            if clip.get('channel'):
                if channel_name:
                    tags.append(channel_name)
            
            # Extract streamer info
            streamer_followers = 0
            streamer_verified = False
            if clip.get('channel'):
                channel = clip['channel']
                if isinstance(channel, dict):
                    streamer_followers = channel.get('followers_count', 0)
                    streamer_verified = channel.get('verified', False)
                    if not channel_name:
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
                'category_slug': category_slug,
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
