"""Creative genre-based variant templates."""

from typing import Any, Dict

VARIANT_SOFT_SUPERNATURAL = {
    "name": "Soft Supernatural",
    "description": "Light supernatural elements in everyday settings",
    "fields": {
        "supernatural_element": "The magical or unexplained element",
        "grounding_reality": "The everyday world it exists in",
        "discovery_moment": "How the supernatural is revealed",
        "emotional_core": "What human truth it illuminates",
        "visual_aesthetic": "The look and feel",
        "stakes": "What's at risk",
    },
    "example": {
        "supernatural_element": "Objects that hold memories you can experience",
        "grounding_reality": "A thrift store in a small town",
        "discovery_moment": "Finding an object connected to your own past",
        "emotional_core": "How objects carry our stories",
        "visual_aesthetic": "cozy, slightly dreamlike",
        "stakes": "Understanding your own history",
    },
}

VARIANT_LIGHT_MYSTERY = {
    "name": "Light Mystery",
    "description": "Cozy or light mystery format",
    "fields": {
        "mystery_type": "What kind of mystery",
        "setting": "Where this takes place",
        "detective_figure": "Who's solving this",
        "red_herrings": "Misleading clues",
        "resolution_type": "How it gets solved",
        "comfort_element": "What makes it cozy",
    },
    "example": {
        "mystery_type": "Missing item with sentimental value",
        "setting": "Small community everyone knows",
        "detective_figure": "Someone who notices what others miss",
        "red_herrings": "Obvious suspects who aren't guilty",
        "resolution_type": "Understanding rather than punishment",
        "comfort_element": "Community coming together",
    },
}

VARIANT_SCIFI_SCHOOL = {
    "name": "Sci-Fi School",
    "description": "Science fiction elements in educational settings",
    "fields": {
        "scifi_concept": "The futuristic or tech element",
        "school_setting": "The educational environment",
        "protagonist_role": "The main character's position",
        "conflict_source": "What creates tension",
        "learning_journey": "What's being learned",
        "hopeful_element": "The optimistic thread",
    },
    "example": {
        "scifi_concept": "AI tutors that adapt to emotions",
        "school_setting": "Near-future high school",
        "protagonist_role": "Student questioning the system",
        "conflict_source": "When technology misses human nuance",
        "learning_journey": "What can't be taught by algorithms",
        "hopeful_element": "Human connection wins",
    },
}

VARIANT_SAFE_SURVIVAL = {
    "name": "Safe Survival",
    "description": "Survival themes without graphic content",
    "fields": {
        "survival_scenario": "The challenge to overcome",
        "protagonist_strength": "What makes them capable",
        "obstacle_progression": "How challenges escalate",
        "help_element": "Support that arrives",
        "growth_arc": "How the character changes",
        "safety_note": "What keeps it appropriate",
    },
    "example": {
        "survival_scenario": "Lost in wilderness, must find way back",
        "protagonist_strength": "Resourcefulness and calm",
        "obstacle_progression": "Weather, terrain, self-doubt",
        "help_element": "Skills learned from unlikely sources",
        "growth_arc": "From dependent to self-reliant",
        "safety_note": "Focus on problem-solving, not danger",
    },
}

VARIANT_EMOTIONAL_DRAMA = {
    "name": "Emotional Drama",
    "description": "Character-driven emotional stories",
    "fields": {
        "emotional_conflict": "The internal struggle",
        "relationship_tension": "The relationship at stake",
        "turning_point": "The moment things shift",
        "vulnerability_moment": "When guards come down",
        "resolution_type": "How it resolves (or doesn't)",
        "takeaway_feeling": "What audiences feel after",
    },
    "example": {
        "emotional_conflict": "Wanting to be understood vs. fear of being seen",
        "relationship_tension": "Growing apart from a close friend",
        "turning_point": "A honest conversation finally happens",
        "vulnerability_moment": "Admitting hurt instead of hiding it",
        "resolution_type": "Understanding without full resolution",
        "takeaway_feeling": "Bittersweet hope",
    },
}

VARIANT_RIVALS_TO_ALLIES = {
    "name": "Rivals to Allies",
    "description": "Competition becoming cooperation",
    "fields": {
        "rivalry_source": "Why they're competing",
        "common_ground": "What they secretly share",
        "forced_cooperation": "What makes them work together",
        "respect_moment": "When respect begins",
        "alliance_benefit": "What they achieve together",
        "relationship_end_state": "Where they land",
    },
    "example": {
        "rivalry_source": "Both want the same recognition",
        "common_ground": "Similar backgrounds, similar wounds",
        "forced_cooperation": "A challenge neither can win alone",
        "respect_moment": "Seeing each other's hidden struggles",
        "alliance_benefit": "Better together than apart",
        "relationship_end_state": "Respectful allies, maybe friends",
    },
}

VARIANT_IDENTITY_POWER = {
    "name": "Identity Power",
    "description": "Finding strength in identity",
    "fields": {
        "identity_aspect": "The part of self being explored",
        "challenge_to_identity": "What threatens or questions it",
        "source_of_strength": "Where power comes from",
        "community_element": "Others who share this experience",
        "transformation_arc": "How identity understanding grows",
        "empowerment_message": "The affirming takeaway",
    },
    "example": {
        "identity_aspect": "Being different in a conformist space",
        "challenge_to_identity": "Pressure to hide or change",
        "source_of_strength": "Realizing difference is an asset",
        "community_element": "Finding others who celebrate difference",
        "transformation_arc": "From hiding to proudly being",
        "empowerment_message": "Your uniqueness is your power",
    },
}

VARIANT_AI_COMPANION = {
    "name": "AI Companion",
    "description": "AI relationship stories",
    "fields": {
        "ai_nature": "What kind of AI",
        "relationship_dynamic": "How human and AI relate",
        "trust_building": "How connection develops",
        "ethical_question": "The moral dimension",
        "human_element": "What makes it about humanity",
        "resolution": "Where the relationship goes",
    },
    "example": {
        "ai_nature": "AI that learns from conversations",
        "relationship_dynamic": "Unexpected friendship",
        "trust_building": "Shared secrets and growth",
        "ethical_question": "Can AI truly understand us?",
        "human_element": "What connection really means",
        "resolution": "Appreciation for both digital and human bonds",
    },
}

VARIANT_URBAN_QUEST = {
    "name": "Urban Quest",
    "description": "Adventure in city settings",
    "fields": {
        "quest_goal": "What's being sought",
        "urban_setting": "The city environment",
        "clue_progression": "How the quest unfolds",
        "helper_characters": "People met along the way",
        "city_as_character": "How the city itself matters",
        "discovery": "What's found (beyond the goal)",
    },
    "example": {
        "quest_goal": "Finding a hidden community space",
        "urban_setting": "City neighborhood with layers of history",
        "clue_progression": "Each clue reveals more about the city",
        "helper_characters": "Long-time residents who hold keys",
        "city_as_character": "The city reveals itself to those who look",
        "discovery": "Community was there all along",
    },
}

VARIANT_MAGICAL_AESTHETIC = {
    "name": "Magical Aesthetic",
    "description": "Aesthetic-forward magical realism",
    "fields": {
        "visual_style": "The dominant aesthetic",
        "magical_element": "The enchanted aspect",
        "emotional_resonance": "The feeling it evokes",
        "world_rules": "How the magic works",
        "character_connection": "How character relates to magic",
        "mood": "The overall atmosphere",
    },
    "example": {
        "visual_style": "Soft pastels and golden light",
        "magical_element": "Emotions manifest as visible colors",
        "emotional_resonance": "Wonder and gentle melancholy",
        "world_rules": "Only some people can see the colors",
        "character_connection": "Learning to read their own emotions",
        "mood": "Dreamlike but grounded",
    },
}


__all__ = [
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
]
