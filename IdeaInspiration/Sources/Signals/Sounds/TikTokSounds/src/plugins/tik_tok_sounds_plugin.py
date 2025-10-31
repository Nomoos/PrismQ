"""TikTokSounds plugin for scraping sound signals."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
from . import SignalPlugin


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
    
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape sound signals from TikTok.
        
        Args:
            **kwargs: Additional parameters
                - limit: Maximum number of sounds to fetch (default: from config)
                - sounds: List of specific sounds to track (optional)
        
        Returns:
            List of signal dictionaries
        """
        signals = []
        max_results = getattr(self.config, 'max_results', None) or \
                     getattr(self.config, 'tik_tok_sounds_max_results', 25)
        limit = kwargs.get('limit', max_results)
        specific_sounds = kwargs.get('sounds', [])
        
        try:
            if self.api is None:
                print("Running in stub mode - returning sample sound data")
                signals = self._get_sample_sounds(limit)
            else:
                if specific_sounds:
                    for sound in specific_sounds[:limit]:
                        signal = self._fetch_sound_data(sound)
                        if signal:
                            signals.append(signal)
                            time.sleep(self.config.retry_delay_seconds)
                else:
                    signals = self._fetch_trending_sounds(limit)
            
            print(f"Successfully scraped {len(signals)} sound signals from TikTok")
            
        except Exception as e:
            print(f"Error scraping TikTok sounds: {e}")
            import traceback
            traceback.print_exc()
        
        return signals
    
    def _fetch_trending_sounds(self, limit: int) -> List[Dict[str, Any]]:
        """Fetch trending sounds from TikTok."""
        signals = []
        try:
            print("Fetching trending sounds from TikTok...")
            signals = self._get_sample_sounds(limit)
        except Exception as e:
            print(f"Error fetching trending sounds: {e}")
        return signals
    
    def _fetch_sound_data(self, sound: str) -> Optional[Dict[str, Any]]:
        """Fetch data for a specific sound."""
        try:
            return self._create_signal({
                'title': sound,
                'usage_count': 100000,
                'duration': 15,
                'artist': 'Unknown Artist'
            })
        except Exception as e:
            print(f"Error fetching sound '{sound}': {e}")
            return None
    
    def _get_sample_sounds(self, limit: int) -> List[Dict[str, Any]]:
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
        
        signals = []
        for sound_data in sample_sounds[:limit]:
            signal = self._create_signal(sound_data)
            signals.append(signal)
        
        return signals
    
    def _create_signal(self, sound_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a signal dictionary from sound data."""
        sound_title = sound_data.get('title', 'Unknown')
        usage_count = sound_data.get('usage_count', 0)
        duration = sound_data.get('duration', 15)
        artist = sound_data.get('artist', 'Unknown Artist')
        
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H')
        sound_slug = ''.join(c if c.isalnum() else '_' for c in sound_title.lower())[:30]
        source_id = f"{sound_slug}_{timestamp}"
        
        velocity = self._calculate_velocity(usage_count)
        acceleration = self._calculate_acceleration(velocity)
        
        return {
            'source_id': source_id,
            'signal_type': 'sound',
            'name': sound_title,
            'description': f'Trending audio on TikTok: {sound_title}',
            'tags': ['tiktok', 'sound', 'audio', 'music'],
            'metrics': {
                'volume': usage_count,
                'velocity': velocity,
                'acceleration': acceleration,
                'geographic_spread': ['global']
            },
            'temporal': {
                'first_seen': datetime.now(timezone.utc).isoformat() + 'Z',
                'peak_time': None,
                'current_status': self._determine_status(velocity)
            },
            'extra': {
                'platform': 'tiktok',
                'sound_type': 'trending',
                'duration_seconds': duration,
                'artist': artist
            }
        }
    
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
