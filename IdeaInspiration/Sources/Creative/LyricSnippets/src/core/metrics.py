"""Universal metrics schema for creative resources.

This module defines a standardized metrics structure for creative content
including lyrics, narratives, and visual aesthetics.
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List


@dataclass
class CreativeMetrics:
    """Universal metrics schema for creative resource analysis.
    
    This schema standardizes metrics for creative content to enable
    consistent analysis and inspiration value calculation.
    """
    
    # === Core Creative Metrics ===
    emotional_impact: float = 0.0      # 0-10 scale
    versatility: float = 0.0           # 0-10 scale (reusability)
    inspiration_value: float = 0.0     # 0-10 scale
    
    # === Content Characteristics ===
    content_type: str = "lyrics"       # lyrics|narrative|visual
    content_format: str = "text"       # text|image|video|audio
    content_length: Optional[int] = None  # Character/word count or duration
    
    # === Thematic Elements ===
    themes: List[str] = field(default_factory=list)  # ['love', 'loss', 'triumph']
    mood: Optional[str] = None         # melancholic|uplifting|dramatic
    style: Optional[str] = None        # modern|classical|abstract
    
    # === Source Attribution ===
    creator: Optional[str] = None      # Artist/author name
    work_title: Optional[str] = None   # Original work
    license_type: Optional[str] = None # CC-BY|All Rights Reserved|etc
    
    # === Usage Context ===
    genre: Optional[str] = None        # Musical/narrative/visual genre
    cultural_relevance: Optional[float] = None  # 0-10 scale
    trend_score: Optional[float] = None         # 0-10 scale
    
    # === Engagement Metrics (if available) ===
    popularity_score: Optional[float] = None    # Platform-dependent
    shares_count: Optional[int] = None
    saves_count: Optional[int] = None
    
    # === Platform Context ===
    platform: str = "manual"           # genius|unsplash|manual|etc
    source_url: Optional[str] = None
    collection_date: Optional[str] = None  # ISO format
    
    # === Raw Platform Data ===
    platform_specific: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_derived_metrics(self):
        """Calculate derived metrics from raw data."""
        # Average of core metrics for overall score
        if self.emotional_impact or self.versatility or self.inspiration_value:
            scores = [s for s in [self.emotional_impact, self.versatility, self.inspiration_value] if s > 0]
            if scores:
                self.inspiration_value = sum(scores) / len(scores)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format.
        
        Returns:
            Dictionary representation of metrics
        """
        return asdict(self)
    
    @classmethod
    def from_genius(cls, genius_data: Dict[str, Any]) -> 'CreativeMetrics':
        """Create CreativeMetrics from Genius API data.
        
        Args:
            genius_data: Data from Genius API
            
        Returns:
            CreativeMetrics instance
        """
        stats = genius_data.get('stats', {})
        
        metrics = cls(
            content_type='lyrics',
            content_format='text',
            platform='genius',
            source_url=genius_data.get('url'),
            creator=genius_data.get('primary_artist', {}).get('name'),
            work_title=genius_data.get('title'),
            popularity_score=stats.get('pageviews', 0) / 10000,  # Normalize
            platform_specific=genius_data
        )
        
        # Estimate emotional impact from hot score
        if stats.get('hot'):
            metrics.emotional_impact = min(stats.get('hot', 0) / 1000, 10.0)
        
        # Set default values for metrics
        metrics.versatility = 5.0  # Default medium versatility
        metrics.inspiration_value = 5.0
        
        metrics.calculate_derived_metrics()
        return metrics
    
    @classmethod
    def from_manual(cls, resource_data: Dict[str, Any]) -> 'CreativeMetrics':
        """Create CreativeMetrics from manually imported data.
        
        Args:
            resource_data: Manually curated resource data
            
        Returns:
            CreativeMetrics instance
        """
        # Get explicit inspiration_value or default
        inspiration_value = resource_data.get('inspiration_value', 5.0)
        
        metrics = cls(
            content_type=resource_data.get('type', 'lyrics'),
            content_format=resource_data.get('format', 'text'),
            platform='manual',
            creator=resource_data.get('creator'),
            work_title=resource_data.get('work_title'),
            license_type=resource_data.get('license'),
            emotional_impact=resource_data.get('emotional_impact', 5.0),
            versatility=resource_data.get('versatility', 5.0),
            inspiration_value=inspiration_value,
            themes=resource_data.get('themes', []),
            mood=resource_data.get('mood'),
            style=resource_data.get('style'),
            platform_specific=resource_data
        )
        
        # Only recalculate if inspiration_value wasn't explicitly set
        if 'inspiration_value' not in resource_data:
            metrics.calculate_derived_metrics()
        
        return metrics
