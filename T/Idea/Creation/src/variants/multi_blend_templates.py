"""Multi-blend variant templates - triple and double blends of new themes."""

from typing import Any, Dict

# Triple-blend templates: combining 3 seeds
VARIANT_FANDOM_CONFESSION_ONLINE = {
    "name": "Fandom + Confession + Online Triple Blend",
    "description": "Confessing fandom passion through online community.",
    "fields": {
        "the_secret": "The fandom passion I've hidden",
        "where_i_confessed": "The online space where I finally shared",
        "who_understood": "The online community that got it",
        "what_changed": "How confessing online changed things",
        "the_paradox": "Strangers understood what friends didn't",
        "the_truth": "What this taught me about community",
    },
    "example": {
        "the_secret": "I've memorized every lyric of an album most people mock",
        "where_i_confessed": "A Discord server at 2am with people I'll never meet",
        "who_understood": "People who had the same 'guilty pleasure' that isn't guilty at all",
        "what_changed": "I stopped pretending to be cooler than my interests",
        "the_paradox": "My deepest passions are understood by people I've never seen",
        "the_truth": "Real community is about sharing what you love without shame",
    },
}

VARIANT_BODY_SIBLING_MIRROR = {
    "name": "Body + Sibling + Mirror Triple Blend",
    "description": "Body image through the lens of sibling comparison.",
    "fields": {
        "the_comparison": "How sibling bodies were compared",
        "what_the_mirror_showed": "What I saw vs what they saw",
        "the_words_that_stuck": "Things said that shaped body image",
        "the_moment_of_seeing": "When I saw my sibling struggle too",
        "shared_healing": "How understanding changed the dynamic",
        "the_new_mirror": "What we both see now",
    },
    "example": {
        "the_comparison": "'Why can't you be thin like your sister?'",
        "what_the_mirror_showed": "I saw every flaw. She saw them too, in herself.",
        "the_words_that_stuck": "Comparison dressed up as motivation",
        "the_moment_of_seeing": "When I caught her doing the same rituals I did",
        "shared_healing": "We stopped comparing because we're not enemies",
        "the_new_mirror": "Bodies that are doing their best, together",
    },
}

VARIANT_IMPOSTER_FUTURE_MENTOR = {
    "name": "Imposter + Future + Mentor Triple Blend",
    "description": "A mentor helping navigate imposter syndrome about the future.",
    "fields": {
        "the_fear": "The future fear mixed with imposter feelings",
        "what_the_mentor_saw": "What they noticed I couldn't see",
        "the_intervention": "The moment they intervened",
        "reframing_future": "How they reframed what's possible",
        "permission_granted": "What they gave me permission to believe",
        "carrying_forward": "What I carry from that conversation",
    },
    "example": {
        "the_fear": "I'll get to college and everyone will know I don't belong",
        "what_the_mentor_saw": "The potential I called luck",
        "the_intervention": "'Let me tell you about the first time I felt like a fraud'",
        "reframing_future": "'What if you belong more than you know?'",
        "permission_granted": "Permission to be imperfect and still worthy",
        "carrying_forward": "Their voice in my head when the doubt gets loud",
    },
}

VARIANT_HERITAGE_FAMILY_QUIET = {
    "name": "Heritage + Family + Quiet Rebellion Triple Blend",
    "description": "Quietly reclaiming heritage against family expectations.",
    "fields": {
        "the_expectation": "What family expected about cultural identity",
        "the_quiet_choice": "The small rebellion of reclaiming heritage",
        "family_tension": "How this choice created friction",
        "what_heritage_means": "What I'm actually reclaiming",
        "the_bridge": "Finding middle ground or choosing my path",
        "the_truth": "What this journey taught about identity",
    },
    "example": {
        "the_expectation": "'Don't be too ethnic. Blend in.'",
        "the_quiet_choice": "Wearing my grandmother's jewelry to school",
        "family_tension": "'Why are you making yourself stand out?'",
        "what_heritage_means": "The parts of me that got hidden for safety",
        "the_bridge": "Respecting their survival while choosing my pride",
        "the_truth": "I can honor their protection while refusing their shame",
    },
}

VARIANT_GRIEF_PET_HOLDING = {
    "name": "Grief + Pet + Holding Space Triple Blend",
    "description": "A pet holding space during grief.",
    "fields": {
        "the_loss": "The grief being processed",
        "how_they_knew": "How the pet sensed the pain",
        "wordless_comfort": "What they offered without words",
        "the_healing_presence": "How their presence helped",
        "what_they_taught": "What the pet taught about grief",
        "the_gratitude": "What I learned about being held",
    },
    "example": {
        "the_loss": "The first major loss I'd ever experienced",
        "how_they_knew": "She stopped playing. Just stayed close.",
        "wordless_comfort": "A warm weight on my chest when I couldn't stop crying",
        "the_healing_presence": "She never tried to fix it. She just stayed.",
        "what_they_taught": "Sometimes presence is the only medicine",
        "the_gratitude": "Thank you for not needing me to be okay",
    },
}

VARIANT_MONEY_FITTING_COMPARISON = {
    "name": "Money + Fitting In + Comparison Triple Blend",
    "description": "Class anxiety in social comparison culture.",
    "fields": {
        "the_gap": "When money differences became visible in social spaces",
        "performing_belonging": "How I tried to fit in despite the gap",
        "comparison_spiral": "How comparison made it worse",
        "what_i_couldnt_say": "The truth I couldn't share",
        "the_realization": "What I learned about real vs performed worth",
        "the_truth": "Where I landed about money and belonging",
    },
    "example": {
        "the_gap": "Everyone's talking about vacations I'll never take",
        "performing_belonging": "Learning to deflect instead of explain",
        "comparison_spiral": "Their 'normal' is my 'impossible'",
        "what_i_couldnt_say": "It's not 'can't' - it's 'literally cannot afford'",
        "the_realization": "Some comparisons are set up to make you lose",
        "the_truth": "My worth isn't in my family's bank account",
    },
}

# Double-blend variations with new themes
VARIANT_FANDOM_IMPOSTER = {
    "name": "Fandom + Imposter Double Blend",
    "description": "Imposter syndrome about 'real' fan status.",
    "fields": {
        "the_passion": "The fandom that matters deeply",
        "the_gatekeeping": "The 'real fan' tests that hurt",
        "imposter_voice": "The doubt about belonging in the fandom",
        "evidence_of_love": "Proof of genuine passion",
        "the_realization": "What 'real' fan actually means",
        "owning_it": "How I claim my fan identity now",
    },
    "example": {
        "the_passion": "This show saved me during hard times",
        "the_gatekeeping": "'You only started watching after season 3'",
        "imposter_voice": "Maybe I don't love it enough to count",
        "evidence_of_love": "The joy it brings me, the community it gave me",
        "the_realization": "Love isn't measured in timestamps",
        "owning_it": "My love is valid. Full stop.",
    },
}

VARIANT_PET_GRIEF = {
    "name": "Pet + Grief Double Blend",
    "description": "Grief about a pet or pets helping process grief.",
    "fields": {
        "the_bond": "What this pet meant",
        "the_loss_or_fear": "The grief being faced",
        "what_they_gave": "What the pet gave that humans couldn't",
        "the_hardest_part": "The most difficult aspect of this grief",
        "the_carrying": "What I carry forward",
        "the_growth": "How this shaped me",
    },
    "example": {
        "the_bond": "Ten years of knowing exactly what I need",
        "the_loss_or_fear": "Watching them get older and knowing",
        "what_they_gave": "Love without conditions or explanations needed",
        "the_hardest_part": "They won't know how much they mattered",
        "the_carrying": "Every pet I love will break my heart and it's worth it",
        "the_growth": "Learning that love worth having hurts to lose",
    },
}

VARIANT_SIBLING_MONEY = {
    "name": "Sibling + Money Double Blend",
    "description": "Sibling dynamics around family financial stress.",
    "fields": {
        "the_reality": "The family financial situation",
        "different_responses": "How siblings responded differently",
        "unspoken_understanding": "What we knew but didn't say",
        "the_tension": "Where money created sibling friction",
        "the_solidarity": "Where we found common ground",
        "the_lesson": "What this taught about family and money",
    },
    "example": {
        "the_reality": "We knew things were tight before anyone said it",
        "different_responses": "I stopped asking. They kept asking. Both ways hurt.",
        "unspoken_understanding": "Why mom was always tired",
        "the_tension": "'You got to go to camp' - years later, still stings",
        "the_solidarity": "Protecting the younger ones from worrying",
        "the_lesson": "Scarcity brings out different survival modes",
    },
}

VARIANT_MENTOR_HERITAGE = {
    "name": "Mentor + Heritage Double Blend",
    "description": "A mentor helping navigate cultural identity.",
    "fields": {
        "who_they_were": "The mentor who understood the cultural struggle",
        "what_they_saw": "The identity tension they recognized",
        "their_story": "Their own heritage journey",
        "the_gift": "What they modeled or said",
        "permission_given": "What they gave me permission to embrace",
        "the_path": "How this shaped my identity journey",
    },
    "example": {
        "who_they_were": "A teacher who also grew up between cultures",
        "what_they_saw": "The code-switching exhaustion",
        "their_story": "'I used to hide my accent too'",
        "the_gift": "Being proudly hybrid in front of me",
        "permission_given": "Permission to be fully both, not half of each",
        "the_path": "Building an identity that doesn't apologize",
    },
}

VARIANT_FUTURE_HERITAGE = {
    "name": "Future + Heritage Double Blend",
    "description": "Future fears complicated by cultural expectations.",
    "fields": {
        "the_expectation": "Cultural/family expectations about the future",
        "the_personal_want": "What I actually want for myself",
        "the_collision": "Where these conflict",
        "the_guilt": "The guilt of wanting something different",
        "finding_balance": "How I'm navigating this",
        "the_truth": "What I've decided about my own future",
    },
    "example": {
        "the_expectation": "Doctor, lawyer, engineer - the approved list",
        "the_personal_want": "Something creative that brings me alive",
        "the_collision": "'You're wasting your potential'",
        "the_guilt": "Feeling like betrayal for wanting my own life",
        "finding_balance": "Honoring their sacrifices while choosing my path",
        "the_truth": "Their dreams for me came from love. So does my own dream.",
    },
}

VARIANT_ONLINE_IMPOSTER = {
    "name": "Online + Imposter Double Blend",
    "description": "Imposter syndrome in online community spaces.",
    "fields": {
        "the_space": "The online community where imposter feelings hit",
        "the_doubt": "What makes me feel like I don't belong",
        "what_they_see": "The version of me others see online",
        "the_fear": "What I'm afraid they'll discover",
        "the_reality": "What's actually true about my belonging",
        "the_choice": "How I choose to show up now",
    },
    "example": {
        "the_space": "A creative community where everyone seems so talented",
        "the_doubt": "'Everyone else knows what they're doing'",
        "what_they_see": "Someone who seems confident in their work",
        "the_fear": "That they'll realize I'm figuring it out as I go",
        "the_reality": "Everyone is figuring it out. That's the secret.",
        "the_choice": "Showing up imperfect and learning in public",
    },
}

VARIANT_BUTTERFLIES_HERITAGE = {
    "name": "Butterflies + Heritage Double Blend",
    "description": "First attraction complicated by cultural identity.",
    "fields": {
        "the_feeling": "The butterflies experience",
        "the_complication": "How heritage/culture complicated it",
        "family_factor": "What family would think or say",
        "identity_question": "What this brought up about identity",
        "navigating_both": "How I'm handling both feelings",
        "the_learning": "What this taught about identity and connection",
    },
    "example": {
        "the_feeling": "The first time someone made my heart race",
        "the_complication": "'What would your grandmother say?'",
        "family_factor": "Unspoken rules about who's 'acceptable'",
        "identity_question": "Does liking them mean rejecting my culture?",
        "navigating_both": "Learning that attraction doesn't have to be rebellion",
        "the_learning": "My heart is not a betrayal of my heritage",
    },
}

VARIANT_BODY_ONLINE = {
    "name": "Body + Online Double Blend",
    "description": "Body image journey through online community.",
    "fields": {
        "the_struggle": "The body image battle",
        "online_discovery": "Finding body positive spaces online",
        "community_healing": "What online community offered",
        "real_vs_filtered": "Navigating real bodies in filtered spaces",
        "the_shift": "How online connection changed perspective",
        "the_current": "Where I am with body image now",
    },
    "example": {
        "the_struggle": "Years of war with my reflection",
        "online_discovery": "An account that showed bodies like mine, living fully",
        "community_healing": "People who celebrate instead of critique",
        "real_vs_filtered": "Learning to spot the filters, both digital and internal",
        "the_shift": "Seeing someone my size happy made me believe it's possible",
        "the_current": "Still a journey. But the destination changed.",
    },
}

VARIANT_COMPARISON_SIBLING = {
    "name": "Comparison + Sibling Double Blend",
    "description": "Sibling comparison in the age of social media.",
    "fields": {
        "the_comparison": "How sibling comparison shows up",
        "social_media_factor": "How social media amplifies it",
        "what_i_see": "What I see when I compare",
        "what_i_miss": "What I don't see in their life",
        "the_conversation": "An honest moment between siblings",
        "the_truth": "What comparison was really about",
    },
    "example": {
        "the_comparison": "Their highlight reel vs my behind the scenes",
        "social_media_factor": "Even my sibling looks more together online",
        "what_i_see": "Everything they have that I don't",
        "what_i_miss": "They're comparing themselves to me too",
        "the_conversation": "'Your life looks perfect' 'So does yours'",
        "the_truth": "We're both losing at a game neither of us wanted to play",
    },
}

VARIANT_QUIET_MONEY = {
    "name": "Quiet Rebellion + Money Double Blend",
    "description": "Small rebellions against class expectations.",
    "fields": {
        "the_expectation": "What poverty/wealth was supposed to mean",
        "the_quiet_no": "The small way I refused to accept it",
        "what_it_cost": "What the rebellion cost me",
        "what_it_gave": "What the rebellion gave me",
        "the_perception": "How others saw this choice",
        "the_truth": "What I was really fighting for",
    },
    "example": {
        "the_expectation": "Low expectations because of zip code",
        "the_quiet_no": "Applying anyway. Showing up anyway.",
        "what_it_cost": "The exhaustion of constantly proving",
        "what_it_gave": "A refusal to be defined by circumstances",
        "the_perception": "Some called it ambition. Some called it denial.",
        "the_truth": "I was fighting for the right to want more",
    },
}

VARIANT_FANDOM_CHOSEN = {
    "name": "Fandom + Chosen Family Double Blend",
    "description": "Finding chosen family through shared fandom.",
    "fields": {
        "the_passion": "The fandom that connected us",
        "how_we_found_each_other": "The community where we met",
        "what_we_share": "Beyond fandom - what else we share",
        "the_moments": "Times they showed up as family",
        "the_evolution": "How the bond grew beyond the thing we loved",
        "the_truth": "What this family means to me",
    },
    "example": {
        "the_passion": "A book series we all loved too much",
        "how_we_found_each_other": "A forum thread that turned into group chats",
        "what_we_share": "The same fears, the same hopes, the same weird humor",
        "the_moments": "They knew about the hard stuff before anyone else",
        "the_evolution": "We'd talk about the series for five minutes, then life for hours",
        "the_truth": "Found family is still family. Sometimes more.",
    },
}

VARIANT_MENTOR_IMPOSTER = {
    "name": "Mentor + Imposter Double Blend",
    "description": "A mentor addressing imposter syndrome.",
    "fields": {
        "the_doubt": "The imposter belief that was paralyzing",
        "what_they_saw": "What the mentor noticed",
        "their_approach": "How they addressed it",
        "the_reframe": "What they helped me see differently",
        "the_ongoing": "How this conversation stays with me",
        "the_gift": "What they gave me about self-belief",
    },
    "example": {
        "the_doubt": "'I got in by accident and they'll figure it out'",
        "what_they_saw": "The hesitation in sharing my work",
        "their_approach": "'Let me tell you about impostor syndrome'",
        "the_reframe": "Doubt isn't evidence of fraud. It's evidence of growth.",
        "the_ongoing": "I hear their voice when the doubt gets loud",
        "the_gift": "Permission to be a work in progress",
    },
}

VARIANT_GRIEF_HERITAGE = {
    "name": "Grief + Heritage Double Blend",
    "description": "Grief that connects to cultural identity.",
    "fields": {
        "the_loss": "What was lost",
        "heritage_connection": "How it connected to culture/heritage",
        "what_was_carried": "Cultural wisdom or tradition in the grief",
        "the_complicated": "Complex feelings about heritage in grief",
        "the_reclaiming": "What I'm choosing to carry forward",
        "the_meaning": "What this grief taught about identity",
    },
    "example": {
        "the_loss": "My grandmother - the last one who spoke the old language",
        "heritage_connection": "With her, a whole way of being went quiet",
        "what_was_carried": "The rituals we did, the recipes, the stories",
        "the_complicated": "Grief for a language I never learned",
        "the_reclaiming": "Learning the words she used to call me, at least",
        "the_meaning": "Heritage is what we choose to carry, even imperfectly",
    },
}

VARIANT_FITTING_ONLINE = {
    "name": "Fitting In + Online Double Blend",
    "description": "Finding belonging online when IRL doesn't fit.",
    "fields": {
        "the_struggle": "What made fitting in IRL hard",
        "finding_the_space": "Where online belonging happened",
        "what_was_different": "Why online worked when IRL didn't",
        "the_realness": "Was it 'real' belonging?",
        "the_bridge": "How online affected IRL",
        "the_truth": "What this taught about belonging",
    },
    "example": {
        "the_struggle": "Too weird for the normal kids, not weird enough for the weird kids",
        "finding_the_space": "A community where my weird was the entry fee",
        "what_was_different": "No one judging the packaging, just the content",
        "the_realness": "Critics say online friends aren't real. They're wrong.",
        "the_bridge": "Online confidence leaked into real life, slowly",
        "the_truth": "Belonging is belonging, regardless of medium",
    },
}

VARIANT_BODY_FUTURE = {
    "name": "Body + Future Double Blend",
    "description": "Future fears complicated by body image.",
    "fields": {
        "the_fear": "Future anxiety tangled with body image",
        "the_belief": "What I believed my body prevented",
        "challenging_it": "Moments that challenged this belief",
        "the_work": "Working on both body image and future vision",
        "the_shift": "How perspective is changing",
        "the_new_vision": "What I'm allowing myself to imagine now",
    },
    "example": {
        "the_fear": "'No one will take me seriously looking like this'",
        "the_belief": "Success requires a certain body",
        "challenging_it": "Seeing people in bodies like mine winning",
        "the_work": "Separating worth from weight, ability from appearance",
        "the_shift": "What if my body isn't the obstacle I made it?",
        "the_new_vision": "A future where I show up as I am, and it's enough",
    },
}

VARIANT_PET_MIRROR = {
    "name": "Pet + Mirror Double Blend",
    "description": "Seeing yourself through your pet's love.",
    "fields": {
        "who_they_are": "Your pet",
        "the_mirror": "What their love reflects about you",
        "what_they_see": "The version of you they love",
        "the_contrast": "Vs the version you criticize",
        "the_lesson": "What their unconditional love teaches",
        "the_seeing": "How they helped you see yourself differently",
    },
    "example": {
        "who_they_are": "A dog who thinks I'm the best person alive",
        "the_mirror": "Someone worth loving, just for existing",
        "what_they_see": "The person who feeds them, yes, but also the one who plays, laughs, tries",
        "the_contrast": "I see flaws. They see their favorite human.",
        "the_lesson": "Maybe worthiness isn't earned. Maybe it just is.",
        "the_seeing": "If I could see myself the way they see me",
    },
}

VARIANT_LAST_TIME_GRIEF = {
    "name": "Last Time + Grief Double Blend",
    "description": "The 'last time' moments in grief.",
    "fields": {
        "the_last_time": "A last moment you didn't know was last",
        "what_you_would_have_done": "What you'd do differently knowing",
        "the_weight": "How this 'last' feels",
        "the_ordinary": "The ordinary nature of it",
        "the_carrying": "How you carry this",
        "the_truth": "What this teaches about presence",
    },
    "example": {
        "the_last_time": "The last time I heard them laugh",
        "what_you_would_have_done": "Recorded it. Memorized it. Told them.",
        "the_weight": "The weight of not knowing you should pay attention",
        "the_ordinary": "It was just a Tuesday. Just a laugh. Now it's everything.",
        "the_carrying": "I try to hear it still. The memory is fading.",
        "the_truth": "Every moment could be the last. That's unbearable and important.",
    },
}

VARIANT_PARALLEL_FANDOM = {
    "name": "Parallel Lives + Fandom Double Blend",
    "description": "What-if me through the lens of fandom.",
    "fields": {
        "the_fandom": "The fandom",
        "the_parallel": "The parallel life if I'd never found it",
        "who_i_would_be": "Who I'd be without this passion",
        "who_i_am": "Who I became because of it",
        "the_gratitude": "Gratitude for this path",
        "the_butterfly": "The small choice that led here",
    },
    "example": {
        "the_fandom": "A community I stumbled into at exactly the right time",
        "the_parallel": "A version of me who never clicked that link",
        "who_i_would_be": "More isolated, less creative, less understood",
        "who_i_am": "Part of something bigger, with people who get it",
        "the_gratitude": "Thank you, algorithm gods, for this one",
        "the_butterfly": "One random recommendation changed my whole life",
    },
}


__all__ = [
    # Triple blends
    "VARIANT_FANDOM_CONFESSION_ONLINE",
    "VARIANT_BODY_SIBLING_MIRROR",
    "VARIANT_IMPOSTER_FUTURE_MENTOR",
    "VARIANT_HERITAGE_FAMILY_QUIET",
    "VARIANT_GRIEF_PET_HOLDING",
    "VARIANT_MONEY_FITTING_COMPARISON",
    # Double blends
    "VARIANT_FANDOM_IMPOSTER",
    "VARIANT_PET_GRIEF",
    "VARIANT_SIBLING_MONEY",
    "VARIANT_MENTOR_HERITAGE",
    "VARIANT_FUTURE_HERITAGE",
    "VARIANT_ONLINE_IMPOSTER",
    "VARIANT_BUTTERFLIES_HERITAGE",
    "VARIANT_BODY_ONLINE",
    "VARIANT_COMPARISON_SIBLING",
    "VARIANT_QUIET_MONEY",
    "VARIANT_FANDOM_CHOSEN",
    "VARIANT_MENTOR_IMPOSTER",
    "VARIANT_GRIEF_HERITAGE",
    "VARIANT_FITTING_ONLINE",
    "VARIANT_BODY_FUTURE",
    "VARIANT_PET_MIRROR",
    "VARIANT_LAST_TIME_GRIEF",
    "VARIANT_PARALLEL_FANDOM",
]
