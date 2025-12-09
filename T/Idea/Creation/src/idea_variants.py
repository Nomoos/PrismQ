"""Flavor-based Idea Generation System - SOLID Design.

This module provides the main API for generating ideas using flavors.
It follows SOLID principles:
- Single Responsibility: Idea generation logic only
- Open/Closed: Extended via flavor configuration, not code changes
- Dependency Inversion: Depends on FlavorLoader abstraction

Flavors are loaded from external JSON configuration (data/flavors.json).
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
    
    def __init__(self, flavor_loader=None, use_ai=True, ai_config=None):
        """Initialize idea generator.
        
        Args:
            flavor_loader: Optional FlavorLoader instance.
                          If None, uses global loader.
            use_ai: Whether to use AI generation (default: True)
            ai_config: Optional AIConfig instance for AI generation
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
                logger.warning("AI generation requested but Ollama not available. Falling back to template generation.")
                self.ai_generator = None
    
    def generate_from_flavor(
        self,
        title: str,
        flavor_name: str,
        description: str = "",
        variation_index: int = 0,
    ) -> Dict[str, Any]:
        """Generate an idea using a specific flavor.
        
        Args:
            title: Input title/topic
            flavor_name: Name of the flavor to use
            description: Optional description
            variation_index: Variation number for uniqueness
            
        Returns:
            Dictionary with generated idea content
            
        Raises:
            KeyError: If flavor not found
        """
        flavor = self.loader.get_flavor(flavor_name)
        default_fields = self.loader.get_default_fields()
        seed = self._generate_seed(title, description, variation_index)
        
        # Build idea dictionary
        idea = {
            'flavor_name': flavor_name,
            'variant_name': flavor_name,  # For display compatibility (used by interactive UI)
            'flavor_description': flavor['description'],
            'source_title': title,
            'source_description': description,
            'variation_index': variation_index,
            'keywords': flavor.get('keywords', []),
        }
        
        # Generate content for each field
        # AI will be used automatically if available via the helper methods
        focus_field = flavor.get('focus', 'core_concept')
        
        for field_name, field_desc in default_fields.items():
            if field_name == focus_field:
                # Make the focus field more detailed
                idea[field_name] = self._generate_focused_content(
                    title, description, field_desc, flavor_name, seed
                )
            else:
                # Generate standard content
                idea[field_name] = self._generate_field_content(
                    title, description, field_desc, flavor_name, seed
                )
        
        # Add metadata
        idea['generated_at'] = datetime.now().isoformat()
        idea['idea_hash'] = self._generate_idea_hash(title, flavor_name, variation_index)
        
        return idea
    
    def generate_multiple(
        self,
        title: str,
        count: int = 10,
        description: str = "",
        specific_flavors: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Generate multiple ideas from input.
        
        Args:
            title: Input title/topic
            count: Number of ideas to generate
            description: Optional description
            specific_flavors: Optional list of specific flavors.
                            If None, uses weighted random selection.
                            
        Returns:
            List of generated ideas
        """
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
                    title=title,
                    flavor_name=flavor_name,
                    description=description,
                    variation_index=i,
                )
                ideas.append(idea)
            except Exception as e:
                print(f"Warning: Failed to generate with flavor {flavor_name}: {e}")
                continue
        
        return ideas
    
    # Helper methods
    
    @staticmethod
    def _generate_seed(title: str, description: str, variation_index: int) -> int:
        """Generate consistent seed from inputs."""
        content = f"{title}{description}{variation_index}"
        hash_obj = hashlib.md5(content.encode())
        return int(hash_obj.hexdigest()[:8], 16)
    
    @staticmethod
    def _generate_idea_hash(title: str, flavor_name: str, variation_index: int) -> str:
        """Generate unique hash for the idea."""
        content = f"{title}{flavor_name}{variation_index}{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @staticmethod
    def _humanize_topic(title: str) -> str:
        """Convert title to readable topic format."""
        topic = re.sub(r'[^\w\s-]', '', title)
        topic = topic.strip().lower()
        if topic:
            topic = topic[0].upper() + topic[1:]
        return topic if topic else "this topic"
    
    def _generate_focused_content(
        self,
        title: str,
        description: str,
        field_desc: str,
        flavor_name: str,
        seed: int,
    ) -> str:
        """Generate detailed content for the focus field.
        
        Uses AI generation if available, falls back to templates otherwise.
        """
        # Try AI generation first
        if self.ai_generator:
            try:
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
                
                # If AI generated meaningful content, use it
                if generated and len(generated) > 20:
                    logger.debug(f"AI generated focused content for '{field_desc}': {generated[:80]}...")
                    return generated.strip()
                else:
                    logger.warning(f"AI generated content too short for '{field_desc}', falling back to template")
            except Exception as e:
                logger.warning(f"AI generation failed for focused content '{field_desc}': {e}, falling back to template")
        
        # Fallback to template generation
        topic = self._humanize_topic(title)
        flavor_lower = flavor_name.lower()
        
        templates = [
            f"{topic} - {field_desc}",
            f"Exploring {topic} through {flavor_lower}",
            f"{field_desc} centered on {topic}",
            f"A story about {topic} that emphasizes {field_desc.lower()}",
        ]
        
        rng = random.Random(seed)
        return rng.choice(templates)
    
    def _generate_field_content(
        self,
        title: str,
        description: str,
        field_desc: str,
        flavor_name: str,
        seed: int,
    ) -> str:
        """Generate standard content for a field.
        
        Uses AI generation if available, falls back to templates otherwise.
        """
        # Try AI generation first
        if self.ai_generator:
            try:
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
                
                # If AI generated meaningful content, use it
                if generated and len(generated) > 20:
                    logger.debug(f"AI generated field content for '{field_desc}': {generated[:80]}...")
                    return generated.strip()
                else:
                    logger.warning(f"AI generated content too short for '{field_desc}', falling back to template")
            except Exception as e:
                logger.warning(f"AI generation failed for field content '{field_desc}': {e}, falling back to template")
        
        # Fallback to template generation
        topic = self._humanize_topic(title)
        
        templates = [
            f"{field_desc} for {topic}",
            f"{topic}: {field_desc.lower()}",
            f"How {topic} relates to {field_desc.lower()}",
        ]
        
        rng = random.Random(seed)
        return rng.choice(templates)


# =============================================================================
# FLAVOR SELECTION SERVICE
# =============================================================================

class FlavorSelector:
    """Selects flavors using weighted random selection.
    
    Single Responsibility: Flavor selection logic only.
    """
    
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
    
    def select_multiple(
        self,
        count: int,
        seed: Optional[int] = None,
        allow_duplicates: bool = False,
    ) -> List[str]:
        """Select multiple flavors using weighted random selection.
        
        Args:
            count: Number of flavors to select
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
        
        # Add core content fields
        for field in ['hook', 'core_concept', 'emotional_core', 'audience_connection', 
                      'key_elements', 'tone_style']:
            if field in idea:
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
    title: str,
    count: int = 10,
    description: str = "",
    flavors: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Create multiple ideas from input - convenience function.
    
    Args:
        title: Input title/topic
        count: Number of ideas (default: 10)
        description: Optional description
        flavors: Optional list of specific flavors
        
    Returns:
        List of generated ideas
    """
    generator = _get_generator()
    return generator.generate_multiple(title, count, description, flavors)


def generate_idea_from_flavor(
    title: str,
    flavor_name: str,
    description: str = "",
    variation_index: int = 0,
) -> Dict[str, Any]:
    """Generate single idea from flavor - convenience function.
    
    Args:
        title: Input title/topic
        flavor_name: Flavor to use
        description: Optional description
        variation_index: Variation number
        
    Returns:
        Generated idea dictionary
    """
    generator = _get_generator()
    return generator.generate_from_flavor(title, flavor_name, description, variation_index)


def format_idea_as_text(idea: Dict[str, Any]) -> str:
    """Format idea as text - convenience function.
    
    Args:
        idea: Generated idea
        
    Returns:
        Formatted text
    """
    global _global_formatter
    if _global_formatter is None:
        _global_formatter = IdeaFormatter()
    return _global_formatter.format_as_text(idea)


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
    count: int,
    seed: Optional[int] = None,
    allow_duplicates: bool = False,
) -> List[str]:
    """Pick multiple flavors - convenience function.
    
    Args:
        count: Number to select
        seed: Optional seed
        allow_duplicates: Allow duplicate flavors
        
    Returns:
        List of flavor names
    """
    global _global_selector
    if _global_selector is None:
        _global_selector = FlavorSelector()
    return _global_selector.select_multiple(count, seed, allow_duplicates)


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


# Backward compatibility aliases
list_templates = list_flavors
get_template = get_flavor
DEFAULT_IDEA_COUNT = 10

__all__ = [
    # Classes (SOLID design)
    'IdeaGenerator',
    'FlavorSelector',
    'IdeaFormatter',
    # Main convenience functions
    'create_ideas_from_input',
    'generate_idea_from_flavor',
    'format_idea_as_text',
    'pick_weighted_flavor',
    'pick_multiple_weighted_flavors',
    'list_flavors',
    'get_flavor',
    'get_flavor_count',
    # Constants
    'DEFAULT_IDEA_COUNT',
    # Backward compatibility
    'list_templates',
    'get_template',
]
