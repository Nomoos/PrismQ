"""Example usage of Title Acceptance Gate (MVP-012).

This example demonstrates how to use the Title Acceptance Gate module
in the PrismQ MVP workflow to evaluate whether a title is ready to
proceed or needs further refinement.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(project_root))

from T.Review.Title.Acceptance import (
    check_title_acceptance,
    AcceptanceCriteria
)


def example_basic_usage():
    """Example 1: Basic acceptance check."""
    print("=" * 70)
    print("Example 1: Basic Title Acceptance Check")
    print("=" * 70)
    
    result = check_title_acceptance(
        title_text="The Echo Mystery: Dark Secrets Revealed",
        title_version="v3",
        script_text="""
        In the old house on Elm Street, a mysterious echo reveals dark secrets.
        Every sound carries a message from the past. The echo grows stronger
        as the mystery deepens and secrets are unveiled one by one.
        """,
        script_version="v3"
    )
    
    print(f"\nTitle: {result.title_text}")
    print(f"Version: {result.title_version}")
    print(f"Status: {'✓ ACCEPTED' if result.accepted else '✗ NOT ACCEPTED'}")
    print(f"Overall Score: {result.overall_score}/100")
    print(f"Reason: {result.reason}")
    
    if not result.accepted:
        print("\nRecommendations:")
        for rec in result.recommendations:
            print(f"  - {rec}")
    
    print()


def example_detailed_analysis():
    """Example 2: Detailed criterion analysis."""
    print("=" * 70)
    print("Example 2: Detailed Criterion Analysis")
    print("=" * 70)
    
    result = check_title_acceptance(
        title_text="The Haunting Echo",
        title_version="v4",
        script_text="A haunting echo fills the old mansion, revealing secrets of the past",
        script_version="v4"
    )
    
    print(f"\nTitle: {result.title_text}")
    print(f"\nDetailed Scores:")
    print("-" * 70)
    
    for cr in result.criteria_results:
        status = "✓" if cr.passed else "✗"
        print(f"{status} {cr.criterion.value.upper()}: {cr.score}/100 (threshold: {cr.threshold})")
        print(f"  Reasoning: {cr.reasoning}")
        print()
    
    print(f"Overall Score: {result.overall_score}/100")
    print(f"Final Status: {'ACCEPTED' if result.accepted else 'NOT ACCEPTED'}")
    print()


def example_iterative_refinement():
    """Example 3: Iterative refinement through versions."""
    print("=" * 70)
    print("Example 3: Iterative Refinement (v3 → v4 → v5)")
    print("=" * 70)
    
    script_text = """
    A mysterious echo in an old mansion reveals hidden secrets from the past.
    The mystery deepens as the echo becomes stronger and more secrets emerge.
    """
    
    titles = [
        ("v3", "The House"),
        ("v4", "The Echo Mystery"),
        ("v5", "The Echo Mystery: Secrets of the Old Mansion")
    ]
    
    for version, title_text in titles:
        result = check_title_acceptance(
            title_text=title_text,
            title_version=version,
            script_text=script_text,
            script_version=version
        )
        
        status = "✓ ACCEPTED" if result.accepted else "✗ NOT ACCEPTED"
        print(f"\n{version}: '{title_text}'")
        print(f"  Status: {status}")
        print(f"  Score: {result.overall_score}/100")
        
        if not result.accepted:
            print(f"  Action: Loop to MVP-008 for review and refinement")
        else:
            print(f"  Action: Proceed to MVP-013 (Script Acceptance)")
    
    print()


def example_acceptance_vs_rejection():
    """Example 4: Comparing accepted vs rejected titles."""
    print("=" * 70)
    print("Example 4: Acceptance vs Rejection Scenarios")
    print("=" * 70)
    
    script_text = """
    A gripping mystery unfolds in an old house where echoes reveal dark secrets.
    The investigation leads to shocking discoveries hidden for decades.
    """
    
    test_cases = [
        ("High Quality", "The Echo Mystery: Hidden Secrets Revealed"),
        ("Medium Quality", "The Mystery House"),
        ("Low Quality", "Title"),
        ("Very Low Quality", "X")
    ]
    
    for label, title_text in test_cases:
        result = check_title_acceptance(
            title_text=title_text,
            title_version="v3",
            script_text=script_text,
            script_version="v3"
        )
        
        status = "✓" if result.accepted else "✗"
        print(f"\n{status} {label}: '{title_text}'")
        print(f"  Score: {result.overall_score}/100")
        
        # Show criterion scores
        clarity = result.get_criterion_result(AcceptanceCriteria.CLARITY)
        engagement = result.get_criterion_result(AcceptanceCriteria.ENGAGEMENT)
        alignment = result.get_criterion_result(AcceptanceCriteria.SCRIPT_ALIGNMENT)
        
        print(f"  Clarity: {clarity.score}/100 {'✓' if clarity.passed else '✗'}")
        print(f"  Engagement: {engagement.score}/100 {'✓' if engagement.passed else '✗'}")
        print(f"  Alignment: {alignment.score}/100 {'✓' if alignment.passed else '✗'}")
    
    print()


def example_workflow_integration():
    """Example 5: Integration with MVP workflow."""
    print("=" * 70)
    print("Example 5: MVP Workflow Integration")
    print("=" * 70)
    
    print("\nSimulating MVP-012 workflow with iteration limit...")
    
    script_text = """
    The haunting mystery begins with an echo in the old house on Elm Street.
    Dark secrets are revealed through the mysterious echo as the story unfolds.
    Each echo brings new revelations about the hidden past of the house.
    """
    
    # Simulate iterative refinement
    titles = [
        ("v3", "Story"),  # Poor title
        ("v4", "The Echo Story"),  # Better
        ("v5", "The Echo Mystery: Secrets of Elm Street")  # Good
    ]
    
    for version, title_text in titles:
        print(f"\n--- Iteration: {version} ---")
        print(f"Title: '{title_text}'")
        
        result = check_title_acceptance(
            title_text=title_text,
            title_version=version,
            script_text=script_text,
            script_version=version
        )
        
        print(f"Score: {result.overall_score}/100")
        
        if result.accepted:
            print(f"✓ ACCEPTED at {version}")
            print("→ Proceeding to MVP-013 (Script Acceptance Gate)")
            break
        else:
            print(f"✗ NOT ACCEPTED")
            print(f"→ Reason: {result.reason}")
            if result.recommendations:
                print(f"→ Top recommendation: {result.recommendations[0]}")
            print("→ Looping to MVP-008 (Title Review) → MVP-009 (Title Refinement)")
    
    print()


def example_json_export():
    """Example 6: JSON export for API integration."""
    print("=" * 70)
    print("Example 6: JSON Export for API Integration")
    print("=" * 70)
    
    import json
    
    result = check_title_acceptance(
        title_text="The Mystery Unveiled: Echoes from the Past",
        title_version="v3",
        script_text="A mystery from the past is unveiled through mysterious echoes",
        script_version="v3"
    )
    
    # Convert to JSON
    result_dict = result.to_dict()
    result_json = json.dumps(result_dict, indent=2)
    
    print("\nJSON Output (abbreviated):")
    print("-" * 70)
    
    # Show key fields
    print(json.dumps({
        "title_text": result_dict["title_text"],
        "title_version": result_dict["title_version"],
        "accepted": result_dict["accepted"],
        "overall_score": result_dict["overall_score"],
        "reason": result_dict["reason"],
        "criteria_count": len(result_dict["criteria_results"]),
        "timestamp": result_dict["timestamp"]
    }, indent=2))
    
    print("\n(Full JSON structure available via result.to_dict())")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Title Acceptance Gate (MVP-012) - Usage Examples")
    print("=" * 70 + "\n")
    
    # Run all examples
    example_basic_usage()
    example_detailed_analysis()
    example_iterative_refinement()
    example_acceptance_vs_rejection()
    example_workflow_integration()
    example_json_export()
    
    print("=" * 70)
    print("Examples completed successfully!")
    print("=" * 70)
