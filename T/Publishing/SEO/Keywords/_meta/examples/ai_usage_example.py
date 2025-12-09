"""Examples for AI-powered SEO metadata generation (POST-001).

This module demonstrates how to use the AI-powered SEO metadata
generation features with prompt engineering.
"""

from T.Publishing.SEO.Keywords import (
    AIConfig,
    extract_keywords,
    generate_ai_seo_metadata,
    process_content_seo,
)


def example_1_basic_ai_generation():
    """Example 1: Basic AI-powered SEO metadata generation."""
    print("\n" + "=" * 70)
    print("Example 1: Basic AI-Powered SEO Metadata Generation")
    print("=" * 70)

    title = "The Complete Guide to Machine Learning in 2024"
    script = """
    Machine learning is revolutionizing how we interact with technology.
    From recommendation systems to autonomous vehicles, ML algorithms are
    everywhere. This comprehensive guide will walk you through the fundamentals
    of machine learning, including supervised learning, unsupervised learning,
    and reinforcement learning. We'll explore popular algorithms like decision
    trees, neural networks, and support vector machines. You'll learn how to
    preprocess data, train models, and evaluate their performance. Whether
    you're a beginner or looking to advance your skills, this guide covers
    everything you need to know about machine learning in 2024.
    """

    # Use AI-powered generation
    result = process_content_seo(
        title=title,
        script=script,
        use_ai=True,  # Enable AI-powered metadata generation
        brand_name="ML Academy",
    )

    print(f"\n📊 SEO Analysis Results:")
    print(f"Primary Keywords: {', '.join(result['primary_keywords'][:5])}")
    print(f"\n📝 AI-Generated Meta Description ({len(result['meta_description'])} chars):")
    print(f"   {result['meta_description']}")
    print(f"\n🏷️ AI-Generated Title Tag ({len(result['title_tag'])} chars):")
    print(f"   {result['title_tag']}")
    print(f"\n📱 Open Graph Description ({len(result['og_description'])} chars):")
    print(f"   {result['og_description']}")
    print(f"\n✅ Quality Score: {result['quality_score']}/100")
    print(f"🤖 AI Generated: {result['ai_generated']}")


def example_2_compare_ai_vs_rulebased():
    """Example 2: Compare AI-generated vs rule-based metadata."""
    print("\n" + "=" * 70)
    print("Example 2: Compare AI vs Rule-Based Generation")
    print("=" * 70)

    title = "Python for Data Science: A Beginner's Journey"
    script = """
    Python has become the lingua franca of data science. With powerful
    libraries like NumPy, Pandas, and Scikit-learn, Python makes data
    analysis accessible to everyone. This tutorial will guide you through
    the essential skills needed for data science, from data manipulation
    and visualization to statistical analysis and machine learning. You'll
    work with real datasets, learn to clean and preprocess data, create
    stunning visualizations with Matplotlib and Seaborn, and build your
    first predictive models. Perfect for beginners with basic Python knowledge.
    """

    # Rule-based generation
    print("\n🔧 RULE-BASED GENERATION:")
    result_rule = process_content_seo(
        title=title, script=script, use_ai=False, brand_name="DataLearn"
    )

    print(f"Meta Description: {result_rule['meta_description']}")
    print(f"Title Tag: {result_rule['title_tag']}")
    print(f"Quality Score: {result_rule['quality_score']}/100")

    # AI-powered generation
    print("\n🤖 AI-POWERED GENERATION:")
    result_ai = process_content_seo(title=title, script=script, use_ai=True, brand_name="DataLearn")

    print(f"Meta Description: {result_ai['meta_description']}")
    print(f"Title Tag: {result_ai['title_tag']}")
    print(f"Quality Score: {result_ai['quality_score']}/100")

    print("\n📊 COMPARISON:")
    print(f"Description Length - Rule-based: {len(result_rule['meta_description'])} chars")
    print(f"Description Length - AI: {len(result_ai['meta_description'])} chars")
    print(f"Quality Score Diff: {result_ai['quality_score'] - result_rule['quality_score']}")


def example_3_custom_ai_config():
    """Example 3: Using custom AI configuration."""
    print("\n" + "=" * 70)
    print("Example 3: Custom AI Configuration")
    print("=" * 70)

    title = "Building Scalable Web Applications with Django"
    script = """
    Django is a high-level Python web framework that enables rapid development
    of secure and maintainable websites. This guide covers Django's architecture,
    including models, views, templates, and URLs. You'll learn to build a complete
    web application from scratch, implement user authentication, work with databases,
    and deploy to production. We'll explore Django's ORM, form handling, middleware,
    and best practices for building scalable applications. Perfect for developers
    looking to master web development with Python.
    """

    # Create custom AI configuration
    custom_config = AIConfig(
        model="qwen3:32b",  # Default local AI model (can be customized)
        temperature=0.2,  # More focused output
        max_tokens=400,
        timeout=30,
        enable_ai=True,
    )

    # Extract keywords first
    extraction = extract_keywords(title=title, script=script, method="tfidf")

    print(f"Extracted Keywords: {', '.join(extraction.primary_keywords)}")

    # Generate AI metadata with custom config
    metadata = generate_ai_seo_metadata(
        title=title,
        script=script,
        primary_keywords=extraction.primary_keywords,
        secondary_keywords=extraction.secondary_keywords,
        keyword_density=extraction.keyword_density,
        config=custom_config,
        brand_name="WebDev Pro",
    )

    print(f"\n📝 AI Metadata (Custom Config):")
    print(f"Meta Description: {metadata.meta_description}")
    print(f"Title Tag: {metadata.title_tag}")
    print(f"Related Keywords: {', '.join(metadata.related_keywords[:5])}")
    print(f"Quality Score: {metadata.quality_score}/100")

    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(metadata.recommendations, 1):
        print(f"   {i}. {rec}")


def example_4_batch_processing():
    """Example 4: Batch processing multiple articles."""
    print("\n" + "=" * 70)
    print("Example 4: Batch Processing with AI")
    print("=" * 70)

    articles = [
        {
            "title": "Introduction to Neural Networks",
            "script": "Neural networks are computational models inspired by the human brain. "
            "They consist of layers of interconnected nodes that process information. " * 5,
        },
        {
            "title": "Getting Started with Docker",
            "script": "Docker is a containerization platform that simplifies application deployment. "
            "It packages applications and dependencies into portable containers. " * 5,
        },
        {
            "title": "React Hooks: A Complete Guide",
            "script": "React Hooks revolutionized functional components in React. "
            "Learn how to use useState, useEffect, and custom hooks effectively. " * 5,
        },
    ]

    results = []
    for article in articles:
        result = process_content_seo(
            title=article["title"],
            script=article["script"],
            use_ai=True,
            brand_name="TechTutorials",
        )
        results.append(result)

    print(f"\n📊 Processed {len(results)} articles:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {articles[i-1]['title']}")
        print(f"   Keywords: {', '.join(result['primary_keywords'][:3])}")
        print(f"   Meta Desc: {result['meta_description'][:80]}...")
        print(f"   Score: {result['quality_score']}/100")


def example_5_fallback_handling():
    """Example 5: Handling AI unavailability with graceful fallback."""
    print("\n" + "=" * 70)
    print("Example 5: Graceful Fallback When AI Unavailable")
    print("=" * 70)

    title = "Kubernetes Best Practices for Production"
    script = """
    Kubernetes has become the de facto standard for container orchestration.
    This guide covers production-ready Kubernetes configurations, including
    high availability setups, security best practices, monitoring strategies,
    and disaster recovery plans. Learn how to optimize resource allocation,
    implement CI/CD pipelines, and manage secrets securely. We'll explore
    real-world scenarios and solutions for scaling applications in production.
    """

    # Configure AI to be unavailable (simulating Ollama not running)
    config = AIConfig(enable_ai=False)

    result = process_content_seo(
        title=title,
        script=script,
        use_ai=True,  # Request AI but it will fallback
        ai_config=config,
        brand_name="DevOps Hub",
    )

    print(f"AI Requested: Yes")
    print(f"AI Actually Used: {result.get('ai_generated', False)}")
    print(f"\n📝 Fallback Metadata:")
    print(f"Meta Description: {result['meta_description']}")
    print(f"Title Tag: {result['title_tag']}")
    print(f"Quality Score: {result['quality_score']}/100")
    print(f"\n✅ Graceful fallback to rule-based generation successful!")


def example_6_seo_optimization_workflow():
    """Example 6: Complete SEO optimization workflow."""
    print("\n" + "=" * 70)
    print("Example 6: Complete SEO Optimization Workflow")
    print("=" * 70)

    title = "Understanding Blockchain Technology and Cryptocurrencies"
    script = """
    Blockchain technology is transforming industries beyond cryptocurrency.
    This comprehensive guide explains the fundamentals of blockchain, including
    distributed ledgers, consensus mechanisms, and smart contracts. We'll explore
    how cryptocurrencies like Bitcoin and Ethereum work, discuss use cases in
    finance, supply chain, and healthcare, and examine the future of decentralized
    applications. Whether you're an investor, developer, or curious learner,
    this guide provides a solid foundation in blockchain technology.
    """

    print("Step 1: Extract Keywords...")
    extraction = extract_keywords(
        title=title, script=script, method="hybrid"  # Use hybrid method for best results
    )

    print(f"✓ Found {len(extraction.primary_keywords)} primary keywords")
    print(f"  Primary: {', '.join(extraction.primary_keywords[:5])}")

    print("\nStep 2: Generate AI-Powered Metadata...")
    result = process_content_seo(
        title=title, script=script, use_ai=True, extraction_method="hybrid", brand_name="CryptoEdu"
    )

    print(f"✓ Generated metadata with quality score: {result['quality_score']}/100")

    print("\nStep 3: Review SEO Metadata...")
    print(f"\n📝 Meta Description ({len(result['meta_description'])} chars):")
    print(f"   {result['meta_description']}")

    print(f"\n🏷️ Title Tag ({len(result['title_tag'])} chars):")
    print(f"   {result['title_tag']}")

    print(f"\n🔑 Keyword Density:")
    for keyword, density in list(result["keyword_density"].items())[:5]:
        print(f"   {keyword}: {density}%")

    print(f"\n💡 SEO Recommendations:")
    for i, rec in enumerate(result["recommendations"], 1):
        print(f"   {i}. {rec}")

    print(f"\n📱 Social Media (Open Graph):")
    print(f"   Title: {result['og_title']}")
    print(f"   Description: {result['og_description'][:80]}...")

    print("\nStep 4: Ready for Publishing!")
    print(f"✓ SEO optimization complete with AI-enhanced metadata")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("AI-POWERED SEO METADATA GENERATION EXAMPLES (POST-001)")
    print("Worker13: Prompt Engineering Master")
    print("=" * 70)

    print("\nNOTE: These examples demonstrate AI-powered metadata generation.")
    print("If Ollama is not running, examples will use rule-based fallback.")
    print("\nTo enable AI generation:")
    print("1. Install Ollama: https://ollama.com/")
    print("2. Pull the default model: ollama pull qwen3:32b")
    print("3. Run the server: ollama serve")

    try:
        # Run examples
        example_1_basic_ai_generation()
        example_2_compare_ai_vs_rulebased()
        example_3_custom_ai_config()
        example_4_batch_processing()
        example_5_fallback_handling()
        example_6_seo_optimization_workflow()

        print("\n" + "=" * 70)
        print("✅ All examples completed successfully!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install nltk scikit-learn requests")


if __name__ == "__main__":
    main()
