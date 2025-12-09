"""Profile Client Backend module performance.

This script profiles critical backend operations including:
- Module registry operations
- Process management
- Configuration storage
- Log capture and streaming
"""

import sys
from pathlib import Path

# Add paths
script_dir = Path(__file__).parent
perf_dir = script_dir.parent
sys.path.insert(0, str(perf_dir))

from profiling_utils import CPUProfiler, MemoryProfiler, time_function

# Add Client Backend to path
client_backend_path = perf_dir.parent.parent / "Client" / "Backend" / "src"
sys.path.insert(0, str(client_backend_path))

from core.config_storage import ConfigStorage
from core.module_runner import ModuleRunner
from core.output_capture import OutputCapture
from core.process_manager import ProcessManager
from core.run_registry import RunRegistry


@time_function
def profile_run_registry():
    """Profile run registry operations."""
    print("\n📊 Profiling Run Registry...")

    registry = RunRegistry()
    cpu_profiler = CPUProfiler(output_dir=str(perf_dir / "reports" / "cpu"))
    mem_profiler = MemoryProfiler(output_dir=str(perf_dir / "reports" / "memory"))

    def test_registry():
        # Create multiple runs
        runs = []
        for i in range(100):
            run = registry.create_run(
                module_id=f"test-module-{i}",
                script_path=Path(f"/test/script{i}.py"),
                parameters={"index": i},
            )
            runs.append(run)

        # Lookup runs
        for run in runs[:50]:
            registry.get_run(run.run_id)

        # List all runs
        all_runs = registry.list_runs()

        return len(all_runs)

    # CPU profiling
    result, cpu_report = cpu_profiler.profile(test_registry)
    print(f"  ✓ CPU profile: {cpu_report}")

    # Memory profiling
    result, mem_report, peak_mb, increase_mb = mem_profiler.profile(test_registry)
    print(f"  ✓ Memory profile: {mem_report}")
    print(f"    Peak memory: {peak_mb:.2f} MB")
    print(f"    Memory increase: {increase_mb:.2f} MB")


@time_function
def profile_config_storage():
    """Profile configuration storage operations."""
    print("\n📊 Profiling Config Storage...")

    import tempfile

    storage = ConfigStorage(tempfile.mkdtemp())
    cpu_profiler = CPUProfiler(output_dir=str(perf_dir / "reports" / "cpu"))
    mem_profiler = MemoryProfiler(output_dir=str(perf_dir / "reports" / "memory"))

    def test_storage():
        # Save configurations
        for i in range(50):
            config = {
                "param1": f"value{i}",
                "param2": i,
                "param3": ["list", "of", "values", str(i)],
                "param4": {"nested": f"dict{i}"},
            }
            storage.save_config(f"module-{i}", config)

        # Load configurations
        for i in range(50):
            storage.get_config(f"module-{i}")

        # Merge with defaults
        defaults = {"default1": "val1", "default2": "val2"}
        for i in range(25):
            storage.merge_with_defaults(f"module-{i}", defaults)

        return True

    # CPU profiling
    result, cpu_report = cpu_profiler.profile(test_storage)
    print(f"  ✓ CPU profile: {cpu_report}")

    # Memory profiling
    result, mem_report, peak_mb, increase_mb = mem_profiler.profile(test_storage)
    print(f"  ✓ Memory profile: {mem_report}")
    print(f"    Peak memory: {peak_mb:.2f} MB")
    print(f"    Memory increase: {increase_mb:.2f} MB")


@time_function
def profile_output_capture():
    """Profile log capture operations."""
    print("\n📊 Profiling Output Capture...")

    capture = OutputCapture(buffer_size=100000)
    cpu_profiler = CPUProfiler(output_dir=str(perf_dir / "reports" / "cpu"))
    mem_profiler = MemoryProfiler(output_dir=str(perf_dir / "reports" / "memory"))

    def test_capture():
        run_id = "test-run-123"

        # Capture many log lines
        for i in range(10000):
            capture.capture_line(run_id, f"Log line {i} with some additional content\n")

        # Retrieve logs multiple times
        for _ in range(100):
            capture.get_logs(run_id, tail=500)

        # Stream logs
        list(capture.stream_logs(run_id))

        return True

    # CPU profiling
    result, cpu_report = cpu_profiler.profile(test_capture)
    print(f"  ✓ CPU profile: {cpu_report}")

    # Memory profiling
    result, mem_report, peak_mb, increase_mb = mem_profiler.profile(test_capture)
    print(f"  ✓ Memory profile: {mem_report}")
    print(f"    Peak memory: {peak_mb:.2f} MB")
    print(f"    Memory increase: {increase_mb:.2f} MB")


def main():
    """Main entry point."""
    print("=" * 80)
    print("  Client Backend Performance Profiling")
    print("=" * 80)

    profile_run_registry()
    profile_config_storage()
    profile_output_capture()

    print("\n" + "=" * 80)
    print("  Client Backend Profiling Complete")
    print("=" * 80)
    print("\nReports saved to:")
    print(f"  CPU: {perf_dir / 'reports' / 'cpu'}")
    print(f"  Memory: {perf_dir / 'reports' / 'memory'}")


if __name__ == "__main__":
    main()
