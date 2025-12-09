"""Idea Creation module for generating Ideas from simple inputs.

This module provides functionality to create multiple Ideas from minimal
inputs like titles or descriptions, using AI-powered generation for
variable-length content optimized for different platforms.

Requires AI (Ollama) to be available for idea generation. If AI is not
available, an error is logged and an empty list is returned.
"""

import logging
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional

# Add parent directories to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
model_path = os.path.join(parent_dir, "Model")
sys.path.insert(0, os.path.join(model_path, "src"))
sys.path.insert(0, model_path)

from ai_generator import AIConfig, AIIdeaGenerator

from idea import ContentGenre, Idea, IdeaStatus

logger = logging.getLogger(__name__)


@dataclass
class CreationConfig:
    """Configuration for idea creation process.

    Attributes:
        min_title_length: Minimum title length in characters
        max_title_length: Maximum title length in characters
        min_story_length: Minimum story/synopsis length in words
        max_story_length: Maximum story/synopsis length in words
        variation_degree: How different generated ideas should be (low/medium/high)
        include_all_fields: Whether to generate all narrative fields
        use_ai: Whether to use AI for generation (requires Ollama)
        ai_model: AI model to use (e.g., "qwen3:32b")
        ai_temperature: Temperature for AI generation (0.0-2.0)
        default_num_ideas: Default number of ideas to generate
        prompt_template: Custom prompt template for AI generation (optional)
    """

    min_title_length: int = 20
    max_title_length: int = 100
    min_story_length: int = 100
    max_story_length: int = 1000
    variation_degree: Literal["low", "medium", "high"] = "medium"
    include_all_fields: bool = True
    use_ai: bool = True  # Enable AI by default
    ai_model: str = "qwen3:32b"  # Best for RTX 5090
    ai_temperature: float = 0.8
    default_num_ideas: int = 10  # Default to 10 ideas as per requirements
    prompt_template: Optional[str] = None  # Custom prompt template


class IdeaCreator:
    """Create multiple Ideas from simple inputs like titles or descriptions.

    This class generates rich, detailed Ideas from minimal input using
    AI-powered content generation (via Ollama) with variable length optimization.
    AI is required - if AI is not available, an error is logged and an empty list is returned.
    """

    def __init__(self, config: Optional[CreationConfig] = None):
        """Initialize IdeaCreator with configuration.

        Args:
            config: Optional creation configuration
        """
        self.config = config or CreationConfig()

        # Initialize AI generator if enabled
        self.ai_generator = None
        if self.config.use_ai:
            ai_config = AIConfig(model=self.config.ai_model, temperature=self.config.ai_temperature)
            self.ai_generator = AIIdeaGenerator(ai_config)

            if self.ai_generator.available:
                logger.info(f"AI generation enabled with model: {self.config.ai_model}")
                # Pass prompt template to AI generator if configured (only if AI is available)
                if self.config.prompt_template:
                    self.ai_generator.set_prompt_template(self.config.prompt_template)
            else:
                logger.error(
                    "AI generation requested but Ollama not available. Ideas cannot be created without AI."
                )
                self.ai_generator = None

    def create_from_title(
        self,
        title: str,
        num_ideas: Optional[int] = None,  # Use default from config if None
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[ContentGenre] = None,
        length_target: Optional[str] = None,
        **kwargs,
    ) -> List[Idea]:
        """Create multiple Ideas from a title.

        Args:
            title: Base title to generate ideas from
            num_ideas: Number of ideas to generate (default: 10 from config)
            target_platforms: Optional target platforms
            target_formats: Optional target formats
            genre: Optional content genre
            length_target: Optional length target specification
            **kwargs: Additional arguments to pass to Idea creation

        Returns:
            List of generated Idea instances (empty list if AI not available)

        Raises:
            ValueError: If title is empty or num_ideas < 1
        """
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")

        # Use default from config if not specified
        if num_ideas is None:
            num_ideas = self.config.default_num_ideas

        if num_ideas < 1:
            raise ValueError("num_ideas must be at least 1")

        # AI is required for idea generation
        if not self.ai_generator:
            logger.error(
                "Cannot create ideas: AI generator not available. Please ensure Ollama is running."
            )
            return []

        try:
            ai_ideas = self.ai_generator.generate_ideas_from_title(
                title=title,
                num_ideas=num_ideas,
                target_platforms=target_platforms,
                target_formats=target_formats,
                genre=genre.value if genre else None,
                length_target=length_target,
            )

            if ai_ideas:
                return self._create_ideas_from_ai_data(
                    ai_ideas=ai_ideas,
                    target_platforms=target_platforms,
                    target_formats=target_formats,
                    genre=genre,
                    length_target=length_target,
                    source_type="title",
                    source=title,
                    **kwargs,
                )
            else:
                logger.error("AI generation returned no ideas")
                return []
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return []

    def create_from_description(
        self,
        description: str,
        num_ideas: Optional[int] = None,  # Use default from config if None
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[ContentGenre] = None,
        length_target: Optional[str] = None,
        **kwargs,
    ) -> List[Idea]:
        """Create multiple Ideas from a description.

        Args:
            description: Base description to generate ideas from
            num_ideas: Number of ideas to generate (default: 10 from config)
            target_platforms: Optional target platforms
            target_formats: Optional target formats
            genre: Optional content genre
            length_target: Optional length target specification
            **kwargs: Additional arguments to pass to Idea creation

        Returns:
            List of generated Idea instances (empty list if AI not available)

        Raises:
            ValueError: If description is empty or num_ideas < 1
        """
        if not description or not description.strip():
            raise ValueError("Description cannot be empty")

        # Use default from config if not specified
        if num_ideas is None:
            num_ideas = self.config.default_num_ideas

        if num_ideas < 1:
            raise ValueError("num_ideas must be at least 1")

        # AI is required for idea generation
        if not self.ai_generator:
            logger.error(
                "Cannot create ideas: AI generator not available. Please ensure Ollama is running."
            )
            return []

        try:
            ai_ideas = self.ai_generator.generate_ideas_from_description(
                description=description,
                num_ideas=num_ideas,
                target_platforms=target_platforms,
                target_formats=target_formats,
                genre=genre.value if genre else None,
                length_target=length_target,
            )

            if ai_ideas:
                return self._create_ideas_from_ai_data(
                    ai_ideas=ai_ideas,
                    target_platforms=target_platforms,
                    target_formats=target_formats,
                    genre=genre,
                    length_target=length_target,
                    source_type="description",
                    source=description,
                    **kwargs,
                )
            else:
                logger.error("AI generation returned no ideas")
                return []
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return []

    def _create_ideas_from_ai_data(
        self,
        ai_ideas: List[Dict[str, Any]],
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[ContentGenre] = None,
        length_target: Optional[str] = None,
        source_type: str = "unknown",
        source: str = "",
        **kwargs,
    ) -> List[Idea]:
        """Create Idea objects from AI-generated data.

        Args:
            ai_ideas: List of idea dictionaries from AI
            target_platforms: Target platforms
            target_formats: Target formats
            genre: Content genre
            length_target: Target length
            source_type: Type of source (title/description)
            source: Original source text
            **kwargs: Additional Idea arguments

        Returns:
            List of Idea instances
        """
        ideas = []
        for i, ai_idea in enumerate(ai_ideas):
            idea = Idea(
                title=ai_idea.get("title", f"Untitled Idea {i + 1}"),
                concept=ai_idea.get("concept", ""),
                idea=ai_idea.get(
                    "idea_text", ai_idea.get("title", "")
                ),  # Use idea_text or title as idea spark
                premise=ai_idea.get("premise", ""),
                logline=ai_idea.get("logline", ""),
                hook=ai_idea.get("hook", ""),
                synopsis=ai_idea.get("synopsis", ""),
                story_premise=ai_idea.get("premise", ""),  # Same as premise
                skeleton=ai_idea.get("skeleton", ""),
                outline=ai_idea.get("outline", ""),
                target_platforms=target_platforms or ["youtube", "medium"],
                target_formats=target_formats or ["text", "video"],
                genre=genre or ContentGenre.OTHER,
                length_target=length_target or "variable",
                keywords=ai_idea.get("keywords", []),
                themes=ai_idea.get("themes", []),
                status=IdeaStatus.DRAFT,
                notes=f"AI-generated from {source_type}: '{source}' (variation {i + 1}/{len(ai_ideas)})",
                created_by=kwargs.get("created_by", "IdeaCreator-AI"),
                **{k: v for k, v in kwargs.items() if k != "created_by"},
            )
            ideas.append(idea)

        return ideas


__all__ = ["IdeaCreator", "CreationConfig"]
