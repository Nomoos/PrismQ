"""MemeTracker plugin for scraping meme signals."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
from . import SignalPlugin, IdeaInspiration


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
    
    def scrape(self, **kwargs) -> List[IdeaInspiration]:
        """
        Scrape meme signals from various platforms.
        
        Args:
            **kwargs: Additional parameters
                - limit: Maximum number of memes to fetch
                - platform: Specific platform to track (reddit, twitter, etc.)
        
        Returns:
            List of IdeaInspiration objects
        """
        ideas = []
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
        
        return ideas
    
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
        
        ideas = []
        for meme_data in sample_memes[:limit]:
            idea = self._create_idea_inspiration(meme_data)
            ideas.append(idea)
        
        return ideas
    
    def _create_idea_inspiration(self, meme_data: Dict[str, Any]) -> IdeaInspiration:
        """Create an IdeaInspiration object from meme data."""
        meme_title = meme_data.get('title', 'Unknown Meme')
        virality = meme_data.get('virality_score', 5.0)
        platform = meme_data.get('platform', 'unknown')
        category = meme_data.get('category', 'general')
        
        velocity = self._calculate_velocity(virality)
        
        # Format tags
        tags = self.format_tags(['meme', 'viral', platform, category])
        
        # Build metadata with platform-specific data
        metadata = {
            'virality_score': str(virality),
            'velocity': str(velocity),
            'platform': platform,
            'category': category,
            'signal_type': 'meme',
            'current_status': self._determine_status(velocity)
        }
        
        # Create IdeaInspiration using from_text factory method
        idea = IdeaInspiration.from_text(
            title=meme_title,
            description=f'Trending meme: {meme_title}',
            text_content=f'Viral meme from {platform}: {meme_title}',
            keywords=tags,
            source_platform="meme_tracker",  # Platform identifier
            metadata=metadata,
            source_id=f"meme_tracker_{meme_title.lower().replace(' ', '_')}",
            source_url=f"https://knowyourmeme.com/search?q={meme_title.replace(' ', '+')}"
        )
        
        return idea
    
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
