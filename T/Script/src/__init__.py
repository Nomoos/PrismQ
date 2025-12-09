"""PrismQ.T.Script - AI Script Writer with Feedback Loop

AI-powered script writer with iterative optimization based on review feedback.

Note: The ScriptWriter is located in T/Script/src/ but exported through
the parent module for cleaner imports: `from PrismQ.T.Script import ScriptWriter`
"""

from .script_writer import (
    FeedbackLoopIteration,
    OptimizationResult,
    OptimizationStrategy,
    ScriptWriter,
)

__all__ = ["ScriptWriter", "OptimizationStrategy", "OptimizationResult", "FeedbackLoopIteration"]
