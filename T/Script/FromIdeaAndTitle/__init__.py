"""PrismQ.T.Script.FromIdeaAndTitle - Initial Script Generation Module

This module generates initial script drafts (v1) from an Idea object and a title variant.

Stage 3 in MVP workflow:
    Idea Creation → Title FromIdea (v1) → Script FromIdeaAndTitle (v1)

Key Features:
- Generate structured scripts with intro, body, and conclusion
- Platform optimization (YouTube shorts, etc.)
- Multiple structure types (hook-deliver-cta, three-act, problem-solution)
- Duration targeting and estimation
- Coherence with title promises and idea intent
- Batch processing of stories needing scripts

Usage:
    # Generate a single script
    from PrismQ.T.Script.FromIdeaAndTitle import ScriptGenerator
    
    generator = ScriptGenerator()
    script = generator.generate_script_v1(idea=my_idea, title="My Title")
    
    # Process stories from database
    from PrismQ.T.Script.FromIdeaAndTitle import StoryScriptService
    
    service = StoryScriptService(connection)
    results = service.process_stories_needing_scripts()
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
