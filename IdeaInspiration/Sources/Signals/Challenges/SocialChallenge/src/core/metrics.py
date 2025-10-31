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
    def from_challenge(cls, metrics: Dict[str, Any]) -> 'UniversalMetrics':
        """Create universal metrics from challenge data.
        
        Args:
            metrics: Challenge metrics dictionary
            
        Returns:
            UniversalMetrics instance
        """
        # Extract metrics with defaults
        volume = metrics.get('volume', 0)
        virality = metrics.get('virality', 0.0)
        signal_strength = metrics.get('signal_strength', 0.0)
        
        # Calculate trend strength (0-10 scale)
        trend_strength = signal_strength
        
        # Calculate virality score (0-10 scale)
        virality_score = virality * 10.0  # Convert 0-1 to 0-10
        
        return cls(
            trend_strength=round(trend_strength, 2),
            virality_score=round(virality_score, 2),
            velocity=None,
            acceleration=None,
            geographic_spread=None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return asdict(self)
