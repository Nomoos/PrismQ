"""Script generation from idea and title using AI.

This module provides AI-powered script generation using Qwen2.5-14B-Instruct.
ALL generation goes through local AI models via Ollama.

Input to AI:
    - Title (Titulek)
    - Idea text
    - One seed (randomly picked from 500 predefined variations like "pudding", "fire", "ocean", etc.)

Key Components:
    - ScriptGenerator: Generates ScriptV1 from Idea and Title using AI
    - AIScriptGenerator: Direct AI script generation interface
    - generate_script: Convenience function for AI script generation
    - SEED_VARIATIONS: 500 predefined seed words for creative variation
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
    STATE_REVIEW_TITLE_FROM_SCRIPT_IDEA,
    INITIAL_SCRIPT_VERSION
)
from .ai_script_generator import (
    AIScriptGenerator,
    AIScriptGeneratorConfig,
    generate_script,
    get_random_seed,
    get_seed_by_index,
    SEED_VARIATIONS
)

__all__ = [
    # Script Generator (AI-powered)
    "ScriptGenerator",
    "ScriptGeneratorConfig",
    "ScriptV1",
    "ScriptTone",
    "ScriptSection",
    "ScriptStructure",
    "PlatformTarget",
    # AI Script Generator (Qwen2.5-14B-Instruct)
    "AIScriptGenerator",
    "AIScriptGeneratorConfig",
    "generate_script",
    "get_random_seed",
    "get_seed_by_index",
    "SEED_VARIATIONS",
    # Story Script Service (legacy)
    "StoryScriptService",
    "ScriptGenerationResult",
    "process_all_pending_stories",
    # State-based Script Service (PrismQ.T.Script.From.Idea.Title)
    "ScriptFromIdeaTitleService",
    "StateBasedScriptResult",
    "process_oldest_from_idea_title",
    "STATE_SCRIPT_FROM_IDEA_TITLE",
    "STATE_REVIEW_TITLE_FROM_SCRIPT_IDEA",
    "INITIAL_SCRIPT_VERSION"
]
