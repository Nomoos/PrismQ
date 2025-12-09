"""Example usage of PrismQ.T.Story.Polish module."""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from polish import PolishConfig, PriorityLevel, polish_story_with_gpt


def example_basic_polish():
    """Basic example of story polishing."""
    print("=" * 60)
    print("Example: Basic Story Polish")
    print("=" * 60)

    # Expert review data from Stage 21
    review_data = {
        "overall_assessment": {"quality_score": 92, "ready_for_publishing": False},
        "improvement_suggestions": [
            {
                "component": "title",
                "priority": "medium",
                "suggestion": 'Capitalize "and" for stronger visual impact',
                "impact": "Improves thumbnail readability",
            },
            {
                "component": "script",
                "priority": "high",
                "suggestion": "Add brief relatable context in opening",
                "impact": "Increases immediate audience connection",
            },
        ],
    }

    # Polish the story
    polish = polish_story_with_gpt(
        story_id="horror_short_001",
        current_title="The House That Remembers: and Hunts",
        current_script="Every night at midnight, she returns.\nNot as a ghost. Not as a memory.\nAs herself.",
        expert_review_data=review_data,
        iteration_number=1,
    )

    # Display results
    print(f"\nStory ID: {polish.story_id}")
    print(f"Iteration: {polish.iteration_number}")
    print(
        f"\nQuality: {polish.original_quality_score} → {polish.expected_quality_score} (+{polish.quality_delta})"
    )

    print(f"\n--- TITLE ---")
    print(f"Before: {polish.original_title}")
    print(f"After:  {polish.polished_title}")

    print(f"\n--- SCRIPT ---")
    print(f"Before: {polish.original_script[:80]}...")
    print(f"After:  {polish.polished_script[:120]}...")

    print(f"\n--- CHANGES ---")
    for i, change in enumerate(polish.change_log, 1):
        print(f"{i}. {change.component.value.upper()} - {change.change_type.value}")
        print(f"   Rationale: {change.rationale}")

    print(f"\nTotal improvements: {len(polish.change_log)}")
    print(f"Ready for re-review: {polish.ready_for_review}")


if __name__ == "__main__":
    example_basic_polish()
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)
