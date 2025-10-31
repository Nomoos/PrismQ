"""Base plugin interface for commerce source scrapers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

# Import IdeaInspiration model from the Model directory
import sys
from pathlib import Path

# Add Model directory to path to import IdeaInspiration
# Note: parents[6] assumes specific directory nesting level
# This works for current structure but should be made more robust in production
# Consider: environment variable, setuptools entry points, or relative imports
model_path = Path(__file__).resolve().parents[6] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration import IdeaInspiration


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
    def scrape(self) -> List[IdeaInspiration]:
        """Scrape products from the source.
        
        Returns:
            List of IdeaInspiration objects
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name (e.g., 'amazon_bestsellers')
        """
        pass

    def format_tags(self, tags: List[str]) -> List[str]:
        """Format a list of tags by stripping whitespace.
        
        Args:
            tags: List of tag strings
            
        Returns:
            List of cleaned tag strings
        """
        return [tag.strip() for tag in tags if tag.strip()]


# Export the base class and concrete implementations
from .google_play_plugin import GooglePlayPlugin
from .apple_app_store_plugin import AppleAppStorePlugin

__all__ = [
    "CommercePlugin",
    "GooglePlayPlugin",
    "AppleAppStorePlugin",
]
