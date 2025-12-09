"""PrismQ.T.Review.Content.ByTitle - Content Review Against Title and Idea

AI-powered script evaluation that reviews scripts against titles and ideas.
Provides structured feedback on alignment, flow, completeness, and gaps.

Supports:
- v1 reviews: Initial script against initial title
- v2+ reviews: Refined scripts against refined titles with improvement tracking
"""

from .by_title_v2 import (
    ImprovementComparison,
    compare_reviews,
    extract_improvements_from_review,
    get_next_steps,
    is_ready_to_proceed,
    review_content_by_title_v2,
)
from .script_review_by_title import AlignmentScore, review_content_by_title

__all__ = [
    "review_content_by_title",
    "AlignmentScore",
    "review_content_by_title_v2",
    "ImprovementComparison",
    "compare_reviews",
    "extract_improvements_from_review",
    "is_ready_to_proceed",
    "get_next_steps",
]
