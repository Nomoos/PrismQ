"""Title Improvement module - Generate improved titles from review feedback.

This module implements MVP-006: Title Improvements v2.

Public exports:
    - TitleImprover: Main class for generating improved titles
    - ImprovedTitle: Result object with new version and rationale
    - TitleVersion: Version tracking for titles
    - improve_title_from_reviews: Convenience function
"""

from .title_improver import (
    ImprovedTitle,
    TitleImprover,
    TitleVersion,
    improve_title_from_reviews,
)

__all__ = ["TitleImprover", "ImprovedTitle", "TitleVersion", "improve_title_from_reviews"]
