"""Universal metrics for community sources."""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CommunityMetrics:
    """Universal metrics for community content.
    
    Follows the Data Transfer Object pattern for clean data encapsulation.
    """
    engagement_score: float = 0.0
    relevance_score: float = 0.0
    actionability: float = 0.0
    sentiment_score: float = 0.0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommunityMetrics':
        """Create metrics from dictionary.
        
        Args:
            data: Dictionary with metric values
            
        Returns:
            CommunityMetrics instance
        """
        return cls(
            engagement_score=data.get('engagement_score', 0.0),
            relevance_score=data.get('relevance_score', 0.0),
            actionability=data.get('actionability', 0.0),
            sentiment_score=data.get('sentiment_score', 0.0)
        )
    
    @classmethod
    def from_community_signal(cls, signal: Dict[str, Any]) -> 'CommunityMetrics':
        """Create metrics from community signal dictionary.
        
        Args:
            signal: Community signal dictionary
            
        Returns:
            CommunityMetrics instance
        """
        universal = signal.get('universal_metrics', {})
        analysis = signal.get('analysis', {})
        
        return cls(
            engagement_score=universal.get('engagement_score', 0.0),
            relevance_score=universal.get('relevance_score', 0.0),
            actionability=universal.get('actionability', 0.0),
            sentiment_score=analysis.get('sentiment_score', 0.0)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary.
        
        Returns:
            Dictionary with all metrics
        """
        return {
            'engagement_score': self.engagement_score,
            'relevance_score': self.relevance_score,
            'actionability': self.actionability,
            'sentiment_score': self.sentiment_score
        }
    
    def calculate_overall_score(self) -> float:
        """Calculate overall score from all metrics.
        
        Returns:
            Overall score (weighted average, 0-10)
        """
        # Weight different metrics
        weights = {
            'engagement': 0.25,
            'relevance': 0.25,
            'actionability': 0.35,
            'sentiment': 0.15
        }
        
        # Normalize sentiment_score from -1..1 to 0..10
        normalized_sentiment = (self.sentiment_score + 1) * 5
        
        overall = (
            self.engagement_score * weights['engagement'] +
            self.relevance_score * weights['relevance'] +
            self.actionability * weights['actionability'] +
            normalized_sentiment * weights['sentiment']
        )
        
        return round(overall, 2)
