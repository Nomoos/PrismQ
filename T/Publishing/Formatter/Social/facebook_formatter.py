"""Facebook post formatter for PrismQ.T.Script.Formatter.Social.

This module transforms scripts into Facebook post format with preview
optimization and engagement features.
"""

from typing import Optional

from .base_formatter import BaseSocialFormatter, SocialMediaContent, SocialMediaMetadata


class FacebookFormatter(BaseSocialFormatter):
    """Format scripts into Facebook posts.

    Creates engaging Facebook posts with:
    - 63,206 character limit (first 400 visible in feed)
    - Compelling preview (first 400 characters)
    - Paragraph breaks every 2-3 sentences
    - Questions to drive engagement
    - Link preview optimization considerations
    """

    # Facebook character limits
    CHAR_LIMIT = 63206  # Theoretical limit
    PRACTICAL_LIMIT = 5000  # Practical recommended limit
    PREVIEW_LIMIT = 400  # Characters visible before "see more"

    def __init__(self):
        """Initialize Facebook formatter."""
        super().__init__()

    def format_facebook_post(
        self,
        script: str,
        content_id: str,
        add_engagement_question: bool = True,
        use_emojis: bool = True,
        optimize_preview: bool = True,
    ) -> SocialMediaContent:
        """Format script into Facebook post.

        Args:
            script: Script content to format
            content_id: Unique identifier for content
            add_engagement_question: Whether to add engagement question
            use_emojis: Whether to add relevant emojis
            optimize_preview: Whether to optimize for preview visibility

        Returns:
            SocialMediaContent with Facebook post
        """
        result = SocialMediaContent(
            content_id=content_id,
            platform="facebook",
            formatted_content="",
            metadata=SocialMediaMetadata(platform="facebook"),
        )

        try:
            # Step 1: Create compelling preview
            if optimize_preview:
                preview = self._create_facebook_preview(script, use_emojis)
            else:
                preview = ""

            # Step 2: Format main content
            main_content = self._format_facebook_content(script, preview)

            # Step 3: Build post sections
            sections = []

            if preview:
                sections.append(preview)
                sections.append("")  # Blank line

            sections.append(main_content)

            # Step 4: Add engagement question
            if add_engagement_question:
                question = self._generate_engagement_question(script)
                sections.append("")
                sections.append(question)

            # Step 5: Combine sections
            full_post = "\n".join(sections)

            # Step 6: Validate practical length
            if len(full_post) > self.PRACTICAL_LIMIT:
                full_post = self._truncate_to_limit(full_post, self.PRACTICAL_LIMIT, "...")

            result.formatted_content = full_post

            # Step 7: Generate metadata
            result.metadata = self._generate_facebook_metadata(full_post)

        except Exception as e:
            result.errors.append(f"Facebook formatting error: {str(e)}")
            result.success = False

        return result

    def _create_facebook_preview(self, script: str, use_emojis: bool) -> str:
        """Create compelling preview for first 400 characters.

        Args:
            script: Script content
            use_emojis: Whether to add emojis

        Returns:
            Preview text
        """
        # Get hook from script
        sentences = self._split_into_sentences(script)

        if not sentences:
            return "Here's something interesting..."

        # Use first 1-2 sentences for preview
        preview = sentences[0]
        if len(preview) < 200 and len(sentences) > 1:
            preview += " " + sentences[1]

        # Ensure it fits in preview limit
        if len(preview) > self.PREVIEW_LIMIT - 10:
            preview = self._truncate_to_limit(preview, self.PREVIEW_LIMIT - 10, "...")

        # Add emoji if requested
        if use_emojis:
            preview = self._add_facebook_emoji(preview)

        return preview

    def _format_facebook_content(self, script: str, preview: str) -> str:
        """Format main content for Facebook.

        Args:
            script: Script content
            preview: Preview text (to avoid duplication)

        Returns:
            Formatted content
        """
        # Split into sentences
        sentences = self._split_into_sentences(script)

        # Remove preview sentences if present
        if preview:
            preview_clean = preview.replace("...", "").strip()
            sentences = [s for s in sentences if not s.startswith(preview_clean[:50])]

        # Group into paragraphs (2-3 sentences each)
        paragraphs = []
        current_para = []

        for i, sentence in enumerate(sentences):
            current_para.append(sentence)

            # Create paragraph every 2-3 sentences
            if len(current_para) >= 2 or i == len(sentences) - 1:
                paragraphs.append(" ".join(current_para))
                current_para = []

        # Join with double newlines
        content = "\n\n".join(paragraphs)

        return content

    def _generate_engagement_question(self, script: str) -> str:
        """Generate engagement-driving question.

        Args:
            script: Script content

        Returns:
            Engagement question
        """
        # Look for topics in the script
        text_lower = script.lower()

        if any(word in text_lower for word in ["success", "achieve", "goal"]):
            return "What's been your biggest success story? Share below! 👇"
        elif any(word in text_lower for word in ["challenge", "problem", "difficult"]):
            return "Have you faced this challenge? How did you overcome it?"
        elif any(word in text_lower for word in ["learn", "discover", "insight"]):
            return "What's the most valuable lesson you've learned? Let us know!"
        else:
            return "What are your thoughts on this? Comment below!"

    def _add_facebook_emoji(self, text: str) -> str:
        """Add relevant emoji to text.

        Args:
            text: Text to enhance

        Returns:
            Text with emoji
        """
        # Add emoji at the end if not present
        common_emojis = ["💡", "🎯", "✨", "🚀", "💪", "🔥"]

        if not any(emoji in text for emoji in common_emojis):
            # Add contextually relevant emoji
            if any(word in text.lower() for word in ["idea", "think", "insight"]):
                return f"{text} 💡"
            elif any(word in text.lower() for word in ["goal", "target", "achieve"]):
                return f"{text} 🎯"
            elif any(word in text.lower() for word in ["grow", "improve", "success"]):
                return f"{text} 🚀"
            else:
                return f"{text} ✨"

        return text

    def _generate_facebook_metadata(self, post: str) -> SocialMediaMetadata:
        """Generate metadata for Facebook post.

        Args:
            post: Full post content

        Returns:
            SocialMediaMetadata
        """
        metadata = SocialMediaMetadata(
            platform="facebook",
            character_count=len(post),
            word_count=len(post.split()),
            estimated_engagement_score=self._estimate_facebook_engagement(post),
            suggested_posting_time="1:00 PM - 3:00 PM, 7:00 PM - 9:00 PM",
            hashtags=[],  # Facebook doesn't emphasize hashtags as much
            variant_count=1,
        )

        return metadata

    def _estimate_facebook_engagement(self, post: str) -> int:
        """Estimate engagement score for Facebook post.

        Args:
            post: Full post content

        Returns:
            Engagement score (0-100)
        """
        score = 50  # Base score

        # Bonus for optimal length (500-2000 chars)
        post_len = len(post)
        if 500 <= post_len <= 2000:
            score += 15
        elif post_len > 4000:
            score -= 10

        # Bonus for paragraph breaks
        if post.count("\n\n") >= 2:
            score += 10

        # Bonus for questions (drive engagement)
        if post.count("?") >= 1:
            score += 15

        # Bonus for emojis (but not too many)
        emoji_count = sum(1 for char in post if ord(char) > 127)
        if 1 <= emoji_count <= 5:
            score += 10
        elif emoji_count > 10:
            score -= 5

        return min(max(score, 0), 100)


def format_facebook_post(
    script: str,
    content_id: str,
    add_engagement_question: bool = True,
    use_emojis: bool = True,
    optimize_preview: bool = True,
) -> SocialMediaContent:
    """Convenience function to format script as Facebook post.

    Args:
        script: Script content to format
        content_id: Unique identifier for content
        add_engagement_question: Whether to add engagement question
        use_emojis: Whether to add relevant emojis
        optimize_preview: Whether to optimize for preview

    Returns:
        SocialMediaContent with Facebook post
    """
    formatter = FacebookFormatter()
    return formatter.format_facebook_post(
        script=script,
        content_id=content_id,
        add_engagement_question=add_engagement_question,
        use_emojis=use_emojis,
        optimize_preview=optimize_preview,
    )
