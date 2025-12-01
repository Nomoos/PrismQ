"""Script generation from idea and title.

This module provides functionality to generate initial script drafts (v1)
from an Idea object and a title variant.

Key Components:
    - ScriptGenerator: Generates ScriptV1 from Idea and Title
    - StoryScriptService: Service to process stories needing scripts
    - process_all_pending_stories: Convenience function for batch processing
"""

from .script_generator import (
    ScriptGenerator,
    ScriptGeneratorConfig,
    ScriptV1,
    ScriptTone,
    ScriptSection,
    ScriptStructure,
    PlatformTarget
)
from .story_script_service import (
    StoryScriptService,
    ScriptGenerationResult,
    process_all_pending_stories
)

__all__ = [
    # Script Generator
    "ScriptGenerator",
    "ScriptGeneratorConfig",
    "ScriptV1",
    "ScriptTone",
    "ScriptSection",
    "ScriptStructure",
    "PlatformTarget",
    # Story Script Service
    "StoryScriptService",
    "ScriptGenerationResult",
    "process_all_pending_stories"
]
