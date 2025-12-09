"""Example usage of Blog Formatter module.

This script demonstrates how to use the Blog Formatter to transform
scripts into blog-optimized content for various platforms.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

from T.Content.Formatter.Blog import BlogFormatter, export_for_platform, format_blog


def example_basic_usage():
    """Example 1: Basic blog formatting."""
    print("=" * 70)
    print("Example 1: Basic Blog Formatting")
    print("=" * 70)

    script = """
    This is a comprehensive story about innovation and how it shapes our world.
    
    Innovation is not just about new technologies. It's about new ways of thinking.
    It's about challenging assumptions and breaking boundaries. Throughout history,
    innovation has been the driving force behind human progress.
    
    Consider the industrial revolution. It transformed how we manufacture goods.
    It changed how we live and work. The same is true for the digital revolution.
    The internet connected billions of people. It created new industries.
    
    Today, we stand at the threshold of new innovations. Artificial intelligence
    is reshaping industries. Renewable energy is transforming how we power our world.
    Biotechnology is revolutionizing healthcare. These innovations will define our future.
    
    But innovation comes with challenges. We must consider ethical implications.
    We must ensure equitable access. We must balance progress with sustainability.
    
    The future belongs to those who innovate. Those who dare to dream.
    Those who are willing to take risks. Innovation is not just about technology.
    It's about human creativity and determination.
    """

    result = format_blog(
        script=script, title="Innovation: Shaping Our Future", content_id="blog-001"
    )

    if result.success:
        print("\n✅ Formatting successful!")
        print(f"\nMetadata:")
        print(f"  - Reading time: {result.metadata.reading_time}")
        print(f"  - Word count: {result.metadata.word_count}")
        print(f"  - Paragraph count: {result.metadata.paragraph_count}")
        print(f"  - Heading count: {result.metadata.heading_count}")
        print(f"\nExcerpt:")
        print(f"  {result.metadata.excerpt}")
        print(f"\nFormatted Content (first 500 chars):")
        print(f"{result.formatted_content[:500]}...")
    else:
        print(f"\n❌ Errors: {result.errors}")

    print("\n")


def example_platform_specific():
    """Example 2: Platform-specific exports."""
    print("=" * 70)
    print("Example 2: Platform-Specific Exports")
    print("=" * 70)

    script = """
    Machine learning is transforming the world of technology. From self-driving cars
    to personalized recommendations, ML algorithms are everywhere. But what exactly
    is machine learning, and why should you care?
    
    Machine learning is a subset of artificial intelligence. It enables computers
    to learn from data without being explicitly programmed. Instead of following
    rigid rules, ML systems adapt and improve over time.
    
    There are three main types of machine learning: supervised learning, unsupervised
    learning, and reinforcement learning. Each has its own use cases and applications.
    
    As we look to the future, machine learning will only become more important.
    It's not just a tool for tech companies. It's becoming essential across all
    industries, from healthcare to finance to entertainment.
    """

    platforms = ["medium", "wordpress", "ghost"]

    for platform in platforms:
        print(f"\n--- {platform.upper()} Export ---")

        format_type = "html" if platform == "wordpress" else "markdown"

        result = export_for_platform(
            script=script,
            title="Understanding Machine Learning",
            content_id=f"ml-{platform}",
            platform=platform,
            format_type=format_type,
        )

        if result.success:
            print(f"✅ {platform.capitalize()} export successful")
            print(f"   Format: {result.format_type}")
            print(f"   Reading time: {result.metadata.reading_time}")
            print(f"   First 200 chars:")
            print(f"   {result.formatted_content[:200]}...")
        else:
            print(f"❌ Errors: {result.errors}")

    print("\n")


def example_with_cta():
    """Example 3: Blog with Call-to-Action sections."""
    print("=" * 70)
    print("Example 3: Blog with Call-to-Action")
    print("=" * 70)

    script = """
    Content marketing is essential for business growth. It helps build trust,
    establish authority, and drive conversions. But creating effective content
    requires strategy and consistency.
    
    Start by understanding your audience. What are their pain points? What
    information are they seeking? Create content that addresses these needs.
    
    Use multiple formats: blog posts, videos, infographics, and podcasts.
    Different formats appeal to different audiences. Diversify your content
    to maximize reach.
    
    Measure your results. Track engagement metrics, conversion rates, and ROI.
    Use data to refine your strategy and improve performance.
    
    Remember, content marketing is a long-term investment. It takes time to
    build an audience and see results. But with patience and persistence,
    the rewards are substantial.
    """

    cta_text = "📧 Subscribe to our newsletter for weekly marketing tips and strategies!"

    result = format_blog(
        script=script,
        title="The Ultimate Guide to Content Marketing",
        content_id="cta-example",
        cta_text=cta_text,
        platform="medium",
    )

    if result.success:
        print("\n✅ Formatting with CTA successful!")
        print(f"\nCTA text: {cta_text}")
        print(f"\nCTA appears in blog: {'Yes' if cta_text in result.formatted_content else 'No'}")
        print(f"\nFormatted content length: {len(result.formatted_content)} chars")
        print(f"\nSample output:")
        print(result.formatted_content)
    else:
        print(f"\n❌ Errors: {result.errors}")

    print("\n")


def example_html_format():
    """Example 4: HTML output format."""
    print("=" * 70)
    print("Example 4: HTML Output Format")
    print("=" * 70)

    script = """
    Web design has evolved dramatically over the years. From simple text-based
    pages to rich, interactive experiences, the web has come a long way.
    
    Modern web design focuses on user experience. Responsive design ensures
    sites work on all devices. Accessibility ensures everyone can use your site.
    
    The future of web design includes AI-powered personalization, voice interfaces,
    and augmented reality experiences. Staying current with these trends is essential.
    """

    result = format_blog(
        script=script,
        title="The Evolution of Web Design",
        content_id="html-example",
        format_type="html",
    )

    if result.success:
        print("\n✅ HTML formatting successful!")
        print(f"\nFormat: {result.format_type}")
        print(f"\nHTML structure includes:")
        print(f"  - H1 tags: {'Yes' if '<h1>' in result.formatted_content else 'No'}")
        print(f"  - H2 tags: {'Yes' if '<h2>' in result.formatted_content else 'No'}")
        print(f"  - Paragraph tags: {'Yes' if '<p>' in result.formatted_content else 'No'}")
        print(f"\nFirst 400 chars of HTML:")
        print(result.formatted_content[:400])
    else:
        print(f"\n❌ Errors: {result.errors}")

    print("\n")


def example_metadata_analysis():
    """Example 5: Detailed metadata analysis."""
    print("=" * 70)
    print("Example 5: Metadata Analysis")
    print("=" * 70)

    # Create scripts of different lengths
    scripts = {
        "short": "Innovation. " * 50,  # ~50 words
        "medium": "Innovation drives progress. " * 100,  # ~300 words
        "long": "Innovation is the key to success. " * 300,  # ~1800 words
    }

    for length, script in scripts.items():
        result = format_blog(
            script=script, title=f"{length.capitalize()} Article", content_id=f"meta-{length}"
        )

        if result.success:
            print(f"\n{length.upper()} Article:")
            print(f"  Word count: {result.metadata.word_count}")
            print(f"  Character count: {result.metadata.char_count}")
            print(f"  Reading time: {result.metadata.reading_time}")
            print(f"  Paragraphs: {result.metadata.paragraph_count}")
            print(f"  Headings: {result.metadata.heading_count}")

    print("\n")


def main():
    """Run all examples."""
    print("\n")
    print("*" * 70)
    print("  BLOG FORMATTER - EXAMPLE USAGE")
    print("*" * 70)
    print("\n")

    # Run examples
    example_basic_usage()
    example_platform_specific()
    example_with_cta()
    example_html_format()
    example_metadata_analysis()

    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)
    print("\n")


if __name__ == "__main__":
    main()
