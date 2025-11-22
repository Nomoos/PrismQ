"""Example usage of ToneReview module for MVP-015.

This example demonstrates how to use the ToneReview model to evaluate
script tone, style alignment, and voice consistency.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import json
from T.Review.Tone import (
    ToneReview,
    ToneIssue,
    ToneIssueType,
    ToneSeverity
)


def example_basic_tone_review():
    """Example: Basic tone review creation."""
    print("=" * 60)
    print("Example 1: Basic Tone Review")
    print("=" * 60)
    
    review = ToneReview(
        script_id="script-001",
        script_version="v3",
        overall_score=88,
        emotional_intensity_score=85,
        style_alignment_score=92,
        voice_consistency_score=88,
        audience_fit_score=86,
        target_tone="dark suspense",
        target_audience="US female 14-29"
    )
    
    print(f"\nReview: {review}")
    print(f"Passes: {review.passes}")
    print(f"Target Tone: {review.target_tone}")
    print(f"Target Audience: {review.target_audience}")
    print()


def example_with_issues():
    """Example: Tone review with detected issues."""
    print("=" * 60)
    print("Example 2: Tone Review with Issues")
    print("=" * 60)
    
    review = ToneReview(
        script_id="script-002",
        script_version="v3",
        overall_score=82,
        target_tone="dark horror",
        target_audience="Adults 18+"
    )
    
    # Add emotional intensity issue
    review.add_issue(ToneIssue(
        issue_type=ToneIssueType.EMOTIONAL_INTENSITY,
        severity=ToneSeverity.MEDIUM,
        line_number=42,
        text="This is really exciting and fun!",
        suggestion="This discovery was deeply unsettling.",
        explanation="Emotional intensity too upbeat for dark horror tone"
    ))
    
    # Add style alignment issue
    review.add_issue(ToneIssue(
        issue_type=ToneIssueType.STYLE_ALIGNMENT,
        severity=ToneSeverity.HIGH,
        line_number=67,
        text="The hilarious mishap made everyone laugh.",
        suggestion="The grotesque scene filled them with dread.",
        explanation="Comedy style doesn't align with horror genre"
    ))
    
    # Add voice consistency issue
    review.add_issue(ToneIssue(
        issue_type=ToneIssueType.VOICE_CONSISTENCY,
        severity=ToneSeverity.MEDIUM,
        line_number=89,
        text="We decided to investigate the strange sounds.",
        suggestion="I decided to investigate the strange sounds.",
        explanation="POV shift from first person singular to plural"
    ))
    
    print(f"\nReview: {review}")
    print(f"\nIssues found: {len(review.issues)}")
    print(f"  - Critical: {review.critical_count}")
    print(f"  - High: {review.high_count}")
    print(f"  - Medium: {review.medium_count}")
    print(f"  - Low: {review.low_count}")
    
    print("\nHigh priority issues:")
    for issue in review.get_high_priority_issues():
        print(f"  Line {issue.line_number}: {issue.issue_type.value}")
        print(f"    Problem: {issue.text}")
        print(f"    Suggestion: {issue.suggestion}")
        print(f"    Explanation: {issue.explanation}")
        print()


def example_failing_review():
    """Example: Tone review that fails."""
    print("=" * 60)
    print("Example 3: Failing Tone Review")
    print("=" * 60)
    
    review = ToneReview(
        script_id="script-003",
        script_version="v3",
        overall_score=72,  # Below threshold of 80
        target_tone="dark suspense"
    )
    
    review.add_issue(ToneIssue(
        issue_type=ToneIssueType.STYLE_ALIGNMENT,
        severity=ToneSeverity.CRITICAL,
        line_number=15,
        text="This slapstick comedy scene had everyone in stitches!",
        suggestion="The chilling atmosphere grew oppressive.",
        explanation="Complete genre mismatch - comedy in horror script"
    ))
    
    print(f"\nReview: {review}")
    print(f"Passes: {review.passes}")
    print(f"Overall Score: {review.overall_score}% (threshold: {review.pass_threshold}%)")
    
    if not review.passes:
        print("\n⚠️  Review FAILED - returning to Script Refinement (Stage 11)")
        print("\nCritical issues that must be fixed:")
        for issue in review.get_critical_issues():
            print(f"  Line {issue.line_number}: {issue.explanation}")
    print()


def example_json_output():
    """Example: JSON output for tone analysis."""
    print("=" * 60)
    print("Example 4: JSON Output")
    print("=" * 60)
    
    review = ToneReview(
        script_id="script-004",
        script_version="v3",
        overall_score=88,
        emotional_intensity_score=87,
        style_alignment_score=90,
        voice_consistency_score=88,
        audience_fit_score=86,
        target_tone="psychological thriller",
        target_audience="Adults 25-45",
        summary="Strong tone consistency with minor adjustments needed",
        primary_concerns=["One POV shift in middle section"],
        strengths=["Excellent emotional pacing", "Consistent dark atmosphere"],
        recommendations=["Maintain first-person throughout", "Deepen suspense in Act 2"]
    )
    
    review.add_issue(ToneIssue(
        issue_type=ToneIssueType.VOICE_CONSISTENCY,
        severity=ToneSeverity.LOW,
        line_number=125,
        text="They wondered what secrets the house held.",
        suggestion="I wondered what secrets the house held.",
        explanation="Brief POV shift from first to third person"
    ))
    
    # Convert to JSON
    review_data = review.to_dict()
    json_output = json.dumps(review_data, indent=2)
    
    print("\nJSON Output:")
    print(json_output)
    print()


def example_tone_styles():
    """Example: Testing various tone styles."""
    print("=" * 60)
    print("Example 5: Various Tone Styles")
    print("=" * 60)
    
    tone_styles = [
        ("dark suspense", "Female 14-29"),
        ("horror", "Adults 18+"),
        ("psychological thriller", "Adults 25-45"),
        ("mystery", "General audience"),
        ("dark comedy", "Adults 21+"),
        ("dramatic", "Young adults 18-30")
    ]
    
    for tone, audience in tone_styles:
        review = ToneReview(
            script_id=f"script-{tone.replace(' ', '-')}",
            overall_score=85,
            target_tone=tone,
            target_audience=audience
        )
        
        status = "✓ PASS" if review.passes else "✗ FAIL"
        print(f"{status} | Tone: {tone:25s} | Audience: {audience:20s} | Score: {review.overall_score}%")
    
    print()


def example_workflow_integration():
    """Example: Integration with MVP workflow."""
    print("=" * 60)
    print("Example 6: MVP Workflow Integration")
    print("=" * 60)
    
    print("\nMVP-015: Tone Review Workflow")
    print("-" * 60)
    
    # Simulate script passing grammar review (MVP-014)
    print("✓ MVP-014 (Grammar Review): PASSED")
    print("→ Proceeding to MVP-015 (Tone Review)...")
    
    # Create tone review
    review = ToneReview(
        script_id="script-workflow-001",
        script_version="v3",
        overall_score=89,
        emotional_intensity_score=88,
        style_alignment_score=91,
        voice_consistency_score=87,
        audience_fit_score=90,
        target_tone="dark suspense",
        target_audience="US female 14-29"
    )
    
    # Add minor issue
    review.add_issue(ToneIssue(
        issue_type=ToneIssueType.EMOTIONAL_INTENSITY,
        severity=ToneSeverity.LOW,
        line_number=203,
        text="The situation was quite pleasant.",
        suggestion="The situation grew increasingly ominous.",
        explanation="Slightly too positive for dark tone"
    ))
    
    print(f"\nTone Review Results:")
    print(f"  Overall Score: {review.overall_score}%")
    print(f"  Emotional Intensity: {review.emotional_intensity_score}%")
    print(f"  Style Alignment: {review.style_alignment_score}%")
    print(f"  Voice Consistency: {review.voice_consistency_score}%")
    print(f"  Audience Fit: {review.audience_fit_score}%")
    print(f"  Issues: {len(review.issues)} (Low: {review.low_count})")
    
    if review.passes:
        print("\n✓ MVP-015 (Tone Review): PASSED")
        print("→ Proceeding to MVP-016...")
    else:
        print("\n✗ MVP-015 (Tone Review): FAILED")
        print("→ Returning to Script Refinement (Stage 11) with feedback")
    
    print()


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "ToneReview Module Examples (MVP-015)" + " " * 11 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    example_basic_tone_review()
    example_with_issues()
    example_failing_review()
    example_json_output()
    example_tone_styles()
    example_workflow_integration()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
