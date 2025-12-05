"""Story model for PrismQ content workflow.

This module re-exports the Story model from Model.entities.story
for backward compatibility.

For new code, prefer importing directly:
    >>> from Model import Story  # Recommended
    >>> from Model.entities import Story  # Also valid
"""

# Re-export Story from the canonical location
from Model.entities.story import Story

__all__ = ["Story"]
