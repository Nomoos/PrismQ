"""Blend variant templates - combinations of themes."""

from typing import Any, Dict

# Theme blends - new themes combined with each other
VARIANT_BUTTERFLIES_ANXIETY = {
    "name": "Butterflies + Anxiety Blend",
    "description": "Attraction complicated by social anxiety",
    "fields": {
        "the_attraction": "The butterflies feeling",
        "the_anxiety": "The social fear mixed in",
        "the_conflict": "How they fight each other",
        "the_moment": "When both hit at once",
        "the_choice": "What wins - approach or avoid?",
        "the_lesson": "What this combination taught",
    },
    "example": {
        "the_attraction": "Wanting to talk to them so badly",
        "the_anxiety": "Terrified of saying the wrong thing",
        "the_conflict": "Heart says go, brain says DANGER",
        "the_moment": "They looked at me and I forgot how words work",
        "the_choice": "Smiled instead of ran. Small victory.",
        "the_lesson": "Attraction and anxiety can coexist",
    },
}

VARIANT_BODY_COMPARISON = {
    "name": "Body + Comparison Blend",
    "description": "Body image in comparison culture",
    "fields": {
        "the_comparison": "What bodies I compare to",
        "the_platform": "Where comparison happens",
        "the_feeling": "How it affects body image",
        "the_reality": "What filters and editing hide",
        "the_shift": "Moments of perspective",
        "the_practice": "Working on both body image and comparison",
    },
    "example": {
        "the_comparison": "Bodies that don't look like mine",
        "the_platform": "Every feed, every scroll",
        "the_feeling": "Never enough. Always wrong.",
        "the_reality": "Angles, filters, editing, best moments",
        "the_shift": "Realizing I'm comparing reality to fantasy",
        "the_practice": "Muting accounts that make me feel bad about my body",
    },
}

VARIANT_ONLINE_FITTING = {
    "name": "Online + Fitting In Blend",
    "description": "Finding belonging online when IRL is hard",
    "fields": {
        "irl_struggle": "Where fitting in IRL is hard",
        "online_discovery": "The online space where you fit",
        "what_changed": "How online belonging helps",
        "the_contrast": "Online vs. IRL fitting in",
        "the_bridge": "How online affects offline",
        "the_truth": "What this taught about belonging",
    },
    "example": {
        "irl_struggle": "School where no one gets me",
        "online_discovery": "A community where weird is welcome",
        "what_changed": "Proof that my kind of people exist",
        "the_contrast": "IRL: performance. Online: me.",
        "the_bridge": "Online confidence slowly leaking into real life",
        "the_truth": "Belonging doesn't require geography",
    },
}

VARIANT_FUTURE_COMPARISON = {
    "name": "Future + Comparison Blend",
    "description": "Future anxiety amplified by comparison",
    "fields": {
        "the_fear": "Specific future anxiety",
        "the_comparison": "Others who seem ahead",
        "the_spiral": "How comparison makes anxiety worse",
        "the_reality": "What comparison hides about others' fears",
        "the_break": "Moments of clarity",
        "the_now": "Focusing on present instead of comparing futures",
    },
    "example": {
        "the_fear": "Everyone has a plan and I don't",
        "the_comparison": "Their college plans, their certainty",
        "the_spiral": "They know. I don't. I'm behind.",
        "the_reality": "They're scared too. They just perform better.",
        "the_break": "Hearing someone 'together' admit they're terrified",
        "the_now": "Today's decision, not tomorrow's whole life",
    },
}

VARIANT_BODY_BUTTERFLIES = {
    "name": "Body + Butterflies Blend",
    "description": "Attraction complicated by body image",
    "fields": {
        "the_attraction": "The butterflies",
        "the_body_worry": "How body image interferes",
        "the_question": "Whether they'd like the real body",
        "the_hiding": "What gets hidden because of body image",
        "the_conflict": "Wanting to be seen but fearing it",
        "the_work": "Separating attraction from body image",
    },
    "example": {
        "the_attraction": "Wanting them to notice me",
        "the_body_worry": "But not THIS me. A different me.",
        "the_question": "Would they still like me in person?",
        "the_hiding": "Strategic angles. Careful clothes.",
        "the_conflict": "Want connection. Fear being seen.",
        "the_work": "Learning that attraction isn't conditional on perfect bodies",
    },
}

VARIANT_ONLINE_FUTURE = {
    "name": "Online + Future Blend",
    "description": "Online friends understanding future fears",
    "fields": {
        "the_fear": "Future anxiety",
        "the_online_friend": "Who you share it with online",
        "why_online": "Why it's easier to share online",
        "what_they_get": "What they understand",
        "the_support": "How they help",
        "the_value": "What this online support means",
    },
    "example": {
        "the_fear": "What if I make the wrong choice?",
        "the_online_friend": "Someone 3000 miles away who gets it",
        "why_online": "No judgment from people who know my 'real' life",
        "what_they_get": "They're scared too. We share the fear.",
        "the_support": "Just knowing someone else is also lost",
        "the_value": "Not alone in the uncertainty",
    },
}

VARIANT_FITTING_COMPARISON = {
    "name": "Fitting In + Comparison Blend",
    "description": "Social anxiety meets comparison culture",
    "fields": {
        "the_not_fitting": "Where you don't fit",
        "the_comparison": "Who seems to fit effortlessly",
        "the_spiral": "How comparison makes fitting in harder",
        "the_performance": "What you perform to try to fit",
        "the_exhaustion": "The cost of trying",
        "the_question": "Is fitting in worth it?",
    },
    "example": {
        "the_not_fitting": "Every social situation",
        "the_comparison": "People who make it look easy",
        "the_spiral": "They belong. I don't. It's obvious.",
        "the_performance": "Laughing at jokes I don't get",
        "the_exhaustion": "Being fake is a full-time job",
        "the_question": "What if I found places where I don't have to try?",
    },
}

# Cross blends - new themes with older templates
VARIANT_CONFESSION_BODY = {
    "name": "Confession + Body Acceptance Blend",
    "description": "Confessing body image struggles",
    "fields": {
        "the_confession": "What you're admitting about body image",
        "why_hidden": "Why this has been secret",
        "who_you_tell": "Who receives this confession",
        "the_vulnerability": "How scary this is to admit",
        "their_response": "What they say/do",
        "what_changes": "After confessing",
    },
    "example": {
        "the_confession": "I've never felt comfortable in my own skin",
        "why_hidden": "Supposed to love yourself. Can't admit you don't.",
        "who_you_tell": "Someone who feels safe",
        "the_vulnerability": "Admitting weakness feels dangerous",
        "their_response": "'Me too' - the most healing words",
        "what_changes": "Lighter. Less alone in the struggle.",
    },
}

VARIANT_UNSENT_FUTURE = {
    "name": "Unsent + Future Anxiety Blend",
    "description": "Unsent messages about future fears",
    "fields": {
        "the_unsent": "The message about the future never sent",
        "to_whom": "Who it was meant for",
        "the_fear": "The future fear it contained",
        "why_not_sent": "What stopped you",
        "what_you_sent": "The safer version (or nothing)",
        "where_the_fear_lives": "What happens to unsaid fears",
    },
    "example": {
        "the_unsent": "'I have no idea what I'm doing and I'm terrified'",
        "to_whom": "Anyone who seems to have it figured out",
        "the_fear": "Being the only one without a plan",
        "why_not_sent": "Don't want to be the only mess",
        "what_you_sent": "'Yeah I'm figuring it out'",
        "where_the_fear_lives": "Inside, growing",
    },
}

VARIANT_MIRROR_BODY = {
    "name": "Mirror Moment + Body Acceptance Blend",
    "description": "Mirror moments about body image",
    "fields": {
        "the_mirror": "What the mirror showed",
        "the_feeling": "The body feeling that came",
        "the_usual": "Normal mirror reaction",
        "this_time": "What was different this time",
        "the_shift": "A new way of seeing",
        "the_ongoing": "How mirror relationship is changing",
    },
    "example": {
        "the_mirror": "Same body as always",
        "the_feeling": "For once, not criticism",
        "the_usual": "Finding every flaw, making plans to fix",
        "this_time": "Just... looked. Without attacking.",
        "the_shift": "What if this body is just... mine?",
        "the_ongoing": "Some days war, some days truce",
    },
}

VARIANT_GROWING_ONLINE = {
    "name": "Growing Apart + Online Connection Blend",
    "description": "IRL friendships drifting while online ones grow",
    "fields": {
        "the_irl": "The IRL friendship that's fading",
        "the_online": "The online connection that's growing",
        "the_contrast": "Why one is thriving while other fades",
        "the_guilt": "Feeling bad about online being more real",
        "the_question": "Which friendship is more valid?",
        "the_truth": "What you've decided about connection",
    },
    "example": {
        "the_irl": "Best friend since elementary. Strangers now.",
        "the_online": "Username I talk to every day for years",
        "the_contrast": "IRL: small talk. Online: real talk.",
        "the_guilt": "Should IRL friends matter more?",
        "the_question": "Is proximity the measure of friendship?",
        "the_truth": "Connection is connection. Medium doesn't matter.",
    },
}

VARIANT_QUIET_BODY = {
    "name": "Quiet Rebellion + Body Acceptance Blend",
    "description": "Small rebellions against body expectations",
    "fields": {
        "the_expectation": "What body rules say",
        "the_quiet_no": "Small body acceptance rebellion",
        "what_it_felt_like": "The feeling of defying expectations",
        "who_noticed": "Did anyone see the rebellion?",
        "what_it_meant": "Why this small act mattered",
        "the_bigger_fight": "What you're really fighting for",
    },
    "example": {
        "the_expectation": "Hide. Cover. Apologize for existing.",
        "the_quiet_no": "Wore the thing anyway. Took up space.",
        "what_it_felt_like": "Terrifying and alive",
        "who_noticed": "Maybe no one. Maybe everyone.",
        "what_it_meant": "My body is not the enemy",
        "the_bigger_fight": "The right to exist without shrinking",
    },
}

VARIANT_CHOSEN_ONLINE = {
    "name": "Chosen Family + Online Connection Blend",
    "description": "Found family through online community",
    "fields": {
        "who_they_are": "Your online chosen family",
        "how_you_met": "The digital origin story",
        "what_makes_them_family": "Why they count as family",
        "never_met": "The in-person situation",
        "the_realness": "Whether it's 'real' family",
        "what_it_means": "What this online family provides",
    },
    "example": {
        "who_they_are": "Group chat that's been going for years",
        "how_you_met": "Shared interest that became shared lives",
        "what_makes_them_family": "Show up when it matters. Always.",
        "never_met": "Most of them, never seen their faces",
        "the_realness": "As real as any family I have",
        "what_it_means": "Chosen across distance is still chosen",
    },
}

VARIANT_PERMISSION_BODY = {
    "name": "Permission To + Body Acceptance Blend",
    "description": "Giving yourself permission about your body",
    "fields": {
        "the_permission": "What permission your body needed",
        "who_you_waited_for": "Whose approval you thought you needed",
        "the_realization": "That you could give it yourself",
        "the_moment": "When you gave yourself permission",
        "what_it_felt_like": "The feeling of body permission",
        "what_changed": "Life after giving yourself this",
    },
    "example": {
        "the_permission": "To exist in this body. As it is.",
        "who_you_waited_for": "Society. Media. Someone to say it's okay.",
        "the_realization": "They'll never give permission. Have to take it.",
        "the_moment": "Decided my body deserves to be here",
        "what_it_felt_like": "Revolutionary and ordinary at once",
        "what_changed": "Started living instead of waiting to deserve living",
    },
}

VARIANT_SMALL_COMPARISON = {
    "name": "Small Moment + Comparison Blend",
    "description": "Small comparison moment with big impact",
    "fields": {
        "the_small_thing": "The seemingly tiny comparison",
        "why_it_seemed_small": "Why it shouldn't have mattered",
        "why_it_hit": "What made it actually significant",
        "the_spiral": "Where the comparison led",
        "the_break": "Breaking out of the spiral",
        "the_lesson": "What small comparisons taught",
    },
    "example": {
        "the_small_thing": "Their Instagram got more likes",
        "why_it_seemed_small": "Just numbers. Meaningless.",
        "why_it_hit": "Proof of something I feared about myself",
        "the_spiral": "They're better. More liked. More everything.",
        "the_break": "Remembering numbers aren't worth",
        "the_lesson": "Small comparisons reveal big fears",
    },
}

VARIANT_IDENTITY_FITTING = {
    "name": "Identity Power + Fitting In Blend",
    "description": "Being yourself vs. fitting in",
    "fields": {
        "the_identity": "Who you really are",
        "the_fitting": "What fitting in requires",
        "the_conflict": "Where identity and fitting in clash",
        "the_cost": "What dimming yourself costs",
        "the_choice": "What you've chosen",
        "the_power": "Strength in choosing authenticity",
    },
    "example": {
        "the_identity": "All the 'weird' parts of me",
        "the_fitting": "Being normal. Blending.",
        "the_conflict": "Can't be both real and fitting in",
        "the_cost": "Performed belonging feels hollow",
        "the_choice": "Finding spaces where real fits",
        "the_power": "Authenticity as the ultimate belonging",
    },
}

VARIANT_LEARNED_BODY = {
    "name": "Learned Young + Body Acceptance Blend",
    "description": "Body lessons learned in childhood",
    "fields": {
        "the_lesson": "What you learned about bodies young",
        "who_taught_it": "Where the lesson came from",
        "how_it_stuck": "How the lesson shaped you",
        "the_truth": "Whether the lesson was true",
        "the_unlearning": "What you're trying to undo",
        "the_new_story": "The body story you're writing now",
    },
    "example": {
        "the_lesson": "Bodies like mine are wrong",
        "who_taught_it": "Comments. Comparisons. Looks.",
        "how_it_stuck": "Believed it was fact, not opinion",
        "the_truth": "It was never true. Just repeated.",
        "the_unlearning": "Catching old thoughts, questioning them",
        "the_new_story": "This body is trying its best. So am I.",
    },
}

VARIANT_SAFE_ONLINE = {
    "name": "Safe Person + Online Connection Blend",
    "description": "Finding your safe person online",
    "fields": {
        "who_they_are": "Your online safe person",
        "how_it_built": "How the safety developed",
        "what_you_share": "What you can be with them",
        "the_paradox": "Stranger who knows you best",
        "what_others_say": "Skepticism about online safety",
        "why_it_works": "What makes online safety real",
    },
    "example": {
        "who_they_are": "Someone I've never met, know completely",
        "how_it_built": "Slow trust over years of texts",
        "what_you_share": "The version of me that's 'too much' for IRL",
        "the_paradox": "They've never seen my face but know my soul",
        "what_others_say": "'That's not a real friendship'",
        "why_it_works": "No performance required. Just truth.",
    },
}

VARIANT_REWRITING_BODY = {
    "name": "Rewriting Story + Body Acceptance Blend",
    "description": "Rewriting the body narrative",
    "fields": {
        "the_old_story": "The narrative you've carried about your body",
        "who_wrote_it": "Where this story came from",
        "the_chapter": "The moment that defined this story",
        "the_new_story": "What you want to believe instead",
        "the_evidence": "What supports the new story",
        "the_work": "How the rewriting is going",
    },
    "example": {
        "the_old_story": "'My body is wrong and needs fixing'",
        "who_wrote_it": "Diet culture, that one comment in middle school, mirrors that felt like enemies",
        "the_chapter": "The first time someone laughed at me in a swimsuit",
        "the_new_story": "My body is trying its best. So am I.",
        "the_evidence": "It healed when I was sick. It carries me through hard days. It's trying.",
        "the_work": "Some days the old story wins. But less often now.",
    },
}


__all__ = [
    # Theme blends
    "VARIANT_BUTTERFLIES_ANXIETY",
    "VARIANT_BODY_COMPARISON",
    "VARIANT_ONLINE_FITTING",
    "VARIANT_FUTURE_COMPARISON",
    "VARIANT_BODY_BUTTERFLIES",
    "VARIANT_ONLINE_FUTURE",
    "VARIANT_FITTING_COMPARISON",
    # Cross blends
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
]
