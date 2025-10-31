"""Signal processor for transforming data to unified signal format."""

from typing import Dict, Any
from datetime import datetime, timezone


class SignalProcessor:
    """Processes and transforms signal data to unified format."""
    
    @staticmethod
    def process_google_trends_signal(
        trend_data: Dict[str, Any],
        region: str = "US"
    ) -> Dict[str, Any]:
        """Process Google Trends data to unified signal format.
        
        Args:
            trend_data: Raw trend data from Google Trends
            region: Region code for the trend
            
        Returns:
            Unified signal dictionary
        """
        # Extract trend name (query)
        name = trend_data.get('query', 'Unknown')
        
        # Extract metrics
        volume = trend_data.get('value', 0)
        
        # Calculate velocity and acceleration (simplified - in real implementation,
        # this would compare with previous time periods)
        velocity = trend_data.get('velocity', 0.0)
        acceleration = trend_data.get('acceleration', 0.0)
        
        # Build metrics dictionary
        metrics = {
            'volume': volume,
            'velocity': velocity,
            'acceleration': acceleration,
            'geographic_spread': [region]
        }
        
        # Build temporal dictionary
        temporal = {
            'first_seen': datetime.now(timezone.utc).isoformat() + 'Z',
            'peak_time': None,  # Would be calculated from time series data
            'current_status': SignalProcessor._determine_status(velocity, acceleration)
        }
        
        # Build unified signal
        signal = {
            'source': 'google_trends',
            'source_id': f"{name}_{region}_{datetime.now(timezone.utc).strftime('%Y%m%d%H')}",
            'signal_type': 'trend',
            'name': name,
            'description': f"Trending search query in {region}",
            'tags': ['google', 'search', 'trend', region.lower()],
            'metrics': metrics,
            'temporal': temporal
        }
        
        return signal
    
    @staticmethod
    def _determine_status(velocity: float, acceleration: float) -> str:
        """Determine current trend status.
        
        Args:
            velocity: Rate of change
            acceleration: Change in velocity
            
        Returns:
            Status string: 'rising', 'peak', or 'declining'
        """
        if velocity > 20 and acceleration > 0:
            return 'rising'
        elif velocity < -20:
            return 'declining'
        else:
            return 'peak'
