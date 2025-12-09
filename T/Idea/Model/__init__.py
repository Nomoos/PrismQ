"""PrismQ.Idea.Model

Core data model for content ideas in the PrismQ ecosystem.

This module provides the Idea data model which represents distilled/fused
concepts derived from IdeaInspiration instances. Ideas serve as the foundation
for creative content generation in the workflow:

    IdeaInspiration → Idea → Script → Proofreading → Publishing

Example:
    >>> from idea import Idea, ContentGenre
    >>>
    >>> idea = Idea(
    ...     title="The Digital Phantom Mystery",
    ...     concept="An investigation into unsolved internet mysteries",
    ...     purpose="Engage true crime audience with unique digital angle",
    ...     target_platform="youtube",
    ...     genre=ContentGenre.TRUE_CRIME
    ... )
"""

from src.idea import (
    ContentGenre,
    Idea,
    IdeaStatus,
)

__all__ = [
    "Idea",
    "IdeaStatus",
    "ContentGenre",
]

__version__ = "0.1.0"
