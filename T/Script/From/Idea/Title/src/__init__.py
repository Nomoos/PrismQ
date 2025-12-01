"""Script generation from idea and title.

This module provides functionality to generate initial script drafts (v1)
from an Idea object and a title variant.

Key Components:
    - ScriptGenerator: Generates ScriptV1 from Idea and Title
    - StoryScriptService: Service to process stories needing scripts
    - ScriptFromIdeaTitleService: State-based service for PrismQ.T.Script.From.Idea.Title
    - process_oldest_from_idea_title: Process oldest story in the state
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
    process_all_pending_stories,
    # State-based processing
    ScriptFromIdeaTitleService,
    StateBasedScriptResult,
    process_oldest_from_idea_title,
    STATE_SCRIPT_FROM_IDEA_TITLE,
    STATE_REVIEW_TITLE_FROM_SCRIPT_IDEA
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
    # Story Script Service (legacy)
    "StoryScriptService",
    "ScriptGenerationResult",
    "process_all_pending_stories",
    # State-based Script Service (PrismQ.T.Script.From.Idea.Title)
    "ScriptFromIdeaTitleService",
    "StateBasedScriptResult",
    "process_oldest_from_idea_title",
    "STATE_SCRIPT_FROM_IDEA_TITLE",
    "STATE_REVIEW_TITLE_FROM_SCRIPT_IDEA"
]
