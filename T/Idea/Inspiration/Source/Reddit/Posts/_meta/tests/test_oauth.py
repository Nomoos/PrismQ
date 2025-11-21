"""Unit tests for Reddit OAuth client.

Tests the RedditOAuthClient class without requiring actual Reddit API credentials.
Uses mocking to simulate PRAW behavior.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add core directory to path directly to avoid importing __init__.py
_core_path = Path(__file__).resolve().parent.parent.parent / "src" / "core"
if str(_core_path) not in sys.path:
    sys.path.insert(0, str(_core_path))


class TestRedditOAuthClient(unittest.TestCase):
    """Test cases for RedditOAuthClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_client_id = "test_client_id"
        self.test_client_secret = "test_client_secret"
        self.test_user_agent = "TestAgent/1.0"
        self.test_username = "test_user"
        self.test_password = "test_password"
    
    @patch('oauth._praw_available', True)
    @patch('oauth.praw')
    def test_client_initialization_read_only(self, mock_praw):
        """Test client initialization in read-only mode."""
        from oauth import RedditOAuthClient
        
        client = RedditOAuthClient(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret,
            user_agent=self.test_user_agent
        )
        
        self.assertEqual(client.client_id, self.test_client_id)
        self.assertEqual(client.client_secret, self.test_client_secret)
        self.assertEqual(client.user_agent, self.test_user_agent)
        self.assertIsNone(client.username)
        self.assertIsNone(client.password)
    
    @patch('oauth._praw_available', True)
    @patch('oauth.praw')
    def test_client_initialization_with_user_auth(self, mock_praw):
        """Test client initialization with user authentication."""
        from oauth import RedditOAuthClient
        
        client = RedditOAuthClient(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret,
            user_agent=self.test_user_agent,
            username=self.test_username,
            password=self.test_password
        )
        
        self.assertEqual(client.username, self.test_username)
        self.assertEqual(client.password, self.test_password)
    
    @patch('oauth._praw_available', False)
    def test_client_initialization_without_praw(self):
        """Test client initialization fails gracefully without PRAW."""
        from oauth import RedditOAuthClient
        
        with self.assertRaises(ImportError) as context:
            RedditOAuthClient(
                client_id=self.test_client_id,
                client_secret=self.test_client_secret,
                user_agent=self.test_user_agent
            )
        
        self.assertIn("PRAW", str(context.exception))
    
    @patch('oauth._praw_available', True)
    @patch('oauth.praw')
    def test_reddit_property_lazy_initialization(self, mock_praw):
        """Test that reddit property does lazy initialization."""
        from oauth import RedditOAuthClient
        
        # Mock Reddit instance
        mock_reddit = MagicMock()
        mock_reddit.user.me.return_value = None
        mock_praw.Reddit.return_value = mock_reddit
        
        client = RedditOAuthClient(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret,
            user_agent=self.test_user_agent
        )
        
        # Reddit instance should not be created yet
        self.assertIsNone(client._reddit)
        
        # Access reddit property
        reddit = client.reddit
        
        # Reddit instance should now be created
        self.assertIsNotNone(client._reddit)
        self.assertEqual(reddit, mock_reddit)
    
    @patch('oauth._praw_available', True)
    @patch('oauth.praw')
    def test_test_connection_success(self, mock_praw):
        """Test successful connection test."""
        from oauth import RedditOAuthClient
        
        # Mock Reddit instance
        mock_subreddit = MagicMock()
        mock_subreddit.display_name = "python"
        mock_reddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit
        mock_reddit.user.me.return_value = None
        mock_praw.Reddit.return_value = mock_reddit
        
        client = RedditOAuthClient(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret,
            user_agent=self.test_user_agent
        )
        
        # Test connection
        result = client.test_connection()
        
        self.assertTrue(result)
        mock_reddit.subreddit.assert_called_with("python")
    
    @patch('oauth._praw_available', True)
    @patch('oauth.praw')
    def test_test_connection_failure(self, mock_praw):
        """Test failed connection test."""
        from oauth import RedditOAuthClient
        
        # Mock Reddit instance that raises an error
        mock_reddit = MagicMock()
        mock_reddit.subreddit.side_effect = Exception("Connection failed")
        mock_reddit.user.me.return_value = None
        mock_praw.Reddit.return_value = mock_reddit
        
        client = RedditOAuthClient(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret,
            user_agent=self.test_user_agent
        )
        
        # Test connection
        result = client.test_connection()
        
        self.assertFalse(result)
    
    @patch('oauth._praw_available', True)
    @patch('oauth.praw')
    def test_get_subreddit_success(self, mock_praw):
        """Test successful subreddit retrieval."""
        from oauth import RedditOAuthClient
        
        # Mock Reddit instance
        mock_subreddit = MagicMock()
        mock_reddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit
        mock_reddit.user.me.return_value = None
        mock_praw.Reddit.return_value = mock_reddit
        
        client = RedditOAuthClient(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret,
            user_agent=self.test_user_agent
        )
        
        # Get subreddit
        result = client.get_subreddit("python")
        
        self.assertEqual(result, mock_subreddit)
        mock_reddit.subreddit.assert_called_with("python")
    
    @patch('oauth._praw_available', True)
    @patch('oauth.praw')
    def test_get_subreddit_failure(self, mock_praw):
        """Test subreddit retrieval failure."""
        from oauth import RedditOAuthClient
        
        # Mock Reddit instance that raises an error
        mock_reddit = MagicMock()
        mock_reddit.subreddit.side_effect = Exception("Subreddit not found")
        mock_reddit.user.me.return_value = None
        mock_praw.Reddit.return_value = mock_reddit
        
        client = RedditOAuthClient(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret,
            user_agent=self.test_user_agent
        )
        
        # Get subreddit
        result = client.get_subreddit("nonexistent")
        
        self.assertIsNone(result)
    
    @patch('oauth._praw_available', True)
    @patch('oauth.praw')
    def test_close(self, mock_praw):
        """Test client close method."""
        from oauth import RedditOAuthClient
        
        # Mock Reddit instance
        mock_reddit = MagicMock()
        mock_reddit.user.me.return_value = None
        mock_praw.Reddit.return_value = mock_reddit
        
        client = RedditOAuthClient(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret,
            user_agent=self.test_user_agent
        )
        
        # Access reddit to initialize
        _ = client.reddit
        self.assertIsNotNone(client._reddit)
        
        # Close client
        client.close()
        self.assertIsNone(client._reddit)
    
    @patch('oauth._praw_available', True)
    @patch('oauth.praw')
    @patch.dict('os.environ', {
        'REDDIT_CLIENT_ID': 'test_id',
        'REDDIT_CLIENT_SECRET': 'test_secret',
        'REDDIT_USER_AGENT': 'TestAgent/1.0'
    })
    def test_create_client_from_env(self, mock_praw):
        """Test creating client from environment variables."""
        from oauth import create_reddit_client_from_env
        
        # Mock Reddit instance
        mock_reddit = MagicMock()
        mock_reddit.user.me.return_value = None
        mock_praw.Reddit.return_value = mock_reddit
        
        client = create_reddit_client_from_env()
        
        self.assertIsNotNone(client)
        self.assertEqual(client.client_id, 'test_id')
        self.assertEqual(client.client_secret, 'test_secret')
        self.assertEqual(client.user_agent, 'TestAgent/1.0')
    
    @patch('oauth._praw_available', True)
    @patch.dict('os.environ', {}, clear=True)
    def test_create_client_from_env_missing_vars(self):
        """Test creating client from env fails with missing variables."""
        from oauth import create_reddit_client_from_env
        
        client = create_reddit_client_from_env()
        
        self.assertIsNone(client)


def run_tests():
    """Run all tests."""
    print("=" * 70)
    print("Reddit OAuth Client Tests")
    print("=" * 70)
    print()
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRedditOAuthClient)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    if result.wasSuccessful():
        print("✅ All OAuth tests passed!")
    else:
        print("❌ Some OAuth tests failed")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
