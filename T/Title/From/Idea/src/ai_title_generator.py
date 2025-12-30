"""AI-powered title generation from Ideas.

This module orchestrates AI-based title generation using the literary-focused prompt.
This is the ONLY approved way to generate titles from Ideas in this system.
Follows SOLID principles with dependency injection and single responsibility.
"""

import logging
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# Add parent directories to path for imports
current_file = Path(__file__)
t_module_dir = current_file.parent.parent.parent.parent.parent
model_path = t_module_dir / "Idea" / "Model"
sys.path.insert(0, str(model_path / "src"))
sys.path.insert(0, str(model_path))

from idea import Idea

# Import refactored components
# Try relative imports first (when used as package), fallback to absolute
try:
    from .ollama_client import OllamaClient, OllamaConfig
    from .prompt_loader import PromptLoader
    from .title_scorer import TitleScorer, ScoringConfig
    from .title_variant import TitleVariant
except ImportError:
    # Fallback for when module is imported directly (e.g., in tests)
    from ollama_client import OllamaClient, OllamaConfig
    from prompt_loader import PromptLoader
    from title_scorer import TitleScorer, ScoringConfig
    from title_variant import TitleVariant

logger = logging.getLogger(__name__)


class AIUnavailableError(Exception):
    """Exception raised when AI service (Ollama) is unavailable.
    
    This exception is raised when title generation cannot proceed because
    the AI service is not accessible.
    """
    pass


@dataclass
class TitleGeneratorConfig:
    """Configuration for AI title generation.
    
    Attributes:
        num_variants: Number of title variants to generate (3-10)
        temperature_min: Minimum temperature for randomization
        temperature_max: Maximum temperature for randomization
    """
    
    num_variants: int = 10
    temperature_min: float = 0.6
    temperature_max: float = 0.8


class AITitleGenerator:
    """Generate title variants from Ideas using AI.
    
    This is the ONLY approved method for generating titles in this system.
    It uses a literary-focused prompt that emphasizes emotional essence,
    symbolism, and book-style titles for narrative videos.
    
    The generator follows SOLID principles:
    - Single Responsibility: Orchestrates title generation workflow
    - Open/Closed: Extensible through dependency injection
    - Dependency Inversion: Depends on abstractions (injected dependencies)
    
    Example:
        >>> generator = AITitleGenerator()
        >>> idea = Idea(title="Story", concept="A tale of connection...")
        >>> variants = generator.generate_from_idea(idea, num_variants=5)
        >>> for variant in variants:
        ...     print(f"{variant.text} (score: {variant.score})")
    """
    
    def __init__(
        self,
        config: Optional[TitleGeneratorConfig] = None,
        ollama_client: Optional[OllamaClient] = None,
        prompt_loader: Optional[PromptLoader] = None,
        scorer: Optional[TitleScorer] = None
    ):
        """Initialize the AI title generator.
        
        Args:
            config: Generator configuration. Uses defaults if not provided.
            ollama_client: Ollama API client for text generation.
                          Creates default client if not provided.
            prompt_loader: Prompt template loader.
                          Creates default loader if not provided.
            scorer: Title quality scorer.
                   Creates default scorer if not provided.
        """
        self.config = config or TitleGeneratorConfig()
        self.ollama_client = ollama_client or OllamaClient()
        self.prompt_loader = prompt_loader or PromptLoader()
        self.scorer = scorer or TitleScorer()
        
        if not self.ollama_client.is_available():
            logger.warning(
                "Ollama is not currently available. "
                "Title generation will fail until Ollama is running."
            )
    
    def is_available(self) -> bool:
        """Check if AI title generation is available.
        
        Returns:
            True if Ollama service is accessible
        """
        return self.ollama_client.is_available()
    
    def generate_from_idea(
        self,
        idea: Idea,
        num_variants: Optional[int] = None
    ) -> List[TitleVariant]:
        """Generate title variants from an Idea using AI.
        
        This method generates multiple title options by calling the AI model
        multiple times with randomized temperature for diversity. Each call
        generates one high-quality title with varying temperature to ensure
        creative diversity.
        
        Args:
            idea: Idea object to generate titles from
            num_variants: Number of variants to generate (3-10).
                         Uses config default if not specified.
        
        Returns:
            List of TitleVariant objects sorted by quality score
        
        Raises:
            ValueError: If idea is invalid or num_variants out of range
            AIUnavailableError: If Ollama service is unavailable
        """
        # Validate inputs
        if not idea:
            raise ValueError("Idea cannot be None")
        if not idea.title and not idea.concept:
            raise ValueError("Idea must have at least a title or concept")
        
        # Determine number of variants
        n_variants = num_variants if num_variants is not None else self.config.num_variants
        if n_variants < 3 or n_variants > 10:
            raise ValueError("num_variants must be between 3 and 10")
        
        # Check AI availability
        if not self.is_available():
            error_msg = (
                "AI title generation unavailable: Ollama not running. "
                "Start Ollama service to generate titles."
            )
            logger.error(error_msg)
            raise AIUnavailableError(error_msg)
        
        # Create prompt with idea content (directly inserted without analysis)
        prompt = self._create_prompt(idea)
        logger.info(f"Generating {n_variants} title variants (one-by-one for quality)")
        logger.debug(f"Prompt:\n{'-' * 80}\n{prompt}\n{'-' * 80}")
        
        # Generate variants one-by-one with random temperature for diversity
        variants = []
        try:
            for i in range(n_variants):
                # Random temperature in sweet spot for creative titles
                temp = random.uniform(
                    self.config.temperature_min,
                    self.config.temperature_max
                )
                
                logger.debug(f"Generating title {i+1}/{n_variants} with temperature={temp:.2f}")
                
                # Generate title from AI
                response_text = self.ollama_client.generate(prompt, temperature=temp)
                
                # Parse and score the response
                variant = self._parse_response(response_text, idea)
                if variant:
                    variants.append(variant)
                    logger.debug(f"  Generated: '{variant.text}' (score={variant.score:.2f})")
                else:
                    logger.warning(f"  Failed to parse response for variant {i+1}")
            
            # Sort by score (highest first) for better quality results
            variants.sort(key=lambda v: v.score, reverse=True)
            
            logger.info(f"Successfully generated {len(variants)}/{n_variants} title variants")
            return variants
            
        except Exception as e:
            error_msg = f"AI title generation failed: {e}"
            logger.error(error_msg)
            raise AIUnavailableError(error_msg) from e
    
    def _create_prompt(self, idea: Idea) -> str:
        """Create the title generation prompt.
        
        This method directly inserts the Idea text into the prompt template
        without any analysis or preprocessing. The complete Idea content
        (concept or title) is passed as-is to the AI model.
        
        Args:
            idea: Idea object
        
        Returns:
            Formatted prompt string with idea content
        """
        # Extract the complete idea text without analysis
        # Use concept as primary content, fallback to title
        idea_text = idea.concept or idea.title or "No idea provided"
        
        # Load the literary-focused prompt template
        template = self.prompt_loader.get_title_generation_prompt()
        
        # Format with idea text (direct insertion without analysis)
        return template.format(IDEA=idea_text)
    
    def _parse_response(self, response_text: str, idea: Idea) -> Optional[TitleVariant]:
        """Parse AI response into a TitleVariant.
        
        The AI prompt generates a single title (plain text), so we
        clean it and create a variant with scoring.
        
        Args:
            response_text: Raw text from AI
            idea: Original idea (for extracting keywords)
        
        Returns:
            TitleVariant object or None if parsing fails
        """
        try:
            # Clean the response
            title_text = response_text.strip()
            
            # Remove quotes if present
            if title_text.startswith('"') and title_text.endswith('"'):
                title_text = title_text[1:-1]
            if title_text.startswith("'") and title_text.endswith("'"):
                title_text = title_text[1:-1]
            
            # Validate
            if not title_text:
                logger.warning("AI returned empty title")
                return None
            
            # Extract keywords from idea
            keywords = []
            if hasattr(idea, "keywords") and idea.keywords:
                keywords = idea.keywords[:3]
            
            # Infer style and calculate score
            style = self.scorer.infer_style(title_text)
            score = self.scorer.score_by_length(title_text)
            length = len(title_text)
            
            return TitleVariant(
                text=title_text,
                style=style,
                length=length,
                keywords=keywords,
                score=score
            )
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return None


def generate_titles_from_idea(
    idea: Idea,
    num_variants: int = 10
) -> List[TitleVariant]:
    """Convenience function to generate titles from an Idea.
    
    This is a simple wrapper around AITitleGenerator for ease of use.
    
    Args:
        idea: Idea object to generate titles from
        num_variants: Number of variants to generate (3-10, default 10)
    
    Returns:
        List of TitleVariant objects
    
    Raises:
        AIUnavailableError: If Ollama service is unavailable
    """
    generator = AITitleGenerator()
    return generator.generate_from_idea(idea, num_variants)


# Export public API
__all__ = [
    "AITitleGenerator",
    "TitleGeneratorConfig",
    "AIUnavailableError",
    "generate_titles_from_idea",
]
