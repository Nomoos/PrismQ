"""Example: Script Versioning for Comparison and Research

This example demonstrates how to use script versioning to:
- Store each iteration's script text
- Compare versions side-by-side
- Track what changed between iterations
- Research feedback loop effectiveness
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from T.Script.Review import (
    ScriptReview,
    ScriptVersion,
    ReviewCategory,
    ContentLength,
    ImprovementPoint
)
from T.Script.Writer import ScriptWriter


def example_version_tracking():
    """Demonstrate version tracking and comparison."""
    print("=" * 80)
    print("SCRIPT VERSIONING - Tracking Changes Across Iterations")
    print("=" * 80)
    
    # Initial script
    script_v1 = """
    A girl wakes up at 3 AM to a voice calling her name. 
    
    The voice sounds exactly like her own. She investigates her apartment,
    checking each room carefully - the bedroom, bathroom, living room, kitchen,
    and hallway. The voice continues, warning her about things that haven't 
    happened yet.
    
    She finds nothing but the voice persists. It warns about an accident
    at the coffee shop tomorrow morning - and when she goes there, it happens 
    exactly as predicted. The voice says "run NOW" but she hesitates, trying 
    to understand what's happening and where the voice is coming from.
    
    In the mirror, she sees herself - but the reflection moves differently,
    mouthing the words she's been hearing. She realizes with horror that she's 
    already dead, trying to warn her past self. But it's too late to change 
    the outcome.
    
    [Length: ~145 seconds]
    """
    
    print("\n📝 VERSION 1: Original Script")
    print("─" * 80)
    print(f"Length: 145 seconds")
    print(f"Content preview: {script_v1[:100]}...")
    
    # Create review for V1
    review_v1 = ScriptReview(
        script_id="script-echo-001",
        script_title="The Echo",
        overall_score=68,
        is_youtube_short=True,
        target_length=ContentLength.YOUTUBE_SHORT_EXTENDED,
        current_length_seconds=145,
        optimal_length_seconds=90
    )
    
    # Store V1 in review
    review_v1.add_script_version(
        script_text=script_v1,
        length_seconds=145,
        created_by="Human-Writer",
        changes_from_previous="Initial version"
    )
    
    print(f"\n✓ Version 1 stored in review")
    print(f"  Score: {review_v1.overall_score}%")
    
    # Iteration 1: AI Writer optimizes
    print("\n✍️  AI WRITER: Optimizing based on feedback...")
    writer = ScriptWriter(target_score_threshold=80)
    
    review_v1.improvement_points.append(ImprovementPoint(
        category=ReviewCategory.PACING,
        title="Drastically reduce investigation sequence",
        description="Cut investigation from 45s to 15s",
        priority="high",
        impact_score=30,
        suggested_fix="Show investigation with quick visual montage"
    ))
    
    result1 = writer.optimize_from_review(script_v1, review_v1)
    
    script_v2 = """
    "Wake up." The voice sounds exactly like her own.
    
    3 AM. She checks each room - nothing. The voice continues, warning about 
    an accident at the coffee shop. It happens exactly as warned.
    
    "Run NOW" the voice says. In the mirror, she sees herself - but the 
    reflection moves differently, mouthing the words. She's already dead, 
    trying to warn her past self.
    
    [Length: ~105 seconds]
    """
    
    print(f"\n📝 VERSION 2: After First Optimization")
    print("─" * 80)
    print(f"Length: 105 seconds (-40s from V1)")
    print(f"Content preview: {script_v2[:100]}...")
    print(f"Changes: {len(result1.changes_made)} improvements applied")
    
    # Create review for V2
    review_v2 = ScriptReview(
        script_id="script-echo-001",
        script_title="The Echo",
        overall_score=80,
        is_youtube_short=True,
        target_length=ContentLength.YOUTUBE_SHORT_EXTENDED,
        current_length_seconds=105,
        optimal_length_seconds=90
    )
    
    # Store V2
    review_v2.add_script_version(
        script_text=script_v2,
        length_seconds=105,
        created_by="AI-Writer-001",
        changes_from_previous="Reduced investigation sequence, stronger opening"
    )
    
    print(f"\n✓ Version 2 stored")
    print(f"  Score: {review_v2.overall_score}% (+{review_v2.overall_score - review_v1.overall_score}%)")
    
    # Iteration 2: Further optimization
    result2 = writer.optimize_from_review(script_v2, review_v2)
    
    script_v3 = """
    "Wake up." Her own voice echoes. 3 AM.
    
    Quick check: empty rooms. Voice warns: coffee shop accident. It happens.
    
    "Run NOW." Mirror reflection moves wrong - mouthing her words. Already dead.
    Warning her past self.
    
    [Length: ~75 seconds]
    """
    
    print(f"\n📝 VERSION 3: Final Optimization")
    print("─" * 80)
    print(f"Length: 75 seconds (-30s from V2)")
    print(f"Content preview: {script_v3[:80]}...")
    
    # Store V3
    review_v3 = ScriptReview(
        script_id="script-echo-001",
        script_title="The Echo",
        overall_score=88,
        is_youtube_short=True,
        target_length=ContentLength.YOUTUBE_SHORT,
        current_length_seconds=75,
        optimal_length_seconds=75
    )
    
    review_v3.add_script_version(
        script_text=script_v3,
        length_seconds=75,
        created_by="AI-Writer-001",
        changes_from_previous="Ultra-compressed for YouTube shorts, removed all padding"
    )
    
    print(f"\n✓ Version 3 stored")
    print(f"  Score: {review_v3.overall_score}% (+{review_v3.overall_score - review_v2.overall_score}%)")
    
    # Combine all versions for comparison
    all_reviews = [review_v1, review_v2, review_v3]
    all_versions = []
    for review in all_reviews:
        all_versions.extend(review.script_versions_history)
    
    # Show comparison
    print("\n" + "=" * 80)
    print("VERSION COMPARISON & RESEARCH")
    print("=" * 80)
    
    print("\n📊 Version Progression:")
    print("─" * 80)
    print(f"{'Version':<10} {'Length':<12} {'Score':<10} {'Changes':<50}")
    print("─" * 80)
    for v in all_versions:
        print(f"V{v.version_number:<9} {str(v.length_seconds)+'s':<12} {str(v.review_score)+'%':<10} {v.changes_from_previous[:47]:<50}")
    
    print("\n📈 Improvements Over Time:")
    print("─" * 80)
    first = all_versions[0]
    latest = all_versions[-1]
    
    length_reduction = first.length_seconds - latest.length_seconds
    length_pct = (length_reduction / first.length_seconds) * 100
    score_improvement = latest.review_score - first.review_score
    
    print(f"  Length: {first.length_seconds}s → {latest.length_seconds}s (-{length_reduction}s, -{length_pct:.1f}%)")
    print(f"  Score: {first.review_score}% → {latest.review_score}% (+{score_improvement}%)")
    print(f"  Iterations: {len(all_versions) - 1}")
    print(f"  Total changes: {len(all_versions)} versions created")
    
    print("\n🔬 Research Value:")
    print("─" * 80)
    print("  ✓ Complete history of all script iterations")
    print("  ✓ Side-by-side comparison capability")
    print("  ✓ Track effectiveness of each change")
    print("  ✓ Measure feedback loop performance")
    print("  ✓ Analyze what optimizations work best")
    
    # Writer's version comparison
    print("\n📋 Writer's Version Tracking:")
    print("─" * 80)
    comparison = writer.get_version_comparison()
    if comparison["comparison_available"]:
        print(f"  Versions stored: {comparison['versions_count']}")
        print(f"  Score improvement: +{comparison['summary']['score_improvement']}%")
        print(f"  Length change: {comparison['summary']['length_change_seconds']}s")
        print(f"  Total changes: {comparison['summary']['total_changes']}")
    
    print("\n" + "=" * 80)
    print("VERSIONING COMPLETE - Ready for Research & Analysis")
    print("=" * 80)
    
    return all_versions, writer


def main():
    """Run the example."""
    versions, writer = example_version_tracking()
    
    print("\n💡 USE CASES:")
    print("  1. Compare any two versions side-by-side")
    print("  2. Analyze which changes had most impact")
    print("  3. Research optimal iteration count")
    print("  4. Study feedback loop convergence patterns")
    print("  5. Export version history for external analysis")


if __name__ == "__main__":
    main()
