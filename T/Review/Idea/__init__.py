"""Idea Review module for analyzing generated idea variants.

This module provides Worker10's review capabilities for analyzing ideas
generated from Idea.Creation, producing comprehensive reviews containing:
- Gaps analysis
- Pros and cons
- Differences across variants
- Similarity/compatibility with original text
"""

from .idea_review import (
    IdeaReviewGenerator,
    IdeaReviewResult,
    IdeaVariantAnalysis,
    generate_idea_review,
)

__all__ = [
    "IdeaReviewGenerator",
    "IdeaReviewResult",
    "IdeaVariantAnalysis",
    "generate_idea_review",
]
