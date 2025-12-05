"""DEPRECATED: Use Model.entities.story instead.

This module re-exports from Model.entities.story for backward compatibility.
"""
from Model.entities.story import Story
from Model.state import StoryState

__all__ = ["Story", "StoryState"]
