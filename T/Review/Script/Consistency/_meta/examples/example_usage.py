"""Example usage of PrismQ.T.Review.Script.Consistency module.

This example demonstrates how to use the Consistency Review module to check
scripts for character name consistency, timeline issues, location tracking,
and internal contradictions.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]  # examples -> _meta -> Consistency -> Script -> Review -> T -> PrismQ
sys.path.insert(0, str(project_root))

from T.Review.Script.Consistency import (
    review_script_consistency,
    review_script_consistency_to_json,
    get_consistency_feedback,
    ScriptConsistencyChecker
)


def example_basic_usage():
    """Basic usage example."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Consistency Review")
    print("=" * 70)
    
    script = """Sarah walked into the old library.
The library was quiet and peaceful.
Sarah found a book about ancient civilizations.
She sat down to read in a comfortable chair.
After an hour, Sarah closed the book and left the library."""
    
    print("\nScript:")
    print(script)
    
    # Review the script
    review = review_script_consistency(script, "example-001", "v3")
    
    print(f"\n{'='*70}")
    print("Review Results:")
    print(f"{'='*70}")
    print(f"Script ID: {review.script_id}")
    print(f"Version: {review.script_version}")
    print(f"Overall Score: {review.overall_score}/100")
    print(f"Character Score: {review.character_score}/100")
    print(f"Timeline Score: {review.timeline_score}/100")
    print(f"Location Score: {review.location_score}/100")
    print(f"Detail Score: {review.detail_score}/100")
    print(f"Passes: {'YES ✓' if review.passes else 'NO ✗'}")
    print(f"Total Issues: {len(review.issues)}")
    
    if review.characters_found:
        print(f"\nCharacters Found: {', '.join(sorted(review.characters_found))}")
    
    print(f"\nSummary: {review.summary}")
    
    if review.issues:
        print(f"\n{'='*70}")
        print("Issues Found:")
        print(f"{'='*70}")
        for issue in review.issues:
            print(f"\n{issue.location} [{issue.severity.value.upper()}]")
            print(f"  Type: {issue.issue_type.value}")
            print(f"  Description: {issue.description}")
            print(f"  Details: {issue.details}")
            print(f"  Suggestion: {issue.suggestion}")
    
    print()


def example_character_inconsistency():
    """Example with character name inconsistency."""
    print("=" * 70)
    print("EXAMPLE 2: Detecting Character Name Inconsistency")
    print("=" * 70)
    
    script = """John walked into the room nervously.
He looked around, searching for something.
Suddenly, Johnny heard a noise from upstairs.
John climbed the stairs slowly.
At the top, there was a closed door.
Johnny opened it carefully."""
    
    print("\nScript:")
    print(script)
    
    # Review the script
    review = review_script_consistency(script, "example-002", "v3")
    
    print(f"\n{'='*70}")
    print("Review Results:")
    print(f"{'='*70}")
    print(f"Overall Score: {review.overall_score}/100")
    print(f"Passes: {'YES ✓' if review.passes else 'NO ✗'}")
    print(f"Total Issues: {len(review.issues)}")
    
    # Get character-specific issues
    character_issues = review.get_character_issues()
    if character_issues:
        print(f"\n{'='*70}")
        print(f"Character Name Issues ({len(character_issues)}):")
        print(f"{'='*70}")
        for issue in character_issues:
            print(f"\n{issue.location}")
            print(f"  {issue.description}")
            print(f"  {issue.details}")
            print(f"  Suggestion: {issue.suggestion}")
    
    print()


def example_json_output():
    """Example with JSON output."""
    print("=" * 70)
    print("EXAMPLE 3: JSON Output")
    print("=" * 70)
    
    script = """Alice met Bob at the coffee shop.
They discussed their plans for the project.
Alice suggested a new approach.
Bob agreed with the idea."""
    
    print("\nScript:")
    print(script)
    
    # Get JSON output
    json_result = review_script_consistency_to_json(script, "example-003", "v3")
    
    print(f"\n{'='*70}")
    print("JSON Output (first 500 characters):")
    print(f"{'='*70}")
    print(json_result[:500])
    print("...")
    print()


def example_feedback():
    """Example using get_consistency_feedback."""
    print("=" * 70)
    print("EXAMPLE 4: Structured Feedback")
    print("=" * 70)
    
    script = """Emma walked into the park.
The park was beautiful in the spring.
Emmy found a bench and sat down.
Emma watched the birds flying."""
    
    print("\nScript:")
    print(script)
    
    # Review and get feedback
    review = review_script_consistency(script, "example-004", "v3")
    feedback = get_consistency_feedback(review)
    
    print(f"\n{'='*70}")
    print("Structured Feedback:")
    print(f"{'='*70}")
    print(f"Script ID: {feedback['script_id']}")
    print(f"Version: {feedback['script_version']}")
    print(f"Overall Score: {feedback['overall_score']}/100")
    print(f"Passes: {'YES ✓' if feedback['passes'] else 'NO ✗'}")
    print(f"Summary: {feedback['summary']}")
    print(f"\nNext Action: {feedback['next_action']}")
    
    if feedback['character_issues']:
        print(f"\n{'='*70}")
        print("Character Issues:")
        print(f"{'='*70}")
        for issue in feedback['character_issues']:
            print(f"\n{issue['location']}")
            print(f"  {issue['description']}")
            print(f"  {issue['details']}")
    
    print()


def example_custom_checker():
    """Example using ScriptConsistencyChecker with custom threshold."""
    print("=" * 70)
    print("EXAMPLE 5: Custom Threshold")
    print("=" * 70)
    
    script = """The detective walked into the crime scene.
Detective Smith examined the evidence carefully.
The room was a mess, with papers scattered everywhere.
Smith found a crucial clue hidden under the desk."""
    
    print("\nScript:")
    print(script)
    
    # Create checker with custom threshold
    checker = ScriptConsistencyChecker(pass_threshold=85)
    review = checker.review_script(script, "example-005", "v3")
    
    print(f"\n{'='*70}")
    print("Review Results (Pass Threshold: 85):")
    print(f"{'='*70}")
    print(f"Overall Score: {review.overall_score}/100")
    print(f"Threshold: {review.pass_threshold}")
    print(f"Passes: {'YES ✓' if review.passes else 'NO ✗'}")
    print(f"Total Issues: {len(review.issues)}")
    
    if review.characters_found:
        print(f"\nCharacters Found: {', '.join(sorted(review.characters_found))}")
    
    print()


def example_workflow_integration():
    """Example showing workflow integration."""
    print("=" * 70)
    print("EXAMPLE 6: Workflow Integration (MVP-017)")
    print("=" * 70)
    
    script = """Michael entered the laboratory.
The lab was filled with advanced equipment.
Mike checked the experiment results.
Everything looked perfect.
Michael prepared the final report."""
    
    print("\nScript:")
    print(script)
    print("\nWorkflow: Script v3+ → Consistency Review → Decision")
    
    # Review the script
    review = review_script_consistency(script, "workflow-001", "v3", pass_threshold=80)
    
    print(f"\n{'='*70}")
    print("Consistency Review Decision:")
    print(f"{'='*70}")
    print(f"Overall Score: {review.overall_score}/100")
    print(f"Passes: {'YES ✓' if review.passes else 'NO ✗'}")
    
    if review.passes:
        print("\n✓ PASS: Proceed to Stage 18 (Editing Review / MVP-018)")
    else:
        print("\n✗ FAIL: Return to Stage 11 (Script Refinement) with feedback")
        
        if review.critical_count > 0:
            print(f"\n  → {review.critical_count} critical issue(s) must be fixed")
        if review.high_count > 0:
            print(f"  → {review.high_count} high-priority issue(s) should be addressed")
        
        if review.primary_concerns:
            print("\n  Primary Concerns:")
            for concern in review.primary_concerns:
                print(f"    • {concern}")
    
    print()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PrismQ Script Consistency Review - Example Usage")
    print("=" * 70)
    print("\nModule: T.Review.Script.Consistency")
    print("Stage: 17 (MVP-017)")
    print("Purpose: Check character names, timeline, locations, contradictions")
    print()
    
    example_basic_usage()
    example_character_inconsistency()
    example_json_output()
    example_feedback()
    example_custom_checker()
    example_workflow_integration()
    
    print("=" * 70)
    print("Examples Complete")
    print("=" * 70)
