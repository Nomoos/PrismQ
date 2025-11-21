"""Tests for YouTube API Client with Quota Management.

This test suite verifies the YouTubeAPIClient integration with
quota tracking and error handling.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call

from src.core.youtube_api_client import YouTubeAPIClient
from src.core.youtube_quota_manager import QuotaExceededException
from googleapiclient.errors import HttpError


@pytest.fixture
def temp_quota_storage():
    """Create temporary quota storage file."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        storage_path = f.name
    
    yield storage_path
    
    # Cleanup
    Path(storage_path).unlink(missing_ok=True)


@pytest.fixture
def mock_youtube_service():
    """Create mock YouTube API service."""
    with patch('src.core.youtube_api_client.build') as mock_build:
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        yield mock_service


class TestYouTubeAPIClientInitialization:
    """Test API client initialization."""
    
    def test_initialization_with_valid_key(self, temp_quota_storage, mock_youtube_service):
        """Test initialization with valid API key."""
        client = YouTubeAPIClient(
            api_key='test_key_123',
            quota_storage_path=temp_quota_storage
        )
        
        assert client.api_key == 'test_key_123'
        assert client.quota_manager is not None
        assert client.quota_manager.daily_limit == 10000
    
    def test_initialization_with_custom_quota_limit(self, temp_quota_storage, mock_youtube_service):
        """Test initialization with custom quota limit."""
        client = YouTubeAPIClient(
            api_key='test_key_123',
            quota_storage_path=temp_quota_storage,
            daily_quota_limit=5000
        )
        
        assert client.quota_manager.daily_limit == 5000
    
    def test_initialization_without_api_key(self, temp_quota_storage):
        """Test initialization fails without API key."""
        with pytest.raises(ValueError) as exc_info:
            YouTubeAPIClient(
                api_key='',
                quota_storage_path=temp_quota_storage
            )
        
        assert 'API key is required' in str(exc_info.value)


class TestSearchVideos:
    """Test video search functionality."""
    
    def test_search_videos_success(self, temp_quota_storage, mock_youtube_service):
        """Test successful video search."""
        # Setup mock response
        mock_request = MagicMock()
        mock_request.execute.return_value = {
            'items': [
                {
                    'id': {'videoId': 'video123', 'kind': 'youtube#video'},
                    'snippet': {'title': 'Test Video'}
                }
            ]
        }
        mock_youtube_service.search().list.return_value = mock_request
        
        # Create client and search
        client = YouTubeAPIClient(
            api_key='test_key',
            quota_storage_path=temp_quota_storage
        )
        
        results = client.search_videos(query='test', max_results=5)
        
        assert len(results) == 1
        assert results[0]['id']['videoId'] == 'video123'
        
        # Verify quota was consumed
        assert client.get_remaining_quota() == 10000 - 100  # search.list costs 100
    
    def test_search_videos_no_results(self, temp_quota_storage, mock_youtube_service):
        """Test search with no results."""
        mock_request = MagicMock()
        mock_request.execute.return_value = {'items': []}
        mock_youtube_service.search().list.return_value = mock_request
        
        client = YouTubeAPIClient(
            api_key='test_key',
            quota_storage_path=temp_quota_storage
        )
        
        results = client.search_videos(query='test')
        
        assert len(results) == 0
        assert client.get_remaining_quota() == 10000 - 100
    
    def test_search_videos_quota_exceeded(self, temp_quota_storage, mock_youtube_service):
        """Test search fails when quota exceeded."""
        client = YouTubeAPIClient(
            api_key='test_key',
            quota_storage_path=temp_quota_storage,
            daily_quota_limit=50  # Less than search cost
        )
        
        with pytest.raises(QuotaExceededException) as exc_info:
            client.search_videos(query='test')
        
        assert exc_info.value.operation == 'search.list'
        assert exc_info.value.cost == 100


class TestGetVideoDetails:
    """Test get video details functionality."""
    
    def test_get_video_details_success(self, temp_quota_storage, mock_youtube_service):
        """Test successfully getting video details."""
        mock_request = MagicMock()
        mock_request.execute.return_value = {
            'items': [{
                'id': 'video123',
                'snippet': {'title': 'Test Video'},
                'statistics': {'viewCount': '1000'}
            }]
        }
        mock_youtube_service.videos().list.return_value = mock_request
        
        client = YouTubeAPIClient(
            api_key='test_key',
            quota_storage_path=temp_quota_storage
        )
        
        video = client.get_video_details('video123')
        
        assert video is not None
        assert video['id'] == 'video123'
        assert client.get_remaining_quota() == 10000 - 1  # videos.list costs 1
    
    def test_get_video_details_not_found(self, temp_quota_storage, mock_youtube_service):
        """Test getting details for non-existent video."""
        mock_request = MagicMock()
        mock_request.execute.return_value = {'items': []}
        mock_youtube_service.videos().list.return_value = mock_request
        
        client = YouTubeAPIClient(
            api_key='test_key',
            quota_storage_path=temp_quota_storage
        )
        
        video = client.get_video_details('nonexistent')
        
        assert video is None
        assert client.get_remaining_quota() == 10000 - 1


class TestGetVideosBatch:
    """Test batch video details retrieval."""
    
    def test_get_videos_batch_success(self, temp_quota_storage, mock_youtube_service):
        """Test successfully getting multiple videos."""
        mock_request = MagicMock()
        mock_request.execute.return_value = {
            'items': [
                {'id': 'video1', 'snippet': {'title': 'Video 1'}},
                {'id': 'video2', 'snippet': {'title': 'Video 2'}},
            ]
        }
        mock_youtube_service.videos().list.return_value = mock_request
        
        client = YouTubeAPIClient(
            api_key='test_key',
            quota_storage_path=temp_quota_storage
        )
        
        videos = client.get_videos_batch(['video1', 'video2'])
        
        assert len(videos) == 2
        assert videos[0]['id'] == 'video1'
        assert videos[1]['id'] == 'video2'
        assert client.get_remaining_quota() == 10000 - 1
    
    def test_get_videos_batch_empty(self, temp_quota_storage, mock_youtube_service):
        """Test batch retrieval with empty list."""
        client = YouTubeAPIClient(
            api_key='test_key',
            quota_storage_path=temp_quota_storage
        )
        
        videos = client.get_videos_batch([])
        
        assert len(videos) == 0
        assert client.get_remaining_quota() == 10000  # No API call made
    
    def test_get_videos_batch_limits_to_50(self, temp_quota_storage, mock_youtube_service):
        """Test batch retrieval limits to 50 videos."""
        mock_request = MagicMock()
        mock_request.execute.return_value = {'items': []}
        mock_youtube_service.videos().list.return_value = mock_request
        
        client = YouTubeAPIClient(
            api_key='test_key',
            quota_storage_path=temp_quota_storage
        )
        
        # Try to get 100 videos
        video_ids = [f'video{i}' for i in range(100)]
        client.get_videos_batch(video_ids)
        
        # Verify only 50 IDs were sent
        call_args = mock_youtube_service.videos().list.call_args
        ids_param = call_args[1]['id']
        assert len(ids_param.split(',')) == 50


class TestErrorHandling:
    """Test error handling and retries."""
    
    def test_http_error_403_quota_exceeded(self, temp_quota_storage, mock_youtube_service):
        """Test handling of 403 quota exceeded error."""
        # Create mock error
        mock_resp = Mock()
        mock_resp.status = 403
        
        mock_error = HttpError(mock_resp, b'{"error": {"errors": [{"reason": "quotaExceeded"}]}}')
        mock_error.error_details = [{'reason': 'quotaExceeded'}]
        
        mock_request = MagicMock()
        mock_request.execute.side_effect = mock_error
        mock_youtube_service.videos().list.return_value = mock_request
        
        client = YouTubeAPIClient(
            api_key='test_key',
            quota_storage_path=temp_quota_storage
        )
        
        with pytest.raises(QuotaExceededException):
            client.get_video_details('video123')
    
    def test_http_error_500_retries(self, temp_quota_storage, mock_youtube_service):
        """Test that 500 errors trigger retries."""
        mock_resp = Mock()
        mock_resp.status = 500
        
        mock_error = HttpError(mock_resp, b'Server error')
        
        mock_request = MagicMock()
        mock_request.execute.side_effect = [mock_error, mock_error, mock_error]
        mock_youtube_service.videos().list.return_value = mock_request
        
        client = YouTubeAPIClient(
            api_key='test_key',
            quota_storage_path=temp_quota_storage,
            max_retries=3,
            base_delay=0.01  # Fast for testing
        )
        
        with pytest.raises(HttpError):
            client.get_video_details('video123')
        
        # Verify it retried 3 times
        assert mock_request.execute.call_count == 3


class TestQuotaIntegration:
    """Test quota tracking integration."""
    
    def test_quota_usage_tracking(self, temp_quota_storage, mock_youtube_service):
        """Test that quota usage is tracked correctly."""
        mock_request = MagicMock()
        mock_request.execute.return_value = {
            'items': [{'id': 'video123', 'snippet': {}}]
        }
        mock_youtube_service.videos().list.return_value = mock_request
        
        client = YouTubeAPIClient(
            api_key='test_key',
            quota_storage_path=temp_quota_storage,
            daily_quota_limit=10000
        )
        
        # Make multiple API calls
        client.get_video_details('video1')
        client.get_video_details('video2')
        client.get_video_details('video3')
        
        # Check quota usage
        usage = client.get_quota_usage()
        assert usage['total_used'] == 3  # 3 videos.list calls
        assert usage['remaining'] == 9997
        assert usage['operations']['videos.list'] == 3
    
    def test_can_execute_operation(self, temp_quota_storage, mock_youtube_service):
        """Test checking if operation can be executed."""
        client = YouTubeAPIClient(
            api_key='test_key',
            quota_storage_path=temp_quota_storage,
            daily_quota_limit=150
        )
        
        # Should be able to execute one search
        assert client.can_execute_operation('search.list') is True
        
        # Should not be able to execute two searches
        assert client.can_execute_operation('search.list', count=2) is False
        
        # Should be able to execute many videos.list
        assert client.can_execute_operation('videos.list', count=100) is True
    
    def test_get_remaining_quota(self, temp_quota_storage, mock_youtube_service):
        """Test getting remaining quota."""
        mock_request = MagicMock()
        mock_request.execute.return_value = {'items': []}
        mock_youtube_service.search().list.return_value = mock_request
        
        client = YouTubeAPIClient(
            api_key='test_key',
            quota_storage_path=temp_quota_storage,
            daily_quota_limit=1000
        )
        
        # Initial quota
        assert client.get_remaining_quota() == 1000
        
        # After search
        client.search_videos(query='test')
        assert client.get_remaining_quota() == 900  # 1000 - 100
