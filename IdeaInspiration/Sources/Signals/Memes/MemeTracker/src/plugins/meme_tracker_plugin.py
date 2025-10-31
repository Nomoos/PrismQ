"""MemeTracker plugin for scraping meme signals."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
from . import SignalPlugin


class MemeTrackerPlugin(SignalPlugin):
    """Plugin for scraping meme signals from various sources."""
    
    def __init__(self, config):
        """Initialize Meme Tracker plugin."""
        super().__init__(config)
        self.api = None
        print("MemeTracker initialized in stub mode")
    
    def get_source_name(self) -> str:
        """Get the name of this source."""
        return "meme_tracker"
    
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape meme signals from various platforms.
        
        Args:
            **kwargs: Additional parameters
                - limit: Maximum number of memes to fetch
                - platform: Specific platform to track (reddit, twitter, etc.)
        
        Returns:
            List of signal dictionaries
        """
        signals = []
        max_results = getattr(self.config, 'max_results', None) or \
                     getattr(self.config, 'meme_tracker_max_results', 25)
        limit = kwargs.get('limit', max_results)
        platform = kwargs.get('platform', 'all')
        
        try:
            print("Running in stub mode - returning sample meme data")
            signals = self._get_sample_memes(limit, platform)
            print(f"Successfully scraped {len(signals)} meme signals from MemeTracker")
            
        except Exception as e:
            print(f"Error scraping meme trends: {e}")
            import traceback
            traceback.print_exc()
        
        return signals
    
    def _get_sample_memes(self, limit: int, platform: str) -> List[Dict[str, Any]]:
        """Get sample meme data for testing/stub mode."""
        sample_memes = [
            {'title': 'Distracted Boyfriend Returns', 'virality_score': 9.5, 'platform': 'reddit', 'category': 'reaction'},
            {'title': 'AI Art Fail Compilation', 'virality_score': 8.8, 'platform': 'twitter', 'category': 'technology'},
            {'title': 'Drake Hotline Bling Remix', 'virality_score': 8.5, 'platform': 'reddit', 'category': 'comparison'},
            {'title': 'Surprised Pikachu 2024', 'virality_score': 8.2, 'platform': 'instagram', 'category': 'reaction'},
            {'title': 'Woman Yelling at Cat Update', 'virality_score': 7.9, 'platform': 'twitter', 'category': 'reaction'},
            {'title': 'Stonks Guy Investment Advice', 'virality_score': 7.5, 'platform': 'reddit', 'category': 'finance'},
            {'title': 'This Is Fine Dog 2024', 'virality_score': 7.2, 'platform': 'twitter', 'category': 'situation'},
            {'title': 'Expanding Brain Galaxy', 'virality_score': 6.8, 'platform': 'reddit', 'category': 'comparison'},
            {'title': 'Bernie Sanders Mittens Return', 'virality_score': 6.5, 'platform': 'instagram', 'category': 'celebrity'},
            {'title': 'Success Kid All Grown Up', 'virality_score': 6.0, 'platform': 'twitter', 'category': 'wholesome'},
        ]
        
        # Filter by platform if specified
        if platform != 'all':
            sample_memes = [m for m in sample_memes if m['platform'] == platform]
        
        signals = []
        for meme_data in sample_memes[:limit]:
            signal = self._create_signal(meme_data)
            signals.append(signal)
        
        return signals
    
    def _create_signal(self, meme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a signal dictionary from meme data."""
        meme_title = meme_data.get('title', 'Unknown Meme')
        virality = meme_data.get('virality_score', 5.0)
        platform = meme_data.get('platform', 'unknown')
        category = meme_data.get('category', 'general')
        
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H')
        meme_slug = ''.join(c if c.isalnum() else '_' for c in meme_title.lower())[:30]
        source_id = f"{meme_slug}_{timestamp}"
        
        velocity = self._calculate_velocity(virality)
        
        return {
            'source_id': source_id,
            'signal_type': 'meme',
            'name': meme_title,
            'description': f'Trending meme: {meme_title}',
            'tags': ['meme', 'viral', platform, category],
            'metrics': {
                'volume': int(virality * 100000),
                'velocity': velocity,
                'acceleration': round(velocity / 5, 2),
                'geographic_spread': ['global']
            },
            'temporal': {
                'first_seen': datetime.now(timezone.utc).isoformat() + 'Z',
                'peak_time': None,
                'current_status': self._determine_status(velocity)
            },
            'extra': {
                'platform': platform,
                'category': category,
                'virality_score': virality
            }
        }
    
    def _calculate_velocity(self, virality_score: float) -> float:
        """Calculate meme velocity based on virality score."""
        velocity = min(100.0, virality_score * 10)
        return round(velocity, 2)
    
    def _determine_status(self, velocity: float) -> str:
        """Determine meme trend status."""
        if velocity > 80:
            return 'viral'
        elif velocity > 60:
            return 'trending'
        elif velocity > 30:
            return 'growing'
        else:
            return 'emerging'
