"""Platform-agnostic content classification for PrismQ Idea Sources.

This module provides classification enrichment for IdeaInspiration objects.
It scores and classifies content to enrich IdeaInspiration with:
    - Top category classification
    - Classification flags (is_story, is_usable, etc.)
    - Classification tags derived from indicators
    - Field-level confidence scores

Note: The IdeaInspiration model is defined in the parent PrismQ.IdeaInspiration package.
This classification module enriches that external model with classification metadata.

Classifiers:
    - StoryDetector: Identifies story-based content (narratives, experiences, confessions)
    - CategoryClassifier: Categorizes content into 8 primary categories for short-form video
    - TextClassifier: Enriches IdeaInspiration with classification metadata

Categories:
    - Storytelling: Narratives, fictional or real
    - Entertainment: Quick fun content (memes, comedy, pranks, fails, reactions)
    - Education / Informational: Explainers, tutorials, facts, news
    - Lifestyle / Vlog: Daily life, beauty, fashion, fitness, food, travel
    - Gaming: Gameplay clips, highlights, speedruns, walkthroughs
    - Challenges & Trends: Social challenges, trending sounds, AR effects
    - Reviews & Commentary: Product reviews, reactions, opinion commentary
    - Unusable: Content not useful for story generation

Compatible with all PrismQ content sources:
- Content.Shorts (YouTube, TikTok, Instagram Reels)
- Content.Streams (Twitch Clips, Kick Clips)
- Content.Forums (Reddit, HackerNews)
- Content.Articles (Medium, Web Articles)
- Content.Podcasts (Spotify, Apple Podcasts)
- Signals.* (Trends, Hashtags, Memes, Challenges, etc.)
- Commerce, Events, Community, Creative, Internal sources
"""

from .story_detector import StoryDetector
from .category_classifier import CategoryClassifier
from .categories import PrimaryCategory, CategoryResult
from .text_classifier import TextClassifier, ClassificationEnrichment
from .extract import IdeaInspirationExtractor
from .builder import IdeaInspirationBuilder

# Type hints for working with external IdeaInspiration model
from .idea_inspiration import (
    IdeaInspirationProtocol,
    IdeaInspirationDict,
    IdeaInspirationLike
)

__version__ = "2.1.0"
__all__ = [
    # Core classifiers
    'StoryDetector',
    'CategoryClassifier',
    'TextClassifier',
    # Category types
    'PrimaryCategory',
    'CategoryResult',
    # Classification enrichment
    'ClassificationEnrichment',
    # Helper utilities
    'IdeaInspirationExtractor',
    'IdeaInspirationBuilder',
    # Type hints
    'IdeaInspirationProtocol',
    'IdeaInspirationDict',
    'IdeaInspirationLike'
]
