# Issue #004: Implement Worker Factory Pattern

**Priority**: High  
**Status**: New  
**Dependencies**: Issues #001, #002, #003  
**Duration**: 2 days

## Objective

Implement a factory pattern for creating and managing Reddit workers dynamically, simplifying worker instantiation and configuration.

## Problem Statement

Currently, workers must be instantiated manually with all dependencies. We need:
- Dynamic worker creation based on task type
- Centralized configuration management
- Worker lifecycle management
- Easy addition of new worker types

## Proposed Solution

### WorkerFactory Implementation

**File**: `Source/Text/Reddit/Posts/src/workers/factory.py` (NEW)

```python
"""Worker factory for creating Reddit workers dynamically.

Following Factory Pattern and SOLID principles.
"""

from typing import Dict, Type, Optional
from workers.base_worker import BaseWorker
from workers.reddit_subreddit_worker import RedditSubredditWorker
from workers.reddit_trending_worker import RedditTrendingWorker
from workers.reddit_search_worker import RedditSearchWorker
from workers.reddit_rising_worker import RedditRisingWorker
from core.config import Config
from core.database import Database


class WorkerFactory:
    """Factory for creating Reddit workers.
    
    Follows Single Responsibility Principle (SRP):
    - Only responsible for worker creation
    - Manages worker registry
    - Handles configuration injection
    
    Follows Open/Closed Principle (OCP):
    - Open for extension (add new workers)
    - Closed for modification (core logic stable)
    """
    
    # Worker registry mapping task types to worker classes
    _WORKER_REGISTRY: Dict[str, Type[BaseWorker]] = {
        'subreddit_scrape': RedditSubredditWorker,
        'trending_scrape': RedditTrendingWorker,
        'search_scrape': RedditSearchWorker,
        'rising_scrape': RedditRisingWorker,
    }
    
    def __init__(self, config: Config, results_db: Database):
        """Initialize worker factory.
        
        Args:
            config: Configuration object
            results_db: Results database
        """
        self.config = config
        self.results_db = results_db
    
    def create_worker(
        self,
        worker_id: str,
        queue_db_path: str,
        task_types: Optional[list[str]] = None,
        strategy: str = "LIFO",
        **kwargs
    ) -> BaseWorker:
        """Create a worker for specified task types.
        
        Args:
            worker_id: Unique worker identifier
            queue_db_path: Path to queue database
            task_types: List of task types to handle (if None, picks first available)
            strategy: Claiming strategy
            **kwargs: Additional worker arguments
            
        Returns:
            Configured worker instance
            
        Raises:
            ValueError: If task type unknown or no workers available
        """
        if task_types is None:
            task_types = list(self._WORKER_REGISTRY.keys())
        
        # For now, pick the first task type and create appropriate worker
        # TODO: Support multi-task-type workers
        if not task_types:
            raise ValueError("At least one task type must be specified")
        
        task_type = task_types[0]
        worker_class = self._WORKER_REGISTRY.get(task_type)
        
        if worker_class is None:
            raise ValueError(
                f"Unknown task type: {task_type}. "
                f"Available: {', '.join(self._WORKER_REGISTRY.keys())}"
            )
        
        # Create worker instance
        return worker_class(
            worker_id=worker_id,
            queue_db_path=queue_db_path,
            config=self.config,
            results_db=self.results_db,
            strategy=strategy,
            **kwargs
        )
    
    @classmethod
    def register_worker(cls, task_type: str, worker_class: Type[BaseWorker]) -> None:
        """Register a new worker type.
        
        Allows extending the factory without modifying it (OCP).
        
        Args:
            task_type: Task type identifier
            worker_class: Worker class to handle this task type
        """
        cls._WORKER_REGISTRY[task_type] = worker_class
    
    @classmethod
    def get_available_task_types(cls) -> list[str]:
        """Get list of available task types.
        
        Returns:
            List of registered task type names
        """
        return list(cls._WORKER_REGISTRY.keys())


def create_worker_for_task_type(
    task_type: str,
    worker_id: str,
    queue_db_path: str,
    config: Config,
    results_db: Database,
    **kwargs
) -> BaseWorker:
    """Convenience function to create a worker for a specific task type.
    
    Args:
        task_type: Task type to handle
        worker_id: Worker identifier
        queue_db_path: Queue database path
        config: Configuration
        results_db: Results database
        **kwargs: Additional worker arguments
        
    Returns:
        Configured worker instance
    """
    factory = WorkerFactory(config, results_db)
    return factory.create_worker(
        worker_id=worker_id,
        queue_db_path=queue_db_path,
        task_types=[task_type],
        **kwargs
    )


__all__ = ['WorkerFactory', 'create_worker_for_task_type']
```

## Acceptance Criteria

- [ ] `WorkerFactory` class implemented
- [ ] Supports all Reddit worker types
- [ ] Easy to register new worker types
- [ ] Centralized configuration injection
- [ ] Tests covering all worker creation paths
- [ ] Documentation complete
- [ ] Example usage provided

## Testing Strategy

```python
def test_factory_creates_subreddit_worker():
    factory = WorkerFactory(config, db)
    worker = factory.create_worker(
        worker_id="test-1",
        queue_db_path="queue.db",
        task_types=["subreddit_scrape"]
    )
    assert isinstance(worker, RedditSubredditWorker)

def test_factory_unknown_task_type():
    factory = WorkerFactory(config, db)
    with pytest.raises(ValueError):
        factory.create_worker(
            worker_id="test-1",
            queue_db_path="queue.db",
            task_types=["unknown_type"]
        )

def test_register_custom_worker():
    WorkerFactory.register_worker("custom_type", CustomWorker)
    assert "custom_type" in WorkerFactory.get_available_task_types()
```

## Implementation Notes

- Factory centralizes worker creation logic
- Makes it easy to add new worker types
- Simplifies configuration management
- Enables dynamic worker scaling
- Foundation for advanced features (auto-scaling, load balancing)

## Usage Example

```python
from workers.factory import WorkerFactory
from core.config import Config
from core.database import Database

# Initialize factory
config = Config()
db = Database(config.database_path)
factory = WorkerFactory(config, db)

# Create worker for subreddit scraping
worker = factory.create_worker(
    worker_id="worker-01",
    queue_db_path="queue.db",
    task_types=["subreddit_scrape"],
    strategy="LIFO"
)

# Run worker
worker.run()
```

## Future Enhancements

- Support workers handling multiple task types
- Auto-scaling based on queue depth
- Worker pool management
- Health monitoring integration

## References

- YouTube Worker Factory: `Source/Video/YouTube/src/workers/factory.py`
- Factory Pattern: Gang of Four Design Patterns
