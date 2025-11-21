"""Worker factory for creating worker instances using TaskManager API.

Following Open/Closed Principle (OCP) - new workers can be registered
without modifying the factory logic.

Note: This factory creates workers that use pure TaskManager API pattern.
No local queue database is used.
"""

from typing import Dict, Type
from .base_worker import BaseWorker
from ..core.config import Config


class WorkerFactory:
    """Factory for creating worker instances (Factory Pattern).
    
    Follows Open/Closed Principle (OCP):
    - Open for extension: New workers can be registered
    - Closed for modification: Factory logic remains stable
    
    Workers created by this factory use TaskManager API for task management.
    """
    
    def __init__(self):
        """Initialize the worker factory with default workers."""
        self._worker_types: Dict[str, Type[BaseWorker]] = {}
        
        # Register default workers (lazy import to avoid dependency issues)
        self._register_default_workers()
    
    def _register_default_workers(self):
        """Register default worker types with lazy import."""
        # Import RedditSubredditWorker lazily to avoid import errors
        # when IdeaInspiration model is not available
        try:
            from .reddit_subreddit_worker import RedditSubredditWorker
            self.register('reddit_subreddit', RedditSubredditWorker)
        except ImportError:
            # If import fails (e.g., during testing), workers can be registered later
            pass
    
    def register(self, worker_type: str, worker_class: Type[BaseWorker]):
        """Register a worker class for a worker type.
        
        Args:
            worker_type: Worker type identifier
            worker_class: Worker class to instantiate
        """
        self._worker_types[worker_type] = worker_class
    
    def create(
        self,
        worker_type: str,
        worker_id: str,
        config: Config,
        **kwargs
    ) -> BaseWorker:
        """Create a worker instance for a worker type.
        
        Args:
            worker_type: Type of worker to create
            worker_id: Unique worker identifier
            config: Configuration object
            **kwargs: Additional worker arguments
            
        Returns:
            Worker instance
            
        Raises:
            ValueError: If worker type not registered
        """
        if worker_type not in self._worker_types:
            raise ValueError(
                f"Unknown worker type: {worker_type}. "
                f"Registered types: {', '.join(self.get_supported_types())}"
            )
        
        worker_class = self._worker_types[worker_type]
        return worker_class(
            worker_id=worker_id,
            config=config,
            **kwargs
        )
    
    def get_supported_types(self) -> list:
        """Get list of supported worker types.
        
        Returns:
            List of registered worker type identifiers
        """
        return list(self._worker_types.keys())


# Global factory instance
worker_factory = WorkerFactory()


__all__ = ["WorkerFactory", "worker_factory"]
