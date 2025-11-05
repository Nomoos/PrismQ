# Concurrency Guide

**Platform**: Windows (primary), Linux/macOS (supported)  
**Last Updated**: 2025-11-05

## Overview

This guide covers concurrent module execution in the PrismQ Client Backend using the `ConcurrentExecutor` class. The implementation follows **Pattern 3** from the [Background Tasks Best Practices](BACKGROUND_TASKS_BEST_PRACTICES.md) guide.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Usage Examples](#usage-examples)
4. [Configuration](#configuration)
5. [Resource Management](#resource-management)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)
8. [Performance Tuning](#performance-tuning)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Basic Usage

```python
from pathlib import Path
from src.core.concurrent_executor import ConcurrentExecutor

# Create executor with default settings (max 10 concurrent)
executor = ConcurrentExecutor()

# Execute single module
result = await executor.execute_module(
    module_id="my_module",
    script_path=Path("path/to/script.py"),
    args=["--verbose"]
)

# Check result
if result['success']:
    print(f"Module {result['module_id']} completed successfully")
else:
    print(f"Module failed: {result['error']}")

# Cleanup
executor.cleanup()
```

### Batch Execution

```python
# Prepare batch of modules
modules = [
    ("module1", Path("scripts/module1.py"), ["--arg1"]),
    ("module2", Path("scripts/module2.py"), None),
    ("module3", Path("scripts/module3.py"), ["--verbose", "--debug"]),
]

# Execute all concurrently
results = await executor.execute_batch(modules)

# Process results (all results are dictionaries due to no-raise policy)
for result in results:
    if result['success']:
        print(f"✓ {result['module_id']}")
    else:
        print(f"✗ {result['module_id']}: {result['error']}")

executor.cleanup()
```

---

## Architecture

### Design Principles

The `ConcurrentExecutor` follows SOLID principles:

- **Single Responsibility**: Manages concurrent module execution
- **Open/Closed**: Extensible via configuration
- **Liskov Substitution**: Compatible with different subprocess modes
- **Interface Segregation**: Minimal, focused API
- **Dependency Inversion**: Depends on abstractions (ResourceManager, SubprocessWrapper)

### Component Diagram

```
┌─────────────────────────────────────────┐
│       ConcurrentExecutor                │
│  ┌───────────────────────────────────┐  │
│  │  Semaphore (concurrency limit)   │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  SubprocessWrapper                │  │
│  │  (cross-platform execution)       │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  ResourceManager (optional)       │  │
│  │  (system resource checks)         │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Key Features

1. **Semaphore-Based Limiting**: Uses `asyncio.Semaphore` to bound concurrent executions
2. **Resource Checking**: Optional integration with `ResourceManager` for system checks
3. **Exception Isolation**: Each task's exceptions are isolated and returned
4. **Cross-Platform**: Works on Windows, Linux, and macOS via `SubprocessWrapper`
5. **Async/Await**: Fully asynchronous for efficient I/O

---

## Usage Examples

### Example 1: Basic Concurrent Execution

```python
import asyncio
from pathlib import Path
from src.core.concurrent_executor import ConcurrentExecutor

async def run_modules():
    executor = ConcurrentExecutor(max_concurrent=5)
    
    try:
        modules = [
            ("data_fetch", Path("scripts/fetch_data.py"), ["--source", "api"]),
            ("data_clean", Path("scripts/clean_data.py"), None),
            ("data_analyze", Path("scripts/analyze_data.py"), ["--output", "results/"]),
        ]
        
        results = await executor.execute_batch(modules)
        
        # Process results
        for result in results:
            print(f"Module: {result['module_id']}")
            print(f"Success: {result['success']}")
            print(f"Exit Code: {result['exit_code']}")
            if result['error']:
                print(f"Error: {result['error']}")
            print("-" * 40)
    
    finally:
        executor.cleanup()

# Run
asyncio.run(run_modules())
```

### Example 2: With Resource Management

```python
from pathlib import Path
from src.core.concurrent_executor import ConcurrentExecutor
from src.core.resource_manager import ResourceManager

async def run_with_resource_checks():
    # Configure resource manager
    resource_manager = ResourceManager(
        cpu_threshold_percent=80.0,
        memory_required_gb=4.0
    )
    
    # Create executor with resource checks
    executor = ConcurrentExecutor(
        max_concurrent=10,
        resource_manager=resource_manager
    )
    
    try:
        modules = [
            (f"module_{i}", Path(f"scripts/module_{i}.py"), None)
            for i in range(20)
        ]
        
        results = await executor.execute_batch(modules)
        
        # Count successes and failures
        successes = sum(1 for r in results if r['success'])
        failures = len(results) - successes
        
        print(f"Completed: {successes} succeeded, {failures} failed")
        
    finally:
        executor.cleanup()

asyncio.run(run_with_resource_checks())
```

### Example 3: Handling Partial Failures

```python
from pathlib import Path
from src.core.concurrent_executor import ConcurrentExecutor

async def handle_partial_failures():
    executor = ConcurrentExecutor(max_concurrent=5)
    
    try:
        modules = [
            ("module_a", Path("scripts/module_a.py"), None),
            ("module_b", Path("scripts/module_b.py"), None),
            ("module_c", Path("scripts/module_c.py"), None),
        ]
        
        results = await executor.execute_batch(modules)
        
        # Separate successes and failures
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        # Process successful modules
        for result in successful:
            print(f"✓ {result['module_id']} completed successfully")
        
        # Handle failures
        for result in failed:
            print(f"✗ {result['module_id']} failed: {result['error']}")
            # Could retry, log, or alert here
        
        # Continue processing if at least some succeeded
        if successful:
            print(f"Proceeding with {len(successful)} successful results")
        
    finally:
        executor.cleanup()

asyncio.run(handle_partial_failures())
```

### Example 4: Dynamic Batch Processing

```python
from pathlib import Path
from src.core.concurrent_executor import ConcurrentExecutor

async def process_in_batches(all_modules, batch_size=10):
    """Process modules in batches to avoid overwhelming the system."""
    executor = ConcurrentExecutor(max_concurrent=5)
    
    try:
        all_results = []
        
        # Process in batches
        for i in range(0, len(all_modules), batch_size):
            batch = all_modules[i:i + batch_size]
            print(f"Processing batch {i // batch_size + 1}...")
            
            results = await executor.execute_batch(batch)
            all_results.extend(results)
            
            # Optional: delay between batches
            await asyncio.sleep(1.0)
        
        return all_results
    
    finally:
        executor.cleanup()

# Example usage
all_modules = [
    (f"module_{i}", Path(f"scripts/module_{i}.py"), None)
    for i in range(50)
]

results = asyncio.run(process_in_batches(all_modules, batch_size=10))
```

---

## Configuration

### Constructor Parameters

```python
ConcurrentExecutor(
    max_concurrent: int = 10,
    resource_manager: ResourceManager = None
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_concurrent` | `int` | `10` | Maximum concurrent executions |
| `resource_manager` | `ResourceManager` | `None` | Optional resource manager for system checks |

### Choosing max_concurrent

The optimal `max_concurrent` value depends on:

1. **System Resources**:
   - CPU cores: Start with 2x CPU cores
   - Memory: Ensure enough RAM for all concurrent processes
   - I/O: Higher for I/O-bound tasks, lower for CPU-bound

2. **Module Characteristics**:
   - CPU-intensive: Lower limit (e.g., number of cores)
   - I/O-bound: Higher limit (e.g., 2-3x cores)
   - Memory-intensive: Consider total available memory

3. **Platform**:
   - **Windows**: Test with lower values first (Windows has higher process overhead)
   - **Linux/macOS**: Can typically handle higher concurrency

**Example configurations:**

```python
# CPU-intensive modules on 8-core system
executor = ConcurrentExecutor(max_concurrent=8)

# I/O-bound modules (API calls, file downloads)
executor = ConcurrentExecutor(max_concurrent=20)

# Conservative setting for mixed workloads
executor = ConcurrentExecutor(max_concurrent=5)
```

---

## Resource Management

### Using ResourceManager

The `ResourceManager` checks CPU and memory before starting each module:

```python
from src.core.resource_manager import ResourceManager
from src.core.concurrent_executor import ConcurrentExecutor

# Configure thresholds
resource_manager = ResourceManager(
    cpu_threshold_percent=80.0,  # Max CPU usage
    memory_required_gb=4.0       # Min available memory
)

executor = ConcurrentExecutor(
    max_concurrent=10,
    resource_manager=resource_manager
)
```

### Resource Check Behavior

When a module execution starts:
1. Semaphore acquired (blocks if at limit)
2. **If resource_manager is set**: Check resources
   - If resources available: Proceed with execution
   - If insufficient: Raise `ResourceLimitException` (captured in result)
3. Execute subprocess
4. Semaphore released

### Example: Handling Resource Limits

```python
from src.core.concurrent_executor import ConcurrentExecutor
from src.core.resource_manager import ResourceManager

async def run_with_monitoring():
    resource_manager = ResourceManager(
        cpu_threshold_percent=75.0,
        memory_required_gb=8.0
    )
    
    executor = ConcurrentExecutor(
        max_concurrent=5,
        resource_manager=resource_manager
    )
    
    try:
        # Get current stats
        stats = resource_manager.get_system_stats()
        print(f"CPU: {stats['cpu_percent']}%")
        print(f"Memory Available: {stats['memory_available_gb']:.1f} GB")
        
        # Execute batch
        results = await executor.execute_batch(modules)
        
        # Check for resource-related failures
        resource_failures = [
            r for r in results
            if not r['success'] and 'resource' in r['error'].lower()
        ]
        
        if resource_failures:
            print(f"Warning: {len(resource_failures)} modules failed due to resources")
    
    finally:
        executor.cleanup()
```

---

## Error Handling

### Exception Handling Strategy

The `ConcurrentExecutor` follows a **no-raise policy** for individual module failures:

- ✅ **Exceptions are captured** in the result dictionary
- ✅ **Batch execution continues** even if some modules fail
- ✅ **All results are returned** (successful and failed)

### Result Structure

Each result is a dictionary:

```python
{
    'module_id': str,      # Module identifier
    'exit_code': int,      # Process exit code (-1 for exceptions)
    'success': bool,       # True if exit_code == 0
    'error': str | None    # Error message if failed, None if successful
}
```

### Common Error Scenarios

#### 1. Script Not Found

```python
result = await executor.execute_module(
    module_id="missing",
    script_path=Path("nonexistent.py")
)

# result['success'] == False
# result['error'] contains file not found message
```

#### 2. Resource Limit Exceeded

```python
# result['success'] == False
# result['error'] == "Insufficient system resources: CPU usage too high: 95%"
```

#### 3. Script Execution Error

```python
# Script exits with non-zero code
# result['success'] == False
# result['exit_code'] == <non-zero value>
```

### Best Practices for Error Handling

```python
async def robust_batch_execution(modules):
    executor = ConcurrentExecutor(max_concurrent=10)
    
    try:
        results = await executor.execute_batch(modules)
        
        # Categorize results
        successful = []
        failed_resource = []
        failed_execution = []
        
        for result in results:
            if result['success']:
                successful.append(result)
            elif 'resource' in result.get('error', '').lower():
                failed_resource.append(result)
            else:
                failed_execution.append(result)
        
        # Log summary
        print(f"Summary:")
        print(f"  Successful: {len(successful)}")
        print(f"  Failed (resource): {len(failed_resource)}")
        print(f"  Failed (execution): {len(failed_execution)}")
        
        # Handle failures appropriately
        if failed_resource:
            print("Warning: Some modules failed due to resource constraints")
            # Maybe retry later when resources free up
        
        if failed_execution:
            print("Error: Some modules failed during execution")
            # Log details, alert, etc.
        
        return successful, failed_resource, failed_execution
    
    finally:
        executor.cleanup()
```

---

## Best Practices

### 1. Always Cleanup

```python
# ✅ Good: Use try/finally
executor = ConcurrentExecutor()
try:
    results = await executor.execute_batch(modules)
finally:
    executor.cleanup()

# ✅ Better: Use async context manager (if implemented)
# async with ConcurrentExecutor() as executor:
#     results = await executor.execute_batch(modules)
```

### 2. Choose Appropriate Concurrency Limits

```python
# ✅ Good: Based on system and workload
import os

cpu_count = os.cpu_count() or 4

if workload_is_cpu_intensive:
    max_concurrent = cpu_count
elif workload_is_io_intensive:
    max_concurrent = cpu_count * 2
else:
    max_concurrent = cpu_count

executor = ConcurrentExecutor(max_concurrent=max_concurrent)
```

### 3. Use Resource Manager for Production

```python
# ✅ Good: Protect system from overload
from src.core.resource_manager import ResourceManager

resource_manager = ResourceManager(
    cpu_threshold_percent=80.0,
    memory_required_gb=4.0
)

executor = ConcurrentExecutor(
    max_concurrent=10,
    resource_manager=resource_manager
)
```

### 4. Log and Monitor

```python
# ✅ Good: Comprehensive logging
import logging

logger = logging.getLogger(__name__)

async def execute_with_logging(modules):
    executor = ConcurrentExecutor(max_concurrent=10)
    
    try:
        logger.info(f"Starting batch execution of {len(modules)} modules")
        
        results = await executor.execute_batch(modules)
        
        successes = sum(1 for r in results if r['success'])
        failures = len(results) - successes
        
        logger.info(f"Batch complete: {successes} succeeded, {failures} failed")
        
        # Log failures in detail
        for result in results:
            if not result['success']:
                logger.error(
                    f"Module {result['module_id']} failed: {result['error']}"
                )
        
        return results
    
    finally:
        executor.cleanup()
```

### 5. Handle Partial Failures Gracefully

```python
# ✅ Good: Continue with successful results
async def process_with_fallback(modules):
    executor = ConcurrentExecutor(max_concurrent=10)
    
    try:
        results = await executor.execute_batch(modules)
        
        successful = [r for r in results if r['success']]
        
        if len(successful) >= len(modules) * 0.5:  # At least 50% succeeded
            print(f"Proceeding with {len(successful)} successful modules")
            return successful
        else:
            print(f"Too many failures: {len(successful)}/{len(modules)} succeeded")
            return None
    
    finally:
        executor.cleanup()
```

---

## Performance Tuning

### Benchmarking

```python
import time
from src.core.concurrent_executor import ConcurrentExecutor

async def benchmark_concurrency():
    """Compare different concurrency limits."""
    modules = [(f"m{i}", Path(f"script{i}.py"), None) for i in range(50)]
    
    for max_concurrent in [5, 10, 20, 50]:
        executor = ConcurrentExecutor(max_concurrent=max_concurrent)
        
        start = time.time()
        results = await executor.execute_batch(modules)
        duration = time.time() - start
        
        successes = sum(1 for r in results if r['success'])
        
        print(f"max_concurrent={max_concurrent:2d}: "
              f"{duration:6.2f}s, {successes} succeeded")
        
        executor.cleanup()
```

### Memory Optimization

For memory-intensive modules:

```python
# Process in smaller batches
async def memory_conscious_execution(all_modules, batch_size=10):
    executor = ConcurrentExecutor(max_concurrent=5)
    
    try:
        for i in range(0, len(all_modules), batch_size):
            batch = all_modules[i:i + batch_size]
            results = await executor.execute_batch(batch)
            
            # Process/save results before next batch
            # This prevents accumulating all results in memory
            process_results(results)
            
            # Optional: Give system time to cleanup
            await asyncio.sleep(0.5)
    
    finally:
        executor.cleanup()
```

### Platform-Specific Tuning

```python
import sys
import os

def get_optimal_concurrency():
    """Get platform-specific optimal concurrency."""
    cpu_count = os.cpu_count() or 4
    
    if sys.platform == 'win32':
        # Windows: Lower concurrency due to higher process overhead
        return max(cpu_count // 2, 2)
    else:
        # Linux/macOS: Can handle higher concurrency
        return cpu_count * 2

executor = ConcurrentExecutor(max_concurrent=get_optimal_concurrency())
```

---

## Troubleshooting

### Issue: "Too many open files"

**Symptoms**: Errors about file descriptors or open files

**Solution**: Reduce `max_concurrent` or increase system limits

```python
# Reduce concurrency
executor = ConcurrentExecutor(max_concurrent=5)  # Instead of 20

# Or process in batches
async def batch_process(modules, batch_size=10):
    executor = ConcurrentExecutor(max_concurrent=5)
    try:
        for i in range(0, len(modules), batch_size):
            batch = modules[i:i + batch_size]
            await executor.execute_batch(batch)
    finally:
        executor.cleanup()
```

### Issue: System becomes unresponsive

**Symptoms**: High CPU/memory usage, system slowdown

**Solution**: Use `ResourceManager` and lower `max_concurrent`

```python
from src.core.resource_manager import ResourceManager

resource_manager = ResourceManager(
    cpu_threshold_percent=70.0,  # Lower threshold
    memory_required_gb=8.0
)

executor = ConcurrentExecutor(
    max_concurrent=5,  # Lower limit
    resource_manager=resource_manager
)
```

### Issue: Modules failing with resource errors

**Symptoms**: Many modules failing with "Insufficient system resources"

**Solutions**:
1. Lower `max_concurrent`
2. Adjust `ResourceManager` thresholds
3. Process in batches with delays

```python
# Option 1: Lower concurrency
executor = ConcurrentExecutor(max_concurrent=3)

# Option 2: Relaxed thresholds
resource_manager = ResourceManager(
    cpu_threshold_percent=90.0,  # More permissive
    memory_required_gb=2.0       # Lower requirement
)

# Option 3: Batch with delays
async def batch_with_delays(modules):
    executor = ConcurrentExecutor(max_concurrent=10)
    try:
        for i in range(0, len(modules), 10):
            batch = modules[i:i + 10]
            await executor.execute_batch(batch)
            await asyncio.sleep(2.0)  # Give system time to recover
    finally:
        executor.cleanup()
```

### Issue: Some modules hang indefinitely

**Symptoms**: Batch execution never completes

**Solution**: Add timeouts (future enhancement)

```python
# Current workaround: Set timeout in module scripts themselves
# Or implement wrapper with asyncio.wait_for

async def execute_with_timeout(executor, module_id, script_path, timeout=300):
    """Execute module with timeout (5 minutes)."""
    try:
        result = await asyncio.wait_for(
            executor.execute_module(module_id, script_path),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        return {
            'module_id': module_id,
            'exit_code': -1,
            'success': False,
            'error': f'Module execution timed out after {timeout}s'
        }
```

---

## See Also

- [Background Tasks Best Practices](BACKGROUND_TASKS_BEST_PRACTICES.md) - Overall background task patterns
- [API Reference](../API_REFERENCE.md) - API endpoint documentation
- [Windows Setup](../WINDOWS_SETUP.md) - Windows-specific configuration

---

## Changelog

### 2025-11-05
- Initial version
- Implemented Pattern 3 from Background Tasks Best Practices
- Added semaphore-based concurrency limiting
- Added ResourceManager integration
- Added comprehensive examples and troubleshooting guide
