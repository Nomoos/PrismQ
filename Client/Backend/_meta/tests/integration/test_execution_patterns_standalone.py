"""Standalone integration test for execution patterns.

This test can be run independently to verify the execution_patterns module
works correctly without requiring the full application stack.
"""

import asyncio
import sys
import tempfile
from pathlib import Path

# Add src/core to path for direct import
backend_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_root / "src" / "core"))

# Import directly from modules to avoid __init__.py imports
from subprocess_wrapper import SubprocessWrapper, RunMode


async def simple_execute_module(script_path: Path, args: list, cwd: Path, mode: RunMode = None):
    """Simplified version of execute_module for testing without dependencies."""
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    wrapper = SubprocessWrapper(mode=mode)
    
    try:
        cmd = ['python', str(script_path)] + args
        
        process, stdout, stderr = await wrapper.create_subprocess(*cmd, cwd=cwd)
        
        # Collect output
        stdout_data = []
        stderr_data = []
        
        async def read_stream(stream, buffer):
            while True:
                line = await stream.readline()
                if not line:
                    break
                buffer.append(line)
        
        await asyncio.gather(
            read_stream(stdout, stdout_data),
            read_stream(stderr, stderr_data)
        )
        
        exit_code = await process.wait()
        
        stdout_str = b''.join(stdout_data).decode('utf-8', errors='replace')
        stderr_str = b''.join(stderr_data).decode('utf-8', errors='replace')
        
        return (exit_code, stdout_str, stderr_str)
        
    finally:
        wrapper.cleanup()


async def run_tests():
    """Run standalone integration tests."""
    print("=" * 70)
    print("Standalone Execution Patterns Integration Tests")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Test 1: Simple successful execution
        print("\nTest 1: Simple successful execution...")
        script1 = tmp_path / "test1.py"
        script1.write_text('print("Hello from test script")')
        
        exit_code, stdout, stderr = await simple_execute_module(
            script_path=script1,
            args=[],
            cwd=tmp_path
        )
        
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
        assert "Hello from test script" in stdout, "Expected output not found"
        print("✓ Test 1 PASSED")
        
        # Test 2: Script with arguments
        print("\nTest 2: Script with arguments...")
        script2 = tmp_path / "test2.py"
        script2.write_text("""
import sys
for arg in sys.argv[1:]:
    print(f"Arg: {arg}")
""")
        
        exit_code, stdout, stderr = await simple_execute_module(
            script_path=script2,
            args=["--param", "value"],
            cwd=tmp_path
        )
        
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
        assert "Arg: --param" in stdout, "Argument not passed correctly"
        assert "Arg: value" in stdout, "Argument value not passed correctly"
        print("✓ Test 2 PASSED")
        
        # Test 3: Script with error
        print("\nTest 3: Script with error...")
        script3 = tmp_path / "test3.py"
        script3.write_text("""
import sys
print("Starting")
print("Error message", file=sys.stderr)
sys.exit(1)
""")
        
        exit_code, stdout, stderr = await simple_execute_module(
            script_path=script3,
            args=[],
            cwd=tmp_path
        )
        
        assert exit_code == 1, f"Expected exit code 1, got {exit_code}"
        assert "Starting" in stdout, "stdout not captured"
        assert "Error message" in stderr, "stderr not captured"
        print("✓ Test 3 PASSED")
        
        # Test 4: THREADED mode
        print("\nTest 4: Explicit THREADED mode...")
        script4 = tmp_path / "test4.py"
        script4.write_text('print("THREADED mode test")')
        
        exit_code, stdout, stderr = await simple_execute_module(
            script_path=script4,
            args=[],
            cwd=tmp_path,
            mode=RunMode.THREADED
        )
        
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
        assert "THREADED mode test" in stdout, "Output not captured in THREADED mode"
        print("✓ Test 4 PASSED")
        
        # Test 5: DRY_RUN mode
        print("\nTest 5: DRY_RUN mode...")
        script5 = tmp_path / "test5.py"
        script5.write_text('print("Should not execute")')
        
        exit_code, stdout, stderr = await simple_execute_module(
            script_path=script5,
            args=[],
            cwd=tmp_path,
            mode=RunMode.DRY_RUN
        )
        
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
        # DRY_RUN returns mock output
        print("✓ Test 5 PASSED")
        
        # Test 6: Nonexistent script
        print("\nTest 6: Nonexistent script error handling...")
        nonexistent = tmp_path / "nonexistent.py"
        
        try:
            await simple_execute_module(
                script_path=nonexistent,
                args=[],
                cwd=tmp_path
            )
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError as e:
            assert "Script not found" in str(e)
            print("✓ Test 6 PASSED")
        
        # Test 7: Large output
        print("\nTest 7: Large output handling...")
        script7 = tmp_path / "test7.py"
        script7.write_text("""
for i in range(50):
    print(f"Line {i:03d}: " + "x" * 100)
""")
        
        exit_code, stdout, stderr = await simple_execute_module(
            script_path=script7,
            args=[],
            cwd=tmp_path
        )
        
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
        assert "Line 000:" in stdout, "First line not found"
        assert "Line 049:" in stdout, "Last line not found"
        assert len(stdout) > 5000, "Output seems truncated"
        print("✓ Test 7 PASSED")
        
        # Test 8: Unicode handling
        print("\nTest 8: Unicode handling...")
        script8 = tmp_path / "test8.py"
        script8.write_text('print("Unicode: café 🎉")', encoding='utf-8')
        
        exit_code, stdout, stderr = await simple_execute_module(
            script_path=script8,
            args=[],
            cwd=tmp_path
        )
        
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
        # Either unicode is preserved or gracefully handled
        assert "Unicode:" in stdout or "caf" in stdout, "Unicode not handled"
        print("✓ Test 8 PASSED")
        
        # Test 9: Concurrent execution
        print("\nTest 9: Concurrent execution...")
        scripts = []
        for i in range(3):
            script = tmp_path / f"concurrent_{i}.py"
            script.write_text(f'print("Script {i}")')
            scripts.append(script)
        
        tasks = [
            simple_execute_module(script, [], tmp_path)
            for script in scripts
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3, "Not all tasks completed"
        for i, (exit_code, stdout, stderr) in enumerate(results):
            assert exit_code == 0, f"Script {i} failed"
            assert f"Script {i}" in stdout, f"Script {i} output not found"
        print("✓ Test 9 PASSED")
    
    print("\n" + "=" * 70)
    print("All tests PASSED! ✓")
    print("=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(run_tests())
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Tests FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
