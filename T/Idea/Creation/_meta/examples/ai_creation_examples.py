"""
Example usage of AI-powered Idea Creation with local LLMs via Ollama.

This example demonstrates how to use the IdeaCreator to generate Ideas
using local AI models optimized for RTX 5090 and other high-end GPUs.
"""

import os
import sys

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../Model/src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../Model"))

from ai_generator import AIConfig
from creation import CreationConfig, IdeaCreator

from idea import ContentGenre


def example_default_usage():
    """Example 1: Default usage - creates 10 ideas using AI (or fallback)."""
    print("=" * 80)
    print("Example 1: Default Usage (10 ideas with AI)")
    print("=" * 80)

    creator = IdeaCreator()

    # Default: creates 10 ideas from a title
    ideas = creator.create_from_title("The Future of Artificial Intelligence")

    print(f"\nCreated {len(ideas)} ideas:")
    for i, idea in enumerate(ideas, 1):
        print(f"\n{i}. {idea.title}")
        print(f"   Concept: {idea.concept[:100]}...")
        print(f"   Keywords: {', '.join(idea.keywords[:5])}")


def example_custom_number():
    """Example 2: Custom number of ideas."""
    print("\n" + "=" * 80)
    print("Example 2: Custom Number of Ideas")
    print("=" * 80)

    creator = IdeaCreator()

    # Create 5 ideas instead of default 10
    ideas = creator.create_from_title("Quantum Computing Explained", num_ideas=5)

    print(f"\nCreated {len(ideas)} ideas with custom count")


def example_with_targeting():
    """Example 3: Ideas with platform and format targeting."""
    print("\n" + "=" * 80)
    print("Example 3: Platform and Format Targeting")
    print("=" * 80)

    creator = IdeaCreator()

    # Create ideas targeted for specific platforms and formats
    ideas = creator.create_from_title(
        "Social Media Trends 2024",
        num_ideas=10,
        target_platforms=["youtube", "tiktok", "instagram"],
        target_formats=["video", "short-form"],
        genre=ContentGenre.ENTERTAINMENT,
        length_target="60 seconds",
    )

    print(f"\nCreated {len(ideas)} ideas for social media platforms")
    print(f"Target platforms: {ideas[0].target_platforms}")
    print(f"Target formats: {ideas[0].target_formats}")
    print(f"Genre: {ideas[0].genre}")


def example_from_description():
    """Example 4: Creating ideas from a description."""
    print("\n" + "=" * 80)
    print("Example 4: Creating Ideas from Description")
    print("=" * 80)

    creator = IdeaCreator()

    description = """
    Explore the ethical implications of AI in healthcare, focusing on 
    privacy concerns, bias in algorithms, and the balance between 
    innovation and patient safety.
    """

    ideas = creator.create_from_description(
        description,
        num_ideas=10,
        genre=ContentGenre.EDUCATIONAL,
        target_platforms=["medium", "youtube", "linkedin"],
    )

    print(f"\nCreated {len(ideas)} ideas from description:")
    for i, idea in enumerate(ideas[:3], 1):  # Show first 3
        print(f"\n{i}. {idea.title}")
        print(f"   Premise: {idea.premise[:150]}...")


def example_rtx_5090_optimized():
    """Example 5: RTX 5090 optimized configuration."""
    print("\n" + "=" * 80)
    print("Example 5: RTX 5090 Optimized Configuration")
    print("=" * 80)

    # Configure for best quality using RTX 5090 recommended models
    config = CreationConfig(
        use_ai=True,
        ai_model="qwen3:30b",  # Best for RTX 5090
        ai_temperature=0.8,
        default_num_ideas=10,
    )

    creator = IdeaCreator(config)

    ideas = creator.create_from_title("The Ethics of AI Development")

    print(f"\nUsing model: {config.ai_model}")
    print(f"Created {len(ideas)} high-quality ideas")

    if ideas:
        print(f"\nFirst idea:")
        print(f"Title: {ideas[0].title}")
        print(f"Concept: {ideas[0].concept}")
        print(f"Logline: {ideas[0].logline}")


def example_alternative_models():
    """Example 6: Using alternative AI models."""
    print("\n" + "=" * 80)
    print("Example 6: Alternative AI Models")
    print("=" * 80)

    # Qwen 3.30b - Excellent for creative writing and balance
    config_qwen = CreationConfig(use_ai=True, ai_model="qwen3:30b", ai_temperature=0.9)

    # Command-R - Great for structured output
    config_command = CreationConfig(use_ai=True, ai_model="command-r:35b", ai_temperature=0.7)

    print("\nAvailable model configurations:")
    print(f"1. Qwen 3:30B: qwen3:30b (Default, best overall)")
    print(f"2. Qwen 2.5 72B: qwen2.5:72b-q4_K_M (Creative writing, higher resource)")
    print(f"3. Command-R 35B: command-r:35b (Structured output)")
    print(f"4. Mixtral 8x7B: mixtral:8x7b-q4_K_M (Balanced performance)")


def example_no_ai_fallback():
    """Example 7: Fallback mode without AI."""
    print("\n" + "=" * 80)
    print("Example 7: Fallback Mode (No AI)")
    print("=" * 80)

    # Explicitly disable AI to use fallback generation
    config = CreationConfig(use_ai=False)
    creator = IdeaCreator(config)

    ideas = creator.create_from_title("Machine Learning Basics", num_ideas=5)

    print(f"\nCreated {len(ideas)} ideas using fallback generation (no AI)")
    print("Note: Fallback uses placeholder generation for testing/development")


def example_batch_creation():
    """Example 8: Batch creation for multiple topics."""
    print("\n" + "=" * 80)
    print("Example 8: Batch Creation for Multiple Topics")
    print("=" * 80)

    creator = IdeaCreator()

    topics = ["AI in Education", "Sustainable Technology", "Future of Work"]

    all_ideas = []
    for topic in topics:
        ideas = creator.create_from_title(topic, num_ideas=3)
        all_ideas.extend(ideas)
        print(f"\nCreated {len(ideas)} ideas for: {topic}")

    print(f"\nTotal ideas created: {len(all_ideas)}")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("AI-Powered Idea Creation Examples")
    print("Optimized for RTX 5090 with Ollama")
    print("=" * 80)

    examples = [
        example_default_usage,
        example_custom_number,
        example_with_targeting,
        example_from_description,
        example_rtx_5090_optimized,
        example_alternative_models,
        example_no_ai_fallback,
        example_batch_creation,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nExample failed: {e}")

    print("\n" + "=" * 80)
    print("Examples completed!")
    print("=" * 80)
    print("\nNote: If Ollama is not running, all examples will use fallback generation.")
    print("To use AI generation:")
    print("1. Install Ollama: https://ollama.com/")
    print("2. Pull a model: ollama pull qwen3:30b")
    print("3. Run the server: ollama serve")
    print("4. Run these examples again")


if __name__ == "__main__":
    main()
