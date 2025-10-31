"""Universal metrics for entertainment release analysis."""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class UniversalMetrics:
    """Universal metrics schema for entertainment release analysis."""
    
    # Release significance metrics
    significance_score: float = 0.0
    content_opportunity: float = 0.0
    audience_interest: float = 0.0
    
    # Timing metrics
    days_until_release: Optional[int] = None
    content_window_start: Optional[str] = None
    content_window_end: Optional[str] = None
    optimal_publish_date: Optional[str] = None
    
    # Scope metrics
    release_scope: Optional[str] = None  # worldwide, limited, exclusive
    media_type: Optional[str] = None  # movie, tv, game, music
    
    # Entertainment-specific metrics
    anticipated_box_office: Optional[int] = None
    franchise_value: Optional[float] = None  # 0-10
    social_buzz: Optional[float] = None  # 0-10
    
    # Platform-specific data
    platform_specific: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.platform_specific is None:
            self.platform_specific = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_entertainment_release(cls, release_data: Dict[str, Any]) -> 'UniversalMetrics':
        """Create metrics from entertainment release data."""
        scope = release_data.get('scope', 'limited')
        importance = release_data.get('importance', 'moderate')
        media_type = release_data.get('media_type', 'movie')
        
        scope_scores = {'worldwide': 10.0, 'limited': 6.0, 'exclusive': 4.0}
        importance_multiplier = {'blockbuster': 1.3, 'major': 1.0, 'moderate': 0.7, 'indie': 0.4}
        
        base_score = scope_scores.get(scope, 6.0)
        multiplier = importance_multiplier.get(importance, 0.7)
        significance = min(10.0, base_score * multiplier)
        
        content_opp = significance * 0.88
        audience_base = base_score * 0.85
        if release_data.get('franchise', False):
            audience_base *= 1.4
        
        audience_interest = min(10.0, audience_base)
        
        release_date = release_data.get('date')
        days_until = None
        if release_date:
            try:
                # Handle date-only format (YYYY-MM-DD) from TMDB
                if 'T' not in str(release_date) and len(str(release_date)) == 10:
                    # Date only, add midnight time
                    release_dt = datetime.strptime(str(release_date), '%Y-%m-%d')
                else:
                    # Full datetime with potential timezone
                    release_dt = datetime.fromisoformat(release_date.replace('Z', '+00:00'))
                
                days_until = (release_dt - datetime.now()).days
            except (ValueError, TypeError):
                pass
        
        return cls(
            significance_score=round(significance, 2),
            content_opportunity=round(content_opp, 2),
            audience_interest=round(audience_interest, 2),
            days_until_release=days_until,
            release_scope=scope,
            media_type=media_type,
            anticipated_box_office=release_data.get('anticipated_box_office'),
            franchise_value=release_data.get('franchise_value'),
            social_buzz=release_data.get('social_buzz'),
            platform_specific=release_data.get('platform_specific', {})
        )
