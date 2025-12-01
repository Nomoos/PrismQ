"""PrismQ.T.Review.Title - Title Review Module

AI-powered title evaluation modules.
"""

# Import v1 review (ByScriptAndIdea - located at From.Script.Idea)
try:
    from .From.Script.Idea import (
        review_title_by_script_and_idea,
        TitleReview,
        TitleReviewCategory,
        TitleImprovementPoint,
        TitleCategoryScore
    )
    _has_v1 = True
except ImportError:
    _has_v1 = False

# Import v2 review (ByScript - located at From.Script)
try:
    from .From.Script import (
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
