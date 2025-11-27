#!/usr/bin/env python3
"""CLI script for creating idea variants.

Usage:
    python create_variants.py "My Idea Title"
    python create_variants.py "My Idea Title" --variant emotion_first
    python create_variants.py "My Idea Title" --variant emotion_first --count 5
    python create_variants.py "My Idea Title" --all
    python create_variants.py --list

Examples:
    python create_variants.py "Záhadná událost v lese"
    python create_variants.py "AI Revolution" --variant mystery --count 3
    python create_variants.py "Horror Story" --all
"""

import sys
import os
import argparse
import json

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
        description='Create idea variants from a title',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_variants.py "My Idea"
  python create_variants.py "My Idea" --variant emotion_first
  python create_variants.py "My Idea" --variant emotion_first --count 5
  python create_variants.py "My Idea" --all
  python create_variants.py --list
        """
    )
    
    parser.add_argument('title', nargs='?', help='Idea title to create variants from')
    parser.add_argument('--variant', '-v', help='Specific variant type to create')
    parser.add_argument('--count', '-c', type=int, default=1, help='Number of variants to create (default: 1)')
    parser.add_argument('--all', '-a', action='store_true', help='Create all variant types')
    parser.add_argument('--list', '-l', action='store_true', help='List available variant templates')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    parser.add_argument('--description', '-d', default='', help='Optional description')
    
    args = parser.parse_args()
    
    # List templates
    if args.list:
        list_available_templates()
        return 0
    
    # Require title for variant creation
    if not args.title:
        parser.print_help()
        return 1
    
    variants = []
    
    if args.all:
        # Create all variant types
        print(f"\nCreating all variants for: '{args.title}'")
        variants = create_all_variants(args.title, args.description)
    elif args.variant:
        # Create specific variant type
        if args.count > 1:
            print(f"\nCreating {args.count} '{args.variant}' variants for: '{args.title}'")
            variants = create_multiple_of_same_variant(
                args.title, args.variant, count=args.count, description=args.description
            )
        else:
            print(f"\nCreating '{args.variant}' variant for: '{args.title}'")
            variant = create_idea_variant(args.title, args.variant, args.description)
            variants = [variant]
    else:
        # Default: create minimal variant
        print(f"\nCreating 'minimal' variant for: '{args.title}'")
        variant = create_idea_variant(args.title, 'minimal', args.description)
        variants = [variant]
    
    # Output
    if args.json:
        print(json.dumps(variants, indent=2, ensure_ascii=False))
    else:
        for i, variant in enumerate(variants):
            print_variant(variant, i if len(variants) > 1 else None)
        
        print(f"\nTotal: {len(variants)} variant(s) created")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
