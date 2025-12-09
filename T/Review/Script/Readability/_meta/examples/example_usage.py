"""Example usage of Content Readability Review for voiceover suitability checking.

This example demonstrates how to use the PrismQ.T.Review.Content.Readability module
to check if a script is suitable for voiceover narration.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

from T.Review.Content.Readability import (
    get_readability_feedback,
    review_content_readability,
    review_content_readability_to_json,
)


def example_basic_review():
    """Example: Basic readability review."""
    print("=" * 60)
    print("Example 1: Basic Readability Review")
    print("=" * 60 + "\n")

    script = """Welcome to our story about a young scientist making a discovery.
She walked into the laboratory early one morning.
The equipment was ready for the experiment.
Everything went according to plan."""

    print("Content:")
    print(script)
    print("\n" + "-" * 60 + "\n")

    review = review_content_readability(
        content_text=script, content_id="example-001", script_version="v3"
    )

    print(f"Overall Score: {review.overall_score}/100")
    print(f"Pronunciation Score: {review.pronunciation_score}/100")
    print(f"Pacing Score: {review.pacing_score}/100")
    print(f"Flow Score: {review.flow_score}/100")
    print(f"Mouthfeel Score: {review.mouthfeel_score}/100")
    print(f"Passes: {'YES ✓' if review.passes else 'NO ✗'}")
    print(f"\nSummary: {review.summary}")
    print("\n")


def example_problematic_content():
    """Example: Content with voiceover issues."""
    print("=" * 60)
    print("Example 2: Content with Voiceover Issues")
    print("=" * 60 + "\n")

    script = """Peter Piper picked particularly problematic peppers from the phosphorescent patch.
The phenomenon of phosphorescence perplexed physicists persistently pursuing practical explanations.
This is an extraordinarily long sentence that continues on and on without providing any natural breathing pauses or places for the voiceover artist to take a breath making it extremely difficult to deliver this narration smoothly and naturally without running out of breath.
Subsequently, the methodology employed in the implementation of the aforementioned functionality was unequivocally quintessential for the contemporaneous understanding of the phenomenon."""

    print("Content:")
    print(script[:200] + "...")
    print("\n" + "-" * 60 + "\n")

    review = review_content_readability(
        content_text=script, content_id="example-002", script_version="v3"
    )

    print(f"Overall Score: {review.overall_score}/100")
    print(f"Passes: {'YES ✓' if review.passes else 'NO ✗'}")
    print(f"\nSummary: {review.summary}")

    if review.voiceover_notes:
        print("\nVoiceover Notes:")
        for note in review.voiceover_notes:
            print(f"  • {note}")

    if review.primary_concerns:
        print("\nPrimary Concerns:")
        for concern in review.primary_concerns:
            print(f"  • {concern}")

    print(f"\nTotal Issues Found: {len(review.issues)}")

    # Show first few issues
    if review.issues:
        print("\nSample Issues:")
        for issue in review.issues[:3]:
            print(f"\n  Line {issue.line_number} [{issue.severity.value.upper()}]")
            print(f"  Type: {issue.issue_type.value}")
            print(f"  Text: '{issue.text[:60]}...'")
            print(f"  Suggestion: {issue.suggestion}")
            print(f"  Explanation: {issue.explanation}")

    print("\n")


def example_json_output():
    """Example: JSON output for integration."""
    print("=" * 60)
    print("Example 3: JSON Output for Integration")
    print("=" * 60 + "\n")

    script = "She sells seashells by the seashore, specifically selecting superior specimens."

    json_output = review_content_readability_to_json(
        content_text=script, content_id="example-003", script_version="v3"
    )

    print("JSON Output (first 500 characters):")
    print(json_output[:500] + "...")
    print("\n")


def example_feedback_extraction():
    """Example: Extracting structured feedback."""
    print("=" * 60)
    print("Example 4: Structured Feedback for Content Writers")
    print("=" * 60 + "\n")

    script = """The strengths of the sixth method remained unclear despite extensive testing.
This extraordinarily complex and convoluted sentence structure makes comprehension difficult."""

    review = review_content_readability(script, "example-004", "v3")
    feedback = get_readability_feedback(review)

    print(f"Content ID: {feedback['content_id']}")
    print(f"Passes: {feedback['passes']}")
    print(f"Overall Score: {feedback['overall_score']}/100")
    print(f"\nBreakdown:")
    print(f"  Pronunciation: {feedback['pronunciation_score']}/100")
    print(f"  Pacing: {feedback['pacing_score']}/100")
    print(f"  Flow: {feedback['flow_score']}/100")
    print(f"  Mouthfeel: {feedback['mouthfeel_score']}/100")
    print(f"\nNext Action: {feedback['next_action']}")

    if feedback["high_priority_issues"]:
        print(f"\nHigh Priority Issues ({len(feedback['high_priority_issues'])}):")
        for issue in feedback["high_priority_issues"]:
            print(f"  Line {issue['line']}: {issue['explanation']}")

    print("\n")


def example_workflow_integration():
    """Example: Integration in the workflow."""
    print("=" * 60)
    print("Example 5: Workflow Integration (Stage 20)")
    print("=" * 60 + "\n")

    print("Content Review Workflow:")
    print("  Stage 17: Consistency Review → PASS")
    print("  Stage 18: Editing Review → PASS")
    print("  Stage 19: Title Readability → PASS")
    print("  Stage 20: Content Readability (MVP-020) → CHECKING...")
    print()

    script = """A young inventor discovers a revolutionary technology.
He tests it carefully in his workshop.
The results exceed all expectations.
The world will never be the same."""

    review = review_content_readability(script, "workflow-001", "v3")

    print(f"  Result: {'PASS ✓' if review.passes else 'FAIL ✗'}")
    print(f"  Score: {review.overall_score}/100")

    if review.passes:
        print("\n  ✓ Content is ready for voiceover")
        print("  → Proceed to Stage 21: Expert Review (MVP-021)")
    else:
        print("\n  ✗ Content needs voiceover improvements")
        print("  → Return to Stage 11: Content Refinement")
        print(f"\n  Issues to address: {len(review.issues)}")
        for issue in review.get_high_priority_issues():
            print(f"    • Line {issue.line_number}: {issue.explanation}")

    print("\n")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("PrismQ Content Readability Review - Example Usage")
    print("Stage 20 (MVP-020): Voiceover Suitability Checking")
    print("=" * 60 + "\n")

    example_basic_review()
    example_problematic_content()
    example_json_output()
    example_feedback_extraction()
    example_workflow_integration()

    print("=" * 60)
    print("Examples Complete")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
