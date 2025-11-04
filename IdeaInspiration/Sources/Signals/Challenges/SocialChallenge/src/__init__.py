"""Main module exports for SocialChallengeSource."""

from .core import Config
from .plugins.social_challenge_plugin import SocialChallengePlugin

__all__ = [
    "Config",
    "SocialChallengePlugin",
]

__version__ = "1.0.0"
