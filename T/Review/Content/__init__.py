"""PrismQ.T.Review.Content - AI Content Review Module

AI-powered content evaluation with scoring and improvement recommendations.
"""

try:
    from .review_content_from_title_idea import AlignmentScore, review_content_from_title_idea
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
        "review_content_from_title_idea",
        "AlignmentScore",
    ]
except ImportError:
    # Imports may fail when review_content_from_title_idea.py uses non-relative imports
    # (requires T/Review/Content in sys.path). This is safe to ignore.
    pass
