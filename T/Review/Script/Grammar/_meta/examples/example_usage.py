"""Example usage of Script Grammar Review (MVP-014).

Demonstrates how to use PrismQ.T.Review.Script.Grammar for validating
script grammar before proceeding to Tone Review (MVP-015).
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]  # examples -> _meta -> Grammar -> Script -> Review -> T -> PrismQ
sys.path.insert(0, str(project_root))

from T.Review.Script.Grammar import (
    review_script_grammar,
    review_script_grammar_to_json,
    get_grammar_feedback
)
import json


def example_basic_usage():
    """Basic example of grammar review."""
    print("="*60)
    print("EXAMPLE 1: Basic Grammar Review")
    print("="*60 + "\n")
    
    script = """The hero stands at the edge of the cliff.
Below, the ocean crashes against jagged rocks.
A storm approaches from the distance.
Thunder rumbles across the sky.
The hero takes a deep breath and prepares to jump."""
    
    print("Script:")
    print(script)
    print("\n" + "-"*60 + "\n")
    
    # Perform grammar review
    review = review_script_grammar(script, script_id="hero-001", script_version="v3")
    
    print(f"Overall Score: {review.overall_score}/100")
    print(f"Passes: {'YES ✓' if review.passes else 'NO ✗'}")
    print(f"Total Issues: {len(review.issues)}")
    print(f"\nSummary: {review.summary}")
    
    if review.passes:
        print("\n✓ Script is ready for Stage 15: Tone Review")
    else:
        print("\n✗ Script needs refinement before proceeding")
    
    print("\n")


def example_with_errors():
    """Example showing error detection and feedback."""
    print("="*60)
    print("EXAMPLE 2: Script with Grammar Errors")
    print("="*60 + "\n")
    
    script = """i recieved a mysterious message yesterday.
He were very excited about the discovery.
The old mansion has many secrets
We was all curious about what happened there."""
    
    print("Script:")
    print(script)
    print("\n" + "-"*60 + "\n")
    
    # Perform grammar review
    review = review_script_grammar(script, script_id="mansion-001", script_version="v3")
    
    print(f"Overall Score: {review.overall_score}/100")
    print(f"Passes: {'YES ✓' if review.passes else 'NO ✗'}")
    print(f"Total Issues: {len(review.issues)}")
    print(f"  - Critical: {review.critical_count}")
    print(f"  - High: {review.high_count}")
    print(f"  - Medium: {review.medium_count}")
    print(f"  - Low: {review.low_count}")
    
    print(f"\nSummary: {review.summary}")
    
    if review.issues:
        print("\n" + "="*60)
        print("Issues Found (with line references):")
        print("="*60)
        
        for i, issue in enumerate(review.issues, 1):
            print(f"\n{i}. Line {issue.line_number} [{issue.severity.value.upper()}] - {issue.issue_type.value.upper()}")
            print(f"   Problem: '{issue.text}'")
            print(f"   Suggestion: '{issue.suggestion}'")
            print(f"   Explanation: {issue.explanation}")
    
    print("\n")


def example_json_output():
    """Example showing JSON output format."""
    print("="*60)
    print("EXAMPLE 3: JSON Output Format")
    print("="*60 + "\n")
    
    script = """The detective examines the evidence.
He were looking for clues everywhere.
I recieved a tip from an informant."""
    
    print("Script:")
    print(script)
    print("\n" + "-"*60 + "\n")
    
    # Get JSON output
    json_output = review_script_grammar_to_json(
        script,
        script_id="detective-001",
        script_version="v3"
    )
    
    print("JSON Output:")
    print(json_output)
    
    # Parse and use JSON
    data = json.loads(json_output)
    print("\n" + "-"*60)
    print(f"\nParsed from JSON:")
    print(f"  Script ID: {data['script_id']}")
    print(f"  Score: {data['overall_score']}/100")
    print(f"  Passes: {data['passes']}")
    print(f"  Issues found: {len(data['issues'])}")
    
    print("\n")


def example_feedback_for_refinement():
    """Example showing structured feedback for script refinement."""
    print("="*60)
    print("EXAMPLE 4: Structured Feedback for Script Writer")
    print("="*60 + "\n")
    
    script = """the hero enters the room cautiously.
He were carrying a flashlight.
Strange shadows move across the walls.
I recieved a warning about this place."""
    
    print("Script:")
    print(script)
    print("\n" + "-"*60 + "\n")
    
    # Perform review
    review = review_script_grammar(script, script_id="room-001", script_version="v3")
    
    # Get structured feedback
    feedback = get_grammar_feedback(review)
    
    print("FEEDBACK FOR SCRIPT WRITER")
    print("="*60)
    print(f"\nScript: {feedback['script_id']} ({feedback['script_version']})")
    print(f"Status: {'PASS ✓' if feedback['passes'] else 'FAIL ✗'}")
    print(f"Score: {feedback['overall_score']}/{feedback['threshold']}")
    print(f"\nSummary: {feedback['summary']}")
    
    if feedback['primary_concerns']:
        print("\nPrimary Concerns:")
        for concern in feedback['primary_concerns']:
            print(f"  • {concern}")
    
    if feedback['critical_issues']:
        print("\n" + "-"*60)
        print("Critical Issues (MUST FIX):")
        for issue in feedback['critical_issues']:
            print(f"\n  Line {issue['line']}: {issue['type'].upper()}")
            print(f"    Problem: '{issue['text']}'")
            print(f"    Fix: '{issue['suggestion']}'")
            print(f"    Reason: {issue['explanation']}")
    
    if feedback['high_priority_issues']:
        print("\n" + "-"*60)
        print("High Priority Issues (SHOULD FIX):")
        for issue in feedback['high_priority_issues']:
            print(f"\n  Line {issue['line']}: {issue['type'].upper()}")
            print(f"    Problem: '{issue['text']}'")
            print(f"    Fix: '{issue['suggestion']}'")
    
    if feedback['quick_fixes']:
        print("\n" + "-"*60)
        print("Quick Fixes:")
        for fix in feedback['quick_fixes']:
            print(f"  • {fix}")
    
    print("\n" + "="*60)
    print(f"Next Action: {feedback['next_action']}")
    print("="*60)
    
    print("\n")


def example_workflow_integration():
    """Example showing integration with the workflow."""
    print("="*60)
    print("EXAMPLE 5: Workflow Integration (Stage 14)")
    print("="*60 + "\n")
    
    print("Simulating the workflow from Script v3 to next stage...\n")
    
    # Script v3 (after initial creation and review)
    script_v3 = """The old house creaks in the wind.
Sarah approaches the front door nervously.
She were warned not to come here.
The door opens with a haunting sound."""
    
    print("Script v3 (from previous stage):")
    print(script_v3)
    print("\n" + "-"*60)
    
    # Stage 14: Grammar Review
    print("\nStage 14: Grammar Review (MVP-014)")
    print("-"*60)
    
    review = review_script_grammar(script_v3, script_id="house-001", script_version="v3")
    
    print(f"Score: {review.overall_score}/100")
    print(f"Result: {'PASS' if review.passes else 'FAIL'}")
    
    if review.passes:
        print("\n✓ WORKFLOW: Proceed to Stage 15 (Tone Review / MVP-015)")
    else:
        print(f"\n✗ WORKFLOW: Return to Stage 11 (Script Refinement)")
        print(f"   Issues to fix: {len(review.issues)}")
        
        if review.critical_count > 0:
            print(f"\n   CRITICAL ISSUES (must fix before proceeding):")
            for issue in review.get_critical_issues():
                print(f"     • Line {issue.line_number}: {issue.explanation}")
                print(f"       Change '{issue.text}' to '{issue.suggestion}'")
        
        # Simulate refinement
        print("\n" + "-"*60)
        print("After refinement (applying fixes):")
        print("-"*60)
        
        script_v4 = """The old house creaks in the wind.
Sarah approaches the front door nervously.
She was warned not to come here.
The door opens with a haunting sound."""
        
        print(script_v4)
        
        review_v4 = review_script_grammar(script_v4, script_id="house-001", script_version="v4")
        
        print(f"\nRe-review Score: {review_v4.overall_score}/100")
        print(f"Result: {'PASS' if review_v4.passes else 'FAIL'}")
        
        if review_v4.passes:
            print("\n✓ WORKFLOW: Now proceeding to Stage 15 (Tone Review / MVP-015)")
    
    print("\n")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("SCRIPT GRAMMAR REVIEW EXAMPLES")
    print("MVP-014: PrismQ.T.Review.Script.Grammar")
    print("="*60 + "\n")
    
    # Run all examples
    example_basic_usage()
    example_with_errors()
    example_json_output()
    example_feedback_for_refinement()
    example_workflow_integration()
    
    print("="*60)
    print("END OF EXAMPLES")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
