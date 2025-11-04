"""Instagram Explore/Trending plugin for scraping reels from explore page.

This plugin scrapes trending/explore Instagram Reels with comprehensive metadata.
Uses instaloader library for Instagram access.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from . import SourcePlugin, IdeaInspiration


class InstagramExplorePlugin(SourcePlugin):
    """Plugin for scraping reels from Instagram explore/trending page."""
    
    # Instagram Reels constraints
    REELS_MAX_DURATION = 90  # Instagram Reels max is 90 seconds
    
    def __init__(self, config):
        """Initialize Instagram explore plugin.
        
        Args:
            config: Configuration object
        """
        super().__init__(config)
        self._loader = None
        
        # Check if instaloader is available
        if not self._check_instaloader():
            raise ValueError(
                "instaloader is not installed. Install with: pip install instaloader"
            )
    
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        return "instagram_reels_explore"
    
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
                    print("Continuing without authentication (limited access)")
        
        return self._loader
    
    def scrape_explore(self, max_reels: Optional[int] = None) -> List[IdeaInspiration]:
        """Scrape reels from Instagram explore page.
        
        Args:
            max_reels: Maximum number of reels to scrape
            
        Returns:
            List of IdeaInspiration objects
        """
        if max_reels is None:
            max_reels = getattr(self.config, 'instagram_explore_max_reels', 50)
        
        reels = []
        loader = self._get_loader()
        
        print(f"Scraping explore reels (max: {max_reels})...")
        
        try:
            # Note: This is a placeholder implementation
            # Real implementation would need to access Instagram's explore page
            # which may require more sophisticated scraping or API access
            
            # For now, we'll return a placeholder message
            print("Note: Instagram explore scraping requires authenticated access")
            print("This is a template implementation - actual scraping logic")
            print("would use instaloader or alternative methods to access explore page")
            
            # Placeholder: You would implement actual explore page scraping here
            # Example structure for what would be returned:
            # for post in loader.get_explore_posts():
            #     if self._is_reel(post) and len(reels) < max_reels:
            #         reel_data = self._extract_reel_metadata(post)
            #         if reel_data:
            #             reels.append(reel_data)
            
        except Exception as e:
            print(f"Error scraping explore reels: {e}")
        
        return reels
    
    def scrape(self, max_reels: Optional[int] = None) -> List[IdeaInspiration]:
        """Main scrape method.
        
        Args:
            max_reels: Maximum number of reels to scrape
            
        Returns:
            List of IdeaInspiration objects
        """
        return self.scrape_explore(max_reels=max_reels)
    
    def _is_reel(self, post) -> bool:
        """Check if a post is a reel.
        
        Args:
            post: Instagram post object
            
        Returns:
            True if post is a reel
        """
        # Check if post is a video and has reel characteristics
        if not hasattr(post, 'is_video') or not post.is_video:
            return False
        
        # Check duration (reels are max 90 seconds)
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
            # Extract basic info
            shortcode = post.shortcode
            caption = post.caption if post.caption else ""
            
            # Extract hashtags
            hashtags = []
            if post.caption_hashtags:
                hashtags = list(post.caption_hashtags)
            
            # Extract metrics
            likes = post.likes
            comments = post.comments
            views = post.video_view_count if hasattr(post, 'video_view_count') else 0
            
            # Extract creator info
            username = post.owner_username
            owner_profile = post.owner_profile
            followers = owner_profile.followers if hasattr(owner_profile, 'followers') else 0
            verified = owner_profile.is_verified if hasattr(owner_profile, 'is_verified') else False
            
            # Extract upload date
            upload_date = post.date_utc.isoformat() if hasattr(post, 'date_utc') else None
            
            # Calculate days since upload
            days_since = None
            if upload_date:
                upload_datetime = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                days_since = (datetime.now() - upload_datetime).days
            
            # Build reel data structure
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
                    'saves': 0,  # Not available via basic API
                    'shares': 0  # Not available via basic API
                },
                'reel': {
                    'duration': post.video_duration if hasattr(post, 'video_duration') else 0,
                    'audio': 'Original audio' if not hasattr(post, 'audio_info') else str(post.audio_info),
                    'location': post.location.name if post.location else None,
                    'filters': [],  # Not available via basic API
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
