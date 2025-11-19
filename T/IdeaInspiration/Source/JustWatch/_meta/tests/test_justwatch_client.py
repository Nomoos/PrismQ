"""
Tests for JustWatch Client

Basic tests to ensure the JustWatch client initializes correctly
and has the expected interface.
"""

import pytest
from Source.JustWatch.src import JustWatchClient, StreamingProvider


class TestJustWatchClient:
    """Test suite for JustWatchClient"""
    
    def test_client_initialization(self):
        """Test that client can be initialized with required parameters"""
        client = JustWatchClient(api_key="test_key")
        
        assert client.api_key == "test_key"
        assert client.default_country == "US"
        assert client.base_url == "https://apis.justwatch.com"
    
    def test_client_custom_configuration(self):
        """Test client with custom configuration"""
        client = JustWatchClient(
            api_key="test_key",
            base_url="https://custom.api.com",
            default_country="UK",
            request_timeout=60,
            requests_per_minute=100
        )
        
        assert client.api_key == "test_key"
        assert client.base_url == "https://custom.api.com"
        assert client.default_country == "UK"
        assert client.request_timeout == 60
        assert client.requests_per_minute == 100
    
    def test_supported_providers(self):
        """Test that all expected providers are supported"""
        client = JustWatchClient(api_key="test_key")
        
        expected_providers = ['disney', 'prime', 'netflix', 'hulu', 'hbomax', 'appletv', 'paramount']
        assert client.supported_providers == expected_providers
    
    def test_streaming_provider_enum(self):
        """Test StreamingProvider enum values"""
        assert StreamingProvider.DISNEY.value == "disney"
        assert StreamingProvider.PRIME.value == "prime"
        assert StreamingProvider.NETFLIX.value == "netflix"
        assert StreamingProvider.HULU.value == "hulu"
        assert StreamingProvider.HBOMAX.value == "hbomax"
        assert StreamingProvider.APPLETV.value == "appletv"
        assert StreamingProvider.PARAMOUNT.value == "paramount"
    
    def test_validate_provider_valid(self):
        """Test provider validation with valid provider"""
        client = JustWatchClient(api_key="test_key")
        
        # Should not raise an exception
        client._validate_provider("disney")
        client._validate_provider("netflix")
    
    def test_validate_provider_invalid(self):
        """Test provider validation with invalid provider"""
        client = JustWatchClient(api_key="test_key")
        
        with pytest.raises(ValueError) as exc_info:
            client._validate_provider("invalid_provider")
        
        assert "not supported" in str(exc_info.value).lower()
    
    def test_create_inspiration_from_content(self):
        """Test creating IdeaInspiration-compatible dict from content"""
        client = JustWatchClient(api_key="test_key")
        
        content = {
            'title': 'Test Show',
            'short_description': 'A great show',
            'object_type': 'show',
            'id': '12345',
            'jw_popularity': 8.5,
            'trending_rank': 3,
            'original_release_year': '2024',
            'genres': ['Drama', 'Action'],
            'imdb_score': 8.7,
            'tmdb_score': 8.3,
            'runtime_minutes': 45,
            'seasons': 2,
            'episodes': 20,
            'is_original': True
        }
        
        result = client.create_inspiration_from_content(
            content=content,
            provider='disney',
            country='US'
        )
        
        assert result['title'] == 'Test Show'
        assert result['content'] == 'A great show'
        assert result['metadata']['platform'] == 'justwatch'
        assert result['metadata']['provider'] == 'disney'
        assert result['metadata']['content_type'] == 'show'
        assert result['metadata']['popularity_score'] == 8.5
        assert result['metadata']['imdb_score'] == 8.7
        assert result['metadata']['is_original'] is True
    
    def test_get_statistics_initial(self):
        """Test statistics with no requests made"""
        client = JustWatchClient(api_key="test_key")
        
        stats = client.get_statistics()
        
        assert stats['total_requests'] == 0
        assert stats['successful_requests'] == 0
        assert stats['failed_requests'] == 0
        assert stats['success_rate'] == 0.0
    
    def test_client_has_required_methods(self):
        """Test that client has all required methods"""
        client = JustWatchClient(api_key="test_key")
        
        assert hasattr(client, 'fetch_popular_content')
        assert hasattr(client, 'fetch_trending_content')
        assert hasattr(client, 'fetch_new_releases')
        assert hasattr(client, 'search_content')
        assert hasattr(client, 'get_content_availability')
        assert hasattr(client, 'compare_popularity_across_providers')
        assert hasattr(client, 'get_cross_platform_trending')
        assert hasattr(client, 'create_inspiration_from_content')
        assert hasattr(client, 'get_statistics')


class TestStreamingProviderEnum:
    """Test suite for StreamingProvider enum"""
    
    def test_all_providers_defined(self):
        """Test that all expected providers are in the enum"""
        providers = [p.value for p in StreamingProvider]
        
        assert 'disney' in providers
        assert 'prime' in providers
        assert 'netflix' in providers
        assert 'hulu' in providers
        assert 'hbomax' in providers
        assert 'appletv' in providers
        assert 'paramount' in providers
    
    def test_provider_count(self):
        """Test that we have exactly 7 providers"""
        assert len(list(StreamingProvider)) == 7
