"""Rate limiter and quota management for YouTube API.

This module provides rate limiting and quota tracking to ensure compliance
with YouTube API usage limits and prevent quota exhaustion.
"""

import time
from datetime import datetime, timedelta
from threading import Lock
from typing import Optional

try:
    from ..exceptions import YouTubeQuotaExceededError, YouTubeRateLimitError
except ImportError:
    from exceptions.youtube_exceptions import (
        YouTubeQuotaExceededError,
        YouTubeRateLimitError,
    )


class RateLimiter:
    """Rate limiter with quota tracking for YouTube API.

    Implements token bucket algorithm for rate limiting and tracks daily
    quota usage to prevent exceeding YouTube API limits.

    YouTube API Limits:
    - Free tier: 10,000 quota units per day
    - Rate limiting: Recommended to stay under 100 requests/minute

    Attributes:
        requests_per_minute: Maximum requests allowed per minute
        quota_per_day: Daily quota limit in units
        current_quota_usage: Current quota usage for the day
        last_reset: Timestamp of last quota reset

    Example:
        >>> limiter = RateLimiter(requests_per_minute=100, quota_per_day=10000)
        >>> limiter.wait_if_needed()  # Blocks if rate limit would be exceeded
        >>> limiter.track_request(cost=1)  # Track quota usage
    """

    def __init__(self, requests_per_minute: int = 100, quota_per_day: int = 10000):
        """Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute (default: 100)
            quota_per_day: Daily quota limit in units (default: 10000)
        """
        self.requests_per_minute = requests_per_minute
        self.quota_per_day = quota_per_day

        # Token bucket for rate limiting
        self.tokens = float(requests_per_minute)
        self.max_tokens = float(requests_per_minute)
        self.refill_rate = requests_per_minute / 60.0  # tokens per second
        self.last_refill = time.time()

        # Quota tracking
        self.current_quota_usage = 0
        self.last_reset = datetime.utcnow()

        # Thread safety
        self._lock = Lock()

    def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded.

        This method blocks until a token is available, implementing
        the token bucket algorithm for smooth rate limiting.

        Raises:
            YouTubeRateLimitError: If system time goes backwards
        """
        with self._lock:
            # Refill tokens based on time elapsed
            now = time.time()
            elapsed = now - self.last_refill

            if elapsed < 0:
                # System time went backwards
                raise YouTubeRateLimitError("System time went backwards", retry_after=1)

            # Add tokens based on elapsed time
            self.tokens = min(self.max_tokens, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now

            # Wait if no tokens available
            if self.tokens < 1.0:
                wait_time = (1.0 - self.tokens) / self.refill_rate
                time.sleep(wait_time)
                self.tokens = 1.0
                self.last_refill = time.time()

            # Consume one token
            self.tokens -= 1.0

    def track_request(self, cost: int) -> None:
        """Track API request quota usage.

        YouTube API operations have different quota costs:
        - search: 100 units
        - videos.list: 1 unit
        - channels.list: 1 unit

        Args:
            cost: Quota cost of the request in units

        Raises:
            YouTubeQuotaExceededError: If adding cost would exceed daily quota
        """
        with self._lock:
            # Reset quota if new day
            self._reset_if_new_day()

            # Check if request would exceed quota
            if self.current_quota_usage + cost > self.quota_per_day:
                raise YouTubeQuotaExceededError(
                    f"Request would exceed daily quota "
                    f"({self.current_quota_usage + cost}/{self.quota_per_day})",
                    current_usage=self.current_quota_usage,
                    daily_limit=self.quota_per_day,
                )

            self.current_quota_usage += cost

    def can_make_request(self, cost: int) -> bool:
        """Check if a request can be made without exceeding quota.

        Args:
            cost: Quota cost of the potential request

        Returns:
            True if request can be made, False otherwise
        """
        with self._lock:
            self._reset_if_new_day()
            return self.current_quota_usage + cost <= self.quota_per_day

    def get_remaining_quota(self) -> int:
        """Get remaining quota for the day.

        Returns:
            Remaining quota units
        """
        with self._lock:
            self._reset_if_new_day()
            return self.quota_per_day - self.current_quota_usage

    def reset_daily_quota(self) -> None:
        """Manually reset daily quota (for testing or admin purposes)."""
        with self._lock:
            self.current_quota_usage = 0
            self.last_reset = datetime.utcnow()

    def _reset_if_new_day(self) -> None:
        """Reset quota if it's a new day (UTC).

        Private method called by quota tracking methods to automatically
        reset quota at midnight UTC.
        """
        now = datetime.utcnow()
        if now.date() > self.last_reset.date():
            self.current_quota_usage = 0
            self.last_reset = now

    def get_stats(self) -> dict:
        """Get current rate limiter statistics.

        Returns:
            Dictionary with current stats including quota usage,
            available tokens, and time until quota reset
        """
        with self._lock:
            self._reset_if_new_day()

            # Calculate time until next quota reset
            tomorrow = (self.last_reset + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            seconds_until_reset = (tomorrow - datetime.utcnow()).total_seconds()

            return {
                "quota_used": self.current_quota_usage,
                "quota_remaining": self.quota_per_day - self.current_quota_usage,
                "quota_limit": self.quota_per_day,
                "available_tokens": self.tokens,
                "max_tokens": self.max_tokens,
                "requests_per_minute": self.requests_per_minute,
                "seconds_until_quota_reset": max(0, seconds_until_reset),
            }
