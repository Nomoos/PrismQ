"""Tests for PrismQ.T.Script.Formatter.Social module.

Tests cover:
- Base formatter utilities
- Twitter/X thread formatting
- LinkedIn post formatting
- Instagram caption formatting
- Facebook post formatting
- Character limit validation
- Edge cases and error handling
"""

import pytest
from T.Script.Formatter.Social import (
    # Base classes
    BaseSocialFormatter,
    SocialMediaContent,
    SocialMediaMetadata,
    # Twitter
    TwitterFormatter,
    format_twitter_thread,
    # LinkedIn
    LinkedInFormatter,
    format_linkedin_post,
    # Instagram
    InstagramFormatter,
    format_instagram_caption,
    # Facebook
    FacebookFormatter,
    format_facebook_post,
)


# Sample script for testing
SAMPLE_SCRIPT_SHORT = """
Innovation drives progress. Here's how we transformed our approach to solve real problems.
The challenge was clear: traditional methods weren't scaling. We needed a fresh perspective.
Our solution focused on three key areas: rethinking fundamentals, building incrementally, and testing relentlessly.
The results were remarkable: 10x improvement in efficiency, 85% cost reduction, and team satisfaction through the roof.
"""

SAMPLE_SCRIPT_MEDIUM = """
Innovation drives progress. Here's how we transformed our approach to solve real problems.
The challenge was clear: traditional methods weren't scaling. We needed a fresh perspective.
Our solution focused on three key areas: rethinking fundamentals, building incrementally, and testing relentlessly.
The results were remarkable: 10x improvement in efficiency, 85% cost reduction, and team satisfaction through the roof.
Innovation isn't about big leaps—it's about consistent, smart iteration.
Every small step compounds over time. When you focus on continuous improvement, you build momentum.
The key is maintaining discipline while staying adaptable. That's how real transformation happens.
We learned that the best innovations often come from questioning assumptions and trying new approaches.
Don't wait for perfect conditions. Start with what you have and iterate your way to excellence.
"""

SAMPLE_SCRIPT_LONG = SAMPLE_SCRIPT_MEDIUM * 3


# Test Dataclasses
class TestSocialMediaMetadata:
    """Test SocialMediaMetadata dataclass."""
    
    def test_metadata_creation(self):
        """Test creating metadata."""
        metadata = SocialMediaMetadata(
            platform="twitter",
            character_count=280,
            word_count=50
        )
        assert metadata.platform == "twitter"
        assert metadata.character_count == 280
        assert metadata.word_count == 50
    
    def test_metadata_to_dict(self):
        """Test converting metadata to dict."""
        metadata = SocialMediaMetadata(platform="linkedin")
        data = metadata.to_dict()
        assert isinstance(data, dict)
        assert data['platform'] == "linkedin"


class TestSocialMediaContent:
    """Test SocialMediaContent dataclass."""
    
    def test_content_creation(self):
        """Test creating social media content."""
        metadata = SocialMediaMetadata(platform="instagram")
        content = SocialMediaContent(
            content_id="test-001",
            platform="instagram",
            formatted_content="Test content",
            metadata=metadata
        )
        assert content.content_id == "test-001"
        assert content.platform == "instagram"
        assert content.success is True
    
    def test_content_to_dict(self):
        """Test converting content to dict."""
        metadata = SocialMediaMetadata(platform="facebook")
        content = SocialMediaContent(
            content_id="test-002",
            platform="facebook",
            formatted_content="Test",
            metadata=metadata
        )
        data = content.to_dict()
        assert isinstance(data, dict)
        assert data['content_id'] == "test-002"
        assert 'metadata' in data


# Test Base Formatter
class TestBaseSocialFormatter:
    """Test BaseSocialFormatter utilities."""
    
    def test_extract_key_points(self):
        """Test extracting key points from script."""
        formatter = BaseSocialFormatter()
        points = formatter._extract_key_points(SAMPLE_SCRIPT_SHORT, max_points=3)
        assert isinstance(points, list)
        assert len(points) <= 3
    
    def test_split_into_sentences(self):
        """Test sentence splitting."""
        formatter = BaseSocialFormatter()
        text = "First sentence. Second sentence! Third sentence?"
        sentences = formatter._split_into_sentences(text)
        assert len(sentences) == 3
    
    def test_generate_hook(self):
        """Test hook generation."""
        formatter = BaseSocialFormatter()
        hook = formatter._generate_hook(SAMPLE_SCRIPT_SHORT, "statement")
        assert isinstance(hook, str)
        assert len(hook) > 0
    
    def test_extract_hashtags(self):
        """Test hashtag extraction."""
        formatter = BaseSocialFormatter()
        hashtags = formatter._extract_hashtags(SAMPLE_SCRIPT_SHORT, 3, 5)
        assert isinstance(hashtags, list)
        assert 3 <= len(hashtags) <= 5
    
    def test_truncate_to_limit(self):
        """Test text truncation."""
        formatter = BaseSocialFormatter()
        long_text = "A" * 500
        truncated = formatter._truncate_to_limit(long_text, 100)
        assert len(truncated) <= 100


# Test Twitter Formatter
class TestTwitterFormatter:
    """Test TwitterFormatter."""
    
    def test_format_twitter_thread_basic(self):
        """Test basic Twitter thread formatting."""
        result = format_twitter_thread(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="twitter-001"
        )
        assert result.success is True
        assert result.platform == "twitter"
        assert len(result.formatted_content) > 0
    
    def test_twitter_character_limit(self):
        """Test Twitter character limit validation."""
        result = format_twitter_thread(
            script=SAMPLE_SCRIPT_MEDIUM,
            content_id="twitter-002"
        )
        # Check each tweet in thread
        tweets = result.formatted_content.split("\n\n")
        for tweet in tweets:
            assert len(tweet) <= 280, f"Tweet exceeds limit: {len(tweet)} chars"
    
    def test_twitter_thread_numbering(self):
        """Test thread numbering."""
        result = format_twitter_thread(
            script=SAMPLE_SCRIPT_MEDIUM,
            content_id="twitter-003"
        )
        # Should have thread numbers like "1/5", "2/5", etc.
        # Check that numbering pattern exists (could be 3, 4, 5, or 6 tweets)
        has_numbering = any(f"/{i}" in result.formatted_content for i in range(3, 10))
        assert has_numbering, "Thread should have numbering pattern"
    
    def test_twitter_with_cta(self):
        """Test Twitter thread with CTA."""
        result = format_twitter_thread(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="twitter-004",
            add_cta=True,
            cta_text="What do you think?"
        )
        assert "What do you think?" in result.formatted_content
    
    def test_twitter_with_emojis(self):
        """Test Twitter with emojis."""
        result = format_twitter_thread(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="twitter-005",
            add_emojis=True
        )
        # Should have at least one emoji
        assert any(ord(char) > 127 for char in result.formatted_content)
    
    def test_twitter_metadata(self):
        """Test Twitter metadata generation."""
        result = format_twitter_thread(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="twitter-006"
        )
        assert result.metadata.platform == "twitter"
        assert result.metadata.character_count > 0
        assert 0 <= result.metadata.estimated_engagement_score <= 100


# Test LinkedIn Formatter
class TestLinkedInFormatter:
    """Test LinkedInFormatter."""
    
    def test_format_linkedin_post_basic(self):
        """Test basic LinkedIn post formatting."""
        result = format_linkedin_post(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="linkedin-001"
        )
        assert result.success is True
        assert result.platform == "linkedin"
        assert len(result.formatted_content) > 0
    
    def test_linkedin_character_limit(self):
        """Test LinkedIn character limit."""
        result = format_linkedin_post(
            script=SAMPLE_SCRIPT_LONG,
            content_id="linkedin-002"
        )
        assert len(result.formatted_content) <= 3000
    
    def test_linkedin_preview_optimization(self):
        """Test LinkedIn preview (first 140 chars)."""
        result = format_linkedin_post(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="linkedin-003"
        )
        # First line should be compelling hook
        first_line = result.formatted_content.split('\n')[0]
        assert len(first_line) <= 140
    
    def test_linkedin_with_hashtags(self):
        """Test LinkedIn with hashtags."""
        result = format_linkedin_post(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="linkedin-004",
            add_hashtags=True,
            num_hashtags=5
        )
        # Should have hashtags
        assert '#' in result.formatted_content
        assert len(result.metadata.hashtags) <= 5
    
    def test_linkedin_structure(self):
        """Test LinkedIn post structure."""
        result = format_linkedin_post(
            script=SAMPLE_SCRIPT_MEDIUM,
            content_id="linkedin-005"
        )
        # Should have proper structure with line breaks
        assert '\n\n' in result.formatted_content
    
    def test_linkedin_metadata(self):
        """Test LinkedIn metadata."""
        result = format_linkedin_post(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="linkedin-006"
        )
        assert result.metadata.platform == "linkedin"
        assert result.metadata.estimated_engagement_score > 0


# Test Instagram Formatter
class TestInstagramFormatter:
    """Test InstagramFormatter."""
    
    def test_format_instagram_caption_basic(self):
        """Test basic Instagram caption formatting."""
        result = format_instagram_caption(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="instagram-001"
        )
        assert result.success is True
        assert result.platform == "instagram"
        assert len(result.formatted_content) > 0
    
    def test_instagram_character_limit(self):
        """Test Instagram character limit."""
        result = format_instagram_caption(
            script=SAMPLE_SCRIPT_LONG,
            content_id="instagram-002"
        )
        assert len(result.formatted_content) <= 2200
    
    def test_instagram_preview(self):
        """Test Instagram preview optimization."""
        result = format_instagram_caption(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="instagram-003"
        )
        # Should have engaging first line
        first_line = result.formatted_content.split('\n')[0]
        assert len(first_line) <= 125
    
    def test_instagram_separator(self):
        """Test Instagram line separator."""
        result = format_instagram_caption(
            script=SAMPLE_SCRIPT_MEDIUM,
            content_id="instagram-004"
        )
        # Should have Instagram-style separator
        assert '\n.\n.\n.\n' in result.formatted_content
    
    def test_instagram_with_hashtags(self):
        """Test Instagram with hashtags."""
        result = format_instagram_caption(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="instagram-005",
            add_hashtags=True,
            num_hashtags=15
        )
        # Should have multiple hashtags (10-20)
        hashtag_count = result.formatted_content.count('#')
        assert 10 <= hashtag_count <= 20
    
    def test_instagram_with_emojis(self):
        """Test Instagram with emojis."""
        result = format_instagram_caption(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="instagram-006",
            add_emojis=True
        )
        # Should have emojis
        assert any(ord(char) > 127 for char in result.formatted_content)
    
    def test_instagram_metadata(self):
        """Test Instagram metadata."""
        result = format_instagram_caption(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="instagram-007"
        )
        assert result.metadata.platform == "instagram"
        assert len(result.metadata.hashtags) > 0


# Test Facebook Formatter
class TestFacebookFormatter:
    """Test FacebookFormatter."""
    
    def test_format_facebook_post_basic(self):
        """Test basic Facebook post formatting."""
        result = format_facebook_post(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="facebook-001"
        )
        assert result.success is True
        assert result.platform == "facebook"
        assert len(result.formatted_content) > 0
    
    def test_facebook_practical_limit(self):
        """Test Facebook practical length limit."""
        result = format_facebook_post(
            script=SAMPLE_SCRIPT_LONG,
            content_id="facebook-002"
        )
        # Should be under practical limit (5000)
        assert len(result.formatted_content) <= 5000
    
    def test_facebook_preview_optimization(self):
        """Test Facebook preview (first 400 chars)."""
        result = format_facebook_post(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="facebook-003",
            optimize_preview=True
        )
        # Should have compelling opening
        assert len(result.formatted_content) > 0
    
    def test_facebook_with_engagement_question(self):
        """Test Facebook with engagement question."""
        result = format_facebook_post(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="facebook-004",
            add_engagement_question=True
        )
        # Should have a question
        assert '?' in result.formatted_content
    
    def test_facebook_structure(self):
        """Test Facebook post structure."""
        result = format_facebook_post(
            script=SAMPLE_SCRIPT_MEDIUM,
            content_id="facebook-005"
        )
        # Should have paragraph breaks
        assert '\n\n' in result.formatted_content
    
    def test_facebook_metadata(self):
        """Test Facebook metadata."""
        result = format_facebook_post(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="facebook-006"
        )
        assert result.metadata.platform == "facebook"
        assert result.metadata.estimated_engagement_score > 0


# Test Edge Cases
class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_script(self):
        """Test handling of empty script."""
        result = format_twitter_thread(
            script="",
            content_id="edge-001"
        )
        # Should handle gracefully
        assert isinstance(result, SocialMediaContent)
    
    def test_very_short_script(self):
        """Test handling of very short script."""
        result = format_linkedin_post(
            script="Short.",
            content_id="edge-002"
        )
        assert result.success is True
        assert len(result.formatted_content) > 0
    
    def test_script_with_special_characters(self):
        """Test handling of special characters."""
        script = "Test with special chars: @#$%^&*()"
        result = format_instagram_caption(
            script=script,
            content_id="edge-003"
        )
        assert result.success is True
    
    def test_script_with_urls(self):
        """Test handling of URLs in script."""
        script = "Check out https://example.com for more info."
        result = format_facebook_post(
            script=script,
            content_id="edge-004"
        )
        assert result.success is True
        assert "https://example.com" in result.formatted_content


# Test Platform-Specific Features
class TestPlatformSpecificFeatures:
    """Test platform-specific formatting features."""
    
    def test_twitter_hook_types(self):
        """Test different Twitter hook types."""
        for hook_type in ["question", "statement", "stat"]:
            result = format_twitter_thread(
                script=SAMPLE_SCRIPT_SHORT,
                content_id=f"twitter-hook-{hook_type}",
                hook_type=hook_type
            )
            assert result.success is True
    
    def test_linkedin_bullet_formatting(self):
        """Test LinkedIn bullet point formatting."""
        result = format_linkedin_post(
            script=SAMPLE_SCRIPT_MEDIUM,
            content_id="linkedin-bullets"
        )
        # Should use arrows for key takeaways
        assert '→' in result.formatted_content or 'Key Takeaways' in result.formatted_content
    
    def test_instagram_engagement_prompts(self):
        """Test Instagram engagement prompts."""
        result = format_instagram_caption(
            script=SAMPLE_SCRIPT_SHORT,
            content_id="instagram-engagement",
            add_engagement_prompt=True
        )
        # Should have engagement language
        assert any(word in result.formatted_content.lower() 
                  for word in ['comment', 'tag', 'share', 'save'])


# Test Convenience Functions
class TestConvenienceFunctions:
    """Test convenience functions work correctly."""
    
    def test_all_convenience_functions(self):
        """Test all convenience functions."""
        script = SAMPLE_SCRIPT_SHORT
        
        twitter = format_twitter_thread(script, "conv-twitter")
        assert twitter.platform == "twitter"
        
        linkedin = format_linkedin_post(script, "conv-linkedin")
        assert linkedin.platform == "linkedin"
        
        instagram = format_instagram_caption(script, "conv-instagram")
        assert instagram.platform == "instagram"
        
        facebook = format_facebook_post(script, "conv-facebook")
        assert facebook.platform == "facebook"


# Test Multiple Variants
class TestMultipleVariants:
    """Test generating multiple variants for A/B testing."""
    
    def test_twitter_different_hooks(self):
        """Test Twitter with different hook styles."""
        variants = []
        for hook_type in ["question", "statement", "stat"]:
            result = format_twitter_thread(
                script=SAMPLE_SCRIPT_SHORT,
                content_id=f"variant-{hook_type}",
                hook_type=hook_type
            )
            variants.append(result)
        
        # Variants should be different
        contents = [v.formatted_content for v in variants]
        assert len(set(contents)) > 1  # At least some variation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
