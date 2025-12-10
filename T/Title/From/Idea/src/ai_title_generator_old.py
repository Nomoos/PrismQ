"""AI-powered Title Generation using local LLMs via Ollama.

This module provides AI generation capabilities for creating title variants
from Ideas using local LLM models (Qwen3:30b) through Ollama API.
Optimized for RTX 5090 and other high-end GPUs.

Prompts are stored as separate text files in _meta/prompts/ for easier
maintenance and editing.
"""

import json
import logging
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# Add parent directories to path for imports
current_file = Path(__file__)
t_module_dir = current_file.parent.parent.parent.parent.parent
model_path = t_module_dir / "Idea" / "Model"
sys.path.insert(0, str(model_path / "src"))
sys.path.insert(0, str(model_path))

from title_generator import TitleConfig, TitleVariant

from idea import ContentGenre, Idea

logger = logging.getLogger(__name__)


# =============================================================================
# PROMPT FILE LOADING
# =============================================================================

_PROMPTS_DIR = Path(__file__).parent.parent / "_meta" / "prompts"


def _load_prompt(filename: str) -> str:
    """Load a prompt from the prompts directory.

    Args:
        filename: Name of the prompt file (e.g., 'title_generation.txt')

    Returns:
        The prompt text content

    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    prompt_path = _PROMPTS_DIR / filename
    return prompt_path.read_text(encoding="utf-8")


class AIUnavailableError(Exception):
    """Exception raised when AI service (Ollama) is unavailable.

    This exception is raised instead of falling back to alternative methods,
    as per the requirement to not perform fallback when AI is unavailable.
    The caller should handle this exception and wait for AI to become available.
    """

    pass


@dataclass
class AITitleConfig:
    """Configuration for AI title generation.

    Attributes:
        model: Name of the Ollama model to use
        api_base: Base URL for Ollama API
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate
        timeout: Request timeout in seconds
        num_variants: Number of title variants to generate (3-10)
    """

    model: str = "qwen3:32b"  # Qwen3:30b for RTX 5090
    api_base: str = "http://localhost:11434"
    temperature: float = 0.7  # Fallback temperature (when not using randomization)
    max_tokens: int = 2000
    timeout: int = 60
    num_variants: int = 10
    
    # Temperature randomization for diversity (sweet spot for creative titles)
    # Random value between 0.6-0.8 for each variant
    temperature_min: float = 0.6
    temperature_max: float = 0.8
    
    # Title length scoring thresholds (in characters)
    ideal_length_min: int = 45
    ideal_length_max: int = 52
    good_length_min: int = 40
    good_length_max: int = 55
    acceptable_length_max: int = 60
    
    # Scoring values
    base_score: float = 0.85
    ideal_score: float = 0.95
    good_score: float = 0.90
    short_score: float = 0.80
    acceptable_score: float = 0.82
    long_score: float = 0.75
    
    # Style inference
    listicle_check_prefix_length: int = 10  # Check first N chars for numbers


class AITitleGenerator:
    """Generate title variants using local AI models via Ollama.

    This class handles communication with local LLM models (Qwen3:30b)
    through the Ollama API to generate creative, engaging title variants.
    Falls back to template-based generation if Ollama is unavailable.
    """

    def __init__(self, config: Optional[AITitleConfig] = None, manual_mode: bool = False):
        """Initialize AI title generator with configuration.

        Args:
            config: Optional AI configuration
            manual_mode: If True, enables manual mode where prompts are shown
                        and responses are entered by the user
        """
        self.config = config or AITitleConfig()
        self.manual_mode = manual_mode
        self.available = self._check_ollama_availability()
        self._custom_prompt_template: Optional[str] = None

        if not self.available and not manual_mode:
            logger.error(
                f"Ollama not available at {self.config.api_base}. "
                "AI title generation will not be possible until Ollama is available."
            )

    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is available and the model is loaded.

        Returns:
            True if Ollama is available, False otherwise
        """
        try:
            response = requests.get(f"{self.config.api_base}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama availability check failed: {e}")
            return False

    def is_available(self) -> bool:
        """Check if AI title generation is available.

        Returns:
            True if Ollama is available for AI generation
        """
        return self.available

    def set_prompt_template(self, template: str) -> None:
        """Set a custom prompt template for title generation.

        The template can use the following placeholders:
        - {num_variants}: Number of titles to generate
        - {title}: The idea title/topic
        - {concept}: The idea concept
        - {genre}: Content genre
        - {keywords}: Relevant keywords
        - {themes}: Main themes

        Args:
            template: Custom prompt template string
        """
        self._custom_prompt_template = template
        logger.info("Custom prompt template set for AI title generation")

    def get_prompt_template(self) -> str:
        """Get the current prompt template.

        Returns:
            The current prompt template (custom or default from file)
        """
        if self._custom_prompt_template:
            return self._custom_prompt_template
        return _load_prompt("title_generation.txt")

    def _read_multiline_input(self) -> str:
        """Read multi-line input from user until double newline or EOF.
        
        Continues reading lines until the user enters two consecutive empty lines
        or reaches EOF (Ctrl+D on Unix, Ctrl+Z on Windows).
        
        Returns:
            The combined input text with newlines preserved
        """
        lines = []
        empty_line_count = 0
        while True:
            try:
                line = input()
                if not line:
                    # Empty line - increment counter
                    empty_line_count += 1
                    if empty_line_count >= 2:
                        # Two consecutive empty lines - done
                        break
                else:
                    # Non-empty line - reset counter and add line
                    empty_line_count = 0
                    lines.append(line)
            except EOFError:
                break
        
        return "\n".join(lines).strip()

    def generate_from_idea(
        self, idea: Idea, num_variants: Optional[int] = None
    ) -> List[TitleVariant]:
        """Generate title variants from an Idea using AI.

        Args:
            idea: Idea object to generate titles from
            num_variants: Optional override for number of variants (3-10)

        Returns:
            List of TitleVariant instances

        Raises:
            ValueError: If idea is invalid or num_variants out of range
        """
        if not idea:
            raise ValueError("Idea cannot be None")
        if not idea.title and not idea.concept:
            raise ValueError("Idea must have at least a title or concept")

        # Determine number of variants
        n_variants = num_variants if num_variants is not None else self.config.num_variants
        if n_variants < 3 or n_variants > 10:
            raise ValueError("num_variants must be between 3 and 10")

        # In manual mode, skip availability check since user will provide responses
        if not self.available and not self.manual_mode:
            error_msg = (
                f"AI title generation unavailable: Ollama not running at {self.config.api_base}"
            )
            logger.error(error_msg)
            raise AIUnavailableError(error_msg)

        # Call Ollama multiple times to generate n_variants titles
        # The new prompt generates one title per call
        # Build prompt once (it's the same for all calls with the new single-title format)
        prompt = self._create_prompt(idea, n_variants)
        
        # Log the prompt for debugging (when logger is configured)
        logger.info(f"Generated prompt for {n_variants} title variants")
        logger.info(f"Prompt:\n{'-' * 80}\n{prompt}\n{'-' * 80}")
        
        # Generate variants with random temperature for diversity
        variants = []
        try:
            for i in range(n_variants):
                # Use random temperature between min and max for balanced creativity
                # Sweet spot (0.6-0.8) for creative titles without being chaotic
                temp = random.uniform(self.config.temperature_min, self.config.temperature_max)
                response_text = self._call_ollama(prompt, temperature=temp)
                variant = self._parse_single_title_response(response_text, idea)
                if variant:
                    variants.append(variant)
            
            return variants
        except Exception as e:
            error_msg = f"AI title generation failed: {e}"
            logger.error(error_msg)
            raise AIUnavailableError(error_msg) from e

    def _create_prompt(self, idea: Idea, num_variants: int) -> str:
        """Create the prompt for title generation.

        Args:
            idea: Idea object
            num_variants: Number of variants to generate

        Returns:
            Formatted prompt string
        """
        # Extract the complete idea text (concept is the primary content)
        idea_text = idea.concept or idea.title or "No idea provided"

        template = self.get_prompt_template()

        return template.format(IDEA=idea_text)

    def _call_ollama(self, prompt: str, temperature: Optional[float] = None) -> str:
        """Call Ollama API to generate titles.

        Args:
            prompt: Prompt to send to the model
            temperature: Optional temperature override for this call

        Returns:
            Generated text response

        Raises:
            RuntimeError: If API call fails
        """
        # Use provided temperature or fall back to config
        temp = temperature if temperature is not None else self.config.temperature
        
        # Log the prompt being sent to AI
        logger.debug(f"Sending prompt to AI (temperature={temp}):\n{prompt}")
        
        # Manual mode: show prompt and wait for user to provide response
        if self.manual_mode:
            print("\n" + "=" * 80)
            print("MANUAL MODE - PROMPT TO SEND TO AI")
            print("=" * 80)
            print(f"\nModel: {self.config.model}")
            print(f"Temperature: {temp}")
            print(f"\nPrompt:\n{'-' * 80}")
            print(prompt)
            print("-" * 80)
            print("\nInstructions:")
            print("1. Copy the prompt above")
            print(f"2. Run it in your AI tool (e.g., Ollama CLI: ollama run {self.config.model})")
            print("3. Paste the AI response below")
            print("\nEnter AI response (press Enter twice when done):")
            
            response_text = self._read_multiline_input()
            logger.info(f"Manual mode: Received {len(response_text)} characters of response")
            return response_text
        
        # Automatic mode: call Ollama API
        try:
            response = requests.post(
                f"{self.config.api_base}/api/generate",
                json={
                    "model": self.config.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temp,
                        "num_predict": self.config.max_tokens,
                    },
                },
                timeout=self.config.timeout,
            )

            response.raise_for_status()
            result = response.json()
            return result.get("response", "")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API call failed: {e}")
            raise RuntimeError(f"Failed to generate titles: {e}")

    def _parse_single_title_response(
        self, response_text: str, idea: Idea
    ) -> Optional[TitleVariant]:
        """Parse AI response for single title output (plain text).

        This method handles the new prompt format that outputs only the title text,
        not a JSON structure.

        Args:
            response_text: Raw response from AI (should be just the title)
            idea: Original idea (for extracting keywords)

        Returns:
            TitleVariant instance or None if parsing fails
        """
        try:
            # The new prompt outputs only the title text, so just clean and use it
            title_text = response_text.strip()
            
            # Basic validation
            if not title_text:
                logger.warning("AI returned empty title text")
                return None
            
            # Extract keywords from the idea for the variant
            keywords = []
            if hasattr(idea, "keywords") and idea.keywords:
                keywords = idea.keywords[:3]
            
            # Determine a style based on title characteristics
            style = self._infer_title_style(title_text)
            
            # Calculate a score based on title characteristics
            # Prefer titles in the ideal length range per prompt requirements
            length = len(title_text)
            
            # Use config thresholds and scores
            if self.config.ideal_length_min <= length <= self.config.ideal_length_max:
                score = self.config.ideal_score  # Ideal length (45-52 chars)
            elif self.config.good_length_min <= length <= self.config.good_length_max:
                score = self.config.good_score  # Good length (40-55 chars)
            elif length < self.config.good_length_min:
                score = self.config.short_score  # A bit short
            elif length <= self.config.acceptable_length_max:
                score = self.config.acceptable_score  # A bit long but acceptable (56-60 chars)
            else:
                score = self.config.long_score  # Too long
            
            return TitleVariant(
                text=title_text,
                style=style,
                length=length,
                keywords=keywords,
                score=score
            )
        except Exception as e:
            logger.error(f"Failed to parse single title response: {e}")
            return None

    def _infer_title_style(self, title_text: str) -> str:
        """Infer the style of a title based on its text.

        Args:
            title_text: The title text

        Returns:
            Style string
        """
        title_lower = title_text.lower()
        
        # Check for question
        if "?" in title_text or title_lower.startswith(("what", "why", "how", "when", "where", "who")):
            return "question"
        
        # Check for how-to
        if title_lower.startswith("how to"):
            return "how-to"
        
        # Check for listicle (numbers in first N characters)
        if any(char.isdigit() for char in title_text[:self.config.listicle_check_prefix_length]):
            return "listicle"
        
        # Default to direct style
        return "direct"

    def _parse_response(
        self, response_text: str, idea: Idea, expected_count: int
    ) -> List[TitleVariant]:
        """Parse AI response into TitleVariant objects.

        Args:
            response_text: Raw response from AI
            idea: Original idea (for fallback data)
            expected_count: Expected number of variants

        Returns:
            List of TitleVariant instances
        """
        try:
            # Try to extract JSON from response
            start_idx = response_text.find("[")
            end_idx = response_text.rfind("]")

            if start_idx >= 0 and end_idx > start_idx:
                json_text = response_text[start_idx : end_idx + 1]
                titles = json.loads(json_text)

                if isinstance(titles, list):
                    variants = []
                    for title_data in titles[:expected_count]:
                        if isinstance(title_data, dict) and "text" in title_data:
                            variant = self._create_variant_from_dict(title_data)
                            if variant:
                                variants.append(variant)

                    return variants

            logger.warning("Failed to parse JSON from AI response")
            return []

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            return []

    def _create_variant_from_dict(self, data: Dict[str, Any]) -> Optional[TitleVariant]:
        """Create a TitleVariant from parsed dictionary.

        Args:
            data: Parsed title data dictionary

        Returns:
            TitleVariant instance or None if invalid
        """
        try:
            text = str(data.get("text", "")).strip()
            if not text:
                return None

            style = str(data.get("style", "direct")).lower()
            valid_styles = {
                "direct",
                "question",
                "how-to",
                "curiosity",
                "authoritative",
                "listicle",
                "problem-solution",
                "comparison",
                "ultimate-guide",
                "benefit",
            }
            if style not in valid_styles:
                style = "direct"

            score = float(data.get("score", 0.8))
            score = max(0.0, min(1.0, score))  # Clamp to 0-1

            keywords = data.get("keywords", [])
            if not isinstance(keywords, list):
                keywords = [str(keywords)] if keywords else []
            keywords = [str(k) for k in keywords[:5]]  # Limit to 5 keywords

            return TitleVariant(
                text=text, style=style, length=len(text), keywords=keywords, score=score
            )

        except Exception as e:
            logger.warning(f"Failed to create variant from dict: {e}")
            return None


def generate_ai_titles_from_idea(
    idea: Idea, num_variants: int = 10, config: Optional[AITitleConfig] = None
) -> List[TitleVariant]:
    """Convenience function to generate titles from an idea using AI.

    Args:
        idea: Idea object to generate titles from
        num_variants: Number of variants to generate (3-10, default 10)
        config: Optional AI configuration

    Returns:
        List of TitleVariant instances
    """
    generator = AITitleGenerator(config)
    return generator.generate_from_idea(idea, num_variants)


# Export public classes for the module
__all__ = [
    "AITitleGenerator",
    "AITitleConfig",
    "AIUnavailableError",
    "generate_ai_titles_from_idea",
]
