"""Unit tests for RateLimiter."""

import pytest
import time
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src directory to path for direct imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'src'))

from client.rate_limiter import RateLimiter
from exceptions.youtube_exceptions import YouTubeQuotaExceededError, YouTubeRateLimitError


class TestRateLimiterInitialization:
    """Tests for RateLimiter initialization."""
    
    def test_default_initialization(self):
        """Test rate limiter with default parameters."""
        limiter = RateLimiter()
        assert limiter.requests_per_minute == 100
        assert limiter.quota_per_day == 10000
        assert limiter.current_quota_usage == 0
        assert limiter.tokens == 100.0
    
    def test_custom_initialization(self):
        """Test rate limiter with custom parameters."""
        limiter = RateLimiter(requests_per_minute=50, quota_per_day=5000)
        assert limiter.requests_per_minute == 50
        assert limiter.quota_per_day == 5000
        assert limiter.max_tokens == 50.0


class TestRateLimiting:
    """Tests for rate limiting functionality."""
    
    def test_wait_if_needed_basic(self):
        """Test that wait_if_needed doesn't block when tokens available."""
        limiter = RateLimiter(requests_per_minute=100)
        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start
        assert elapsed < 0.1  # Should be nearly instant
    
    def test_wait_if_needed_blocks(self):
        """Test that wait_if_needed blocks when no tokens available."""
        limiter = RateLimiter(requests_per_minute=60)  # 1 per second
        
        # Consume all tokens
        limiter.tokens = 0.5
        
        start = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start
        
        # Should wait approximately 0.5 seconds
        assert elapsed >= 0.4  # Allow some tolerance
    
    def test_multiple_sequential_requests(self):
        """Test multiple requests in sequence."""
        limiter = RateLimiter(requests_per_minute=120)  # 2 per second
        
        for _ in range(3):
            limiter.wait_if_needed()
        
        # Should complete without significant delay
        assert limiter.tokens >= 0


class TestQuotaTracking:
    """Tests for quota tracking functionality."""
    
    def test_track_request_basic(self):
        """Test tracking a single request."""
        limiter = RateLimiter()
        limiter.track_request(cost=1)
        assert limiter.current_quota_usage == 1
    
    def test_track_multiple_requests(self):
        """Test tracking multiple requests."""
        limiter = RateLimiter()
        limiter.track_request(cost=100)  # search
        limiter.track_request(cost=1)    # videos.list
        limiter.track_request(cost=1)    # videos.list
        assert limiter.current_quota_usage == 102
    
    def test_track_request_exceeds_quota(self):
        """Test tracking request that would exceed quota."""
        limiter = RateLimiter(quota_per_day=100)
        limiter.current_quota_usage = 50
        
        with pytest.raises(YouTubeQuotaExceededError) as exc_info:
            limiter.track_request(cost=51)
        
        assert exc_info.value.current_usage == 50
        assert exc_info.value.daily_limit == 100
    
    def test_track_request_at_quota_limit(self):
        """Test tracking request at exact quota limit."""
        limiter = RateLimiter(quota_per_day=100)
        limiter.current_quota_usage = 99
        
        # Should succeed
        limiter.track_request(cost=1)
        assert limiter.current_quota_usage == 100
        
        # Next request should fail
        with pytest.raises(YouTubeQuotaExceededError):
            limiter.track_request(cost=1)


class TestQuotaChecking:
    """Tests for quota checking methods."""
    
    def test_can_make_request_true(self):
        """Test can_make_request when quota available."""
        limiter = RateLimiter(quota_per_day=1000)
        limiter.current_quota_usage = 500
        assert limiter.can_make_request(cost=100) is True
    
    def test_can_make_request_false(self):
        """Test can_make_request when quota insufficient."""
        limiter = RateLimiter(quota_per_day=100)
        limiter.current_quota_usage = 90
        assert limiter.can_make_request(cost=20) is False
    
    def test_can_make_request_exact(self):
        """Test can_make_request at exact quota limit."""
        limiter = RateLimiter(quota_per_day=100)
        limiter.current_quota_usage = 50
        assert limiter.can_make_request(cost=50) is True
        assert limiter.can_make_request(cost=51) is False
    
    def test_get_remaining_quota(self):
        """Test getting remaining quota."""
        limiter = RateLimiter(quota_per_day=10000)
        limiter.current_quota_usage = 2500
        assert limiter.get_remaining_quota() == 7500


class TestQuotaReset:
    """Tests for quota reset functionality."""
    
    def test_manual_reset(self):
        """Test manual quota reset."""
        limiter = RateLimiter()
        limiter.current_quota_usage = 5000
        
        limiter.reset_daily_quota()
        
        assert limiter.current_quota_usage == 0
        assert isinstance(limiter.last_reset, datetime)
    
    def test_automatic_daily_reset(self):
        """Test automatic quota reset on new day."""
        limiter = RateLimiter()
        limiter.current_quota_usage = 5000
        
        # Simulate next day
        limiter.last_reset = datetime.utcnow() - timedelta(days=1)
        
        # This should trigger reset
        remaining = limiter.get_remaining_quota()
        
        assert limiter.current_quota_usage == 0
        assert remaining == limiter.quota_per_day


class TestRateLimiterStats:
    """Tests for rate limiter statistics."""
    
    def test_get_stats_basic(self):
        """Test getting basic stats."""
        limiter = RateLimiter(quota_per_day=10000)
        limiter.current_quota_usage = 2500
        
        stats = limiter.get_stats()
        
        assert stats['quota_used'] == 2500
        assert stats['quota_remaining'] == 7500
        assert stats['quota_limit'] == 10000
        assert 'available_tokens' in stats
        assert 'seconds_until_quota_reset' in stats
    
    def test_get_stats_full_quota(self):
        """Test stats when quota is exhausted."""
        limiter = RateLimiter(quota_per_day=1000)
        limiter.current_quota_usage = 1000
        
        stats = limiter.get_stats()
        
        assert stats['quota_used'] == 1000
        assert stats['quota_remaining'] == 0
        assert stats['seconds_until_quota_reset'] >= 0


class TestEdgeCases:
    """Tests for edge cases and error conditions."""
    
    def test_zero_quota(self):
        """Test behavior with zero quota."""
        limiter = RateLimiter(quota_per_day=0)
        
        with pytest.raises(YouTubeQuotaExceededError):
            limiter.track_request(cost=1)
    
    def test_negative_cost(self):
        """Test tracking request with negative cost."""
        limiter = RateLimiter()
        initial = limiter.current_quota_usage
        
        # Negative cost should still work (unusual but not error)
        limiter.track_request(cost=-10)
        assert limiter.current_quota_usage == initial - 10
    
    def test_very_high_rate_limit(self):
        """Test with very high rate limit."""
        limiter = RateLimiter(requests_per_minute=10000)
        
        # Should handle many sequential requests quickly
        start = time.time()
        for _ in range(10):
            limiter.wait_if_needed()
        elapsed = time.time() - start
        
        assert elapsed < 0.5  # Should be fast


class TestThreadSafety:
    """Tests for thread safety (basic checks)."""
    
    def test_quota_tracking_consistency(self):
        """Test that quota tracking is consistent."""
        limiter = RateLimiter()
        
        # Track multiple requests
        for i in range(100):
            limiter.track_request(cost=1)
        
        assert limiter.current_quota_usage == 100
    
    def test_rate_limiting_consistency(self):
        """Test that rate limiting is consistent."""
        limiter = RateLimiter(requests_per_minute=60)
        
        # Multiple wait calls
        for _ in range(5):
            limiter.wait_if_needed()
        
        # Should have consumed tokens
        assert limiter.tokens < 60.0
