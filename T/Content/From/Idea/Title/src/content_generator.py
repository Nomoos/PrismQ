"""Content Generator for creating v1 scripts from ideas and titles.

This module implements the content generation logic using local AI models:
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
# Path: T/Content/From/Idea/Title/src/content_generator.py
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
            from . import ai_content_generator as _ai_generator_module
        except ImportError:
            logger.warning("AI script generator module not available")
            _ai_generator_module = False
    return _ai_generator_module if _ai_generator_module else None


class ContentStructure(Enum):
    """Content structure types."""

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


class ContentTone(Enum):
    """Content tone options."""

    ENGAGING = "engaging"
    MYSTERIOUS = "mysterious"
    EDUCATIONAL = "educational"
    DRAMATIC = "dramatic"
    CONVERSATIONAL = "conversational"


@dataclass
class ContentSection:
    """A section of the script."""

    section_type: str  # "introduction", "body", "conclusion"
    content: str
    estimated_duration_seconds: int
    purpose: str  # What this section aims to achieve
    notes: str = ""


@dataclass
class ContentV1:
    """Initial script draft (version 1).

    Attributes:
        content_id: Unique identifier for this script
        idea_id: str
        title: The title (v1) this script was generated from
        full_text: Complete content text
        sections: Breakdown into intro, body, conclusion
        total_duration_seconds: Estimated total duration
        max_duration_seconds: Maximum allowed duration
        audience: Target audience information (age_range, gender, country)
        metadata: Additional metadata (includes AI model, seed, etc.)
        created_at: Creation timestamp
        version: Version number (integer, 1 for initial draft)
        notes: Additional notes or context
    """

    content_id: str
    idea_id: str
    title: str
    full_text: str
    sections: List[ContentSection]
    total_duration_seconds: int
    max_duration_seconds: int
    audience: Dict[str, str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: int = 1
    notes: str = ""

    def get_section(self, section_type: str) -> Optional[ContentSection]:
        """Get a specific section by type."""
        for section in self.sections:
            if section.section_type == section_type:
                return section
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content_id": self.content_id,
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
            "max_duration_seconds": self.max_duration_seconds,
            "audience": self.audience,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "version": self.version,
            "notes": self.notes,
        }


@dataclass
class ContentGeneratorConfig:
    """Configuration for AI-powered content generation.

    All content generation uses local AI models via Ollama.
    AI model and temperature are obtained from global configuration.

    Attributes:
        platform_target: Target platform for content optimization
        target_duration_seconds: Target script duration (default: 120s)
        max_duration_seconds: Maximum script duration (default: 175s, 5s before platform limits)
        structure_type: Content structure (hook_deliver_cta, three_act, etc.)
        tone: Content tone (engaging, mysterious, educational, etc.)
        audience: Target audience dict with age_range, gender, country
        words_per_second: Narration speed (for duration estimation)
        include_cta: Whether to include call-to-action
    """

    platform_target: PlatformTarget = PlatformTarget.YOUTUBE_MEDIUM
    target_duration_seconds: int = 120
    max_duration_seconds: int = 175
    structure_type: ContentStructure = ContentStructure.HOOK_DELIVER_CTA
    tone: ContentTone = ContentTone.ENGAGING
    audience: Dict[str, str] = field(
        default_factory=lambda: {
            "age_range": "13-23",
            "gender": "Female",
            "country": "United States",
        }
    )
    words_per_second: float = 2.5  # Average speaking rate
    include_cta: bool = True


class ContentGenerator:
    """Generate script drafts (v1) from ideas and titles using local AI models.

    This class uses Qwen3:30b via Ollama for all content generation.
    AI availability is required - an error is raised if AI is not available.
    """

    def __init__(self, config: Optional[ContentGeneratorConfig] = None):
        """Initialize ContentGenerator with configuration.

        Args:
            config: Optional generation configuration

        Raises:
            RuntimeError: If AI module is not available
        """
        self.config = config or ContentGeneratorConfig()
        self._ai_generator = None
        self._ai_available = False
        self._init_ai_generator()

    def _init_ai_generator(self):
        """Initialize AI generator using global AI configuration."""
        # Import global AI configuration
        try:
            from .ai_config import get_local_ai_config
            ai_model, ai_api_base, ai_temperature, ai_timeout = get_local_ai_config()
        except ImportError:
            logger.warning("Global AI configuration not available, using defaults")
            ai_model = "qwen3:32b"
            ai_api_base = "http://localhost:11434"
            ai_temperature = 0.7
            ai_timeout = 120
        
        ai_module = _get_ai_generator_module()
        if ai_module is None:
            error_msg = "AI script generator module not available. Cannot proceed without AI."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        try:
            ai_config = ai_module.AIContentGeneratorConfig(
                model=ai_model,
                api_base=ai_api_base,
                temperature=ai_temperature,
                timeout=ai_timeout,
                enable_ai=True,
            )
            self._ai_generator = ai_module.AIContentGenerator(config=ai_config)
            self._ai_available = self._ai_generator.is_available()

            if self._ai_available:
                logger.info(f"AI content generation initialized with model: {ai_model}")
            else:
                logger.warning(
                    f"AI model '{ai_model}' not available at {ai_api_base}"
                )
        except Exception as e:
            logger.error(f"Failed to initialize AI generator: {e}")
            self._ai_generator = None
            self._ai_available = False

    def is_ai_available(self) -> bool:
        """Check if AI-powered content generation is available.

        Returns:
            True if AI generation is available, False otherwise
        """
        return self._ai_available

    def generate_content_v1(
        self, idea: "Idea", title: str, content_id: Optional[str] = None, **kwargs
    ) -> ContentV1:
        """Generate initial script (v1) from idea and title using AI.

        All generation uses local AI models (Qwen2.5-14B-Instruct).
        An error is raised if AI is not available.

        Args:
            idea: Source Idea object
            title: Title variant (v1) to use
            content_id: Optional script ID (generated if not provided)
            **kwargs: Additional configuration overrides

        Returns:
            ContentV1 object with AI-generated structured script

        Raises:
            ValueError: If idea or title is invalid
            RuntimeError: If AI generation is unavailable or fails
        """
        # Validate inputs
        if not idea:
            raise ValueError("Idea cannot be None")
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        
        # Validate title length (reasonable limits)
        title = title.strip()
        if len(title) > 500:
            raise ValueError(f"Title too long ({len(title)} chars). Maximum: 500 characters")
        
        # Override config with kwargs
        config = self._apply_config_overrides(kwargs)
        
        # Validate configuration parameters
        if config.target_duration_seconds <= 0:
            raise ValueError(f"target_duration_seconds must be positive, got: {config.target_duration_seconds}")
        if config.max_duration_seconds <= 0:
            raise ValueError(f"max_duration_seconds must be positive, got: {config.max_duration_seconds}")
        if config.target_duration_seconds > config.max_duration_seconds:
            raise ValueError(
                f"target_duration_seconds ({config.target_duration_seconds}) cannot exceed "
                f"max_duration_seconds ({config.max_duration_seconds})"
            )
        if config.words_per_second <= 0:
            raise ValueError(f"words_per_second must be positive, got: {config.words_per_second}")
        
        # Validate audience if provided
        if config.audience:
            if not isinstance(config.audience, dict):
                raise ValueError("audience must be a dictionary")

        # Check if AI is available
        if not self._ai_available:
            # Get AI model from global config for error message
            try:
                from .ai_config import get_local_ai_model, get_local_ai_api_base
                ai_model = get_local_ai_model()
                ai_api_base = get_local_ai_api_base()
            except ImportError:
                ai_model = "qwen3:32b"
                ai_api_base = "http://localhost:11434"
            
            error_msg = (
                f"AI content generation is not available. "
                f"Please ensure Ollama is running with model '{ai_model}' at {ai_api_base}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Generate script ID if not provided
        if not content_id:
            content_id = self._generate_content_id(idea, title)

        logger.info(f"Generating script with AI for '{title}'")
        
        # Generate with AI - with timeout and error handling
        try:
            full_text, sections = self._generate_with_ai(idea, title, config)
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            raise RuntimeError(f"AI content generation failed: {str(e)}")

        if full_text is None:
            # Get AI model from global config for error message
            try:
                from .ai_config import get_local_ai_model
                ai_model = get_local_ai_model()
            except ImportError:
                ai_model = "qwen3:32b"
            
            error_msg = (
                f"AI content generation failed for '{title}'. "
                f"Please check that Ollama is running and the model '{ai_model}' is available."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        logger.info("AI content generation successful")

        # Calculate total duration
        total_duration = sum(s.estimated_duration_seconds for s in sections)

        # Create ContentV1 object
        # Get AI model from global config for metadata
        try:
            from .ai_config import get_local_ai_model
            ai_model = get_local_ai_model()
        except ImportError:
            ai_model = "qwen3:32b"
        
        script = ContentV1(
            content_id=content_id,
            idea_id=getattr(idea, "id", "unknown"),
            title=title,
            full_text=full_text,
            sections=sections,
            total_duration_seconds=total_duration,
            max_duration_seconds=config.max_duration_seconds,
            audience=config.audience,
            metadata={
                "idea_concept": idea.concept if hasattr(idea, "concept") else "",
                "idea_genre": idea.genre.value if hasattr(idea, "genre") else "unknown",
                "generation_config": {
                    "target_duration": config.target_duration_seconds,
                    "max_duration": config.max_duration_seconds,
                    "words_per_second": config.words_per_second,
                    "ai_model": ai_model,
                    "platform_target": config.platform_target.value,
                    "structure_type": config.structure_type.value,
                    "tone": config.tone.value,
                },
                "ai_generated": True,
            },
            notes=f"Generated from idea '{getattr(idea, 'title', 'untitled')}' with title '{title}' (AI-powered)",
        )

        return script

    def _generate_with_ai(self, idea: "Idea", title: str, config: ContentGeneratorConfig) -> tuple:
        """Generate script content using AI.

        Args:
            idea: Source Idea object
            title: Content title
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

            # Generate full script using AI (title + idea_text + random seed + audience)
            full_text = self._ai_generator.generate_content(
                title=title,
                idea_text=idea_text,
                target_duration_seconds=config.target_duration_seconds,
                max_duration_seconds=config.max_duration_seconds,
                audience=config.audience,
            )

            if full_text is None:
                return None, None

            # Create sections from AI-generated text
            sections = self._create_sections_from_ai_text(full_text, config)

            return full_text, sections

        except Exception as e:
            logger.error(f"AI content generation error: {e}")
            return None, None

    def _create_sections_from_ai_text(
        self, full_text: str, config: ContentGeneratorConfig
    ) -> List[ContentSection]:
        """Create section objects from AI-generated text.

        Since AI generates a cohesive script, we estimate section boundaries
        based on the target duration ratios.

        Args:
            full_text: AI-generated content text
            config: Generation configuration

        Returns:
            List of ContentSection objects
        """
        # Calculate section durations based on structure type
        if config.structure_type == ContentStructure.HOOK_DELIVER_CTA:
            intro_ratio, body_ratio, conclusion_ratio = 0.15, 0.70, 0.15
        elif config.structure_type == ContentStructure.THREE_ACT:
            intro_ratio, body_ratio, conclusion_ratio = 0.25, 0.50, 0.25
        elif config.structure_type == ContentStructure.PROBLEM_SOLUTION:
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

        # Get AI model from global config for notes
        try:
            from .ai_config import get_local_ai_model
            ai_model = get_local_ai_model()
        except ImportError:
            ai_model = "qwen3:32b"

        sections = [
            ContentSection(
                section_type="introduction",
                content=intro_text,
                estimated_duration_seconds=intro_duration,
                purpose="AI-generated hook to grab attention",
                notes=f"Generated with {ai_model}",
            ),
            ContentSection(
                section_type="body",
                content=body_text,
                estimated_duration_seconds=body_duration,
                purpose="AI-generated main content",
                notes=f"Generated with {ai_model}",
            ),
            ContentSection(
                section_type="conclusion",
                content=conclusion_text,
                estimated_duration_seconds=conclusion_duration,
                purpose="AI-generated conclusion",
                notes=f"Generated with {ai_model}",
            ),
        ]

        return sections

    def _apply_config_overrides(self, kwargs: Dict[str, Any]) -> ContentGeneratorConfig:
        """Apply configuration overrides from kwargs."""
        config = ContentGeneratorConfig(
            platform_target=kwargs.get("platform_target", self.config.platform_target),
            target_duration_seconds=kwargs.get(
                "target_duration_seconds", self.config.target_duration_seconds
            ),
            max_duration_seconds=kwargs.get(
                "max_duration_seconds", self.config.max_duration_seconds
            ),
            structure_type=kwargs.get("structure_type", self.config.structure_type),
            tone=kwargs.get("tone", self.config.tone),
            audience=kwargs.get("audience", self.config.audience),
            words_per_second=kwargs.get("words_per_second", self.config.words_per_second),
            include_cta=kwargs.get("include_cta", self.config.include_cta),
        )
        return config

    def _generate_content_id(self, idea: "Idea", title: str) -> str:
        """Generate a unique script ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        idea_id = getattr(idea, "id", "unknown")
        return f"script_v1_{idea_id}_{timestamp}"


__all__ = [
    "ContentGenerator",
    "ContentGeneratorConfig",
    "ContentV1",
    "ContentSection",
    "ContentStructure",
    "PlatformTarget",
    "ContentTone",
]
