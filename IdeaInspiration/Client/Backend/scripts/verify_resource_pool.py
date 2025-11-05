#!/usr/bin/env python3
"""Simple script to verify ResourcePool implementation.

This script demonstrates and validates the ResourcePool functionality
without requiring pytest or other dependencies.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add Backend directory to path for proper imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.core.resource_pool import ResourcePool, initialize_resource_pool, get_resource_pool, cleanup_resource_pool
from src.core.subprocess_wrapper import RunMode


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
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("ResourcePool implementation is working correctly.")
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
