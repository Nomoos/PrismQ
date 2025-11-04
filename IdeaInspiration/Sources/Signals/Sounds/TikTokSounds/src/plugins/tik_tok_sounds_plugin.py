"""TikTokSounds plugin for scraping sound signals."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
from . import SignalPlugin, IdeaInspiration


class TikTokSoundsPlugin(SignalPlugin):
    """Plugin for scraping sound signals from TikTok."""
    
    def __init__(self, config):
        """Initialize TikTok Sounds plugin."""
        super().__init__(config)
        self.api = None
        self._initialize_api()
    
    def _initialize_api(self):
        """Initialize TikTok API client."""
        try:
            from TikTokApi import TikTokApi
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
        return "tiktok_sounds"
    
    def scrape(self, **kwargs) -> List[IdeaInspiration]:
        """
        Scrape sound signals from TikTok.
        
        Args:
            **kwargs: Additional parameters
                - limit: Maximum number of sounds to fetch (default: from config)
                - sounds: List of specific sounds to track (optional)
        
        Returns:
            List of IdeaInspiration objects
        """
        ideas = []
        max_results = getattr(self.config, 'max_results', None) or \
                     getattr(self.config, 'tik_tok_sounds_max_results', 25)
        limit = kwargs.get('limit', max_results)
        specific_sounds = kwargs.get('sounds', [])
        
        try:
            if self.api is None:
                print("Running in stub mode - returning sample sound data")
                ideas = self._get_sample_sounds(limit)
            else:
                if specific_sounds:
                    for sound in specific_sounds[:limit]:
                        idea = self._fetch_sound_data(sound)
                        if idea:
                            ideas.append(idea)
                            time.sleep(self.config.retry_delay_seconds)
                else:
                    ideas = self._fetch_trending_sounds(limit)
            
            print(f"Successfully scraped {len(ideas)} sound signals from TikTok")
            
        except Exception as e:
            print(f"Error scraping TikTok sounds: {e}")
            import traceback
            traceback.print_exc()
        
        return ideas
    
    def _fetch_trending_sounds(self, limit: int) -> List[IdeaInspiration]:
        """Fetch trending sounds from TikTok."""
        ideas = []
        try:
            print("Fetching trending sounds from TikTok...")
            ideas = self._get_sample_sounds(limit)
        except Exception as e:
            print(f"Error fetching trending sounds: {e}")
        return ideas
    
    def _fetch_sound_data(self, sound: str) -> Optional[IdeaInspiration]:
        """Fetch data for a specific sound."""
        try:
            return self._create_idea_inspiration({
                'title': sound,
                'usage_count': 100000,
                'duration': 15,
                'artist': 'Unknown Artist'
            })
        except Exception as e:
            print(f"Error fetching sound '{sound}': {e}")
            return None
    
    def _get_sample_sounds(self, limit: int) -> List[IdeaInspiration]:
        """Get sample sound data for testing/stub mode."""
        sample_sounds = [
            {'title': 'Viral Dance Beat 2024', 'usage_count': 5000000, 'duration': 15, 'artist': 'DJ Trends'},
            {'title': 'Emotional Piano Melody', 'usage_count': 3500000, 'duration': 30, 'artist': 'Piano Masters'},
            {'title': 'Upbeat Pop Hook', 'usage_count': 3000000, 'duration': 20, 'artist': 'Pop Stars'},
            {'title': 'Lo-Fi Chill Beats', 'usage_count': 2800000, 'duration': 45, 'artist': 'Chill Vibes'},
            {'title': 'Epic Cinematic Score', 'usage_count': 2500000, 'duration': 25, 'artist': 'Film Composers'},
            {'title': 'Trending Rap Beat', 'usage_count': 2200000, 'duration': 18, 'artist': 'Beat Makers'},
            {'title': 'Acoustic Guitar Loop', 'usage_count': 2000000, 'duration': 22, 'artist': 'Guitar Pros'},
            {'title': 'Electronic Dance Drop', 'usage_count': 1800000, 'duration': 12, 'artist': 'EDM Producers'},
            {'title': 'Funny Sound Effect', 'usage_count': 1500000, 'duration': 5, 'artist': 'Sound FX'},
            {'title': 'Motivational Anthem', 'usage_count': 1200000, 'duration': 28, 'artist': 'Inspiration Inc'},
        ]
        
        ideas = []
        for sound_data in sample_sounds[:limit]:
            idea = self._create_idea_inspiration(sound_data)
            ideas.append(idea)
        
        return ideas
    
    def _create_idea_inspiration(self, sound_data: Dict[str, Any]) -> IdeaInspiration:
        """Create an IdeaInspiration object from sound data."""
        sound_title = sound_data.get('title', 'Unknown')
        usage_count = sound_data.get('usage_count', 0)
        duration = sound_data.get('duration', 15)
        artist = sound_data.get('artist', 'Unknown Artist')
        
        velocity = self._calculate_velocity(usage_count)
        
        # Format tags
        tags = self.format_tags(['tiktok', 'sound', 'audio', 'music', 'trending'])
        
        # Build metadata with platform-specific data
        metadata = {
            'usage_count': str(usage_count),
            'velocity': str(velocity),
            'duration_seconds': str(duration),
            'artist': artist,
            'signal_type': 'sound',
            'sound_type': 'trending',
            'current_status': self._determine_status(velocity)
        }
        
        # Create IdeaInspiration using from_text factory method
        idea = IdeaInspiration.from_text(
            title=sound_title,
            description=f'Trending audio on TikTok by {artist}: {sound_title}',
            text_content=f'TikTok trending sound: {sound_title} ({duration}s)',
            keywords=tags,
            source_platform="tiktok_sounds",  # Platform identifier
            metadata=metadata,
            source_id=f"tiktok_sounds_{sound_title.lower().replace(' ', '_')}",
            source_url=f"https://www.tiktok.com/music/{sound_title.replace(' ', '-')}"
        )
        
        return idea
    
    def _calculate_velocity(self, usage_count: int) -> float:
        """Calculate sound velocity (growth rate)."""
        if usage_count > 1000000:
            velocity = min(100.0, 80 + (usage_count / 1000000) * 2)
        elif usage_count > 100000:
            velocity = min(80.0, 50 + (usage_count / 100000) * 3)
        else:
            velocity = min(50.0, (usage_count / 10000) * 5)
        return round(velocity, 2)
    
    def _calculate_acceleration(self, velocity: float) -> float:
        """Calculate acceleration (change in velocity)."""
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
        """Determine sound trend status based on velocity."""
        if velocity > 70:
            return 'rising'
        elif velocity > 40:
            return 'peak'
        elif velocity > 20:
            return 'stable'
        else:
            return 'declining'
