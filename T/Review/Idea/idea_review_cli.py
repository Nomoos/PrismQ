#!/usr/bin/env python3
"""CLI for Worker10 Idea Review Generator.

Generates ideas from text input and produces a comprehensive review
containing gaps, pros, cons, differences across variants, and
similarity/compatibility with original text.

Usage:
    idea_review_cli.py "<text>" [--count N] [--seed N] [--output FILE]
    
Examples:
    idea_review_cli.py "skirts 2000"
    idea_review_cli.py "když jsem se probudil sobotního rána po tahu" --count 10
"""

import sys
import os
import argparse
from typing import Optional

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from idea_review import IdeaReviewGenerator, generate_idea_review


DEFAULT_COUNT = 10


def main(args: Optional[list] = None) -> int:
    """Main entry point for the CLI.
    
    Args:
        args: Optional list of arguments (defaults to sys.argv)
        
    Returns:
        Exit code (0 for success)
    """
    parser = argparse.ArgumentParser(
        description="Worker10 Idea Review Generator - Analyze generated ideas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "skirts 2000"
  %(prog)s "skirts 2000" --count 5
  %(prog)s "když jsem se probudil sobotního rána po tahu" --output review.md
  %(prog)s "AI in medicine" --seed 42 --count 10
        """
    )
    
    parser.add_argument(
        'text',
        help='Text input to generate ideas from (keyword, phrase, or longer text)'
    )
    
    parser.add_argument(
        '--count', '-n',
        type=int,
        default=DEFAULT_COUNT,
        help=f'Number of ideas to generate (default: {DEFAULT_COUNT})'
    )
    
    parser.add_argument(
        '--seed', '-s',
        type=int,
        default=None,
        help='Random seed for reproducible generation'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output file path for markdown report (default: print to stdout)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON instead of markdown'
    )
    
    parsed = parser.parse_args(args)
    
    # Validate count
    if parsed.count < 1:
        parser.error("--count must be at least 1")
    if parsed.count > 100:
        parser.error("--count cannot exceed 100")
    
    # Generate review
    print(f"🔄 Generating {parsed.count} ideas from input: '{parsed.text}'")
    print("⏳ Please wait...")
    print()
    
    try:
        review = generate_idea_review(
            text_input=parsed.text,
            num_ideas=parsed.count,
            seed=parsed.seed
        )
        
        # Format output
        if parsed.json:
            import json
            output = json.dumps(review.to_dict(), indent=2, ensure_ascii=False)
        else:
            output = review.format_as_markdown()
        
        # Write or print output
        if parsed.output:
            with open(parsed.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"✅ Review saved to: {parsed.output}")
        else:
            print(output)
        
        # Print summary statistics
        print()
        print("=" * 60)
        print("📊 Summary Statistics")
        print("=" * 60)
        print(f"   Input: {parsed.text}")
        print(f"   Input Type: {review.input_type}")
        print(f"   Variants Generated: {review.total_variants}")
        print(f"   Average Similarity: {review.average_similarity_score:.1f}%")
        print(f"   Overall Strengths: {len(review.overall_strengths)}")
        print(f"   Overall Gaps: {len(review.overall_gaps)}")
        print(f"   Recommendations: {len(review.recommendations)}")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
