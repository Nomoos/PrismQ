"""Plugin base class for ScriptBeatsSource."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SourcePlugin(ABC):
    """Abstract base class for source plugins."""

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
    def scrape(self) -> List[Dict[str, Any]]:
        """Scrape creative resources from the source.
        
        Returns:
            List of resource dictionaries
        """
        pass
