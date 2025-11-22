"""PrismQ.T.Script.FromOriginalScriptAndReviewAndTitle - Script Improvement Module

This module implements MVP-007 (Stage 7) of the PrismQ workflow:
Generate improved script versions (v2+) using review feedback and updated title.

The module handles all script improvements after the initial v1:
- Stage 7: First improvements (v1 → v2) using both reviews + new title v2
- Stage 11: Iterative refinements (v2 → v3+) until acceptance
- Stages 14-18: Quality dimension fixes (grammar, tone, content, consistency, editing)
- Stage 20: Readability polish for voiceover

Key Features:
- Process review feedback from multiple sources
- Align script with improved title versions
- Preserve successful elements while addressing issues
- Track version history and improvements made
- Support iterative refinement cycles

Usage:
    from PrismQ.T.Script.FromOriginalScriptAndReviewAndTitle import ScriptImprover, ReviewFeedback
    
    improver = ScriptImprover()
    
    # Create review feedback
    feedback = ReviewFeedback(
        script_review=script_review_obj,
        title_review=title_review_obj,
        priority_issues=["Issue 1", "Issue 2"]
    )
    
    # Generate improved script
    script_v2 = improver.generate_script_v2(
        original_script=script_v1,
        title_v2="Improved Title",
        review_feedback=feedback
    )
"""

from .src.script_improver import (
    ScriptImprover,
    ScriptImproverConfig,
    ScriptV2,
    ReviewFeedback
)

__all__ = ["ScriptImprover", "ScriptImproverConfig", "ScriptV2", "ReviewFeedback"]
