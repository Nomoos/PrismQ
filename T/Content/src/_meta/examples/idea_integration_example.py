"""Example: Integration with Idea Model

Shows how the AI Content Review and Writer feedback loop integrates
with the existing PrismQ Idea workflow.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "T", "Idea", "Model")
)

from src.idea import ContentGenre, Idea, IdeaStatus
from T.Review.Content import (
    CategoryScore,
    ContentLength,
    ImprovementPoint,
    ReviewCategory,
    ScriptReview,
)
from T.Content import OptimizationStrategy, ScriptWriter


def example_idea_to_content_workflow():
    """Demonstrate complete workflow from Idea to approved script."""
    print("=" * 80)
    print("PRISMQ IDEA → SCRIPT WORKFLOW WITH AI FEEDBACK LOOP")
    print("=" * 80)

    # 1. Create an Idea for YouTube short horror content
    print("\n📋 STEP 1: Create Idea for YouTube Short")
    print("─" * 80)

    idea = Idea(
        title="The Echo",
        concept="A girl hears a voice that sounds exactly like her own",
        premise="A teenage girl starts hearing a voice that sounds identical to her own, "
        "giving her warnings about the future. When the warnings come true, "
        "she realizes the voice is her future self trying to prevent her death.",
        logline="A girl discovers she can hear her own future thoughts—and they're telling her to run.",
        hook="Last night I woke up... but my body kept sleeping.",
        skeleton="1. Girl hears strange voice\n2. Voice sounds like her\n3. Voice predicts events\n"
        "4. Predictions come true\n5. Final warning: run now\n6. She realizes too late",
        target_platforms=["tiktok", "youtube", "instagram"],
        target_formats=["video"],
        genre=ContentGenre.HORROR,
        length_target="60-90 seconds video",
        tone_guidance="Start mysterious, build to terrifying, end with shocking twist",
        status=IdeaStatus.SCRIPT_DRAFT,
    )

    print(f"✓ Idea created: {idea.title}")
    print(f"  Genre: {idea.genre.value}")
    print(f"  Platforms: {', '.join(idea.target_platforms)}")
    print(f"  Target length: {idea.length_target}")
    print(f"  Status: {idea.status.value}")

    # 2. Create initial script draft
    print("\n📝 STEP 2: Create Initial Content Draft")
    print("─" * 80)

    initial_content = """
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
    
    [Length: ~145 seconds]
    """

    print(f"✓ Initial draft created")
    print(f"  Estimated length: 145 seconds")
    print(f"  Target length: 60-90 seconds")

    # Update Idea status
    idea.status = IdeaStatus.SCRIPT_REVIEW
    print(f"  Idea status updated: {idea.status.value}")

    # 3. AI Reviewer evaluates
    print("\n🔍 STEP 3: AI Reviewer Evaluation")
    print("─" * 80)

    review = ScriptReview(
        content_id=f"script-{idea.title}",
        script_title=idea.title,
        overall_score=68,
        target_audience="Horror enthusiasts aged 18-35",
        audience_alignment_score=85,
        target_length=ContentLength.YOUTUBE_SHORT_EXTENDED,
        current_length_seconds=145,
        optimal_length_seconds=75,  # Tighter for TikTok/Shorts
        is_youtube_short=True,
        hook_strength_score=90,
        retention_score=65,
        viral_potential_score=75,
        needs_major_revision=False,
        iteration_number=1,
    )

    # Add evaluation details
    review.category_scores.append(
        CategoryScore(
            category=ReviewCategory.ENGAGEMENT,
            score=85,
            reasoning="Strong premise and hook, but middle drags",
            strengths=["Compelling premise", "Great twist ending"],
            weaknesses=["Investigation sequence too detailed"],
        )
    )

    review.category_scores.append(
        CategoryScore(
            category=ReviewCategory.PACING,
            score=60,
            reasoning="Too slow in middle section",
            strengths=["Good opening", "Strong climax"],
            weaknesses=["Middle investigation takes too long", "Hesitation scene unnecessary"],
        )
    )

    review.improvement_points.append(
        ImprovementPoint(
            category=ReviewCategory.PACING,
            title="Drastically reduce investigation sequence",
            description="Cut investigation from 45s to 15s",
            priority="high",
            impact_score=30,
            suggested_fix="Show investigation with quick visual montage, not detailed exploration",
        )
    )

    review.improvement_points.append(
        ImprovementPoint(
            category=ReviewCategory.YOUTUBE_SHORT_OPTIMIZATION,
            title="Start with immediate tension",
            description="Open with the voice, not the waking up",
            priority="high",
            impact_score=20,
            suggested_fix="First line: Voice saying her name in her own voice",
        )
    )

    print(f"✓ Review complete")
    print(f"  Overall score: {review.overall_score}%")
    print(f"  High-priority improvements: {len(review.get_high_priority_improvements())}")
    print(f"  Needs major revision: {review.needs_major_revision}")

    # 4. AI Writer optimizes
    print("\n✍️  STEP 4: AI Writer Optimization")
    print("─" * 80)

    writer = ScriptWriter(
        target_score_threshold=80,
        max_iterations=3,
        optimization_strategy=OptimizationStrategy.YOUTUBE_SHORT,
    )

    result = writer.optimize_from_review(
        original_content=initial_content,
        review=review,
        target_audience="Horror fans 18-35 on TikTok/YouTube Shorts",
    )

    print(f"✓ Optimization complete")
    print(f"  Changes applied: {len(result.changes_made)}")
    print(f"  Expected improvement: +{result.estimated_score_improvement}%")
    print(f"  Length: {result.length_before_seconds}s → {result.length_after_seconds}s")

    # 5. Check if approved
    print("\n✅ STEP 5: Approval Check")
    print("─" * 80)

    # In real implementation, would re-review the optimized script
    estimated_new_score = review.overall_score + result.estimated_score_improvement

    if estimated_new_score >= writer.target_score_threshold:
        idea.status = IdeaStatus.SCRIPT_APPROVED
        print(f"✓ SCRIPT APPROVED!")
        print(f"  Final score: {estimated_new_score}%")
        print(f"  Status updated: {idea.status.value}")
    else:
        print(f"✗ Additional iteration needed")
        print(f"  Current score: {estimated_new_score}%")
        print(f"  Target: {writer.target_score_threshold}%")

    # 6. Show workflow progression
    print("\n📊 WORKFLOW PROGRESSION")
    print("─" * 80)

    print(
        f"""
    IdeaInspiration → Idea ({IdeaStatus.IDEA.value})
        ↓
    Outline/Skeleton → ({IdeaStatus.OUTLINE.value})
        ↓
    Content Draft → ({IdeaStatus.SCRIPT_DRAFT.value})
        ↓
    AI Review → ({IdeaStatus.SCRIPT_REVIEW.value})
        ↓
    AI Writer Optimization
        ↓
    Content Approved → ({IdeaStatus.SCRIPT_APPROVED.value}) ← YOU ARE HERE
        ↓
    Text Publishing → ({IdeaStatus.TEXT_PUBLISHING.value})
        ↓
    Published Text → ({IdeaStatus.TEXT_PUBLISHED.value})
    """
    )

    print("\n" + "=" * 80)
    print("WORKFLOW COMPLETE - Ready for Text Publishing")
    print("=" * 80)

    return idea, review, writer


def main():
    """Run the example."""
    idea, review, writer = example_idea_to_content_workflow()

    print("\n💡 NEXT STEPS:")
    print("  1. Publish as text content (blog, Medium, LinkedIn)")
    print("  2. Generate voiceover from published text")
    print("  3. Create video from audio + visuals")
    print("  4. Publish to TikTok/YouTube Shorts")


if __name__ == "__main__":
    main()
