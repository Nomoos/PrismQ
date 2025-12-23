"""Content generation from idea and title using AI.

This module provides AI-powered content generation using Qwen3:30b.
ALL generation goes through local AI models via Ollama.

Input to AI:
    - Title (Titulek)
    - Idea text
    - One seed (randomly picked from 500 predefined variations like "pudding", "fire", "ocean", etc.)

Key Components:
    - ContentGenerator: Generates ContentV1 from Idea and Title using AI
    - AIContentGenerator: Direct AI content generation interface
    - generate_content: Convenience function for AI content generation
    - SEED_VARIATIONS: 500 predefined seed words for creative variation
"""

from .ai_content_generator import (
    SEED_VARIATIONS,
    AIContentGenerator,
    AIContentGeneratorConfig,
    generate_content,
    get_random_seed,
    get_seed_by_index,
)
from .content_generator import (
    PlatformTarget,
    ContentGenerator,
    ContentGeneratorConfig,
    ContentSection,
    ContentStructure,
    ContentTone,
    ContentV1,
)
from .story_content_service import (  # State-based processing
    INITIAL_CONTENT_VERSION,
    STATE_REVIEW_TITLE_FROM_CONTENT_IDEA,
    STATE_CONTENT_FROM_IDEA_TITLE,
    ContentFromIdeaTitleService,
    ContentGenerationResult,
    StateBasedContentResult,
    StoryContentService,
    process_all_pending_stories,
    process_oldest_from_idea_title,
)

__all__ = [
    # Content Generator (AI-powered)
    "ContentGenerator",
    "ContentGeneratorConfig",
    "ContentV1",
    "ContentTone",
    "ContentSection",
    "ContentStructure",
    "PlatformTarget",
    # AI Content Generator (Qwen3:30b)
    "AIContentGenerator",
    "AIContentGeneratorConfig",
    "generate_content",
    "get_random_seed",
    "get_seed_by_index",
    "SEED_VARIATIONS",
    # Story Content Service (legacy)
    "StoryContentService",
    "ContentGenerationResult",
    "process_all_pending_stories",
    # State-based Content Service (PrismQ.T.Content.From.Idea.Title)
    "ContentFromIdeaTitleService",
    "StateBasedContentResult",
    "process_oldest_from_idea_title",
    "STATE_CONTENT_FROM_IDEA_TITLE",
    "STATE_REVIEW_TITLE_FROM_CONTENT_IDEA",
    "INITIAL_CONTENT_VERSION",
]
