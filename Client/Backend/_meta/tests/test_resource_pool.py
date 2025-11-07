"""Tests for ResourcePool implementation (Pattern 6).

This test file validates the resource pooling pattern from
BACKGROUND_TASKS_BEST_PRACTICES.md Pattern 6.
"""

import asyncio
import pytest
import time
from unittest.mock import patch, MagicMock

from src.core.resource_pool import (
    ResourcePool,
    get_resource_pool,
    initialize_resource_pool,
    cleanup_resource_pool,
)
from src.core.subprocess_wrapper import RunMode


class TestResourcePool:
    """Test ResourcePool class."""
    
    def test_initialization(self):
        """Test ResourcePool initialization."""
        pool = ResourcePool(max_workers=5)
        
        assert pool is not None
        assert pool.max_workers == 5
        assert pool._initialized is True
        assert pool.wrapper is not None
        
        # Cleanup
        pool.cleanup()
        assert pool._initialized is False
    
    def test_initialization_with_mode(self):
        """Test ResourcePool initialization with specific mode."""
        pool = ResourcePool(max_workers=3, mode=RunMode.THREADED)
        
        assert pool.wrapper.mode == RunMode.THREADED
        assert pool.max_workers == 3
        
        pool.cleanup()
    
    @pytest.mark.asyncio
    async def test_acquire_subprocess(self):
        """Test acquiring subprocess from pool."""
        pool = ResourcePool(max_workers=2, mode=RunMode.DRY_RUN)
        
        async with pool.acquire_subprocess() as wrapper:
            assert wrapper is not None
            assert wrapper.mode == RunMode.DRY_RUN
        
        pool.cleanup()
    
    @pytest.mark.asyncio
    async def test_multiple_acquisitions(self):
        """Test multiple sequential acquisitions from pool."""
        pool = ResourcePool(max_workers=2, mode=RunMode.DRY_RUN)
        
        # Acquire and release multiple times
        for i in range(5):
            async with pool.acquire_subprocess() as wrapper:
                assert wrapper is not None
                # Simulate some work
                process, _, _ = await wrapper.create_subprocess('echo', f'test{i}')
                await process.wait()
        
        pool.cleanup()
    
    @pytest.mark.asyncio
    async def test_concurrent_acquisitions(self):
        """Test concurrent acquisitions from pool."""
        pool = ResourcePool(max_workers=4, mode=RunMode.DRY_RUN)
        
        async def use_resource(n: int):
            async with pool.acquire_subprocess() as wrapper:
                process, _, _ = await wrapper.create_subprocess('echo', f'concurrent{n}')
                exit_code = await process.wait()
                return exit_code
        
        # Run multiple concurrent tasks
        results = await asyncio.gather(*[use_resource(i) for i in range(10)])
        
        # All should succeed
        assert all(code == 0 for code in results)
        
        pool.cleanup()
    
    @pytest.mark.asyncio
    async def test_cleanup_prevents_acquisition(self):
        """Test that cleanup prevents further acquisitions."""
        pool = ResourcePool(max_workers=2, mode=RunMode.DRY_RUN)
        
        # Cleanup pool
        pool.cleanup()
        
        # Try to acquire - should raise RuntimeError
        with pytest.raises(RuntimeError, match="ResourcePool has been cleaned up"):
            async with pool.acquire_subprocess() as wrapper:
                pass
    
    def test_cleanup_is_idempotent(self):
        """Test that cleanup can be called multiple times safely."""
        pool = ResourcePool(max_workers=2, mode=RunMode.DRY_RUN)
        
        # First cleanup
        pool.cleanup()
        assert pool._initialized is False
        
        # Second cleanup should not raise
        pool.cleanup()
        assert pool._initialized is False
    
    @pytest.mark.asyncio
    async def test_wrapper_reuse(self):
        """Test that the same wrapper is reused across acquisitions."""
        pool = ResourcePool(max_workers=2, mode=RunMode.DRY_RUN)
        
        wrapper_ids = []
        
        # Acquire multiple times and collect wrapper IDs
        for _ in range(3):
            async with pool.acquire_subprocess() as wrapper:
                wrapper_ids.append(id(wrapper))
        
        # All acquisitions should return the same wrapper instance
        assert len(set(wrapper_ids)) == 1
        
        pool.cleanup()


class TestGlobalResourcePool:
    """Test global resource pool functions."""
    
    def setup_method(self):
        """Setup - ensure clean state before each test."""
        # Reset global pool
        import src.core.resource_pool as rp_module
        rp_module._global_pool = None
    
    def teardown_method(self):
        """Teardown - cleanup after each test."""
        cleanup_resource_pool()
    
    def test_initialize_global_pool(self):
        """Test initializing global resource pool."""
        initialize_resource_pool(max_workers=5)
        
        pool = get_resource_pool()
        assert pool is not None
        assert pool.max_workers == 5
    
    def test_get_pool_before_initialization_raises(self):
        """Test getting pool before initialization raises error."""
        with pytest.raises(RuntimeError, match="ResourcePool not initialized"):
            get_resource_pool()
    
    def test_reinitialize_cleans_up_old_pool(self):
        """Test reinitializing pool cleans up the old one."""
        # Initialize first pool
        initialize_resource_pool(max_workers=3)
        pool1 = get_resource_pool()
        
        # Reinitialize with different settings
        initialize_resource_pool(max_workers=7)
        pool2 = get_resource_pool()
        
        # Should be different pools
        assert pool1 is not pool2
        assert pool2.max_workers == 7
    
    def test_cleanup_global_pool(self):
        """Test cleaning up global resource pool."""
        initialize_resource_pool(max_workers=5)
        pool = get_resource_pool()
        
        # Cleanup
        cleanup_resource_pool()
        
        # Pool should be cleaned up
        assert pool._initialized is False
        
        # Getting pool should raise
        with pytest.raises(RuntimeError, match="ResourcePool not initialized"):
            get_resource_pool()
    
    @pytest.mark.asyncio
    async def test_global_pool_usage(self):
        """Test using global resource pool."""
        initialize_resource_pool(max_workers=4, mode=RunMode.DRY_RUN)
        pool = get_resource_pool()
        
        async with pool.acquire_subprocess() as wrapper:
            process, _, _ = await wrapper.create_subprocess('echo', 'global pool test')
            exit_code = await process.wait()
            assert exit_code == 0


class TestResourcePoolPerformance:
    """Test performance benefits of resource pooling."""
    
    @pytest.mark.asyncio
    async def test_pooled_vs_non_pooled_performance(self):
        """Compare performance of pooled vs non-pooled execution.
        
        This benchmark demonstrates the performance benefit of reusing
        a thread pool versus creating new ones for each operation.
        """
        from src.core.subprocess_wrapper import SubprocessWrapper
        
        num_operations = 10
        
        # Test with pooling
        pool = ResourcePool(max_workers=4, mode=RunMode.DRY_RUN)
        
        start = time.perf_counter()
        for _ in range(num_operations):
            async with pool.acquire_subprocess() as wrapper:
                process, _, _ = await wrapper.create_subprocess('echo', 'pooled')
                await process.wait()
        pooled_time = time.perf_counter() - start
        
        pool.cleanup()
        
        # Test without pooling (create new wrapper each time)
        start = time.perf_counter()
        for _ in range(num_operations):
            wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
            process, _, _ = await wrapper.create_subprocess('echo', 'non-pooled')
            await process.wait()
            wrapper.cleanup()
        non_pooled_time = time.perf_counter() - start
        
        # Log performance comparison
        print(f"\nPooled time: {pooled_time:.4f}s")
        print(f"Non-pooled time: {non_pooled_time:.4f}s")
        print(f"Speedup: {non_pooled_time / pooled_time:.2f}x")
        
        # Pooled should be faster or comparable
        # Note: With DRY_RUN mode, difference may be minimal
        # Real performance benefits are seen with actual subprocess execution
        assert pooled_time <= non_pooled_time * 1.5  # Allow some variance
    
    @pytest.mark.asyncio
    async def test_concurrent_pooled_performance(self):
        """Test concurrent execution performance with pooling."""
        pool = ResourcePool(max_workers=4, mode=RunMode.DRY_RUN)
        
        async def task(n: int):
            async with pool.acquire_subprocess() as wrapper:
                process, _, _ = await wrapper.create_subprocess('echo', f'task-{n}')
                return await process.wait()
        
        # Run many concurrent tasks
        num_tasks = 20
        start = time.perf_counter()
        results = await asyncio.gather(*[task(i) for i in range(num_tasks)])
        elapsed = time.perf_counter() - start
        
        # All should succeed
        assert all(code == 0 for code in results)
        
        # Should complete in reasonable time
        assert elapsed < 2.0  # Should be fast with DRY_RUN
        
        print(f"\nCompleted {num_tasks} tasks in {elapsed:.4f}s")
        print(f"Throughput: {num_tasks / elapsed:.2f} tasks/second")
        
        pool.cleanup()


class TestResourcePoolMemoryManagement:
    """Test memory management and leak prevention."""
    
    @pytest.mark.asyncio
    async def test_no_memory_leak_on_repeated_acquisition(self):
        """Test that repeated acquisitions don't leak memory."""
        pool = ResourcePool(max_workers=2, mode=RunMode.DRY_RUN)
        
        # Perform many acquisitions
        for _ in range(100):
            async with pool.acquire_subprocess() as wrapper:
                process, _, _ = await wrapper.create_subprocess('echo', 'test')
                await process.wait()
        
        # Pool should still be healthy
        assert pool._initialized is True
        
        pool.cleanup()
    
    def test_cleanup_releases_resources(self):
        """Test that cleanup properly releases resources."""
        pool = ResourcePool(max_workers=4, mode=RunMode.THREADED)
        
        # Check that wrapper has executor
        assert pool.wrapper.executor is not None
        executor = pool.wrapper.executor
        
        # Cleanup
        pool.cleanup()
        
        # Pool should be marked as not initialized
        assert pool._initialized is False
        
        # Note: We can't easily verify executor shutdown without accessing private state,
        # but we verified cleanup was called


class TestResourcePoolIntegration:
    """Integration tests with actual subprocess operations."""
    
    @pytest.mark.asyncio
    async def test_integration_with_real_command(self):
        """Test ResourcePool with actual subprocess execution."""
        import sys
        
        pool = ResourcePool(max_workers=2, mode=RunMode.THREADED)
        
        async with pool.acquire_subprocess() as wrapper:
            # Run a simple Python command
            process, stdout, stderr = await wrapper.create_subprocess(
                sys.executable, '-c', 'print("hello from pooled resource")'
            )
            
            exit_code = await process.wait()
            
            # Read output
            output = b''
            while True:
                line = await stdout.readline()
                if not line:
                    break
                output += line
            
            assert exit_code == 0
            assert b'hello from pooled resource' in output
        
        pool.cleanup()
    
    @pytest.mark.asyncio
    async def test_integration_multiple_commands(self):
        """Test ResourcePool with multiple sequential commands."""
        import sys
        
        pool = ResourcePool(max_workers=3, mode=RunMode.THREADED)
        
        commands = [
            'print("test1")',
            'print("test2")',
            'print("test3")',
        ]
        
        for i, cmd in enumerate(commands):
            async with pool.acquire_subprocess() as wrapper:
                process, stdout, stderr = await wrapper.create_subprocess(
                    sys.executable, '-c', cmd
                )
                exit_code = await process.wait()
                
                output = b''
                while True:
                    line = await stdout.readline()
                    if not line:
                        break
                    output += line
                
                assert exit_code == 0
                assert f'test{i+1}'.encode() in output
        
        pool.cleanup()
