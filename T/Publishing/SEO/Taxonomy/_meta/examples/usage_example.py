"""Usage examples for PrismQ.T.Publishing.SEO.Taxonomy module.

This script demonstrates how to use the Taxonomy module for automatic tag
generation and category classification.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

from T.Publishing.SEO.Taxonomy import (
    DEFAULT_TAXONOMY,
    TECH_FOCUSED_TAXONOMY,
    CategoryClassifier,
    TagGenerator,
    TaxonomyConfig,
    classify_categories,
    create_custom_taxonomy,
    generate_tags,
    process_taxonomy,
)


def example_basic_usage():
    """Example 1: Basic taxonomy processing."""
    print("=" * 80)
    print("Example 1: Basic Taxonomy Processing")
    print("=" * 80)

    title = "Introduction to Machine Learning with Python"
    script = """
    Machine learning is a subset of artificial intelligence that enables
    computers to learn from data without being explicitly programmed. Python
    has become the de facto language for machine learning due to its simplicity
    and powerful libraries like scikit-learn, TensorFlow, and PyTorch.
    
    In this guide, we'll explore the fundamentals of machine learning, including
    supervised and unsupervised learning, neural networks, and deep learning.
    Data science professionals use these techniques to build predictive models
    and extract insights from data.
    """

    # Process with default configuration
    result = process_taxonomy(
        title=title, script=script, keywords=["machine learning", "python", "AI", "data science"]
    )

    print(f"\nTitle: {title}")
    print(f"\nGenerated Tags ({len(result['tags'])}):")
    for tag in result["tags"]:
        score = result["tag_scores"].get(tag, 0)
        print(f"  - {tag:30} (relevance: {score:.2f})")

    print(f"\nAssigned Categories ({len(result['categories'])}):")
    for category in result["categories"]:
        score = result["category_scores"].get(category, 0)
        print(f"  - {category:40} (confidence: {score:.2f})")

    print(f"\nHierarchical Structure:")
    for parent, children in result["hierarchy"].items():
        print(f"  {parent}")
        for child in children:
            print(f"    └─ {child}")

    print(f"\nQuality Metrics:")
    print(f"  Total Tags: {result['stats']['total_tags']}")
    print(f"  Total Categories: {result['stats']['total_categories']}")
    print(f"  Avg Tag Relevance: {result['stats']['avg_tag_relevance']:.2f}")
    print(f"  Avg Category Confidence: {result['stats']['avg_category_confidence']:.2f}")
    print(f"  Quality Score: {result['stats']['quality_score']}/100")
    print()


def example_tag_generation_only():
    """Example 2: Tag generation only."""
    print("=" * 80)
    print("Example 2: Tag Generation Only")
    print("=" * 80)

    title = "Building Modern Web Applications with React and Node.js"
    script = """
    React is a popular JavaScript library for building user interfaces.
    Combined with Node.js for backend development, you can create full-stack
    web applications using JavaScript throughout the entire stack.
    """

    # Generate tags only
    result = generate_tags(
        title=title, script=script, keywords=["react", "nodejs", "javascript", "web development"]
    )

    print(f"\nTitle: {title}")
    print(f"\nGenerated Tags:")
    for tag, score in list(result.relevance_scores.items())[:10]:
        print(f"  - {tag:30} (score: {score:.2f})")

    print(f"\nSource Breakdown:")
    for source, count in result.source_breakdown.items():
        print(f"  - {source}: {count} tags")

    print(f"\nDuplicates Removed: {result.duplicates_removed}")
    print()


def example_category_classification_only():
    """Example 3: Category classification only."""
    print("=" * 80)
    print("Example 3: Category Classification Only")
    print("=" * 80)

    title = "10 Healthy Eating Habits for Better Wellness"
    script = """
    Maintaining a balanced diet is crucial for health and wellness. Focus on
    whole foods, vegetables, and fruits. Stay hydrated and eat mindfully.
    Regular meal planning helps maintain healthy eating habits and supports
    fitness goals.
    """

    # Classify categories only
    result = classify_categories(
        title=title, script=script, tags=["health", "nutrition", "wellness", "fitness", "diet"]
    )

    print(f"\nTitle: {title}")
    print(f"\nClassified Categories:")
    for category, score in result.confidence_scores.items():
        print(f"  - {category:40} (confidence: {score:.2f})")

    print(f"\nHierarchy:")
    for parent, children in result.hierarchy.items():
        print(f"  {parent}")
        if children:
            for child in children:
                print(f"    └─ {child}")
    print()


def example_custom_configuration():
    """Example 4: Using custom taxonomy configuration."""
    print("=" * 80)
    print("Example 4: Custom Taxonomy Configuration")
    print("=" * 80)

    # Create custom taxonomy for a cooking blog
    custom_config = create_custom_taxonomy(
        categories={
            "Cooking": ["Baking", "Grilling", "Healthy Recipes"],
            "Ingredients": ["Vegetables", "Meat", "Dairy"],
            "Cuisine": ["Italian", "Asian", "Mexican"],
        },
        min_relevance=0.65,
        max_tags=8,
        max_categories=2,
    )

    title = "Easy Healthy Grilled Chicken Recipe"
    script = """
    This grilled chicken recipe is perfect for a healthy dinner. The chicken
    is marinated in herbs and grilled to perfection. Serve with vegetables
    for a complete meal. Great for healthy eating and meal prep.
    """

    result = process_taxonomy(
        title=title,
        script=script,
        keywords=["chicken", "grilling", "healthy", "recipe"],
        config=custom_config,
    )

    print(f"\nTitle: {title}")
    print(f"\nTags: {', '.join(result['tags'])}")
    print(f"\nCategories: {', '.join(result['categories'])}")
    print(f"Quality Score: {result['stats']['quality_score']}/100")
    print()


def example_tech_focused_taxonomy():
    """Example 5: Using tech-focused preset taxonomy."""
    print("=" * 80)
    print("Example 5: Tech-Focused Taxonomy")
    print("=" * 80)

    title = "Building Microservices with Docker and Kubernetes"
    script = """
    Microservices architecture combined with containerization using Docker
    and orchestration with Kubernetes enables scalable cloud-native applications.
    DevOps practices and continuous deployment are essential for modern
    software development.
    """

    result = process_taxonomy(
        title=title,
        script=script,
        keywords=["docker", "kubernetes", "microservices", "devops"],
        config=TECH_FOCUSED_TAXONOMY,
    )

    print(f"\nTitle: {title}")
    print(f"\nTags: {', '.join(result['tags'])}")
    print(f"\nCategories: {', '.join(result['categories'])}")
    print(f"Quality Score: {result['stats']['quality_score']}/100")
    print()


def example_advanced_usage():
    """Example 6: Advanced usage with generators and classifiers."""
    print("=" * 80)
    print("Example 6: Advanced Usage")
    print("=" * 80)

    # Create custom config
    config = TaxonomyConfig(
        categories={"Tech": ["AI", "Web"], "Business": ["Marketing"]},
        max_tags=7,
        min_relevance=0.75,
    )

    # Use TagGenerator directly
    tag_gen = TagGenerator(config=config)
    tag_result = tag_gen.generate_tags(
        title="AI-Powered Marketing Strategies",
        script="Using artificial intelligence for marketing automation and personalization.",
        base_keywords=["ai", "marketing"],
    )

    print(f"\nTag Generation:")
    print(f"  Tags: {', '.join(tag_result.tags)}")
    print(f"  Method: {tag_result.generation_method}")

    # Use CategoryClassifier directly
    cat_classifier = CategoryClassifier(config=config)
    cat_result = cat_classifier.classify_categories(
        title="AI-Powered Marketing Strategies",
        script="Using artificial intelligence for marketing automation and personalization.",
        tags=tag_result.tags,
    )

    print(f"\nCategory Classification:")
    print(f"  Categories: {', '.join(cat_result.categories)}")
    print(f"  Method: {cat_result.classification_method}")
    print()


def example_without_keywords():
    """Example 7: Processing without SEO keywords."""
    print("=" * 80)
    print("Example 7: Processing Without Keywords")
    print("=" * 80)

    title = "The Future of Remote Work"
    script = """
    Remote work has transformed how businesses operate. Technology enables
    teams to collaborate from anywhere. Companies are adopting hybrid models
    that balance flexibility with in-office collaboration.
    """

    # Process without keywords (will extract from content only)
    result = process_taxonomy(title=title, script=script, keywords=None)  # No keywords provided

    print(f"\nTitle: {title}")
    print(f"\nAuto-extracted Tags: {', '.join(result['tags'])}")
    print(f"Categories: {', '.join(result['categories'])}")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("PrismQ Taxonomy Module - Usage Examples")
    print("=" * 80 + "\n")

    try:
        example_basic_usage()
        example_tag_generation_only()
        example_category_classification_only()
        example_custom_configuration()
        example_tech_focused_taxonomy()
        example_advanced_usage()
        example_without_keywords()

        print("=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
