"""LinkedIn post formatter for PrismQ.T.Content.Formatter.Social.

This module transforms scripts into LinkedIn post format with professional
structure, hook optimization, and hashtag management.
"""

from typing import List, Optional

from .base_formatter import BaseSocialFormatter, SocialMediaContent, SocialMediaMetadata


class LinkedInFormatter(BaseSocialFormatter):
    """Format scripts into LinkedIn posts.

    Creates professional LinkedIn posts with:
    - 3,000 character limit (first 140 visible in feed)
    - Strong hook (first 140 characters)
    - Professional structure with sections
    - Bullet points with proper formatting
    - 3-5 relevant hashtags
    """

    # LinkedIn character limits
    CHAR_LIMIT = 3000
    PREVIEW_LIMIT = 140  # Characters visible before "see more"

    def __init__(self):
        """Initialize LinkedIn formatter."""
        super().__init__()

    def format_linkedin_post(
        self,
        script: str,
        content_id: str,
        hook_type: str = "statement",
        add_hashtags: bool = True,
        num_hashtags: int = 5,
        add_cta: bool = True,
        cta_text: Optional[str] = None,
    ) -> SocialMediaContent:
        """Format script into LinkedIn post.

        Args:
            script: Content content to format
            content_id: Unique identifier for content
            hook_type: Type of hook (question, statement, stat)
            add_hashtags: Whether to add hashtags
            num_hashtags: Number of hashtags to include (3-5)
            add_cta: Whether to add CTA
            cta_text: Custom CTA text

        Returns:
            SocialMediaContent with LinkedIn post
        """
        result = SocialMediaContent(
            content_id=content_id,
            platform="linkedin",
            formatted_content="",
            metadata=SocialMediaMetadata(platform="linkedin"),
        )

        try:
            # Step 1: Generate strong hook (optimized for first 140 chars)
            hook = self._generate_linkedin_hook(script, hook_type)

            # Step 2: Extract and structure main content
            main_content = self._structure_linkedin_content(script)

            # Step 3: Extract key takeaways
            takeaways = self._extract_key_points(script, max_points=3)

            # Step 4: Build post sections
            sections = []
            sections.append(hook)
            sections.append("")  # Blank line
            sections.append(main_content)
            sections.append("")  # Blank line

            # Add key takeaways section if we have points
            if takeaways:
                sections.append(self._format_takeaways(takeaways))
                sections.append("")  # Blank line

            # Step 5: Add CTA if requested
            if add_cta:
                cta = cta_text or self._generate_linkedin_cta()
                sections.append(cta)
                sections.append("")  # Blank line

            # Step 6: Add hashtags
            hashtags = []
            if add_hashtags:
                hashtags = self._extract_hashtags(script, 3, num_hashtags)
                hashtag_line = " ".join(f"#{tag}" for tag in hashtags)
                sections.append(hashtag_line)

            # Step 7: Combine all sections
            full_post = "\n".join(sections)

            # Step 8: Validate character limit
            if len(full_post) > self.CHAR_LIMIT:
                full_post = self._truncate_to_limit(
                    full_post, self.CHAR_LIMIT - 50  # Leave room for hashtags
                )
                if add_hashtags:
                    hashtag_line = " ".join(f"#{tag}" for tag in hashtags)
                    full_post = full_post + "\n\n" + hashtag_line

            result.formatted_content = full_post

            # Step 9: Generate metadata
            result.metadata = self._generate_linkedin_metadata(full_post, hook, hashtags)

        except Exception as e:
            result.errors.append(f"LinkedIn formatting error: {str(e)}")
            result.success = False

        return result

    def _generate_linkedin_hook(self, script: str, hook_type: str) -> str:
        """Generate LinkedIn-optimized hook.

        LinkedIn hook must be compelling in first 140 characters.

        Args:
            script: Content content
            hook_type: Type of hook

        Returns:
            Hook text optimized for LinkedIn preview
        """
        base_hook = self._generate_hook(script, hook_type)

        # Ensure hook is strong and fits in preview
        if len(base_hook) > self.PREVIEW_LIMIT:
            base_hook = self._truncate_to_limit(base_hook, self.PREVIEW_LIMIT - 3, "...")

        # Make it more LinkedIn-professional
        if hook_type == "question":
            return base_hook
        elif hook_type == "stat":
            # Stats work great on LinkedIn
            return base_hook
        else:
            # Statement - make it bold/professional
            if not base_hook.endswith(("!", "?", ".")):
                base_hook += "."
            return base_hook

    def _structure_linkedin_content(self, script: str) -> str:
        """Structure main content for LinkedIn.

        Args:
            script: Content content

        Returns:
            Structured content with paragraphs
        """
        # Extract main message (first portion of script)
        sentences = self._split_into_sentences(script)

        # LinkedIn works well with short paragraphs (2-3 sentences each)
        paragraphs = []
        current_para = []

        for i, sentence in enumerate(sentences):
            current_para.append(sentence)

            # Create paragraph every 2-3 sentences
            if len(current_para) >= 2 or i == len(sentences) - 1:
                paragraphs.append(" ".join(current_para))
                current_para = []

        # Join with double newlines for readability
        content = "\n\n".join(paragraphs[:4])  # Limit to 4 paragraphs for readability

        return content

    def _format_takeaways(self, takeaways: List[str]) -> str:
        """Format key takeaways with bullets.

        Args:
            takeaways: List of key points

        Returns:
            Formatted takeaways section
        """
        lines = ["Key Takeaways:"]

        for takeaway in takeaways:
            # Use arrow for LinkedIn (looks professional)
            # Truncate if too long
            if len(takeaway) > 100:
                takeaway = takeaway[:97] + "..."
            lines.append(f"→ {takeaway}")

        return "\n".join(lines)

    def _generate_linkedin_cta(self) -> str:
        """Generate LinkedIn-appropriate CTA.

        Returns:
            CTA text
        """
        ctas = [
            "What's your experience with this? Share in the comments.",
            "I'd love to hear your thoughts on this.",
            "Have you faced this challenge? Let's discuss.",
            "What strategies have worked for you?",
        ]
        return ctas[0]

    def _generate_linkedin_metadata(
        self, post: str, hook: str, hashtags: List[str]
    ) -> SocialMediaMetadata:
        """Generate metadata for LinkedIn post.

        Args:
            post: Full post content
            hook: Hook text
            hashtags: List of hashtags

        Returns:
            SocialMediaMetadata
        """
        metadata = SocialMediaMetadata(
            platform="linkedin",
            character_count=len(post),
            word_count=len(post.split()),
            estimated_engagement_score=self._estimate_linkedin_engagement(post, hook),
            suggested_posting_time="8:00 AM - 10:00 AM, 12:00 PM - 2:00 PM",
            hashtags=hashtags,
            variant_count=1,
        )

        return metadata

    def _estimate_linkedin_engagement(self, post: str, hook: str) -> int:
        """Estimate engagement score for LinkedIn post.

        Args:
            post: Full post content
            hook: Hook text

        Returns:
            Engagement score (0-100)
        """
        score = 50  # Base score

        # Bonus for optimal length (500-1500 chars)
        post_len = len(post)
        if 500 <= post_len <= 1500:
            score += 15
        elif post_len > 2500:
            score -= 10

        # Bonus for strong hook (<140 chars)
        if len(hook) <= self.PREVIEW_LIMIT:
            score += 10

        # Bonus for using bullets/arrows
        if "→" in post or "•" in post:
            score += 10

        # Bonus for hashtags
        if "#" in post:
            score += 5

        # Bonus for CTA/question
        if post.count("?") >= 1:
            score += 10

        return min(max(score, 0), 100)


def format_linkedin_post(
    script: str,
    content_id: str,
    hook_type: str = "statement",
    add_hashtags: bool = True,
    num_hashtags: int = 5,
    add_cta: bool = True,
    cta_text: Optional[str] = None,
) -> SocialMediaContent:
    """Convenience function to format script as LinkedIn post.

    Args:
        script: Content content to format
        content_id: Unique identifier for content
        hook_type: Type of hook (question, statement, stat)
        add_hashtags: Whether to add hashtags
        num_hashtags: Number of hashtags (3-5)
        add_cta: Whether to add CTA
        cta_text: Custom CTA text

    Returns:
        SocialMediaContent with LinkedIn post
    """
    formatter = LinkedInFormatter()
    return formatter.format_linkedin_post(
        script=script,
        content_id=content_id,
        hook_type=hook_type,
        add_hashtags=add_hashtags,
        num_hashtags=num_hashtags,
        add_cta=add_cta,
        cta_text=cta_text,
    )
