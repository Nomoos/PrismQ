"""Story seed variant templates - designed for US women 13-20."""

from typing import Dict, Any


VARIANT_CONFESSION_MOMENT = {
    "name": "Confession Moment",
    "description": "A moment of confession or reveal",
    "fields": {
        "the_secret": "What's being confessed",
        "why_now": "Why this moment to share",
        "to_whom": "Who receives the confession",
        "the_buildup": "What led to this moment",
        "the_reaction": "How it's received",
        "the_aftermath": "What changes after"
    },
    "example": {
        "the_secret": "Something I've been hiding about who I really am",
        "why_now": "Couldn't hold it anymore",
        "to_whom": "The person who needed to know",
        "the_buildup": "Small moments that made hiding impossible",
        "the_reaction": "Not what I expected",
        "the_aftermath": "Everything shifted, but not how I feared"
    }
}

VARIANT_BEFORE_AFTER = {
    "name": "Before/After",
    "description": "Transformation or change story",
    "fields": {
        "before_state": "What things were like before",
        "catalyst": "What triggered the change",
        "during_transition": "The messy middle",
        "after_state": "What things are like now",
        "what_i_miss": "What was lost in the change",
        "what_i_gained": "What was gained"
    },
    "example": {
        "before_state": "When I thought I knew who I was",
        "catalyst": "The thing that shattered that certainty",
        "during_transition": "Lost, confused, rebuilding",
        "after_state": "A different kind of knowing",
        "what_i_miss": "The simplicity of before",
        "what_i_gained": "Authenticity I didn't know I was missing"
    }
}

VARIANT_OVERHEARD_TRUTH = {
    "name": "Overheard Truth",
    "description": "Learning something by accident",
    "fields": {
        "what_was_heard": "The revelation overheard",
        "who_said_it": "Who was speaking",
        "the_context": "Where/when this happened",
        "immediate_feeling": "First reaction",
        "what_it_changed": "How this knowledge shifted things",
        "what_i_did": "The response chosen"
    },
    "example": {
        "what_was_heard": "Something said when they didn't know I was listening",
        "who_said_it": "Someone I trusted",
        "the_context": "Just around the corner, out of sight",
        "immediate_feeling": "Heart dropping, mind racing",
        "what_it_changed": "How I see that relationship now",
        "what_i_did": "Had to decide: confront or pretend I never heard"
    }
}

VARIANT_PARALLEL_LIVES = {
    "name": "Parallel Lives",
    "description": "What-if version of self",
    "fields": {
        "the_split": "The moment paths could have diverged",
        "the_other_path": "The life not lived",
        "who_i_am_now": "Who I became instead",
        "what_i_wonder": "The questions about the other path",
        "which_is_better": "The comparison I can't help making",
        "the_truth": "What I've accepted about choice"
    },
    "example": {
        "the_split": "That one decision that changed everything",
        "the_other_path": "The version of me who chose differently",
        "who_i_am_now": "This version, with these scars and strengths",
        "what_i_wonder": "Would she be happier? More successful?",
        "which_is_better": "Maybe neither. Maybe both.",
        "the_truth": "Every path has its losses and wins"
    }
}

VARIANT_LAST_TIME = {
    "name": "Last Time",
    "description": "The last moment before change",
    "fields": {
        "the_last_time": "What happened for the last time",
        "did_i_know": "Whether I knew it was the last",
        "what_i_remember": "The details that stuck",
        "what_came_after": "What replaced it",
        "the_grief": "What I mourn about that ending",
        "the_gift": "What that last time gave me"
    },
    "example": {
        "the_last_time": "The last time everything felt simple",
        "did_i_know": "I had no idea it would be the last",
        "what_i_remember": "Small details I wish I'd savored",
        "what_came_after": "A new reality I wasn't ready for",
        "the_grief": "The innocence that can't come back",
        "the_gift": "Appreciation for ordinary moments"
    }
}

VARIANT_UNSENT_MESSAGE = {
    "name": "Unsent Message",
    "description": "Words never shared",
    "fields": {
        "the_message": "What I wrote but never sent",
        "who_it_was_for": "The intended recipient",
        "why_i_didnt_send": "What stopped me",
        "what_i_sent_instead": "The safer version (or nothing)",
        "what_would_have_changed": "The ripple effects of sending",
        "where_it_lives_now": "Where these unsaid words exist"
    },
    "example": {
        "the_message": "Everything I really wanted to say",
        "who_it_was_for": "The person who needed to hear it",
        "why_i_didnt_send": "Fear. Pride. Timing. All of it.",
        "what_i_sent_instead": "Something safer, less true",
        "what_would_have_changed": "Maybe everything. Maybe nothing.",
        "where_it_lives_now": "In drafts. In my head. In the space between us."
    }
}

VARIANT_SMALL_MOMENT_BIG = {
    "name": "Small Moment Big Impact",
    "description": "Tiny moment with huge meaning",
    "fields": {
        "the_moment": "The seemingly small thing that happened",
        "why_it_seems_small": "Why others might dismiss it",
        "why_it_was_big": "What made it actually significant",
        "what_it_revealed": "The truth it exposed",
        "the_shift": "How I changed because of it",
        "the_lesson": "What I carry from that moment"
    },
    "example": {
        "the_moment": "A single sentence someone said without thinking",
        "why_it_seems_small": "Just words, easily forgotten",
        "why_it_was_big": "It confirmed something I'd suspected",
        "what_it_revealed": "How they really saw me",
        "the_shift": "Permission to trust my instincts",
        "the_lesson": "Small moments tell big truths"
    }
}

VARIANT_ALMOST_SAID = {
    "name": "Almost Said",
    "description": "Words caught before speaking",
    "fields": {
        "what_i_almost_said": "The words that nearly came out",
        "what_stopped_me": "Why I held back",
        "what_i_said_instead": "The edited version",
        "their_reaction": "How they responded to the safer words",
        "what_they_dont_know": "The truth they're missing",
        "the_weight": "How carrying unsaid things feels"
    },
    "example": {
        "what_i_almost_said": "The honest answer to 'how are you?'",
        "what_stopped_me": "Not sure they actually want to know",
        "what_i_said_instead": "'Fine, just tired'",
        "their_reaction": "Moved on, conversation continued",
        "what_they_dont_know": "I needed someone to ask twice",
        "the_weight": "The loneliness of edited truth"
    }
}

VARIANT_WHAT_THEY_DONT_KNOW = {
    "name": "What They Don't Know",
    "description": "Hidden truths about self",
    "fields": {
        "who_they_are": "The people who don't know",
        "what_they_see": "The version I show them",
        "what_they_dont_see": "What I hide",
        "why_i_hide_it": "The reason for the mask",
        "the_exhaustion": "The cost of hiding",
        "the_wish": "What it would take to show them"
    },
    "example": {
        "who_they_are": "My friends, family, everyone",
        "what_they_see": "The together version",
        "what_they_dont_see": "The mess behind closed doors",
        "why_i_hide_it": "Don't want to be a burden",
        "the_exhaustion": "Performing okay is its own full-time job",
        "the_wish": "Someone to know without me having to say"
    }
}

VARIANT_QUIET_REBELLION = {
    "name": "Quiet Rebellion",
    "description": "Small acts of defiance",
    "fields": {
        "the_expectation": "What I was supposed to do/be",
        "the_quiet_no": "My small act of rebellion",
        "who_noticed": "Did anyone see?",
        "what_it_felt_like": "The feeling of small defiance",
        "what_it_meant": "Why it mattered even if small",
        "the_bigger_picture": "What I'm really fighting for"
    },
    "example": {
        "the_expectation": "Be perfect, be agreeable, be small",
        "the_quiet_no": "Said what I actually thought for once",
        "who_noticed": "Maybe no one. Maybe everyone.",
        "what_it_felt_like": "Terrifying and alive",
        "what_it_meant": "Proof I still exist under the expectations",
        "the_bigger_picture": "The right to be my own person"
    }
}

VARIANT_MIRROR_MOMENT = {
    "name": "Mirror Moment",
    "description": "Seeing self clearly",
    "fields": {
        "what_i_saw": "The reflection that hit different",
        "when_it_happened": "The moment of seeing",
        "why_it_hit": "What made this time different",
        "what_i_realized": "The truth in the reflection",
        "the_before": "How I saw myself before",
        "the_after": "How I see myself now"
    },
    "example": {
        "what_i_saw": "Not just my face, but who I've become",
        "when_it_happened": "Ordinary moment, extraordinary clarity",
        "why_it_hit": "Saw past the performance to the real",
        "what_i_realized": "I don't recognize myself anymore",
        "the_before": "The version I thought I was",
        "the_after": "The version I might need to become"
    }
}

VARIANT_CHOSEN_FAMILY = {
    "name": "Chosen Family",
    "description": "Found family over blood",
    "fields": {
        "who_they_are": "My chosen family",
        "how_we_found_each_other": "The origin story",
        "what_makes_them_family": "Why they count as family",
        "what_blood_family_couldnt_give": "The gap they fill",
        "a_moment_that_proved_it": "When I knew for sure",
        "what_family_means_now": "My new definition"
    },
    "example": {
        "who_they_are": "Friends who became more than friends",
        "how_we_found_each_other": "Unlikely circumstances, perfect timing",
        "what_makes_them_family": "Show up when it matters. Always.",
        "what_blood_family_couldnt_give": "Understanding without explanation",
        "a_moment_that_proved_it": "The crisis they stayed for",
        "what_family_means_now": "The people who choose to stay"
    }
}

VARIANT_GROWING_APART = {
    "name": "Growing Apart",
    "description": "Relationships changing with growth",
    "fields": {
        "who_we_were": "The relationship at its peak",
        "the_drift": "When the distance started",
        "what_changed": "The growth that created distance",
        "the_grief": "Mourning a living relationship",
        "what_i_still_love": "What remains despite the distance",
        "where_we_are_now": "The new shape of us"
    },
    "example": {
        "who_we_were": "Inseparable. Finishing sentences.",
        "the_drift": "Slow at first, then obvious",
        "what_changed": "I grew. Or they did. Maybe both.",
        "the_grief": "Missing someone who's still here",
        "what_i_still_love": "The history we share",
        "where_we_are_now": "Different orbits. Same universe."
    }
}

VARIANT_PERMISSION_TO = {
    "name": "Permission To",
    "description": "Allowing self to feel/be",
    "fields": {
        "what_i_needed_permission_for": "The thing I held back",
        "who_i_thought_had_to_give_it": "Where I looked for permission",
        "what_i_realized": "That I could give it to myself",
        "the_moment_i_gave_it": "When I finally let myself",
        "what_it_felt_like": "The feeling of self-permission",
        "what_changed": "Life after giving myself permission"
    },
    "example": {
        "what_i_needed_permission_for": "To be angry. To be sad. To be me.",
        "who_i_thought_had_to_give_it": "Someone, anyone, other than me",
        "what_i_realized": "I was the one holding the key",
        "the_moment_i_gave_it": "Decided I was allowed",
        "what_it_felt_like": "Terrifying freedom",
        "what_changed": "Started living instead of waiting to live"
    }
}

VARIANT_LEARNED_YOUNG = {
    "name": "Learned Young",
    "description": "Early lessons that stuck",
    "fields": {
        "what_i_learned": "The lesson from childhood",
        "how_i_learned_it": "The experience that taught it",
        "who_taught_me": "Intentionally or not",
        "how_it_shaped_me": "What it made me believe",
        "is_it_true": "Whether the lesson holds up",
        "unlearning": "What I'm trying to undo"
    },
    "example": {
        "what_i_learned": "Don't ask for too much",
        "how_i_learned_it": "Watching needs be ignored",
        "who_taught_me": "Family, without meaning to",
        "how_it_shaped_me": "Learned to need less. Want less.",
        "is_it_true": "Maybe it was survival, not truth",
        "unlearning": "Learning to take up space again"
    }
}

VARIANT_THE_VERSION_OF_ME = {
    "name": "The Version of Me",
    "description": "Different selves in different spaces",
    "fields": {
        "the_context": "The specific situation or space",
        "who_i_am_there": "The version I become",
        "why_that_version": "Why this context brings this self",
        "the_contrast": "How different from other versions",
        "which_is_real": "The question of authenticity",
        "integration": "Learning to hold all versions"
    },
    "example": {
        "the_context": "At home vs. at school vs. online",
        "who_i_am_there": "Different voices, different selves",
        "why_that_version": "Safety, expectation, habit",
        "the_contrast": "Sometimes I don't recognize the other me",
        "which_is_real": "All of them? None of them?",
        "integration": "Finding the thread that connects all versions"
    }
}

VARIANT_EMOTIONAL_INHERITANCE = {
    "name": "Emotional Inheritance",
    "description": "Patterns passed down",
    "fields": {
        "the_pattern": "The inherited emotional pattern",
        "where_it_came_from": "Who passed it down",
        "how_it_shows_up": "Where I see it in myself",
        "the_recognition": "The moment I saw it clearly",
        "the_choice": "To keep or break the pattern",
        "the_work": "What breaking it requires"
    },
    "example": {
        "the_pattern": "Avoiding conflict at any cost",
        "where_it_came_from": "Generations of 'keeping the peace'",
        "how_it_shows_up": "Swallowing words. Performing okay.",
        "the_recognition": "Caught myself doing exactly what they did",
        "the_choice": "This pattern stops with me",
        "the_work": "Learning that conflict isn't catastrophe"
    }
}

VARIANT_SAFE_PERSON = {
    "name": "Safe Person",
    "description": "The person who feels like home",
    "fields": {
        "who_they_are": "My safe person",
        "how_i_knew": "When I realized they were safe",
        "what_i_can_be": "How I am around them",
        "what_they_do": "What makes them safe",
        "what_it_means": "The significance of having this",
        "the_gratitude": "What I want them to know"
    },
    "example": {
        "who_they_are": "The person I don't have to perform for",
        "how_i_knew": "Could be ugly and they stayed",
        "what_i_can_be": "Messy. Real. All of it.",
        "what_they_do": "Nothing. Everything. Just exist.",
        "what_it_means": "Proof that being known is possible",
        "the_gratitude": "You made being myself feel survivable"
    }
}

VARIANT_HOLDING_SPACE = {
    "name": "Holding Space",
    "description": "Being present for someone's pain",
    "fields": {
        "who_i_held_space_for": "The person going through it",
        "what_they_were_facing": "Their struggle",
        "what_i_wanted_to_do": "The urge to fix it",
        "what_i_actually_did": "Just being present",
        "what_it_taught_me": "The lesson about support",
        "the_growth": "How I changed through holding space"
    },
    "example": {
        "who_i_held_space_for": "Someone I love in crisis",
        "what_they_were_facing": "Something I couldn't solve",
        "what_i_wanted_to_do": "Fix it. Make it better. Do something.",
        "what_i_actually_did": "Sat with them. Let them feel.",
        "what_it_taught_me": "Presence is the help",
        "the_growth": "Learned that fixing isn't always love"
    }
}

VARIANT_REWRITING_THE_STORY = {
    "name": "Rewriting the Story",
    "description": "Changing personal narrative",
    "fields": {
        "the_old_story": "The narrative I carried",
        "who_wrote_it": "Where it came from",
        "how_it_shaped_me": "What it made me believe",
        "the_moment_of_questioning": "When I started doubting it",
        "the_new_story": "The narrative I'm choosing",
        "the_rewrite": "How I'm actively changing it"
    },
    "example": {
        "the_old_story": "'I'm too much and not enough'",
        "who_wrote_it": "Critics. Comparisons. My own fear.",
        "how_it_shaped_me": "Made myself smaller. Quieter.",
        "the_moment_of_questioning": "Realized I was living someone else's opinion",
        "the_new_story": "'I'm exactly the amount I'm supposed to be'",
        "the_rewrite": "Catching old thoughts. Choosing new ones."
    }
}


__all__ = [
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
]
