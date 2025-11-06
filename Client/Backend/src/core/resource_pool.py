"""Resource pooling for efficient reuse of expensive resources.

This module implements Pattern 6 from the Background Tasks Best Practices guide,
providing resource pooling for thread pools and subprocess wrappers.

Primary Platform: Windows (with support for Linux/macOS)
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

from .subprocess_wrapper import SubprocessWrapper, RunMode

logger = logging.getLogger(__name__)


class ResourcePool:
    """Pool of reusable resources for background tasks.
    
    This class manages a pool of SubprocessWrapper instances to avoid the
    overhead of creating new thread pools for each operation.
    
    Follows SOLID principles:
    - Single Responsibility: Manages resource pooling
    - Open/Closed: Extensible for other resource types
    - Liskov Substitution: Context manager interface is standard
    - Interface Segregation: Minimal interface for resource acquisition
    - Dependency Inversion: Depends on SubprocessWrapper abstraction
    
    Example:
        ```python
        # Initialize pool
        pool = ResourcePool(max_workers=10)
        
        # Use pooled resource
        async with pool.acquire_subprocess() as wrapper:
            process, stdout, stderr = await wrapper.create_subprocess(
                'python', 'script.py'
            )
            await process.wait()
        
        # Cleanup on shutdown
        pool.cleanup()
        ```
    """
    
    def __init__(self, max_workers: int = 10, mode: Optional[RunMode] = None):
        """Initialize resource pool.
        
        Args:
            max_workers: Maximum thread pool workers for THREADED mode
            mode: Execution mode (auto-detected if None)
        """
        self.max_workers = max_workers
        self.mode = mode
        self.wrapper = SubprocessWrapper(
            mode=self.mode,
            max_workers=self.max_workers
        )
        self._initialized = True
        self._lock = asyncio.Lock()
        
        logger.info(
            f"ResourcePool initialized with max_workers={max_workers}, "
            f"mode={self.wrapper.mode}"
        )
    
    @asynccontextmanager
    async def acquire_subprocess(self):
        """Acquire a subprocess slot from the pool.
        
        This context manager provides thread-safe access to the pooled
        SubprocessWrapper. The wrapper's ThreadPoolExecutor handles
        the actual pooling of workers.
        
        The lock is held during the initialization check but released
        during resource usage to allow concurrent access to the pool.
        The pool is designed to be used concurrently - the SubprocessWrapper
        and its ThreadPoolExecutor handle thread-safety internally.
        
        Yields:
            SubprocessWrapper: Pooled subprocess wrapper
            
        Example:
            ```python
            async with pool.acquire_subprocess() as wrapper:
                process, stdout, stderr = await wrapper.create_subprocess(
                    'python', '-c', 'print("hello")'
                )
                exit_code = await process.wait()
            ```
        """
        # Acquire lock only to check initialization status
        # Release immediately to allow concurrent resource usage
        async with self._lock:
            if not self._initialized:
                raise RuntimeError("ResourcePool has been cleaned up")
            
            logger.debug("Acquired subprocess resource from pool")
            
        try:
            # Yield the wrapper - the ThreadPoolExecutor handles pooling
            # Multiple coroutines can use the same wrapper concurrently
            yield self.wrapper
        finally:
            # No cleanup needed - wrapper is reused
            logger.debug("Released subprocess resource back to pool")
    
    def cleanup(self):
        """Clean up all pooled resources.
        
        This should be called during application shutdown to properly
        release all resources and shutdown thread pools.
        
        Example:
            ```python
            # On application shutdown
            pool.cleanup()
            ```
        """
        if self._initialized:
            logger.info("Cleaning up ResourcePool...")
            self.wrapper.cleanup()
            self._initialized = False
            logger.info("ResourcePool cleanup complete")
        else:
            logger.warning("ResourcePool already cleaned up")
    
    def __del__(self):
        """Ensure cleanup on garbage collection."""
        if self._initialized:
            logger.warning("ResourcePool not explicitly cleaned up - cleaning up in __del__")
            self.cleanup()


# Global resource pool instance (initialized in main.py lifespan)
_global_pool: Optional[ResourcePool] = None
_global_pool_lock = asyncio.Lock()


def get_resource_pool() -> ResourcePool:
    """Get the global resource pool instance.
    
    Returns:
        ResourcePool: The global resource pool
        
    Raises:
        RuntimeError: If the pool has not been initialized
        
    Example:
        ```python
        pool = get_resource_pool()
        async with pool.acquire_subprocess() as wrapper:
            # Use wrapper
            pass
        ```
    """
    if _global_pool is None:
        raise RuntimeError(
            "ResourcePool not initialized. "
            "Ensure application lifespan has started."
        )
    return _global_pool


async def initialize_resource_pool_async(max_workers: int = 10, mode: Optional[RunMode] = None):
    """Initialize the global resource pool (async, thread-safe).
    
    This is the async version that should be used during application startup.
    
    Args:
        max_workers: Maximum thread pool workers
        mode: Execution mode (auto-detected if None)
        
    Example:
        ```python
        # In application startup
        await initialize_resource_pool_async(max_workers=10)
        ```
    """
    global _global_pool
    
    async with _global_pool_lock:
        if _global_pool is not None:
            logger.warning("ResourcePool already initialized - cleaning up old instance")
            _global_pool.cleanup()
        
        _global_pool = ResourcePool(max_workers=max_workers, mode=mode)
        logger.info("Global ResourcePool initialized")


def initialize_resource_pool(max_workers: int = 10, mode: Optional[RunMode] = None):
    """Initialize the global resource pool (sync version).
    
    This should be called during application startup. For async contexts,
    use initialize_resource_pool_async() instead.
    
    Note: This function is not thread-safe. It should only be called
    from the main thread during application initialization.
    
    Args:
        max_workers: Maximum thread pool workers
        mode: Execution mode (auto-detected if None)
        
    Example:
        ```python
        # In application startup (sync context)
        initialize_resource_pool(max_workers=10)
        ```
    """
    global _global_pool
    
    # Note: No locking in sync version - assumes single-threaded initialization
    # If thread safety is needed, use initialize_resource_pool_async()
    if _global_pool is not None:
        logger.warning("ResourcePool already initialized - cleaning up old instance")
        _global_pool.cleanup()
    
    _global_pool = ResourcePool(max_workers=max_workers, mode=mode)
    logger.info("Global ResourcePool initialized")


def cleanup_resource_pool():
    """Cleanup the global resource pool.
    
    This should be called during application shutdown.
    
    Example:
        ```python
        # In application shutdown
        cleanup_resource_pool()
        ```
    """
    global _global_pool
    if _global_pool is not None:
        _global_pool.cleanup()
        _global_pool = None
        logger.info("Global ResourcePool cleaned up")
