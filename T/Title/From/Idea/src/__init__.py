"""PrismQ.T.Title.From.Idea - AI Title Generation Module

This module generates emotionally resonant titles from Ideas using AI.

⚠️  IMPORTANT: AI-based title generation is the ONLY approved method.
⚠️  The literary-focused prompt in ai_title_generator is the canonical approach.

Public API:
    - AITitleGenerator: Main class for generating titles (AI-only)
    - TitleVariant: Data model for generated title variants
    - TitleGeneratorConfig: Configuration for title generation
    - AIUnavailableError: Exception when AI service is unavailable
    - generate_titles_from_idea: Convenience function for title generation

Module Structure (SOLID Principles):
    - ai_title_generator.py: Orchestrates title generation workflow
    - prompt_loader.py: Loads prompt templates from files
    - ollama_client.py: Handles Ollama API communication
    - title_scorer.py: Scores title quality
    - title_variant.py: Title data model

Deprecated (kept for backward compatibility):
    - title_generator.py: Template-based generation (DO NOT USE)
    - TitleGenerator class: Use AITitleGenerator instead

Example:
    >>> from T.Title.From.Idea.src import AITitleGenerator
    >>> from T.Idea.Model.src.idea import Idea
    >>> 
    >>> idea = Idea(title="Story", concept="A tale of connection...")
    >>> generator = AITitleGenerator()
    >>> variants = generator.generate_from_idea(idea, num_variants=5)
    >>> for variant in variants:
    ...     print(f"{variant.text} (score: {variant.score})")
"""

# Primary API - AI-based title generation (RECOMMENDED)
from .ai_title_generator import (
    AITitleGenerator,
    TitleGeneratorConfig,
    AIUnavailableError,
    generate_titles_from_idea,
)

# Data models
from .title_variant import TitleVariant

# Component modules (for advanced usage)
from .prompt_loader import PromptLoader
from .ollama_client import OllamaClient, OllamaConfig
from .title_scorer import TitleScorer, ScoringConfig

# Story service
from .story_title_service import (
    StoryTitleResult,
    StoryTitleService,
    create_stories_from_idea,
)

# Deprecated - kept for backward compatibility only
from .title_generator import (
    TitleGenerator,  # DEPRECATED: Use AITitleGenerator instead
    TitleConfig,      # DEPRECATED: Use TitleGeneratorConfig instead
)

# Public API
__all__ = [
    # Primary API (RECOMMENDED)
    "AITitleGenerator",
    "TitleGeneratorConfig",
    "AIUnavailableError",
    "generate_titles_from_idea",
    "TitleVariant",
    
    # Component modules
    "PromptLoader",
    "OllamaClient",
    "OllamaConfig",
    "TitleScorer",
    "ScoringConfig",
    
    # Story service
    "StoryTitleService",
    "StoryTitleResult",
    "create_stories_from_idea",
    
    # Deprecated (DO NOT USE)
    "TitleGenerator",
    "TitleConfig",
]
