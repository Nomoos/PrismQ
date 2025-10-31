"""Plugin base class for SportsHighlights source."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SourcePlugin(ABC):
    """Base class for sports event source plugins."""

    def __init__(self, config):
        """Initialize plugin with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config

    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name
        """
        pass

    @abstractmethod
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """Scrape events from the source.
        
        Args:
            **kwargs: Keyword arguments specific to each plugin
        
        Returns:
            List of event dictionaries
        """
        pass
