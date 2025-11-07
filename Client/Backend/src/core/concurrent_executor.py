"""Concurrent module execution with resource limits.

This module implements Pattern 3 from BACKGROUND_TASKS_BEST_PRACTICES.md,
providing semaphore-based concurrency limiting and resource management.

Platform: Windows (primary), Linux/macOS (supported)
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from .exceptions import ResourceLimitException
from .resource_manager import ResourceManager
from .subprocess_wrapper import SubprocessWrapper

logger = logging.getLogger(__name__)


class ConcurrentExecutor:
    """Execute multiple modules concurrently with resource limits.
    
    This class implements Pattern 3 from the Background Tasks Best Practices guide,
    providing:
    - Semaphore-based concurrency limiting
    - Resource manager integration for system checks
    - Batch execution support
    - Per-task error handling with exception return
    
    Follows SOLID principles:
    - Single Responsibility: Manages concurrent module execution
    - Open/Closed: Extensible via configuration parameters
    - Dependency Inversion: Depends on ResourceManager abstraction
    - Interface Segregation: Provides focused, minimal interface
    
    Example:
        >>> executor = ConcurrentExecutor(max_concurrent=5)
        >>> modules = [
        ...     ("mod1", Path("script1.py"), ["arg1"]),
        ...     ("mod2", Path("script2.py"), ["arg2"]),
        ... ]
        >>> results = await executor.execute_batch(modules)
        >>> executor.cleanup()
    """
    
    def __init__(
        self,
        max_concurrent: int = 10,
        resource_manager: Optional[ResourceManager] = None
    ):
        """Initialize concurrent executor.
        
        Args:
            max_concurrent: Maximum number of concurrent executions (default: 10)
            resource_manager: Optional resource manager for system checks
            
        Raises:
            ValueError: If max_concurrent is less than 1
        """
        if max_concurrent < 1:
            raise ValueError("max_concurrent must be at least 1")
        
        self.max_concurrent = max_concurrent
        self.resource_manager = resource_manager
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.wrapper = SubprocessWrapper()
        
        logger.info(
            f"ConcurrentExecutor initialized with max_concurrent={max_concurrent}, "
            f"resource_manager={'enabled' if resource_manager else 'disabled'}"
        )
    
    async def execute_module(
        self,
        module_id: str,
        script_path: Path,
        args: Optional[List[str]] = None,
        cwd: Optional[Path] = None
    ) -> Dict[str, Union[str, int, bool, Optional[str]]]:
        """Execute a single module with resource management.
        
        This method uses a semaphore to limit concurrent executions and optionally
        checks system resources before starting execution.
        
        Args:
            module_id: Module identifier for tracking
            script_path: Path to the Python script to execute
            args: Optional command-line arguments
            cwd: Optional working directory (defaults to script_path.parent)
            
        Returns:
            Dictionary containing:
                - module_id: str - Module identifier
                - exit_code: int - Process exit code (or -1 for exceptions)
                - success: bool - True if exit_code == 0
                - error: Optional[str] - Error message if execution failed
                
        Note:
            This method never raises exceptions - all errors are captured in the
            return dictionary following Pattern 3's exception handling approach.
        """
        async with self.semaphore:  # Limit concurrency
            try:
                # Check resources before starting
                if self.resource_manager:
                    available, reason = await self._check_resources_async()
                    if not available:
                        logger.warning(
                            f"Insufficient resources for module {module_id}: {reason}"
                        )
                        raise ResourceLimitException(
                            f"Insufficient system resources: {reason}",
                            resource_type="system"
                        )
                
                logger.info(f"Executing module {module_id}")
                
                # Prepare arguments
                args = args or []
                cwd = cwd or script_path.parent
                
                # Execute module
                process, stdout, stderr = await self.wrapper.create_subprocess(
                    'python', str(script_path), *args,
                    cwd=cwd
                )
                
                logger.debug(f"Module {module_id} started with PID={process.pid}")
                
                # Wait for completion
                exit_code = await process.wait()
                
                logger.info(
                    f"Module {module_id} completed with exit_code={exit_code}"
                )
                
                return {
                    'module_id': module_id,
                    'exit_code': exit_code,
                    'success': exit_code == 0,
                    'error': None
                }
                
            except Exception as e:
                logger.error(
                    f"Module {module_id} failed: {e}",
                    exc_info=True
                )
                return {
                    'module_id': module_id,
                    'exit_code': -1,
                    'success': False,
                    'error': str(e)
                }
    
    async def execute_batch(
        self,
        modules: List[Tuple[str, Path, Optional[List[str]]]]
    ) -> List[Dict[str, Union[str, int, bool, Optional[str]]]]:
        """Execute multiple modules concurrently.
        
        This method starts all module executions concurrently, respecting the
        semaphore limit. It uses asyncio.gather with return_exceptions=True to
        ensure all tasks complete. Since execute_module has a no-raise policy,
        all results will be dictionaries (exceptions are captured in the 'error' field).
        
        Args:
            modules: List of tuples containing:
                - module_id: str
                - script_path: Path
                - args: Optional[List[str]]
                
        Returns:
            List of execution result dictionaries.
            Each result contains module_id, exit_code, success, and error fields.
            
        Example:
            >>> modules = [
            ...     ("module1", Path("/path/to/script1.py"), ["--arg1"]),
            ...     ("module2", Path("/path/to/script2.py"), None),
            ...     ("module3", Path("/path/to/script3.py"), ["--verbose"]),
            ... ]
            >>> results = await executor.execute_batch(modules)
            >>> for result in results:
            ...     if result['success']:
            ...         print(f"{result['module_id']} succeeded")
        """
        if not modules:
            logger.warning("execute_batch called with empty modules list")
            return []
        
        logger.info(f"Starting batch execution of {len(modules)} modules")
        
        # Create tasks for all modules
        tasks = [
            self.execute_module(module_id, script_path, args)
            for module_id, script_path, args in modules
        ]
        
        # Execute all tasks concurrently
        # Note: return_exceptions=True is used for safety, but execute_module
        # has a no-raise policy, so all results will be dictionaries
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log summary (all results are guaranteed to be dictionaries)
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful
        
        logger.info(
            f"Batch execution complete: {successful} succeeded, {failed} failed"
        )
        
        return results
    
    async def _check_resources_async(self) -> Tuple[bool, Optional[str]]:
        """Check system resources asynchronously.
        
        Wraps the synchronous resource_manager.check_resources_available()
        in an async context to avoid blocking the event loop.
        
        Returns:
            Tuple of (available: bool, reason: Optional[str])
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.resource_manager.check_resources_available
        )
    
    def cleanup(self):
        """Clean up resources.
        
        This method should be called when the executor is no longer needed
        to ensure proper cleanup of the subprocess wrapper.
        """
        logger.debug("Cleaning up ConcurrentExecutor resources")
        self.wrapper.cleanup()
