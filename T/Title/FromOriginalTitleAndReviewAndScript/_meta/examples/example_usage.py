"""Example usage of Title Improvement module (MVP-006).

This example demonstrates:
1. Starting with title v1 and script v1
2. Getting review feedback from both reviews
3. Generating improved title v2
4. Understanding the improvement rationale
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'T' / 'Title' / 'FromOriginalTitleAndReviewAndScript' / 'src'))
sys.path.insert(0, str(project_root / 'T' / 'Review' / 'Title' / 'ByScriptAndIdea'))
sys.path.insert(0, str(project_root / 'T' / 'Review' / 'Script' / 'ByTitle'))
sys.path.insert(0, str(project_root / 'T' / 'Review' / 'Script'))
sys.path.insert(0, str(project_root / 'T' / 'Idea' / 'Model' / 'src'))

from title_improver import improve_title_from_reviews
from title_review import (
    TitleReview,
    TitleImprovementPoint,
    TitleReviewCategory
)
from script_review import (
    ScriptReview,
    ImprovementPoint,
    ReviewCategory,
    ContentLength
)
from idea import Idea, IdeaStatus


def example_complete_workflow():
    """Example: Complete title improvement workflow (v1 → v2)."""
    print("=" * 80)
    print("Example: Title Improvement Workflow (MVP-006)")
    print("Stage 6: Generate Title v2 from v1 + Reviews")
    print("=" * 80)
    
    # -------------------------------------------------------------------------
    # Stage 2: Title v1 (from Idea)
    # -------------------------------------------------------------------------
    title_v1 = "The Haunting Echo"
    
    print("\n📝 ORIGINAL TITLE (v1)")
    print(f"Title: '{title_v1}'")
    
    # -------------------------------------------------------------------------
    # Stage 3: Script v1 (from Idea + Title)
    # -------------------------------------------------------------------------
    script_v1 = """
    In the abandoned Victorian house on Elm Street, strange echoes fill the air.
    Every night at midnight, Sarah hears voices repeating her words.
    The haunting sound grows stronger, revealing dark secrets buried in the walls.
    
    As Sarah investigates deeper, she discovers the house's tragic past.
    Each echo brings her closer to uncovering a century-old mystery.
    The voices aren't random - they're messages from trapped souls.
    
    In a climactic revelation, Sarah realizes the echoes are warnings.
    A danger still lurks in the shadows of the old Victorian house.
    She must break the curse before she becomes the next echo.
    """
    
    print("\n📄 SCRIPT (v1)")
    print(f"Length: {len(script_v1.split())} words")
    print(f"Preview: {script_v1.strip()[:100]}...")
    
    # -------------------------------------------------------------------------
    # Stage 4: Title Review (MVP-004)
    # -------------------------------------------------------------------------
    title_review = TitleReview(
        title_id="title-001",
        title_text=title_v1,
        title_version="v1",
        overall_score=72,
        script_alignment_score=68,
        idea_alignment_score=75,
        engagement_score=70,
        script_id="script-001",
        script_title=title_v1,
        script_summary="Horror mystery about echoes revealing secrets",
        key_script_elements=["Victorian", "secrets", "trapped souls", "curse", "mystery"],
        suggested_keywords=["Victorian", "curse", "souls"],
        current_length_chars=len(title_v1),
        optimal_length_chars=60,
        seo_score=65
    )
    
    # Add specific improvement points
    title_review.improvement_points = [
        TitleImprovementPoint(
            category=TitleReviewCategory.SCRIPT_ALIGNMENT,
            title="Missing Victorian era element",
            description="Script emphasizes Victorian house but title doesn't reflect this setting",
            priority="high",
            impact_score=85,
            suggested_fix="Incorporate 'Victorian' or time period reference"
        ),
        TitleImprovementPoint(
            category=TitleReviewCategory.ENGAGEMENT,
            title="Missing danger/stakes element",
            description="Script has strong danger element (curse, trapped souls) not in title",
            priority="high",
            impact_score=80,
            suggested_fix="Add element of danger or threat"
        ),
        TitleImprovementPoint(
            category=TitleReviewCategory.CLARITY,
            title="'Haunting Echo' is somewhat generic",
            description="Title could be more specific about the unique aspects",
            priority="medium",
            impact_score=65,
            suggested_fix="Make more unique and specific"
        )
    ]
    
    print("\n🔍 TITLE REVIEW (Stage 4: MVP-004)")
    print(f"Overall Score: {title_review.overall_score}%")
    print(f"Script Alignment: {title_review.script_alignment_score}%")
    print(f"Engagement: {title_review.engagement_score}%")
    print(f"\nKey Script Elements: {', '.join(title_review.key_script_elements)}")
    print(f"\nImprovement Points ({len(title_review.improvement_points)}):")
    for i, point in enumerate(title_review.improvement_points, 1):
        print(f"  {i}. [{point.priority.upper()}] {point.title}")
        print(f"     {point.description}")
    
    # -------------------------------------------------------------------------
    # Stage 5: Script Review (MVP-005)
    # -------------------------------------------------------------------------
    script_review = ScriptReview(
        script_id="script-001",
        script_title=title_v1,
        overall_score=76,
        target_audience="Horror enthusiasts aged 18-35",
        audience_alignment_score=80,
        target_length=ContentLength.SHORT_FORM,
        current_length_seconds=135
    )
    
    # Add improvement points
    script_review.improvement_points = [
        ImprovementPoint(
            category=ReviewCategory.ENGAGEMENT,
            title="Title promise vs script delivery",
            description="Title promises 'haunting echo' but script delivers Victorian Gothic mystery with trapped souls",
            priority="high",
            impact_score=85,
            suggested_fix="Title should reflect Victorian Gothic elements and trapped souls theme"
        ),
        ImprovementPoint(
            category=ReviewCategory.STRUCTURE,
            title="Opening hook strength",
            description="Strong opening with Victorian house and mystery - title could better set up this Gothic atmosphere",
            priority="medium",
            impact_score=70,
            suggested_fix="Consider Gothic or period-specific language in title"
        )
    ]
    
    print("\n🔍 SCRIPT REVIEW (Stage 5: MVP-005)")
    print(f"Overall Score: {script_review.overall_score}%")
    print(f"Audience Alignment: {script_review.audience_alignment_score}%")
    print(f"\nImprovement Points ({len(script_review.improvement_points)}):")
    for i, point in enumerate(script_review.improvement_points, 1):
        print(f"  {i}. [{point.priority.upper()}] {point.title}")
        print(f"     {point.description}")
    
    # -------------------------------------------------------------------------
    # Stage 6: Generate Title v2 (MVP-006) - THIS MODULE
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("🚀 GENERATING IMPROVED TITLE (v2)")
    print("=" * 80)
    
    # Create idea for context
    idea = Idea(
        title="Victorian Echo Mystery",
        concept="Horror story about mysterious echoes in an abandoned Victorian house revealing trapped souls and a century-old curse",
        status=IdeaStatus.APPROVED
    )
    
    # Generate improved title
    result = improve_title_from_reviews(
        original_title=title_v1,
        script_text=script_v1,
        title_review=title_review,
        script_review=script_review,
        idea=idea,
        original_version="v1",
        new_version="v2"
    )
    
    # -------------------------------------------------------------------------
    # Display Results
    # -------------------------------------------------------------------------
    print("\n✨ IMPROVEMENT RESULTS")
    print(f"\nOriginal (v1): '{result.original_version.text}'")
    print(f"Improved (v2): '{result.new_version.text}'")
    
    print(f"\n📊 CHANGES")
    print(f"Length: {len(result.original_version.text)} → {len(result.new_version.text)} chars")
    
    print(f"\n📝 RATIONALE")
    print(result.rationale)
    
    print(f"\n✅ ADDRESSED IMPROVEMENTS ({len(result.addressed_improvements)})")
    for i, improvement in enumerate(result.addressed_improvements, 1):
        print(f"  {i}. {improvement}")
    
    print(f"\n🎯 SCRIPT ALIGNMENT NOTES")
    print(result.script_alignment_notes)
    
    print(f"\n💡 ENGAGEMENT NOTES")
    print(result.engagement_notes)
    
    print(f"\n📚 VERSION HISTORY")
    for version in result.version_history:
        print(f"  - {version.version_number}: '{version.text}'")
        if version.changes_from_previous:
            print(f"    Changes: {version.changes_from_previous[:100]}...")
    
    print("\n" + "=" * 80)
    print("✓ Title v2 generated successfully!")
    print("Next Step: Stage 7 - Generate Script v2 (MVP-007)")
    print("=" * 80)
    
    return result


def example_iteration_v2_to_v3():
    """Example: Iterative refinement (v2 → v3) - MVP-009.
    
    This example demonstrates the MVP-009 acceptance criteria:
    1. Refine title from v2 to v3 using v2 review feedback
    2. Polish for clarity and engagement
    3. Store v3 with reference to v2
    4. Support versioning (v3, v4, v5, v6, v7, etc.)
    5. Verify v3 incorporates v2 feedback
    """
    print("\n\n" + "=" * 80)
    print("Example: MVP-009 - Iterative Refinement (v2 → v3)")
    print("Stage 9: Further refinement based on v2 reviews")
    print("=" * 80)
    
    # Title v2 from previous iteration
    title_v2 = "The Victorian Echo: Trapped Souls"
    
    print(f"\n📝 CURRENT TITLE (v2)")
    print(f"Title: '{title_v2}'")
    
    script_v2 = """
    The Victorian mansion on Elm Street harbors a dark secret.
    Inside its walls, trapped souls echo their final moments.
    Sarah discovers she can hear them - but listening comes at a price.
    
    Each night, the echoes grow louder, revealing a century-old curse.
    The spirits are not random - they're trying to warn her.
    Someone must break the curse before it claims another victim.
    """
    
    # Create v2 review with minor refinements
    title_review_v2 = TitleReview(
        title_id="title-001",
        title_text=title_v2,
        title_version="v2",
        overall_score=82,
        script_alignment_score=85,
        idea_alignment_score=84,
        engagement_score=80,
        script_id="script-001",
        key_script_elements=["curse", "Victorian", "souls", "warning"],
        current_length_chars=len(title_v2),
        optimal_length_chars=60
    )
    
    # Minor improvement points for v3
    title_review_v2.improvement_points = [
        TitleImprovementPoint(
            category=TitleReviewCategory.ENGAGEMENT,
            title="Could emphasize the danger/warning aspect",
            description="Script shows souls are warning, could be in title",
            priority="medium",
            impact_score=70,
            suggested_fix="Consider 'Warning' or 'Curse' emphasis"
        )
    ]
    
    script_review_v2 = ScriptReview(
        script_id="script-001",
        script_title=title_v2,
        overall_score=85
    )
    
    print(f"\n🔍 REVIEWS (v2)")
    print(f"Title Score: {title_review_v2.overall_score}%")
    print(f"Script Score: {script_review_v2.overall_score}%")
    print(f"Status: Good alignment, minor refinement suggested")
    
    # Generate v3
    result = improve_title_from_reviews(
        original_title=title_v2,
        script_text=script_v2,
        title_review=title_review_v2,
        script_review=script_review_v2,
        original_version="v2",
        new_version="v3"
    )
    
    print(f"\n✨ REFINEMENT RESULTS")
    print(f"\nv2: '{result.original_version.text}'")
    print(f"v3: '{result.new_version.text}'")
    print(f"\nRationale: {result.rationale}")
    
    print("\n" + "=" * 80)
    print("✓ Title v3 generated!")
    print("Next: Stage 12 - Title Acceptance Check")
    print("=" * 80)


if __name__ == "__main__":
    # Run examples
    print("\n" + "=" * 80)
    print("MVP-006: TITLE IMPROVEMENTS v2 - EXAMPLES")
    print("Module: PrismQ.T.Title.FromOriginalTitleAndReviewAndScript")
    print("=" * 80)
    
    # Example 1: v1 → v2
    result1 = example_complete_workflow()
    
    # Example 2: v2 → v3 (iterative)
    example_iteration_v2_to_v3()
    
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("""
This module implements MVP-006: Title Improvements v2

Key Features:
✓ Generates improved title versions based on dual review feedback
✓ Uses feedback from both Title Review (MVP-004) and Script Review (MVP-005)
✓ Maintains engagement while improving alignment
✓ Tracks version history and changes
✓ Provides detailed rationale for improvements
✓ Addresses specific improvement points from reviews

Workflow Position:
  Title v1 + Script v1 + Reviews → [THIS MODULE] → Title v2 → Next stages

The module is ready for use in Stage 6 of the MVP workflow!
""")
