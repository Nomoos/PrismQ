#!/usr/bin/env python3
"""Example: Comparing all prompt variations.

This example demonstrates all 6 prompt variations for idea refinement
and shows how to choose the right one for your needs.
"""

import sys
from pathlib import Path

# Add src to path for imports
SCRIPT_DIR = Path(__file__).parent.absolute()
CREATION_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(CREATION_ROOT / "src"))

from ai_generator import AIIdeaGenerator, list_available_prompts


def show_available_variations():
    """Show all available prompt variations."""
    print("\n" + "=" * 70)
    print("Available Prompt Variations")
    print("=" * 70)
    
    prompts = list_available_prompts()
    improvement_prompts = [p for p in prompts if p.startswith('idea_improvement')]
    
    variations = {
        'idea_improvement': 'Current Default - Balanced approach',
        'idea_improvement_analytical': 'Analytical Structure - More organized thinking',
        'idea_improvement_contrast': 'Contrast-and-Refine - Sharper thematic output',
        'idea_improvement_minimalist': 'Minimalist Precision - Cleaner, denser ideas',
        'idea_improvement_academic': 'Academic Interpretation - More depth',
        'idea_improvement_high_constraint': 'High-Constraint Logic - Most resistant to drift',
        'idea_improvement_growth': 'Interpretive Growth - Best for emotional themes',
    }
    
    print("\n6 Prompt Variations Available:\n")
    for i, prompt in enumerate(sorted(improvement_prompts), 1):
        desc = variations.get(prompt, 'Template')
        print(f"{i}. {prompt}")
        print(f"   {desc}\n")


def compare_variations_demo():
    """Demonstrate comparing different variations."""
    print("\n" + "=" * 70)
    print("Comparing Prompt Variations")
    print("=" * 70)
    
    generator = AIIdeaGenerator()
    
    if not generator.available:
        print("\nNOTE: Ollama is not available.")
        print("This demonstrates the API for comparing variations.\n")
    
    input_text = "Acadia Night Hikers"
    flavor = "Mystery + Unease"
    
    variations = [
        ('idea_improvement_analytical', 'Analytical Structure'),
        ('idea_improvement_contrast', 'Contrast-and-Refine'),
        ('idea_improvement_minimalist', 'Minimalist Precision'),
    ]
    
    print(f"\nInput: '{input_text}'")
    print(f"Flavor: {flavor}\n")
    
    for template_name, display_name in variations:
        print(f"\n{display_name}:")
        print("-" * 60)
        
        if generator.available:
            result = generator.generate_with_custom_prompt(
                input_text=input_text,
                prompt_template_name=template_name,
                flavor=flavor
            )
            print(result)
        else:
            print(f"Would use template: {template_name}")
            print(f"API call:")
            print(f"  generator.generate_with_custom_prompt(")
            print(f"      input_text='{input_text}',")
            print(f"      prompt_template_name='{template_name}',")
            print(f"      flavor='{flavor}'")
            print(f"  )")


def choosing_guide():
    """Guide for choosing the right variation."""
    print("\n" + "=" * 70)
    print("Choosing the Right Variation")
    print("=" * 70)
    
    print("""
BY CONTENT TYPE:

Conceptual/Abstract Ideas
  → idea_improvement_analytical or idea_improvement_academic

Dramatic/Conflict-Driven
  → idea_improvement_contrast

Technical/Precise
  → idea_improvement_minimalist or idea_improvement_high_constraint

Character/Emotional
  → idea_improvement_growth

Pipeline/Automated
  → idea_improvement_high_constraint or idea_improvement_minimalist

BY OUTPUT REQUIREMENTS:

Need consistency?
  → idea_improvement_high_constraint

Need depth?
  → idea_improvement_academic or idea_improvement_analytical

Need brevity?
  → idea_improvement_minimalist

Need drama?
  → idea_improvement_contrast

Need emotional arc?
  → idea_improvement_growth

COMPARISON MATRIX:

                        Logic   Drift     Emotional  Technical
                        Strength Resist   Depth      Clarity
Analytical Structure    ★★★★★   ★★★★☆    ★★★☆☆     ★★★★★
Contrast-and-Refine     ★★★★☆   ★★★☆☆    ★★★★☆     ★★★☆☆
Minimalist Precision    ★★★★☆   ★★★★★    ★★☆☆☆     ★★★★★
Academic Interpretation ★★★★★   ★★★★☆    ★★★☆☆     ★★★★★
High-Constraint Logic   ★★★★★   ★★★★★    ★★☆☆☆     ★★★★★
Interpretive Growth     ★★★☆☆   ★★★☆☆    ★★★★★     ★★★☆☆
""")


def ab_testing_example():
    """Show how to A/B test variations."""
    print("\n" + "=" * 70)
    print("A/B Testing Variations")
    print("=" * 70)
    
    print("""
To find the best variation for your workflow:

```python
from ai_generator import AIIdeaGenerator

generator = AIIdeaGenerator()

# Test multiple variations
variations = [
    "idea_improvement_analytical",
    "idea_improvement_contrast",
    "idea_improvement_minimalist",
]

test_ideas = [
    "The Last Lighthouse",
    "Digital Nomad Dreams",
    "Underground Garden Project",
]

results = {}
for idea in test_ideas:
    results[idea] = {}
    for variation in variations:
        result = generator.generate_with_custom_prompt(
            input_text=idea,
            prompt_template_name=variation,
            flavor="Mystery + Unease"
        )
        results[idea][variation] = result

# Evaluate which produces best results
for idea, outputs in results.items():
    print(f"\\nIdea: {idea}")
    for variation, output in outputs.items():
        print(f"  {variation}: {output[:80]}...")
```

Evaluation criteria:
- Consistency across inputs
- Appropriateness for your use case
- Quality of conceptual refinement
- Absence of drift or unwanted elements
""")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("Prompt Variation Examples for PrismQ")
    print("=" * 70)
    
    print("\n6 high-quality prompt variations optimized for Qwen/Ollama.")
    print("Each produces different strengths for different use cases.")
    
    # Run examples
    show_available_variations()
    choosing_guide()
    ab_testing_example()
    
    # Ask about running comparison
    print("\n" + "=" * 70)
    print("Would you like to see a live comparison?")
    print("(Requires Ollama to be running)")
    response = input("\nRun comparison? (y/n): ").strip().lower()
    
    if response == 'y':
        compare_variations_demo()
    else:
        print("\nSkipping live comparison.")
    
    print("\n" + "=" * 70)
    print("See PROMPT_VARIATIONS.md for complete details")
    print("=" * 70)


if __name__ == "__main__":
    main()
