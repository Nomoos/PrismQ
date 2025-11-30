"""Structural blend templates - new themes combined with structural templates."""

from typing import Dict, Any


VARIANT_FANDOM_SKELETON = {
    "name": "Fandom + Story Skeleton Blend",
    "description": "Structured fandom passion journey",
    "fields": {
        "opening_hook": "The moment that captures fandom passion",
        "the_discovery": "How this passion was found",
        "rising_investment": "How the passion deepened",
        "peak_moment": "The defining fandom experience",
        "community_element": "The people found through this passion",
        "conclusion_shape": "How the passion fits into identity now"
    },
    "example": {
        "opening_hook": "I've refreshed this page 47 times in the last hour. New episode day.",
        "the_discovery": "Started as background noise. Became the only thing I wanted to watch.",
        "rising_investment": "From casual viewer to someone who reads theories at 2am",
        "peak_moment": "The finale watch party with online friends who became real friends",
        "community_element": "People who get excited about the same fictional characters I do",
        "conclusion_shape": "This show didn't just entertain me. It gave me a community."
    }
}

VARIANT_IMPOSTER_MYSTERY = {
    "name": "Imposter + Mystery Structure Blend",
    "description": "Mystery-structured imposter syndrome exploration",
    "fields": {
        "central_mystery": "The core imposter question",
        "clues_against": "The 'evidence' the imposter voice uses",
        "clues_for": "The evidence that contradicts imposter voice",
        "investigation": "Tracing where these feelings started",
        "the_reveal": "What's really behind the imposter feelings",
        "aftermath": "How understanding changes things"
    },
    "example": {
        "central_mystery": "Why do I feel like a fraud when I earned my spot?",
        "clues_against": "Every mistake feels like proof. Every success feels like luck.",
        "clues_for": "The work I did. The growth I can trace. The people who believe in me.",
        "investigation": "That moment in fourth grade when I got praised for the wrong thing",
        "the_reveal": "I tied my worth to being 'the smart one' - and now I'm afraid to not be",
        "aftermath": "Learning I can fail without being a failure"
    }
}

VARIANT_SIBLING_EMOTION_FIRST = {
    "name": "Sibling + Emotion-First Blend",
    "description": "Emotion-driven sibling story structure",
    "fields": {
        "main_emotion": "The core emotion of the sibling relationship",
        "the_hook": "What captures this relationship's essence",
        "dynamic_setup": "The roles you both play",
        "emotional_turning_point": "When the emotion shifted",
        "unusual_understanding": "What siblings understand that others don't",
        "emotional_resolution": "Where the relationship sits now"
    },
    "example": {
        "main_emotion": "Protective anger that's actually love",
        "the_hook": "The first time I realized I'd fight anyone who hurt them",
        "dynamic_setup": "I'm the anxious one. They're the one who takes risks.",
        "emotional_turning_point": "When they protected ME for the first time",
        "unusual_understanding": "We can have a whole conversation in looks",
        "emotional_resolution": "We don't always like each other. We always have each other."
    }
}

VARIANT_MENTOR_HOOK_FRAME = {
    "name": "Mentor + Hook Frame Blend",
    "description": "Hook-framed mentor impact story",
    "fields": {
        "hook_question": "The question that captures the mentor's impact",
        "before_them": "Who you were before this person",
        "the_intervention": "What they did that changed things",
        "frame_shift": "How they reframed something for you",
        "ripple_effects": "How their influence spread",
        "the_answer": "The answer to the hook question"
    },
    "example": {
        "hook_question": "What if one conversation could change your entire direction?",
        "before_them": "Convinced I wasn't good enough for the thing I wanted",
        "the_intervention": "They asked 'What would you do if you knew you couldn't fail?'",
        "frame_shift": "Made me realize I was planning around fear, not around dreams",
        "ripple_effects": "I applied. I tried. I started believing 'what if I could?'",
        "the_answer": "One conversation didn't change everything. It changed me."
    }
}

VARIANT_MONEY_SHORTFORM = {
    "name": "Money Reality + Shortform Blend",
    "description": "Quick-hit money awareness story structure",
    "fields": {
        "hook_moment": "The 10-second moment that reveals money reality",
        "quick_context": "The fast setup",
        "the_realization": "What clicked in that moment",
        "emotional_punch": "The feeling that hit",
        "one_truth": "The takeaway in one sentence",
        "relate_factor": "Why this hits for others too"
    },
    "example": {
        "hook_moment": "When my friend casually said 'just buy another one'",
        "quick_context": "I'd been wearing the same shoes for two years",
        "the_realization": "Some people don't think about money before every purchase",
        "emotional_punch": "Not envy. Just... awareness. A quiet 'oh.'",
        "one_truth": "We're living in different economies at the same school.",
        "relate_factor": "Everyone has a 'oh, we're not the same' moment"
    }
}

VARIANT_HERITAGE_GENRE = {
    "name": "Heritage + Genre Frame Blend",
    "description": "Genre-framed cultural identity exploration",
    "fields": {
        "genre_lens": "The genre that frames this identity journey",
        "the_quest": "The identity question being explored",
        "dual_world_building": "The two cultural worlds navigated",
        "allies_and_obstacles": "Who helps and what gets in the way",
        "genre_climax": "The defining moment in genre terms",
        "resolution_type": "How the identity quest resolves"
    },
    "example": {
        "genre_lens": "Coming-of-age with a fantasy element: language as magic",
        "the_quest": "Finding a way to be whole instead of halved",
        "dual_world_building": "Home where I'm one person, school where I'm another",
        "allies_and_obstacles": "Cousins who get it. Classmates who don't even try to pronounce my name.",
        "genre_climax": "The moment I spoke my language in public and didn't feel ashamed",
        "resolution_type": "Not choosing one world. Creating a third."
    }
}

VARIANT_GRIEF_SCENE_SEED = {
    "name": "Grief + Scene Seed Blend",
    "description": "Scene-based grief processing structure",
    "fields": {
        "opening_scene": "The scene that captures the grief",
        "sensory_details": "What grief looks/feels/sounds like in this moment",
        "memory_scene": "A scene from before the loss",
        "turning_scene": "The scene where something shifted",
        "present_scene": "Where you are now, scene-style",
        "closing_image": "The final image that holds both grief and growth"
    },
    "example": {
        "opening_scene": "Their chair at the dinner table. Still there. Still empty.",
        "sensory_details": "The smell of their perfume in their closet. Fading.",
        "memory_scene": "Them teaching me to cook. Patient with every mistake.",
        "turning_scene": "The first time I made their recipe and got it right",
        "present_scene": "I cook their dishes now. Talk to them while I do.",
        "closing_image": "Their recipe card, sauce-stained and beloved, on my kitchen wall"
    }
}

VARIANT_PET_PERSONAL_VOICE = {
    "name": "Pet Bond + Personal Voice Blend",
    "description": "Personal voice narrative about pet connection",
    "fields": {
        "voice_style": "The tone of the narrative",
        "direct_address": "Speaking to the pet directly",
        "everyday_observation": "A small daily detail",
        "deeper_meaning": "What this bond represents",
        "vulnerability_moment": "The honest admission",
        "closing_voice": "The final thought, in your voice"
    },
    "example": {
        "voice_style": "Warm but trying to sound casual about how much I care",
        "direct_address": "You know exactly when I need you, don't you?",
        "everyday_observation": "The way you wait by the door exactly when I'm coming home",
        "deeper_meaning": "The only relationship where I never have to perform",
        "vulnerability_moment": "Some days you're the only reason I get out of bed",
        "closing_voice": "Thanks for choosing me back. Every single day."
    }
}


__all__ = [
    "VARIANT_FANDOM_SKELETON",
    "VARIANT_IMPOSTER_MYSTERY",
    "VARIANT_SIBLING_EMOTION_FIRST",
    "VARIANT_MENTOR_HOOK_FRAME",
    "VARIANT_MONEY_SHORTFORM",
    "VARIANT_HERITAGE_GENRE",
    "VARIANT_GRIEF_SCENE_SEED",
    "VARIANT_PET_PERSONAL_VOICE",
]
