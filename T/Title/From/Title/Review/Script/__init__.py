"""Title FromOriginalTitleAndReviewAndScript module.

This module implements MVP-006: Generate improved title v2 using feedback
from both title review (MVP-004) and script review (MVP-005).
"""

from .src.title_improver import (
    TitleImprover,
    ImprovedTitle,
    TitleVersion,
    improve_title_from_reviews
)

__all__ = [
    'TitleImprover',
    'ImprovedTitle',
    'TitleVersion',
    'improve_title_from_reviews'
]
