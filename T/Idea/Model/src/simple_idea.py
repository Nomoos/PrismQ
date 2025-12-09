"""Simple Idea model for PrismQ content creation.

This module defines a simplified Idea data model with just essential fields:
- id: Unique identifier
- text: Prompt-like text describing the idea
- version: Version number for tracking iterations (uses CHECK >= 0 to simulate unsigned integer)
- created_at: Timestamp of creation

The SimpleIdea is designed to be referenced by Story via foreign key (FK).
It focuses on storing idea prompts/text in a clean, minimal structure.
"""

import re
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class SimpleIdea:
    """Simplified Idea model for prompt-based idea storage.

    This model represents a simple idea with just text content in prompt format.
    It is designed to be referenced by Story via foreign key relationship.

    Schema:
        -- Idea: Simple prompt-based idea data (Story references Idea via FK in Story.idea_id)
        -- Text field contains prompt-like content for content generation
        -- Note: version uses INTEGER with CHECK >= 0 to simulate unsigned integer
        Idea (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,                                      -- Prompt-like text describing the idea
            version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 0),  -- Version tracking (UINT simulation)
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )

    Attributes:
        id: Unique identifier (auto-generated in database)
        text: Prompt-like text describing the idea
        version: Version number for tracking iterations (>= 0, defaults to 1)
        created_at: Timestamp of creation

    Example:
        >>> idea = SimpleIdea(
        ...     text="Write a horror story about a girl who hears her own voice "
        ...          "warning her about the future, only to discover she's already dead.",
        ...     version=1
        ... )
        >>> print(idea.text)
        Write a horror story about a girl who hears her own voice...
    """

    text: str
    version: int = 1
    id: Optional[int] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.version < 1:
            self.version = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert SimpleIdea to dictionary representation.

        Returns:
            Dictionary containing all fields
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimpleIdea":
        """Create SimpleIdea from dictionary.

        Args:
            data: Dictionary containing SimpleIdea fields

        Returns:
            SimpleIdea instance
        """
        return cls(
            id=data.get("id"),
            text=data.get("text", ""),
            version=data.get("version", 1),
            created_at=data.get("created_at"),
        )

    def create_new_version(self, text: Optional[str] = None) -> "SimpleIdea":
        """Create a new version of this idea.

        Args:
            text: Optional new text. If not provided, uses existing text.

        Returns:
            New SimpleIdea instance with incremented version
        """
        return SimpleIdea(
            id=None,  # New version gets new ID
            text=text if text is not None else self.text,
            version=self.version + 1,
            created_at=None,  # New timestamp will be generated
        )

    @classmethod
    def from_prompt_template(cls, template_name: str, **kwargs) -> "SimpleIdea":
        """Create SimpleIdea from a prompt template.

        Args:
            template_name: Name of the template to use
            **kwargs: Variables to substitute in the template

        Returns:
            SimpleIdea instance with formatted prompt text

        Raises:
            ValueError: If template_name is not found
        """
        templates = IdeaPromptTemplates.get_all_templates()
        if template_name not in templates:
            available = ", ".join(templates.keys())
            raise ValueError(
                f"Template '{template_name}' not found. " f"Available templates: {available}"
            )

        template = templates[template_name]
        text = template.format(**kwargs) if kwargs else template

        return cls(text=text, version=1)

    def __repr__(self) -> str:
        """String representation of SimpleIdea."""
        text_preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"SimpleIdea(id={self.id}, version={self.version}, text='{text_preview}')"


class IdeaPromptTemplates:
    """Collection of prompt templates for idea generation.

    These templates provide structured formats for creating idea prompts
    that can be used to generate content across different genres and formats.

    Example:
        >>> templates = IdeaPromptTemplates.get_all_templates()
        >>> horror_template = templates["horror_story"]
        >>> prompt = horror_template.format(
        ...     protagonist="a teenage girl",
        ...     supernatural_element="hearing her future self",
        ...     twist="she's already dead"
        ... )
    """

    # Horror story template
    HORROR_STORY = (
        "Write a horror story about {protagonist} who discovers "
        "{supernatural_element}. The twist: {twist}. "
        "Build tension gradually, use sensory details, and end with a chilling revelation."
    )

    # Mystery story template
    MYSTERY_STORY = (
        "Create a mystery story where {detective} investigates {crime}. "
        "Include {red_herrings} red herrings and reveal that {culprit}. "
        "Use clues that the reader can follow to solve alongside the detective."
    )

    # Educational content template
    EDUCATIONAL_CONTENT = (
        "Explain {topic} for {audience}. "
        "Start with {hook}, then cover {key_points}. "
        "Use analogies and examples to make complex concepts accessible. "
        "End with practical takeaways the audience can apply."
    )

    # Viral short content template
    VIRAL_SHORT = (
        "Create a {duration} second video script about {topic}. "
        "Hook viewers in the first 3 seconds with: {hook}. "
        "Keep the energy high, include a surprising element: {surprise}. "
        "End with a call to action: {cta}."
    )

    # Documentary style template
    DOCUMENTARY_STYLE = (
        "Document the story of {subject} focusing on {angle}. "
        "Include perspectives from {stakeholders}. "
        "Balance facts with emotional storytelling. "
        "Key themes to explore: {themes}."
    )

    # Personal narrative template
    PERSONAL_NARRATIVE = (
        "Tell the story of {experience} from {perspective}. "
        "Show the emotional journey from {starting_emotion} to {ending_emotion}. "
        "Include specific sensory details and moments of realization. "
        "What lesson or insight emerges: {lesson}."
    )

    # How-to guide template
    HOW_TO_GUIDE = (
        "Create a guide on how to {goal} for {audience}. "
        "Prerequisites: {prerequisites}. "
        "Break it into {num_steps} clear steps. "
        "Include common mistakes to avoid: {mistakes}. "
        "Expected outcome: {outcome}."
    )

    # Opinion/Analysis template
    OPINION_ANALYSIS = (
        "Analyze {topic} and argue that {thesis}. "
        "Present {num_arguments} supporting arguments with evidence. "
        "Address counterarguments: {counterarguments}. "
        "Conclude with implications for {implications}."
    )

    # True crime template
    TRUE_CRIME = (
        "Investigate the case of {case_name}. "
        "Timeline: {timeline}. Key figures: {key_figures}. "
        "Evidence examined: {evidence}. "
        "Theories explored: {theories}. "
        "Current status: {status}."
    )

    # Technology explainer template
    TECH_EXPLAINER = (
        "Explain how {technology} works for {audience}. "
        "Start with the problem it solves: {problem}. "
        "Core mechanism: {mechanism}. "
        "Real-world applications: {applications}. "
        "Future implications: {future}."
    )

    # Simple prompt template (minimal formatting)
    SIMPLE_PROMPT = "{concept}"

    # Structured idea template
    STRUCTURED_IDEA = (
        "Title: {title}\n"
        "Concept: {concept}\n"
        "Target Audience: {audience}\n"
        "Key Message: {message}\n"
        "Format: {format}"
    )

    # Emotion-driven template
    EMOTION_DRIVEN = (
        "Create content that makes the audience feel {primary_emotion}. "
        "Story premise: {premise}. "
        "Emotional journey: {start_emotion} → {middle_emotion} → {end_emotion}. "
        "Key moment that triggers emotion: {trigger_moment}."
    )

    @classmethod
    def get_all_templates(cls) -> Dict[str, str]:
        """Get all available prompt templates.

        Returns:
            Dictionary mapping template names to template strings
        """
        return {
            "horror_story": cls.HORROR_STORY,
            "mystery_story": cls.MYSTERY_STORY,
            "educational_content": cls.EDUCATIONAL_CONTENT,
            "viral_short": cls.VIRAL_SHORT,
            "documentary_style": cls.DOCUMENTARY_STYLE,
            "personal_narrative": cls.PERSONAL_NARRATIVE,
            "how_to_guide": cls.HOW_TO_GUIDE,
            "opinion_analysis": cls.OPINION_ANALYSIS,
            "true_crime": cls.TRUE_CRIME,
            "tech_explainer": cls.TECH_EXPLAINER,
            "simple_prompt": cls.SIMPLE_PROMPT,
            "structured_idea": cls.STRUCTURED_IDEA,
            "emotion_driven": cls.EMOTION_DRIVEN,
        }

    @classmethod
    def get_template(cls, name: str) -> str:
        """Get a specific template by name.

        Args:
            name: Template name

        Returns:
            Template string

        Raises:
            ValueError: If template not found
        """
        templates = cls.get_all_templates()
        if name not in templates:
            available = ", ".join(templates.keys())
            raise ValueError(f"Template '{name}' not found. Available: {available}")
        return templates[name]

    @classmethod
    def format_template(cls, name: str, **kwargs) -> str:
        """Format a template with provided variables.

        Args:
            name: Template name
            **kwargs: Variables to substitute

        Returns:
            Formatted prompt string
        """
        template = cls.get_template(name)
        return template.format(**kwargs)

    @classmethod
    def list_template_names(cls) -> List[str]:
        """Get list of available template names.

        Returns:
            List of template names
        """
        return list(cls.get_all_templates().keys())

    @classmethod
    def get_template_variables(cls, name: str) -> List[str]:
        """Get list of variables required by a template.

        Args:
            name: Template name

        Returns:
            List of variable names in the template
        """
        template = cls.get_template(name)
        # Find all {variable_name} patterns
        variables = re.findall(r"\{(\w+)\}", template)
        return list(dict.fromkeys(variables))  # Preserve order, remove duplicates


# Example pre-filled ideas for quick start
EXAMPLE_IDEAS: List[SimpleIdea] = [
    SimpleIdea(
        text="Write a horror story about a teenage girl who starts hearing a voice "
        "that sounds exactly like her own, warning her about the future. "
        "As the warnings come true, she realizes the voice is her future self "
        "trying to prevent her death - but the twist is she's already dead.",
        version=1,
    ),
    SimpleIdea(
        text="Create an educational explainer about how quantum computers work, "
        "using the analogy of a GPS that can explore all possible routes "
        "simultaneously. Target audience: curious adults without tech background. "
        "Keep it under 10 minutes, use visual analogies.",
        version=1,
    ),
    SimpleIdea(
        text="Document the rise and fall of a once-popular social media platform, "
        "exploring what made it successful and why it failed. Include interviews "
        "with former employees and power users. Themes: innovation, hubris, "
        "community, and the ephemeral nature of digital spaces.",
        version=1,
    ),
    SimpleIdea(
        text="Create a 60-second viral video about the most counterintuitive "
        "productivity hack: doing less. Hook: 'The most successful people "
        "don't work 80-hour weeks.' Include surprising statistics and "
        "a clear call-to-action to learn more.",
        version=1,
    ),
    SimpleIdea(
        text="Tell the personal story of someone who quit their dream job "
        "to pursue an unconventional path. Show the emotional journey from "
        "security to fear to fulfillment. Include specific moments of doubt "
        "and the breakthrough realization that changed everything.",
        version=1,
    ),
]


__all__ = [
    "SimpleIdea",
    "IdeaPromptTemplates",
    "EXAMPLE_IDEAS",
]
