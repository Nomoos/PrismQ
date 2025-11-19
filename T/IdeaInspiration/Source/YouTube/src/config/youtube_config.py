"""YouTube configuration management.

This module provides configuration classes for YouTube API integration,
including API keys, rate limits, and other settings.
"""

from dataclasses import dataclass, field
from typing import Optional
import os


@dataclass
class YouTubeConfig:
    """Configuration for YouTube API integration.
    
    Manages all YouTube-specific configuration including API credentials,
    rate limits, quota settings, and operational parameters.
    
    Configuration can be loaded from:
    1. Explicit parameters
    2. Environment variables
    3. Configuration files (future enhancement)
    
    Attributes:
        api_key: YouTube Data API key (required)
        rate_limit: Maximum requests per minute (default: 100)
        quota_per_day: Daily quota limit in units (default: 10000)
        max_retries: Maximum retry attempts for failed requests (default: 3)
        timeout: Request timeout in seconds (default: 30)
        cache_ttl: Cache time-to-live in seconds (default: 3600)
        batch_size: Batch processing size (default: 50)
        
    Example:
        >>> # From explicit parameters
        >>> config = YouTubeConfig(api_key="YOUR_KEY")
        
        >>> # From environment
        >>> config = YouTubeConfig.from_env()
        
        >>> # Custom settings
        >>> config = YouTubeConfig(
        ...     api_key="YOUR_KEY",
        ...     rate_limit=50,
        ...     quota_per_day=5000
        ... )
    """
    
    # API credentials
    api_key: str = ""
    
    # Rate limiting
    rate_limit: int = 100  # requests per minute
    quota_per_day: int = 10000  # daily quota limit (free tier)
    
    # Request settings
    max_retries: int = 3
    timeout: int = 30  # seconds
    
    # Caching
    cache_ttl: int = 3600  # seconds (1 hour)
    
    # Batch processing
    batch_size: int = 50  # max items per batch request
    
    # Optional settings
    enable_caching: bool = True
    enable_rate_limiting: bool = True
    enable_quota_tracking: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Validate configuration values.
        
        Raises:
            ValueError: If required values are missing or invalid
        """
        if not self.api_key:
            raise ValueError(
                "YouTube API key is required. "
                "Set via api_key parameter or YOUTUBE_API_KEY environment variable."
            )
        
        if self.rate_limit <= 0:
            raise ValueError("rate_limit must be positive")
        
        if self.quota_per_day <= 0:
            raise ValueError("quota_per_day must be positive")
        
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        
        if self.cache_ttl < 0:
            raise ValueError("cache_ttl cannot be negative")
        
        if self.batch_size <= 0 or self.batch_size > 50:
            raise ValueError("batch_size must be between 1 and 50")
    
    @classmethod
    def from_env(cls, prefix: str = "YOUTUBE_") -> "YouTubeConfig":
        """Create configuration from environment variables.
        
        Looks for environment variables with the specified prefix:
        - YOUTUBE_API_KEY
        - YOUTUBE_RATE_LIMIT
        - YOUTUBE_QUOTA_PER_DAY
        - YOUTUBE_MAX_RETRIES
        - YOUTUBE_TIMEOUT
        - YOUTUBE_CACHE_TTL
        - YOUTUBE_BATCH_SIZE
        
        Args:
            prefix: Environment variable prefix (default: "YOUTUBE_")
            
        Returns:
            YouTubeConfig instance with values from environment
            
        Raises:
            ValueError: If YOUTUBE_API_KEY is not set
        """
        return cls(
            api_key=os.getenv(f"{prefix}API_KEY", ""),
            rate_limit=int(os.getenv(f"{prefix}RATE_LIMIT", "100")),
            quota_per_day=int(os.getenv(f"{prefix}QUOTA_PER_DAY", "10000")),
            max_retries=int(os.getenv(f"{prefix}MAX_RETRIES", "3")),
            timeout=int(os.getenv(f"{prefix}TIMEOUT", "30")),
            cache_ttl=int(os.getenv(f"{prefix}CACHE_TTL", "3600")),
            batch_size=int(os.getenv(f"{prefix}BATCH_SIZE", "50")),
            enable_caching=os.getenv(f"{prefix}ENABLE_CACHING", "true").lower() == "true",
            enable_rate_limiting=os.getenv(f"{prefix}ENABLE_RATE_LIMITING", "true").lower() == "true",
            enable_quota_tracking=os.getenv(f"{prefix}ENABLE_QUOTA_TRACKING", "true").lower() == "true",
        )
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> "YouTubeConfig":
        """Create configuration from dictionary.
        
        Args:
            config_dict: Dictionary with configuration values
            
        Returns:
            YouTubeConfig instance
        """
        return cls(**{
            k: v for k, v in config_dict.items()
            if k in cls.__annotations__
        })
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary.
        
        Returns:
            Dictionary with all configuration values
        """
        return {
            'api_key': '***' if self.api_key else '',  # Masked for security
            'rate_limit': self.rate_limit,
            'quota_per_day': self.quota_per_day,
            'max_retries': self.max_retries,
            'timeout': self.timeout,
            'cache_ttl': self.cache_ttl,
            'batch_size': self.batch_size,
            'enable_caching': self.enable_caching,
            'enable_rate_limiting': self.enable_rate_limiting,
            'enable_quota_tracking': self.enable_quota_tracking,
        }
    
    def __repr__(self) -> str:
        """String representation with masked API key."""
        return (
            f"YouTubeConfig("
            f"api_key={'***' if self.api_key else 'NOT_SET'}, "
            f"rate_limit={self.rate_limit}, "
            f"quota_per_day={self.quota_per_day})"
        )
