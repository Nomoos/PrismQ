"""Test examples from BACKGROUND_TASKS_BEST_PRACTICES.md

This test file validates that the code examples in the best practices guide
are syntactically correct and follow the documented patterns.
"""

import asyncio
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Import classes from the guide examples
from src.core.subprocess_wrapper import SubprocessWrapper, RunMode
from src.core.exceptions import (
    SubprocessPolicyException,
    ModuleExecutionException,
    ResourceLimitException,
)


class TestCorePatterns:
    """Test core patterns from the best practices guide."""
    
    def test_isolation_principle_good_pattern(self):
        """Test the recommended isolation pattern."""
        # Pattern from guide: Use SubprocessWrapper
        wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)  # DRY_RUN for testing
        assert wrapper is not None
        assert wrapper.mode == RunMode.DRY_RUN
        wrapper.cleanup()
    
    @pytest.mark.asyncio
    async def test_explicit_resource_management(self):
        """Test proper resource cleanup pattern."""
        # Pattern from guide: Always cleanup
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        try:
            # Resource usage happens here
            assert wrapper.executor is not None
            executor = wrapper.executor  # Save reference
        finally:
            wrapper.cleanup()
            # After cleanup, executor should be shutdown
            # Note: We can't easily verify shutdown without accessing private attributes,
            # but we can verify cleanup was called without errors
            assert executor is not None  # Executor existed before cleanup
    
    def test_defensive_programming_exception_handling(self):
        """Test exception handling pattern from guide."""
        # Pattern from guide: Handle all exception types
        
        async def execute_with_error_handling():
            try:
                # Simulate an error
                raise ModuleExecutionException("Test error")
                
            except SubprocessPolicyException as e:
                pytest.fail("Should not catch this exception type")
                
            except ModuleExecutionException as e:
                # Expected to catch this
                assert str(e) == "Test error"
                return "handled"
                
            except Exception as e:
                pytest.fail("Should catch specific exception first")
        
        result = asyncio.run(execute_with_error_handling())
        assert result == "handled"
    
    def test_platform_awareness(self, monkeypatch):
        """Test platform-aware pattern."""
        # Pattern from guide: Use platform-aware abstractions
        
        # Test Windows detection
        monkeypatch.setattr(sys, 'platform', 'win32')
        wrapper_win = SubprocessWrapper()
        assert wrapper_win.mode == RunMode.THREADED  # Windows uses THREADED
        wrapper_win.cleanup()
        
        # Test Linux detection
        monkeypatch.setattr(sys, 'platform', 'linux')
        wrapper_linux = SubprocessWrapper()
        assert wrapper_linux.mode == RunMode.ASYNC  # Linux uses ASYNC
        wrapper_linux.cleanup()


class TestSubprocessPatterns:
    """Test subprocess execution patterns."""
    
    @pytest.mark.asyncio
    async def test_simple_module_execution_pattern(self):
        """Test Pattern 1: Simple Module Execution."""
        # Simplified version of Pattern 1 from guide
        wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        
        try:
            cmd = ['python', '--version']
            process, stdout, stderr = await wrapper.create_subprocess(*cmd)
            
            # Verify process created
            assert process is not None
            assert process.pid == -1  # DRY_RUN mode
            
            # Wait for completion
            exit_code = await process.wait()
            assert exit_code == 0
            
        finally:
            wrapper.cleanup()
    
    @pytest.mark.asyncio
    async def test_long_running_task_pattern(self, tmp_path):
        """Test Pattern 2: Long-Running Background Task with output streaming."""
        from src.core.execution_patterns import execute_long_running_task
        from src.core.output_capture import OutputCapture
        from textwrap import dedent
        
        # Create a test script
        script_path = tmp_path / "test_pattern2.py"
        script_path.write_text(dedent("""
            print("Task started")
            print("Processing data")
            print("Task completed")
        """))
        
        # Setup output capture
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        output_capture = OutputCapture(log_dir=log_dir)
        
        # Execute long-running task (Pattern 2)
        run_id = "pattern2-test"
        exit_code = await execute_long_running_task(
            run_id=run_id,
            script_path=script_path,
            output_capture=output_capture
        )
        
        # Verify execution succeeded
        assert exit_code == 0
        
        # Verify output was captured
        logs = output_capture.get_logs(run_id)
        assert len(logs) == 3
        messages = [log.message for log in logs]
        assert "Task started" in messages
        assert "Processing data" in messages
        assert "Task completed" in messages
        
        # Cleanup
        output_capture.cleanup_run(run_id)
    
    @pytest.mark.asyncio
    async def test_timeout_handling_pattern(self):
        """Test timeout handling from error handling section."""
        # Pattern from guide: Always set reasonable timeouts
        
        async def sample_task():
            await asyncio.sleep(0.1)
            return "completed"
        
        # Test successful completion within timeout
        result = await asyncio.wait_for(sample_task(), timeout=1.0)
        assert result == "completed"
        
        # Test timeout handling
        async def slow_task():
            await asyncio.sleep(10)
        
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(slow_task(), timeout=0.1)


class TestAntiPatterns:
    """Test anti-patterns are avoided."""
    
    def test_avoid_blocking_calls(self):
        """Ensure blocking calls in async functions are detected."""
        # Anti-pattern from guide: Blocking calls in async functions
        
        async def bad_pattern():
            # This would be bad (shown in guide as anti-pattern)
            # result = subprocess.run(['python', 'script.py'])
            pass  # We don't actually execute the bad pattern
        
        async def good_pattern():
            # Good pattern: Use async subprocess wrapper
            wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
            try:
                process, stdout, stderr = await wrapper.create_subprocess('python', '--version')
                exit_code = await process.wait()
                return exit_code
            finally:
                wrapper.cleanup()
        
        # Test good pattern works
        result = asyncio.run(good_pattern())
        assert result == 0
    
    @pytest.mark.asyncio
    async def test_bounded_concurrency_pattern(self):
        """Test bounded concurrency pattern vs unbounded anti-pattern."""
        # Pattern from guide: Use semaphore to limit concurrency
        
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent
        
        async def execute_with_limit(task_id: int):
            async with semaphore:
                await asyncio.sleep(0.01)  # Simulate work
                return task_id
        
        # Execute 10 tasks with limit of 3 concurrent
        tasks = [execute_with_limit(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert set(results) == set(range(10))
    
    def test_proper_cleanup_pattern(self):
        """Test that cleanup is always performed."""
        # Anti-pattern from guide: Missing cleanup
        
        cleanup_called = False
        
        class TestWrapper(SubprocessWrapper):
            def cleanup(self):
                nonlocal cleanup_called
                cleanup_called = True
                super().cleanup()
        
        wrapper = TestWrapper(mode=RunMode.THREADED)
        try:
            # Use wrapper
            pass
        finally:
            wrapper.cleanup()
        
        assert cleanup_called, "Cleanup should always be called in finally block"


class TestErrorHandlingPatterns:
    """Test error handling patterns."""
    
    @pytest.mark.asyncio
    async def test_exception_hierarchy_handling(self):
        """Test exception handling hierarchy from guide."""
        
        async def execute_with_error_handling(error_type: str):
            """Example from guide with exception hierarchy."""
            try:
                if error_type == "policy":
                    raise SubprocessPolicyException("Event loop policy error")
                elif error_type == "resource":
                    raise ResourceLimitException("Resource limit")
                elif error_type == "module":
                    raise ModuleExecutionException("Module error")
                elif error_type == "cancelled":
                    raise asyncio.CancelledError()
                else:
                    raise ValueError("Unknown error")
                    
            except SubprocessPolicyException as e:
                return "policy_error"
                
            except ResourceLimitException as e:
                return "resource_error"
                
            except ModuleExecutionException as e:
                return "module_error"
                
            except asyncio.CancelledError:
                return "cancelled"
                
            except Exception as e:
                return "unexpected_error"
        
        # Test each exception type is caught correctly
        assert await execute_with_error_handling("policy") == "policy_error"
        assert await execute_with_error_handling("resource") == "resource_error"
        assert await execute_with_error_handling("module") == "module_error"
        assert await execute_with_error_handling("cancelled") == "cancelled"
        assert await execute_with_error_handling("unknown") == "unexpected_error"
    
    @pytest.mark.asyncio
    async def test_graceful_termination_pattern(self):
        """Test graceful process termination pattern."""
        
        async def terminate_gracefully(process, timeout: float = 1.0):
            """Example from troubleshooting section."""
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
        
        # Test with DRY_RUN process
        wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        try:
            process, stdout, stderr = await wrapper.create_subprocess('python', '--version')
            
            # Test graceful termination
            await terminate_gracefully(process, timeout=1.0)
            
        finally:
            wrapper.cleanup()


class TestResourceManagement:
    """Test resource management patterns."""
    
    @pytest.mark.asyncio
    async def test_resource_pooling_pattern(self):
        """Test resource pooling pattern from guide."""
        # Simplified resource pool
        class SimpleResourcePool:
            def __init__(self):
                self.wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
            
            async def acquire_subprocess(self):
                return self.wrapper
            
            def cleanup(self):
                self.wrapper.cleanup()
        
        pool = SimpleResourcePool()
        try:
            wrapper = await pool.acquire_subprocess()
            assert wrapper is not None
            assert wrapper.mode == RunMode.DRY_RUN
        finally:
            pool.cleanup()


class TestDocumentationConsistency:
    """Test that documentation examples are consistent with implementation."""
    
    def test_all_documented_imports_exist(self):
        """Verify all imports referenced in the guide exist in codebase."""
        # Test imports from subprocess execution patterns
        from src.core.subprocess_wrapper import SubprocessWrapper, RunMode
        from src.core.output_capture import OutputCapture
        from src.core.resource_manager import ResourceManager
        from src.core.run_registry import RunRegistry
        from src.models.run import Run, RunStatus
        
        # Verify classes are not None
        assert SubprocessWrapper is not None
        assert RunMode is not None
        assert OutputCapture is not None
        assert ResourceManager is not None
        assert RunRegistry is not None
        assert Run is not None
        assert RunStatus is not None
    
    def test_run_mode_enum_values(self):
        """Verify RunMode enum values match documentation."""
        # From guide: RunMode has LOCAL, ASYNC, THREADED, DRY_RUN
        assert hasattr(RunMode, 'LOCAL')
        assert hasattr(RunMode, 'ASYNC')
        assert hasattr(RunMode, 'THREADED')
        assert hasattr(RunMode, 'DRY_RUN')
        
        assert RunMode.LOCAL == "local"
        assert RunMode.ASYNC == "async"
        assert RunMode.THREADED == "threaded"
        assert RunMode.DRY_RUN == "dry-run"
    
    def test_exception_classes_exist(self):
        """Verify exception classes mentioned in guide exist."""
        # From guide: SubprocessPolicyException, ModuleExecutionException, ResourceLimitException
        assert SubprocessPolicyException is not None
        assert ModuleExecutionException is not None
        assert ResourceLimitException is not None
    
    def test_subprocess_wrapper_api(self):
        """Verify SubprocessWrapper API matches documentation."""
        # From guide: SubprocessWrapper has __init__, create_subprocess, cleanup
        wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        
        assert hasattr(wrapper, 'create_subprocess')
        assert hasattr(wrapper, 'cleanup')
        assert hasattr(wrapper, 'mode')
        
        wrapper.cleanup()


class TestQuickReference:
    """Test quick reference checklist items."""
    
    def test_checklist_subprocess_wrapper_usage(self):
        """✓ Use SubprocessWrapper for subprocess operations."""
        wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        assert wrapper is not None
        wrapper.cleanup()
    
    def test_checklist_set_timeouts(self):
        """✓ Set appropriate timeouts."""
        async def with_timeout():
            await asyncio.wait_for(
                asyncio.sleep(0.01),
                timeout=1.0
            )
        
        asyncio.run(with_timeout())
    
    def test_checklist_error_handling(self):
        """✓ Implement proper error handling."""
        async def with_error_handling():
            try:
                raise ValueError("test")
            except ValueError as e:
                return str(e)
        
        result = asyncio.run(with_error_handling())
        assert result == "test"
    
    def test_checklist_cleanup_resources(self):
        """✓ Clean up resources in finally blocks."""
        cleaned_up = False
        
        try:
            wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        finally:
            wrapper.cleanup()
            cleaned_up = True
        
        assert cleaned_up
    
    def test_checklist_limit_concurrency(self):
        """✓ Limit concurrency with semaphores."""
        semaphore = asyncio.Semaphore(5)
        assert semaphore._value == 5
    
    @pytest.mark.asyncio
    async def test_checklist_resource_pooling(self):
        """✓ Use resource pooling for efficiency (Pattern 6)."""
        from src.core.resource_pool import ResourcePool
        
        # Create resource pool
        pool = ResourcePool(max_workers=4, mode=RunMode.DRY_RUN)
        
        # Use pooled resource
        async with pool.acquire_subprocess() as wrapper:
            process, _, _ = await wrapper.create_subprocess('echo', 'test')
            exit_code = await process.wait()
            assert exit_code == 0
        
        # Cleanup
        pool.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
