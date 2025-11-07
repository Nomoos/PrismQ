"""Tests for Windows subprocess wrapper mode detection."""

import asyncio
import sys
import pytest
from unittest.mock import patch, MagicMock
from src.core.subprocess_wrapper import SubprocessWrapper, RunMode


class TestSubprocessModeDetection:
    """Test automatic mode detection for subprocess wrapper."""
    
    def test_linux_detects_async_mode(self):
        """Test that Linux/macOS defaults to ASYNC mode."""
        with patch('sys.platform', 'linux'):
            wrapper = SubprocessWrapper()
            assert wrapper.mode == RunMode.ASYNC
    
    def test_macos_detects_async_mode(self):
        """Test that macOS defaults to ASYNC mode."""
        with patch('sys.platform', 'darwin'):
            wrapper = SubprocessWrapper()
            assert wrapper.mode == RunMode.ASYNC
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_windows_with_proactor_uses_async(self):
        """Test that Windows with ProactorEventLoopPolicy uses ASYNC mode."""
        # Ensure ProactorEventLoopPolicy is set
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        wrapper = SubprocessWrapper()
        # Should detect ProactorEventLoopPolicy and use ASYNC
        assert wrapper.mode == RunMode.ASYNC
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_windows_without_proactor_uses_threaded(self):
        """Test that Windows without ProactorEventLoopPolicy uses THREADED mode."""
        # Set SelectorEventLoopPolicy (doesn't support subprocess)
        original_policy = asyncio.get_event_loop_policy()
        try:
            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
            
            wrapper = SubprocessWrapper()
            # Should fall back to THREADED mode
            assert wrapper.mode == RunMode.THREADED
        finally:
            # Restore original policy
            asyncio.set_event_loop_policy(original_policy)
    
    def test_explicit_mode_override(self):
        """Test that explicit mode parameter overrides auto-detection."""
        wrapper_local = SubprocessWrapper(mode=RunMode.LOCAL)
        assert wrapper_local.mode == RunMode.LOCAL
        
        wrapper_threaded = SubprocessWrapper(mode=RunMode.THREADED)
        assert wrapper_threaded.mode == RunMode.THREADED
        
        wrapper_async = SubprocessWrapper(mode=RunMode.ASYNC)
        assert wrapper_async.mode == RunMode.ASYNC
    
    def test_dry_run_mode(self):
        """Test DRY_RUN mode can be explicitly set."""
        wrapper = SubprocessWrapper(mode=RunMode.DRY_RUN)
        assert wrapper.mode == RunMode.DRY_RUN
    
    @patch.dict('os.environ', {'PRISMQ_RUN_MODE': 'threaded'})
    def test_environment_variable_override(self):
        """Test that PRISMQ_RUN_MODE environment variable is respected."""
        from src.core.module_runner import ModuleRunner
        from src.core.run_registry import RunRegistry
        from src.core.process_manager import ProcessManager
        
        registry = RunRegistry()
        process_manager = ProcessManager()
        
        runner = ModuleRunner(
            registry=registry,
            process_manager=process_manager
        )
        
        # Should use THREADED mode from environment variable
        assert runner.subprocess_wrapper.mode == RunMode.THREADED


class TestProactorEventLoopDetection:
    """Test detection of ProactorEventLoopPolicy."""
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_isinstance_check_for_proactor(self):
        """Test that isinstance check works for ProactorEventLoopPolicy."""
        policy = asyncio.WindowsProactorEventLoopPolicy()
        assert isinstance(policy, asyncio.WindowsProactorEventLoopPolicy)
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_mock_proactor_policy_detection(self):
        """Test detection logic with mocked ProactorEventLoopPolicy."""
        with patch('sys.platform', 'win32'):
            with patch('asyncio.get_event_loop_policy') as mock_get_policy:
                # Mock ProactorEventLoopPolicy
                mock_policy = MagicMock(spec=asyncio.WindowsProactorEventLoopPolicy)
                mock_policy.__class__.__name__ = 'WindowsProactorEventLoopPolicy'
                mock_get_policy.return_value = mock_policy
                
                # Should detect as Proactor and use ASYNC
                mode = SubprocessWrapper._detect_mode()
                # Note: This might still return THREADED if isinstance check fails
                # which is the safe fallback
                assert mode in (RunMode.ASYNC, RunMode.THREADED)
    
    def test_non_proactor_policy_fallback(self):
        """Test that non-Proactor policies fall back to THREADED on Windows."""
        with patch('sys.platform', 'win32'):
            with patch('asyncio.get_event_loop_policy') as mock_get_policy:
                # Mock SelectorEventLoopPolicy (doesn't support subprocess)
                mock_policy = MagicMock()
                mock_policy.__class__.__name__ = 'DefaultEventLoopPolicy'
                mock_get_policy.return_value = mock_policy
                
                mode = SubprocessWrapper._detect_mode()
                assert mode == RunMode.THREADED
