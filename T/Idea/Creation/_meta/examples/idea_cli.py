#!/usr/bin/env python3
"""
Simple CLI tool for generating Ideas using AI-powered Creation module.

Usage:
    python idea_cli.py "Your topic or description here"
    python idea_cli.py --from-description "Detailed description" --num-ideas 5
    python idea_cli.py --from-title "Short Title" --model qwen2.5:72b-q4_K_M
"""

import argparse
import os
import sys

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "../../src")
model_dir = os.path.join(current_dir, "../../../Model/src")
model_base = os.path.join(current_dir, "../../../Model")

sys.path.insert(0, src_dir)
sys.path.insert(0, model_dir)
sys.path.insert(0, model_base)

from creation import CreationConfig, IdeaCreator

from idea import ContentGenre


def print_idea(idea, index=1, verbose=False):
    """Print an idea in a formatted way."""
    print(f"\n{'='*80}")
    print(f"Idea {index}: {idea.title}")
    print(f"{'='*80}")
    print(f"\nConcept: {idea.concept}")

    if verbose:
        if idea.premise:
            print(f"\nPremise: {idea.premise}")
        if idea.logline:
            print(f"\nLogline: {idea.logline}")
        if idea.hook:
            print(f"\nHook: {idea.hook}")
        if idea.synopsis:
            print(f"\nSynopsis:\n{idea.synopsis}")
        if idea.skeleton:
            print(f"\nSkeleton:\n{idea.skeleton}")
        if idea.outline:
            print(f"\nOutline:\n{idea.outline}")

    if idea.keywords:
        print(f"\nKeywords: {', '.join(idea.keywords[:10])}")
    if idea.themes:
        print(f"Themes: {', '.join(idea.themes)}")
    print(f"\nTarget Platforms: {', '.join(idea.target_platforms)}")
    print(f"Target Formats: {', '.join(idea.target_formats)}")
    print(f"Genre: {idea.genre.value}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Ideas using AI-powered Creation module",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "The Future of AI"
  %(prog)s --from-description "Exploring ethical AI in healthcare"
  %(prog)s --from-title "Quantum Computing" --num-ideas 5
  %(prog)s "AI Story Ideas" --verbose --model qwen2.5:72b-q4_K_M
  %(prog)s "Social Media" --no-ai --num-ideas 3
        """,
    )

    parser.add_argument("input", nargs="?", help="Topic or description to generate ideas from")
    parser.add_argument(
        "--from-title", action="store_true", help="Treat input as a title (default behavior)"
    )
    parser.add_argument(
        "--from-description", action="store_true", help="Treat input as a detailed description"
    )
    parser.add_argument("--num-ideas", type=int, help="Number of ideas to generate (default: 10)")
    parser.add_argument(
        "--model",
        default="qwen2.5:32b",
        help="AI model to use (default: qwen2.5:32b - Qwen 3.30b)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.8,
        help="AI temperature for creativity (0.0-2.0, default: 0.8)",
    )
    parser.add_argument(
        "--no-ai", action="store_true", help="Disable AI and use fallback generation"
    )
    parser.add_argument("--genre", choices=[g.value for g in ContentGenre], help="Content genre")
    parser.add_argument("--platforms", nargs="+", help="Target platforms (e.g., youtube tiktok)")
    parser.add_argument("--formats", nargs="+", help="Target formats (e.g., video audio text)")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed idea information"
    )

    args = parser.parse_args()

    # Validate input
    if not args.input:
        parser.print_help()
        sys.exit(1)

    # Create configuration
    config = CreationConfig(
        use_ai=not args.no_ai,
        ai_model=args.model,
        ai_temperature=args.temperature,
        default_num_ideas=args.num_ideas or 10,
    )

    # Create IdeaCreator
    creator = IdeaCreator(config)

    # Print configuration
    print(f"\n{'='*80}")
    print("AI-Powered Idea Generation")
    print(f"{'='*80}")
    print(f"Input: {args.input}")
    print(f"Mode: {'Description' if args.from_description else 'Title'}")
    print(f"Number of ideas: {args.num_ideas or 10}")
    print(f"AI enabled: {not args.no_ai}")
    if not args.no_ai:
        print(f"Model: {args.model}")
        print(f"Temperature: {args.temperature}")

    # Parse genre
    genre = None
    if args.genre:
        genre = ContentGenre(args.genre)

    # Generate ideas
    try:
        if args.from_description:
            ideas = creator.create_from_description(
                description=args.input,
                num_ideas=args.num_ideas,
                target_platforms=args.platforms,
                target_formats=args.formats,
                genre=genre,
            )
        else:
            ideas = creator.create_from_title(
                title=args.input,
                num_ideas=args.num_ideas,
                target_platforms=args.platforms,
                target_formats=args.formats,
                genre=genre,
            )

        # Print results
        print(f"\n{'='*80}")
        print(f"Generated {len(ideas)} Ideas")
        print(f"{'='*80}")

        for i, idea in enumerate(ideas, 1):
            print_idea(idea, i, args.verbose)

        print(f"\n{'='*80}")
        print("Generation Complete!")
        print(f"{'='*80}")

    except Exception as e:
        print(f"\nError generating ideas: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
