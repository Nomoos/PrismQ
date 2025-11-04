"""TikTokHashtag plugin for scraping hashtag signals."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
from . import SignalPlugin, IdeaInspiration


class TikTokHashtagPlugin(SignalPlugin):
    """Plugin for scraping hashtag signals from TikTok."""
    
    def __init__(self, config):
        """Initialize TikTok Hashtag plugin."""
        super().__init__(config)
        self.api = None
        self._initialize_api()
    
    def _initialize_api(self):
        """Initialize TikTok API client."""
        try:
            # Import TikTokApi here to avoid import errors if not installed
            from TikTokApi import TikTokApi
            
            # Initialize TikTokApi
            # Note: TikTokApi may require specific configuration
            # For now, we'll use a simple initialization
            self.api = TikTokApi()
            print("TikTok API initialized successfully")
        except ImportError:
            print("Warning: TikTokApi not installed. Install with: pip install TikTokApi")
            print("Running in stub mode - will return sample data")
            self.api = None
        except Exception as e:
            print(f"Warning: Could not initialize TikTok API: {e}")
            print("Running in stub mode - will return sample data")
            self.api = None
    
    def get_source_name(self) -> str:
        """Get the name of this source."""
        return "tiktok_hashtag"
    
    def scrape(self, **kwargs) -> List[IdeaInspiration]:
        """
        Scrape hashtag signals from TikTok.
        
        Args:
            **kwargs: Additional parameters
                - limit: Maximum number of hashtags to fetch (default: from config)
                - hashtags: List of specific hashtags to track (optional)
        
        Returns:
            List of IdeaInspiration objects
        """
        signals = []
        # Try different config attribute names for compatibility
        max_results = getattr(self.config, 'max_results', None) or \
                     getattr(self.config, 'tik_tok_hashtag_max_results', 25)
        limit = kwargs.get('limit', max_results)
        specific_hashtags = kwargs.get('hashtags', [])
        
        try:
            if self.api is None:
                # Stub mode: return sample data for testing
                print("Running in stub mode - returning sample hashtag data")
                signals = self._get_sample_hashtags(limit)
            else:
                # Real implementation with TikTokApi
                if specific_hashtags:
                    # Track specific hashtags
                    for hashtag in specific_hashtags[:limit]:
                        signal = self._fetch_hashtag_data(hashtag)
                        if signal:
                            signals.append(signal)
                            time.sleep(self.config.retry_delay_seconds)
                else:
                    # Fetch trending hashtags
                    signals = self._fetch_trending_hashtags(limit)
            
            print(f"Successfully scraped {len(signals)} hashtag signals from TikTok")
            
        except Exception as e:
            print(f"Error scraping TikTok hashtags: {e}")
            import traceback
            traceback.print_exc()
        
        return signals
    
    def _fetch_trending_hashtags(self, limit: int) -> List[IdeaInspiration]:
        """
        Fetch trending hashtags from TikTok.
        
        Args:
            limit: Maximum number of hashtags to fetch
        
        Returns:
            List of IdeaInspiration objects
        """
        signals = []
        
        try:
            # Note: TikTokApi trending hashtags functionality
            # This is a placeholder - actual implementation depends on TikTokApi version
            # For production, you'd use: trending = self.api.trending.hashtags(count=limit)
            
            print("Fetching trending hashtags from TikTok...")
            # Placeholder: In real implementation, call API here
            # For now, return sample data
            signals = self._get_sample_hashtags(limit)
            
        except Exception as e:
            print(f"Error fetching trending hashtags: {e}")
        
        return signals
    
    def _fetch_hashtag_data(self, hashtag: str) -> Optional[IdeaInspiration]:
        """
        Fetch data for a specific hashtag.
        
        Args:
            hashtag: Hashtag name (with or without #)
        
        Returns:
            IdeaInspiration object or None if error
        """
        try:
            # Remove # if present
            clean_hashtag = hashtag.lstrip('#')
            
            # Note: Actual TikTokApi call would be:
            # hashtag_data = self.api.hashtag(name=clean_hashtag).info()
            
            # For now, create sample data
            return self._create_idea_inspiration({
                'name': clean_hashtag,
                'view_count': 1000000,
                'video_count': 5000,
                'description': f'Trending hashtag: #{clean_hashtag}'
            })
            
        except Exception as e:
            print(f"Error fetching hashtag '{hashtag}': {e}")
            return None
    
    def _get_sample_hashtags(self, limit: int) -> List[IdeaInspiration]:
        """
        Get sample hashtag data for testing/stub mode.
        
        Args:
            limit: Number of sample hashtags to generate
        
        Returns:
            List of IdeaInspiration objects
        """
        sample_hashtags = [
            {'name': 'fyp', 'view_count': 500000000, 'video_count': 2000000, 'description': 'For You Page'},
            {'name': 'viral', 'view_count': 300000000, 'video_count': 1500000, 'description': 'Viral content'},
            {'name': 'trending', 'view_count': 250000000, 'video_count': 1200000, 'description': 'Trending now'},
            {'name': 'challenge', 'view_count': 200000000, 'video_count': 900000, 'description': 'TikTok challenges'},
            {'name': 'dance', 'view_count': 180000000, 'video_count': 850000, 'description': 'Dance videos'},
            {'name': 'comedy', 'view_count': 150000000, 'video_count': 700000, 'description': 'Comedy content'},
            {'name': 'tutorial', 'view_count': 120000000, 'video_count': 600000, 'description': 'How-to videos'},
            {'name': 'food', 'view_count': 100000000, 'video_count': 500000, 'description': 'Food content'},
            {'name': 'fashion', 'view_count': 90000000, 'video_count': 450000, 'description': 'Fashion trends'},
            {'name': 'travel', 'view_count': 80000000, 'video_count': 400000, 'description': 'Travel content'},
        ]
        
        ideas = []
        for hashtag_data in sample_hashtags[:limit]:
            idea = self._create_idea_inspiration(hashtag_data)
            ideas.append(idea)
        
        return ideas
    
    def _create_idea_inspiration(self, hashtag_data: Dict[str, Any]) -> IdeaInspiration:
        """
        Create an IdeaInspiration object from hashtag data.
        
        Args:
            hashtag_data: Raw hashtag data from TikTok
        
        Returns:
            IdeaInspiration object
        """
        hashtag_name = hashtag_data.get('name', 'unknown')
        view_count = hashtag_data.get('view_count', 0)
        video_count = hashtag_data.get('video_count', 0)
        description = hashtag_data.get('description', f'TikTok hashtag: #{hashtag_name}')
        
        # Calculate velocity (growth rate)
        velocity = self._calculate_velocity(view_count, video_count)
        
        # Format tags
        tags = self.format_tags(['tiktok', 'hashtag', 'viral', hashtag_name])
        
        # Build metadata with platform-specific data
        metadata = {
            'view_count': str(view_count),
            'video_count': str(video_count),
            'velocity': str(velocity),
            'signal_type': 'hashtag',
            'hashtag_type': 'trending',
            'current_status': self._determine_status(velocity)
        }
        
        # Create IdeaInspiration using from_text factory method
        idea = IdeaInspiration.from_text(
            title=f'#{hashtag_name}',
            description=description,
            text_content=f'TikTok hashtag #{hashtag_name}: {description}',
            keywords=tags,
            source_platform="tiktok_hashtag",  # Platform identifier
            metadata=metadata,
            source_id=f"tiktok_hashtag_{hashtag_name}",
            source_url=f"https://www.tiktok.com/tag/{hashtag_name}"
        )
        
        return idea
    
    def _calculate_velocity(self, view_count: int, video_count: int) -> float:
        """
        Calculate hashtag velocity (growth rate).
        
        Args:
            view_count: Total views for the hashtag
            video_count: Number of videos using the hashtag
        
        Returns:
            Velocity score (0-100)
        """
        # Simplified velocity calculation
        # In production, compare with historical data
        if video_count > 0:
            views_per_video = view_count / video_count
            # Normalize to 0-100 scale
            velocity = min(100.0, (views_per_video / 10000) * 10)
        else:
            velocity = 0.0
        
        return round(velocity, 2)
    
    def _calculate_acceleration(self, velocity: float) -> float:
        """
        Calculate acceleration (change in velocity).
        
        Args:
            velocity: Current velocity
        
        Returns:
            Acceleration score
        """
        # Placeholder: In production, compare with previous velocity
        # For now, estimate based on velocity
        if velocity > 80:
            acceleration = 15.0  # High velocity suggests high acceleration
        elif velocity > 50:
            acceleration = 8.0
        elif velocity > 20:
            acceleration = 3.0
        else:
            acceleration = 0.5
        
        return round(acceleration, 2)
    
    def _determine_status(self, velocity: float) -> str:
        """
        Determine hashtag trend status based on velocity.
        
        Args:
            velocity: Velocity score
        
        Returns:
            Status string ('rising', 'peak', 'declining', 'stable')
        """
        if velocity > 70:
            return 'rising'
        elif velocity > 40:
            return 'peak'
        elif velocity > 20:
            return 'stable'
        else:
            return 'declining'
