"""Worker factory for creating worker instances.

Following Open/Closed Principle (OCP) - new workers can be registered
without modifying the factory logic.
"""

from typing import Dict, Type

from ..core.config import Config
from ..core.database import Database
from .base_worker import BaseWorker
from .youtube_video_worker import YouTubeVideoWorker


class WorkerFactory:
    """Factory for creating worker instances (Factory Pattern).

    Follows Open/Closed Principle (OCP):
    - Open for extension: New workers can be registered
    - Closed for modification: Factory logic remains stable
    """

    def __init__(self):
        """Initialize the worker factory with default workers."""
        self._worker_types: Dict[str, Type[BaseWorker]] = {}

        # Register default workers
        self.register("youtube_video_single", YouTubeVideoWorker)
        self.register("youtube_video_search", YouTubeVideoWorker)

    def register(self, task_type: str, worker_class: Type[BaseWorker]):
        """Register a worker class for a task type.

        Args:
            task_type: Task type identifier
            worker_class: Worker class to handle this task type
        """
        self._worker_types[task_type] = worker_class

    def create(
        self,
        task_type: str,
        worker_id: str,
        config: Config,
        results_db: Database,
        task_type_ids: list,
        **kwargs,
    ) -> BaseWorker:
        """Create a worker instance for a task type.

        Args:
            task_type: Type of task to handle (for internal routing)
            worker_id: Unique worker identifier
            config: Configuration
            results_db: Results database
            task_type_ids: List of TaskManager API task type IDs (required)
            **kwargs: Additional worker arguments

        Returns:
            Worker instance

        Raises:
            ValueError: If task type not registered or required parameters missing
        """
        if task_type not in self._worker_types:
            raise ValueError(
                f"Unknown task type: {task_type}. "
                f"Registered types: {', '.join(self.get_supported_types())}"
            )

        worker_class = self._worker_types[task_type]
        return worker_class(
            worker_id=worker_id,
            config=config,
            results_db=results_db,
            task_type_ids=task_type_ids,
            **kwargs,
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
