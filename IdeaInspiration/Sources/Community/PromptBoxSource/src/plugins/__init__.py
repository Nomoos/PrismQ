"""Base plugin interface for community source scrapers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class CommunitySourcePlugin(ABC):
    """Abstract base class for community source scraper plugins.
    
    Follows the Interface Segregation Principle (ISP) by providing
    a minimal interface that all community source plugins must implement.
    """

    def __init__(self, config):
        """Initialize plugin with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config

    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape community signals from the source.
        
        Returns:
            List of community signal dictionaries with keys:
                - source: Community source name
                - source_id: Unique identifier from source
                - content: Dictionary with type, text, title, author
                - context: Dictionary with platform, parent_content, category
                - metrics: Dictionary with engagement metrics
                - analysis: Dictionary with sentiment, topics, intent
                - universal_metrics: Engagement, relevance, actionability scores
        """
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Get the name of this source.
        
        Returns:
            Source name (e.g., 'user_feedback', 'qa')
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


from .form_submission_plugin import FormSubmissionPlugin

__all__ = [
    "CommunitySourcePlugin",
    "FormSubmissionPlugin",
]
