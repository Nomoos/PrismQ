"""Base plugin interface for HackerNews source scrapers."""

# Import IdeaInspiration model from the Model directory
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

# Add Model directory to path to import IdeaInspiration
model_path = Path(__file__).resolve().parents[6] / "Model"
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration import IdeaInspiration


class SourcePlugin(ABC):
    """Abstract base class for source scraper plugins.

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
        """Scrape ideas from the source.

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


# Will be imported after concrete implementations are defined
__all__ = ["SourcePlugin"]
