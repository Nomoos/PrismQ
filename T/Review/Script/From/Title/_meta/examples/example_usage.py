"""Example usage of PrismQ.T.Review.Content.ByTitle module.

This example demonstrates how to review scripts against titles and ideas
to get structured feedback with JSON output.
"""

import json
import sys
from pathlib import Path

# Add paths for imports
_example_dir = Path(__file__).parent
_repo_root = _example_dir.parent.parent.parent.parent.parent.parent
_idea_model = _repo_root / "T" / "Idea" / "Model"

sys.path.insert(0, str(_repo_root))
sys.path.insert(0, str(_idea_model))

from src.idea import ContentGenre, Idea

# Now we can import
from T.Review.Content.ByTitle.script_review_by_title import review_content_by_title


def example_basic_review():
    """Basic script review example."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Content Review")
    print("=" * 60)

    # Create an idea
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

    # Define title and script
    title = "The Voice That Knows Tomorrow"
    script = """
    Last night I heard a whisper through my grandmother's old radio.
    
    At first, I thought it was just static, but then I recognized the voice.
    It was mine. But the words... they were warning me about tomorrow.
    
    "Don't trust him," my own voice said. "The echo knows what's coming."
    
    I'm scared. I'm terrified. Because tomorrow is here, and I don't know
    who to trust anymore. The future voice was right about everything.
    
    Now I understand - the echo isn't just a warning. It's a curse.
    """

    # Review the script
    review = review_content_by_title(
        content_text=script, title=title, idea=idea, target_length_seconds=90
    )

    # Display results
    print(f"\nScript: {review.script_title}")
    print(f"Overall Score: {review.overall_score}%")
    print(f"Title Alignment: {review.metadata['title_alignment_score']}%")
    print(f"Idea Alignment: {review.metadata['idea_alignment_score']}%")
    print(f"Needs Major Revision: {review.needs_major_revision}")
    print(f"Primary Concern: {review.primary_concern}")

    print("\nStrengths:")
    for strength in review.strengths[:3]:
        print(f"  ✓ {strength}")

    print("\nQuick Wins:")
    for win in review.quick_wins:
        print(f"  ⚡ {win}")

    print("\n")


def example_gap_identification():
    """Example showing gap identification between script and title promise."""
    print("=" * 60)
    print("EXAMPLE 2: Gap Identification")
    print("=" * 60)

    # Create an idea with specific promise
    idea = Idea(
        title="5 Secrets to Perfect Memory",
        concept="Learn proven techniques to improve your memory",
        premise="A quick guide to enhancing memory using science-backed methods",
        genre=ContentGenre.EDUCATIONAL,
        target_audience="Students and professionals",
        length_target="60 seconds",
    )

    # Content that doesn't deliver on the title's promise of "5 secrets"
    title = "5 Secrets to Perfect Memory"
    script = """
    Want better memory? Here's a tip: get more sleep.
    Studies show sleep helps consolidate memories.
    That's it - sweet dreams!
    """

    # Review
    review = review_content_by_title(script, title, idea, target_length_seconds=60)

    print(f"\nScript: {review.script_title}")
    print(f"Overall Score: {review.overall_score}%")

    print("\nIdentified Gaps:")
    for improvement in review.improvement_points:
        if improvement.priority == "high":
            print(f"\n[HIGH PRIORITY] {improvement.title}")
            print(f"  Issue: {improvement.description}")
            print(f"  Example: {improvement.specific_example}")
            print(f"  Suggested Fix: {improvement.suggested_fix}")
            print(f"  Impact: +{improvement.impact_score}%")

    print("\n")


def example_json_output():
    """Example showing JSON output format."""
    print("=" * 60)
    print("EXAMPLE 3: JSON Output Format")
    print("=" * 60)

    # Create a simple idea
    idea = Idea(
        title="Quick Tips", concept="Fast actionable advice", genre=ContentGenre.EDUCATIONAL
    )

    title = "3 Quick Productivity Tips"
    script = """
    Tip 1: Use the Pomodoro Technique - work for 25 minutes, rest for 5.
    Tip 2: Eliminate distractions - turn off notifications during focus time.
    Tip 3: Plan tomorrow today - spend 5 minutes each evening planning.
    """

    # Review
    review = review_content_by_title(script, title, idea)

    # Convert to JSON
    review_dict = review.to_dict()

    print("\nJSON Output (truncated for readability):")
    print(
        json.dumps(
            {
                "content_id": review_dict["content_id"],
                "script_title": review_dict["script_title"],
                "overall_score": review_dict["overall_score"],
                "needs_major_revision": review_dict["needs_major_revision"],
                "metadata": review_dict["metadata"],
                "category_count": len(review_dict["category_scores"]),
                "improvement_count": len(review_dict["improvement_points"]),
            },
            indent=2,
        )
    )

    print("\nFull JSON available via review.to_dict()")
    print("\n")


def example_category_scores():
    """Example showing detailed category scores."""
    print("=" * 60)
    print("EXAMPLE 4: Detailed Category Scores")
    print("=" * 60)

    # Create an idea
    idea = Idea(
        title="The Storm",
        concept="A mysterious storm reveals hidden truths",
        premise="When a strange storm hits a small town, secrets are revealed",
        genre=ContentGenre.MYSTERY,
    )

    title = "Secrets in the Storm"
    script = """
    What if a storm could reveal more than just rain and wind?
    
    Last Tuesday, when the storm hit Millbrook, something changed.
    The power went out, but that's when we started seeing things -
    messages appearing on fogged windows, secrets written in the rain.
    
    Each drop seemed to carry a hidden truth, a mystery waiting to be discovered.
    The storm knew our secrets. And it was ready to reveal them all.
    
    By morning, the town would never be the same. The storm had spoken,
    and we had no choice but to listen to what it had to say.
    """

    # Review
    review = review_content_by_title(script, title, idea)

    print(f"\nScript: {review.script_title}")
    print(f"Overall Score: {review.overall_score}%")

    print("\nCategory Scores:")
    for cat_score in review.category_scores:
        print(f"\n{cat_score.category.value.upper()}: {cat_score.score}%")
        print(f"  Reasoning: {cat_score.reasoning}")
        if cat_score.strengths:
            print(f"  Strengths: {', '.join(cat_score.strengths)}")
        if cat_score.weaknesses:
            print(f"  Weaknesses: {', '.join(cat_score.weaknesses)}")

    print("\n")


def example_iterative_improvement():
    """Example showing iterative improvement workflow."""
    print("=" * 60)
    print("EXAMPLE 5: Iterative Improvement Workflow")
    print("=" * 60)

    # Create an idea
    idea = Idea(
        title="Morning Routine",
        concept="Perfect morning routine in 5 steps",
        genre=ContentGenre.EDUCATIONAL,
    )

    title = "Your Perfect 5-Step Morning Routine"

    # First draft - incomplete
    script_v1 = """
    Wake up early. That's step one.
    Step two is... also important.
    """

    print("\n--- ITERATION 1 ---")
    review_v1 = review_content_by_title(script_v1, title, idea)
    print(f"Score: {review_v1.overall_score}%")
    print(f"Needs Major Revision: {review_v1.needs_major_revision}")
    print("\nTop Improvement:")
    if review_v1.improvement_points:
        top = review_v1.improvement_points[0]
        print(f"  {top.title}: {top.suggested_fix}")

    # Improved draft
    script_v2 = """
    Your perfect morning routine starts here!
    
    Step 1: Wake at 6 AM - consistency is key for your perfect routine.
    Step 2: Hydrate immediately - your body needs water after sleep.
    Step 3: Move your body - 10 minutes of stretching or exercise.
    Step 4: Eat a healthy breakfast - fuel for your perfect day.
    Step 5: Plan your day - 5 minutes to set your intentions.
    
    Follow this perfect morning routine and transform your mornings!
    """

    print("\n--- ITERATION 2 ---")
    review_v2 = review_content_by_title(script_v2, title, idea)
    print(f"Score: {review_v2.overall_score}%")
    print(f"Needs Major Revision: {review_v2.needs_major_revision}")
    print(f"Improvement: +{review_v2.overall_score - review_v1.overall_score}%")

    print("\n")


def main():
    """Run all examples."""
    print("\n")
    print("*" * 60)
    print("PrismQ.T.Review.Content.ByTitle - Usage Examples")
    print("*" * 60)
    print("\n")

    example_basic_review()
    example_gap_identification()
    example_json_output()
    example_category_scores()
    example_iterative_improvement()

    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
    print("\n")


if __name__ == "__main__":
    main()
