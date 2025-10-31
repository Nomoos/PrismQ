"""Primary content categories for short-form vertical video classification.

This module defines the taxonomy of primary content categories optimized for
short-form vertical video (YouTube Shorts, TikTok, Instagram Reels, Facebook Reels).

The taxonomy is:
- Broad and platform-agnostic
- Covers all major content types
- Uses a single 'Unusable' category for content not relevant to story generation

Categories:
    1. Storytelling - Narratives, fictional or real
    2. Entertainment - Quick fun content (memes, comedy, pranks, fails, reactions)
    3. Education / Informational - Explainers, tutorials, facts, news
    4. Lifestyle / Vlog - Daily life, beauty, fashion, fitness, food, travel
    5. Gaming - Gameplay clips, highlights, speedruns, walkthroughs
    6. Challenges & Trends - Social challenges, trending sounds, AR effects
    7. Reviews & Commentary - Product reviews, reactions, opinion commentary
    8. Unusable - Content not useful for story generation
"""

from enum import Enum
from typing import NamedTuple


class PrimaryCategory(Enum):
    """Primary content categories for short-form video classification."""
    
    STORYTELLING = "Storytelling"
    ENTERTAINMENT = "Entertainment"
    EDUCATION = "Education / Informational"
    LIFESTYLE = "Lifestyle / Vlog"
    GAMING = "Gaming"
    CHALLENGES_TRENDS = "Challenges & Trends"
    REVIEWS_COMMENTARY = "Reviews & Commentary"
    UNUSABLE = "Unusable"
    
    @property
    def is_usable_for_stories(self) -> bool:
        """Check if this category is usable for story generation."""
        return self != PrimaryCategory.UNUSABLE
    
    @property
    def description(self) -> str:
        """Get detailed description of this category."""
        descriptions = {
            PrimaryCategory.STORYTELLING: (
                "Narratives, fictional or real. Examples: Storytime, POV, "
                "creepypasta, confessionals, true stories."
            ),
            PrimaryCategory.ENTERTAINMENT: (
                "Quick fun content: memes, comedy, pranks, fails, reactions, edits."
            ),
            PrimaryCategory.EDUCATION: (
                "Explainers, tutorials, facts, productivity hacks, news bites."
            ),
            PrimaryCategory.LIFESTYLE: (
                "Daily life, beauty, fashion, fitness, food, travel."
            ),
            PrimaryCategory.GAMING: (
                "Gameplay clips, highlights, speedruns, walkthroughs."
            ),
            PrimaryCategory.CHALLENGES_TRENDS: (
                "Social challenges, trending sounds, AR effects."
            ),
            PrimaryCategory.REVIEWS_COMMENTARY: (
                "Product reviews, reactions, opinion commentary."
            ),
            PrimaryCategory.UNUSABLE: (
                "Catch-all for content not useful for story generation: "
                "Music & Performance, ASMR, Promotional/Branded, Pets & Animals, "
                "Sports, News/Politics, etc."
            ),
        }
        return descriptions[self]


class CategoryResult(NamedTuple):
    """Result of category classification."""
    
    category: PrimaryCategory
    confidence: float  # 0.0 to 1.0
    indicators: list  # List of matched indicators
    secondary_matches: dict  # Dictionary of other categories and their scores
