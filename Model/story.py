"""Story model for PrismQ content workflow.

This module re-exports the Story model from Model.Entities.story
for backward compatibility.

For new code, prefer importing directly:
    >>> from Model import Story  # Recommended
    >>> from Model.Entities import Story  # Also valid
"""

# Re-export Story from the canonical location
from Model.Entities.story import Story

__all__ = ["Story"]
