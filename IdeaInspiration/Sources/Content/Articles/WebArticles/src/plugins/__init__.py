"""Base plugin interface for article scraper plugins."""

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



class SourcePlugin(ABC):
    """Abstract base class for article scraper plugins.
    
    Follows the Interface Segregation Principle (ISP) by providing
    a minimal interface that all source plugins must implement.
    """

    def __init__(self, config):
        """Initialize plugin with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config

    @abstractmethod
    def scrape(self, **kwargs) -> List[IdeaInspiration]:
        """Scrape articles from the source.
        
        Returns:
            List of IdeaInspiration objects
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
from .article_url import ArticleUrlPlugin
from .article_rss import ArticleRssPlugin
from .article_sitemap import ArticleSitemapPlugin

__all__ = [
    "SourcePlugin",
    "ArticleUrlPlugin",
    "ArticleRssPlugin",
    "ArticleSitemapPlugin",
]
