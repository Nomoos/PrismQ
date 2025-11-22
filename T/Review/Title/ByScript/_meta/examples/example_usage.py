"""Example usage of PrismQ.T.Review.Title.ByScript (v2) module.

This example demonstrates how to use the v2 title review functionality
to evaluate refined titles against refined scripts with improvement tracking.
"""

import sys
import os
import json

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../..')))

from T.Review.Title.ByScript import (
    review_title_by_script_v2,
    get_improvement_summary
)
from T.Review.Title.ByScriptAndIdea import review_title_by_script_and_idea


def example_basic_v2_review():
    """Example 1: Basic v2 title review."""
    print("=" * 80)
    print("Example 1: Basic v2 Title Review")
    print("=" * 80)
    
    title_v2 = "The Echo - A Haunting Discovery"
    script_v2 = """
    The Echo - A Haunting Discovery is a suspenseful horror short film that follows
    Sarah, a paranormal investigator, as she explores the abandoned Mercy Hospital.
    
    Strange echoes seem to anticipate her thoughts and movements. Through her
    investigation, Sarah uncovers the hospital's tragic history and discovers that
    the echoes are manifestations of past trauma. The haunting sounds lead her
    to a shocking revelation about the true nature of the phenomena.
    """
    
    review = review_title_by_script_v2(
        title_text=title_v2,
        script_text=script_v2,
        title_version="v2",
        script_version="v2"
    )
    
    print(f"\nTitle: {review.title_text}")
    print(f"Version: {review.title_version}")
    print(f"Overall Score: {review.overall_score}%")
    print(f"Script Alignment: {review.script_alignment_score}%")
    print(f"Engagement Score: {review.engagement_score}%")
    print(f"\nTop Improvements:")
    for imp in review.improvement_points[:3]:
        print(f"  - [{imp.priority}] {imp.title}: {imp.description}")
    print()


def example_v1_to_v2_comparison():
    """Example 2: Compare v1 and v2 reviews."""
    print("=" * 80)
    print("Example 2: v1 to v2 Comparison with Improvement Tracking")
    print("=" * 80)
    
    # Original v1 title and script
    title_v1 = "The Echo"
    script_v1 = """
    The Echo is a horror short film about mysterious sounds in an abandoned hospital.
    Sarah investigates strange echoes that seem to repeat her thoughts.
    As she delves deeper, she discovers the source of the haunting echoes.
    """
    idea = "A psychological horror story about mysterious sounds in an abandoned hospital"
    
    # Create v1 review
    v1_review = review_title_by_script_and_idea(
        title_text=title_v1,
        script_text=script_v1,
        idea_summary=idea,
        title_version="v1",
        script_version="v1"
    )
    
    print(f"\nv1 Title: {title_v1}")
    print(f"v1 Overall Score: {v1_review.overall_score}%")
    print(f"v1 Script Alignment: {v1_review.script_alignment_score}%")
    
    # Improved v2 title and script
    title_v2 = "The Echo - A Haunting Discovery"
    script_v2 = """
    The Echo - A Haunting Discovery is a suspenseful horror short film that follows
    Sarah, a paranormal investigator, as she explores the abandoned Mercy Hospital.
    
    Strange echoes seem to anticipate her thoughts and movements. Through her
    investigation, Sarah uncovers the hospital's tragic history and discovers that
    the echoes are manifestations of past trauma. The haunting sounds lead her
    to a shocking revelation about the true nature of the phenomena.
    """
    
    # Create v2 review with v1 comparison
    v2_review = review_title_by_script_v2(
        title_text=title_v2,
        script_text=script_v2,
        title_version="v2",
        script_version="v2",
        previous_review=v1_review
    )
    
    print(f"\nv2 Title: {title_v2}")
    print(f"v2 Overall Score: {v2_review.overall_score}%")
    print(f"v2 Script Alignment: {v2_review.script_alignment_score}%")
    print(f"Iteration Number: {v2_review.iteration_number}")
    
    # Get improvement summary
    summary = get_improvement_summary(v1_review, v2_review)
    
    print(f"\n--- Improvement Summary ---")
    print(f"Overall Assessment: {summary['overall_assessment']}")
    print(f"Score Change: {summary['v1_score']}% -> {summary['v2_score']}% (Δ{summary['overall_delta']:+d}%)")
    
    if summary['improvements']:
        print(f"\nImprovements:")
        for imp in summary['improvements']:
            print(f"  - {imp['category']}: {imp['feedback']} (Δ{imp['delta']:+d}%)")
    
    if summary['regressions']:
        print(f"\nRegressions:")
        for reg in summary['regressions']:
            print(f"  - {reg['category']}: {reg['feedback']} (Δ{reg['delta']:+d}%)")
    
    print(f"\nRecommendation: {summary['recommendation']}")
    print(f"\nNext Steps:")
    for step in summary['next_steps']:
        print(f"  - {step}")
    print()


def example_json_export():
    """Example 3: Export review as JSON."""
    print("=" * 80)
    print("Example 3: JSON Export of v2 Review")
    print("=" * 80)
    
    title_v2 = "The Echo - A Haunting Discovery"
    script_v2 = """
    The Echo - A Haunting Discovery follows Sarah as she explores an abandoned
    hospital, uncovering the mystery behind haunting echoes that seem to know
    her thoughts. A suspenseful journey into the paranormal.
    """
    
    review = review_title_by_script_v2(
        title_text=title_v2,
        script_text=script_v2
    )
    
    # Convert to JSON
    review_dict = review.to_dict()
    json_output = json.dumps(review_dict, indent=2)
    
    print("\nJSON Output (first 1000 chars):")
    print(json_output[:1000])
    print("...\n")


def example_multiple_iterations():
    """Example 4: Track multiple iterations (v1 -> v2 -> v3)."""
    print("=" * 80)
    print("Example 4: Multiple Iterations (v1 -> v2 -> v3)")
    print("=" * 80)
    
    idea = "A psychological horror story about mysterious sounds"
    
    # v1
    title_v1 = "The Echo"
    script_v1 = "A horror short about mysterious sounds in an abandoned hospital."
    
    v1_review = review_title_by_script_and_idea(
        title_text=title_v1,
        script_text=script_v1,
        idea_summary=idea
    )
    
    print(f"\nv1: {title_v1}")
    print(f"    Score: {v1_review.overall_score}%")
    
    # v2
    title_v2 = "The Echo - A Haunting Discovery"
    script_v2 = "The Echo follows Sarah as she explores an abandoned hospital, uncovering mysterious echoes and haunting discoveries."
    
    v2_review = review_title_by_script_v2(
        title_text=title_v2,
        script_text=script_v2,
        title_version="v2",
        previous_review=v1_review
    )
    
    print(f"\nv2: {title_v2}")
    print(f"    Score: {v2_review.overall_score}% (Δ{v2_review.overall_score - v1_review.overall_score:+d}%)")
    
    # v3
    title_v3 = "The Echo - Uncovering Dark Secrets in the Abandoned Hospital"
    script_v3 = "The Echo - A suspenseful horror journey as Sarah investigates paranormal echoes in the abandoned Mercy Hospital, uncovering dark secrets and haunting discoveries."
    
    v3_review = review_title_by_script_v2(
        title_text=title_v3,
        script_text=script_v3,
        title_version="v3",
        previous_review=v2_review
    )
    
    print(f"\nv3: {title_v3}")
    print(f"    Score: {v3_review.overall_score}% (Δ{v3_review.overall_score - v2_review.overall_score:+d}%)")
    
    print(f"\nImprovement Trajectory:")
    print(f"  Iteration 1 (v1): {v1_review.overall_score}%")
    print(f"  Iteration 2 (v2): {v2_review.overall_score}%")
    print(f"  Iteration 3 (v3): {v3_review.overall_score}%")
    print(f"  Total Change: {v3_review.overall_score - v1_review.overall_score:+d}%")
    print()


def example_regression_detection():
    """Example 5: Detect regressions in v2."""
    print("=" * 80)
    print("Example 5: Regression Detection")
    print("=" * 80)
    
    idea = "A psychological horror story"
    script_v1 = "A horror short about mysterious sounds in an abandoned hospital with haunting echoes."
    
    # Good v1
    title_v1 = "The Echo - Mysterious Sounds in the Abandoned Hospital"
    v1_review = review_title_by_script_and_idea(
        title_text=title_v1,
        script_text=script_v1,
        idea_summary=idea
    )
    
    print(f"\nv1 Title: {title_v1}")
    print(f"v1 Score: {v1_review.overall_score}%")
    
    # Worse v2 (simulating a bad revision)
    title_v2 = "Video"
    script_v2 = "A horror short about mysterious sounds in an abandoned hospital with haunting echoes."
    
    v2_review = review_title_by_script_v2(
        title_text=title_v2,
        script_text=script_v2,
        previous_review=v1_review
    )
    
    print(f"\nv2 Title: {title_v2}")
    print(f"v2 Score: {v2_review.overall_score}%")
    
    summary = get_improvement_summary(v1_review, v2_review)
    
    print(f"\nAssessment: {summary['overall_assessment']}")
    print(f"Score Change: {summary['overall_delta']:+d}%")
    
    if summary['regressions']:
        print("\n⚠️  REGRESSIONS DETECTED:")
        for reg in summary['regressions']:
            print(f"  - {reg['category']}: {reg['feedback']}")
    
    print(f"\nRecommendation: {summary['recommendation']}")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "PrismQ Title Review v2 Examples" + " " * 27 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")
    
    example_basic_v2_review()
    example_v1_to_v2_comparison()
    example_json_export()
    example_multiple_iterations()
    example_regression_detection()
    
    print("=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
