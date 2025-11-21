"""Tests for Reddit OAuth client."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add source to path
src_path = Path(__file__).resolve().parents[2] / 'src'
sys.path.insert(0, str(src_path))


def test_client_import():
    """Test that client module can be imported."""
    from client import RedditOAuthClient
    assert RedditOAuthClient is not None
    print("✓ Client module imports successfully")


def test_client_initialization():
    """Test client initialization with valid credentials."""
    from client import RedditOAuthClient
    
    client = RedditOAuthClient(
        client_id="test_client_id",
        client_secret="test_client_secret",
        user_agent="test/1.0"
    )
    
    assert client.client_id == "test_client_id"
    assert client.client_secret == "test_client_secret"
    assert client.user_agent == "test/1.0"
    assert client.username is None
    assert client.password is None
    print("✓ Client initialization works correctly")


def test_client_requires_credentials():
    """Test that client requires credentials."""
    from client import RedditOAuthClient
    
    try:
        client = RedditOAuthClient(
            client_id="",
            client_secret="secret",
            user_agent="test/1.0"
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "client_id" in str(e).lower()
        print("✓ Client validates credentials correctly")


def test_client_with_user_auth():
    """Test client initialization with user authentication."""
    from client import RedditOAuthClient
    
    client = RedditOAuthClient(
        client_id="test_client_id",
        client_secret="test_client_secret",
        user_agent="test/1.0",
        username="test_user",
        password="test_pass"
    )
    
    assert client.username == "test_user"
    assert client.password == "test_pass"
    print("✓ Client supports user authentication")


def test_client_lazy_initialization():
    """Test that Reddit client is lazily initialized."""
    from client import RedditOAuthClient
    
    client = RedditOAuthClient(
        client_id="test_client_id",
        client_secret="test_client_secret",
        user_agent="test/1.0"
    )
    
    # Reddit client should not be initialized yet
    assert client._reddit is None
    print("✓ Client uses lazy initialization")


if __name__ == "__main__":
    print("\n=== Running Reddit OAuth Client Tests ===\n")
    
    test_client_import()
    test_client_initialization()
    test_client_requires_credentials()
    test_client_with_user_auth()
    test_client_lazy_initialization()
    
    print("\n=== All Tests Passed! ===\n")
