"""Universal metrics for event-based content analysis."""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime, date


@dataclass
class UniversalMetrics:
    """Universal metrics schema for event analysis."""
    
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
    cultural_scope: Optional[str] = None    # universal, cultural, niche
    demographic_reach: Optional[str] = None  # broad, targeted, specific
    
    # Historical metrics
    historical_search_volume: Optional[int] = None
    year_over_year_growth: Optional[float] = None
    
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
    def from_holiday(cls, holiday_data: Dict[str, Any]) -> 'UniversalMetrics':
        """Create metrics from holiday data.
        
        Args:
            holiday_data: Dictionary containing holiday information
            
        Returns:
            UniversalMetrics instance
        """
        # Calculate significance based on scope and type
        scope = holiday_data.get('scope', 'local')
        importance = holiday_data.get('importance', 'minor')
        
        # Base significance scoring
        scope_scores = {
            'global': 10.0,
            'national': 7.0,
            'regional': 5.0,
            'local': 3.0
        }
        
        importance_multiplier = {
            'major': 1.0,
            'moderate': 0.7,
            'minor': 0.4
        }
        
        base_score = scope_scores.get(scope, 3.0)
        multiplier = importance_multiplier.get(importance, 0.5)
        significance = base_score * multiplier
        
        # Calculate content opportunity (slightly lower than significance)
        content_opp = significance * 0.9
        
        # Calculate audience interest (based on scope and recurrence)
        recurring = holiday_data.get('recurring', False)
        audience_base = base_score * 0.8
        if recurring:
            audience_base *= 1.2  # Recurring events have more interest
        
        audience_interest = min(10.0, audience_base)
        
        # Calculate timing
        event_date = holiday_data.get('date')
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
                
                # Content window based on pre/post event days
                pre_days = holiday_data.get('pre_event_days', 14)
                post_days = holiday_data.get('post_event_days', 7)
                
                from datetime import timedelta
                window_start = event_dt - timedelta(days=pre_days)
                window_end = event_dt + timedelta(days=post_days)
                
                content_window_start = window_start.isoformat()
                content_window_end = window_end.isoformat()
                
                # Optimal publish is usually a week before
                optimal_dt = event_dt - timedelta(days=7)
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
            cultural_scope=holiday_data.get('cultural_scope'),
            demographic_reach=holiday_data.get('demographic_reach'),
            platform_specific=holiday_data.get('platform_specific', {})
        )
