"""Example usage of T.Title.From.Idea module.

This example demonstrates how to generate title variants from an Idea.
"""

import os
import sys

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../Idea/Model/src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../Idea/Model"))

from title_generator import TitleConfig, TitleGenerator, generate_titles_from_idea

from idea import ContentGenre, Idea, IdeaStatus


def example_basic_usage():
    """Example: Basic title generation from idea."""
    print("=" * 80)
    print("Example 1: Basic Title Generation (10 Variants)")
    print("=" * 80)

    # Create an idea
    idea = Idea(
        title="The Future of Artificial Intelligence",
        concept="Exploring how AI will transform industries and society in the next decade",
        genre=ContentGenre.EDUCATIONAL,
        keywords=["AI", "technology", "future", "innovation"],
        themes=["artificial intelligence", "digital transformation"],
        status=IdeaStatus.DRAFT,
    )

    # Generate title variants (default is now 10)
    generator = TitleGenerator()
    variants = generator.generate_from_idea(idea)

    # Display results
    print(f"\nOriginal Idea Title: {idea.title}")
    print(f"Concept: {idea.concept}\n")
    print(f"Generated {len(variants)} title variants:\n")

    for i, variant in enumerate(variants, 1):
        print(f"{i}. [{variant.style.upper()}] {variant.text}")
        print(f"   Length: {variant.length} chars | Score: {variant.score:.2f}")
        print(f"   Keywords: {', '.join(variant.keywords[:3])}")
        print()


def example_with_config():
    """Example: Title generation with custom configuration."""
    print("=" * 80)
    print("Example 2: Custom Configuration")
    print("=" * 80)

    # Create custom config
    config = TitleConfig(
        num_variants=4, min_length=30, max_length=70, focus="engagement", include_keywords=True
    )

    # Create an idea
    idea = Idea(
        title="Machine Learning in Healthcare",
        concept="How ML is revolutionizing medical diagnosis and treatment",
        genre=ContentGenre.EDUCATIONAL,
        keywords=["machine-learning", "healthcare", "diagnosis"],
        status=IdeaStatus.DRAFT,
    )

    # Generate with custom config
    generator = TitleGenerator(config)
    variants = generator.generate_from_idea(idea)

    print(f"\nOriginal Title: {idea.title}")
    print(f"Max Length: {config.max_length} chars\n")
    print(f"Generated {len(variants)} variants:\n")

    for i, variant in enumerate(variants, 1):
        print(f"{i}. {variant.text} [{variant.style}]")
        print(f"   {variant.length} chars | Score: {variant.score:.2f}\n")


def example_from_concept_only():
    """Example: Generate titles from concept when no title exists."""
    print("=" * 80)
    print("Example 3: Generation from Concept Only")
    print("=" * 80)

    # Create idea with only concept
    idea = Idea(
        title="",  # No title provided
        concept="A comprehensive guide to understanding blockchain technology and its applications in finance, supply chain, and beyond",
        genre=ContentGenre.EDUCATIONAL,
        status=IdeaStatus.DRAFT,
    )

    # Generate titles
    variants = generate_titles_from_idea(idea, num_variants=3)

    print(f"\nConcept: {idea.concept}\n")
    print(f"Generated {len(variants)} title variants:\n")

    for i, variant in enumerate(variants, 1):
        print(f"{i}. {variant.text}")
        print(f"   Style: {variant.style} | {variant.length} chars\n")


def example_entertainment_genre():
    """Example: Titles for entertainment content."""
    print("=" * 80)
    print("Example 4: Entertainment Genre Titles")
    print("=" * 80)

    # Create entertainment idea
    idea = Idea(
        title="Space Exploration Adventures",
        concept="The thrilling journey of humanity's quest to explore the cosmos",
        genre=ContentGenre.ENTERTAINMENT,
        keywords=["space", "exploration", "adventure", "cosmos"],
        status=IdeaStatus.DRAFT,
    )

    # Generate variants
    generator = TitleGenerator()
    variants = generator.generate_from_idea(idea, num_variants=5)

    print(f"\nGenre: {idea.genre.value}")
    print(f"Original Title: {idea.title}\n")
    print("Generated title variants:\n")

    for variant in variants:
        print(f"• {variant.text}")
        print(f"  [{variant.style} style - Score: {variant.score:.2f}]\n")


def example_variant_comparison():
    """Example: Compare different variant styles."""
    print("=" * 80)
    print("Example 5: Variant Style Comparison (All 10 Styles)")
    print("=" * 80)

    # Create idea
    idea = Idea(
        title="Cybersecurity Best Practices",
        concept="Essential security measures for protecting digital assets",
        genre=ContentGenre.EDUCATIONAL,
        status=IdeaStatus.DRAFT,
    )

    # Generate all 10 variants
    generator = TitleGenerator()
    variants = generator.generate_from_idea(idea, num_variants=10)

    print(f"\nOriginal: {idea.title}\n")
    print("All 10 Style Variants:\n")

    # Display all variants
    for variant in variants:
        print(f"{variant.style.upper():20} | {variant.text}")

    print("\n" + "-" * 80)
    print("\nStyle Characteristics:")
    print("• DIRECT:            Straightforward, clear title")
    print("• QUESTION:          Poses a question to engage readers")
    print("• HOW-TO:            Action-oriented, instructional")
    print("• CURIOSITY:         Intriguing, creates interest")
    print("• AUTHORITATIVE:     Expert perspective, comprehensive")
    print("• LISTICLE:          Number-based, digestible format")
    print("• PROBLEM-SOLUTION:  Addresses challenges and solutions")
    print("• COMPARISON:        Contrasts different approaches")
    print("• ULTIMATE-GUIDE:    Comprehensive resource positioning")
    print("• BENEFIT:           Value proposition, reader-focused")


def example_to_dict_export():
    """Example: Export variants to dictionary format."""
    print("=" * 80)
    print("Example 6: Export to Dictionary")
    print("=" * 80)

    # Create idea
    idea = Idea(
        title="Cloud Computing Fundamentals",
        concept="Understanding cloud infrastructure and services",
        status=IdeaStatus.DRAFT,
    )

    # Generate variants
    variants = generate_titles_from_idea(idea, num_variants=3)

    print(f"\nOriginal: {idea.title}\n")
    print("Exported Variants (Dictionary Format):\n")

    for i, variant in enumerate(variants, 1):
        variant_dict = variant.to_dict()
        print(f"Variant {i}:")
        print(f"  {variant_dict}")
        print()


def main():
    """Run all examples."""
    examples = [
        example_basic_usage,
        example_with_config,
        example_from_concept_only,
        example_entertainment_genre,
        example_variant_comparison,
        example_to_dict_export,
    ]

    for example_func in examples:
        try:
            example_func()
            print("\n")
        except Exception as e:
            print(f"Error in {example_func.__name__}: {e}\n")


if __name__ == "__main__":
    main()
