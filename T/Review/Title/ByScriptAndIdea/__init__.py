"""PrismQ.T.Review.Title.ByScriptAndIdea - AI Title Review Module

Alias module that re-exports from T.Review.Title.From.Content.Idea.
AI-powered title evaluation against script content and idea intent.
"""

from T.Review.Title.From.Content.Idea import (
    AlignmentAnalysis,
    TitleCategoryScore,
    TitleImprovementPoint,
    TitleReview,
    TitleReviewCategory,
    review_title_by_content_and_idea,
)
from T.Review.Title.From.Content.Idea.by_content_and_idea import (
    analyze_engagement,
    analyze_seo,
    analyze_title_content_alignment,
    analyze_title_idea_alignment,
    extract_keywords,
    generate_improvement_points,
)

__all__ = [
    "TitleReview",
    "TitleReviewCategory",
    "TitleImprovementPoint",
    "TitleCategoryScore",
    "AlignmentAnalysis",
    "review_title_by_content_and_idea",
    "analyze_engagement",
    "analyze_seo",
    "analyze_title_content_alignment",
    "analyze_title_idea_alignment",
    "extract_keywords",
    "generate_improvement_points",
]
