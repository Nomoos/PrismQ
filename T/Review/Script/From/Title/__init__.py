"""PrismQ.T.Review.Script.ByTitle - Script Review Against Title and Idea

AI-powered script evaluation that reviews scripts against titles and ideas.
Provides structured feedback on alignment, flow, completeness, and gaps.

Supports:
- v1 reviews: Initial script against initial title
- v2+ reviews: Refined scripts against refined titles with improvement tracking
"""

from .script_review_by_title import (
    review_script_by_title,
    AlignmentScore
)
from .by_title_v2 import (
    review_script_by_title_v2,
    ImprovementComparison,
    compare_reviews,
    extract_improvements_from_review,
    is_ready_to_proceed,
    get_next_steps
)

__all__ = [
    "review_script_by_title",
    "AlignmentScore",
    "review_script_by_title_v2",
    "ImprovementComparison",
    "compare_reviews",
    "extract_improvements_from_review",
    "is_ready_to_proceed",
    "get_next_steps"
]
