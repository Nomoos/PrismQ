"""PrismQ.T.Story.Review - AI Review Prompt Templates

This module contains prompt templates for local AI story reviews.
These prompts are designed for critical analysis of story structure,
pacing, worldbuilding, logic, thematic execution, and character development.

The prompts are optimized for use with local AI models and provide
structured output formats for integration with the review workflow.

Prompts are stored as separate text files in _meta/prompts/ for easier
maintenance and editing.
"""

from pathlib import Path

# =============================================================================
# CRITICAL STORY REVIEW PROMPT
# =============================================================================
# This prompt is loaded from _meta/prompts/critical_story_review.txt
# It focuses exclusively on identifying flaws and providing actionable feedback.
# The review determines if a story is ready for final polish (>= 75%) or not.
# =============================================================================

# Path to the prompt file
_PROMPT_FILE = Path(__file__).parent / "_meta" / "prompts" / "critical_story_review.txt"


def _load_prompt() -> str:
    """Load the critical story review prompt from the text file.

    Returns:
        The prompt text content

    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    return _PROMPT_FILE.read_text(encoding="utf-8")


# Load the prompt at module level for backward compatibility
CRITICAL_STORY_REVIEW_PROMPT = _load_prompt()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

# Unique placeholder that is unlikely to appear in story text
_STORY_PLACEHOLDER = "[INSERT STORY HERE]"


def get_critical_review_prompt(story_text: str) -> str:
    """Generate a critical review prompt with the story text inserted.

    Args:
        story_text: The complete story text to be reviewed

    Returns:
        The complete prompt with story text inserted

    Note:
        The placeholder '[INSERT STORY HERE]' is replaced with the story text.
        If the story text itself contains this exact placeholder string,
        it will remain in the final prompt as part of the story content.

    Example:
        >>> prompt = get_critical_review_prompt("Once upon a time...")
        >>> # Use prompt with local AI model
    """
    return CRITICAL_STORY_REVIEW_PROMPT.replace(_STORY_PLACEHOLDER, story_text, 1)


def get_critical_review_prompt_template() -> str:
    """Get the raw critical review prompt template.

    Returns:
        The prompt template with [INSERT STORY HERE] placeholder

    Example:
        >>> template = get_critical_review_prompt_template()
        >>> print(template)
    """
    return CRITICAL_STORY_REVIEW_PROMPT


from typing import Union

# Threshold for determining readiness for final polish
FINAL_POLISH_THRESHOLD = 75  # 75% or higher means ready for final polish


def is_ready_for_final_polish(score: Union[int, float]) -> bool:
    """Determine if a story is ready for final polish based on review score.

    Args:
        score: The review score (0-100), can be int or float

    Returns:
        True if score >= 75, False otherwise

    Example:
        >>> is_ready_for_final_polish(80)
        True
        >>> is_ready_for_final_polish(70)
        False
        >>> is_ready_for_final_polish(75.5)
        True
    """
    return score >= FINAL_POLISH_THRESHOLD


def get_readiness_statement(score: Union[int, float]) -> str:
    """Generate the appropriate readiness statement based on score.

    Args:
        score: The review score (0-100), can be int or float

    Returns:
        The readiness statement string

    Example:
        >>> get_readiness_statement(80)
        'This story is ready for final polish.'
        >>> get_readiness_statement(70)
        'This story is not yet ready for final polish.'
    """
    if is_ready_for_final_polish(score):
        return "This story is ready for final polish."
    else:
        return "This story is not yet ready for final polish."


# =============================================================================
# REVIEW FOCUS AREAS
# =============================================================================
# These constants define the key areas that the critical review focuses on.
# They can be used for parsing review output or generating targeted prompts.
# =============================================================================

REVIEW_FOCUS_AREAS = [
    "pacing",
    "narrative_flow",
    "worldbuilding",
    "logic",
    "character_motivation",
    "thematic_execution",
    "structure",
    "emotional_impact",
]


REVIEW_OUTPUT_STRUCTURE = {
    "introduction": "Brief statement of what the story attempts to accomplish",
    "major_flaws": "Bullet points or subsections with evidence",
    "suggestions": "Clear and practical improvement suggestions",
    "conclusion": "Short summary of why the weaknesses matter",
    "final_score": "Numerical score 0-100%",
    "readiness_statement": "Statement on readiness for final polish",
}


# =============================================================================
# REVIEW CONSTRAINTS
# =============================================================================

REVIEW_CONSTRAINTS = {
    "max_words": 1200,
    "tone": "analytical, objective, constructive",
    "avoid": ["superlatives", "unjustified_praise", "invented_scenes", "vague_criticism"],
    "require_evidence": True,
    "require_actionable_suggestions": True,
}
