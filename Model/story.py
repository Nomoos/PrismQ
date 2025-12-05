"""Story model for PrismQ content workflow.

This module re-exports the Story model from Model.Database.models.story
for backward compatibility.

Story represents a content piece that progresses through the workflow.
It references versioned Title and Script content, along with an Idea.

Relationship Pattern:
    - Story 1:N Title (one story has many title versions)
    - Story 1:N Script (one story has many script versions)
    - Story stores idea_id as reference to Idea table

Note:
    Story is the only model that supports UPDATE operations
    (for state transitions). Other models use INSERT-only pattern.
    
    Current title/script versions are implicit - determined by highest version
    in Title/Script tables via ORDER BY version DESC LIMIT 1.

For new code, prefer importing directly from Model.Database.models.story:
    >>> from Model.Database.models.story import Story
"""

# Re-export Story from the canonical location
from Model.Database.models.story import Story

__all__ = ["Story"]
