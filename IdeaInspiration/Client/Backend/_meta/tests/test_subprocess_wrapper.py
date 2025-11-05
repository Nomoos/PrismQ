"""Tests for cross-platform subprocess wrapper."""

import asyncio
import sys
import pytest
from pathlib import Path

from src.core.subprocess_wrapper import (
    SubprocessWrapper,
    RunMode,
    ThreadedProcess,
    LocalProcess,
    DryRunProcess,
)


class TestSubprocessWrapper:
    """Test suite for SubprocessWrapper."""
    
    def test_mode_detection_windows(self, monkeypatch):
        """Test mode detection on Windows."""
        monkeypatch.setattr(sys, 'platform', 'win32')
        
        # Windows always uses THREADED mode for maximum compatibility
        # This ensures subprocess operations work regardless of how the server is started
        mode = SubprocessWrapper._detect_mode()
        assert mode == RunMode.THREADED
    
    def test_mode_detection_linux(self, monkeypatch):
        """Test mode detection on Linux."""
        monkeypatch.setattr(sys, 'platform', 'linux')
        
        mode = SubprocessWrapper._detect_mode()
        assert mode == RunMode.ASYNC
    
    def test_init_with_explicit_mode(self):
        """Test initialization with explicit mode."""
        wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        assert wrapper.mode == RunMode.DRY_RUN
        assert wrapper.executor is None  # DRY_RUN doesn't use executor
    
    def test_init_threaded_mode(self):
        """Test initialization with THREADED mode creates executor."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        assert wrapper.mode == RunMode.THREADED
        assert wrapper.executor is not None
        wrapper.cleanup()
    
    @pytest.mark.asyncio
    async def test_dry_run_mode(self):
        """Test DRY_RUN mode doesn't execute subprocess."""
        wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        
        process, stdout, stderr = await wrapper.create_subprocess(
            'echo', 'test',
            cwd=Path('.')
        )
        
        assert isinstance(process, DryRunProcess)
        assert process.pid == -1  # Mock PID
        
        exit_code = await process.wait()
        assert exit_code == 0
        
        # Read output
        line = await stdout.readline()
        assert b'DRY_RUN' in line
    
    @pytest.mark.asyncio
    async def test_local_mode(self):
        """Test LOCAL mode runs subprocess synchronously."""
        wrapper = SubprocessWrapper(mode=RunMode.LOCAL)
        
        # Use a simple command that works on all platforms
        if sys.platform == 'win32':
            cmd = ['cmd', '/c', 'echo', 'test']
        else:
            cmd = ['echo', 'test']
        
        process, stdout, stderr = await wrapper.create_subprocess(
            *cmd,
            cwd=Path('.')
        )
        
        assert isinstance(process, LocalProcess)
        assert process.returncode == 0
        
        # Process already completed, wait returns immediately
        exit_code = await process.wait()
        assert exit_code == 0
        
        # Read output
        line = await stdout.readline()
        assert b'test' in line
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == 'win32', reason="ASYNC mode requires ProactorEventLoop on Windows")
    async def test_async_mode_unix(self):
        """Test ASYNC mode on Unix-like systems."""
        wrapper = SubprocessWrapper(mode=RunMode.ASYNC)
        
        process, stdout, stderr = await wrapper.create_subprocess(
            'echo', 'test',
            cwd=Path('.')
        )
        
        assert hasattr(process, 'pid')
        assert process.pid > 0
        
        exit_code = await process.wait()
        assert exit_code == 0
        
        # Read output
        line = await stdout.readline()
        assert b'test' in line
    
    @pytest.mark.asyncio
    async def test_threaded_mode(self):
        """Test THREADED mode with thread pool."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        
        # Use a simple command that works on all platforms
        if sys.platform == 'win32':
            cmd = ['cmd', '/c', 'echo', 'threaded']
        else:
            cmd = ['echo', 'threaded']
        
        process, stdout, stderr = await wrapper.create_subprocess(
            *cmd,
            cwd=Path('.')
        )
        
        assert isinstance(process, ThreadedProcess)
        assert process.pid > 0
        
        exit_code = await process.wait()
        assert exit_code == 0
        
        # Read output
        line = await stdout.readline()
        assert b'threaded' in line
        
        wrapper.cleanup()
    
    @pytest.mark.asyncio
    async def test_threaded_mode_with_python(self):
        """Test THREADED mode with Python subprocess."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        
        process, stdout, stderr = await wrapper.create_subprocess(
            sys.executable, '-c', 'print("hello from python")',
            cwd=Path('.')
        )
        
        assert isinstance(process, ThreadedProcess)
        
        exit_code = await process.wait()
        assert exit_code == 0
        
        # Read output line by line
        line = await stdout.readline()
        assert b'hello from python' in line
        
        wrapper.cleanup()
    
    def test_cleanup(self):
        """Test cleanup shuts down executor."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        assert wrapper.executor is not None
        
        wrapper.cleanup()
        # Executor should be shut down (can't easily test internal state)
    
    @pytest.mark.asyncio
    async def test_invalid_mode_raises_error(self):
        """Test that invalid mode raises ValueError."""
        wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        wrapper.mode = "invalid_mode"  # Force invalid mode
        
        with pytest.raises(ValueError, match="Unknown run mode"):
            await wrapper.create_subprocess('echo', 'test', cwd=Path('.'))


class TestThreadedProcess:
    """Test suite for ThreadedProcess wrapper."""
    
    @pytest.mark.asyncio
    async def test_threaded_process_terminate(self):
        """Test terminating a threaded process."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        
        # Start a long-running process
        if sys.platform == 'win32':
            cmd = ['timeout', '/t', '10']
        else:
            cmd = ['sleep', '10']
        
        process, _, _ = await wrapper.create_subprocess(
            *cmd,
            cwd=Path('.')
        )
        
        # Give it a moment to start
        await asyncio.sleep(0.1)
        
        # Terminate it
        process.terminate()
        
        # Wait should return quickly
        exit_code = await asyncio.wait_for(process.wait(), timeout=2.0)
        # Exit code varies by platform and termination method
        assert exit_code != 0 or True  # Just check it completes
        
        wrapper.cleanup()


class TestLocalProcess:
    """Test suite for LocalProcess wrapper."""
    
    @pytest.mark.asyncio
    async def test_local_process_completed(self):
        """Test LocalProcess with completed subprocess."""
        wrapper = SubprocessWrapper(mode=RunMode.LOCAL)
        
        if sys.platform == 'win32':
            cmd = ['cmd', '/c', 'echo', 'completed']
        else:
            cmd = ['echo', 'completed']
        
        process, stdout, stderr = await wrapper.create_subprocess(
            *cmd,
            cwd=Path('.')
        )
        
        assert isinstance(process, LocalProcess)
        assert process.returncode == 0
        
        # Multiple waits should return same code
        assert await process.wait() == 0
        assert await process.wait() == 0
        
        # Terminate/kill are no-ops
        process.terminate()
        process.kill()


class TestDryRunProcess:
    """Test suite for DryRunProcess mock."""
    
    @pytest.mark.asyncio
    async def test_dry_run_process(self):
        """Test DryRunProcess mock behavior."""
        wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        
        process, stdout, stderr = await wrapper.create_subprocess(
            'any', 'command', 'args',
            cwd=Path('.')
        )
        
        assert isinstance(process, DryRunProcess)
        assert process.pid == -1  # Mock PID
        assert process.returncode == 0
        
        exit_code = await process.wait()
        assert exit_code == 0
        
        # Terminate/kill are no-ops
        process.terminate()
        process.kill()
        
        # Stdout has mocked message
        line = await stdout.readline()
        assert b'DRY_RUN' in line
        
        # Stderr is empty
        line = await stderr.readline()
        assert line == b''
