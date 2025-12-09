"""Example usage of TitleReview for title evaluation against script and idea.

This example demonstrates how to create and use a TitleReview to evaluate
a title v1 against script v1 and the original idea, following the workflow
for Stage 4 (MVP-004).
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

from T.Review.Title.ByScriptAndIdea import (
    TitleCategoryScore,
    TitleImprovementPoint,
    TitleReview,
    TitleReviewCategory,
)


def example_basic_review():
    """Example: Create a basic title review."""
    print("=" * 70)
    print("Example 1: Basic Title Review")
    print("=" * 70)

    review = TitleReview(
        title_id="title-horror-001",
        title_text="The Echo",
        title_version="v1",
        overall_score=68,
        # Script context
        script_id="script-horror-001",
        script_title="The Echo",
        script_summary="A horror short about mysterious echoes in an abandoned house",
        script_alignment_score=75,
        # Idea context
        idea_id="idea-horror-001",
        idea_summary="Horror story using auditory suspense",
        idea_alignment_score=70,
        # Basic scores
        engagement_score=65,
        seo_score=60,
    )

    print(f"\nTitle: '{review.title_text}'")
    print(f"Overall Score: {review.overall_score}%")
    print(f"Script Alignment: {review.script_alignment_score}%")
    print(f"Idea Alignment: {review.idea_alignment_score}%")
    print(f"Engagement: {review.engagement_score}%")
    print()


def example_complete_review():
    """Example: Create a complete review with all context."""
    print("=" * 70)
    print("Example 2: Complete Title Review with Full Context")
    print("=" * 70)

    review = TitleReview(
        title_id="title-horror-001",
        title_text="The Echo - A Haunting Discovery",
        title_version="v1",
        overall_score=78,
        # Script context
        script_id="script-horror-001",
        script_title="The Echo",
        script_summary="A horror short about mysterious echoes in an abandoned house that reveal dark secrets",
        script_version="v1",
        script_alignment_score=85,
        key_script_elements=["echo", "haunting", "abandoned house", "discovery", "secrets"],
        # Idea context
        idea_id="idea-horror-001",
        idea_summary="Horror story about sounds that repeat with increasing intensity",
        idea_intent="Create suspense through auditory elements and psychological tension",
        idea_alignment_score=82,
        target_audience="Horror enthusiasts aged 18-35",
        # Engagement metrics
        engagement_score=75,
        clickthrough_potential=72,
        curiosity_score=80,
        expectation_accuracy=76,
        # SEO metrics
        seo_score=68,
        keyword_relevance=70,
        suggested_keywords=["echo", "horror short", "haunting", "mystery", "abandoned house"],
        length_score=85,
        # Metadata
        reviewer_id="AI-TitleReviewer-001",
        confidence_score=88,
    )

    # Add category scores
    review.category_scores.append(
        TitleCategoryScore(
            category=TitleReviewCategory.SCRIPT_ALIGNMENT,
            score=85,
            reasoning="Title accurately reflects script content with key elements 'echo' and 'haunting'",
            strengths=[
                "Includes main element (echo)",
                "Indicates genre (haunting)",
                "Mentions discovery aspect",
            ],
            weaknesses=["Could be more specific about setting", "Subtitle is somewhat generic"],
        )
    )

    review.category_scores.append(
        TitleCategoryScore(
            category=TitleReviewCategory.IDEA_ALIGNMENT,
            score=82,
            reasoning="Captures the auditory suspense concept from the idea",
            strengths=[
                "Reflects sound-based horror theme",
                "Mysterious and ominous tone",
                "Suggests progressive revelation",
            ],
            weaknesses=[
                "Doesn't hint at intensification element",
                "Missing psychological tension aspect",
            ],
        )
    )

    review.category_scores.append(
        TitleCategoryScore(
            category=TitleReviewCategory.ENGAGEMENT,
            score=75,
            reasoning="Reasonably engaging but could be stronger",
            strengths=[
                "Creates curiosity about 'echo'",
                "Implies mystery with 'haunting'",
                "Promise of discovery",
            ],
            weaknesses=[
                "Subtitle lacks emotional punch",
                "Somewhat predictable horror formula",
                "Could be more unique",
            ],
        )
    )

    review.category_scores.append(
        TitleCategoryScore(
            category=TitleReviewCategory.EXPECTATION_SETTING,
            score=88,
            reasoning="Effectively sets expectations for horror content",
            strengths=[
                "Clear genre indication",
                "Promises mystery and discovery",
                "Tone matches content",
            ],
            weaknesses=["Could better hint at specific horror elements"],
        )
    )

    # Add improvement points
    review.improvement_points.append(
        TitleImprovementPoint(
            category=TitleReviewCategory.SCRIPT_ALIGNMENT,
            title="Add setting reference",
            description="Include reference to the abandoned house setting for better script alignment",
            priority="high",
            impact_score=20,
            specific_example="Current: 'The Echo - A Haunting Discovery' | Missing: Reference to house/location",
            suggested_fix="Consider: 'The Echo House' or 'Echoes of the Abandoned' to reference setting",
        )
    )

    review.improvement_points.append(
        TitleImprovementPoint(
            category=TitleReviewCategory.ENGAGEMENT,
            title="Strengthen emotional hook in subtitle",
            description="Make subtitle more emotionally compelling and less generic",
            priority="high",
            impact_score=18,
            specific_example="Current: 'A Haunting Discovery' (generic) | Needed: Specific emotional impact",
            suggested_fix="Replace with something like 'When Silence Answers Back' or 'The Sound That Never Dies'",
        )
    )

    review.improvement_points.append(
        TitleImprovementPoint(
            category=TitleReviewCategory.IDEA_ALIGNMENT,
            title="Hint at intensification",
            description="Add element that suggests the increasing intensity mentioned in the idea",
            priority="medium",
            impact_score=15,
            specific_example="Idea mentions 'increasing intensity' which isn't reflected in title",
            suggested_fix="Consider words like 'Growing', 'Rising', 'Amplified' to suggest escalation",
        )
    )

    review.improvement_points.append(
        TitleImprovementPoint(
            category=TitleReviewCategory.SEO_OPTIMIZATION,
            title="Improve keyword density",
            description="Include more searchable keywords without sacrificing creativity",
            priority="medium",
            impact_score=12,
            specific_example="Missing keywords: 'short film', 'horror story', 'psychological'",
            suggested_fix="Consider subtitle that naturally includes genre keywords",
        )
    )

    review.improvement_points.append(
        TitleImprovementPoint(
            category=TitleReviewCategory.CLARITY,
            title="Consider length optimization",
            description="Current title might be too brief for optimal engagement",
            priority="low",
            impact_score=8,
            specific_example="Current: 32 characters | Optimal range: 50-70 characters",
            suggested_fix="Expand subtitle to provide more context and intrigue",
        )
    )

    # Add strengths and concerns
    review.strengths = [
        "Clear genre identification",
        "Creates curiosity about 'echo' element",
        "Appropriate for target audience",
        "Good script-to-title alignment",
    ]

    review.primary_concern = (
        "Subtitle is generic and doesn't fully capture the unique elements of the script"
    )

    review.quick_wins = [
        "Replace generic subtitle with specific emotional hook",
        "Add reference to house/abandoned setting",
        "Include intensification keyword",
    ]

    # Display review results
    print(f"\nTitle Under Review: '{review.title_text}'")
    print(f"Version: {review.title_version}")
    print(f"\n--- OVERALL SCORE ---")
    print(f"Overall: {review.overall_score}%")
    print(f"Confidence: {review.confidence_score}%")

    print(f"\n--- ALIGNMENT SCORES ---")
    print(f"Script Alignment: {review.script_alignment_score}%")
    print(f"Idea Alignment: {review.idea_alignment_score}%")

    alignment_summary = review.get_alignment_summary()
    print(f"Average Alignment: {alignment_summary['average_alignment']}%")
    print(f"Status: {alignment_summary['alignment_status']}")
    print(f"Needs Improvement: {alignment_summary['needs_improvement']}")

    print(f"\n--- ENGAGEMENT METRICS ---")
    engagement = review.get_engagement_summary()
    print(f"Composite Engagement: {engagement['composite_score']}%")
    print(f"Clickthrough Potential: {review.clickthrough_potential}%")
    print(f"Curiosity Score: {review.curiosity_score}%")
    print(f"Expectation Accuracy: {review.expectation_accuracy}%")
    print(f"Ready for Publication: {engagement['ready_for_publication']}")

    print(f"\n--- LENGTH ASSESSMENT ---")
    length = review.get_length_assessment()
    print(f"Current Length: {length['current_length']} characters")
    print(f"Optimal Length: {length['optimal_length']} characters")
    print(f"Status: {length['status']}")
    print(f"Feedback: {length['feedback']}")

    print(f"\n--- CATEGORY SCORES ---")
    for cat_score in review.category_scores:
        print(f"\n{cat_score.category.value.upper()}: {cat_score.score}%")
        print(f"  Reasoning: {cat_score.reasoning}")
        if cat_score.strengths:
            print(f"  Strengths: {', '.join(cat_score.strengths)}")
        if cat_score.weaknesses:
            print(f"  Weaknesses: {', '.join(cat_score.weaknesses)}")

    print(f"\n--- HIGH-PRIORITY IMPROVEMENTS ---")
    high_priority = review.get_high_priority_improvements()
    for i, imp in enumerate(high_priority, 1):
        print(f"\n{i}. {imp.title} (Impact: +{imp.impact_score}%)")
        print(f"   Category: {imp.category.value}")
        print(f"   Description: {imp.description}")
        if imp.suggested_fix:
            print(f"   Suggested Fix: {imp.suggested_fix}")

    print(f"\n--- QUICK WINS ---")
    for i, win in enumerate(review.quick_wins, 1):
        print(f"{i}. {win}")

    print(f"\n--- PRIMARY CONCERN ---")
    print(f"{review.primary_concern}")

    print(f"\n--- READINESS CHECK ---")
    print(f"Ready for Improvement Stage: {review.is_ready_for_improvement()}")

    print()


def example_serialization():
    """Example: Serialization to/from dictionary."""
    print("=" * 70)
    print("Example 3: Serialization (to_dict / from_dict)")
    print("=" * 70)

    # Create a review
    original = TitleReview(
        title_id="title-003",
        title_text="The Midnight Echo",
        overall_score=82,
        script_alignment_score=85,
        idea_alignment_score=80,
    )

    original.category_scores.append(
        TitleCategoryScore(
            category=TitleReviewCategory.SCRIPT_ALIGNMENT,
            score=85,
            reasoning="Strong alignment with script",
        )
    )

    # Convert to dictionary
    data = original.to_dict()
    print("\nSerialized to dictionary:")
    print(f"  title_id: {data['title_id']}")
    print(f"  title_text: {data['title_text']}")
    print(f"  overall_score: {data['overall_score']}")
    print(f"  category_scores: {len(data['category_scores'])} scores")

    # Restore from dictionary
    restored = TitleReview.from_dict(data)
    print("\nRestored from dictionary:")
    print(f"  title_id: {restored.title_id}")
    print(f"  title_text: {restored.title_text}")
    print(f"  overall_score: {restored.overall_score}")
    print(f"  category_scores: {len(restored.category_scores)} scores")
    print(f"\nRound-trip successful: {original.title_id == restored.title_id}")
    print()


def example_workflow_integration():
    """Example: Integration with title improvement workflow."""
    print("=" * 70)
    print("Example 4: Workflow Integration (Stage 4 → Stage 6)")
    print("=" * 70)

    # Stage 4: Review title v1 against script v1 and idea
    print("\n[Stage 4: Title Review - MVP-004]")
    print("Input: Title v1 + Script v1 + Idea")

    review = TitleReview(
        title_id="title-wf-001",
        title_text="The Forgotten Voice",
        title_version="v1",
        overall_score=72,
        script_id="script-wf-001",
        script_alignment_score=78,
        idea_id="idea-wf-001",
        idea_alignment_score=75,
        engagement_score=70,
    )

    review.improvement_points.append(
        TitleImprovementPoint(
            category=TitleReviewCategory.ENGAGEMENT,
            title="Add emotional specificity",
            description="Make the emotional angle more specific",
            priority="high",
            impact_score=20,
        )
    )

    print(f"\nTitle being reviewed: '{review.title_text}'")
    print(f"Overall score: {review.overall_score}%")
    print(f"Improvement points identified: {len(review.improvement_points)}")

    # Check if ready for next stage
    if review.is_ready_for_improvement():
        print("\n✓ Review complete - ready for Stage 6 (Title Improvements v2)")
        print(f"  Script alignment: {review.script_alignment_score}%")
        print(f"  Idea alignment: {review.idea_alignment_score}%")
        print(f"  Feedback available: {len(review.improvement_points)} improvements")

        # Stage 6 would use this review to generate title v2
        print("\n[Stage 6: Title Improvements v2]")
        print("Input: Title v1 + Review Feedback + Script v1")
        print("Output: Title v2 (improved version)")
        print("Module: T/Title/From/Title/Review/Script")
    else:
        print("\n✗ Review incomplete - cannot proceed to Stage 6")

    print()


if __name__ == "__main__":
    # Run all examples
    example_basic_review()
    example_complete_review()
    example_serialization()
    example_workflow_integration()

    print("=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
