"""PrismQ.T.Review.Title - Title Review Module

AI-powered title evaluation modules.
"""

# Import v1 review (located at From.Content.Idea)
try:
    from .From.Content.Idea import (
        TitleCategoryScore,
        TitleImprovementPoint,
        TitleReview,
        TitleReviewCategory,
        review_title_from_content_idea,
    )

    _has_v1 = True
except ImportError:
    _has_v1 = False

# Import v2 review (FromContent - located at From.Content)
try:
    from .From.Content import (
        ImprovementComparison,
        compare_reviews,
        get_improvement_summary,
        review_title_from_content_v2,
    )

    _has_v2 = True
except ImportError:
    _has_v2 = False

__all__ = []

if _has_v1:
    __all__.extend(
        [
            "review_title_from_content_idea",
            "TitleReview",
            "TitleReviewCategory",
            "TitleImprovementPoint",
            "TitleCategoryScore",
        ]
    )

if _has_v2:
    __all__.extend(
        [
            "review_title_from_content_v2",
            "compare_reviews",
            "get_improvement_summary",
            "ImprovementComparison",
        ]
    )
