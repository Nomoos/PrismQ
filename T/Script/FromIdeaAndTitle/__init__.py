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

Usage:
    from PrismQ.T.Script.FromIdeaAndTitle import ScriptGenerator
    
    generator = ScriptGenerator()
    script = generator.generate_script_v1(idea=my_idea, title="My Title")
"""

from .src.script_generator import (
    ScriptGenerator,
    ScriptGeneratorConfig,
    ScriptV1,
    ScriptSection,
    ScriptStructure,
    PlatformTarget
)

__version__ = "0.1.0"
__all__ = [
    "ScriptGenerator",
    "ScriptGeneratorConfig",
    "ScriptV1",
    "ScriptSection",
    "ScriptStructure",
    "PlatformTarget"
]
