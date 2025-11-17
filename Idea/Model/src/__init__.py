"""PrismQ.Idea.Model - Core data model for content ideas.

This package provides the Idea model for representing distilled/fused
content concepts in the PrismQ content creation workflow.
"""

from .idea import (
    Idea,
    IdeaStatus,
    TargetPlatform,
    ContentGenre,
)
from .idea_db import (
    IdeaDatabase,
    setup_database,
)

__all__ = [
    "Idea",
    "IdeaStatus",
    "TargetPlatform",
    "ContentGenre",
    "IdeaDatabase",
    "setup_database",
]

__version__ = "0.1.0"
