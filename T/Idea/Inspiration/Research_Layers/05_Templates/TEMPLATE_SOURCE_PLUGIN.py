"""
Template for creating a new Source Plugin.

Location: Source/{MediaType}/{Platform}/{Endpoint}/src/plugins/

Usage:
1. Copy this template
2. Rename to {platform}_{endpoint}_plugin.py
3. Replace all {PLACEHOLDERS}
4. Implement the abstract methods
5. Write tests in tests/plugins/test_{platform}_{endpoint}_plugin.py

Example:
- File: Source/Video/YouTube/Channel/src/plugins/youtube_channel_plugin.py
- Class: YouTubeChannelPlugin
"""

from typing import List, Optional
from Model import IdeaInspiration
from EnvLoad import Config
from Source.{MediaType}.src.plugins import {MediaType}Plugin  # e.g., VideoPlugin


class {Platform}{Endpoint}Plugin({MediaType}Plugin):
    """{Platform} {endpoint} scraper plugin.
    
    This plugin fetches {description of what it fetches} from {Platform}
    and converts them to IdeaInspiration objects.
    
    Follows SOLID principles:
    - Single Responsibility: Only handles {Platform} {endpoint} scraping
    - Dependency Inversion: Depends on injected Config
    - Interface Segregation: Implements minimal SourcePlugin interface
    
    Attributes:
        config: Configuration object with API keys and settings
        api_key: {Platform} API key from config
        {other_attributes}: Description
    
    Example:
        >>> config = Config()
        >>> plugin = {Platform}{Endpoint}Plugin(config)
        >>> ideas = plugin.scrape()
        >>> print(f"Scraped {len(ideas)} ideas")
    """
    
    def __init__(self, config: Config):
        """Initialize plugin with configuration.
        
        Args:
            config: Configuration object containing API keys and settings
                   Must include {platform}_api_key
        
        Raises:
            ConfigError: If required configuration is missing
        """
        super().__init__(config)
        self.config = config
        
        # Get API credentials from config (injected dependency)
        self.api_key = config.{platform}_api_key
        if not self.api_key:
            raise ValueError("{Platform} API key not configured")
        
        # Initialize any other attributes
        self.{endpoint_name} = config.{endpoint_config_key}
    
    def scrape(self) -> List[IdeaInspiration]:
        """Scrape ideas from {Platform} {endpoint}.
        
        This method:
        1. Fetches data from {Platform} API
        2. Parses the response
        3. Converts each item to IdeaInspiration
        
        Returns:
            List of IdeaInspiration objects, one per {item}
            Empty list if no {items} found
        
        Raises:
            APIError: If {Platform} API request fails
            ValueError: If response format is invalid
            
        Example:
            >>> plugin = {Platform}{Endpoint}Plugin(config)
            >>> ideas = plugin.scrape()
            >>> assert all(isinstance(idea, IdeaInspiration) for idea in ideas)
        """
        try:
            # Step 1: Fetch from API
            raw_data = self._fetch_from_api()
            
            # Step 2: Parse and validate
            items = self._parse_response(raw_data)
            
            # Step 3: Convert to IdeaInspiration
            ideas = []
            for item in items:
                try:
                    idea = self._convert_to_idea(item)
                    ideas.append(idea)
                except Exception as e:
                    # Log but don't fail entire scrape
                    self.logger.warning(f"Failed to convert item: {e}")
            
            self.logger.info(f"Scraped {len(ideas)} ideas from {Platform} {endpoint}")
            return ideas
            
        except Exception as e:
            self.logger.error(f"Failed to scrape {Platform} {endpoint}: {e}")
            raise
    
    def get_source_name(self) -> str:
        """Get source identifier for this plugin.
        
        Returns:
            String identifier in format: {platform}_{endpoint}
            
        Example:
            >>> plugin.get_source_name()
            '{platform}_{endpoint}'
        """
        return "{platform}_{endpoint}"
    
    # Private helper methods (internal implementation)
    
    def _fetch_from_api(self) -> dict:
        """Fetch raw data from {Platform} API.
        
        Returns:
            Raw API response as dictionary
            
        Raises:
            APIError: If request fails
        """
        # TODO: Implement API call
        # Example:
        # response = requests.get(
        #     f"{API_BASE_URL}/{endpoint}",
        #     headers={"Authorization": f"Bearer {self.api_key}"},
        #     params={...}
        # )
        # response.raise_for_status()
        # return response.json()
        pass
    
    def _parse_response(self, raw_data: dict) -> List[dict]:
        """Parse API response and extract items.
        
        Args:
            raw_data: Raw API response
            
        Returns:
            List of parsed items
            
        Raises:
            ValueError: If response format is invalid
        """
        # TODO: Implement parsing
        # Example:
        # if 'items' not in raw_data:
        #     raise ValueError("Invalid response format")
        # return raw_data['items']
        pass
    
    def _convert_to_idea(self, item: dict) -> IdeaInspiration:
        """Convert API item to IdeaInspiration.
        
        Args:
            item: Single item from API response
            
        Returns:
            IdeaInspiration object
            
        Raises:
            ValueError: If required fields are missing
        """
        # TODO: Implement conversion
        # Example:
        # return IdeaInspiration(
        #     id=f"{platform}-{item['id']}",
        #     source=self.get_source_name(),
        #     platform="{platform}",
        #     title=item['title'],
        #     description=item.get('description'),
        #     url=item['url'],
        #     created_at=self._parse_date(item['created_at']),
        #     collected_at=datetime.now(),
        #     # Add media-specific fields
        #     {media_specific_fields}
        # )
        pass


# Testing Template
"""
Create tests/plugins/test_{platform}_{endpoint}_plugin.py:

import pytest
from unittest.mock import Mock, patch
from {module}.plugins.{platform}_{endpoint}_plugin import {Platform}{Endpoint}Plugin
from Model import IdeaInspiration
from EnvLoad import Config


class Test{Platform}{Endpoint}Plugin:
    '''Tests for {Platform}{Endpoint}Plugin.'''
    
    @pytest.fixture
    def config(self):
        '''Provide test configuration.'''
        config = Mock(spec=Config)
        config.{platform}_api_key = 'test_key'
        config.{endpoint_config_key} = 'test_value'
        return config
    
    @pytest.fixture
    def plugin(self, config):
        '''Provide plugin instance.'''
        return {Platform}{Endpoint}Plugin(config)
    
    def test_scrape_returns_list_of_ideas(self, plugin):
        '''scrape() returns list of IdeaInspiration objects.'''
        # Arrange
        mock_data = {...}  # Mock API response
        
        # Act
        with patch.object(plugin, '_fetch_from_api', return_value=mock_data):
            ideas = plugin.scrape()
        
        # Assert
        assert isinstance(ideas, list)
        assert all(isinstance(idea, IdeaInspiration) for idea in ideas)
    
    def test_scrape_handles_empty_response(self, plugin):
        '''scrape() handles empty API response.'''
        # Arrange
        mock_data = {'items': []}
        
        # Act
        with patch.object(plugin, '_fetch_from_api', return_value=mock_data):
            ideas = plugin.scrape()
        
        # Assert
        assert ideas == []
    
    def test_scrape_raises_on_api_error(self, plugin):
        '''scrape() raises APIError when API call fails.'''
        # Arrange
        with patch.object(plugin, '_fetch_from_api', side_effect=Exception("API Error")):
            # Act & Assert
            with pytest.raises(Exception):
                plugin.scrape()
    
    def test_get_source_name_returns_correct_identifier(self, plugin):
        '''get_source_name() returns correct source identifier.'''
        # Act
        name = plugin.get_source_name()
        
        # Assert
        assert name == "{platform}_{endpoint}"
    
    def test_convert_to_idea_creates_valid_idea(self, plugin):
        '''_convert_to_idea() creates valid IdeaInspiration.'''
        # Arrange
        item = {...}  # Mock item data
        
        # Act
        idea = plugin._convert_to_idea(item)
        
        # Assert
        assert isinstance(idea, IdeaInspiration)
        assert idea.id is not None
        assert idea.source == "{platform}_{endpoint}"
        assert idea.platform == "{platform}"
"""
