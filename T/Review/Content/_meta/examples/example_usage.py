"""Example usage of ContentReview module.

This example demonstrates how to use the ContentReview module to evaluate
script content for logic gaps, plot issues, character motivation, and pacing.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(project_root))

from T.Review.Content import (
    ContentReview,
    ContentIssue,
    ContentIssueType,
    ContentSeverity
)
import json


def example_coherent_script():
    """Example of reviewing a coherent script that passes."""
    print("\n=== Example 1: Coherent Script (PASSES) ===\n")
    
    review = ContentReview(
        script_id="script-mystery-001",
        script_version="v3",
        overall_score=88,
        logic_score=90,
        plot_score=88,
        character_score=85,
        pacing_score=90
    )
    
    review.summary = "Well-structured mystery with good pacing and clear character motivation"
    review.strengths = [
        "Strong opening hook that draws reader in",
        "Characters have clear and believable motivations",
        "Plot twists are well-foreshadowed",
        "Pacing keeps reader engaged throughout"
    ]
    
    print(f"Review: {review}")
    print(f"Overall Score: {review.overall_score}%")
    print(f"Logic Score: {review.logic_score}%")
    print(f"Plot Score: {review.plot_score}%")
    print(f"Character Score: {review.character_score}%")
    print(f"Pacing Score: {review.pacing_score}%")
    print(f"Passes: {'YES ✓' if review.passes else 'NO ✗'}")
    print(f"Issues: {len(review.issues)}")
    print(f"\nSummary: {review.summary}")
    print(f"\nStrengths:")
    for strength in review.strengths:
        print(f"  • {strength}")
    
    if review.passes:
        print("\n→ Ready for Stage 17: Consistency Review")


def example_incoherent_script():
    """Example of reviewing an incoherent script that fails."""
    print("\n=== Example 2: Incoherent Script (FAILS) ===\n")
    
    review = ContentReview(
        script_id="script-mystery-002",
        script_version="v3",
        overall_score=62,
        logic_score=55,
        plot_score=60,
        character_score=65,
        pacing_score=68
    )
    
    # Add critical plot issue
    review.add_issue(ContentIssue(
        issue_type=ContentIssueType.PLOT_ISSUE,
        severity=ContentSeverity.CRITICAL,
        section="Act 2, Scene 5",
        description="Major plot hole: Detective solves case with information never revealed to reader",
        suggestion="Add scene showing how detective discovered the key clue, or reveal it to reader earlier",
        impact="Breaks suspension of disbelief, reader feels cheated by 'deus ex machina' solution"
    ))
    
    # Add high severity logic gap
    review.add_issue(ContentIssue(
        issue_type=ContentIssueType.LOGIC_GAP,
        severity=ContentSeverity.HIGH,
        section="Act 1, Scene 3",
        description="Character knows victim's secret despite never being told",
        suggestion="Add dialogue or flashback showing how character learned this information",
        impact="Logic gap makes character seem omniscient, breaks realism"
    ))
    
    # Add high severity character motivation issue
    review.add_issue(ContentIssue(
        issue_type=ContentIssueType.CHARACTER_MOTIVATION,
        severity=ContentSeverity.HIGH,
        section="Act 3, Scene 2",
        description="Protagonist suddenly decides to risk life without clear motivation",
        suggestion="Add internal monologue or dialogue establishing stakes and why this matters personally",
        impact="Character's actions feel arbitrary, undermines emotional investment"
    ))
    
    # Add medium pacing issue
    review.add_issue(ContentIssue(
        issue_type=ContentIssueType.PACING,
        severity=ContentSeverity.MEDIUM,
        section="Act 1, Scenes 1-4",
        description="Opening is too slow, takes 15 minutes to establish conflict",
        suggestion="Start with inciting incident, move character introduction earlier",
        impact="Risk losing audience in first act before story hooks them"
    ))
    
    review.summary = "Script has intriguing premise but suffers from logic gaps and plot holes that undermine story"
    review.primary_concerns = [
        "Critical plot hole in Act 2 finale",
        "Multiple logic gaps create confusion",
        "Character motivations need strengthening",
        "Opening pacing could be tighter"
    ]
    
    print(f"Review: {review}")
    print(f"Overall Score: {review.overall_score}%")
    print(f"Passes: {'YES ✓' if review.passes else 'NO ✗'}")
    print(f"Issues: {len(review.issues)}")
    print(f"  - Critical: {review.critical_count}")
    print(f"  - High: {review.high_count}")
    print(f"  - Medium: {review.medium_count}")
    print(f"  - Low: {review.low_count}")
    
    print(f"\nSummary: {review.summary}")
    print(f"\nPrimary Concerns:")
    for concern in review.primary_concerns:
        print(f"  • {concern}")
    
    print("\nDetailed Issues:")
    for i, issue in enumerate(review.issues, 1):
        print(f"\n  Issue {i} [{issue.severity.value.upper()}]:")
        print(f"    Type: {issue.issue_type.value}")
        print(f"    Section: {issue.section}")
        print(f"    Description: {issue.description}")
        print(f"    Suggestion: {issue.suggestion}")
        print(f"    Impact: {issue.impact}")
    
    if not review.passes:
        print("\n→ Return to Stage 11: Script Refinement with feedback")


def example_json_export():
    """Example of exporting review to JSON."""
    print("\n=== Example 3: JSON Export ===\n")
    
    review = ContentReview(
        script_id="script-thriller-001",
        script_version="v4",
        overall_score=78,
        logic_score=80,
        plot_score=75,
        character_score=78,
        pacing_score=80
    )
    
    review.add_issue(ContentIssue(
        issue_type=ContentIssueType.PACING,
        severity=ContentSeverity.MEDIUM,
        section="Act 2, Middle",
        description="Middle section drags, loses tension",
        suggestion="Add subplot or escalate stakes to maintain momentum",
        impact="Audience engagement may drop during second act"
    ))
    
    review.summary = "Solid thriller with good fundamentals, minor pacing adjustment needed"
    
    # Export to dictionary
    review_dict = review.to_dict()
    
    # Convert to JSON
    review_json = json.dumps(review_dict, indent=2)
    print("Review as JSON:")
    print(review_json)
    
    # Demonstrate round-trip
    print("\n--- Round-trip test ---")
    restored_review = ContentReview.from_dict(review_dict)
    print(f"Original: {review}")
    print(f"Restored: {restored_review}")
    print(f"Passes match: {review.passes == restored_review.passes}")
    print(f"Issues match: {len(review.issues) == len(restored_review.issues)}")


def example_issue_filtering():
    """Example of filtering issues by type and severity."""
    print("\n=== Example 4: Issue Filtering ===\n")
    
    review = ContentReview(
        script_id="script-drama-001",
        script_version="v3",
        overall_score=70
    )
    
    # Add various issues
    review.add_issue(ContentIssue(
        issue_type=ContentIssueType.LOGIC_GAP,
        severity=ContentSeverity.HIGH,
        section="Act 1",
        description="Logic gap in character backstory",
        suggestion="Add flashback",
        impact="Confusion"
    ))
    
    review.add_issue(ContentIssue(
        issue_type=ContentIssueType.LOGIC_GAP,
        severity=ContentSeverity.MEDIUM,
        section="Act 2",
        description="Minor logic inconsistency",
        suggestion="Clarify timeline",
        impact="Minor confusion"
    ))
    
    review.add_issue(ContentIssue(
        issue_type=ContentIssueType.PLOT_ISSUE,
        severity=ContentSeverity.HIGH,
        section="Act 3",
        description="Plot thread unresolved",
        suggestion="Add resolution scene",
        impact="Unsatisfying ending"
    ))
    
    review.add_issue(ContentIssue(
        issue_type=ContentIssueType.PACING,
        severity=ContentSeverity.LOW,
        section="Act 1",
        description="Scene slightly too long",
        suggestion="Trim dialogue",
        impact="Minor pacing slowdown"
    ))
    
    print(f"Total issues: {len(review.issues)}")
    print(f"\nBy severity:")
    print(f"  Critical: {len(review.get_issues_by_severity(ContentSeverity.CRITICAL))}")
    print(f"  High: {len(review.get_issues_by_severity(ContentSeverity.HIGH))}")
    print(f"  Medium: {len(review.get_issues_by_severity(ContentSeverity.MEDIUM))}")
    print(f"  Low: {len(review.get_issues_by_severity(ContentSeverity.LOW))}")
    
    print(f"\nBy type:")
    print(f"  Logic gaps: {len(review.get_logic_issues())}")
    print(f"  Plot issues: {len(review.get_plot_issues())}")
    print(f"  Character issues: {len(review.get_character_issues())}")
    print(f"  Pacing issues: {len(review.get_pacing_issues())}")
    
    print(f"\nHigh priority issues (Critical + High):")
    high_priority = review.get_high_priority_issues()
    for issue in high_priority:
        print(f"  • [{issue.severity.value}] {issue.issue_type.value}: {issue.description}")


if __name__ == "__main__":
    print("=" * 70)
    print("ContentReview Module Examples")
    print("=" * 70)
    
    example_coherent_script()
    example_incoherent_script()
    example_json_export()
    example_issue_filtering()
    
    print("\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70)
