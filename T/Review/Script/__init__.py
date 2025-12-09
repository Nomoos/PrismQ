"""PrismQ.T.Script.Review - AI Script Review Module

AI-powered script evaluation with scoring and improvement recommendations.
"""

# Import submodules
from . import Grammar

# Import Acceptance module (MVP-013)
from .Acceptance import ScriptAcceptanceResult, check_script_acceptance
from .by_title_and_idea import AlignmentScore, review_script_by_title_and_idea
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
    "review_script_by_title_and_idea",
    "AlignmentScore",
    "Grammar",
    "check_script_acceptance",
    "ScriptAcceptanceResult",
]
