"""PrismQ.Idea.Model - Core data model for content ideas.

This package provides the Idea model for representing distilled/fused
content concepts in the PrismQ content creation workflow.

Extended with multi-language story translation support.
"""

from .idea import (
    Idea,
    IdeaStatus,
    ContentGenre,
)
from .idea_db import (
    IdeaDatabase,
    setup_database,
)
from .story_translation import (
    StoryTranslation,
    TranslationStatus,
    TranslationFeedback,
    MEANING_SCORE_THRESHOLD,
)

__all__ = [
    "Idea",
    "IdeaStatus",
    "ContentGenre",
    "IdeaDatabase",
    "setup_database",
    "StoryTranslation",
    "TranslationStatus",
    "TranslationFeedback",
    "MEANING_SCORE_THRESHOLD",
]

__version__ = "0.1.0"
