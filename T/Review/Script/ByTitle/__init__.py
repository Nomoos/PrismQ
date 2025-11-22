"""PrismQ.T.Review.Script.ByTitle - Script Review Against Title and Idea

AI-powered script evaluation that reviews script v1 against title v1 and idea.
Provides structured feedback on alignment, flow, completeness, and gaps.
"""

from .script_review_by_title import (
    review_script_by_title,
    AlignmentScore
)

__all__ = [
    "review_script_by_title",
    "AlignmentScore"
]
