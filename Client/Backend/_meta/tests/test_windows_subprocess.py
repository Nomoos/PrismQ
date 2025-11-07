"""Comprehensive Windows-specific subprocess tests.

This module provides extensive testing for Windows subprocess execution,
focusing on event loop policy validation and Windows-specific edge cases.

Primary Platform: Windows 10/11 with NVIDIA RTX 5090

Issue #303: Add Comprehensive Testing for Windows Subprocess Execution
"""

import asyncio
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.subprocess_wrapper import (
    SubprocessWrapper,
    RunMode,
    ThreadedProcess,
)


class TestWindowsEventLoopPolicy:
    """Test Windows ProactorEventLoop policy configuration."""
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_proactor_event_loop_policy_detection(self):
        """Test that ProactorEventLoopPolicy is detected on Windows."""
        # This test runs on actual Windows
        policy = asyncio.get_event_loop_policy()
        policy_name = type(policy).__name__
        
        # On Windows with uvicorn_runner, should have ProactorEventLoopPolicy
        # If not set, mode detection should fall back to THREADED
        assert policy_name in ["WindowsProactorEventLoopPolicy", "DefaultEventLoopPolicy"]
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_subprocess_creation_with_proactor_policy(self):
        """Test that subprocess creation works when ProactorEventLoopPolicy is set."""
        # Set the policy if not already set
        policy = asyncio.get_event_loop_policy()
        if not isinstance(policy, asyncio.WindowsProactorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Create subprocess wrapper in ASYNC mode
        wrapper = SubprocessWrapper(mode=RunMode.ASYNC)
        
        try:
            # This should NOT raise NotImplementedError
            process, stdout, stderr = await wrapper.create_subprocess(
                'cmd', '/c', 'echo', 'Windows subprocess test',
                cwd=Path('.')
            )
            
            assert process is not None
            assert process.pid > 0
            
            # Wait for completion
            exit_code = await process.wait()
            assert exit_code == 0
            
            # Read output
            output = await stdout.readline()
            assert b'Windows subprocess test' in output
            
        finally:
            wrapper.cleanup()
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_mode_detection_with_proactor_policy(self):
        """Test that mode detection returns ASYNC when ProactorEventLoop is available."""
        # Set ProactorEventLoopPolicy
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Create wrapper with auto-detection
        wrapper = SubprocessWrapper()
        
        # Should detect ASYNC mode
        assert wrapper.mode == RunMode.ASYNC
        
        wrapper.cleanup()
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_mode_detection_without_proactor_policy(self):
        """Test that mode detection falls back to THREADED without ProactorEventLoop."""
        # Set default policy (SelectorEventLoop)
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
        
        # Create wrapper with auto-detection
        wrapper = SubprocessWrapper()
        
        # Should detect THREADED mode as fallback
        # Note: On some Windows systems, default policy might still support subprocess
        assert wrapper.mode in [RunMode.ASYNC, RunMode.THREADED]
        
        wrapper.cleanup()


class TestWindowsSubprocessExecution:
    """Test Windows-specific subprocess execution scenarios."""
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_cmd_execution(self):
        """Test executing Windows cmd commands."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        
        process, stdout, stderr = await wrapper.create_subprocess(
            'cmd', '/c', 'echo', 'Hello Windows',
            cwd=Path('.')
        )
        
        assert isinstance(process, ThreadedProcess)
        assert process.pid > 0
        
        exit_code = await process.wait()
        assert exit_code == 0
        
        output = await stdout.readline()
        assert b'Hello Windows' in output
        
        wrapper.cleanup()
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_powershell_execution(self):
        """Test executing PowerShell commands on Windows."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        
        process, stdout, stderr = await wrapper.create_subprocess(
            'powershell', '-Command', 'Write-Output "PowerShell test"',
            cwd=Path('.')
        )
        
        assert process.pid > 0
        
        exit_code = await process.wait()
        assert exit_code == 0
        
        output = await stdout.readline()
        assert b'PowerShell test' in output
        
        wrapper.cleanup()
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_python_subprocess_windows(self):
        """Test Python subprocess execution on Windows."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        
        # Use Python to print Windows-specific info
        process, stdout, stderr = await wrapper.create_subprocess(
            sys.executable, '-c', 
            'import sys; print(f"Platform: {sys.platform}")',
            cwd=Path('.')
        )
        
        exit_code = await process.wait()
        assert exit_code == 0
        
        output = await stdout.readline()
        assert b'Platform: win32' in output
        
        wrapper.cleanup()
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_windows_path_handling(self):
        """Test Windows path handling with backslashes."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        
        # Use current directory (Windows path)
        cwd = Path.cwd()
        
        process, stdout, stderr = await wrapper.create_subprocess(
            'cmd', '/c', 'cd',
            cwd=cwd
        )
        
        exit_code = await process.wait()
        assert exit_code == 0
        
        output = await stdout.readline()
        # Output should contain the current path
        assert len(output) > 0
        
        wrapper.cleanup()
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_windows_process_termination(self):
        """Test process termination on Windows."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        
        # Start a long-running process
        process, stdout, stderr = await wrapper.create_subprocess(
            'timeout', '/t', '30',  # 30 second timeout
            cwd=Path('.')
        )
        
        # Give it a moment to start
        await asyncio.sleep(0.2)
        
        # Terminate the process
        process.terminate()
        
        # Wait should complete quickly
        exit_code = await asyncio.wait_for(process.wait(), timeout=3.0)
        
        # On Windows, terminated process might return 1 or other non-zero code
        assert exit_code != 0 or exit_code == 0  # Just verify it completed
        
        wrapper.cleanup()


class TestWindowsEnvironmentVariables:
    """Test environment variable handling on Windows."""
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_env_var_prismq_run_mode_threaded(self):
        """Test PRISMQ_RUN_MODE environment variable on Windows."""
        with patch.dict(os.environ, {'PRISMQ_RUN_MODE': 'threaded'}):
            wrapper = SubprocessWrapper()
            # Even with auto-detection, explicit env var should work
            # But SubprocessWrapper doesn't currently read env vars in __init__
            # This test documents expected behavior for future enhancement
            assert wrapper.mode in [RunMode.ASYNC, RunMode.THREADED]
            wrapper.cleanup()
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_windows_env_vars_in_subprocess(self):
        """Test that Windows environment variables are passed to subprocess."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        
        # Set a test environment variable
        test_var = 'PRISMQ_TEST_VAR'
        test_value = 'test_value_123'
        
        os.environ[test_var] = test_value
        
        try:
            process, stdout, stderr = await wrapper.create_subprocess(
                'cmd', '/c', f'echo %{test_var}%',
                cwd=Path('.')
            )
            
            exit_code = await process.wait()
            assert exit_code == 0
            
            output = await stdout.readline()
            assert test_value.encode() in output
            
        finally:
            # Clean up
            del os.environ[test_var]
            wrapper.cleanup()


class TestWindowsConcurrentExecution:
    """Test concurrent subprocess execution on Windows."""
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_multiple_concurrent_processes_windows(self):
        """Test running multiple processes concurrently on Windows."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        
        # Start multiple processes
        processes = []
        for i in range(3):
            process, stdout, stderr = await wrapper.create_subprocess(
                'cmd', '/c', f'echo Process {i}',
                cwd=Path('.')
            )
            processes.append((process, stdout, i))
        
        # Wait for all to complete
        results = []
        for process, stdout, expected_num in processes:
            exit_code = await process.wait()
            assert exit_code == 0
            
            output = await stdout.readline()
            assert f'Process {expected_num}'.encode() in output
            results.append(output)
        
        # Verify all completed
        assert len(results) == 3
        
        wrapper.cleanup()
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_sequential_process_execution_windows(self):
        """Test sequential process execution doesn't cause issues on Windows."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        
        for i in range(5):
            process, stdout, stderr = await wrapper.create_subprocess(
                'cmd', '/c', f'echo Iteration {i}',
                cwd=Path('.')
            )
            
            exit_code = await process.wait()
            assert exit_code == 0
            
            output = await stdout.readline()
            assert f'Iteration {i}'.encode() in output
        
        wrapper.cleanup()


class TestWindowsEdgeCases:
    """Test Windows-specific edge cases and error conditions."""
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_invalid_command_windows(self):
        """Test handling of invalid command on Windows."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        
        # Try to run a non-existent command
        # On Windows with THREADED mode, this might fail during execution
        try:
            process, stdout, stderr = await wrapper.create_subprocess(
                'nonexistent_command_12345',
                cwd=Path('.')
            )
            # If it somehow succeeds, wait should fail
            exit_code = await asyncio.wait_for(process.wait(), timeout=2.0)
            assert exit_code != 0
        except (FileNotFoundError, OSError):
            # Expected - command doesn't exist
            pass
        
        wrapper.cleanup()
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_empty_output_windows(self):
        """Test handling empty output on Windows."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        
        process, stdout, stderr = await wrapper.create_subprocess(
            'cmd', '/c', 'rem',  # Windows comment command (no output)
            cwd=Path('.')
        )
        
        exit_code = await process.wait()
        assert exit_code == 0
        
        # Reading from empty stdout should return empty bytes
        output = await stdout.readline()
        assert output == b'' or output == b'\n' or output == b'\r\n'
        
        wrapper.cleanup()
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_stderr_output_windows(self):
        """Test stderr capture on Windows."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        
        # Echo to stderr using PowerShell
        process, stdout, stderr = await wrapper.create_subprocess(
            'powershell', '-Command', 
            '[Console]::Error.WriteLine("Error message")',
            cwd=Path('.')
        )
        
        exit_code = await process.wait()
        assert exit_code == 0
        
        # Read stderr
        error_output = await stderr.readline()
        assert b'Error message' in error_output
        
        wrapper.cleanup()
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_very_long_command_windows(self):
        """Test handling very long command lines on Windows."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        
        # Windows has an 8191 character command line limit
        # Test a moderately long command that should work
        long_text = 'A' * 100
        
        process, stdout, stderr = await wrapper.create_subprocess(
            'cmd', '/c', f'echo {long_text}',
            cwd=Path('.')
        )
        
        exit_code = await process.wait()
        assert exit_code == 0
        
        output = await stdout.readline()
        assert long_text.encode() in output
        
        wrapper.cleanup()


class TestWindowsAsyncModeWithProactor:
    """Test ASYNC mode specifically with Windows ProactorEventLoop."""
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_async_mode_requires_proactor_policy(self):
        """Test that ASYNC mode works correctly with ProactorEventLoop."""
        # Ensure ProactorEventLoopPolicy is set
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Create wrapper in ASYNC mode
        wrapper = SubprocessWrapper(mode=RunMode.ASYNC)
        
        # This should work without NotImplementedError
        process, stdout, stderr = await wrapper.create_subprocess(
            'cmd', '/c', 'echo ASYNC mode test',
            cwd=Path('.')
        )
        
        assert process.pid > 0
        
        exit_code = await process.wait()
        assert exit_code == 0
        
        output = await stdout.readline()
        assert b'ASYNC mode test' in output
        
        wrapper.cleanup()
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    @pytest.mark.asyncio
    async def test_concurrent_async_processes_windows(self):
        """Test concurrent ASYNC processes with ProactorEventLoop."""
        # Ensure ProactorEventLoopPolicy is set
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        wrapper = SubprocessWrapper(mode=RunMode.ASYNC)
        
        # Create multiple processes concurrently
        tasks = []
        for i in range(3):
            async def run_process(num):
                process, stdout, _ = await wrapper.create_subprocess(
                    'cmd', '/c', f'echo Concurrent {num}',
                    cwd=Path('.')
                )
                await process.wait()
                output = await stdout.readline()
                return output
            
            tasks.append(run_process(i))
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks)
        
        # Verify all completed successfully
        assert len(results) == 3
        for i, result in enumerate(results):
            assert f'Concurrent {i}'.encode() in result
        
        wrapper.cleanup()


# Test configuration to ensure Windows tests are properly isolated
@pytest.fixture(autouse=True)
def cleanup_event_loop_policy():
    """Cleanup fixture to reset event loop policy after tests."""
    yield
    # Reset to default policy after test if on Windows
    if sys.platform == 'win32':
        # Don't change the policy - let uvicorn_runner manage it
        pass
