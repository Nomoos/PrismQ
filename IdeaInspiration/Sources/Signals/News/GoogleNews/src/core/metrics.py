"""Universal metrics calculation for signals."""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class UniversalMetrics:
    """Universal metrics for cross-platform signal comparison."""
    
    trend_strength: Optional[float] = None  # 0-10 scale
    virality_score: Optional[float] = None  # 0-10 scale
    velocity: Optional[float] = None  # % change rate
    acceleration: Optional[float] = None  # % change in velocity
    geographic_spread: Optional[int] = None  # Number of regions
    
    @classmethod
    def from_google_news(cls, metrics: Dict[str, Any]) -> 'UniversalMetrics':
        """Create universal metrics from Google Trends data.
        
        Args:
            metrics: Google Trends metrics dictionary
            
        Returns:
            UniversalMetrics instance
        """
        # Extract metrics with defaults
        volume = metrics.get('volume', 0)
        velocity = metrics.get('velocity', 0.0)
        acceleration = metrics.get('acceleration', 0.0)
        geographic_spread = len(metrics.get('geographic_spread', []))
        
        # Calculate trend strength (0-10 scale)
        # Based on search volume normalized to 0-10
        trend_strength = min(10.0, (volume / 100.0) * 10.0) if volume else 0.0
        
        # Calculate virality score (0-10 scale)
        # Based on velocity and acceleration
        virality_score = 0.0
        if velocity > 0:
            # Weight velocity more heavily than acceleration
            virality_score = min(10.0, (velocity / 50.0) * 7.0 + (acceleration / 50.0) * 3.0)
        
        return cls(
            trend_strength=round(trend_strength, 2),
            virality_score=round(virality_score, 2),
            velocity=round(velocity, 2),
            acceleration=round(acceleration, 2),
            geographic_spread=geographic_spread
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return asdict(self)
