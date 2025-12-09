"""Example usage of PrismQ.T.Publishing.SEO.Keywords module.

This example demonstrates how to use the SEO Keywords module to:
1. Extract keywords from content
2. Generate SEO metadata
3. Get quality recommendations
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

import json

# Now we can import
from T.Publishing.SEO.Keywords import process_content_seo


def example_basic_usage():
    """Basic usage example."""
    print("=" * 70)
    print("EXAMPLE 1: Basic SEO Processing")
    print("=" * 70)

    # Sample content
    title = "The Complete Guide to Python Programming for Beginners"
    script = """
    Python is one of the most popular programming languages in the world today.
    Learning Python programming opens doors to exciting careers in software 
    development, data science, machine learning, and web development.
    
    Python's simple and readable syntax makes it an ideal programming language 
    for beginners. The Python programming community is large and supportive, 
    providing countless tutorials, libraries, and frameworks that make development 
    faster and easier.
    
    Many beginners start their programming journey with Python because of its 
    readability, versatility, and gentle learning curve. Python is used by tech 
    giants like Google, Netflix, and Instagram, making it a valuable skill in 
    today's job market.
    
    To learn Python effectively, practice coding regularly and work on real projects.
    Start with basic concepts like variables, loops, and functions, then progress to
    more advanced topics like object-oriented programming and data structures.
    Python programming skills are highly valued in the tech industry, and mastering
    Python can lead to numerous job opportunities.
    """

    # Process content for SEO
    result = process_content_seo(
        title=title,
        script=script,
        extraction_method="tfidf",  # Use TF-IDF for keyword extraction
        brand_name="CodeAcademy",
    )

    # Display results
    print(f"\n✓ Title: {title}")
    print(f"\n✓ Primary Keywords ({len(result['primary_keywords'])}):")
    for i, keyword in enumerate(result["primary_keywords"], 1):
        score = result["keyword_scores"].get(keyword, 0)
        density = result["keyword_density"].get(keyword, 0)
        print(f"  {i}. {keyword} (score: {score:.3f}, density: {density}%)")

    print(f"\n✓ Secondary Keywords ({len(result['secondary_keywords'])}):")
    print(f"  {', '.join(result['secondary_keywords'][:5])}...")

    print(f"\n✓ Meta Description ({len(result['meta_description'])} chars):")
    print(f"  {result['meta_description']}")

    print(f"\n✓ Title Tag ({len(result['title_tag'])} chars):")
    print(f"  {result['title_tag']}")

    print(f"\n✓ Open Graph Metadata:")
    print(f"  OG Title: {result['og_title']}")
    print(
        f"  OG Description ({len(result['og_description'])} chars): {result['og_description'][:80]}..."
    )

    print(f"\n✓ SEO Quality Score: {result['quality_score']}/100")

    print(f"\n✓ Recommendations:")
    for i, rec in enumerate(result["recommendations"], 1):
        print(f"  {i}. {rec}")

    print(f"\n✓ Related Keywords: {', '.join(result['related_keywords'][:5])}")
    print(f"\n✓ Total Words Analyzed: {result['total_words']}")
    print(f"✓ Extraction Method: {result['extraction_method']}")


def example_different_methods():
    """Example comparing different extraction methods."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Comparing Extraction Methods")
    print("=" * 70)

    title = "Machine Learning with Python and TensorFlow"
    script = """
    Machine learning is revolutionizing technology. Python and TensorFlow make
    machine learning accessible to developers. Deep learning neural networks can
    solve complex problems using Python programming and TensorFlow framework.
    """

    methods = ["tfidf", "frequency", "hybrid"]

    for method in methods:
        result = process_content_seo(
            title=title, script=script, extraction_method=method, primary_count=5
        )

        print(f"\n{method.upper()} Method:")
        print(f"  Keywords: {', '.join(result['primary_keywords'])}")
        print(f"  Quality Score: {result['quality_score']}/100")


def example_with_brand():
    """Example with brand integration."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Brand Integration")
    print("=" * 70)

    title = "Essential JavaScript Tips for Web Developers"
    script = """
    JavaScript is the language of the web. Every web developer needs to master
    JavaScript fundamentals. Modern web development relies heavily on JavaScript
    frameworks and libraries like React and Vue.
    """

    # Without brand
    result_no_brand = process_content_seo(title=title, script=script)

    # With brand
    result_with_brand = process_content_seo(title=title, script=script, brand_name="DevMaster")

    print("\nWithout Brand:")
    print(f"  Title Tag: {result_no_brand['title_tag']}")

    print("\nWith Brand:")
    print(f"  Title Tag: {result_with_brand['title_tag']}")


def example_export_to_json():
    """Example exporting results to JSON."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Export to JSON")
    print("=" * 70)

    title = "Building REST APIs with Python Flask"
    script = """
    Flask is a lightweight Python web framework perfect for building REST APIs.
    Learn to create scalable and secure APIs using Flask and Python.
    """

    result = process_content_seo(title=title, script=script, brand_name="APISchool")

    # Export to JSON (excluding some verbose fields for display)
    export_data = {
        "title": title,
        "seo": {
            "primary_keywords": result["primary_keywords"],
            "meta_description": result["meta_description"],
            "title_tag": result["title_tag"],
            "quality_score": result["quality_score"],
        },
    }

    json_output = json.dumps(export_data, indent=2)
    print("\nJSON Export:")
    print(json_output)


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("PrismQ SEO Keywords Module - Usage Examples")
    print("=" * 70)

    example_basic_usage()
    example_different_methods()
    example_with_brand()
    example_export_to_json()

    print("\n" + "=" * 70)
    print("Examples Complete!")
    print("=" * 70)
    print("\nTo use in your code:")
    print("  from T.Publishing.SEO.Keywords import process_content_seo")
    print("  result = process_content_seo(title='...', script='...')")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
