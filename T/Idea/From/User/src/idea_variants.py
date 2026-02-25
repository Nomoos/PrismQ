"""Flavor-based Idea Generation System - SOLID Design.

This module provides the main API for generating ideas using flavors.
It follows SOLID principles:
- Single Responsibility: Idea generation logic only
- Open/Closed: Extended via flavor configuration, not code changes
- Dependency Inversion: Depends on FlavorLoader abstraction

Flavors are loaded from external JSON configuration (data/flavors.json).

**Input Handling**: Input text is passed directly to AI prompts without any 
parsing, extraction, validation, or cleaning. The system uses exactly what 
you provide, ensuring full flexibility in input format.
"""

import hashlib
import random
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

from flavor_loader import get_flavor_loader
from ai_generator import AIIdeaGenerator, AIConfig

logger = logging.getLogger(__name__)


# =============================================================================
# IDEA GENERATION SERVICE
# =============================================================================

class IdeaGenerator:
    """Generates ideas using flavor definitions.
    
    Single Responsibility: Generate idea content from input and flavor.
    """
    
    # Minimum length for AI-generated content to be considered valid
    MIN_AI_CONTENT_LENGTH = 20
    
    def __init__(self, flavor_loader=None, use_ai=True, ai_config=None):
        """Initialize idea generator.
        
        Args:
            flavor_loader: Optional FlavorLoader instance.
                          If None, uses global loader.
            use_ai: Whether to use AI generation (default: True)
            ai_config: Optional AIConfig instance for AI generation
            
        Raises:
            RuntimeError: If use_ai is True but Ollama is not available
        """
        self.loader = flavor_loader or get_flavor_loader()
        self.loader.ensure_loaded()
        
        # Initialize AI generator if requested
        self.ai_generator = None
        self.use_ai = use_ai
        if use_ai:
            config = ai_config or AIConfig()
            self.ai_generator = AIIdeaGenerator(config)
            if self.ai_generator.available:
                logger.info(f"AI generation enabled with model: {config.model}")
            else:
                error_msg = (
                    "AI generation requested but Ollama is not available. "
                    "Please ensure Ollama is installed and running. "
                    "Install from https://ollama.com/ and start with 'ollama serve'."
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)
    
    def generate_from_flavor(
        self,
        flavor_name: str,
        input_text: str,
        variation_index: int = 0,
        second_flavor_chance: float = 0.4,
        db: Optional[Any] = None,
        logger: Optional[logging.Logger] = None,
    ) -> Dict[str, Any]:
        """Generate an idea using a specific flavor.

        Starting from ``flavor_name`` the method uses
        :meth:`FlavorSelector.select_flavor_combination` to recursively add
        extra flavors.  Each additional flavor is appended with
        ``second_flavor_chance`` probability (matches
        ``FlavorSelector.MULTI_FLAVOR_CHANCE`` = 0.4 by default), producing:

            2nd flavor   40 %
            3rd flavor   16 %  (0.4²)
            4th flavor  6.4 %  (0.4³)  … and so on

        ``FlavorSelector.NO_FLAVOR_CHANCE`` (5 %) is also applied so that
        roughly 1 in 20 ideas is generated without any flavor, adding
        surprise variety to a batch.

        Args:
            flavor_name: Name of the primary flavor to use
            input_text: Raw input text from user (no parsing or processing)
            variation_index: Variation number for uniqueness
            second_flavor_chance: Probability (0.0-1.0) of adding each extra
                                  flavor recursively (default: 0.4)
            db: Optional database connection for direct save after generation
            logger: Optional logger for tracking
            
        Returns:
            Dictionary with minimal data (text + variant_name + optional idea_id)
            
        Raises:
            KeyError: If flavor not found
            ValueError: If input_text is empty
        """
        if not input_text:
            raise ValueError("input_text parameter is required and cannot be empty")

        # Validate primary flavor exists
        self.loader.get_flavor(flavor_name)
        seed = self._generate_seed(input_text, variation_index)

        # Build a recursive flavor combination starting from flavor_name
        selector = FlavorSelector(self.loader)
        combination = selector.select_flavor_combination(
            primary_flavor=flavor_name,
            seed=seed,
            multi_chance=second_flavor_chance,
            no_flavor_chance=FlavorSelector.NO_FLAVOR_CHANCE,
        )

        # combination may be empty (no-flavor wild card) or contain 1+ flavors
        variant_name = " + ".join(combination) if combination else "(no flavor)"
        if len(combination) > 1 and logger:
            logger.info(f"Using multi-flavor combination: {variant_name}")
        elif not combination and logger:
            logger.info("Using no-flavor (unguided) generation")

        # Generate complete refined idea using idea_improvement prompt
        if not self.ai_generator:
            raise RuntimeError(
                "AI generator not available. Cannot generate ideas without AI. "
                "Please ensure Ollama is installed and running."
            )

        # Build flavor text: joined names, or empty string when no flavor
        flavor_text = " and ".join(combination) if combination else ""

        # Use idea_improvement prompt to generate complete refined idea
        # Pass input_text directly without any parsing or transformation
        generated_idea = self.ai_generator.generate_with_custom_prompt(
            input_text=input_text,
            prompt_template_name="idea_improvement",
            flavor=flavor_text,
            use_random_flavor=False
        )
        
        # Validate content
        if not generated_idea or len(generated_idea) <= self.MIN_AI_CONTENT_LENGTH:
            raise RuntimeError(
                f"AI generated insufficient content. "
                f"Generated: {len(generated_idea) if generated_idea else 0} characters, "
                f"minimum required: {self.MIN_AI_CONTENT_LENGTH}."
            )
        
        # Save directly to database if provided (not preview mode)
        idea_id = None
        if db:
            try:
                idea_id = db.insert_idea(text=generated_idea, version=1)
                if logger:
                    logger.debug(f"Saved idea directly to database with ID: {idea_id}")
            except Exception as e:
                if logger:
                    logger.error(f"Failed to save idea to database: {e}")
                raise RuntimeError(f"Database save failed: {e}")
        
        # Return minimal data for display only
        result = {
            'text': generated_idea,
            'variant_name': variant_name,
            'source_input': input_text,
        }
        
        if idea_id:
            result['idea_id'] = idea_id
        
        return result
    
    def generate_multiple(
        self,
        input_text: str,
        count: int = 10,
        specific_flavors: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Generate multiple ideas from input.
        
        Args:
            input_text: Raw input text (no parsing)
            count: Number of ideas to generate
            specific_flavors: Optional list of specific flavors.
                            If None, uses weighted random selection.
                            
        Returns:
            List of generated ideas
            
        Raises:
            ValueError: If input_text is empty
        """
        if not input_text:
            raise ValueError("input_text parameter is required and cannot be empty")
        
        ideas = []
        
        if specific_flavors:
            # Use specified flavors
            selected_flavors = specific_flavors[:count]
        else:
            # Use weighted random selection
            selector = FlavorSelector(self.loader)
            selected_flavors = selector.select_multiple(count)
        
        for i, flavor_name in enumerate(selected_flavors):
            try:
                idea = self.generate_from_flavor(
                    flavor_name=flavor_name,
                    input_text=input_text,
                    variation_index=i,
                )
                ideas.append(idea)
            except Exception as e:
                print(f"Warning: Failed to generate with flavor {flavor_name}: {e}")
                continue
        
        return ideas
    
    # Helper methods
    
    @staticmethod
    def _generate_seed(input_text: str, variation_index: int) -> int:
        """Generate consistent seed from inputs.
        
        Args:
            input_text: Raw input text
            variation_index: Variation number
            
        Returns:
            Seed value for random generation
        """
        content = f"{input_text}{variation_index}"
        hash_obj = hashlib.md5(content.encode())
        return int(hash_obj.hexdigest()[:8], 16)
    
    @staticmethod
    def _generate_idea_hash(input_text: str, flavor_name: str, variation_index: int) -> str:
        """Generate unique hash for the idea.
        
        Args:
            input_text: Raw input text
            flavor_name: Flavor name
            variation_index: Variation number
            
        Returns:
            Unique hash string
        """
        content = f"{input_text}{flavor_name}{variation_index}{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @staticmethod
    def _humanize_topic(title: str) -> str:
        """Convert title to readable topic format."""
        topic = re.sub(r'[^\w\s-]', '', title)
        topic = topic.strip().lower()
        if topic:
            topic = topic[0].upper() + topic[1:]
        return topic if topic else "this topic"
    
    def _try_ai_generation(
        self,
        title: str,
        description: str,
        field_desc: str,
        flavor_name: str,
    ) -> str:
        """Generate content using AI.
        
        Args:
            title: Input title
            description: Optional description
            field_desc: Field description for the prompt
            flavor_name: Flavor name
            
        Returns:
            Generated content from AI
            
        Raises:
            RuntimeError: If AI generator is not available or generation fails
        """
        if not self.ai_generator:
            raise RuntimeError(
                "AI generator not available. Cannot generate ideas without AI. "
                "Please ensure Ollama is installed and running."
            )
        
        # Create input text
        input_text = title
        if description:
            input_text = f"{title}: {description}"
        
        # Use custom field generation prompt
        generated = self.ai_generator.generate_with_custom_prompt(
            input_text=input_text,
            prompt_template_name="field_generation",
            flavor=flavor_name,
            field_description=field_desc,
            use_random_flavor=False
        )
        
        # Validate content length
        if not generated or len(generated) <= self.MIN_AI_CONTENT_LENGTH:
            raise RuntimeError(
                f"AI generated insufficient content for '{field_desc}'. "
                f"Generated: {len(generated) if generated else 0} characters, "
                f"minimum required: {self.MIN_AI_CONTENT_LENGTH}."
            )
        
        logger.debug(f"AI generated content for '{field_desc}': {generated[:80]}...")
        return generated.strip()
    
    def _generate_focused_content(
        self,
        title: str,
        description: str,
        field_desc: str,
        flavor_name: str,
        seed: int,
    ) -> str:
        """Generate detailed content for the focus field.
        
        Uses AI generation (required).
        
        Raises:
            RuntimeError: If AI generation fails
        """
        # AI generation is required, no fallback
        return self._try_ai_generation(title, description, field_desc, flavor_name)
    
    def _generate_field_content(
        self,
        title: str,
        description: str,
        field_desc: str,
        flavor_name: str,
        seed: int,
    ) -> str:
        """Generate standard content for a field.
        
        Uses AI generation (required).
        
        Raises:
            RuntimeError: If AI generation fails
        """
        # AI generation is required, no fallback
        return self._try_ai_generation(title, description, field_desc, flavor_name)


# =============================================================================
# FLAVOR SELECTION SERVICE
# =============================================================================

class FlavorSelector:
    """Selects flavors using weighted random selection.
    
    Single Responsibility: Flavor selection logic only.
    """

    # Default number of ideas (slots) to generate
    DEFAULT_COUNT = 10

    # Base probability that each additional flavor is appended to a combination.
    # Produces the following per-level probabilities:
    #   1st flavor  100 %   (always)
    #   2nd flavor   40 %   (MULTI_FLAVOR_CHANCE)
    #   3rd flavor   16 %   (0.4²)
    #   4th flavor  6.4 %   (0.4³)
    #   5th flavor  2.56 %  (0.4⁴)  … and so on
    #
    # 0.4 keeps single-flavor as the plurality (~60 %) while making dual/triple
    # combinations meaningfully more common than the previous 0.3 setting.
    MULTI_FLAVOR_CHANCE: float = 0.4

    # Probability that a generation uses *no* flavor at all (unguided "wild card").
    # 5 % means roughly one unguided idea every other 10-idea batch — noticeable
    # but not dominant, adding surprise variety without overwhelming the output.
    NO_FLAVOR_CHANCE: float = 0.05

    def __init__(self, flavor_loader=None):
        """Initialize flavor selector.
        
        Args:
            flavor_loader: Optional FlavorLoader instance
        """
        self.loader = flavor_loader or get_flavor_loader()
        self.loader.ensure_loaded()
    
    def select_one(self, seed: Optional[int] = None) -> str:
        """Select a single flavor using weighted random selection.
        
        Args:
            seed: Optional seed for reproducibility
            
        Returns:
            Selected flavor name
        """
        rng = random.Random(seed) if seed is not None else random.Random()
        
        flavors = self.loader.list_flavor_names()
        weights = self.loader.get_weights()
        flavor_weights = [weights.get(f, 50) for f in flavors]
        
        return rng.choices(flavors, weights=flavor_weights, k=1)[0]

    def select_flavor_combination(
        self,
        primary_flavor: Optional[str] = None,
        seed: Optional[int] = None,
        multi_chance: float = MULTI_FLAVOR_CHANCE,
        no_flavor_chance: float = NO_FLAVOR_CHANCE,
    ) -> List[str]:
        """Select a flavor combination using recursive multi-flavor probability.

        Returns an empty list (no flavor) with ``no_flavor_chance`` probability,
        which is a perfectly valid case that produces unguided, neutral generation.

        Otherwise always selects at least one flavor, then each additional flavor
        is appended with ``multi_chance`` (default 40%), giving:

            1st flavor  100 %
            2nd flavor   40 %   (multi_chance)
            3rd flavor   16 %   (multi_chance²)
            4th flavor  6.4 %   (multi_chance³)
            5th flavor  2.56%   (multi_chance⁴)  … and so on

        All selections use weighted random so high-weight flavors appear more
        often.  Duplicates within a single combination are never produced.

        Args:
            primary_flavor: First flavor to include.  If None a weighted-random
                            flavor is chosen automatically.
            seed: Optional seed for reproducible results.
            multi_chance: Probability (0–1) of appending each extra flavor.
                          Default: ``MULTI_FLAVOR_CHANCE`` (0.4).
            no_flavor_chance: Probability (0–1) of returning an empty list,
                              i.e. no flavor at all.
                              Default: ``NO_FLAVOR_CHANCE`` (0.05).

        Returns:
            List of unique flavor names (may be empty when no_flavor_chance > 0).
        """
        rng = random.Random(seed) if seed is not None else random.Random()

        # Possibly return no flavors (valid case for unguided generation)
        if no_flavor_chance > 0.0 and rng.random() < no_flavor_chance:
            return []

        flavors = self.loader.list_flavor_names()
        weights = self.loader.get_weights()

        # --- first flavor ---
        if primary_flavor is not None:
            selected = [primary_flavor]
        else:
            flavor_weights = [weights.get(f, 50) for f in flavors]
            selected = [rng.choices(flavors, weights=flavor_weights, k=1)[0]]

        # --- recursively add more flavors ---
        remaining = [f for f in flavors if f not in selected]
        while remaining and rng.random() < multi_chance:
            remaining_weights = [weights.get(f, 50) for f in remaining]
            next_flavor = rng.choices(remaining, weights=remaining_weights, k=1)[0]
            selected.append(next_flavor)
            remaining = [f for f in remaining if f != next_flavor]

        return selected

    def select_multiple(
        self,
        count: int = DEFAULT_COUNT,
        seed: Optional[int] = None,
        allow_duplicates: bool = False,
    ) -> List[str]:
        """Select multiple flavors using weighted random selection.
        
        Args:
            count: Number of flavors to select (default: DEFAULT_COUNT = 10)
            seed: Optional seed for reproducibility
            allow_duplicates: If False, ensures unique flavors
            
        Returns:
            List of selected flavor names
        """
        rng = random.Random(seed) if seed is not None else random.Random()
        
        flavors = self.loader.list_flavor_names()
        weights = self.loader.get_weights()
        flavor_weights = [weights.get(f, 50) for f in flavors]
        
        if allow_duplicates or count > len(flavors):
            return rng.choices(flavors, weights=flavor_weights, k=count)
        
        # Ensure unique flavors
        selected = []
        remaining_flavors = flavors.copy()
        remaining_weights = flavor_weights.copy()
        
        for _ in range(min(count, len(flavors))):
            choice = rng.choices(remaining_flavors, weights=remaining_weights, k=1)[0]
            selected.append(choice)
            
            idx = remaining_flavors.index(choice)
            remaining_flavors.pop(idx)
            remaining_weights.pop(idx)
        
        return selected


# =============================================================================
# TEXT FORMATTING SERVICE
# =============================================================================

class IdeaFormatter:
    """Formats ideas for display.
    
    Single Responsibility: Text formatting only.
    """
    
    @staticmethod
    def format_as_text(idea: Dict[str, Any]) -> str:
        """Format idea as clean text without metadata.
        
        Args:
            idea: Generated idea dictionary
            
        Returns:
            Formatted text string
        """
        lines = []
        
        # Add core content fields (skip empty fields)
        for field in ['hook', 'core_concept', 'emotional_core', 'audience_connection', 
                      'key_elements', 'tone_style']:
            if field in idea and idea[field]:
                lines.append(f"  {idea[field]}")
        
        return '\n'.join(lines)


# =============================================================================
# CONVENIENCE FUNCTIONS (Backward Compatibility)
# =============================================================================

_global_generator = None
_global_selector = None
_global_formatter = None


def _get_generator() -> IdeaGenerator:
    """Get global generator instance."""
    global _global_generator
    if _global_generator is None:
        _global_generator = IdeaGenerator()
    return _global_generator


def create_ideas_from_input(
    input_text: str,
    count: int = 10,
    flavors: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Create multiple ideas from input - convenience function.
    
    Args:
        input_text: Raw input text (no parsing)
        count: Number of ideas (default: 10)
        flavors: Optional list of specific flavors
        
    Returns:
        List of generated ideas
    """
    generator = _get_generator()
    return generator.generate_multiple(
        input_text=input_text,
        count=count,
        specific_flavors=flavors
    )


def generate_idea_from_flavor(
    flavor_name: str,
    input_text: str,
    variation_index: int = 0,
) -> Dict[str, Any]:
    """Generate single idea from flavor - convenience function.
    
    Args:
        flavor_name: Flavor to use
        input_text: Raw input text (no parsing)
        variation_index: Variation number
        
    Returns:
        Generated idea dictionary
    """
    generator = _get_generator()
    return generator.generate_from_flavor(
        flavor_name=flavor_name,
        input_text=input_text,
        variation_index=variation_index,
    )


def pick_weighted_flavor(seed: Optional[int] = None) -> str:
    """Pick single flavor - convenience function.
    
    Args:
        seed: Optional seed
        
    Returns:
        Selected flavor name
    """
    global _global_selector
    if _global_selector is None:
        _global_selector = FlavorSelector()
    return _global_selector.select_one(seed)


def pick_multiple_weighted_flavors(
    count: int = FlavorSelector.DEFAULT_COUNT,
    seed: Optional[int] = None,
    allow_duplicates: bool = False,
) -> List[str]:
    """Pick multiple flavors - convenience function.
    
    Args:
        count: Number to select (default: FlavorSelector.DEFAULT_COUNT = 10)
        seed: Optional seed
        allow_duplicates: Allow duplicate flavors
        
    Returns:
        List of flavor names
    """
    global _global_selector
    if _global_selector is None:
        _global_selector = FlavorSelector()
    return _global_selector.select_multiple(count, seed, allow_duplicates)


def pick_flavor_combination(
    primary_flavor: Optional[str] = None,
    seed: Optional[int] = None,
    multi_chance: float = FlavorSelector.MULTI_FLAVOR_CHANCE,
    no_flavor_chance: float = FlavorSelector.NO_FLAVOR_CHANCE,
) -> List[str]:
    """Pick a recursive flavor combination - convenience function.

    Returns one or more flavors (or an empty list when no_flavor_chance fires).
    See :meth:`FlavorSelector.select_flavor_combination` for full details.

    Args:
        primary_flavor: First flavor name; None for weighted-random selection.
        seed: Optional seed for reproducibility.
        multi_chance: Probability of adding each extra flavor (default: 0.4).
        no_flavor_chance: Probability of returning no flavor (default: 0.05).

    Returns:
        List of unique flavor names (possibly empty).
    """
    global _global_selector
    if _global_selector is None:
        _global_selector = FlavorSelector()
    return _global_selector.select_flavor_combination(
        primary_flavor=primary_flavor,
        seed=seed,
        multi_chance=multi_chance,
        no_flavor_chance=no_flavor_chance,
    )


def list_flavors() -> List[str]:
    """List all flavor names - convenience function."""
    loader = get_flavor_loader()
    loader.ensure_loaded()
    return loader.list_flavor_names()


def get_flavor(flavor_name: str) -> Dict[str, Any]:
    """Get flavor definition - convenience function."""
    loader = get_flavor_loader()
    loader.ensure_loaded()
    return loader.get_flavor(flavor_name)


def get_flavor_count() -> int:
    """Get flavor count - convenience function."""
    loader = get_flavor_loader()
    loader.ensure_loaded()
    return loader.get_flavor_count()


# =============================================================================
# TEMPLATE-BASED GENERATION (not replaced by AI — flavor is one variable in AI template)
# =============================================================================

# Import the template-based generation system from the templates module.
# These are distinct from the AI/flavor-based system above:
#   - Templates define structured idea dictionaries (deterministic, no AI required)
#   - Flavor is one variable injected into AI prompts (see ai_generator.py)
from idea_variants_OLD_BACKUP import (  # noqa: E402
    VARIANT_TEMPLATES,
    VARIANT_EMOTION_FIRST,
    VARIANT_MYSTERY,
    VARIANT_SKELETON,
    VARIANT_SHORTFORM,
    VARIANT_NICHE_BLEND,
    VARIANT_MINIMAL,
    VARIANT_4POINT,
    VARIANT_HOOK_FRAME,
    VARIANT_SHORTFORM2,
    VARIANT_GENRE,
    VARIANT_SCENE_SEED,
    create_idea_variant,
    create_all_variants,
    create_selected_variants,
    create_multiple_of_same_variant,
    create_idea_text,
    create_ideas_as_text,
    format_idea_as_text,
    get_template,
    get_template_fields,
    get_template_example,
    list_templates,
    MIN_IDEA_TEXT_LENGTH,
)

DEFAULT_IDEA_COUNT = 10

__all__ = [
    # Classes (SOLID design)
    'IdeaGenerator',
    'FlavorSelector',
    'IdeaFormatter',
    # AI/flavor convenience functions
    'create_ideas_from_input',
    'generate_idea_from_flavor',
    'pick_weighted_flavor',
    'pick_multiple_weighted_flavors',
    'list_flavors',
    'get_flavor',
    'get_flavor_count',
    # FlavorSelector helpers
    'pick_flavor_combination',
    # Constants
    'DEFAULT_IDEA_COUNT',
    # Template-based generation (not replaced by AI)
    'VARIANT_TEMPLATES',
    'VARIANT_EMOTION_FIRST',
    'VARIANT_MYSTERY',
    'VARIANT_SKELETON',
    'VARIANT_SHORTFORM',
    'VARIANT_NICHE_BLEND',
    'VARIANT_MINIMAL',
    'VARIANT_4POINT',
    'VARIANT_HOOK_FRAME',
    'VARIANT_SHORTFORM2',
    'VARIANT_GENRE',
    'VARIANT_SCENE_SEED',
    'create_idea_variant',
    'create_all_variants',
    'create_selected_variants',
    'create_multiple_of_same_variant',
    'create_idea_text',
    'create_ideas_as_text',
    'format_idea_as_text',
    'get_template',
    'get_template_fields',
    'get_template_example',
    'list_templates',
    'MIN_IDEA_TEXT_LENGTH',
]
