"""Flavor-based Idea Generation System.

This module replaces the old variant template system with a simpler,
flavor-driven approach. Flavors define thematic directions for ideas
without complex structural templates.

Each flavor has:
- Name: User-friendly flavor name
- Description: What this flavor offers
- Keywords: Thematic keywords
- Core fields: Essential story elements
"""

import hashlib
import random
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

# =============================================================================
# CORE FLAVOR STRUCTURE
# =============================================================================

# Simple, flexible field structure for all flavors
DEFAULT_IDEA_FIELDS = {
    "hook": "The attention-grabbing opening or central question",
    "core_concept": "The main idea or premise in 1-2 sentences",
    "emotional_core": "The emotional heart of the story",
    "audience_connection": "Why this resonates with the target audience",
    "key_elements": "3-5 key story elements or beats",
    "tone_style": "Overall tone and style approach",
}

# =============================================================================
# FLAVOR DEFINITIONS
# =============================================================================

# All flavors now defined with simple structure
FLAVOR_DEFINITIONS = {
    # Base Flavors (from original 11 base templates)
    'Emotion-First Hook': {
        'description': 'Emotion as the primary driver',
        'keywords': ['emotional', 'hook', 'feeling'],
        'focus': 'emotional_core',
    },
    'Mystery/Curiosity Gap': {
        'description': 'Central mystery or unanswered question',
        'keywords': ['mystery', 'curiosity', 'question'],
        'focus': 'hook',
    },
    'Story Skeleton': {
        'description': 'Complete story structure framework',
        'keywords': ['structure', 'framework', 'narrative'],
        'focus': 'key_elements',
    },
    'Short-Form Viral': {
        'description': 'Optimized for short-form viral platforms',
        'keywords': ['viral', 'short', 'engaging'],
        'focus': 'hook',
    },
    'Niche-Blend': {
        'description': 'Combines multiple niches',
        'keywords': ['blend', 'niche', 'unique'],
        'focus': 'core_concept',
    },
    
    # Creative Genre Flavors
    'Soft Supernatural + Friendship': {
        'description': 'Gentle supernatural with friendship and emotional growth',
        'keywords': ['supernatural', 'friendship', 'wonder'],
        'focus': 'emotional_core',
    },
    'Light Mystery + Adventure': {
        'description': 'Puzzles and adventure without dark themes',
        'keywords': ['mystery', 'adventure', 'light'],
        'focus': 'key_elements',
    },
    'Sci-Fi + School Realism': {
        'description': 'Near-future tech meets real school life',
        'keywords': ['scifi', 'school', 'identity'],
        'focus': 'core_concept',
    },
    'Emotional Drama + Growth': {
        'description': 'Character-driven feelings and transformation',
        'keywords': ['emotional', 'drama', 'growth'],
        'focus': 'emotional_core',
    },
    'Identity + Empowerment': {
        'description': 'Finding voice and embracing difference',
        'keywords': ['identity', 'empowerment', 'voice'],
        'focus': 'emotional_core',
    },
    
    # Story Seed Flavors (for primary audience)
    'Confession Story Seed': {
        'description': 'First-person confession revealing hidden truth',
        'keywords': ['confession', 'vulnerable', 'honest'],
        'focus': 'emotional_core',
    },
    'Before/After Transformation Seed': {
        'description': 'Pivotal moment that changed everything',
        'keywords': ['transformation', 'change', 'moment'],
        'focus': 'key_elements',
    },
    'Overheard Truth Seed': {
        'description': 'Accidentally hearing something not meant for them',
        'keywords': ['overheard', 'secret', 'discovery'],
        'focus': 'hook',
    },
    'Mirror Moment Seed': {
        'description': 'Self-recognition or confrontation with self-image',
        'keywords': ['mirror', 'self', 'realization'],
        'focus': 'emotional_core',
    },
    'Chosen Family Seed': {
        'description': 'Finding belonging outside blood ties',
        'keywords': ['family', 'chosen', 'belonging'],
        'focus': 'emotional_core',
    },
    'Growing Apart Seed': {
        'description': 'Recognizing a connection is changing or fading',
        'keywords': ['relationship', 'change', 'grief'],
        'focus': 'emotional_core',
    },
    
    # Theme Flavors (teen-focused)
    'First Butterflies Seed': {
        'description': 'First crush and attraction experiences',
        'keywords': ['crush', 'butterflies', 'attraction'],
        'focus': 'emotional_core',
    },
    'Body Acceptance Seed': {
        'description': 'Journey toward body acceptance and self-love',
        'keywords': ['body', 'acceptance', 'self-love'],
        'focus': 'emotional_core',
    },
    'Fitting In Seed': {
        'description': 'Navigating social belonging and acceptance',
        'keywords': ['fitting', 'belonging', 'social'],
        'focus': 'audience_connection',
    },
    'Online Connection Seed': {
        'description': 'Digital life and online relationships',
        'keywords': ['online', 'digital', 'connection'],
        'focus': 'audience_connection',
    },
    'Future Anxiety Seed': {
        'description': 'Fears and uncertainty about the future',
        'keywords': ['future', 'anxiety', 'uncertainty'],
        'focus': 'emotional_core',
    },
    'Comparison Trap Seed': {
        'description': 'Struggles with social comparison',
        'keywords': ['comparison', 'social', 'self-worth'],
        'focus': 'emotional_core',
    },
    
    # Custom Audience-Specific Flavors
    'Youth Adventure Quest': {
        'description': 'Adventure-focused coming-of-age for ages 10-22',
        'keywords': ['adventure', 'growth', 'discovery'],
        'focus': 'key_elements',
        'audience': '10-22 years',
    },
    'Teen Identity Journey': {
        'description': 'Identity exploration for ages 10-22',
        'keywords': ['identity', 'self-discovery', 'transformation'],
        'focus': 'emotional_core',
        'audience': '10-22 years',
    },
    'Modern Woman\'s Voice': {
        'description': 'Contemporary women\'s experiences',
        'keywords': ['identity', 'empowerment', 'authentic'],
        'focus': 'emotional_core',
        'audience': 'US women',
    },
    'Women\'s Real Talk': {
        'description': 'Honest stories about real-life challenges',
        'keywords': ['honest', 'relational', 'vulnerable'],
        'focus': 'emotional_core',
        'audience': 'US women',
    },
    'Maine Youth Stories': {
        'description': 'Regional stories for Maine youth',
        'keywords': ['regional', 'community', 'nature'],
        'focus': 'audience_connection',
        'audience': 'Maine residents 10-25',
    },
    'Teen Girl Confessional': {
        'description': 'First-person confessional for girls 13-16',
        'keywords': ['confession', 'emotional', 'authentic'],
        'focus': 'emotional_core',
        'audience': 'US women 13-16',
    },
    'Young Woman\'s Moment': {
        'description': 'Snapshot moments of teenage girlhood',
        'keywords': ['moment', 'growth', 'relational'],
        'focus': 'emotional_core',
        'audience': 'US women 13-16',
    },
    'Teen Girl Drama': {
        'description': 'Relatable dramatic stories for teen girls',
        'keywords': ['drama', 'relational', 'friendship'],
        'focus': 'emotional_core',
        'audience': 'teen girls',
    },
    'Girl Squad Chronicles': {
        'description': 'Friendship and group dynamics',
        'keywords': ['friendship', 'group', 'loyalty'],
        'focus': 'audience_connection',
        'audience': 'teen girls',
    },
    
    # Mixed/Blended Flavors
    'Confession + Teen Identity': {
        'description': 'Confessional moments with identity exploration',
        'keywords': ['confession', 'identity', 'transformation'],
        'focus': 'emotional_core',
        'audience': '13-17 young women US/Canada',
    },
    'Body Acceptance + Real Talk': {
        'description': 'Body image with honest emotional depth',
        'keywords': ['body', 'honest', 'transformation'],
        'focus': 'emotional_core',
        'audience': '13-17 young women US/Canada',
    },
    'Friend Drama + Girl Squad': {
        'description': 'Friendship dynamics with group complexity',
        'keywords': ['friendship', 'drama', 'loyalty'],
        'focus': 'emotional_core',
        'audience': '13-17 young women US/Canada',
    },
    'Online Connection + Teen Voice': {
        'description': 'Digital life meets authentic teen expression',
        'keywords': ['online', 'authentic', 'identity'],
        'focus': 'audience_connection',
        'audience': '13-17 young women US/Canada',
    },
    'Mirror Moment + Identity Power': {
        'description': 'Self-recognition leading to empowerment',
        'keywords': ['mirror', 'identity', 'empowerment'],
        'focus': 'emotional_core',
        'audience': '13-17 young women US/Canada',
    },
    
    # Primary Audience Optimized
    'Teen Girl Heart': {
        'description': 'Emotional core stories for 13-17 young women',
        'keywords': ['emotional', 'authentic', 'relational'],
        'focus': 'emotional_core',
        'audience': '13-17 young women US/Canada',
        'score': 10.0,
    },
    'Young Woman\'s Truth': {
        'description': 'Honest first-person narratives',
        'keywords': ['honest', 'confession', 'vulnerable'],
        'focus': 'emotional_core',
        'audience': '13-17 young women US/Canada',
        'score': 9.8,
    },
    'Teen Moment Magic': {
        'description': 'Small moments with big meaning',
        'keywords': ['moment', 'meaning', 'growth'],
        'focus': 'emotional_core',
        'audience': '13-17 young women US/Canada',
        'score': 9.5,
    },
}

# Flavor weights for weighted random selection
FLAVOR_WEIGHTS = {
    # High weight for primary audience flavors
    'Teen Girl Heart': 100,
    'Young Woman\'s Truth': 100,
    'Teen Moment Magic': 98,
    'Confession + Teen Identity': 100,
    'Body Acceptance + Real Talk': 98,
    'Friend Drama + Girl Squad': 96,
    'Online Connection + Teen Voice': 94,
    'Mirror Moment + Identity Power': 97,
    
    # High weight for teen-focused flavors
    'Teen Girl Confessional': 95,
    'Young Woman\'s Moment': 95,
    'Teen Girl Drama': 92,
    'Girl Squad Chronicles': 88,
    'Teen Identity Journey': 90,
    
    # High weight for emotional/relational flavors
    'Emotional Drama + Growth': 90,
    'Confession Story Seed': 88,
    'Body Acceptance Seed': 85,
    'First Butterflies Seed': 85,
    'Mirror Moment Seed': 85,
    'Chosen Family Seed': 83,
    'Growing Apart Seed': 83,
    'Identity + Empowerment': 85,
    
    # Medium-high weight for audience-relevant flavors
    'Online Connection Seed': 80,
    'Fitting In Seed': 80,
    'Future Anxiety Seed': 78,
    'Comparison Trap Seed': 78,
    'Overheard Truth Seed': 75,
    'Before/After Transformation Seed': 75,
    
    # Medium weight for creative flavors
    'Soft Supernatural + Friendship': 70,
    'Light Mystery + Adventure': 68,
    'Emotion-First Hook': 70,
    'Mystery/Curiosity Gap': 68,
    
    # Lower weight for specific audience flavors
    'Modern Woman\'s Voice': 85,
    'Women\'s Real Talk': 80,
    'Youth Adventure Quest': 85,
    'Maine Youth Stories': 75,
    
    # Standard weight for structural flavors
    'Story Skeleton': 60,
    'Short-Form Viral': 65,
    'Niche-Blend': 55,
    'Sci-Fi + School Realism': 60,
}

# Default weight for flavors not explicitly listed
DEFAULT_FLAVOR_WEIGHT = 50

# =============================================================================
# IDEA GENERATION FUNCTIONS
# =============================================================================

def generate_idea_from_flavor(
    title: str,
    flavor_name: str,
    description: str = "",
    variation_index: int = 0,
) -> Dict[str, Any]:
    """Generate an idea using a flavor.
    
    Args:
        title: Input title/topic
        flavor_name: Name of the flavor to use
        description: Optional description
        variation_index: Variation number for uniqueness
        
    Returns:
        Dictionary with generated idea content
    """
    if flavor_name not in FLAVOR_DEFINITIONS:
        raise ValueError(f"Unknown flavor: {flavor_name}")
    
    flavor = FLAVOR_DEFINITIONS[flavor_name]
    seed = _generate_seed(title, description, variation_index)
    
    # Generate idea content based on flavor
    idea = {
        'flavor_name': flavor_name,
        'flavor_description': flavor['description'],
        'source_title': title,
        'source_description': description,
        'variation_index': variation_index,
        'keywords': flavor['keywords'],
    }
    
    # Generate core fields
    focus_field = flavor.get('focus', 'core_concept')
    
    for field_name, field_desc in DEFAULT_IDEA_FIELDS.items():
        if field_name == focus_field:
            # Make the focus field more detailed
            idea[field_name] = _generate_focused_content(
                title, description, field_desc, flavor_name, seed
            )
        else:
            # Generate standard content for other fields
            idea[field_name] = _generate_field_content(
                title, description, field_desc, flavor_name, seed
            )
    
    # Add metadata
    idea['generated_at'] = datetime.now().isoformat()
    idea['idea_hash'] = _generate_idea_hash(title, flavor_name, variation_index)
    
    return idea


def create_ideas_from_input(
    title: str,
    count: int = 10,
    description: str = "",
    flavors: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Create multiple ideas from input using flavors.
    
    Args:
        title: Input title/topic
        count: Number of ideas to generate (default: 10)
        description: Optional description
        flavors: Optional list of specific flavors to use.
                If None, uses weighted random selection.
                
    Returns:
        List of generated ideas
    """
    ideas = []
    
    if flavors:
        # Use specified flavors
        selected_flavors = flavors[:count]
    else:
        # Use weighted random selection
        selected_flavors = pick_multiple_weighted_flavors(count)
    
    for i, flavor_name in enumerate(selected_flavors):
        try:
            idea = generate_idea_from_flavor(
                title=title,
                flavor_name=flavor_name,
                description=description,
                variation_index=i,
            )
            ideas.append(idea)
        except Exception as e:
            print(f"Warning: Failed to generate idea with flavor {flavor_name}: {e}")
            continue
    
    return ideas


def pick_weighted_flavor(seed: Optional[int] = None) -> str:
    """Pick a flavor using weighted random selection.
    
    Args:
        seed: Optional seed for reproducibility
        
    Returns:
        Selected flavor name
    """
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()
    
    flavors = list(FLAVOR_DEFINITIONS.keys())
    weights = [FLAVOR_WEIGHTS.get(f, DEFAULT_FLAVOR_WEIGHT) for f in flavors]
    
    selected = rng.choices(flavors, weights=weights, k=1)[0]
    return selected


def pick_multiple_weighted_flavors(
    count: int,
    seed: Optional[int] = None,
    allow_duplicates: bool = False,
) -> List[str]:
    """Pick multiple flavors using weighted random selection.
    
    Args:
        count: Number of flavors to pick
        seed: Optional seed for reproducibility
        allow_duplicates: If False, ensures unique flavors
        
    Returns:
        List of selected flavor names
    """
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()
    
    flavors = list(FLAVOR_DEFINITIONS.keys())
    weights = [FLAVOR_WEIGHTS.get(f, DEFAULT_FLAVOR_WEIGHT) for f in flavors]
    
    if allow_duplicates or count > len(flavors):
        # Allow duplicates
        selected = rng.choices(flavors, weights=weights, k=count)
    else:
        # Ensure unique flavors
        selected = []
        remaining_flavors = flavors.copy()
        remaining_weights = weights.copy()
        
        for _ in range(min(count, len(flavors))):
            choice = rng.choices(remaining_flavors, weights=remaining_weights, k=1)[0]
            selected.append(choice)
            
            # Remove selected flavor to avoid duplicates
            idx = remaining_flavors.index(choice)
            remaining_flavors.pop(idx)
            remaining_weights.pop(idx)
    
    return selected


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _generate_seed(title: str, description: str, variation_index: int) -> int:
    """Generate a consistent seed from inputs."""
    content = f"{title}{description}{variation_index}"
    hash_obj = hashlib.md5(content.encode())
    return int(hash_obj.hexdigest()[:8], 16)


def _generate_idea_hash(title: str, flavor_name: str, variation_index: int) -> str:
    """Generate a unique hash for the idea."""
    content = f"{title}{flavor_name}{variation_index}{datetime.now().isoformat()}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def _generate_focused_content(
    title: str,
    description: str,
    field_desc: str,
    flavor_name: str,
    seed: int,
) -> str:
    """Generate detailed content for the focus field."""
    # Create more detailed content for the main focus field
    topic = _humanize_topic(title)
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
    title: str,
    description: str,
    field_desc: str,
    flavor_name: str,
    seed: int,
) -> str:
    """Generate standard content for a field."""
    topic = _humanize_topic(title)
    
    templates = [
        f"{field_desc} for {topic}",
        f"{topic}: {field_desc.lower()}",
        f"How {topic} relates to {field_desc.lower()}",
    ]
    
    rng = random.Random(seed)
    return rng.choice(templates)


def _humanize_topic(title: str) -> str:
    """Convert title to readable topic format."""
    # Remove special characters, convert to lowercase
    topic = re.sub(r'[^\w\s-]', '', title)
    topic = topic.strip().lower()
    
    # Capitalize first letter
    if topic:
        topic = topic[0].upper() + topic[1:]
    
    return topic if topic else "this topic"


# =============================================================================
# TEXT FORMATTING
# =============================================================================

def format_idea_as_text(idea: Dict[str, Any]) -> str:
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
# COMPATIBILITY FUNCTIONS
# =============================================================================

def list_flavors() -> List[str]:
    """Get list of all available flavors."""
    return sorted(FLAVOR_DEFINITIONS.keys())


def get_flavor(flavor_name: str) -> Dict[str, Any]:
    """Get flavor definition."""
    if flavor_name not in FLAVOR_DEFINITIONS:
        raise KeyError(f"Flavor not found: {flavor_name}")
    return FLAVOR_DEFINITIONS[flavor_name].copy()


def get_flavor_count() -> int:
    """Get total number of flavors."""
    return len(FLAVOR_DEFINITIONS)


# Backward compatibility aliases
list_templates = list_flavors
get_template = get_flavor
DEFAULT_IDEA_COUNT = 10

__all__ = [
    'FLAVOR_DEFINITIONS',
    'FLAVOR_WEIGHTS',
    'DEFAULT_FLAVOR_WEIGHT',
    'DEFAULT_IDEA_FIELDS',
    'generate_idea_from_flavor',
    'create_ideas_from_input',
    'pick_weighted_flavor',
    'pick_multiple_weighted_flavors',
    'format_idea_as_text',
    'list_flavors',
    'get_flavor',
    'get_flavor_count',
    'DEFAULT_IDEA_COUNT',
    # Compatibility
    'list_templates',
    'get_template',
]
