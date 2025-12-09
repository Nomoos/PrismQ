"""Drama-focused variant templates - Reddit-style and personal drama."""

from typing import Any, Dict

VARIANT_FAMILY_DRAMA = {
    "name": "Family Drama Seed",
    "description": "Family conflict story seeds",
    "fields": {
        "hook_line": "The attention-grabbing opening",
        "family_dynamic": "The family relationship pattern",
        "conflict_core": "What the conflict is really about",
        "emotional_weight": "The feeling beneath the surface",
        "twist_potential": "Where this could go unexpectedly",
        "resolution_direction": "How understanding might come",
    },
    "example": {
        "hook_line": "I just found out why my parents treated my sibling differently",
        "family_dynamic": "Favoritism hiding deeper issues",
        "conflict_core": "Love expressed through control vs. freedom",
        "emotional_weight": "Betrayal mixed with understanding",
        "twist_potential": "The 'favorite' also suffered",
        "resolution_direction": "Seeing parents as flawed humans",
    },
}

VARIANT_SOCIAL_HOME = {
    "name": "Social + Home Drama",
    "description": "When social media intersects with family",
    "fields": {
        "digital_trigger": "The online event that started it",
        "family_reaction": "How family responded",
        "misunderstanding": "What was misread",
        "aftermath": "How things changed",
        "lesson": "What was learned about online/offline",
    },
    "example": {
        "digital_trigger": "A screenshot taken out of context",
        "family_reaction": "Assumptions before questions",
        "misunderstanding": "Tone lost in text",
        "aftermath": "New rules about digital communication",
        "lesson": "Context matters everywhere",
    },
}

VARIANT_REALISTIC_MYSTERY = {
    "name": "Realistic Mystery",
    "description": "Everyday mysteries with grounded solutions",
    "fields": {
        "mystery_setup": "The puzzle presented",
        "investigation_path": "How it gets explored",
        "red_herrings": "Misleading possibilities",
        "real_answer": "The grounded explanation",
        "human_element": "What it reveals about people",
        "satisfaction": "Why the resolution feels right",
    },
    "example": {
        "mystery_setup": "Things keep going missing from shared spaces",
        "investigation_path": "Observation and careful questions",
        "red_herrings": "Obvious suspects who aren't responsible",
        "real_answer": "Misunderstanding about shared property",
        "human_element": "Communication gaps cause most mysteries",
        "satisfaction": "Understanding replaces suspicion",
    },
}

VARIANT_SCHOOL_FAMILY = {
    "name": "School + Family Crossover",
    "description": "When school life affects home or vice versa",
    "fields": {
        "crossover_trigger": "What bridged the two worlds",
        "parent_involvement": "How parents got involved",
        "student_perspective": "How the student sees it",
        "tension_point": "Where conflict peaks",
        "bridge_building": "How understanding develops",
        "new_normal": "Where things land after",
    },
    "example": {
        "crossover_trigger": "A school issue that required parent contact",
        "parent_involvement": "Parents who didn't understand the full picture",
        "student_perspective": "Feeling caught between two worlds",
        "tension_point": "When assumptions clashed with reality",
        "bridge_building": "Honest conversation finally happening",
        "new_normal": "Better communication going forward",
    },
}

VARIANT_PERSONAL_VOICE = {
    "name": "Personal Voice",
    "description": "First-person intimate storytelling",
    "fields": {
        "voice_tone": "The narrative voice quality",
        "opening_confession": "The vulnerable opening",
        "core_experience": "What's being shared",
        "emotional_honesty": "The raw truth underneath",
        "universal_thread": "What makes it relatable",
        "closing_thought": "Where the reflection lands",
    },
    "example": {
        "voice_tone": "Honest and slightly self-deprecating",
        "opening_confession": "I've never told anyone this, but...",
        "core_experience": "A moment that changed perspective",
        "emotional_honesty": "The feelings that are hard to admit",
        "universal_thread": "Everyone has moments like this",
        "closing_thought": "What I understand now that I didn't then",
    },
}


__all__ = [
    "VARIANT_FAMILY_DRAMA",
    "VARIANT_SOCIAL_HOME",
    "VARIANT_REALISTIC_MYSTERY",
    "VARIANT_SCHOOL_FAMILY",
    "VARIANT_PERSONAL_VOICE",
]
