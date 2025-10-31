"""Base plugin interface for signal scrapers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

# Import IdeaInspiration model from the Model directory
import sys
from pathlib import Path

# Add Model directory to path to import IdeaInspiration
model_path = Path(__file__).resolve().parents[6] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration import IdeaInspiration


class SignalPlugin(ABC):
    """Abstract base class for signal scraper plugins.
    
    Follows the Interface Segregation Principle (ISP) by providing
    a minimal interface that all signal plugins must implement.
    """

    def __init__(self, config):
        """Initialize plugin with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config

    @abstractmethod
    def scrape(self, **kwargs) -> List[IdeaInspiration]:
        """Scrape signals from the source.
        
        Args:
            **kwargs: Source-specific parameters (e.g., keywords, filters)
        
        Returns:
            List of IdeaInspiration objects representing signals
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name (e.g., 'google_trends', 'tiktok_hashtag')
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
