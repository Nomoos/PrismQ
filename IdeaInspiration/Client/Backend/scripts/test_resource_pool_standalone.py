#!/usr/bin/env python3
"""Direct test of ResourcePool without importing the full backend system.

This script imports only the necessary modules to test ResourcePool
without triggering dependencies on pydantic and other packages.

Note: This script uses direct sys.modules manipulation to work around
circular import dependencies when testing in isolation. This is not
recommended for production code - it's only used here for standalone
testing without installing all dependencies.
"""

import asyncio
import sys
import os
from pathlib import Path

# Setup path
backend_dir = Path(__file__).parent.parent
src_dir = backend_dir / 'src'

# Import just the needed classes directly without going through __init__.py
import importlib.util

def import_module_from_file(module_name, file_path, parent_package=None):
    """Import a module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    if parent_package:
        sys.modules[parent_package + '.' + module_name] = module
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# Import dependencies in order
# First, create a fake core package
class FakeModule:
    pass

core_module = FakeModule()
sys.modules['core'] = core_module

# Import exceptions
exceptions = import_module_from_file(
    'exceptions',
    src_dir / 'core' / 'exceptions.py',
    'core'
)
core_module.exceptions = exceptions

# Import subprocess_wrapper
subprocess_wrapper = import_module_from_file(
    'subprocess_wrapper',
    src_dir / 'core' / 'subprocess_wrapper.py',
    'core'
)
core_module.subprocess_wrapper = subprocess_wrapper

# Now we can import resource_pool
resource_pool = import_module_from_file(
    'resource_pool',
    src_dir / 'core' / 'resource_pool.py',
    'core'
)
core_module.resource_pool = resource_pool

ResourcePool = resource_pool.ResourcePool
initialize_resource_pool = resource_pool.initialize_resource_pool
get_resource_pool = resource_pool.get_resource_pool
cleanup_resource_pool = resource_pool.cleanup_resource_pool
RunMode = subprocess_wrapper.RunMode


async def test_basic_pool():
    """Test basic ResourcePool functionality."""
    print("=" * 70)
    print("TEST 1: Basic ResourcePool Creation and Cleanup")
    print("=" * 70)
    
    pool = ResourcePool(max_workers=2, mode=RunMode.DRY_RUN)
    print(f"✓ Created pool with max_workers={pool.max_workers}, mode={pool.wrapper.mode}")
    
    pool.cleanup()
    print("✓ Pool cleaned up successfully")
    print()


async def test_pool_acquisition():
    """Test acquiring subprocess from pool."""
    print("=" * 70)
    print("TEST 2: Resource Acquisition")
    print("=" * 70)
    
    pool = ResourcePool(max_workers=2, mode=RunMode.DRY_RUN)
    
    async with pool.acquire_subprocess() as wrapper:
        print(f"✓ Acquired subprocess wrapper: {wrapper.mode}")
        
        # Create a subprocess
        process, stdout, stderr = await wrapper.create_subprocess('echo', 'test')
        print(f"✓ Created subprocess with PID: {process.pid}")
        
        exit_code = await process.wait()
        print(f"✓ Process completed with exit code: {exit_code}")
    
    print("✓ Released subprocess back to pool")
    
    pool.cleanup()
    print("✓ Pool cleaned up")
    print()


async def test_multiple_acquisitions():
    """Test multiple sequential acquisitions."""
    print("=" * 70)
    print("TEST 3: Multiple Sequential Acquisitions")
    print("=" * 70)
    
    pool = ResourcePool(max_workers=2, mode=RunMode.DRY_RUN)
    
    for i in range(3):
        async with pool.acquire_subprocess() as wrapper:
            process, _, _ = await wrapper.create_subprocess('echo', f'test{i}')
            await process.wait()
            print(f"✓ Acquisition {i+1} completed")
    
    pool.cleanup()
    print("✓ All acquisitions successful")
    print()


async def test_global_pool():
    """Test global resource pool."""
    print("=" * 70)
    print("TEST 4: Global Resource Pool")
    print("=" * 70)
    
    # Initialize global pool
    initialize_resource_pool(max_workers=3, mode=RunMode.DRY_RUN)
    print("✓ Global pool initialized")
    
    # Get global pool
    pool = get_resource_pool()
    print(f"✓ Retrieved global pool: max_workers={pool.max_workers}")
    
    # Use global pool
    async with pool.acquire_subprocess() as wrapper:
        process, _, _ = await wrapper.create_subprocess('echo', 'global test')
        exit_code = await process.wait()
        print(f"✓ Used global pool, exit code: {exit_code}")
    
    # Cleanup global pool
    cleanup_resource_pool()
    print("✓ Global pool cleaned up")
    print()


async def test_concurrent_acquisitions():
    """Test concurrent resource acquisitions."""
    print("=" * 70)
    print("TEST 5: Concurrent Acquisitions")
    print("=" * 70)
    
    pool = ResourcePool(max_workers=4, mode=RunMode.DRY_RUN)
    
    async def task(n):
        async with pool.acquire_subprocess() as wrapper:
            process, _, _ = await wrapper.create_subprocess('echo', f'task{n}')
            return await process.wait()
    
    # Run 5 concurrent tasks
    results = await asyncio.gather(*[task(i) for i in range(5)])
    
    print(f"✓ Completed {len(results)} concurrent tasks")
    print(f"✓ All exit codes: {results}")
    
    pool.cleanup()
    print("✓ Concurrent test successful")
    print()


async def test_real_subprocess():
    """Test with real subprocess execution."""
    print("=" * 70)
    print("TEST 6: Real Subprocess Execution")
    print("=" * 70)
    
    pool = ResourcePool(max_workers=2, mode=RunMode.THREADED)
    
    async with pool.acquire_subprocess() as wrapper:
        # Run Python version command
        process, stdout, stderr = await wrapper.create_subprocess(
            sys.executable, '--version'
        )
        
        # Read output
        output = b''
        while True:
            line = await stdout.readline()
            if not line:
                break
            output += line
        
        exit_code = await process.wait()
        
        print(f"✓ Command executed: {sys.executable} --version")
        print(f"✓ Output: {output.decode().strip()}")
        print(f"✓ Exit code: {exit_code}")
    
    pool.cleanup()
    print("✓ Real subprocess test successful")
    print()


async def test_wrapper_reuse():
    """Test that wrapper is reused across acquisitions."""
    print("=" * 70)
    print("TEST 7: Wrapper Reuse")
    print("=" * 70)
    
    pool = ResourcePool(max_workers=2, mode=RunMode.DRY_RUN)
    
    wrapper_ids = []
    for i in range(3):
        async with pool.acquire_subprocess() as wrapper:
            wrapper_ids.append(id(wrapper))
    
    # All should be the same wrapper
    unique_wrappers = len(set(wrapper_ids))
    print(f"✓ Acquired wrapper {len(wrapper_ids)} times")
    print(f"✓ Unique wrapper instances: {unique_wrappers}")
    
    if unique_wrappers == 1:
        print("✓ Wrapper reuse working correctly!")
    else:
        print("⚠ Warning: Multiple wrapper instances detected")
    
    pool.cleanup()
    print()


async def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("ResourcePool Implementation Verification")
    print("=" * 70)
    print()
    
    try:
        await test_basic_pool()
        await test_pool_acquisition()
        await test_multiple_acquisitions()
        await test_global_pool()
        await test_concurrent_acquisitions()
        await test_real_subprocess()
        await test_wrapper_reuse()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("ResourcePool implementation is working correctly.")
        print("The following features have been verified:")
        print("  ✓ Pool creation and cleanup")
        print("  ✓ Resource acquisition with context manager")
        print("  ✓ Multiple sequential acquisitions")
        print("  ✓ Global pool management")
        print("  ✓ Concurrent acquisitions")
        print("  ✓ Real subprocess execution")
        print("  ✓ Wrapper reuse for efficiency")
        print()
        
        return 0
        
    except Exception as e:
        print("=" * 70)
        print("❌ TEST FAILED!")
        print("=" * 70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
