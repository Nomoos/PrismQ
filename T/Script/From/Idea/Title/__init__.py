"""PrismQ.T.Script.From.Idea.Title - Initial Script Generation Module

This module generates initial script drafts (v1) from an Idea object and a title variant.

Stage 3 in MVP workflow:
    Idea Creation → Title From.Idea (v1) → Script From.Idea.Title (v1)

Workflow States:
    Input State: PrismQ.T.Script.From.Idea.Title
    Output State: PrismQ.T.Review.Title.From.Script

Key Features:
- Select oldest Story where state is PrismQ.T.Script.From.Idea.Title
- Generate structured scripts with intro, body, and conclusion
- Platform optimization (YouTube shorts, etc.)
- Multiple structure types (hook-deliver-cta, three-act, problem-solution)
- Duration targeting and estimation
- Coherence with title promises and idea intent
- State transition to PrismQ.T.Review.Title.From.Script

Usage:
    # Generate a single script (primary state-based workflow)
    from T.Script.From.Idea.Title import StoryScriptService
    
    service = StoryScriptService(connection)
    result = service.process_oldest_story()
    if result and result.success:
        print(f"Generated script {result.script_id}")
    
    # Generate script directly
    from T.Script.From.Idea.Title import ScriptGenerator
    
    generator = ScriptGenerator()
    script = generator.generate_script_v1(idea=my_idea, title="My Title")
"""

from .src.script_generator import (
    ScriptGenerator,
    ScriptGeneratorConfig,
    ScriptV1,
    ScriptSection,
    ScriptStructure,
    PlatformTarget,
    ScriptTone
)
from .src.story_script_service import (
    StoryScriptService,
    ScriptGenerationResult,
    process_all_pending_stories
)

__version__ = "0.2.0"
__all__ = [
    # Script Generator
    "ScriptGenerator",
    "ScriptGeneratorConfig",
    "ScriptV1",
    "ScriptSection",
    "ScriptStructure",
    "PlatformTarget",
    "ScriptTone",
    # Story Script Service
    "StoryScriptService",
    "ScriptGenerationResult",
    "process_all_pending_stories"
]
