"""PrismQ.T.Script.Review - AI Script Review Module

AI-powered script evaluation with scoring and improvement recommendations.
"""

from .script_review import (
    ScriptReview,
    ScriptVersion,
    ReviewCategory,
    ContentLength,
    ImprovementPoint,
    CategoryScore
)
from .by_title_and_idea import (
    review_script_by_title_and_idea,
    AlignmentScore
)

# Import ByTitle submodule
from . import ByTitle

# Import Acceptance module (MVP-013)
from .Acceptance import (
    check_script_acceptance,
    ScriptAcceptanceResult
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
    "ByTitle",
    "check_script_acceptance",
    "ScriptAcceptanceResult"
]
