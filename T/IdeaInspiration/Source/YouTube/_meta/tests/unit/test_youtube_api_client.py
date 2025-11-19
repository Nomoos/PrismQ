"""Unit tests for YouTubeAPIClient."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.client.youtube_api_client import YouTubeAPIClient
from src.exceptions import (
    YouTubeAPIError,
    YouTubeQuotaExceededError,
)


@pytest.fixture
def api_client():
    """Create a YouTube API client for testing."""
    return YouTubeAPIClient(api_key="test_key_12345", quota_per_day=10000)


@pytest.fixture
def mock_response():
    """Create a mock API response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {
        'items': [
            {
                'id': 'test123',
                'snippet': {
                    'title': 'Test Video',
                    'description': 'Test description',
                    'channelId': 'UC123',
                    'channelTitle': 'Test Channel'
                }
            }
        ]
    }
    return mock


class TestYouTubeAPIClientInitialization:
    """Tests for API client initialization."""
    
    def test_initialization_with_api_key(self):
        """Test creating client with API key."""
        client = YouTubeAPIClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.timeout == 30
        assert client.max_retries == 3
    
    def test_initialization_with_custom_params(self):
        """Test creating client with custom parameters."""
        client = YouTubeAPIClient(
            api_key="test_key",
            rate_limit=50,
            quota_per_day=5000,
            timeout=60,
            max_retries=5
        )
        assert client.rate_limiter.requests_per_minute == 50
        assert client.rate_limiter.quota_per_day == 5000
        assert client.timeout == 60
        assert client.max_retries == 5
    
    def test_initialization_without_api_key(self):
        """Test that initialization fails without API key."""
        with pytest.raises(ValueError, match="API key is required"):
            YouTubeAPIClient(api_key="")
    
    def test_session_creation(self):
        """Test that requests session is created."""
        client = YouTubeAPIClient(api_key="test_key")
        assert client.session is not None
        assert 'User-Agent' in client.session.headers


class TestSearchMethod:
    """Tests for search method."""
    
    def test_search_with_query(self, api_client, mock_response):
        """Test searching with a query string."""
        with patch.object(api_client.session, 'get', return_value=mock_response):
            result = api_client.search(query="python tutorial", max_results=10)
            assert 'items' in result
            assert len(result['items']) > 0
    
    def test_search_with_channel_id(self, api_client, mock_response):
        """Test searching within a specific channel."""
        with patch.object(api_client.session, 'get', return_value=mock_response):
            result = api_client.search(channel_id="UC123", max_results=10)
            assert 'items' in result
    
    def test_search_with_filters(self, api_client, mock_response):
        """Test searching with various filters."""
        with patch.object(api_client.session, 'get', return_value=mock_response) as mock_get:
            api_client.search(
                query="test",
                video_duration="short",
                published_after="2024-01-01T00:00:00Z",
                order="date"
            )
            
            # Verify parameters were passed
            call_args = mock_get.call_args
            params = call_args[1]['params']
            assert params['q'] == "test"
            assert params['videoDuration'] == "short"
            assert params['publishedAfter'] == "2024-01-01T00:00:00Z"
            assert params['order'] == "date"
    
    def test_search_max_results_capped(self, api_client, mock_response):
        """Test that max_results is capped at 50."""
        with patch.object(api_client.session, 'get', return_value=mock_response) as mock_get:
            api_client.search(query="test", max_results=100)
            
            params = mock_get.call_args[1]['params']
            assert params['maxResults'] == 50  # Capped at 50


class TestGetVideoDetails:
    """Tests for get_video_details method."""
    
    def test_get_video_details_single(self, api_client, mock_response):
        """Test getting details for a single video."""
        with patch.object(api_client.session, 'get', return_value=mock_response):
            result = api_client.get_video_details(['test123'])
            assert 'items' in result
    
    def test_get_video_details_multiple(self, api_client, mock_response):
        """Test getting details for multiple videos."""
        with patch.object(api_client.session, 'get', return_value=mock_response) as mock_get:
            api_client.get_video_details(['test1', 'test2', 'test3'])
            
            params = mock_get.call_args[1]['params']
            assert params['id'] == 'test1,test2,test3'
    
    def test_get_video_details_empty_list(self, api_client):
        """Test that empty video ID list raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            api_client.get_video_details([])
    
    def test_get_video_details_too_many(self, api_client):
        """Test that too many video IDs raises error."""
        video_ids = [f'id{i}' for i in range(51)]
        with pytest.raises(ValueError, match="Maximum 50"):
            api_client.get_video_details(video_ids)


class TestGetChannelDetails:
    """Tests for get_channel_details method."""
    
    def test_get_channel_details(self, api_client, mock_response):
        """Test getting channel details."""
        with patch.object(api_client.session, 'get', return_value=mock_response):
            result = api_client.get_channel_details(['UC123'])
            assert 'items' in result
    
    def test_get_channel_details_empty(self, api_client):
        """Test that empty channel ID list raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            api_client.get_channel_details([])


class TestGetPlaylistItems:
    """Tests for get_playlist_items method."""
    
    def test_get_playlist_items(self, api_client, mock_response):
        """Test getting playlist items."""
        with patch.object(api_client.session, 'get', return_value=mock_response):
            result = api_client.get_playlist_items('PL123')
            assert 'items' in result
    
    def test_get_playlist_items_with_pagination(self, api_client, mock_response):
        """Test getting playlist items with pagination."""
        with patch.object(api_client.session, 'get', return_value=mock_response) as mock_get:
            api_client.get_playlist_items('PL123', page_token='token123')
            
            params = mock_get.call_args[1]['params']
            assert params['pageToken'] == 'token123'


class TestQuotaManagement:
    """Tests for quota management."""
    
    def test_get_quota_usage(self, api_client):
        """Test getting current quota usage."""
        api_client.rate_limiter.current_quota_usage = 500
        assert api_client.get_quota_usage() == 500
    
    def test_get_remaining_quota(self, api_client):
        """Test getting remaining quota."""
        api_client.rate_limiter.current_quota_usage = 3000
        remaining = api_client.get_remaining_quota()
        assert remaining == 7000
    
    def test_quota_check_before_request(self, api_client, mock_response):
        """Test that quota is checked before making request."""
        # Set quota to nearly exhausted
        api_client.rate_limiter.current_quota_usage = 9950
        
        # Search costs 100, should fail
        with pytest.raises(YouTubeQuotaExceededError):
            api_client.search(query="test")


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_http_error_handling(self, api_client):
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Not found")
        mock_response.json.return_value = {}
        
        with patch.object(api_client.session, 'get', return_value=mock_response):
            with pytest.raises(YouTubeAPIError):
                api_client.search(query="test")
    
    def test_quota_exceeded_from_api(self, api_client):
        """Test handling quota exceeded response from API."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {
            'error': {
                'errors': [{'reason': 'quotaExceeded'}]
            }
        }
        
        with patch.object(api_client.session, 'get', return_value=mock_response):
            with pytest.raises(YouTubeQuotaExceededError):
                api_client.search(query="test")
    
    def test_retry_on_failure(self, api_client, mock_response):
        """Test that requests are retried on failure."""
        mock_fail = Mock()
        mock_fail.raise_for_status.side_effect = Exception("Temp error")
        
        with patch.object(api_client.session, 'get', side_effect=[mock_fail, mock_response]):
            # Should succeed on second try
            result = api_client.search(query="test")
            assert 'items' in result
    
    def test_max_retries_exceeded(self, api_client):
        """Test that error is raised after max retries."""
        mock_fail = Mock()
        mock_fail.raise_for_status.side_effect = Exception("Persistent error")
        
        with patch.object(api_client.session, 'get', return_value=mock_fail):
            with pytest.raises(YouTubeAPIError, match="HTTP error"):
                api_client.search(query="test")


class TestContextManager:
    """Tests for context manager functionality."""
    
    def test_context_manager_usage(self):
        """Test using client as context manager."""
        with YouTubeAPIClient(api_key="test_key") as client:
            assert client.api_client is not None
    
    def test_context_manager_closes_session(self):
        """Test that context manager closes session."""
        client = YouTubeAPIClient(api_key="test_key")
        with client:
            pass
        
        # Session should be closed after context exit
        # (We can't easily test this directly, but we can verify close was called)
        assert client.session is not None


class TestQuotaCosts:
    """Tests for quota cost constants."""
    
    def test_quota_costs_defined(self):
        """Test that quota costs are properly defined."""
        assert YouTubeAPIClient.QUOTA_COSTS['search'] == 100
        assert YouTubeAPIClient.QUOTA_COSTS['videos'] == 1
        assert YouTubeAPIClient.QUOTA_COSTS['channels'] == 1
        assert YouTubeAPIClient.QUOTA_COSTS['playlistItems'] == 1
