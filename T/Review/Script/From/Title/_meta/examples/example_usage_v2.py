"""Example usage of PrismQ.T.Review.Script.ByTitle v2 module.

This example demonstrates how to use the v2 review functionality to:
1. Review script v2 against title v3
2. Compare improvements from v1 to v2
3. Track regression and improvements
4. Generate next steps for refinement
"""

import os
import sys
from pathlib import Path

# Add paths for imports
_example_dir = Path(__file__).parent
_repo_root = _example_dir.parent.parent.parent.parent.parent.parent
_idea_model = _repo_root / "T" / "Idea" / "Model"

sys.path.insert(0, str(_repo_root))
sys.path.insert(0, str(_idea_model))

from src.idea import ContentGenre, Idea
from T.Review.Script.ByTitle.by_title_v2 import (
    compare_reviews,
    extract_improvements_from_review,
    get_next_steps,
    is_ready_to_proceed,
    review_script_by_title_v2,
)

# Now we can import
from T.Review.Script.ByTitle.script_review_by_title import review_script_by_title


def main():
    """Demonstrate v2 review workflow."""

    print("=" * 80)
    print("PrismQ.T.Review.Script.ByTitle v2 - Example Usage")
    print("=" * 80)
    print()

    # Step 1: Create an idea
    print("Step 1: Create an idea")
    print("-" * 80)
    idea = Idea(
        title="The Echo",
        concept="A girl hears her own future voice warning her",
        premise="A teenage girl discovers she can hear warnings from her future self through an old radio",
        hook="What if you could hear your own voice... from tomorrow?",
        genre=ContentGenre.HORROR,
        target_audience="Young adults interested in psychological horror",
        target_platforms=["youtube"],
        length_target="90 seconds",
    )
    print(f"Idea: {idea.title}")
    print(f"Concept: {idea.concept}")
    print()

    # Step 2: Initial versions (v1)
    print("Step 2: Create v1 script and title")
    print("-" * 80)
    title_v1 = "The Voice"
    script_v1 = """
    Last night I heard a whisper through my grandmother's old radio.
    At first, I thought it was just static.
    """
    print(f"Title v1: {title_v1}")
    print(f"Script v1 (excerpt): {script_v1[:100]}...")
    print()

    # Step 3: Review v1
    print("Step 3: Review script v1 against title v1")
    print("-" * 80)
    v1_review = review_script_by_title(script_v1, title_v1, idea)
    print(f"V1 Overall Score: {v1_review.overall_score}%")
    print(f"V1 Title Alignment: {v1_review.metadata['title_alignment_score']}%")
    print(f"V1 Idea Alignment: {v1_review.metadata['idea_alignment_score']}%")
    print(f"V1 Needs Major Revision: {v1_review.needs_major_revision}")
    print()

    # Step 4: Improved versions (v2 script, v3 title)
    print("Step 4: Create improved versions")
    print("-" * 80)
    title_v3 = "The Voice That Knows Tomorrow - An Echo from the Future"
    script_v2 = """
    Last night I heard a whisper through my grandmother's old radio.
    
    At first, I thought it was just static, but then I recognized the voice.
    It was mine. But the words... they were warning me about tomorrow.
    
    "Don't trust him," my own voice said. "The echo knows what's coming."
    
    I'm scared. I'm terrified. Because tomorrow is here, and I don't know
    who to trust anymore. The future voice was right about everything.
    
    Now I understand - the echo isn't just a warning. It's a curse.
    """
    print(f"Title v3: {title_v3}")
    print(f"Script v2: Expanded with more detail and emotional depth")
    print()

    # Step 5: Review v2
    print("Step 5: Review script v2 against title v3 (with comparison)")
    print("-" * 80)
    v2_review = review_script_by_title_v2(
        script_text=script_v2,
        title=title_v3,
        idea=idea,
        script_version="v2",
        title_version="v3",
        previous_review=v1_review,
    )
    print(f"V2 Overall Score: {v2_review.overall_score}%")
    print(f"V2 Title Alignment: {v2_review.metadata['title_alignment_score']}%")
    print(f"V2 Idea Alignment: {v2_review.metadata['idea_alignment_score']}%")
    print(f"V2 Needs Major Revision: {v2_review.needs_major_revision}")
    print()

    # Step 6: Analyze improvements
    print("Step 6: Analyze improvements from v1 to v2")
    print("-" * 80)
    comparisons = compare_reviews(v1_review, v2_review)

    improvements = [c for c in comparisons if c.improved]
    regressions = [c for c in comparisons if c.regression]
    maintained = [c for c in comparisons if c.maintained]

    print(f"Improvements: {len(improvements)}")
    for imp in improvements[:5]:
        print(
            f"  ✓ {imp.category}: {imp.v1_score}% → {imp.v2_score}% (+{imp.delta}%) - {imp.feedback}"
        )
    print()

    if regressions:
        print(f"Regressions: {len(regressions)}")
        for reg in regressions:
            print(
                f"  ✗ {reg.category}: {reg.v1_score}% → {reg.v2_score}% ({reg.delta}%) - {reg.feedback}"
            )
        print()

    print(f"Maintained: {len(maintained)}")
    for maint in maintained[:3]:
        print(f"  = {maint.category}: {maint.v1_score}% → {maint.v2_score}% - {maint.feedback}")
    print()

    # Step 7: Extract improvements
    print("Step 7: Extract high-priority improvements")
    print("-" * 80)
    improvements_list = extract_improvements_from_review(v2_review)
    for i, imp in enumerate(improvements_list[:5], 1):
        print(f"{i}. {imp}")
    print()

    # Step 8: Check readiness
    print("Step 8: Check if ready to proceed")
    print("-" * 80)
    ready = is_ready_to_proceed(v2_review, threshold=80)
    print(f"Ready to proceed (threshold=80): {ready}")
    print()

    # Step 9: Get next steps
    print("Step 9: Get recommended next steps")
    print("-" * 80)
    steps = get_next_steps(v2_review)
    for i, step in enumerate(steps, 1):
        print(f"{i}. {step}")
    print()

    # Step 10: JSON output
    print("Step 10: JSON output format")
    print("-" * 80)
    review_dict = v2_review.to_dict()
    print(f"JSON fields available: {', '.join(review_dict.keys())}")
    print()
    print("Metadata:")
    for key, value in v2_review.metadata.items():
        if not key.startswith("_"):
            print(f"  {key}: {value}")
    print()

    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    score_change = v2_review.overall_score - v1_review.overall_score
    print(
        f"Overall Score Change: {v1_review.overall_score}% → {v2_review.overall_score}% ({score_change:+d}%)"
    )

    if score_change > 0:
        print(f"✓ Script improved by {score_change}%")
    elif score_change < 0:
        print(f"✗ Script regressed by {abs(score_change)}%")
    else:
        print("= Script quality maintained")

    if v2_review.overall_score >= 80:
        print("✓ Script ready for acceptance check")
    elif v2_review.overall_score >= 60:
        print("⚠ Script needs minor improvements")
    else:
        print("✗ Script needs major revision")

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
