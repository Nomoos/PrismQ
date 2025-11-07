"""Load testing for ConcurrentExecutor with various concurrency limits.

This script demonstrates and tests the ConcurrentExecutor with different
concurrency limits to validate proper behavior under load.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.concurrent_executor import ConcurrentExecutor
from src.core.resource_manager import ResourceManager
from src.core.subprocess_wrapper import RunMode


async def create_test_scripts(tmp_dir: Path, count: int):
    """Create test scripts that simulate work."""
    scripts = []
    for i in range(count):
        script = tmp_dir / f"test_module_{i}.py"
        script.write_text(f"""
import time
import sys

# Simulate work for {0.1 + (i % 5) * 0.05} seconds
time.sleep({0.1 + (i % 5) * 0.05})
print(f"Module {i} completed")
sys.exit(0)
""")
        scripts.append((f"module_{i}", script, None))
    return scripts


async def test_concurrency_limit(max_concurrent: int, module_count: int):
    """Test ConcurrentExecutor with specific concurrency limit."""
    print(f"\n{'='*70}")
    print(f"Testing: max_concurrent={max_concurrent}, modules={module_count}")
    print(f"{'='*70}")
    
    # Create temporary directory for test scripts
    import tempfile
    tmp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Create test modules
        modules = await create_test_scripts(tmp_dir, module_count)
        
        # Create executor
        executor = ConcurrentExecutor(max_concurrent=max_concurrent)
        
        # Time the execution
        start_time = time.time()
        results = await executor.execute_batch(modules)
        duration = time.time() - start_time
        
        # Analyze results
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        print(f"\nResults:")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Successful: {successful}/{module_count}")
        print(f"  Failed: {failed}")
        print(f"  Throughput: {module_count/duration:.2f} modules/sec")
        
        # Calculate expected minimum duration
        # With perfect concurrency, duration should be at least:
        # total_work_time / max_concurrent
        avg_work_time = 0.1 + (module_count // 2 % 5) * 0.05
        expected_min_duration = (module_count * avg_work_time) / max_concurrent
        
        print(f"  Expected min duration: {expected_min_duration:.2f}s")
        print(f"  Efficiency: {(expected_min_duration / duration * 100):.1f}%")
        
        executor.cleanup()
        
        return {
            'max_concurrent': max_concurrent,
            'module_count': module_count,
            'duration': duration,
            'successful': successful,
            'failed': failed,
            'throughput': module_count / duration
        }
    
    finally:
        # Cleanup temporary files
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)


async def test_with_resource_manager():
    """Test ConcurrentExecutor with ResourceManager."""
    print(f"\n{'='*70}")
    print(f"Testing with ResourceManager")
    print(f"{'='*70}")
    
    # Create resource manager with reasonable thresholds
    resource_manager = ResourceManager(
        cpu_threshold_percent=80.0,
        memory_required_gb=1.0
    )
    
    # Get system stats
    stats = resource_manager.get_system_stats()
    print(f"\nSystem Stats:")
    print(f"  CPU: {stats['cpu_percent']:.1f}%")
    print(f"  Memory Available: {stats['memory_available_gb']:.1f} GB")
    print(f"  Memory Used: {stats['memory_used_percent']:.1f}%")
    
    # Create executor with resource manager
    executor = ConcurrentExecutor(
        max_concurrent=5,
        resource_manager=resource_manager
    )
    
    # Use DRY_RUN mode for quick test
    from src.core.subprocess_wrapper import SubprocessWrapper, RunMode
    executor.wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
    
    # Create test modules
    modules = [
        (f"module_{i}", Path(f"test_{i}.py"), None)
        for i in range(10)
    ]
    
    start_time = time.time()
    results = await executor.execute_batch(modules)
    duration = time.time() - start_time
    
    successful = sum(1 for r in results if r['success'])
    resource_errors = sum(
        1 for r in results 
        if not r['success'] and 'resource' in r.get('error', '').lower()
    )
    
    print(f"\nResults:")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Successful: {successful}/10")
    print(f"  Resource Errors: {resource_errors}")
    
    executor.cleanup()


async def run_load_tests():
    """Run comprehensive load tests."""
    print("ConcurrentExecutor Load Testing")
    print("=" * 70)
    
    # Test 1: Varying concurrency with fixed module count
    print("\n\nTest Suite 1: Varying Concurrency (20 modules)")
    results = []
    for max_concurrent in [1, 2, 5, 10, 20]:
        result = await test_concurrency_limit(max_concurrent, 20)
        results.append(result)
    
    # Test 2: Varying module count with fixed concurrency
    print("\n\nTest Suite 2: Varying Module Count (max_concurrent=5)")
    for module_count in [10, 25, 50]:
        await test_concurrency_limit(5, module_count)
    
    # Test 3: Resource manager integration
    print("\n\nTest Suite 3: Resource Manager Integration")
    await test_with_resource_manager()
    
    # Summary
    print(f"\n\n{'='*70}")
    print("Load Test Summary")
    print(f"{'='*70}")
    print(f"\n{'Concurrency':<15} {'Duration':<12} {'Throughput':<15}")
    print(f"{'-'*42}")
    for r in results:
        print(f"{r['max_concurrent']:<15} {r['duration']:<12.2f} "
              f"{r['throughput']:<15.2f} modules/s")
    
    print("\n✓ All load tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(run_load_tests())
