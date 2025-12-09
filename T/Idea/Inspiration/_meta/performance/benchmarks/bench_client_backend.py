"""Benchmark tests for Client Backend module.

These benchmarks measure the performance of critical backend operations including:
- Module registry operations
- Process management
- Configuration storage
- Log capture and streaming

Run with: pytest bench_client_backend.py -v --benchmark-only
"""

import asyncio
import sys
from pathlib import Path

# Add Client Backend to path
client_backend_path = Path(__file__).parent.parent.parent.parent / "Client" / "Backend" / "src"
sys.path.insert(0, str(client_backend_path))

import pytest
from core.config_storage import ConfigStorage
from core.module_runner import ModuleRunner
from core.output_capture import OutputCapture
from core.process_manager import ProcessManager
from core.run_registry import RunRegistry


class TestModuleRegistryBenchmarks:
    """Benchmarks for module registry operations."""

    @pytest.fixture
    def runner(self, tmp_path):
        """Create a module runner instance."""
        registry = RunRegistry()
        process_manager = ProcessManager()
        return ModuleRunner(registry, process_manager)

    def test_bench_run_creation(self, benchmark, runner):
        """Benchmark run object creation."""

        def create_run():
            return runner.registry.create_run(
                module_id="test-module",
                script_path=Path("/fake/path.py"),
                parameters={"key": "value"},
            )

        result = benchmark(create_run)
        assert result.run_id is not None

    def test_bench_run_lookup(self, benchmark, runner):
        """Benchmark run lookup by ID."""
        # Create a run first
        run = runner.registry.create_run(
            module_id="test-module", script_path=Path("/fake/path.py"), parameters={}
        )

        def lookup_run():
            return runner.registry.get_run(run.run_id)

        result = benchmark(lookup_run)
        assert result.run_id == run.run_id

    def test_bench_list_runs(self, benchmark, runner):
        """Benchmark listing all runs."""
        # Create multiple runs
        for i in range(10):
            runner.registry.create_run(
                module_id=f"test-module-{i}", script_path=Path(f"/fake/path{i}.py"), parameters={}
            )

        def list_runs():
            return runner.registry.list_runs()

        result = benchmark(list_runs)
        assert len(result) >= 10


class TestConfigStorageBenchmarks:
    """Benchmarks for configuration storage operations."""

    @pytest.fixture
    def storage(self, tmp_path):
        """Create a config storage instance."""
        return ConfigStorage(tmp_path)

    def test_bench_save_config(self, benchmark, storage):
        """Benchmark saving configuration."""
        config = {
            "param1": "value1",
            "param2": 42,
            "param3": ["list", "of", "values"],
            "param4": {"nested": "dict"},
        }

        def save_config():
            storage.save_config("test-module", config)

        benchmark(save_config)

    def test_bench_load_config(self, benchmark, storage):
        """Benchmark loading configuration."""
        # Save config first
        config = {"key": "value", "number": 123}
        storage.save_config("test-module", config)

        def load_config():
            return storage.get_config("test-module")

        result = benchmark(load_config)
        assert result == config

    def test_bench_merge_configs(self, benchmark, storage):
        """Benchmark configuration merging."""
        defaults = {
            "param1": "default1",
            "param2": "default2",
            "param3": "default3",
        }
        saved = {"param1": "saved1", "param4": "saved4"}
        storage.save_config("test-module", saved)

        def merge_configs():
            return storage.merge_with_defaults("test-module", defaults)

        result = benchmark(merge_configs)
        assert result["param1"] == "saved1"  # Saved takes precedence
        assert result["param2"] == "default2"  # From defaults


class TestOutputCaptureBenchmarks:
    """Benchmarks for log capture operations."""

    @pytest.fixture
    def capture(self):
        """Create an output capture instance."""
        return OutputCapture(buffer_size=10000)

    def test_bench_log_capture(self, benchmark, capture):
        """Benchmark capturing log lines."""
        run_id = "test-run-123"

        def capture_log():
            capture.capture_line(run_id, "This is a test log line\n")

        benchmark(capture_log)

    def test_bench_get_logs_small(self, benchmark, capture):
        """Benchmark retrieving small number of logs."""
        run_id = "test-run-123"
        # Add 100 log lines
        for i in range(100):
            capture.capture_line(run_id, f"Log line {i}\n")

        def get_logs():
            return capture.get_logs(run_id, tail=50)

        result = benchmark(get_logs)
        assert len(result) == 50

    def test_bench_get_logs_large(self, benchmark, capture):
        """Benchmark retrieving large number of logs."""
        run_id = "test-run-123"
        # Add 10,000 log lines (full buffer)
        for i in range(10000):
            capture.capture_line(run_id, f"Log line {i}\n")

        def get_logs():
            return capture.get_logs(run_id, tail=1000)

        result = benchmark(get_logs)
        assert len(result) == 1000

    def test_bench_stream_logs(self, benchmark, capture):
        """Benchmark streaming log generator."""
        run_id = "test-run-123"
        # Add logs
        for i in range(100):
            capture.capture_line(run_id, f"Log line {i}\n")

        def stream_logs():
            logs = list(capture.stream_logs(run_id))
            return logs

        result = benchmark(stream_logs)
        assert len(result) > 0


class TestProcessManagerBenchmarks:
    """Benchmarks for process management operations."""

    @pytest.fixture
    def manager(self):
        """Create a process manager instance."""
        return ProcessManager()

    def test_bench_process_tracking(self, benchmark, manager):
        """Benchmark adding and tracking processes."""
        run_id = "test-run-123"

        def track_process():
            # Simulate process tracking
            manager.active_processes[run_id] = {"pid": 12345, "started_at": "2024-01-01T00:00:00"}
            return run_id in manager.active_processes

        result = benchmark(track_process)
        assert result is True

    def test_bench_cleanup_processes(self, benchmark, manager):
        """Benchmark cleaning up completed processes."""
        # Add some processes
        for i in range(10):
            manager.active_processes[f"run-{i}"] = {
                "pid": 1000 + i,
                "started_at": "2024-01-01T00:00:00",
            }

        def cleanup():
            # Simulate cleanup
            completed = [
                k for k in list(manager.active_processes.keys()) if int(k.split("-")[1]) % 2 == 0
            ]
            for run_id in completed:
                del manager.active_processes[run_id]

        benchmark(cleanup)


# Stress test scenarios
class TestStressScenarios:
    """Stress test scenarios for backend."""

    @pytest.fixture
    def runner(self, tmp_path):
        """Create a module runner instance."""
        registry = RunRegistry()
        process_manager = ProcessManager()
        return ModuleRunner(registry, process_manager)

    def test_bench_concurrent_run_creation(self, benchmark, runner):
        """Benchmark creating multiple runs concurrently."""

        def create_multiple_runs():
            runs = []
            for i in range(10):
                run = runner.registry.create_run(
                    module_id=f"module-{i}",
                    script_path=Path(f"/path/to/script{i}.py"),
                    parameters={"index": i},
                )
                runs.append(run)
            return runs

        result = benchmark(create_multiple_runs)
        assert len(result) == 10

    def test_bench_high_log_volume(self, benchmark):
        """Benchmark handling high volume of log lines."""
        capture = OutputCapture(buffer_size=100000)
        run_id = "stress-test-run"

        def capture_many_logs():
            for i in range(1000):
                capture.capture_line(run_id, f"Log line {i} with some content\n")

        benchmark(capture_many_logs)

        # Verify all logs were captured
        logs = capture.get_logs(run_id, tail=1000)
        assert len(logs) == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])
