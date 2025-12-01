"""Instagram caption formatter for PrismQ.T.Script.Formatter.Social.

This module transforms scripts into Instagram caption format with preview
optimization, line breaks, and hashtag management.
"""

from typing import List, Optional
from .base_formatter import BaseSocialFormatter, SocialMediaContent, SocialMediaMetadata


class InstagramFormatter(BaseSocialFormatter):
    """Format scripts into Instagram captions.
    
    Creates engaging Instagram captions with:
    - 2,200 character limit (first 125 visible in feed)
    - Engaging preview (first 125 characters)
    - Line breaks for readability (using ... separator)
    - 10-20 relevant hashtags
    - Emojis for visual appeal
    - Engagement prompts
    """
    
    # Instagram character limits
    CHAR_LIMIT = 2200
    PREVIEW_LIMIT = 125  # Characters visible before "more"
    
    # Hashtag recommendations
    MIN_HASHTAGS = 10
    MAX_HASHTAGS = 20
    
    def __init__(self):
        """Initialize Instagram formatter."""
        super().__init__()
    
    def format_instagram_caption(
        self,
        script: str,
        content_id: str,
        add_hashtags: bool = True,
        num_hashtags: int = 15,
        add_emojis: bool = True,
        add_engagement_prompt: bool = True
    ) -> SocialMediaContent:
        """Format script into Instagram caption.
        
        Args:
            script: Script content to format
            content_id: Unique identifier for content
            add_hashtags: Whether to add hashtags
            num_hashtags: Number of hashtags (10-20 recommended)
            add_emojis: Whether to add emojis
            add_engagement_prompt: Whether to add engagement question
        
        Returns:
            SocialMediaContent with Instagram caption
        """
        result = SocialMediaContent(
            content_id=content_id,
            platform="instagram",
            formatted_content="",
            metadata=SocialMediaMetadata(platform="instagram")
        )
        
        try:
            # Step 1: Create engaging preview (first 125 chars)
            preview = self._create_instagram_preview(script, add_emojis)
            
            # Step 2: Format main content with line breaks
            main_content = self._format_instagram_content(script)
            
            # Step 3: Add visual separator
            separator = "\n.\n.\n.\n"
            
            # Step 4: Extract key message
            key_message = self._extract_key_message(script)
            
            # Step 5: Build caption sections
            sections = []
            sections.append(preview)
            sections.append(separator)
            sections.append(main_content)
            
            # Add key message if different from main content
            if key_message and key_message[:50] not in main_content[:100]:
                sections.append(separator)
                sections.append(key_message)
            
            # Step 6: Add engagement prompt
            if add_engagement_prompt:
                prompt = self._generate_engagement_prompt()
                sections.append("")
                sections.append(prompt)
            
            # Step 7: Add hashtags
            hashtags = []
            if add_hashtags:
                hashtags = self._extract_instagram_hashtags(script, num_hashtags)
                sections.append("")
                sections.append("")
                hashtag_line = " ".join(f"#{tag}" for tag in hashtags)
                sections.append(hashtag_line)
            
            # Step 8: Combine sections
            full_caption = "\n".join(sections)
            
            # Step 9: Validate character limit
            if len(full_caption) > self.CHAR_LIMIT:
                # Truncate main content, keep hashtags
                truncated = self._truncate_caption(
                    preview, main_content, key_message, 
                    hashtags, self.CHAR_LIMIT
                )
                full_caption = truncated
            
            result.formatted_content = full_caption
            
            # Step 10: Generate metadata
            result.metadata = self._generate_instagram_metadata(
                full_caption, hashtags
            )
            
        except Exception as e:
            result.errors.append(f"Instagram formatting error: {str(e)}")
            result.success = False
        
        return result
    
    def _create_instagram_preview(self, script: str, add_emojis: bool) -> str:
        """Create engaging preview for first 125 characters.
        
        Args:
            script: Script content
            add_emojis: Whether to add emoji
        
        Returns:
            Preview text
        """
        # Get first sentence or compelling hook
        sentences = self._split_into_sentences(script)
        
        if not sentences:
            preview = "Check this out!"
        else:
            preview = sentences[0]
        
        # Ensure it fits in preview
        if len(preview) > self.PREVIEW_LIMIT - 5:  # Leave room for emoji
            preview = self._truncate_to_limit(preview, self.PREVIEW_LIMIT - 5, "...")
        
        # Add emoji if requested
        if add_emojis:
            preview = self._add_instagram_emoji(preview)
        
        return preview
    
    def _format_instagram_content(self, script: str) -> str:
        """Format main content with Instagram line breaks.
        
        Args:
            script: Script content
        
        Returns:
            Formatted content
        """
        # Split into sentences
        sentences = self._split_into_sentences(script)
        
        # Skip first sentence (used in preview)
        content_sentences = sentences[1:] if len(sentences) > 1 else sentences
        
        # Group into short paragraphs (1-2 sentences each for Instagram)
        paragraphs = []
        for i in range(0, len(content_sentences), 2):
            para = " ".join(content_sentences[i:i+2])
            paragraphs.append(para)
        
        # Join with single newline (Instagram style)
        content = "\n\n".join(paragraphs[:3])  # Limit to 3 paragraphs
        
        return content
    
    def _extract_key_message(self, script: str) -> str:
        """Extract key message for Instagram.
        
        Args:
            script: Script content
        
        Returns:
            Key message
        """
        # Look for impactful sentences with numbers or strong words
        sentences = self._split_into_sentences(script)
        
        for sentence in sentences:
            # Look for sentences with results, numbers, or strong impact
            if any(word in sentence.lower() for word in 
                   ['result', 'achieve', 'transform', 'improve', '%', 'x']):
                return sentence
        
        # Fall back to a middle sentence
        if len(sentences) > 2:
            return sentences[len(sentences) // 2]
        
        return ""
    
    def _generate_engagement_prompt(self) -> str:
        """Generate Instagram engagement prompt.
        
        Returns:
            Engagement prompt
        """
        prompts = [
            "What's your take? Drop a comment! 👇",
            "Tag someone who needs to see this! 💫",
            "Save this for later! 🔖",
            "Share your story below! ⬇️",
            "Double tap if you agree! ❤️"
        ]
        return prompts[0]
    
    def _add_instagram_emoji(self, text: str) -> str:
        """Add relevant emoji to text.
        
        Args:
            text: Text to enhance
        
        Returns:
            Text with emoji
        """
        # Add emoji at the end if not present
        common_emojis = ['✨', '💫', '🚀', '💡', '🎯', '🔥', '💪']
        
        if not any(emoji in text for emoji in common_emojis):
            # Add contextually relevant emoji
            if any(word in text.lower() for word in ['success', 'achieve', 'win']):
                return f"{text} 🎯"
            elif any(word in text.lower() for word in ['growth', 'improve', 'transform']):
                return f"{text} 🚀"
            else:
                return f"{text} ✨"
        
        return text
    
    def _extract_instagram_hashtags(self, script: str, num_hashtags: int) -> List[str]:
        """Extract Instagram-optimized hashtags.
        
        Args:
            script: Script content
            num_hashtags: Target number of hashtags
        
        Returns:
            List of hashtags
        """
        # Get base hashtags
        base_hashtags = self._extract_hashtags(script, 5, 10)
        
        # Add Instagram-specific popular hashtags
        instagram_hashtags = [
            'Instagram', 'InstaGood', 'PhotoOfTheDay', 'InstaDaily',
            'Motivation', 'Inspiration', 'Goals', 'Success',
            'GrowthMindset', 'Mindset', 'Entrepreneur', 'Business',
            'ContentCreator', 'DigitalMarketing', 'SocialMedia'
        ]
        
        # Combine and limit
        all_hashtags = base_hashtags + [tag for tag in instagram_hashtags 
                                        if tag not in base_hashtags]
        
        return all_hashtags[:num_hashtags]
    
    def _truncate_caption(
        self,
        preview: str,
        main_content: str,
        key_message: str,
        hashtags: List[str],
        limit: int
    ) -> str:
        """Truncate caption to character limit.
        
        Args:
            preview: Preview text
            main_content: Main content
            key_message: Key message
            hashtags: List of hashtags
            limit: Character limit
        
        Returns:
            Truncated caption
        """
        # Build sections with priority
        hashtag_line = " ".join(f"#{tag}" for tag in hashtags)
        hashtag_length = len(hashtag_line) + 10  # +10 for spacing
        
        # Calculate available space for content
        available = limit - hashtag_length - len(preview) - 20  # Buffer
        
        # Truncate main content
        if len(main_content) > available:
            main_content = self._truncate_to_limit(main_content, available, "...")
        
        # Build final caption
        separator = "\n.\n.\n.\n"
        caption = f"{preview}{separator}{main_content}\n\n{hashtag_line}"
        
        return caption
    
    def _generate_instagram_metadata(
        self,
        caption: str,
        hashtags: List[str]
    ) -> SocialMediaMetadata:
        """Generate metadata for Instagram caption.
        
        Args:
            caption: Full caption
            hashtags: List of hashtags
        
        Returns:
            SocialMediaMetadata
        """
        metadata = SocialMediaMetadata(
            platform="instagram",
            character_count=len(caption),
            word_count=len(caption.split()),
            estimated_engagement_score=self._estimate_instagram_engagement(
                caption, hashtags
            ),
            suggested_posting_time="11:00 AM - 1:00 PM, 7:00 PM - 9:00 PM",
            hashtags=hashtags,
            variant_count=1
        )
        
        return metadata
    
    def _estimate_instagram_engagement(
        self,
        caption: str,
        hashtags: List[str]
    ) -> int:
        """Estimate engagement score for Instagram post.
        
        Args:
            caption: Full caption
            hashtags: List of hashtags
        
        Returns:
            Engagement score (0-100)
        """
        score = 50  # Base score
        
        # Bonus for optimal caption length (500-1500 chars)
        caption_len = len(caption)
        if 500 <= caption_len <= 1500:
            score += 10
        
        # Bonus for line breaks
        if '\n.\n.\n.\n' in caption:
            score += 10
        
        # Bonus for emojis
        emoji_count = sum(1 for char in caption if ord(char) > 127)
        if emoji_count >= 3:
            score += 10
        
        # Bonus for hashtags (10-20 is optimal)
        if 10 <= len(hashtags) <= 20:
            score += 15
        
        # Bonus for engagement prompt
        if any(word in caption.lower() for word in ['comment', 'tag', 'share', 'save']):
            score += 10
        
        return min(max(score, 0), 100)


def format_instagram_caption(
    script: str,
    content_id: str,
    add_hashtags: bool = True,
    num_hashtags: int = 15,
    add_emojis: bool = True,
    add_engagement_prompt: bool = True
) -> SocialMediaContent:
    """Convenience function to format script as Instagram caption.
    
    Args:
        script: Script content to format
        content_id: Unique identifier for content
        add_hashtags: Whether to add hashtags
        num_hashtags: Number of hashtags (10-20)
        add_emojis: Whether to add emojis
        add_engagement_prompt: Whether to add engagement question
    
    Returns:
        SocialMediaContent with Instagram caption
    """
    formatter = InstagramFormatter()
    return formatter.format_instagram_caption(
        script=script,
        content_id=content_id,
        add_hashtags=add_hashtags,
        num_hashtags=num_hashtags,
        add_emojis=add_emojis,
        add_engagement_prompt=add_engagement_prompt
    )
