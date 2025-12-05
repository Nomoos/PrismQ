"""PrismQ.T.Story.Review - AI Review Prompt Templates

This module contains prompt templates for local AI story reviews.
These prompts are designed for critical analysis of story structure,
pacing, worldbuilding, logic, thematic execution, and character development.

The prompts are optimized for use with local AI models and provide
structured output formats for integration with the review workflow.
"""

# =============================================================================
# CRITICAL STORY REVIEW PROMPT
# =============================================================================
# This prompt is designed for local AI review of stories.
# It focuses exclusively on identifying flaws and providing actionable feedback.
# The review determines if a story is ready for final polish (>= 75%) or not.
# =============================================================================

CRITICAL_STORY_REVIEW_PROMPT = """Write a critical review of the following story that focuses exclusively on its biggest flaws in structure, pacing, worldbuilding, logic, thematic execution, and character development.

Requirements:

Length: Maximum 1200 words. Do NOT exceed.

Tone: analytical, objective, constructive; avoid excessive praise.

Do NOT summarize the entire plot.

Focus your critique on:

Major pacing and narrative-flow issues

Worldbuilding inconsistencies or contradictions

Logical gaps in the story's rules or mechanics

Underdeveloped or unclear character motivations

Thematic weaknesses or missed opportunities

Structural problems that reduce emotional impact

Use specific examples from the story for each flaw.

Provide actionable suggestions explaining how the author can improve or fix each issue.

Avoid:

Superlatives

Unjustified praise

Invention of scenes not present in the text

Vague criticism without evidence

Structure your review as follows:

Introduction: brief statement of what the story attempts to accomplish

Major Flaws: bullet points or subsections with evidence

Suggestions for Improvement: clear and practical

Conclusion: short summary of why the weaknesses matter

Final Score: Give a numerical score 0–100% based on overall effectiveness in light of its flaws

Readiness Statement:

If the score is 75% or higher, explicitly state: "This story is ready for final polish."

If the score is below 75%, explicitly state: "This story is not yet ready for final polish."

Now analyze the following story:
[INSERT STORY HERE]"""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_critical_review_prompt(story_text: str) -> str:
    """Generate a critical review prompt with the story text inserted.
    
    Args:
        story_text: The complete story text to be reviewed
        
    Returns:
        The complete prompt with story text inserted
        
    Example:
        >>> prompt = get_critical_review_prompt("Once upon a time...")
        >>> # Use prompt with local AI model
    """
    return CRITICAL_STORY_REVIEW_PROMPT.replace("[INSERT STORY HERE]", story_text)


def get_critical_review_prompt_template() -> str:
    """Get the raw critical review prompt template.
    
    Returns:
        The prompt template with [INSERT STORY HERE] placeholder
        
    Example:
        >>> template = get_critical_review_prompt_template()
        >>> print(template)
    """
    return CRITICAL_STORY_REVIEW_PROMPT


# Threshold for determining readiness for final polish
FINAL_POLISH_THRESHOLD = 75  # 75% or higher means ready for final polish


def is_ready_for_final_polish(score: int) -> bool:
    """Determine if a story is ready for final polish based on review score.
    
    Args:
        score: The review score (0-100)
        
    Returns:
        True if score >= 75, False otherwise
        
    Example:
        >>> is_ready_for_final_polish(80)
        True
        >>> is_ready_for_final_polish(70)
        False
    """
    return score >= FINAL_POLISH_THRESHOLD


def get_readiness_statement(score: int) -> str:
    """Generate the appropriate readiness statement based on score.
    
    Args:
        score: The review score (0-100)
        
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
    "emotional_impact"
]


REVIEW_OUTPUT_STRUCTURE = {
    "introduction": "Brief statement of what the story attempts to accomplish",
    "major_flaws": "Bullet points or subsections with evidence",
    "suggestions": "Clear and practical improvement suggestions",
    "conclusion": "Short summary of why the weaknesses matter",
    "final_score": "Numerical score 0-100%",
    "readiness_statement": "Statement on readiness for final polish"
}


# =============================================================================
# REVIEW CONSTRAINTS
# =============================================================================

REVIEW_CONSTRAINTS = {
    "max_words": 1200,
    "tone": "analytical, objective, constructive",
    "avoid": [
        "superlatives",
        "unjustified_praise",
        "invented_scenes",
        "vague_criticism"
    ],
    "require_evidence": True,
    "require_actionable_suggestions": True
}
