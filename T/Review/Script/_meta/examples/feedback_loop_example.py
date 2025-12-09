"""Example: Complete AI Script Review and Writer Feedback Loop

This example demonstrates the complete feedback loop between AI Script Reviewer
and AI Script Writer for optimizing content for YouTube shorts.

Workflow:
1. AI Reviewer evaluates original script
2. AI Writer optimizes based on review feedback
3. Loop continues until target score reached (80%+)
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from T.Review.Script import (
    CategoryScore,
    ContentLength,
    ImprovementPoint,
    ReviewCategory,
    ScriptReview,
)
from T.Script import OptimizationStrategy, ScriptWriter


def create_mock_review(script_text: str, iteration: int) -> ScriptReview:
    """Create a mock review (simulates AI Reviewer evaluation).

    In production, this would be replaced with actual AI model.
    """
    # Simulate score improvement with each iteration
    base_score = 65
    score = min(100, base_score + (iteration * 10))

    review = ScriptReview(
        script_id=f"script-youtube-short-{iteration}",
        script_title="The Echo - Horror Short",
        overall_score=score,
        target_audience="Horror enthusiasts aged 18-35",
        audience_alignment_score=85,
        target_length=ContentLength.YOUTUBE_SHORT_EXTENDED,
        current_length_seconds=145 - (iteration * 20),  # Gets shorter
        optimal_length_seconds=90,
        is_youtube_short=True,
        hook_strength_score=95,
        retention_score=68 + (iteration * 8),
        viral_potential_score=78 + (iteration * 5),
        needs_major_revision=(iteration == 1 and score < 70),
        iteration_number=iteration,
        reviewer_id="AI-ScriptReviewer-001",
        confidence_score=85 + (iteration * 3),
    )

    # Add category scores
    review.category_scores = [
        CategoryScore(
            category=ReviewCategory.ENGAGEMENT,
            score=85 + (iteration * 5),
            reasoning=(
                "Strong hook, pacing needs work" if iteration == 1 else "Excellent engagement"
            ),
            strengths=["Compelling opening", "Emotional impact"],
            weaknesses=["Mid-section drag"] if iteration == 1 else [],
        ),
        CategoryScore(
            category=ReviewCategory.PACING,
            score=60 + (iteration * 10),
            reasoning="Too slow in middle" if iteration == 1 else "Good rhythm",
            strengths=["Strong start"],
            weaknesses=["Investigation sequence too long"] if iteration < 3 else [],
        ),
        CategoryScore(
            category=ReviewCategory.YOUTUBE_SHORT_OPTIMIZATION,
            score=70 + (iteration * 10),
            reasoning="Length needs reduction" if iteration == 1 else "Well optimized for shorts",
            strengths=["Good hook for shorts"],
            weaknesses=["Too long for optimal retention"] if iteration < 2 else [],
        ),
    ]

    # Add improvement points (fewer with each iteration)
    if iteration == 1:
        review.improvement_points = [
            ImprovementPoint(
                category=ReviewCategory.PACING,
                title="Reduce middle section length",
                description="Cut 30-40 seconds from investigation sequence",
                priority="high",
                impact_score=25,
                specific_example="Investigation has 5 moments, feels slow",
                suggested_fix="Focus on 2-3 key moments instead of 5",
            ),
            ImprovementPoint(
                category=ReviewCategory.YOUTUBE_SHORT_OPTIMIZATION,
                title="Optimize opening for YouTube shorts",
                description="First 3 seconds need stronger hook for retention",
                priority="high",
                impact_score=20,
                specific_example="Current: 'A girl wakes up...' (slow start)",
                suggested_fix="Start with the voice: 'Wake up...' (immediate tension)",
            ),
            ImprovementPoint(
                category=ReviewCategory.STRUCTURE,
                title="Faster build to climax",
                description="Compress the revelation sequence",
                priority="medium",
                impact_score=15,
                specific_example="Revelation takes 30 seconds",
                suggested_fix="Cut to 15 seconds with visual cues",
            ),
        ]

        review.strengths = [
            "Compelling premise",
            "Strong emotional hook",
            "Clear horror atmosphere",
        ]
        review.primary_concern = (
            "Length optimization for YouTube shorts (currently 145s, target 90s)"
        )
        review.quick_wins = [
            "Cut 20s from investigation sequence",
            "Start with voice calling name",
            "Remove explanatory dialogue",
        ]

    elif iteration == 2:
        review.improvement_points = [
            ImprovementPoint(
                category=ReviewCategory.PACING,
                title="Minor pacing adjustment",
                description="Slightly tighten the climax sequence",
                priority="medium",
                impact_score=10,
                suggested_fix="Reduce climax by 5-10 seconds",
            )
        ]

        review.strengths = [
            "Great opening hook",
            "Well-paced overall",
            "Strong emotional impact",
            "Good length for YouTube shorts",
        ]
        review.primary_concern = "Minor pacing refinement needed"
        review.quick_wins = ["Tighten climax by 5 seconds"]

    else:  # iteration 3+
        review.improvement_points = []
        review.strengths = [
            "Perfect opening hook",
            "Excellent pacing",
            "Strong emotional impact",
            "Optimal length for YouTube shorts",
            "High viral potential",
        ]
        review.primary_concern = ""
        review.quick_wins = []

    review.notes = f"Iteration {iteration} evaluation complete"

    return review


def example_complete_feedback_loop():
    """Demonstrate complete feedback loop."""
    print("=" * 80)
    print("AI SCRIPT REVIEW & WRITER FEEDBACK LOOP - YouTube Short Optimization")
    print("=" * 80)

    # Original script
    original_script = """
    A girl wakes up at 3 AM to a voice calling her name. 
    
    The voice sounds exactly like her own. She investigates her apartment,
    checking each room carefully. The voice continues, warning her about
    things that haven't happened yet.
    
    She finds nothing but the voice persists. It warns about an accident
    at the coffee shop - and it happens exactly as predicted. The voice
    says "run NOW" but she hesitates, trying to understand.
    
    In the mirror, she sees herself - but the reflection moves differently,
    mouthing the words she's been hearing. She realizes she's already dead,
    trying to warn her past self. But it's too late.
    
    [Original length: 145 seconds]
    """

    print(f"\n📝 ORIGINAL SCRIPT:")
    print(f"Length: 145 seconds (target: 90 seconds for YouTube short)")
    print(f"Content: {original_script[:100]}...")

    # Initialize writer
    writer = ScriptWriter(
        writer_id="AI-Writer-YouTubeShort-001",
        target_score_threshold=80,
        max_iterations=3,
        optimization_strategy=OptimizationStrategy.YOUTUBE_SHORT,
    )

    current_script = original_script

    # Feedback loop
    print("\n" + "=" * 80)
    print("FEEDBACK LOOP ITERATIONS")
    print("=" * 80)

    while writer.should_continue_iteration():
        iteration = writer.current_iteration + 1

        print(f"\n{'─' * 80}")
        print(f"📊 ITERATION {iteration}")
        print(f"{'─' * 80}")

        # 1. AI REVIEWER evaluates
        print(f"\n🔍 AI REVIEWER: Evaluating script...")
        review = create_mock_review(current_script, iteration)

        print(f"\n   Overall Score: {review.overall_score}%")
        print(
            f"   Length: {review.current_length_seconds}s (target: {review.optimal_length_seconds}s)"
        )
        print(f"   Hook Strength: {review.hook_strength_score}%")
        print(f"   Retention Score: {review.retention_score}%")
        print(f"   Viral Potential: {review.viral_potential_score}%")

        print(f"\n   Category Scores:")
        for cat_score in review.category_scores:
            print(f"   - {cat_score.category.value}: {cat_score.score}% - {cat_score.reasoning}")

        if review.improvement_points:
            print(
                f"\n   🎯 High Priority Improvements ({len(review.get_high_priority_improvements())}):"
            )
            for imp in review.get_high_priority_improvements():
                print(f"   - {imp.title} (impact: +{imp.impact_score}%)")
                print(f"     Fix: {imp.suggested_fix}")

        if review.quick_wins:
            print(f"\n   ⚡ Quick Wins:")
            for win in review.quick_wins:
                print(f"   - {win}")

        # Check YouTube short readiness
        readiness = review.get_youtube_short_readiness()
        print(f"\n   YouTube Short Readiness:")
        print(f"   - Ready: {'✓' if readiness['ready'] else '✗'}")
        print(f"   - Readiness Score: {readiness['readiness_score']}%")
        print(f"   - {readiness['length_feedback']}")

        # 2. AI WRITER optimizes
        print(f"\n✍️  AI WRITER: Optimizing based on feedback...")
        result = writer.optimize_from_review(
            original_script=current_script,
            review=review,
            target_audience="Horror enthusiasts aged 18-35",
        )

        print(f"\n   Strategy: {result.optimization_strategy.value}")
        print(f"   Changes Applied ({len(result.changes_made)}):")
        for change in result.changes_made[:5]:  # Show first 5
            print(f"   - {change}")

        if len(result.changes_made) > 5:
            print(f"   ... and {len(result.changes_made) - 5} more")

        print(f"\n   Expected Score Improvement: +{result.estimated_score_improvement}%")
        print(
            f"   Expected New Score: {review.overall_score + result.estimated_score_improvement}%"
        )

        # Update current script (in production, this would be the actual optimized text)
        current_script = result.optimized_text

        # Check if should continue
        if not writer.should_continue_iteration():
            print(f"\n{'─' * 80}")
            if review.overall_score >= writer.target_score_threshold:
                print(
                    f"✓ TARGET SCORE REACHED ({review.overall_score}% >= {writer.target_score_threshold}%)"
                )
            elif writer.current_iteration >= writer.max_iterations:
                print(
                    f"✓ MAX ITERATIONS REACHED ({writer.current_iteration}/{writer.max_iterations})"
                )
            else:
                print(f"✓ STOPPING: Diminishing returns detected")
            print(f"{'─' * 80}")
            break

    # Final summary
    print("\n" + "=" * 80)
    print("FEEDBACK LOOP SUMMARY")
    print("=" * 80)

    summary = writer.get_feedback_loop_summary()

    print(f"\n📈 Progress:")
    print(f"   Initial Score: {summary['initial_score']}%")
    print(f"   Final Score: {summary['current_score']}%")
    print(f"   Total Improvement: +{summary['total_improvement']}%")
    print(f"   Iterations: {summary['current_iteration']}/{summary['max_iterations']}")

    print(f"\n📊 Score Progression:")
    print(f"   {' → '.join(str(s) + '%' for s in summary['score_progression'])}")

    print(f"\n✨ Key Improvements Applied ({summary['improvements_applied']}):")
    for improvement in writer.cumulative_improvements[:5]:
        print(f"   - {improvement}")

    print(f"\n🎯 Focus Areas:")
    for area in summary["focus_areas"][:5]:
        print(f"   - {area}")

    print(f"\n⚙️  Configuration:")
    print(f"   Strategy: {summary['optimization_strategy']}")
    print(f"   YouTube Short Mode: {'✓' if summary['youtube_short_mode'] else '✗'}")
    print(f"   Target Audience: {summary['target_audience']}")
    print(f"   Target Reached: {'✓' if summary['target_reached'] else '✗'}")

    print("\n" + "=" * 80)
    print("FEEDBACK LOOP COMPLETE")
    print("=" * 80)


def main():
    """Run the example."""
    example_complete_feedback_loop()


if __name__ == "__main__":
    main()
