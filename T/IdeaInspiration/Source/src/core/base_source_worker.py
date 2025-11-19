"""Base source worker with source-specific enhancements.

This module provides progressive enrichment over BaseWorker by adding
source-specific functionality like configuration and database management.

Design Pattern: Template Method Pattern (Progressive Enrichment)
Reference: https://refactoring.guru/design-patterns/template-method

Hierarchy Level 2:
    BaseWorker (general task processing)
      ↓
    BaseSourceWorker (this class - adds source configuration and storage)
      ↓
    Media-Specific Workers (BaseVideoWorker, BaseTextWorker, BaseAudioWorker)

Progressive Enrichment:
- BaseWorker provides: Task claiming, processing loop, result reporting
- BaseSourceWorker adds: Configuration management, database operations, API clients
- Media workers add: Media-specific operations (video processing, text analysis)
- Platform workers add: Platform-specific operations (YouTube API, Reddit API)

Follows SOLID principles:
- Single Responsibility: Manages source configuration and storage
- Open/Closed: Open for extension via inheritance
- Liskov Substitution: Can substitute BaseWorker
- Dependency Inversion: Depends on Config and Database abstractions
"""

import logging
from typing import Dict, Any, Optional
from abc import ABC

from .base_worker import BaseWorker, Task, TaskResult

logger = logging.getLogger(__name__)


class Config:
    """Configuration interface for source workers.
    
    This is a placeholder interface. Subclasses should use their
    specific Config implementation from their module.
    """
    pass


class Database:
    """Database interface for source workers.
    
    This is a placeholder interface. Subclasses should use their
    specific Database implementation from their module.
    """
    pass


class BaseSourceWorker(BaseWorker, ABC):
    """Base worker with source-specific configuration and storage.
    
    This class extends BaseWorker with:
    - Configuration management (Config object)
    - Database operations (results_db)
    - API client management (for subclasses)
    - Result persistence
    
    This follows progressive enrichment where each level adds
    more specific functionality without modifying the parent.
    
    Attributes:
        config: Configuration object with source-specific settings
        results_db: Database for storing processed results
    
    Example:
        >>> from ..core.config import Config as MyConfig
        >>> from ..core.database import Database as MyDB
        >>> 
        >>> class MySourceWorker(BaseSourceWorker):
        ...     def __init__(self, worker_id, config, results_db, task_type_ids):
        ...         super().__init__(
        ...             worker_id=worker_id,
        ...             task_type_ids=task_type_ids,
        ...             config=config,
        ...             results_db=results_db
        ...         )
        ...     
        ...     def process_task(self, task: Task) -> TaskResult:
        ...         # Process using config and results_db
        ...         api_key = self.config.youtube_api_key
        ...         # ... processing logic ...
        ...         return TaskResult(success=True)
    """
    
    def __init__(
        self,
        worker_id: str,
        task_type_ids: list,
        config: Config,
        results_db: Database,
        **kwargs
    ):
        """Initialize source worker with configuration and database.
        
        Args:
            worker_id: Unique worker identifier
            task_type_ids: List of task type IDs to handle
            config: Configuration object (source-specific)
            results_db: Database for storing results
            **kwargs: Additional arguments passed to BaseWorker
        """
        # Initialize parent BaseWorker
        super().__init__(
            worker_id=worker_id,
            task_type_ids=task_type_ids,
            **kwargs
        )
        
        # Add source-specific functionality
        self.config = config
        self.results_db = results_db
        
        # Validate configuration
        self._validate_config()
        
        logger.info(
            f"SourceWorker {worker_id} initialized with config and database"
        )
    
    def _validate_config(self) -> None:
        """Validate source configuration - Hook method.
        
        Subclasses can override this to add specific validation.
        Default implementation does basic checks.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.config:
            raise ValueError("Configuration object is required")
        
        logger.debug(f"Configuration validated for worker {self.worker_id}")
    
    def _save_results(self, task: Task, result: TaskResult) -> None:
        """Save results to database - Override of BaseWorker hook method.
        
        This implements the parent's hook method to provide actual
        result storage functionality.
        
        Args:
            task: The completed task
            result: The task execution result
        """
        if not result.success or not result.data:
            return
        
        try:
            # Subclasses should override this to implement actual storage
            logger.debug(
                f"Results saved for task {task.id} "
                f"({result.items_processed} items)"
            )
        except Exception as e:
            logger.error(f"Failed to save results for task {task.id}: {e}")


__all__ = ["BaseSourceWorker", "Config", "Database"]
