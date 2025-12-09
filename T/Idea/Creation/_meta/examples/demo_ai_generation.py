"""
Demonstration of AI-powered idea generation.

This script demonstrates how the idea generation system works:
1. With Ollama available: Generates rich, AI-powered content for each field
2. Without Ollama: Falls back to template generation

To run with AI generation:
1. Install Ollama: https://ollama.com/
2. Start Ollama: ollama serve
3. Pull a model: ollama pull qwen3:32b
4. Run this script

Expected output WITH Ollama:
- Each field (hook, core_concept, etc.) contains rich, narrative content
- No template phrases like "How X relates to Y"
- Content is specific to the input and flavor

Expected output WITHOUT Ollama:
- Falls back to template-based generation
- Contains template phrases (this is the old behavior that was being fixed)
"""

import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from idea_variants import create_ideas_from_input


def demonstrate_idea_generation():
    """Demonstrate idea generation with and without AI."""
    
    print("=" * 80)
    print("PrismQ Idea Generation - AI Integration Demonstration")
    print("=" * 80)
    
    title = "Acadia Night Hikers"
    
    print(f"\nInput: {title}")
    print(f"Generating 2 idea variants...\n")
    
    # Generate ideas (will use AI if Ollama is running, templates otherwise)
    ideas = create_ideas_from_input(title, count=2)
    
    if not ideas:
        print("⚠ No ideas generated. Please check if Ollama is running.")
        return
    
    print(f"Generated {len(ideas)} ideas:\n")
    
    for i, idea in enumerate(ideas, 1):
        print(f"\n{'─' * 70}")
        print(f"Variant {i}: {idea.get('variant_name', 'Unknown')}")
        print(f"{'─' * 70}")
        
        # Show each field
        fields = ['hook', 'core_concept', 'emotional_core', 'audience_connection', 
                  'key_elements', 'tone_style']
        
        for field in fields:
            if field in idea:
                value = idea[field]
                field_name = field.replace('_', ' ').title()
                print(f"\n{field_name}:")
                print(f"  {value}")
        
        # Check for template phrases (indicates fallback)
        template_indicators = [
            "How", "relates to", "the attention-grabbing opening",
            "the main idea or premise in 1-2 sentences"
        ]
        
        has_template_text = any(
            indicator.lower() in str(idea.get(field, '')).lower()
            for field in fields
            for indicator in template_indicators
        )
        
        if has_template_text:
            print("\n⚠ Note: Template-based generation detected (Ollama not available)")
        else:
            print("\n✓ AI-generated content (rich, narrative descriptions)")
    
    print(f"\n{'=' * 80}")
    print("Demonstration complete!")
    print("=" * 80)
    
    print("\nInterpretation:")
    print("- If you see template phrases like 'How X relates to Y', Ollama is not running")
    print("- If you see rich narrative content, AI generation is working correctly")
    print("\nTo enable AI generation:")
    print("1. Install Ollama: https://ollama.com/")
    print("2. Start Ollama server: ollama serve")
    print("3. Pull a model: ollama pull qwen3:32b")
    print("4. Run this script again")


if __name__ == '__main__':
    demonstrate_idea_generation()
