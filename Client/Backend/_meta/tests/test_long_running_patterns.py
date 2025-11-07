"""Test long-running background task patterns.

This test file validates Pattern 2 from BACKGROUND_TASKS_BEST_PRACTICES.md:
Long-Running Background Task with real-time output streaming and proper cancellation.
"""

import asyncio
import pytest
import tempfile
from pathlib import Path
from textwrap import dedent

from src.core.execution_patterns import execute_long_running_task
from src.core.output_capture import OutputCapture
from src.core.subprocess_wrapper import SubprocessWrapper, RunMode


class TestLongRunningPattern:
    """Test Pattern 2: Long-Running Background Task pattern."""
    
    @pytest.mark.asyncio
    async def test_basic_long_running_execution(self, tmp_path):
        """Test basic long-running task execution with output capture."""
        # Create a simple script that produces output
        script_path = tmp_path / "test_script.py"
        script_path.write_text(dedent("""
            import time
            print("Starting task")
            time.sleep(0.1)
            print("Processing item 1")
            time.sleep(0.1)
            print("Processing item 2")
            time.sleep(0.1)
            print("Task complete")
        """))
        
        # Setup output capture
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        output_capture = OutputCapture(log_dir=log_dir)
        
        # Execute task
        run_id = "test-run-1"
        exit_code = await execute_long_running_task(
            run_id=run_id,
            script_path=script_path,
            output_capture=output_capture
        )
        
        # Verify execution
        assert exit_code == 0
        
        # Verify output was captured
        logs = output_capture.get_logs(run_id)
        assert len(logs) > 0
        
        # Verify specific messages were captured
        messages = [log.message for log in logs]
        assert "Starting task" in messages
        assert "Task complete" in messages
        
        # Verify log file was created
        log_file = log_dir / f"{run_id}.log"
        assert log_file.exists()
        
        # Cleanup
        output_capture.cleanup_run(run_id)
    
    @pytest.mark.asyncio
    async def test_streaming_output_capture(self, tmp_path):
        """Test real-time output streaming during task execution."""
        # Create script with progressive output
        script_path = tmp_path / "streaming_script.py"
        script_path.write_text(dedent("""
            import sys
            for i in range(5):
                print(f"Progress: {i+1}/5")
                sys.stdout.flush()
        """))
        
        # Setup output capture
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        output_capture = OutputCapture(log_dir=log_dir)
        
        # Execute task
        run_id = "test-stream-1"
        exit_code = await execute_long_running_task(
            run_id=run_id,
            script_path=script_path,
            output_capture=output_capture
        )
        
        # Verify streaming captured all lines
        assert exit_code == 0
        logs = output_capture.get_logs(run_id)
        assert len(logs) == 5
        
        # Verify progressive messages
        for i, log in enumerate(logs):
            assert f"Progress: {i+1}/5" in log.message
        
        # Cleanup
        output_capture.cleanup_run(run_id)
    
    @pytest.mark.asyncio
    async def test_stderr_capture(self, tmp_path):
        """Test stderr output capture in addition to stdout."""
        # Create script with both stdout and stderr
        script_path = tmp_path / "error_script.py"
        script_path.write_text(dedent("""
            import sys
            print("Normal output to stdout")
            print("Warning message", file=sys.stderr)
            print("More stdout")
            print("Error message", file=sys.stderr)
        """))
        
        # Setup output capture
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        output_capture = OutputCapture(log_dir=log_dir)
        
        # Execute task
        run_id = "test-stderr-1"
        exit_code = await execute_long_running_task(
            run_id=run_id,
            script_path=script_path,
            output_capture=output_capture
        )
        
        # Verify both streams captured
        assert exit_code == 0
        logs = output_capture.get_logs(run_id)
        
        # Check for stdout messages
        stdout_logs = [log for log in logs if log.stream == 'stdout']
        assert len(stdout_logs) >= 2
        
        # Check for stderr messages
        stderr_logs = [log for log in logs if log.stream == 'stderr']
        assert len(stderr_logs) >= 2
        
        # Verify specific messages
        all_messages = [log.message for log in logs]
        assert "Normal output to stdout" in all_messages
        assert "Warning message" in all_messages
        
        # Cleanup
        output_capture.cleanup_run(run_id)
    
    @pytest.mark.asyncio
    async def test_cancellation_handling(self, tmp_path):
        """Test proper cancellation handling with graceful termination."""
        # Create a long-running script
        script_path = tmp_path / "long_script.py"
        script_path.write_text(dedent("""
            import time
            print("Starting long task")
            for i in range(100):
                print(f"Step {i}")
                time.sleep(0.1)
            print("Should not reach here")
        """))
        
        # Setup output capture
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        output_capture = OutputCapture(log_dir=log_dir)
        
        # Start task
        run_id = "test-cancel-1"
        task = asyncio.create_task(
            execute_long_running_task(
                run_id=run_id,
                script_path=script_path,
                output_capture=output_capture
            )
        )
        
        # Let it run briefly
        await asyncio.sleep(0.3)
        
        # Cancel the task
        task.cancel()
        
        # Verify cancellation is handled
        with pytest.raises(asyncio.CancelledError):
            await task
        
        # Verify some output was captured before cancellation
        logs = output_capture.get_logs(run_id)
        assert len(logs) > 0
        assert logs[0].message == "Starting long task"
        
        # Verify we didn't reach the end
        messages = [log.message for log in logs]
        assert "Should not reach here" not in messages
        
        # Cleanup
        output_capture.cleanup_run(run_id)
    
    @pytest.mark.asyncio
    async def test_task_with_arguments(self, tmp_path):
        """Test long-running task with command-line arguments."""
        # Create script that uses arguments
        script_path = tmp_path / "args_script.py"
        script_path.write_text(dedent("""
            import sys
            print(f"Arguments: {sys.argv[1:]}")
            for arg in sys.argv[1:]:
                print(f"Processing: {arg}")
        """))
        
        # Setup output capture
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        output_capture = OutputCapture(log_dir=log_dir)
        
        # Execute with arguments
        run_id = "test-args-1"
        exit_code = await execute_long_running_task(
            run_id=run_id,
            script_path=script_path,
            output_capture=output_capture,
            args=["arg1", "arg2", "arg3"]
        )
        
        # Verify execution
        assert exit_code == 0
        
        # Verify arguments were passed
        logs = output_capture.get_logs(run_id)
        messages = [log.message for log in logs]
        assert any("arg1" in msg for msg in messages)
        assert any("arg2" in msg for msg in messages)
        assert any("arg3" in msg for msg in messages)
        
        # Cleanup
        output_capture.cleanup_run(run_id)
    
    @pytest.mark.asyncio
    async def test_custom_working_directory(self, tmp_path):
        """Test task execution with custom working directory."""
        # Create script that checks current directory
        work_dir = tmp_path / "custom_dir"
        work_dir.mkdir()
        
        script_path = tmp_path / "cwd_script.py"
        script_path.write_text(dedent("""
            import os
            print(f"Working directory: {os.getcwd()}")
        """))
        
        # Setup output capture
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        output_capture = OutputCapture(log_dir=log_dir)
        
        # Execute with custom cwd
        run_id = "test-cwd-1"
        exit_code = await execute_long_running_task(
            run_id=run_id,
            script_path=script_path,
            output_capture=output_capture,
            cwd=work_dir
        )
        
        # Verify execution
        assert exit_code == 0
        
        # Verify working directory was used
        logs = output_capture.get_logs(run_id)
        messages = [log.message for log in logs]
        assert any("custom_dir" in msg for msg in messages)
        
        # Cleanup
        output_capture.cleanup_run(run_id)
    
    @pytest.mark.asyncio
    async def test_script_with_exit_code(self, tmp_path):
        """Test that non-zero exit codes are properly returned."""
        # Create script that exits with error
        script_path = tmp_path / "error_exit_script.py"
        script_path.write_text(dedent("""
            import sys
            print("About to exit with error")
            sys.exit(42)
        """))
        
        # Setup output capture
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        output_capture = OutputCapture(log_dir=log_dir)
        
        # Execute task
        run_id = "test-exitcode-1"
        exit_code = await execute_long_running_task(
            run_id=run_id,
            script_path=script_path,
            output_capture=output_capture
        )
        
        # Verify exit code is propagated
        assert exit_code == 42
        
        # Verify output was still captured
        logs = output_capture.get_logs(run_id)
        assert len(logs) > 0
        assert "About to exit with error" in [log.message for log in logs]
        
        # Cleanup
        output_capture.cleanup_run(run_id)


class TestOutputCaptureAppendLine:
    """Test the append_line method added to OutputCapture."""
    
    @pytest.mark.asyncio
    async def test_append_line_basic(self, tmp_path):
        """Test basic append_line functionality."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        output_capture = OutputCapture(log_dir=log_dir)
        
        run_id = "test-append-1"
        
        # Append some lines
        await output_capture.append_line(run_id, "First line\n")
        await output_capture.append_line(run_id, "Second line\n")
        await output_capture.append_line(run_id, "Third line\n")
        
        # Verify lines are in buffer
        logs = output_capture.get_logs(run_id)
        assert len(logs) == 3
        assert logs[0].message == "First line"
        assert logs[1].message == "Second line"
        assert logs[2].message == "Third line"
        
        # Verify log file exists
        log_file = log_dir / f"{run_id}.log"
        assert log_file.exists()
        
        # Cleanup
        output_capture.cleanup_run(run_id)
    
    @pytest.mark.asyncio
    async def test_append_line_strips_whitespace(self, tmp_path):
        """Test that append_line strips trailing whitespace."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        output_capture = OutputCapture(log_dir=log_dir)
        
        run_id = "test-strip-1"
        
        # Append line with trailing whitespace
        await output_capture.append_line(run_id, "Line with spaces   \n\r")
        
        # Verify whitespace is stripped
        logs = output_capture.get_logs(run_id)
        assert len(logs) == 1
        assert logs[0].message == "Line with spaces"
        
        # Cleanup
        output_capture.cleanup_run(run_id)
    
    @pytest.mark.asyncio
    async def test_append_line_stderr(self, tmp_path):
        """Test append_line with stderr stream."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        output_capture = OutputCapture(log_dir=log_dir)
        
        run_id = "test-stderr-append-1"
        
        # Append to different streams
        await output_capture.append_line(run_id, "Stdout message\n", stream='stdout')
        await output_capture.append_line(run_id, "Stderr message\n", stream='stderr')
        
        # Verify both are captured
        logs = output_capture.get_logs(run_id)
        assert len(logs) == 2
        
        # Verify stream types
        assert logs[0].stream == 'stdout'
        assert logs[1].stream == 'stderr'
        
        # Cleanup
        output_capture.cleanup_run(run_id)
    
    @pytest.mark.asyncio
    async def test_append_line_initializes_buffers(self, tmp_path):
        """Test that append_line initializes buffers if they don't exist."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        output_capture = OutputCapture(log_dir=log_dir)
        
        run_id = "test-init-1"
        
        # append_line should initialize buffers automatically
        await output_capture.append_line(run_id, "First line\n")
        
        # Verify buffers were created
        assert run_id in output_capture.log_buffers
        assert run_id in output_capture.sse_subscribers
        assert run_id in output_capture.log_files
        
        # Cleanup
        output_capture.cleanup_run(run_id)
    
    @pytest.mark.asyncio
    async def test_append_line_concurrent_writes(self, tmp_path):
        """Test concurrent append_line calls."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        output_capture = OutputCapture(log_dir=log_dir)
        
        run_id = "test-concurrent-1"
        
        # Append lines concurrently
        await asyncio.gather(
            output_capture.append_line(run_id, "Line 1\n"),
            output_capture.append_line(run_id, "Line 2\n"),
            output_capture.append_line(run_id, "Line 3\n"),
            output_capture.append_line(run_id, "Line 4\n"),
            output_capture.append_line(run_id, "Line 5\n"),
        )
        
        # Verify all lines captured (order may vary)
        logs = output_capture.get_logs(run_id)
        assert len(logs) == 5
        
        messages = {log.message for log in logs}
        expected = {"Line 1", "Line 2", "Line 3", "Line 4", "Line 5"}
        assert messages == expected
        
        # Cleanup
        output_capture.cleanup_run(run_id)
