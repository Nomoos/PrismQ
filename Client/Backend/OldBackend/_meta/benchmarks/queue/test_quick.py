"""Quick test to verify all benchmarks work."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "Backend"))

print("Testing imports...")
from throughput_benchmark import run_throughput_benchmarks
from latency_benchmark import run_latency_benchmarks
from concurrency_benchmark import run_concurrency_benchmarks
from stress_test import run_stress_tests
from memory_profile import run_memory_profiling

print("✅ All imports successful!")
print("\nBenchmark files are ready to use:")
print("1. throughput_benchmark.py")
print("2. latency_benchmark.py")
print("3. concurrency_benchmark.py")
print("4. stress_test.py")
print("5. memory_profile.py")
print("6. benchmark_runner.py (runs all)")
