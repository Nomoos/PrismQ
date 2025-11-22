"""PrismQ.T.Review.Title.ByScriptAndIdea - AI Title Review Module

AI-powered title evaluation against script content and idea intent.
"""

from .title_review import (
    TitleReview,
    TitleReviewCategory,
    TitleImprovementPoint,
    TitleCategoryScore
)
from .by_script_and_idea import (
    review_title_by_script_and_idea,
    AlignmentAnalysis
)

__all__ = [
    "TitleReview",
    "TitleReviewCategory",
    "TitleImprovementPoint",
    "TitleCategoryScore",
    "review_title_by_script_and_idea",
    "AlignmentAnalysis"
]
