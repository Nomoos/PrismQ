"""Score breakdown models for PrismQ.IdeaInspiration.Scoring.

This module defines the score breakdown structure returned by the scoring engine.
The IdeaInspiration model itself should be imported from the PrismQ.IdeaCollector
or similar module - this scoring module enriches existing IdeaInspiration objects
with detailed scoring information.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ScoreBreakdown:
    """Detailed score breakdown for an IdeaInspiration object.
    
    This class provides comprehensive scoring details for different aspects
    of content, acting as an enrichment layer for IdeaInspiration objects.
    
    Attributes:
        overall_score: Combined overall score (0-100)
        title_score: Score for title quality and effectiveness
        description_score: Score for description quality
        text_quality_score: Score for content text quality
        engagement_score: Score based on engagement metrics (if available)
        readability_score: Text readability score
        sentiment_score: Sentiment analysis score
        seo_score: SEO optimization score (placeholder for future)
        tags_score: Tags quality and relevance score (placeholder for future)
        similarity_score: Content similarity score (placeholder for future)
        score_details: Detailed breakdown with all metrics
    """
    
    overall_score: float
    title_score: float = 0.0
    description_score: float = 0.0
    text_quality_score: float = 0.0
    engagement_score: float = 0.0
    readability_score: float = 0.0
    sentiment_score: float = 0.0
    seo_score: float = 0.0
    tags_score: float = 0.0
    similarity_score: float = 0.0
    score_details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ScoreBreakdown to dictionary.
        
        Returns:
            Dictionary representation of the score breakdown
        """
        return {
            'overall_score': self.overall_score,
            'title_score': self.title_score,
            'description_score': self.description_score,
            'text_quality_score': self.text_quality_score,
            'engagement_score': self.engagement_score,
            'readability_score': self.readability_score,
            'sentiment_score': self.sentiment_score,
            'seo_score': self.seo_score,
            'tags_score': self.tags_score,
            'similarity_score': self.similarity_score,
            'score_details': self.score_details
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScoreBreakdown':
        """Create ScoreBreakdown from dictionary.
        
        Args:
            data: Dictionary containing score breakdown data
            
        Returns:
            ScoreBreakdown instance
        """
        return cls(
            overall_score=data.get('overall_score', 0.0),
            title_score=data.get('title_score', 0.0),
            description_score=data.get('description_score', 0.0),
            text_quality_score=data.get('text_quality_score', 0.0),
            engagement_score=data.get('engagement_score', 0.0),
            readability_score=data.get('readability_score', 0.0),
            sentiment_score=data.get('sentiment_score', 0.0),
            seo_score=data.get('seo_score', 0.0),
            tags_score=data.get('tags_score', 0.0),
            similarity_score=data.get('similarity_score', 0.0),
            score_details=data.get('score_details', {})
        )
