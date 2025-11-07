"""
Task Orchestrator - Unified interface for all background task patterns.

This module provides:
- TaskOrchestrator: Single entry point for executing tasks using any pattern
- PatternAdvisor: Helper for recommending appropriate patterns
- TaskPattern: Enum of available patterns

Integrates all 6 patterns from BACKGROUND_TASKS_BEST_PRACTICES.md:
1. Simple Module Execution
2. Long-Running Background Task  
3. Concurrent Module Execution
4. Fire-and-Forget with Tracking
5. Periodic Background Tasks
6. Resource Pooling
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TaskPattern(Enum):
    """Available background task patterns."""
    SIMPLE = "simple"  # Pattern 1: Simple Module Execution
    LONG_RUNNING = "long_running"  # Pattern 2: Long-Running Background Task
    CONCURRENT = "concurrent"  # Pattern 3: Concurrent Module Execution
    FIRE_AND_FORGET = "fire_and_forget"  # Pattern 4: Fire-and-Forget with Tracking
    PERIODIC = "periodic"  # Pattern 5: Periodic Background Tasks
    POOLED = "pooled"  # Pattern 6: Resource Pooling


class TaskOrchestrator:
    """
    Unified orchestrator for all background task patterns.
    
    Provides a single interface to execute tasks using any of the
    6 documented patterns, with automatic pattern selection based
    on task requirements.
    
    Example:
        >>> orchestrator = TaskOrchestrator()
        >>> 
        >>> # Auto-select pattern
        >>> result = await orchestrator.execute(
        ...     script_path=Path("process.py"),
        ...     args=["--input", "data.csv"],
        ...     streaming=True  # Auto-selects LONG_RUNNING
        ... )
        >>>
        >>> # Explicit pattern selection
        >>> result = await orchestrator.execute(
        ...     script_path=Path("batch.py"),
        ...     args=[],
        ...     pattern=TaskPattern.CONCURRENT,
        ...     concurrent_tasks=10
        ... )
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize orchestrator with all pattern implementations.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Pattern implementations will be imported lazily to avoid circular dependencies
        self._concurrent_executor = None
        self._task_manager = None
        self._periodic_task_manager = None
        self._resource_pool = None
    
    def _get_concurrent_executor(self):
        """Lazy load ConcurrentExecutor."""
        if self._concurrent_executor is None:
            from .concurrent_executor import ConcurrentExecutor
            self._concurrent_executor = ConcurrentExecutor()
        return self._concurrent_executor
    
    def _get_task_manager(self):
        """Lazy load BackgroundTaskManager."""
        if self._task_manager is None:
            from .task_manager import BackgroundTaskManager
            from .run_registry import RunRegistry
            # Create with a shared registry
            registry = RunRegistry()
            self._task_manager = BackgroundTaskManager(registry=registry)
        return self._task_manager
    
    def _get_periodic_task_manager(self):
        """Lazy load PeriodicTaskManager."""
        if self._periodic_task_manager is None:
            from .periodic_tasks import PeriodicTaskManager
            self._periodic_task_manager = PeriodicTaskManager()
        return self._periodic_task_manager
    
    def _get_resource_pool(self):
        """Lazy load ResourcePool."""
        if self._resource_pool is None:
            from .resource_pool import ResourcePool
            self._resource_pool = ResourcePool()
        return self._resource_pool
    
    async def execute(
        self,
        script_path: Path,
        args: Optional[List[str]] = None,
        pattern: Optional[TaskPattern] = None,
        **kwargs
    ) -> Any:
        """
        Execute a task using the specified or auto-selected pattern.
        
        Args:
            script_path: Path to the script to execute
            args: Arguments for the script (optional)
            pattern: Pattern to use (auto-selected if None)
            **kwargs: Pattern-specific options:
                - streaming (bool): Enable real-time output streaming
                - concurrent_tasks (int): Number of concurrent tasks
                - wait_for_result (bool): Whether to wait for result
                - periodic (bool): Run as periodic task
                - interval_seconds (int): Interval for periodic tasks
                - use_pool (bool): Use resource pooling
                - cwd (Path): Working directory
                - mode: RunMode override
        
        Returns:
            Result based on the pattern used:
            - SIMPLE: Tuple[int, str, str] (exit_code, stdout, stderr)
            - LONG_RUNNING: int (exit_code)
            - CONCURRENT: List of results
            - FIRE_AND_FORGET: Run object
            - PERIODIC: PeriodicTask object
            - POOLED: Task result
        
        Raises:
            ValueError: If pattern is unknown
            FileNotFoundError: If script_path doesn't exist
        """
        args = args or []
        
        # Auto-select pattern if not specified
        if pattern is None:
            pattern = self._select_pattern(script_path, args, kwargs)
        
        logger.info(f"Executing {script_path.name} using pattern: {pattern.value}")
        
        # Execute using the selected pattern
        if pattern == TaskPattern.SIMPLE:
            return await self._execute_simple(script_path, args, kwargs)
        elif pattern == TaskPattern.LONG_RUNNING:
            return await self._execute_long_running(script_path, args, kwargs)
        elif pattern == TaskPattern.CONCURRENT:
            return await self._execute_concurrent(script_path, args, kwargs)
        elif pattern == TaskPattern.FIRE_AND_FORGET:
            return await self._execute_fire_and_forget(script_path, args, kwargs)
        elif pattern == TaskPattern.PERIODIC:
            return await self._execute_periodic(script_path, args, kwargs)
        elif pattern == TaskPattern.POOLED:
            return await self._execute_pooled(script_path, args, kwargs)
        else:
            raise ValueError(f"Unknown pattern: {pattern}")
    
    def _select_pattern(
        self,
        script_path: Path,
        args: List[str],
        options: Dict[str, Any]
    ) -> TaskPattern:
        """
        Auto-select the most appropriate pattern based on task characteristics.
        
        Selection criteria (in order of priority):
        1. periodic=True -> PERIODIC
        2. streaming=True -> LONG_RUNNING
        3. concurrent_tasks > 1 -> CONCURRENT
        4. wait_for_result=False -> FIRE_AND_FORGET
        5. use_pool=True -> POOLED
        6. Otherwise -> SIMPLE
        
        Args:
            script_path: Path to script
            args: Script arguments
            options: Execution options
        
        Returns:
            Selected TaskPattern
        """
        if options.get('periodic'):
            return TaskPattern.PERIODIC
        if options.get('streaming'):
            return TaskPattern.LONG_RUNNING
        if options.get('concurrent_tasks', 1) > 1:
            return TaskPattern.CONCURRENT
        if not options.get('wait_for_result', True):
            return TaskPattern.FIRE_AND_FORGET
        if options.get('use_pool'):
            return TaskPattern.POOLED
        
        return TaskPattern.SIMPLE
    
    async def _execute_simple(
        self,
        script_path: Path,
        args: List[str],
        options: Dict[str, Any]
    ) -> Tuple[int, str, str]:
        """Execute using Pattern 1: Simple Module Execution."""
        from .execution_patterns import execute_module
        
        cwd = options.get('cwd', script_path.parent)
        mode = options.get('mode')
        
        return await execute_module(
            script_path=script_path,
            args=args,
            cwd=cwd,
            mode=mode
        )
    
    async def _execute_long_running(
        self,
        script_path: Path,
        args: List[str],
        options: Dict[str, Any]
    ) -> int:
        """Execute using Pattern 2: Long-Running Background Task."""
        from .execution_patterns import execute_long_running_task
        from .output_capture import OutputCapture
        
        run_id = options.get('run_id', f"run_{script_path.stem}")
        cwd = options.get('cwd', script_path.parent)
        
        # Create output capture for streaming
        output_capture = OutputCapture(max_lines=options.get('max_lines', 1000))
        
        return await execute_long_running_task(
            run_id=run_id,
            script_path=script_path,
            output_capture=output_capture,
            args=args,
            cwd=cwd
        )
    
    async def _execute_concurrent(
        self,
        script_path: Path,
        args: List[str],
        options: Dict[str, Any]
    ) -> List[Any]:
        """Execute using Pattern 3: Concurrent Module Execution."""
        executor = self._get_concurrent_executor()
        
        tasks = options.get('tasks', [script_path])
        max_concurrent = options.get('max_concurrent', 5)
        
        return await executor.execute_batch(
            tasks=tasks,
            max_concurrent=max_concurrent
        )
    
    async def _execute_fire_and_forget(
        self,
        script_path: Path,
        args: List[str],
        options: Dict[str, Any]
    ):
        """Execute using Pattern 4: Fire-and-Forget with Tracking."""
        task_manager = self._get_task_manager()
        
        from .run_registry import Run, RunStatus
        from uuid import uuid4
        
        # Create a run object for tracking
        run = Run(
            run_id=options.get('run_id', str(uuid4())),
            module_id=script_path.stem,
            module_name=options.get('module_name', script_path.stem),
            status=RunStatus.QUEUED,
            parameters=options.get('parameters', {})
        )
        
        # Define async coroutine for the task
        async def task_coro():
            from .execution_patterns import execute_module
            cwd = options.get('cwd', script_path.parent)
            return await execute_module(script_path, args, cwd)
        
        # Start task in background
        await task_manager.start_task(run, task_coro())
        
        return run
    
    async def _execute_periodic(
        self,
        script_path: Path,
        args: List[str],
        options: Dict[str, Any]
    ):
        """Execute using Pattern 5: Periodic Background Tasks."""
        manager = self._get_periodic_task_manager()
        
        from .periodic_tasks import PeriodicTask
        
        async def task_func():
            from .execution_patterns import execute_module
            cwd = options.get('cwd', script_path.parent)
            return await execute_module(script_path, args, cwd)
        
        task = PeriodicTask(
            name=options.get('task_name', script_path.stem),
            coroutine=task_func,
            interval_seconds=options.get('interval_seconds', 3600),
            enabled=options.get('enabled', True)
        )
        
        await manager.add_task(task)
        return task
    
    async def _execute_pooled(
        self,
        script_path: Path,
        args: List[str],
        options: Dict[str, Any]
    ):
        """Execute using Pattern 6: Resource Pooling."""
        pool = self._get_resource_pool()
        
        # Acquire resource from pool
        async with pool.acquire() as resource:
            from .execution_patterns import execute_module
            cwd = options.get('cwd', script_path.parent)
            return await execute_module(script_path, args, cwd)


class PatternAdvisor:
    """
    Helper to advise which pattern to use based on requirements.
    
    Provides recommendations and explanations for pattern selection.
    
    Example:
        >>> # Get recommendation
        >>> pattern = PatternAdvisor.recommend(
        ...     expected_duration_seconds=300,
        ...     requires_streaming=True
        ... )
        >>> print(pattern)  # TaskPattern.LONG_RUNNING
        >>>
        >>> # Get explanation
        >>> info = PatternAdvisor.explain(TaskPattern.LONG_RUNNING)
        >>> print(info['use_when'])
    """
    
    @staticmethod
    def recommend(
        *,
        expected_duration_seconds: Optional[int] = None,
        requires_streaming: bool = False,
        concurrent_tasks: int = 1,
        needs_result: bool = True,
        recurring: bool = False,
        high_frequency: bool = False
    ) -> TaskPattern:
        """
        Recommend a pattern based on task requirements.
        
        Args:
            expected_duration_seconds: Expected task duration (None if unknown)
            requires_streaming: Whether real-time output is needed
            concurrent_tasks: Number of tasks to run concurrently
            needs_result: Whether caller needs the result
            recurring: Whether task runs on a schedule
            high_frequency: Whether task runs frequently (>10 times/min)
        
        Returns:
            Recommended TaskPattern
        
        Example:
            >>> pattern = PatternAdvisor.recommend(
            ...     expected_duration_seconds=120,
            ...     requires_streaming=True
            ... )
            >>> assert pattern == TaskPattern.LONG_RUNNING
        """
        if recurring:
            return TaskPattern.PERIODIC
        
        if requires_streaming or (expected_duration_seconds and expected_duration_seconds > 60):
            return TaskPattern.LONG_RUNNING
        
        if concurrent_tasks > 1:
            return TaskPattern.CONCURRENT
        
        if not needs_result:
            return TaskPattern.FIRE_AND_FORGET
        
        if high_frequency:
            return TaskPattern.POOLED
        
        return TaskPattern.SIMPLE
    
    @staticmethod
    def explain(pattern: TaskPattern) -> Dict[str, Any]:
        """
        Explain when to use a pattern and its characteristics.
        
        Args:
            pattern: Pattern to explain
        
        Returns:
            Dictionary with pattern information including:
            - name: Human-readable name
            - use_when: When to use this pattern
            - benefits: List of benefits
            - limitations: List of limitations
            - example: Example use case
        
        Example:
            >>> info = PatternAdvisor.explain(TaskPattern.SIMPLE)
            >>> print(info['name'])
            'Simple Module Execution'
        """
        explanations = {
            TaskPattern.SIMPLE: {
                "name": "Simple Module Execution",
                "use_when": "Running a single task with known duration (<60s)",
                "benefits": ["Simple to use", "Full error handling", "Complete output capture"],
                "limitations": ["Blocks until complete", "No streaming output"],
                "example": "Quick data processing script"
            },
            TaskPattern.LONG_RUNNING: {
                "name": "Long-Running Background Task",
                "use_when": "Task takes >60s or requires real-time output",
                "benefits": ["Real-time output streaming", "Cancellable", "Progress tracking"],
                "limitations": ["More complex setup", "Requires SSE support"],
                "example": "Training ML model, processing large dataset"
            },
            TaskPattern.CONCURRENT: {
                "name": "Concurrent Module Execution",
                "use_when": "Running multiple tasks simultaneously",
                "benefits": ["Parallel execution", "Resource limits", "Batch processing"],
                "limitations": ["Requires resource management", "More memory usage"],
                "example": "Processing 100 videos in parallel"
            },
            TaskPattern.FIRE_AND_FORGET: {
                "name": "Fire-and-Forget with Tracking",
                "use_when": "Launch task without waiting for result",
                "benefits": ["Non-blocking", "Status tracking", "Background execution"],
                "limitations": ["No direct result", "Requires polling for status"],
                "example": "Sending analytics, generating reports"
            },
            TaskPattern.PERIODIC: {
                "name": "Periodic Background Tasks",
                "use_when": "Task runs on a schedule (maintenance, cleanup, etc.)",
                "benefits": ["Automated scheduling", "Configurable intervals", "Retry logic"],
                "limitations": ["Not for one-time tasks", "Requires scheduler setup"],
                "example": "Nightly cleanup, hourly data sync"
            },
            TaskPattern.POOLED: {
                "name": "Resource Pooling",
                "use_when": "High-frequency task execution (>10 tasks/min)",
                "benefits": ["Resource reuse", "Better performance", "Lower overhead"],
                "limitations": ["More complex initialization", "Pool size tuning needed"],
                "example": "API request handling, frequent data queries"
            }
        }
        return explanations.get(pattern, {})
    
    @staticmethod
    def compare_patterns() -> Dict[TaskPattern, Dict[str, Any]]:
        """
        Get comparison matrix for all patterns.
        
        Returns:
            Dictionary mapping each pattern to its characteristics
        
        Example:
            >>> matrix = PatternAdvisor.compare_patterns()
            >>> for pattern, info in matrix.items():
            ...     print(f"{pattern.value}: {info['use_when']}")
        """
        return {pattern: PatternAdvisor.explain(pattern) for pattern in TaskPattern}
