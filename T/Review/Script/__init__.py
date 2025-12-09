"""PrismQ.T.Content.Review - AI Content Review Module

AI-powered script evaluation with scoring and improvement recommendations.
"""

# Import submodules
from . import Grammar

# Import Acceptance module (MVP-013)
from .Acceptance import ScriptAcceptanceResult, check_content_acceptance
from .by_title_and_idea import AlignmentScore, review_content_by_title_and_idea
from .script_review import (
    CategoryScore,
    ContentLength,
    ImprovementPoint,
    ReviewCategory,
    ScriptReview,
    ScriptVersion,
)

__all__ = [
    "ScriptReview",
    "ScriptVersion",
    "ReviewCategory",
    "ContentLength",
    "ImprovementPoint",
    "CategoryScore",
    "review_content_by_title_and_idea",
    "AlignmentScore",
    "Grammar",
    "check_content_acceptance",
    "ScriptAcceptanceResult",
]
