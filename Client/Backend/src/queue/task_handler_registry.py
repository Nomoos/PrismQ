"""
Task Handler Registry for managing registered task handlers.

Implements Worker 10 Issue #339: Ensure Client takes only registered task handlers.
Prevents automatic module discovery from database - only explicitly registered
handlers can process tasks.

Part of: Worker 10 (Integration Specialist) - Queue Integration
"""

from typing import Dict, Callable, Optional, Set, Any
from dataclasses import dataclass
import logging
from threading import RLock

from .models import Task
from .exceptions import QueueDatabaseError


logger = logging.getLogger(__name__)


class TaskHandlerNotRegisteredError(Exception):
    """Raised when attempting to process a task without a registered handler."""
    pass


class TaskHandlerAlreadyRegisteredError(Exception):
    """Raised when attempting to register a handler that already exists."""
    pass


@dataclass
class TaskHandlerInfo:
    """
    Information about a registered task handler.
    
    Attributes:
        task_type: Type of task this handler processes
        handler: Callable that processes the task
        description: Human-readable description of what this handler does
        version: Handler version for tracking
    """
    task_type: str
    handler: Callable[[Task], None]
    description: str = ""
    version: str = "1.0.0"


class TaskHandlerRegistry:
    """
    Registry for managing task handlers.
    
    Ensures that only explicitly registered handlers can process tasks.
    Prevents automatic discovery of task types from the database.
    
    Follows SOLID principles:
    - Single Responsibility: Manages task handler registration only
    - Open/Closed: Can be extended with new handler types without modification
    - Dependency Inversion: Handlers depend on Task abstraction
    
    Thread-safe: Uses RLock to protect concurrent access
    
    Usage:
        >>> registry = TaskHandlerRegistry()
        >>> 
        >>> # Register a handler
        >>> def my_handler(task: Task):
        ...     print(f"Processing {task.type}")
        >>> 
        >>> registry.register_handler("my_task_type", my_handler, "Processes my tasks")
        >>> 
        >>> # Get handler for a task
        >>> handler = registry.get_handler("my_task_type")
        >>> handler(task)
    """
    
    def __init__(self):
        """Initialize the task handler registry."""
        self._handlers: Dict[str, TaskHandlerInfo] = {}
        self._lock = RLock()
        logger.info("TaskHandlerRegistry initialized")
    
    def register_handler(
        self,
        task_type: str,
        handler: Callable[[Task], None],
        description: str = "",
        version: str = "1.0.0",
        allow_override: bool = False
    ) -> None:
        """
        Register a task handler for a specific task type.
        
        Args:
            task_type: Type of task this handler will process
            handler: Callable that takes a Task and processes it
            description: Human-readable description of the handler
            version: Version string for tracking
            allow_override: If True, allows overriding existing handlers
            
        Raises:
            TaskHandlerAlreadyRegisteredError: If handler already registered and allow_override=False
            ValueError: If task_type is empty or handler is not callable
        """
        if not task_type:
            raise ValueError("task_type cannot be empty")
        
        if not callable(handler):
            raise ValueError("handler must be callable")
        
        with self._lock:
            if task_type in self._handlers and not allow_override:
                raise TaskHandlerAlreadyRegisteredError(
                    f"Handler for task type '{task_type}' is already registered. "
                    f"Use allow_override=True to replace it."
                )
            
            handler_info = TaskHandlerInfo(
                task_type=task_type,
                handler=handler,
                description=description,
                version=version
            )
            
            self._handlers[task_type] = handler_info
            
            action = "Overridden" if task_type in self._handlers and allow_override else "Registered"
            logger.info(
                f"{action} handler for task type '{task_type}' "
                f"(version: {version}, description: {description or 'none'})"
            )
    
    def unregister_handler(self, task_type: str) -> bool:
        """
        Unregister a task handler.
        
        Args:
            task_type: Type of task handler to remove
            
        Returns:
            True if handler was removed, False if it didn't exist
        """
        with self._lock:
            if task_type in self._handlers:
                del self._handlers[task_type]
                logger.info(f"Unregistered handler for task type '{task_type}'")
                return True
            return False
    
    def get_handler(self, task_type: str) -> Callable[[Task], None]:
        """
        Get the registered handler for a task type.
        
        Args:
            task_type: Type of task to get handler for
            
        Returns:
            Handler callable for the task type
            
        Raises:
            TaskHandlerNotRegisteredError: If no handler registered for this type
        """
        with self._lock:
            handler_info = self._handlers.get(task_type)
            
            if handler_info is None:
                raise TaskHandlerNotRegisteredError(
                    f"No handler registered for task type '{task_type}'. "
                    f"Registered types: {sorted(self._handlers.keys())}"
                )
            
            return handler_info.handler
    
    def is_registered(self, task_type: str) -> bool:
        """
        Check if a handler is registered for a task type.
        
        Args:
            task_type: Type of task to check
            
        Returns:
            True if handler is registered, False otherwise
        """
        with self._lock:
            return task_type in self._handlers
    
    def get_registered_types(self) -> Set[str]:
        """
        Get all registered task types.
        
        Returns:
            Set of registered task type strings
        """
        with self._lock:
            return set(self._handlers.keys())
    
    def get_handler_info(self, task_type: str) -> Optional[TaskHandlerInfo]:
        """
        Get detailed information about a registered handler.
        
        Args:
            task_type: Type of task to get info for
            
        Returns:
            TaskHandlerInfo if handler is registered, None otherwise
        """
        with self._lock:
            return self._handlers.get(task_type)
    
    def clear(self) -> None:
        """
        Clear all registered handlers.
        
        Useful for testing or resetting the registry.
        """
        with self._lock:
            count = len(self._handlers)
            self._handlers.clear()
            logger.info(f"Cleared all {count} registered handlers")
    
    def validate_task(self, task: Task) -> None:
        """
        Validate that a task has a registered handler.
        
        Args:
            task: Task to validate
            
        Raises:
            TaskHandlerNotRegisteredError: If task type has no registered handler
        """
        if not self.is_registered(task.type):
            raise TaskHandlerNotRegisteredError(
                f"Cannot process task #{task.id}: No handler registered for type '{task.type}'. "
                f"Registered types: {sorted(self.get_registered_types())}"
            )


# Global singleton registry instance
_global_registry: Optional[TaskHandlerRegistry] = None
_global_registry_lock = RLock()


def get_global_registry() -> TaskHandlerRegistry:
    """
    Get the global task handler registry instance.
    
    Returns:
        Global TaskHandlerRegistry singleton
    """
    global _global_registry
    
    with _global_registry_lock:
        if _global_registry is None:
            _global_registry = TaskHandlerRegistry()
        return _global_registry


def reset_global_registry() -> None:
    """
    Reset the global registry.
    
    Useful for testing. Creates a new empty registry.
    """
    global _global_registry
    
    with _global_registry_lock:
        _global_registry = TaskHandlerRegistry()
