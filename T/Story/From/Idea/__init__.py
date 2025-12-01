"""PrismQ.T.Story.From.Idea - Create Story objects from Idea objects.

This module provides functionality to create Story objects from Idea objects
that don't yet have Story references in the database.

The module:
1. Selects the oldest Idea that has no references in the Story table
2. Creates 10 Story objects for that Idea, each with a reference to the Idea
3. Stories are created with state PrismQ.T.Title.From.Idea (ready for title generation)

Workflow Position: Early stage before Title generation
    PrismQ.T.Idea.Creation
        ↓
    PrismQ.T.Story.From.Idea (creates Stories only) ← This module
        ↓
    PrismQ.T.Title.From.Idea (generates Titles for Stories)

Example:
    >>> from T.Story.From.Idea import StoryFromIdeaService, process_oldest_unreferenced_idea
    >>> 
    >>> service = StoryFromIdeaService(db_connection, idea_db)
    >>> 
    >>> # Process the oldest unreferenced idea (main workflow entry point)
    >>> result = service.process_oldest_unreferenced_idea()
    >>> if result:
    ...     print(f"Created {result.count} stories for idea {result.idea_id}")
    >>> 
    >>> # Or use convenience function
    >>> result = process_oldest_unreferenced_idea(db_connection, idea_db)
"""

from T.Story.From.Idea.src.story_from_idea_service import (
    StoryFromIdeaService,
    StoryCreationResult,
    create_stories_from_idea,
    get_unreferenced_ideas,
    process_oldest_unreferenced_idea,
)

__all__ = [
    "StoryFromIdeaService",
    "StoryCreationResult",
    "create_stories_from_idea",
    "get_unreferenced_ideas",
    "process_oldest_unreferenced_idea",
]
