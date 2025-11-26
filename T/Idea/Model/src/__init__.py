"""PrismQ.Idea.Model - Core data model for content ideas.

This package provides the Idea model for representing distilled/fused
content concepts in the PrismQ content creation workflow.

Extended with:
- Multi-language story translation support
- SimpleIdea model for prompt-based idea storage (referenced by Story via FK)
- Idea prompt templates for content generation
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
from .simple_idea import (
    SimpleIdea,
    IdeaPromptTemplates,
    EXAMPLE_IDEAS,
)
from .simple_idea_db import (
    SimpleIdeaDatabase,
    setup_simple_idea_database,
)

__all__ = [
    # Original Idea model
    "Idea",
    "IdeaStatus",
    "ContentGenre",
    "IdeaDatabase",
    "setup_database",
    # Translation support
    "StoryTranslation",
    "TranslationStatus",
    "TranslationFeedback",
    "MEANING_SCORE_THRESHOLD",
    # SimpleIdea model (prompt-based, referenced by Story via FK)
    "SimpleIdea",
    "IdeaPromptTemplates",
    "EXAMPLE_IDEAS",
    "SimpleIdeaDatabase",
    "setup_simple_idea_database",
]

__version__ = "0.1.0"
