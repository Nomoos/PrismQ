"""PrismQ.T.Review.Title.ByScript - Title Review v2 Module

AI-powered title evaluation for v2+ iterations with improvement tracking.
"""

from .by_script_v2 import (
    ImprovementComparison,
    compare_reviews,
    get_improvement_summary,
    review_title_by_script_v2,
)

__all__ = [
    "review_title_by_script_v2",
    "compare_reviews",
    "get_improvement_summary",
    "ImprovementComparison",
]
