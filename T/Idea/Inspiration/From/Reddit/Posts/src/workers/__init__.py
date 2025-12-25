"""Worker system for Reddit scraping using TaskManager API.

This package provides the worker infrastructure for processing tasks from
the external TaskManager API. No local queue is used.

Architecture:
    Worker → TaskManagerClient → External TaskManager API
           ↓
    IdeaInspiration Database (results only)
"""

# Import main components
from .base_worker import BaseWorker


# Lazy import of RedditSubredditWorker to avoid import errors when
# IdeaInspiration model is not available (e.g., during testing)
def __getattr__(name):
    """Lazy import for RedditSubredditWorker."""
    if name == "RedditSubredditWorker":
        from .reddit_subreddit_worker import RedditSubredditWorker

        return RedditSubredditWorker
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "BaseWorker",
    "RedditSubredditWorker",
]
