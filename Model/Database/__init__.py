"""PrismQ Database module - DEPRECATED, use Model directly.

This module provides backward compatibility imports.
New code should import from Model directly:
    >>> from Model import Story, StoryRepository
    >>> from Model.entities import Story
    >>> from Model.repositories import StoryRepository
    >>> from Model.infrastructure import get_connection
"""

# Re-export entities for backward compatibility
from Model.entities import (
    Story,
    Title,
    Script,
    Review,
    IdeaSchema,
    IModel,
    IReadable,
)

# Re-export repositories
from Model.repositories import (
    StoryRepository,
    TitleRepository,
    ScriptRepository,
    ReviewRepository,
    IRepository,
    IUpdatableRepository,
)

# Re-export infrastructure
from Model.infrastructure import (
    get_connection,
    connection_context,
    initialize_database,
    SchemaManager,
    DatabaseException,
    EntityNotFoundError,
    DuplicateEntityError,
    ForeignKeyViolationError,
    ConstraintViolationError,
    DatabaseConnectionError,
    DataIntegrityError,
    InvalidStateTransitionError,
    map_sqlite_error,
)

# Re-export state
from Model.state import StoryState

__all__ = [
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
    # Infrastructure
    "get_connection",
    "connection_context",
    "initialize_database",
    "SchemaManager",
    "DatabaseException",
    "EntityNotFoundError",
    "DuplicateEntityError",
    "ForeignKeyViolationError",
    "ConstraintViolationError",
    "DatabaseConnectionError",
    "DataIntegrityError",
    "InvalidStateTransitionError",
    "map_sqlite_error",
    # State
    "StoryState",
]
