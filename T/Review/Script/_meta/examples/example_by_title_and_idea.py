"""Example usage of review_script_by_title_and_idea module.

This example demonstrates MVP-005: Reviewing script v1 against title v1 and idea.
"""

import sys
from pathlib import Path

# Add T/Idea/Model to path for src.idea import
_repo_root = Path(__file__).parent.parent.parent.parent.parent.parent
_idea_model_path = _repo_root / "T" / "Idea" / "Model"
if str(_idea_model_path) not in sys.path:
    sys.path.insert(0, str(_idea_model_path))

from src.idea import ContentGenre, Idea
from T.Review.Script import review_script_by_title_and_idea


def example_horror_short():
    """Example: Review a horror short script."""
    print("=" * 80)
    print("Example 1: Horror Short Script Review")
    print("=" * 80)

    # Create an Idea for a horror short
    idea = Idea(
        title="The Echo",
        concept="A girl hears her own future voice warning her",
        premise="A teenage girl starts hearing a voice that sounds identical to her own, "
        "giving her warnings about the future. When the warnings come true, "
        "she realizes the voice is her future self trying to prevent her death.",
        logline="A girl discovers she can hear her own future thoughts—and they're telling her to run.",
        hook="Last night I woke up... but my body kept sleeping.",
        genre=ContentGenre.HORROR,
        target_platforms=["youtube", "tiktok"],
        target_formats=["video", "audio"],
        length_target="60 seconds video",
    )

    # Title v1
    title = "The Voice That Knows Tomorrow"

    # Script v1
    script = """
    Last night I heard a whisper in the darkness. It sounded exactly like my own voice,
    but I knew it couldn't be me. The voice was telling me things that hadn't happened yet.
    
    At first, I thought I was going crazy. But then the predictions started coming true.
    Small things at first - my mom would call exactly when the voice said she would.
    Then bigger things. The voice warned me about an accident, and it happened.
    
    Now the voice is saying something terrifying: "Run. Now. Don't look back."
    But when I looked in the mirror, I saw myself... but it wasn't me. It was my future self,
    trying to warn my past self. And I realized - I'm already too late.
    """

    # Review the script
    review = review_script_by_title_and_idea(
        script_text=script, title=title, idea=idea, target_length_seconds=60
    )

    # Display results
    print(f"\nScript ID: {review.script_id}")
    print(f"Title: {review.script_title}")
    print(f"Overall Score: {review.overall_score}%")
    print(f"Title Alignment: {review.metadata['title_alignment_score']}%")
    print(f"Idea Alignment: {review.metadata['idea_alignment_score']}%")
    print(f"Target Length: {review.target_length.value}")
    print(f"Current Length: {review.current_length_seconds}s")
    print(f"Is YouTube Short: {review.is_youtube_short}")
    print(f"Needs Major Revision: {review.needs_major_revision}")

    print(f"\nStrengths ({len(review.strengths)}):")
    for strength in review.strengths[:3]:
        print(f"  - {strength}")

    print(f"\nCategory Scores:")
    for cat_score in review.category_scores:
        print(f"  - {cat_score.category.value}: {cat_score.score}%")

    print(f"\nTop Improvement Points ({len(review.improvement_points)} total):")
    for point in review.improvement_points[:3]:
        print(f"  - [{point.priority}] {point.title}")
        print(f"    Impact: +{point.impact_score}%")
        print(f"    {point.description}")

    print(f"\nQuick Wins:")
    for win in review.quick_wins:
        print(f"  - {win}")

    if review.primary_concern:
        print(f"\nPrimary Concern: {review.primary_concern}")

    print()


def example_educational_content():
    """Example: Review an educational content script."""
    print("=" * 80)
    print("Example 2: Educational Content Script Review")
    print("=" * 80)

    # Create an Idea for educational content
    idea = Idea(
        title="How Quantum Computers Work",
        concept="Explaining quantum computing through everyday analogies",
        premise="Quantum computers process information fundamentally differently than regular computers. "
        "This explainer uses everyday analogies to make the complex simple.",
        logline="Your computer checks one path at a time; quantum computers check all paths at once.",
        hook="What if your GPS could explore every possible route simultaneously?",
        genre=ContentGenre.EDUCATIONAL,
        target_platforms=["youtube", "medium"],
        target_formats=["video", "text"],
        length_target="3-5 minutes",
    )

    title = "Quantum Computing Explained Simply"

    script = """
    What if your GPS could explore every possible route simultaneously? That's essentially
    what quantum computers do with information.
    
    Traditional computers process information one step at a time. They check one route,
    then another, then another. But quantum computers use quantum mechanics to explore
    all routes at once. This is called quantum superposition.
    
    Think of it like this: a regular computer is like reading a book page by page.
    A quantum computer is like being able to read all pages simultaneously and instantly
    know which page has the answer you're looking for.
    
    This fundamental difference makes quantum computers incredibly powerful for certain
    types of problems - like breaking encryption, simulating molecules, or optimizing
    complex systems. They're not faster at everything, but for specific tasks, they're
    revolutionary.
    """

    # Review the script
    review = review_script_by_title_and_idea(script_text=script, title=title, idea=idea)

    # Display results
    print(f"\nScript ID: {review.script_id}")
    print(f"Overall Score: {review.overall_score}%")
    print(f"Title Alignment: {review.metadata['title_alignment_score']}%")
    print(f"Idea Alignment: {review.metadata['idea_alignment_score']}%")

    print(f"\nCategory Scores:")
    for cat_score in review.category_scores:
        print(f"  - {cat_score.category.value}: {cat_score.score}%")
        if cat_score.reasoning:
            print(f"    {cat_score.reasoning}")

    print(f"\nHigh-Priority Improvements:")
    high_priority = review.get_high_priority_improvements()
    if high_priority:
        for point in high_priority[:3]:
            print(f"  - {point.title} (Impact: +{point.impact_score}%)")
            if point.suggested_fix:
                print(f"    Fix: {point.suggested_fix}")
    else:
        print("  No high-priority improvements needed!")

    print()


def example_poor_alignment():
    """Example: Script with poor alignment to title and idea."""
    print("=" * 80)
    print("Example 3: Poor Alignment - Pizza Recipe vs Mystery Title")
    print("=" * 80)

    idea = Idea(
        title="The Mystery of the Lost City",
        concept="Archaeologists discover an ancient civilization",
        premise="A team finds ruins that challenge everything we know about history",
        genre=ContentGenre.MYSTERY,
    )

    title = "Uncovering the Lost Civilization"

    # Completely unrelated script
    script = """
    The best pizza recipes require three key ingredients: quality flour, fresh yeast,
    and good mozzarella cheese. Start by mixing your dough and letting it rise for
    at least two hours.
    
    The secret to a perfect crust is high heat - at least 450°F. Once your dough is ready,
    stretch it gently to avoid tearing. Add your sauce sparingly - too much will make it soggy.
    Finally, add your toppings and bake until the crust is golden brown.
    """

    review = review_script_by_title_and_idea(script, title, idea)

    print(f"\nOverall Score: {review.overall_score}%")
    print(f"Title Alignment: {review.metadata['title_alignment_score']}%")
    print(f"Idea Alignment: {review.metadata['idea_alignment_score']}%")
    print(f"Needs Major Revision: {review.needs_major_revision}")

    print(f"\nPrimary Concern: {review.primary_concern}")

    print(f"\nCritical Issues:")
    for point in review.improvement_points:
        if point.priority == "high":
            print(f"  - {point.title}")
            print(f"    {point.description}")
            if point.specific_example:
                print(f"    Example: {point.specific_example}")

    print()


def main():
    """Run all examples."""
    example_horror_short()
    example_educational_content()
    example_poor_alignment()

    print("=" * 80)
    print("Examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
