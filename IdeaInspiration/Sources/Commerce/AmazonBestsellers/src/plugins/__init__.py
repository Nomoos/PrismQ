"""Base plugin interface for commerce source scrapers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class CommercePlugin(ABC):
    """Abstract base class for commerce scraper plugins.
    
    Follows the Interface Segregation Principle (ISP) by providing
    a minimal interface that all commerce plugins must implement.
    """

    def __init__(self, config):
        """Initialize plugin with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config

    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape products from the source.
        
        Returns:
            List of product dictionaries with standardized fields
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name (e.g., 'amazon_bestsellers')
        """
        pass

    def format_tags(self, tags: List[str]) -> str:
        """Format a list of tags into a comma-separated string.
        
        Args:
            tags: List of tag strings
            
        Returns:
            Comma-separated tag string
        """
        return ",".join(tag.strip() for tag in tags if tag.strip())


# Export the base class and concrete implementations
from .amazon_bestsellers import AmazonBestsellersPlugin

__all__ = [
    "CommercePlugin",
    "AmazonBestsellersPlugin",
]
