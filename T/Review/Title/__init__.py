"""PrismQ.T.Review.Title - Title Review Module

AI-powered title evaluation modules.
"""

# Import v1 review (ByScriptAndIdea)
try:
    from .ByScriptAndIdea import (
        review_title_by_script_and_idea,
        TitleReview,
        TitleReviewCategory,
        TitleImprovementPoint,
        TitleCategoryScore
    )
    _has_v1 = True
except ImportError:
    _has_v1 = False

# Import v2 review (ByScript)
try:
    from .ByScript import (
        review_title_by_script_v2,
        compare_reviews,
        get_improvement_summary,
        ImprovementComparison
    )
    _has_v2 = True
except ImportError:
    _has_v2 = False

__all__ = []

if _has_v1:
    __all__.extend([
        "review_title_by_script_and_idea",
        "TitleReview",
        "TitleReviewCategory",
        "TitleImprovementPoint",
        "TitleCategoryScore"
    ])

if _has_v2:
    __all__.extend([
        "review_title_by_script_v2",
        "compare_reviews",
        "get_improvement_summary",
        "ImprovementComparison"
    ])
