"""PrismQ.T.Story.Review - GPT-Based Expert Story Review Module

AI-powered expert-level review of complete story using GPT (Stage 21 / MVP-021).
Provides holistic assessment of title + script + audience context after all local
AI reviews have passed.

This module serves as a quality gate in the workflow:
- If READY FOR PUBLISHING: proceed to Stage 23 (Publishing.Finalization)
- If NEEDS POLISH: proceed to Stage 22 (Story.Polish) with improvement suggestions
"""

from .prompts import (
    CRITICAL_STORY_REVIEW_PROMPT,
    FINAL_POLISH_THRESHOLD,
    REVIEW_CONSTRAINTS,
    REVIEW_FOCUS_AREAS,
    REVIEW_OUTPUT_STRUCTURE,
    get_critical_review_prompt,
    get_critical_review_prompt_template,
    get_readiness_statement,
    is_ready_for_final_polish,
)
from .review import (
    AlignmentLevel,
    AudienceFit,
    ComponentType,
    EffortLevel,
    ExpertReview,
    ImprovementSuggestion,
    MatchLevel,
    OverallAssessment,
    PlatformOptimization,
    Priority,
    ProfessionalQuality,
    ReviewDecision,
    StoryCoherence,
    StoryExpertReviewer,
    get_expert_feedback,
    review_story_to_json,
    review_story_with_gpt,
)

__all__ = [
    # Main review class
    "ExpertReview",
    # Assessment components
    "OverallAssessment",
    "StoryCoherence",
    "AudienceFit",
    "ProfessionalQuality",
    "PlatformOptimization",
    "ImprovementSuggestion",
    # Enums
    "ComponentType",
    "Priority",
    "EffortLevel",
    "AlignmentLevel",
    "MatchLevel",
    "ReviewDecision",
    # Reviewer class
    "StoryExpertReviewer",
    # Convenience functions
    "review_story_with_gpt",
    "review_story_to_json",
    "get_expert_feedback",
    # Prompt templates and utilities
    "CRITICAL_STORY_REVIEW_PROMPT",
    "FINAL_POLISH_THRESHOLD",
    "REVIEW_FOCUS_AREAS",
    "REVIEW_OUTPUT_STRUCTURE",
    "REVIEW_CONSTRAINTS",
    "get_critical_review_prompt",
    "get_critical_review_prompt_template",
    "is_ready_for_final_polish",
    "get_readiness_statement",
]
