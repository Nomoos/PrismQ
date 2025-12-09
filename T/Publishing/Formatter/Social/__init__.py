"""PrismQ.T.Script.Formatter.Social - Social Media Format Optimizer.

This module transforms scripts into social media-optimized formats for
various platforms including Twitter/X, LinkedIn, Instagram, and Facebook.

Public API:
    Twitter/X:
        - TwitterFormatter: Twitter thread formatter class
        - format_twitter_thread: Convenience function

    LinkedIn:
        - LinkedInFormatter: LinkedIn post formatter class
        - format_linkedin_post: Convenience function

    Instagram:
        - InstagramFormatter: Instagram caption formatter class
        - format_instagram_caption: Convenience function

    Facebook:
        - FacebookFormatter: Facebook post formatter class
        - format_facebook_post: Convenience function

    Base Classes:
        - BaseSocialFormatter: Base formatter with common utilities
        - SocialMediaContent: Result dataclass
        - SocialMediaMetadata: Metadata dataclass
"""

from .base_formatter import BaseSocialFormatter, SocialMediaContent, SocialMediaMetadata
from .facebook_formatter import FacebookFormatter, format_facebook_post
from .instagram_formatter import InstagramFormatter, format_instagram_caption
from .linkedin_formatter import LinkedInFormatter, format_linkedin_post
from .twitter_formatter import TwitterFormatter, format_twitter_thread

__all__ = [
    # Base classes
    "BaseSocialFormatter",
    "SocialMediaContent",
    "SocialMediaMetadata",
    # Twitter/X
    "TwitterFormatter",
    "format_twitter_thread",
    # LinkedIn
    "LinkedInFormatter",
    "format_linkedin_post",
    # Instagram
    "InstagramFormatter",
    "format_instagram_caption",
    # Facebook
    "FacebookFormatter",
    "format_facebook_post",
]

__version__ = "1.0.0"
__author__ = "Worker12 (Content Specialist)"
