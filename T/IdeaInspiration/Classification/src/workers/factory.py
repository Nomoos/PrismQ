"""Worker factory for creating classification worker instances.

Following Open/Closed Principle (OCP) - new workers can be registered
without modifying the factory logic.
"""

from typing import Dict, Type, Any
import logging

logger = logging.getLogger(__name__)


class WorkerFactory:
    """Factory for creating worker instances (Factory Pattern).
    
    Follows Open/Closed Principle (OCP):
    - Open for extension: New workers can be registered
    - Closed for modification: Factory logic remains stable
    """
    
    def __init__(self):
        """Initialize the worker factory with default workers."""
        self._worker_types: Dict[str, Type] = {}
        
        # Register default workers (lazy import to avoid dependency issues)
        self._register_default_workers()
    
    def _register_default_workers(self):
        """Register default worker types with lazy import."""
        try:
            from .classification_worker import ClassificationWorker
            self.register('classification_enrich', ClassificationWorker)
            self.register('classification_batch', ClassificationWorker)
        except ImportError as e:
            logger.warning(f"Failed to register default workers: {e}")
    
    def register(self, task_type: str, worker_class: Type):
        """Register a worker class for a task type.
        
        Args:
            task_type: Task type identifier
            worker_class: Worker class to handle this task type
        """
        self._worker_types[task_type] = worker_class
        logger.debug(f"Registered worker for task type: {task_type}")
    
    def create(
        self,
        task_type: str,
        worker_id: str,
        **kwargs: Any
    ):
        """Create a worker instance for a task type.
        
        Args:
            task_type: Type of task to handle
            worker_id: Unique worker identifier
            **kwargs: Additional worker arguments
            
        Returns:
            Worker instance
            
        Raises:
            ValueError: If task type not registered
        """
        if task_type not in self._worker_types:
            raise ValueError(
                f"Unknown task type: {task_type}. "
                f"Registered types: {', '.join(self.get_supported_types())}"
            )
        
        worker_class = self._worker_types[task_type]
        return worker_class(
            worker_id=worker_id,
            **kwargs
        )
    
    def get_supported_types(self) -> list:
        """Get list of supported task types.
        
        Returns:
            List of registered task type identifiers
        """
        return list(self._worker_types.keys())


# Global factory instance
worker_factory = WorkerFactory()


__all__ = ["WorkerFactory", "worker_factory"]
