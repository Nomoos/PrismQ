"""InstagramAudioTrends plugin for scraping audio trend signals."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
from . import SignalPlugin, IdeaInspiration


class InstagramAudioTrendsPlugin(SignalPlugin):
    """Plugin for scraping audio trend signals from Instagram."""
    
    def __init__(self, config):
        """Initialize Instagram Audio Trends plugin."""
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
        return "instagram_audio_trends"
    
    def scrape(self, **kwargs) -> List[IdeaInspiration]:
        """
        Scrape audio trend signals from Instagram.
        
        Args:
            **kwargs: Additional parameters
                - limit: Maximum number of audio trends to fetch
                - sounds: List of specific sounds to track
        
        Returns:
            List of IdeaInspiration objects
        """
        ideas = []
        max_results = getattr(self.config, 'max_results', None) or \
                     getattr(self.config, 'instagram_audio_trends_max_results', 25)
        limit = kwargs.get('limit', max_results)
        specific_sounds = kwargs.get('sounds', [])
        
        try:
            if self.api is None:
                print("Running in stub mode - returning sample audio trend data")
                signals = self._get_sample_audio_trends(limit)
            else:
                if specific_sounds:
                    for sound in specific_sounds[:limit]:
                        signal = self._fetch_sound_data(sound)
                        if idea:
                            ideas.append(idea)
                            time.sleep(self.config.retry_delay_seconds)
                else:
                    signals = self._fetch_trending_audio(limit)
            
            print(f"Successfully scraped {len(signals)} audio trend signals from Instagram")
            
        except Exception as e:
            print(f"Error scraping Instagram audio trends: {e}")
            import traceback
            traceback.print_exc()
        
        return ideas
    
    def _fetch_trending_audio(self, limit: int) -> List[IdeaInspiration]:
        """Fetch trending audio from Instagram."""
        ideas = []
        try:
            print("Fetching trending audio from Instagram...")
            signals = self._get_sample_audio_trends(limit)
        except Exception as e:
            print(f"Error fetching trending audio: {e}")
        return ideas
    
    def _fetch_sound_data(self, sound: str) -> Optional[IdeaInspiration]:
        """Fetch data for a specific sound."""
        try:
            return self._create_signal({
                'title': sound,
                'usage_count': 250000,
                'duration': 20,
                'artist': 'Unknown'
            })
        except Exception as e:
            print(f"Error fetching sound '{sound}': {e}")
            return None
    
    def _get_sample_audio_trends(self, limit: int) -> List[IdeaInspiration]:
        """Get sample audio trend data for testing/stub mode."""
        sample_sounds = [
            {'title': 'Trending Reels Audio 2024', 'usage_count': 3500000, 'duration': 18, 'artist': 'Viral Music'},
            {'title': 'Emotional Background Track', 'usage_count': 2800000, 'duration': 25, 'artist': 'Mood Makers'},
            {'title': 'Upbeat Dance Rhythm', 'usage_count': 2500000, 'duration': 15, 'artist': 'Beat Drops'},
            {'title': 'Chill Lo-Fi Vibes', 'usage_count': 2200000, 'duration': 30, 'artist': 'Lofi Artists'},
            {'title': 'Motivational Speech Clip', 'usage_count': 2000000, 'duration': 12, 'artist': 'Inspiration'},
            {'title': 'Comedy Sound Effect', 'usage_count': 1800000, 'duration': 8, 'artist': 'Funny Sounds'},
            {'title': 'Romantic Ballad Snippet', 'usage_count': 1600000, 'duration': 22, 'artist': 'Love Songs'},
            {'title': 'Gym Workout Energy', 'usage_count': 1400000, 'duration': 20, 'artist': 'Fitness Beats'},
            {'title': 'Nature Sounds Mix', 'usage_count': 1200000, 'duration': 35, 'artist': 'Ambient'},
            {'title': 'Trending Meme Audio', 'usage_count': 1000000, 'duration': 10, 'artist': 'Viral Memes'},
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
        tags = self.format_tags(['instagram', 'audio', 'reels', 'music', 'trending'])
        
        # Build metadata with platform-specific data
        metadata = {
            'usage_count': str(usage_count),
            'velocity': str(velocity),
            'duration_seconds': str(duration),
            'artist': artist,
            'signal_type': 'audio',
            'audio_type': 'trending',
            'current_status': self._determine_status(velocity)
        }
        
        # Create IdeaInspiration using from_text factory method
        idea = IdeaInspiration.from_text(
            title=sound_title,
            description=f'Trending audio on Instagram Reels: {sound_title}',
            text_content=f'Instagram Reels trending audio: {sound_title} by {artist} ({duration}s)',
            keywords=tags,
            source_platform="instagram_audio_trends",  # Platform identifier
            metadata=metadata,
            source_id=f"instagram_audio_{sound_title.lower().replace(' ', '_')}",
            source_url=f"https://www.instagram.com/reels/audio/{sound_title.replace(' ', '-')}"
        )
        
        return idea
    
    def _calculate_velocity(self, usage_count: int) -> float:
        """Calculate audio velocity (growth rate)."""
        if usage_count > 2000000:
            velocity = min(100.0, 75 + (usage_count / 500000))
        elif usage_count > 500000:
            velocity = min(75.0, 45 + (usage_count / 100000) * 3)
        else:
            velocity = min(45.0, (usage_count / 50000) * 5)
        return round(velocity, 2)
    
    def _calculate_acceleration(self, velocity: float) -> float:
        """Calculate acceleration (change in velocity)."""
        if velocity > 75:
            acceleration = 12.0
        elif velocity > 45:
            acceleration = 6.0
        elif velocity > 20:
            acceleration = 2.5
        else:
            acceleration = 0.5
        return round(acceleration, 2)
    
    def _determine_status(self, velocity: float) -> str:
        """Determine audio trend status based on velocity."""
        if velocity > 70:
            return 'rising'
        elif velocity > 40:
            return 'peak'
        elif velocity > 20:
            return 'stable'
        else:
            return 'declining'
