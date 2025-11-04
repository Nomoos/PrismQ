"""GeoLocalTrends plugin for scraping location-based trend signals."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
from . import SignalPlugin, IdeaInspiration


class GeoLocalTrendsPlugin(SignalPlugin):
    """Plugin for scraping geographic location-based trend signals."""
    
    def __init__(self, config):
        """Initialize GeoLocalTrends plugin."""
        super().__init__(config)
        self.api = None
        print("GeoLocalTrends initialized in stub mode")
    
    def get_source_name(self) -> str:
        """Get the name of this source."""
        return "geo_local_trends"
    
    def scrape(self, **kwargs) -> List[IdeaInspiration]:
        """
        Scrape location-based trend signals.
        
        Args:
            **kwargs: Additional parameters
                - limit: Maximum number of trends to fetch
                - location: Specific location/region (e.g., 'US', 'UK', 'Tokyo')
        
        Returns:
            List of IdeaInspiration objects
        """
        ideas = []
        max_results = getattr(self.config, 'max_results', None) or \
                     getattr(self.config, 'geo_local_trends_max_results', 25)
        limit = kwargs.get('limit', max_results)
        location = kwargs.get('location', 'global')
        
        try:
            print("Running in stub mode - returning sample geographic trend data")
            signals = self._get_sample_geo_trends(limit, location)
            print(f"Successfully scraped {len(signals)} geographic trend signals")
            
        except Exception as e:
            print(f"Error scraping geographic trends: {e}")
            import traceback
            traceback.print_exc()
        
        return ideas
    
    def _get_sample_geo_trends(self, limit: int = 10, location: str = 'global') -> List[Dict[str, Any]]:
        """
        Generate sample geographic trend data for testing.
        
        Args:
            limit: Number of trends to generate
            location: Location filter
            
        Returns:
            List of IdeaInspiration objects
        """
        trends = [
            {
                'name': 'Local Food Festival',
                'description': 'Annual food festival trending in region',
                'location': 'San Francisco',
                'country': 'US',
                'volume': 500000,
                'category': 'events',
                'spread_score': 7.5
            },
            {
                'name': 'Cherry Blossom Season',
                'description': 'Spring cherry blossom viewing trend',
                'location': 'Tokyo',
                'country': 'Japan',
                'volume': 2000000,
                'category': 'seasonal',
                'spread_score': 9.0
            },
            {
                'name': 'Local Election',
                'description': 'Regional election discussion trending',
                'location': 'New York',
                'country': 'US',
                'volume': 1500000,
                'category': 'politics',
                'spread_score': 8.0
            },
            {
                'name': 'Tech Startup Hub',
                'description': 'Local tech startup ecosystem growth',
                'location': 'Austin',
                'country': 'US',
                'volume': 800000,
                'category': 'business',
                'spread_score': 7.0
            },
            {
                'name': 'Football Derby',
                'description': 'Local football rivalry match trending',
                'location': 'London',
                'country': 'UK',
                'volume': 3000000,
                'category': 'sports',
                'spread_score': 9.5
            },
            {
                'name': 'Beach Season Opening',
                'description': 'Summer beach season kickoff',
                'location': 'Sydney',
                'country': 'Australia',
                'volume': 600000,
                'category': 'seasonal',
                'spread_score': 6.5
            },
            {
                'name': 'Local Music Festival',
                'description': 'Annual music festival trending',
                'location': 'Berlin',
                'country': 'Germany',
                'volume': 900000,
                'category': 'entertainment',
                'spread_score': 7.8
            },
            {
                'name': 'Winter Holiday Markets',
                'description': 'Traditional holiday market season',
                'location': 'Munich',
                'country': 'Germany',
                'volume': 1200000,
                'category': 'seasonal',
                'spread_score': 8.5
            },
            {
                'name': 'Local Traffic Update',
                'description': 'Major road construction trending',
                'location': 'Los Angeles',
                'country': 'US',
                'volume': 400000,
                'category': 'local',
                'spread_score': 5.0
            },
            {
                'name': 'Regional Restaurant Week',
                'description': 'Food week promotion trending',
                'location': 'Chicago',
                'country': 'US',
                'volume': 550000,
                'category': 'food',
                'spread_score': 6.8
            }
        ]
        
        # Filter by location if specified (not 'global')
        if location != 'global':
            trends = [t for t in trends if location.lower() in t['location'].lower() or 
                     location.lower() in t['country'].lower()]
        
        # Apply limit
        trends = trends[:limit]
        
        # Convert to signals
        ideas = []
        for trend in trends:
            idea = self._create_idea_inspiration(trend)
            ideas.append(idea)
        
        return ideas
    
    def _create_signal(self, trend: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a signal from geographic trend data.
        
        Args:
            trend: Raw trend data
            
        Returns:
            IdeaInspiration object
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Calculate metrics
        volume = trend.get('volume', 0)
        spread_score = trend.get('spread_score', 5.0)
        signal_strength = min(10.0, spread_score)
        
        signal = {
            'signal_type': 'location',
            'name': trend.get('name', 'Unknown Trend'),
            'source': self.get_source_name(),
            'signal_id': f"{trend.get('location', 'unknown')}_{trend.get('name', 'trend').replace(' ', '_')}_{int(time.time())}",
            'first_seen': timestamp,
            'last_seen': timestamp,
            'description': trend.get('description', ''),
            'tags': [
                'location',
                trend.get('category', 'general'),
                trend.get('country', 'global').lower()
            ],
            'metrics': {
                'signal_strength': signal_strength,
                'volume': volume,
                'spread_score': spread_score,
                'virality': min(1.0, volume / 5000000)  # 0-1 scale
            },
            'temporal': {
                'first_observed': timestamp,
                'last_updated': timestamp,
                'current_status': 'active'
            },
            'extra': {
                'location': trend.get('location', 'Unknown'),
                'country': trend.get('country', 'Unknown'),
                'category': trend.get('category', 'general'),
                'volume': volume
            }
        }
        
        return signal
