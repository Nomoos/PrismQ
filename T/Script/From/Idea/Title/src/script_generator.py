"""Script Generator for creating v1 scripts from ideas and titles.

This module implements the script generation logic using local AI models:
- Takes Idea object and Title v1 as input
- Generates structured script with intro, body, and conclusion using Qwen3:30b
- Optimizes for platform requirements (YouTube shorts < 180s)
- Maintains coherence with title promises and idea intent
- ALL generation goes through local AI models via Ollama
"""

import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Add parent directories to path for imports
# Path: T/Script/From/Idea/Title/src/script_generator.py
# Up 6 levels to T/, then into Idea/Model/src
parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
)
idea_model_path = os.path.join(parent_dir, "Idea", "Model", "src")
sys.path.insert(0, idea_model_path)

try:
    from idea import ContentGenre, Idea
except ImportError:
    # Fallback for testing or development
    pass

# Import AI script generator (lazy import to avoid circular dependency)
_ai_generator_module = None


def _get_ai_generator_module():
    """Lazy import of AI script generator module."""
    global _ai_generator_module
    if _ai_generator_module is None:
        try:
            from . import ai_script_generator as _ai_generator_module
        except ImportError:
            logger.warning("AI script generator module not available")
            _ai_generator_module = False
    return _ai_generator_module if _ai_generator_module else None


class ScriptStructure(Enum):
    """Script structure types."""

    THREE_ACT = "three_act"  # Introduction, Development, Conclusion
    HOOK_DELIVER_CTA = "hook_deliver_cta"  # Hook, Deliver, Call-to-Action
    PROBLEM_SOLUTION = "problem_solution"  # Problem, Investigation, Solution
    STORY = "story"  # Beginning, Middle, End


class PlatformTarget(Enum):
    """Target platforms for script optimization."""

    YOUTUBE_SHORT = "youtube_short"  # < 60 seconds
    YOUTUBE_MEDIUM = "youtube_medium"  # 60-180 seconds
    YOUTUBE_LONG = "youtube_long"  # > 180 seconds
    TIKTOK = "tiktok"  # < 60 seconds
    INSTAGRAM_REEL = "instagram_reel"  # < 90 seconds
    GENERAL = "general"  # No specific constraints


class ScriptTone(Enum):
    """Script tone options."""

    ENGAGING = "engaging"
    MYSTERIOUS = "mysterious"
    EDUCATIONAL = "educational"
    DRAMATIC = "dramatic"
    CONVERSATIONAL = "conversational"


@dataclass
class ScriptSection:
    """A section of the script."""

    section_type: str  # "introduction", "body", "conclusion"
    content: str
    estimated_duration_seconds: int
    purpose: str  # What this section aims to achieve
    notes: str = ""


@dataclass
class ScriptV1:
    """Initial script draft (version 1).

    Attributes:
        script_id: Unique identifier for this script
        idea_id: Reference to source Idea
        title: The title (v1) this script was generated from
        full_text: Complete script text
        sections: Breakdown into intro, body, conclusion
        total_duration_seconds: Estimated total duration
        structure_type: Type of structure used
        platform_target: Target platform
        metadata: Additional metadata
        created_at: Creation timestamp
        version: Version number (integer, 1 for initial draft)
        notes: Additional notes or context
    """

    script_id: str
    idea_id: str
    title: str
    full_text: str
    sections: List[ScriptSection]
    total_duration_seconds: int
    structure_type: ScriptStructure
    platform_target: PlatformTarget
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: int = 1
    notes: str = ""

    def get_section(self, section_type: str) -> Optional[ScriptSection]:
        """Get a specific section by type."""
        for section in self.sections:
            if section.section_type == section_type:
                return section
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "script_id": self.script_id,
            "idea_id": self.idea_id,
            "title": self.title,
            "full_text": self.full_text,
            "sections": [
                {
                    "section_type": s.section_type,
                    "content": s.content,
                    "estimated_duration_seconds": s.estimated_duration_seconds,
                    "purpose": s.purpose,
                    "notes": s.notes,
                }
                for s in self.sections
            ],
            "total_duration_seconds": self.total_duration_seconds,
            "structure_type": self.structure_type.value,
            "platform_target": self.platform_target.value,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "version": self.version,
            "notes": self.notes,
        }


@dataclass
class ScriptGeneratorConfig:
    """Configuration for AI-powered script generation.

    All script generation uses local AI models via Ollama.

    Attributes:
        platform_target: Target platform for optimization
        target_duration_seconds: Target script duration
        structure_type: Script structure to use
        words_per_second: Narration speed (for duration estimation)
        include_cta: Whether to include call-to-action
        tone: Script tone (engaging, mysterious, educational, etc.)
        ai_model: AI model to use for generation (default: Qwen3:30b)
        ai_api_base: Base URL for Ollama API
        ai_temperature: AI generation temperature (0.0-2.0)
        ai_timeout: AI request timeout in seconds
    """

    platform_target: PlatformTarget = PlatformTarget.YOUTUBE_MEDIUM
    target_duration_seconds: int = 90
    structure_type: ScriptStructure = ScriptStructure.HOOK_DELIVER_CTA
    words_per_second: float = 2.5  # Average speaking rate
    include_cta: bool = True
    tone: ScriptTone = ScriptTone.ENGAGING
    # AI generation settings (required - all generation uses AI)
    ai_model: str = "qwen3:32b"
    ai_api_base: str = "http://localhost:11434"
    ai_temperature: float = 0.7
    ai_timeout: int = 120


class ScriptGenerator:
    """Generate script drafts (v1) from ideas and titles using local AI models.

    This class uses Qwen3:30b via Ollama for all script generation.
    AI availability is required - an error is raised if AI is not available.
    """

    def __init__(self, config: Optional[ScriptGeneratorConfig] = None):
        """Initialize ScriptGenerator with configuration.

        Args:
            config: Optional generation configuration

        Raises:
            RuntimeError: If AI module is not available
        """
        self.config = config or ScriptGeneratorConfig()
        self._ai_generator = None
        self._ai_available = False
        self._init_ai_generator()

    def _init_ai_generator(self):
        """Initialize AI generator."""
        ai_module = _get_ai_generator_module()
        if ai_module is None:
            error_msg = "AI script generator module not available. Cannot proceed without AI."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        try:
            ai_config = ai_module.AIScriptGeneratorConfig(
                model=self.config.ai_model,
                api_base=self.config.ai_api_base,
                temperature=self.config.ai_temperature,
                timeout=self.config.ai_timeout,
                enable_ai=True,
            )
            self._ai_generator = ai_module.AIScriptGenerator(config=ai_config)
            self._ai_available = self._ai_generator.is_available()

            if self._ai_available:
                logger.info(f"AI script generation initialized with model: {self.config.ai_model}")
            else:
                logger.warning(
                    f"AI model '{self.config.ai_model}' not available at {self.config.ai_api_base}"
                )
        except Exception as e:
            logger.error(f"Failed to initialize AI generator: {e}")
            self._ai_generator = None
            self._ai_available = False

    def is_ai_available(self) -> bool:
        """Check if AI-powered script generation is available.

        Returns:
            True if AI generation is available, False otherwise
        """
        return self._ai_available

    def generate_script_v1(
        self, idea: "Idea", title: str, script_id: Optional[str] = None, **kwargs
    ) -> ScriptV1:
        """Generate initial script (v1) from idea and title using AI.

        All generation uses local AI models (Qwen2.5-14B-Instruct).
        An error is raised if AI is not available.

        Args:
            idea: Source Idea object
            title: Title variant (v1) to use
            script_id: Optional script ID (generated if not provided)
            **kwargs: Additional configuration overrides

        Returns:
            ScriptV1 object with AI-generated structured script

        Raises:
            ValueError: If idea or title is invalid
            RuntimeError: If AI generation is unavailable or fails
        """
        if not idea:
            raise ValueError("Idea cannot be None")
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")

        # Override config with kwargs
        config = self._apply_config_overrides(kwargs)

        # Check if AI is available
        if not self._ai_available:
            error_msg = (
                f"AI script generation is not available. "
                f"Please ensure Ollama is running with model '{config.ai_model}' at {config.ai_api_base}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Generate script ID if not provided
        if not script_id:
            script_id = self._generate_script_id(idea, title)

        logger.info(f"Generating script with AI for '{title}'")
        full_text, sections = self._generate_with_ai(idea, title, config)

        if full_text is None:
            error_msg = (
                f"AI script generation failed for '{title}'. "
                f"Please check that Ollama is running and the model '{config.ai_model}' is available."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        logger.info("AI script generation successful")

        # Calculate total duration
        total_duration = sum(s.estimated_duration_seconds for s in sections)

        # Create ScriptV1 object
        script = ScriptV1(
            script_id=script_id,
            idea_id=getattr(idea, "id", "unknown"),
            title=title,
            full_text=full_text,
            sections=sections,
            total_duration_seconds=total_duration,
            structure_type=config.structure_type,
            platform_target=config.platform_target,
            metadata={
                "idea_concept": idea.concept if hasattr(idea, "concept") else "",
                "idea_genre": idea.genre.value if hasattr(idea, "genre") else "unknown",
                "target_audience": getattr(idea, "target_audience", "general"),
                "generation_config": {
                    "tone": (
                        config.tone.value if hasattr(config.tone, "value") else str(config.tone)
                    ),
                    "target_duration": config.target_duration_seconds,
                    "words_per_second": config.words_per_second,
                    "ai_model": config.ai_model,
                },
                "ai_generated": True,
            },
            notes=f"Generated from idea '{getattr(idea, 'title', 'untitled')}' with title '{title}' (AI-powered)",
        )

        return script

    def _generate_with_ai(self, idea: "Idea", title: str, config: ScriptGeneratorConfig) -> tuple:
        """Generate script content using AI.

        Args:
            idea: Source Idea object
            title: Script title
            config: Generation configuration

        Returns:
            Tuple of (full_text, sections) if successful, (None, None) otherwise
        """
        if not self._ai_generator:
            return None, None

        try:
            # Build idea text from Idea object
            idea_parts = []
            if hasattr(idea, "concept") and idea.concept:
                idea_parts.append(f"Concept: {idea.concept}")
            if hasattr(idea, "synopsis") and idea.synopsis:
                idea_parts.append(f"Synopsis: {idea.synopsis}")
            if hasattr(idea, "hook") and idea.hook:
                idea_parts.append(f"Hook: {idea.hook}")
            if hasattr(idea, "premise") and idea.premise:
                idea_parts.append(f"Premise: {idea.premise}")
            if hasattr(idea, "genre"):
                genre_value = idea.genre.value if hasattr(idea.genre, "value") else str(idea.genre)
                idea_parts.append(f"Genre: {genre_value}")
            if hasattr(idea, "target_audience") and idea.target_audience:
                idea_parts.append(f"Target audience: {idea.target_audience}")

            idea_text = " | ".join(idea_parts) if idea_parts else "General content"

            # Get platform string
            platform = (
                config.platform_target.value
                if hasattr(config.platform_target, "value")
                else str(config.platform_target)
            )

            # Get tone string
            tone = config.tone.value if hasattr(config.tone, "value") else str(config.tone)

            # Generate full script using AI (title + idea_text + random seed)
            full_text = self._ai_generator.generate_script(
                title=title,
                idea_text=idea_text,
                target_duration_seconds=config.target_duration_seconds,
                platform=platform,
                tone=tone,
            )

            if full_text is None:
                return None, None

            # Create sections from AI-generated text
            sections = self._create_sections_from_ai_text(full_text, config)

            return full_text, sections

        except Exception as e:
            logger.error(f"AI script generation error: {e}")
            return None, None

    def _create_sections_from_ai_text(
        self, full_text: str, config: ScriptGeneratorConfig
    ) -> List[ScriptSection]:
        """Create section objects from AI-generated text.

        Since AI generates a cohesive script, we estimate section boundaries
        based on the target duration ratios.

        Args:
            full_text: AI-generated script text
            config: Generation configuration

        Returns:
            List of ScriptSection objects
        """
        # Calculate section durations based on structure type
        if config.structure_type == ScriptStructure.HOOK_DELIVER_CTA:
            intro_ratio, body_ratio, conclusion_ratio = 0.15, 0.70, 0.15
        elif config.structure_type == ScriptStructure.THREE_ACT:
            intro_ratio, body_ratio, conclusion_ratio = 0.25, 0.50, 0.25
        elif config.structure_type == ScriptStructure.PROBLEM_SOLUTION:
            intro_ratio, body_ratio, conclusion_ratio = 0.30, 0.50, 0.20
        else:
            intro_ratio, body_ratio, conclusion_ratio = 0.20, 0.60, 0.20

        total_words = len(full_text.split())

        # Split text roughly by word count
        words = full_text.split()
        intro_words = int(total_words * intro_ratio)
        body_words = int(total_words * body_ratio)

        intro_text = " ".join(words[:intro_words])
        body_text = " ".join(words[intro_words : intro_words + body_words])
        conclusion_text = " ".join(words[intro_words + body_words :])

        # Calculate durations
        intro_duration = int(config.target_duration_seconds * intro_ratio)
        body_duration = int(config.target_duration_seconds * body_ratio)
        conclusion_duration = int(config.target_duration_seconds * conclusion_ratio)

        sections = [
            ScriptSection(
                section_type="introduction",
                content=intro_text,
                estimated_duration_seconds=intro_duration,
                purpose="AI-generated hook to grab attention",
                notes=f"Generated with {config.ai_model}",
            ),
            ScriptSection(
                section_type="body",
                content=body_text,
                estimated_duration_seconds=body_duration,
                purpose="AI-generated main content",
                notes=f"Generated with {config.ai_model}",
            ),
            ScriptSection(
                section_type="conclusion",
                content=conclusion_text,
                estimated_duration_seconds=conclusion_duration,
                purpose="AI-generated conclusion",
                notes=f"Generated with {config.ai_model}",
            ),
        ]

        return sections

    def _apply_config_overrides(self, kwargs: Dict[str, Any]) -> ScriptGeneratorConfig:
        """Apply configuration overrides from kwargs."""
        config = ScriptGeneratorConfig(
            platform_target=kwargs.get("platform_target", self.config.platform_target),
            target_duration_seconds=kwargs.get(
                "target_duration_seconds", self.config.target_duration_seconds
            ),
            structure_type=kwargs.get("structure_type", self.config.structure_type),
            words_per_second=kwargs.get("words_per_second", self.config.words_per_second),
            include_cta=kwargs.get("include_cta", self.config.include_cta),
            tone=kwargs.get("tone", self.config.tone),
            # AI settings
            ai_model=kwargs.get("ai_model", self.config.ai_model),
            ai_api_base=kwargs.get("ai_api_base", self.config.ai_api_base),
            ai_temperature=kwargs.get("ai_temperature", self.config.ai_temperature),
            ai_timeout=kwargs.get("ai_timeout", self.config.ai_timeout),
        )
        return config

    def _generate_script_id(self, idea: "Idea", title: str) -> str:
        """Generate a unique script ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        idea_id = getattr(idea, "id", "unknown")
        return f"script_v1_{idea_id}_{timestamp}"


__all__ = [
    "ScriptGenerator",
    "ScriptGeneratorConfig",
    "ScriptV1",
    "ScriptSection",
    "ScriptStructure",
    "PlatformTarget",
    "ScriptTone",
]
