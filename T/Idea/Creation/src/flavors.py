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


# =============================================================================
# CUSTOM AUDIENCE-SPECIFIC FLAVORS
# =============================================================================

# Custom flavors for specific target audiences
# These are manually curated combinations optimized for different demographics

CUSTOM_AUDIENCE_FLAVORS = {
    # Audience: 10-22 years (broad young audience)
    'Youth Adventure Quest': {
        'description': 'Adventure-focused stories with coming-of-age elements for ages 10-22',
        'variant_key': 'custom_youth_adventure',
        'keywords': ['adventure', 'growth', 'discovery', 'friendship', 'challenge'],
        'template_name': 'Youth Adventure Quest',
        'audience': '10-22 years',
        'weight': 85,
    },
    'Teen Identity Journey': {
        'description': 'Identity exploration and self-discovery for ages 10-22',
        'variant_key': 'custom_teen_identity',
        'keywords': ['identity', 'transformation', 'empowerment', 'self-discovery'],
        'template_name': 'Teen Identity Journey',
        'audience': '10-22 years',
        'weight': 90,
    },
    
    # Audience: US women (broad women audience)
    'Modern Woman\'s Voice': {
        'description': 'Contemporary stories centering women\'s experiences and perspectives',
        'variant_key': 'custom_us_woman_voice',
        'keywords': ['identity', 'empowerment', 'emotional', 'relational', 'authentic'],
        'template_name': 'Modern Woman\'s Voice',
        'audience': 'US women',
        'weight': 85,
    },
    'Women\'s Real Talk': {
        'description': 'Honest, relatable stories about real-life challenges for women',
        'variant_key': 'custom_women_real_talk',
        'keywords': ['emotional', 'relational', 'honest', 'vulnerable', 'authentic'],
        'template_name': 'Women\'s Real Talk',
        'audience': 'US women',
        'weight': 80,
    },
    
    # Audience: Maine residents aged 10-25
    'Maine Youth Stories': {
        'description': 'Regional stories with local flavor for Maine youth aged 10-25',
        'variant_key': 'custom_maine_youth',
        'keywords': ['regional', 'community', 'nature', 'identity', 'belonging'],
        'template_name': 'Maine Youth Stories',
        'audience': 'Maine residents 10-25',
        'weight': 75,
    },
    
    # Audience: US women aged 13-16
    'Teen Girl Confessional': {
        'description': 'First-person confessional stories for US girls aged 13-16',
        'variant_key': 'custom_teen_girl_confessional',
        'keywords': ['emotional', 'confession', 'identity', 'relational', 'authentic'],
        'template_name': 'Teen Girl Confessional',
        'audience': 'US women 13-16',
        'weight': 95,
    },
    'Young Woman\'s Moment': {
        'description': 'Snapshot moments of teenage girlhood for ages 13-16',
        'variant_key': 'custom_young_woman_moment',
        'keywords': ['emotional', 'moment', 'growth', 'relational', 'authentic'],
        'template_name': 'Young Woman\'s Moment',
        'audience': 'US women 13-16',
        'weight': 95,
    },
    
    # Audience: teen girls (general)
    'Teen Girl Drama': {
        'description': 'Relatable dramatic stories for teen girls',
        'variant_key': 'custom_teen_girl_drama',
        'keywords': ['emotional', 'drama', 'relational', 'friendship', 'identity'],
        'template_name': 'Teen Girl Drama',
        'audience': 'teen girls',
        'weight': 92,
    },
    'Girl Squad Chronicles': {
        'description': 'Friendship and group dynamic stories for teen girls',
        'variant_key': 'custom_girl_squad',
        'keywords': ['friendship', 'relational', 'group', 'loyalty', 'drama'],
        'template_name': 'Girl Squad Chronicles',
        'audience': 'teen girls',
        'weight': 88,
    },
}

# Mixed/blended custom flavors (combinations of existing + custom)
MIXED_CUSTOM_FLAVORS = {
    'Confession + Teen Identity': {
        'description': 'Confessional moments mixed with identity exploration',
        'variant_key': 'mixed_confession_identity',
        'keywords': ['confession', 'identity', 'emotional', 'transformation'],
        'template_name': 'Confession + Teen Identity',
        'base_flavors': ['Confession Story Seed', 'Teen Identity Journey'],
        'audience': '13-17 young women US/Canada',
        'weight': 100,
    },
    'Body Acceptance + Real Talk': {
        'description': 'Body image stories with honest emotional depth',
        'variant_key': 'mixed_body_real_talk',
        'keywords': ['body', 'emotional', 'honest', 'transformation', 'acceptance'],
        'template_name': 'Body Acceptance + Real Talk',
        'base_flavors': ['Body Acceptance Seed', 'Women\'s Real Talk'],
        'audience': '13-17 young women US/Canada',
        'weight': 98,
    },
    'Friend Drama + Girl Squad': {
        'description': 'Friendship dynamics with group complexity',
        'variant_key': 'mixed_friend_squad',
        'keywords': ['friendship', 'relational', 'drama', 'group', 'loyalty'],
        'template_name': 'Friend Drama + Girl Squad',
        'base_flavors': ['Growing Apart Seed', 'Girl Squad Chronicles'],
        'audience': '13-17 young women US/Canada',
        'weight': 96,
    },
    'Online Connection + Teen Voice': {
        'description': 'Digital life meets authentic teen expression',
        'variant_key': 'mixed_online_teen_voice',
        'keywords': ['online', 'digital', 'authentic', 'connection', 'identity'],
        'template_name': 'Online Connection + Teen Voice',
        'base_flavors': ['Online Connection Seed', 'Modern Woman\'s Voice'],
        'audience': '13-17 young women US/Canada',
        'weight': 94,
    },
    'Mirror Moment + Identity Power': {
        'description': 'Self-recognition leading to empowerment',
        'variant_key': 'mixed_mirror_identity',
        'keywords': ['mirror', 'identity', 'empowerment', 'transformation', 'realization'],
        'template_name': 'Mirror Moment + Identity Power',
        'base_flavors': ['Mirror Moment Seed', 'Identity + Empowerment'],
        'audience': '13-17 young women US/Canada',
        'weight': 97,
    },
}

# Primary audience optimized flavors (best for 13-17 young women in US/Canada)
PRIMARY_AUDIENCE_FLAVORS = {
    'Teen Girl Heart': {
        'description': 'Emotional core stories optimized for 13-17 young women',
        'variant_key': 'primary_teen_heart',
        'keywords': ['emotional', 'authentic', 'relational', 'growth', 'vulnerability'],
        'template_name': 'Teen Girl Heart',
        'audience': '13-17 young women US/Canada',
        'weight': 100,
        'score': 10.0,  # Perfect score for primary audience
    },
    'Young Woman\'s Truth': {
        'description': 'Honest first-person narratives for 13-17 young women',
        'variant_key': 'primary_young_truth',
        'keywords': ['honest', 'confession', 'emotional', 'authentic', 'vulnerable'],
        'template_name': 'Young Woman\'s Truth',
        'audience': '13-17 young women US/Canada',
        'weight': 100,
        'score': 9.8,
    },
    'Teen Moment Magic': {
        'description': 'Small moments with big meaning for 13-17 young women',
        'variant_key': 'primary_teen_moment',
        'keywords': ['moment', 'meaning', 'emotional', 'realization', 'growth'],
        'template_name': 'Teen Moment Magic',
        'audience': '13-17 young women US/Canada',
        'weight': 98,
        'score': 9.5,
    },
}

# Merge custom flavors into main flavor dict
_ALL_FLAVORS.update(CUSTOM_AUDIENCE_FLAVORS)
_ALL_FLAVORS.update(MIXED_CUSTOM_FLAVORS)
_ALL_FLAVORS.update(PRIMARY_AUDIENCE_FLAVORS)

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
    'Custom Audience-Specific': [
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
    'Primary Audience Optimized (13-17 US/Canada)': [
        'Teen Girl Heart',
        'Young Woman\'s Truth',
        'Teen Moment Magic',
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
    """Generate flavor weights based on variant weights.
    
    Maps each flavor (variant name) to its weight from VARIANT_WEIGHTS.
    Flavors inherit the weights of their corresponding variants.
    Custom audience-specific flavors have their own weights defined inline.
    
    Returns:
        Dictionary mapping flavor names to weights
    """
    flavor_weights = {}
    
    for flavor_name, info in _ALL_FLAVORS.items():
        variant_key = info['variant_key']
        # Check if weight is defined in the flavor info (custom flavors)
        if 'weight' in info:
            weight = info['weight']
        else:
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


