"""PrismQ.T.Review.Title - AI Review Prompt Templates

This module contains modular prompt templates for AI-powered title reviews.
The prompts are designed for title evaluation with different contexts:
- Base review: Core evaluation criteria (content, engagement, SEO)
- Idea context: Additional idea alignment evaluation
- Comparison context: Version comparison and improvement tracking

The modular design allows:
1. Reuse of common evaluation criteria across review types
2. Context-specific additions (idea alignment, version tracking)
3. Flexible composition for different review scenarios
4. Centralized maintenance of prompt templates

Prompts are stored as separate text files in _meta/prompts/ for easier
maintenance and editing.
"""

from pathlib import Path
from typing import Dict, Optional

# =============================================================================
# PROMPT FILE PATHS
# =============================================================================

_PROMPTS_DIR = Path(__file__).parent / "_meta" / "prompts"

# Base prompt template (common evaluation criteria)
_BASE_REVIEW_FILE = _PROMPTS_DIR / "base_review.txt"

# Context-specific prompt sections
_IDEA_CONTEXT_FILE = _PROMPTS_DIR / "idea_context.txt"
_COMPARISON_CONTEXT_FILE = _PROMPTS_DIR / "comparison_context.txt"

# Output format specifications
_JSON_OUTPUT_BASIC_FILE = _PROMPTS_DIR / "json_output_basic.txt"
_JSON_OUTPUT_WITH_IDEA_FILE = _PROMPTS_DIR / "json_output_with_idea.txt"
_JSON_OUTPUT_COMPARISON_FILE = _PROMPTS_DIR / "json_output_comparison.txt"


# =============================================================================
# PROMPT LOADING FUNCTIONS
# =============================================================================


def _load_prompt_file(file_path: Path) -> str:
    """Load a prompt template from file.

    Args:
        file_path: Path to the prompt file

    Returns:
        The prompt text content

    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {file_path}")
    return file_path.read_text(encoding="utf-8")


# =============================================================================
# WEIGHT CONFIGURATIONS
# =============================================================================

# Default weights for v1 review (with idea context)
WEIGHTS_V1_WITH_IDEA = {
    "content_weight": 30,
    "idea_weight": 25,
    "engagement_weight": 25,
    "seo_weight": 20,
}

# Default weights for v2+ review (content-focused, no idea)
WEIGHTS_V2_CONTENT_ONLY = {
    "content_weight": 40,
    "engagement_weight": 30,
    "seo_weight": 20,
    "length_weight": 10,
}


# =============================================================================
# PROMPT COMPOSITION FUNCTIONS
# =============================================================================


def compose_review_prompt_with_idea(
    title_text: str,
    content_text: str,
    idea_summary: str,
    target_audience: str = "",
    weights: Optional[Dict[str, int]] = None,
) -> str:
    """Compose a review prompt with idea context (v1 review).

    This creates a comprehensive prompt that evaluates:
    - Content alignment (script)
    - Idea alignment (original concept)
    - Engagement
    - SEO & Length

    Args:
        title_text: The title to review
        content_text: The content/script text
        idea_summary: Summary of the core idea
        target_audience: Optional target audience description
        weights: Optional custom weights for evaluation criteria

    Returns:
        Complete prompt with all sections composed

    Example:
        >>> prompt = compose_review_prompt_with_idea(
        ...     title_text="The Echo - A Haunting Discovery",
        ...     content_text="Sarah investigates mysterious sounds...",
        ...     idea_summary="Horror story about echoes in hospital",
        ...     target_audience="Horror enthusiasts aged 18-35"
        ... )
    """
    if weights is None:
        weights = WEIGHTS_V1_WITH_IDEA

    # Load template sections
    base_review = _load_prompt_file(_BASE_REVIEW_FILE)
    idea_context = _load_prompt_file(_IDEA_CONTEXT_FILE)
    json_output = _load_prompt_file(_JSON_OUTPUT_WITH_IDEA_FILE)

    # Insert idea context into base review (after engagement, before output format)
    # Split at the "Provide:" section
    parts = base_review.split("\nProvide:\n")
    if len(parts) != 2:
        # Fallback: just concatenate
        composed = base_review + idea_context + json_output
    else:
        # Insert idea context between criteria and output specification
        composed = parts[0] + idea_context + "\nProvide:\n" + parts[1] + json_output

    # Fill in variables
    composed = composed.format(
        content_weight=weights.get("content_weight", 30),
        idea_weight=weights.get("idea_weight", 25),
        engagement_weight=weights.get("engagement_weight", 25),
        seo_weight=weights.get("seo_weight", 20),
        title_text=title_text,
        content_text=content_text,
        idea_summary=idea_summary,
        target_audience=target_audience or "General audience",
    )

    return composed


def compose_review_prompt_content_only(
    title_text: str,
    content_text: str,
    weights: Optional[Dict[str, int]] = None,
) -> str:
    """Compose a review prompt for content-only evaluation (v2+ review).

    This creates a prompt that evaluates:
    - Content alignment (script) - higher weight
    - Engagement
    - SEO & Length

    Args:
        title_text: The title to review
        content_text: The content/script text
        weights: Optional custom weights for evaluation criteria

    Returns:
        Complete prompt with base review and JSON output

    Example:
        >>> prompt = compose_review_prompt_content_only(
        ...     title_text="The Echo - A Haunting Discovery",
        ...     content_text="Enhanced horror short about..."
        ... )
    """
    if weights is None:
        weights = WEIGHTS_V2_CONTENT_ONLY

    # Load template sections
    base_review = _load_prompt_file(_BASE_REVIEW_FILE)
    json_output = _load_prompt_file(_JSON_OUTPUT_BASIC_FILE)

    # Compose prompt
    composed = base_review + json_output

    # Fill in variables
    composed = composed.format(
        content_weight=weights.get("content_weight", 40),
        engagement_weight=weights.get("engagement_weight", 30),
        seo_weight=weights.get("seo_weight", 30),
        title_text=title_text,
        content_text=content_text,
    )

    return composed


def compose_comparison_prompt(
    title_current: str,
    title_previous: str,
    content_text: str,
    score_current: int,
    score_previous: int,
    feedback_previous: str,
    current_version: str = "v2",
    previous_version: str = "v1",
    next_version: str = "v3",
) -> str:
    """Compose a prompt for comparing title versions.

    This creates a prompt that:
    - Compares scores between versions
    - Identifies improvements and regressions
    - Provides recommendations for next iteration

    Args:
        title_current: Current title version
        title_previous: Previous title version
        content_text: The content/script text
        score_current: Current overall score
        score_previous: Previous overall score
        feedback_previous: Previous review feedback
        current_version: Version label (default "v2")
        previous_version: Previous version label (default "v1")
        next_version: Next version label (default "v3")

    Returns:
        Complete comparison prompt

    Example:
        >>> prompt = compose_comparison_prompt(
        ...     title_current="The Echo - A Haunting Discovery",
        ...     title_previous="The Echo",
        ...     content_text="Enhanced horror short...",
        ...     score_current=78,
        ...     score_previous=65,
        ...     feedback_previous="Needs more specificity..."
        ... )
    """
    # Load template sections
    comparison_context = _load_prompt_file(_COMPARISON_CONTEXT_FILE)
    json_output = _load_prompt_file(_JSON_OUTPUT_COMPARISON_FILE)

    # Compose prompt
    composed = comparison_context + json_output

    # Fill in variables
    composed = composed.format(
        current_version=current_version,
        previous_version=previous_version,
        next_version=next_version,
        title_current=title_current,
        title_previous=title_previous,
        content_text=content_text,
        score_current=score_current,
        score_previous=score_previous,
        feedback_previous=feedback_previous,
    )

    return composed


# =============================================================================
# LEGACY COMPATIBILITY
# =============================================================================
# These functions maintain compatibility with existing code that uses
# the old prompt format from T/Review/Title/From/Content/_meta/prompts/
# =============================================================================


def get_v1_review_prompt(
    title_text: str,
    content_text: str,
    idea_summary: str,
    target_audience: str = "",
) -> str:
    """Get v1 title review prompt (with idea context).

    This is a convenience function that wraps compose_review_prompt_with_idea()
    with default weights for v1 reviews.

    Args:
        title_text: The title to review
        content_text: The content/script text
        idea_summary: Summary of the core idea
        target_audience: Optional target audience description

    Returns:
        Complete v1 review prompt

    Example:
        >>> prompt = get_v1_review_prompt(
        ...     title_text="The Echo",
        ...     content_text="A horror short...",
        ...     idea_summary="Horror story about echoes"
        ... )
    """
    return compose_review_prompt_with_idea(
        title_text=title_text,
        content_text=content_text,
        idea_summary=idea_summary,
        target_audience=target_audience,
        weights=WEIGHTS_V1_WITH_IDEA,
    )


def get_v2_review_prompt(
    title_text: str,
    content_text: str,
) -> str:
    """Get v2+ title review prompt (content-only).

    This is a convenience function that wraps compose_review_prompt_content_only()
    with default weights for v2+ reviews.

    Args:
        title_text: The title to review
        content_text: The content/script text

    Returns:
        Complete v2 review prompt

    Example:
        >>> prompt = get_v2_review_prompt(
        ...     title_text="The Echo - A Haunting Discovery",
        ...     content_text="Enhanced horror short..."
        ... )
    """
    return compose_review_prompt_content_only(
        title_text=title_text,
        content_text=content_text,
        weights=WEIGHTS_V2_CONTENT_ONLY,
    )


# =============================================================================
# PROMPT TEMPLATES (Module-level constants for backward compatibility)
# =============================================================================

# Load base templates at module level
BASE_REVIEW_PROMPT = _load_prompt_file(_BASE_REVIEW_FILE)
IDEA_CONTEXT_PROMPT = _load_prompt_file(_IDEA_CONTEXT_FILE)
COMPARISON_CONTEXT_PROMPT = _load_prompt_file(_COMPARISON_CONTEXT_FILE)
