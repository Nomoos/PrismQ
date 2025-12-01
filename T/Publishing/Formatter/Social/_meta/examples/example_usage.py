"""Example usage of PrismQ.T.Script.Formatter.Social module.

This file demonstrates various use cases for the Social Media Formatter
including basic usage, A/B testing, custom options, and error handling.

Note: This example file is for documentation purposes and shows the expected
      usage patterns. To run it, ensure the T.Script.Formatter.Social module
      is properly installed in your Python path.
      
Usage Pattern (adjust import based on your setup):
    from T.Script.Formatter.Social import format_twitter_thread, ...
"""

# For documentation: show the correct import pattern
# In actual usage, uncomment these imports:
"""
from T.Script.Formatter.Social import (
    format_twitter_thread,
    format_linkedin_post,
    format_instagram_caption,
    format_facebook_post,
    TwitterFormatter,
    LinkedInFormatter,
    InstagramFormatter,
    FacebookFormatter,
)
"""

# For this example file to run standalone, we'll mock the imports
# In production, use the actual imports above
import sys
from pathlib import Path

# Mock setup for standalone execution
try:
    from T.Script.Formatter.Social import (
        format_twitter_thread,
        format_linkedin_post,
        format_instagram_caption,
        format_facebook_post,
        TwitterFormatter,
        LinkedInFormatter,
        InstagramFormatter,
        FacebookFormatter,
    )
except ImportError:
    print("Note: This example requires the T.Script.Formatter.Social module.")
    print("In production, use: from T.Script.Formatter.Social import ...")
    sys.exit(0)


# Sample script content
SAMPLE_SCRIPT = """
Innovation drives progress. Here's how we transformed our approach to solve real problems.
The challenge was clear: traditional methods weren't scaling. We needed a fresh perspective.
Our solution focused on three key areas: rethinking fundamentals, building incrementally, and testing relentlessly.
The results were remarkable: 10x improvement in efficiency, 85% cost reduction, and team satisfaction through the roof.
Innovation isn't about big leaps—it's about consistent, smart iteration.
Every small step compounds over time. When you focus on continuous improvement, you build momentum.
The key is maintaining discipline while staying adaptable. That's how real transformation happens.
"""


def example_1_twitter_basic():
    """Example 1: Basic Twitter thread formatting."""
    print("=" * 60)
    print("Example 1: Basic Twitter Thread")
    print("=" * 60)
    
    result = format_twitter_thread(
        script=SAMPLE_SCRIPT,
        content_id="twitter-001"
    )
    
    if result.success:
        print("\n✅ Twitter Thread Generated:")
        print(result.formatted_content)
        print(f"\n📊 Metadata:")
        print(f"  - Character Count: {result.metadata.character_count}")
        print(f"  - Engagement Score: {result.metadata.estimated_engagement_score}/100")
        print(f"  - Suggested Time: {result.metadata.suggested_posting_time}")
    else:
        print("❌ Error:", result.errors)
    
    print("\n")


def example_2_twitter_with_custom_options():
    """Example 2: Twitter thread with custom options."""
    print("=" * 60)
    print("Example 2: Twitter Thread with Custom Options")
    print("=" * 60)
    
    result = format_twitter_thread(
        script=SAMPLE_SCRIPT,
        content_id="twitter-002",
        hook_type="question",  # Use question hook
        add_cta=True,
        cta_text="What's your innovation story? Share below! 👇",
        add_emojis=True
    )
    
    if result.success:
        print("\n✅ Custom Twitter Thread:")
        print(result.formatted_content)
    
    print("\n")


def example_3_linkedin_basic():
    """Example 3: Basic LinkedIn post formatting."""
    print("=" * 60)
    print("Example 3: Basic LinkedIn Post")
    print("=" * 60)
    
    result = format_linkedin_post(
        script=SAMPLE_SCRIPT,
        content_id="linkedin-001"
    )
    
    if result.success:
        print("\n✅ LinkedIn Post Generated:")
        print(result.formatted_content)
        print(f"\n📊 Metadata:")
        print(f"  - Character Count: {result.metadata.character_count}")
        print(f"  - Hashtags: {', '.join(result.metadata.hashtags)}")
        print(f"  - Engagement Score: {result.metadata.estimated_engagement_score}/100")
    
    print("\n")


def example_4_linkedin_custom_hashtags():
    """Example 4: LinkedIn with custom hashtag count."""
    print("=" * 60)
    print("Example 4: LinkedIn with Custom Hashtags")
    print("=" * 60)
    
    result = format_linkedin_post(
        script=SAMPLE_SCRIPT,
        content_id="linkedin-002",
        hook_type="stat",  # Use stat-based hook
        add_hashtags=True,
        num_hashtags=3,  # Only 3 hashtags
        add_cta=True,
        cta_text="What's been your biggest innovation win?"
    )
    
    if result.success:
        print("\n✅ LinkedIn Post with 3 Hashtags:")
        print(result.formatted_content)
    
    print("\n")


def example_5_instagram_basic():
    """Example 5: Basic Instagram caption formatting."""
    print("=" * 60)
    print("Example 5: Basic Instagram Caption")
    print("=" * 60)
    
    result = format_instagram_caption(
        script=SAMPLE_SCRIPT,
        content_id="instagram-001"
    )
    
    if result.success:
        print("\n✅ Instagram Caption Generated:")
        print(result.formatted_content)
        print(f"\n📊 Metadata:")
        print(f"  - Character Count: {result.metadata.character_count}")
        print(f"  - Hashtag Count: {len(result.metadata.hashtags)}")
        print(f"  - Engagement Score: {result.metadata.estimated_engagement_score}/100")
    
    print("\n")


def example_6_instagram_minimal_hashtags():
    """Example 6: Instagram with minimal hashtags."""
    print("=" * 60)
    print("Example 6: Instagram with Minimal Hashtags")
    print("=" * 60)
    
    result = format_instagram_caption(
        script=SAMPLE_SCRIPT,
        content_id="instagram-002",
        add_hashtags=True,
        num_hashtags=10,  # Minimal hashtags
        add_emojis=True,
        add_engagement_prompt=True
    )
    
    if result.success:
        print("\n✅ Instagram Caption with 10 Hashtags:")
        print(result.formatted_content)
    
    print("\n")


def example_7_facebook_basic():
    """Example 7: Basic Facebook post formatting."""
    print("=" * 60)
    print("Example 7: Basic Facebook Post")
    print("=" * 60)
    
    result = format_facebook_post(
        script=SAMPLE_SCRIPT,
        content_id="facebook-001"
    )
    
    if result.success:
        print("\n✅ Facebook Post Generated:")
        print(result.formatted_content)
        print(f"\n📊 Metadata:")
        print(f"  - Character Count: {result.metadata.character_count}")
        print(f"  - Engagement Score: {result.metadata.estimated_engagement_score}/100")
    
    print("\n")


def example_8_facebook_no_preview():
    """Example 8: Facebook without preview optimization."""
    print("=" * 60)
    print("Example 8: Facebook without Preview Optimization")
    print("=" * 60)
    
    result = format_facebook_post(
        script=SAMPLE_SCRIPT,
        content_id="facebook-002",
        add_engagement_question=True,
        use_emojis=False,
        optimize_preview=False
    )
    
    if result.success:
        print("\n✅ Facebook Post (No Preview Optimization):")
        print(result.formatted_content)
    
    print("\n")


def example_9_ab_testing_variants():
    """Example 9: Generate A/B testing variants for Twitter."""
    print("=" * 60)
    print("Example 9: A/B Testing Variants (Twitter)")
    print("=" * 60)
    
    hook_types = ["question", "statement", "stat"]
    variants = []
    
    for i, hook_type in enumerate(hook_types, 1):
        result = format_twitter_thread(
            script=SAMPLE_SCRIPT,
            content_id=f"twitter-variant-{i}",
            hook_type=hook_type,
            add_emojis=(i % 2 == 0)  # Alternate emoji usage
        )
        variants.append((hook_type, result))
    
    print("\n✅ Generated 3 Variants:")
    for hook_type, result in variants:
        if result.success:
            first_tweet = result.formatted_content.split('\n\n')[0]
            print(f"\nVariant ({hook_type}):")
            print(f"  First Tweet: {first_tweet}")
            print(f"  Engagement Score: {result.metadata.estimated_engagement_score}/100")
    
    print("\n")


def example_10_batch_processing():
    """Example 10: Batch process multiple scripts."""
    print("=" * 60)
    print("Example 10: Batch Processing Multiple Scripts")
    print("=" * 60)
    
    scripts = [
        "Innovation drives progress. Transform your approach.",
        "Success comes from consistent effort. Small steps lead to big results.",
        "Leadership isn't about authority. It's about enabling others to succeed."
    ]
    
    results = []
    
    for i, script in enumerate(scripts, 1):
        # Generate for all platforms
        twitter = format_twitter_thread(script, f"batch-twitter-{i}")
        linkedin = format_linkedin_post(script, f"batch-linkedin-{i}")
        instagram = format_instagram_caption(script, f"batch-instagram-{i}")
        facebook = format_facebook_post(script, f"batch-facebook-{i}")
        
        results.append({
            'script': script[:50] + "...",
            'twitter': twitter.success,
            'linkedin': linkedin.success,
            'instagram': instagram.success,
            'facebook': facebook.success
        })
    
    print("\n✅ Batch Processing Results:")
    for i, result in enumerate(results, 1):
        print(f"\nScript {i}: {result['script']}")
        print(f"  Twitter: {'✅' if result['twitter'] else '❌'}")
        print(f"  LinkedIn: {'✅' if result['linkedin'] else '❌'}")
        print(f"  Instagram: {'✅' if result['instagram'] else '❌'}")
        print(f"  Facebook: {'✅' if result['facebook'] else '❌'}")
    
    print("\n")


def example_11_using_formatter_classes():
    """Example 11: Using formatter classes directly."""
    print("=" * 60)
    print("Example 11: Using Formatter Classes Directly")
    print("=" * 60)
    
    # Create formatter instances
    twitter_formatter = TwitterFormatter()
    linkedin_formatter = LinkedInFormatter()
    instagram_formatter = InstagramFormatter()
    facebook_formatter = FacebookFormatter()
    
    # Use formatters
    twitter_result = twitter_formatter.format_twitter_thread(
        script=SAMPLE_SCRIPT,
        content_id="class-twitter-001",
        hook_type="statement"
    )
    
    linkedin_result = linkedin_formatter.format_linkedin_post(
        script=SAMPLE_SCRIPT,
        content_id="class-linkedin-001"
    )
    
    print("\n✅ Using Formatter Classes:")
    print(f"  Twitter: {twitter_result.success}")
    print(f"  LinkedIn: {linkedin_result.success}")
    
    print("\n")


def example_12_error_handling():
    """Example 12: Error handling with edge cases."""
    print("=" * 60)
    print("Example 12: Error Handling")
    print("=" * 60)
    
    # Test with empty script
    result_empty = format_twitter_thread(
        script="",
        content_id="error-001"
    )
    
    print(f"\nEmpty Script:")
    print(f"  Success: {result_empty.success}")
    print(f"  Errors: {result_empty.errors if result_empty.errors else 'None'}")
    
    # Test with very short script
    result_short = format_linkedin_post(
        script="Short.",
        content_id="error-002"
    )
    
    print(f"\nVery Short Script:")
    print(f"  Success: {result_short.success}")
    print(f"  Content Length: {len(result_short.formatted_content)}")
    
    # Test with special characters
    result_special = format_instagram_caption(
        script="Test with @#$%^&*()",
        content_id="error-003"
    )
    
    print(f"\nSpecial Characters:")
    print(f"  Success: {result_special.success}")
    
    print("\n")


def example_13_metadata_analysis():
    """Example 13: Analyzing metadata for optimization."""
    print("=" * 60)
    print("Example 13: Metadata Analysis")
    print("=" * 60)
    
    # Generate content for all platforms
    platforms = {
        'Twitter': format_twitter_thread(SAMPLE_SCRIPT, "meta-twitter"),
        'LinkedIn': format_linkedin_post(SAMPLE_SCRIPT, "meta-linkedin"),
        'Instagram': format_instagram_caption(SAMPLE_SCRIPT, "meta-instagram"),
        'Facebook': format_facebook_post(SAMPLE_SCRIPT, "meta-facebook")
    }
    
    print("\n✅ Metadata Comparison:")
    print(f"\n{'Platform':<12} {'Chars':<8} {'Words':<8} {'Engagement':<12} {'Hashtags'}")
    print("-" * 60)
    
    for platform, result in platforms.items():
        if result.success:
            m = result.metadata
            hashtag_count = len(m.hashtags) if m.hashtags else 0
            print(f"{platform:<12} {m.character_count:<8} {m.word_count:<8} "
                  f"{m.estimated_engagement_score:<12} {hashtag_count}")
    
    print("\n")


def run_all_examples():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("SOCIAL MEDIA FORMATTER - EXAMPLE USAGE")
    print("=" * 60 + "\n")
    
    example_1_twitter_basic()
    example_2_twitter_with_custom_options()
    example_3_linkedin_basic()
    example_4_linkedin_custom_hashtags()
    example_5_instagram_basic()
    example_6_instagram_minimal_hashtags()
    example_7_facebook_basic()
    example_8_facebook_no_preview()
    example_9_ab_testing_variants()
    example_10_batch_processing()
    example_11_using_formatter_classes()
    example_12_error_handling()
    example_13_metadata_analysis()
    
    print("=" * 60)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    # Run individual example or all examples
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        example_func = f"example_{example_num}"
        if example_func in globals():
            globals()[example_func]()
        else:
            print(f"Example {example_num} not found.")
            print("Available examples: 1-13")
    else:
        # Run all examples
        run_all_examples()
