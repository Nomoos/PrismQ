"""Mapper for transforming Reddit posts to IdeaInspiration model."""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add Model to path
_model_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "Model"
if str(_model_path) not in sys.path:
    sys.path.insert(0, str(_model_path))

from src.idea_inspiration import ContentType, IdeaInspiration


class RedditMapper:
    """
    Maps Reddit post data to IdeaInspiration model.

    Follows SOLID principles:
    - SRP: Only handles Reddit-to-IdeaInspiration transformation
    - OCP: Can be extended for different Reddit content types
    """

    @staticmethod
    def map_post_to_idea(post_data: Dict[str, Any]) -> IdeaInspiration:
        """
        Transform Reddit post data to IdeaInspiration.

        Args:
            post_data: Dictionary containing Reddit post data with keys:
                - id: Reddit post ID
                - title: Post title
                - selftext: Post body text (for text posts)
                - url: Post URL
                - subreddit: Subreddit name
                - author: Author username
                - created_utc: Unix timestamp
                - score: Post score (upvotes - downvotes)
                - upvote_ratio: Ratio of upvotes
                - num_comments: Number of comments
                - link_flair_text: Post flair
                - is_self: Boolean indicating text post
                - permalink: Reddit permalink

        Returns:
            IdeaInspiration object
        """
        # Extract basic fields
        title = post_data.get("title", "")
        selftext = post_data.get("selftext", "")
        url = post_data.get("url", "")

        # Description: first 200 chars of text or URL
        description = selftext[:200] if selftext else f"Link post: {url}"

        # Content: full text or URL
        content = selftext if selftext else url

        # Keywords from subreddit and flair
        keywords = []
        if post_data.get("subreddit"):
            keywords.append(post_data["subreddit"])
        if post_data.get("link_flair_text"):
            keywords.append(post_data["link_flair_text"])

        # Metadata: Store Reddit-specific fields as strings
        metadata = {
            "subreddit": str(post_data.get("subreddit", "")),
            "flair": str(post_data.get("link_flair_text", "")),
            "is_self": str(post_data.get("is_self", False)),
            "upvote_ratio": str(post_data.get("upvote_ratio", 0)),
            "num_comments": str(post_data.get("num_comments", 0)),
            "permalink": str(post_data.get("permalink", "")),
        }

        # Source information
        source_id = post_data.get("id", "")
        source_url = f"https://reddit.com{post_data.get('permalink', '')}"
        source_created_by = post_data.get("author", "unknown")

        # Convert Unix timestamp to ISO 8601
        created_utc = post_data.get("created_utc")
        source_created_at = None
        if created_utc:
            source_created_at = datetime.fromtimestamp(created_utc).isoformat()

        # Score
        score = post_data.get("score", 0)

        return IdeaInspiration(
            title=title,
            description=description,
            content=content,
            keywords=keywords,
            source_type=ContentType.TEXT,
            metadata=metadata,
            source_id=source_id,
            source_url=source_url,
            source_platform="reddit",
            source_created_by=source_created_by,
            source_created_at=source_created_at,
            score=score,
        )
