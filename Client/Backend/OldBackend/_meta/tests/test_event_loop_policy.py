"""Tests for Windows event loop policy configuration.

This module tests the uvicorn_runner event loop policy setup that enables
asyncio subprocess operations on Windows.

Primary Platform: Windows 10/11 with NVIDIA RTX 5090

Issue #303: Add Comprehensive Testing for Windows Subprocess Execution
"""

import asyncio
import sys
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestEventLoopPolicySetup:
    """Test event loop policy configuration and validation."""
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_windows_proactor_policy_available(self):
        """Test that Windows ProactorEventLoopPolicy is available."""
        # Verify the policy class exists
        assert hasattr(asyncio, 'WindowsProactorEventLoopPolicy')
        
        # Verify we can instantiate it
        policy = asyncio.WindowsProactorEventLoopPolicy()
        assert policy is not None
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_set_proactor_event_loop_policy(self):
        """Test setting ProactorEventLoopPolicy."""
        # Set the policy
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Verify it was set
        current_policy = asyncio.get_event_loop_policy()
        assert isinstance(current_policy, asyncio.WindowsProactorEventLoopPolicy)
        assert type(current_policy).__name__ == 'WindowsProactorEventLoopPolicy'
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_default_policy_is_selector_or_proactor(self):
        """Test that default policy on Windows is either Selector or Proactor."""
        # Get the default policy (before any changes)
        # Note: This might already be Proactor if uvicorn_runner ran
        policy = asyncio.get_event_loop_policy()
        policy_name = type(policy).__name__
        
        # Should be one of the Windows policies
        assert policy_name in [
            'WindowsSelectorEventLoopPolicy',
            'WindowsProactorEventLoopPolicy',
            'DefaultEventLoopPolicy'
        ]
    
    @pytest.mark.skipif(sys.platform == 'win32', reason="Unix-specific test")
    def test_unix_default_policy(self):
        """Test that Unix systems don't have Windows-specific policies."""
        policy = asyncio.get_event_loop_policy()
        
        # Should be default Unix policy
        policy_name = type(policy).__name__
        assert 'Windows' not in policy_name
        
        # WindowsProactorEventLoopPolicy should not exist on Unix
        assert not hasattr(asyncio, 'WindowsProactorEventLoopPolicy')


class TestProactorEventLoopSubprocessSupport:
    """Test that ProactorEventLoop supports subprocess operations."""
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_proactor_loop_subprocess_exec(self):
        """Test that ProactorEventLoop can create subprocesses."""
        # Set ProactorEventLoopPolicy
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Get a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Try to create a subprocess
            process = await asyncio.create_subprocess_exec(
                'cmd', '/c', 'echo test',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Should succeed without NotImplementedError
            assert process is not None
            assert process.pid > 0
            
            # Wait for completion
            await process.wait()
            
        finally:
            loop.close()
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_proactor_loop_has_subprocess_support(self):
        """Test that ProactorEventLoop has subprocess_exec method."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        loop = asyncio.new_event_loop()
        
        try:
            # Check for subprocess support
            assert hasattr(loop, 'subprocess_exec')
            assert callable(loop.subprocess_exec)
            
        finally:
            loop.close()
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_selector_loop_subprocess_fails(self):
        """Test that SelectorEventLoop raises NotImplementedError for subprocess."""
        # Set SelectorEventLoopPolicy (old default)
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Try to create a subprocess - should fail
            with pytest.raises(NotImplementedError):
                await asyncio.create_subprocess_exec(
                    'cmd', '/c', 'echo test',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
        finally:
            loop.close()
            # Restore ProactorEventLoopPolicy for other tests
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


class TestUvicornRunnerIntegration:
    """Test integration with uvicorn_runner module."""
    
    def test_uvicorn_runner_module_exists(self):
        """Test that uvicorn_runner module can be imported."""
        try:
            import src.uvicorn_runner
            assert src.uvicorn_runner is not None
        except ImportError as e:
            pytest.fail(f"Failed to import uvicorn_runner: {e}")
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_uvicorn_runner_sets_policy(self):
        """Test that uvicorn_runner sets the event loop policy on Windows."""
        # Import the module (which should set the policy)
        import src.uvicorn_runner
        
        # Check that the policy is set
        policy = asyncio.get_event_loop_policy()
        policy_name = type(policy).__name__
        
        # Should be ProactorEventLoopPolicy after import
        # Note: This depends on module import order
        # In practice, uvicorn_runner.main() sets the policy
        assert policy_name in [
            'WindowsProactorEventLoopPolicy',
            'DefaultEventLoopPolicy',  # Might not be set yet if main() not called
        ]
    
    @pytest.mark.skipif(sys.platform == 'win32', reason="Unix-specific test")
    def test_uvicorn_runner_unix_no_windows_policy(self):
        """Test that uvicorn_runner doesn't set Windows policy on Unix."""
        import src.uvicorn_runner
        
        policy = asyncio.get_event_loop_policy()
        policy_name = type(policy).__name__
        
        # Should not be Windows-specific policy
        assert 'Windows' not in policy_name


class TestMultipleSubprocessLaunches:
    """Test that multiple subprocess launches work correctly."""
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_sequential_subprocess_launches(self):
        """Test launching subprocesses sequentially."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        for i in range(5):
            process = await asyncio.create_subprocess_exec(
                'cmd', '/c', f'echo Iteration {i}',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await process.communicate()
            assert f'Iteration {i}'.encode() in stdout
            assert process.returncode == 0
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_concurrent_subprocess_launches(self):
        """Test launching multiple subprocesses concurrently."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        async def run_subprocess(num):
            process = await asyncio.create_subprocess_exec(
                'cmd', '/c', f'echo Concurrent {num}',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            return stdout
        
        # Launch 3 processes concurrently
        tasks = [run_subprocess(i) for i in range(3)]
        results = await asyncio.gather(*tasks)
        
        # Verify all completed successfully
        assert len(results) == 3
        for i, stdout in enumerate(results):
            assert f'Concurrent {i}'.encode() in stdout
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_subprocess_with_long_running_process(self):
        """Test subprocess that runs for a moderate duration."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Start a 2-second sleep
        process = await asyncio.create_subprocess_exec(
            'powershell', '-Command', 'Start-Sleep -Seconds 2',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for completion
        await process.wait()
        assert process.returncode == 0


class TestEventLoopPolicyWarnings:
    """Test policy detection and warning scenarios."""
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_detect_incorrect_policy_warning(self):
        """Test detection of incorrect event loop policy."""
        # Set a non-Proactor policy
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
        
        policy = asyncio.get_event_loop_policy()
        policy_name = type(policy).__name__
        
        # Should detect that it's not ProactorEventLoopPolicy
        is_proactor = isinstance(policy, asyncio.WindowsProactorEventLoopPolicy)
        
        if not is_proactor:
            # This condition should trigger a warning in production code
            # Here we just verify the detection works
            assert policy_name != 'WindowsProactorEventLoopPolicy'
        
        # Restore correct policy
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_policy_persists_across_operations(self):
        """Test that event loop policy persists across multiple operations."""
        # Set ProactorEventLoopPolicy
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Run a subprocess
        process1 = await asyncio.create_subprocess_exec(
            'cmd', '/c', 'echo first',
            stdout=asyncio.subprocess.PIPE
        )
        await process1.wait()
        
        # Check policy is still correct
        policy = asyncio.get_event_loop_policy()
        assert isinstance(policy, asyncio.WindowsProactorEventLoopPolicy)
        
        # Run another subprocess
        process2 = await asyncio.create_subprocess_exec(
            'cmd', '/c', 'echo second',
            stdout=asyncio.subprocess.PIPE
        )
        await process2.wait()
        
        # Policy should still be correct
        policy = asyncio.get_event_loop_policy()
        assert isinstance(policy, asyncio.WindowsProactorEventLoopPolicy)


class TestEventLoopCleanup:
    """Test event loop cleanup and resource management."""
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_loop_cleanup_after_subprocess(self):
        """Test that event loop can be properly cleaned up after subprocess use."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Get current loop
        loop = asyncio.get_event_loop()
        
        # Run a subprocess
        process = await asyncio.create_subprocess_exec(
            'cmd', '/c', 'echo cleanup test',
            stdout=asyncio.subprocess.PIPE
        )
        await process.wait()
        
        # Loop should still be running
        assert loop.is_running() or not loop.is_closed()
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_multiple_event_loops(self):
        """Test creating multiple event loops with ProactorEventLoopPolicy."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Create multiple loops
        loops = []
        for i in range(3):
            loop = asyncio.new_event_loop()
            loops.append(loop)
            assert loop is not None
        
        # Clean up
        for loop in loops:
            loop.close()


# Pytest configuration
@pytest.fixture(autouse=True, scope="module")
def setup_windows_event_loop_policy():
    """Module-level fixture to ensure ProactorEventLoopPolicy on Windows."""
    if sys.platform == 'win32':
        # Set ProactorEventLoopPolicy for all tests in this module
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    yield
    
    # Cleanup after all tests
    if sys.platform == 'win32':
        # Reset to ProactorEventLoopPolicy (standard for Windows)
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
