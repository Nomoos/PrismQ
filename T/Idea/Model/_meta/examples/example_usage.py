"""Example usage of PrismQ.Idea.Model

This example demonstrates how to create and work with Idea instances,
including fusion from IdeaInspiration sources.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.idea import ContentGenre, Idea, IdeaStatus


def example_basic_idea():
    """Example: Creating a basic Idea."""
    print("=" * 60)
    print("Example 1: Creating a Basic Idea")
    print("=" * 60)

    idea = Idea(
        title="The Digital Phantom Mystery",
        concept="An investigation into unsolved internet mysteries",
        purpose="Engage true crime audience with unique digital angle",
        emotional_quality="mysterious, suspenseful, intriguing",
        target_audience="True crime enthusiasts aged 18-35",
        target_demographics={
            "age_range": "18-35",
            "interests": "true_crime,technology",
            "regions": "US,UK,CA",
        },
        target_platform="youtube",
        genre=ContentGenre.TRUE_CRIME,
        style="narrative investigation",
        keywords=["mystery", "unsolved", "internet", "investigation", "digital"],
        outline="1. Hook\n2. Case Introduction\n3. Investigation\n4. Theory\n5. Conclusion",
        skeleton="Mystery → Evidence → Analysis → Resolution",
    )

    print(f"\nCreated: {idea}")
    print(f"Title: {idea.title}")
    print(f"Platform: {idea.target_platform}")
    print(f"Genre: {idea.genre.value}")
    print(f"Keywords: {', '.join(idea.keywords)}")
    print(f"Status: {idea.status.value}")
    print(f"Version: {idea.version}")


def example_manual_idea():
    """Example: Creating Idea without IdeaInspiration sources."""
    print("\n" + "=" * 60)
    print("Example 2: Manual Idea (Without IdeaInspiration)")
    print("=" * 60)

    # Ideas can be created independently without source inspirations
    idea = Idea(
        title="Python Beginner Tutorial Series",
        concept="Teaching Python fundamentals through practical projects",
        purpose="Help absolute beginners learn programming",
        target_audience="Complete programming beginners",
        target_platform="youtube",
        genre=ContentGenre.EDUCATIONAL,
        keywords=["python", "programming", "tutorial", "beginner", "coding"],
        outline="1. Setup\n2. Variables\n3. Functions\n4. Projects",
        skeleton="Intro → Theory → Practice → Challenge",
        inspiration_ids=[],  # No source inspirations
    )

    print(f"\nCreated manually: {idea}")
    print(f"Title: {idea.title}")
    print(f"Has inspirations: {len(idea.inspiration_ids) > 0}")
    print(f"Keywords: {', '.join(idea.keywords)}")
    print(f"Outline: {idea.outline}")
    print(f"Skeleton: {idea.skeleton}")


def example_from_inspirations():
    """Example: Creating Idea from IdeaInspiration sources."""
    print("\n" + "=" * 60)
    print("Example 3: Fusion from Multiple Inspirations")
    print("=" * 60)

    # Mock IdeaInspiration objects
    class MockInspiration:
        def __init__(self, source_id, title, scores):
            self.source_id = source_id
            self.title = title
            self.contextual_category_scores = scores

    inspirations = [
        MockInspiration(
            "insp-001",
            "Unsolved Internet Mysteries",
            {"region:us": 85, "age:18-24": 78, "platform:youtube": 90},
        ),
        MockInspiration(
            "insp-002",
            "True Crime Technology",
            {"region:us": 88, "age:25-34": 92, "platform:youtube": 87},
        ),
        MockInspiration(
            "insp-003",
            "Digital Detective Work",
            {"region:uk": 82, "age:18-24": 85, "platform:tiktok": 75},
        ),
    ]

    # Fuse inspirations into a single Idea
    idea = Idea.from_inspirations(
        inspirations=inspirations,
        title="Digital Detectives: Solving Internet Cold Cases",
        concept="Using modern technology and digital forensics to investigate and solve internet mysteries",
        purpose="Combine true crime storytelling with tech education",
        emotional_quality="suspenseful, investigative, educational",
        target_audience="Tech-savvy true crime fans",
        target_platform="youtube",
        genre=ContentGenre.TRUE_CRIME,
        style="investigative documentary",
        created_by="AI-ContentAgent-001",
    )

    print(f"\nFused from {len(inspirations)} inspirations:")
    for insp in inspirations:
        print(f"  - {insp.title} ({insp.source_id})")

    print(f"\nCreated: {idea}")
    print(f"Linked inspirations: {idea.inspiration_ids}")
    print(f"Potential scores: {idea.potential_scores}")
    print(f"Created by: {idea.created_by}")


def example_versioning():
    """Example: Working with Idea versions."""
    print("\n" + "=" * 60)
    print("Example 4: Version Management")
    print("=" * 60)

    # Create initial idea
    idea_v1 = Idea(
        title="Mystery Podcast Series",
        concept="Weekly podcast exploring unsolved mysteries",
        target_platform="podcast",
        genre=ContentGenre.MYSTERY,
        status=IdeaStatus.DRAFT,
    )

    print(f"\nVersion 1: {idea_v1}")
    print(f"  Status: {idea_v1.status.value}")
    print(f"  Version: {idea_v1.version}")

    # Update to validated version
    idea_v2 = idea_v1.create_new_version(
        concept="Weekly podcast exploring unsolved mysteries with expert interviews",
        status=IdeaStatus.VALIDATED,
        notes="Added expert interview component after team review",
    )

    print(f"\nVersion 2: {idea_v2}")
    print(f"  Status: {idea_v2.status.value}")
    print(f"  Version: {idea_v2.version}")
    print(f"  Notes: {idea_v2.notes}")

    # Update to approved version
    idea_v3 = idea_v2.create_new_version(
        purpose="Build engaged community around mystery content",
        status=IdeaStatus.APPROVED,
        notes="Approved for production with community engagement focus",
    )

    print(f"\nVersion 3: {idea_v3}")
    print(f"  Status: {idea_v3.status.value}")
    print(f"  Version: {idea_v3.version}")
    print(f"  Purpose: {idea_v3.purpose}")


def example_serialization():
    """Example: Serialization and deserialization."""
    print("\n" + "=" * 60)
    print("Example 5: Serialization")
    print("=" * 60)

    original = Idea(
        title="Tech Documentary",
        concept="Exploring the future of AI",
        target_platform="youtube",
        genre=ContentGenre.DOCUMENTARY,
        potential_scores={"platform:youtube": 88, "region:us": 90, "age:25-34": 85},
    )

    print(f"\nOriginal: {original}")

    # Convert to dict
    data = original.to_dict()
    print(f"\nSerialized to dict with {len(data)} fields")
    print(f"Sample fields: title='{data['title']}', platform='{data['target_platform']}'")

    # Restore from dict
    restored = Idea.from_dict(data)
    print(f"\nRestored: {restored}")
    print(f"Match: {restored.title == original.title and restored.concept == original.concept}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("PrismQ.Idea.Model - Example Usage")
    print("=" * 60)

    example_basic_idea()
    example_manual_idea()
    example_from_inspirations()
    example_versioning()
    example_serialization()

    print("\n" + "=" * 60)
    print("Examples completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
