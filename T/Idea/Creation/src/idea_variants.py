"""Idea Variant Templates module.

This module provides template definitions for different idea variant formats.
Each template defines the structure and fields needed for a specific type
of idea output, which can be used by AI generators or manual creation.

Templates are dictionaries that describe:
- Required fields and their descriptions
- Optional metadata
- Example values for guidance
"""

from typing import Dict, Any, List


# =============================================================================
# VARIANT TEMPLATE DEFINITIONS
# =============================================================================

VARIANT_EMOTION_FIRST = {
    "name": "Emotion-First Hook",
    "description": "Formats an idea with emotion as the primary driver",
    "fields": {
        "main_emotion": "Primary emotion to evoke (e.g., fear, excitement, curiosity, sadness, anger, joy)",
        "core_hook": "One sentence that captures the emotional hook",
        "target_audience": "Who this content is for",
        "unusual_angle": "A unique perspective or approach",
        "ending_style": "How the content ends (twist, cliffhanger, resolution, open)",
        "content_constraints": {
            "length": "Content length (short, medium, long)",
            "safety": "Safety considerations for the content"
        }
    },
    "example": {
        "main_emotion": "curiosity",
        "core_hook": "The untold truth about ancient mysteries will surprise you.",
        "target_audience": "History enthusiasts aged 25-45",
        "unusual_angle": "from an insider's perspective",
        "ending_style": "twist",
        "content_constraints": {
            "length": "5-10 minutes / 1000-2000 words",
            "safety": "Review for sensitive content before publishing"
        }
    }
}

VARIANT_MYSTERY = {
    "name": "Mystery/Curiosity Gap",
    "description": "Structures an idea around a central mystery or unanswered question",
    "fields": {
        "central_mystery": "The main unanswered question driving the content",
        "emotional_hook": "Why the audience will care about this mystery",
        "key_hook_scene": "One pivotal scene or moment that hooks the viewer",
        "title_direction": {
            "type": "Title framing type (question, reveal, mystery, declaration)",
            "suggestion": "Suggested title based on the type"
        },
        "tone_notes": "Overall tone (suspenseful, intriguing, dark, playful)",
        "style_notes": "Presentation style (investigative, narrative, documentary)",
        "sensitivities": "Boundaries and considerations to respect"
    },
    "example": {
        "central_mystery": "What really happened in the abandoned facility?",
        "emotional_hook": "Everyone thinks they know the story, but the truth reveals something deeply human.",
        "key_hook_scene": "The moment the door opens and silence falls.",
        "title_direction": {
            "type": "question",
            "suggestion": "What Really Happened at Building 7?"
        },
        "tone_notes": "suspenseful",
        "style_notes": "investigative",
        "sensitivities": ["Avoid sensationalism", "Respect privacy", "Fact-check claims"]
    }
}

VARIANT_SKELETON = {
    "name": "Story Skeleton",
    "description": "Provides a complete story structure framework",
    "fields": {
        "opening_hook": "The attention-grabbing opening moment",
        "context_setup": "Background information and setup",
        "rising_stakes": "How tension builds throughout",
        "peak_moment": "The climax or twist seed",
        "conclusion_shape": "How the story ends (resolution, cliffhanger, open_ended)",
        "platform": "Ideal platform for this content",
        "target_audience": "Who this content is for",
        "title_keywords": "Keywords for title generation",
        "title_images": "Visual concepts for thumbnails/covers"
    },
    "example": {
        "opening_hook": "Nobody expected what would happen next...",
        "context_setup": "Establish the who, what, where, why",
        "rising_stakes": "Each revelation raises the stakes higher",
        "peak_moment": "A surprising discovery that reframes everything",
        "conclusion_shape": "resolution",
        "platform": "youtube",
        "target_audience": "Story lovers aged 18-35",
        "title_keywords": ["mystery", "reveal", "truth"],
        "title_images": ["Dramatic reveal", "Key character", "Symbolic visual"]
    }
}

VARIANT_SHORTFORM = {
    "name": "Short-Form Viral",
    "description": "Optimized for short-form viral content platforms",
    "fields": {
        "hook_essence": "5-8 word hook/essence",
        "premise": "1-sentence premise",
        "first_frame_concept": "Scroll-stopping first frame visual",
        "wow_moment": "The 'wow' moment that makes viewers share",
        "engagement_mechanic": {
            "type": "Type of engagement (debate, question, emotional_statement)",
            "content": "The actual engagement prompt"
        },
        "audience_segment": {
            "demographic": "Target demographic",
            "interest": "Interest category",
            "platform": "Target platform"
        },
        "safety_checklist": "Platform guideline considerations"
    },
    "example": {
        "hook_essence": "This changes everything you know",
        "premise": "The untold story that will blow your mind.",
        "first_frame_concept": "Bold text overlay with dramatic visual",
        "wow_moment": "The reveal that makes viewers say 'No way!'",
        "engagement_mechanic": {
            "type": "question",
            "content": "Did you know this? Comment below!"
        },
        "audience_segment": {
            "demographic": "18-34",
            "interest": "entertainment",
            "platform": "tiktok"
        },
        "safety_checklist": ["No copyrighted music", "Follow guidelines", "Fact-check claims"]
    }
}

VARIANT_NICHE_BLEND = {
    "name": "Niche-Blend",
    "description": "Combines multiple niches for unique content positioning",
    "fields": {
        "combined_niches": "Three niches to blend (e.g., horror + true crime + psychology)",
        "niche_blend_description": "How the niches work together",
        "hook_scene": "A specific scene demonstrating the blend",
        "emotional_driver": "The emotional core of the blend",
        "title_framing": "Multiple title options showing the blend",
        "platform": "Target platform",
        "target_audience": "Who this appeals to",
        "content_limits": "Boundaries to maintain clarity"
    },
    "example": {
        "combined_niches": ["horror", "true crime", "psychology"],
        "niche_blend_description": "Combining horror atmosphere with true crime investigation and psychological analysis",
        "hook_scene": "Opening: A horror-style approach meets unexpected psychological insight",
        "emotional_driver": "The intersection creates unique emotional resonance",
        "title_framing": {
            "option_1": "The Psychology of Horror",
            "option_2": "When Horror Meets True Crime",
            "option_3": "A Horror-Psychology Story"
        },
        "platform": "youtube",
        "target_audience": "Niche enthusiasts",
        "content_limits": {
            "primary_focus": "Horror elements",
            "secondary": "True crime support",
            "avoid": "Over-mixing that confuses the message"
        }
    }
}

VARIANT_MINIMAL = {
    "name": "Minimal Idea Packet",
    "description": "The simplest possible idea structure",
    "fields": {
        "hook": "1 sentence hook",
        "audience": "Target audience",
        "tone": "Content tone",
        "length": "Target length"
    },
    "example": {
        "hook": "Discover the truth that changes everything.",
        "audience": "General audience",
        "tone": "engaging",
        "length": "medium"
    }
}

VARIANT_4POINT = {
    "name": "4-Point Quick Structure",
    "description": "Four essential points for quick idea definition",
    "fields": {
        "hook_moment": "The key hook moment",
        "target_audience": "Who this is for",
        "style_tone": "Style and tone",
        "ideal_length": "Ideal content length"
    },
    "example": {
        "hook_moment": "The moment you realize everything is not what you thought.",
        "target_audience": "General audience",
        "style_tone": "engaging",
        "ideal_length": "5-10 minutes"
    }
}

VARIANT_HOOK_FRAME = {
    "name": "Hook + Frame",
    "description": "Simple hook with title framing strategy",
    "fields": {
        "hook_sentence": "One attention-grabbing sentence",
        "title_frame": {
            "type": "Frame type (question, shock, mystery, reveal)",
            "framed_title": "The title using this frame"
        },
        "target_audience": "Who this is for",
        "suggested_length": "Suggested content length"
    },
    "example": {
        "hook_sentence": "What if everything you knew was wrong?",
        "title_frame": {
            "type": "question",
            "framed_title": "What Really Happened?"
        },
        "target_audience": "General audience",
        "suggested_length": "medium"
    }
}

VARIANT_SHORTFORM2 = {
    "name": "Short Form 2.0",
    "description": "Enhanced short-form viral content structure",
    "fields": {
        "concept": "5-8 word concept",
        "premise": "1-sentence premise",
        "audience": "Target audience",
        "length": "Target length",
        "tone": "Content tone"
    },
    "example": {
        "concept": "This changes everything - Wait for it",
        "premise": "The wild story that everyone needs to see.",
        "audience": "Social media users",
        "length": "60 seconds",
        "tone": "viral"
    }
}

VARIANT_GENRE = {
    "name": "Genre Focus",
    "description": "Genre-specific idea structure",
    "fields": {
        "hook": "Genre-appropriate hook",
        "genre": "Content genre",
        "audience": "Target audience",
        "tone_style": "Tone and style",
        "length_limit": "Length constraint"
    },
    "example": {
        "hook": "The terrifying truth that haunts to this day...",
        "genre": "horror",
        "audience": "Horror fans",
        "tone_style": "dark and suspenseful",
        "length_limit": "10-15 minutes"
    }
}

VARIANT_SCENE_SEED = {
    "name": "Scene Seed",
    "description": "Starting point for scene/script development",
    "fields": {
        "scene_hook": "1 sentence scene opener",
        "audience": "Target audience",
        "tone": "Scene tone",
        "target_script_length": "Target script length"
    },
    "example": {
        "scene_hook": "FADE IN: The moment everything changes...",
        "audience": "General audience",
        "tone": "cinematic",
        "target_script_length": "5-10 minutes"
    }
}


# =============================================================================
# TEMPLATE REGISTRY
# =============================================================================

VARIANT_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "emotion_first": VARIANT_EMOTION_FIRST,
    "mystery": VARIANT_MYSTERY,
    "skeleton": VARIANT_SKELETON,
    "shortform": VARIANT_SHORTFORM,
    "niche_blend": VARIANT_NICHE_BLEND,
    "minimal": VARIANT_MINIMAL,
    "4point": VARIANT_4POINT,
    "hook_frame": VARIANT_HOOK_FRAME,
    "shortform2": VARIANT_SHORTFORM2,
    "genre": VARIANT_GENRE,
    "scene_seed": VARIANT_SCENE_SEED,
}


def get_template(variant_name: str) -> Dict[str, Any]:
    """Get a variant template by name.
    
    Args:
        variant_name: Name of the variant template
        
    Returns:
        Template dictionary
        
    Raises:
        KeyError: If variant_name is not found
    """
    if variant_name not in VARIANT_TEMPLATES:
        raise KeyError(f"Unknown variant: {variant_name}. Available: {list(VARIANT_TEMPLATES.keys())}")
    return VARIANT_TEMPLATES[variant_name]


def list_templates() -> List[str]:
    """List all available variant template names.
    
    Returns:
        List of template names
    """
    return list(VARIANT_TEMPLATES.keys())


def get_template_fields(variant_name: str) -> Dict[str, Any]:
    """Get only the fields definition for a variant template.
    
    Args:
        variant_name: Name of the variant template
        
    Returns:
        Fields dictionary
    """
    template = get_template(variant_name)
    return template.get("fields", {})


def get_template_example(variant_name: str) -> Dict[str, Any]:
    """Get the example for a variant template.
    
    Args:
        variant_name: Name of the variant template
        
    Returns:
        Example dictionary
    """
    template = get_template(variant_name)
    return template.get("example", {})


# =============================================================================
# IDEA VARIANT CREATION
# =============================================================================

import random
import hashlib
from datetime import datetime

# Configuration constants
MIN_KEYWORD_LENGTH = 3  # Minimum word length for keywords
MAX_KEYWORDS = 5  # Maximum number of keywords to extract
MAX_ESSENCE_WORDS = 5  # Maximum words for hook essence
MAX_CONCEPT_WORDS = 6  # Maximum words for concept

# Variability pools for generating diverse content
EMOTION_POOL = ["curiosity", "fear", "excitement", "wonder", "surprise", "intrigue", "nostalgia", "hope", "tension", "empathy"]
ANGLE_POOL = [
    "from an insider's perspective",
    "through a completely unexpected lens", 
    "revealing what experts missed",
    "from the perspective of those affected",
    "through a counter-intuitive approach",
    "exploring the hidden connections",
    "with a fresh modern take",
    "uncovering forgotten details",
    "challenging conventional wisdom",
    "from a psychological angle"
]
ENDING_STYLES = ["twist", "cliffhanger", "resolution", "open", "revelation", "callback", "question"]
TONE_POOL = ["suspenseful", "intriguing", "dark", "playful", "dramatic", "mysterious", "contemplative", "intense"]
STYLE_POOL = ["investigative", "narrative", "documentary", "cinematic", "conversational", "immersive"]
HOOK_TEMPLATES = [
    "What if everything you knew about {topic} was wrong?",
    "The untold truth about {topic} will change how you see everything.",
    "Nobody talks about this aspect of {topic}...",
    "Here's what they don't want you to know about {topic}.",
    "The hidden story behind {topic} finally revealed.",
    "You've never seen {topic} like this before.",
    "The moment that changed {topic} forever.",
    "Why {topic} matters more than you think.",
    "The secret connection between {topic} and everything else.",
    "What happens when {topic} goes wrong?"
]
MYSTERY_TEMPLATES = [
    "What really happened with {topic}?",
    "The unsolved mystery of {topic}",
    "Why does no one talk about {topic}?",
    "The question everyone is afraid to ask about {topic}",
    "What's hiding behind {topic}?",
    "The disappearance of the truth about {topic}",
    "Who benefits from keeping {topic} secret?"
]
CONCLUSION_SHAPES = ["resolution", "cliffhanger", "open_ended", "twist_ending", "circular", "revelation"]
PLATFORMS = ["youtube", "tiktok", "instagram", "medium", "podcast", "blog"]
DEMOGRAPHICS = ["18-24", "25-34", "35-44", "18-34", "25-45", "all ages"]
INTERESTS = ["entertainment", "education", "true crime", "science", "history", "culture", "technology", "lifestyle"]


def _get_variation_seed(title: str, variant_name: str, variation_index: int = 0, use_time: bool = False) -> int:
    """Generate a deterministic but varied seed for consistent randomization.
    
    Args:
        title: The idea title
        variant_name: Name of the variant
        variation_index: Index for additional variation
        use_time: Whether to include time component (makes it non-deterministic)
        
    Returns:
        Integer seed for randomization
    """
    seed_string = f"{title}_{variant_name}_{variation_index}"
    if use_time:
        seed_string += f"_{datetime.now().strftime('%Y%m%d%H')}"
    return int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16)


def _pick_from_pool(pool: list, seed: int, offset: int = 0) -> str:
    """Pick an item from pool based on seed for variability."""
    return pool[(seed + offset) % len(pool)]


def create_idea_variant(
    title: str,
    variant_name: str,
    description: str = "",
    variation_index: int = 0,
    randomize: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """Create an idea variant from a title using a specific template.
    
    This function generates a structured idea variant based on the specified
    template. It populates the template fields with content derived from
    the input title and description, with built-in variability to prevent
    repetition.
    
    Args:
        title: The idea title/concept
        variant_name: Name of the variant template to use
        description: Optional description/concept
        variation_index: Index for creating multiple different variants of same type
        randomize: Whether to add randomization for more variety
        **kwargs: Additional parameters to override template defaults
        
    Returns:
        Dictionary with the variant structure populated
        
    Raises:
        ValueError: If title is empty
        KeyError: If variant_name is not found
    """
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")
    
    template = get_template(variant_name)
    
    # Generate variation seed for consistent but varied output
    seed = _get_variation_seed(title, variant_name, variation_index, use_time=randomize)
    if randomize:
        # Use seed to initialize random state for reproducibility when debugging
        rng = random.Random(seed)
        seed += rng.randint(0, 1000)
    
    # Start with the example as base and customize
    result = {
        "variant_type": variant_name,
        "variant_name": template["name"],
        "source_title": title,
        "source_description": description,
        "variation_index": variation_index,
        "variation_seed": seed,
    }
    
    # Generate variant-specific content based on title with variation
    if variant_name == "emotion_first":
        result.update(_create_emotion_first_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "mystery":
        result.update(_create_mystery_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "skeleton":
        result.update(_create_skeleton_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "shortform":
        result.update(_create_shortform_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "niche_blend":
        result.update(_create_niche_blend_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "minimal":
        result.update(_create_minimal_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "4point":
        result.update(_create_4point_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "hook_frame":
        result.update(_create_hook_frame_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "shortform2":
        result.update(_create_shortform2_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "genre":
        result.update(_create_genre_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "scene_seed":
        result.update(_create_scene_seed_variant(title, description, kwargs, seed, variation_index))
    
    return result


def create_all_variants(
    title: str,
    description: str = "",
    **kwargs
) -> List[Dict[str, Any]]:
    """Create all idea variants from a single title.
    
    Generates one variant for each template type, providing multiple
    perspectives and structures for the same base idea.
    
    Args:
        title: The idea title/concept
        description: Optional description/concept
        **kwargs: Additional parameters passed to each variant
        
    Returns:
        List of variant dictionaries, one per template
    """
    variants = []
    for i, variant_name in enumerate(VARIANT_TEMPLATES.keys()):
        variant = create_idea_variant(title, variant_name, description, variation_index=i, **kwargs)
        variants.append(variant)
    return variants


def create_selected_variants(
    title: str,
    variant_names: List[str],
    description: str = "",
    **kwargs
) -> List[Dict[str, Any]]:
    """Create specific idea variants from a title.
    
    Args:
        title: The idea title/concept
        variant_names: List of variant template names to use
        description: Optional description/concept
        **kwargs: Additional parameters passed to each variant
        
    Returns:
        List of variant dictionaries for selected templates
    """
    variants = []
    for i, variant_name in enumerate(variant_names):
        variant = create_idea_variant(title, variant_name, description, variation_index=i, **kwargs)
        variants.append(variant)
    return variants


def create_multiple_of_same_variant(
    title: str,
    variant_name: str,
    count: int = 5,
    description: str = "",
    **kwargs
) -> List[Dict[str, Any]]:
    """Create multiple different variants of the same type.
    
    This ensures each variant is unique even when using the same template,
    by varying the seed and picking different options from variation pools.
    
    Args:
        title: The idea title/concept
        variant_name: Name of the variant template to use
        count: Number of variants to create
        description: Optional description/concept
        **kwargs: Additional parameters passed to each variant
        
    Returns:
        List of variant dictionaries, all different despite same template
    """
    variants = []
    for i in range(count):
        variant = create_idea_variant(
            title, variant_name, description, 
            variation_index=i, 
            randomize=True, 
            **kwargs
        )
        variants.append(variant)
    return variants


# =============================================================================
# VARIANT CREATION HELPERS (with variability)
# =============================================================================

def _create_emotion_first_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create emotion-first variant content with variability."""
    emotion = kwargs.get("main_emotion") or _pick_from_pool(EMOTION_POOL, seed, variation_index)
    hook_template = _pick_from_pool(HOOK_TEMPLATES, seed, variation_index + 1)
    angle = _pick_from_pool(ANGLE_POOL, seed, variation_index + 2)
    ending = _pick_from_pool(ENDING_STYLES, seed, variation_index + 3)
    
    return {
        "main_emotion": emotion,
        "core_hook": hook_template.format(topic=title.lower()),
        "target_audience": kwargs.get("target_audience", "General audience"),
        "unusual_angle": angle,
        "ending_style": kwargs.get("ending_style", ending),
        "content_constraints": {
            "length": kwargs.get("length", "5-10 minutes"),
            "safety": "Review for sensitive content before publishing"
        }
    }


def _create_mystery_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create mystery variant content with variability."""
    mystery_template = _pick_from_pool(MYSTERY_TEMPLATES, seed, variation_index)
    tone = _pick_from_pool(TONE_POOL, seed, variation_index + 1)
    style = _pick_from_pool(STYLE_POOL, seed, variation_index + 2)
    
    title_types = ["question", "reveal", "mystery", "declaration"]
    title_type = _pick_from_pool(title_types, seed, variation_index + 3)
    
    title_suggestions = {
        "question": f"What Really Happened to {title}?",
        "reveal": f"The {title} Secret Finally Exposed",
        "mystery": f"The Unsolved Mystery of {title}",
        "declaration": f"The Truth About {title}"
    }
    
    return {
        "central_mystery": mystery_template.format(topic=title.lower()),
        "emotional_hook": f"Everyone thinks they know about {title.lower()}, but the truth reveals something deeper.",
        "key_hook_scene": f"The moment the truth about {title.lower()} is revealed.",
        "title_direction": {
            "type": title_type,
            "suggestion": title_suggestions[title_type]
        },
        "tone_notes": kwargs.get("tone", tone),
        "style_notes": kwargs.get("style", style),
        "sensitivities": ["Avoid sensationalism", "Respect privacy", "Fact-check claims"]
    }


def _create_skeleton_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create story skeleton variant content with variability."""
    conclusion = _pick_from_pool(CONCLUSION_SHAPES, seed, variation_index)
    platform = _pick_from_pool(PLATFORMS, seed, variation_index + 1)
    
    opening_hooks = [
        f"Nobody expected what would happen with {title.lower()}...",
        f"The story of {title.lower()} begins in an unexpected place...",
        f"Everything changed when {title.lower()} was discovered...",
        f"This is the moment {title.lower()} changed everything...",
        f"Before we knew about {title.lower()}, the world was different..."
    ]
    
    return {
        "opening_hook": _pick_from_pool(opening_hooks, seed, variation_index + 2),
        "context_setup": f"Establish the background of {title.lower()}",
        "rising_stakes": f"Each revelation about {title.lower()} raises the stakes",
        "peak_moment": f"A surprising discovery that reframes {title.lower()}",
        "conclusion_shape": kwargs.get("conclusion", conclusion),
        "platform": kwargs.get("platform", platform),
        "target_audience": kwargs.get("target_audience", "Story lovers"),
        "title_keywords": [w for w in title.split() if len(w) > MIN_KEYWORD_LENGTH][:MAX_KEYWORDS],
        "title_images": ["Dramatic reveal", "Key visual", "Symbolic image"]
    }


def _create_shortform_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create short-form viral variant content with variability."""
    words = title.split()
    
    essence_templates = [
        " ".join(words[:MAX_ESSENCE_WORDS]) + "..." if len(words) > MAX_ESSENCE_WORDS else f"{title} - Wait for it",
        f"The truth about {title.lower()}",
        f"You won't believe {title.lower()}",
        f"This is {title.lower()} explained",
        f"POV: You discover {title.lower()}"
    ]
    
    engagement_types = ["question", "debate", "emotional_statement", "poll", "challenge"]
    engagement_contents = [
        f"Did you know this about {title.lower()}? Comment below!",
        f"Agree or disagree? {title} is...",
        f"This changed my perspective on {title.lower()}",
        f"Which side are you on? {title}",
        f"Try this with {title.lower()} and see what happens!"
    ]
    
    demographic = _pick_from_pool(DEMOGRAPHICS, seed, variation_index)
    interest = _pick_from_pool(INTERESTS, seed, variation_index + 1)
    platform = _pick_from_pool(["tiktok", "instagram", "youtube_shorts"], seed, variation_index + 2)
    
    return {
        "hook_essence": _pick_from_pool(essence_templates, seed, variation_index + 3),
        "premise": f"The untold story of {title.lower()} that will blow your mind.",
        "first_frame_concept": f"Bold text: \"{title.upper()}\" with dramatic visual",
        "wow_moment": f"The reveal about {title.lower()} that makes viewers say 'No way!'",
        "engagement_mechanic": {
            "type": _pick_from_pool(engagement_types, seed, variation_index + 4),
            "content": _pick_from_pool(engagement_contents, seed, variation_index + 5)
        },
        "audience_segment": {
            "demographic": kwargs.get("demographic", demographic),
            "interest": kwargs.get("interest", interest),
            "platform": kwargs.get("platform", platform)
        },
        "safety_checklist": ["No copyrighted music", "Follow guidelines", "Fact-check claims"]
    }


def _create_niche_blend_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create niche-blend variant content with variability."""
    all_niches = ["horror", "true crime", "psychology", "history", "science", "comedy", 
                  "drama", "mystery", "documentary", "education", "technology", "lifestyle"]
    
    # Pick 3 different niches based on seed
    niches = kwargs.get("niches")
    if not niches:
        n1 = _pick_from_pool(all_niches, seed, variation_index)
        n2 = _pick_from_pool([n for n in all_niches if n != n1], seed, variation_index + 1)
        n3 = _pick_from_pool([n for n in all_niches if n not in [n1, n2]], seed, variation_index + 2)
        niches = [n1, n2, n3]
    
    platform = _pick_from_pool(PLATFORMS, seed, variation_index + 3)
    
    return {
        "combined_niches": niches,
        "niche_blend_description": f"Combining {niches[0]}, {niches[1]}, and {niches[2]} perspectives on {title.lower()}",
        "hook_scene": f"Opening: A {niches[0]} approach to {title.lower()} meets unexpected {niches[1]} elements",
        "emotional_driver": f"The intersection of {niches[0]} and {niches[1]} creates unique resonance",
        "title_framing": {
            "option_1": f"The {niches[0].title()} of {title}",
            "option_2": f"When {niches[0].title()} Meets {niches[1].title()}: {title}",
            "option_3": f"{title}: A {niches[0].title()}-{niches[1].title()} Story"
        },
        "platform": kwargs.get("platform", platform),
        "target_audience": kwargs.get("target_audience", "Niche enthusiasts"),
        "content_limits": {
            "primary_focus": f"{niches[0]} elements",
            "secondary": f"{niches[1]} support",
            "avoid": "Over-mixing that confuses the message"
        }
    }


def _create_minimal_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create minimal variant content with variability."""
    hook_template = _pick_from_pool(HOOK_TEMPLATES, seed, variation_index)
    tone = _pick_from_pool(TONE_POOL, seed, variation_index + 1)
    lengths = ["short", "medium", "long", "micro", "extended"]
    
    return {
        "hook": hook_template.format(topic=title.lower()),
        "audience": kwargs.get("audience", "General audience"),
        "tone": kwargs.get("tone", tone),
        "length": kwargs.get("length", _pick_from_pool(lengths, seed, variation_index + 2))
    }


def _create_4point_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create 4-point variant content with variability."""
    hook_moments = [
        f"The moment you realize {title.lower()} is not what you thought.",
        f"When {title.lower()} reveals its true nature.",
        f"The turning point that changes everything about {title.lower()}.",
        f"The revelation about {title.lower()} you never saw coming.",
        f"That one detail about {title.lower()} that changes the whole story."
    ]
    
    style_tones = ["engaging", "dramatic", "informative", "suspenseful", "playful", "serious"]
    lengths = ["3-5 minutes", "5-10 minutes", "10-15 minutes", "15-20 minutes", "60 seconds"]
    
    return {
        "hook_moment": _pick_from_pool(hook_moments, seed, variation_index),
        "target_audience": kwargs.get("target_audience", "General audience"),
        "style_tone": kwargs.get("style_tone", _pick_from_pool(style_tones, seed, variation_index + 1)),
        "ideal_length": kwargs.get("ideal_length", _pick_from_pool(lengths, seed, variation_index + 2))
    }


def _create_hook_frame_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create hook + frame variant content with variability."""
    frame_types = ["question", "shock", "mystery", "reveal"]
    frame_type = kwargs.get("frame_type") or _pick_from_pool(frame_types, seed, variation_index)
    
    frame_titles = {
        "question": f"What Really Happened to {title}?",
        "shock": f"The Shocking Truth About {title}",
        "mystery": f"The Unsolved Mystery of {title}",
        "reveal": f"Finally Exposed: The {title} Story"
    }
    
    hook_sentences = [
        f"What if everything you knew about {title.lower()} was wrong?",
        f"The truth about {title.lower()} will shock you.",
        f"Nobody is talking about this aspect of {title.lower()}.",
        f"Here's what they don't want you to know about {title.lower()}.",
        f"This changes everything about {title.lower()}."
    ]
    
    lengths = ["short", "medium", "long"]
    
    return {
        "hook_sentence": _pick_from_pool(hook_sentences, seed, variation_index + 1),
        "title_frame": {
            "type": frame_type,
            "framed_title": frame_titles.get(frame_type, title)
        },
        "target_audience": kwargs.get("target_audience", "General audience"),
        "suggested_length": kwargs.get("suggested_length", _pick_from_pool(lengths, seed, variation_index + 2))
    }


def _create_shortform2_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create short form 2.0 variant content with variability."""
    words = title.split()
    
    concepts = [
        " ".join(words[:MAX_CONCEPT_WORDS]) if len(words) > MAX_CONCEPT_WORDS else f"{title} - Wait for it",
        f"POV: {title}",
        f"This is {title} in 60 seconds",
        f"The {title} story",
        f"Everything about {title}"
    ]
    
    premises = [
        f"The wild story of {title.lower()} that everyone needs to see.",
        f"You won't believe what happened with {title.lower()}.",
        f"This is the {title.lower()} content you've been waiting for.",
        f"The viral truth about {title.lower()}.",
        f"Why {title.lower()} is breaking the internet."
    ]
    
    tones = ["viral", "dramatic", "funny", "shocking", "inspiring", "educational"]
    lengths = ["30 seconds", "60 seconds", "90 seconds", "15 seconds"]
    
    return {
        "concept": _pick_from_pool(concepts, seed, variation_index),
        "premise": _pick_from_pool(premises, seed, variation_index + 1),
        "audience": kwargs.get("audience", "Social media users"),
        "length": kwargs.get("length", _pick_from_pool(lengths, seed, variation_index + 2)),
        "tone": kwargs.get("tone", _pick_from_pool(tones, seed, variation_index + 3))
    }


def _create_genre_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create genre-focused variant content with variability."""
    genres = ["horror", "comedy", "drama", "thriller", "documentary", "educational", "entertainment"]
    genre = kwargs.get("genre") or _pick_from_pool(genres, seed, variation_index)
    genre_hooks = {
        "horror": f"The terrifying truth about {title.lower()} that haunts to this day...",
        "comedy": f"You won't believe what happened with {title.lower()}!",
        "drama": f"The emotional journey of {title.lower()} will move you...",
        "thriller": f"The pulse-pounding story of {title.lower()} begins now...",
        "documentary": f"An in-depth look at {title.lower()} reveals surprising truths...",
        "educational": f"Everything you need to know about {title.lower()}...",
        "entertainment": f"Get ready for the ultimate {title.lower()} experience...",
    }
    return {
        "hook": genre_hooks.get(genre.lower(), f"Discover {title.lower()} like never before..."),
        "genre": genre,
        "audience": kwargs.get("audience", f"{genre.title()} fans"),
        "tone_style": kwargs.get("tone_style", f"{genre}-appropriate"),
        "length_limit": kwargs.get("length_limit", "standard")
    }


def _create_scene_seed_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create scene seed variant content with variability."""
    scene_hooks = [
        f"FADE IN: The moment everything changes for {title.lower()}...",
        f"INT. UNKNOWN LOCATION - NIGHT: We discover {title.lower()}...",
        f"EXT. CITY STREET - DAY: The story of {title.lower()} begins...",
        f"CLOSE UP: The detail that reveals everything about {title.lower()}...",
        f"MONTAGE: The journey through {title.lower()} unfolds...",
        f"FLASHBACK: Before anyone knew about {title.lower()}..."
    ]
    
    tones = ["cinematic", "intimate", "epic", "documentary", "noir", "suspenseful", "whimsical"]
    lengths = ["3-5 minutes", "5-10 minutes", "10-15 minutes", "15-20 minutes", "short film"]
    
    return {
        "scene_hook": _pick_from_pool(scene_hooks, seed, variation_index),
        "audience": kwargs.get("audience", "General audience"),
        "tone": kwargs.get("tone", _pick_from_pool(tones, seed, variation_index + 1)),
        "target_script_length": kwargs.get("target_script_length", _pick_from_pool(lengths, seed, variation_index + 2))
    }


__all__ = [
    "VARIANT_TEMPLATES",
    "VARIANT_EMOTION_FIRST",
    "VARIANT_MYSTERY",
    "VARIANT_SKELETON",
    "VARIANT_SHORTFORM",
    "VARIANT_NICHE_BLEND",
    "VARIANT_MINIMAL",
    "VARIANT_4POINT",
    "VARIANT_HOOK_FRAME",
    "VARIANT_SHORTFORM2",
    "VARIANT_GENRE",
    "VARIANT_SCENE_SEED",
    "get_template",
    "list_templates",
    "get_template_fields",
    "get_template_example",
    "create_idea_variant",
    "create_all_variants",
    "create_selected_variants",
    "create_multiple_of_same_variant",
]
