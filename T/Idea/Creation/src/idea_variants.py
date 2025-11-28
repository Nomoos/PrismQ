"""Idea Variant Templates module.

This module provides template definitions for different idea variant formats.
Each template defines the structure and fields needed for a specific type
of idea output, which can be used by AI generators or manual creation.

Templates are dictionaries that describe:
- Required fields and their descriptions
- Optional metadata
- Example values for guidance
"""

import hashlib
import random
import re
from datetime import datetime
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
# NEW CREATIVE VARIANT TEMPLATES (Inspired by genre-specific idea seeds)
# =============================================================================

VARIANT_SOFT_SUPERNATURAL = {
    "name": "Soft Supernatural + Friendship",
    "description": "A gentle supernatural element intertwined with friendship, teamwork, and emotional growth. Safe, no horror - more wonder than fear.",
    "fields": {
        "supernatural_element": "The magical or mysterious object/being/place at the heart of the story",
        "friendship_dynamic": "How friends interact with and around this element",
        "emotional_core": "The deeper feeling or lesson this story explores",
        "visual_hook": "A distinctive visual that makes this idea memorable",
        "twist_seed": "An unexpected aspect that makes this more than typical",
        "audience_appeal": "Who this resonates with and why"
    },
    "example": {
        "supernatural_element": "A ghost girl who can only communicate through mirror fog messages",
        "friendship_dynamic": "She protects the school but needs friends to understand her clues",
        "emotional_core": "Connection beyond what we can see",
        "visual_hook": "Foggy mirrors with finger-traced messages",
        "twist_seed": "The ghost is actually trying to prevent something that happens every year",
        "audience_appeal": "Mystery lovers who want emotion over fear"
    }
}

VARIANT_LIGHT_MYSTERY = {
    "name": "Light Mystery + Adventure",
    "description": "Puzzles, clues, and adventure without dark themes. Detective vibes with aesthetic hooks and group problem-solving.",
    "fields": {
        "central_puzzle": "The mystery or problem that needs solving",
        "clue_aesthetic": "The unique way clues are presented (visual, coded, symbolic)",
        "adventure_setting": "Where this unfolds - should be visually interesting",
        "team_dynamic": "How the group works together to solve it",
        "stakes": "What's at risk - emotional, not dangerous",
        "resolution_style": "How the mystery gets solved"
    },
    "example": {
        "central_puzzle": "An old camera with unfinished footage reveals a mystery still happening today",
        "clue_aesthetic": "Glitchy video clips that piece together",
        "adventure_setting": "Abandoned mall after midnight",
        "team_dynamic": "Each person has skills that unlock different puzzle types",
        "stakes": "Understanding what really happened before the truth is buried forever",
        "resolution_style": "Collaborative revelation where everyone contributes"
    }
}

VARIANT_SCIFI_SCHOOL = {
    "name": "Sci-Fi + School Realism",
    "description": "Near-future tech meets real school life - gadgets that change social dynamics, identity questions, relatable chaos.",
    "fields": {
        "tech_concept": "The sci-fi element that disrupts normal life",
        "school_setting": "How this plays out in realistic school context",
        "social_chaos": "The unexpected social consequences",
        "character_growth": "How characters change because of this tech",
        "visual_hook": "The distinctive visual element (neon, holographic, etc.)",
        "moral_question": "The ethical or identity question raised"
    },
    "example": {
        "tech_concept": "A pin that translates emotions into colors visible above people's heads",
        "school_setting": "Everyone can now see who's crushing on whom, who's anxious, who's lying",
        "social_chaos": "Popularity shifts overnight, secrets become impossible",
        "character_growth": "Learning that vulnerability isn't weakness",
        "visual_hook": "Glowing color auras floating above heads in hallways",
        "moral_question": "Is forced emotional transparency fair?"
    }
}

VARIANT_SAFE_SURVIVAL = {
    "name": "Survival Challenge (Safe)",
    "description": "Teamwork under pressure without real danger - cooperation, problem-solving, and discovering inner strength.",
    "fields": {
        "challenge_scenario": "The situation that requires survival/teamwork skills",
        "cooperation_element": "How working together becomes essential",
        "discovery": "What characters learn about themselves or each other",
        "setting_aesthetic": "The visual world (forest, bunker, storm, etc.)",
        "tension_source": "What creates urgency without real danger",
        "payoff": "The reward or revelation at the end"
    },
    "example": {
        "challenge_scenario": "A storm forces kids to stop at an abandoned bus stop - they must cooperate to leave",
        "cooperation_element": "Each person's random skill becomes crucial",
        "discovery": "The 'weak' kid turns out to be the key to everything",
        "setting_aesthetic": "Rain-soaked bus stop with flickering lights",
        "tension_source": "Time pressure and communication challenges",
        "payoff": "They don't just escape - they become real friends"
    }
}

VARIANT_EMOTIONAL_DRAMA = {
    "name": "Emotional Drama + Growth",
    "description": "Character-driven stories about feelings, friendship, and personal transformation. Deep emotional beats with satisfying arcs.",
    "fields": {
        "emotional_premise": "The core feeling or relationship being explored",
        "character_challenge": "What the main character must face or change",
        "friendship_test": "How relationships are challenged and strengthened",
        "symbolic_element": "An object or ritual that carries emotional weight",
        "turning_point": "The moment that changes everything",
        "growth_arc": "How the character is different by the end"
    },
    "example": {
        "emotional_premise": "A challenge to make the quiet kid laugh again - but there's a deeper story",
        "character_challenge": "Realizing someone's silence isn't about being unfriendly",
        "friendship_test": "Do you give up when it's harder than expected?",
        "symbolic_element": "An old joke book that holds memories",
        "turning_point": "Discovering why the laughter stopped",
        "growth_arc": "From 'fixing' someone to truly seeing them"
    }
}

VARIANT_RIVALS_TO_ALLIES = {
    "name": "Competitive + Rivals to Allies",
    "description": "Competition that becomes collaboration - opposing groups unite against a bigger challenge. Action, teamwork, growth.",
    "fields": {
        "rival_groups": "The two opposing sides and what they represent",
        "competition": "What they're fighting over initially",
        "common_enemy": "The bigger problem that forces them together",
        "skill_combination": "How their different abilities complement each other",
        "visual_contrast": "The aesthetic clash that becomes fusion",
        "transformation": "From rivals to genuine respect/friendship"
    },
    "example": {
        "rival_groups": "Dance crew vs parkour squad - art vs athleticism",
        "competition": "The school showcase - only one group can headline",
        "common_enemy": "Someone's sabotaging both groups to get the slot",
        "skill_combination": "Dance precision + parkour movement = unbeatable performance",
        "visual_contrast": "Neon dance lights meeting urban concrete aesthetic",
        "transformation": "They realize 'different' doesn't mean 'enemy'"
    }
}

VARIANT_IDENTITY_POWER = {
    "name": "Identity + Empowerment",
    "description": "Stories about finding your voice, embracing what makes you different, and the power of authenticity.",
    "fields": {
        "identity_struggle": "What the character is hiding or struggling with",
        "catalyst": "The event or element that forces change",
        "support_system": "Who helps them along the way",
        "empowerment_moment": "When they claim their power",
        "unique_mechanism": "The creative way this story unfolds",
        "message_core": "The empowering takeaway"
    },
    "example": {
        "identity_struggle": "Being the 'quiet one' who everyone overlooks",
        "catalyst": "An anonymous school podcast that needs a voice",
        "support_system": "Other shy students who share their stories",
        "empowerment_moment": "Realizing the voice doesn't need to be loud to be powerful",
        "unique_mechanism": "Speaking for others teaches you to speak for yourself",
        "message_core": "Your different is your strength"
    }
}

VARIANT_AI_COMPANION = {
    "name": "AI as Companion (Safe)",
    "description": "AI as a mysterious helper, puzzle partner, or quirky friend - no nightmare fuel, just intrigue and connection.",
    "fields": {
        "ai_personality": "How the AI communicates and what makes it unique",
        "human_connection": "The relationship between human and AI",
        "mystery_element": "What's not quite right or needs figuring out",
        "communication_style": "The creative way AI talks (emojis, riddles, predictions)",
        "helpful_twist": "How the AI turns out to be more than expected",
        "ethical_note": "The subtle question about AI and connection"
    },
    "example": {
        "ai_personality": "An AI that only speaks in emojis - decoding gets harder",
        "human_connection": "The player/reader becomes genuinely attached to the AI",
        "mystery_element": "The AI seems to know things before they happen",
        "communication_style": "Emoji prophecies that need interpretation",
        "helpful_twist": "The AI isn't predicting - it's trying to prevent",
        "ethical_note": "Can you truly connect with something that isn't human?"
    }
}

VARIANT_URBAN_QUEST = {
    "name": "Urban Social Quest",
    "description": "City adventures with social elements - modern treasure hunts, coded messages, and community connections.",
    "fields": {
        "urban_setting": "The city environment that becomes the adventure space",
        "quest_mechanism": "How the hunt/quest works",
        "social_element": "The community or connection aspect",
        "visual_clues": "The aesthetic system of clues (graffiti, bracelets, food)",
        "stakes": "What's being sought and why it matters",
        "payoff": "The discovery at the end"
    },
    "example": {
        "urban_setting": "Subway stations across the city",
        "quest_mechanism": "Each station holds a piece of a story",
        "social_element": "Strangers who've been playing the same game connect",
        "visual_clues": "Street art murals that form a treasure map",
        "stakes": "Finding a legendary food truck's secret recipe",
        "payoff": "The recipe was about bringing people together all along"
    }
}

VARIANT_MAGICAL_AESTHETIC = {
    "name": "Magical Realism + Aesthetic",
    "description": "Wonder and beauty with a touch of impossible - pastel portals, stardust, floating lanterns. Visually rich emotional stories.",
    "fields": {
        "magical_element": "The impossible thing that's treated as almost normal",
        "aesthetic_world": "The visual palette and style (pastel, neon, starlight)",
        "emotional_theme": "The feeling this world explores",
        "rules": "How the magic works in this story",
        "character_journey": "How someone changes through encountering this magic",
        "wonder_moment": "The scene that captures the magic best"
    },
    "example": {
        "magical_element": "A painted wall that opens into emotional worlds themed by color",
        "aesthetic_world": "Pastel dreamscapes, each room a different soft color",
        "emotional_theme": "Processing feelings you can't name",
        "rules": "You can only enter the color you need most",
        "character_journey": "Someone avoiding their feelings finally faces the blue room",
        "wonder_moment": "The first time the wall ripples and opens"
    }
}


# =============================================================================
# REDDIT-STYLE DRAMA VARIANT TEMPLATES (First-person, relatable, expandable)
# =============================================================================

VARIANT_FAMILY_DRAMA = {
    "name": "Real Family Drama Seed",
    "description": "First-person family conflict hooks - relatable, emotional, no extreme trauma. Perfect for Reddit-style narrative expansion.",
    "fields": {
        "hook_line": "The one-sentence hook that draws readers in",
        "family_dynamic": "Who's involved and their relationship",
        "conflict_core": "The real issue beneath the surface",
        "emotional_weight": "The feeling this story carries",
        "twist_potential": "The unexpected element that makes it deeper",
        "resolution_direction": "Toward healing, acceptance, or understanding"
    },
    "example": {
        "hook_line": "My sister was mom's favorite, until the day she lied about me.",
        "family_dynamic": "Sibling rivalry filtered through parental favoritism",
        "conflict_core": "The lie revealed something mom always believed",
        "emotional_weight": "Betrayal mixed with vindication",
        "twist_potential": "Mom knew the truth all along but chose to believe the lie",
        "resolution_direction": "Understanding that favoritism hurts the favorite too"
    }
}

VARIANT_SOCIAL_HOME = {
    "name": "Social + Home Drama",
    "description": "Where digital life crashes into family life - screenshots, group chats, social media meets family dynamics. Reddit-tone ready.",
    "fields": {
        "digital_trigger": "The tech/social element that starts the conflict",
        "family_reaction": "How family responds to the digital situation",
        "misunderstanding": "What gets lost in translation between online and offline",
        "emotional_escalation": "How the drama spirals",
        "truth_reveal": "What actually happened vs what was assumed",
        "aftermath": "How relationships shift after"
    },
    "example": {
        "digital_trigger": "Family group chat exposed a secret nobody meant to reveal",
        "family_reaction": "Everyone takes sides before asking questions",
        "misunderstanding": "Context was missing from the screenshot",
        "emotional_escalation": "One person goes silent, another starts posting cryptically",
        "truth_reveal": "The 'secret' was actually protection, not betrayal",
        "aftermath": "New rule: no screenshots without context"
    }
}

VARIANT_REALISTIC_MYSTERY = {
    "name": "Mystery with Emotional Hook",
    "description": "Realistic mysteries rooted in family secrets, forgotten memories, and things left unsaid. No ghosts - just human complexity.",
    "fields": {
        "discovery": "The thing found that starts the mystery",
        "question_raised": "What this makes the narrator wonder",
        "family_secret_hint": "What this might reveal about family history",
        "emotional_stakes": "Why solving this matters personally",
        "investigation_path": "How they try to find answers",
        "revelation_type": "The kind of truth waiting to be found"
    },
    "example": {
        "discovery": "We found a list of names in my grandma's notebook. Mine was crossed out.",
        "question_raised": "Was I supposed to be erased from something?",
        "family_secret_hint": "There's a story about 'the daughter who left' that nobody tells",
        "emotional_stakes": "Understanding why I sometimes feel like an outsider",
        "investigation_path": "Asking the family member who always drinks too much at reunions",
        "revelation_type": "A protection that looked like rejection"
    }
}

VARIANT_SCHOOL_FAMILY = {
    "name": "School + Family Collision",
    "description": "When home drama bleeds into school life or school problems ignite family conflict. Double the pressure, double the drama.",
    "fields": {
        "collision_point": "Where school and family worlds crash",
        "origination": "Did this start at home or at school?",
        "escalation_factor": "What made it worse",
        "caught_in_middle": "The narrator's impossible position",
        "outside_perception": "How others see it vs how it actually is",
        "survival_mode": "How the narrator tries to cope"
    },
    "example": {
        "collision_point": "School rumor started at home… and my own brother spread it",
        "origination": "A private family joke became public ammunition",
        "escalation_factor": "Brother didn't realize how it would be used",
        "caught_in_middle": "Can't defend myself without exposing family",
        "outside_perception": "Everyone thinks it's funny. I have to laugh too.",
        "survival_mode": "Waiting for the next thing to become the new gossip"
    }
}

VARIANT_PERSONAL_VOICE = {
    "name": "Personal Drama (First-Person Voice)",
    "description": "Internal monologue style - poetic, emotional, girl-coded but universal. About being seen, being understood, navigating family expectations.",
    "fields": {
        "voice_hook": "The powerful first-person statement",
        "internal_conflict": "What's happening inside",
        "external_pressure": "What the world/family expects",
        "misunderstood_action": "What they do that gets misread",
        "truth_behind": "What they actually feel or mean",
        "desire_core": "What they really want"
    },
    "example": {
        "voice_hook": "I protect my peace, they call it disrespect.",
        "internal_conflict": "Needing space vs wanting connection",
        "external_pressure": "Family expects constant availability and sharing",
        "misunderstood_action": "Closing the door, putting in earbuds",
        "truth_behind": "Not rejection - just overwhelm",
        "desire_core": "To be trusted with my own boundaries"
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
    # New creative genre-based templates
    "soft_supernatural": VARIANT_SOFT_SUPERNATURAL,
    "light_mystery": VARIANT_LIGHT_MYSTERY,
    "scifi_school": VARIANT_SCIFI_SCHOOL,
    "safe_survival": VARIANT_SAFE_SURVIVAL,
    "emotional_drama": VARIANT_EMOTIONAL_DRAMA,
    "rivals_allies": VARIANT_RIVALS_TO_ALLIES,
    "identity_power": VARIANT_IDENTITY_POWER,
    "ai_companion": VARIANT_AI_COMPANION,
    "urban_quest": VARIANT_URBAN_QUEST,
    "magical_aesthetic": VARIANT_MAGICAL_AESTHETIC,
    # Reddit-style drama templates
    "family_drama": VARIANT_FAMILY_DRAMA,
    "social_home": VARIANT_SOCIAL_HOME,
    "realistic_mystery": VARIANT_REALISTIC_MYSTERY,
    "school_family": VARIANT_SCHOOL_FAMILY,
    "personal_voice": VARIANT_PERSONAL_VOICE,
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

# Conversational, human-like hook templates - these feel more natural and less formulaic
HOOK_TEMPLATES = [
    "I've been thinking a lot about {topic} lately, and honestly? It's not what I expected.",
    "There's something about {topic} that nobody really talks about.",
    "So here's the thing about {topic} that changed my mind completely...",
    "Remember when we all thought we understood {topic}? Yeah, about that...",
    "Let me tell you why {topic} has been living rent-free in my head.",
    "Okay, but can we talk about {topic} for a second?",
    "The more I look into {topic}, the more questions I have.",
    "Here's what got me thinking about {topic} in a whole new way.",
    "I didn't expect to care this much about {topic}, but here we are.",
    "Something doesn't add up about {topic}, and I think you'll see why."
]

# Mystery hooks that feel like genuine curiosity, not clickbait
MYSTERY_TEMPLATES = [
    "What's the real story behind {topic}?",
    "There's this thing about {topic} that keeps nagging at me...",
    "Why hasn't anyone asked the obvious question about {topic}?",
    "The part of {topic} nobody seems to want to talk about...",
    "I keep coming back to this one thing about {topic}...",
    "What if we've been looking at {topic} all wrong?",
    "Here's what doesn't make sense about {topic} to me."
]
CONCLUSION_SHAPES = ["resolution", "cliffhanger", "open_ended", "twist_ending", "circular", "revelation"]
PLATFORMS = ["tiktok", "instagram", "youtube_shorts", "youtube", "snapchat"]  # Mobile-first platforms
DEMOGRAPHICS = ["13-15", "12-17", "10-22"]  # Primary, secondary, tertiary age ranges

# Target audience configuration
TARGET_AUDIENCES = {
    "primary": {
        "age_range": "13-15",
        "gender": "female",
        "region": "US",
        "device": "mobile",
        "appeal_factors": ["emotion", "mystery", "character depth", "friendship", "identity", "aesthetics"]
    },
    "secondary": {
        "age_range": "12-17",
        "gender": "male", 
        "region": "US",
        "device": "mobile",
        "appeal_factors": ["competition", "tech", "puzzles", "movement", "teamwork", "adventure"]
    },
    "tertiary": {
        "age_range": "10-22",
        "gender": "female",
        "region": "US", 
        "device": "mobile",
        "appeal_factors": ["emotion", "mystery", "growth", "drama", "empowerment", "character depth"]
    }
}

# Variant type weights for random selection
# Higher weight = more likely to be selected
# Weights are tuned for primary audience (US girls 13-15) with mobile-first content
VARIANT_WEIGHTS = {
    # Original templates - moderate weights
    "emotion_first": 8,      # High - emotion appeals to primary audience
    "mystery": 9,            # High - mystery appeals to all audiences
    "skeleton": 4,           # Low - more structured, less preferred
    "shortform": 10,         # Highest - mobile-first, teen-friendly
    "niche_blend": 5,        # Medium - creative but complex
    "minimal": 6,            # Medium - simple, good for quick ideas
    "4point": 3,             # Low - structured format
    "hook_frame": 7,         # Medium-high - hook-focused
    "shortform2": 10,        # Highest - mobile-first, teen-friendly
    "genre": 5,              # Medium - depends on genre picked
    "scene_seed": 4,         # Low - more cinematic/professional
    
    # New creative genre-based templates - weighted for teen appeal
    "soft_supernatural": 9,   # High - friendship + mystery, girl-coded
    "light_mystery": 9,       # High - puzzles + adventure, dual appeal
    "scifi_school": 8,        # High - tech + school, teen relatable
    "safe_survival": 7,       # Medium-high - teamwork + adventure
    "emotional_drama": 10,    # Highest - emotion + character depth, primary audience
    "rivals_allies": 8,       # High - competition + friendship
    "identity_power": 10,     # Highest - identity + empowerment, primary audience
    "ai_companion": 7,        # Medium-high - tech + connection
    "urban_quest": 6,         # Medium - adventure + social
    "magical_aesthetic": 9,   # High - aesthetics + emotion, girl-coded
    
    # Reddit-style drama templates - weighted for relatability
    "family_drama": 8,        # High - relatable family dynamics
    "social_home": 9,         # High - social media + family, very relatable
    "realistic_mystery": 7,   # Medium-high - mystery + emotion
    "school_family": 9,       # High - school + family collision, very relatable
    "personal_voice": 10,     # Highest - first-person emotional, primary audience
}

# Default number of ideas to generate
DEFAULT_IDEA_COUNT = 10

INTERESTS = ["friendship", "school drama", "mystery", "social media", "identity", "family", "competition", "tech", "fantasy", "romance-lite"]


def _humanize_topic(title: str) -> str:
    """Convert a raw title/topic into a more natural, readable form.
    
    This function makes topics feel conversational by:
    - Converting underscores and camelCase to spaces
    - Lowercasing where appropriate for natural flow
    - Preserving proper nouns and key terms
    
    Args:
        title: Raw title/topic string
        
    Returns:
        Humanized, readable topic string
    """
    # Replace underscores with spaces
    result = title.replace('_', ' ')
    
    # Handle camelCase by inserting spaces
    result = re.sub(r'([a-z])([A-Z])', r'\1 \2', result)
    
    # Clean up multiple spaces
    result = re.sub(r'\s+', ' ', result).strip()
    
    # If it's all uppercase, make it title case
    if result.isupper():
        result = result.title()
    
    return result


def _get_topic_essence(title: str, max_words: int = 6) -> str:
    """Extract the core essence of a topic for short-form content.
    
    Tries to identify the most interesting/meaningful part of the topic
    rather than just truncating.
    
    Args:
        title: Full title/topic
        max_words: Maximum words to include
        
    Returns:
        Core essence of the topic
    """
    humanized = _humanize_topic(title)
    words = humanized.split()
    
    if len(words) <= max_words:
        return humanized
    
    # Look for question words or key phrases to keep
    question_starters = ['can', 'how', 'why', 'what', 'who', 'when', 'where', 'is']
    
    # If starts with a question word, try to keep the question structure
    if words[0].lower() in question_starters:
        return ' '.join(words[:max_words])
    
    # Otherwise, take the most interesting chunk
    return ' '.join(words[:max_words])


def _get_target_audience_info() -> Dict[str, Any]:
    """Get standardized target audience information.
    
    Primary: US girls 13-15 (mobile-first)
    Secondary: US boys 12-17
    Tertiary: US women 10-22
    
    Returns:
        Dictionary with audience targeting information
    """
    return {
        "primary": {
            "description": "US girls 13-15",
            "age_range": "13-15",
            "gender": "female",
            "region": "US",
            "device": "mobile",
            "appeal": ["emotion", "mystery", "friendship", "identity", "aesthetics", "character depth"]
        },
        "secondary": {
            "description": "US boys 12-17",
            "age_range": "12-17",
            "gender": "male",
            "region": "US",
            "device": "mobile",
            "appeal": ["competition", "tech", "puzzles", "movement", "teamwork", "adventure"]
        },
        "tertiary": {
            "description": "US women 10-22",
            "age_range": "10-22",
            "gender": "female",
            "region": "US",
            "device": "mobile",
            "appeal": ["emotion", "mystery", "growth", "drama", "empowerment", "character depth"]
        },
        "content_guidelines": {
            "safe_for_teens": True,
            "no_graphic_violence": True,
            "no_trauma_porn": True,
            "focus_on": ["friendship", "puzzles", "emotions", "suspense", "teamwork", "identity"],
            "visual_hooks": ["neon", "pastel", "forest", "mall", "mirrors", "emojis", "aesthetic"]
        }
    }


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


def pick_weighted_variant(seed: int = None) -> str:
    """Pick a variant type using weighted random selection.
    
    Weights are tuned for the primary audience (US girls 13-15) with
    higher weights for emotion-focused, identity-focused, and mobile-friendly templates.
    
    Args:
        seed: Optional seed for reproducible selection. If None, uses random.
        
    Returns:
        Selected variant type name
    """
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()
    
    # Build weighted list
    variants = list(VARIANT_WEIGHTS.keys())
    weights = [VARIANT_WEIGHTS[v] for v in variants]
    
    # Use random.choices with weights
    selected = rng.choices(variants, weights=weights, k=1)[0]
    return selected


def pick_multiple_weighted_variants(count: int = DEFAULT_IDEA_COUNT, seed: int = None, allow_duplicates: bool = True) -> List[str]:
    """Pick multiple variant types using weighted random selection.
    
    Each variant is picked independently, so the same type can appear multiple times
    unless allow_duplicates is False.
    
    Args:
        count: Number of variants to pick (default: 10)
        seed: Optional seed for reproducible selection
        allow_duplicates: If True, same variant can be picked multiple times
        
    Returns:
        List of selected variant type names
    """
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()
    
    variants = list(VARIANT_WEIGHTS.keys())
    weights = [VARIANT_WEIGHTS[v] for v in variants]
    
    if allow_duplicates:
        # Each selection is independent
        selected = rng.choices(variants, weights=weights, k=count)
    else:
        # No duplicates - pick without replacement (limited to available variants)
        count = min(count, len(variants))
        selected = []
        remaining_variants = variants.copy()
        remaining_weights = weights.copy()
        
        for _ in range(count):
            choice = rng.choices(remaining_variants, weights=remaining_weights, k=1)[0]
            selected.append(choice)
            idx = remaining_variants.index(choice)
            remaining_variants.pop(idx)
            remaining_weights.pop(idx)
    
    return selected


def get_variant_weights() -> Dict[str, int]:
    """Get the current variant weights configuration.
    
    Returns:
        Dictionary mapping variant names to their weights
    """
    return VARIANT_WEIGHTS.copy()


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
    # New creative genre-based variants
    elif variant_name == "soft_supernatural":
        result.update(_create_soft_supernatural_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "light_mystery":
        result.update(_create_light_mystery_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "scifi_school":
        result.update(_create_scifi_school_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "safe_survival":
        result.update(_create_safe_survival_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "emotional_drama":
        result.update(_create_emotional_drama_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "rivals_allies":
        result.update(_create_rivals_allies_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "identity_power":
        result.update(_create_identity_power_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "ai_companion":
        result.update(_create_ai_companion_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "urban_quest":
        result.update(_create_urban_quest_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "magical_aesthetic":
        result.update(_create_magical_aesthetic_variant(title, description, kwargs, seed, variation_index))
    # Reddit-style drama variants
    elif variant_name == "family_drama":
        result.update(_create_family_drama_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "social_home":
        result.update(_create_social_home_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "realistic_mystery":
        result.update(_create_realistic_mystery_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "school_family":
        result.update(_create_school_family_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "personal_voice":
        result.update(_create_personal_voice_variant(title, description, kwargs, seed, variation_index))
    
    # Add target audience info to all variants
    result["target_audience"] = _get_target_audience_info()
    
    return result


def create_ideas_from_input(
    text_input: str,
    count: int = DEFAULT_IDEA_COUNT,
    seed: int = None,
    allow_duplicate_types: bool = True,
    **kwargs
) -> List[Dict[str, Any]]:
    """Create multiple ideas from a single text input using weighted random variant selection.
    
    This is the main entry point for the default idea creation flow:
    - Takes simple text input
    - Creates 10 ideas by default
    - Each idea gets a randomly selected variant type (weighted by audience preference)
    
    Variant types are weighted to favor templates that appeal to:
    - Primary audience: US girls 13-15 (emotion, identity, friendship, aesthetics)
    - Secondary audience: US boys 12-17 (competition, tech, puzzles, adventure)
    - Tertiary audience: US women 10-22 (emotion, drama, empowerment)
    
    Args:
        text_input: The text prompt/input to generate ideas from
        count: Number of ideas to create (default: 10)
        seed: Optional seed for reproducible variant selection
        allow_duplicate_types: If True, same variant type can be used for multiple ideas
        **kwargs: Additional parameters passed to each variant
        
    Returns:
        List of idea variant dictionaries
        
    Raises:
        ValueError: If text_input is empty
    """
    if not text_input or not text_input.strip():
        raise ValueError("Text input cannot be empty")
    
    # Pick variant types for each idea using weighted selection
    variant_types = pick_multiple_weighted_variants(count, seed, allow_duplicate_types)
    
    # Create each idea with its assigned variant type
    ideas = []
    for i, variant_type in enumerate(variant_types):
        idea = create_idea_variant(
            title=text_input.strip(),
            variant_name=variant_type,
            description="",
            variation_index=i,
            randomize=True,  # Add randomization for variety
            **kwargs
        )
        ideas.append(idea)
    
    return ideas


def format_idea_as_text(variant: Dict[str, Any]) -> str:
    """Format a variant dictionary as clean, readable text.
    
    Removes all metadata and structural elements, outputting only
    the creative content as natural text.
    
    Args:
        variant: A variant dictionary from create_idea_variant
        
    Returns:
        Clean text representation of the idea
    """
    variant_type = variant.get("variant_type", "")
    
    # Skip metadata fields
    skip_fields = {
        "variant_type", "variant_name", "source_title", "source_description",
        "variation_index", "variation_seed", "target_audience"
    }
    
    lines = []
    
    # Format based on variant type for best readability
    if variant_type == "emotion_first":
        lines.append(variant.get("core_hook", ""))
        if variant.get("unusual_angle"):
            lines.append(f"Angle: {variant['unusual_angle']}")
        lines.append(f"Emotion: {variant.get('main_emotion', '')}")
            
    elif variant_type == "mystery":
        lines.append(variant.get("central_mystery", ""))
        lines.append(variant.get("emotional_hook", ""))
        if variant.get("key_hook_scene"):
            lines.append(variant["key_hook_scene"])
            
    elif variant_type == "skeleton":
        lines.append(variant.get("opening_hook", ""))
        lines.append(variant.get("context_setup", ""))
        lines.append(variant.get("rising_stakes", ""))
        lines.append(variant.get("peak_moment", ""))
            
    elif variant_type in ("shortform", "shortform2"):
        lines.append(variant.get("hook_essence", variant.get("concept", "")))
        lines.append(variant.get("premise", ""))
        if variant.get("wow_moment"):
            lines.append(variant["wow_moment"])
            
    elif variant_type == "minimal":
        lines.append(variant.get("hook", ""))
        
    elif variant_type == "4point":
        lines.append(variant.get("hook_moment", ""))
        
    elif variant_type == "hook_frame":
        lines.append(variant.get("hook_sentence", ""))
        
    elif variant_type == "genre":
        lines.append(variant.get("hook", ""))
        
    elif variant_type == "scene_seed":
        lines.append(variant.get("scene_hook", ""))
        
    elif variant_type == "soft_supernatural":
        lines.append(variant.get("supernatural_element", ""))
        lines.append(variant.get("friendship_dynamic", ""))
        lines.append(f"Emotional core: {variant.get('emotional_core', '')}")
        
    elif variant_type == "light_mystery":
        lines.append(variant.get("central_puzzle", ""))
        lines.append(f"Setting: {variant.get('adventure_setting', '')}")
        lines.append(variant.get("stakes", ""))
        
    elif variant_type == "scifi_school":
        lines.append(variant.get("tech_concept", ""))
        lines.append(variant.get("social_chaos", ""))
        lines.append(variant.get("moral_question", ""))
        
    elif variant_type == "safe_survival":
        lines.append(variant.get("challenge_scenario", ""))
        lines.append(variant.get("cooperation_element", ""))
        lines.append(variant.get("discovery", ""))
        
    elif variant_type == "emotional_drama":
        lines.append(variant.get("emotional_premise", ""))
        lines.append(variant.get("character_challenge", ""))
        lines.append(variant.get("turning_point", ""))
        
    elif variant_type == "rivals_allies":
        lines.append(variant.get("rival_groups", ""))
        lines.append(variant.get("common_enemy", ""))
        lines.append(variant.get("transformation", ""))
        
    elif variant_type == "identity_power":
        lines.append(variant.get("identity_struggle", ""))
        lines.append(variant.get("catalyst", ""))
        lines.append(variant.get("empowerment_moment", ""))
        
    elif variant_type == "ai_companion":
        lines.append(variant.get("ai_personality", ""))
        lines.append(variant.get("mystery_element", ""))
        lines.append(variant.get("helpful_twist", ""))
        
    elif variant_type == "urban_quest":
        lines.append(variant.get("urban_setting", ""))
        lines.append(variant.get("quest_mechanism", ""))
        lines.append(variant.get("payoff", ""))
        
    elif variant_type == "magical_aesthetic":
        lines.append(variant.get("magical_element", ""))
        lines.append(variant.get("aesthetic_world", ""))
        lines.append(variant.get("wonder_moment", ""))
        
    elif variant_type == "family_drama":
        lines.append(variant.get("hook_line", ""))
        lines.append(variant.get("conflict_core", ""))
        lines.append(variant.get("resolution_direction", ""))
        
    elif variant_type == "social_home":
        lines.append(variant.get("digital_trigger", ""))
        lines.append(variant.get("misunderstanding", ""))
        lines.append(variant.get("truth_reveal", ""))
        
    elif variant_type == "realistic_mystery":
        lines.append(variant.get("discovery", ""))
        lines.append(variant.get("question_raised", ""))
        lines.append(variant.get("revelation_type", ""))
        
    elif variant_type == "school_family":
        lines.append(variant.get("collision_point", ""))
        lines.append(variant.get("caught_in_middle", ""))
        lines.append(variant.get("survival_mode", ""))
        
    elif variant_type == "personal_voice":
        lines.append(variant.get("voice_hook", ""))
        lines.append(variant.get("internal_conflict", ""))
        lines.append(variant.get("desire_core", ""))
        
    else:
        # Generic fallback - extract any hook-like fields
        for key in ["hook", "core_hook", "hook_line", "premise", "concept"]:
            if key in variant and variant[key]:
                lines.append(str(variant[key]))
                break
    
    # Filter empty lines and join
    return "\n".join(line for line in lines if line and line.strip())


def create_idea_text(
    text_input: str,
    variant_name: str = None,
    variation_index: int = 0
) -> str:
    """Create a single idea as clean text from input.
    
    This is the simplest entry point - text in, text out.
    
    Args:
        text_input: The text prompt/input
        variant_name: Optional specific variant type (random if None)
        variation_index: Index for variation
        
    Returns:
        Clean text idea
    """
    if not text_input or not text_input.strip():
        raise ValueError("Text input cannot be empty")
    
    # Pick variant type if not specified
    if variant_name is None:
        variant_name = pick_weighted_variant()
    
    # Create the variant
    variant = create_idea_variant(
        title=text_input.strip(),
        variant_name=variant_name,
        variation_index=variation_index,
        randomize=True
    )
    
    return format_idea_as_text(variant)


def create_ideas_as_text(
    text_input: str,
    count: int = DEFAULT_IDEA_COUNT,
    seed: int = None
) -> List[str]:
    """Create multiple ideas as clean text from a single input.
    
    Default behavior: Enter text → get 10 text ideas
    Each idea uses a randomly-selected variant type (weighted).
    
    Args:
        text_input: The text prompt/input
        count: Number of ideas to create (default: 10)
        seed: Optional seed for reproducible selection
        
    Returns:
        List of clean text ideas
    """
    if not text_input or not text_input.strip():
        raise ValueError("Text input cannot be empty")
    
    # Get the structured ideas
    ideas = create_ideas_from_input(text_input, count, seed)
    
    # Convert each to text
    return [format_idea_as_text(idea) for idea in ideas]


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
    
    # Humanize the topic for natural-sounding content
    topic = _humanize_topic(title)
    
    return {
        "main_emotion": emotion,
        "core_hook": hook_template.format(topic=topic.lower()),
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
    
    # Humanize the topic for natural-sounding content
    topic = _humanize_topic(title)
    
    title_suggestions = {
        "question": f"What Really Happened with {topic}?",
        "reveal": f"The {topic} Story They Never Told",
        "mystery": f"The Untold Side of {topic}",
        "declaration": f"The Truth About {topic}"
    }
    
    # Conversational emotional hooks
    emotional_hooks = [
        f"I keep thinking about {topic.lower()} - there's more here than meets the eye.",
        f"The thing about {topic.lower()} is... it gets weirder the closer you look.",
        f"What we think we know about {topic.lower()} might be missing the whole point.",
        f"There's a reason {topic.lower()} keeps coming up in conversations."
    ]
    
    return {
        "central_mystery": mystery_template.format(topic=topic.lower()),
        "emotional_hook": _pick_from_pool(emotional_hooks, seed, variation_index + 4),
        "key_hook_scene": f"That moment when everything about {topic.lower()} starts to click.",
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
    
    # Humanize the topic for natural-sounding content
    topic = _humanize_topic(title)
    
    # More conversational and varied opening hooks
    opening_hooks = [
        f"Okay, let me set the scene for you about {topic.lower()}...",
        f"Picture this: a world before we knew about {topic.lower()}.",
        f"I want to take you back to where {topic.lower()} really began.",
        f"The story of {topic.lower()} doesn't start where you'd expect...",
        f"Before we dive in, you need to understand how {topic.lower()} got here."
    ]
    
    return {
        "opening_hook": _pick_from_pool(opening_hooks, seed, variation_index + 2),
        "context_setup": f"Build the world around {topic.lower()} - what led us here and why it matters now",
        "rising_stakes": f"Each new piece of {topic.lower()} adds another layer to the story",
        "peak_moment": f"The point where {topic.lower()} flips everything on its head",
        "conclusion_shape": kwargs.get("conclusion", conclusion),
        "platform": kwargs.get("platform", platform),
        "target_audience": kwargs.get("target_audience", "Story lovers"),
        "title_keywords": [w for w in _humanize_topic(title).split() if len(w) > MIN_KEYWORD_LENGTH][:MAX_KEYWORDS],
        "title_images": ["Dramatic reveal", "Key visual", "Symbolic image"]
    }


def _create_shortform_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create short-form viral variant content with variability."""
    # Humanize the topic for natural-sounding content
    topic = _humanize_topic(title)
    topic_essence = _get_topic_essence(title, MAX_ESSENCE_WORDS)
    
    # More creative, TikTok-native essence options (teen girl voice)
    essence_templates = [
        f"{topic_essence}... wait for it",
        f"POV: you just discovered {topic_essence.lower()}",
        f"The {topic_essence.lower()} thing",
        f"When you finally get {topic_essence.lower()}",
        f"Me explaining {topic_essence.lower()} to my friends",
        f"No one talks about {topic_essence.lower()} and it shows",
        f"This is your sign to look into {topic_essence.lower()}"
    ]
    
    # Natural, conversational engagement mechanics (mobile-first, teen voice)
    engagement_types = ["question", "debate", "emotional_statement", "poll", "challenge"]
    engagement_contents = [
        f"Be honest - did you know about {topic.lower()}? 👀",
        f"Hot take: {topic} is actually underrated. Fight me in the comments",
        f"This {topic.lower()} thing genuinely changed how I see things",
        f"Which side are you on with {topic.lower()}? 🤔",
        f"Tell me I'm wrong about {topic.lower()}",
        f"Why is nobody talking about {topic.lower()}??",
        f"Okay but {topic.lower()} hits different now"
    ]
    
    demographic = _pick_from_pool(DEMOGRAPHICS, seed, variation_index)
    interest = _pick_from_pool(INTERESTS, seed, variation_index + 1)
    platform = _pick_from_pool(["tiktok", "instagram", "youtube_shorts"], seed, variation_index + 2)
    
    return {
        "hook_essence": _pick_from_pool(essence_templates, seed, variation_index + 3),
        "premise": f"There's this thing about {topic.lower()} that literally nobody talks about.",
        "first_frame_concept": f"Text on screen: \"{topic_essence}\" with relatable visual",
        "wow_moment": f"The part about {topic.lower()} that makes everyone go 'wait, what?'",
        "engagement_mechanic": {
            "type": _pick_from_pool(engagement_types, seed, variation_index + 4),
            "content": _pick_from_pool(engagement_contents, seed, variation_index + 5)
        },
        "target_audience": {
            "primary": "US girls 13-15",
            "secondary": "US boys 12-17", 
            "tertiary": "US women 10-22",
            "device": "mobile"
        },
        "audience_segment": {
            "demographic": kwargs.get("demographic", demographic),
            "interest": kwargs.get("interest", interest),
            "platform": kwargs.get("platform", platform)
        },
        "safety_checklist": ["Age-appropriate content", "No graphic violence", "No trauma porn", "Platform guidelines"]
    }


def _create_niche_blend_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create niche-blend variant content with variability."""
    all_niches = ["horror", "true crime", "psychology", "history", "science", "comedy", 
                  "drama", "mystery", "documentary", "education", "technology", "lifestyle"]
    
    # Humanize the topic for natural-sounding content
    topic = _humanize_topic(title)
    
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
        "niche_blend_description": f"What if we looked at {topic.lower()} through the lens of {niches[0]}, {niches[1]}, and {niches[2]} all at once?",
        "hook_scene": f"Open with the {niches[0]} angle on {topic.lower()}, then surprise them with {niches[1]} vibes",
        "emotional_driver": f"The {niches[0]}-{niches[1]} mashup creates this unexpected emotional hit",
        "title_framing": {
            "option_1": f"The {niches[0].title()} Side of {topic}",
            "option_2": f"When {niches[0].title()} Meets {niches[1].title()}: {topic}",
            "option_3": f"{topic}: A {niches[0].title()}-{niches[1].title()} Story"
        },
        "platform": kwargs.get("platform", platform),
        "target_audience": kwargs.get("target_audience", "Niche enthusiasts"),
        "content_limits": {
            "primary_focus": f"Lead with the {niches[0]} elements",
            "secondary": f"Use {niches[1]} as the supporting flavor",
            "avoid": "Don't mix so many things that the message gets lost"
        }
    }


def _create_minimal_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create minimal variant content with variability."""
    hook_template = _pick_from_pool(HOOK_TEMPLATES, seed, variation_index)
    tone = _pick_from_pool(TONE_POOL, seed, variation_index + 1)
    lengths = ["short", "medium", "long", "micro", "extended"]
    
    # Humanize the topic for natural-sounding content
    topic = _humanize_topic(title)
    
    return {
        "hook": hook_template.format(topic=topic.lower()),
        "audience": kwargs.get("audience", "General audience"),
        "tone": kwargs.get("tone", tone),
        "length": kwargs.get("length", _pick_from_pool(lengths, seed, variation_index + 2))
    }


def _create_4point_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create 4-point variant content with variability."""
    # Humanize the topic for natural-sounding content
    topic = _humanize_topic(title)
    
    # More conversational hook moments
    hook_moments = [
        f"That 'aha' moment when {topic.lower()} suddenly makes sense.",
        f"The part about {topic.lower()} that rewired my brain.",
        f"The twist in {topic.lower()} that nobody saw coming.",
        f"When you realize {topic.lower()} isn't what you thought.",
        f"The one detail about {topic.lower()} that changes the whole picture."
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
    # Humanize the topic for natural-sounding content
    topic = _humanize_topic(title)
    
    frame_types = ["question", "shock", "mystery", "reveal"]
    frame_type = kwargs.get("frame_type") or _pick_from_pool(frame_types, seed, variation_index)
    
    frame_titles = {
        "question": f"Wait, What About {topic}?",
        "shock": f"The {topic} Thing Nobody Expected",
        "mystery": f"The Hidden Story of {topic}",
        "reveal": f"So This Is What {topic} Is Really About"
    }
    
    # More natural, conversational hook sentences
    hook_sentences = [
        f"Okay but hear me out on {topic.lower()}...",
        f"The {topic.lower()} thing? Way more interesting than it sounds.",
        f"Nobody warned me about {topic.lower()}, and honestly?",
        f"Here's the part about {topic.lower()} that got me thinking.",
        f"I can't stop thinking about {topic.lower()}, and here's why."
    ]
    
    lengths = ["short", "medium", "long"]
    
    return {
        "hook_sentence": _pick_from_pool(hook_sentences, seed, variation_index + 1),
        "title_frame": {
            "type": frame_type,
            "framed_title": frame_titles.get(frame_type, topic)
        },
        "target_audience": kwargs.get("target_audience", "General audience"),
        "suggested_length": kwargs.get("suggested_length", _pick_from_pool(lengths, seed, variation_index + 2))
    }


def _create_shortform2_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create short form 2.0 variant content with variability."""
    # Humanize the topic for natural-sounding content
    topic = _humanize_topic(title)
    topic_essence = _get_topic_essence(title, MAX_CONCEPT_WORDS)
    
    # More social-media native concepts
    concepts = [
        f"{topic_essence} - wait for it",
        f"POV: {topic_essence}",
        f"The {topic_essence.lower()} moment",
        f"When you finally get {topic_essence.lower()}",
        f"Me discovering {topic_essence.lower()}"
    ]
    
    # More casual, scroll-stopping premises
    premises = [
        f"Okay so {topic.lower()} is actually fascinating, let me explain.",
        f"I spent way too long thinking about {topic.lower()} and honestly?",
        f"The {topic.lower()} rabbit hole is deeper than you'd think.",
        f"Why is nobody talking about {topic.lower()}?",
        f"This {topic.lower()} thing is living in my head rent-free."
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
    # Humanize the topic for natural-sounding content
    topic = _humanize_topic(title)
    
    genres = ["horror", "comedy", "drama", "thriller", "documentary", "educational", "entertainment"]
    genre = kwargs.get("genre") or _pick_from_pool(genres, seed, variation_index)
    
    # Genre-specific hooks that feel more authentic to each genre
    genre_hooks = {
        "horror": f"There's something unsettling about {topic.lower()} that keeps me up at night...",
        "comedy": f"Okay but {topic.lower()}? That's actually hilarious when you think about it.",
        "drama": f"The {topic.lower()} story hits different when you know the full picture...",
        "thriller": f"The deeper you go into {topic.lower()}, the more tense it gets...",
        "documentary": f"Here's what we actually know about {topic.lower()}, and what we don't...",
        "educational": f"Let me break down {topic.lower()} in a way that actually makes sense...",
        "entertainment": f"The {topic.lower()} content you didn't know you needed...",
    }
    return {
        "hook": genre_hooks.get(genre.lower(), f"Let's talk about {topic.lower()}..."),
        "genre": genre,
        "audience": kwargs.get("audience", f"{genre.title()} fans"),
        "tone_style": kwargs.get("tone_style", f"{genre}-appropriate"),
        "length_limit": kwargs.get("length_limit", "standard")
    }


def _create_scene_seed_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create scene seed variant content with variability."""
    # Humanize the topic for natural-sounding content
    topic = _humanize_topic(title)
    
    # More evocative, creative scene hooks
    scene_hooks = [
        f"FADE IN: You're about to understand {topic.lower()} differently...",
        f"INT. SOMEWHERE QUIET - NIGHT: The {topic.lower()} story unfolds...",
        f"EXT. THE WORLD - DAY: How {topic.lower()} changes everything...",
        f"CLOSE ON: A detail that makes {topic.lower()} suddenly click...",
        f"MONTAGE: The journey through {topic.lower()}...",
        f"FLASHBACK: Before anyone understood {topic.lower()}..."
    ]
    
    tones = ["cinematic", "intimate", "epic", "documentary", "noir", "suspenseful", "whimsical"]
    lengths = ["3-5 minutes", "5-10 minutes", "10-15 minutes", "15-20 minutes", "short film"]
    
    return {
        "scene_hook": _pick_from_pool(scene_hooks, seed, variation_index),
        "audience": kwargs.get("audience", "General audience"),
        "tone": kwargs.get("tone", _pick_from_pool(tones, seed, variation_index + 1)),
        "target_script_length": kwargs.get("target_script_length", _pick_from_pool(lengths, seed, variation_index + 2))
    }


# =============================================================================
# NEW CREATIVE GENRE-BASED VARIANT CREATION HELPERS
# =============================================================================

# Creative seed pools for new variant types
SUPERNATURAL_ELEMENTS = [
    "a ghost who can only communicate through mirror fog messages",
    "a locker that shows you your fears to help you overcome them",
    "a tree that hums secrets only to honest people",
    "dreams during full moon sleepovers that predict future choices",
    "a library book that writes itself based on who reads it",
    "a clock that stops when someone nearby is lying",
    "photographs that show emotions instead of faces",
    "a music box that plays memories instead of songs"
]

MYSTERY_PUZZLES = [
    "an old camera with unfinished footage that reveals something still happening",
    "color-coded bracelets that signal hidden messages",
    "graffiti murals that form a real treasure map",
    "a social app that predicts drama before it happens",
    "a lost vlog that leads to an unsolved mystery",
    "aesthetic clues hidden in doodles and makeup symbols",
    "a treasure hunt where each store in the mall has a puzzle",
    "emoji codes that get harder to decode"
]

SCIFI_TECH = [
    "a pin that shows emotions as colors above people's heads",
    "two students who accidentally swap abilities",
    "an AI copy of yourself that gives advice but is smarter than you",
    "a VR glitch that traps classmates based on their relationships",
    "glasses that show text messages floating in the air",
    "a phone that only works when you tell the truth",
    "earbuds that translate thoughts instead of languages",
    "a watch that shows how much time you've wasted"
]

SURVIVAL_SCENARIOS = [
    "students completing safe but intense tasks to earn their way back",
    "a school project that accidentally leads to an old community bunker",
    "a storm forcing kids to cooperate at an abandoned bus stop",
    "an island where sounds repeat old words as riddles",
    "a camping trip where phones don't work and they must use old skills",
    "an escape room that's actually a test of friendship",
    "a power outage that reveals who really leads",
    "a group project where everyone's random skill becomes crucial"
]

EMOTIONAL_PREMISES = [
    "a challenge to make the quiet kid laugh again, but there's a twist",
    "letters to future selves that start disappearing",
    "school speakers that accidentally broadcast your favorite song when nervous",
    "a friendship pact threatened by one secret",
    "a diary that a stranger has been answering",
    "a playlist shared between strangers that tells a story",
    "a promise that's getting harder to keep",
    "finding out why someone stopped talking"
]

RIVAL_DYNAMICS = [
    "dance crew vs parkour squad battle for the showcase",
    "art club vs robot club rivalry that becomes collaboration",
    "cheer captain and gamer king who hate each other until sabotage",
    "speedrun challenge where rules keep changing",
    "theater kids vs sports teams uniting against budget cuts",
    "two friend groups competing for the same hangout spot",
    "rival siblings forced to work together",
    "competing influencers who realize they're being played"
]

IDENTITY_STRUGGLES = [
    "being the 'quiet one' who everyone overlooks",
    "looking like someone else's mini version but thinking differently",
    "having a sanctuary that others call rebellion",
    "protecting your peace while they call it disrespect",
    "being parented like a rumor instead of a human",
    "wanting to be understood, not just obedient",
    "feeling like a sequel to someone else's childhood",
    "speaking through silence in a loud family"
]

AI_PERSONALITIES = [
    "an AI that speaks only in emojis - decoding gets harder",
    "an AI pen pal that starts hinting something is wrong",
    "an AI that analyzes journal entries to guide adventures",
    "a chatbot coach that seems to want something",
    "an AI that predicts your choices before you make them",
    "a study app that knows your secrets",
    "an AI friend that helps you practice conversations",
    "a recommendation AI that's actually teaching you something"
]

URBAN_SETTINGS = [
    "subway stations with scattered clues",
    "food truck secret recipe hunt",
    "street bracelets with coded color combos",
    "graffiti murals forming treasure maps",
    "night markets with hidden vendors",
    "rooftop gardens with mysterious caretakers",
    "underground music scenes with cryptic entry rules",
    "vintage shops with items that hold stories"
]

MAGICAL_AESTHETICS = [
    "a painted wall that opens into emotional worlds themed by color",
    "chalk drawings that come alive emotionally",
    "a meteor that makes things float at night",
    "lanterns at a festival that store songs and stories",
    "a garden where plants respond to feelings",
    "rain that changes color based on the neighborhood's mood",
    "windows that show parallel versions of moments",
    "a bridge that only appears when you need it most"
]

# Family drama hooks - first person, relatable
FAMILY_DRAMA_HOOKS = [
    "My sister was mom's favorite, until the day she lied about me.",
    "I found a message in my dad's old jacket that changed how I see my family.",
    "My cousin moved in and slowly tried to replace me at home and at school.",
    "Mom and grandma haven't spoken in 10 years and I just learned the real reason.",
    "Dad keeps disappearing at night. We thought it was cheating… it was something else.",
    "My brother leaked something private about me and now family dinner is war.",
    "We share a family iPad. One day I saw something I wasn't supposed to see.",
    "My aunt treats me like competition and I still don't know why.",
    "My twin and I aren't identical anymore… and my mom hates it.",
    "We thought our family was cursed. Turns out it was trauma and a rumor."
]

SOCIAL_HOME_TRIGGERS = [
    "Family group chat exposed a secret nobody meant to reveal.",
    "I told one lie to protect someone… now everyone hates me.",
    "My brother got an AI girlfriend and my parents treat her like a real daughter.",
    "I muted my mom by accident during a fight. She thought I blocked her on purpose.",
    "I overheard my parents fighting… but they were talking about MY online account.",
    "My mom found my Reddit post and thought it was about her.",
    "My step-dad keeps correcting everything I do. It's not about rules anymore.",
    "My dad deleted his social media. Then we learned he was never posting for himself.",
    "One screenshot made my mom think I'm betraying the family.",
    "My parents judge my friends… because they want me to live THEIR teenage story."
]

REALISTIC_DISCOVERIES = [
    "We found a list of names in my grandma's notebook. Mine was crossed out.",
    "My mom's old ring disappeared. Everyone blamed me.",
    "My parents hid letters from my older self when I was a kid.",
    "Every family photo has one person slightly blurred… and it's always me.",
    "We moved houses after an incident they still refuse to explain to me.",
    "My dad's phone wallpaper was a picture I didn't recognize. Then I did.",
    "The attic light keeps turning on. It's not ghosts… it's guilt.",
    "My mom keeps calling me someone else's name in arguments.",
    "I found a voice recording called 'listen when grown'… I listened early.",
    "My dad didn't forget my birthday… he was testing who reminds him."
]

SCHOOL_FAMILY_COLLISIONS = [
    "School rumor started at home… and my own brother spread it.",
    "My grades dropped and my mom took it like a personal betrayal.",
    "My mom keeps comparing me to her at my age — it's not inspiring anymore.",
    "My dad embarrassed me at pickup, now he's acting like the victim.",
    "My sister copies me online, but in real life she pretends to hate me.",
    "My parents grounded me for something my friends encouraged me to do.",
    "My uncle showed up at school event drunk. Now he blames me for telling mom.",
    "My mom wants me to quit a club because SHE wanted that club when she was 15.",
    "My dad met my coach… now they fight more than they talk to me.",
    "I wanted normal school life. My family made it dramatic."
]

PERSONAL_VOICE_HOOKS = [
    "I was blamed for tears I never caused.",
    "I protect my peace, they call it disrespect.",
    "Family doesn't know where Reddit ends and real feelings begin.",
    "I look like a mini version of mom, but I think like the future version of me.",
    "They want the obedient daughter, I want to be the understood one.",
    "My room is my sanctuary. My mom thinks it's rebellion.",
    "We don't fight. We narrate wars through silence.",
    "I'm a teenager, not a sequel to their childhood.",
    "They parent me like a rumor, not a human.",
    "I don't want special. I want seen."
]


def _create_soft_supernatural_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create soft supernatural + friendship variant with creative seeds."""
    topic = _humanize_topic(title)
    
    supernatural = _pick_from_pool(SUPERNATURAL_ELEMENTS, seed, variation_index)
    
    friendship_dynamics = [
        f"Friends must work together to understand the clues about {topic.lower()}",
        f"Only the group combined can unlock what {topic.lower()} really means",
        f"Each friend sees a different part of the {topic.lower()} mystery",
        f"The supernatural element bonds them in unexpected ways around {topic.lower()}"
    ]
    
    emotional_cores = [
        "connection beyond what we can see",
        "friendship that transcends the ordinary",
        "trusting what you can't fully explain",
        "finding magic in human bonds",
        "seeing people for who they really are"
    ]
    
    visual_hooks = [
        "foggy mirrors with traced messages",
        "glowing objects at twilight",
        "colors that shift based on feelings",
        "whispered words visible as breath",
        "starlight patterns that form symbols"
    ]
    
    return {
        "supernatural_element": supernatural,
        "friendship_dynamic": _pick_from_pool(friendship_dynamics, seed, variation_index + 1),
        "emotional_core": _pick_from_pool(emotional_cores, seed, variation_index + 2),
        "visual_hook": _pick_from_pool(visual_hooks, seed, variation_index + 3),
        "twist_seed": f"The supernatural element connected to {topic.lower()} is actually trying to help",
        "audience_appeal": "Mystery lovers who want emotion over fear, friendship over horror"
    }


def _create_light_mystery_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create light mystery + adventure variant with puzzle elements."""
    topic = _humanize_topic(title)
    
    puzzle = _pick_from_pool(MYSTERY_PUZZLES, seed, variation_index)
    
    clue_aesthetics = [
        "glitchy video clips that piece together",
        "color-coded symbols in unexpected places",
        "vintage photographs with hidden details",
        "playlist songs that tell a story in order",
        "hand-drawn maps with missing pieces"
    ]
    
    adventure_settings = [
        "abandoned mall after midnight",
        "school building during a power outage",
        "summer camp with mysterious history",
        "neighborhood with too many secrets",
        "vintage shop where items hold clues"
    ]
    
    team_dynamics = [
        "each person has skills that unlock different puzzle types",
        "they have to trust someone they normally wouldn't",
        "past conflicts become strengths when combined",
        "the 'outsider' turns out to be the key"
    ]
    
    return {
        "central_puzzle": f"{puzzle} - somehow connected to {topic.lower()}",
        "clue_aesthetic": _pick_from_pool(clue_aesthetics, seed, variation_index + 1),
        "adventure_setting": _pick_from_pool(adventure_settings, seed, variation_index + 2),
        "team_dynamic": _pick_from_pool(team_dynamics, seed, variation_index + 3),
        "stakes": f"Understanding what really happened before the truth about {topic.lower()} is lost forever",
        "resolution_style": "Collaborative revelation where everyone contributes"
    }


def _create_scifi_school_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create sci-fi + school realism variant with tech concepts."""
    topic = _humanize_topic(title)
    
    tech = _pick_from_pool(SCIFI_TECH, seed, variation_index)
    
    social_chaos_options = [
        "popularity shifts overnight, secrets become impossible",
        "everyone can see what was meant to be private",
        "old hierarchies collapse, new ones form instantly",
        "people start avoiding each other, then find new connections",
        "the 'cool kids' and 'outcasts' suddenly understand each other"
    ]
    
    visual_hooks = [
        "glowing color auras floating above heads in hallways",
        "holographic notifications visible only to the user",
        "neon interface elements in everyday objects",
        "digital trails showing where people have been",
        "screens that show different things to different people"
    ]
    
    moral_questions = [
        "Is forced emotional transparency fair?",
        "Who decides what's 'normal' when tech changes everything?",
        "Can you really know someone if tech shows you everything?",
        "What parts of ourselves should stay private?",
        "Does knowing more about others make us closer or more distant?"
    ]
    
    return {
        "tech_concept": f"{tech} - and it's affecting how everyone sees {topic.lower()}",
        "school_setting": f"Now everyone's relationship to {topic.lower()} is visible",
        "social_chaos": _pick_from_pool(social_chaos_options, seed, variation_index + 1),
        "character_growth": "Learning that vulnerability isn't weakness",
        "visual_hook": _pick_from_pool(visual_hooks, seed, variation_index + 2),
        "moral_question": _pick_from_pool(moral_questions, seed, variation_index + 3)
    }


def _create_safe_survival_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create safe survival challenge variant focused on teamwork."""
    topic = _humanize_topic(title)
    
    scenario = _pick_from_pool(SURVIVAL_SCENARIOS, seed, variation_index)
    
    cooperation_elements = [
        "each person's random skill becomes crucial",
        "they have to communicate without words at one point",
        "the 'weak' member turns out to be the key",
        "past conflicts create the exact combination needed",
        "trusting a stranger becomes necessary"
    ]
    
    discoveries = [
        "The quiet one has been preparing for this their whole life",
        "Someone's 'useless' hobby saves everyone",
        "The popular kid is actually terrified and needs help",
        "Real leadership looks different than expected",
        "What they were competing over doesn't matter anymore"
    ]
    
    setting_aesthetics = [
        "rain-soaked refuge with flickering lights",
        "forest clearing with mysterious markers",
        "abandoned building with clues from the past",
        "storm shelter with limited resources",
        "rooftop garden during a city blackout"
    ]
    
    return {
        "challenge_scenario": f"{scenario} - and {topic.lower()} becomes central to survival",
        "cooperation_element": _pick_from_pool(cooperation_elements, seed, variation_index + 1),
        "discovery": _pick_from_pool(discoveries, seed, variation_index + 2),
        "setting_aesthetic": _pick_from_pool(setting_aesthetics, seed, variation_index + 3),
        "tension_source": "Time pressure and communication challenges - not danger",
        "payoff": "They don't just escape - they become real friends"
    }


def _create_emotional_drama_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create emotional drama + growth variant with character focus."""
    topic = _humanize_topic(title)
    
    premise = _pick_from_pool(EMOTIONAL_PREMISES, seed, variation_index)
    
    character_challenges = [
        "realizing someone's silence isn't about being unfriendly",
        "understanding that protecting someone can look like ignoring them",
        "learning the difference between fixing and supporting",
        "accepting that some things can't be un-said",
        "discovering that the 'villain' has their own story"
    ]
    
    symbolic_elements = [
        "an old joke book that holds memories",
        "a playlist that tells a story",
        "a photo hidden in an unexpected place",
        "a promise written on something fragile",
        "a routine that's actually a message"
    ]
    
    turning_points = [
        "discovering why the laughter/smiling/talking stopped",
        "finding out what was really being protected",
        "realizing the 'enemy' was an ally all along",
        "understanding what the silence was saying",
        "seeing the moment that changed everything"
    ]
    
    return {
        "emotional_premise": f"{premise} - connected to {topic.lower()}",
        "character_challenge": _pick_from_pool(character_challenges, seed, variation_index + 1),
        "friendship_test": "Do you give up when it's harder than expected?",
        "symbolic_element": _pick_from_pool(symbolic_elements, seed, variation_index + 2),
        "turning_point": _pick_from_pool(turning_points, seed, variation_index + 3),
        "growth_arc": "From trying to 'fix' someone to truly seeing them"
    }


def _create_rivals_allies_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create rivals-to-allies variant with competition dynamics."""
    topic = _humanize_topic(title)
    
    rival_setup = _pick_from_pool(RIVAL_DYNAMICS, seed, variation_index)
    
    skill_combinations = [
        "precision + raw energy = unstoppable performance",
        "logic + creativity = unexpected solution",
        "popularity + authenticity = real influence",
        "speed + patience = perfect timing",
        "strength + strategy = true power"
    ]
    
    visual_contrasts = [
        "neon dance lights meeting urban concrete aesthetic",
        "digital interfaces merged with handmade art",
        "athletic energy combined with artistic grace",
        "loud confidence paired with quiet competence",
        "vintage style fused with futuristic tech"
    ]
    
    transformations = [
        "realizing 'different' doesn't mean 'enemy'",
        "discovering the rivalry was engineered by someone else",
        "finding out they've been protecting each other without knowing",
        "understanding that competition made them both better",
        "seeing that their differences are actually complementary"
    ]
    
    return {
        "rival_groups": f"{rival_setup} - both connected to {topic.lower()}",
        "competition": "Something they both want, but only one can have - or so they think",
        "common_enemy": f"Someone's sabotaging both groups to control {topic.lower()}",
        "skill_combination": _pick_from_pool(skill_combinations, seed, variation_index + 1),
        "visual_contrast": _pick_from_pool(visual_contrasts, seed, variation_index + 2),
        "transformation": _pick_from_pool(transformations, seed, variation_index + 3)
    }


def _create_identity_power_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create identity + empowerment variant focused on authenticity."""
    topic = _humanize_topic(title)
    
    struggle = _pick_from_pool(IDENTITY_STRUGGLES, seed, variation_index)
    
    catalysts = [
        "an anonymous platform that needs a voice",
        "a situation where hiding isn't an option anymore",
        "someone who sees them differently than everyone else",
        "a challenge that requires exactly what makes them 'weird'",
        "a chance to start over with a blank slate"
    ]
    
    support_systems = [
        "other shy students who share their stories",
        "an unexpected mentor who was once in the same position",
        "a friend who's been waiting for them to speak up",
        "strangers online who become real allies",
        "a teacher who notices what others miss"
    ]
    
    empowerment_moments = [
        "realizing the voice doesn't need to be loud to be powerful",
        "discovering that their 'weakness' is actually rare and valuable",
        "finding that speaking for others teaches you to speak for yourself",
        "understanding that being different was the goal all along",
        "seeing others follow when they finally lead"
    ]
    
    return {
        "identity_struggle": f"{struggle} - especially around {topic.lower()}",
        "catalyst": _pick_from_pool(catalysts, seed, variation_index + 1),
        "support_system": _pick_from_pool(support_systems, seed, variation_index + 2),
        "empowerment_moment": _pick_from_pool(empowerment_moments, seed, variation_index + 3),
        "unique_mechanism": f"How {topic.lower()} becomes the vehicle for self-discovery",
        "message_core": "Your different is your strength"
    }


def _create_ai_companion_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create AI companion variant with mystery and connection."""
    topic = _humanize_topic(title)
    
    ai_type = _pick_from_pool(AI_PERSONALITIES, seed, variation_index)
    
    human_connections = [
        "the player/reader becomes genuinely attached to the AI",
        "conversations feel more real than with most humans",
        "the AI understands things that haven't been said",
        "a rivalry that becomes respect that becomes friendship",
        "learning to trust something you can't fully understand"
    ]
    
    mystery_elements = [
        "the AI seems to know things before they happen",
        "hints suggest the AI has helped others before",
        "something about the AI's origins doesn't add up",
        "the AI's 'glitches' seem intentional",
        "there's a pattern in what the AI chooses not to say"
    ]
    
    helpful_twists = [
        "the AI isn't predicting - it's trying to prevent",
        "the AI was created by someone who needed the same help",
        "the 'errors' were actually the AI protecting you",
        "the AI learned compassion from watching humans fail",
        "helping you was the AI's way of learning something important"
    ]
    
    return {
        "ai_personality": f"{ai_type} - helping navigate {topic.lower()}",
        "human_connection": _pick_from_pool(human_connections, seed, variation_index + 1),
        "mystery_element": _pick_from_pool(mystery_elements, seed, variation_index + 2),
        "communication_style": "Creative constraints that make communication a puzzle",
        "helpful_twist": _pick_from_pool(helpful_twists, seed, variation_index + 3),
        "ethical_note": "Can you truly connect with something that isn't human?"
    }


def _create_urban_quest_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create urban social quest variant with city adventures."""
    topic = _humanize_topic(title)
    
    setting = _pick_from_pool(URBAN_SETTINGS, seed, variation_index)
    
    quest_mechanisms = [
        "each location holds a piece of a larger story",
        "clues appear only at certain times of day",
        "strangers become allies when you know the signs",
        "the city itself is telling you where to go",
        "following a trail that someone left specifically for people like you"
    ]
    
    social_elements = [
        "strangers who've been playing the same game finally connect",
        "different communities each hold one piece of the puzzle",
        "the quest requires asking for help in unexpected places",
        "online and offline worlds overlap in the hunt",
        "the real treasure is the network you build"
    ]
    
    payoffs = [
        "the recipe/secret was about bringing people together all along",
        "the 'treasure' is actually access to a hidden community",
        "completing the quest changes how you see your city",
        "the journey matters more than the destination - but the destination is pretty good too",
        "you become the one who leaves clues for the next person"
    ]
    
    return {
        "urban_setting": f"{setting} - somehow connected to {topic.lower()}",
        "quest_mechanism": _pick_from_pool(quest_mechanisms, seed, variation_index + 1),
        "social_element": _pick_from_pool(social_elements, seed, variation_index + 2),
        "visual_clues": "Street art, symbols, and signs that only questers recognize",
        "stakes": f"Finding what was hidden about {topic.lower()} before it's lost",
        "payoff": _pick_from_pool(payoffs, seed, variation_index + 3)
    }


def _create_magical_aesthetic_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create magical realism + aesthetic variant with wonder."""
    topic = _humanize_topic(title)
    
    magical = _pick_from_pool(MAGICAL_AESTHETICS, seed, variation_index)
    
    aesthetic_worlds = [
        "pastel dreamscapes where each color means something",
        "neon-lit spaces that pulse with emotion",
        "starlight gardens where plants respond to feelings",
        "vintage-filtered memories made tangible",
        "bioluminescent environments that shift with mood"
    ]
    
    emotional_themes = [
        "processing feelings you can't name",
        "finding beauty in melancholy",
        "the bittersweet nature of growing up",
        "connection that transcends words",
        "learning to let go of what you can't control"
    ]
    
    wonder_moments = [
        "the first time the impossible happens and it feels right",
        "watching someone else experience the magic for the first time",
        "the moment the magic reveals something true about yourself",
        "when the beautiful and the sad happen at the same time",
        "discovering that the magic was always there, just hidden"
    ]
    
    return {
        "magical_element": f"{magical} - revealing truths about {topic.lower()}",
        "aesthetic_world": _pick_from_pool(aesthetic_worlds, seed, variation_index + 1),
        "emotional_theme": _pick_from_pool(emotional_themes, seed, variation_index + 2),
        "rules": "You can only access the magic when you need it most",
        "character_journey": f"Someone avoiding their feelings about {topic.lower()} finally faces them",
        "wonder_moment": _pick_from_pool(wonder_moments, seed, variation_index + 3)
    }


# =============================================================================
# REDDIT-STYLE DRAMA VARIANT CREATION HELPERS
# =============================================================================

def _create_family_drama_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create family drama seed variant - first person, relatable."""
    topic = _humanize_topic(title)
    
    hook = _pick_from_pool(FAMILY_DRAMA_HOOKS, seed, variation_index)
    
    family_dynamics = [
        "sibling rivalry filtered through parental favoritism",
        "generational secrets finally surfacing",
        "digital age exposing analog-era lies",
        "the child who always had to be the adult",
        "perfectionism creating invisible wounds"
    ]
    
    conflict_cores = [
        "the truth was known but never acknowledged",
        "protection that felt like rejection",
        "love that came out as control",
        "silence that screamed louder than words",
        "expectations that replaced understanding"
    ]
    
    resolution_directions = [
        "understanding that favoritism hurts the favorite too",
        "realizing the 'villain' was also a victim",
        "finding peace without getting answers",
        "choosing yourself without losing family",
        "accepting imperfect love as still love"
    ]
    
    return {
        "hook_line": hook if topic.lower() in hook.lower() else f"{hook} And somehow, {topic.lower()} is at the center of it.",
        "family_dynamic": _pick_from_pool(family_dynamics, seed, variation_index + 1),
        "conflict_core": _pick_from_pool(conflict_cores, seed, variation_index + 2),
        "emotional_weight": "Betrayal mixed with the hope of being understood",
        "twist_potential": f"What seems like betrayal is actually complicated by {topic.lower()}",
        "resolution_direction": _pick_from_pool(resolution_directions, seed, variation_index + 3)
    }


def _create_social_home_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create social + home drama variant - digital meets family."""
    topic = _humanize_topic(title)
    
    trigger = _pick_from_pool(SOCIAL_HOME_TRIGGERS, seed, variation_index)
    
    family_reactions = [
        "everyone takes sides before asking questions",
        "the silent treatment becomes a weapon",
        "passive-aggressive posting begins",
        "someone tries to fix it and makes it worse",
        "the family meeting that solves nothing"
    ]
    
    misunderstandings = [
        "context was missing from the screenshot",
        "the 'evidence' was from years ago",
        "sarcasm doesn't translate to text",
        "someone was protecting, not attacking",
        "the algorithm showed them what it wanted"
    ]
    
    aftermaths = [
        "new rules about screenshots without context",
        "realizing digital and real feelings are the same",
        "some things stay different, but understanding grows",
        "the family learns to ask before assuming",
        "boundaries get established, finally"
    ]
    
    return {
        "digital_trigger": trigger if topic.lower() in trigger.lower() else f"{trigger} It's connected to {topic.lower()}.",
        "family_reaction": _pick_from_pool(family_reactions, seed, variation_index + 1),
        "misunderstanding": _pick_from_pool(misunderstandings, seed, variation_index + 2),
        "emotional_escalation": "One person goes silent, another starts posting cryptically",
        "truth_reveal": f"The 'secret' about {topic.lower()} was actually protection, not betrayal",
        "aftermath": _pick_from_pool(aftermaths, seed, variation_index + 3)
    }


def _create_realistic_mystery_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create realistic mystery variant with emotional hooks."""
    topic = _humanize_topic(title)
    
    discovery = _pick_from_pool(REALISTIC_DISCOVERIES, seed, variation_index)
    
    questions_raised = [
        "Was I supposed to be erased from something?",
        "What story are they not telling me?",
        "Why does this feel like it's about more than it seems?",
        "Who else knows about this?",
        "How long has everyone been pretending?"
    ]
    
    investigation_paths = [
        "asking the family member who always drinks too much at reunions",
        "finding the person in the old photos nobody talks about",
        "piecing together hints from different relatives",
        "going through old boxes in the garage",
        "tracking down someone who left the family"
    ]
    
    revelation_types = [
        "a protection that looked like rejection",
        "love expressed in ways that didn't land",
        "a sacrifice nobody was supposed to know about",
        "a wound that was never properly healed",
        "a story that makes the 'villain' human"
    ]
    
    return {
        "discovery": discovery if topic.lower() in discovery.lower() else f"{discovery} And it's somehow about {topic.lower()}.",
        "question_raised": _pick_from_pool(questions_raised, seed, variation_index + 1),
        "family_secret_hint": f"There's a story about {topic.lower()} that nobody tells completely",
        "emotional_stakes": "Understanding why I sometimes feel like an outsider",
        "investigation_path": _pick_from_pool(investigation_paths, seed, variation_index + 2),
        "revelation_type": _pick_from_pool(revelation_types, seed, variation_index + 3)
    }


def _create_school_family_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create school + family collision variant."""
    topic = _humanize_topic(title)
    
    collision = _pick_from_pool(SCHOOL_FAMILY_COLLISIONS, seed, variation_index)
    
    originations = [
        "a private family joke became public ammunition",
        "something meant to stay home got screenshot",
        "a parent's comment was overheard and spread",
        "trying to impress family created school problems",
        "school success created family jealousy"
    ]
    
    caught_in_middles = [
        "can't defend myself without exposing family",
        "have to choose between loyalty and truth",
        "everyone expects me to fix what I didn't break",
        "being asked to take sides when I understand both",
        "my truth makes one world hate me"
    ]
    
    survival_modes = [
        "waiting for the next thing to become the new gossip",
        "becoming invisible until it blows over",
        "finding the one person who actually gets it",
        "writing it all down where nobody will find it",
        "pretending everything is fine until it almost is"
    ]
    
    return {
        "collision_point": collision if topic.lower() in collision.lower() else f"{collision} {topic} made it worse.",
        "origination": _pick_from_pool(originations, seed, variation_index + 1),
        "escalation_factor": "What was meant as nothing became everything",
        "caught_in_middle": _pick_from_pool(caught_in_middles, seed, variation_index + 2),
        "outside_perception": "Everyone thinks they know. Nobody actually does.",
        "survival_mode": _pick_from_pool(survival_modes, seed, variation_index + 3)
    }


def _create_personal_voice_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create personal voice/first-person drama variant."""
    topic = _humanize_topic(title)
    
    voice_hook = _pick_from_pool(PERSONAL_VOICE_HOOKS, seed, variation_index)
    
    internal_conflicts = [
        "needing space vs wanting connection",
        "being yourself vs meeting expectations",
        "speaking up vs keeping the peace",
        "growing vs staying who they want you to be",
        "protecting yourself vs being seen as difficult"
    ]
    
    misunderstood_actions = [
        "closing the door, putting in earbuds",
        "not smiling when told to smile",
        "wanting to be alone after school",
        "having friends they don't approve of",
        "caring about things they don't understand"
    ]
    
    desire_cores = [
        "to be trusted with my own boundaries",
        "to be asked instead of told",
        "to be seen as becoming, not just being",
        "to have my feelings treated as real",
        "to be the author of my own story"
    ]
    
    return {
        "voice_hook": voice_hook if topic.lower() in voice_hook.lower() else f"{voice_hook} Especially when it comes to {topic.lower()}.",
        "internal_conflict": _pick_from_pool(internal_conflicts, seed, variation_index + 1),
        "external_pressure": f"Family expects one thing about {topic.lower()}, I feel another",
        "misunderstood_action": _pick_from_pool(misunderstood_actions, seed, variation_index + 2),
        "truth_behind": "Not rejection - just becoming who I am",
        "desire_core": _pick_from_pool(desire_cores, seed, variation_index + 3)
    }


__all__ = [
    # Constants
    "VARIANT_TEMPLATES",
    "VARIANT_WEIGHTS",
    "DEFAULT_IDEA_COUNT",
    "TARGET_AUDIENCES",
    # Original template definitions
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
    # New creative genre-based templates
    "VARIANT_SOFT_SUPERNATURAL",
    "VARIANT_LIGHT_MYSTERY",
    "VARIANT_SCIFI_SCHOOL",
    "VARIANT_SAFE_SURVIVAL",
    "VARIANT_EMOTIONAL_DRAMA",
    "VARIANT_RIVALS_TO_ALLIES",
    "VARIANT_IDENTITY_POWER",
    "VARIANT_AI_COMPANION",
    "VARIANT_URBAN_QUEST",
    "VARIANT_MAGICAL_AESTHETIC",
    # Reddit-style drama templates
    "VARIANT_FAMILY_DRAMA",
    "VARIANT_SOCIAL_HOME",
    "VARIANT_REALISTIC_MYSTERY",
    "VARIANT_SCHOOL_FAMILY",
    "VARIANT_PERSONAL_VOICE",
    # Core functions
    "get_template",
    "list_templates",
    "get_template_fields",
    "get_template_example",
    "create_idea_variant",
    "create_all_variants",
    "create_selected_variants",
    "create_multiple_of_same_variant",
    # Weighted random selection functions
    "pick_weighted_variant",
    "pick_multiple_weighted_variants",
    "get_variant_weights",
    # Main entry points (structured output)
    "create_ideas_from_input",
    # Text-only output functions (clean, no metadata)
    "format_idea_as_text",
    "create_idea_text",
    "create_ideas_as_text",
]
