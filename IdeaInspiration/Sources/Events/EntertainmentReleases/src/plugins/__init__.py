"""Plugin base class for EntertainmentReleases source."""

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
    """Base class for entertainment release source plugins."""

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
    def scrape(self, **kwargs) -> List[IdeaInspiration]:
        """Scrape events from the source.
        
        Args:
            **kwargs: Keyword arguments specific to each plugin
        
        Returns:
            List of event dictionaries
        """
        pass
