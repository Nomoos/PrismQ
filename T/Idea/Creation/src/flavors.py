"""Flavor definitions for idea refinement templates.

This module provides thematic flavor options that can be used to guide
the conceptual refinement of ideas. Flavors define thematic directions
for story development and are used throughout the system.
"""

from typing import Dict, List, Optional
import sys
import random
from pathlib import Path

# Add path for imports
_SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(_SCRIPT_DIR))

from idea_variants import (
    FLAVOR_DEFINITIONS,
    FLAVOR_WEIGHTS,
    DEFAULT_FLAVOR_WEIGHT,
    list_flavors as _list_flavors,
    get_flavor as _get_flavor,
)


# =============================================================================
# FLAVOR ACCESS FUNCTIONS
# =============================================================================

def _generate_flavors_from_definitions() -> Dict[str, Dict]:
    """Get flavors from the new flavor-based system.
    
    Returns:
        Dictionary mapping flavor names to their definitions
    """
    flavors = {}
    
    for flavor_name, flavor_def in FLAVOR_DEFINITIONS.items():
        flavors[flavor_name] = {
            'description': flavor_def.get('description', ''),
            'variant_key': flavor_name.lower().replace(' ', '_').replace('/', '_').replace('+', 'plus'),
            'keywords': flavor_def.get('keywords', []),
            'template_name': flavor_name,
            'audience': flavor_def.get('audience', ''),
            'weight': FLAVOR_WEIGHTS.get(flavor_name, DEFAULT_FLAVOR_WEIGHT),
        }
        
        if 'score' in flavor_def:
            flavors[flavor_name]['score'] = flavor_def['score']
    
    return flavors


# Generate flavors from the new system
_ALL_FLAVORS = _generate_flavors_from_definitions()

# Create organized flavor categories
FLAVOR_CATEGORIES = {
    'Emotional & Core': [
        'Emotion-First Hook',
        'Emotional Drama + Growth',
        'Confession Story Seed',
        'Teen Girl Heart',
        'Young Woman\'s Truth',
        'Teen Moment Magic',
    ],
    'Mystery & Discovery': [
        'Mystery/Curiosity Gap',
        'Light Mystery + Adventure',
        'Overheard Truth Seed',
    ],
    'Identity & Growth': [
        'Identity + Empowerment',
        'Teen Identity Journey',
        'Mirror Moment Seed',
        'Before/After Transformation Seed',
    ],
    'Relationship & Connection': [
        'Soft Supernatural + Friendship',
        'Chosen Family Seed',
        'Growing Apart Seed',
        'First Butterflies Seed',
        'Online Connection Seed',
    ],
    'Teen Life & Challenges': [
        'Body Acceptance Seed',
        'Fitting In Seed',
        'Future Anxiety Seed',
        'Comparison Trap Seed',
    ],
    'Creative & Aesthetic': [
        'Story Skeleton',
        'Short-Form Viral',
        'Niche-Blend',
        'Sci-Fi + School Realism',
    ],
    'Audience-Specific': [
        'Youth Adventure Quest',
        'Teen Identity Journey',
        'Modern Woman\'s Voice',
        'Women\'s Real Talk',
        'Maine Youth Stories',
        'Teen Girl Confessional',
        'Young Woman\'s Moment',
        'Teen Girl Drama',
        'Girl Squad Chronicles',
    ],
    'Mixed & Blended': [
        'Confession + Teen Identity',
        'Body Acceptance + Real Talk',
        'Friend Drama + Girl Squad',
        'Online Connection + Teen Voice',
        'Mirror Moment + Identity Power',
    ],
}


def list_flavors() -> List[str]:
    """Get list of all available flavor names.
    
    Returns:
        List of flavor names from all variant templates
    """
    return sorted(_ALL_FLAVORS.keys())


def list_flavors_by_audience(audience: Optional[str] = None) -> List[str]:
    """Get list of flavors filtered by target audience.
    
    Args:
        audience: Optional audience filter (e.g., "teen girls", "US women 13-16")
                 If None, returns all flavors
    
    Returns:
        List of flavor names matching the audience
    """
    if not audience:
        return list_flavors()
    
    audience_lower = audience.lower()
    matching = []
    
    for flavor_name, info in _ALL_FLAVORS.items():
        if 'audience' in info and audience_lower in info['audience'].lower():
            matching.append(flavor_name)
    
    return sorted(matching)


def get_primary_audience_flavors() -> List[str]:
    """Get flavors optimized for the primary audience (13-17 young women in US/Canada).
    
    Returns:
        List of flavor names best suited for primary audience
    """
    primary_audience_key = '13-17'
    matching = []
    
    for flavor_name, info in _ALL_FLAVORS.items():
        audience = info.get('audience', '')
        # Match primary audience or high-scoring general flavors
        if primary_audience_key in audience or info.get('score', 0) >= 9.0:
            matching.append(flavor_name)
    
    # Also include high-weight emotional/relational flavors
    high_weight_emotional = [
        'Emotional Drama + Growth',
        'Confession Story Seed',
        'Body Acceptance Seed',
        'First Butterflies Seed',
        'Online Connection Seed',
        'Mirror Moment Seed',
        'Chosen Family Seed',
        'Growing Apart Seed',
    ]
    
    for flavor in high_weight_emotional:
        if flavor in _ALL_FLAVORS and flavor not in matching:
            matching.append(flavor)
    
    return sorted(set(matching))


def score_flavor_for_audience(flavor_name: str, audience: str = '13-17 young women US/Canada') -> float:
    """Score a flavor's fit for a specific audience.
    
    Scoring is based on:
    - Explicit audience match (high score)
    - Keyword alignment with audience interests
    - Weight tuning for audience
    - Pre-defined scores for primary audience flavors
    
    Args:
        flavor_name: Name of the flavor to score
        audience: Target audience (default: primary audience)
        
    Returns:
        Score from 0.0 to 10.0 indicating audience fit
        
    Raises:
        KeyError: If flavor name not found
    """
    info = _ALL_FLAVORS[flavor_name]
    
    # Check for pre-defined score
    if 'score' in info:
        return info['score']
    
    score = 5.0  # Base score
    
    # Explicit audience match
    flavor_audience = info.get('audience', '').lower()
    if audience.lower() in flavor_audience or flavor_audience in audience.lower():
        score += 3.0
    
    # Keyword scoring for primary audience (13-17 young women)
    if '13-17' in audience or 'teen' in audience.lower() or 'young women' in audience.lower():
        primary_keywords = ['emotional', 'relational', 'identity', 'authentic', 'confession', 
                           'body', 'friendship', 'online', 'transformation']
        keyword_matches = sum(1 for kw in info.get('keywords', []) if kw in primary_keywords)
        score += min(2.0, keyword_matches * 0.4)
    
    # Weight-based adjustment (higher weight = better audience fit)
    weight = info.get('weight', 50)
    if weight >= 90:
        score += 1.0
    elif weight >= 80:
        score += 0.5
    
    # Cap at 10.0
    return min(10.0, score)


def get_scored_flavors(audience: str = '13-17 young women US/Canada', 
                       min_score: float = 0.0) -> List[tuple]:
    """Get all flavors scored for a specific audience.
    
    Args:
        audience: Target audience to score for
        min_score: Minimum score threshold (default: 0.0 for all)
        
    Returns:
        List of tuples (flavor_name, score) sorted by score descending
    """
    scored = []
    for flavor_name in _ALL_FLAVORS.keys():
        score = score_flavor_for_audience(flavor_name, audience)
        if score >= min_score:
            scored.append((flavor_name, score))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


def get_top_flavors_for_audience(audience: str = '13-17 young women US/Canada', 
                                  count: int = 10) -> List[str]:
    """Get top N flavors for a specific audience.
    
    Args:
        audience: Target audience
        count: Number of top flavors to return (default: 10)
        
    Returns:
        List of top flavor names for the audience
    """
    scored = get_scored_flavors(audience)
    return [name for name, score in scored[:count]]


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
    """Get flavor weights from the flavor definitions.
    
    Returns:
        Dictionary mapping flavor names to weights
    """
    flavor_weights = {}
    
    for flavor_name, info in _ALL_FLAVORS.items():
        # Weights are already set in the flavor info
        weight = info.get('weight', DEFAULT_FLAVOR_WEIGHT)
        flavor_weights[flavor_name] = weight
    
    return flavor_weights


# Generate flavor weights
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


