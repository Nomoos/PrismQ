"""Flavor definitions for idea refinement templates.

This module provides thematic flavor options that can be used to guide
the conceptual refinement of ideas. Flavors are automatically generated
from the variant templates and represent abstract directions for tone and emphasis.
"""

from typing import Dict, List, Optional
import sys
import random
from pathlib import Path

# Add path for variant templates import
_SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(_SCRIPT_DIR))

from idea_variants import list_templates, get_template, VARIANT_WEIGHTS


# =============================================================================
# FLAVOR GENERATION FROM VARIANT TEMPLATES
# =============================================================================

def _generate_flavors_from_variants() -> Dict[str, Dict]:
    """Generate flavor definitions from all variant templates.
    
    This function analyzes all variant templates and creates corresponding
    flavor definitions that capture their thematic essence.
    
    Returns:
        Dictionary mapping flavor names to their definitions
    """
    flavors = {}
    templates = list_templates()
    
    for template_key in templates:
        template = get_template(template_key)
        variant_name = template.get('name', template_key)
        desc = template.get('description', '')
        
        # Create flavor from variant
        flavor_name = variant_name
        
        # Extract thematic keywords from description
        desc_lower = desc.lower()
        keywords = []
        
        if any(word in desc_lower for word in ['emotion', 'feeling', 'heart']):
            keywords.append('emotional')
        if any(word in desc_lower for word in ['mystery', 'puzzle', 'secret']):
            keywords.append('mystery')
        if any(word in desc_lower for word in ['tension', 'conflict', 'struggle']):
            keywords.append('tension')
        if any(word in desc_lower for word in ['transform', 'growth', 'change']):
            keywords.append('transformation')
        if any(word in desc_lower for word in ['identity', 'power', 'voice']):
            keywords.append('identity')
        if any(word in desc_lower for word in ['romantic', 'love', 'attraction']):
            keywords.append('romantic')
        if any(word in desc_lower for word in ['moral', 'ethical', 'choice']):
            keywords.append('moral')
        if any(word in desc_lower for word in ['friend', 'relationship', 'connect']):
            keywords.append('relational')
        if any(word in desc_lower for word in ['dark', 'shadow', 'unease']):
            keywords.append('dark')
        if any(word in desc_lower for word in ['hope', 'optimis', 'resilience']):
            keywords.append('hopeful')
        
        # Build flavor definition
        flavors[flavor_name] = {
            'description': desc,
            'variant_key': template_key,
            'keywords': keywords,
            'template_name': variant_name,
        }
    
    return flavors


# Generate flavors from all variants
_ALL_FLAVORS = _generate_flavors_from_variants()

# Create organized flavor categories
FLAVOR_CATEGORIES = {
    'Emotional & Dramatic': [
        'Emotion-First Hook',
        'Emotional Drama + Growth',
        'Personal Drama (First-Person Voice)',
        'Confession Story Seed',
        'Real Family Drama Seed',
        'Safe Person Seed',
        'Holding Space Seed',
    ],
    'Mystery & Discovery': [
        'Mystery/Curiosity Gap',
        'Light Mystery + Adventure',
        'Mystery with Emotional Hook',
        'Overheard Truth Seed',
        'What They Don\'t Know Seed',
        'Confession + Mystery Fusion',
    ],
    'Psychological & Internal': [
        'Psychological Tension',
        'Introspective Transformation',
        'Mirror Moment Seed',
        'Before/After Transformation Seed',
        'The Version of Me Seed',
        'Quiet Rebellion Seed',
        'Body Acceptance Seed',
        'Fitting In Seed',
    ],
    'Identity & Growth': [
        'Identity + Empowerment',
        'Heritage Discovery Story Seed',
        'Emotional Inheritance Seed',
        'Permission To Seed',
        'Learned Young Seed',
        'Rewriting the Story Seed',
    ],
    'Relationship & Connection': [
        'Soft Supernatural + Friendship',
        'Chosen Family Seed',
        'Growing Apart Seed',
        'First Butterflies Seed',
        'Online Connection Seed',
        'Safe Person Seed',
    ],
    'Tension & Conflict': [
        'Competitive + Rivals to Allies',
        'School + Family Collision',
        'Social + Home Drama',
        'Unsent Message Seed',
        'Almost Said Seed',
    ],
    'Adventure & Challenge': [
        'Survival Challenge (Safe)',
        'Urban Social Quest',
        'Light Mystery + Adventure',
        'Sci-Fi + School Realism',
    ],
    'Transformation & Change': [
        'Before/After Transformation Seed',
        'Overheard + Transformation Fusion',
        'Parallel Lives Seed',
        'Last Time Seed',
    ],
    'Existential & Meaning': [
        'Existential Conflict',
        'Future Anxiety Seed',
        'Comparison Trap Seed',
        'Emotional Inheritance Seed',
    ],
    'Romance & Attraction': [
        'Romantic Tension',
        'First Butterflies Seed',
        'First Butterflies + Fitting In Blend',
        'Body Acceptance + First Butterflies Blend',
    ],
    'Moral & Ethical': [
        'Moral Dilemma',
        'Sci-Fi + School Realism',
        'Quiet Rebellion Seed',
        'AI as Companion (Safe)',
    ],
    'Creative & Aesthetic': [
        'Magical Realism + Aesthetic',
        'Niche-Blend',
        'Genre Focus',
        'Story Skeleton',
    ],
}


def list_flavors() -> List[str]:
    """Get list of all available flavor names.
    
    Returns:
        List of flavor names from all variant templates
    """
    return sorted(_ALL_FLAVORS.keys())


def list_flavor_categories() -> Dict[str, List[str]]:
    """Get organized categories of flavors.
    
    Returns:
        Dictionary mapping category names to lists of flavor names
    """
    return FLAVOR_CATEGORIES.copy()


def get_flavor_info(flavor_name: str) -> Dict:
    """Get information about a specific flavor.
    
    Args:
        flavor_name: Name of the flavor (variant template name)
        
    Returns:
        Dictionary with flavor information
        
    Raises:
        KeyError: If flavor name not found
    """
    return _ALL_FLAVORS[flavor_name].copy()


def get_flavor_description(flavor_name: str) -> str:
    """Get description of a flavor.
    
    Args:
        flavor_name: Name of the flavor
        
    Returns:
        Flavor description string
        
    Raises:
        KeyError: If flavor name not found
    """
    return _ALL_FLAVORS[flavor_name]['description']


def get_flavor_by_variant_key(variant_key: str) -> Optional[str]:
    """Get flavor name from variant template key.
    
    Args:
        variant_key: Variant template key (e.g., 'emotion_first')
        
    Returns:
        Flavor name or None if not found
    """
    for flavor_name, info in _ALL_FLAVORS.items():
        if info['variant_key'] == variant_key:
            return flavor_name
    return None


def search_flavors_by_keyword(keyword: str) -> List[str]:
    """Search for flavors by keyword.
    
    Args:
        keyword: Keyword to search for
        
    Returns:
        List of matching flavor names
    """
    keyword_lower = keyword.lower()
    matches = []
    
    for flavor_name, info in _ALL_FLAVORS.items():
        if (keyword_lower in flavor_name.lower() or
            keyword_lower in info['description'].lower() or
            keyword_lower in info['keywords']):
            matches.append(flavor_name)
    
    return sorted(matches)


def get_default_flavor() -> str:
    """Get the default flavor for idea refinement.
    
    Returns:
        Default flavor name
    """
    return "Emotional Drama + Growth"


def get_flavor_count() -> int:
    """Get total number of available flavors.
    
    Returns:
        Number of flavors
    """
    return len(_ALL_FLAVORS)


# =============================================================================
# WEIGHTED FLAVOR SELECTION
# =============================================================================

def _generate_flavor_weights() -> Dict[str, int]:
    """Generate flavor weights based on variant weights.
    
    Maps each flavor (variant name) to its weight from VARIANT_WEIGHTS.
    Flavors inherit the weights of their corresponding variants.
    
    Returns:
        Dictionary mapping flavor names to weights
    """
    flavor_weights = {}
    
    for flavor_name, info in _ALL_FLAVORS.items():
        variant_key = info['variant_key']
        # Get weight from VARIANT_WEIGHTS, default to 50 if not found
        weight = VARIANT_WEIGHTS.get(variant_key, 50)
        flavor_weights[flavor_name] = weight
    
    return flavor_weights


# Generate flavor weights from variant weights
_FLAVOR_WEIGHTS = _generate_flavor_weights()


def get_flavor_weights() -> Dict[str, int]:
    """Get the flavor weight mappings.
    
    Returns:
        Dictionary mapping flavor names to their weights
    """
    return _FLAVOR_WEIGHTS.copy()


def pick_weighted_flavor(seed: Optional[int] = None) -> str:
    """Pick a flavor using weighted random selection.
    
    Weights are inherited from variant template weights, which are tuned for
    the primary audience (US girls 13-15) with higher weights for
    emotion-focused, identity-focused, and mobile-friendly themes.
    
    Args:
        seed: Optional seed for reproducible selection. If None, uses random.
        
    Returns:
        Selected flavor name
        
    Examples:
        >>> flavor = pick_weighted_flavor()
        >>> # Likely to get high-weight flavors like "Emotional Drama + Growth"
        
        >>> flavor = pick_weighted_flavor(seed=12345)
        >>> # Reproducible selection with seed
    """
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()
    
    # Build weighted list
    flavors = list(_FLAVOR_WEIGHTS.keys())
    weights = [_FLAVOR_WEIGHTS[f] for f in flavors]
    
    # Use random.choices with weights
    selected = rng.choices(flavors, weights=weights, k=1)[0]
    return selected


def get_default_or_random_flavor(flavor: Optional[str] = None, use_weighted: bool = True, seed: Optional[int] = None) -> str:
    """Get a flavor - use provided, or select default/random.
    
    This is the main function for flavor selection in the system.
    
    Args:
        flavor: Optional flavor name. If provided, returns this.
        use_weighted: If True, uses weighted random selection. If False, uses simple default.
        seed: Optional seed for reproducible weighted selection.
        
    Returns:
        Flavor name to use
        
    Examples:
        >>> # Use provided flavor
        >>> get_default_or_random_flavor("Mystery + Unease")
        'Mystery + Unease'
        
        >>> # Use weighted random (default behavior)
        >>> get_default_or_random_flavor()
        # Returns weighted random flavor, e.g., "Emotional Drama + Growth"
        
        >>> # Use simple default
        >>> get_default_or_random_flavor(use_weighted=False)
        'Emotional Drama + Growth'
    """
    if flavor:
        # Use provided flavor if specified
        return flavor
    
    if use_weighted:
        # Use weighted random selection (default)
        return pick_weighted_flavor(seed=seed)
    else:
        # Use simple default
        return get_default_flavor()


