"""Review title v2 against script v2 with improvement tracking.

This module implements the AI-powered title review function for v2 iterations.
It evaluates how well a refined title (v2) aligns with its refined script (v2)
and tracks improvements from v1.

The v2 reviewer provides:
- Title-script alignment assessment for v2 versions
- Comparison with v1 review results
- Improvement trajectory tracking
- Enhanced feedback for further refinement
- Structured JSON-compatible feedback

Workflow Position:
    Title v2 + Content v2 + v1 Review → From.Script v2 Review → TitleReview Feedback → Title v3
"""

import logging
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Setup logging
logger = logging.getLogger(__name__)

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from T.Review.Title.From.Content.Idea.by_script_and_idea import (
    AlignmentAnalysis,
    analyze_engagement,
    analyze_seo,
    analyze_title_content_alignment,
    extract_keywords,
)
from T.Review.Title.From.Content.Idea.title_review import (
    TitleCategoryScore,
    TitleImprovementPoint,
    TitleReview,
    TitleReviewCategory,
)

# Score thresholds
SCORE_THRESHOLD_LOW = 70  # Scores below this need improvement
SCORE_THRESHOLD_VERY_LOW = 60  # Scores below this need major revision
SCORE_THRESHOLD_HIGH = 80  # Scores above this are ready to proceed
EXPECTATION_THRESHOLD = 80  # Expectation accuracy threshold

# Length thresholds
OPTIMAL_LENGTH_MIN = 30
OPTIMAL_LENGTH_MAX = 75
OPTIMAL_LENGTH_TARGET = 60

# Comparison thresholds
IMPROVEMENT_THRESHOLD = 0  # Score increase > 0 means improved
REGRESSION_THRESHOLD = -5  # Score decrease > 5 means regression
MAINTAINED_THRESHOLD = 5  # Score change within ±5 means maintained


@dataclass
class ImprovementComparison:
    """Comparison of improvements between v1 and v2."""

    category: str
    v1_score: int
    v2_score: int
    delta: int
    improved: bool
    regression: bool
    maintained: bool
    feedback: str


def compare_reviews(
    v1_review: Optional[TitleReview], v2_review: TitleReview
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
    comparisons.append(
        ImprovementComparison(
            category="overall",
            v1_score=v1_review.overall_score,
            v2_score=v2_review.overall_score,
            delta=overall_delta,
            improved=overall_delta > IMPROVEMENT_THRESHOLD,
            regression=overall_delta < REGRESSION_THRESHOLD,
            maintained=abs(overall_delta) <= MAINTAINED_THRESHOLD,
            feedback=_generate_overall_feedback(overall_delta),
        )
    )

    # Compare script alignment
    script_delta = v2_review.script_alignment_score - v1_review.script_alignment_score
    comparisons.append(
        ImprovementComparison(
            category="script_alignment",
            v1_score=v1_review.script_alignment_score,
            v2_score=v2_review.script_alignment_score,
            delta=script_delta,
            improved=script_delta > IMPROVEMENT_THRESHOLD,
            regression=script_delta < REGRESSION_THRESHOLD,
            maintained=abs(script_delta) <= MAINTAINED_THRESHOLD,
            feedback=_generate_alignment_feedback(script_delta, "script"),
        )
    )

    # Compare engagement score
    engagement_delta = v2_review.engagement_score - v1_review.engagement_score
    comparisons.append(
        ImprovementComparison(
            category="engagement",
            v1_score=v1_review.engagement_score,
            v2_score=v2_review.engagement_score,
            delta=engagement_delta,
            improved=engagement_delta > IMPROVEMENT_THRESHOLD,
            regression=engagement_delta < REGRESSION_THRESHOLD,
            maintained=abs(engagement_delta) <= MAINTAINED_THRESHOLD,
            feedback=_generate_engagement_feedback(engagement_delta),
        )
    )

    # Compare SEO score
    seo_delta = v2_review.seo_score - v1_review.seo_score
    comparisons.append(
        ImprovementComparison(
            category="seo",
            v1_score=v1_review.seo_score,
            v2_score=v2_review.seo_score,
            delta=seo_delta,
            improved=seo_delta > IMPROVEMENT_THRESHOLD,
            regression=seo_delta < REGRESSION_THRESHOLD,
            maintained=abs(seo_delta) <= MAINTAINED_THRESHOLD,
            feedback=_generate_seo_feedback(seo_delta),
        )
    )

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


def _generate_engagement_feedback(delta: int) -> str:
    """Generate feedback for engagement score change."""
    if delta > 10:
        return "Much more engaging title"
    elif delta > IMPROVEMENT_THRESHOLD:
        return "More engaging than previous version"
    elif delta == 0:
        return "Engagement level maintained"
    elif delta > REGRESSION_THRESHOLD:
        return "Slightly less engaging"
    else:
        return "Engagement significantly decreased - reconsider changes"


def _generate_seo_feedback(delta: int) -> str:
    """Generate feedback for SEO score change."""
    if delta > 10:
        return "SEO optimization significantly improved"
    elif delta > IMPROVEMENT_THRESHOLD:
        return "Better SEO optimization"
    elif delta == 0:
        return "SEO optimization maintained"
    elif delta > REGRESSION_THRESHOLD:
        return "Minor SEO optimization loss"
    else:
        return "SEO optimization significantly worse"


def review_title_by_content_v2(
    title_text: str,
    content_text: str,
    title_id: Optional[str] = None,
    content_id: Optional[str] = None,
    script_summary: Optional[str] = None,
    title_version: str = "v2",
    script_version: str = "v2",
    previous_review: Optional[TitleReview] = None,
    reviewer_id: str = "AI-TitleReviewer-v2-001",
) -> TitleReview:
    """Review title v2 against script v2 with improvement tracking.

    This function evaluates how well a refined title (v2+) aligns with its
    refined script (v2+) and tracks improvements from previous versions.

    The v2 review focuses on:
    - Title-script alignment for refined versions
    - Improvement tracking from v1 to v2
    - Identification of regressions
    - Enhanced feedback for further refinement

    Args:
        title_text: The title text to review (v2)
        content_text: The script text (v2)
        title_id: Optional identifier for the title
        content_id: Optional identifier for the script
        script_summary: Optional summary of script content
        title_version: Version of title being reviewed (default "v2")
        script_version: Version of script being reviewed (default "v2")
        previous_review: Previous review (v1) for comparison tracking
        reviewer_id: Identifier for the reviewer

    Returns:
        TitleReview object with scores, feedback, and improvement comparisons

    Raises:
        ValueError: If title_text or content_text is empty or invalid
        TypeError: If parameters are of incorrect type

    Example:
        >>> v1_review = review_title_by_content_and_idea(
        ...     title_text="The Echo",
        ...     content_text="A horror short...",
        ...     idea_summary="Horror story"
        ... )
        >>> v2_review = review_title_by_content_v2(
        ...     title_text="The Echo - A Haunting Discovery",
        ...     content_text="Enhanced horror short...",
        ...     previous_review=v1_review
        ... )
        >>> print(v2_review.overall_score)  # Compare with v1
    """
    import uuid

    # Parameter validation
    if not title_text or not isinstance(title_text, str):
        raise ValueError("title_text must be a non-empty string")
    
    if not content_text or not isinstance(content_text, str):
        raise ValueError("content_text must be a non-empty string")
    
    if not isinstance(title_version, str) or not title_version:
        raise ValueError("title_version must be a non-empty string")
    
    if not isinstance(script_version, str) or not script_version:
        raise ValueError("script_version must be a non-empty string")
    
    if not isinstance(reviewer_id, str) or not reviewer_id:
        raise ValueError("reviewer_id must be a non-empty string")
    
    if previous_review is not None and not isinstance(previous_review, TitleReview):
        raise TypeError("previous_review must be a TitleReview instance or None")
    
    # Sanitize inputs (strip excess whitespace)
    title_text = title_text.strip()
    content_text = content_text.strip()
    
    # Validate length constraints
    if len(title_text) > 200:
        raise ValueError(f"title_text exceeds maximum length of 200 characters (got {len(title_text)})")
    
    if len(title_text) < 3:
        raise ValueError(f"title_text is too short (minimum 3 characters, got {len(title_text)})")
    
    if len(content_text) < 10:
        raise ValueError(f"content_text is too short (minimum 10 characters, got {len(content_text)})")

    logger.info(
        "Starting title review",
        extra={
            "title_version": title_version,
            "script_version": script_version,
            "title_length": len(title_text),
            "content_length": len(content_text),
            "has_previous_review": previous_review is not None,
        }
    )

    # Generate IDs if not provided
    if title_id is None:
        title_id = f"title-{uuid.uuid4().hex[:8]}"
        logger.debug(f"Generated title_id: {title_id}")
    if content_id is None:
        content_id = f"script-{uuid.uuid4().hex[:8]}"
        logger.debug(f"Generated content_id: {content_id}")

    # Auto-generate script summary if not provided
    if script_summary is None and content_text:
        script_summary = content_text[:200] + "..." if len(content_text) > 200 else content_text
        logger.debug(f"Generated script summary ({len(script_summary)} chars)")

    try:
        # Analyze title-script alignment
        logger.debug("Analyzing title-script alignment")
        script_alignment = analyze_title_content_alignment(
            title_text=title_text, content_text=content_text, script_summary=script_summary
        )
        logger.debug(f"Script alignment score: {script_alignment.score}")

        # Analyze engagement
        logger.debug("Analyzing engagement")
        engagement_data = analyze_engagement(title_text)
        logger.debug(f"Engagement score: {engagement_data['engagement_score']}")

        # Analyze SEO
        logger.debug("Analyzing SEO")
        script_keywords = extract_keywords(content_text, max_keywords=20)
        seo_data = analyze_seo(title_text, script_keywords)
        logger.debug(f"SEO score: {seo_data['seo_score']}")

        # Calculate overall score (script alignment is primary for v2)
        overall_score = int(
            script_alignment.score * 0.40  # Higher weight on script alignment
            + engagement_data["engagement_score"] * 0.30
            + seo_data["seo_score"] * 0.20
            + seo_data["length_score"] * 0.10
        )
        logger.info(f"Calculated overall score: {overall_score}")

    except Exception as e:
        logger.error(f"Error during review analysis: {e}", exc_info=True)
        raise

    # Build category scores
    category_scores = [
        TitleCategoryScore(
            category=TitleReviewCategory.SCRIPT_ALIGNMENT,
            score=script_alignment.score,
            reasoning=script_alignment.reasoning,
            strengths=script_alignment.matches,
            weaknesses=script_alignment.mismatches,
        ),
        TitleCategoryScore(
            category=TitleReviewCategory.ENGAGEMENT,
            score=engagement_data["engagement_score"],
            reasoning=f"Engagement score based on title structure and emotional appeal",
            strengths=[f"Uses {engagement_data.get('engagement_words', 0)} engagement words"],
            weaknesses=(
                ["Low expectation accuracy"]
                if engagement_data.get("expectation_accuracy", 100) < EXPECTATION_THRESHOLD
                else []
            ),
        ),
        TitleCategoryScore(
            category=TitleReviewCategory.SEO_OPTIMIZATION,
            score=seo_data["seo_score"],
            reasoning="SEO evaluation based on keywords and patterns",
            strengths=(
                ["Good keyword relevance"]
                if seo_data.get("keyword_relevance", 0) > SCORE_THRESHOLD_LOW
                else []
            ),
            weaknesses=[],
        ),
        TitleCategoryScore(
            category=TitleReviewCategory.LENGTH,
            score=seo_data["length_score"],
            reasoning=f"Length assessment: {len(title_text)} chars (optimal: ~{OPTIMAL_LENGTH_TARGET})",
            strengths=(
                ["Appropriate length"] if abs(len(title_text) - OPTIMAL_LENGTH_TARGET) <= 15 else []
            ),
            weaknesses=(
                ["Too long"]
                if len(title_text) > OPTIMAL_LENGTH_MAX
                else (["Too short"] if len(title_text) < OPTIMAL_LENGTH_MIN else [])
            ),
        ),
    ]

    # Generate improvement points based on scores
    improvement_points = []

    if script_alignment.score < SCORE_THRESHOLD_LOW:
        improvement_points.append(
            TitleImprovementPoint(
                category=TitleReviewCategory.SCRIPT_ALIGNMENT,
                title="Improve script alignment",
                description=f"Title alignment with script is {script_alignment.score}%. Consider incorporating more script keywords.",
                priority="high",
                impact_score=85,
                specific_example=f"Missing keywords: {', '.join(script_alignment.mismatches[:3])}",
                suggested_fix=f"Include key script elements: {', '.join(script_alignment.key_elements[:3])}",
            )
        )

    if engagement_data["engagement_score"] < SCORE_THRESHOLD_LOW:
        improvement_points.append(
            TitleImprovementPoint(
                category=TitleReviewCategory.ENGAGEMENT,
                title="Enhance engagement",
                description=f"Engagement score is {engagement_data['engagement_score']}%. Title could be more compelling.",
                priority="medium",
                impact_score=70,
                specific_example="Consider adding emotional hooks or curiosity triggers",
                suggested_fix="Use powerful words or create intrigue",
            )
        )

    if seo_data["seo_score"] < 65:
        improvement_points.append(
            TitleImprovementPoint(
                category=TitleReviewCategory.SEO_OPTIMIZATION,
                title="Optimize for SEO",
                description=f"SEO score is {seo_data['seo_score']}%. Consider SEO best practices.",
                priority="low",
                impact_score=50,
                specific_example="Add relevant keywords or numbers",
                suggested_fix=f"Consider keywords: {', '.join(seo_data['suggested_keywords'][:3])}",
            )
        )

    # Sort by impact score
    improvement_points.sort(key=lambda x: x.impact_score, reverse=True)

    # Determine iteration number and previous review ID
    iteration_number = 2  # Default for v2
    previous_review_id = None
    improvement_trajectory = [overall_score]

    if previous_review:
        iteration_number = previous_review.iteration_number + 1
        previous_review_id = previous_review.title_id
        improvement_trajectory = previous_review.improvement_trajectory + [overall_score]

    # Create the review
    review = TitleReview(
        title_id=title_id,
        title_text=title_text,
        title_version=title_version,
        overall_score=overall_score,
        category_scores=category_scores,
        improvement_points=improvement_points,
        # Content Context
        content_id=content_id,
        script_title="",  # Not needed for v2 (focuses on alignment only)
        script_summary=script_summary or "",
        script_version=script_version,
        script_alignment_score=script_alignment.score,
        key_content_elements=script_alignment.key_elements,
        # Idea Context - Not used in v2 review (focuses on script only)
        idea_id="",
        idea_summary="",
        idea_intent="",
        idea_alignment_score=0,
        target_audience="",
        # Engagement Metrics
        engagement_score=engagement_data["engagement_score"],
        clickthrough_potential=engagement_data["clickthrough_potential"],
        curiosity_score=engagement_data["curiosity_score"],
        expectation_accuracy=engagement_data["expectation_accuracy"],
        # SEO & Optimization
        seo_score=seo_data["seo_score"],
        keyword_relevance=seo_data["keyword_relevance"],
        suggested_keywords=seo_data["suggested_keywords"],
        length_score=seo_data["length_score"],
        current_length_chars=len(title_text),
        optimal_length_chars=60,
        # Review Metadata
        reviewer_id=reviewer_id,
        review_version=2,  # v2 review
        confidence_score=85,
        # Feedback Loop
        needs_major_revision=overall_score < SCORE_THRESHOLD_VERY_LOW,
        iteration_number=iteration_number,
        previous_review_id=previous_review_id,
        improvement_trajectory=improvement_trajectory,
        # Additional Context
        strengths=[
            f"Content alignment: {script_alignment.score}%",
            f"Engagement: {engagement_data['engagement_score']}%",
        ],
        primary_concern=(
            improvement_points[0].description if improvement_points else "No major concerns"
        ),
        quick_wins=[
            imp.title for imp in improvement_points[:3] if imp.priority in ["high", "medium"]
        ],
        notes=f"Review of {title_version} title against {script_version} script",
    )

    return review


def get_improvement_summary(
    v1_review: Optional[TitleReview], v2_review: TitleReview
) -> Dict[str, Any]:
    """Generate a summary of improvements from v1 to v2.

    Args:
        v1_review: Previous review (v1)
        v2_review: Current review (v2)

    Returns:
        Dictionary with improvement summary and recommendations
    """
    if not v1_review:
        return {
            "has_comparison": False,
            "message": "No previous review available for comparison",
            "current_score": v2_review.overall_score,
        }

    comparisons = compare_reviews(v1_review, v2_review)

    # Categorize changes
    improvements = [c for c in comparisons if c.improved]
    regressions = [c for c in comparisons if c.regression]
    maintained = [c for c in comparisons if c.maintained]

    # Overall assessment
    overall_comp = comparisons[0]  # First is always overall
    assessment = (
        "improved"
        if overall_comp.improved
        else "regressed" if overall_comp.regression else "maintained"
    )

    return {
        "has_comparison": True,
        "overall_assessment": assessment,
        "overall_delta": overall_comp.delta,
        "v1_score": v1_review.overall_score,
        "v2_score": v2_review.overall_score,
        "improvements": [
            {"category": c.category, "delta": c.delta, "feedback": c.feedback} for c in improvements
        ],
        "regressions": [
            {"category": c.category, "delta": c.delta, "feedback": c.feedback} for c in regressions
        ],
        "maintained": [c.category for c in maintained],
        "recommendation": _generate_recommendation(comparisons),
        "next_steps": _generate_next_steps(v2_review, comparisons),
    }


def _generate_recommendation(comparisons: List[ImprovementComparison]) -> str:
    """Generate recommendation based on comparison results."""
    improvements = sum(1 for c in comparisons if c.improved)
    regressions = sum(1 for c in comparisons if c.regression)

    if improvements >= 3:
        return "Excellent progress - continue refinement"
    elif improvements >= 2 and regressions == 0:
        return "Good progress - focus on remaining areas"
    elif regressions >= 2:
        return "Multiple regressions detected - review changes carefully"
    elif regressions >= 1:
        return "Some regression - address before proceeding"
    else:
        return "Minimal change - consider more significant revisions"


def _generate_next_steps(
    review: TitleReview, comparisons: List[ImprovementComparison]
) -> List[str]:
    """Generate next steps based on review and comparisons."""
    steps = []

    # Check for regressions
    regressions = [c for c in comparisons if c.regression]
    if regressions:
        steps.append(f"Address regressions in: {', '.join([c.category for c in regressions])}")

    # Check for low scores
    if review.script_alignment_score < SCORE_THRESHOLD_LOW:
        steps.append("Improve script alignment by incorporating more script keywords")

    if review.engagement_score < SCORE_THRESHOLD_LOW:
        steps.append("Enhance engagement with more compelling language")

    if review.overall_score >= SCORE_THRESHOLD_HIGH:
        steps.append("Ready for v3 refinement or acceptance check")
    elif review.overall_score >= SCORE_THRESHOLD_LOW:
        steps.append("Consider minor adjustments before proceeding")
    else:
        steps.append("Significant improvements needed before proceeding")

    return steps if steps else ["Ready to proceed"]
