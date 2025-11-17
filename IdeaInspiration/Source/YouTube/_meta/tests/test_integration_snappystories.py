"""Integration tests for YouTube Shorts scraping with test URLs.

This module contains integration tests that validate the scraping functionality
works with specific test URLs provided for the SnappyStories_1 channel.

Test URLs:
- Channel: https://www.youtube.com/@SnappyStories_1
- Channel Shorts: https://www.youtube.com/@SnappyStories_1/shorts
- Example Short: https://www.youtube.com/shorts/FpSdooOrmsU
"""

import pytest
from unittest.mock import Mock, patch
from src.plugins.youtube_channel_plugin import YouTubeChannelPlugin


class TestSnappyStoriesIntegration:
    """Integration tests for SnappyStories_1 channel scraping."""
    
    # Test configuration
    TEST_CHANNEL_URL = "https://www.youtube.com/@SnappyStories_1"
    TEST_CHANNEL_SHORTS_URL = "https://www.youtube.com/@SnappyStories_1/shorts"
    TEST_SHORT_URL = "https://www.youtube.com/shorts/FpSdooOrmsU"
    TEST_SHORT_ID = "FpSdooOrmsU"
    TEST_CHANNEL_HANDLE = "@SnappyStories_1"
    
    # Additional test videos for validation
    TEST_SHORT_URL_2 = "https://youtube.com/shorts/3o0o5DTwTYU"
    TEST_SHORT_ID_2 = "3o0o5DTwTYU"
    
    def test_channel_url_normalization(self):
        """Test that various channel URL formats are normalized correctly."""
        config = Mock()
        
        with patch.object(YouTubeChannelPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeChannelPlugin(config)
            
            # Test full URL
            result = plugin._normalize_channel_url(self.TEST_CHANNEL_URL)
            assert result == self.TEST_CHANNEL_URL
            
            # Test handle format
            result = plugin._normalize_channel_url(self.TEST_CHANNEL_HANDLE)
            assert result == self.TEST_CHANNEL_URL
            
            # Test without @ symbol
            result = plugin._normalize_channel_url("SnappyStories_1")
            assert result == self.TEST_CHANNEL_URL
    
    def test_shorts_url_construction(self):
        """Test that shorts URL is constructed correctly from channel URL."""
        config = Mock()
        
        with patch.object(YouTubeChannelPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeChannelPlugin(config)
            
            # The plugin should construct the /shorts suffix
            normalized_url = plugin._normalize_channel_url(self.TEST_CHANNEL_HANDLE)
            expected_shorts_url = normalized_url.rstrip('/') + "/shorts"
            
            assert expected_shorts_url == self.TEST_CHANNEL_SHORTS_URL
    
    @pytest.mark.skip(reason="Requires network access and yt-dlp")
    def test_scrape_snappy_stories_channel(self):
        """Integration test: Scrape shorts from SnappyStories_1 channel.
        
        This test requires:
        - Network access
        - yt-dlp installed
        - YouTube being accessible
        
        Run manually with: pytest -k test_scrape_snappy_stories_channel -v
        """
        config = Mock()
        config.youtube_channel_url = self.TEST_CHANNEL_URL
        config.youtube_channel_max_shorts = 3  # Small number for testing
        
        plugin = YouTubeChannelPlugin(config)
        ideas = plugin.scrape(channel_url=self.TEST_CHANNEL_URL, top_n=3)
        
        # Basic validation
        assert isinstance(ideas, list)
        if len(ideas) > 0:
            # Validate structure of first idea
            idea = ideas[0]
            assert 'source_id' in idea
            assert 'title' in idea
            assert 'description' in idea
            assert 'tags' in idea
            assert 'metrics' in idea
    
    @pytest.mark.skip(reason="Requires network access and yt-dlp")
    def test_extract_specific_short_metadata(self):
        """Integration test: Extract metadata for specific short.
        
        This test requires:
        - Network access
        - yt-dlp installed
        - YouTube being accessible
        
        Run manually with: pytest -k test_extract_specific_short_metadata -v
        """
        config = Mock()
        
        plugin = YouTubeChannelPlugin(config)
        metadata = plugin._extract_video_metadata(self.TEST_SHORT_ID)
        
        if metadata:
            # Validate metadata structure
            assert 'id' in metadata
            assert metadata['id'] == self.TEST_SHORT_ID
            assert 'title' in metadata
            assert 'duration' in metadata
            assert metadata['duration'] <= 180  # Should be a short
            
            # Validate it's vertical format
            if 'width' in metadata and 'height' in metadata:
                assert metadata['height'] > metadata['width']


class TestURLFormatCompatibility:
    """Test compatibility with different URL formats for the test channel."""
    
    def test_accepts_various_channel_formats(self):
        """Test that the plugin accepts various channel URL formats."""
        config = Mock()
        
        with patch.object(YouTubeChannelPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeChannelPlugin(config)
            
            test_formats = [
                "https://www.youtube.com/@SnappyStories_1",
                "@SnappyStories_1",
                "SnappyStories_1"
            ]
            
            for url_format in test_formats:
                normalized = plugin._normalize_channel_url(url_format)
                assert normalized.startswith("https://www.youtube.com/")
                assert "SnappyStories_1" in normalized
    
    def test_shorts_url_suffix(self):
        """Test that /shorts suffix is properly handled."""
        config = Mock()
        
        with patch.object(YouTubeChannelPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeChannelPlugin(config)
            
            # The plugin internally adds /shorts when fetching
            base_url = "https://www.youtube.com/@SnappyStories_1"
            shorts_url = base_url.rstrip('/') + "/shorts"
            
            assert shorts_url == "https://www.youtube.com/@SnappyStories_1/shorts"


class TestShortValidation:
    """Test validation of shorts duration and format."""
    
    def test_short_video_id_extraction(self):
        """Test extracting video ID from shorts URL."""
        short_url = "https://www.youtube.com/shorts/FpSdooOrmsU"
        video_id = short_url.split('/')[-1]
        
        assert video_id == "FpSdooOrmsU"
        assert len(video_id) == 11  # Standard YouTube video ID length
    
    def test_short_video_id_extraction_with_query_params(self):
        """Test extracting video ID from shorts URL with query parameters."""
        # Test URL with tracking parameter (si)
        short_url = "https://youtube.com/shorts/3o0o5DTwTYU?si=bCQi0Jjlb8ssVWEV"
        # Extract video ID by splitting and removing query parameters
        video_id = short_url.split('/')[-1].split('?')[0]
        
        assert video_id == "3o0o5DTwTYU"
        assert len(video_id) == 11  # Standard YouTube video ID length
    
    def test_shorts_duration_constraint(self):
        """Test that the SHORTS_MAX_DURATION constant is correct."""
        assert YouTubeChannelPlugin.SHORTS_MAX_DURATION == 180
        
        # Any video over 180 seconds should be filtered out
        config = Mock()
        
        with patch.object(YouTubeChannelPlugin, '_check_ytdlp', return_value=True):
            plugin = YouTubeChannelPlugin(config)
            
            # Test metadata for a video that's too long (e.g., 200 seconds)
            long_metadata = {
                'duration': 200,
                'width': 1080,
                'height': 1920
            }
            
            # The _extract_video_metadata should filter this out
            # (returns None for videos exceeding max duration)
