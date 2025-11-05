"""Tests for ConcurrentExecutor class.

Tests for Pattern 3 implementation from BACKGROUND_TASKS_BEST_PRACTICES.md.
"""

import asyncio
import sys
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from src.core.concurrent_executor import ConcurrentExecutor
from src.core.exceptions import ResourceLimitException
from src.core.resource_manager import ResourceManager
from src.core.subprocess_wrapper import RunMode, SubprocessWrapper


class TestConcurrentExecutor:
    """Test suite for ConcurrentExecutor."""
    
    def test_init_default_params(self):
        """Test initialization with default parameters."""
        executor = ConcurrentExecutor()
        
        assert executor.max_concurrent == 10
        assert executor.resource_manager is None
        assert executor.semaphore._value == 10
        assert executor.wrapper is not None
        
        executor.cleanup()
    
    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        resource_manager = ResourceManager(cpu_threshold_percent=70.0, memory_required_gb=2.0)
        executor = ConcurrentExecutor(max_concurrent=5, resource_manager=resource_manager)
        
        assert executor.max_concurrent == 5
        assert executor.resource_manager is resource_manager
        assert executor.semaphore._value == 5
        
        executor.cleanup()
    
    def test_init_invalid_max_concurrent(self):
        """Test that invalid max_concurrent raises ValueError."""
        with pytest.raises(ValueError, match="max_concurrent must be at least 1"):
            ConcurrentExecutor(max_concurrent=0)
        
        with pytest.raises(ValueError, match="max_concurrent must be at least 1"):
            ConcurrentExecutor(max_concurrent=-5)
    
    @pytest.mark.asyncio
    async def test_execute_module_dry_run(self):
        """Test executing a single module in DRY_RUN mode."""
        # Use DRY_RUN mode to avoid actual subprocess execution
        wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        executor = ConcurrentExecutor(max_concurrent=5)
        executor.wrapper = wrapper
        
        result = await executor.execute_module(
            module_id="test_module",
            script_path=Path("test_script.py"),
            args=["--verbose"]
        )
        
        assert result['module_id'] == "test_module"
        assert result['exit_code'] == 0
        assert result['success'] is True
        assert result['error'] is None
        
        executor.cleanup()
    
    @pytest.mark.asyncio
    async def test_execute_module_with_error(self):
        """Test that errors are captured in result dictionary."""
        executor = ConcurrentExecutor(max_concurrent=5)
        
        # Mock the wrapper to raise an exception
        executor.wrapper.create_subprocess = AsyncMock(
            side_effect=Exception("Simulated error")
        )
        
        result = await executor.execute_module(
            module_id="failing_module",
            script_path=Path("test_script.py")
        )
        
        assert result['module_id'] == "failing_module"
        assert result['exit_code'] == -1
        assert result['success'] is False
        assert "Simulated error" in result['error']
        
        executor.cleanup()
    
    @pytest.mark.asyncio
    async def test_execute_module_with_resource_check(self):
        """Test module execution with resource manager checks."""
        # Create resource manager that always allows execution
        resource_manager = Mock(spec=ResourceManager)
        resource_manager.check_resources_available = Mock(return_value=(True, None))
        
        executor = ConcurrentExecutor(max_concurrent=5, resource_manager=resource_manager)
        executor.wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        
        result = await executor.execute_module(
            module_id="test_module",
            script_path=Path("test_script.py")
        )
        
        assert result['success'] is True
        
        executor.cleanup()
    
    @pytest.mark.asyncio
    async def test_execute_module_resource_limit_exceeded(self):
        """Test that resource limit exceptions are handled correctly."""
        # Create resource manager that denies execution
        resource_manager = Mock(spec=ResourceManager)
        resource_manager.check_resources_available = Mock(
            return_value=(False, "CPU usage too high: 95%")
        )
        
        executor = ConcurrentExecutor(max_concurrent=5, resource_manager=resource_manager)
        
        result = await executor.execute_module(
            module_id="test_module",
            script_path=Path("test_script.py")
        )
        
        assert result['module_id'] == "test_module"
        assert result['exit_code'] == -1
        assert result['success'] is False
        assert "Insufficient system resources" in result['error']
        
        executor.cleanup()
    
    @pytest.mark.asyncio
    async def test_execute_batch_empty_list(self):
        """Test batch execution with empty module list."""
        executor = ConcurrentExecutor(max_concurrent=5)
        
        results = await executor.execute_batch([])
        
        assert results == []
        
        executor.cleanup()
    
    @pytest.mark.asyncio
    async def test_execute_batch_single_module(self):
        """Test batch execution with a single module."""
        executor = ConcurrentExecutor(max_concurrent=5)
        executor.wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        
        modules = [
            ("module1", Path("script1.py"), ["--arg1"])
        ]
        
        results = await executor.execute_batch(modules)
        
        assert len(results) == 1
        assert results[0]['module_id'] == "module1"
        assert results[0]['success'] is True
        
        executor.cleanup()
    
    @pytest.mark.asyncio
    async def test_execute_batch_multiple_modules(self):
        """Test batch execution with multiple modules."""
        executor = ConcurrentExecutor(max_concurrent=5)
        executor.wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        
        modules = [
            ("module1", Path("script1.py"), ["--arg1"]),
            ("module2", Path("script2.py"), None),
            ("module3", Path("script3.py"), ["--verbose"]),
        ]
        
        results = await executor.execute_batch(modules)
        
        assert len(results) == 3
        # Verify no-raise policy: all results should be dicts
        assert all(isinstance(r, dict) for r in results)
        assert all(r['success'] for r in results)
        
        module_ids = [r['module_id'] for r in results]
        assert "module1" in module_ids
        assert "module2" in module_ids
        assert "module3" in module_ids
        
        executor.cleanup()
    
    @pytest.mark.asyncio
    async def test_execute_batch_partial_failures(self):
        """Test batch execution with some modules failing."""
        executor = ConcurrentExecutor(max_concurrent=5)
        
        # Mock wrapper to fail on specific module
        async def mock_create_subprocess(*args, **kwargs):
            # Extract script path from args
            if 'script2.py' in str(args):
                raise Exception("Simulated failure for script2")
            # Return DRY_RUN process for others
            wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
            return await wrapper.create_subprocess(*args, **kwargs)
        
        executor.wrapper.create_subprocess = mock_create_subprocess
        
        modules = [
            ("module1", Path("script1.py"), None),
            ("module2", Path("script2.py"), None),
            ("module3", Path("script3.py"), None),
        ]
        
        results = await executor.execute_batch(modules)
        
        assert len(results) == 3
        
        # Check that module1 and module3 succeeded (all results are dicts)
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        assert len(successful) == 2
        assert len(failed) == 1
        assert failed[0]['module_id'] == "module2"
        
        executor.cleanup()
    
    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrency(self):
        """Test that semaphore properly limits concurrent execution."""
        max_concurrent = 2
        executor = ConcurrentExecutor(max_concurrent=max_concurrent)
        
        # Track concurrent executions
        concurrent_count = 0
        max_observed_concurrent = 0
        lock = asyncio.Lock()
        
        # Mock the subprocess creation to track concurrency
        async def mock_create_subprocess(*args, **kwargs):
            nonlocal concurrent_count, max_observed_concurrent
            
            async with lock:
                concurrent_count += 1
                max_observed_concurrent = max(max_observed_concurrent, concurrent_count)
            
            # Simulate some work
            await asyncio.sleep(0.1)
            
            async with lock:
                concurrent_count -= 1
            
            # Return DRY_RUN process
            wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
            return await wrapper.create_subprocess(*args, **kwargs)
        
        # Replace the subprocess wrapper's create_subprocess
        executor.wrapper.create_subprocess = mock_create_subprocess
        
        # Create 5 modules to ensure we exceed max_concurrent
        modules = [
            (f"module{i}", Path(f"script{i}.py"), None)
            for i in range(5)
        ]
        
        results = await executor.execute_batch(modules)
        
        assert len(results) == 5
        # The maximum concurrent should not exceed our limit
        assert max_observed_concurrent <= max_concurrent
        
        executor.cleanup()
    
    @pytest.mark.asyncio
    async def test_cleanup(self):
        """Test cleanup properly releases resources."""
        executor = ConcurrentExecutor(max_concurrent=5)
        
        # Execute a simple task
        executor.wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        await executor.execute_module("test", Path("test.py"))
        
        # Cleanup should not raise any errors
        executor.cleanup()
        
        # After cleanup, wrapper should have cleaned up its resources
        assert executor.wrapper.executor is None or not executor.wrapper.executor._shutdown
    
    @pytest.mark.asyncio
    async def test_execute_batch_return_exceptions(self):
        """Test that exceptions in batch execution are returned, not raised."""
        executor = ConcurrentExecutor(max_concurrent=5)
        
        # All modules will fail
        executor.wrapper.create_subprocess = AsyncMock(
            side_effect=Exception("All modules fail")
        )
        
        modules = [
            ("module1", Path("script1.py"), None),
            ("module2", Path("script2.py"), None),
        ]
        
        # This should not raise an exception
        results = await executor.execute_batch(modules)
        
        assert len(results) == 2
        # Verify no-raise policy: exceptions should be in error field, not raised
        assert all(isinstance(r, dict) for r in results)
        assert all(not r['success'] for r in results)
        
        executor.cleanup()
    
    @pytest.mark.asyncio
    async def test_execute_module_custom_cwd(self):
        """Test module execution with custom working directory."""
        executor = ConcurrentExecutor(max_concurrent=5)
        executor.wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        
        custom_cwd = Path("/custom/path")
        
        result = await executor.execute_module(
            module_id="test_module",
            script_path=Path("script.py"),
            args=None,
            cwd=custom_cwd
        )
        
        assert result['success'] is True
        
        executor.cleanup()
    
    @pytest.mark.asyncio
    async def test_large_batch_execution(self):
        """Test batch execution with a large number of modules."""
        executor = ConcurrentExecutor(max_concurrent=10)
        executor.wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        
        # Create 50 modules
        modules = [
            (f"module{i}", Path(f"script{i}.py"), None)
            for i in range(50)
        ]
        
        results = await executor.execute_batch(modules)
        
        assert len(results) == 50
        # Verify no-raise policy contract
        assert all(isinstance(r, dict) for r in results)
        assert all(r['success'] for r in results)
        
        executor.cleanup()


class TestConcurrentExecutorIntegration:
    """Integration tests for ConcurrentExecutor with real subprocesses."""
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Skip on Windows for CI")
    async def test_real_subprocess_execution(self, tmp_path):
        """Test execution with real Python scripts."""
        # Create a simple test script
        test_script = tmp_path / "test_script.py"
        test_script.write_text("""
import sys
print("Hello from test script")
sys.exit(0)
""")
        
        executor = ConcurrentExecutor(max_concurrent=2)
        
        result = await executor.execute_module(
            module_id="real_test",
            script_path=test_script,
            args=None
        )
        
        assert result['success'] is True
        assert result['exit_code'] == 0
        
        executor.cleanup()
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Skip on Windows for CI")
    async def test_batch_with_real_scripts(self, tmp_path):
        """Test batch execution with real Python scripts."""
        # Create multiple test scripts
        scripts = []
        for i in range(3):
            script = tmp_path / f"test_script_{i}.py"
            script.write_text(f"""
import sys
print("Hello from script {i}")
sys.exit(0)
""")
            scripts.append(script)
        
        executor = ConcurrentExecutor(max_concurrent=2)
        
        modules = [
            (f"module{i}", script, None)
            for i, script in enumerate(scripts)
        ]
        
        results = await executor.execute_batch(modules)
        
        assert len(results) == 3
        assert all(r['success'] for r in results)
        
        executor.cleanup()
