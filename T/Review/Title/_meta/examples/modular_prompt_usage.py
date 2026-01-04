"""Example: Using modular prompt templates for title reviews.

This example demonstrates the modularity and reusability of the new
prompt template system compared to the old approach.
"""

from T.Review.Title.prompts import (
    compose_review_prompt_with_idea,
    compose_review_prompt_content_only,
    compose_comparison_prompt,
    get_v1_review_prompt,
    get_v2_review_prompt,
    WEIGHTS_V1_WITH_IDEA,
    WEIGHTS_V2_CONTENT_ONLY,
)


def example_v1_review_with_idea():
    """Example: V1 title review with idea context."""
    print("=" * 70)
    print("EXAMPLE 1: V1 Title Review (with Idea Context)")
    print("=" * 70)
    
    # Sample data
    title = "The Echo - A Haunting Discovery"
    content = """
    Sarah investigates mysterious echoes in an abandoned psychiatric hospital.
    Each echo grows louder and more disturbing, revealing the hospital's dark past.
    The sounds lead her to discover that the echoes are not just sounds - 
    they are trapped souls trying to communicate their final moments.
    """
    idea = "Horror story about mysterious echoes that reveal hidden truths"
    audience = "Horror enthusiasts aged 18-35"
    
    # Generate prompt using modular system
    prompt = get_v1_review_prompt(
        title_text=title,
        content_text=content,
        idea_summary=idea,
        target_audience=audience
    )
    
    print(f"\nGenerated prompt length: {len(prompt)} characters")
    print(f"\nPrompt includes:")
    print(f"  ✓ Content Alignment (30%)")
    print(f"  ✓ Idea Alignment (25%)")
    print(f"  ✓ Engagement (25%)")
    print(f"  ✓ SEO & Length (20%)")
    print(f"\nFirst 500 characters of prompt:")
    print("-" * 70)
    print(prompt[:500])
    print("-" * 70)


def example_v2_review_content_only():
    """Example: V2 title review (content-only, no idea)."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: V2 Title Review (Content-Only)")
    print("=" * 70)
    
    # Sample data
    title = "The Echo - When Silence Answers Back"
    content = """
    Enhanced version with more suspense and character development.
    Sarah's investigation becomes personal when she realizes the echoes
    contain her own voice from a future she doesn't remember experiencing.
    """
    
    # Generate prompt using modular system
    prompt = get_v2_review_prompt(
        title_text=title,
        content_text=content
    )
    
    print(f"\nGenerated prompt length: {len(prompt)} characters")
    print(f"\nPrompt includes:")
    print(f"  ✓ Content Alignment (40%) - higher weight for v2")
    print(f"  ✓ Engagement (30%)")
    print(f"  ✓ SEO & Length (30%)")
    print(f"  ✗ Idea Alignment - not included in v2 reviews")
    print(f"\nFirst 500 characters of prompt:")
    print("-" * 70)
    print(prompt[:500])
    print("-" * 70)


def example_version_comparison():
    """Example: Comparing title versions."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Version Comparison (V1 vs V2)")
    print("=" * 70)
    
    # Sample data
    title_v1 = "The Echo"
    title_v2 = "The Echo - When Silence Answers Back"
    content = "Enhanced horror short about mysterious echoes..."
    score_v1 = 65
    score_v2 = 78
    feedback_v1 = "Title needs more specificity and emotional hook"
    
    # Generate comparison prompt
    prompt = compose_comparison_prompt(
        title_current=title_v2,
        title_previous=title_v1,
        content_text=content,
        score_current=score_v2,
        score_previous=score_v1,
        feedback_previous=feedback_v1
    )
    
    print(f"\nGenerated prompt length: {len(prompt)} characters")
    print(f"\nComparing:")
    print(f"  V1: '{title_v1}' (score: {score_v1}%)")
    print(f"  V2: '{title_v2}' (score: {score_v2}%)")
    print(f"  Delta: +{score_v2 - score_v1}% improvement")
    print(f"\nFirst 500 characters of prompt:")
    print("-" * 70)
    print(prompt[:500])
    print("-" * 70)


def example_custom_weights():
    """Example: Using custom evaluation weights."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Custom Evaluation Weights")
    print("=" * 70)
    
    # Custom weights emphasizing content alignment
    custom_weights = {
        "content_weight": 50,  # Higher emphasis on content
        "engagement_weight": 30,
        "seo_weight": 20,
    }
    
    title = "The Echo - A Haunting Discovery"
    content = "Horror short about mysterious echoes..."
    
    # Generate prompt with custom weights
    prompt = compose_review_prompt_content_only(
        title_text=title,
        content_text=content,
        weights=custom_weights
    )
    
    print(f"\nDefault weights (v2): {WEIGHTS_V2_CONTENT_ONLY}")
    print(f"Custom weights: {custom_weights}")
    print(f"\nGenerated prompt length: {len(prompt)} characters")
    print(f"\nPrompt uses:")
    print(f"  ✓ Content Alignment (50%) - custom higher weight")
    print(f"  ✓ Engagement (30%)")
    print(f"  ✓ SEO & Length (20%)")


def demonstrate_modularity():
    """Demonstrate the modular nature of the system."""
    print("\n" + "=" * 70)
    print("MODULARITY BENEFITS")
    print("=" * 70)
    
    print("\n📦 Template Composition:")
    print("  Base Template (base_review.txt)")
    print("    + Idea Context (idea_context.txt)")
    print("    + JSON Output (json_output_with_idea.txt)")
    print("    = V1 Review Prompt")
    
    print("\n  Base Template (base_review.txt)")
    print("    + JSON Output (json_output_basic.txt)")
    print("    = V2 Review Prompt")
    
    print("\n♻️  Reusability:")
    print("  • Base evaluation criteria used in ALL review types")
    print("  • Single source of truth for common prompts")
    print("  • Changes propagate to all review functions")
    
    print("\n🔧 Flexibility:")
    print("  • Configurable weights per review type")
    print("  • Mix and match prompt sections")
    print("  • Easy to add new context sections")
    
    print("\n✨ Consistency:")
    print("  • Same evaluation approach across modules")
    print("  • Predictable AI behavior")
    print("  • Easier to compare results")


def compare_old_vs_new_approach():
    """Compare old approach vs new modular approach."""
    print("\n" + "=" * 70)
    print("OLD vs NEW APPROACH")
    print("=" * 70)
    
    print("\n❌ OLD APPROACH (Duplicated Prompts):")
    print("  • Separate files:")
    print("    - T/Review/Title/From/Content/_meta/prompts/title_review_v1.txt")
    print("    - T/Review/Title/From/Content/_meta/prompts/title_review_v2_comparison.txt")
    print("  • Duplicated evaluation criteria")
    print("  • Changes require editing multiple files")
    print("  • Hard to maintain consistency")
    
    print("\n✅ NEW APPROACH (Modular Templates):")
    print("  • Base components:")
    print("    - T/Review/Title/_meta/prompts/base_review.txt (shared)")
    print("    - T/Review/Title/_meta/prompts/idea_context.txt (optional)")
    print("    - T/Review/Title/_meta/prompts/comparison_context.txt (optional)")
    print("  • Composed in code via T/Review/Title/prompts.py")
    print("  • Single source of truth")
    print("  • Easy to maintain and extend")
    
    print("\n📊 Benefits:")
    print("  • DRY principle (Don't Repeat Yourself)")
    print("  • Centralized maintenance")
    print("  • Flexible composition")
    print("  • Consistent behavior")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("MODULAR PROMPT TEMPLATE SYSTEM - EXAMPLES")
    print("=" * 70)
    
    # Run examples
    example_v1_review_with_idea()
    example_v2_review_content_only()
    example_version_comparison()
    example_custom_weights()
    demonstrate_modularity()
    compare_old_vs_new_approach()
    
    print("\n" + "=" * 70)
    print("EXAMPLES COMPLETE")
    print("=" * 70)
    print("\nFor more information:")
    print("  • See: T/Review/Title/_meta/prompts/README.md")
    print("  • API: T/Review/Title/prompts.py")
    print("  • Tests: T/Review/Title/_meta/tests/test_prompts.py")
    print()


if __name__ == "__main__":
    main()
