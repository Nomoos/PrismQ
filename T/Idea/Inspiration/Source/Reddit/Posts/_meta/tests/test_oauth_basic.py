"""Simple unit tests for Reddit OAuth client.

Tests the RedditOAuthClient class without complex mocking.
"""

import unittest
import sys
from pathlib import Path

# Add core directory to path
_core_path = Path(__file__).resolve().parent.parent.parent / "src" / "core"
if str(_core_path) not in sys.path:
    sys.path.insert(0, str(_core_path))


class TestRedditOAuthBasic(unittest.TestCase):
    """Basic test cases for RedditOAuthClient."""
    
    def test_module_imports(self):
        """Test that oauth module can be imported."""
        try:
            import oauth
            self.assertTrue(hasattr(oauth, 'RedditOAuthClient'))
            self.assertTrue(hasattr(oauth, 'create_reddit_client_from_env'))
            print("✓ OAuth module imports successfully")
        except ImportError as e:
            self.fail(f"Failed to import oauth module: {e}")
    
    def test_class_exists(self):
        """Test that RedditOAuthClient class exists."""
        from oauth import RedditOAuthClient
        self.assertTrue(callable(RedditOAuthClient))
        print("✓ RedditOAuthClient class exists")
    
    def test_praw_not_available_handling(self):
        """Test that client handles missing PRAW gracefully."""
        from oauth import RedditOAuthClient, _praw_available
        
        if not _praw_available:
            # PRAW not installed, should raise ImportError
            with self.assertRaises(ImportError) as context:
                client = RedditOAuthClient(
                    client_id="test",
                    client_secret="test",
                    user_agent="test"
                )
            self.assertIn("PRAW", str(context.exception))
            print("✓ Handles missing PRAW correctly")
        else:
            print("⊙ PRAW is available, skipping missing PRAW test")
    
    def test_function_exists(self):
        """Test that create_reddit_client_from_env function exists."""
        from oauth import create_reddit_client_from_env
        self.assertTrue(callable(create_reddit_client_from_env))
        print("✓ create_reddit_client_from_env function exists")


def run_tests():
    """Run all tests."""
    print("=" * 70)
    print("Reddit OAuth Client Basic Tests")
    print("=" * 70)
    print()
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRedditOAuthBasic)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    if result.wasSuccessful():
        print(f"✅ All {result.testsRun} OAuth basic tests passed!")
    else:
        print("❌ Some OAuth tests failed")
        for failure in result.failures + result.errors:
            print(f"  - {failure[0]}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
