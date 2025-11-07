# Resource Pooling Guide

This guide explains how to use the ResourcePool pattern for efficient reuse of expensive resources in the PrismQ Web Client Backend.

## Overview

The ResourcePool pattern (Pattern 6 from [BACKGROUND_TASKS_BEST_PRACTICES.md](./BACKGROUND_TASKS_BEST_PRACTICES.md)) provides efficient resource management by reusing expensive resources like thread pools and subprocess wrappers instead of creating new ones for each operation.

## Benefits

Resource pooling provides several key benefits:

1. **Performance**: Eliminates thread pool creation overhead
2. **Resource Efficiency**: Reuses subprocess infrastructure
3. **Better Utilization**: Maximizes use of available CPU cores
4. **Memory Efficiency**: Reduces memory allocation overhead
5. **Predictable Behavior**: Consistent performance across operations

## Architecture

```
┌─────────────────────────────────────────────────┐
│            FastAPI Application                  │
│  ┌───────────────────────────────────────────┐ │
│  │         Lifespan Manager                  │ │
│  │  - Initialize ResourcePool on startup    │ │
│  │  - Cleanup ResourcePool on shutdown      │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   Global ResourcePool  │
         │  - SubprocessWrapper   │
         │  - ThreadPoolExecutor  │
         │  - Lock for safety     │
         └────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  Application Modules   │
         │  - Use pooled wrapper  │
         │  - Async operations    │
         └────────────────────────┘
```

### Thread Safety and Concurrency

The ResourcePool is designed for safe concurrent access:

1. **Lock Strategy**: The pool uses an asyncio.Lock only to check initialization status during resource acquisition. The lock is released immediately to allow concurrent usage of the pooled wrapper.

2. **Concurrent Resource Usage**: Multiple coroutines can use the same SubprocessWrapper concurrently. The underlying ThreadPoolExecutor handles thread-safety internally.

3. **No Lock During Usage**: The lock is NOT held during resource usage to maximize concurrency. This design choice allows high-throughput parallel operations.

4. **Cleanup Safety**: Cleanup operations should only be performed during application shutdown when no operations are in progress.

**Design Rationale**: Holding the lock only during the initialization check (not during resource usage) maximizes concurrency while preventing use-after-cleanup errors. The SubprocessWrapper and ThreadPoolExecutor are inherently thread-safe and can be used concurrently by multiple coroutines.

## Basic Usage

### Using the Global Pool

The recommended approach is to use the global resource pool initialized during application startup:

```python
from src.core.resource_pool import get_resource_pool

# In your module or API endpoint
async def run_module():
    pool = get_resource_pool()
    
    async with pool.acquire_subprocess() as wrapper:
        process, stdout, stderr = await wrapper.create_subprocess(
            'python', 'my_script.py'
        )
        
        # Read output
        output = b''
        while True:
            line = await stdout.readline()
            if not line:
                break
            output += line
        
        exit_code = await process.wait()
        
        return exit_code, output
```

### Creating a Custom Pool

For specialized use cases, you can create a custom pool:

```python
from src.core.resource_pool import ResourcePool
from src.core.subprocess_wrapper import RunMode

# Create a custom pool
pool = ResourcePool(max_workers=5, mode=RunMode.THREADED)

try:
    async with pool.acquire_subprocess() as wrapper:
        # Use wrapper
        pass
finally:
    # Always cleanup custom pools
    pool.cleanup()
```

## Application Integration

The ResourcePool is automatically integrated with the FastAPI application lifespan:

```python
# In src/main.py
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    initialize_resource_pool(max_workers=settings.MAX_CONCURRENT_RUNS)
    
    yield
    
    # Shutdown
    cleanup_resource_pool()
```

This ensures:
- Pool is initialized before handling requests
- Pool is cleaned up on shutdown
- Resources are properly released

## Configuration

The ResourcePool can be configured through application settings:

### Environment Variables

```bash
# Maximum concurrent runs (used for pool size)
MAX_CONCURRENT_RUNS=10

# Run mode (optional, auto-detected by default)
PRISMQ_RUN_MODE=threaded
```

### In Code

```python
from src.core.resource_pool import initialize_resource_pool
from src.core.subprocess_wrapper import RunMode

# Initialize with custom settings
initialize_resource_pool(
    max_workers=20,  # Increase for high-concurrency scenarios
    mode=RunMode.THREADED  # Or RunMode.ASYNC on Linux/macOS
)
```

## Advanced Usage

### Concurrent Operations

The pool handles concurrent acquisitions safely:

```python
from src.core.resource_pool import get_resource_pool
import asyncio

async def process_task(task_id: int):
    pool = get_resource_pool()
    
    async with pool.acquire_subprocess() as wrapper:
        process, stdout, stderr = await wrapper.create_subprocess(
            'python', 'task.py', str(task_id)
        )
        return await process.wait()

# Run multiple tasks concurrently
results = await asyncio.gather(*[
    process_task(i) for i in range(10)
])
```

### Error Handling

Always handle errors when using the pool:

```python
from src.core.resource_pool import get_resource_pool
from src.core.exceptions import ModuleExecutionException

async def safe_execution():
    pool = get_resource_pool()
    
    try:
        async with pool.acquire_subprocess() as wrapper:
            process, stdout, stderr = await wrapper.create_subprocess(
                'python', 'script.py'
            )
            
            exit_code = await process.wait()
            
            if exit_code != 0:
                # Read error output
                error = await stderr.read()
                raise ModuleExecutionException(
                    f"Script failed with exit code {exit_code}: {error.decode()}"
                )
                
    except RuntimeError as e:
        # Pool not initialized or cleaned up
        raise ModuleExecutionException(f"Resource pool error: {e}")
```

## Performance Optimization

### Pool Size Tuning

Choose pool size based on your workload:

```python
# CPU-bound tasks: Use CPU core count
import os
max_workers = os.cpu_count()

# I/O-bound tasks: Can use more workers
max_workers = os.cpu_count() * 2

# Limited resources: Use conservative count
max_workers = 4
```

### Benchmarking

Compare pooled vs non-pooled performance:

```python
import time
from src.core.resource_pool import ResourcePool
from src.core.subprocess_wrapper import SubprocessWrapper, RunMode

async def benchmark_pooled():
    pool = ResourcePool(max_workers=4, mode=RunMode.THREADED)
    
    start = time.perf_counter()
    for _ in range(100):
        async with pool.acquire_subprocess() as wrapper:
            process, _, _ = await wrapper.create_subprocess('python', '--version')
            await process.wait()
    elapsed = time.perf_counter() - start
    
    pool.cleanup()
    return elapsed

async def benchmark_non_pooled():
    start = time.perf_counter()
    for _ in range(100):
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        process, _, _ = await wrapper.create_subprocess('python', '--version')
        await process.wait()
        wrapper.cleanup()
    elapsed = time.perf_counter() - start
    
    return elapsed

# Run benchmarks
pooled_time = await benchmark_pooled()
non_pooled_time = await benchmark_non_pooled()

print(f"Pooled: {pooled_time:.4f}s")
print(f"Non-pooled: {non_pooled_time:.4f}s")
print(f"Speedup: {non_pooled_time / pooled_time:.2f}x")
```

## Best Practices

### DO ✅

- **Use the global pool** for most operations
- **Configure pool size** based on workload
- **Use context managers** for resource acquisition
- **Handle errors** appropriately
- **Cleanup custom pools** in finally blocks

### DON'T ❌

- **Don't create pools** for every operation
- **Don't forget cleanup** for custom pools
- **Don't use after cleanup** - check if pool is initialized
- **Don't ignore errors** from pool operations
- **Don't use excessive pool size** - it wastes memory

## Platform Considerations

### Windows

On Windows, the pool automatically uses `RunMode.THREADED`:

```python
# Windows automatically uses THREADED mode
pool = ResourcePool(max_workers=10)
# pool.wrapper.mode == RunMode.THREADED
```

### Linux/macOS

On Linux/macOS, the pool uses `RunMode.ASYNC` by default:

```python
# Linux/macOS automatically uses ASYNC mode
pool = ResourcePool(max_workers=10)
# pool.wrapper.mode == RunMode.ASYNC
```

You can override with explicit mode:

```python
pool = ResourcePool(max_workers=10, mode=RunMode.THREADED)
```

## Monitoring

Monitor pool usage for optimization:

```python
import logging

logger = logging.getLogger(__name__)

async def monitored_execution():
    pool = get_resource_pool()
    
    logger.info(f"Pool max_workers: {pool.max_workers}")
    logger.info(f"Pool mode: {pool.wrapper.mode}")
    
    async with pool.acquire_subprocess() as wrapper:
        logger.info("Acquired subprocess from pool")
        # Use wrapper
        logger.info("Released subprocess back to pool")
```

## Troubleshooting

### Pool Not Initialized

**Error**: `RuntimeError: ResourcePool not initialized`

**Solution**: Ensure application has started and lifespan has run:

```python
# Check if pool is available
from src.core.resource_pool import get_resource_pool

try:
    pool = get_resource_pool()
except RuntimeError:
    # Pool not initialized - application not started
    pass
```

### Pool Cleaned Up

**Error**: `RuntimeError: ResourcePool has been cleaned up`

**Solution**: Don't use pool after application shutdown:

```python
# Avoid using pool after cleanup
pool = get_resource_pool()
cleanup_resource_pool()

# This will raise RuntimeError
async with pool.acquire_subprocess() as wrapper:
    pass
```

### Performance Not Improved

**Issue**: Pooling doesn't improve performance

**Diagnosis**:
1. Check pool size vs workload
2. Verify mode is appropriate for platform
3. Ensure operations benefit from pooling
4. Check for bottlenecks elsewhere

## Testing

Test resource pooling in your code:

```python
import pytest
from src.core.resource_pool import ResourcePool, RunMode

@pytest.mark.asyncio
async def test_my_pooled_function():
    # Create test pool
    pool = ResourcePool(max_workers=2, mode=RunMode.DRY_RUN)
    
    try:
        # Test your function
        result = await my_function(pool)
        assert result is not None
    finally:
        pool.cleanup()
```

## Migration Guide

### From Direct SubprocessWrapper

**Before**:
```python
wrapper = SubprocessWrapper(mode=RunMode.THREADED)
try:
    process, stdout, stderr = await wrapper.create_subprocess('python', 'script.py')
    await process.wait()
finally:
    wrapper.cleanup()
```

**After**:
```python
from src.core.resource_pool import get_resource_pool

pool = get_resource_pool()
async with pool.acquire_subprocess() as wrapper:
    process, stdout, stderr = await wrapper.create_subprocess('python', 'script.py')
    await process.wait()
# No cleanup needed - pool is reused
```

## Related Documentation

- [BACKGROUND_TASKS_BEST_PRACTICES.md](./BACKGROUND_TASKS_BEST_PRACTICES.md) - Best practices guide
- [API_REFERENCE.md](../API_REFERENCE.md) - API documentation
- [README.md](../README.md) - Backend overview

## Examples

See `_meta/tests/test_resource_pool.py` for comprehensive examples of:
- Basic usage
- Concurrent operations
- Performance benchmarks
- Error handling
- Integration tests

## Version History

- **v1.0.0** (2025-11-05): Initial implementation of ResourcePool pattern
