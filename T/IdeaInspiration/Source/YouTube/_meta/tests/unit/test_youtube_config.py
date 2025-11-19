"""Unit tests for YouTubeConfig."""

import pytest
import os
from src.config.youtube_config import YouTubeConfig


class TestYouTubeConfigInitialization:
    """Tests for YouTubeConfig initialization."""
    
    def test_initialization_with_api_key(self):
        """Test creating config with API key."""
        config = YouTubeConfig(api_key="test_key_12345")
        assert config.api_key == "test_key_12345"
        assert config.rate_limit == 100
        assert config.quota_per_day == 10000
    
    def test_initialization_with_custom_values(self):
        """Test creating config with custom values."""
        config = YouTubeConfig(
            api_key="test_key",
            rate_limit=50,
            quota_per_day=5000,
            max_retries=5,
            timeout=60
        )
        assert config.rate_limit == 50
        assert config.quota_per_day == 5000
        assert config.max_retries == 5
        assert config.timeout == 60
    
    def test_initialization_without_api_key(self):
        """Test that initialization fails without API key."""
        with pytest.raises(ValueError, match="API key is required"):
            YouTubeConfig(api_key="")


class TestYouTubeConfigValidation:
    """Tests for configuration validation."""
    
    def test_validate_success(self):
        """Test validation with valid config."""
        config = YouTubeConfig(api_key="test_key")
        config.validate()  # Should not raise
    
    def test_validate_negative_rate_limit(self):
        """Test that negative rate limit fails validation."""
        with pytest.raises(ValueError, match="rate_limit must be positive"):
            YouTubeConfig(api_key="test_key", rate_limit=-1)
    
    def test_validate_negative_quota(self):
        """Test that negative quota fails validation."""
        with pytest.raises(ValueError, match="quota_per_day must be positive"):
            YouTubeConfig(api_key="test_key", quota_per_day=-1)
    
    def test_validate_negative_timeout(self):
        """Test that negative timeout fails validation."""
        with pytest.raises(ValueError, match="timeout must be positive"):
            YouTubeConfig(api_key="test_key", timeout=-1)
    
    def test_validate_invalid_batch_size(self):
        """Test that invalid batch size fails validation."""
        with pytest.raises(ValueError, match="batch_size must be between 1 and 50"):
            YouTubeConfig(api_key="test_key", batch_size=0)
        
        with pytest.raises(ValueError, match="batch_size must be between 1 and 50"):
            YouTubeConfig(api_key="test_key", batch_size=51)


class TestYouTubeConfigFromEnv:
    """Tests for creating config from environment variables."""
    
    def test_from_env_with_api_key(self, monkeypatch):
        """Test creating config from environment."""
        monkeypatch.setenv("YOUTUBE_API_KEY", "env_test_key")
        
        config = YouTubeConfig.from_env()
        assert config.api_key == "env_test_key"
    
    def test_from_env_with_custom_values(self, monkeypatch):
        """Test creating config with custom environment values."""
        monkeypatch.setenv("YOUTUBE_API_KEY", "env_key")
        monkeypatch.setenv("YOUTUBE_RATE_LIMIT", "50")
        monkeypatch.setenv("YOUTUBE_QUOTA_PER_DAY", "5000")
        
        config = YouTubeConfig.from_env()
        assert config.api_key == "env_key"
        assert config.rate_limit == 50
        assert config.quota_per_day == 5000
    
    def test_from_env_without_api_key(self, monkeypatch):
        """Test that missing API key in environment fails."""
        # Clear any existing YOUTUBE_API_KEY
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        
        with pytest.raises(ValueError, match="API key is required"):
            YouTubeConfig.from_env()


class TestYouTubeConfigFromDict:
    """Tests for creating config from dictionary."""
    
    def test_from_dict_basic(self):
        """Test creating config from dictionary."""
        config_dict = {
            'api_key': 'dict_key',
            'rate_limit': 75,
            'quota_per_day': 8000
        }
        
        config = YouTubeConfig.from_dict(config_dict)
        assert config.api_key == 'dict_key'
        assert config.rate_limit == 75
        assert config.quota_per_day == 8000
    
    def test_from_dict_partial(self):
        """Test creating config with partial dictionary."""
        config_dict = {'api_key': 'dict_key'}
        
        config = YouTubeConfig.from_dict(config_dict)
        assert config.api_key == 'dict_key'
        assert config.rate_limit == 100  # Default value
    
    def test_from_dict_extra_keys(self):
        """Test that extra keys in dictionary are ignored."""
        config_dict = {
            'api_key': 'dict_key',
            'extra_key': 'should_be_ignored'
        }
        
        config = YouTubeConfig.from_dict(config_dict)
        assert config.api_key == 'dict_key'
        assert not hasattr(config, 'extra_key')


class TestYouTubeConfigToDict:
    """Tests for converting config to dictionary."""
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = YouTubeConfig(
            api_key="test_key",
            rate_limit=50,
            quota_per_day=5000
        )
        
        config_dict = config.to_dict()
        
        assert config_dict['api_key'] == '***'  # Masked
        assert config_dict['rate_limit'] == 50
        assert config_dict['quota_per_day'] == 5000
    
    def test_to_dict_masks_api_key(self):
        """Test that API key is masked in dict representation."""
        config = YouTubeConfig(api_key="secret_key_12345")
        
        config_dict = config.to_dict()
        assert config_dict['api_key'] == '***'


class TestYouTubeConfigRepresentation:
    """Tests for string representation."""
    
    def test_repr_masks_api_key(self):
        """Test that __repr__ masks the API key."""
        config = YouTubeConfig(api_key="secret_key")
        
        repr_str = repr(config)
        assert 'secret_key' not in repr_str
        assert '***' in repr_str
    
    def test_repr_shows_other_values(self):
        """Test that __repr__ shows other configuration values."""
        config = YouTubeConfig(
            api_key="test_key",
            rate_limit=75,
            quota_per_day=8000
        )
        
        repr_str = repr(config)
        assert 'rate_limit=75' in repr_str
        assert 'quota_per_day=8000' in repr_str


class TestYouTubeConfigDefaults:
    """Tests for default configuration values."""
    
    def test_default_values(self):
        """Test that default values are correct."""
        config = YouTubeConfig(api_key="test_key")
        
        assert config.rate_limit == 100
        assert config.quota_per_day == 10000
        assert config.max_retries == 3
        assert config.timeout == 30
        assert config.cache_ttl == 3600
        assert config.batch_size == 50
        assert config.enable_caching is True
        assert config.enable_rate_limiting is True
        assert config.enable_quota_tracking is True
