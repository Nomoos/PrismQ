"""PrismQ Model package - Domain entities, repositories, and state management.

This package provides the core domain model for the PrismQ workflow system,
following SOLID principles and clean architecture patterns.

Structure:
    - Entities/: Domain entities (Story, Title, Script, Review, etc.)
    - Repositories/: Data access layer with repository pattern
    - Infrastructure/: Database connection, schema, exceptions
    - State: Workflow state constants and validators

Main exports for convenience:
    - Story, Title, Script, Review: Core domain entities
    - StoryRepository, TitleRepository, etc.: Repository implementations
    - StoryState, StateNames: State machine constants
    - TransitionValidator: State transition validation

Example Usage:
    >>> from Model import Story, StoryState, StoryRepository
    >>> from Model.Infrastructure import get_connection
    >>> 
    >>> conn = get_connection("prismq.db")
    >>> repo = StoryRepository(conn)
    >>> story = Story(idea_id="1", state=StoryState.IDEA_CREATION.value)
"""

# State constants and validators
from Model.state import (
    StoryState,
    StateNames,
    StateCategory,
    TransitionValidator,
    INITIAL_STATES,
    TERMINAL_STATES,
    EXPERT_REVIEW_STATES,
)

# Domain entities
from Model.Entities import (
    Story,
    Title,
    Script,
    Review,
    IdeaSchema,
    IModel,
    IReadable,
)

# Repositories
from Model.Repositories import (
    StoryRepository,
    TitleRepository,
    ScriptRepository,
    ReviewRepository,
    IRepository,
    IUpdatableRepository,
)

# Other models
from Model.published import Published, Language, Platform

__all__ = [
    # State
    "StoryState",
    "StateNames",
    "StateCategory",
    "TransitionValidator",
    "INITIAL_STATES",
    "TERMINAL_STATES",
    "EXPERT_REVIEW_STATES",
    # Entities
    "Story",
    "Title",
    "Script",
    "Review",
    "IdeaSchema",
    "IModel",
    "IReadable",
    # Repositories
    "StoryRepository",
    "TitleRepository",
    "ScriptRepository",
    "ReviewRepository",
    "IRepository",
    "IUpdatableRepository",
    # Other
    "Published",
    "Language",
    "Platform",
]
