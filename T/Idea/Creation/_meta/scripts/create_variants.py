#!/usr/bin/env python3
"""CLI script for creating idea variants from any text input.

This tool accepts any piece of text - a title, description, keyword, story snippet,
or even JSON data - and creates idea variants from it.

Usage:
    python create_variants.py "any text input"
    python create_variants.py "text" --variant emotion_first
    python create_variants.py "text" --count 5
    python create_variants.py --file input.txt
    python create_variants.py --list

Examples:
    # From a story snippet
    python create_variants.py "I wore a baggy, graphic tee on the first day of school..."
    
    # From a title/keyword
    python create_variants.py "Fashion Revolution"
    
    # From JSON (auto-detected)
    python create_variants.py '{"story_title": "My Story", "theme": "social betrayal"}'
    
    # Multiple variants
    python create_variants.py "My idea" --count 5
    
    # Specific variant type
    python create_variants.py "My idea" --variant mystery
    
    # From file
    python create_variants.py --file story.txt
"""

import sys
import os
import argparse
import json
import re

# Add parent directories to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, '../../src')
sys.path.insert(0, src_dir)

from idea_variants import (
    create_idea_variant,
    create_all_variants,
    create_selected_variants,
    create_multiple_of_same_variant,
    list_templates,
    get_template,
)


def parse_input_text(text: str) -> tuple:
    """Parse input text and extract title and description.
    
    Handles:
    - Plain text (title, description, story snippet, keyword)
    - JSON data with story_title, title, theme, etc.
    
    Args:
        text: Input text (any format)
        
    Returns:
        Tuple of (title, description)
    """
    text = text.strip()
    
    # Try to parse as JSON
    if text.startswith('{'):
        try:
            data = json.loads(text)
            
            # Extract title from various JSON fields
            title = (
                data.get('story_title') or 
                data.get('title') or 
                data.get('theme') or 
                data.get('topic') or
                data.get('keyword') or
                data.get('name') or
                'Untitled Idea'
            )
            
            # Build description from other fields
            desc_parts = []
            
            if data.get('narrator_gender'):
                desc_parts.append(f"Narrator: {data['narrator_gender']}")
            if data.get('tone'):
                desc_parts.append(f"Tone: {data['tone']}")
            if data.get('theme'):
                desc_parts.append(f"Theme: {data['theme']}")
            if data.get('character_arc'):
                desc_parts.append(f"Character arc: {data['character_arc']}")
            if data.get('outcome'):
                desc_parts.append(f"Outcome: {data['outcome']}")
            if data.get('emotional_core'):
                desc_parts.append(f"Emotional core: {data['emotional_core']}")
            
            # Add platform potential info
            if data.get('potencial') and data['potencial'].get('platforms'):
                platforms = data['potencial']['platforms']
                top_platform = max(platforms, key=platforms.get)
                desc_parts.append(f"Top platform: {top_platform} ({platforms[top_platform]}%)")
            
            description = '. '.join(desc_parts) if desc_parts else ''
            
            return title, description
            
        except json.JSONDecodeError:
            pass  # Not valid JSON, treat as plain text
    
    # Plain text handling
    # If it's a short text (likely a title/keyword), use as-is
    if len(text) <= 100:
        return text, ''
    
    # For longer text (story snippet, description), extract a title
    # Take first sentence or first N characters as title
    sentences = re.split(r'[.!?]', text)
    first_sentence = sentences[0].strip() if sentences else text[:100]
    
    # Truncate title if too long
    if len(first_sentence) > 80:
        title = first_sentence[:77] + '...'
    else:
        title = first_sentence
    
    # Use full text as description
    description = text
    
    return title, description


def print_variant(variant: dict, index: int = None):
    """Pretty print a variant."""
    print()
    if index is not None:
        print(f"{'='*60}")
        print(f"  VARIANT {index + 1}: {variant.get('variant_name', 'Unknown')}")
        print(f"{'='*60}")
    else:
        print(f"{'='*60}")
        print(f"  {variant.get('variant_name', 'Unknown')}")
        print(f"{'='*60}")
    
    print(f"  Type: {variant.get('variant_type', 'N/A')}")
    print(f"  Source: {variant.get('source_title', 'N/A')}")
    print()
    
    # Print variant-specific fields
    skip_keys = {'variant_type', 'variant_name', 'source_title', 'source_description', 
                 'variation_index', 'variation_seed'}
    
    for key, value in variant.items():
        if key in skip_keys:
            continue
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        elif isinstance(value, list):
            print(f"  {key}: {', '.join(str(v) for v in value)}")
        else:
            print(f"  {key}: {value}")
    print()


def list_available_templates():
    """List all available variant templates."""
    print()
    print("Available Variant Templates:")
    print("="*50)
    for name in list_templates():
        template = get_template(name)
        print(f"  {name:15} - {template['name']}")
        print(f"                   {template['description']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Create idea variants from any text input (title, description, keyword, story snippet, or JSON)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From any text
  python create_variants.py "I wore a baggy tee on the first day of school..."
  python create_variants.py "Fashion Revolution"
  
  # From JSON
  python create_variants.py '{"story_title": "My Story", "theme": "betrayal"}'
  
  # Multiple variants
  python create_variants.py "My idea" --count 5
  
  # Specific variant type
  python create_variants.py "My idea" --variant mystery
  
  # All variant types
  python create_variants.py "My idea" --all
  
  # From file
  python create_variants.py --file story.txt
  
  # List available templates
  python create_variants.py --list
        """
    )
    
    parser.add_argument('input', nargs='?', help='Input text (title, description, keyword, story snippet, or JSON)')
    parser.add_argument('--file', '-f', help='Read input from file')
    parser.add_argument('--variant', '-v', help='Specific variant type to create (default: creates all simple variants)')
    parser.add_argument('--count', '-c', type=int, default=10, help='Number of variants to create (default: 10)')
    parser.add_argument('--all', '-a', action='store_true', help='Create all 11 variant types')
    parser.add_argument('--list', '-l', action='store_true', help='List available variant templates')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # List templates
    if args.list:
        list_available_templates()
        return 0
    
    # Get input text
    input_text = None
    
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                input_text = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}")
            return 1
        except Exception as e:
            print(f"Error reading file: {e}")
            return 1
    elif args.input:
        input_text = args.input
    
    if not input_text:
        parser.print_help()
        return 1
    
    # Parse input
    title, description = parse_input_text(input_text)
    
    print(f"\n{'='*60}")
    print("  PrismQ Idea Variant Creator")
    print(f"{'='*60}")
    print(f"  Extracted title: {title}")
    if description:
        desc_preview = description[:100] + '...' if len(description) > 100 else description
        print(f"  Description: {desc_preview}")
    print()
    
    variants = []
    
    if args.all:
        # Create all 11 variant types
        print(f"Creating all 11 variant types...")
        variants = create_all_variants(title, description)
    elif args.variant:
        # Create specific variant type
        if args.count > 1:
            print(f"Creating {args.count} '{args.variant}' variants...")
            variants = create_multiple_of_same_variant(
                title, args.variant, count=args.count, description=description
            )
        else:
            print(f"Creating '{args.variant}' variant...")
            variant = create_idea_variant(title, args.variant, description)
            variants = [variant]
    else:
        # Default: create multiple minimal variants for variety
        print(f"Creating {args.count} idea variants...")
        variants = create_multiple_of_same_variant(
            title, 'minimal', count=args.count, description=description
        )
    
    # Output
    if args.json:
        print(json.dumps(variants, indent=2, ensure_ascii=False))
    else:
        for i, variant in enumerate(variants):
            print_variant(variant, i if len(variants) > 1 else None)
        
        print(f"\n{'='*60}")
        print(f"  Total: {len(variants)} variant(s) created")
        print(f"{'='*60}\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
