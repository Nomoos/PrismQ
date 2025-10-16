"""
Baseline model for computing percentage scores.

This module defines the Baseline dataclass that maps to the baselines SQL table.
This table tracks baseline values for auditable and reproducible percentage calculations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Baseline:
    """
    Represents a baseline definition used for computing percentage scores.
    
    Attributes:
        id: Unique identifier for the baseline
        scope_type: Determines what the baseline represents ('global', 'platform', 'account', 'segment')
        scope_key: Optional identifier for the scope (platform name, account id, segment key)
        metric: Metric name this baseline applies to (e.g., 'engagement_rate', 'watch_through', 'sentiment')
        platform: Platform name (e.g., 'YouTube', 'TikTok'). None for global baselines
        category: Optional niche/category for the baseline
        region: Optional region (e.g., 'US', 'EU')
        length_bucket: Optional length bucket (e.g., '0-15s', '16-30s', '31-60s')
        window: Time window for the baseline (e.g., 'P28D' rolling, '2025-Q3', '2025-10-01..2025-10-07')
        sample_size: Sample size used to compute the baseline (for confidence assessment)
        baseline_value: Raw baseline value in natural units (e.g., 0.045 = 4.5% engagement)
        baseline_units: Units of the baseline value (e.g., 'ratio', 'seconds', 'count')
        method: Method used to compute the baseline (e.g., 'mean', 'median', 'winsorized_mean', 'EWMA@0.3')
        notes: Free-form audit note for documentation
        computed_at: Timestamp when the baseline was computed
    """
    
    id: str = ""
    scope_type: str = ""
    scope_key: Optional[str] = None
    metric: str = ""
    platform: Optional[str] = None
    category: Optional[str] = None
    region: Optional[str] = None
    length_bucket: Optional[str] = None
    window: str = ""
    sample_size: Optional[int] = None
    baseline_value: float = 0.0
    baseline_units: str = ""
    method: Optional[str] = None
    notes: Optional[str] = None
    computed_at: datetime = field(default_factory=lambda: datetime.min)
