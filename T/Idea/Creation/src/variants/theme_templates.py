"""Theme-based variant templates - specific themes for target audience."""

from typing import Dict, Any


VARIANT_FIRST_BUTTERFLIES = {
    "name": "First Butterflies",
    "description": "Light crush/attraction moments - family-friendly",
    "fields": {
        "the_moment": "When butterflies first appeared",
        "the_person": "Who sparked the feeling (without romance)",
        "the_physical": "How it felt in your body",
        "the_confusion": "Not understanding the feeling",
        "the_telling": "Who you told or didn't tell",
        "the_lesson": "What first attraction taught about feelings"
    },
    "example": {
        "the_moment": "They laughed at my joke and everything changed",
        "the_person": "Someone who suddenly looked different than before",
        "the_physical": "Heart racing, palms sweaty, words disappearing",
        "the_confusion": "Is this what 'like' means? This is terrifying.",
        "the_telling": "Told my pillow. That's it.",
        "the_lesson": "Feelings arrive without permission"
    }
}

VARIANT_BODY_ACCEPTANCE = {
    "name": "Body Acceptance Journey",
    "description": "Body image and self-acceptance story",
    "fields": {
        "the_struggle": "The body image battle",
        "where_it_started": "Origin of body feelings",
        "the_messages": "What I was told about my body",
        "the_turning": "When perspective started shifting",
        "the_work": "The ongoing practice",
        "where_i_am": "Current relationship with body"
    },
    "example": {
        "the_struggle": "At war with my reflection for years",
        "where_it_started": "A comment that shouldn't have mattered but did",
        "the_messages": "Smaller, different, wrong, too much",
        "the_turning": "Seeing someone like me living fully",
        "the_work": "Catching the mean thoughts, trying kinder ones",
        "where_i_am": "Not love yet. Maybe acceptance. That's enough for now."
    }
}

VARIANT_FITTING_IN = {
    "name": "Fitting In Struggle",
    "description": "Social anxiety and belonging",
    "fields": {
        "the_context": "Where fitting in felt impossible",
        "the_trying": "How I tried to belong",
        "the_cost": "What performing belonging cost",
        "the_not_fitting": "The moment I knew I didn't fit",
        "the_question": "Is fitting in worth it?",
        "the_answer": "What I've decided about belonging"
    },
    "example": {
        "the_context": "Every social space I've ever entered",
        "the_trying": "Watching, mimicking, dimming",
        "the_cost": "Exhaustion of being not-quite-me",
        "the_not_fitting": "Laughing at a joke I didn't find funny",
        "the_question": "Would I rather fit or be real?",
        "the_answer": "Looking for places where real fits"
    }
}

VARIANT_ONLINE_CONNECTION = {
    "name": "Online Connection",
    "description": "Digital friendships and parasocial relationships",
    "fields": {
        "the_connection": "Who I connect with online",
        "how_it_started": "The origin of the connection",
        "what_we_share": "What the connection provides",
        "the_distance": "The physical distance reality",
        "the_real": "Whether online connection is 'real'",
        "the_value": "What this connection means"
    },
    "example": {
        "the_connection": "People I've never met but know completely",
        "how_it_started": "A shared interest that became everything",
        "what_we_share": "The thoughts too weird for IRL friends",
        "the_distance": "Thousands of miles, zero distance",
        "the_real": "Anyone who says it's not real doesn't understand",
        "the_value": "Sometimes the most real connections are digital"
    }
}

VARIANT_FUTURE_ANXIETY = {
    "name": "Future Anxiety",
    "description": "College, career, growing up pressure",
    "fields": {
        "the_pressure": "The specific future fear",
        "where_it_comes_from": "Source of the pressure",
        "the_comparison": "How others seem to have it figured out",
        "the_spiral": "When anxiety takes over",
        "the_truth": "What I actually know about the future",
        "the_now": "What I can focus on instead"
    },
    "example": {
        "the_pressure": "Everyone asking 'what's your plan?'",
        "where_it_comes_from": "Expectations. Comparisons. Fear.",
        "the_comparison": "Everyone else seems to know their path",
        "the_spiral": "3am thoughts about failing before starting",
        "the_truth": "No one knows. They're all pretending.",
        "the_now": "Today. Just today. Tomorrow will come."
    }
}

VARIANT_COMPARISON_TRAP = {
    "name": "Comparison Trap",
    "description": "Social media comparison culture",
    "fields": {
        "the_compare": "Who/what I compare myself to",
        "the_platform": "Where the comparing happens most",
        "the_feeling": "How comparison makes me feel",
        "the_reality": "What I forget when comparing",
        "the_break": "Moments of clarity",
        "the_practice": "How I'm trying to stop"
    },
    "example": {
        "the_compare": "Everyone who seems to have it together",
        "the_platform": "Every scroll, every feed",
        "the_feeling": "Small. Behind. Wrong.",
        "the_reality": "Highlight reels vs. my behind the scenes",
        "the_break": "Remembering my own highlight reel exists too",
        "the_practice": "Muting. Unfollowing. Remembering what's real."
    }
}

VARIANT_FANDOM_PASSION = {
    "name": "Fandom Passion",
    "description": "Intense interest in shows, artists, games, books",
    "fields": {
        "the_thing": "What you're passionate about",
        "how_it_found_you": "When/how this passion started",
        "what_it_gave_you": "What this passion provides",
        "the_moment": "A defining fandom moment",
        "what_others_dont_get": "What non-fans misunderstand",
        "why_it_matters": "Why this passion is important"
    },
    "example": {
        "the_thing": "That one animated series that changed everything",
        "how_it_found_you": "Started watching ironically, stayed for the characters",
        "what_it_gave_you": "Friends who understand, a creative outlet, something to look forward to",
        "the_moment": "The finale. I cried for an hour. No regrets.",
        "what_others_dont_get": "It's not 'just a show' - it's the community around it",
        "why_it_matters": "These characters taught me things my real life couldn't"
    }
}

VARIANT_PET_BOND = {
    "name": "Pet Bond",
    "description": "Deep connection with a pet",
    "fields": {
        "who_they_are": "Your pet and their personality",
        "how_you_found_each_other": "The origin story",
        "your_routine": "The things you do together",
        "what_they_know": "What your pet seems to understand about you",
        "the_quiet_moment": "A small moment that meant everything",
        "what_they_taught_you": "What this bond has shown you"
    },
    "example": {
        "who_they_are": "A cat who acts like she doesn't care but always knows when I'm sad",
        "how_you_found_each_other": "She was the one who wouldn't let anyone hold her. I get it.",
        "your_routine": "5am zoomies, breakfast negotiations, evening lap time",
        "what_they_know": "She knows the sound of my crying versus my laughing from two rooms away",
        "the_quiet_moment": "The first time she chose to sleep next to me when I was sick",
        "what_they_taught_you": "Love doesn't have to be loud to be real"
    }
}

VARIANT_IMPOSTER_FEELINGS = {
    "name": "Imposter Feelings",
    "description": "Feeling like a fraud despite evidence",
    "fields": {
        "where_it_hits": "The situation where imposter feelings strike",
        "the_voice": "What the inner critic says",
        "the_evidence_against_you": "What seems to 'prove' you don't belong",
        "the_evidence_for_you": "What you try to ignore that says you do belong",
        "the_mask": "How you hide these feelings",
        "the_crack": "The moment the mask almost slipped"
    },
    "example": {
        "where_it_hits": "Every time the teacher calls on me in AP class",
        "the_voice": "'Everyone knows you don't deserve to be here'",
        "the_evidence_against_you": "That one wrong answer. The smarter kids. The grades that feel like flukes.",
        "the_evidence_for_you": "I did the work. I studied. I earned this.",
        "the_mask": "Acting confident even when my heart is racing",
        "the_crack": "When someone said I was 'so smart' and I almost laughed"
    }
}

VARIANT_SIBLING_TRUTH = {
    "name": "Sibling Truth",
    "description": "Complex sibling dynamics",
    "fields": {
        "the_dynamic": "Your role in the sibling relationship",
        "what_they_know": "What your sibling knows about you that others don't",
        "the_fight_that_wasnt_about_the_thing": "A conflict that was really about something deeper",
        "the_moment_of_understanding": "When you saw each other clearly",
        "what_changed": "How the relationship shifted",
        "the_truth_now": "What you understand about siblings now"
    },
    "example": {
        "the_dynamic": "I'm the responsible one. They're the 'fun' one. It's exhausting.",
        "what_they_know": "They know I cry when I'm overwhelmed, not when I'm sad",
        "the_fight_that_wasnt_about_the_thing": "The fight about dishes was really about feeling invisible",
        "the_moment_of_understanding": "When they defended me to a cousin I didn't even know had hurt me",
        "what_changed": "We started texting. Just memes at first. Then real stuff.",
        "the_truth_now": "They're the only person who remembers the same childhood I do"
    }
}

VARIANT_MENTOR_MOMENT = {
    "name": "Mentor Moment",
    "description": "A teacher/mentor who made a difference",
    "fields": {
        "who_they_were": "The mentor/teacher and their role",
        "first_impression": "What you thought of them at first",
        "what_they_saw": "What they noticed in you that others missed",
        "the_moment": "The conversation or moment that changed things",
        "what_they_gave_you": "The gift they didn't know they gave",
        "where_you_carry_it": "How their impact shows up now"
    },
    "example": {
        "who_they_were": "English teacher, junior year. Always wore the same three cardigans.",
        "first_impression": "Thought she was too intense. Always asking 'why'.",
        "what_they_saw": "She noticed I wrote better when I was angry",
        "the_moment": "When she kept me after class to say my essay was the most honest thing she'd read all year",
        "what_they_gave_you": "Permission to write what I actually feel",
        "where_you_carry_it": "Every time I choose honesty over 'correct'"
    }
}

VARIANT_MONEY_REALITY = {
    "name": "Money Reality",
    "description": "Socioeconomic awareness - family-friendly",
    "fields": {
        "the_awareness": "When you first noticed money differences",
        "the_small_thing": "A small moment that revealed class dynamics",
        "what_you_couldnt_say": "The thing you couldn't explain to friends",
        "the_code_switch": "How you adapt in different spaces",
        "what_it_taught_you": "The lesson that stuck",
        "the_truth": "What you understand now about money and worth"
    },
    "example": {
        "the_awareness": "Sixth grade. Someone's birthday party at a country club.",
        "the_small_thing": "When everyone just left their plates and I automatically started cleaning up",
        "what_you_couldnt_say": "Why I couldn't do the school trip. The 'real' reason.",
        "the_code_switch": "Different lunch table, different version of me",
        "what_it_taught_you": "Resourcefulness. Creativity. How to make $20 feel like $100.",
        "the_truth": "Having less didn't make me less. It just made some things harder."
    }
}

VARIANT_HERITAGE_DISCOVERY = {
    "name": "Heritage Discovery",
    "description": "Cultural identity and heritage",
    "fields": {
        "the_two_worlds": "The cultural spaces you navigate",
        "the_question": "The identity question you've asked yourself",
        "too_much_too_little": "When you felt too much of one and not enough of the other",
        "the_bridge": "Something that connects both parts of you",
        "the_reclaiming": "What you've chosen to embrace",
        "the_new_story": "The identity narrative you're writing"
    },
    "example": {
        "the_two_worlds": "Home language vs school language. Home food vs cafeteria food.",
        "the_question": "'Where are you really from?' (And why does it matter so much to them?)",
        "too_much_too_little": "Too American for relatives, too ethnic for classmates",
        "the_bridge": "Music. It doesn't need translation.",
        "the_reclaiming": "The name I stopped letting people mispronounce",
        "the_new_story": "I'm not 'between' cultures. I'm my own culture."
    }
}

VARIANT_GRIEF_GROWTH = {
    "name": "Grief Growth",
    "description": "Processing loss - family-friendly",
    "fields": {
        "what_changed": "The loss or change that shifted everything",
        "the_unexpected": "The grief that surprised you",
        "what_people_said": "The 'helpful' things that weren't helpful",
        "what_actually_helped": "The small thing that made a difference",
        "the_carrying": "What you carry from before",
        "the_growing": "How grief changed you (not fixed you, changed you)"
    },
    "example": {
        "what_changed": "When my grandmother passed. The first big loss.",
        "the_unexpected": "I grieved the future conversations we'd never have",
        "what_people_said": "'She's in a better place.' (I wanted her HERE.)",
        "what_actually_helped": "Someone who just sat with me. No words needed.",
        "the_carrying": "Her recipe cards. Her voice saying my name.",
        "the_growing": "I hold things less tightly now. I say 'I love you' more."
    }
}


__all__ = [
    "VARIANT_FIRST_BUTTERFLIES",
    "VARIANT_BODY_ACCEPTANCE",
    "VARIANT_FITTING_IN",
    "VARIANT_ONLINE_CONNECTION",
    "VARIANT_FUTURE_ANXIETY",
    "VARIANT_COMPARISON_TRAP",
    "VARIANT_FANDOM_PASSION",
    "VARIANT_PET_BOND",
    "VARIANT_IMPOSTER_FEELINGS",
    "VARIANT_SIBLING_TRUTH",
    "VARIANT_MENTOR_MOMENT",
    "VARIANT_MONEY_REALITY",
    "VARIANT_HERITAGE_DISCOVERY",
    "VARIANT_GRIEF_GROWTH",
]
