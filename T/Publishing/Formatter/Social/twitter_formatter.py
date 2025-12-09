"""Twitter/X thread formatter for PrismQ.T.Script.Formatter.Social.

This module transforms scripts into Twitter/X thread format with optimal
tweet breaks, thread numbering, and engagement optimization.
"""

from typing import List, Optional, Tuple

from .base_formatter import BaseSocialFormatter, SocialMediaContent, SocialMediaMetadata


class TwitterFormatter(BaseSocialFormatter):
    """Format scripts into Twitter/X threads.

    Creates optimized tweet threads with:
    - 280 character limit per tweet
    - Natural sentence breaks
    - Thread numbering (1/n, 2/n, etc.)
    - Hook in first tweet
    - CTA in final tweet
    """

    # Twitter character limit
    CHAR_LIMIT = 280

    # Reserve characters for thread numbering (e.g., "10/25 ")
    THREAD_NUMBER_CHARS = 6

    def __init__(self):
        """Initialize Twitter formatter."""
        super().__init__()

    def format_twitter_thread(
        self,
        script: str,
        content_id: str,
        hook_type: str = "statement",
        add_cta: bool = True,
        cta_text: Optional[str] = None,
        add_emojis: bool = False,
    ) -> SocialMediaContent:
        """Format script into Twitter thread.

        Args:
            script: Script content to format
            content_id: Unique identifier for content
            hook_type: Type of hook (question, statement, stat)
            add_cta: Whether to add CTA in final tweet
            cta_text: Custom CTA text (default: engagement question)
            add_emojis: Whether to add relevant emojis

        Returns:
            SocialMediaContent with Twitter thread
        """
        result = SocialMediaContent(
            content_id=content_id,
            platform="twitter",
            formatted_content="",
            metadata=SocialMediaMetadata(platform="twitter"),
        )

        try:
            # Step 1: Generate hook for first tweet
            hook = self._generate_hook(script, hook_type)
            if add_emojis:
                hook = self._add_emoji_to_hook(hook, hook_type)

            # Step 2: Extract key points and main content
            key_points = self._extract_key_points(script, max_points=3)

            # Step 3: Break content into tweet-sized chunks
            tweets = self._create_tweet_chunks(script, hook, key_points)

            # Step 4: Add CTA if requested
            if add_cta:
                cta = cta_text or self._generate_engagement_cta()
                tweets.append(cta)

            # Step 5: Add thread numbering
            numbered_tweets = self._add_thread_numbers(tweets)

            # Step 6: Validate all tweets meet character limit
            valid, error = self._validate_tweets(numbered_tweets)
            if not valid:
                result.errors.append(error)
                result.success = False
                return result

            # Step 7: Format as thread string
            result.formatted_content = self._format_thread_output(numbered_tweets)

            # Step 8: Generate metadata
            result.metadata = self._generate_twitter_metadata(numbered_tweets, script)

        except Exception as e:
            result.errors.append(f"Twitter formatting error: {str(e)}")
            result.success = False

        return result

    def _create_tweet_chunks(self, script: str, hook: str, key_points: List[str]) -> List[str]:
        """Break script into tweet-sized chunks.

        Args:
            script: Full script content
            hook: Hook for first tweet
            key_points: Key points to highlight

        Returns:
            List of tweet strings (without numbering)
        """
        tweets = []

        # First tweet is the hook
        tweets.append(hook)

        # Split remaining content into sentences
        sentences = self._split_into_sentences(script)

        # Remove hook sentence from sentences if present
        hook_text = hook.replace("🚀", "").replace("💡", "").replace("🎯", "").strip()
        sentences = [s for s in sentences if not s.startswith(hook_text[:30])]

        # Build tweets from sentences
        current_tweet = ""
        effective_limit = self.CHAR_LIMIT - self.THREAD_NUMBER_CHARS - 10  # Buffer

        for sentence in sentences:
            # Check if adding this sentence would exceed limit
            test_tweet = current_tweet + " " + sentence if current_tweet else sentence

            if len(test_tweet) <= effective_limit:
                current_tweet = test_tweet
            else:
                # Save current tweet if it has content
                if current_tweet:
                    tweets.append(current_tweet.strip())

                # Start new tweet with current sentence
                if len(sentence) <= effective_limit:
                    current_tweet = sentence
                else:
                    # Sentence itself is too long, need to split it
                    split_tweets = self._split_long_sentence(sentence, effective_limit)
                    tweets.extend(split_tweets[:-1])
                    current_tweet = split_tweets[-1] if split_tweets else ""

        # Add remaining content
        if current_tweet:
            tweets.append(current_tweet.strip())

        # Add key points as separate tweets if not already covered
        for point in key_points[:2]:  # Limit to 2 key points
            # Check if point is substantially different from existing tweets
            if not any(point[:50] in tweet for tweet in tweets):
                formatted_point = f"→ {point}"
                if len(formatted_point) <= effective_limit:
                    tweets.insert(len(tweets) - 1 if len(tweets) > 1 else 0, formatted_point)

        return tweets

    def _split_long_sentence(self, sentence: str, limit: int) -> List[str]:
        """Split a sentence that's too long for a single tweet.

        Args:
            sentence: Long sentence to split
            limit: Character limit

        Returns:
            List of split parts
        """
        parts = []
        words = sentence.split()
        current = ""

        for word in words:
            test = current + " " + word if current else word
            if len(test) <= limit:
                current = test
            else:
                if current:
                    parts.append(current)
                current = word

        if current:
            parts.append(current)

        return parts

    def _add_thread_numbers(self, tweets: List[str]) -> List[str]:
        """Add thread numbering to tweets.

        Args:
            tweets: List of tweet strings

        Returns:
            List of tweets with thread numbers
        """
        total = len(tweets)
        numbered = []

        for i, tweet in enumerate(tweets, 1):
            numbered_tweet = f"{i}/{total} {tweet}"
            numbered.append(numbered_tweet)

        return numbered

    def _validate_tweets(self, tweets: List[str]) -> Tuple[bool, Optional[str]]:
        """Validate all tweets meet character limit.

        Args:
            tweets: List of tweets with numbering

        Returns:
            Tuple of (is_valid, error_message)
        """
        for i, tweet in enumerate(tweets, 1):
            if len(tweet) > self.CHAR_LIMIT:
                return False, f"Tweet {i} exceeds {self.CHAR_LIMIT} chars: {len(tweet)} chars"

        return True, None

    def _format_thread_output(self, tweets: List[str]) -> str:
        """Format tweets as thread string.

        Args:
            tweets: List of numbered tweets

        Returns:
            Formatted thread string
        """
        # Join tweets with double newline for clarity
        return "\n\n".join(tweets)

    def _generate_engagement_cta(self) -> str:
        """Generate default engagement CTA.

        Returns:
            CTA text
        """
        ctas = [
            "What's your take on this? 💭",
            "Share your thoughts below! 👇",
            "Have you experienced this? Let me know!",
            "What's worked for you? Drop a comment! 💬",
        ]
        return ctas[0]  # Use first one as default

    def _add_emoji_to_hook(self, hook: str, hook_type: str) -> str:
        """Add relevant emoji to hook.

        Args:
            hook: Hook text
            hook_type: Type of hook

        Returns:
            Hook with emoji
        """
        emoji_map = {"question": "💭", "statement": "🚀", "stat": "📊"}

        emoji = emoji_map.get(hook_type, "💡")

        # Add emoji at the end if not already present
        if not any(e in hook for e in ["🚀", "💭", "📊", "💡", "🎯"]):
            return f"{hook} {emoji}"

        return hook

    def _generate_twitter_metadata(
        self, tweets: List[str], original_script: str
    ) -> SocialMediaMetadata:
        """Generate metadata for Twitter thread.

        Args:
            tweets: List of tweets
            original_script: Original script content

        Returns:
            SocialMediaMetadata
        """
        # Calculate total character count (excluding thread numbers)
        total_chars = sum(len(t) for t in tweets)

        # Word count from original script
        word_count = len(original_script.split())

        metadata = SocialMediaMetadata(
            platform="twitter",
            character_count=total_chars,
            word_count=word_count,
            estimated_engagement_score=self._estimate_engagement(tweets),
            suggested_posting_time="9:00 AM - 11:00 AM, 5:00 PM - 6:00 PM",
            hashtags=[],  # Twitter threads often don't use hashtags
            variant_count=1,
        )

        return metadata

    def _estimate_engagement(self, tweets: List[str]) -> int:
        """Estimate engagement score for thread.

        Args:
            tweets: List of tweets

        Returns:
            Engagement score (0-100)
        """
        score = 50  # Base score

        # Bonus for optimal thread length (3-10 tweets)
        if 3 <= len(tweets) <= 10:
            score += 15
        elif len(tweets) > 15:
            score -= 10

        # Bonus for hook with emoji
        if any(emoji in tweets[0] for emoji in ["🚀", "💭", "📊", "💡", "🎯"]):
            score += 10

        # Bonus for ending with question (engagement driver)
        if tweets[-1].endswith("?") or "?" in tweets[-1]:
            score += 10

        # Bonus for using arrows/bullets
        if any("→" in tweet or "•" in tweet for tweet in tweets):
            score += 5

        return min(max(score, 0), 100)  # Clamp to 0-100


def format_twitter_thread(
    script: str,
    content_id: str,
    hook_type: str = "statement",
    add_cta: bool = True,
    cta_text: Optional[str] = None,
    add_emojis: bool = False,
) -> SocialMediaContent:
    """Convenience function to format script as Twitter thread.

    Args:
        script: Script content to format
        content_id: Unique identifier for content
        hook_type: Type of hook (question, statement, stat)
        add_cta: Whether to add CTA in final tweet
        cta_text: Custom CTA text
        add_emojis: Whether to add relevant emojis

    Returns:
        SocialMediaContent with Twitter thread
    """
    formatter = TwitterFormatter()
    return formatter.format_twitter_thread(
        script=script,
        content_id=content_id,
        hook_type=hook_type,
        add_cta=add_cta,
        cta_text=cta_text,
        add_emojis=add_emojis,
    )
