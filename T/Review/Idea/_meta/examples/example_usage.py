#!/usr/bin/env python3
"""Example usage of the Worker10 Idea Review Generator.

This script demonstrates different ways to use the idea review functionality
with the test inputs specified in the requirements:
- Keyword: "skirts 2000"
- Longer Czech text: "když jsem se probudil sobotního rána po tahu"
"""

import sys
import os

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
idea_review_dir = os.path.join(current_dir, '../..')
idea_creation_dir = os.path.join(current_dir, '../../../../Idea/Creation/src')
sys.path.insert(0, idea_review_dir)
sys.path.insert(0, idea_creation_dir)

from idea_review import generate_idea_review, IdeaReviewGenerator


def example_keyword_review():
    """Example 1: Review ideas from a keyword input."""
    print("=" * 80)
    print("Example 1: Keyword Input - 'skirts 2000'")
    print("=" * 80)
    
    review = generate_idea_review("skirts 2000", num_ideas=5, seed=42)
    
    print(f"\nInput: {review.original_input}")
    print(f"Input Type: {review.input_type}")
    print(f"Variants Generated: {review.total_variants}")
    print(f"Average Similarity: {review.average_similarity_score:.1f}%")
    
    print("\n--- Variant Overview ---")
    for analysis in review.variant_analyses:
        print(f"\n  [{analysis.variant_index + 1}] {analysis.variant_name}")
        print(f"      Type: {analysis.variant_type}")
        print(f"      Similarity: {analysis.similarity_score}%")
        print(f"      Pros: {len(analysis.pros)} | Cons: {len(analysis.cons)} | Gaps: {len(analysis.gaps)}")
    
    print("\n--- Overall Summary ---")
    print(f"Strengths: {review.overall_strengths}")
    print(f"Gaps: {review.overall_gaps[:2]}...")  # Truncate for brevity
    
    print("\n" + "=" * 80 + "\n")


def example_czech_text_review():
    """Example 2: Review ideas from Czech text input."""
    print("=" * 80)
    print("Example 2: Czech Text Input")
    print("=" * 80)
    
    czech_text = "když jsem se probudil sobotního rána po tahu"
    review = generate_idea_review(czech_text, num_ideas=5, seed=42)
    
    print(f"\nInput: {review.original_input}")
    print(f"Input Type: {review.input_type}")
    print(f"Variants Generated: {review.total_variants}")
    print(f"Average Similarity: {review.average_similarity_score:.1f}%")
    
    print("\n--- Cross-Variant Differences ---")
    for diff in review.cross_variant_differences:
        print(f"  • {diff}")
    
    print("\n--- Recommendations ---")
    for rec in review.recommendations:
        print(f"  💡 {rec}")
    
    print("\n" + "=" * 80 + "\n")


def example_markdown_output():
    """Example 3: Generate full markdown report."""
    print("=" * 80)
    print("Example 3: Full Markdown Report")
    print("=" * 80)
    
    review = generate_idea_review("mystery story", num_ideas=3, seed=42)
    
    # Print just the first part of the markdown for demo
    markdown = review.format_as_markdown()
    lines = markdown.split('\n')[:50]
    print('\n'.join(lines))
    print("\n... (truncated for demo)")
    
    print("\n" + "=" * 80 + "\n")


def example_advanced_usage():
    """Example 4: Advanced usage with custom generator."""
    print("=" * 80)
    print("Example 4: Advanced Usage")
    print("=" * 80)
    
    # Create generator with custom settings
    generator = IdeaReviewGenerator(num_ideas=3)
    
    # Generate review with no duplicate types
    review = generator.generate_review(
        "AI in medicine",
        seed=123,
        allow_duplicate_types=False
    )
    
    print(f"\nInput: {review.original_input}")
    print(f"Unique variant types generated: {len(set(a.variant_type for a in review.variant_analyses))}")
    
    # Access specific variant details
    best_variant = max(review.variant_analyses, key=lambda a: a.similarity_score)
    print(f"\nBest aligned variant: {best_variant.variant_name}")
    print(f"  Similarity: {best_variant.similarity_score}%")
    print(f"  Key themes: {best_variant.key_themes}")
    print(f"  Top pros: {best_variant.pros[:2]}")
    
    print("\n" + "=" * 80 + "\n")


def example_json_output():
    """Example 5: JSON output for API integration."""
    print("=" * 80)
    print("Example 5: JSON Output")
    print("=" * 80)
    
    import json
    
    review = generate_idea_review("tech innovation", num_ideas=2, seed=42)
    
    # Convert to dict (ready for JSON)
    data = review.to_dict()
    
    # Print formatted JSON (first few items)
    print("\nJSON structure overview:")
    print(f"  original_input: {data['original_input']}")
    print(f"  input_type: {data['input_type']}")
    print(f"  total_variants: {data['total_variants']}")
    print(f"  average_similarity_score: {data['average_similarity_score']}")
    print(f"  variant_analyses: [{len(data['variant_analyses'])} items]")
    print(f"  cross_variant_differences: {len(data['cross_variant_differences'])} items")
    print(f"  recommendations: {len(data['recommendations'])} items")
    
    print("\n" + "=" * 80 + "\n")


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("Worker10 Idea Review Generator - Examples")
    print("=" * 80 + "\n")
    
    example_keyword_review()
    example_czech_text_review()
    example_markdown_output()
    example_advanced_usage()
    example_json_output()
    
    print("All examples completed successfully!")
    print("\nTo generate your own reviews, use:")
    print("  python idea_review_cli.py \"<your text>\" [--count N] [--seed N]")


if __name__ == "__main__":
    main()
