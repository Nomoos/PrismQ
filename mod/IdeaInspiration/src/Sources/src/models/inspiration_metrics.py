"""
Inspiration metrics model for normalized metrics.

This module defines the InspirationMetrics dataclass that maps to the inspiration_metrics SQL table.
Note: All percentage fields are INTEGER % (unbounded on high side), where 100 = baseline.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class InspirationMetrics:
    """
    Represents normalized metrics for an inspiration item.
    
    All percentage fields are INTEGER % (unbounded on high side), where 100 = baseline.
    
    Attributes:
        id: Unique identifier for the metrics
        inspiration_item_id: Reference to the inspiration item
        views: Number of views
        likes: Number of likes
        comments: Number of comments
        shares: Number of shares
        saves: Number of saves
        avg_watch_time_sec: Average watch time in seconds
        length_sec: Length in seconds
        conversions: Number of conversions
        engagement_rate_pct: Engagement rate as INTEGER % vs baseline (>= 0). 100 = baseline, >100 indicates viral potential
        watch_through_pct: Watch-through rate as INTEGER % vs baseline (>= 0). 100 = baseline
        conversion_rate_pct: Conversion rate as INTEGER % vs baseline (>= 0). 100 = baseline
        rpi_engagement: Relative Performance Index for engagement vs baseline (>= 0). 100 = baseline
        rpi_watch_through: Relative Performance Index for watch-through vs baseline (>= 0). 100 = baseline
        computed_at: Timestamp when metrics were computed
        engagement_baseline_id: Link to baseline used for engagement computation (audit trail)
        watch_through_baseline_id: Link to baseline used for watch-through computation (audit trail)
        conversion_baseline_id: Link to baseline used for conversion computation (audit trail)
    """
    
    id: str = ""
    inspiration_item_id: str = ""
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    saves: Optional[int] = None
    avg_watch_time_sec: Optional[float] = None
    length_sec: Optional[float] = None
    conversions: Optional[int] = None
    engagement_rate_pct: Optional[int] = None
    watch_through_pct: Optional[int] = None
    conversion_rate_pct: Optional[int] = None
    rpi_engagement: Optional[int] = None
    rpi_watch_through: Optional[int] = None
    computed_at: datetime = field(default_factory=lambda: datetime.min)
    engagement_baseline_id: Optional[str] = None
    watch_through_baseline_id: Optional[str] = None
    conversion_baseline_id: Optional[str] = None
