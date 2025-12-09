"""Example usage of the complete title review workflow.

This example demonstrates:
1. Reviewing a title against script and idea using the AI reviewer
2. Analyzing the feedback and scores
3. Understanding improvement recommendations
4. Working with JSON output format
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

from T.Review.Title.ByScriptAndIdea import (
    TitleReview,
    TitleReviewCategory,
    review_title_by_script_and_idea,
)


def example_complete_workflow():
    """Example: Complete AI-powered title review workflow."""
    print("=" * 80)
    print("Example 1: Complete AI Title Review Workflow")
    print("=" * 80)

    # Sample data
    title = "The Haunting Echo - A Mystery Revealed"

    script = """
    In the abandoned Victorian house on Elm Street, strange echoes fill the air.
    Every night, Sarah hears voices repeating her words moments after she speaks.
    The haunting sound grows stronger, revealing dark secrets buried in the walls.
    
    As Sarah investigates, she discovers the house's tragic past.
    Each echo brings her closer to uncovering a century-old mystery.
    The voices aren't random - they're trying to tell her something important.
    
    In a climactic revelation, Sarah realizes the echoes are messages from the past,
    warning her about a danger that still lurks in the shadows of the old house.
    """

    idea_summary = (
        "Horror mystery about mysterious echoes in an abandoned house that reveal secrets"
    )
    idea_intent = "Create suspense through auditory elements and psychological tension"
    target_audience = "Horror and mystery enthusiasts aged 18-35"

    # Perform AI review
    print("\n[AI REVIEWER ANALYZING TITLE...]")
    review = review_title_by_script_and_idea(
        title_text=title,
        script_text=script,
        idea_summary=idea_summary,
        idea_intent=idea_intent,
        target_audience=target_audience,
        title_id="title-horror-001",
        script_id="script-horror-001",
        idea_id="idea-horror-001",
    )

    print(f"\nTitle Under Review: '{review.title_text}'")
    print(f"Version: {review.title_version}")
    print("\n" + "=" * 80)

    # Overall Assessment
    print("\n📊 OVERALL ASSESSMENT")
    print(f"Overall Score: {review.overall_score}% (Confidence: {review.confidence_score}%)")
    print(
        f"Status: {'✓ APPROVED' if review.overall_score >= 80 else '⚠ NEEDS IMPROVEMENT' if review.overall_score >= 65 else '✗ MAJOR REVISION NEEDED'}"
    )
    print(f"Major Revision Required: {'Yes' if review.needs_major_revision else 'No'}")

    # Alignment Analysis
    print("\n" + "=" * 80)
    print("\n🎯 ALIGNMENT ANALYSIS")
    alignment_summary = review.get_alignment_summary()
    print(
        f"\nScript Alignment: {review.script_alignment_score}% - {alignment_summary['alignment_status'].upper()}"
    )
    print(f"Idea Alignment: {review.idea_alignment_score}%")
    print(f"Average Alignment: {alignment_summary['average_alignment']}%")
    print(f"Needs Improvement: {'Yes' if alignment_summary['needs_improvement'] else 'No'}")

    if review.key_script_elements:
        print(f"\nKey Script Elements: {', '.join(review.key_script_elements[:5])}")

    # Engagement Metrics
    print("\n" + "=" * 80)
    print("\n💡 ENGAGEMENT ANALYSIS")
    engagement = review.get_engagement_summary()
    print(f"\nComposite Engagement Score: {engagement['composite_score']}%")
    print(f"Clickthrough Potential: {review.clickthrough_potential}%")
    print(f"Curiosity Score: {review.curiosity_score}%")
    print(f"Expectation Accuracy: {review.expectation_accuracy}%")
    print(
        f"Ready for Publication: {'✓ Yes' if engagement['ready_for_publication'] else '✗ Not yet'}"
    )

    # SEO Assessment
    print("\n" + "=" * 80)
    print("\n🔍 SEO OPTIMIZATION")
    print(f"\nSEO Score: {review.seo_score}%")
    print(f"Keyword Relevance: {review.keyword_relevance}%")
    if review.suggested_keywords:
        print(f"Suggested Keywords: {', '.join(review.suggested_keywords)}")

    length_assessment = review.get_length_assessment()
    print(
        f"\nLength: {length_assessment['current_length']} chars (Optimal: {length_assessment['optimal_length']})"
    )
    print(f"Length Status: {length_assessment['status']}")
    print(f"Length Score: {review.length_score}%")

    # Category Breakdown
    print("\n" + "=" * 80)
    print("\n📋 DETAILED CATEGORY SCORES")
    for cat_score in review.category_scores:
        print(f"\n{cat_score.category.value.upper().replace('_', ' ')}: {cat_score.score}%")
        print(f"  Reasoning: {cat_score.reasoning}")
        if cat_score.strengths:
            print(f"  ✓ Strengths: {'; '.join(cat_score.strengths)}")
        if cat_score.weaknesses:
            print(f"  ✗ Weaknesses: {'; '.join(cat_score.weaknesses)}")

    # Improvement Recommendations
    print("\n" + "=" * 80)
    print("\n🔧 IMPROVEMENT RECOMMENDATIONS")

    high_priority = review.get_high_priority_improvements()
    if high_priority:
        print(f"\n🔴 HIGH PRIORITY ({len(high_priority)} items):")
        for i, imp in enumerate(high_priority, 1):
            print(f"\n  {i}. {imp.title} (Impact: +{imp.impact_score}%)")
            print(f"     Category: {imp.category.value}")
            print(f"     Issue: {imp.description}")
            if imp.suggested_fix:
                print(f"     💡 Suggestion: {imp.suggested_fix}")

    medium_priority = [imp for imp in review.improvement_points if imp.priority == "medium"]
    if medium_priority:
        print(f"\n🟡 MEDIUM PRIORITY ({len(medium_priority)} items):")
        for i, imp in enumerate(medium_priority[:3], 1):
            print(f"  {i}. {imp.title} (Impact: +{imp.impact_score}%)")

    # Quick Wins
    if review.quick_wins:
        print("\n" + "=" * 80)
        print("\n⚡ QUICK WINS - Easy High-Impact Improvements:")
        for i, win in enumerate(review.quick_wins, 1):
            print(f"  {i}. {win}")

    # Primary Concern
    if review.primary_concern:
        print("\n" + "=" * 80)
        print("\n⚠️  PRIMARY CONCERN:")
        print(f"  {review.primary_concern}")

    # Strengths
    if review.strengths:
        print("\n" + "=" * 80)
        print("\n✨ STRENGTHS:")
        for i, strength in enumerate(review.strengths, 1):
            print(f"  {i}. {strength}")

    print("\n" + "=" * 80)
    print(
        f"\n✅ Review Complete - Ready for {'Title v2 Generation' if review.is_ready_for_improvement() else 'Additional Analysis'}"
    )
    print("\n" + "=" * 80)


def example_json_output():
    """Example: JSON output for integration."""
    print("\n\n" + "=" * 80)
    print("Example 2: JSON Output Format")
    print("=" * 80)

    # Perform review
    review = review_title_by_script_and_idea(
        title_text="The Echo",
        script_text="A mysterious echo haunts an abandoned house, revealing dark secrets.",
        idea_summary="Horror story about echoes revealing secrets",
    )

    # Convert to JSON-compatible dictionary
    review_dict = review.to_dict()

    # Pretty print JSON
    print("\nJSON Output (excerpt):")
    print(
        json.dumps(
            {
                "title_id": review_dict["title_id"],
                "title_text": review_dict["title_text"],
                "overall_score": review_dict["overall_score"],
                "script_alignment_score": review_dict["script_alignment_score"],
                "idea_alignment_score": review_dict["idea_alignment_score"],
                "engagement_score": review_dict["engagement_score"],
                "seo_score": review_dict["seo_score"],
                "needs_major_revision": review_dict["needs_major_revision"],
                "category_scores_count": len(review_dict["category_scores"]),
                "improvement_points_count": len(review_dict["improvement_points"]),
            },
            indent=2,
        )
    )

    print("\n✓ Full review data can be serialized to JSON for API responses or storage")


def example_comparison():
    """Example: Comparing two titles."""
    print("\n\n" + "=" * 80)
    print("Example 3: Comparing Multiple Title Options")
    print("=" * 80)

    script = "A mysterious echo in an old house reveals dark secrets from the past."
    idea = "Horror mystery about echoes revealing secrets"

    titles = ["The Echo", "Echoes of the Past", "The Haunting Echo - Secrets Revealed"]

    print("\nComparing title options for best performance...\n")

    results = []
    for title in titles:
        review = review_title_by_script_and_idea(
            title_text=title, script_text=script, idea_summary=idea
        )
        results.append((title, review))

    # Display comparison
    print(f"{'Title':<40} {'Overall':<8} {'Script':<8} {'Idea':<8} {'Engage':<8}")
    print("-" * 80)

    for title, review in results:
        print(
            f"{title:<40} {review.overall_score:<8} {review.script_alignment_score:<8} "
            f"{review.idea_alignment_score:<8} {review.engagement_score:<8}"
        )

    # Find best
    best = max(results, key=lambda x: x[1].overall_score)
    print(f"\n✓ Best Title: '{best[0]}' with {best[1].overall_score}% overall score")


def example_iterative_improvement():
    """Example: Iterative improvement workflow."""
    print("\n\n" + "=" * 80)
    print("Example 4: Iterative Improvement Workflow")
    print("=" * 80)

    script = """
    In the abandoned house, mysterious echoes reveal dark secrets.
    Each sound brings Sarah closer to uncovering the truth.
    The echoes hold the key to a century-old mystery.
    """

    idea = "Horror mystery using auditory suspense to reveal secrets"

    # Iteration 1
    print("\n[Iteration 1: Initial Title]")
    title_v1 = "A House Story"
    review_v1 = review_title_by_script_and_idea(
        title_text=title_v1, script_text=script, idea_summary=idea
    )
    print(f"Title: '{title_v1}'")
    print(f"Score: {review_v1.overall_score}%")
    print(f"Top Issue: {review_v1.primary_concern}")

    # Iteration 2 (hypothetical improvement based on feedback)
    print("\n[Iteration 2: After Improvements]")
    title_v2 = "The Echo Mystery"
    review_v2 = review_title_by_script_and_idea(
        title_text=title_v2, script_text=script, idea_summary=idea
    )
    print(f"Title: '{title_v2}'")
    print(f"Score: {review_v2.overall_score}%")
    print(f"Improvement: +{review_v2.overall_score - review_v1.overall_score}%")

    # Iteration 3
    print("\n[Iteration 3: Further Refinement]")
    title_v3 = "The Echoing Secrets: Mystery in the Abandoned House"
    review_v3 = review_title_by_script_and_idea(
        title_text=title_v3, script_text=script, idea_summary=idea
    )
    print(f"Title: '{title_v3}'")
    print(f"Score: {review_v3.overall_score}%")
    print(f"Total Improvement: +{review_v3.overall_score - review_v1.overall_score}%")

    print(
        f"\n✓ {'Approved!' if review_v3.overall_score >= 80 else 'Continue iterating for 80%+ score'}"
    )


if __name__ == "__main__":
    # Run all examples
    example_complete_workflow()
    example_json_output()
    example_comparison()
    example_iterative_improvement()

    print("\n\n" + "=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)
