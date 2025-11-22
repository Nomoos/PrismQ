"""Review script v2 against title v3 with improvement tracking.

This module implements MVP-010: AI-powered script review for v2+ iterations.
It evaluates how well a refined script (v2) aligns with its refined title (v3)
and tracks improvements from v1.

The v2 reviewer provides:
- Script-title alignment assessment for v2+ versions
- Comparison with v1 review results
- Improvement trajectory tracking
- Enhanced feedback for further refinement
- Structured JSON-compatible feedback

Workflow Position:
    Script v2 + Title v3 + v1 Review → ByTitle v2 Review → ScriptReview Feedback → Script v3
"""

from typing import Optional, List, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from T.Review.Script.script_review import (
    ScriptReview,
    ReviewCategory,
    ContentLength,
    ImprovementPoint,
    CategoryScore
)
from T.Review.Script.ByTitle.script_review_by_title import (
    review_script_by_title,
    AlignmentScore,
    _analyze_title_alignment,
    _analyze_idea_alignment,
    _calculate_content_scores,
    _determine_target_length,
    _estimate_script_length,
    _calculate_overall_score,
    _generate_improvement_points,
    _create_category_scores,
    _identify_primary_concern,
    _identify_quick_wins
)

# Use TYPE_CHECKING to avoid runtime import issues
if TYPE_CHECKING:
    from T.Idea.Model.src.idea import Idea
else:
    # At runtime, we'll accept any object with the right attributes
    Idea = Any


# Score thresholds
SCORE_THRESHOLD_LOW = 70  # Scores below this need improvement
SCORE_THRESHOLD_VERY_LOW = 60  # Scores below this need major revision
SCORE_THRESHOLD_HIGH = 80  # Scores above this are ready to proceed

# Comparison thresholds
IMPROVEMENT_THRESHOLD = 0  # Score increase > 0 means improved
REGRESSION_THRESHOLD = -5  # Score decrease > 5 means regression
MAINTAINED_THRESHOLD = 5  # Score change within ±5 means maintained


@dataclass
class ImprovementComparison:
    """Comparison of improvements between v1 and v2 reviews."""
    
    category: str
    v1_score: int
    v2_score: int
    delta: int
    improved: bool
    regression: bool
    maintained: bool
    feedback: str


def compare_reviews(
    v1_review: Optional[ScriptReview],
    v2_review: ScriptReview
) -> List[ImprovementComparison]:
    """Compare v1 and v2 reviews to track improvements.
    
    Args:
        v1_review: Previous review (v1) for comparison, can be None
        v2_review: Current review (v2)
        
    Returns:
        List of ImprovementComparison objects showing progress
    """
    if not v1_review:
        return []
    
    comparisons = []
    
    # Compare overall score
    overall_delta = v2_review.overall_score - v1_review.overall_score
    comparisons.append(ImprovementComparison(
        category="overall",
        v1_score=v1_review.overall_score,
        v2_score=v2_review.overall_score,
        delta=overall_delta,
        improved=overall_delta > IMPROVEMENT_THRESHOLD,
        regression=overall_delta < REGRESSION_THRESHOLD,
        maintained=abs(overall_delta) <= MAINTAINED_THRESHOLD,
        feedback=_generate_overall_feedback(overall_delta)
    ))
    
    # Compare title alignment if available
    v1_title_score = int(v1_review.metadata.get("title_alignment_score", "0"))
    v2_title_score = int(v2_review.metadata.get("title_alignment_score", "0"))
    title_delta = v2_title_score - v1_title_score
    comparisons.append(ImprovementComparison(
        category="title_alignment",
        v1_score=v1_title_score,
        v2_score=v2_title_score,
        delta=title_delta,
        improved=title_delta > IMPROVEMENT_THRESHOLD,
        regression=title_delta < REGRESSION_THRESHOLD,
        maintained=abs(title_delta) <= MAINTAINED_THRESHOLD,
        feedback=_generate_alignment_feedback(title_delta, "title")
    ))
    
    # Compare idea alignment if available
    v1_idea_score = int(v1_review.metadata.get("idea_alignment_score", "0"))
    v2_idea_score = int(v2_review.metadata.get("idea_alignment_score", "0"))
    idea_delta = v2_idea_score - v1_idea_score
    comparisons.append(ImprovementComparison(
        category="idea_alignment",
        v1_score=v1_idea_score,
        v2_score=v2_idea_score,
        delta=idea_delta,
        improved=idea_delta > IMPROVEMENT_THRESHOLD,
        regression=idea_delta < REGRESSION_THRESHOLD,
        maintained=abs(idea_delta) <= MAINTAINED_THRESHOLD,
        feedback=_generate_alignment_feedback(idea_delta, "idea")
    ))
    
    # Compare category scores
    for v2_cat_score in v2_review.category_scores:
        v1_cat_score = v1_review.get_category_score(v2_cat_score.category)
        if v1_cat_score:
            delta = v2_cat_score.score - v1_cat_score.score
            comparisons.append(ImprovementComparison(
                category=v2_cat_score.category.value,
                v1_score=v1_cat_score.score,
                v2_score=v2_cat_score.score,
                delta=delta,
                improved=delta > IMPROVEMENT_THRESHOLD,
                regression=delta < REGRESSION_THRESHOLD,
                maintained=abs(delta) <= MAINTAINED_THRESHOLD,
                feedback=_generate_category_feedback(v2_cat_score.category.value, delta)
            ))
    
    return comparisons


def _generate_overall_feedback(delta: int) -> str:
    """Generate feedback for overall score change."""
    if delta > 10:
        return "Significant improvement in overall quality"
    elif delta > IMPROVEMENT_THRESHOLD:
        return "Modest improvement in overall quality"
    elif delta == 0:
        return "Overall quality maintained"
    elif delta > REGRESSION_THRESHOLD:
        return "Slight decrease in overall quality"
    else:
        return "Significant regression in overall quality - review changes"


def _generate_alignment_feedback(delta: int, alignment_type: str) -> str:
    """Generate feedback for alignment score change."""
    if delta > 10:
        return f"Much better alignment with {alignment_type}"
    elif delta > IMPROVEMENT_THRESHOLD:
        return f"Improved alignment with {alignment_type}"
    elif delta == 0:
        return f"Alignment with {alignment_type} maintained"
    elif delta > REGRESSION_THRESHOLD:
        return f"Slight decrease in {alignment_type} alignment"
    else:
        return f"Significant drop in {alignment_type} alignment - needs attention"


def _generate_category_feedback(category: str, delta: int) -> str:
    """Generate feedback for category score change."""
    if delta > 10:
        return f"{category.capitalize()} significantly improved"
    elif delta > IMPROVEMENT_THRESHOLD:
        return f"{category.capitalize()} improved"
    elif delta == 0:
        return f"{category.capitalize()} maintained"
    elif delta > REGRESSION_THRESHOLD:
        return f"{category.capitalize()} slightly decreased"
    else:
        return f"{category.capitalize()} significantly worse - review needed"


def review_script_by_title_v2(
    script_text: str,
    title: str,
    idea: Idea,
    script_id: Optional[str] = None,
    script_version: str = "v2",
    title_version: str = "v3",
    target_length_seconds: Optional[int] = None,
    previous_review: Optional[ScriptReview] = None,
    reviewer_id: str = "AI-ScriptReviewer-ByTitle-v2-001"
) -> ScriptReview:
    """Review script v2 against title v3 with improvement tracking.
    
    This function evaluates how well a refined script (v2+) aligns with its
    refined title (v3+) and tracks improvements from previous versions.
    
    The v2 review focuses on:
    - Script-title alignment for refined versions
    - Improvement tracking from v1 to v2
    - Identification of regressions
    - Enhanced feedback for further refinement
    
    Args:
        script_text: The script text to review (v2 or later)
        title: The title text (v3 or later - latest version)
        idea: The Idea model object containing the core concept
        script_id: Optional identifier for the script
        script_version: Version of script being reviewed (default "v2")
        title_version: Version of title being reviewed (default "v3")
        target_length_seconds: Optional target duration in seconds
        previous_review: Previous review (v1) for comparison tracking
        reviewer_id: Identifier for this reviewer
        
    Returns:
        ScriptReview object with scores, feedback, and improvement comparisons
        
    Example:
        >>> from T.Idea.Model.src.idea import Idea, ContentGenre
        >>> idea = Idea(
        ...     title="The Echo",
        ...     concept="A girl hears her own future voice warning her",
        ...     genre=ContentGenre.HORROR
        ... )
        >>> # First review (v1)
        >>> v1_review = review_script_by_title(script_v1, title_v1, idea)
        >>> 
        >>> # Second review (v2 script against v3 title)
        >>> v2_review = review_script_by_title_v2(
        ...     script_text=script_v2,
        ...     title=title_v3,
        ...     idea=idea,
        ...     previous_review=v1_review
        ... )
        >>> print(f"Overall improvement: {v2_review.overall_score - v1_review.overall_score}%")
    """
    import uuid
    
    # Generate script ID if not provided
    if script_id is None:
        script_id = f"script-{idea.title.lower().replace(' ', '-')}-{script_version}"
    
    # Perform base review using existing logic
    base_review = review_script_by_title(
        script_text=script_text,
        title=title,
        idea=idea,
        script_id=script_id,
        target_length_seconds=target_length_seconds,
        reviewer_id=reviewer_id
    )
    
    # Add version information to metadata
    base_review.metadata["script_version"] = script_version
    base_review.metadata["title_version"] = title_version
    base_review.metadata["review_type"] = "v2_refinement"
    
    # Compare with previous review if available
    if previous_review:
        comparisons = compare_reviews(previous_review, base_review)
        
        # Add comparison results to metadata
        base_review.metadata["has_comparison"] = "true"
        base_review.metadata["comparisons"] = str(len(comparisons))
        
        # Identify improvements and regressions
        improvements = [c for c in comparisons if c.improved]
        regressions = [c for c in comparisons if c.regression]
        
        base_review.metadata["improvements_count"] = str(len(improvements))
        base_review.metadata["regressions_count"] = str(len(regressions))
        
        # Add detailed comparison feedback
        comparison_notes = []
        for comp in comparisons:
            if comp.improved or comp.regression:
                comparison_notes.append(
                    f"{comp.category}: {comp.v1_score}% → {comp.v2_score}% ({comp.feedback})"
                )
        
        if comparison_notes:
            base_review.metadata["improvement_summary"] = "; ".join(comparison_notes[:5])
        
        # Add regression warnings to improvement points if needed
        if regressions:
            for regression in regressions:
                base_review.improvement_points.insert(0, ImprovementPoint(
                    category=ReviewCategory.STRUCTURE,
                    title=f"Address regression in {regression.category}",
                    description=f"Score decreased from {regression.v1_score}% to {regression.v2_score}%",
                    priority="high",
                    impact_score=abs(regression.delta),
                    specific_example=regression.feedback,
                    suggested_fix=f"Review and restore improvements from v1 or find better approach"
                ))
    else:
        base_review.metadata["has_comparison"] = "false"
    
    return base_review


def extract_improvements_from_review(review: ScriptReview) -> List[str]:
    """Extract actionable improvements from a review.
    
    Args:
        review: ScriptReview object
        
    Returns:
        List of improvement descriptions
    """
    improvements = []
    
    # Get high-priority improvements
    for point in review.improvement_points:
        if point.priority == "high":
            improvements.append(
                f"{point.title}: {point.suggested_fix} (impact: +{point.impact_score}%)"
            )
    
    return improvements


def is_ready_to_proceed(review: ScriptReview, threshold: int = SCORE_THRESHOLD_HIGH) -> bool:
    """Check if script is ready to proceed to next stage.
    
    Args:
        review: ScriptReview object
        threshold: Minimum score required (default 80)
        
    Returns:
        True if script meets quality threshold
    """
    return review.overall_score >= threshold and not review.needs_major_revision


def get_next_steps(review: ScriptReview) -> List[str]:
    """Generate next steps based on review results.
    
    Args:
        review: ScriptReview object
        
    Returns:
        List of recommended next steps
    """
    steps = []
    
    if is_ready_to_proceed(review):
        steps.append("Script meets quality standards - proceed to acceptance check")
    else:
        if review.needs_major_revision:
            steps.append("Major revision required - address all high-priority issues")
        else:
            steps.append("Minor improvements needed - address high-priority issues")
        
        # Add specific next steps from improvement points
        for point in review.improvement_points[:3]:
            steps.append(f"[{point.priority}] {point.title}")
    
    return steps
