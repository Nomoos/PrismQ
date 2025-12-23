"""PrismQ.T.Content.From.Idea.Title - Initial Content Generation Module

This module generates initial script drafts (v1) from an Idea object and a title variant.

Stage 3 in MVP workflow:
    Idea Creation → Title From.Idea (v1) → Content From.Idea.Title (v1)

Workflow States:
    Input State: PrismQ.T.Content.From.Idea.Title
    Output State: PrismQ.T.Review.Title.From.Content

Key Features:
- Select oldest Story where state is PrismQ.T.Content.From.Idea.Title
- Generate structured scripts with intro, body, and conclusion
- Platform optimization (YouTube shorts, etc.)
- Multiple structure types (hook-deliver-cta, three-act, problem-solution)
- Duration targeting and estimation
- Coherence with title promises and idea intent
- State transition to PrismQ.T.Review.Title.From.Content

Usage:
    # Generate a single script (primary state-based workflow)
    from T.Content.From.Idea.Title import StoryScriptService

    service = StoryScriptService(connection)
    result = service.process_oldest_story()
    if result and result.success:
        print(f"Generated script {result.content_id}")

    # Generate script directly
    from T.Content.From.Idea.Title import ScriptGenerator

    generator = ScriptGenerator()
    script = generator.generate_content_v1(idea=my_idea, title="My Title")
"""

from .src.script_generator import (
    PlatformTarget,
    ScriptGenerator,
    ScriptGeneratorConfig,
    ScriptSection,
    ScriptStructure,
    ScriptTone,
    ScriptV1,
)
from .src.story_content_service import (
    ContentGenerationResult,
    StoryScriptService,
    process_all_pending_stories,
)

__version__ = "0.2.0"
__all__ = [
    # Content Generator
    "ScriptGenerator",
    "ScriptGeneratorConfig",
    "ScriptV1",
    "ScriptSection",
    "ScriptStructure",
    "PlatformTarget",
    "ScriptTone",
    # Story Content Service
    "StoryScriptService",
    "ContentGenerationResult",
    "process_all_pending_stories",
]
