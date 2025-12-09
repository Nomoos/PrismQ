"""Profile all modules and generate comprehensive performance baseline report.

This script:
1. Runs benchmarks for all modules
2. Generates CPU and memory profiles
3. Creates a consolidated baseline report
4. Identifies performance bottlenecks

Usage:
    python profile_all.py
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def run_benchmarks():
    """Run all benchmark suites."""
    print_header("Running Performance Benchmarks")

    benchmarks_dir = Path(__file__).parent.parent / "benchmarks"
    benchmark_files = [
        "bench_client_backend.py",
        "bench_scoring.py",
        "bench_classification.py",
    ]

    results = []

    for bench_file in benchmark_files:
        bench_path = benchmarks_dir / bench_file
        if not bench_path.exists():
            print(f"⚠️  Benchmark file not found: {bench_file}")
            continue

        print(f"\n📊 Running {bench_file}...")
        print("-" * 80)

        try:
            # Run pytest with benchmark plugin
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(bench_path),
                    "-v",
                    "--benchmark-only",
                    "--benchmark-autosave",
                    "--benchmark-save=baseline",
                ],
                cwd=benchmarks_dir,
                capture_output=False,
                text=True,
            )

            if result.returncode == 0:
                print(f"✓ {bench_file} completed successfully")
                results.append((bench_file, "SUCCESS"))
            else:
                print(f"✗ {bench_file} failed with return code {result.returncode}")
                results.append((bench_file, "FAILED"))

        except Exception as e:
            print(f"✗ Error running {bench_file}: {e}")
            results.append((bench_file, f"ERROR: {e}"))

    return results


def run_profiling():
    """Run CPU and memory profiling."""
    print_header("Running CPU and Memory Profiling")

    scripts_dir = Path(__file__).parent
    profiling_contents = [
        "profile_client.py",
        "profile_scoring.py",
        "profile_classification.py",
    ]

    results = []

    for script in profiling_contents:
        script_path = scripts_dir / script
        if not script_path.exists():
            print(f"⚠️  Profiling script not found: {script}")
            continue

        print(f"\n🔍 Running {script}...")
        print("-" * 80)

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=scripts_dir,
                capture_output=False,
                text=True,
            )

            if result.returncode == 0:
                print(f"✓ {script} completed successfully")
                results.append((script, "SUCCESS"))
            else:
                print(f"✗ {script} failed")
                results.append((script, "FAILED"))

        except Exception as e:
            print(f"✗ Error running {script}: {e}")
            results.append((script, f"ERROR: {e}"))

    return results


def generate_summary_report(benchmark_results, profiling_results):
    """Generate a summary report of all profiling activities."""
    print_header("Performance Baseline Summary")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Timestamp: {timestamp}\n")

    print("Benchmark Results:")
    print("-" * 80)
    for name, status in benchmark_results:
        status_icon = "✓" if status == "SUCCESS" else "✗"
        print(f"  {status_icon} {name}: {status}")

    print("\nProfiling Results:")
    print("-" * 80)
    for name, status in profiling_results:
        status_icon = "✓" if status == "SUCCESS" else "✗"
        print(f"  {status_icon} {name}: {status}")

    # Save summary to file
    reports_dir = Path(__file__).parent.parent / "reports" / "baseline"
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary_file = reports_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(summary_file, "w") as f:
        f.write("Performance Baseline Summary\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Timestamp: {timestamp}\n\n")

        f.write("Benchmark Results:\n")
        f.write("-" * 80 + "\n")
        for name, status in benchmark_results:
            f.write(f"  {name}: {status}\n")

        f.write("\nProfiling Results:\n")
        f.write("-" * 80 + "\n")
        for name, status in profiling_results:
            f.write(f"  {name}: {status}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("\nFor detailed results, see:\n")
        f.write("  - Benchmark results: benchmarks/.benchmarks/\n")
        f.write("  - CPU profiles: reports/cpu/\n")
        f.write("  - Memory profiles: reports/memory/\n")

    print(f"\n✓ Summary report saved to: {summary_file}")


def main():
    """Main entry point."""
    print_header("PrismQ.IdeaInspiration Performance Baseline - Phase A (Issue #111)")

    print("This script will:")
    print("  1. Run all benchmark tests")
    print("  2. Run CPU and memory profiling")
    print("  3. Generate baseline performance reports")
    print("  4. Identify bottlenecks\n")

    input("Press Enter to continue...")

    # Run benchmarks
    benchmark_results = run_benchmarks()

    # Run profiling
    profiling_results = run_profiling()

    # Generate summary
    generate_summary_report(benchmark_results, profiling_results)

    print_header("Performance Baseline Complete")
    print("\n✓ All profiling activities completed!")
    print("\nNext steps:")
    print("  1. Review benchmark results in benchmarks/.benchmarks/")
    print("  2. Review CPU profiles in reports/cpu/")
    print("  3. Review memory profiles in reports/memory/")
    print("  4. Identify bottlenecks and optimization opportunities")
    print("  5. Document findings in performance baseline report\n")


if __name__ == "__main__":
    main()
