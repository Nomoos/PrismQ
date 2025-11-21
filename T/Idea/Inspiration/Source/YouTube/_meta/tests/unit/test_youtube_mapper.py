"""Unit tests for YouTubeMapper."""

import pytest
from datetime import datetime
from src.mappers.youtube_mapper import YouTubeMapper
from src.schemas import YouTubeVideo, YouTubeChannel, YouTubeSearchResult


@pytest.fixture
def mapper():
    """Create a YouTube mapper for testing."""
    return YouTubeMapper()


@pytest.fixture
def sample_video_response():
    """Sample YouTube API video response."""
    return {
        'id': 'abc123',
        'snippet': {
            'title': 'Test Video',
            'description': 'Test description',
            'channelId': 'UC123',
            'channelTitle': 'Test Channel',
            'publishedAt': '2024-01-01T12:00:00Z',
            'tags': ['python', 'tutorial'],
            'categoryId': '28',
            'thumbnails': {
                'default': {'url': 'https://example.com/thumb.jpg'},
                'high': {'url': 'https://example.com/thumb_hq.jpg'}
            }
        },
        'contentDetails': {
            'duration': 'PT5M30S',
            'caption': 'true',
            'definition': 'hd'
        },
        'statistics': {
            'viewCount': '1000',
            'likeCount': '100',
            'commentCount': '10'
        },
        'status': {
            'madeForKids': False
        }
    }


class TestParseVideo:
    """Tests for parse_video method."""
    
    def test_parse_video_basic(self, mapper, sample_video_response):
        """Test parsing a basic video response."""
        video = mapper.parse_video(sample_video_response)
        
        assert isinstance(video, YouTubeVideo)
        assert video.video_id == 'abc123'
        assert video.title == 'Test Video'
        assert video.description == 'Test description'
        assert video.channel_id == 'UC123'
        assert video.channel_title == 'Test Channel'
    
    def test_parse_video_duration(self, mapper, sample_video_response):
        """Test duration parsing."""
        video = mapper.parse_video(sample_video_response)
        assert video.duration == 330  # 5m30s = 330 seconds
    
    def test_parse_video_statistics(self, mapper, sample_video_response):
        """Test statistics parsing."""
        video = mapper.parse_video(sample_video_response)
        assert video.view_count == 1000
        assert video.like_count == 100
        assert video.comment_count == 10
    
    def test_parse_video_thumbnails(self, mapper, sample_video_response):
        """Test thumbnail parsing."""
        video = mapper.parse_video(sample_video_response)
        assert 'default' in video.thumbnails
        assert 'high' in video.thumbnails


class TestParseDuration:
    """Tests for _parse_duration method."""
    
    def test_parse_duration_hours_minutes_seconds(self, mapper):
        """Test parsing duration with hours, minutes, seconds."""
        assert mapper._parse_duration('PT1H2M3S') == 3723
    
    def test_parse_duration_minutes_seconds(self, mapper):
        """Test parsing duration with minutes and seconds."""
        assert mapper._parse_duration('PT5M30S') == 330
    
    def test_parse_duration_seconds_only(self, mapper):
        """Test parsing duration with seconds only."""
        assert mapper._parse_duration('PT45S') == 45
    
    def test_parse_duration_hours_only(self, mapper):
        """Test parsing duration with hours only."""
        assert mapper._parse_duration('PT2H') == 7200
    
    def test_parse_duration_empty(self, mapper):
        """Test parsing empty duration."""
        assert mapper._parse_duration('') == 0
    
    def test_parse_duration_invalid(self, mapper):
        """Test parsing invalid duration."""
        assert mapper._parse_duration('INVALID') == 0


class TestDetectShort:
    """Tests for _detect_short method."""
    
    def test_detect_short_true(self, mapper):
        """Test detecting a YouTube Short."""
        content_details = {'dimension': '2d'}
        assert mapper._detect_short(duration=50, content_details=content_details) is True
    
    def test_detect_short_false_long_duration(self, mapper):
        """Test that long videos are not Shorts."""
        content_details = {'dimension': '2d'}
        assert mapper._detect_short(duration=120, content_details=content_details) is False
    
    def test_detect_short_boundary(self, mapper):
        """Test Short detection at 60 second boundary."""
        content_details = {'dimension': '2d'}
        assert mapper._detect_short(duration=60, content_details=content_details) is True
        assert mapper._detect_short(duration=61, content_details=content_details) is False


class TestToVideoMetadataDict:
    """Tests for to_video_metadata_dict method."""
    
    def test_to_video_metadata_dict(self, mapper):
        """Test converting YouTubeVideo to metadata dict."""
        youtube_video = YouTubeVideo(
            video_id='abc123',
            title='Test Video',
            description='Test desc',
            channel_id='UC123',
            channel_title='Test Channel',
            duration=300,
            view_count=1000,
            like_count=100,
            comment_count=10,
            tags=['python'],
            is_short=False,
            is_live=False,
            thumbnails={'high': 'https://example.com/thumb.jpg'}
        )
        
        metadata = mapper.to_video_metadata_dict(youtube_video)
        
        assert metadata['platform'] == 'youtube'
        assert metadata['video_id'] == 'abc123'
        assert metadata['title'] == 'Test Video'
        assert metadata['url'] == 'https://www.youtube.com/watch?v=abc123'
        assert metadata['duration_seconds'] == 300
        assert metadata['view_count'] == 1000
        assert metadata['thumbnail_url'] == 'https://example.com/thumb.jpg'


class TestParseChannel:
    """Tests for parse_channel method."""
    
    def test_parse_channel(self, mapper):
        """Test parsing channel response."""
        response = {
            'id': 'UC123',
            'snippet': {
                'title': 'Test Channel',
                'description': 'Channel desc',
                'customUrl': '@testchannel',
                'publishedAt': '2020-01-01T00:00:00Z',
                'thumbnails': {'default': {'url': 'https://example.com/thumb.jpg'}}
            },
            'statistics': {
                'subscriberCount': '10000',
                'videoCount': '500',
                'viewCount': '1000000'
            },
            'contentDetails': {
                'relatedPlaylists': {'uploads': 'UU123'}
            }
        }
        
        channel = mapper.parse_channel(response)
        
        assert isinstance(channel, YouTubeChannel)
        assert channel.channel_id == 'UC123'
        assert channel.title == 'Test Channel'
        assert channel.subscriber_count == 10000
        assert channel.uploads_playlist_id == 'UU123'


class TestParseSearchResult:
    """Tests for parse_search_result method."""
    
    def test_parse_search_result(self, mapper):
        """Test parsing search result."""
        response = {
            'id': {'videoId': 'abc123'},
            'snippet': {
                'title': 'Test Video',
                'description': 'Desc',
                'channelId': 'UC123',
                'channelTitle': 'Test Channel',
                'publishedAt': '2024-01-01T00:00:00Z',
                'thumbnails': {'default': {'url': 'https://example.com/thumb.jpg'}}
            }
        }
        
        result = mapper.parse_search_result(response)
        
        assert isinstance(result, YouTubeSearchResult)
        assert result.video_id == 'abc123'
        assert result.title == 'Test Video'
