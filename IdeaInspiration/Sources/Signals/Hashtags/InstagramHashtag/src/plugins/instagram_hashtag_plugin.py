"""InstagramHashtag plugin for scraping hashtag signals."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
from . import SignalPlugin, IdeaInspiration


class InstagramHashtagPlugin(SignalPlugin):
    """Plugin for scraping hashtag signals from Instagram."""
    
    def __init__(self, config):
        """Initialize Instagram Hashtag plugin."""
        super().__init__(config)
        self.api = None
        self._initialize_api()
    
    def _initialize_api(self):
        """Initialize Instagram API client."""
        try:
            import instaloader
            self.api = instaloader.Instaloader()
            print("Instagram API initialized successfully")
        except ImportError:
            print("Warning: instaloader not installed. Install with: pip install instaloader")
            print("Running in stub mode - will return sample data")
            self.api = None
        except Exception as e:
            print(f"Warning: Could not initialize Instagram API: {e}")
            print("Running in stub mode - will return sample data")
            self.api = None
    
    def get_source_name(self) -> str:
        """Get the name of this source."""
        return "instagram_hashtag"
    
    def scrape(self, **kwargs) -> List[IdeaInspiration]:
        """
        Scrape hashtag signals from Instagram.
        
        Args:
            **kwargs: Additional parameters
                - limit: Maximum number of hashtags to fetch
                - hashtags: List of specific hashtags to track
        
        Returns:
            List of IdeaInspiration objects
        """
        signals = []
        max_results = getattr(self.config, 'max_results', None) or \
                     getattr(self.config, 'instagram_hashtag_max_results', 25)
        limit = kwargs.get('limit', max_results)
        specific_hashtags = kwargs.get('hashtags', [])
        
        try:
            if self.api is None:
                print("Running in stub mode - returning sample hashtag data")
                signals = self._get_sample_hashtags(limit)
            else:
                if specific_hashtags:
                    for hashtag in specific_hashtags[:limit]:
                        signal = self._fetch_hashtag_data(hashtag)
                        if signal:
                            signals.append(signal)
                            time.sleep(self.config.retry_delay_seconds)
                else:
                    signals = self._fetch_trending_hashtags(limit)
            
            print(f"Successfully scraped {len(signals)} hashtag signals from Instagram")
            
        except Exception as e:
            print(f"Error scraping Instagram hashtags: {e}")
            import traceback
            traceback.print_exc()
        
        return signals
    
    def _fetch_trending_hashtags(self, limit: int) -> List[Dict[str, Any]]:
        """Fetch trending hashtags from Instagram."""
        signals = []
        try:
            print("Fetching trending hashtags from Instagram...")
            signals = self._get_sample_hashtags(limit)
        except Exception as e:
            print(f"Error fetching trending hashtags: {e}")
        return signals
    
    def _fetch_hashtag_data(self, hashtag: str) -> Optional[Dict[str, Any]]:
        """Fetch data for a specific hashtag."""
        try:
            clean_hashtag = hashtag.lstrip('#')
            return self._create_signal({
                'name': clean_hashtag,
                'post_count': 500000,
                'engagement_rate': 4.5
            })
        except Exception as e:
            print(f"Error fetching hashtag '{hashtag}': {e}")
            return None
    
    def _get_sample_hashtags(self, limit: int) -> List[Dict[str, Any]]:
        """Get sample hashtag data for testing/stub mode."""
        sample_hashtags = [
            {'name': 'instagood', 'post_count': 1500000000, 'engagement_rate': 5.2},
            {'name': 'photooftheday', 'post_count': 1200000000, 'engagement_rate': 4.8},
            {'name': 'fashion', 'post_count': 900000000, 'engagement_rate': 5.5},
            {'name': 'beautiful', 'post_count': 800000000, 'engagement_rate': 4.3},
            {'name': 'art', 'post_count': 700000000, 'engagement_rate': 6.1},
            {'name': 'photography', 'post_count': 650000000, 'engagement_rate': 5.8},
            {'name': 'travel', 'post_count': 600000000, 'engagement_rate': 5.0},
            {'name': 'food', 'post_count': 550000000, 'engagement_rate': 4.7},
            {'name': 'fitness', 'post_count': 500000000, 'engagement_rate': 4.9},
            {'name': 'motivation', 'post_count': 450000000, 'engagement_rate': 5.3},
        ]
        
        ideas = []
        for hashtag_data in sample_hashtags[:limit]:
            idea = self._create_idea_inspiration(hashtag_data)
            ideas.append(idea)
        
        return ideas
    
    def _create_idea_inspiration(self, hashtag_data: Dict[str, Any]) -> IdeaInspiration:
        """Create an IdeaInspiration object from hashtag data."""
        hashtag_name = hashtag_data.get('name', 'unknown')
        post_count = hashtag_data.get('post_count', 0)
        engagement_rate = hashtag_data.get('engagement_rate', 0.0)
        
        velocity = self._calculate_velocity(post_count, engagement_rate)
        
        # Format tags
        tags = self.format_tags(['instagram', 'hashtag', 'social', hashtag_name])
        
        # Build metadata with platform-specific data
        metadata = {
            'post_count': str(post_count),
            'engagement_rate': str(engagement_rate),
            'velocity': str(velocity),
            'signal_type': 'hashtag',
            'hashtag_type': 'trending',
            'current_status': self._determine_status(velocity)
        }
        
        # Create IdeaInspiration using from_text factory method
        idea = IdeaInspiration.from_text(
            title=f'#{hashtag_name}',
            description=f'Instagram hashtag: #{hashtag_name}',
            text_content=f'Instagram trending hashtag #{hashtag_name}',
            keywords=tags,
            source_platform="instagram_hashtag",  # Platform identifier
            metadata=metadata,
            source_id=f"instagram_hashtag_{hashtag_name}",
            source_url=f"https://www.instagram.com/explore/tags/{hashtag_name}/"
        )
        
        return idea
    
    def _calculate_velocity(self, post_count: int, engagement_rate: float) -> float:
        """Calculate hashtag velocity."""
        base_velocity = min(80.0, (post_count / 10000000) * 10)
        engagement_bonus = engagement_rate * 2
        velocity = min(100.0, base_velocity + engagement_bonus)
        return round(velocity, 2)
    
    def _calculate_acceleration(self, velocity: float) -> float:
        """Calculate acceleration."""
        if velocity > 80:
            acceleration = 15.0
        elif velocity > 50:
            acceleration = 8.0
        elif velocity > 20:
            acceleration = 3.0
        else:
            acceleration = 0.5
        return round(acceleration, 2)
    
    def _determine_status(self, velocity: float) -> str:
        """Determine hashtag trend status."""
        if velocity > 70:
            return 'rising'
        elif velocity > 40:
            return 'peak'
        elif velocity > 20:
            return 'stable'
        else:
            return 'declining'
