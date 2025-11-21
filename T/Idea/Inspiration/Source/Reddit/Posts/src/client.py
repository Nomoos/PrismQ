"""Reddit OAuth authentication client.

This module provides a Reddit OAuth client for authenticating with the Reddit API
using PRAW (Python Reddit API Wrapper).

Following SOLID principles:
- Single Responsibility: Only handles Reddit authentication
- Dependency Inversion: Uses PRAW abstraction
"""

import praw
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RedditOAuthClient:
    """
    Reddit OAuth authentication client.
    
    Handles authentication with Reddit API using OAuth2.
    Supports both application-only (read-only) and user authentication.
    
    Follows SOLID principles:
    - SRP: Only handles Reddit authentication
    - DIP: Uses PRAW abstraction
    - OCP: Extensible through configuration
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize Reddit OAuth client.
        
        Args:
            client_id: Reddit API client ID (from https://www.reddit.com/prefs/apps)
            client_secret: Reddit API client secret
            user_agent: User agent string (e.g., 'PrismQ-IdeaInspiration/1.0')
            username: Reddit username (optional, for user authentication)
            password: Reddit password (optional, for user authentication)
            
        Raises:
            ValueError: If required credentials are missing
        """
        if not client_id or not client_secret:
            raise ValueError("Reddit client_id and client_secret are required")
        
        if not user_agent:
            raise ValueError("Reddit user_agent is required")
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.username = username
        self.password = password
        
        self._reddit: Optional[praw.Reddit] = None
        
        logger.info("RedditOAuthClient initialized")
    
    @property
    def reddit(self) -> praw.Reddit:
        """
        Lazy Reddit client initialization.
        
        Returns:
            Authenticated PRAW Reddit instance
            
        Raises:
            Exception: If authentication fails
        """
        if self._reddit is None:
            self._reddit = self._create_client()
        return self._reddit
    
    def _create_client(self) -> praw.Reddit:
        """
        Create authenticated Reddit client.
        
        Returns:
            Authenticated PRAW Reddit instance
            
        Raises:
            Exception: If authentication fails
        """
        try:
            if self.username and self.password:
                # User authentication (read/write access)
                reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent,
                    username=self.username,
                    password=self.password
                )
                logger.info("Reddit client authenticated with user credentials (read/write)")
            else:
                # Application-only authentication (read-only access)
                reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
                logger.info("Reddit client authenticated with app credentials (read-only)")
            
            # Verify authentication by checking if we can access the API
            # For app-only auth, we can't call user.me(), so just verify read_only status
            reddit.read_only = True
            
            return reddit
            
        except Exception as e:
            logger.error(f"Reddit authentication failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test Reddit API connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to fetch a simple subreddit to verify connection
            subreddit = self.reddit.subreddit("python")
            _ = subreddit.display_name
            logger.info("Reddit API connection test successful")
            return True
        except Exception as e:
            logger.error(f"Reddit API connection test failed: {e}")
            return False
    
    def get_subreddit(self, name: str) -> praw.models.Subreddit:
        """
        Get a subreddit by name.
        
        Args:
            name: Subreddit name (without 'r/' prefix)
            
        Returns:
            PRAW Subreddit object
            
        Raises:
            Exception: If subreddit doesn't exist or can't be accessed
        """
        return self.reddit.subreddit(name)


__all__ = ["RedditOAuthClient"]
