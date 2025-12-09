"""Example usage of Script Acceptance Gate (MVP-013).

This example demonstrates how to use the check_script_acceptance function
to evaluate whether a script is ready to proceed to quality reviews.
"""

import sys
from pathlib import Path

# Add project root to path (6 levels up from this file)
project_root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(project_root))

# Import from the module
from T.Review.Script.Acceptance.acceptance import check_script_acceptance


def main():
    """Demonstrate script acceptance checking."""

    print("=" * 70)
    print("Script Acceptance Gate (MVP-013) - Example Usage")
    print("=" * 70)
    print()

    # Example 1: Well-formed script (ACCEPTED)
    print("Example 1: High-Quality Script")
    print("-" * 70)

    script_v3 = """
    In the old house on Elm Street, mysterious echoes fill every room.
    The echoes carry messages from the past, revealing long-hidden secrets.
    As we investigate deeper, we discover clues in the walls and floors.
    Each sound brings us closer to understanding the mystery.
    The echoes grow stronger, more insistent, demanding to be heard.
    Finally, we uncover the truth that has been waiting for decades.
    The mystery of the echo is solved, bringing peace to the house.
    """

    title = "The Echo Mystery"

    result = check_script_acceptance(script_text=script_v3, title=title, script_version="v3")

    print(f"Title: {title}")
    print(f"Script Version: v3")
    print()
    print(f"Accepted: {result['accepted']}")
    print(f"Overall Score: {result['overall_score']}/100")
    print(f"Completeness: {result['completeness_score']}/100")
    print(f"Coherence: {result['coherence_score']}/100")
    print(f"Alignment: {result['alignment_score']}/100")
    print()
    print(f"Decision: {result['reason']}")
    print()

    if result["accepted"]:
        print("✓ ACCEPTED - Proceed to MVP-014 (Quality Reviews)")
    else:
        print("✗ NOT ACCEPTED - Loop back to MVP-010 (Script Review)")
        print()
        print("Issues:")
        for issue in result["issues"]:
            print(f"  - {issue}")
        print()
        print("Suggestions:")
        for suggestion in result["suggestions"]:
            print(f"  - {suggestion}")

    print()
    print()

    # Example 2: Incomplete script (NOT ACCEPTED)
    print("Example 2: Incomplete Script")
    print("-" * 70)

    script_incomplete = "Just a short fragment without proper structure"
    title_incomplete = "The Great Story"

    result2 = check_script_acceptance(
        script_text=script_incomplete, title=title_incomplete, script_version="v3"
    )

    print(f"Title: {title_incomplete}")
    print(f"Script Version: v3")
    print()
    print(f"Accepted: {result2['accepted']}")
    print(f"Overall Score: {result2['overall_score']}/100")
    print(f"Completeness: {result2['completeness_score']}/100")
    print(f"Coherence: {result2['coherence_score']}/100")
    print(f"Alignment: {result2['alignment_score']}/100")
    print()
    print(f"Decision: {result2['reason']}")
    print()

    if result2["accepted"]:
        print("✓ ACCEPTED - Proceed to MVP-014 (Quality Reviews)")
    else:
        print("✗ NOT ACCEPTED - Loop back to MVP-010 (Script Review)")
        print()
        print("Issues:")
        for issue in result2["issues"]:
            print(f"  - {issue}")
        print()
        print("Suggestions:")
        for suggestion in result2["suggestions"]:
            print(f"  - {suggestion}")

    print()
    print()

    # Example 3: Misaligned script (NOT ACCEPTED)
    print("Example 3: Misaligned Script")
    print("-" * 70)

    script_misaligned = """
    The spaceship launches into orbit around the distant planet.
    Astronauts conduct experiments in the zero-gravity environment.
    Mission control monitors all systems from the ground station.
    The journey through space continues for several months.
    New discoveries are made every day in the cosmos.
    """

    title_misaligned = "The Haunted Mansion Mystery"

    result3 = check_script_acceptance(
        script_text=script_misaligned, title=title_misaligned, script_version="v4"
    )

    print(f"Title: {title_misaligned}")
    print(f"Script Version: v4")
    print()
    print(f"Accepted: {result3['accepted']}")
    print(f"Overall Score: {result3['overall_score']}/100")
    print(f"Completeness: {result3['completeness_score']}/100")
    print(f"Coherence: {result3['coherence_score']}/100")
    print(f"Alignment: {result3['alignment_score']}/100")
    print()
    print(f"Decision: {result3['reason']}")
    print()

    if result3["accepted"]:
        print("✓ ACCEPTED - Proceed to MVP-014 (Quality Reviews)")
    else:
        print("✗ NOT ACCEPTED - Loop back to MVP-010 (Script Review)")
        print()
        print("Issues:")
        for issue in result3["issues"]:
            print(f"  - {issue}")
        print()
        print("Suggestions:")
        for suggestion in result3["suggestions"]:
            print(f"  - {suggestion}")

    print()
    print("=" * 70)
    print("End of Examples")
    print("=" * 70)


if __name__ == "__main__":
    main()
