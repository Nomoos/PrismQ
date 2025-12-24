"""PrismQ.T.Content.From.Idea.Title - Initial Content Generation Module

This module generates initial content drafts (v1) from an Idea object and a title variant.

Stage 3 in MVP workflow:
    Idea Creation → Title From.Idea (v1) → Content From.Idea.Title (v1)

Workflow States:
    Input State: PrismQ.T.Content.From.Idea.Title
    Output State: PrismQ.T.Review.Title.From.Content

Key Features:
- Select oldest Story where state is PrismQ.T.Content.From.Idea.Title
- Generate structured content with intro, body, and conclusion
- Platform optimization (YouTube shorts, etc.)
- Multiple structure types (hook-deliver-cta, three-act, problem-solution)
- Duration targeting and estimation
- Coherence with title promises and idea intent
- State transition to PrismQ.T.Review.Title.From.Content

Usage:
    # Generate a single content (primary state-based workflow)
    from T.Content.From.Idea.Title import StoryContentService

    service = StoryContentService(connection)
    result = service.process_oldest_story()
    if result and result.success:
        print(f"Generated content {result.content_id}")

    # Generate content directly
    from T.Content.From.Idea.Title import ContentGenerator

    generator = ContentGenerator()
    content = generator.generate_content_v1(idea=my_idea, title="My Title")
"""

from .src.content_generator import (
    PlatformTarget,
    ContentGenerator,
    ContentGeneratorConfig,
    ContentSection,
    ContentStructure,
    ContentTone,
    ContentV1,
)
from .src.story_content_service import (
    ContentGenerationResult,
    StoryContentService,
    ContentFromIdeaTitleService,
    StateBasedContentResult,
    process_all_pending_stories,
    process_oldest_from_idea_title,
)

__version__ = "0.2.0"
__all__ = [
    # Content Generator
    "ContentGenerator",
    "ContentGeneratorConfig",
    "ContentV1",
    "ContentSection",
    "ContentStructure",
    "PlatformTarget",
    "ContentTone",
    # Story Content Service
    "StoryContentService",
    "ContentFromIdeaTitleService",
    "ContentGenerationResult",
    "StateBasedContentResult",
    "process_all_pending_stories",
    "process_oldest_from_idea_title",
]
