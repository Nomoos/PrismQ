# Issue #313: Integrate All Background Task Patterns into Unified Framework

## Status
Ready to Start - All Dependencies Complete

**Previous Blockers (Now Resolved):**
- ✅ Issue #310 (Pattern 4: Fire-and-Forget) is now complete and merged
- ✅ All 6 patterns (#307-#312) are now complete

**Status of Dependencies:**
- ✅ #307: Pattern 1 - Done
- ✅ #308: Pattern 2 - Done  
- ✅ #309: Pattern 3 - Done
- ✅ #310: Pattern 4 - Done (Recently Merged)
- ✅ #311: Pattern 5 - Done
- ✅ #312: Pattern 6 - Done

**Status:** Ready to implement - all dependencies satisfied

## Priority
Medium

## Category
Feature - Integration & Orchestration

## Worker
Worker 07 - Integration Development

## Description

Create an integration layer that combines all 6 background task patterns (#307-#312) into a unified, easy-to-use framework. This integration will provide a single entry point for developers to use any pattern seamlessly, with proper documentation and examples demonstrating how patterns work together.

## Problem Statement

While each of the 6 background task patterns (#307-#312) will be implemented independently, there is no unified interface or orchestration layer that:
- Provides a single entry point for using different patterns
- Demonstrates how patterns can be combined for complex workflows
- Offers guidance on which pattern to use for different scenarios
- Ensures patterns work well together in the same application
- Provides end-to-end examples of pattern integration

## Proposed Solution

Create an integration framework that:
- Provides a unified `TaskOrchestrator` class that can use any pattern
- Creates a pattern selection helper/advisor
- Implements example workflows combining multiple patterns
- Adds comprehensive integration tests
- Documents best practices for combining patterns
- Provides migration guide for existing code

## Acceptance Criteria

- [x] Create `TaskOrchestrator` class that integrates all 6 patterns
- [x] Implement pattern selection advisor/helper
- [x] Create at least 3 example workflows combining multiple patterns
- [x] Add comprehensive integration tests testing pattern interoperability
- [x] Write migration guide for existing code
- [x] Create comparison matrix showing when to use each pattern
- [ ] Add end-to-end examples in documentation
- [ ] Performance benchmarks comparing pattern combinations
- [x] All tests pass (unit + integration)
- [x] Code reviewed

## Technical Details

### Implementation Approach

Create a unified orchestration layer:

```python
from typing import Dict, Any, Optional, List
from pathlib import Path
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TaskPattern(Enum):
    """Available background task patterns."""
    SIMPLE = "simple"  # Pattern 1
    LONG_RUNNING = "long_running"  # Pattern 2
    CONCURRENT = "concurrent"  # Pattern 3
    FIRE_AND_FORGET = "fire_and_forget"  # Pattern 4
    PERIODIC = "periodic"  # Pattern 5
    POOLED = "pooled"  # Pattern 6

class TaskOrchestrator:
    """
    Unified orchestrator for all background task patterns.
    
    Provides a single interface to execute tasks using any of the
    6 documented patterns, with automatic pattern selection based
    on task requirements.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize orchestrator with all pattern implementations."""
        self.config = config or {}
        
        # Initialize pattern implementations
        from .execution_patterns import SimpleExecutor, LongRunningExecutor
        from .concurrent_executor import ConcurrentExecutor
        from .task_manager import TaskManager
        from .periodic_tasks import PeriodicTaskScheduler
        from .resource_pool import ResourcePool
        
        self.simple_executor = SimpleExecutor()
        self.long_running_executor = LongRunningExecutor()
        self.concurrent_executor = ConcurrentExecutor()
        self.task_manager = TaskManager()
        self.scheduler = PeriodicTaskScheduler()
        self.resource_pool = ResourcePool()
    
    async def execute(
        self,
        script_path: Path,
        args: List[str],
        pattern: Optional[TaskPattern] = None,
        **kwargs
    ):
        """
        Execute a task using the specified or auto-selected pattern.
        
        Args:
            script_path: Path to the script to execute
            args: Arguments for the script
            pattern: Pattern to use (auto-selected if None)
            **kwargs: Pattern-specific options
        
        Returns:
            Result based on the pattern used
        """
        if pattern is None:
            pattern = self._select_pattern(script_path, args, kwargs)
        
        logger.info(f"Executing {script_path} using pattern: {pattern.value}")
        
        if pattern == TaskPattern.SIMPLE:
            return await self.simple_executor.execute(script_path, args, **kwargs)
        elif pattern == TaskPattern.LONG_RUNNING:
            return await self.long_running_executor.execute(script_path, args, **kwargs)
        elif pattern == TaskPattern.CONCURRENT:
            return await self.concurrent_executor.execute(script_path, args, **kwargs)
        elif pattern == TaskPattern.FIRE_AND_FORGET:
            return await self.task_manager.launch(script_path, args, **kwargs)
        elif pattern == TaskPattern.PERIODIC:
            return await self.scheduler.schedule(script_path, args, **kwargs)
        elif pattern == TaskPattern.POOLED:
            return await self._execute_with_pool(script_path, args, **kwargs)
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
        
        Selection criteria:
        - periodic=True -> PERIODIC
        - streaming=True -> LONG_RUNNING
        - concurrent_tasks > 1 -> CONCURRENT
        - wait_for_result=False -> FIRE_AND_FORGET
        - use_pool=True -> POOLED
        - Otherwise -> SIMPLE
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
    
    async def _execute_with_pool(self, script_path: Path, args: List[str], **kwargs):
        """Execute using resource pool pattern."""
        async with self.resource_pool.acquire() as wrapper:
            return await self.simple_executor.execute(
                script_path, args, wrapper=wrapper, **kwargs
            )

class PatternAdvisor:
    """Helper to advise which pattern to use based on requirements."""
    
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
            expected_duration_seconds: Expected task duration
            requires_streaming: Whether real-time output is needed
            concurrent_tasks: Number of tasks to run concurrently
            needs_result: Whether caller needs the result
            recurring: Whether task runs on a schedule
            high_frequency: Whether task runs frequently (>10 times/min)
        
        Returns:
            Recommended TaskPattern
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
        
        Returns:
            Dictionary with pattern information
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
```

### Example Workflow: Combined Patterns

```python
# Example: Video processing workflow using multiple patterns

async def video_processing_workflow():
    """
    Complex workflow combining multiple patterns:
    1. Concurrent pattern: Process multiple videos in parallel
    2. Long-running pattern: Stream progress for each video
    3. Periodic pattern: Clean up temp files every hour
    4. Fire-and-forget: Send completion notifications
    """
    orchestrator = TaskOrchestrator()
    
    # 1. Set up periodic cleanup (Pattern 5)
    await orchestrator.execute(
        script_path=Path("cleanup.py"),
        args=[],
        pattern=TaskPattern.PERIODIC,
        interval_seconds=3600  # Every hour
    )
    
    # 2. Process videos concurrently (Pattern 3)
    video_paths = [Path(f"video_{i}.mp4") for i in range(10)]
    
    results = await orchestrator.execute(
        script_path=Path("process_video.py"),
        args=["--batch"],
        pattern=TaskPattern.CONCURRENT,
        concurrent_tasks=5,  # Process 5 at a time
        max_concurrent=5,
        items=video_paths
    )
    
    # 3. Stream progress for long operations (Pattern 2)
    for video in video_paths:
        if video.stat().st_size > 1_000_000_000:  # > 1GB
            await orchestrator.execute(
                script_path=Path("process_large_video.py"),
                args=[str(video)],
                pattern=TaskPattern.LONG_RUNNING,
                streaming=True
            )
    
    # 4. Fire-and-forget notifications (Pattern 4)
    await orchestrator.execute(
        script_path=Path("send_notification.py"),
        args=["--message", "Processing complete"],
        pattern=TaskPattern.FIRE_AND_FORGET,
        wait_for_result=False
    )
```

### Files to Create/Modify

**New Files:**
- `Client/Backend/src/core/task_orchestrator.py` - Main orchestrator class
- `Client/Backend/src/core/pattern_advisor.py` - Pattern recommendation helper
- `Client/Backend/_meta/examples/pattern_integration_examples.py` - Example workflows
- `Client/Backend/tests/integration/test_pattern_integration.py` - Integration tests
- `Client/Backend/_meta/docs/PATTERN_INTEGRATION_GUIDE.md` - Integration documentation
- `Client/Backend/_meta/docs/PATTERN_COMPARISON.md` - When to use which pattern
- `Client/Backend/_meta/docs/MIGRATION_GUIDE.md` - Migration from old code

**Modified Files:**
- `Client/Backend/src/core/__init__.py` - Export orchestrator
- `Client/Backend/README.md` - Add integration examples
- `Client/Backend/_meta/docs/BACKGROUND_TASKS_BEST_PRACTICES.md` - Add integration section

### Dependencies

This issue depends on the completion of:
- #307 - Simple Module Execution Pattern
- #308 - Long-Running Background Task Pattern
- #309 - Concurrent Module Execution Pattern
- #310 - Fire-and-Forget Pattern
- #311 - Periodic Background Tasks Pattern
- #312 - Resource Pooling Pattern

**Note**: This issue should be started AFTER all pattern implementations (#307-#312) are complete.

## Estimated Effort

5-7 days
- 2 days: Orchestrator and pattern advisor implementation
- 2 days: Example workflows and documentation
- 2 days: Integration testing and benchmarks
- 1 day: Migration guide and code review

## Target Platform

- Windows (primary testing)
- Linux/macOS (compatibility testing)
- NVIDIA RTX 5090 (32GB VRAM)
- AMD Ryzen processor
- 64GB RAM

## Testing Strategy

- [ ] Unit tests for TaskOrchestrator
- [ ] Unit tests for PatternAdvisor
- [ ] Integration tests combining 2 patterns
- [ ] Integration tests combining 3+ patterns
- [ ] End-to-end workflow tests
- [ ] Performance benchmarks comparing:
  - Direct pattern use vs orchestrator overhead
  - Different pattern combinations
  - Resource usage under various loads
- [ ] Test pattern auto-selection logic
- [ ] Test error handling when patterns fail
- [ ] Cross-platform testing (Windows + Linux)

## Related Issues

- **Depends on**: #307, #308, #309, #310, #311, #312 (all pattern implementations)
- **Integrates**: All 6 background task patterns
- **Category**: Integration layer for best practices implementation

## Deliverables

1. **Code**:
   - TaskOrchestrator class with full pattern support
   - PatternAdvisor for pattern recommendations
   - Example workflows demonstrating pattern combinations
   - Integration tests with >80% coverage

2. **Documentation**:
   - Pattern Integration Guide
   - Pattern Comparison Matrix
   - Migration Guide for existing code
   - API documentation
   - Usage examples

3. **Tests**:
   - Unit tests for orchestrator
   - Integration tests for pattern combinations
   - Performance benchmarks
   - End-to-end workflow tests

## Success Metrics

- [ ] All 6 patterns integrated and working together
- [ ] Pattern auto-selection works correctly >95% of the time
- [ ] Orchestrator overhead < 5% compared to direct pattern use
- [ ] All integration tests passing
- [ ] Documentation complete and clear
- [ ] At least 3 real-world example workflows
- [ ] Migration path clear for existing code

## Notes

This integration issue is the culmination of the best practices implementation. It should:
- Make it easy for developers to use any pattern
- Provide clear guidance on pattern selection
- Demonstrate real-world pattern combinations
- Ensure patterns work well together
- Provide smooth migration path

## Parallelization

⚠️ **Cannot be done in parallel with #307-#312**
- This issue DEPENDS on completion of all 6 pattern implementations
- Should be started AFTER all patterns are implemented and tested
- Once started, can be developed independently
- No blocking dependencies for future work

## Pattern Combination Examples

### Example 1: Data Processing Pipeline
```python
# Concurrent batch processing + periodic cleanup
orchestrator.execute(pattern=TaskPattern.CONCURRENT)  # Process batch
orchestrator.execute(pattern=TaskPattern.PERIODIC)    # Cleanup temp files
```

### Example 2: ML Training Workflow
```python
# Long-running training + fire-and-forget notifications
orchestrator.execute(pattern=TaskPattern.LONG_RUNNING)     # Training with progress
orchestrator.execute(pattern=TaskPattern.FIRE_AND_FORGET)  # Notify on completion
```

### Example 3: High-Throughput API
```python
# Resource pooling + concurrent execution
orchestrator.execute(pattern=TaskPattern.POOLED)       # Reuse resources
orchestrator.execute(pattern=TaskPattern.CONCURRENT)   # Handle multiple requests
```

## Implementation Priority

**Priority: Medium** (not blocking, but valuable for developer experience)

**Start**: After #307-#312 are complete
**Estimated Completion**: Week 2-3 after pattern implementations finish

---

**Created**: 2025-11-05
**Last Updated**: 2025-11-05  
**Assigned to**: Worker 07 - Integration Development
