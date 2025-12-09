"""YouTube-specific exception classes.

This module provides custom exceptions for handling YouTube API errors,
rate limiting, quota management, and other YouTube-specific error conditions.
"""


class YouTubeError(Exception):
    """Base exception for all YouTube-related errors.

    All YouTube-specific exceptions inherit from this base class,
    making it easy to catch any YouTube-related error.

    Example:
        >>> try:
        ...     # YouTube operation
        ...     pass
        ... except YouTubeError as e:
        ...     print(f"YouTube error: {e}")
    """

    pass


class YouTubeAPIError(YouTubeError):
    """Exception raised when YouTube API requests fail.

    This includes network errors, invalid responses, authentication failures,
    and other API-level errors.

    Attributes:
        message: Description of the error
        status_code: HTTP status code (if applicable)
        response: Raw API response (if available)

    Example:
        >>> raise YouTubeAPIError("Failed to fetch video details", status_code=404)
    """

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class YouTubeQuotaExceededError(YouTubeError):
    """Exception raised when YouTube API quota is exceeded.

    YouTube has daily quota limits (10,000 units/day for free tier).
    This exception is raised when operations would exceed the quota.

    Attributes:
        message: Description of the quota error
        current_usage: Current quota usage
        daily_limit: Daily quota limit

    Example:
        >>> raise YouTubeQuotaExceededError(
        ...     "Daily quota exceeded",
        ...     current_usage=10000,
        ...     daily_limit=10000
        ... )
    """

    def __init__(self, message: str, current_usage: int = None, daily_limit: int = None):
        super().__init__(message)
        self.current_usage = current_usage
        self.daily_limit = daily_limit


class YouTubeRateLimitError(YouTubeError):
    """Exception raised when rate limit is exceeded.

    This is raised when too many requests are made within a short time period,
    distinct from quota limits which are daily limits.

    Attributes:
        message: Description of the rate limit error
        retry_after: Seconds to wait before retrying

    Example:
        >>> raise YouTubeRateLimitError(
        ...     "Rate limit exceeded",
        ...     retry_after=60
        ... )
    """

    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after


class YouTubeInvalidVideoError(YouTubeError):
    """Exception raised when video data is invalid or missing.

    This includes invalid video IDs, deleted videos, private videos,
    or videos with missing/malformed metadata.

    Attributes:
        message: Description of the error
        video_id: The invalid video ID

    Example:
        >>> raise YouTubeInvalidVideoError(
        ...     "Video not found or private",
        ...     video_id="abc123"
        ... )
    """

    def __init__(self, message: str, video_id: str = None):
        super().__init__(message)
        self.video_id = video_id


class YouTubeConfigError(YouTubeError):
    """Exception raised when YouTube configuration is invalid.

    This includes missing API keys, invalid configuration values,
    or configuration that doesn't meet requirements.

    Attributes:
        message: Description of the configuration error
        config_key: The problematic configuration key

    Example:
        >>> raise YouTubeConfigError(
        ...     "API key is required",
        ...     config_key="api_key"
        ... )
    """

    def __init__(self, message: str, config_key: str = None):
        super().__init__(message)
        self.config_key = config_key
