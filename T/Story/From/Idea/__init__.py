"""PrismQ.T.Story.From.Idea - Create Story objects from Idea objects.

This module provides functionality to create Story objects from Idea objects
that don't yet have Story references in the database.

The module:
1. Loads Idea objects that have no references in the Story table
2. Creates 10 Story objects per Idea, each with just a reference to the Idea
3. Stories are created in CREATED state (without Title or Script)

Workflow Position: Early stage before Title generation
    PrismQ.T.Idea.Creation
        ↓
    PrismQ.T.Story.From.Idea (creates Stories only) ← This module
        ↓
    PrismQ.T.Title.From.Idea (generates Titles for Stories)

Example:
    >>> from T.Story.From.Idea import StoryFromIdeaService
    >>> 
    >>> service = StoryFromIdeaService(db_connection, idea_db)
    >>> 
    >>> # Get unreferenced ideas and create stories
    >>> results = service.process_unreferenced_ideas()
    >>> print(f"Created stories for {len(results)} ideas")
"""

from T.Story.From.Idea.src.story_from_idea_service import (
    StoryFromIdeaService,
    StoryCreationResult,
    create_stories_from_idea,
    get_unreferenced_ideas,
)

__all__ = [
    "StoryFromIdeaService",
    "StoryCreationResult",
    "create_stories_from_idea",
    "get_unreferenced_ideas",
]
