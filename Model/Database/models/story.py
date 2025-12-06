"""DEPRECATED: Use Model.Entities.story instead.

This module re-exports from Model.Entities.story for backward compatibility.
"""
from Model.Entities.story import Story
from Model.state import StoryState

__all__ = ["Story", "StoryState"]
