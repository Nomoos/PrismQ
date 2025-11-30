"""Base variant templates - foundational structural templates."""

from typing import Dict, Any


VARIANT_EMOTION_FIRST = {
    "name": "Emotion-First Hook",
    "description": "Formats an idea with emotion as the primary driver",
    "fields": {
        "main_emotion": "Primary emotion to evoke",
        "core_hook": "One sentence that captures the emotional hook",
        "target_audience": "Who this content is for",
        "unusual_angle": "A unique perspective or approach",
        "ending_style": "How the content ends",
        "content_constraints": {"length": "Content length", "safety": "Safety considerations"}
    },
    "example": {
        "main_emotion": "curiosity",
        "core_hook": "The untold truth about ancient mysteries will surprise you.",
        "target_audience": "History enthusiasts aged 25-45",
        "unusual_angle": "from an insider's perspective",
        "ending_style": "twist",
        "content_constraints": {"length": "5-10 minutes", "safety": "Review for sensitive content"}
    }
}

VARIANT_MYSTERY = {
    "name": "Mystery/Curiosity Gap",
    "description": "Structures an idea around a central mystery or unanswered question",
    "fields": {
        "central_mystery": "The main unanswered question driving the content",
        "emotional_hook": "Why the audience will care about this mystery",
        "key_hook_scene": "One pivotal scene or moment that hooks the viewer",
        "title_direction": {"type": "Title framing type", "suggestion": "Suggested title"},
        "tone_notes": "Overall tone",
        "style_notes": "Presentation style",
        "sensitivities": "Boundaries and considerations to respect"
    },
    "example": {
        "central_mystery": "What really happened in the abandoned facility?",
        "emotional_hook": "Everyone thinks they know the story, but the truth reveals something deeply human.",
        "key_hook_scene": "The moment the door opens and silence falls.",
        "title_direction": {"type": "question", "suggestion": "What Really Happened at Building 7?"},
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
        "conclusion_shape": "How the story ends",
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
        "target_audience": "Young adults 18-34",
        "title_keywords": ["unexpected", "truth", "revealed"],
        "title_images": ["dramatic reveal", "contrast"]
    }
}

VARIANT_SHORTFORM = {
    "name": "Shortform Hook",
    "description": "Optimized for short-form content platforms",
    "fields": {
        "hook_line": "The opening hook (must grab in 3 seconds)",
        "core_tension": "The central conflict or question",
        "emotional_payload": "What feeling to deliver",
        "visual_anchor": "Key visual or moment",
        "call_to_action": "What viewers should do/feel after"
    },
    "example": {
        "hook_line": "POV: You just discovered something that changes everything",
        "core_tension": "The gap between expectation and reality",
        "emotional_payload": "surprised realization",
        "visual_anchor": "The moment of discovery",
        "call_to_action": "Share if this resonates"
    }
}

VARIANT_NICHE_BLEND = {
    "name": "Niche Blend",
    "description": "Combines two niches for unique positioning",
    "fields": {
        "primary_niche": "Main content category",
        "secondary_niche": "Complementary category for blend",
        "blend_concept": "How the two connect",
        "unique_angle": "What makes this combination fresh",
        "audience_overlap": "Who would care about both niches"
    },
    "example": {
        "primary_niche": "Personal development",
        "secondary_niche": "Gaming culture",
        "blend_concept": "Life lessons from video game mechanics",
        "unique_angle": "Using game design principles for real-world goals",
        "audience_overlap": "Gamers interested in self-improvement"
    }
}

VARIANT_MINIMAL = {
    "name": "Minimal Concept",
    "description": "Stripped-down idea with just essential elements",
    "fields": {
        "one_line_hook": "The entire concept in one sentence",
        "emotional_core": "The feeling at the heart of it",
        "format_suggestion": "Best format for this idea"
    },
    "example": {
        "one_line_hook": "What if everything you believed was just one perspective?",
        "emotional_core": "curiosity mixed with uncertainty",
        "format_suggestion": "contemplative essay or video"
    }
}

VARIANT_4POINT = {
    "name": "4-Point Framework",
    "description": "Structured around four key elements",
    "fields": {
        "problem": "The issue or question being addressed",
        "insight": "The key revelation or perspective",
        "proof": "Evidence or story that supports the insight",
        "action": "What the audience can do with this"
    },
    "example": {
        "problem": "People feel disconnected despite being more connected than ever",
        "insight": "Quality of connection matters more than quantity",
        "proof": "Studies show deep conversations improve wellbeing more than many shallow ones",
        "action": "Try having one meaningful conversation today"
    }
}

VARIANT_HOOK_FRAME = {
    "name": "Hook Frame",
    "description": "Centers on a powerful hook with supporting frame",
    "fields": {
        "primary_hook": "The main attention-grabber",
        "supporting_context": "What makes the hook meaningful",
        "payoff_promise": "What the audience will gain",
        "emotional_journey": "The feeling arc from start to finish"
    },
    "example": {
        "primary_hook": "I found out something that nobody was supposed to know",
        "supporting_context": "It changed how I see everything",
        "payoff_promise": "You'll see it differently too",
        "emotional_journey": "curiosity → tension → revelation → reflection"
    }
}

VARIANT_SHORTFORM2 = {
    "name": "Shortform Variant 2",
    "description": "Alternative shortform structure for variety",
    "fields": {
        "scroll_stopper": "Visual or verbal hook to stop scrolling",
        "quick_setup": "Fast context establishment",
        "twist_or_reveal": "The surprise element",
        "emotional_land": "Where viewers emotionally end up",
        "shareability_factor": "Why someone would share this"
    },
    "example": {
        "scroll_stopper": "Wait for it...",
        "quick_setup": "Everyone told me this wouldn't work",
        "twist_or_reveal": "But then THIS happened",
        "emotional_land": "inspired determination",
        "shareability_factor": "Relatable underdog story"
    }
}

VARIANT_GENRE = {
    "name": "Genre Frame",
    "description": "Frames idea within a specific genre convention",
    "fields": {
        "genre": "The genre lens being used",
        "genre_conventions": "Expected elements of the genre",
        "subversion": "How expectations are played with",
        "emotional_target": "The feeling genre fans expect",
        "visual_style": "Visual language of the genre"
    },
    "example": {
        "genre": "mystery thriller",
        "genre_conventions": "clues, red herrings, revelation",
        "subversion": "The mystery is internal, not external",
        "emotional_target": "suspense leading to understanding",
        "visual_style": "moody, detailed, revelatory"
    }
}

VARIANT_SCENE_SEED = {
    "name": "Scene Seed",
    "description": "A single compelling scene that implies a larger story",
    "fields": {
        "scene_description": "What's happening in this moment",
        "sensory_details": "What can be seen, heard, felt",
        "emotional_undercurrent": "The feeling beneath the surface",
        "implied_before": "What happened before this moment",
        "implied_after": "Where this could lead",
        "character_in_scene": "Who we're following"
    },
    "example": {
        "scene_description": "Someone finds an old photo they've never seen before",
        "sensory_details": "Dusty box, faded colors, familiar face in unfamiliar setting",
        "emotional_undercurrent": "Curiosity mixed with unease",
        "implied_before": "A history not fully shared",
        "implied_after": "Questions that will change relationships",
        "character_in_scene": "Someone discovering family secrets"
    }
}


__all__ = [
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
]
