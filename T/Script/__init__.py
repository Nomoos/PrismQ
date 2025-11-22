"""PrismQ.T.Script - Script Development Module

This module provides comprehensive script development capabilities including:
- Initial script drafting from ideas and titles
- Iterative script improvement based on reviews
- AI-powered script optimization with feedback loops

The module structure:
- FromIdeaAndTitle: Initial script generation (v1)
- FromOriginalScriptAndReviewAndTitle: Script improvements (v2, v3+)
- src: AI ScriptWriter with feedback loop optimization

For convenience, the ScriptWriter class is exported at the module level
for cleaner imports: `from PrismQ.T.Script import ScriptWriter`
"""

# Export ScriptWriter from src for convenient imports
from .src import (
    ScriptWriter,
    OptimizationStrategy,
    OptimizationResult,
    FeedbackLoopIteration
)

__all__ = [
    "ScriptWriter",
    "OptimizationStrategy",
    "OptimizationResult",
    "FeedbackLoopIteration"
]

__version__ = "1.0.0"
