"""
Demonstration of AI-powered idea generation.

This script demonstrates how the idea generation system works:
- Requires Ollama to be running - will raise an error if not available
- Generates rich, AI-powered content for each field

To run this script:
1. Install Ollama: https://ollama.com/
2. Pull a model: ollama pull qwen3:32b
3. Start Ollama: ollama serve
4. Run this script

Expected output WITH Ollama:
- Each field (hook, core_concept, etc.) contains rich, narrative content
- No template phrases like "How X relates to Y"
- Content is specific to the input and flavor

Expected output WITHOUT Ollama:
- RuntimeError with clear instructions to install and start Ollama
"""

import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

from idea_variants import create_ideas_from_input


def demonstrate_idea_generation():
    """Demonstrate idea generation with AI."""
    
    print("=" * 80)
    print("PrismQ Idea Generation - AI Required Demonstration")
    print("=" * 80)
    
    title = "Acadia Night Hikers"
    
    print(f"\nInput: {title}")
    print(f"Attempting to generate 2 idea variants...\n")
    
    try:
        # Generate ideas - requires Ollama to be running
        ideas = create_ideas_from_input(title, count=2)
        
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
            
            print("\n✓ AI-generated content (rich, narrative descriptions)")
        
        print(f"\n{'=' * 80}")
        print("Success! AI generation is working correctly.")
        print("=" * 80)
        
    except RuntimeError as e:
        print(f"\n{'=' * 80}")
        print("ERROR: AI Generation Failed")
        print("=" * 80)
        print(f"\n{e}\n")
        print("Setup Instructions:")
        print("1. Install Ollama: https://ollama.com/")
        print("2. Pull a model: ollama pull qwen3:32b")
        print("3. Start Ollama server: ollama serve")
        print("4. Run this script again")
        print(f"\n{'=' * 80}")


if __name__ == '__main__':
    demonstrate_idea_generation()
