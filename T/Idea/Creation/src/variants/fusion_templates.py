"""Fusion variant templates - combinations of story seed templates."""

from typing import Dict, Any


VARIANT_CONFESSION_MYSTERY = {
    "name": "Confession + Mystery Fusion",
    "description": "A confession wrapped in mystery",
    "fields": {
        "the_secret": "What's being confessed",
        "the_mystery": "The unanswered question around it",
        "the_clues": "What hints at the truth",
        "the_reveal": "How confession and mystery connect",
        "emotional_core": "The feeling underneath",
        "resolution": "How understanding comes"
    },
    "example": {
        "the_secret": "Something I've kept hidden even from myself",
        "the_mystery": "Why I've been avoiding this truth",
        "the_clues": "Small patterns I couldn't explain",
        "the_reveal": "The confession IS the solution to the mystery",
        "emotional_core": "Fear of self-knowledge",
        "resolution": "Naming the thing finally makes sense of everything"
    }
}

VARIANT_OVERHEARD_TRANSFORMATION = {
    "name": "Overheard + Transformation Fusion",
    "description": "Overhearing something that changes you",
    "fields": {
        "what_was_heard": "The words that changed things",
        "before_hearing": "Who you were before",
        "the_shift": "The immediate impact",
        "the_process": "How transformation unfolded",
        "after": "Who you became",
        "the_gift": "What the accidental hearing gave you"
    },
    "example": {
        "what_was_heard": "Something that shattered an illusion",
        "before_hearing": "Living in comfortable ignorance",
        "the_shift": "World tilting on its axis",
        "the_process": "Grieving the old understanding",
        "after": "Someone who sees more clearly",
        "the_gift": "Painful truth over comfortable lies"
    }
}

VARIANT_UNSENT_REBELLION = {
    "name": "Unsent Message + Quiet Rebellion Fusion",
    "description": "The rebellion of words you never sent",
    "fields": {
        "the_unsent": "The message never delivered",
        "what_it_would_have_said": "The forbidden truth",
        "why_not_sending_was_rebellion": "The act of restraint as defiance",
        "what_silence_communicated": "What not-saying said",
        "the_power": "Strength in withheld words",
        "the_resolution": "Where the unsent lives now"
    },
    "example": {
        "the_unsent": "The response they expected me to send",
        "what_it_would_have_said": "Apology. Explanation. More of the same.",
        "why_not_sending_was_rebellion": "Refused to perform expected emotions",
        "what_silence_communicated": "I'm done explaining myself",
        "the_power": "They waited for words that never came",
        "the_resolution": "Learned that sometimes silence is the answer"
    }
}

VARIANT_MIRROR_INHERITANCE = {
    "name": "Mirror + Emotional Inheritance Fusion",
    "description": "Seeing inherited patterns in reflection",
    "fields": {
        "what_the_mirror_showed": "The reflection that triggered recognition",
        "the_pattern_recognized": "The inherited behavior spotted",
        "whose_ghost": "Who you saw in yourself",
        "the_feeling": "Emotion of seeing the pattern",
        "the_choice": "What to do with the recognition",
        "the_work": "Breaking or honoring the inheritance"
    },
    "example": {
        "what_the_mirror_showed": "An expression. A posture. A way of being.",
        "the_pattern_recognized": "The exact same way they avoided conflict",
        "whose_ghost": "Parent. Grandparent. The line before me.",
        "the_feeling": "Horror mixed with compassion",
        "the_choice": "This is where the pattern changes",
        "the_work": "Honoring the survival while choosing differently"
    }
}

VARIANT_CHOSEN_GROWING = {
    "name": "Chosen Family + Growing Apart Fusion",
    "description": "When even chosen family grows distant",
    "fields": {
        "the_chosen_bond": "The family you chose",
        "what_brought_you_together": "The original connection",
        "the_drift": "How distance crept in",
        "the_grief": "Losing what you chose",
        "the_difference": "How it differs from blood family distance",
        "the_truth": "What chosen family distance teaches"
    },
    "example": {
        "the_chosen_bond": "Friends who became everything",
        "what_brought_you_together": "Mutual understanding at the right time",
        "the_drift": "We grew in different directions",
        "the_grief": "Hurts more because we chose this",
        "the_difference": "Can't blame circumstance, just change",
        "the_truth": "Even chosen connections need choosing again and again"
    }
}

VARIANT_PARALLEL_PERMISSION = {
    "name": "Parallel Lives + Permission To Fusion",
    "description": "The alternate self who gave themselves permission",
    "fields": {
        "the_parallel_self": "The version who chose differently",
        "the_permission_they_gave": "What they allowed themselves",
        "what_held_you_back": "Why you didn't give yourself that permission",
        "the_comparison": "How their life might be different",
        "the_lesson": "What their choice teaches you",
        "the_now": "Permission you're considering giving yourself"
    },
    "example": {
        "the_parallel_self": "Me, but if I'd said yes instead of no",
        "the_permission_they_gave": "To take the risk. To fail. To try.",
        "what_held_you_back": "Fear dressed as practicality",
        "the_comparison": "Maybe happier. Maybe not. But definitely different.",
        "the_lesson": "Permission was always mine to give",
        "the_now": "Wondering what I'm still waiting for permission for"
    }
}


__all__ = [
    "VARIANT_CONFESSION_MYSTERY",
    "VARIANT_OVERHEARD_TRANSFORMATION",
    "VARIANT_UNSENT_REBELLION",
    "VARIANT_MIRROR_INHERITANCE",
    "VARIANT_CHOSEN_GROWING",
    "VARIANT_PARALLEL_PERMISSION",
]
