#!/usr/bin/env python3
"""Example: Using custom prompt templates with PrismQ AI Generator.

This example demonstrates how to use the new flexible templating system
to generate ideas with custom prompts using local AI (Ollama).

Usage:
    python custom_prompt_example.py
"""

import sys
from pathlib import Path

# Add src to path for imports
SCRIPT_DIR = Path(__file__).parent.absolute()
CREATION_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(CREATION_ROOT / "src"))

from ai_generator import AIIdeaGenerator, AIConfig, list_available_prompts


def example_1_using_template_file():
    """Example 1: Use a prompt template file from _meta/prompts/"""
    print("\n" + "=" * 70)
    print("Example 1: Using prompt template file 'idea_improvement.txt'")
    print("=" * 70)
    
    # Initialize AI generator
    generator = AIIdeaGenerator()
    
    if not generator.available:
        print("ERROR: Ollama is not available. Please start Ollama first.")
        return
    
    # Input text to process
    input_text = "The Vanishing Tide"
    
    print(f"\nInput: {input_text}")
    print("\nGenerating improved idea using template...")
    
    # Generate using the idea_improvement template
    result = generator.generate_with_custom_prompt(
        input_text=input_text,
        prompt_template_name="idea_improvement"
    )
    
    print("\nResult:")
    print("-" * 70)
    print(result)
    print("-" * 70)


def example_2_using_inline_template():
    """Example 2: Use an inline prompt template string"""
    print("\n" + "=" * 70)
    print("Example 2: Using inline prompt template string")
    print("=" * 70)
    
    # Initialize AI generator
    generator = AIIdeaGenerator()
    
    if not generator.available:
        print("ERROR: Ollama is not available. Please start Ollama first.")
        return
    
    # Custom inline template
    custom_template = """You are a creative writing assistant.

Task: Take the following idea and expand it into a compelling story premise.

Input idea: {input}

Output a 2-3 paragraph story premise that includes:
- A strong hook
- Clear conflict
- Emotional stakes

Now generate the premise:"""
    
    input_text = "A lighthouse keeper discovers messages in bottles"
    
    print(f"\nInput: {input_text}")
    print("\nGenerating story premise using inline template...")
    
    # Generate using inline template
    result = generator.generate_with_custom_prompt(
        input_text=input_text,
        prompt_template=custom_template
    )
    
    print("\nResult:")
    print("-" * 70)
    print(result)
    print("-" * 70)


def example_3_list_available_templates():
    """Example 3: List all available prompt templates"""
    print("\n" + "=" * 70)
    print("Example 3: Listing available prompt templates")
    print("=" * 70)
    
    templates = list_available_prompts()
    
    print(f"\nFound {len(templates)} prompt template(s):\n")
    for i, template_name in enumerate(templates, 1):
        print(f"  {i}. {template_name}")
    
    print("\nYou can use these templates with:")
    print("  generator.generate_with_custom_prompt(")
    print("      input_text='Your text',")
    print("      prompt_template_name='template_name'")
    print("  )")


def example_4_with_custom_placeholders():
    """Example 4: Using INSERTTEXTHERE placeholder format"""
    print("\n" + "=" * 70)
    print("Example 4: Using INSERTTEXTHERE placeholder format")
    print("=" * 70)
    
    # Initialize AI generator
    generator = AIIdeaGenerator()
    
    if not generator.available:
        print("ERROR: Ollama is not available. Please start Ollama first.")
        return
    
    # Template using INSERTTEXTHERE placeholder (alternate format)
    custom_template = """Task: Analyze the concept and suggest 3 ways to make it more engaging.

Concept to analyze:
INSERTTEXTHERE

Provide 3 specific suggestions for improvement."""
    
    input_text = "A story about time travel"
    
    print(f"\nInput: {input_text}")
    print("\nGenerating suggestions using INSERTTEXTHERE placeholder...")
    
    # Generate using INSERTTEXTHERE format
    result = generator.generate_with_custom_prompt(
        input_text=input_text,
        prompt_template=custom_template
    )
    
    print("\nResult:")
    print("-" * 70)
    print(result)
    print("-" * 70)


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("Custom Prompt Template Examples for PrismQ")
    print("=" * 70)
    
    print("\nThis script demonstrates the new flexible templating system.")
    print("Make sure Ollama is running before executing these examples.")
    
    # Run examples
    example_3_list_available_templates()
    
    # Ask user which examples to run
    print("\n" + "=" * 70)
    print("Would you like to run the AI generation examples?")
    print("(These require Ollama to be running)")
    response = input("\nRun examples? (y/n): ").strip().lower()
    
    if response == 'y':
        example_1_using_template_file()
        example_2_using_inline_template()
        example_4_with_custom_placeholders()
    else:
        print("\nSkipping AI generation examples.")
    
    print("\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
