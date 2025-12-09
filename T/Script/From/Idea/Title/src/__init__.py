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

from .ai_script_generator import (
    SEED_VARIATIONS,
    AIScriptGenerator,
    AIScriptGeneratorConfig,
    generate_script,
    get_random_seed,
    get_seed_by_index,
)
from .script_generator import (
    PlatformTarget,
    ScriptGenerator,
    ScriptGeneratorConfig,
    ScriptSection,
    ScriptStructure,
    ScriptTone,
    ScriptV1,
)
from .story_script_service import (  # State-based processing
    INITIAL_SCRIPT_VERSION,
    STATE_REVIEW_TITLE_FROM_SCRIPT_IDEA,
    STATE_SCRIPT_FROM_IDEA_TITLE,
    ScriptFromIdeaTitleService,
    ScriptGenerationResult,
    StateBasedScriptResult,
    StoryScriptService,
    process_all_pending_stories,
    process_oldest_from_idea_title,
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
    "INITIAL_SCRIPT_VERSION",
]
