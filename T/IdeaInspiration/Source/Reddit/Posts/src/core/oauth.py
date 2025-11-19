"""Reddit OAuth authentication handler.

This module provides OAuth authentication for Reddit API access using PRAW
(Python Reddit API Wrapper). It supports both application-only (read-only)
and user authentication (read/write) modes.

Security considerations:
- Never commit credentials to source control
- Use environment variables for sensitive data
- Rotate API keys regularly
- Use read-only mode when write access is not needed

Follows SOLID principles:
- SRP: Only handles Reddit authentication
- DIP: Uses PRAW abstraction for Reddit API
- OCP: Extensible for additional authentication methods
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Try to import PRAW
try:
    import praw
    _praw_available = True
except ImportError:
    _praw_available = False
    logger.warning("PRAW not available - Reddit OAuth will not work")


class RedditOAuthClient:
    """Reddit OAuth authentication client.
    
    Provides authenticated Reddit API access via PRAW. Supports both
    application-only (read-only) and user authentication (read/write) modes.
    
    Attributes:
        client_id: Reddit API client ID
        client_secret: Reddit API client secret
        user_agent: User agent string for API requests
        username: Optional Reddit username for user auth
        password: Optional Reddit password for user auth
        
    Example (read-only):
        >>> client = RedditOAuthClient(
        ...     client_id="your_client_id",
        ...     client_secret="your_secret",
        ...     user_agent="PrismQ-IdeaInspiration/1.0"
        ... )
        >>> if client.test_connection():
        ...     reddit = client.reddit
        
    Example (read/write):
        >>> client = RedditOAuthClient(
        ...     client_id="your_client_id",
        ...     client_secret="your_secret",
        ...     user_agent="PrismQ-IdeaInspiration/1.0",
        ...     username="your_username",
        ...     password="your_password"
        ... )
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """Initialize Reddit OAuth client.
        
        Args:
            client_id: Reddit API client ID (from https://www.reddit.com/prefs/apps)
            client_secret: Reddit API client secret
            user_agent: User agent string (should include app name and version)
            username: Optional Reddit username for user authentication
            password: Optional Reddit password for user authentication
            
        Raises:
            ImportError: If PRAW is not installed
        """
        if not _praw_available:
            raise ImportError(
                "PRAW (Python Reddit API Wrapper) is required for Reddit OAuth. "
                "Install it with: pip install praw"
            )
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.username = username
        self.password = password
        
        self._reddit: Optional['praw.Reddit'] = None
        
        logger.info(
            f"Reddit OAuth client initialized "
            f"(mode: {'user' if username else 'read-only'})"
        )
    
    @property
    def reddit(self) -> 'praw.Reddit':
        """Get authenticated Reddit client (lazy initialization).
        
        Returns:
            Authenticated PRAW Reddit instance
            
        Raises:
            Exception: If authentication fails
        """
        if self._reddit is None:
            self._reddit = self._create_client()
        return self._reddit
    
    def _create_client(self) -> 'praw.Reddit':
        """Create authenticated Reddit client.
        
        Returns:
            Authenticated PRAW Reddit instance
            
        Raises:
            Exception: If authentication fails
        """
        try:
            if self.username and self.password:
                # User authentication (read/write)
                reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent,
                    username=self.username,
                    password=self.password
                )
                logger.info("Reddit client authenticated with user credentials (read/write)")
            else:
                # Application-only authentication (read-only)
                reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
                logger.info("Reddit client authenticated with app credentials (read-only)")
            
            # Verify authentication by accessing user info
            # This will raise an exception if auth fails
            try:
                _ = reddit.user.me()
            except Exception:
                # For read-only mode, this is expected
                if self.username and self.password:
                    # But for user auth, this is an error
                    raise
            
            return reddit
            
        except Exception as e:
            logger.error(f"Reddit authentication failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test Reddit API connection.
        
        Attempts to fetch a simple subreddit to verify the connection works.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to fetch a simple subreddit
            subreddit = self.reddit.subreddit("python")
            _ = subreddit.display_name
            logger.info("Reddit API connection test successful")
            return True
        except Exception as e:
            logger.error(f"Reddit API connection test failed: {e}")
            return False
    
    def get_subreddit(self, subreddit_name: str) -> Optional['praw.models.Subreddit']:
        """Get a subreddit by name.
        
        Args:
            subreddit_name: Name of subreddit (without r/ prefix)
            
        Returns:
            PRAW Subreddit object or None if not found
        """
        try:
            return self.reddit.subreddit(subreddit_name)
        except Exception as e:
            logger.error(f"Failed to get subreddit '{subreddit_name}': {e}")
            return None
    
    def close(self):
        """Close the Reddit client connection.
        
        Should be called when done using the client to clean up resources.
        """
        if self._reddit is not None:
            # PRAW doesn't have an explicit close method
            # Just clear the reference
            self._reddit = None
            logger.info("Reddit OAuth client closed")


def create_reddit_client_from_env() -> Optional[RedditOAuthClient]:
    """Create Reddit OAuth client from environment variables.
    
    Expected environment variables:
    - REDDIT_CLIENT_ID: Reddit API client ID
    - REDDIT_CLIENT_SECRET: Reddit API client secret
    - REDDIT_USER_AGENT: User agent string
    - REDDIT_USERNAME: (Optional) Reddit username
    - REDDIT_PASSWORD: (Optional) Reddit password
    
    Returns:
        RedditOAuthClient instance or None if required env vars missing
        
    Example:
        >>> client = create_reddit_client_from_env()
        >>> if client and client.test_connection():
        ...     reddit = client.reddit
    """
    import os
    
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT', 'PrismQ-IdeaInspiration/1.0')
    username = os.getenv('REDDIT_USERNAME')
    password = os.getenv('REDDIT_PASSWORD')
    
    if not client_id or not client_secret:
        logger.error(
            "Missing required environment variables: "
            "REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET"
        )
        return None
    
    try:
        return RedditOAuthClient(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            username=username,
            password=password
        )
    except Exception as e:
        logger.error(f"Failed to create Reddit OAuth client: {e}")
        return None
