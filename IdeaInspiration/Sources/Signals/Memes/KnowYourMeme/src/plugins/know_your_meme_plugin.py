"""KnowYourMeme plugin for scraping meme encyclopedia signals."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
from . import SignalPlugin


class KnowYourMemePlugin(SignalPlugin):
    """Plugin for scraping meme signals from Know Your Meme."""
    
    def __init__(self, config):
        """Initialize Know Your Meme plugin."""
        super().__init__(config)
        self.api = None
        print("KnowYourMeme initialized in stub mode")
    
    def get_source_name(self) -> str:
        """Get the name of this source."""
        return "know_your_meme"
    
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape meme signals from Know Your Meme.
        
        Args:
            **kwargs: Additional parameters
                - limit: Maximum number of memes to fetch
                - category: Specific category (trending, researching, confirmed)
        
        Returns:
            List of signal dictionaries
        """
        signals = []
        max_results = getattr(self.config, 'max_results', None) or \
                     getattr(self.config, 'know_your_meme_max_results', 25)
        limit = kwargs.get('limit', max_results)
        category = kwargs.get('category', 'trending')
        
        try:
            print("Running in stub mode - returning sample KYM data")
            signals = self._get_sample_memes(limit, category)
            print(f"Successfully scraped {len(signals)} meme signals from Know Your Meme")
            
        except Exception as e:
            print(f"Error scraping Know Your Meme: {e}")
            import traceback
            traceback.print_exc()
        
        return signals
    
    def _get_sample_memes(self, limit: int, category: str) -> List[Dict[str, Any]]:
        """Get sample meme data for testing/stub mode."""
        sample_memes = [
            {'title': 'Sigma Grindset Philosophy', 'status': 'confirmed', 'origin': 'Twitter', 'year': 2024, 'spread': 9.0},
            {'title': 'NPC Dialog Tree Wojak', 'status': 'trending', 'origin': '4chan', 'year': 2024, 'spread': 8.5},
            {'title': 'Based Gigachad Energy', 'status': 'confirmed', 'origin': 'Reddit', 'year': 2023, 'spread': 8.8},
            {'title': 'Zoomer Humor Database', 'status': 'researching', 'origin': 'TikTok', 'year': 2024, 'spread': 7.5},
            {'title': 'Cringe vs Based Chart', 'status': 'confirmed', 'origin': 'Twitter', 'year': 2023, 'spread': 8.0},
            {'title': 'Touch Grass Reminder', 'status': 'trending', 'origin': 'Reddit', 'year': 2024, 'spread': 7.8},
            {'title': 'Main Character Syndrome', 'status': 'confirmed', 'origin': 'Instagram', 'year': 2024, 'spread': 7.2},
            {'title': 'POV You Are X Meme', 'status': 'trending', 'origin': 'TikTok', 'year': 2024, 'spread': 8.3},
            {'title': 'Ratio Counter Ratio', 'status': 'confirmed', 'origin': 'Twitter', 'year': 2023, 'spread': 6.9},
            {'title': 'Boomer vs Zoomer Take', 'status': 'researching', 'origin': 'Reddit', 'year': 2024, 'spread': 6.5},
        ]
        
        # Filter by category/status if not 'trending'
        if category != 'trending':
            sample_memes = [m for m in sample_memes if m['status'] == category]
        
        signals = []
        for meme_data in sample_memes[:limit]:
            signal = self._create_signal(meme_data)
            signals.append(signal)
        
        return signals
    
    def _create_signal(self, meme_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a signal dictionary from meme data."""
        meme_title = meme_data.get('title', 'Unknown Meme')
        status = meme_data.get('status', 'researching')
        origin = meme_data.get('origin', 'Unknown')
        year = meme_data.get('year', 2024)
        spread = meme_data.get('spread', 5.0)
        
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H')
        meme_slug = ''.join(c if c.isalnum() else '_' for c in meme_title.lower())[:30]
        source_id = f"{meme_slug}_{timestamp}"
        
        velocity = self._calculate_velocity(spread, status)
        
        return {
            'source_id': source_id,
            'signal_type': 'meme',
            'name': meme_title,
            'description': f'Know Your Meme entry: {meme_title}',
            'tags': ['meme', 'kym', status, origin.lower()],
            'metrics': {
                'volume': int(spread * 150000),
                'velocity': velocity,
                'acceleration': round(velocity / 8, 2),
                'geographic_spread': ['global']
            },
            'temporal': {
                'first_seen': f"{year}-01-01T00:00:00Z",
                'peak_time': None,
                'current_status': status
            },
            'extra': {
                'platform': 'knowyourmeme',
                'origin': origin,
                'year': year,
                'status': status,
                'spread_score': spread
            }
        }
    
    def _calculate_velocity(self, spread: float, status: str) -> float:
        """Calculate meme velocity based on spread and status."""
        base_velocity = min(80.0, spread * 8)
        
        # Boost for confirmed/trending memes
        if status == 'confirmed':
            base_velocity *= 1.1
        elif status == 'trending':
            base_velocity *= 1.2
        
        return round(min(100.0, base_velocity), 2)
    
    def _determine_status(self, velocity: float) -> str:
        """Determine meme trend status."""
        if velocity > 80:
            return 'viral'
        elif velocity > 60:
            return 'trending'
        else:
            return 'documented'
