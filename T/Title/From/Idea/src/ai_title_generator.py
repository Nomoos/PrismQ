"""AI-powered title generation from Ideas.

This module orchestrates AI-based title generation using the literary-focused prompt.
This is the ONLY approved way to generate titles from Ideas in this system.
Follows SOLID principles with dependency injection and single responsibility.
"""

import logging
import re
import random
import sys
import time
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
        length_gate_min: Hard minimum title length (characters). Variants
            shorter than this are discarded before AI scoring.
        length_gate_max: Hard maximum title length (characters). Variants
            longer than this are discarded before AI scoring.
        score_threshold: Minimum combined score (0.0-1.0) a variant must
            reach to be included in the final result. Variants below this
            threshold are dropped after AI scoring.
        use_batch_generation: When True, all variants are requested in a
            single AI call. When False (default), each variant is generated
            with an individual call at a randomised temperature.
    """
    
    num_variants: int = 5
    temperature_min: float = 0.6
    temperature_max: float = 0.8
    length_gate_min: int = 20
    length_gate_max: int = 80
    score_threshold: float = 0.90
    use_batch_generation: bool = False


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
        
        # Generate raw variants
        gen_start = time.monotonic()
        try:
            if self.config.use_batch_generation:
                raw_variants = self._generate_batch_variants(idea, n_variants)
            else:
                raw_variants = self._generate_one_by_one_variants(idea, n_variants)

            gen_elapsed = time.monotonic() - gen_start
            logger.info(
                f"Generated {len(raw_variants)}/{n_variants} raw variants in {gen_elapsed:.1f}s"
            )

            # Gate 1: Hard length filter — discard variants outside [length_gate_min, length_gate_max]
            length_passed = [
                v for v in raw_variants
                if self.config.length_gate_min <= v.length <= self.config.length_gate_max
            ]
            length_dropped = len(raw_variants) - len(length_passed)
            if length_dropped:
                logger.info(
                    f"Length gate [{self.config.length_gate_min}-{self.config.length_gate_max} chars]: "
                    f"dropped {length_dropped} variant(s)"
                )
            logger.info(f"{len(length_passed)} variant(s) passed length gate")

            # Gate 2: AI scoring of length-passing variants
            score_start = time.monotonic()
            logger.info(f"AI-scoring {len(length_passed)} variant(s)")
            for variant in length_passed:
                ai_score = self._ai_score_title(variant.text, idea)
                if ai_score > 0.0:
                    # Combine rule-based score (50%) with AI score (50%)
                    variant.score = (variant.score + ai_score) / 2.0
                    logger.debug(
                        f"  Combined score for '{variant.text}': {variant.score:.2f}"
                    )
            score_elapsed = time.monotonic() - score_start
            logger.info(f"AI scoring completed in {score_elapsed:.1f}s")

            # Gate 3: Score threshold — accept only variants at or above threshold
            variants = [
                v for v in length_passed if v.score >= self.config.score_threshold
            ]
            below_threshold = len(length_passed) - len(variants)
            if below_threshold:
                logger.info(
                    f"Score threshold {self.config.score_threshold:.2f}: "
                    f"dropped {below_threshold} variant(s)"
                )

            # Sort accepted variants by score (highest first)
            variants.sort(key=lambda v: v.score, reverse=True)

            total_elapsed = time.monotonic() - gen_start
            logger.info(
                f"Accepted {len(variants)}/{n_variants} title variants "
                f"(score >= {self.config.score_threshold:.2f}, total time: {total_elapsed:.1f}s)"
            )
            return variants

        except Exception as e:
            error_msg = f"AI title generation failed: {e}"
            logger.error(error_msg)
            raise AIUnavailableError(error_msg) from e
    
    def _generate_batch_variants(self, idea: Idea, n_variants: int) -> List[TitleVariant]:
        """Generate all title variants in a single AI call.
        
        Sends one prompt that asks the model for N titled variants at once,
        then parses the numbered-list response. Reduces total AI call count
        from N to 1 compared to one-by-one generation.
        
        Args:
            idea: Idea object to generate titles from
            n_variants: Number of titles to request
        
        Returns:
            List of parsed TitleVariant objects (may be fewer than n_variants
            if the model returns some unparseable lines)
        """
        template = self.prompt_loader.get_title_generation_batch_prompt()
        idea_text = idea.concept or idea.title or "No idea provided"
        prompt = template.format(IDEA=idea_text, COUNT=n_variants)
        
        logger.info(f"Generating {n_variants} title variants (batch mode, 1 AI call)")
        logger.debug(f"Batch prompt:\n{'-' * 80}\n{prompt}\n{'-' * 80}")
        
        # Use midpoint temperature — diversity comes from the prompt instructions
        temp = (self.config.temperature_min + self.config.temperature_max) / 2.0
        t0 = time.monotonic()
        response_text = self.ollama_client.generate(prompt, temperature=temp)
        elapsed = time.monotonic() - t0
        logger.debug(f"Batch AI response received in {elapsed:.1f}s")
        
        variants = self._parse_batch_response(response_text, idea)
        logger.info(f"Parsed {len(variants)}/{n_variants} variants from batch response")
        return variants
    
    def _generate_one_by_one_variants(self, idea: Idea, n_variants: int) -> List[TitleVariant]:
        """Generate title variants with individual AI calls (one per variant).
        
        Each call uses a randomly varied temperature for diversity. Slower
        than batch mode but allows per-variant temperature control.
        
        Args:
            idea: Idea object to generate titles from
            n_variants: Number of titles to generate
        
        Returns:
            List of parsed TitleVariant objects
        """
        prompt = self._create_prompt(idea)
        logger.info(f"Generating {n_variants} title variants (one-by-one mode, {n_variants} AI calls)")
        logger.debug(f"Prompt:\n{'-' * 80}\n{prompt}\n{'-' * 80}")
        
        variants = []
        for i in range(n_variants):
            temp = random.uniform(self.config.temperature_min, self.config.temperature_max)
            logger.debug(f"Generating title {i+1}/{n_variants} with temperature={temp:.2f}")
            
            t0 = time.monotonic()
            response_text = self.ollama_client.generate(prompt, temperature=temp)
            elapsed = time.monotonic() - t0
            logger.debug(f"  AI response received in {elapsed:.1f}s for variant {i+1}")
            
            variant = self._parse_response(response_text, idea)
            if variant:
                variants.append(variant)
                logger.debug(f"  Generated: '{variant.text}' (score={variant.score:.2f})")
            else:
                logger.warning(f"  Failed to parse response for variant {i+1}")
        return variants
    
    def _parse_batch_response(self, response_text: str, idea: Idea) -> List[TitleVariant]:
        """Parse a batch AI response containing multiple numbered titles.
        
        Expects the model to have returned a numbered list such as:
            1. The Weight of Unspoken Words
            2. Silence Spoke Loudest
            ...
        
        Also strips <think>...</think> blocks before parsing.
        
        Args:
            response_text: Raw text from AI containing a numbered list of titles
            idea: Original idea (for keyword extraction and scoring)
        
        Returns:
            List of TitleVariant objects; lines that cannot be parsed are skipped
        """
        # Strip <think>...</think> blocks
        response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
        
        keywords = []
        if hasattr(idea, "keywords") and idea.keywords:
            keywords = idea.keywords[:3]
        
        variants: List[TitleVariant] = []
        for line in response_text.splitlines():
            # Strip whitespace and leading numbering like "1.", "1)", "1 -", etc.
            line = line.strip()
            if not line:
                continue
            title_text = re.sub(r'^\d+[\.\)\-]\s*', '', line).strip()
            
            # Remove surrounding quotes if present
            if title_text.startswith('"') and title_text.endswith('"'):
                title_text = title_text[1:-1]
            if title_text.startswith("'") and title_text.endswith("'"):
                title_text = title_text[1:-1]
            
            if not title_text:
                continue
            
            style = self.scorer.infer_style(title_text)
            score = self.scorer.score_by_length(title_text)
            variants.append(TitleVariant(
                text=title_text,
                style=style,
                length=len(title_text),
                keywords=keywords,
                score=score,
            ))
        
        return variants
    
    def _ai_score_title(self, title_text: str, idea: Idea) -> float:
        """Score a title using AI based on readability, keywords, emotional impact and SEO.
        
        Uses the title_scoring.txt prompt template to evaluate each title.
        Returns 0.0 if AI scoring fails so the rule-based score is preserved.
        
        Args:
            title_text: The title to evaluate
            idea: Original idea for context
        
        Returns:
            Score between 0.0 and 1.0 (normalized from AI's 0-100 response),
            or 0.0 if scoring fails
        """
        try:
            template = self.prompt_loader.get_title_scoring_prompt()
            idea_text = idea.concept or idea.title or ""
            prompt = template.format(IDEA=idea_text, TITLE=title_text)
            
            # Use low temperature for consistent, deterministic scoring
            response_text = self.ollama_client.generate(prompt, temperature=0.1)
            
            # Extract the first integer (0-100) from the response
            numbers = re.findall(r'\b(\d{1,3})\b', response_text.strip())
            if numbers:
                score_int = int(numbers[0])
                # Clamp to valid 0-100 range
                score_int = max(0, min(100, score_int))
                return score_int / 100.0
            
            logger.warning(f"AI scoring returned no parseable score for '{title_text}'")
            return 0.0
            
        except Exception as e:
            logger.warning(f"AI scoring failed for '{title_text}': {e}")
            return 0.0
    
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
            # Strip <think>...</think> blocks (used by qwen3 thinking mode)
            response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)

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
    num_variants: int = 5
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
