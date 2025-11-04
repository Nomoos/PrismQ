"""Instagram Creator plugin for scraping reels from creator profiles.

This plugin scrapes Instagram Reels from specific creator profiles.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from . import SourcePlugin, IdeaInspiration


class InstagramCreatorPlugin(SourcePlugin):
    """Plugin for scraping reels from creator profiles."""
    
    REELS_MAX_DURATION = 90
    
    def __init__(self, config):
        """Initialize Instagram creator plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        self._loader = None
        
        if not self._check_instaloader():
            raise ValueError(
                "instaloader is not installed. Install with: pip install instaloader"
            )
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "instagram_reels_creator"
    
    def _check_instaloader(self) -> bool:
        """Check if instaloader is installed.
        
        Returns:
            True if instaloader is available
        """
        try:
            import instaloader
            return True
        except ImportError:
            return False
    
    def _get_loader(self):
        """Get or create instaloader instance.
        
        Returns:
            Instaloader instance
        """
        if self._loader is None:
            import instaloader
            self._loader = instaloader.Instaloader(
                download_pictures=False,
                download_videos=False,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,
                compress_json=False
            )
            
            # Login if credentials provided
            username = getattr(self.config, 'instagram_username', '')
            password = getattr(self.config, 'instagram_password', '')
            
            if username and password:
                try:
                    self._loader.login(username, password)
                    print(f"Logged in as {username}")
                except Exception as e:
                    print(f"Warning: Failed to login: {e}")
        
        return self._loader
    
    def scrape_creator(self, username: str, max_reels: Optional[int] = None) -> List[IdeaInspiration]:
        """Scrape reels from creator profile.
        
        Args:
            username: Instagram username
            max_reels: Maximum number of reels to scrape
            
        Returns:
            List of IdeaInspiration objects
        """
        if max_reels is None:
            max_reels = getattr(self.config, 'instagram_creator_max_reels', 50)
        
        reels = []
        loader = self._get_loader()
        
        print(f"Scraping reels from @{username} (max: {max_reels})...")
        
        try:
            import instaloader
            
            # Get profile
            profile = instaloader.Profile.from_username(loader.context, username)
            
            count = 0
            for post in profile.get_posts():
                if count >= max_reels:
                    break
                
                # Check if it's a reel
                if self._is_reel(post):
                    reel_data = self._extract_reel_metadata(post)
                    if reel_data:
                        idea = self.transform_reel_to_idea(reel_data)
                        if idea:
                            reels.append(idea)
                            count += 1
                            print(f"  Scraped reel {count}/{max_reels}: {idea.source_id}")
        
        except Exception as e:
            print(f"Error scraping creator @{username}: {e}")
        
        return reels
    
    def scrape(self, username: Optional[str] = None, max_reels: Optional[int] = None) -> List[IdeaInspiration]:
        """Main scrape method.
        
        Args:
            username: Instagram username
            max_reels: Maximum number of reels
            
        Returns:
            List of IdeaInspiration objects
        """
        if not username:
            raise ValueError("Username is required for creator scraping")
        
        return self.scrape_creator(username, max_reels=max_reels)
    
    def _is_reel(self, post) -> bool:
        """Check if a post is a reel.
        
        Args:
            post: Instagram post object
            
        Returns:
            True if post is a reel
        """
        if not hasattr(post, 'is_video') or not post.is_video:
            return False
        
        if hasattr(post, 'video_duration'):
            return post.video_duration <= self.REELS_MAX_DURATION
        
        return True
    
    def _extract_reel_metadata(self, post) -> Optional[Dict[str, Any]]:
        """Extract metadata from Instagram post/reel.
        
        Args:
            post: Instagram post object
            
        Returns:
            Reel metadata dictionary or None
        """
        try:
            shortcode = post.shortcode
            caption = post.caption if post.caption else ""
            
            hashtags = []
            if post.caption_hashtags:
                hashtags = list(post.caption_hashtags)
            
            likes = post.likes
            comments = post.comments
            views = post.video_view_count if hasattr(post, 'video_view_count') else 0
            
            username = post.owner_username
            owner_profile = post.owner_profile
            followers = owner_profile.followers if hasattr(owner_profile, 'followers') else 0
            verified = owner_profile.is_verified if hasattr(owner_profile, 'is_verified') else False
            
            upload_date = post.date_utc.isoformat() if hasattr(post, 'date_utc') else None
            
            reel_data = {
                'source': 'instagram_reels',
                'source_id': shortcode,
                'title': caption[:100] if caption else f"Reel by {username}",
                'description': caption,
                'tags': hashtags,
                'creator': {
                    'username': username,
                    'followers': followers,
                    'verified': verified
                },
                'metrics': {
                    'plays': views,
                    'likes': likes,
                    'comments': comments,
                    'saves': 0,
                    'shares': 0
                },
                'reel': {
                    'duration': post.video_duration if hasattr(post, 'video_duration') else 0,
                    'audio': 'Original audio',
                    'location': post.location.name if post.location else None,
                    'filters': [],
                },
                'upload_date': upload_date
            }
            
            return reel_data
            
        except Exception as e:
            print(f"Error extracting reel metadata: {e}")
            return None
    
    def transform_reel_to_idea(self, reel_data: Dict[str, Any]) -> Optional[IdeaInspiration]:
        """Transform reel data dictionary to IdeaInspiration object.
        
        Args:
            reel_data: Reel data dictionary
            
        Returns:
            IdeaInspiration object or None
        """
        try:
            # Extract metrics and move to metadata
            metrics = reel_data.get('metrics', {})
            creator = reel_data.get('creator', {})
            reel_info = reel_data.get('reel', {})
            
            # Build metadata dict with all metrics and additional info
            metadata = {
                'plays': str(metrics.get('plays', 0)),
                'likes': str(metrics.get('likes', 0)),
                'comments': str(metrics.get('comments', 0)),
                'saves': str(metrics.get('saves', 0)),
                'shares': str(metrics.get('shares', 0)),
                'creator_username': creator.get('username', ''),
                'creator_followers': str(creator.get('followers', 0)),
                'creator_verified': str(creator.get('verified', False)),
                'duration': str(reel_info.get('duration', 0)),
                'audio': reel_info.get('audio', ''),
                'location': reel_info.get('location', '') if reel_info.get('location') else '',
            }
            
            # Create IdeaInspiration using from_video factory method
            return IdeaInspiration.from_video(
                title=reel_data.get('title', ''),
                description=reel_data.get('description', ''),
                subtitle_text='',  # Instagram doesn't provide subtitles via API
                keywords=reel_data.get('tags', []),
                metadata=metadata,
                source_id=reel_data.get('source_id'),
                source_url=f"https://www.instagram.com/reel/{reel_data.get('source_id', '')}" if reel_data.get('source_id') else None,
                source_platform='instagram_reels',
                source_created_by=creator.get('username'),
                source_created_at=reel_data.get('upload_date'),
            )
        except Exception as e:
            print(f"Error transforming reel to IdeaInspiration: {e}")
            return None
