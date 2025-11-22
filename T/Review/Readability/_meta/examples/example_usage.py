"""Example usage of Title Readability Review (MVP-019).

This example demonstrates how to use the TitleReadabilityReview model to
evaluate titles for voiceover suitability, checking clarity, length,
engagement, rhythm, and mouthfeel.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

from T.Review.Readability import (
    TitleReadabilityReview,
    ReadabilityIssue,
    ReadabilityIssueType,
    ReadabilitySeverity
)


def example_perfect_voiceover_title():
    """Example: Title with perfect voiceover readability."""
    print("\n" + "="*80)
    print("Example 1: Perfect Voiceover Title")
    print("="*80)
    
    review = TitleReadabilityReview(
        title_id="title-perfect-001",
        title_text="The Echo Mystery: Secrets Revealed",
        title_version="v3",
        overall_score=95
    )
    
    review.summary = "Excellent voiceover title with clear rhythm and engagement"
    review.voiceover_notes.append("Perfect pace with natural dramatic pause at colon")
    review.voiceover_notes.append("Easy to pronounce, flows naturally")
    
    print(f"\nTitle: {review.title_text}")
    print(f"Version: {review.title_version}")
    print(f"Overall Score: {review.overall_score}/100")
    print(f"Status: {'✓ PASSES' if review.passes else '✗ FAILS'}")
    print(f"\nSummary: {review.summary}")
    print("\nVoiceover Notes:")
    for note in review.voiceover_notes:
        print(f"  • {note}")
    
    if review.passes:
        print("\n→ Ready for Finalization")
    
    return review


def example_title_with_mouthfeel_issues():
    """Example: Title with mouthfeel issues that need fixing."""
    print("\n" + "="*80)
    print("Example 2: Title with Mouthfeel Issues")
    print("="*80)
    
    review = TitleReadabilityReview(
        title_id="title-mouthfeel-001",
        title_text="Cryptographic Catastrophic Crypts",
        title_version="v3",
        overall_score=65
    )
    
    # Add mouthfeel issue
    review.add_issue(ReadabilityIssue(
        issue_type=ReadabilityIssueType.MOUTHFEEL,
        severity=ReadabilitySeverity.CRITICAL,
        text="Cryptographic Catastrophic Crypts",
        suggestion="Secret Digital Dangers",
        explanation="Multiple consonant clusters ('cr', 'pt', 'str', 'ct') make this extremely difficult to say smoothly. Creates awkward mouth positions and breaks voiceover flow.",
        confidence=95
    ))
    
    # Add rhythm issue
    review.add_issue(ReadabilityIssue(
        issue_type=ReadabilityIssueType.RHYTHM,
        severity=ReadabilitySeverity.HIGH,
        text="Cryptographic Catastrophic Crypts",
        suggestion="Secret Digital Dangers",
        explanation="Three long words in a row create poor rhythm. No natural breathing points.",
        confidence=90
    ))
    
    review.summary = "Critical mouthfeel issues make this title unsuitable for voiceover"
    
    print(f"\nTitle: {review.title_text}")
    print(f"Version: {review.title_version}")
    print(f"Overall Score: {review.overall_score}/100")
    print(f"Status: {'✓ PASSES' if review.passes else '✗ FAILS'}")
    print(f"\nIssues Found: {len(review.issues)}")
    print(f"  Critical: {review.critical_count}")
    print(f"  High: {review.high_count}")
    
    print("\nDetailed Issues:")
    for i, issue in enumerate(review.issues, 1):
        print(f"\n  Issue {i}: {issue.issue_type.value.upper()}")
        print(f"    Severity: {issue.severity.value.upper()}")
        print(f"    Problem: '{issue.text}'")
        print(f"    Suggestion: '{issue.suggestion}'")
        print(f"    Explanation: {issue.explanation}")
    
    print(f"\nSummary: {review.summary}")
    
    if not review.passes:
        print("\n→ Return to Title Refinement with voiceover feedback")
    
    return review


def example_title_with_listening_clarity_issues():
    """Example: Title that's unclear when listened to."""
    print("\n" + "="*80)
    print("Example 3: Title with Listening Clarity Issues")
    print("="*80)
    
    review = TitleReadabilityReview(
        title_id="title-clarity-001",
        title_text="Their There They're: Three Ways",
        title_version="v4",
        overall_score=70
    )
    
    # Add listening clarity issue
    review.add_issue(ReadabilityIssue(
        issue_type=ReadabilityIssueType.LISTENING_CLARITY,
        severity=ReadabilitySeverity.CRITICAL,
        text="Their There They're",
        suggestion="Three Common Mix-ups",
        explanation="Homophones are confusing when only heard. Listeners cannot distinguish between 'their', 'there', and 'they're' in audio format.",
        confidence=98
    ))
    
    review.summary = "Title relies on visual distinction - fails for audio-only format"
    review.voiceover_notes.append("Avoid homophones in titles meant for voiceover")
    
    print(f"\nTitle: {review.title_text}")
    print(f"Version: {review.title_version}")
    print(f"Overall Score: {review.overall_score}/100")
    print(f"Status: {'✓ PASSES' if review.passes else '✗ FAILS'}")
    
    print("\nCritical Issues:")
    for issue in review.get_critical_issues():
        print(f"  • {issue.explanation}")
    
    print("\nVoiceover Notes:")
    for note in review.voiceover_notes:
        print(f"  • {note}")
    
    if not review.passes:
        print("\n→ Return to Title Refinement - needs audio-friendly alternative")
    
    return review


def example_title_with_good_rhythm():
    """Example: Title with excellent rhythm and pacing."""
    print("\n" + "="*80)
    print("Example 4: Title with Excellent Rhythm")
    print("="*80)
    
    review = TitleReadabilityReview(
        title_id="title-rhythm-001",
        title_text="Lost City: Found Again",
        title_version="v3",
        overall_score=92
    )
    
    review.summary = "Excellent rhythm with natural pauses and clear pacing"
    review.voiceover_notes.append("Short words create natural rhythm: Lost (pause) City (pause) Found (pause) Again")
    review.voiceover_notes.append("Colon provides dramatic pause point")
    review.voiceover_notes.append("Parallel structure ('Lost'/'Found') creates memorable contrast")
    
    print(f"\nTitle: {review.title_text}")
    print(f"Version: {review.title_version}")
    print(f"Overall Score: {review.overall_score}/100")
    print(f"Status: {'✓ PASSES' if review.passes else '✗ FAILS'}")
    
    print("\nVoiceover Notes:")
    for note in review.voiceover_notes:
        print(f"  • {note}")
    
    if review.passes:
        print("\n→ Ready for Finalization")
    
    return review


def example_title_length_issues():
    """Example: Title with length issues for voiceover."""
    print("\n" + "="*80)
    print("Example 5: Title with Length Issues")
    print("="*80)
    
    review = TitleReadabilityReview(
        title_id="title-length-001",
        title_text="The Comprehensive and Detailed Investigation into the Mysterious Disappearance of the Ancient Artifact",
        title_version="v3",
        overall_score=55
    )
    
    # Add length issue
    review.add_issue(ReadabilityIssue(
        issue_type=ReadabilityIssueType.LENGTH,
        severity=ReadabilitySeverity.HIGH,
        text="The Comprehensive and Detailed Investigation into the Mysterious Disappearance of the Ancient Artifact",
        suggestion="The Ancient Artifact Mystery",
        explanation="Title is too long (98 characters). Voiceover audience will lose attention. Optimal length for voiceover: 30-60 characters.",
        confidence=95
    ))
    
    # Add engagement issue
    review.add_issue(ReadabilityIssue(
        issue_type=ReadabilityIssueType.ENGAGEMENT,
        severity=ReadabilitySeverity.MEDIUM,
        text="too wordy and academic",
        suggestion="more punchy and mysterious",
        explanation="Long academic phrasing reduces engagement for audio format",
        confidence=85
    ))
    
    review.summary = "Title too long for effective voiceover delivery"
    
    print(f"\nTitle: {review.title_text}")
    print(f"Length: {len(review.title_text)} characters")
    print(f"Version: {review.title_version}")
    print(f"Overall Score: {review.overall_score}/100")
    print(f"Status: {'✓ PASSES' if review.passes else '✗ FAILS'}")
    
    print("\nHigh Priority Issues:")
    for issue in review.get_high_priority_issues():
        print(f"\n  • {issue.issue_type.value.upper()}")
        print(f"    Suggestion: '{issue.suggestion}'")
        print(f"    Reason: {issue.explanation}")
    
    if not review.passes:
        print("\n→ Return to Title Refinement - shorten significantly")
    
    return review


def example_workflow_integration():
    """Example: Complete workflow integration."""
    print("\n" + "="*80)
    print("Example 6: Workflow Integration (MVP-019)")
    print("="*80)
    
    review = TitleReadabilityReview(
        title_id="title-workflow-001",
        title_text="Echoes of Tomorrow: A Journey",
        title_version="v5",
        overall_score=88
    )
    
    # Add metadata for workflow tracking
    review.metadata["script_id"] = "script-123"
    review.metadata["script_version"] = "v5"
    review.metadata["previous_stage"] = "MVP-018-Editing-Review"
    review.metadata["workflow_stage"] = "MVP-019-Title-Readability"
    
    review.summary = "Good voiceover title with minor improvements possible"
    review.voiceover_notes.append("Natural rhythm with good pacing")
    review.voiceover_notes.append("'Echoes' and 'Journey' create nice bookends")
    review.quick_fixes.append("Consider emphasizing 'Tomorrow' for impact")
    
    # Add minor issue
    review.add_issue(ReadabilityIssue(
        issue_type=ReadabilityIssueType.VOICEOVER_FLOW,
        severity=ReadabilitySeverity.LOW,
        text="of Tomorrow",
        suggestion="from Tomorrow",
        explanation="'From' might flow slightly better than 'of' before 'Tomorrow'",
        confidence=75
    ))
    
    print(f"\nTitle: {review.title_text}")
    print(f"Version: {review.title_version}")
    print(f"Overall Score: {review.overall_score}/100")
    print(f"Status: {'✓ PASSES' if review.passes else '✗ FAILS'}")
    
    print("\nWorkflow Metadata:")
    for key, value in review.metadata.items():
        print(f"  {key}: {value}")
    
    print(f"\nIssues: {len(review.issues)} (all low priority)")
    print(f"\nQuick Fixes Available: {len(review.quick_fixes)}")
    for fix in review.quick_fixes:
        print(f"  • {fix}")
    
    if review.passes:
        print("\n✓ Stage 19 (MVP-019) COMPLETE")
        print("→ Ready for Finalization")
    
    # Demonstrate serialization for workflow
    print("\nSerialized for Workflow:")
    import json
    print(json.dumps(review.to_dict(), indent=2)[:500] + "...")
    
    return review


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("TITLE READABILITY REVIEW (MVP-019) - EXAMPLES")
    print("Stage 19: Final review for voiceover suitability")
    print("="*80)
    
    # Run all examples
    example_perfect_voiceover_title()
    example_title_with_mouthfeel_issues()
    example_title_with_listening_clarity_issues()
    example_title_with_good_rhythm()
    example_title_length_issues()
    example_workflow_integration()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("""
The Title Readability Review (MVP-019) is the FINAL review stage for titles.
It focuses exclusively on voiceover suitability:

Key Checks:
  • Mouthfeel: Is it easy to say aloud?
  • Rhythm: Does it have natural pacing?
  • Listening Clarity: Is it clear when heard (not read)?
  • Pronunciation: Any difficult words?
  • Voiceover Flow: Does it flow naturally when spoken?
  • Length: Appropriate length for audio format?
  • Engagement: Engaging when listened to?

Workflow:
  MVP-018 (Editing Review passes) → MVP-019 (Title Readability) → {
      PASS: Ready for Finalization
      FAIL: Return to Title Refinement with voiceover feedback
  }

This is the last quality gate before finalization!
    """)


if __name__ == "__main__":
    main()
