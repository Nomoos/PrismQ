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
# STORY SEED VARIANT TEMPLATES FOR US WOMEN 13-20
# These are designed as story seeds where the input text decides the context.
# Combinations and variations of existing templates optimized for relatability.
# =============================================================================

VARIANT_CONFESSION_MOMENT = {
    "name": "Confession Story Seed",
    "description": "First-person confession style - the narrator reveals something they've been holding back. Perfect for emotional storytelling where text provides the secret.",
    "fields": {
        "confession_hook": "The opening line that promises a reveal",
        "what_im_hiding": "The core secret or truth being confessed",
        "why_now": "What made them finally speak up",
        "fear_of_judgment": "What they're afraid people will think",
        "relief_element": "The freeing feeling of finally saying it",
        "hope_for": "What they hope happens after confessing"
    },
    "example": {
        "confession_hook": "I've never told anyone this, but...",
        "what_im_hiding": "The real reason I stopped going to parties",
        "why_now": "I saw someone going through the same thing",
        "fear_of_judgment": "That people will think I'm being dramatic",
        "relief_element": "It feels lighter just typing this out",
        "hope_for": "That someone reading this feels less alone"
    }
}

VARIANT_BEFORE_AFTER = {
    "name": "Before/After Transformation Seed",
    "description": "Story structured around a pivotal moment that changed everything. The text defines what was transformed.",
    "fields": {
        "before_state": "How things were before the change",
        "the_moment": "The specific event or realization that changed things",
        "after_state": "How things are different now",
        "what_triggered": "What made this moment happen",
        "unexpected_lesson": "What they learned that they didn't expect",
        "still_processing": "What they're still figuring out"
    },
    "example": {
        "before_state": "I used to think confidence meant being loud",
        "the_moment": "The day someone praised my 'quiet strength'",
        "after_state": "Now I understand power doesn't need volume",
        "what_triggered": "A random comment from a stranger",
        "unexpected_lesson": "Not everyone sees silence as weakness",
        "still_processing": "How to believe it myself"
    }
}

VARIANT_OVERHEARD_TRUTH = {
    "name": "Overheard Truth Seed",
    "description": "Story triggered by accidentally hearing something not meant for them. The text defines what was overheard.",
    "fields": {
        "what_was_heard": "The specific thing overheard",
        "where_it_happened": "The setting of the overhearing",
        "immediate_reaction": "First feeling/action after hearing it",
        "who_was_talking": "Who was speaking (without revealing names)",
        "what_it_changed": "How this knowledge affected them",
        "dilemma": "The impossible choice they now face"
    },
    "example": {
        "what_was_heard": "Mom telling grandma she was 'disappointed' in me",
        "where_it_happened": "Kitchen, while I was supposed to be asleep",
        "immediate_reaction": "Frozen on the stairs, heart racing",
        "who_was_talking": "The two people I thought believed in me most",
        "what_it_changed": "Every compliment now feels conditional",
        "dilemma": "Confront them or pretend I never heard"
    }
}

VARIANT_PARALLEL_LIVES = {
    "name": "Parallel Lives Seed",
    "description": "Comparing two versions of self or two paths - the one lived and the one imagined. The text defines the fork.",
    "fields": {
        "the_choice_point": "The moment two paths diverged",
        "path_taken": "What actually happened",
        "path_imagined": "What could have been",
        "what_haunts": "What lingers from the unchosen path",
        "current_peace": "What makes the chosen path okay",
        "wondering": "The question that still surfaces"
    },
    "example": {
        "the_choice_point": "The day I chose to stay quiet instead of defend myself",
        "path_taken": "I became the 'mature one' who let things slide",
        "path_imagined": "Maybe people would respect me more if I'd fought back",
        "what_haunts": "Wondering if peace was just people-pleasing",
        "current_peace": "I kept relationships that fighting might have destroyed",
        "wondering": "Was I wise or just afraid?"
    }
}

VARIANT_LAST_TIME = {
    "name": "Last Time Seed",
    "description": "Story about the last time something happened before everything changed. The text defines what ended.",
    "fields": {
        "the_last_moment": "The final time it happened",
        "didnt_know_then": "What they didn't realize at the time",
        "looking_back": "How they see it now with hindsight",
        "wish_id_known": "What they wish they'd done differently",
        "what_replaced_it": "What fills that space now",
        "carrying_forward": "What they'll never forget"
    },
    "example": {
        "the_last_moment": "The last time I laughed with my best friend before the fight",
        "didnt_know_then": "That one sentence would end three years of friendship",
        "looking_back": "It was already fragile; I just didn't want to see",
        "wish_id_known": "I would have held onto that laugh longer",
        "what_replaced_it": "Careful friendships where I watch what I say",
        "carrying_forward": "The sound of her real laugh, not the polite one"
    }
}

VARIANT_UNSENT_MESSAGE = {
    "name": "Unsent Message Seed",
    "description": "Story built around a message written but never sent. The text defines the unsaid words.",
    "fields": {
        "the_message": "What the message says",
        "who_its_for": "The intended recipient",
        "why_unsent": "Why they never hit send",
        "what_it_would_change": "What sending it might do",
        "what_they_did_instead": "The alternative action taken",
        "still_saved": "Whether they kept it and why"
    },
    "example": {
        "the_message": "I know you didn't mean it, but it still hurt.",
        "who_its_for": "My sister who always thinks she's just being honest",
        "why_unsent": "She'd turn it into a lecture about being sensitive",
        "what_it_would_change": "Maybe nothing. Maybe everything.",
        "what_they_did_instead": "Wrote it here instead",
        "still_saved": "In drafts, proof that I have words too"
    }
}

VARIANT_SMALL_MOMENT_BIG = {
    "name": "Small Moment, Big Meaning Seed",
    "description": "A tiny moment that carried unexpected weight. The text defines the seemingly insignificant thing.",
    "fields": {
        "the_small_thing": "The moment that seemed ordinary",
        "why_it_hit": "Why it affected them so deeply",
        "bigger_pattern": "What larger truth it revealed",
        "who_noticed": "Whether anyone else saw it",
        "internal_shift": "How it changed something inside",
        "still_thinking": "Why it keeps coming back"
    },
    "example": {
        "the_small_thing": "Dad saying 'good job' without looking up from his phone",
        "why_it_hit": "Realized I'd been performing for someone not watching",
        "bigger_pattern": "All those achievements for approval that never really came",
        "who_noticed": "Just me and the silence after",
        "internal_shift": "Started asking why I actually want things",
        "still_thinking": "When did I start needing witnesses to feel proud?"
    }
}

VARIANT_ALMOST_SAID = {
    "name": "Almost Said Seed",
    "description": "Story about the words that almost came out. The text defines what was swallowed.",
    "fields": {
        "what_almost_came_out": "The words on the edge of being spoken",
        "the_setting": "Where this almost-moment happened",
        "what_stopped_them": "What made them hold back",
        "the_safer_thing": "What they said instead",
        "consequence": "What happened because of silence",
        "next_time": "What they'd do if they could redo it"
    },
    "example": {
        "what_almost_came_out": "I'm not okay, and I need help.",
        "the_setting": "Family dinner when everyone asked how school was going",
        "what_stopped_them": "Mom's stressed face, Dad's distracted scrolling",
        "the_safer_thing": "'Fine, same as always'",
        "consequence": "They moved on, I stayed stuck",
        "next_time": "Maybe find a quieter moment, one-on-one"
    }
}

VARIANT_WHAT_THEY_DONT_KNOW = {
    "name": "What They Don't Know Seed",
    "description": "Revealing what others don't see behind the surface. The text defines the hidden truth.",
    "fields": {
        "the_surface": "What everyone sees and assumes",
        "the_truth": "What's really going on underneath",
        "why_hidden": "Why they don't show the real version",
        "closest_to_knowing": "Who might suspect something",
        "cost_of_hiding": "What hiding costs them",
        "would_change_if": "What would have to happen to reveal truth"
    },
    "example": {
        "the_surface": "The friend who always has advice for everyone",
        "the_truth": "I give advice so I don't have to take any for myself",
        "why_hidden": "Being needed feels safer than being vulnerable",
        "closest_to_knowing": "The friend who once asked if I was okay twice",
        "cost_of_hiding": "Loneliness disguised as being helpful",
        "would_change_if": "Someone asked the right question at the right time"
    }
}

VARIANT_QUIET_REBELLION = {
    "name": "Quiet Rebellion Seed",
    "description": "Small acts of resistance that no one notices. The text defines the silent defiance.",
    "fields": {
        "the_rule_they_break": "The expectation they refuse to meet",
        "how_they_do_it": "The subtle way they push back",
        "who_theyre_defying": "The person or system being resisted",
        "why_it_matters": "What this small act represents",
        "risk_if_caught": "What would happen if noticed",
        "victory_feeling": "The private satisfaction they get"
    },
    "example": {
        "the_rule_they_break": "Always being available when family texts",
        "how_they_do_it": "Leaving on read for exactly one hour before replying",
        "who_theyre_defying": "The expectation that I drop everything instantly",
        "why_it_matters": "Proof that my time is mine too",
        "risk_if_caught": "'Why didn't you answer? Is something wrong?'",
        "victory_feeling": "That hour belongs to no one but me"
    }
}

VARIANT_MIRROR_MOMENT = {
    "name": "Mirror Moment Seed",
    "description": "A moment of self-recognition or confrontation with self-image. The text defines what they saw.",
    "fields": {
        "what_they_saw": "The reflection or realization they faced",
        "expected_vs_actual": "How it differed from expectations",
        "trigger": "What led to this moment of seeing",
        "emotional_response": "First feeling when it hit",
        "action_taken": "What they did with this awareness",
        "ongoing_question": "What they're still asking themselves"
    },
    "example": {
        "what_they_saw": "I looked like my mom when she's angry",
        "expected_vs_actual": "I always thought I was nothing like her",
        "trigger": "Caught my reflection while yelling at my sibling",
        "emotional_response": "Shock, then shame, then sadness",
        "action_taken": "Apologized and went to my room to think",
        "ongoing_question": "Which parts of her am I choosing vs inheriting?"
    }
}

VARIANT_CHOSEN_FAMILY = {
    "name": "Chosen Family Seed",
    "description": "Story about finding belonging outside blood ties. The text defines the found connection.",
    "fields": {
        "the_connection": "Who or what became family",
        "the_moment_it_clicked": "When they realized this was their person/people",
        "what_was_missing": "What they weren't getting from blood family",
        "what_they_offer_each_other": "The mutual exchange of care",
        "how_its_different": "Why this feels more real",
        "gratitude_for": "What they're most thankful for"
    },
    "example": {
        "the_connection": "My friend's mom who actually asks how I'm feeling",
        "the_moment_it_clicked": "When she remembered something I said weeks ago",
        "what_was_missing": "Being listened to without being fixed or judged",
        "what_they_offer_each_other": "She gets to mother, I get to be soft",
        "how_its_different": "No history, no baggage, just care",
        "gratitude_for": "Showing me what attention can feel like"
    }
}

VARIANT_GROWING_APART = {
    "name": "Growing Apart Seed",
    "description": "Recognizing that a connection is changing or fading. The text defines what's drifting.",
    "fields": {
        "the_relationship": "Who or what is changing",
        "first_signs": "Early indicators something was different",
        "the_undeniable_moment": "When they couldn't ignore it anymore",
        "what_they_miss": "The specific thing they mourn",
        "acceptance_level": "How they're processing it",
        "hope_or_grief": "Whether there's still hope or just letting go"
    },
    "example": {
        "the_relationship": "Best friend since elementary school",
        "first_signs": "Conversations became updates, not real talks",
        "the_undeniable_moment": "Realized I hadn't told her anything real in months",
        "what_they_miss": "The person who knew me without explaining",
        "acceptance_level": "Mourning what was while protecting what's left",
        "hope_or_grief": "Maybe we're just different chapters, not ended books"
    }
}

VARIANT_PERMISSION_TO = {
    "name": "Permission To Seed",
    "description": "Story about finally allowing themselves something. The text defines what's being permitted.",
    "fields": {
        "the_permission": "What they're allowing themselves to do/feel/be",
        "who_denied_it_before": "Where the restriction came from",
        "what_changed": "What made them decide it was okay now",
        "how_it_feels": "The sensation of this new freedom",
        "what_they_feared": "What they thought would happen",
        "whats_next": "How this permission opens doors"
    },
    "example": {
        "the_permission": "To be mediocre at something I enjoy",
        "who_denied_it_before": "My own need to be the best or not try",
        "what_changed": "Watching someone enjoy being bad at something",
        "how_it_feels": "Like breathing room I didn't know I needed",
        "what_they_feared": "That being okay at things means I'm not special",
        "whats_next": "Maybe I can try things just for fun now"
    }
}

VARIANT_LEARNED_YOUNG = {
    "name": "Learned Young Seed",
    "description": "Realizing when a belief or behavior was first instilled. The text defines the early lesson.",
    "fields": {
        "the_belief": "What they learned early",
        "age_or_moment": "When it was taught",
        "who_taught_it": "Who or what was the teacher",
        "how_it_shaped_them": "The long-term effect",
        "questioning_now": "What's making them reconsider",
        "unlearning_process": "How they're trying to change it"
    },
    "example": {
        "the_belief": "That crying is manipulation",
        "age_or_moment": "Around 8, when mom said tears wouldn't work on her",
        "who_taught_it": "Parents who mistook emotion for drama",
        "how_it_shaped_them": "I learned to perform calm when I'm breaking inside",
        "questioning_now": "Therapy showing me emotions aren't weapons",
        "unlearning_process": "Letting myself cry alone first, then maybe with safe people"
    }
}

VARIANT_THE_VERSION_OF_ME = {
    "name": "The Version of Me Seed",
    "description": "Exploring different versions of self in different contexts. The text defines which version.",
    "fields": {
        "which_version": "The specific self being described",
        "where_it_appears": "The context where this version shows up",
        "how_its_different": "What makes this version distinct",
        "authenticity_level": "How real vs performed this version is",
        "what_others_see": "How others perceive this version",
        "wish_for_integration": "What they hope for these versions"
    },
    "example": {
        "which_version": "School Me vs Home Me",
        "where_it_appears": "School Me laughs more, Home Me is quiet",
        "how_its_different": "Energy levels, openness, even my voice changes",
        "authenticity_level": "Both are real, just different real",
        "what_others_see": "They'd be surprised the other exists",
        "wish_for_integration": "A space where I can just be all of me at once"
    }
}

VARIANT_EMOTIONAL_INHERITANCE = {
    "name": "Emotional Inheritance Seed",
    "description": "Recognizing patterns passed down through family. The text defines what was inherited.",
    "fields": {
        "what_was_passed_down": "The pattern or trait inherited",
        "from_whom": "Who it came from",
        "how_they_noticed": "The moment of recognition",
        "feeling_about_it": "How they feel about carrying this",
        "breaking_or_keeping": "Whether they want to continue or change it",
        "what_theyd_pass_on": "What they hope to give/not give forward"
    },
    "example": {
        "what_was_passed_down": "The silent treatment as conflict resolution",
        "from_whom": "Mom got it from grandma who got it from hers",
        "how_they_noticed": "Realized I go quiet when hurt, just like them",
        "feeling_about_it": "Angry that I learned it, sad that they did too",
        "breaking_or_keeping": "Trying to break it by speaking even when hard",
        "what_theyd_pass_on": "The courage to stay in the conversation"
    }
}

VARIANT_SAFE_PERSON = {
    "name": "Safe Person Seed",
    "description": "Story about who makes them feel safe enough to be real. The text defines the safe person.",
    "fields": {
        "who_they_are": "The person who creates safety",
        "what_makes_them_safe": "The specific quality that allows openness",
        "what_happens_around_them": "How the narrator changes in their presence",
        "contrast_with_others": "How this differs from other relationships",
        "how_it_was_earned": "The history that built this trust",
        "what_they_give_back": "How the narrator reciprocates"
    },
    "example": {
        "who_they_are": "My cousin who never judges, just listens",
        "what_makes_them_safe": "She asks questions but never pushes for answers",
        "what_happens_around_them": "I can say the ugly thoughts out loud",
        "contrast_with_others": "With others I edit myself before speaking",
        "how_it_was_earned": "She shared her mess with me first",
        "what_they_give_back": "Being her safe person too"
    }
}

VARIANT_HOLDING_SPACE = {
    "name": "Holding Space Seed",
    "description": "Being present for someone else's pain without fixing. The text defines the moment of holding.",
    "fields": {
        "who_needed_it": "The person being held",
        "what_was_happening": "The pain or situation being witnessed",
        "what_they_didnt_do": "The urge to fix that was resisted",
        "what_they_did_instead": "The simple presence offered",
        "what_it_cost": "The emotional labor of witnessing",
        "what_was_learned": "The lesson about support and silence"
    },
    "example": {
        "who_needed_it": "My friend after her parents announced divorce",
        "what_was_happening": "She was crying and couldn't form sentences",
        "what_they_didnt_do": "Didn't say 'it'll be okay' or try to relate",
        "what_they_did_instead": "Sat with her in silence, held her hand",
        "what_it_cost": "Fighting my own discomfort with her pain",
        "what_was_learned": "Sometimes presence is the only medicine"
    }
}

VARIANT_REWRITING_THE_STORY = {
    "name": "Rewriting the Story Seed",
    "description": "Changing the narrative about a past event or self. The text defines what's being rewritten.",
    "fields": {
        "the_old_story": "The previous narrative held",
        "what_it_protected": "Why that version was believed",
        "the_new_understanding": "The revised interpretation",
        "what_made_rewrite_possible": "What opened the new perspective",
        "how_it_feels_different": "The emotional shift from old to new",
        "ongoing_revision": "What parts are still being understood"
    },
    "example": {
        "the_old_story": "Dad left because I wasn't enough",
        "what_it_protected": "Made the pain feel like something I could control",
        "the_new_understanding": "Dad left because he couldn't handle his own stuff",
        "what_made_rewrite_possible": "Learning about his childhood from grandma",
        "how_it_feels_different": "Less shame, more sadness, more freedom",
        "ongoing_revision": "Still learning it wasn't about me being lovable"
    }
}


# =============================================================================
# FUSION VARIANT TEMPLATES - Combinations of existing templates
# These blend elements from multiple templates for unique story seeds
# =============================================================================

VARIANT_CONFESSION_MYSTERY = {
    "name": "Confession + Mystery Fusion",
    "description": "First-person confession that reveals a mystery element. Combines confession_moment's vulnerability with mystery's intrigue.",
    "fields": {
        "confession_hook": "Opening line promising a reveal",
        "hidden_mystery": "The mysterious element being confessed",
        "clues_dropped": "Hints the narrator has been leaving",
        "why_speaking_now": "What triggered this confession",
        "what_they_discovered": "The truth they finally uncovered",
        "unresolved_question": "What still haunts them"
    },
    "example": {
        "confession_hook": "I've been lying to everyone about what I found...",
        "hidden_mystery": "A pattern in old family photos that nobody else noticed",
        "clues_dropped": "Comments I made that everyone dismissed",
        "why_speaking_now": "I finally have proof I wasn't imagining it",
        "what_they_discovered": "The family secret hidden in plain sight",
        "unresolved_question": "Why did they hide this from me specifically?"
    }
}

VARIANT_OVERHEARD_TRANSFORMATION = {
    "name": "Overheard + Transformation Fusion",
    "description": "Something overheard triggers a major personal transformation. Combines overheard_truth's discovery with before_after's change arc.",
    "fields": {
        "what_was_heard": "The overheard words that changed everything",
        "before_hearing": "Who they were before this moment",
        "immediate_impact": "First reaction to hearing it",
        "transformation_process": "How they changed because of it",
        "after_hearing": "Who they became",
        "confrontation_choice": "Whether they ever addressed what they heard"
    },
    "example": {
        "what_was_heard": "Mom saying she wished I was more like my sister",
        "before_hearing": "The kid trying desperately to be enough",
        "immediate_impact": "Something broke and something clicked at the same time",
        "transformation_process": "Stopped trying to be what they wanted",
        "after_hearing": "Someone who defines their own worth",
        "confrontation_choice": "Never told them - the change speaks for itself"
    }
}

VARIANT_UNSENT_REBELLION = {
    "name": "Unsent Message + Quiet Rebellion Fusion",
    "description": "The unsent message IS the rebellion. Combines unsent_message's unspoken words with quiet_rebellion's silent defiance.",
    "fields": {
        "the_message": "What the message says",
        "who_its_for": "The authority figure it's addressed to",
        "why_writing_is_rebellion": "How even writing this is an act of defiance",
        "what_theyd_lose": "What would happen if it was sent",
        "power_in_keeping": "The strength in choosing not to send",
        "where_its_saved": "Where this rebellion lives"
    },
    "example": {
        "the_message": "I don't actually want the future you planned for me.",
        "who_its_for": "Dad who has my whole life mapped out",
        "why_writing_is_rebellion": "I was never supposed to have different dreams",
        "what_theyd_lose": "The family peace that depends on my compliance",
        "power_in_keeping": "I know my truth even if they don't",
        "where_its_saved": "In a notes app they'll never check"
    }
}

VARIANT_MIRROR_INHERITANCE = {
    "name": "Mirror Moment + Emotional Inheritance Fusion",
    "description": "Seeing inherited patterns in your own reflection. Combines mirror_moment's self-recognition with emotional_inheritance's generational themes.",
    "fields": {
        "what_they_saw": "The inherited trait visible in their reflection",
        "who_they_saw": "Which family member they recognized",
        "the_pattern": "The generational pattern being witnessed",
        "emotional_response": "How it felt to see this",
        "choice_moment": "The decision about continuing or breaking the pattern",
        "what_changes": "The first step toward change"
    },
    "example": {
        "what_they_saw": "The same tightness in my jaw mom gets when angry",
        "who_they_saw": "Three generations of women who hold it in until explosion",
        "the_pattern": "Silence until it's too much, then regret",
        "emotional_response": "Grief for all of us who learned this",
        "choice_moment": "Do I let this become automatic too?",
        "what_changes": "Speaking when it's small instead of waiting"
    }
}

VARIANT_CHOSEN_GROWING = {
    "name": "Chosen Family + Growing Apart Fusion",
    "description": "Finding new family while old connections fade. Combines chosen_family's found belonging with growing_apart's relationship changes.",
    "fields": {
        "fading_connection": "The relationship that's changing",
        "new_connection": "The chosen family being found",
        "what_old_gave": "What the fading relationship used to provide",
        "what_new_offers": "What the new connection gives instead",
        "guilt_feeling": "The complicated feelings about this shift",
        "acceptance": "Coming to terms with the change"
    },
    "example": {
        "fading_connection": "Best friend since childhood who doesn't get me anymore",
        "new_connection": "Online friends who understand without explaining",
        "what_old_gave": "History, shared memories, the comfort of being known",
        "what_new_offers": "Being seen for who I'm becoming, not who I was",
        "guilt_feeling": "Like I'm betraying something sacred",
        "acceptance": "People can be 'for a season' without it being failure"
    }
}

VARIANT_PARALLEL_PERMISSION = {
    "name": "Parallel Lives + Permission To Fusion",
    "description": "Imagining who you'd be if you'd given yourself permission earlier. Combines parallel_lives' what-ifs with permission_to's self-acceptance.",
    "fields": {
        "the_permission": "What they're finally allowing now",
        "earlier_version": "Who they were before permission",
        "parallel_version": "Who they might have been with earlier permission",
        "what_delayed_it": "Why they couldn't allow this before",
        "what_unlocked_it": "What finally made permission possible",
        "bridging_the_gap": "Connecting present self to possible self"
    },
    "example": {
        "the_permission": "To take up space without apologizing",
        "earlier_version": "The girl who made herself small to avoid attention",
        "parallel_version": "Someone confident who never learned to shrink",
        "what_delayed_it": "Being told 'don't be too much' so many times",
        "what_unlocked_it": "Meeting someone who celebrated 'too much'",
        "bridging_the_gap": "That parallel me isn't gone - she's just been waiting"
    }
}


# =============================================================================
# MISSING THEME TEMPLATES - Additional templates for primary audience
# =============================================================================

VARIANT_FIRST_BUTTERFLIES = {
    "name": "First Butterflies Seed",
    "description": "Light, innocent moments of first attraction - butterflies, nervousness, noticing someone. Not romance, just the feeling.",
    "fields": {
        "the_moment": "When the butterflies first appeared",
        "physical_feeling": "How it felt in the body",
        "what_they_noticed": "The specific thing that caught attention",
        "internal_panic": "The overthinking that followed",
        "acting_normal": "Trying to seem unaffected",
        "replay_loop": "The moment playing on repeat"
    },
    "example": {
        "the_moment": "They laughed at something I said, really laughed",
        "physical_feeling": "Stomach dropped, face got warm, forgot how to breathe",
        "what_they_noticed": "The way their eyes crinkle when they smile",
        "internal_panic": "Did I say something weird? Do they think I'm weird?",
        "acting_normal": "Looked at my phone like I got a text",
        "replay_loop": "That laugh. That laugh. That laugh."
    }
}

VARIANT_BODY_ACCEPTANCE = {
    "name": "Body Acceptance Seed",
    "description": "Journey of making peace with one's body - the struggles, small victories, and ongoing process of self-acceptance.",
    "fields": {
        "the_struggle": "What's been hardest to accept",
        "where_it_started": "When this struggle began",
        "the_voice": "What the critical inner voice says",
        "moment_of_shift": "A moment that changed perspective",
        "what_helps": "What makes it easier",
        "current_truth": "Where they are now with it"
    },
    "example": {
        "the_struggle": "Seeing photos of myself and not recognizing me",
        "where_it_started": "Middle school when someone made a comment",
        "the_voice": "'You'd be prettier if...' on repeat",
        "moment_of_shift": "Realizing my body carried me through hard things",
        "what_helps": "Unfollowing accounts that make me compare",
        "current_truth": "Some days are harder. Today I'm trying."
    }
}

VARIANT_FITTING_IN = {
    "name": "Fitting In Seed",
    "description": "Social anxiety, feeling like an outsider, the exhaustion of trying to belong. The gap between how you feel and how you appear.",
    "fields": {
        "the_situation": "Where the anxiety shows up",
        "what_others_see": "How they appear to others",
        "internal_reality": "What's actually happening inside",
        "the_exhaustion": "The cost of performing normal",
        "coping_mechanism": "How they get through it",
        "wish_for": "What they wish people understood"
    },
    "example": {
        "the_situation": "Group projects, lunch tables, parties",
        "what_others_see": "Quiet, maybe shy, probably fine",
        "internal_reality": "Heart racing, scripting every sentence, counting minutes",
        "the_exhaustion": "Going home and sleeping for hours after socializing",
        "coping_mechanism": "Bathroom breaks to breathe, texting someone safe",
        "wish_for": "That being social didn't feel like a performance"
    }
}

VARIANT_ONLINE_CONNECTION = {
    "name": "Online Connection Seed",
    "description": "Friendships formed online, parasocial relationships, the realness of digital connections vs dismissal from others.",
    "fields": {
        "the_connection": "Who/what the online connection is",
        "how_it_started": "How this connection formed",
        "what_it_provides": "What this relationship gives them",
        "others_opinion": "How others view this connection",
        "defense_of_realness": "Why it matters despite being 'online'",
        "complicated_feeling": "The part that's hard to explain"
    },
    "example": {
        "the_connection": "Friends from a Discord server I've never met",
        "how_it_started": "We bonded over the same niche interest three years ago",
        "what_it_provides": "They know me better than people who see me daily",
        "others_opinion": "'They're not real friends' - but they showed up when no one else did",
        "defense_of_realness": "We've talked through my worst moments",
        "complicated_feeling": "Mourning that we might never meet in person"
    }
}

VARIANT_FUTURE_ANXIETY = {
    "name": "Future Anxiety Seed",
    "description": "Anxiety about growing up, college, career, not knowing what you want. The pressure to have it figured out.",
    "fields": {
        "the_pressure": "The specific future pressure they feel",
        "source_of_pressure": "Where this pressure comes from",
        "what_theyre_supposed_to_know": "What everyone expects them to have figured out",
        "the_truth": "What they actually feel/know",
        "comparison_trap": "How others seem to have it together",
        "what_theyd_say_if_honest": "The thing they can't admit out loud"
    },
    "example": {
        "the_pressure": "Having a major picked, a plan, a direction",
        "source_of_pressure": "Family questions, college apps, everyone asking",
        "what_theyre_supposed_to_know": "What I want to do with my life",
        "the_truth": "I can barely decide what to eat for lunch",
        "comparison_trap": "Everyone else seems to have passions and plans",
        "what_theyd_say_if_honest": "I'm terrified of picking wrong and wasting my life"
    }
}

VARIANT_COMPARISON_TRAP = {
    "name": "Comparison Trap Seed",
    "description": "Social media comparison culture, measuring yourself against curated lives, the exhaustion of never being enough.",
    "fields": {
        "the_trigger": "What sets off the comparison spiral",
        "who_theyre_comparing_to": "The person/people they measure against",
        "what_it_does": "How comparison makes them feel",
        "logical_brain": "What they know rationally",
        "emotional_reality": "What they feel despite knowing better",
        "breaking_point": "When it becomes too much"
    },
    "example": {
        "the_trigger": "Scrolling and seeing someone's perfect life",
        "who_theyre_comparing_to": "Girls who seem to have it all figured out",
        "what_it_does": "Makes my own life feel small and behind",
        "logical_brain": "I know it's curated, I know it's highlight reels",
        "emotional_reality": "Still feels like proof that I'm failing somehow",
        "breaking_point": "Had to delete the app for my own sanity"
    }
}


# =============================================================================
# BLEND TEMPLATES - Combinations of new and existing templates
# =============================================================================

# Blends using new missing theme templates with each other
VARIANT_BUTTERFLIES_ANXIETY = {
    "name": "First Butterflies + Fitting In Blend",
    "description": "The intersection of first attraction and social anxiety - wanting to be noticed while also wanting to disappear.",
    "fields": {
        "the_feeling": "The butterflies mixed with panic",
        "what_they_want": "To be seen by them specifically",
        "what_they_fear": "Being seen by everyone else",
        "the_conflict": "Wanting attention but dreading it",
        "coping_attempt": "How they try to manage both",
        "internal_chaos": "The war between hope and fear"
    },
    "example": {
        "the_feeling": "Heart racing - half butterflies, half panic attack",
        "what_they_want": "For them to look at me, just me",
        "what_they_fear": "What if I say something stupid in front of everyone?",
        "the_conflict": "Wanting them to notice me while hoping I'm invisible to everyone else",
        "coping_attempt": "Standing close enough to be seen, far enough to escape",
        "internal_chaos": "Be cool be cool be cool - oh god they're looking this way"
    }
}

VARIANT_BODY_COMPARISON = {
    "name": "Body Acceptance + Comparison Trap Blend",
    "description": "The exhausting cycle of comparing your body to filtered images, knowing better but feeling worse.",
    "fields": {
        "the_scroll": "What they see online that triggers it",
        "the_mirror": "What they see when they look at themselves after",
        "the_knowledge": "What they know is true rationally",
        "the_feeling": "What they feel despite knowing",
        "the_exhaustion": "The tiredness of this cycle",
        "small_rebellion": "A tiny act of resistance against it"
    },
    "example": {
        "the_scroll": "Perfect bodies, perfect skin, perfect everything",
        "the_mirror": "All the ways I don't measure up",
        "the_knowledge": "Filters, angles, editing - none of it's real",
        "the_feeling": "But what if they're just naturally like that and I'm not?",
        "the_exhaustion": "I'm so tired of hating what I see",
        "small_rebellion": "Wearing the outfit anyway"
    }
}

VARIANT_ONLINE_FITTING = {
    "name": "Online Connection + Fitting In Blend",
    "description": "Finding belonging online because IRL fitting in feels impossible.",
    "fields": {
        "irl_struggle": "What makes belonging offline so hard",
        "online_ease": "Why online connections feel easier",
        "the_irony": "The strange reality of this situation",
        "what_irl_people_think": "How offline people view this",
        "the_truth": "What they wish people understood",
        "both_worlds": "Navigating between them"
    },
    "example": {
        "irl_struggle": "Every word feels scripted, every interaction exhausting",
        "online_ease": "I can be myself in text, think before I respond",
        "the_irony": "More 'real' with people I've never met than people I see daily",
        "what_irl_people_think": "'You should get out more' 'Those aren't real friends'",
        "the_truth": "They've seen me ugly cry at 3am - that's real enough",
        "both_worlds": "Code-switching between who they expect and who I actually am"
    }
}

VARIANT_FUTURE_COMPARISON = {
    "name": "Future Anxiety + Comparison Trap Blend",
    "description": "Comparing your uncertain future to everyone else's seemingly certain plans.",
    "fields": {
        "their_plans": "What everyone else seems to have figured out",
        "your_blank": "The emptiness where a plan should be",
        "the_question": "What everyone keeps asking",
        "the_lie": "What you say vs what's true",
        "the_spiral": "Where the comparison leads",
        "quiet_hope": "The thing you haven't told anyone"
    },
    "example": {
        "their_plans": "Med school, gap year, starting a business - everyone has A Thing",
        "your_blank": "A future that looks like a fog machine",
        "the_question": "'So what's your plan?' at every family dinner",
        "the_lie": "'Still figuring it out!' said with fake confidence",
        "the_spiral": "Maybe I'm just not the kind of person who has dreams",
        "quiet_hope": "Maybe not knowing yet means I could be anything"
    }
}

VARIANT_BODY_BUTTERFLIES = {
    "name": "Body Acceptance + First Butterflies Blend",
    "description": "Attraction complicated by body insecurity - wanting to be wanted while not believing you could be.",
    "fields": {
        "the_attraction": "What draws them to this person",
        "the_block": "What body insecurity whispers",
        "the_fantasy": "What they'd do if they weren't insecure",
        "the_reality": "What they actually do instead",
        "almost_moment": "A time they almost let themselves be seen",
        "the_wish": "What they want to believe"
    },
    "example": {
        "the_attraction": "The way they make everyone feel comfortable",
        "the_block": "'They'd never look at someone like me'",
        "the_fantasy": "Walk up, be confident, just talk to them",
        "the_reality": "Look away, hide, convince myself it's not worth trying",
        "almost_moment": "They smiled at me and I almost smiled back before I remembered",
        "the_wish": "That I could see myself the way I see everyone else"
    }
}

VARIANT_ONLINE_FUTURE = {
    "name": "Online Connection + Future Anxiety Blend",
    "description": "Online friends who understand your future fears when IRL people just add pressure.",
    "fields": {
        "irl_pressure": "What people offline keep saying",
        "online_understanding": "What online friends actually get",
        "the_conversation": "A moment of real support online",
        "the_relief": "What it feels like to be understood",
        "the_gap": "The difference between these two worlds",
        "shared_uncertainty": "Finding others in the same fog"
    },
    "example": {
        "irl_pressure": "'You need to start thinking seriously about your future'",
        "online_understanding": "'Same, I have no idea what I'm doing either'",
        "the_conversation": "3am voice chat where we all admitted we're terrified",
        "the_relief": "Not being the only one who doesn't have it figured out",
        "the_gap": "Online: 'it's okay to not know' / Offline: 'you should know by now'",
        "shared_uncertainty": "Building a support system of equally lost people"
    }
}

VARIANT_FITTING_COMPARISON = {
    "name": "Fitting In + Comparison Trap Blend",
    "description": "Social anxiety amplified by comparing yourself to people who seem to belong effortlessly.",
    "fields": {
        "them": "The people who seem to fit naturally",
        "you": "How you feel in comparison",
        "the_performance": "What belonging looks like when you're faking it",
        "the_exhaustion": "The cost of performing normal",
        "the_question": "What you can't stop wondering",
        "secret_truth": "What you suspect but can't confirm"
    },
    "example": {
        "them": "Walking into rooms like they own them, effortless conversation",
        "you": "Calculating every word, planning bathroom escape routes",
        "the_performance": "Laughing at the right times, nodding along, seeming present",
        "the_exhaustion": "Social hangover that lasts for days",
        "the_question": "Are they actually confident or just better at pretending?",
        "secret_truth": "Maybe everyone's performing and I just think I'm the only one"
    }
}

# Blends with older existing templates
VARIANT_CONFESSION_BODY = {
    "name": "Confession Moment + Body Acceptance Blend",
    "description": "Finally confessing the body image struggles you've been hiding.",
    "fields": {
        "the_secret": "What you've been hiding about how you see yourself",
        "who_youre_telling": "Who finally gets to hear this",
        "why_now": "What made this the moment",
        "the_hardest_part": "What's most difficult to admit",
        "their_response": "What you hope/fear they'll say",
        "after_speaking": "How it feels to have said it"
    },
    "example": {
        "the_secret": "I've never liked a single photo of myself",
        "who_youre_telling": "My best friend who doesn't know how bad it is",
        "why_now": "I can't keep pretending I'm fine",
        "the_hardest_part": "That I spend hours some days just... hating",
        "their_response": "Please don't tell me I'm beautiful, just tell me you understand",
        "after_speaking": "Lighter, even though nothing's fixed"
    }
}

VARIANT_UNSENT_FUTURE = {
    "name": "Unsent Message + Future Anxiety Blend",
    "description": "The message you'll never send about the pressure to have your life figured out.",
    "fields": {
        "to_whom": "Who the message is addressed to",
        "the_message": "What you'd say if you could",
        "what_sparked_it": "What made you want to write this",
        "why_unsent": "Why you'll never actually send it",
        "what_youd_need": "What you actually need from them",
        "instead": "What you'll say instead if anything"
    },
    "example": {
        "to_whom": "Mom, Dad, everyone who keeps asking about my plans",
        "the_message": "Your 'helpful' questions feel like you're measuring my worth by my resume",
        "what_sparked_it": "Another dinner where my future was the main course",
        "why_unsent": "They'd just worry more and ask different questions",
        "what_youd_need": "'I believe in you even if you don't know yet'",
        "instead": "'Still exploring my options!' with a smile"
    }
}

VARIANT_MIRROR_BODY = {
    "name": "Mirror Moment + Body Acceptance Blend",
    "description": "A moment in the mirror that changes how you see yourself - for better or worse.",
    "fields": {
        "the_moment": "The specific mirror moment",
        "usual_script": "What you usually think/see",
        "the_shift": "What was different this time",
        "new_thought": "A thought you've never had before",
        "what_it_means": "What this might change",
        "still_uncertain": "The doubt that remains"
    },
    "example": {
        "the_moment": "Getting out of the shower, not avoiding the mirror for once",
        "usual_script": "Catalog of flaws, comparison to an impossible standard",
        "the_shift": "Seeing tired eyes instead of 'wrong' features",
        "new_thought": "This body has been fighting for me while I've been fighting against it",
        "what_it_means": "Maybe we can be on the same team",
        "still_uncertain": "Tomorrow I might hate it again, but today was different"
    }
}

VARIANT_GROWING_ONLINE = {
    "name": "Growing Apart + Online Connection Blend",
    "description": "Growing apart from IRL friends while growing closer to online ones.",
    "fields": {
        "the_old_friend": "The IRL friendship that's fading",
        "the_new_friend": "The online connection that's growing",
        "what_changed": "When you noticed the shift",
        "the_guilt": "Complicated feelings about this",
        "the_defense": "What you'd say if questioned",
        "the_truth": "What you know in your heart"
    },
    "example": {
        "the_old_friend": "Known her since third grade, but conversations feel like work now",
        "the_new_friend": "Met in a server six months ago, tells me things they don't tell anyone",
        "what_changed": "Realized I was excited to go home and text them, not to see her",
        "the_guilt": "Am I a bad friend? Am I replacing her?",
        "the_defense": "Connection isn't measured in proximity",
        "the_truth": "People grow in different directions. It's sad but it's okay."
    }
}

VARIANT_QUIET_BODY = {
    "name": "Quiet Rebellion + Body Acceptance Blend",
    "description": "Small acts of rebellion against body expectations - wearing what you want, eating what you want.",
    "fields": {
        "the_rule": "The body 'rule' you're breaking",
        "who_made_it": "Where this rule came from",
        "the_rebellion": "Your quiet act of defiance",
        "the_fear": "What you're scared of happening",
        "the_power": "What it feels like to do it anyway",
        "the_message": "What you're telling yourself"
    },
    "example": {
        "the_rule": "'Girls like you shouldn't wear that'",
        "who_made_it": "Magazine covers, comments, looks that linger too long",
        "the_rebellion": "Wearing the crop top anyway",
        "the_fear": "People staring, people laughing, people confirming what I fear",
        "the_power": "Walking out the door with my stomach visible to the world",
        "the_message": "My body is allowed to exist in spaces, in clothes, in public"
    }
}

VARIANT_CHOSEN_ONLINE = {
    "name": "Chosen Family + Online Connection Blend",
    "description": "Building a chosen family of online friends who feel more like home than home does.",
    "fields": {
        "the_group": "Who this online family is",
        "how_found": "How you found each other",
        "what_they_give": "What this family provides",
        "irl_gap": "What's missing in offline relationships",
        "defining_moment": "When you knew this was family",
        "future_hope": "What you hope for this connection"
    },
    "example": {
        "the_group": "Five people scattered across four time zones",
        "how_found": "A fandom that became so much more than the show",
        "what_they_give": "Unconditional support, 2am check-ins, inside jokes that span years",
        "irl_gap": "Family that loves conditions, friends who don't really know me",
        "defining_moment": "When they pooled money to send me a care package during my worst week",
        "future_hope": "One day we'll all be in the same room"
    }
}

VARIANT_PERMISSION_BODY = {
    "name": "Permission To + Body Acceptance Blend",
    "description": "Giving yourself permission to stop fighting your body.",
    "fields": {
        "the_permission": "What you're finally allowing",
        "the_war": "What the fight has been like",
        "what_triggered": "What made you ready to stop",
        "the_fear": "What you're scared will happen if you stop",
        "the_relief": "What peace might feel like",
        "first_step": "The first thing you're doing differently"
    },
    "example": {
        "the_permission": "To not hate what I see",
        "the_war": "Years of diets, disguises, avoiding cameras",
        "what_triggered": "Realized I don't remember a time I liked my body",
        "the_fear": "If I stop fighting, will I 'let myself go'?",
        "the_relief": "What would it be like to just... exist? Without the commentary?",
        "first_step": "Eating when I'm hungry without negotiating with myself"
    }
}

VARIANT_SMALL_COMPARISON = {
    "name": "Small Moment Big + Comparison Trap Blend",
    "description": "A small moment that reveals how deep the comparison runs.",
    "fields": {
        "the_small_thing": "The tiny thing that set it off",
        "why_big": "Why something so small hit so hard",
        "the_comparison": "Who you compared yourself to",
        "the_spiral": "Where it led mentally",
        "the_realization": "What you understood about yourself",
        "what_now": "Where you go from here"
    },
    "example": {
        "the_small_thing": "She got more likes on a similar photo",
        "why_big": "Because it confirmed what I already believed",
        "the_comparison": "Her: effortless. Me: trying so hard and still less",
        "the_spiral": "Maybe I'm just... less likable, less pretty, less everything",
        "the_realization": "I've been measuring my worth in double-taps",
        "what_now": "Maybe worth isn't a number. Maybe it never was."
    }
}

VARIANT_IDENTITY_FITTING = {
    "name": "Identity Power + Fitting In Blend",
    "description": "The tension between being yourself and fitting in - choosing authenticity over belonging.",
    "fields": {
        "who_you_are": "The authentic self that doesn't fit",
        "what_fitting_requires": "What you'd have to change to belong",
        "the_cost": "What hiding costs you",
        "the_risk": "What being yourself risks",
        "the_choice": "The decision you're facing",
        "the_power": "What you gain from choosing you"
    },
    "example": {
        "who_you_are": "Weird interests, strong opinions, too much or not enough",
        "what_fitting_requires": "Dulling the edges, laughing at the right things, caring about the right stuff",
        "the_cost": "Feeling like a ghost in my own life",
        "the_risk": "Being alone, being mocked, being the weird one",
        "the_choice": "Keep performing or let them see",
        "the_power": "The exhaustion of pretending is worse than the fear of being seen"
    }
}

VARIANT_LEARNED_BODY = {
    "name": "Learned Young + Body Acceptance Blend",
    "description": "The body beliefs you absorbed young and are now trying to unlearn.",
    "fields": {
        "the_lesson": "What you learned about bodies young",
        "who_taught": "Where this belief came from",
        "how_it_stuck": "How it became part of you",
        "the_damage": "What it's cost you",
        "the_unlearning": "What you're trying to believe instead",
        "the_work": "How you're doing that work"
    },
    "example": {
        "the_lesson": "That taking up space was bad, that hunger was weakness",
        "who_taught": "Mom's comments about her own body, magazines, everything",
        "how_it_stuck": "Started monitoring myself before I knew what I was monitoring",
        "the_damage": "Never just... existing. Always calculating, comparing, controlling",
        "the_unlearning": "My body is a home, not a project",
        "the_work": "Catching the old thoughts, replacing them, being patient with the process"
    }
}

VARIANT_SAFE_ONLINE = {
    "name": "Safe Person + Online Connection Blend",
    "description": "When your safest person is someone you've never met in person.",
    "fields": {
        "who_they_are": "This person you've found online",
        "how_safety_built": "How they became safe",
        "what_you_share": "What you tell them that you tell no one else",
        "the_paradox": "The strange reality of this",
        "what_others_say": "What IRL people think about this",
        "why_it_works": "Why this works when other things don't"
    },
    "example": {
        "who_they_are": "Someone I met on tumblr five years ago, never seen their face",
        "how_safety_built": "Slow sharing, matched vulnerability, never judgment",
        "what_you_share": "The thoughts I can't say out loud, the fears that feel too dramatic",
        "the_paradox": "A stranger knows me better than my family",
        "what_others_say": "'That's not a real friendship' 'You should talk to real people'",
        "why_it_works": "No history to disappoint, no face to perform for"
    }
}

VARIANT_REWRITING_BODY = {
    "name": "Rewriting Story + Body Acceptance Blend",
    "description": "Rewriting the story you've told yourself about your body.",
    "fields": {
        "old_story": "The narrative you've carried about your body",
        "who_wrote_it": "Where this story came from",
        "the_chapter": "The moment that defined this story",
        "new_story": "What you want to believe instead",
        "the_evidence": "What supports the new story",
        "work_in_progress": "How the rewriting is going"
    },
    "example": {
        "old_story": "'My body is wrong and needs fixing'",
        "who_wrote_it": "Diet culture, that one comment in middle school, mirrors that felt like enemies",
        "the_chapter": "The first time someone laughed at me in a swimsuit",
        "new_story": "My body is trying its best. So am I.",
        "the_evidence": "It healed when I was sick. It carries me through hard days. It's trying.",
        "work_in_progress": "Some days the old story wins. But less often now."
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
    # Story seed templates for US women 13-20
    "confession_moment": VARIANT_CONFESSION_MOMENT,
    "before_after": VARIANT_BEFORE_AFTER,
    "overheard_truth": VARIANT_OVERHEARD_TRUTH,
    "parallel_lives": VARIANT_PARALLEL_LIVES,
    "last_time": VARIANT_LAST_TIME,
    "unsent_message": VARIANT_UNSENT_MESSAGE,
    "small_moment_big": VARIANT_SMALL_MOMENT_BIG,
    "almost_said": VARIANT_ALMOST_SAID,
    "what_they_dont_know": VARIANT_WHAT_THEY_DONT_KNOW,
    "quiet_rebellion": VARIANT_QUIET_REBELLION,
    "mirror_moment": VARIANT_MIRROR_MOMENT,
    "chosen_family": VARIANT_CHOSEN_FAMILY,
    "growing_apart": VARIANT_GROWING_APART,
    "permission_to": VARIANT_PERMISSION_TO,
    "learned_young": VARIANT_LEARNED_YOUNG,
    "the_version_of_me": VARIANT_THE_VERSION_OF_ME,
    "emotional_inheritance": VARIANT_EMOTIONAL_INHERITANCE,
    "safe_person": VARIANT_SAFE_PERSON,
    "holding_space": VARIANT_HOLDING_SPACE,
    "rewriting_the_story": VARIANT_REWRITING_THE_STORY,
    # Fusion variants - combinations of existing templates
    "confession_mystery": VARIANT_CONFESSION_MYSTERY,
    "overheard_transformation": VARIANT_OVERHEARD_TRANSFORMATION,
    "unsent_rebellion": VARIANT_UNSENT_REBELLION,
    "mirror_inheritance": VARIANT_MIRROR_INHERITANCE,
    "chosen_growing": VARIANT_CHOSEN_GROWING,
    "parallel_permission": VARIANT_PARALLEL_PERMISSION,
    # Missing theme templates - crucial for primary audience
    "first_butterflies": VARIANT_FIRST_BUTTERFLIES,
    "body_acceptance": VARIANT_BODY_ACCEPTANCE,
    "fitting_in": VARIANT_FITTING_IN,
    "online_connection": VARIANT_ONLINE_CONNECTION,
    "future_anxiety": VARIANT_FUTURE_ANXIETY,
    "comparison_trap": VARIANT_COMPARISON_TRAP,
    # Blend templates - new themes with each other
    "butterflies_anxiety": VARIANT_BUTTERFLIES_ANXIETY,
    "body_comparison": VARIANT_BODY_COMPARISON,
    "online_fitting": VARIANT_ONLINE_FITTING,
    "future_comparison": VARIANT_FUTURE_COMPARISON,
    "body_butterflies": VARIANT_BODY_BUTTERFLIES,
    "online_future": VARIANT_ONLINE_FUTURE,
    "fitting_comparison": VARIANT_FITTING_COMPARISON,
    # Blend templates - new themes with older templates
    "confession_body": VARIANT_CONFESSION_BODY,
    "unsent_future": VARIANT_UNSENT_FUTURE,
    "mirror_body": VARIANT_MIRROR_BODY,
    "growing_online": VARIANT_GROWING_ONLINE,
    "quiet_body": VARIANT_QUIET_BODY,
    "chosen_online": VARIANT_CHOSEN_ONLINE,
    "permission_body": VARIANT_PERMISSION_BODY,
    "small_comparison": VARIANT_SMALL_COMPARISON,
    "identity_fitting": VARIANT_IDENTITY_FITTING,
    "learned_body": VARIANT_LEARNED_BODY,
    "safe_online": VARIANT_SAFE_ONLINE,
    "rewriting_body": VARIANT_REWRITING_BODY,
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
# Weights tuned for:
#   - Primary audience: US women 13-22
#   - Ultra-primary (core) audience: 15-18 (highest weights)
# Mobile-first content optimized
VARIANT_WEIGHTS = {
    # ==========================================================================
    # ORIGINAL TEMPLATES - varied appeal across age range
    # ==========================================================================
    "emotion_first": 75,      # Good for all ages, slightly less for ultra-primary
    "mystery": 85,            # Appeals to full range, especially 13-16
    "skeleton": 35,           # Too structured, less appealing for teens
    "shortform": 100,         # ULTRA-PRIMARY - mobile-first, perfect for 15-18
    "niche_blend": 45,        # More complex, appeals to older 19-22
    "minimal": 55,            # Moderate - simple but less engaging
    "4point": 25,             # Too academic/structured for teens
    "hook_frame": 65,         # Good hook appeal, moderate for teens
    "shortform2": 100,        # ULTRA-PRIMARY - mobile-first, perfect for 15-18
    "genre": 50,              # Varies by genre, moderate overall
    "scene_seed": 35,         # More cinematic, appeals to older 19-22
    
    # ==========================================================================
    # CREATIVE GENRE-BASED TEMPLATES - teen appeal focus
    # ==========================================================================
    "soft_supernatural": 92,   # HIGH - friendship + mystery, strong 13-18 appeal
    "light_mystery": 88,       # HIGH - puzzles appeal to 13-17
    "scifi_school": 85,        # HIGH - school + tech, 14-18 sweet spot
    "safe_survival": 70,       # MODERATE - adventure, broader appeal
    "emotional_drama": 100,    # ULTRA-PRIMARY - emotion resonates 15-18 peak
    "rivals_allies": 82,       # HIGH - competition themes, 14-18 focus
    "identity_power": 100,     # ULTRA-PRIMARY - identity crucial for 15-18
    "ai_companion": 72,        # MODERATE-HIGH - tech interest varies
    "urban_quest": 58,         # MODERATE - adventure, less specific
    "magical_aesthetic": 95,   # VERY HIGH - aesthetics peak 14-18
    
    # ==========================================================================
    # REDDIT-STYLE DRAMA TEMPLATES - high relatability
    # ==========================================================================
    "family_drama": 85,        # HIGH - family relatable across 13-22
    "social_home": 95,         # VERY HIGH - social media + family, 15-19 peak
    "realistic_mystery": 72,   # MODERATE-HIGH - mystery + drama
    "school_family": 98,       # ULTRA-PRIMARY - school themes peak 15-18
    "personal_voice": 100,     # ULTRA-PRIMARY - first-person emotional, 15-18 core
    
    # ==========================================================================
    # STORY SEED TEMPLATES - optimized for 15-18 ultra-primary
    # ==========================================================================
    "confession_moment": 100,      # ULTRA-PRIMARY - confession style peak 15-18
    "before_after": 88,            # HIGH - transformation, good 14-20
    "overheard_truth": 100,        # ULTRA-PRIMARY - dramatic discovery, 15-18 core
    "parallel_lives": 78,          # HIGH - introspective, better for 17-22
    "last_time": 90,               # VERY HIGH - nostalgia hits 16-22
    "unsent_message": 100,         # ULTRA-PRIMARY - deeply relatable 15-18
    "small_moment_big": 92,        # VERY HIGH - emotional depth 15-19
    "almost_said": 100,            # ULTRA-PRIMARY - unspoken truths 15-18 core
    "what_they_dont_know": 95,     # VERY HIGH - hidden self theme 15-19
    "quiet_rebellion": 100,        # ULTRA-PRIMARY - teen empowerment 15-18 peak
    "mirror_moment": 82,           # HIGH - self-recognition 16-20
    "chosen_family": 92,           # VERY HIGH - found family 14-20
    "growing_apart": 95,           # VERY HIGH - friendship loss peak 15-18
    "permission_to": 100,          # ULTRA-PRIMARY - self-acceptance 15-18 core
    "learned_young": 85,           # HIGH - family patterns 16-22
    "the_version_of_me": 100,      # ULTRA-PRIMARY - identity exploration 15-18
    "emotional_inheritance": 78,   # HIGH - generational, better 17-22
    "safe_person": 92,             # VERY HIGH - trust themes 15-19
    "holding_space": 75,           # HIGH - mature emotional theme 17-22
    "rewriting_the_story": 98,     # ULTRA-PRIMARY - healing narrative 15-19
    
    # ==========================================================================
    # FUSION VARIANTS - unique story seed combinations
    # ==========================================================================
    "confession_mystery": 100,         # ULTRA-PRIMARY - confession + mystery 15-18
    "overheard_transformation": 98,    # ULTRA-PRIMARY - discovery + change 15-18
    "unsent_rebellion": 95,            # VERY HIGH - silent defiance 15-19
    "mirror_inheritance": 80,          # HIGH - family patterns 17-22
    "chosen_growing": 92,              # VERY HIGH - found family + change 15-19
    "parallel_permission": 95,         # VERY HIGH - what-if + acceptance 15-19
    
    # ==========================================================================
    # MISSING THEME TEMPLATES - crucial for 15-18 core audience
    # ==========================================================================
    "first_butterflies": 100,      # ULTRA-PRIMARY - universal teen experience 14-17
    "body_acceptance": 100,        # ULTRA-PRIMARY - peak relevance 15-18
    "fitting_in": 100,             # ULTRA-PRIMARY - core 15-18 anxiety
    "online_connection": 98,       # ULTRA-PRIMARY - digital native 15-18
    "future_anxiety": 100,         # ULTRA-PRIMARY - college pressure 16-18 peak
    "comparison_trap": 100,        # ULTRA-PRIMARY - social media 15-18
    
    # ==========================================================================
    # BLEND TEMPLATES - new themes combined with each other
    # ==========================================================================
    "butterflies_anxiety": 100,    # ULTRA-PRIMARY - attraction + social anxiety 15-17
    "body_comparison": 100,        # ULTRA-PRIMARY - body image + comparison 15-18
    "online_fitting": 98,          # ULTRA-PRIMARY - online vs IRL 15-18
    "future_comparison": 100,      # ULTRA-PRIMARY - future + comparison 16-18
    "body_butterflies": 98,        # ULTRA-PRIMARY - attraction + body image 15-17
    "online_future": 92,           # VERY HIGH - online support 15-19
    "fitting_comparison": 100,     # ULTRA-PRIMARY - social anxiety spiral 15-18
    
    # ==========================================================================
    # BLEND TEMPLATES - new themes with older templates
    # ==========================================================================
    "confession_body": 100,        # ULTRA-PRIMARY - confessing struggles 15-18
    "unsent_future": 98,           # ULTRA-PRIMARY - unsent pressure 16-18
    "mirror_body": 100,            # ULTRA-PRIMARY - mirror + body 15-18
    "growing_online": 90,          # VERY HIGH - IRL/online shift 15-19
    "quiet_body": 100,             # ULTRA-PRIMARY - body rebellion 15-18
    "chosen_online": 95,           # VERY HIGH - online chosen family 15-19
    "permission_body": 100,        # ULTRA-PRIMARY - body acceptance 15-18
    "small_comparison": 98,        # ULTRA-PRIMARY - small trigger spiral 15-18
    "identity_fitting": 100,       # ULTRA-PRIMARY - authenticity vs belonging 15-18
    "learned_body": 95,            # VERY HIGH - unlearning beliefs 16-20
    "safe_online": 92,             # VERY HIGH - online safe person 15-19
    "rewriting_body": 100,         # ULTRA-PRIMARY - body narrative 15-18
}

# Default number of ideas to generate
DEFAULT_IDEA_COUNT = 10

# Default decay factor for variant selection (0.4 = new weight is 40% of current)
DEFAULT_DECAY_FACTOR = 0.4

# Minimum weight after decay (ensures variant can still be selected even after multiple uses)
# Weight scale is 0-100, minimum is 2 to ensure variants remain selectable
MIN_DECAY_WEIGHT = 2

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


def pick_multiple_weighted_variants(count: int = DEFAULT_IDEA_COUNT, seed: int = None, allow_duplicates: bool = True, decay_factor: float = DEFAULT_DECAY_FACTOR) -> List[str]:
    """Pick multiple variant types using weighted random selection with usage decay.
    
    Each variant is picked based on weights. When a variant is selected, its weight
    is reduced by the decay_factor for subsequent selections within this call.
    This promotes variety while still allowing duplicates.
    
    Note: When allow_duplicates=False, the function may return fewer variants than
    requested if all available variants have been selected.
    
    Args:
        count: Number of variants to pick (default: 10)
        seed: Optional seed for reproducible selection
        allow_duplicates: If True, same variant can be picked multiple times (with reduced weight)
        decay_factor: Multiplier applied to weight after each usage (0.0-1.0). 
                     Default 0.5 means each usage halves the probability.
                     Set to 1.0 to disable decay (original behavior).
        
    Returns:
        List of selected variant type names. May be shorter than count if 
        allow_duplicates=False and all variants have been selected.
        
    Raises:
        ValueError: If decay_factor is not between 0.0 and 1.0 (inclusive)
    """
    # Validate decay_factor
    if not (0.0 <= decay_factor <= 1.0):
        raise ValueError(f"decay_factor must be between 0.0 and 1.0, got {decay_factor}")
    
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()
    
    variants = list(VARIANT_WEIGHTS.keys())
    # Start with original weights - not persistent across runs
    current_weights = {v: float(VARIANT_WEIGHTS[v]) for v in variants}
    
    selected = []
    
    for _ in range(count):
        # Build weight list from current (possibly decayed) weights
        weights = [current_weights[v] for v in variants]
        
        # Filter out zero-weight variants if not allowing duplicates
        if not allow_duplicates:
            available = [(v, w) for v, w in zip(variants, weights) if w > 0]
            if not available:
                break  # No more variants available
            available_variants = [v for v, _ in available]
            available_weights = [w for _, w in available]
            choice = rng.choices(available_variants, weights=available_weights, k=1)[0]
        else:
            choice = rng.choices(variants, weights=weights, k=1)[0]
        
        selected.append(choice)
        
        # Apply decay to the selected variant's weight for next iteration
        if allow_duplicates:
            # Reduce weight but keep positive minimum to still allow selection
            current_weights[choice] = max(MIN_DECAY_WEIGHT, current_weights[choice] * decay_factor)
        else:
            # Set to 0 to prevent re-selection
            current_weights[choice] = 0
    
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
    # Story seed variants for US women 13-20
    elif variant_name == "confession_moment":
        result.update(_create_confession_moment_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "before_after":
        result.update(_create_before_after_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "overheard_truth":
        result.update(_create_overheard_truth_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "parallel_lives":
        result.update(_create_parallel_lives_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "last_time":
        result.update(_create_last_time_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "unsent_message":
        result.update(_create_unsent_message_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "small_moment_big":
        result.update(_create_small_moment_big_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "almost_said":
        result.update(_create_almost_said_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "what_they_dont_know":
        result.update(_create_what_they_dont_know_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "quiet_rebellion":
        result.update(_create_quiet_rebellion_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "mirror_moment":
        result.update(_create_mirror_moment_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "chosen_family":
        result.update(_create_chosen_family_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "growing_apart":
        result.update(_create_growing_apart_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "permission_to":
        result.update(_create_permission_to_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "learned_young":
        result.update(_create_learned_young_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "the_version_of_me":
        result.update(_create_the_version_of_me_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "emotional_inheritance":
        result.update(_create_emotional_inheritance_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "safe_person":
        result.update(_create_safe_person_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "holding_space":
        result.update(_create_holding_space_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "rewriting_the_story":
        result.update(_create_rewriting_the_story_variant(title, description, kwargs, seed, variation_index))
    # Fusion variants
    elif variant_name == "confession_mystery":
        result.update(_create_confession_mystery_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "overheard_transformation":
        result.update(_create_overheard_transformation_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "unsent_rebellion":
        result.update(_create_unsent_rebellion_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "mirror_inheritance":
        result.update(_create_mirror_inheritance_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "chosen_growing":
        result.update(_create_chosen_growing_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "parallel_permission":
        result.update(_create_parallel_permission_variant(title, description, kwargs, seed, variation_index))
    # Missing theme templates
    elif variant_name == "first_butterflies":
        result.update(_create_first_butterflies_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "body_acceptance":
        result.update(_create_body_acceptance_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "fitting_in":
        result.update(_create_fitting_in_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "online_connection":
        result.update(_create_online_connection_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "future_anxiety":
        result.update(_create_future_anxiety_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "comparison_trap":
        result.update(_create_comparison_trap_variant(title, description, kwargs, seed, variation_index))
    # Blend templates - new themes combined
    elif variant_name == "butterflies_anxiety":
        result.update(_create_butterflies_anxiety_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "body_comparison":
        result.update(_create_body_comparison_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "online_fitting":
        result.update(_create_online_fitting_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "future_comparison":
        result.update(_create_future_comparison_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "body_butterflies":
        result.update(_create_body_butterflies_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "online_future":
        result.update(_create_online_future_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "fitting_comparison":
        result.update(_create_fitting_comparison_variant(title, description, kwargs, seed, variation_index))
    # Blend templates - new with older
    elif variant_name == "confession_body":
        result.update(_create_confession_body_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "unsent_future":
        result.update(_create_unsent_future_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "mirror_body":
        result.update(_create_mirror_body_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "growing_online":
        result.update(_create_growing_online_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "quiet_body":
        result.update(_create_quiet_body_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "chosen_online":
        result.update(_create_chosen_online_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "permission_body":
        result.update(_create_permission_body_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "small_comparison":
        result.update(_create_small_comparison_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "identity_fitting":
        result.update(_create_identity_fitting_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "learned_body":
        result.update(_create_learned_body_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "safe_online":
        result.update(_create_safe_online_variant(title, description, kwargs, seed, variation_index))
    elif variant_name == "rewriting_body":
        result.update(_create_rewriting_body_variant(title, description, kwargs, seed, variation_index))
    
    # Add target audience info to all variants
    result["target_audience"] = _get_target_audience_info()
    
    return result


def create_ideas_from_input(
    text_input: str,
    count: int = DEFAULT_IDEA_COUNT,
    seed: int = None,
    allow_duplicate_types: bool = True,
    description: str = "",
    decay_factor: float = DEFAULT_DECAY_FACTOR,
    **kwargs
) -> List[Dict[str, Any]]:
    """Create multiple ideas from a single text input using weighted random variant selection.
    
    This is the main entry point for the default idea creation flow:
    - Takes simple text input
    - Creates 10 ideas by default
    - Each idea gets a randomly selected variant type (weighted by audience preference)
    - Already-used variant types have decreased probability (but can still be selected)
    
    Variant types are weighted to favor templates that appeal to:
    - Primary audience: US girls 13-15 (emotion, identity, friendship, aesthetics)
    - Secondary audience: US boys 12-17 (competition, tech, puzzles, adventure)
    - Tertiary audience: US women 10-22 (emotion, drama, empowerment)
    
    The decay_factor controls how much a variant's probability decreases after each use:
    - 0.5 (default): Each usage halves the probability
    - 0.3: More aggressive decay, promotes higher variety
    - 1.0: No decay (original behavior, equal probability for duplicates)
    
    Note: Decay is NOT persistent - each new call starts with original weights.
    
    Args:
        text_input: The text prompt/input to generate ideas from
        count: Number of ideas to create (default: 10)
        seed: Optional seed for reproducible variant selection
        allow_duplicate_types: If True, same variant type can be used for multiple ideas (with reduced weight)
        description: Optional description to enrich the variants
        decay_factor: Multiplier applied to weight after each usage (0.0-1.0). Default 0.5.
        **kwargs: Additional parameters passed to each variant
        
    Returns:
        List of idea variant dictionaries
        
    Raises:
        ValueError: If text_input is empty or decay_factor is not between 0.0 and 1.0
    """
    if not text_input or not text_input.strip():
        raise ValueError("Text input cannot be empty")
    
    # Validation is handled in pick_multiple_weighted_variants, but provide clearer error message
    if not (0.0 <= decay_factor <= 1.0):
        raise ValueError(f"decay_factor must be between 0.0 and 1.0, got {decay_factor}")
    
    # Pick variant types for each idea using weighted selection with decay
    variant_types = pick_multiple_weighted_variants(count, seed, allow_duplicate_types, decay_factor)
    
    # Create each idea with its assigned variant type
    ideas = []
    for i, variant_type in enumerate(variant_types):
        idea = create_idea_variant(
            title=text_input.strip(),
            variant_name=variant_type,
            description=description,
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


# =============================================================================
# STORY SEED VARIANT CREATION HELPERS (US Women 13-20)
# =============================================================================

# Pools for story seed variants
CONFESSION_HOOKS = [
    "I've never told anyone this, but...",
    "This is the first time I'm saying this out loud...",
    "I don't know why I'm sharing this, but here goes...",
    "Promise you won't judge me for this...",
    "I've been carrying this for way too long...",
    "I need to get this off my chest...",
    "Nobody knows this about me, not even my best friend...",
    "I've drafted this confession so many times..."
]

TRANSFORMATION_BEFORES = [
    "I used to think confidence meant being loud",
    "I was the person who always said yes",
    "I thought being good meant being quiet",
    "I believed my worth came from how useful I was",
    "I spent years trying to be who they wanted",
    "I measured myself by other people's standards",
    "I thought disagreeing meant disrespecting",
    "I lived like my needs didn't matter"
]

OVERHEARD_SETTINGS = [
    "Kitchen, while I was supposed to be asleep",
    "Their bedroom, through thin walls",
    "The car, when they thought I had headphones in",
    "The bathroom, where sound carries",
    "The hallway, around the corner",
    "A video call I wasn't supposed to hear",
    "A text notification I saw accidentally",
    "A conversation they forgot to end"
]

SMALL_MOMENTS = [
    "The way they said 'fine' without looking up",
    "Noticing I wasn't in the group photo",
    "Realizing they stopped asking how I was",
    "Seeing my name spelled wrong on something important",
    "Finding out plans were made without me",
    "A compliment that felt like an insult",
    "Being corrected in front of everyone",
    "A pause that lasted too long before they answered"
]

QUIET_REBELLIONS = [
    "Leaving on read for exactly one hour",
    "Wearing what I actually like under their approved outfit",
    "Having opinions I only share with safe people",
    "Keeping a journal they don't know about",
    "Being 'busy' when I just need space",
    "Having a playlist that's nothing like what they think I listen to",
    "Saving money they don't know about",
    "Having dreams I don't tell them about"
]

PERMISSION_STATEMENTS = [
    "To be mediocre at something I enjoy",
    "To change my mind about what I want",
    "To take up space without apologizing",
    "To feel my feelings without explaining them",
    "To want things that don't make sense to others",
    "To rest without being productive",
    "To disappoint people who expect too much",
    "To be in progress, not perfect"
]


def _create_confession_moment_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create confession story seed variant."""
    topic = _humanize_topic(title)
    
    confession_hook = _pick_from_pool(CONFESSION_HOOKS, seed, variation_index)
    
    fear_judgments = [
        "That people will think I'm being dramatic",
        "That this makes me a bad person",
        "That no one will understand",
        "That they'll see me differently",
        "That I'm making a big deal out of nothing"
    ]
    
    relief_elements = [
        "It feels lighter just typing this out",
        "Even if no one reads this, it's out of me now",
        "The words exist somewhere besides my head",
        "I can breathe a little easier now",
        "It feels less real and more manageable now"
    ]
    
    hopes = [
        "That someone reading this feels less alone",
        "That saying it makes it easier to change",
        "That this is the first step to something better",
        "That the shame loses some power now",
        "That I can finally move forward"
    ]
    
    return {
        "confession_hook": confession_hook,
        "what_im_hiding": f"The truth about {topic.lower()} that I've been keeping",
        "why_now": f"Something about {topic.lower()} finally pushed me to speak",
        "fear_of_judgment": _pick_from_pool(fear_judgments, seed, variation_index + 1),
        "relief_element": _pick_from_pool(relief_elements, seed, variation_index + 2),
        "hope_for": _pick_from_pool(hopes, seed, variation_index + 3)
    }


def _create_before_after_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create before/after transformation seed variant."""
    topic = _humanize_topic(title)
    
    before_state = _pick_from_pool(TRANSFORMATION_BEFORES, seed, variation_index)
    
    unexpected_lessons = [
        "Not everyone sees things the way I was taught",
        "The rules I followed weren't universal",
        "What felt like weakness was actually strength",
        "I'd been solving the wrong problem",
        "Permission was mine to give all along"
    ]
    
    still_processing = [
        "How to believe it myself",
        "Whether I can maintain this version of me",
        "What else I believed that isn't true",
        "How to explain this to people who knew me before",
        "If this change is permanent or just temporary"
    ]
    
    return {
        "before_state": before_state,
        "the_moment": f"The day something about {topic.lower()} made me see differently",
        "after_state": f"Now I understand {topic.lower()} isn't what I thought",
        "what_triggered": "A moment that shouldn't have been important but was",
        "unexpected_lesson": _pick_from_pool(unexpected_lessons, seed, variation_index + 1),
        "still_processing": _pick_from_pool(still_processing, seed, variation_index + 2)
    }


def _create_overheard_truth_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create overheard truth seed variant."""
    topic = _humanize_topic(title)
    
    setting = _pick_from_pool(OVERHEARD_SETTINGS, seed, variation_index)
    
    immediate_reactions = [
        "Frozen in place, heart racing",
        "Pretended I didn't hear and walked away",
        "Felt my whole body go cold",
        "Had to hold my breath to stay quiet",
        "Replayed it in my head immediately"
    ]
    
    what_changed = [
        "Every interaction now has a shadow of doubt",
        "I see our history differently",
        "Trust became something I have to rebuild",
        "I notice things I used to ignore",
        "The way I talk to them changed without them knowing why"
    ]
    
    dilemmas = [
        "Confront them or pretend I never heard",
        "Tell someone or carry this alone",
        "Protect them from knowing I know",
        "Use this information or let it go",
        "Process this quietly or make it a conversation"
    ]
    
    return {
        "what_was_heard": f"Something about {topic.lower()} I wasn't meant to know",
        "where_it_happened": setting,
        "immediate_reaction": _pick_from_pool(immediate_reactions, seed, variation_index + 1),
        "who_was_talking": "People I trusted with a different version of reality",
        "what_it_changed": _pick_from_pool(what_changed, seed, variation_index + 2),
        "dilemma": _pick_from_pool(dilemmas, seed, variation_index + 3)
    }


def _create_parallel_lives_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create parallel lives seed variant."""
    topic = _humanize_topic(title)
    
    choice_points = [
        "The moment I chose to stay quiet instead of speak up",
        "The day I decided to play it safe",
        "When I let someone else decide for me",
        "The time I walked away instead of staying",
        "That conversation I avoided having"
    ]
    
    what_haunts = [
        "Wondering if the other path was better",
        "The person I might have become",
        "The relationship that might have survived",
        "The confidence I might have built",
        "The story I'll never know"
    ]
    
    current_peace = [
        "At least I know what this path holds",
        "I kept relationships that fighting might have destroyed",
        "The safe choice gave me time to grow quietly",
        "Sometimes protection is its own wisdom",
        "This version of me learned different lessons"
    ]
    
    wonderings = [
        "Was I wise or just afraid?",
        "Did I choose or did I avoid?",
        "Would I be stronger or just different?",
        "Is it too late to take that other path?",
        "Would I even recognize that other me?"
    ]
    
    return {
        "the_choice_point": f"{_pick_from_pool(choice_points, seed, variation_index)} when it came to {topic.lower()}",
        "path_taken": f"I became the version of me shaped by this choice about {topic.lower()}",
        "path_imagined": "The me who chose differently lives in my what-ifs",
        "what_haunts": _pick_from_pool(what_haunts, seed, variation_index + 1),
        "current_peace": _pick_from_pool(current_peace, seed, variation_index + 2),
        "wondering": _pick_from_pool(wonderings, seed, variation_index + 3)
    }


def _create_last_time_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create last time seed variant."""
    topic = _humanize_topic(title)
    
    didnt_know_then = [
        "That one moment would change everything",
        "That I'd replay this in my head for months",
        "That this was an ending, not just another day",
        "That I should have paid more attention",
        "That this memory would mean so much later"
    ]
    
    looking_back = [
        "I see signs I couldn't read at the time",
        "The moment was already fragile; I just didn't know",
        "Everything after was different, even small things",
        "I understand now what I was feeling but couldn't name",
        "The context changes the whole memory"
    ]
    
    what_replaced_it = [
        "A careful version of what used to be natural",
        "Something quieter and more guarded",
        "New routines that avoid the old patterns",
        "A space that nothing quite fills",
        "Different relationships that don't hit the same"
    ]
    
    return {
        "the_last_moment": f"The last time {topic.lower()} felt normal before everything shifted",
        "didnt_know_then": _pick_from_pool(didnt_know_then, seed, variation_index),
        "looking_back": _pick_from_pool(looking_back, seed, variation_index + 1),
        "wish_id_known": "I would have been more present, held on longer",
        "what_replaced_it": _pick_from_pool(what_replaced_it, seed, variation_index + 2),
        "carrying_forward": f"The feeling of {topic.lower()} before it changed"
    }


def _create_unsent_message_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create unsent message seed variant."""
    topic = _humanize_topic(title)
    
    unsent_messages = [
        "I know you didn't mean it, but it still hurt.",
        "I wish you'd asked instead of assumed.",
        "I'm tired of being the one who adjusts.",
        "You don't see me the way you think you do.",
        "I needed you and you weren't there.",
        "This isn't the relationship I thought we had.",
        "I forgive you, but I won't forget.",
        "I'm changing, even if you don't notice."
    ]
    
    why_unsents = [
        "They'd turn it into a lecture about being sensitive",
        "The conversation would become about them, not me",
        "Some things are better processed alone",
        "I'm not ready for what sending it would start",
        "Writing it was enough; sending it would be too much"
    ]
    
    what_they_did_instead = [
        "Wrote it here instead",
        "Let time do what words couldn't",
        "Found someone safer to talk to",
        "Processed it through other ways",
        "Accepted that some things stay unsaid"
    ]
    
    return {
        "the_message": f"{_pick_from_pool(unsent_messages, seed, variation_index)} It's about {topic.lower()}.",
        "who_its_for": "Someone who needs to hear this but probably wouldn't receive it well",
        "why_unsent": _pick_from_pool(why_unsents, seed, variation_index + 1),
        "what_it_would_change": "Maybe nothing. Maybe everything.",
        "what_they_did_instead": _pick_from_pool(what_they_did_instead, seed, variation_index + 2),
        "still_saved": "In drafts, proof that I have words too"
    }


def _create_small_moment_big_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create small moment, big meaning seed variant."""
    topic = _humanize_topic(title)
    
    small_thing = _pick_from_pool(SMALL_MOMENTS, seed, variation_index)
    
    why_it_hit = [
        "It confirmed something I was afraid to believe",
        "The pattern suddenly became impossible to ignore",
        "My body knew before my mind caught up",
        "It was too small to complain about but too real to dismiss",
        "Years of small moments finally added up"
    ]
    
    internal_shifts = [
        "Started trusting my own perception more",
        "Stopped making excuses for people",
        "Began asking what I actually want",
        "Noticed I'd been performing without an audience",
        "Realized the problem wasn't just me"
    ]
    
    still_thinkings = [
        "When did I start needing witnesses to feel valid?",
        "How many small moments have I been dismissing?",
        "Is this a pattern or am I being sensitive?",
        "What else have I normalized that isn't normal?",
        "When did I learn to shrink around this?"
    ]
    
    return {
        "the_small_thing": f"{small_thing} — related to {topic.lower()}",
        "why_it_hit": _pick_from_pool(why_it_hit, seed, variation_index + 1),
        "bigger_pattern": f"What it revealed about {topic.lower()} in my life",
        "who_noticed": "Just me and the silence after",
        "internal_shift": _pick_from_pool(internal_shifts, seed, variation_index + 2),
        "still_thinking": _pick_from_pool(still_thinkings, seed, variation_index + 3)
    }


def _create_almost_said_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create almost said seed variant."""
    topic = _humanize_topic(title)
    
    almost_statements = [
        "I'm not okay, and I need help.",
        "You hurt me and I don't think you know.",
        "I don't actually agree with you.",
        "This isn't working for me anymore.",
        "I've been pretending this whole time.",
        "Can you actually listen, not just respond?",
        "I need more than you're giving.",
        "I'm scared of what I'm becoming."
    ]
    
    what_stopped = [
        "Their stressed face, their distracted attention",
        "The conversation was already moving on",
        "I couldn't find the simple version of my feelings",
        "The timing felt wrong, even though it always does",
        "I was afraid of what would happen next"
    ]
    
    safer_things = [
        "'Fine, same as always'",
        "'Nothing, nevermind'",
        "'I'm just tired'",
        "'It doesn't matter'",
        "'You wouldn't understand anyway'"
    ]
    
    consequences = [
        "They moved on, I stayed stuck",
        "The moment passed, the feeling didn't",
        "They thought we connected; I felt more alone",
        "The silence became heavier",
        "I got smaller to avoid the conversation"
    ]
    
    return {
        "what_almost_came_out": f"{_pick_from_pool(almost_statements, seed, variation_index)} About {topic.lower()}.",
        "the_setting": "A moment when saying it might have been possible",
        "what_stopped_them": _pick_from_pool(what_stopped, seed, variation_index + 1),
        "the_safer_thing": _pick_from_pool(safer_things, seed, variation_index + 2),
        "consequence": _pick_from_pool(consequences, seed, variation_index + 3),
        "next_time": "Maybe find a quieter moment, or write it down first"
    }


def _create_what_they_dont_know_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create what they don't know seed variant."""
    topic = _humanize_topic(title)
    
    surfaces = [
        "The friend who always has advice for everyone",
        "The one who seems to have it together",
        "The person who never complains",
        "The responsible one in the group",
        "The one who's always cheerful"
    ]
    
    truths = [
        "I give advice so I don't have to take any for myself",
        "I'm barely holding it together most days",
        "I've learned complaining makes people leave",
        "Responsibility was survival, not choice",
        "The cheerfulness is a shield, not a feeling"
    ]
    
    costs = [
        "Loneliness disguised as being helpful",
        "Exhaustion from maintaining the image",
        "Relationships that don't know the real me",
        "Resentment I can't express",
        "A self I barely recognize sometimes"
    ]
    
    would_change_ifs = [
        "Someone asked the right question at the right time",
        "I felt safe enough to be seen messy",
        "The mask became too heavy to wear",
        "Someone noticed without me having to tell them",
        "I decided I'd rather be rejected as myself"
    ]
    
    return {
        "the_surface": f"{_pick_from_pool(surfaces, seed, variation_index)} when it comes to {topic.lower()}",
        "the_truth": _pick_from_pool(truths, seed, variation_index + 1),
        "why_hidden": "Being needed feels safer than being vulnerable",
        "closest_to_knowing": "The person who once asked if I was okay twice",
        "cost_of_hiding": _pick_from_pool(costs, seed, variation_index + 2),
        "would_change_if": _pick_from_pool(would_change_ifs, seed, variation_index + 3)
    }


def _create_quiet_rebellion_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create quiet rebellion seed variant."""
    topic = _humanize_topic(title)
    
    rebellion = _pick_from_pool(QUIET_REBELLIONS, seed, variation_index)
    
    why_it_matters = [
        "Proof that my time is mine too",
        "A boundary I set without permission",
        "A version of me they don't control",
        "My own space in a crowded life",
        "Evidence that I'm more than they allow"
    ]
    
    risks_if_caught = [
        "'Why didn't you...? Is something wrong?'",
        "A conversation I'm not ready for",
        "Being called ungrateful or difficult",
        "Losing the one space that's truly mine",
        "Their disappointment and my guilt"
    ]
    
    victory_feelings = [
        "That hour/moment belongs to no one but me",
        "I exist in ways they don't know about",
        "The small defiance keeps me sane",
        "I'm not as controlled as they think",
        "This tiny thing is proof I'm still me"
    ]
    
    return {
        "the_rule_they_break": f"The expectation around {topic.lower()} that I refuse to meet",
        "how_they_do_it": rebellion,
        "who_theyre_defying": "The assumption that I'll always comply",
        "why_it_matters": _pick_from_pool(why_it_matters, seed, variation_index + 1),
        "risk_if_caught": _pick_from_pool(risks_if_caught, seed, variation_index + 2),
        "victory_feeling": _pick_from_pool(victory_feelings, seed, variation_index + 3)
    }


def _create_mirror_moment_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create mirror moment seed variant."""
    topic = _humanize_topic(title)
    
    what_saw = [
        "I looked like my mom when she's angry",
        "My expression matched someone I promised I'd never be like",
        "I saw exhaustion I'd been hiding from myself",
        "The person staring back looked afraid",
        "I noticed I've been performing even alone"
    ]
    
    emotional_responses = [
        "Shock, then shame, then sadness",
        "A recognition I couldn't deny",
        "Compassion mixed with discomfort",
        "Anger at who taught me this",
        "Grief for who I used to be"
    ]
    
    actions_taken = [
        "Took a breath and changed something small",
        "Apologized to someone nearby",
        "Went somewhere quiet to process",
        "Wrote down what I saw",
        "Made a decision to pay more attention"
    ]
    
    ongoing_questions = [
        "Which parts of them am I choosing vs inheriting?",
        "Is this who I want to become?",
        "How long have I been like this?",
        "What triggered this version of me?",
        "Can I change what I saw?"
    ]
    
    return {
        "what_they_saw": f"{_pick_from_pool(what_saw, seed, variation_index)} — connected to {topic.lower()}",
        "expected_vs_actual": "I always thought I was different from this",
        "trigger": "A moment when I caught myself mid-action",
        "emotional_response": _pick_from_pool(emotional_responses, seed, variation_index + 1),
        "action_taken": _pick_from_pool(actions_taken, seed, variation_index + 2),
        "ongoing_question": _pick_from_pool(ongoing_questions, seed, variation_index + 3)
    }


def _create_chosen_family_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create chosen family seed variant."""
    topic = _humanize_topic(title)
    
    connections = [
        "My friend's parent who actually listens",
        "An online community that gets it",
        "A mentor who sees my potential",
        "Friends who became siblings",
        "Someone random who changed everything"
    ]
    
    what_makes_safe = [
        "They ask questions but never push for answers",
        "No history of disappointment to navigate",
        "They celebrate the weird parts of me",
        "I don't have to translate my feelings",
        "They notice when I'm not okay"
    ]
    
    what_was_missing = [
        "Being listened to without being fixed or judged",
        "Attention that feels like care, not surveillance",
        "Permission to be in progress",
        "Unconditional positive regard",
        "Space to be messy without consequences"
    ]
    
    gratitude_fors = [
        "Showing me what attention can feel like",
        "Proving relationships can be easy",
        "Being the template for what I deserve",
        "Receiving me without conditions",
        "Teaching me how to be there for others"
    ]
    
    return {
        "the_connection": f"{_pick_from_pool(connections, seed, variation_index)} who helped with {topic.lower()}",
        "the_moment_it_clicked": "When they remembered something small I mentioned",
        "what_was_missing": _pick_from_pool(what_was_missing, seed, variation_index + 1),
        "what_they_offer_each_other": "A version of family that actually feels safe",
        "how_its_different": _pick_from_pool(what_makes_safe, seed, variation_index + 2),
        "gratitude_for": _pick_from_pool(gratitude_fors, seed, variation_index + 3)
    }


def _create_growing_apart_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create growing apart seed variant."""
    topic = _humanize_topic(title)
    
    first_signs = [
        "Conversations became updates, not real talks",
        "I started editing what I shared",
        "The energy was different but I couldn't name how",
        "We kept making plans we'd cancel",
        "Silences that used to be comfortable felt awkward"
    ]
    
    undeniable_moments = [
        "Realized I hadn't told them anything real in months",
        "Found out something big from someone else",
        "Noticed they'd moved on without telling me",
        "Saw them be different with others than with me",
        "A conversation felt like talking to a stranger"
    ]
    
    what_they_miss = [
        "The person who knew me without explaining",
        "Inside jokes that don't land anymore",
        "The shorthand we used to have",
        "Being someone's first call",
        "History that only we shared"
    ]
    
    hope_or_griefs = [
        "Maybe we're just different chapters, not ended books",
        "Some people are for seasons, not forever",
        "Grief for who we were, acceptance for who we became",
        "Still hoping time will bring us back somehow",
        "Letting go with love instead of drama"
    ]
    
    return {
        "the_relationship": f"Someone important who's connected to {topic.lower()}",
        "first_signs": _pick_from_pool(first_signs, seed, variation_index),
        "the_undeniable_moment": _pick_from_pool(undeniable_moments, seed, variation_index + 1),
        "what_they_miss": _pick_from_pool(what_they_miss, seed, variation_index + 2),
        "acceptance_level": "Mourning what was while protecting what's left",
        "hope_or_grief": _pick_from_pool(hope_or_griefs, seed, variation_index + 3)
    }


def _create_permission_to_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create permission to seed variant."""
    topic = _humanize_topic(title)
    
    permission = _pick_from_pool(PERMISSION_STATEMENTS, seed, variation_index)
    
    who_denied = [
        "My own perfectionism",
        "Rules I absorbed without questioning",
        "The fear of what others would think",
        "Beliefs passed down without examination",
        "A younger version of me who was scared"
    ]
    
    what_changed = [
        "Watching someone else do it unapologetically",
        "Getting tired of my own limitations",
        "Realizing the rules weren't making me happy",
        "Someone giving me permission I needed to hear",
        "Understanding the cost of not allowing this"
    ]
    
    how_it_feels = [
        "Like breathing room I didn't know I needed",
        "Terrifying and freeing at the same time",
        "Like meeting a version of me I'd locked away",
        "Lighter, even though nothing external changed",
        "Like the start of something, not an arrival"
    ]
    
    whats_next = [
        "Maybe I can try things just for fun now",
        "Other permissions are waiting to be given",
        "I get to discover what I actually want",
        "The standards are mine to set now",
        "More of me is available for living"
    ]
    
    return {
        "the_permission": f"{permission} — especially regarding {topic.lower()}",
        "who_denied_it_before": _pick_from_pool(who_denied, seed, variation_index + 1),
        "what_changed": _pick_from_pool(what_changed, seed, variation_index + 2),
        "how_it_feels": _pick_from_pool(how_it_feels, seed, variation_index + 3),
        "what_they_feared": "That allowing this makes me less worthy",
        "whats_next": _pick_from_pool(whats_next, seed, variation_index + 4)
    }


def _create_learned_young_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create learned young seed variant."""
    topic = _humanize_topic(title)
    
    beliefs = [
        "That crying is manipulation",
        "That asking for help is weakness",
        "That love has to be earned",
        "That being good means being quiet",
        "That my feelings are too much",
        "That conflict means someone has to lose",
        "That my needs are inconvenient",
        "That being perfect keeps me safe"
    ]
    
    how_shaped = [
        "I learned to perform calm when I'm breaking inside",
        "I became the helper, never the helped",
        "I measure every good thing I do",
        "I got quieter and smaller over time",
        "I dismiss my own feelings before others can"
    ]
    
    questioning_now = [
        "Therapy showing me emotions aren't weapons",
        "Meeting people who were raised differently",
        "Getting older and questioning the source",
        "Seeing the damage in others from the same lesson",
        "Noticing how this belief hasn't served me"
    ]
    
    unlearning = [
        "Letting myself feel alone first, then with safe people",
        "Practicing asking for small things first",
        "Catching the old thoughts and questioning them",
        "Building new experiences to replace old patterns",
        "Forgiving myself for how long I believed it"
    ]
    
    return {
        "the_belief": f"{_pick_from_pool(beliefs, seed, variation_index)} — connected to {topic.lower()}",
        "age_or_moment": "Young enough that I thought it was truth, not teaching",
        "who_taught_it": "People who probably learned it the same way",
        "how_it_shaped_them": _pick_from_pool(how_shaped, seed, variation_index + 1),
        "questioning_now": _pick_from_pool(questioning_now, seed, variation_index + 2),
        "unlearning_process": _pick_from_pool(unlearning, seed, variation_index + 3)
    }


def _create_the_version_of_me_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create the version of me seed variant."""
    topic = _humanize_topic(title)
    
    versions = [
        "School Me vs Home Me",
        "Online Me vs Real Life Me",
        "Who I am alone vs who I am in groups",
        "The me my parents see vs who I really am",
        "Stressed Me vs Relaxed Me"
    ]
    
    differences = [
        "Energy levels, openness, even my voice changes",
        "The topics I'll talk about, the humor I use",
        "How honest I can be without fear",
        "Whether my body feels tense or loose",
        "The version of my story I tell"
    ]
    
    authenticity_levels = [
        "Both are real, just different real",
        "One is performance, one is survival",
        "Pieces of me, none the whole picture",
        "One is who I wish I could always be",
        "Protective layers with a core underneath"
    ]
    
    wishes = [
        "A space where I can just be all of me at once",
        "For people to know all versions are me",
        "To stop code-switching constantly",
        "For the gap between versions to shrink",
        "Integration that doesn't require sacrifice"
    ]
    
    return {
        "which_version": f"{_pick_from_pool(versions, seed, variation_index)} — how {topic.lower()} brings out different sides",
        "where_it_appears": "Different contexts call out different versions",
        "how_its_different": _pick_from_pool(differences, seed, variation_index + 1),
        "authenticity_level": _pick_from_pool(authenticity_levels, seed, variation_index + 2),
        "what_others_see": "They'd be surprised the other version exists",
        "wish_for_integration": _pick_from_pool(wishes, seed, variation_index + 3)
    }


def _create_emotional_inheritance_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create emotional inheritance seed variant."""
    topic = _humanize_topic(title)
    
    patterns = [
        "The silent treatment as conflict resolution",
        "Making everything about performance and success",
        "Love expressed through criticism",
        "Keeping feelings private until explosion",
        "Handling problems by pretending they don't exist"
    ]
    
    from_whoms = [
        "Mom got it from grandma who got it from hers",
        "Dad's side, a long line of holding it in",
        "Both sides, reinforcing each other",
        "The culture I was raised in",
        "Trauma that became tradition"
    ]
    
    feelings_about = [
        "Angry that I learned it, sad that they did too",
        "Compassion mixed with frustration",
        "Grief for what we all could have had",
        "Understanding but still wanting to break it",
        "Tired of carrying something that isn't mine"
    ]
    
    what_theyd_pass = [
        "The courage to stay in the conversation",
        "Permission to feel without shame",
        "Tools they never taught me",
        "A different pattern, even if imperfect",
        "Awareness that this can change"
    ]
    
    return {
        "what_was_passed_down": f"{_pick_from_pool(patterns, seed, variation_index)} — especially around {topic.lower()}",
        "from_whom": _pick_from_pool(from_whoms, seed, variation_index + 1),
        "how_they_noticed": "Realized I was doing exactly what they do",
        "feeling_about_it": _pick_from_pool(feelings_about, seed, variation_index + 2),
        "breaking_or_keeping": "Trying to break it, even when it's hard",
        "what_theyd_pass_on": _pick_from_pool(what_theyd_pass, seed, variation_index + 3)
    }


def _create_safe_person_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create safe person seed variant."""
    topic = _humanize_topic(title)
    
    who_they_are = [
        "A friend who never judges, just listens",
        "Someone who's been through similar things",
        "The person who asks questions without agenda",
        "My therapist who creates space I can't find elsewhere",
        "A family member who broke the mold"
    ]
    
    what_makes_safe = [
        "They ask questions but never push for answers",
        "I can say the ugly thoughts out loud",
        "They've seen my worst and stayed",
        "No fixing, no advice unless I ask",
        "Silence with them isn't awkward"
    ]
    
    contrasts = [
        "With others I edit myself before speaking",
        "Everyone else gets the curated version",
        "Other relationships feel like performance",
        "They're the only one who knows this part",
        "The relief I feel is the contrast itself"
    ]
    
    how_earned = [
        "They showed me their mess first",
        "Consistency over time, not one big moment",
        "They kept showing up when it wasn't easy",
        "Small moments of trust that accumulated",
        "They remembered things others forgot"
    ]
    
    return {
        "who_they_are": f"{_pick_from_pool(who_they_are, seed, variation_index)} who helps me with {topic.lower()}",
        "what_makes_them_safe": _pick_from_pool(what_makes_safe, seed, variation_index + 1),
        "what_happens_around_them": "I can be all of me without explanation",
        "contrast_with_others": _pick_from_pool(contrasts, seed, variation_index + 2),
        "how_it_was_earned": _pick_from_pool(how_earned, seed, variation_index + 3),
        "what_they_give_back": "Being their safe person too"
    }


def _create_holding_space_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create holding space seed variant."""
    topic = _humanize_topic(title)
    
    who_needed = [
        "My friend going through something big",
        "A family member in crisis",
        "Someone who finally opened up",
        "A person I didn't expect to be there for",
        "Someone I'm learning to support better"
    ]
    
    what_didnt_do = [
        "Didn't say 'it'll be okay' or try to relate",
        "Resisted the urge to fix or solve",
        "Didn't make it about me",
        "Didn't fill the silence with empty words",
        "Didn't panic at their pain"
    ]
    
    what_did_instead = [
        "Sat with them in silence, held their hand",
        "Said 'I'm here' and meant it",
        "Let them talk without interrupting",
        "Mirrored back what I heard",
        "Was present without agenda"
    ]
    
    what_it_cost = [
        "Fighting my own discomfort with their pain",
        "Feeling helpless but staying anyway",
        "Processing my own stuff later, alone",
        "The weight of witnessing without fixing",
        "Energy I didn't know I had to give"
    ]
    
    what_was_learned = [
        "Sometimes presence is the only medicine",
        "Fixing isn't the same as helping",
        "Being uncomfortable is part of caring",
        "I'm stronger than I thought I was",
        "Connection doesn't require solutions"
    ]
    
    return {
        "who_needed_it": f"{_pick_from_pool(who_needed, seed, variation_index)} dealing with {topic.lower()}",
        "what_was_happening": "Pain that needed witnessing, not solving",
        "what_they_didnt_do": _pick_from_pool(what_didnt_do, seed, variation_index + 1),
        "what_they_did_instead": _pick_from_pool(what_did_instead, seed, variation_index + 2),
        "what_it_cost": _pick_from_pool(what_it_cost, seed, variation_index + 3),
        "what_was_learned": _pick_from_pool(what_was_learned, seed, variation_index + 4)
    }


def _create_rewriting_the_story_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create rewriting the story seed variant."""
    topic = _humanize_topic(title)
    
    old_stories = [
        "They left because I wasn't enough",
        "I'm too much for people to handle",
        "I'm the difficult one in the family",
        "If I were different, this wouldn't have happened",
        "I don't deserve the good things"
    ]
    
    what_protected = [
        "Made the pain feel like something I could control",
        "Gave me a role to play in my own tragedy",
        "Let me blame myself instead of feeling helpless",
        "Created order out of chaos",
        "Was easier than accepting randomness"
    ]
    
    new_understandings = [
        "They left because they couldn't handle their own stuff",
        "The 'too much' was them being too little",
        "I was just the one who asked questions",
        "I couldn't have changed their choices",
        "I was surviving, not causing"
    ]
    
    how_feels_different = [
        "Less shame, more sadness, more freedom",
        "Anger redirected to where it belongs",
        "Compassion for who I was",
        "Room to grieve without guilt",
        "Space for a different future"
    ]
    
    ongoing_revision = [
        "Still learning it wasn't about me being lovable",
        "Catching old thoughts and replacing them",
        "The body remembers what the mind has rewritten",
        "Some days the old story wins",
        "New evidence needed to cement the new version"
    ]
    
    return {
        "the_old_story": f"{_pick_from_pool(old_stories, seed, variation_index)} — about {topic.lower()}",
        "what_it_protected": _pick_from_pool(what_protected, seed, variation_index + 1),
        "the_new_understanding": _pick_from_pool(new_understandings, seed, variation_index + 2),
        "what_made_rewrite_possible": "Time, therapy, or someone who told me the truth",
        "how_it_feels_different": _pick_from_pool(how_feels_different, seed, variation_index + 3),
        "ongoing_revision": _pick_from_pool(ongoing_revision, seed, variation_index + 4)
    }


# =============================================================================
# FUSION VARIANT CREATION HELPERS
# =============================================================================

def _create_confession_mystery_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create confession + mystery fusion variant."""
    topic = _humanize_topic(title)
    
    confession_hooks = [
        "I've been lying to everyone about what I found...",
        "There's something I've been keeping that I need to confess...",
        "I know something that changes everything, and I can't stay silent...",
        "I finally understand something I wasn't supposed to discover...",
        "What I'm about to say will make you see things differently..."
    ]
    
    hidden_mysteries = [
        "A pattern nobody else noticed",
        "Something that doesn't add up in our family",
        "A secret hidden in plain sight",
        "Connections everyone else dismissed",
        "Evidence of something I was never meant to find"
    ]
    
    unresolved_questions = [
        "Why did they hide this from me specifically?",
        "What else don't I know?",
        "Who else is keeping this secret?",
        "What happens now that I know?",
        "Was I better off not knowing?"
    ]
    
    return {
        "confession_hook": _pick_from_pool(confession_hooks, seed, variation_index),
        "hidden_mystery": f"Something about {topic.lower()} that I discovered",
        "clues_dropped": "Comments I made that everyone dismissed",
        "why_speaking_now": f"I finally have proof about {topic.lower()}",
        "what_they_discovered": _pick_from_pool(hidden_mysteries, seed, variation_index + 1),
        "unresolved_question": _pick_from_pool(unresolved_questions, seed, variation_index + 2)
    }


def _create_overheard_transformation_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create overheard + transformation fusion variant."""
    topic = _humanize_topic(title)
    
    before_hearings = [
        "The kid trying desperately to be enough",
        "Someone who believed what they were told about themselves",
        "A people-pleaser who hadn't questioned the system yet",
        "The one who always adjusted to keep the peace",
        "Someone who thought their worth depended on others' approval"
    ]
    
    transformation_processes = [
        "Stopped trying to be what they wanted",
        "Started questioning every 'truth' they'd been taught",
        "Built boundaries for the first time",
        "Found validation from within instead of seeking it outside",
        "Learned to trust my own perception over their narrative"
    ]
    
    after_hearings = [
        "Someone who defines their own worth",
        "A person who doesn't shrink to fit others' comfort",
        "The version of me they never expected",
        "Someone who chose authenticity over approval",
        "A person who knows the truth and lives accordingly"
    ]
    
    return {
        "what_was_heard": f"Something about {topic.lower()} that changed my understanding",
        "before_hearing": _pick_from_pool(before_hearings, seed, variation_index),
        "immediate_impact": "Something broke and something clicked at the same time",
        "transformation_process": _pick_from_pool(transformation_processes, seed, variation_index + 1),
        "after_hearing": _pick_from_pool(after_hearings, seed, variation_index + 2),
        "confrontation_choice": "Never told them - the change speaks for itself"
    }


def _create_unsent_rebellion_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create unsent message + quiet rebellion fusion variant."""
    topic = _humanize_topic(title)
    
    rebellion_messages = [
        "I don't actually want the future you planned for me.",
        "Your expectations are suffocating me.",
        "I'm tired of being who you need me to be.",
        "You don't actually know me at all.",
        "I've been pretending to agree for years.",
        "The version of me you love isn't real."
    ]
    
    why_rebellions = [
        "I was never supposed to have different dreams",
        "Disagreement was never allowed",
        "Writing this truth is the first honest thing I've done",
        "Even thinking this was forbidden",
        "This message exists because speaking is impossible"
    ]
    
    power_in_keepings = [
        "I know my truth even if they don't",
        "This is mine, and they can't control it",
        "The words exist even if unspoken",
        "Knowing I could send it is enough",
        "This rebellion lives where they can't reach"
    ]
    
    return {
        "the_message": f"{_pick_from_pool(rebellion_messages, seed, variation_index)} About {topic.lower()}.",
        "who_its_for": "The authority figure who thinks they know what's best",
        "why_writing_is_rebellion": _pick_from_pool(why_rebellions, seed, variation_index + 1),
        "what_theyd_lose": "The peace that depends on my compliance",
        "power_in_keeping": _pick_from_pool(power_in_keepings, seed, variation_index + 2),
        "where_its_saved": "In a place they'll never think to look"
    }


def _create_mirror_inheritance_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create mirror moment + emotional inheritance fusion variant."""
    topic = _humanize_topic(title)
    
    inherited_traits = [
        "The same tightness in my jaw when angry",
        "That way of going quiet when hurt",
        "The need to fix everything for everyone",
        "Deflecting with humor when it's serious",
        "The inability to ask for what I need"
    ]
    
    patterns = [
        "Silence until it's too much, then regret",
        "Putting others first until there's nothing left",
        "Hiding pain behind productivity",
        "Love expressed as worry instead of warmth",
        "Conflict avoided until it explodes"
    ]
    
    choice_moments = [
        "Do I let this become automatic too?",
        "Is this who I want to become?",
        "Can I break what they couldn't?",
        "Where does their pattern end and my choice begin?",
        "Do I have to carry what they gave me?"
    ]
    
    return {
        "what_they_saw": f"An inherited response to {topic.lower()} — {_pick_from_pool(inherited_traits, seed, variation_index)}",
        "who_they_saw": "Generations of family members who did the same",
        "the_pattern": _pick_from_pool(patterns, seed, variation_index + 1),
        "emotional_response": "Grief for all of us who learned this",
        "choice_moment": _pick_from_pool(choice_moments, seed, variation_index + 2),
        "what_changes": "Choosing differently, starting with something small"
    }


def _create_chosen_growing_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create chosen family + growing apart fusion variant."""
    topic = _humanize_topic(title)
    
    fading_connections = [
        "Best friend since childhood who doesn't get me anymore",
        "The person who was once my whole world",
        "Someone who used to know me without words",
        "The relationship I thought would last forever",
        "A bond that's becoming a memory"
    ]
    
    new_connections = [
        "Online friends who understand without explaining",
        "People who see who I'm becoming, not who I was",
        "A community that celebrates what others criticized",
        "Someone who asks the questions old friends never did",
        "Chosen family who chose me back"
    ]
    
    guilt_feelings = [
        "Like I'm betraying something sacred",
        "Torn between loyalty and growth",
        "Grieving while also feeling free",
        "Wondering if I'm the one who changed too much",
        "Carrying both gratitude and goodbye"
    ]
    
    return {
        "fading_connection": f"A relationship around {topic.lower()} that's changing — {_pick_from_pool(fading_connections, seed, variation_index)}",
        "new_connection": _pick_from_pool(new_connections, seed, variation_index + 1),
        "what_old_gave": "History, shared memories, the comfort of being known",
        "what_new_offers": "Being seen for who I'm becoming, not who I was",
        "guilt_feeling": _pick_from_pool(guilt_feelings, seed, variation_index + 2),
        "acceptance": "People can be 'for a season' without it being failure"
    }


def _create_parallel_permission_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create parallel lives + permission to fusion variant."""
    topic = _humanize_topic(title)
    
    permissions = [
        "To take up space without apologizing",
        "To want things that don't make sense to others",
        "To change who I've always been",
        "To disappoint people who expect too much",
        "To be in progress instead of finished"
    ]
    
    what_delayed = [
        "Being told 'don't be too much' so many times",
        "Fear of what they'd think",
        "Believing I didn't deserve it",
        "Rules I absorbed without questioning",
        "The weight of others' expectations"
    ]
    
    what_unlocked = [
        "Meeting someone who celebrated what I hid",
        "Getting tired of being small",
        "Realizing the cost of not allowing this",
        "Seeing someone else live the permission I wanted",
        "Understanding I was waiting for approval that wasn't coming"
    ]
    
    bridging_gaps = [
        "That parallel me isn't gone - she's just been waiting",
        "Every permission I take now brings those versions closer",
        "I can become who I might have been, starting today",
        "The gap is smaller than it looked from the inside",
        "I'm not too late - I'm right on time for this version"
    ]
    
    return {
        "the_permission": f"To {_pick_from_pool(permissions, seed, variation_index).lower()} when it comes to {topic.lower()}",
        "earlier_version": "The one who made themselves small",
        "parallel_version": "Who I might have been with earlier permission",
        "what_delayed_it": _pick_from_pool(what_delayed, seed, variation_index + 1),
        "what_unlocked_it": _pick_from_pool(what_unlocked, seed, variation_index + 2),
        "bridging_the_gap": _pick_from_pool(bridging_gaps, seed, variation_index + 3)
    }


# =============================================================================
# MISSING THEME VARIANT CREATION HELPERS
# =============================================================================

def _create_first_butterflies_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create first butterflies/crush variant."""
    topic = _humanize_topic(title)
    
    moments = [
        "They laughed at something I said, really laughed",
        "We accidentally made eye contact and neither looked away",
        "Their hand brushed mine reaching for the same thing",
        "They remembered something I mentioned weeks ago",
        "I heard them say something nice about me to someone else"
    ]
    
    physical_feelings = [
        "Stomach dropped, face got warm, forgot how to breathe",
        "Heart beating so loud I was sure everyone could hear",
        "Couldn't stop smiling and had to look away",
        "Hands suddenly didn't know what to do",
        "Words got stuck somewhere between my brain and mouth"
    ]
    
    internal_panics = [
        "Did I say something weird? Do they think I'm weird?",
        "Act normal act normal act normal",
        "What do I do with my face right now?",
        "Please don't let me say something embarrassing",
        "Are they looking? Don't look. Should I look?"
    ]
    
    return {
        "the_moment": f"{_pick_from_pool(moments, seed, variation_index)} — something about {topic.lower()}",
        "physical_feeling": _pick_from_pool(physical_feelings, seed, variation_index + 1),
        "what_they_noticed": "A small detail that keeps replaying in my head",
        "internal_panic": _pick_from_pool(internal_panics, seed, variation_index + 2),
        "acting_normal": "Looked at my phone like I got a text",
        "replay_loop": "That moment. Over and over. On repeat."
    }


def _create_body_acceptance_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create body acceptance/self-image variant."""
    topic = _humanize_topic(title)
    
    struggles = [
        "Seeing photos of myself and not recognizing me",
        "Avoiding mirrors and cameras",
        "Comparing every feature to everyone else",
        "The way clothes fit differently than I expect",
        "Hearing my voice in recordings"
    ]
    
    voices = [
        "'You'd be prettier if...' on repeat",
        "Cataloging every flaw before anyone else can",
        "The things I'd never say to a friend, but say to myself",
        "Measuring myself against impossible standards",
        "Noticing what I hate before what I like"
    ]
    
    shifts = [
        "Realizing my body carried me through hard things",
        "Someone seeing me as beautiful and meaning it",
        "Noticing my body doing amazing things without me thanking it",
        "A photo where I actually looked happy, not just 'good'",
        "Getting tired of the constant war with myself"
    ]
    
    return {
        "the_struggle": f"The way {topic.lower()} makes me see myself — {_pick_from_pool(struggles, seed, variation_index)}",
        "where_it_started": "Young enough that I don't remember not feeling this way",
        "the_voice": _pick_from_pool(voices, seed, variation_index + 1),
        "moment_of_shift": _pick_from_pool(shifts, seed, variation_index + 2),
        "what_helps": "Unfollowing accounts that make me compare",
        "current_truth": "Some days are harder. Today I'm trying."
    }


def _create_fitting_in_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create social anxiety/fitting in variant."""
    topic = _humanize_topic(title)
    
    situations = [
        "Group projects, lunch tables, parties",
        "Walking into a room where everyone already knows each other",
        "Being the new one, the quiet one, the different one",
        "Trying to join a conversation already happening",
        "Anytime I have to be 'on' around people"
    ]
    
    what_others_see = [
        "Quiet, maybe shy, probably fine",
        "Chill, doesn't seem to care much",
        "Keeps to themselves, mysterious maybe",
        "Nice enough, just doesn't talk much",
        "Independent, likes being alone"
    ]
    
    internal_realities = [
        "Heart racing, scripting every sentence, counting minutes",
        "Rehearsing what to say, replaying what I said wrong",
        "Wondering if they noticed me being awkward",
        "Exhausted from performing 'relaxed'",
        "Waiting for the moment I can finally leave"
    ]
    
    return {
        "the_situation": f"When {topic.lower()} puts me in — {_pick_from_pool(situations, seed, variation_index)}",
        "what_others_see": _pick_from_pool(what_others_see, seed, variation_index + 1),
        "internal_reality": _pick_from_pool(internal_realities, seed, variation_index + 2),
        "the_exhaustion": "Going home and needing hours to recover",
        "coping_mechanism": "Bathroom breaks to breathe, texting someone safe",
        "wish_for": "That being social didn't feel like a performance"
    }


def _create_online_connection_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create online friendship/connection variant."""
    topic = _humanize_topic(title)
    
    connections = [
        "Friends from a Discord server I've never met",
        "Someone I've been DMing for years",
        "A creator whose content feels like they get me",
        "People from a fandom who became real friends",
        "A group chat that knows more about me than my IRL friends"
    ]
    
    what_it_provides = [
        "They know me better than people who see me daily",
        "A space where I can be fully myself",
        "Understanding without having to explain everything",
        "Connection that doesn't require performing",
        "Acceptance for the weird parts of me"
    ]
    
    complicated_feelings = [
        "Mourning that we might never meet in person",
        "Feeling closer to strangers than to family sometimes",
        "Not knowing if this makes me antisocial or just... different",
        "Wondering if this connection is 'real' enough",
        "Being more honest through a screen than in person"
    ]
    
    return {
        "the_connection": f"{_pick_from_pool(connections, seed, variation_index)} — connected through {topic.lower()}",
        "how_it_started": "We bonded over something most people don't understand",
        "what_it_provides": _pick_from_pool(what_it_provides, seed, variation_index + 1),
        "others_opinion": "'They're not real friends' - but they showed up when no one else did",
        "defense_of_realness": "We've talked through my worst moments",
        "complicated_feeling": _pick_from_pool(complicated_feelings, seed, variation_index + 2)
    }


def _create_future_anxiety_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create future anxiety/growing up variant."""
    topic = _humanize_topic(title)
    
    pressures = [
        "Having a major picked, a plan, a direction",
        "Knowing what I want to do with my life",
        "Being as put-together as everyone else seems",
        "Having it figured out when I can barely handle today",
        "Making decisions that will define my whole future"
    ]
    
    sources = [
        "Family questions, college apps, everyone asking",
        "Comparison to siblings, cousins, classmates",
        "The timeline I was supposed to be following",
        "Adults who expect more certainty than I have",
        "My own expectations of who I should be by now"
    ]
    
    honest_truths = [
        "I'm terrified of picking wrong and wasting my life",
        "I don't know what I'm passionate about and that scares me",
        "Everyone else seems to have it figured out except me",
        "I'm not ready to be an adult but time keeps passing",
        "I feel behind in a race I never agreed to run"
    ]
    
    return {
        "the_pressure": f"The pressure around {topic.lower()} — {_pick_from_pool(pressures, seed, variation_index)}",
        "source_of_pressure": _pick_from_pool(sources, seed, variation_index + 1),
        "what_theyre_supposed_to_know": "What I want to do with my life",
        "the_truth": "I can barely decide what to eat for lunch",
        "comparison_trap": "Everyone else seems to have passions and plans",
        "what_theyd_say_if_honest": _pick_from_pool(honest_truths, seed, variation_index + 2)
    }


def _create_comparison_trap_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create comparison culture/social media comparison variant."""
    topic = _humanize_topic(title)
    
    triggers = [
        "Scrolling and seeing someone's perfect life",
        "A post from someone doing better than me",
        "Photos from events I wasn't invited to",
        "Someone achieving what I've been trying for",
        "Highlight reels that make my real life feel small"
    ]
    
    who_comparing = [
        "Girls who seem to have it all figured out",
        "People with more followers, more friends, more everything",
        "The version of me I thought I'd be by now",
        "Influencers who make it all look easy",
        "People whose lives look like the ones I want"
    ]
    
    what_it_does = [
        "Makes my own life feel small and behind",
        "Triggers a spiral of everything I'm not",
        "Takes the joy out of my own achievements",
        "Makes me question if I'm doing anything right",
        "Steals hours and leaves me feeling worse"
    ]
    
    return {
        "the_trigger": f"When {topic.lower()} triggers — {_pick_from_pool(triggers, seed, variation_index)}",
        "who_theyre_comparing_to": _pick_from_pool(who_comparing, seed, variation_index + 1),
        "what_it_does": _pick_from_pool(what_it_does, seed, variation_index + 2),
        "logical_brain": "I know it's curated, I know it's highlight reels",
        "emotional_reality": "Still feels like proof that I'm failing somehow",
        "breaking_point": "Had to delete the app for my own sanity"
    }


# =============================================================================
# BLEND VARIANT CREATION HELPERS
# =============================================================================

def _create_butterflies_anxiety_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create butterflies + anxiety blend variant."""
    topic = _humanize_topic(title)
    
    feelings = [
        "Heart racing - half butterflies, half panic attack",
        "Excitement and dread doing a tango in my chest",
        "The good nervous and the bad nervous all at once",
        "Giddy terror - there's no other word for it",
        "Wanting this moment and wanting to escape it simultaneously"
    ]
    
    conflicts = [
        "Wanting them to notice me while hoping I'm invisible to everyone else",
        "Desperate to be seen, terrified of being watched",
        "Craving connection, dreading the vulnerability it requires",
        "Hoping they look my way, planning my exit route",
        "The fantasy vs the fear of it actually happening"
    ]
    
    return {
        "the_feeling": f"{_pick_from_pool(feelings, seed, variation_index)} — related to {topic.lower()}",
        "what_they_want": "For them to notice, just them",
        "what_they_fear": "What if I freeze? What if everyone sees?",
        "the_conflict": _pick_from_pool(conflicts, seed, variation_index + 1),
        "coping_attempt": "Deep breaths, phone as shield, planned escape routes",
        "internal_chaos": "Be cool be cool be cool - oh god they're looking this way"
    }


def _create_body_comparison_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create body acceptance + comparison trap blend variant."""
    topic = _humanize_topic(title)
    
    scrolls = [
        "Perfect bodies, perfect skin, perfect everything",
        "Before and after transformations that look impossible",
        "That girl who makes everything look effortless",
        "Influencers in bikinis like it's nothing",
        "Everyone's glow-up except mine"
    ]
    
    rebellions = [
        "Wearing the outfit anyway",
        "Refusing to suck in for photos",
        "Eating without counting, just this once",
        "Unfollowing, muting, protecting my peace",
        "Looking in the mirror and not cataloging flaws"
    ]
    
    return {
        "the_scroll": f"When {topic.lower()} fills my feed — {_pick_from_pool(scrolls, seed, variation_index)}",
        "the_mirror": "All the ways I don't measure up",
        "the_knowledge": "Filters, angles, editing - none of it's real",
        "the_feeling": "But what if they're just naturally like that and I'm not?",
        "the_exhaustion": "I'm so tired of hating what I see",
        "small_rebellion": _pick_from_pool(rebellions, seed, variation_index + 1)
    }


def _create_online_fitting_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create online connection + fitting in blend variant."""
    topic = _humanize_topic(title)
    
    irl_struggles = [
        "Every word feels scripted, every interaction exhausting",
        "Never knowing the right thing to say until it's too late",
        "Feeling like everyone got a manual I never received",
        "The gap between who I am and who I perform",
        "Belonging that requires becoming someone else"
    ]
    
    online_ease = [
        "I can be myself in text, think before I respond",
        "Time to process, no pressure to be instant",
        "They like me for my thoughts, not my performance",
        "Deleting and rewriting until it's right",
        "Being weird is normal here"
    ]
    
    return {
        "irl_struggle": f"When it comes to {topic.lower()} — {_pick_from_pool(irl_struggles, seed, variation_index)}",
        "online_ease": _pick_from_pool(online_ease, seed, variation_index + 1),
        "the_irony": "More 'real' with people I've never met than people I see daily",
        "what_irl_people_think": "'You should get out more' 'Those aren't real friends'",
        "the_truth": "They've seen me ugly cry at 3am - that's real enough",
        "both_worlds": "Code-switching between who they expect and who I actually am"
    }


def _create_future_comparison_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create future anxiety + comparison trap blend variant."""
    topic = _humanize_topic(title)
    
    their_plans = [
        "Med school, gap year, starting a business - everyone has A Thing",
        "Applications submitted, acceptances celebrated, futures secured",
        "Internships, passion projects, five-year plans",
        "They've known what they wanted since they were twelve",
        "LinkedIn profiles that read like success stories"
    ]
    
    quiet_hopes = [
        "Maybe not knowing yet means I could be anything",
        "Maybe my path just isn't linear",
        "Maybe the late bloomers have their own garden",
        "Maybe I'm not behind, just on a different road",
        "Maybe uncertainty is its own kind of possibility"
    ]
    
    return {
        "their_plans": f"Everyone else and {topic.lower()} — {_pick_from_pool(their_plans, seed, variation_index)}",
        "your_blank": "A future that looks like a fog machine",
        "the_question": "'So what's your plan?' at every gathering",
        "the_lie": "'Still figuring it out!' said with fake confidence",
        "the_spiral": "Maybe I'm just not the kind of person who has dreams",
        "quiet_hope": _pick_from_pool(quiet_hopes, seed, variation_index + 1)
    }


def _create_body_butterflies_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create body acceptance + first butterflies blend variant."""
    topic = _humanize_topic(title)
    
    blocks = [
        "'They'd never look at someone like me'",
        "How can they like this when I don't?",
        "They deserve someone who looks like the people they follow",
        "I'd have to be different to be worth wanting",
        "The mirror said no before they could"
    ]
    
    fantasies = [
        "Walk up, be confident, just talk to them",
        "Let them see me without apologizing for existing",
        "Wear what I want, not what hides me best",
        "Believe them if they said something nice",
        "Exist in their space like I belong there"
    ]
    
    return {
        "the_attraction": f"Something about them and {topic.lower()} that draws me in",
        "the_block": _pick_from_pool(blocks, seed, variation_index),
        "the_fantasy": _pick_from_pool(fantasies, seed, variation_index + 1),
        "the_reality": "Look away, hide, convince myself it's not worth trying",
        "almost_moment": "They smiled at me and I almost smiled back before I remembered",
        "the_wish": "That I could see myself the way I see everyone else"
    }


def _create_online_future_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create online connection + future anxiety blend variant."""
    topic = _humanize_topic(title)
    
    irl_pressures = [
        "'You need to start thinking seriously about your future'",
        "'When I was your age I already knew what I wanted'",
        "'Your cousin got accepted early decision, you know'",
        "'What's the plan? What's the backup plan?'",
        "'You're running out of time to figure this out'"
    ]
    
    online_understanding = [
        "'Same, I have no idea what I'm doing either'",
        "'Honestly? Everyone's just pretending they know'",
        "'At least we're lost together'",
        "'No one our age actually has it figured out'",
        "'Can we just be confused in peace?'"
    ]
    
    return {
        "irl_pressure": f"About {topic.lower()} — {_pick_from_pool(irl_pressures, seed, variation_index)}",
        "online_understanding": _pick_from_pool(online_understanding, seed, variation_index + 1),
        "the_conversation": "3am voice chat where we all admitted we're terrified",
        "the_relief": "Not being the only one who doesn't have it figured out",
        "the_gap": "Online: 'it's okay to not know' / Offline: 'you should know by now'",
        "shared_uncertainty": "Building a support system of equally lost people"
    }


def _create_fitting_comparison_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create fitting in + comparison trap blend variant."""
    topic = _humanize_topic(title)
    
    thems = [
        "Walking into rooms like they own them, effortless conversation",
        "Never seeming to second-guess what they just said",
        "Laughing without checking if it was the right amount",
        "Belonging without earning it, like it's their birthright",
        "Confidence that doesn't look like a costume"
    ]
    
    secret_truths = [
        "Maybe everyone's performing and I just think I'm the only one",
        "What if being bad at this is normal and no one talks about it?",
        "Maybe 'natural' is just 'practiced until invisible'",
        "What if they're all exhausted too, just hiding it better?",
        "Maybe belonging is something everyone's faking"
    ]
    
    return {
        "them": f"People and {topic.lower()} — {_pick_from_pool(thems, seed, variation_index)}",
        "you": "Calculating every word, planning escape routes",
        "the_performance": "Laughing at the right times, nodding along, seeming present",
        "the_exhaustion": "Social hangover that lasts for days",
        "the_question": "Are they actually confident or just better at pretending?",
        "secret_truth": _pick_from_pool(secret_truths, seed, variation_index + 1)
    }


def _create_confession_body_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create confession moment + body acceptance blend variant."""
    topic = _humanize_topic(title)
    
    secrets = [
        "I've never liked a single photo of myself",
        "I spend more time hating my body than living in it",
        "The mirror and I have never been friends",
        "I don't know when I started feeling wrong, but I can't remember before",
        "I've never felt at home in my own skin"
    ]
    
    hardest_parts = [
        "That I spend hours some days just... hating",
        "That I've skipped things because of how I thought I'd look",
        "That compliments feel like lies I have to pretend to believe",
        "That I've been at war with myself for years",
        "That I'm exhausted from the constant negotiation"
    ]
    
    return {
        "the_secret": f"What I've been hiding about {topic.lower()} — {_pick_from_pool(secrets, seed, variation_index)}",
        "who_youre_telling": "Someone who might finally understand",
        "why_now": "I can't keep pretending I'm fine",
        "the_hardest_part": _pick_from_pool(hardest_parts, seed, variation_index + 1),
        "their_response": "Please don't tell me I'm beautiful, just tell me you understand",
        "after_speaking": "Lighter, even though nothing's fixed"
    }


def _create_unsent_future_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create unsent message + future anxiety blend variant."""
    topic = _humanize_topic(title)
    
    messages = [
        "Your 'helpful' questions feel like you're measuring my worth by my resume",
        "I don't have the answers you want and your disappointment is exhausting",
        "I'm terrified and your pressure isn't helping",
        "Can you love me even without a plan?",
        "I need support, not more expectations"
    ]
    
    what_needed = [
        "'I believe in you even if you don't know yet'",
        "'Your worth isn't tied to your productivity'",
        "'Take your time. The right path will become clear'",
        "'I'm proud of you for who you are, not what you achieve'",
        "'It's okay to not have it figured out yet'"
    ]
    
    return {
        "to_whom": f"Everyone who keeps asking about {topic.lower()}",
        "the_message": _pick_from_pool(messages, seed, variation_index),
        "what_sparked_it": "Another conversation where my future was the main topic",
        "why_unsent": "They'd just worry more and ask different questions",
        "what_youd_need": _pick_from_pool(what_needed, seed, variation_index + 1),
        "instead": "'Still exploring my options!' with a practiced smile"
    }


def _create_mirror_body_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create mirror moment + body acceptance blend variant."""
    topic = _humanize_topic(title)
    
    moments = [
        "Getting out of the shower, not avoiding the mirror for once",
        "Catching my reflection unexpectedly and pausing",
        "Looking - really looking - instead of glancing and flinching",
        "A moment where the usual script didn't play",
        "Seeing myself through different eyes, just for a second"
    ]
    
    new_thoughts = [
        "This body has been fighting for me while I've been fighting against it",
        "Maybe we can be on the same team",
        "What if I stopped treating myself like an enemy?",
        "I've survived things. This body carried me through.",
        "There's more to me than what I see in reflections"
    ]
    
    return {
        "the_moment": f"A mirror moment about {topic.lower()} — {_pick_from_pool(moments, seed, variation_index)}",
        "usual_script": "Catalog of flaws, comparison to an impossible standard",
        "the_shift": "Something was different this time",
        "new_thought": _pick_from_pool(new_thoughts, seed, variation_index + 1),
        "what_it_means": "Maybe a truce is possible",
        "still_uncertain": "Tomorrow I might hate it again, but today was different"
    }


def _create_growing_online_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create growing apart + online connection blend variant."""
    topic = _humanize_topic(title)
    
    old_friends = [
        "Known her since third grade, but conversations feel like work now",
        "The person who used to know me without words",
        "Someone I share history with but not much else anymore",
        "A friendship running on nostalgia and obligation",
        "We've become strangers who know each other's childhood"
    ]
    
    defenses = [
        "Connection isn't measured in proximity",
        "Real isn't defined by being in the same room",
        "Depth doesn't require face-to-face",
        "They know my soul. Geography is irrelevant.",
        "Some people meet you where you are. Some just knew where you were."
    ]
    
    return {
        "the_old_friend": f"The IRL connection fading, related to {topic.lower()} — {_pick_from_pool(old_friends, seed, variation_index)}",
        "the_new_friend": "Someone online who gets it without explanation",
        "what_changed": "Realized I was excited to go home and text them, not to meet her",
        "the_guilt": "Am I a bad friend? Am I replacing her?",
        "the_defense": _pick_from_pool(defenses, seed, variation_index + 1),
        "the_truth": "People grow in different directions. It's sad but it's okay."
    }


def _create_quiet_body_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create quiet rebellion + body acceptance blend variant."""
    topic = _humanize_topic(title)
    
    rules = [
        "'Girls like you shouldn't wear that'",
        "'You'd look better if you just...'",
        "'That's not flattering on your body type'",
        "'Are you sure you want to eat that?'",
        "'You should try to be healthier' (but they mean thinner)"
    ]
    
    rebellions = [
        "Wearing the crop top anyway",
        "Eating dessert without earning it with exercise",
        "Taking up space without apologizing",
        "Posting a photo without editing",
        "Existing in public like I belong there"
    ]
    
    return {
        "the_rule": f"The body rule about {topic.lower()} — {_pick_from_pool(rules, seed, variation_index)}",
        "who_made_it": "Comments, looks, diet culture, everywhere",
        "the_rebellion": _pick_from_pool(rebellions, seed, variation_index + 1),
        "the_fear": "People staring, people laughing, people confirming what I fear",
        "the_power": "Doing it anyway, terrified and free",
        "the_message": "My body is allowed to exist in spaces, in clothes, in public"
    }


def _create_chosen_online_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create chosen family + online connection blend variant."""
    topic = _humanize_topic(title)
    
    groups = [
        "Five people scattered across four time zones",
        "A group chat that's been going for years",
        "Strangers who became siblings",
        "People who found each other in the digital wilderness",
        "A community that became a family"
    ]
    
    what_they_give = [
        "Unconditional support, 2am check-ins, inside jokes that span years",
        "A place where I don't have to explain myself",
        "Love that doesn't require performance",
        "The kind of acceptance I didn't get at home",
        "Chosen family in the truest sense"
    ]
    
    return {
        "the_group": f"My online family around {topic.lower()} — {_pick_from_pool(groups, seed, variation_index)}",
        "how_found": "A fandom/interest that became so much more",
        "what_they_give": _pick_from_pool(what_they_give, seed, variation_index + 1),
        "irl_gap": "What's missing in offline relationships",
        "defining_moment": "When they showed up for me in a way no one else had",
        "future_hope": "One day we'll all be in the same room"
    }


def _create_permission_body_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create permission to + body acceptance blend variant."""
    topic = _humanize_topic(title)
    
    permissions = [
        "To not hate what I see",
        "To exist without shrinking",
        "To stop the constant negotiation with food",
        "To buy clothes I like instead of clothes that hide",
        "To be in photos without analyzing them for hours"
    ]
    
    first_steps = [
        "Eating when I'm hungry without negotiating with myself",
        "Wearing something I've been hiding in my closet",
        "Looking in the mirror without the usual script",
        "Saying 'thank you' to a compliment instead of arguing",
        "Letting myself rest without earning it"
    ]
    
    return {
        "the_permission": f"Permission about {topic.lower()} — {_pick_from_pool(permissions, seed, variation_index)}",
        "the_war": "Years of monitoring, controlling, hating",
        "what_triggered": "Realized I don't remember a time I liked my body",
        "the_fear": "If I stop fighting, will I 'let myself go'?",
        "the_relief": "What would it be like to just... exist? Without the commentary?",
        "first_step": _pick_from_pool(first_steps, seed, variation_index + 1)
    }


def _create_small_comparison_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create small moment big + comparison trap blend variant."""
    topic = _humanize_topic(title)
    
    small_things = [
        "She got more likes on a similar photo",
        "They invited her and not me",
        "A comment that was probably nothing",
        "Seeing them tagged in something I wasn't part of",
        "The smallest thing that proved everything I feared"
    ]
    
    realizations = [
        "I've been measuring my worth in double-taps",
        "The comparison has been running in the background constantly",
        "I didn't know how much I needed external validation until this",
        "This isn't about them. It's about what I already believed about myself.",
        "The comparison trap has me and I didn't even see the walls"
    ]
    
    return {
        "the_small_thing": f"A tiny thing about {topic.lower()} — {_pick_from_pool(small_things, seed, variation_index)}",
        "why_big": "Because it confirmed what I already believed",
        "the_comparison": "Her: effortless. Me: trying so hard and still less",
        "the_spiral": "Maybe I'm just... less likable, less pretty, less everything",
        "the_realization": _pick_from_pool(realizations, seed, variation_index + 1),
        "what_now": "Maybe worth isn't a number. Maybe it never was."
    }


def _create_identity_fitting_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create identity power + fitting in blend variant."""
    topic = _humanize_topic(title)
    
    who_you_are = [
        "Weird interests, strong opinions, too much or not enough",
        "The person who doesn't fit the mold",
        "Someone whose authentic self clashes with expectations",
        "Different in ways that are hard to hide",
        "The version of me that makes people uncomfortable"
    ]
    
    choices = [
        "Keep performing or let them see",
        "Belonging at the cost of being myself",
        "The exhaustion of pretending vs the fear of being seen",
        "Hiding to fit in or showing up and maybe being alone",
        "Safety of blending in vs authenticity that stands out"
    ]
    
    return {
        "who_you_are": f"My authentic self with {topic.lower()} — {_pick_from_pool(who_you_are, seed, variation_index)}",
        "what_fitting_requires": "Dulling the edges, caring about the right stuff",
        "the_cost": "Feeling like a ghost in my own life",
        "the_risk": "Being alone, being mocked, being the weird one",
        "the_choice": _pick_from_pool(choices, seed, variation_index + 1),
        "the_power": "The exhaustion of pretending is worse than the fear of being seen"
    }


def _create_learned_body_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create learned young + body acceptance blend variant."""
    topic = _humanize_topic(title)
    
    lessons = [
        "That taking up space was bad, that hunger was weakness",
        "That my body was a project to be fixed",
        "That certain foods were 'good' and eating was something to monitor",
        "That I should always be smaller than I am",
        "That my worth and my weight were connected"
    ]
    
    unlearnings = [
        "My body is a home, not a project",
        "Hunger is information, not failure",
        "I'm allowed to take up exactly as much space as I take up",
        "My worth has nothing to do with my size",
        "I can stop fighting the body that's kept me alive"
    ]
    
    return {
        "the_lesson": f"What I learned young about {topic.lower()} — {_pick_from_pool(lessons, seed, variation_index)}",
        "who_taught": "Mom's comments, magazines, everything everywhere",
        "how_it_stuck": "Started monitoring myself before I knew what I was monitoring",
        "the_damage": "Never just... existing. Always calculating, comparing, controlling",
        "the_unlearning": _pick_from_pool(unlearnings, seed, variation_index + 1),
        "the_work": "Catching the old thoughts, replacing them, being patient with the process"
    }


def _create_safe_online_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create safe person + online connection blend variant."""
    topic = _humanize_topic(title)
    
    who_they_are = [
        "Someone I met online five years ago, never seen their face",
        "A username that became the person I trust most",
        "A stranger who knows me better than my family",
        "Someone I found in the comments and never stopped talking to",
        "My safest person, 3000 miles away"
    ]
    
    what_you_share = [
        "The thoughts I can't say out loud, the fears that feel too dramatic",
        "The ugly parts I hide from everyone else",
        "The version of me that would scare people in person",
        "Everything I've been told is 'too much'",
        "The full truth, not the edited version"
    ]
    
    return {
        "who_they_are": f"My safe person online, related to {topic.lower()} — {_pick_from_pool(who_they_are, seed, variation_index)}",
        "how_safety_built": "Slow sharing, matched vulnerability, never judgment",
        "what_you_share": _pick_from_pool(what_you_share, seed, variation_index + 1),
        "the_paradox": "A stranger knows me better than my family",
        "what_others_say": "'That's not a real friendship' 'You should talk to real people'",
        "why_it_works": "No history to disappoint, no face to perform for"
    }


def _create_rewriting_body_variant(title: str, description: str, kwargs: Dict, seed: int, variation_index: int) -> Dict[str, Any]:
    """Create rewriting story + body acceptance blend variant."""
    topic = _humanize_topic(title)
    
    old_stories = [
        "'My body is wrong and needs fixing'",
        "'I'll be happy when I'm thinner'",
        "'I don't deserve to be seen like this'",
        "'Good things don't happen to people who look like me'",
        "'My body is the enemy and I'm losing the war'"
    ]
    
    new_stories = [
        "My body is trying its best. So am I.",
        "My worth isn't measured in pounds or inches",
        "This body has survived things. It deserves gentleness.",
        "I'm allowed to exist exactly as I am",
        "The war is optional. I can choose peace."
    ]
    
    return {
        "old_story": f"The story about {topic.lower()} — {_pick_from_pool(old_stories, seed, variation_index)}",
        "who_wrote_it": "Diet culture, that one comment in middle school, mirrors that felt like enemies",
        "the_chapter": "The moment that started the story",
        "new_story": _pick_from_pool(new_stories, seed, variation_index + 1),
        "the_evidence": "It healed when I was sick. It carries me through hard days. It's trying.",
        "work_in_progress": "Some days the old story wins. But less often now."
    }


__all__ = [
    # Constants
    "VARIANT_TEMPLATES",
    "VARIANT_WEIGHTS",
    "DEFAULT_IDEA_COUNT",
    "DEFAULT_DECAY_FACTOR",
    "MIN_DECAY_WEIGHT",
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
    # Story seed templates for US women 13-20
    "VARIANT_CONFESSION_MOMENT",
    "VARIANT_BEFORE_AFTER",
    "VARIANT_OVERHEARD_TRUTH",
    "VARIANT_PARALLEL_LIVES",
    "VARIANT_LAST_TIME",
    "VARIANT_UNSENT_MESSAGE",
    "VARIANT_SMALL_MOMENT_BIG",
    "VARIANT_ALMOST_SAID",
    "VARIANT_WHAT_THEY_DONT_KNOW",
    "VARIANT_QUIET_REBELLION",
    "VARIANT_MIRROR_MOMENT",
    "VARIANT_CHOSEN_FAMILY",
    "VARIANT_GROWING_APART",
    "VARIANT_PERMISSION_TO",
    "VARIANT_LEARNED_YOUNG",
    "VARIANT_THE_VERSION_OF_ME",
    "VARIANT_EMOTIONAL_INHERITANCE",
    "VARIANT_SAFE_PERSON",
    "VARIANT_HOLDING_SPACE",
    "VARIANT_REWRITING_THE_STORY",
    # Fusion variant templates
    "VARIANT_CONFESSION_MYSTERY",
    "VARIANT_OVERHEARD_TRANSFORMATION",
    "VARIANT_UNSENT_REBELLION",
    "VARIANT_MIRROR_INHERITANCE",
    "VARIANT_CHOSEN_GROWING",
    "VARIANT_PARALLEL_PERMISSION",
    # Missing theme templates
    "VARIANT_FIRST_BUTTERFLIES",
    "VARIANT_BODY_ACCEPTANCE",
    "VARIANT_FITTING_IN",
    "VARIANT_ONLINE_CONNECTION",
    "VARIANT_FUTURE_ANXIETY",
    "VARIANT_COMPARISON_TRAP",
    # Blend template definitions
    "VARIANT_BUTTERFLIES_ANXIETY",
    "VARIANT_BODY_COMPARISON",
    "VARIANT_ONLINE_FITTING",
    "VARIANT_FUTURE_COMPARISON",
    "VARIANT_BODY_BUTTERFLIES",
    "VARIANT_ONLINE_FUTURE",
    "VARIANT_FITTING_COMPARISON",
    "VARIANT_CONFESSION_BODY",
    "VARIANT_UNSENT_FUTURE",
    "VARIANT_MIRROR_BODY",
    "VARIANT_GROWING_ONLINE",
    "VARIANT_QUIET_BODY",
    "VARIANT_CHOSEN_ONLINE",
    "VARIANT_PERMISSION_BODY",
    "VARIANT_SMALL_COMPARISON",
    "VARIANT_IDENTITY_FITTING",
    "VARIANT_LEARNED_BODY",
    "VARIANT_SAFE_ONLINE",
    "VARIANT_REWRITING_BODY",
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
