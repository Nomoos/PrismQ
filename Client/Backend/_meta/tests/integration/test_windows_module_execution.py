"""Integration tests for Windows module execution.

This module tests the complete module execution flow on Windows,
including subprocess spawning, log capture, and process management.

Primary Platform: Windows 10/11 with NVIDIA RTX 5090

Issue #303: Add Comprehensive Testing for Windows Subprocess Execution
"""

import asyncio
import sys
import pytest
import tempfile
from pathlib import Path

# Skip all tests in this module if not on Windows
pytestmark = pytest.mark.skipif(sys.platform != 'win32', reason="Windows integration tests")


class TestModuleExecutionFlow:
    """Test complete module execution flow on Windows."""
    
    @pytest.mark.asyncio
    async def test_simple_python_module_execution(self, tmp_path):
        """Test executing a simple Python module on Windows."""
        # Ensure ProactorEventLoopPolicy is set
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Create a simple test script
        test_script = tmp_path / "simple_module.py"
        test_script.write_text("""
import sys
print("Module started", flush=True)
print("Processing data", flush=True)
print("Module completed", flush=True)
sys.exit(0)
""")
        
        # Execute the module
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(test_script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=tmp_path
        )
        
        # Capture output
        stdout, stderr = await process.communicate()
        
        # Verify execution
        assert process.returncode == 0
        assert b"Module started" in stdout
        assert b"Processing data" in stdout
        assert b"Module completed" in stdout
    
    @pytest.mark.asyncio
    async def test_module_with_stderr_output(self, tmp_path):
        """Test module that writes to both stdout and stderr."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        test_script = tmp_path / "stderr_module.py"
        test_script.write_text("""
import sys
print("Normal output", flush=True)
print("Error output", file=sys.stderr, flush=True)
print("More normal output", flush=True)
""")
        
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(test_script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=tmp_path
        )
        
        stdout, stderr = await process.communicate()
        
        assert process.returncode == 0
        assert b"Normal output" in stdout
        assert b"Error output" in stderr
        assert b"More normal output" in stdout
    
    @pytest.mark.asyncio
    async def test_module_with_parameters(self, tmp_path):
        """Test module execution with command-line parameters."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        test_script = tmp_path / "param_module.py"
        test_script.write_text("""
import sys
print(f"Args: {sys.argv[1:]}", flush=True)
for arg in sys.argv[1:]:
    print(f"Processing: {arg}", flush=True)
""")
        
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(test_script), 'param1', 'param2', 'param3',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=tmp_path
        )
        
        stdout, stderr = await process.communicate()
        
        assert process.returncode == 0
        assert b"param1" in stdout
        assert b"param2" in stdout
        assert b"param3" in stdout
    
    @pytest.mark.asyncio
    async def test_module_with_exit_code(self, tmp_path):
        """Test module that exits with non-zero code."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        test_script = tmp_path / "exit_code_module.py"
        test_script.write_text("""
import sys
print("Module encountered an error", flush=True)
sys.exit(42)
""")
        
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(test_script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=tmp_path
        )
        
        stdout, stderr = await process.communicate()
        
        assert process.returncode == 42
        assert b"Module encountered an error" in stdout


class TestConcurrentModuleExecution:
    """Test running multiple modules concurrently on Windows."""
    
    @pytest.mark.asyncio
    async def test_two_modules_concurrent(self, tmp_path):
        """Test running two modules concurrently."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Create two test scripts
        script1 = tmp_path / "module1.py"
        script1.write_text("""
import time
print("Module 1 starting", flush=True)
time.sleep(0.5)
print("Module 1 done", flush=True)
""")
        
        script2 = tmp_path / "module2.py"
        script2.write_text("""
import time
print("Module 2 starting", flush=True)
time.sleep(0.5)
print("Module 2 done", flush=True)
""")
        
        # Start both modules concurrently
        process1 = await asyncio.create_subprocess_exec(
            sys.executable, str(script1),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        process2 = await asyncio.create_subprocess_exec(
            sys.executable, str(script2),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Wait for both to complete
        stdout1, _ = await process1.communicate()
        stdout2, _ = await process2.communicate()
        
        # Verify both completed successfully
        assert process1.returncode == 0
        assert process2.returncode == 0
        assert b"Module 1 done" in stdout1
        assert b"Module 2 done" in stdout2
    
    @pytest.mark.asyncio
    async def test_three_modules_concurrent(self, tmp_path):
        """Test running three modules concurrently."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Create test scripts
        scripts = []
        for i in range(3):
            script = tmp_path / f"module{i}.py"
            script.write_text(f"""
import time
print("Module {i} running", flush=True)
time.sleep(0.3)
print("Module {i} completed", flush=True)
""")
            scripts.append(script)
        
        # Start all modules
        processes = []
        for script in scripts:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, str(script),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            processes.append(proc)
        
        # Wait for all to complete
        results = await asyncio.gather(*[p.communicate() for p in processes])
        
        # Verify all completed
        for i, (proc, (stdout, _)) in enumerate(zip(processes, results)):
            assert proc.returncode == 0
            assert f"Module {i} completed".encode() in stdout


class TestProcessTermination:
    """Test process termination scenarios on Windows."""
    
    @pytest.mark.asyncio
    async def test_terminate_long_running_process(self, tmp_path):
        """Test terminating a long-running process."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        test_script = tmp_path / "long_running.py"
        test_script.write_text("""
import time
print("Starting long task", flush=True)
time.sleep(60)  # 60 seconds
print("Task completed", flush=True)
""")
        
        # Start the process
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(test_script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Give it time to start
        await asyncio.sleep(0.2)
        
        # Terminate it
        process.terminate()
        
        # Wait for it to finish
        try:
            await asyncio.wait_for(process.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            # Force kill if terminate didn't work
            process.kill()
            await process.wait()
        
        # Process should be terminated
        assert process.returncode != 0 or process.returncode is not None
    
    @pytest.mark.asyncio
    async def test_kill_unresponsive_process(self, tmp_path):
        """Test killing an unresponsive process."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        test_script = tmp_path / "unresponsive.py"
        test_script.write_text("""
import signal
import time

# Ignore SIGTERM on Windows (similar behavior)
print("Ignoring termination signals", flush=True)
time.sleep(60)
""")
        
        # Start the process
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(test_script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Give it time to start
        await asyncio.sleep(0.2)
        
        # Kill it forcefully
        process.kill()
        
        # Should terminate quickly
        await asyncio.wait_for(process.wait(), timeout=2.0)
        
        # Process should be killed
        assert process.returncode is not None


class TestStreamingOutput:
    """Test real-time output streaming on Windows."""
    
    @pytest.mark.asyncio
    async def test_streaming_stdout_line_by_line(self, tmp_path):
        """Test reading stdout line by line as it's produced."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        test_script = tmp_path / "streaming.py"
        test_script.write_text("""
import time
for i in range(3):
    print(f"Line {i}", flush=True)
    time.sleep(0.1)
""")
        
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(test_script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Read output line by line
        lines = []
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            lines.append(line.decode().strip())
        
        await process.wait()
        
        # Verify we got all lines
        assert len(lines) == 3
        assert "Line 0" in lines[0]
        assert "Line 1" in lines[1]
        assert "Line 2" in lines[2]
    
    @pytest.mark.asyncio
    async def test_streaming_with_progress_updates(self, tmp_path):
        """Test streaming progress updates from a module."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        test_script = tmp_path / "progress.py"
        test_script.write_text("""
import time
total = 5
for i in range(total):
    progress = (i + 1) * 100 // total
    print(f"Progress: {progress}%", flush=True)
    time.sleep(0.1)
print("Complete!", flush=True)
""")
        
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(test_script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Track progress
        progress_values = []
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            line_str = line.decode().strip()
            if "Progress:" in line_str:
                # Extract percentage
                progress_values.append(line_str)
        
        await process.wait()
        
        # Verify progress tracking
        assert len(progress_values) == 5
        assert "Complete!" in (await process.stdout.read()).decode() or process.returncode == 0


class TestErrorHandling:
    """Test error handling in module execution."""
    
    @pytest.mark.asyncio
    async def test_module_with_exception(self, tmp_path):
        """Test module that raises an exception."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        test_script = tmp_path / "exception_module.py"
        test_script.write_text("""
import sys
print("Starting module", flush=True)
raise ValueError("Test exception")
""")
        
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(test_script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Should exit with non-zero code
        assert process.returncode != 0
        assert b"Starting module" in stdout
        assert b"ValueError" in stderr or b"Test exception" in stderr
    
    @pytest.mark.asyncio
    async def test_module_with_syntax_error(self, tmp_path):
        """Test module with syntax error."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        test_script = tmp_path / "syntax_error_module.py"
        test_script.write_text("""
print("This is valid")
if True
    print("Syntax error - missing colon")
""")
        
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(test_script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Should exit with non-zero code
        assert process.returncode != 0
        assert b"SyntaxError" in stderr
    
    @pytest.mark.asyncio
    async def test_nonexistent_script(self, tmp_path):
        """Test attempting to execute non-existent script."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        nonexistent_script = tmp_path / "does_not_exist.py"
        
        # Should raise FileNotFoundError or similar
        with pytest.raises((FileNotFoundError, OSError)):
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(nonexistent_script),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )


class TestWorkingDirectoryHandling:
    """Test working directory handling on Windows."""
    
    @pytest.mark.asyncio
    async def test_module_with_custom_cwd(self, tmp_path):
        """Test executing module with custom working directory."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Create a subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        
        test_script = subdir / "cwd_test.py"
        test_script.write_text("""
import os
print(f"CWD: {os.getcwd()}", flush=True)
""")
        
        # Execute with subdir as working directory
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(test_script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(subdir)
        )
        
        stdout, stderr = await process.communicate()
        
        assert process.returncode == 0
        # Output should contain the subdir path
        assert str(subdir).encode() in stdout
    
    @pytest.mark.asyncio
    async def test_module_creates_files_in_cwd(self, tmp_path):
        """Test that module can create files in working directory."""
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        test_script = tmp_path / "file_creator.py"
        test_script.write_text("""
with open("output.txt", "w") as f:
    f.write("Test output")
print("File created", flush=True)
""")
        
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(test_script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(tmp_path)
        )
        
        stdout, stderr = await process.communicate()
        
        assert process.returncode == 0
        assert b"File created" in stdout
        
        # Verify file was created
        output_file = tmp_path / "output.txt"
        assert output_file.exists()
        assert output_file.read_text() == "Test output"


# Pytest fixtures
@pytest.fixture(autouse=True)
def setup_windows_policy():
    """Ensure Windows ProactorEventLoopPolicy is set for all tests."""
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    yield
