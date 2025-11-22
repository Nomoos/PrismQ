"""Example usage of Script Editing Review (MVP-018).

This example demonstrates how to use the Editing Review module to validate
script clarity, flow, and conciseness.

Stage 18 (MVP-018): Editing Review
- Detects wordiness, redundancy, clarity issues
- Checks for weak transitions and poor flow
- Provides specific improvement suggestions
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(project_root))

from T.Review.Script.Editing import (
    review_script_editing,
    review_script_editing_to_json,
    get_editing_feedback
)


def example_1_well_edited_script():
    """Example 1: Well-edited script that passes."""
    print("="*60)
    print("EXAMPLE 1: Well-Edited Script")
    print("="*60)
    
    script = """INT. COFFEE SHOP - DAY

Sarah enters the bustling coffee shop.
She spots her friend waiting at a corner table.

SARAH
Hey! Sorry I'm late.

MICHAEL
No worries. I just got here.

They sit down and begin their conversation.
The ambient noise creates a cozy atmosphere."""
    
    print("\nScript:")
    print(script)
    print("\n" + "-"*60)
    
    review = review_script_editing(script, script_id="example-001", script_version="v3")
    
    print(f"\nOverall Score: {review.overall_score}/100")
    print(f"Passes: {'✅ YES' if review.passes else '❌ NO'}")
    print(f"Total Issues: {len(review.issues)}")
    print(f"\nSummary: {review.summary}")
    
    if review.passes:
        print("\n✅ Script is ready for Stage 19 (Title Readability)")
    else:
        print("\n❌ Script needs revision - return to Stage 11 (Script Refinement)")


def example_2_wordy_script():
    """Example 2: Wordy script with editing issues."""
    print("\n\n" + "="*60)
    print("EXAMPLE 2: Wordy Script (Needs Editing)")
    print("="*60)
    
    script = """In order to complete the mission, the team needs to proceed carefully.
At this point in time, the situation is becoming more complex.
Due to the fact that the weather is bad, we should postpone the operation.
The hero makes a decision to fight the villain in spite of the danger."""
    
    print("\nScript:")
    print(script)
    print("\n" + "-"*60)
    
    review = review_script_editing(script, script_id="example-002", script_version="v3")
    
    print(f"\nOverall Score: {review.overall_score}/100")
    print(f"Passes: {'✅ YES' if review.passes else '❌ NO'}")
    print(f"Total Issues: {len(review.issues)}")
    print(f"\nSummary: {review.summary}")
    
    if review.issues:
        print("\n📋 Issues Detected:")
        for i, issue in enumerate(review.issues[:5], 1):  # Show first 5
            print(f"\n{i}. Line {issue.line_number} [{issue.severity.value.upper()}] - {issue.issue_type.value.upper()}")
            print(f"   Text: '{issue.text[:60]}...'")
            print(f"   Suggestion: {issue.suggestion[:60]}...")
            print(f"   Explanation: {issue.explanation}")
    
    if review.quick_fixes:
        print("\n🔧 Quick Fixes:")
        for fix in review.quick_fixes:
            print(f"   • {fix}")


def example_3_redundant_script():
    """Example 3: Script with redundancy issues."""
    print("\n\n" + "="*60)
    print("EXAMPLE 3: Redundant Script")
    print("="*60)
    
    script = """This opportunity is very unique and special.
We need to review the past history of events.
The location is in close proximity to the building.
The final outcome was exactly the exact same as predicted."""
    
    print("\nScript:")
    print(script)
    print("\n" + "-"*60)
    
    review = review_script_editing(script, script_id="example-003", script_version="v3")
    
    print(f"\nOverall Score: {review.overall_score}/100")
    print(f"Passes: {'✅ YES' if review.passes else '❌ NO'}")
    print(f"Total Issues: {len(review.issues)}")
    
    if review.issues:
        print("\n📋 Redundancy Issues:")
        redundancy_issues = [i for i in review.issues if i.issue_type.value == 'redundancy']
        for i, issue in enumerate(redundancy_issues, 1):
            print(f"\n{i}. Line {issue.line_number}")
            print(f"   ❌ Redundant: '{issue.text[:60]}'")
            print(f"   ✅ Better: {issue.suggestion[:60]}...")


def example_4_json_output():
    """Example 4: Getting JSON output for API integration."""
    print("\n\n" + "="*60)
    print("EXAMPLE 4: JSON Output")
    print("="*60)
    
    script = """In order to proceed, we give consideration to all options."""
    
    print("\nScript:")
    print(script)
    print("\n" + "-"*60)
    
    json_output = review_script_editing_to_json(script, script_id="example-004")
    
    print("\n📄 JSON Output:")
    print(json_output[:500] + "...")
    
    print("\n💡 Use this JSON format for:")
    print("   • API responses")
    print("   • Database storage")
    print("   • Frontend integration")
    print("   • Logging and auditing")


def example_5_feedback_for_refinement():
    """Example 5: Getting structured feedback for script refinement."""
    print("\n\n" + "="*60)
    print("EXAMPLE 5: Structured Feedback")
    print("="*60)
    
    script = """In order to understand this, we need to give consideration to the facts.
The decision was made made by the team at this point in time."""
    
    print("\nScript:")
    print(script)
    print("\n" + "-"*60)
    
    review = review_script_editing(script, script_id="example-005")
    feedback = get_editing_feedback(review)
    
    print(f"\n📊 Feedback Summary:")
    print(f"   Script ID: {feedback['script_id']}")
    print(f"   Score: {feedback['overall_score']}/100")
    print(f"   Passes: {feedback['passes']}")
    print(f"   Total Issues: {feedback['total_issues']}")
    
    if feedback['primary_concerns']:
        print(f"\n⚠️ Primary Concerns:")
        for concern in feedback['primary_concerns']:
            print(f"   • {concern}")
    
    if feedback['quick_fixes']:
        print(f"\n🔧 Quick Fixes:")
        for fix in feedback['quick_fixes']:
            print(f"   • {fix}")
    
    print(f"\n➡️ Next Action: {feedback['next_action']}")


def example_6_custom_threshold():
    """Example 6: Using custom pass threshold."""
    print("\n\n" + "="*60)
    print("EXAMPLE 6: Custom Pass Threshold")
    print("="*60)
    
    script = """In order to proceed, we continue with the plan."""
    
    print("\nScript:")
    print(script)
    print("\n" + "-"*60)
    
    # Strict threshold (95)
    review_strict = review_script_editing(script, script_id="strict", pass_threshold=95)
    
    # Lenient threshold (70)
    review_lenient = review_script_editing(script, script_id="lenient", pass_threshold=70)
    
    print(f"\n📊 With Strict Threshold (95):")
    print(f"   Score: {review_strict.overall_score}/100")
    print(f"   Passes: {'✅ YES' if review_strict.passes else '❌ NO'}")
    
    print(f"\n📊 With Lenient Threshold (70):")
    print(f"   Score: {review_lenient.overall_score}/100")
    print(f"   Passes: {'✅ YES' if review_lenient.passes else '❌ NO'}")
    
    print("\n💡 Tip: Adjust threshold based on:")
    print("   • Content type (narrative vs. technical)")
    print("   • Target audience")
    print("   • Production stage")


if __name__ == "__main__":
    print("\n" + "🎬 SCRIPT EDITING REVIEW EXAMPLES (MVP-018)" + "\n")
    print("Stage 18: Editing Review - Clarity, Flow, and Conciseness")
    print("="*60)
    
    example_1_well_edited_script()
    example_2_wordy_script()
    example_3_redundant_script()
    example_4_json_output()
    example_5_feedback_for_refinement()
    example_6_custom_threshold()
    
    print("\n\n" + "="*60)
    print("✅ All examples completed!")
    print("="*60)
    
    print("\n📚 Key Features:")
    print("   • Wordiness detection and suggestions")
    print("   • Redundancy removal")
    print("   • Clarity improvements (passive voice, long sentences)")
    print("   • Transition quality checks")
    print("   • Flow and structure validation")
    print("   • Configurable pass/fail thresholds")
    print("   • JSON output for API integration")
    print("   • Structured feedback for refinement")
    
    print("\n🔗 Integration:")
    print("   • Use after Consistency Review (Stage 17/MVP-017)")
    print("   • Before Title Readability (Stage 19/MVP-019)")
    print("   • Part of the quality review pipeline")
    print("\n")
