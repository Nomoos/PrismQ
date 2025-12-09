"""AI-powered Idea generation using local LLMs via Ollama.

This module provides AI generation capabilities for creating Ideas using
local LLM models through Ollama API. It supports various high-quality models
optimized for RTX 5090 and other high-end GPUs.

Prompts are stored as separate text files in _meta/prompts/ for easier
maintenance and editing.
"""

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import requests

logger = logging.getLogger(__name__)


# =============================================================================
# PROMPT FILE LOADING
# =============================================================================

_PROMPTS_DIR = Path(__file__).parent.parent / "_meta" / "prompts"


def _load_prompt(filename: str) -> str:
    """Load a prompt from the prompts directory.

    Args:
        filename: Name of the prompt file (e.g., 'idea_from_title.txt')

    Returns:
        The prompt text content

    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    prompt_path = _PROMPTS_DIR / filename
    return prompt_path.read_text(encoding="utf-8")


def list_available_prompts() -> List[str]:
    """List all available prompt templates in the prompts directory.
    
    Returns:
        List of prompt template names (without .txt extension)
    """
    if not _PROMPTS_DIR.exists():
        return []
    
    prompts = []
    for prompt_file in _PROMPTS_DIR.glob("*.txt"):
        prompts.append(prompt_file.stem)
    
    return sorted(prompts)


def apply_template(template: str, **kwargs) -> str:
    """Apply variable substitution to a template string.
    
    Supports multiple placeholder formats:
    - {variable} - Standard Python format strings
    - [VARIABLE] - Bracket notation (e.g., [FLAVOR], [INSERT TEXT HERE])
    - INSERTTEXTHERE or INSERT_TEXT_HERE - Custom placeholder formats
    
    Args:
        template: The template string with placeholders
        **kwargs: Variable values to substitute
        
    Returns:
        Template with variables substituted
        
    Examples:
        >>> apply_template("Hello {name}!", name="World")
        'Hello World!'
        >>> apply_template("Text: INSERTTEXTHERE", input="My text")
        'Text: My text'
        >>> apply_template("Flavor: [FLAVOR]", flavor="Mystery")
        'Flavor: Mystery'
    """
    # First handle custom placeholder formats
    result = template
    
    # Handle INSERTTEXTHERE and similar custom formats
    if 'input' in kwargs:
        input_value = kwargs['input']
        # Replace various custom placeholder formats
        result = result.replace('INSERTTEXTHERE', str(input_value))
        result = result.replace('INSERT_TEXT_HERE', str(input_value))
        result = result.replace('INSERT TEXT HERE', str(input_value))
        result = result.replace('[INSERT TEXT HERE]', str(input_value))
        result = result.replace('[INPUT]', str(input_value))  # Simpler placeholder
        result = result.replace('[TEXT]', str(input_value))   # Alternative placeholder
    
    # Handle [FLAVOR] and similar bracket notation
    if 'flavor' in kwargs:
        flavor_value = kwargs['flavor']
        result = result.replace('[FLAVOR]', str(flavor_value))
    
    # Handle generic [VARIABLE] bracket notation
    bracket_placeholders = re.findall(r'\[(\w+(?:\s+\w+)*)\]', result)
    for placeholder in bracket_placeholders:
        # Try to find matching key (case-insensitive)
        key = placeholder.lower().replace(' ', '_')
        if key in kwargs:
            result = result.replace(f'[{placeholder}]', str(kwargs[key]))
    
    # Then apply standard Python format string substitution
    # Use a safe approach that only substitutes available keys
    try:
        # Build a dict with only the placeholders that exist in the template
        # Find all {variable} patterns
        placeholders = re.findall(r'\{(\w+)\}', result)
        safe_kwargs = {k: v for k, v in kwargs.items() if k in placeholders}
        
        # Apply standard format substitution
        if safe_kwargs:
            result = result.format(**safe_kwargs)
    except (KeyError, ValueError) as e:
        logger.warning(f"Template substitution warning: {e}")
    
    return result


@dataclass
class AIConfig:
    """Configuration for AI model and generation.

    Attributes:
        model: Name of the Ollama model to use
        api_base: Base URL for Ollama API
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate
        timeout: Request timeout in seconds
    """

    model: str = "qwen3:32b"  # Default: Best for RTX 5090
    api_base: str = "http://localhost:11434"
    temperature: float = 0.8
    max_tokens: int = 2000
    timeout: int = 120


class AIIdeaGenerator:
    """Generate Ideas using local AI models via Ollama.

    This class handles communication with local LLM models through the
    Ollama API to generate rich, detailed Ideas with comprehensive
    narrative structure.
    """

    # Minimum length for generated idea text in characters
    MIN_IDEA_TEXT_LENGTH = 100

    def __init__(self, config: Optional[AIConfig] = None):
        """Initialize AI generator with configuration.

        Args:
            config: Optional AI configuration
        """
        self.config = config or AIConfig()
        self.available = self._check_ollama_availability()
        self._custom_prompt_template: Optional[str] = None

    def set_prompt_template(self, template: str) -> None:
        """Set a custom prompt template for AI generation.

        The template can use the following placeholders:
        - {num_ideas}: Number of ideas to generate
        - {input}: The title or description input
        - {platforms}: Target platforms
        - {formats}: Target formats
        - {genre}: Content genre
        - {length}: Target length

        Args:
            template: Custom prompt template string
        """
        self._custom_prompt_template = template
        logger.info("Custom prompt template set for AI generation")

    def get_prompt_template(self, for_description: bool = False) -> str:
        """Get the current prompt template.

        Args:
            for_description: If True, return template for description-based generation

        Returns:
            The current prompt template (custom or default from file)
        """
        if self._custom_prompt_template:
            return self._custom_prompt_template
        filename = "idea_from_description.txt" if for_description else "idea_from_title.txt"
        return _load_prompt(filename)

    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is available and running.

        Returns:
            True if Ollama is available, False otherwise
        """
        try:
            response = requests.get(f"{self.config.api_base}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False

    def generate_ideas_from_title(
        self,
        title: str,
        num_ideas: int = 10,
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[str] = None,
        length_target: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Generate multiple idea variations from a title using AI.

        Args:
            title: Base title to generate ideas from
            num_ideas: Number of idea variations to generate
            target_platforms: Target platforms for content
            target_formats: Target formats for content
            genre: Content genre
            length_target: Target content length

        Returns:
            List of dictionaries containing idea data
        """
        if not self.available:
            logger.warning("Ollama not available, returning empty list")
            return []

        prompt = self._create_title_prompt(
            title=title,
            num_ideas=num_ideas,
            target_platforms=target_platforms,
            target_formats=target_formats,
            genre=genre,
            length_target=length_target,
        )

        response_text = self._call_ollama(prompt)
        return self._parse_ideas_response(response_text, num_ideas)

    def generate_ideas_from_description(
        self,
        description: str,
        num_ideas: int = 10,
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[str] = None,
        length_target: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Generate multiple ideas from a description using AI.

        Args:
            description: Description to generate ideas from
            num_ideas: Number of ideas to generate
            target_platforms: Target platforms for content
            target_formats: Target formats for content
            genre: Content genre
            length_target: Target content length

        Returns:
            List of dictionaries containing idea data
        """
        if not self.available:
            logger.warning("Ollama not available, returning empty list")
            return []

        prompt = self._create_description_prompt(
            description=description,
            num_ideas=num_ideas,
            target_platforms=target_platforms,
            target_formats=target_formats,
            genre=genre,
            length_target=length_target,
        )

        response_text = self._call_ollama(prompt)
        return self._parse_ideas_response(response_text, num_ideas)

    def generate_with_custom_prompt(
        self,
        input_text: str,
        prompt_template_name: Optional[str] = None,
        prompt_template: Optional[str] = None,
        flavor: Optional[str] = None,
        use_random_flavor: bool = True,
        **kwargs,
    ) -> str:
        """Generate text using a custom prompt template.
        
        This method provides maximum flexibility for using custom prompts
        with the AI. You can either:
        1. Provide a prompt template name (loads from _meta/prompts/)
        2. Provide a prompt template string directly
        
        The template supports multiple placeholder formats:
        - {input} or {variable} - Standard Python format strings
        - [FLAVOR] - Thematic flavor for idea refinement
        - INSERTTEXTHERE - Custom placeholder format
        
        Args:
            input_text: The input text to process
            prompt_template_name: Name of prompt template file (without .txt)
            prompt_template: Template string directly (if not using a file)
            flavor: Optional thematic flavor for refinement (e.g., "Mystery + Unease").
                   If None and use_random_flavor=True, a weighted random flavor is selected.
            use_random_flavor: If True and flavor is None, uses weighted random flavor selection.
                              If False and flavor is None, no flavor is applied.
            **kwargs: Additional variables for template substitution
            
        Returns:
            Generated text from the AI
            
        Raises:
            ValueError: If neither template name nor template provided
            
        Examples:
            >>> gen = AIIdeaGenerator()
            >>> # Using a template file with specific flavor
            >>> result = gen.generate_with_custom_prompt(
            ...     "The Vanishing Tide",
            ...     prompt_template_name="idea_improvement",
            ...     flavor="Mystery + Unease"
            ... )
            >>> # Using weighted random flavor (default)
            >>> result = gen.generate_with_custom_prompt(
            ...     "Acadia Night Hikers",
            ...     prompt_template_name="idea_improvement"
            ... )  # Automatically selects weighted random flavor
            >>> # No flavor
            >>> result = gen.generate_with_custom_prompt(
            ...     "My story",
            ...     prompt_template="Improve this: {input}",
            ...     use_random_flavor=False
            ... )
        """
        # Validate template parameters first (before availability check)
        if not prompt_template_name and not prompt_template:
            raise ValueError("Must provide either prompt_template_name or prompt_template")
        
        if not self.available:
            logger.warning("Ollama not available, returning empty string")
            return ""
        
        # Load or use provided template
        if prompt_template_name:
            template_file = f"{prompt_template_name}.txt"
            template = _load_prompt(template_file)
            logger.info(f"Loaded prompt template: {prompt_template_name}")
        else:
            template = prompt_template
            logger.info("Using provided prompt template string")
        
        # Apply template with input text, flavor, and any additional kwargs
        kwargs['input'] = input_text
        
        # Handle flavor selection
        if flavor:
            kwargs['flavor'] = flavor
            logger.info(f"Using specified flavor: {flavor}")
        elif use_random_flavor and '[FLAVOR]' in template:
            # Import here to avoid circular dependency
            from flavors import pick_weighted_flavor
            selected_flavor = pick_weighted_flavor()
            kwargs['flavor'] = selected_flavor
            logger.info(f"Using weighted random flavor: {selected_flavor}")
        
        prompt = apply_template(template, **kwargs)
        
        logger.debug(f"Generated prompt: {prompt[:200]}...")
        
        # Call AI and return raw response
        response_text = self._call_ollama(prompt)
        return response_text.strip()

    def _create_title_prompt(
        self,
        title: str,
        num_ideas: int,
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[str] = None,
        length_target: Optional[str] = None,
    ) -> str:
        """Create a prompt for generating ideas from a title.

        Uses the configured prompt template with variable substitution.

        Args:
            title: Base title
            num_ideas: Number of ideas to generate
            target_platforms: Target platforms
            target_formats: Target formats
            genre: Content genre
            length_target: Target length

        Returns:
            Formatted prompt string
        """
        platforms_str = ", ".join(target_platforms) if target_platforms else "youtube, medium"
        formats_str = ", ".join(target_formats) if target_formats else "text, video"
        genre_str = genre if genre else "general"
        length_str = length_target if length_target else "variable"

        template = self.get_prompt_template(for_description=False)

        return apply_template(
            template,
            num_ideas=num_ideas,
            input=title,
            platforms=platforms_str,
            formats=formats_str,
            genre=genre_str,
            length=length_str,
        )

    def _create_description_prompt(
        self,
        description: str,
        num_ideas: int,
        target_platforms: Optional[List[str]] = None,
        target_formats: Optional[List[str]] = None,
        genre: Optional[str] = None,
        length_target: Optional[str] = None,
    ) -> str:
        """Create a prompt for generating ideas from a description.

        Uses the configured prompt template with variable substitution.

        Args:
            description: Base description
            num_ideas: Number of ideas to generate
            target_platforms: Target platforms
            target_formats: Target formats
            genre: Content genre
            length_target: Target length

        Returns:
            Formatted prompt string
        """
        platforms_str = ", ".join(target_platforms) if target_platforms else "youtube, medium"
        formats_str = ", ".join(target_formats) if target_formats else "text, video"
        genre_str = genre if genre else "general"
        length_str = length_target if length_target else "variable"

        template = self.get_prompt_template(for_description=True)

        return apply_template(
            template,
            num_ideas=num_ideas,
            input=description,
            platforms=platforms_str,
            formats=formats_str,
            genre=genre_str,
            length=length_str,
        )

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API to generate content.

        Args:
            prompt: Prompt to send to the model

        Returns:
            Generated text response

        Raises:
            RuntimeError: If API call fails
        """
        try:
            response = requests.post(
                f"{self.config.api_base}/api/generate",
                json={
                    "model": self.config.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config.temperature,
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
            raise RuntimeError(f"Failed to generate ideas: {e}")

    def _parse_ideas_response(
        self, response_text: str, expected_count: int
    ) -> List[Dict[str, Any]]:
        """Parse AI response into idea dictionaries.

        Args:
            response_text: Raw response from AI
            expected_count: Expected number of ideas

        Returns:
            List of parsed idea dictionaries
        """
        try:
            # Try to extract JSON from response
            # Sometimes models add explanatory text before/after JSON
            start_idx = response_text.find("[")
            end_idx = response_text.rfind("]")

            if start_idx >= 0 and end_idx > start_idx:
                json_text = response_text[start_idx : end_idx + 1]
                ideas = json.loads(json_text)

                if isinstance(ideas, list):
                    # Validate and clean each idea
                    validated_ideas = []
                    for idea in ideas[:expected_count]:
                        if isinstance(idea, dict) and "title" in idea:
                            validated_ideas.append(self._validate_idea_dict(idea))

                    return validated_ideas

            logger.warning("Failed to parse JSON from AI response")
            return []

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            return []

    def _validate_idea_dict(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure all required fields exist in idea dict.

        Args:
            idea: Raw idea dictionary

        Returns:
            Validated idea dictionary with all fields
        """
        # Ensure all required fields exist
        required_fields = {
            "title": "",
            "concept": "",
            "premise": "",
            "logline": "",
            "hook": "",
            "synopsis": "",
            "skeleton": "",
            "outline": "",
            "keywords": [],
            "themes": [],
            "idea_text": "",
        }

        for field, default in required_fields.items():
            if field not in idea:
                idea[field] = default
            elif field in ["keywords", "themes"] and not isinstance(idea[field], list):
                idea[field] = [idea[field]] if idea[field] else []

        # Ensure idea_text meets minimum length requirement
        idea_text = idea.get("idea_text", "")
        if len(idea_text) < self.MIN_IDEA_TEXT_LENGTH:
            idea["idea_text"] = self._generate_idea_text(idea)

        return idea

    def _generate_idea_text(self, idea: Dict[str, Any]) -> str:
        """Generate idea_text field from other fields when missing or too short.

        Combines hook, premise, concept, and other fields to create a rich
        description that meets the minimum length requirement.

        Args:
            idea: The idea dictionary

        Returns:
            Generated idea_text of at least MIN_IDEA_TEXT_LENGTH characters
        """
        parts = []

        # Start with hook if available
        hook = idea.get("hook", "")
        if hook and len(hook) > 3:
            parts.append(hook)

        # Add premise
        premise = idea.get("premise", "")
        if premise and len(premise) > 3:
            parts.append(premise)

        # Add concept if still short
        text = " ".join(parts)
        if len(text) < self.MIN_IDEA_TEXT_LENGTH:
            concept = idea.get("concept", "")
            if concept and len(concept) > 3:
                parts.append(concept)

        # Add logline if still short
        text = " ".join(parts)
        if len(text) < self.MIN_IDEA_TEXT_LENGTH:
            logline = idea.get("logline", "")
            if logline and len(logline) > 3:
                parts.append(logline)

        # Add themes if still short
        text = " ".join(parts)
        if len(text) < self.MIN_IDEA_TEXT_LENGTH:
            themes = idea.get("themes", [])
            if themes:
                parts.append(f"Themes: {', '.join(str(t) for t in themes)}")

        # Add keywords if still short
        text = " ".join(parts)
        if len(text) < self.MIN_IDEA_TEXT_LENGTH:
            keywords = idea.get("keywords", [])
            if keywords:
                parts.append(f"Keywords: {', '.join(str(k) for k in keywords)}")

        # Combine all parts
        text = " ".join(parts)

        # If still too short, add title and synopsis excerpt
        title = idea.get("title", "")
        if len(text) < self.MIN_IDEA_TEXT_LENGTH and title:
            text = f"About: {title}. {text}" if text else f"About: {title}"

        synopsis = idea.get("synopsis", "")
        if len(text) < self.MIN_IDEA_TEXT_LENGTH and synopsis:
            # Add excerpt of synopsis
            excerpt = synopsis[:200].rsplit(" ", 1)[0] if len(synopsis) > 200 else synopsis
            text = f"{text} {excerpt}" if text else excerpt

        # Add skeleton if still short
        skeleton = idea.get("skeleton", "")
        if len(text) < self.MIN_IDEA_TEXT_LENGTH and skeleton:
            excerpt = skeleton[:150] if len(skeleton) > 150 else skeleton
            text = f"{text} Structure: {excerpt}" if text else f"Structure: {excerpt}"

        # Final fallback: pad with contextual description
        if len(text) < self.MIN_IDEA_TEXT_LENGTH:
            padding = f" This idea explores creative possibilities for engaging content targeting various platforms and formats."
            text = text + padding if text else padding.strip()

        return text


# Export public classes for the module
__all__ = ["AIIdeaGenerator", "AIConfig"]
