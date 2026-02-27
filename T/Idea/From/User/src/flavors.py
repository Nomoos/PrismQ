"""Flavor module - High-level flavor API using SOLID design.

This module provides a high-level API for working with flavors,
built on top of the FlavorLoader service.

It provides additional functionality like:
- Flavor categorization
- Audience-specific filtering
- Scoring systems
- Weighted selection helpers
"""

from typing import Dict, List, Optional, Tuple
import random

from flavor_loader import get_flavor_loader


# =============================================================================
# FLAVOR CATEGORIES
# =============================================================================

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
    'Engagement Flawors': [
        'Infinity Loop Close',
        'Hidden Detail Hunt',
        'Before/After Reveal',
        'Micro-Mystery (8\u201312s)',
        'Chat Screenshot Story',
        '"Wait for it" Payoff',
        'Checklist Replay',
        '"POV: Girl Math"',
        'Green/Red Flag Radar',
        'Soft Hot Take',
        'Mini-Series Hook',
        '"I Wish I Knew" Confessional',
        '"Rate My Outfit/Plan"',
        'Aesthetic Satisfying Loop',
        '"2 Endings" Replay',
        '"Spot the Difference"',
        '"One Line Twist"',
        '"Teach Me, Babe"',
    ],
    'Geo-Embedded Story Flavors': [
        'The Morning Train Confession in Halifax',
        'The Girl Who Noticed Something Off in Toronto at 8 AM',
        'The Text I Received Before School in New York',
        'The Silent Walk Through Boston That Changed Everything',
        'The Message I Opened Too Late in Montreal',
        'The Coffee Shop Encounter in Philadelphia',
        'The Routine Morning That Felt Different in Toronto',
        'The Stranger Who Sat Next to Me in New York Subway',
        'The Snowy Morning Secret in Montreal',
        'The Sunrise Realization in Halifax',
        'The Voice Note I Listened to on My Way to School in Boston',
        'The Day Started Normally in Philadelphia\u2026 Until It Didn\u2019t',
        'The Girl Watching Me on the Train to New York',
        'The Feeling I Had Walking Alone in Toronto',
        'The Friend Who Texted Me at 8:03 AM in Boston',
        'The Last Normal Morning in Montreal',
        'The Uneasy Silence in a Halifax Classroom',
        'The Call I Missed in Philadelphia Morning',
        'The Eye Contact That Felt Wrong in New York',
        'The Moment I Knew Something Was About to Happen in Toronto',
    ],
    'Comment-Trigger Flavors': [
        '"This Happened to Me Before School in Boston"',
        'The Girl Who Seemed Perfect in New York',
        'The Friend Group Shift in Toronto Morning',
        'The Subtle Red Flag I Ignored in Philadelphia',
        'The Gut Feeling I Had in Montreal',
        'The Story I Never Told Anyone in Halifax',
        'The Overthinking Spiral on a New York Morning',
        'The Quiet Girl Sitting Behind Me in Boston',
        'The One Detail Nobody Noticed in Toronto',
        'The Morning That Felt Scripted in Montreal',
    ],
    'Rewatch Loop Flavors': [
        'The Clue Hidden in the First Scene (New York)',
        'What You Miss on First Watch in Toronto',
        'The Detail in the Background (Boston Morning)',
        'The Timeline That Doesn\u2019t Add Up in Philadelphia',
        'The Story That Makes Sense Only at the End (Montreal)',
        'The Second Watch Changes Everything in Halifax',
        'The Girl Who Was There the Whole Time (New York)',
        'The Subtle Foreshadowing in Toronto Sunrise',
        'The Scene That Feels Different After the Reveal (Boston)',
        'The Memory That Doesn\u2019t Match Reality (Montreal)',
    ],
    'Psychological & Soft Dark Flavors': [
        'The Girl Who Pretended Everything Was Fine in New York',
        'The Quiet Breakdown on a Toronto Morning',
        'The Smile That Hid Something in Boston',
        'The Safe Place That Suddenly Felt Unsafe in Montreal',
        'The Thought I Couldn\u2019t Ignore in Philadelphia',
        'The Feeling of Being Watched in Halifax',
        'The Version of Me No One Saw in New York',
        'The Secret I Realized Too Late in Toronto',
        'The Emotional Shift During a Normal Morning in Boston',
        'The Story That Gets Darker Each Part (Montreal Setting)',
    ],
    'Hybrid Viral Flavors': [
        'Soft Morning Routine \u2192 Sudden Disturbance (Toronto)',
        'Innocent Beginning \u2192 Creepy Realization (New York)',
        'Comfort Aesthetic \u2192 Psychological Twist (Boston)',
        'Relatable POV \u2192 Dark Reveal (Montreal)',
        'Nostalgic School Morning \u2192 Hidden Truth (Halifax)',
        'Cozy Coffee Scene \u2192 Unsettling Ending (Philadelphia)',
        'Slice of Life \u2192 Suspense Escalation (Toronto)',
        'Emotional Confession \u2192 Unexpected Clue (New York)',
        'Calm Sunrise \u2192 Anxiety Shift (Boston)',
        'Ordinary Day \u2192 Disturbing Pattern (Montreal)',
    ],
    'Ultra-Optimized Meta Flavors': [
        '"I Shouldn\u2019t Be Telling This (Happened in New York)"',
        '"Nobody Believed Me That Morning in Toronto"',
        '"This Still Feels Unreal (Boston Story)"',
        '"I Never Talk About What Happened in Montreal"',
        '"You Won\u2019t Notice It at First (Philadelphia)"',
        '"This Happened at 8:07 AM in Halifax"',
        '"It Started Like Any Normal Morning in New York"',
        '"Something Felt Off in Toronto and I Ignored It"',
        '"The Moment Everything Changed in Boston"',
        '"The Story I Wish I Could Forget (Montreal)"',
    ],
}


# =============================================================================
# BASIC FLAVOR ACCESS
# =============================================================================

def list_flavors() -> List[str]:
    """Get list of all available flavor names.
    
    Returns:
        Sorted list of flavor names
    """
    loader = get_flavor_loader()
    return loader.list_flavor_names()


def get_flavor_count() -> int:
    """Get total number of flavors.
    
    Returns:
        Number of flavors
    """
    loader = get_flavor_loader()
    return loader.get_flavor_count()


def get_flavor_info(flavor_name: str) -> Dict:
    """Get information about a specific flavor.
    
    Args:
        flavor_name: Name of the flavor
        
    Returns:
        Dictionary with flavor information
    """
    loader = get_flavor_loader()
    return loader.get_flavor(flavor_name)


def get_flavor_description(flavor_name: str) -> str:
    """Get description of a flavor.
    
    Args:
        flavor_name: Name of the flavor
        
    Returns:
        Flavor description string
    """
    info = get_flavor_info(flavor_name)
    return info.get('description', '')


def list_flavor_categories() -> Dict[str, List[str]]:
    """Get organized categories of flavors.
    
    Returns:
        Dictionary mapping category names to lists of flavor names
    """
    return FLAVOR_CATEGORIES.copy()


# =============================================================================
# AUDIENCE-SPECIFIC ACCESS
# =============================================================================

def list_flavors_by_audience(audience: Optional[str] = None) -> List[str]:
    """Get list of flavors filtered by target audience.
    
    Args:
        audience: Optional audience filter
                 If None, returns all flavors
    
    Returns:
        List of flavor names matching the audience
    """
    if not audience:
        return list_flavors()
    
    loader = get_flavor_loader()
    return loader.get_flavors_by_audience(audience)


def get_primary_audience_flavors() -> List[str]:
    """Get flavors optimized for the primary audience (13-17 young women in US/Canada).
    
    Returns:
        List of flavor names best suited for primary audience
    """
    primary_audience_key = '13-17'
    loader = get_flavor_loader()
    matching = []
    
    all_flavors = loader.get_all_flavors()
    for flavor_name, info in all_flavors.items():
        audience = info.get('audience', '')
        # Match primary audience or high-scoring flavors
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
        if flavor in all_flavors and flavor not in matching:
            matching.append(flavor)
    
    return sorted(set(matching))


# =============================================================================
# FLAVOR SCORING
# =============================================================================

def score_flavor_for_audience(
    flavor_name: str, 
    audience: str = '13-17 young women US/Canada'
) -> float:
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
    """
    info = get_flavor_info(flavor_name)
    
    # Check for pre-defined score
    if 'score' in info:
        return info['score']
    
    score = 5.0  # Base score
    
    # Explicit audience match
    flavor_audience = info.get('audience', '').lower()
    if audience.lower() in flavor_audience or flavor_audience in audience.lower():
        score += 3.0
    
    # Keyword scoring for primary audience
    if '13-17' in audience or 'teen' in audience.lower() or 'young women' in audience.lower():
        primary_keywords = ['emotional', 'relational', 'identity', 'authentic', 'confession', 
                           'body', 'friendship', 'online', 'transformation']
        keyword_matches = sum(1 for kw in info.get('keywords', []) if kw in primary_keywords)
        score += min(2.0, keyword_matches * 0.4)
    
    # Weight-based adjustment
    weight = info.get('weight', 50)
    if weight >= 90:
        score += 1.0
    elif weight >= 80:
        score += 0.5
    
    return min(10.0, score)


def get_scored_flavors(
    audience: str = '13-17 young women US/Canada', 
    min_score: float = 0.0
) -> List[Tuple[str, float]]:
    """Get all flavors scored for a specific audience.
    
    Args:
        audience: Target audience to score for
        min_score: Minimum score threshold (default: 0.0 for all)
        
    Returns:
        List of tuples (flavor_name, score) sorted by score descending
    """
    scored = []
    for flavor_name in list_flavors():
        score = score_flavor_for_audience(flavor_name, audience)
        if score >= min_score:
            scored.append((flavor_name, score))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


def get_top_flavors_for_audience(
    audience: str = '13-17 young women US/Canada', 
    count: int = 10
) -> List[str]:
    """Get top N flavors for a specific audience.
    
    Args:
        audience: Target audience
        count: Number of top flavors to return (default: 10)
        
    Returns:
        List of top flavor names for the audience
    """
    scored = get_scored_flavors(audience)
    return [name for name, score in scored[:count]]


# =============================================================================
# WEIGHTED SELECTION
# =============================================================================

# Engagement goals that matter for the primary audience (girls 15-20, US/Canada)
# targeting interactions, rewatch, and sharing.
_PRIMARY_ENGAGEMENT_GOALS: frozenset = frozenset({"rewatch", "comment", "share"})


def get_flavor_weights() -> Dict[str, int]:
    """Get the flavor weight mappings.
    
    Returns:
        Dictionary mapping flavor names to their weights
    """
    loader = get_flavor_loader()
    return loader.get_weights()


def pick_weighted_flavor(seed: Optional[int] = None) -> str:
    """Pick a flavor using weighted random selection.

    Uses the full flavor pool minus any flavors that carry ``risk_flags``
    (restricted variants). Each flavor's base weight is boosted by 0.5× for
    every ``engagement_goal`` that aligns with the primary audience goals
    (rewatch, comment, share) — reflecting the content strategy for girls
    15–20 in the US/Canada targeting interactions, rewatch, and sharing.

    Args:
        seed: Optional seed for reproducible selection
        
    Returns:
        Selected flavor name
    """
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()

    loader = get_flavor_loader()
    all_flavor_data = loader.get_all_flavors()
    base_weights = get_flavor_weights()

    flavors = []
    weights = []
    for name, info in all_flavor_data.items():
        if info.get("risk_flags"):
            continue  # skip restricted variants
        base = base_weights.get(name, 50)
        goal_overlap = len(_PRIMARY_ENGAGEMENT_GOALS & set(info.get("engagement_goal", [])))
        effective = base * (1.0 + 0.5 * goal_overlap)
        flavors.append(name)
        weights.append(effective)

    return rng.choices(flavors, weights=weights, k=1)[0]


def get_default_or_random_flavor(
    flavor: Optional[str] = None, 
    use_weighted: bool = True, 
    seed: Optional[int] = None
) -> str:
    """Get a flavor - use provided, or select default/random.
    
    Args:
        flavor: Optional flavor name. If provided, returns this.
        use_weighted: If True, uses weighted random selection
        seed: Optional seed for reproducible weighted selection
        
    Returns:
        Flavor name to use
    """
    if flavor:
        return flavor
    
    if use_weighted:
        return pick_weighted_flavor(seed=seed)
    else:
        # Return highest-weighted primary audience flavor
        top = get_top_flavors_for_audience(count=1)
        return top[0] if top else list_flavors()[0]


def get_default_flavor() -> str:
    """Get the default flavor for idea refinement.
    
    Returns:
        Default flavor name
    """
    return "Emotional Drama + Growth"


# =============================================================================
# SEARCH
# =============================================================================

def search_flavors_by_keyword(keyword: str) -> List[str]:
    """Search for flavors by keyword.
    
    Args:
        keyword: Keyword to search for
        
    Returns:
        List of matching flavor names
    """
    keyword_lower = keyword.lower()
    matches = []
    
    loader = get_flavor_loader()
    all_flavors = loader.get_all_flavors()
    
    for flavor_name, info in all_flavors.items():
        if (keyword_lower in flavor_name.lower() or
            keyword_lower in info.get('description', '').lower() or
            keyword_lower in info.get('keywords', [])):
            matches.append(flavor_name)
    
    return sorted(matches)


# =============================================================================
# ENGAGEMENT FLAWORS
# =============================================================================

def get_engagement_flavors(goal: Optional[str] = None) -> List[str]:
    """Get engagement flavors, optionally filtered by engagement goal.

    Engagement flavors are flavors that carry the ``engagement_goal`` field,
    meaning they are specifically designed to drive rewatch, comments, shares,
    saves, follows or watch-more.

    Args:
        goal: Optional engagement goal to filter by.  Supported values:
              ``"rewatch"``, ``"comment"``, ``"share"``, ``"save"``,
              ``"follow"``, ``"watch_more"``.
              If *None*, all flavors that have any ``engagement_goal`` are
              returned.

    Returns:
        Sorted list of matching flavor names
    """
    loader = get_flavor_loader()
    if goal:
        return loader.get_flavors_by_engagement_goal(goal)
    all_flavors = loader.get_all_flavors()
    return sorted(
        name for name, info in all_flavors.items() if 'engagement_goal' in info
    )


def get_flavors_by_format(format_name: str) -> List[str]:
    """Get flavors that fit a specific content format.

    Args:
        format_name: Platform format, e.g. ``"reels"``, ``"shorts"``,
                     ``"tiktok"``, ``"stories"``.

    Returns:
        Sorted list of matching flavor names
    """
    loader = get_flavor_loader()
    return loader.get_flavors_by_format(format_name)


__all__ = [
    # Categories
    'FLAVOR_CATEGORIES',
    # Basic access
    'list_flavors',
    'get_flavor_count',
    'get_flavor_info',
    'get_flavor_description',
    'list_flavor_categories',
    # Audience-specific
    'list_flavors_by_audience',
    'get_primary_audience_flavors',
    # Scoring
    'score_flavor_for_audience',
    'get_scored_flavors',
    'get_top_flavors_for_audience',
    # Selection
    'get_flavor_weights',
    'pick_weighted_flavor',
    'get_default_or_random_flavor',
    'get_default_flavor',
    # Search
    'search_flavors_by_keyword',
    # Engagement flavors
    'get_engagement_flavors',
    'get_flavors_by_format',
]
