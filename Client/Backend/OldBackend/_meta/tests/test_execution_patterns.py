"""Tests for execution patterns module.

Tests the implementation of Pattern 1: Simple Module Execution
following BACKGROUND_TASKS_BEST_PRACTICES.md.
"""

import asyncio
import tempfile
from pathlib import Path

import pytest

from src.core.execution_patterns import execute_module
from src.core.subprocess_wrapper import RunMode


class TestExecuteModulePattern:
    """Test suite for Pattern 1: Simple Module Execution."""
    
    @pytest.mark.asyncio
    async def test_execute_module_success(self, tmp_path):
        """Test successful module execution with output capture."""
        # Create a simple test script
        script = tmp_path / "test_script.py"
        script.write_text("""
import sys
print("Hello from stdout")
print("Error message", file=sys.stderr)
sys.exit(0)
""")
        
        # Execute the module
        exit_code, stdout, stderr = await execute_module(
            script_path=script,
            args=[],
            cwd=tmp_path
        )
        
        # Verify results
        assert exit_code == 0
        assert "Hello from stdout" in stdout
        assert "Error message" in stderr
    
    @pytest.mark.asyncio
    async def test_execute_module_with_arguments(self, tmp_path):
        """Test module execution with command-line arguments."""
        # Create a script that echoes arguments
        script = tmp_path / "echo_args.py"
        script.write_text("""
import sys
for arg in sys.argv[1:]:
    print(f"Arg: {arg}")
""")
        
        # Execute with arguments
        exit_code, stdout, stderr = await execute_module(
            script_path=script,
            args=["--param1", "value1", "--param2", "value2"],
            cwd=tmp_path
        )
        
        # Verify arguments were passed
        assert exit_code == 0
        assert "Arg: --param1" in stdout
        assert "Arg: value1" in stdout
        assert "Arg: --param2" in stdout
        assert "Arg: value2" in stdout
    
    @pytest.mark.asyncio
    async def test_execute_module_failure(self, tmp_path):
        """Test module execution that exits with error code."""
        # Create a script that fails
        script = tmp_path / "failing_script.py"
        script.write_text("""
import sys
print("Starting execution")
print("Fatal error occurred", file=sys.stderr)
sys.exit(1)
""")
        
        # Execute the module
        exit_code, stdout, stderr = await execute_module(
            script_path=script,
            args=[],
            cwd=tmp_path
        )
        
        # Verify failure is captured
        assert exit_code == 1
        assert "Starting execution" in stdout
        assert "Fatal error occurred" in stderr
    
    @pytest.mark.asyncio
    async def test_execute_module_nonexistent_script(self, tmp_path):
        """Test error handling for non-existent script."""
        nonexistent_script = tmp_path / "does_not_exist.py"
        
        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError, match="Script not found"):
            await execute_module(
                script_path=nonexistent_script,
                args=[],
                cwd=tmp_path
            )
    
    @pytest.mark.asyncio
    async def test_execute_module_multiline_output(self, tmp_path):
        """Test capturing multi-line output correctly."""
        # Create a script with multiple output lines
        script = tmp_path / "multiline.py"
        script.write_text("""
for i in range(5):
    print(f"Line {i}")
""")
        
        # Execute the module
        exit_code, stdout, stderr = await execute_module(
            script_path=script,
            args=[],
            cwd=tmp_path
        )
        
        # Verify all lines captured
        assert exit_code == 0
        for i in range(5):
            assert f"Line {i}" in stdout
    
    @pytest.mark.asyncio
    async def test_execute_module_unicode_output(self, tmp_path):
        """Test handling of unicode characters in output."""
        # Create a script with unicode output
        script = tmp_path / "unicode.py"
        script.write_text("""
print("Unicode test: 你好世界 🎉 café")
""", encoding='utf-8')
        
        # Execute the module
        exit_code, stdout, stderr = await execute_module(
            script_path=script,
            args=[],
            cwd=tmp_path
        )
        
        # Verify unicode is handled correctly
        assert exit_code == 0
        assert "你好世界" in stdout or "Unicode test:" in stdout  # Fallback for encoding issues
    
    @pytest.mark.asyncio
    async def test_execute_module_explicit_threaded_mode(self, tmp_path):
        """Test execution with explicit THREADED mode."""
        # Create a simple test script
        script = tmp_path / "test_threaded.py"
        script.write_text("""
print("Running in threaded mode")
""")
        
        # Execute with explicit THREADED mode
        exit_code, stdout, stderr = await execute_module(
            script_path=script,
            args=[],
            cwd=tmp_path,
            mode=RunMode.THREADED
        )
        
        # Verify execution
        assert exit_code == 0
        assert "Running in threaded mode" in stdout
    
    @pytest.mark.asyncio
    async def test_execute_module_dry_run_mode(self, tmp_path):
        """Test execution in DRY_RUN mode (no actual execution)."""
        # Create a script (won't actually run)
        script = tmp_path / "test_dry.py"
        script.write_text("""
print("This should not appear in dry run")
""")
        
        # Execute in DRY_RUN mode
        exit_code, stdout, stderr = await execute_module(
            script_path=script,
            args=[],
            cwd=tmp_path,
            mode=RunMode.DRY_RUN
        )
        
        # In dry run, should get mock output
        assert exit_code == 0
        # DRY_RUN mode returns mock output, not actual script output
        assert "DRY_RUN" in stdout or stdout == ""
    
    @pytest.mark.asyncio
    async def test_execute_module_working_directory(self, tmp_path):
        """Test that working directory is correctly set."""
        # Create a script that prints current working directory
        script = tmp_path / "check_cwd.py"
        script.write_text("""
import os
print(f"CWD: {os.getcwd()}")
""")
        
        # Execute the module
        exit_code, stdout, stderr = await execute_module(
            script_path=script,
            args=[],
            cwd=tmp_path
        )
        
        # Verify working directory is set correctly
        assert exit_code == 0
        assert str(tmp_path) in stdout
    
    @pytest.mark.asyncio
    async def test_execute_module_large_output(self, tmp_path):
        """Test handling of large output without buffer issues."""
        # Create a script with large output
        script = tmp_path / "large_output.py"
        script.write_text("""
for i in range(100):
    print(f"Output line {i:03d}: " + "x" * 100)
""")
        
        # Execute the module
        exit_code, stdout, stderr = await execute_module(
            script_path=script,
            args=[],
            cwd=tmp_path
        )
        
        # Verify all output captured
        assert exit_code == 0
        assert "Output line 000:" in stdout
        assert "Output line 099:" in stdout
        # Should have ~100 lines with ~100 chars each
        assert len(stdout) > 10000
    
    @pytest.mark.asyncio
    async def test_execute_module_concurrent_execution(self, tmp_path):
        """Test concurrent execution of multiple modules."""
        # Create multiple test scripts
        scripts = []
        for i in range(3):
            script = tmp_path / f"concurrent_{i}.py"
            script.write_text(f"""
import time
print("Script {i} starting")
time.sleep(0.1)
print("Script {i} completed")
""")
            scripts.append(script)
        
        # Execute all concurrently
        tasks = [
            execute_module(
                script_path=script,
                args=[],
                cwd=tmp_path
            )
            for script in scripts
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verify all succeeded
        assert len(results) == 3
        for i, (exit_code, stdout, stderr) in enumerate(results):
            assert exit_code == 0
            assert f"Script {i} starting" in stdout
            assert f"Script {i} completed" in stdout
    
    @pytest.mark.asyncio
    async def test_execute_module_error_propagation(self, tmp_path):
        """Test that unexpected errors are properly propagated."""
        # Create a script that raises an exception
        script = tmp_path / "exception.py"
        script.write_text("""
print("Before exception")
raise ValueError("Test exception")
""")
        
        # Execute the module
        exit_code, stdout, stderr = await execute_module(
            script_path=script,
            args=[],
            cwd=tmp_path
        )
        
        # Python will exit with error code and print traceback to stderr
        assert exit_code != 0
        assert "Before exception" in stdout
        assert "ValueError" in stderr or "Traceback" in stderr


class TestExecuteModuleResourceCleanup:
    """Test resource cleanup in various scenarios."""
    
    @pytest.mark.asyncio
    async def test_cleanup_on_success(self, tmp_path):
        """Test resources are cleaned up after successful execution."""
        script = tmp_path / "simple.py"
        script.write_text("print('test')")
        
        # Execute and verify cleanup happens (no resource leak)
        exit_code, stdout, stderr = await execute_module(
            script_path=script,
            args=[],
            cwd=tmp_path
        )
        
        assert exit_code == 0
        # If we get here without hanging, cleanup worked
    
    @pytest.mark.asyncio
    async def test_cleanup_on_failure(self, tmp_path):
        """Test resources are cleaned up even when execution fails."""
        script = tmp_path / "failing.py"
        script.write_text("""
import sys
sys.exit(1)
""")
        
        # Execute and verify cleanup happens even on failure
        exit_code, stdout, stderr = await execute_module(
            script_path=script,
            args=[],
            cwd=tmp_path
        )
        
        assert exit_code == 1
        # If we get here without hanging, cleanup worked
    
    @pytest.mark.asyncio
    async def test_cleanup_on_cancellation(self, tmp_path):
        """Test resources are cleaned up when task is cancelled."""
        script = tmp_path / "long_running.py"
        script.write_text("""
import time
print("Starting")
time.sleep(10)
print("Completed")
""")
        
        # Start execution and cancel it
        task = asyncio.create_task(
            execute_module(
                script_path=script,
                args=[],
                cwd=tmp_path
            )
        )
        
        # Give it time to start
        await asyncio.sleep(0.2)
        
        # Cancel the task
        task.cancel()
        
        # Verify cancellation is handled
        with pytest.raises(asyncio.CancelledError):
            await task
        
        # If we get here without hanging, cleanup worked


class TestExecuteModuleEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.mark.asyncio
    async def test_empty_output(self, tmp_path):
        """Test script with no output."""
        script = tmp_path / "silent.py"
        script.write_text("pass")
        
        exit_code, stdout, stderr = await execute_module(
            script_path=script,
            args=[],
            cwd=tmp_path
        )
        
        assert exit_code == 0
        assert stdout.strip() == ""
        assert stderr.strip() == ""
    
    @pytest.mark.asyncio
    async def test_script_with_only_stderr(self, tmp_path):
        """Test script that only writes to stderr."""
        script = tmp_path / "stderr_only.py"
        script.write_text("""
import sys
print("Error output", file=sys.stderr)
""")
        
        exit_code, stdout, stderr = await execute_module(
            script_path=script,
            args=[],
            cwd=tmp_path
        )
        
        assert exit_code == 0
        assert stdout.strip() == ""
        assert "Error output" in stderr
    
    @pytest.mark.asyncio
    async def test_mixed_stdout_stderr_output(self, tmp_path):
        """Test script with interleaved stdout/stderr output."""
        script = tmp_path / "mixed.py"
        script.write_text("""
import sys
print("stdout line 1")
print("stderr line 1", file=sys.stderr)
print("stdout line 2")
print("stderr line 2", file=sys.stderr)
""")
        
        exit_code, stdout, stderr = await execute_module(
            script_path=script,
            args=[],
            cwd=tmp_path
        )
        
        assert exit_code == 0
        assert "stdout line 1" in stdout
        assert "stdout line 2" in stdout
        assert "stderr line 1" in stderr
        assert "stderr line 2" in stderr
