#!/usr/bin/env python3
"""Example: Using flavors with idea refinement.

This example demonstrates how to use the flavor system to guide
AI-powered idea refinement with different thematic orientations.

All 93 variant templates have been transformed into flavors.
"""

import sys
from pathlib import Path

# Add src to path for imports
SCRIPT_DIR = Path(__file__).parent.absolute()
CREATION_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(CREATION_ROOT / "src"))

from ai_generator import AIIdeaGenerator
from flavors import (
    list_flavors,
    list_flavor_categories,
    get_flavor_description,
    search_flavors_by_keyword,
    get_flavor_count,
)


def example_1_list_all_flavors():
    """Example 1: List all available flavors."""
    print("\n" + "=" * 70)
    print("Example 1: List All Available Flavors")
    print("=" * 70)
    
    total = get_flavor_count()
    all_flavors = list_flavors()
    
    print(f"\nTotal flavors available: {total}")
    print(f"\n(All {total} variant templates have been transformed into flavors)")
    print("\nFirst 10 flavors:")
    for i, flavor in enumerate(all_flavors[:10], 1):
        print(f"  {i:2}. {flavor}")
    print(f"  ... and {total - 10} more")


def example_2_browse_by_category():
    """Example 2: Browse flavors by category."""
    print("\n" + "=" * 70)
    print("Example 2: Browse Flavors by Category")
    print("=" * 70)
    
    categories = list_flavor_categories()
    
    print(f"\nTotal categories: {len(categories)}")
    print("\nSample categories:")
    
    for cat_name in list(categories.keys())[:5]:
        flavors = categories[cat_name]
        print(f"\n{cat_name}:")
        for flavor in flavors[:3]:
            print(f"  - {flavor}")
        if len(flavors) > 3:
            print(f"  ... and {len(flavors) - 3} more")


def example_3_search_flavors():
    """Example 3: Search for flavors by keyword."""
    print("\n" + "=" * 70)
    print("Example 3: Search Flavors by Keyword")
    print("=" * 70)
    
    keywords = ["emotional", "mystery", "transformation", "romantic"]
    
    for keyword in keywords:
        matches = search_flavors_by_keyword(keyword)
        print(f"\nFlavors with '{keyword}': {len(matches)} found")
        for flavor in matches[:3]:
            print(f"  - {flavor}")
        if len(matches) > 3:
            print(f"  ... and {len(matches) - 3} more")


def example_4_use_flavor_with_ai():
    """Example 4: Use a flavor with AI generation."""
    print("\n" + "=" * 70)
    print("Example 4: Using Flavors with AI Generation")
    print("=" * 70)
    
    generator = AIIdeaGenerator()
    
    if not generator.available:
        print("\nNOTE: Ollama is not available. This is a demonstration of the API.")
        print("When Ollama is running, this would generate AI output.\n")
    
    input_text = "Acadia Night Hikers"
    flavors_to_try = [
        "Mystery + Unease",
        "Emotional Drama + Growth",
        "Introspective Transformation",
    ]
    
    print(f"\nInput: '{input_text}'")
    print("\nTrying different flavors:\n")
    
    for flavor in flavors_to_try:
        print(f"Flavor: {flavor}")
        print("-" * 60)
        
        if generator.available:
            result = generator.generate_with_custom_prompt(
                input_text=input_text,
                prompt_template_name="idea_improvement",
                flavor=flavor
            )
            print(f"Result: {result}\n")
        else:
            print(f"(Would generate 5 refined sentences with {flavor} orientation)")
            print(f"Example API call:")
            print(f"  generator.generate_with_custom_prompt(")
            print(f"      input_text='{input_text}',")
            print(f"      prompt_template_name='idea_improvement',")
            print(f"      flavor='{flavor}'")
            print(f"  )\n")


def example_5_flavor_details():
    """Example 5: Get details about specific flavors."""
    print("\n" + "=" * 70)
    print("Example 5: Flavor Details")
    print("=" * 70)
    
    sample_flavors = [
        "Emotional Drama + Growth",
        "Mystery/Curiosity Gap",
        "Identity + Empowerment",
    ]
    
    for flavor in sample_flavors:
        print(f"\n{flavor}:")
        desc = get_flavor_description(flavor)
        print(f"  Description: {desc[:80]}...")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("Flavor System Examples for PrismQ")
    print("=" * 70)
    
    print("\nThe flavor system transforms all 93 variant templates into")
    print("thematic orientations that guide AI-powered idea refinement.")
    
    # Run examples
    example_1_list_all_flavors()
    example_2_browse_by_category()
    example_3_search_flavors()
    example_5_flavor_details()
    
    # Ask about AI examples
    print("\n" + "=" * 70)
    print("Would you like to see the AI generation examples?")
    print("(These require Ollama to be running)")
    response = input("\nRun AI examples? (y/n): ").strip().lower()
    
    if response == 'y':
        example_4_use_flavor_with_ai()
    else:
        print("\nSkipping AI generation examples.")
        print("\nTo use flavors with AI:")
        print("  from ai_generator import AIIdeaGenerator")
        print("  generator = AIIdeaGenerator()")
        print("  result = generator.generate_with_custom_prompt(")
        print("      input_text='Your text',")
        print("      prompt_template_name='idea_improvement',")
        print("      flavor='Mystery + Unease'")
        print("  )")
    
    print("\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
