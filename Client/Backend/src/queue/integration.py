"""
Integration utilities for queue system.

Provides helper functions and utilities for integrating the queue system
with existing code and facilitating migration from BackgroundTaskManager.
"""

import logging
from typing import Optional
from pathlib import Path

from .database import QueueDatabase
from .task_handler_registry import TaskHandlerRegistry, get_global_registry

logger = logging.getLogger(__name__)


def create_queue_database(db_path: Optional[str] = None) -> QueueDatabase:
    """
    Create and initialize a queue database instance.
    
    Args:
        db_path: Path to database file. If None, uses default path.
        
    Returns:
        Initialized QueueDatabase instance
        
    Example:
        >>> db = create_queue_database()
        >>> # Database is ready to use
    """
    db = QueueDatabase(db_path)
    db.initialize_schema()
    logger.info(f"Queue database initialized at {db.db_path}")
    return db


def get_or_create_queue_database(db_path: Optional[str] = None) -> QueueDatabase:
    """
    Get existing or create new queue database instance (singleton pattern).
    
    This is useful for ensuring a single database instance is shared
    across the application.
    
    Args:
        db_path: Path to database file. If None, uses default path.
        
    Returns:
        QueueDatabase instance
    """
    # Simple singleton implementation
    if not hasattr(get_or_create_queue_database, '_instance'):
        get_or_create_queue_database._instance = create_queue_database(db_path)
    return get_or_create_queue_database._instance


def create_queued_task_manager(queue_db: Optional[QueueDatabase] = None, registry=None):
    """
    Create a QueuedTaskManager adapter instance.
    
    This is a convenience function that creates all necessary components
    for using the queue-based task manager.
    
    Args:
        queue_db: Optional QueueDatabase instance. If None, creates new one.
        registry: Optional RunRegistry instance. If None, uses default.
        
    Returns:
        QueuedTaskManager instance ready to use
        
    Example:
        >>> from src.queue.integration import create_queued_task_manager
        >>> 
        >>> manager = create_queued_task_manager()
        >>> 
        >>> # Register handlers
        >>> await manager.register_task("cleanup", cleanup_handler)
        >>> 
        >>> # Schedule tasks
        >>> task_id = await manager.schedule_task("cleanup", {"max_age": 24})
    """
    from ..core.queued_task_manager import QueuedTaskManager
    from ..core.run_registry import RunRegistry
    
    if queue_db is None:
        queue_db = get_or_create_queue_database()
    
    if registry is None:
        # Use default RunRegistry
        registry = RunRegistry()
    
    manager = QueuedTaskManager(queue_db, registry)
    logger.info("QueuedTaskManager created and ready to use")
    return manager


def migrate_to_queue_system(
    existing_manager,
    queue_db: Optional[QueueDatabase] = None,
    registry=None
):
    """
    Helper function to migrate from BackgroundTaskManager to QueuedTaskManager.
    
    This function doesn't actually replace the manager in-place, but returns
    a new QueuedTaskManager instance that can be used as a drop-in replacement.
    
    Args:
        existing_manager: Current BackgroundTaskManager instance
        queue_db: Optional QueueDatabase instance
        registry: Optional RunRegistry instance
        
    Returns:
        QueuedTaskManager instance configured with same registry
        
    Example:
        >>> # Old code
        >>> old_manager = BackgroundTaskManager(registry)
        >>> 
        >>> # Migrate
        >>> new_manager = migrate_to_queue_system(old_manager)
        >>> 
        >>> # new_manager can now be used instead of old_manager
        >>> # Same API, but backed by queue system
    """
    if registry is None:
        # Try to get registry from existing manager
        if hasattr(existing_manager, 'registry'):
            registry = existing_manager.registry
    
    return create_queued_task_manager(queue_db, registry)


def validate_queue_integration() -> dict:
    """
    Validate that the queue system is properly set up and accessible.
    
    Returns:
        Dictionary with validation results:
        - 'success': bool - Whether validation passed
        - 'database': bool - Whether database is accessible
        - 'schema': bool - Whether schema is initialized
        - 'errors': list - Any errors encountered
        
    Example:
        >>> from src.queue.integration import validate_queue_integration
        >>> 
        >>> result = validate_queue_integration()
        >>> if result['success']:
        ...     print("Queue system ready!")
        ... else:
        ...     print(f"Errors: {result['errors']}")
    """
    errors = []
    database_ok = False
    schema_ok = False
    
    try:
        # Try to create database
        db = QueueDatabase()
        database_ok = True
        
        # Try to initialize schema
        db.initialize_schema()
        schema_ok = True
        
        # Try a simple query
        cursor = db.execute("SELECT COUNT(*) FROM task_queue")
        cursor.fetchone()
        
        db.close()
        
    except Exception as e:
        errors.append(str(e))
        logger.error(f"Queue integration validation failed: {e}")
    
    success = database_ok and schema_ok and len(errors) == 0
    
    return {
        'success': success,
        'database': database_ok,
        'schema': schema_ok,
        'errors': errors
    }


class QueueIntegrationError(Exception):
    """Raised when queue integration encounters an error."""
    pass


def ensure_queue_ready(db_path: Optional[str] = None) -> QueueDatabase:
    """
    Ensure queue system is ready for use, or raise an exception.
    
    This function validates the queue system and raises an exception
    if there are any problems.
    
    Args:
        db_path: Optional path to database file
        
    Returns:
        Ready-to-use QueueDatabase instance
        
    Raises:
        QueueIntegrationError: If queue system is not ready
        
    Example:
        >>> try:
        ...     db = ensure_queue_ready()
        ...     # Queue system is ready
        ... except QueueIntegrationError as e:
        ...     print(f"Queue not ready: {e}")
    """
    try:
        db = QueueDatabase(db_path)
        db.initialize_schema()
        
        # Verify schema
        cursor = db.execute("SELECT COUNT(*) FROM task_queue")
        cursor.fetchone()
        
        logger.info("Queue system is ready")
        return db
        
    except Exception as e:
        raise QueueIntegrationError(f"Queue system initialization failed: {e}") from e


__all__ = [
    'create_queue_database',
    'get_or_create_queue_database',
    'create_queued_task_manager',
    'migrate_to_queue_system',
    'validate_queue_integration',
    'ensure_queue_ready',
    'QueueIntegrationError',
]
