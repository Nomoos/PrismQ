"""Universal metrics for sports event analysis."""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class UniversalMetrics:
    """Universal metrics schema for sports event analysis."""
    
    # Event significance metrics
    significance_score: float = 0.0  # Overall significance (0-10)
    content_opportunity: float = 0.0  # Content opportunity score (0-10)
    audience_interest: float = 0.0    # Estimated audience interest (0-10)
    
    # Timing metrics
    days_until_event: Optional[int] = None
    content_window_start: Optional[str] = None  # ISO date
    content_window_end: Optional[str] = None    # ISO date
    optimal_publish_date: Optional[str] = None  # ISO date
    
    # Scope metrics
    geographic_scope: Optional[str] = None  # global, national, regional, local
    competition_level: Optional[str] = None  # international, professional, amateur
    
    # Sports-specific metrics
    expected_viewership: Optional[int] = None
    rivalry_intensity: Optional[float] = None  # 0-10
    championship_stakes: Optional[bool] = None
    
    # Platform-specific data
    platform_specific: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize empty dict for platform_specific if None."""
        if self.platform_specific is None:
            self.platform_specific = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary.
        
        Returns:
            Dictionary representation of metrics
        """
        return asdict(self)
    
    @classmethod
    def from_sports_event(cls, event_data: Dict[str, Any]) -> 'UniversalMetrics':
        """Create metrics from sports event data.
        
        Args:
            event_data: Dictionary containing sports event information
            
        Returns:
            UniversalMetrics instance
        """
        # Calculate significance based on competition level and type
        scope = event_data.get('scope', 'regional')
        importance = event_data.get('importance', 'moderate')
        competition_level = event_data.get('competition_level', 'professional')
        
        # Base significance scoring
        scope_scores = {
            'global': 10.0,
            'international': 9.0,
            'national': 7.0,
            'regional': 5.0,
            'local': 3.0
        }
        
        importance_multiplier = {
            'championship': 1.2,
            'playoff': 1.0,
            'major': 1.0,
            'regular': 0.7,
            'moderate': 0.7,
            'minor': 0.4
        }
        
        base_score = scope_scores.get(scope, 5.0)
        multiplier = importance_multiplier.get(importance, 0.7)
        significance = min(10.0, base_score * multiplier)
        
        # Calculate content opportunity
        content_opp = significance * 0.85
        
        # Calculate audience interest
        audience_base = base_score * 0.9
        if event_data.get('rivalry', False):
            audience_base *= 1.3  # Rivalry games have more interest
        if event_data.get('championship', False):
            audience_base *= 1.4  # Championships have even more interest
        
        audience_interest = min(10.0, audience_base)
        
        # Calculate timing
        event_date = event_data.get('date')
        days_until = None
        content_window_start = None
        content_window_end = None
        optimal_publish = None
        
        if event_date:
            try:
                if isinstance(event_date, str):
                    event_dt = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
                else:
                    event_dt = event_date
                
                today = datetime.now()
                days_until = (event_dt - today).days
                
                # Content window for sports events
                pre_days = event_data.get('pre_event_days', 7)
                post_days = event_data.get('post_event_days', 3)
                
                from datetime import timedelta
                window_start = event_dt - timedelta(days=pre_days)
                window_end = event_dt + timedelta(days=post_days)
                
                content_window_start = window_start.isoformat()
                content_window_end = window_end.isoformat()
                
                # Optimal publish is usually 1-2 days before
                optimal_dt = event_dt - timedelta(days=2)
                optimal_publish = optimal_dt.isoformat()
                
            except (ValueError, TypeError):
                pass
        
        return cls(
            significance_score=round(significance, 2),
            content_opportunity=round(content_opp, 2),
            audience_interest=round(audience_interest, 2),
            days_until_event=days_until,
            content_window_start=content_window_start,
            content_window_end=content_window_end,
            optimal_publish_date=optimal_publish,
            geographic_scope=scope,
            competition_level=competition_level,
            expected_viewership=event_data.get('expected_viewership'),
            rivalry_intensity=event_data.get('rivalry_intensity'),
            championship_stakes=event_data.get('championship', False),
            platform_specific=event_data.get('platform_specific', {})
        )
